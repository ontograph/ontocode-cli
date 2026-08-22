---
name: gemini-subagent
description: Run Gemini 3.1 Pro Preview or Gemini 3 Flash Preview as a Codex sub-agent by launching a second codex exec session/process. Use when the user asks to start, dispatch, spawn, run, monitor, stop, or manage a Gemini sub-agent/session using gemini-3.1-pro-preview or gemini-3-flash-preview, especially when native spawn_agent does not support those models.
---

# Gemini Sub-agent

Use this skill to run `gemini-3.1-pro-preview` or `gemini-3-flash-preview` as a second Codex process/session from the main agent.

## Core rule

Do **not** use native `spawn_agent` for these models unless the current tool schema explicitly lists them. Prefer `codex exec` because it accepts model slugs from the local Codex catalog.

Supported model slugs:

- `gemini-3.1-pro-preview` — stronger, slower, for architecture/review/large-context tasks.
- `gemini-3-flash-preview` — faster, cheaper, for bounded implementation/search/check tasks.

## Quick commands

Run foreground one-shot:

```bash
codex exec -m gemini-3.1-pro-preview -C "$PWD" --dangerously-bypass-approvals-and-sandbox "TASK"
```

Run background sub-agent:

```bash
~/.agents/skills/gemini-subagent/scripts/run-gemini-subagent.sh \
  --model gemini-3.1-pro-preview \
  --name gemini31-task \
  --cwd "$PWD" \
  --prompt "TASK"
```

Use Flash instead:

```bash
~/.agents/skills/gemini-subagent/scripts/run-gemini-subagent.sh \
  --model gemini-3-flash-preview \
  --name gemini3-flash-task \
  --cwd "$PWD" \
  --prompt "TASK"
```

## Workflow

1. Choose model:
   - Use `gemini-3.1-pro-preview` for deep reasoning, large audits, design review, integration planning.
   - Use `gemini-3-flash-preview` for fast exploratory checks, simple code edits, test triage, summaries.
2. Write a self-contained prompt. Include:
   - exact task
   - repo path / working directory
   - files or ownership scope
   - output expected
   - instruction not to revert others' edits if multiple agents run
3. Start with `scripts/run-gemini-subagent.sh` for background work.
4. Monitor log with the command printed by the script.
5. Inspect final output file before trusting results.

## Script behavior

The bundled script creates `.codex-subagents/<name>/` under the selected cwd with:

- `prompt.txt` — prompt sent to Codex
- `events.jsonl` — Codex JSON event stream
- `last-message.md` — final assistant message from the sub-agent
- `pid` — background process id
- `run.sh` — exact command used


## Smoke test

Run deterministic smoke tests without calling real Gemini models:

```bash
~/.agents/skills/gemini-subagent/scripts/smoke-test.sh
```

The smoke test injects a fake `codex` executable and returns structured JSON with `status`, `pass`, `fail`, and per-test `results`. It verifies help output, invalid model rejection, background artifacts for both supported models, and foreground structured output.

## Monitoring

```bash
tail -f .codex-subagents/<name>/events.jsonl
cat .codex-subagents/<name>/last-message.md
ps -p "$(cat .codex-subagents/<name>/pid)"
```

Stop:

```bash
kill "$(cat .codex-subagents/<name>/pid)"
```

## Safety

- Use unique `--name` values to avoid overwriting logs.
- For code edits, assign disjoint files/modules to each sub-agent.
- Tell each sub-agent: "You are not alone in the codebase; do not revert edits made by others."
- Prefer foreground mode for risky changes or when immediate supervision is needed.
