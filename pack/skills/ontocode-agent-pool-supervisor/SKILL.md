---
name: ontocode-agent-pool-supervisor
description: Observe, drain, and close a healthy Ontocode sub-agent pool with bounded polling and compact status reporting. Use when asked to wait for all agents, check agent status, collect completed results, or close finished agents. Use ontocode-subagent-recovery instead when an agent has a provider, transport, schema, receipt, quota, null-result, or budget failure.
---

# Ontocode Agent Pool Supervisor

Drain one healthy pool without changing task scope or retry policy.

## Workflow

1. List live agents once and record each task path and state.
2. Collect terminal results once. Close completed agents when no follow-up is pending.
3. If agents are still working, call `wait_agent` once with a bounded timeout. Do not repeatedly poll `list_agents` while nothing changes.
4. Report each state transition, collect newly completed results, and close agents no longer needed.
5. Repeat only while a healthy agent remains active and the user asked to wait through completion.
6. Route provider, transport, schema, receipt, quota, null-result, or budget failures to `ontocode-subagent-recovery`. Continue supervising unrelated healthy agents.
7. Finish when every agent is closed, retained for a named follow-up, or routed to recovery.
8. Consolidate the terminal state into one table. Include one row per task path with final state, result or receipt identity when available, closure state, and recovery route. Do not repeat full agent messages.

## Boundaries

- Do not spawn work, alter prompts, retry failures, or change models.
- Do not interrupt a healthy agent merely because it has not produced a recent message.
- Do not close an agent before collecting a result needed by the parent task.
- Report only state changes, terminal results, and the final pool summary.

## Output

Report initial and final agent counts, followed by one terminal table:

```text
task_path | state | result_or_receipt | closure | recovery
```

Use `none` for unavailable fields. Then report the pool state: `DRAINED`, `ACTIVE`, or `RECOVERY_REQUIRED`.

## Routine Tool Ownership

This skill owns routine-tool operations 21-22 in
`~/.ontocode/skills/ontocode-routine-tools/references/tool-catalog.md`. Pool
snapshots and waits must be deadline-bounded, avoid busy polling, and return the
coordinator's shared envelope.
