#!/usr/bin/env bash
set -euo pipefail

usage() {
    cat <<'EOFU'
Usage: run_qt_perf_monitor.sh [--duration SECONDS] [--interval SECONDS] [--repo DIR] [--out DIR] [--qt-log-level LEVEL] [--threads] [--memory-snapshots] [--dry-run] [--] [run-qt args...]

Runs ./run-qt.sh, samples Qt/COOL process CPU and memory, then writes a compact report.
Defaults: --duration 180 --interval 5 --repo . --out tools/runtime-trace/artifacts/qt-perf-monitor/<timestamp>
EOFU
}

DURATION=180
INTERVAL=5
REPO="."
OUT=""
DRY_RUN=0
THREADS=0
MEMORY_SNAPSHOTS=0
QT_LOG_LEVEL="${QT_LOG_LEVEL:-information}"
RUN_QT_ARGS=()

while [[ $# -gt 0 ]]; do
    case "$1" in
        --duration) DURATION="$2"; shift 2 ;;
        --interval) INTERVAL="$2"; shift 2 ;;
        --repo) REPO="$2"; shift 2 ;;
        --out) OUT="$2"; shift 2 ;;
        --qt-log-level) QT_LOG_LEVEL="$2"; shift 2 ;;
        --threads) THREADS=1; shift ;;
        --memory-snapshots) MEMORY_SNAPSHOTS=1; shift ;;
        --dry-run) DRY_RUN=1; shift ;;
        -h|--help) usage; exit 0 ;;
        --) shift; RUN_QT_ARGS+=("$@"); break ;;
        *) RUN_QT_ARGS+=("$1"); shift ;;
    esac
done

[[ "$DURATION" =~ ^[0-9]+$ ]] || { echo "duration must be integer seconds" >&2; exit 2; }
[[ "$INTERVAL" =~ ^[0-9]+$ ]] || { echo "interval must be integer seconds" >&2; exit 2; }
(( DURATION > 0 )) || { echo "duration must be > 0" >&2; exit 2; }
(( INTERVAL > 0 )) || { echo "interval must be > 0" >&2; exit 2; }

REPO="$(cd "$REPO" && pwd)"
RUN_QT="$REPO/run-qt.sh"
[[ -x "$RUN_QT" ]] || { echo "missing executable: $RUN_QT" >&2; exit 1; }

RUN_QT_LAUNCH_ARGS=("${RUN_QT_ARGS[@]}")
if [[ " ${RUN_QT_LAUNCH_ARGS[*]} " != *" --log-level="* && " ${RUN_QT_LAUNCH_ARGS[*]} " != *" --log-level "* ]]; then
    RUN_QT_LAUNCH_ARGS=("--log-level=$QT_LOG_LEVEL" "${RUN_QT_LAUNCH_ARGS[@]}")
fi

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
if [[ -z "$OUT" ]]; then
    OUT="$REPO/tools/runtime-trace/artifacts/qt-perf-monitor/$STAMP"
fi
mkdir -p "$OUT"

SAMPLES="$OUT/process-samples.tsv"
THREAD_SAMPLES="$OUT/thread-samples.tsv"
RUN_LOG="$OUT/run-qt.log"
SUMMARY="$OUT/SUMMARY.md"
META="$OUT/meta.env"
MEMORY_DIR="$OUT/memory-snapshots"
MEMORY_SUMMARY="$OUT/memory-summary.tsv"

collect_glxinfo() {
    if ! command -v glxinfo >/dev/null 2>&1; then
        return 0
    fi
    if command -v timeout >/dev/null 2>&1; then
        timeout 5 glxinfo -B 2>/dev/null || true
    else
        glxinfo -B 2>/dev/null || true
    fi
}

GLXINFO_OUTPUT="$(collect_glxinfo)"
OPENGL_VENDOR="$(printf '%s\n' "$GLXINFO_OUTPUT" | awk -F: '/OpenGL vendor string/ { sub(/^ +/, "", $2); print $2; exit }')"
OPENGL_RENDERER="$(printf '%s\n' "$GLXINFO_OUTPUT" | awk -F: '/OpenGL renderer string/ { sub(/^ +/, "", $2); print $2; exit }')"
OPENGL_VERSION="$(printf '%s\n' "$GLXINFO_OUTPUT" | awk -F: '/OpenGL version string/ { sub(/^ +/, "", $2); print $2; exit }')"

