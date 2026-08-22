#!/usr/bin/env bash
set -euo pipefail

MODEL="gemini-3.1-pro-preview"
NAME=""
CWD="$(pwd)"
PROMPT=""
PROMPT_FILE=""
FOREGROUND=0
SANDBOX_ARGS=(--dangerously-bypass-approvals-and-sandbox)

usage() {
  cat <<'USAGE'
Usage: run-gemini-subagent.sh [options]

Start a Gemini Codex sub-agent as a second codex exec session/process.

Options:
  --model MODEL        gemini-3.1-pro-preview or gemini-3-flash-preview
  --name NAME          log/session name under .codex-subagents/ (default: model-timestamp)
  --cwd DIR            working directory for the sub-agent (default: current dir)
  --prompt TEXT        prompt text
  --prompt-file FILE   read prompt from file
  --foreground         run in foreground instead of background
  --safe-sandbox       use Codex default sandbox instead of dangerous bypass
  -h, --help           show this help

Examples:
  run-gemini-subagent.sh --model gemini-3.1-pro-preview --name audit --prompt "Review current diff"
  run-gemini-subagent.sh --model gemini-3-flash-preview --cwd /repo --prompt-file task.md
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --model) MODEL="${2:?missing value for --model}"; shift 2 ;;
    --name) NAME="${2:?missing value for --name}"; shift 2 ;;
    --cwd) CWD="${2:?missing value for --cwd}"; shift 2 ;;
    --prompt) PROMPT="${2:?missing value for --prompt}"; shift 2 ;;
    --prompt-file) PROMPT_FILE="${2:?missing value for --prompt-file}"; shift 2 ;;
    --foreground) FOREGROUND=1; shift ;;
    --safe-sandbox) SANDBOX_ARGS=(); shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; usage >&2; exit 2 ;;
  esac
done

case "$MODEL" in
  gemini-3.1-pro-preview|gemini-3-flash-preview) ;;
  *) echo "Unsupported model: $MODEL" >&2; exit 2 ;;
esac

if [[ -n "$PROMPT_FILE" ]]; then
  [[ -f "$PROMPT_FILE" ]] || { echo "Prompt file not found: $PROMPT_FILE" >&2; exit 2; }
  PROMPT="$(cat "$PROMPT_FILE")"
fi

[[ -n "$PROMPT" ]] || { echo "Missing --prompt or --prompt-file" >&2; usage >&2; exit 2; }
[[ -d "$CWD" ]] || { echo "CWD not found: $CWD" >&2; exit 2; }
command -v codex >/dev/null || { echo "codex not found in PATH" >&2; exit 127; }

if [[ -z "$NAME" ]]; then
  NAME="${MODEL}-$(date +%Y%m%d-%H%M%S)"
fi
NAME="$(printf '%s' "$NAME" | tr -c 'A-Za-z0-9_.-' '-')"

RUN_DIR="$CWD/.codex-subagents/$NAME"
mkdir -p "$RUN_DIR"
PROMPT_PATH="$RUN_DIR/prompt.txt"
EVENTS_PATH="$RUN_DIR/events.jsonl"
LAST_PATH="$RUN_DIR/last-message.md"
PID_PATH="$RUN_DIR/pid"
RUN_PATH="$RUN_DIR/run.sh"

printf '%s\n' "$PROMPT" > "$PROMPT_PATH"

cat > "$RUN_PATH" <<RUN
#!/usr/bin/env bash
set -euo pipefail
cd "$(printf '%q' "$CWD")"
codex exec --json -m "$(printf '%q' "$MODEL")" -C "$(printf '%q' "$CWD")" ${SANDBOX_ARGS[*]} -o "$(printf '%q' "$LAST_PATH")" - < "$(printf '%q' "$PROMPT_PATH")"
RUN
chmod +x "$RUN_PATH"

if [[ "$FOREGROUND" -eq 1 ]]; then
  echo "Running foreground Gemini sub-agent: $NAME ($MODEL)" >&2
  "$RUN_PATH" | tee "$EVENTS_PATH"
else
  nohup "$RUN_PATH" > "$EVENTS_PATH" 2>&1 &
  PID=$!
  printf '%s\n' "$PID" > "$PID_PATH"
  cat <<OUT
Started Gemini sub-agent: $NAME
model: $MODEL
pid: $PID
run_dir: $RUN_DIR
monitor: tail -f "$EVENTS_PATH"
final: cat "$LAST_PATH"
stop: kill "\$(cat '$PID_PATH')"
OUT
fi
