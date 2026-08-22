#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNNER="$SKILL_DIR/scripts/run-gemini-subagent.sh"
TMP="$(mktemp -d)"
KEEP=0

usage() {
  cat <<'USAGE'
Usage: smoke-test.sh [--keep]

Runs deterministic smoke tests for gemini-subagent without calling real models.
It injects a fake codex executable, then verifies runner behavior/artifacts.
Output is JSON.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --keep) KEEP=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ "$KEEP" -eq 0 ]]; then
  trap 'rm -rf "$TMP"' EXIT
fi

mkdir -p "$TMP/bin" "$TMP/work"

cat > "$TMP/bin/codex" <<'FAKE_CODEX'
#!/usr/bin/env bash
set -euo pipefail
model=""
out=""
cwd=""
json=0
stdin_prompt=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    exec) shift ;;
    --json) json=1; shift ;;
    -m|--model) model="${2:-}"; shift 2 ;;
    -C|--cd) cwd="${2:-}"; shift 2 ;;
    -o|--output-last-message) out="${2:-}"; shift 2 ;;
    --dangerously-bypass-approvals-and-sandbox) shift ;;
    -) stdin_prompt="$(cat)"; shift ;;
    *) shift ;;
  esac
done

[[ -n "$model" ]] || { echo "missing model" >&2; exit 9; }
[[ -n "$cwd" ]] || { echo "missing cwd" >&2; exit 9; }
[[ -n "$stdin_prompt" ]] || { echo "missing stdin prompt" >&2; exit 9; }

if [[ -n "$out" ]]; then
  printf 'fake final: model=%s cwd=%s prompt=%s\n' "$model" "$cwd" "$stdin_prompt" > "$out"
fi

if [[ "$json" -eq 1 ]]; then
  printf '{"type":"session.started","model":"%s"}\n' "$model"
  printf '{"type":"message","content":"ok"}\n'
else
  printf 'ok model=%s\n' "$model"
fi
FAKE_CODEX
chmod +x "$TMP/bin/codex"

PASS=0
FAIL=0
RESULTS=()

json_escape() {
  python3 -c 'import json,sys; print(json.dumps(sys.stdin.read())[1:-1])'
}

record() {
  local name="$1" status="$2" detail="${3:-}"
  if [[ "$status" == "pass" ]]; then PASS=$((PASS+1)); else FAIL=$((FAIL+1)); fi
  local escaped_detail
  escaped_detail="$(printf '%s' "$detail" | json_escape)"
  RESULTS+=("{\"name\":\"$name\",\"status\":\"$status\",\"detail\":\"$escaped_detail\"}")
}

run_test() {
  local name="$1"; shift
  local output rc
  set +e
  output="$("$@" 2>&1)"
  rc=$?
  set -e
  if [[ "$rc" -eq 0 ]]; then
    record "$name" pass "$output"
  else
    record "$name" fail "rc=$rc output=$output"
  fi
}

assert_file_contains() {
  local path="$1" needle="$2"
  [[ -f "$path" ]] || { echo "missing file: $path"; return 1; }
  grep -Fq "$needle" "$path" || { echo "missing needle '$needle' in $path"; return 1; }
}

run_test help_mentions_models bash -c "'$RUNNER' --help | grep -F 'gemini-3.1-pro-preview' >/dev/null && '$RUNNER' --help | grep -F 'gemini-3-flash-preview' >/dev/null"

set +e
invalid_out="$(PATH="$TMP/bin:$PATH" "$RUNNER" --model bad-model --cwd "$TMP/work" --prompt x 2>&1)"
invalid_rc=$?
set -e
if [[ "$invalid_rc" -ne 0 && "$invalid_out" == *"Unsupported model"* ]]; then
  record invalid_model_rejected pass "$invalid_out"
else
  record invalid_model_rejected fail "rc=$invalid_rc output=$invalid_out"
fi

for model in gemini-3.1-pro-preview gemini-3-flash-preview; do
  name="smoke-${model}"
  set +e
  start_out="$(PATH="$TMP/bin:$PATH" "$RUNNER" --model "$model" --name "$name" --cwd "$TMP/work" --prompt "structured smoke $model" 2>&1)"
  rc=$?
  set -e
  if [[ "$rc" -ne 0 ]]; then
    record "background_start_$model" fail "rc=$rc output=$start_out"
    continue
  fi

  run_dir="$TMP/work/.codex-subagents/$name"
  pid_file="$run_dir/pid"
  pid=""
  [[ -f "$pid_file" ]] && pid="$(cat "$pid_file")"
  if [[ -n "$pid" ]]; then
    for _ in {1..50}; do
      kill -0 "$pid" 2>/dev/null || break
      sleep 0.05
    done
  fi

  if assert_file_contains "$run_dir/prompt.txt" "structured smoke $model" \
    && assert_file_contains "$run_dir/events.jsonl" "\"model\":\"$model\"" \
    && assert_file_contains "$run_dir/last-message.md" "fake final: model=$model" \
    && assert_file_contains "$run_dir/run.sh" "codex exec"; then
    record "background_artifacts_$model" pass "$run_dir"
  else
    record "background_artifacts_$model" fail "$run_dir"
  fi
done

set +e
fg_out="$(PATH="$TMP/bin:$PATH" "$RUNNER" --foreground --model gemini-3-flash-preview --name smoke-foreground --cwd "$TMP/work" --prompt "foreground smoke" 2>&1)"
fg_rc=$?
set -e
fg_dir="$TMP/work/.codex-subagents/smoke-foreground"
if [[ "$fg_rc" -eq 0 ]] && [[ "$fg_out" == *'"type":"session.started"'* ]] && assert_file_contains "$fg_dir/last-message.md" "foreground smoke" >/dev/null 2>&1; then
  record foreground_flash pass "$fg_out"
else
  record foreground_flash fail "rc=$fg_rc output=$fg_out"
fi

printf '{\n'
printf '  "suite": "gemini-subagent smoke",\n'
printf '  "status": "%s",\n' "$([[ "$FAIL" -eq 0 ]] && echo pass || echo fail)"
printf '  "pass": %d,\n' "$PASS"
printf '  "fail": %d,\n' "$FAIL"
printf '  "tmp": "%s",\n' "$TMP"
printf '  "results": [\n'
for i in "${!RESULTS[@]}"; do
  sep=','
  [[ "$i" == "$((${#RESULTS[@]}-1))" ]] && sep=''
  printf '    %s%s\n' "${RESULTS[$i]}" "$sep"
done
printf '  ]\n'
printf '}\n'

[[ "$FAIL" -eq 0 ]]