cat > "$META" <<EOFM
repo=$REPO
duration=$DURATION
interval=$INTERVAL
out=$OUT
stamp=$STAMP
run_qt=$RUN_QT
run_qt_args=${RUN_QT_LAUNCH_ARGS[*]-}
qt_log_level=$QT_LOG_LEVEL
threads=$THREADS
memory_snapshots=$MEMORY_SNAPSHOTS
live_server=${LIVE_SERVER:-1}
coda_qt_keep_cache=${CODA_QT_KEEP_CACHE:-}
qtwebengine_chromium_flags=${QTWEBENGINE_CHROMIUM_FLAGS:-}
qt_quick_backend=${QT_QUICK_BACKEND:-}
qt_open_gl=${QT_OPENGL:-}
libgl_always_software=${LIBGL_ALWAYS_SOFTWARE:-}
mesa_loader_driver_override=${MESA_LOADER_DRIVER_OVERRIDE:-}
lp_num_threads=${LP_NUM_THREADS:-}
coda_qt_use_gpu=${CODA_QT_USE_GPU:-}
opengl_vendor=${OPENGL_VENDOR:-unknown}
opengl_renderer=${OPENGL_RENDERER:-unknown}
opengl_version=${OPENGL_VERSION:-unknown}
EOFM

if [[ "$DRY_RUN" == "1" ]]; then
    cat <<EOFD
DRY RUN
repo: $REPO
command: $RUN_QT ${RUN_QT_LAUNCH_ARGS[*]-}
duration: $DURATION
interval: $INTERVAL
out: $OUT
qt_log_level: $QT_LOG_LEVEL
threads: $THREADS
memory_snapshots: $MEMORY_SNAPSHOTS
EOFD
    exit 0
fi

# Header: epoch, elapsed_s, pid, ppid, pgid, comm, pcpu, pmem, rss_kb, vsz_kb, etime, args
echo -e "epoch\telapsed_s\tpid\tppid\tpgid\tcomm\tpcpu\tpmem\trss_kb\tvsz_kb\tetime\targs" > "$SAMPLES"
if [[ "$THREADS" == "1" ]]; then
    echo -e "epoch\telapsed_s\tpid\ttid\tpsr\tstat\tpcpu\tcomm\targs" > "$THREAD_SAMPLES"
fi
if [[ "$MEMORY_SNAPSHOTS" == "1" ]]; then
    mkdir -p "$MEMORY_DIR"
    echo -e "epoch\telapsed_s\tpid\tcomm\tVmPeak_kb\tVmSize_kb\tVmHWM_kb\tVmRSS_kb\tRssAnon_kb\tRssFile_kb\tRssShmem_kb\tThreads\tPss_kb\tPrivate_Dirty_kb\tAnonymous_kb\tSwap_kb" > "$MEMORY_SUMMARY"
fi

snapshot_process_memory() {
    local epoch="$1"
    local elapsed="$2"
    local sample_file="$3"
    [[ "$MEMORY_SNAPSHOTS" == "1" ]] || return 0
    [[ -s "$sample_file" ]] || return 0

    local snap_dir="$MEMORY_DIR/elapsed-$(printf '%05d' "$elapsed")"
    mkdir -p "$snap_dir"
    cp "$sample_file" "$snap_dir/processes.tsv" 2>/dev/null || true

    awk -F '\t' 'NR > 1 { print $3 "\t" $6 }' "$sample_file" | sort -u | while IFS=$'\t' read -r pid comm; do
        [[ -n "$pid" && -d "/proc/$pid" ]] || continue

        if [[ -r "/proc/$pid/status" ]]; then
            cp "/proc/$pid/status" "$snap_dir/$pid.status" 2>/dev/null || true
        fi
        if [[ -r "/proc/$pid/smaps_rollup" ]]; then
            cp "/proc/$pid/smaps_rollup" "$snap_dir/$pid.smaps_rollup" 2>/dev/null || true
        fi
        if command -v pmap >/dev/null 2>&1; then
            pmap -x "$pid" > "$snap_dir/$pid.pmap" 2>/dev/null || true
        fi

        awk -v epoch="$epoch" -v elapsed="$elapsed" -v pid="$pid" -v comm="$comm" '
            FILENAME ~ /status$/ {
                if ($1 == "VmPeak:") vmpeak=$2;
                else if ($1 == "VmSize:") vmsize=$2;
                else if ($1 == "VmHWM:") vmhwm=$2;
                else if ($1 == "VmRSS:") vmrss=$2;
                else if ($1 == "RssAnon:") rssanon=$2;
                else if ($1 == "RssFile:") rssfile=$2;
                else if ($1 == "RssShmem:") rssshmem=$2;
                else if ($1 == "Threads:") threads=$2;
            }
            FILENAME ~ /smaps_rollup$/ {
                if ($1 == "Pss:") pss=$2;
                else if ($1 == "Private_Dirty:") privdirty=$2;
                else if ($1 == "Anonymous:") anon=$2;
                else if ($1 == "Swap:") swap=$2;
            }
            END {
                printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n",
                    epoch, elapsed, pid, comm, vmpeak+0, vmsize+0, vmhwm+0, vmrss+0,
                    rssanon+0, rssfile+0, rssshmem+0, threads+0, pss+0,
                    privdirty+0, anon+0, swap+0;
            }' "$snap_dir/$pid.status" "$snap_dir/$pid.smaps_rollup" 2>/dev/null >> "$MEMORY_SUMMARY" || true
    done
}

