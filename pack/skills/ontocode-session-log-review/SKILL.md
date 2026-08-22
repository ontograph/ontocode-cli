---
name: ontocode-session-log-review
description: Analyze local Ontocode JSONL rollout logs longitudinally for recurring workflows, failure and recovery patterns, tool usage, session churn, and skill opportunities. Use for requests to review logs over the last N days, quantify repeated operations, compare sessions, or propose reusable skills. Use session-issue-diagnostics instead for one specific failure or interpretation of a submitted sanitized /diagnostics report.
---

# Ontocode Session Log Review

Use the bundled reporter for deterministic corpus extraction, then inspect only the high-signal sessions it identifies.

## Routing

Own date-window and cross-session analysis of local rollout history. Route a
specific runtime, MCP, stream, or aborted-turn incident to
`session-issue-diagnostics`, especially when the user can submit a sanitized
`/diagnostics` report.

## Workflow

1. Run `scripts/review_sessions.py --days N`; default to 14 days when the user does not specify a period. Use `--output PATH` to save a sanitized JSON snapshot without prompt text.
2. Treat the report window as inclusive calendar dates in the requested timezone.
3. Use distinct rollout files as the session-count unit. Report originators exactly. Classify `source: cli` as root and `source.subagent` as delegated; keep other source shapes `unknown`.
4. Exclude injected `AGENTS.md`, user-profile memory, environment context, exact-response probes, greetings, internal goal envelopes, and manager dispatch packets from human-intent counts.
5. Count malformed JSONL lines and continue parsing valid lines. Never silently drop the affected file.
6. Rank workflows by distinct root sessions first. Use `aborts_by_role`, `tools_by_role`, and `operation_clusters` to separate root, delegated, and unknown calls, sessions, and repeated sessions. Report when files grow during the scan so byte totals are understood as a snapshot.
7. Check `references/recommendation-lifecycle.json` before recommending work. Verify the owning skill's `SKILL.md` contains the declared evidence terms; a matching folder name alone is insufficient.
8. For a repeated review, pass the prior sanitized snapshot with `--baseline PATH`. Prioritize `NEW` and `INCREASING` clusters whose lifecycle is not already `IMPLEMENTED`, and explain any implemented owner whose content check fails.

## Output

Report:

- exact date window, file count, byte count, originator counts, any provable root/delegated split, and malformed-line count;
- repeated human prompts and workflow families;
- frequent tool or command families;
- retry, abort, polling, and long-running job patterns from `aborts_by_role`, `tools_by_role`, and `operation_clusters`;
- three to six skill candidates with trigger phrases, scope, and overlap warnings.

Do not expose secrets or reproduce full prompts. Quote only short user-authored phrases needed as evidence.

## Script

```bash
python3 ~/.ontocode/skills/ontocode-session-log-review/scripts/review_sessions.py --days 14
```

Use `--end YYYY-MM-DD`, `--sessions-dir PATH`, or `--json` when a bounded machine-readable report is needed.

For a delta review:

```bash
python3 ~/.ontocode/skills/ontocode-session-log-review/scripts/review_sessions.py \
  --days 56 --baseline previous-summary.json --output current-summary.json --json
```

Keep lifecycle states in `references/recommendation-lifecycle.json` as `NEW`, `SELECTED`, `IMPLEMENTED`, `REJECTED`, or `SUPERSEDED`. Store only workflow identifiers, status, owner skill, and non-sensitive content terms.

Run the focused regression check after changing the reporter:

```bash
python3 ~/.ontocode/skills/ontocode-session-log-review/scripts/test_review_sessions.py
```

## Routine Tool Ownership

This skill owns routine-tool operations 1-5 and 40 in
`~/.ontocode/skills/ontocode-routine-tools/references/tool-catalog.md`. Extend the
existing reporter rather than creating parallel parsers. New implementations must
return the coordinator's shared envelope and pass its implementation gate.
