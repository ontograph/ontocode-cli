---
name: session-issue-diagnostics
description: Guide users through Ontocode's local session issue diagnostics for a specific runtime, model-stream, MCP, dynamic-tool, or aborted-turn failure. Use when asked why a session failed or to interpret a user-consented sanitized /diagnostics report. Use ontocode-session-log-review instead for longitudinal local-log analysis, workflow frequencies, or skill opportunities. The model cannot start diagnostics or read reports autonomously.
---

# Session Issue Diagnostics

## Routing

Own specific incident diagnosis and submitted sanitized `/diagnostics` reports.
Route requests to review local logs over a date range, count repeated workflows,
or propose skills to `ontocode-session-log-review`.

Use the human-started TUI workflow:

1. Ask the user to run `/diagnostics` and choose **Analyze session issues**.
2. Let the user select and confirm the effective period. Only full success
   advances diagnostics state.
3. To inspect the result with the assistant, ask the user to choose
   **Analyze latest report with assistant** from `/diagnostics`.
4. Interpret only the bounded sanitized evidence supplied to the conversation.
   Recommend concrete debugging or verification steps grounded in its event
   class, subsystem, normalized code, outcome, severity, counts, timestamps,
   and validated Ontocode versions.

Describe diagnostics state precisely:

- **Not invoked:** no sanitized report context was submitted. Say that no
  diagnostics execution was attempted; do not call this a tool or analyzer
  failure. Direct the user to the human-started workflow above.
- **No committed report:** use only when the TUI reports that no committed
  report is available. Ask the user to run and complete an analysis first.
- **Analysis failed:** use only when a TUI terminal outcome or submitted
  sanitized evidence explicitly reports failure. Preserve its typed outcome
  rather than inferring a cause.

Do not claim that you ran diagnostics, read local rollout files, or accessed a
report unless the user explicitly submitted the sanitized report context. Do
not ask for raw rollout logs, credentials, paths, commands, tool output, or
unredacted error text when the diagnostics workflow can provide typed evidence.