cleanup_done=0
RUNNER_PID=""
RUNNER_PGID=""
RUN_MARKER="qt-perf-monitor-run-$STAMP"

collect_descendants() {
    local root_pid="$1"
    local children child
    [[ -n "$root_pid" ]] || return 0
    printf "%s\n" "$root_pid"
    children=$(ps -eo pid=,ppid= | awk -v root="$root_pid" '$2 == root { print $1 }')
    for child in $children; do
        collect_descendants "$child"
    done
}

kill_pid_list() {
    local signal="$1"
    shift || true
    local pid
    for pid in "$@"; do
        [[ -n "$pid" ]] || continue
        kill -"$signal" "$pid" 2>/dev/null || true
    done
}

cleanup() {
    [[ "$cleanup_done" == "1" ]] && return 0
    cleanup_done=1

    local descendants=()
    local pid extra_pids=()

    if [[ -n "${RUNNER_PID:-}" ]]; then
        while IFS= read -r pid; do
            [[ -n "$pid" ]] && descendants+=("$pid")
        done < <(collect_descendants "$RUNNER_PID" | awk 'NF { print $1 }' | sort -u)
    fi

    while IFS= read -r pid; do
        [[ -n "$pid" ]] && extra_pids+=("$pid")
    done < <(ps -eo pid=,args= | awk -v repo="$REPO" 'index($0, repo "/run-qt.sh") || index($0, repo "/build-scratch/coolwsd") || index($0, repo "/build-scratch/qt/coda-qt") || index($0, repo "/instdir/program/coolforkit") || index($0, repo "/instdir/program/kit_spare_") { print $1 }' | sort -u)

    if [[ -n "${RUNNER_PGID:-}" ]]; then
        kill -TERM -- -"$RUNNER_PGID" 2>/dev/null || true
    fi
    if (( ${#descendants[@]} > 0 )); then
        kill_pid_list TERM "${descendants[@]}"
    fi
    if (( ${#extra_pids[@]} > 0 )); then
        kill_pid_list TERM "${extra_pids[@]}"
    fi

    sleep 2

    if [[ -n "${RUNNER_PGID:-}" ]]; then
        kill -KILL -- -"$RUNNER_PGID" 2>/dev/null || true
    fi
    if (( ${#descendants[@]} > 0 )); then
        kill_pid_list KILL "${descendants[@]}"
    fi
    if (( ${#extra_pids[@]} > 0 )); then
        kill_pid_list KILL "${extra_pids[@]}"
    fi

    local extra_xvfb=()
    while IFS= read -r pid; do
        [[ -n "$pid" ]] && extra_xvfb+=("$pid")
    done < <(ps -eo pid=,args= | awk '/Xvfb :99/ && /\/tmp\/xvfb-run\./ { print $1 }' | sort -u)
    if (( ${#extra_xvfb[@]} > 0 )); then
        kill_pid_list TERM "${extra_xvfb[@]}"
        sleep 1
        kill_pid_list KILL "${extra_xvfb[@]}"
    fi

    if [[ -n "${RUNNER_PID:-}" ]]; then
        wait "$RUNNER_PID" 2>/dev/null || true
    fi
}
trap cleanup EXIT INT TERM

CODA_QT_PERF_RUN_MARKER="$RUN_MARKER" setsid bash -c 'cd "$1" && shift && exec ./run-qt.sh "$@"' _ "$REPO" "${RUN_QT_LAUNCH_ARGS[@]}" > "$RUN_LOG" 2>&1 &
RUNNER_PID=$!
RUNNER_PGID=$(ps -o pgid= -p "$RUNNER_PID" 2>/dev/null | tr -d " ")
echo "$RUNNER_PID" > "$OUT/runner.pid"

start_epoch="$(date +%s)"
end_epoch=$((start_epoch + DURATION))

while :; do
    now="$(date +%s)"
    (( now > end_epoch )) && break
    elapsed=$((now - start_epoch))

    SAMPLE_TMP="$OUT/.process-sample-$elapsed.tsv"
    echo -e "epoch\telapsed_s\tpid\tppid\tpgid\tcomm\tpcpu\tpmem\trss_kb\tvsz_kb\tetime\targs" > "$SAMPLE_TMP"

    ps -eo pid=,ppid=,pgid=,comm=,pcpu=,pmem=,rss=,vsz=,etime=,args= \
      | awk -v epoch="$now" -v elapsed="$elapsed" '
            /coda-qt|run-qt.sh|coolwsd|coolforkit|kit_spare|QtWebEngine|lo_kit|forkit/ {
                pid=$1; ppid=$2; pgid=$3; comm=$4; pcpu=$5; pmem=$6; rss=$7; vsz=$8; etime=$9;
                $1=$2=$3=$4=$5=$6=$7=$8=$9=""; sub(/^ +/, "");
                gsub(/\t/, " ");
                printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n", epoch, elapsed, pid, ppid, pgid, comm, pcpu, pmem, rss, vsz, etime, $0;
            }' >> "$SAMPLE_TMP"
    tail -n +2 "$SAMPLE_TMP" >> "$SAMPLES"
    snapshot_process_memory "$now" "$elapsed" "$SAMPLE_TMP"
    rm -f "$SAMPLE_TMP"

    if [[ "$THREADS" == "1" ]]; then
        tail -n +2 "$SAMPLES" | awk -F '\t' '{print $3}' | sort -u | while IFS= read -r pid; do
            [[ -n "$pid" ]] || continue
            ps -L -p "$pid" -o pid=,tid=,psr=,stat=,pcpu=,comm=,args= 2>/dev/null \
              | awk -v epoch="$now" -v elapsed="$elapsed" -v pid="$pid" '
                    { tid=$2; psr=$3; stat=$4; pcpu=$5; comm=$6; $1=$2=$3=$4=$5=$6=""; sub(/^ +/, ""); gsub(/\t/, " "); printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n", epoch, elapsed, pid, tid, psr, stat, pcpu, comm, $0; }' \
              >> "$THREAD_SAMPLES" || true
        done
    fi

    sleep "$INTERVAL"
done

cleanup
trap - EXIT INT TERM

QT_SURFACE_TYPE="$(awk -F: '/Surface Type:/ { sub(/^ +/, "", $2); print $2; exit }' "$RUN_LOG" 2>/dev/null || true)"
QSG_RHI_BACKEND="$(awk -F: '/QSG RHI Backend:/ { sub(/^ +/, "", $2); print $2; exit }' "$RUN_LOG" 2>/dev/null || true)"
QSG_MULTITHREADED_OPENGL="$(awk -F: '/Using Multithreaded OpenGL:/ { sub(/^ +/, "", $2); print $2; exit }' "$RUN_LOG" 2>/dev/null || true)"
{
    echo "qt_surface_type=${QT_SURFACE_TYPE:-unknown}"
    echo "qsg_rhi_backend=${QSG_RHI_BACKEND:-unknown}"
    echo "qsg_multithreaded_opengl=${QSG_MULTITHREADED_OPENGL:-unknown}"
} >> "$META"

awk -F '\t' '
NR==1 { next }
{
    comm=$6; count[comm]++;
    cpuSum[comm]+=$7; rssSum[comm]+=$9;
    if ($7+0 > cpuMax[comm]) cpuMax[comm]=$7+0;
    if ($9+0 > rssMax[comm]) rssMax[comm]=$9+0;
}
END {
    print "| process | samples | avg_cpu_pct | max_cpu_pct | avg_rss_mb | max_rss_mb |";
    print "| --- | ---: | ---: | ---: | ---: | ---: |";
    for (comm in count) {
        printf "| %s | %d | %.2f | %.2f | %.1f | %.1f |\n", comm, count[comm], cpuSum[comm]/count[comm], cpuMax[comm], (rssSum[comm]/count[comm])/1024, rssMax[comm]/1024;
    }
}' "$SAMPLES" | sort > "$OUT/process-summary.md"

if [[ "$THREADS" == "1" && -s "$THREAD_SAMPLES" ]]; then
    {
        echo "| tid | comm | samples | avg_cpu_pct |"
        echo "| ---: | --- | ---: | ---: |"
        awk -F '\t' '
NR==1 { next }
{
    key=$4 SUBSEP $8;
    count[key]++;
    cpuSum[key]+=$7;
}
END {
    for (key in count) {
        split(key, parts, SUBSEP);
        printf "%s\t| %s | %s | %d | %.2f |\n", parts[1], parts[1], parts[2], count[key], cpuSum[key]/count[key];
    }
}' "$THREAD_SAMPLES" | sort -n -k1,1 | cut -f2-
    } > "$OUT/thread-summary.md"
fi

{
    echo "# Qt Performance Monitor Summary"
    echo
    echo "- Date UTC: $STAMP"
    echo "- Repo: $REPO"
    echo "- Duration seconds: $DURATION"
    echo "- Interval seconds: $INTERVAL"
    echo "- Command: ./run-qt.sh ${RUN_QT_LAUNCH_ARGS[*]-}"
    echo "- Samples: $(($(wc -l < "$SAMPLES") - 1)) process rows"
    echo "- Thread sampling: $THREADS"
    echo "- Memory snapshots: $MEMORY_SNAPSHOTS"
    echo "- Qt log level: $QT_LOG_LEVEL"
    echo "- LIVE_SERVER: ${LIVE_SERVER:-1}"
    echo "- CODA_QT_KEEP_CACHE: ${CODA_QT_KEEP_CACHE:-}"
    echo "- QTWEBENGINE_CHROMIUM_FLAGS: ${QTWEBENGINE_CHROMIUM_FLAGS:-}"
    echo "- QT_QUICK_BACKEND: ${QT_QUICK_BACKEND:-}"
    echo "- QT_OPENGL: ${QT_OPENGL:-}"
    echo "- LIBGL_ALWAYS_SOFTWARE: ${LIBGL_ALWAYS_SOFTWARE:-}"
    echo "- MESA_LOADER_DRIVER_OVERRIDE: ${MESA_LOADER_DRIVER_OVERRIDE:-}"
    echo "- LP_NUM_THREADS: ${LP_NUM_THREADS:-}"
    echo "- CODA_QT_USE_GPU: ${CODA_QT_USE_GPU:-}"
    echo "- OpenGL vendor: ${OPENGL_VENDOR:-unknown}"
    echo "- OpenGL renderer: ${OPENGL_RENDERER:-unknown}"
    echo "- OpenGL version: ${OPENGL_VERSION:-unknown}"
    echo "- Qt surface type: ${QT_SURFACE_TYPE:-unknown}"
    echo "- QSG RHI backend: ${QSG_RHI_BACKEND:-unknown}"
    echo "- QSG multithreaded OpenGL: ${QSG_MULTITHREADED_OPENGL:-unknown}"
    echo
    echo "## Process summary"
    echo
    cat "$OUT/process-summary.md"
    if [[ -f "$OUT/thread-summary.md" ]]; then
        echo
        echo "## Thread summary"
        echo
        cat "$OUT/thread-summary.md"
    fi
    echo
    echo "## Artifacts"
    echo
    echo "- process samples: process-samples.tsv"
    [[ -f "$THREAD_SAMPLES" ]] && echo "- thread samples: thread-samples.tsv"
    [[ -f "$MEMORY_SUMMARY" ]] && echo "- memory summary: memory-summary.tsv"
    [[ -d "$MEMORY_DIR" ]] && echo "- memory snapshots: memory-snapshots/"
    echo "- run log: run-qt.log"
    echo "- metadata: meta.env"
} > "$SUMMARY"

cat "$SUMMARY"
