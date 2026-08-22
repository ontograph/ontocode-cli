---
name: delegate-to-luna
description: Route one already-decided, file-bounded implementation task to the built-in luna_worker after local or explorer discovery. Use when the user explicitly requests Luna or sub-agent delegation and exact files, target symbols, behavior, validation, and stop conditions are known. Do not use for discovery, planning, architecture decisions, broad reviews, or whole project plans.
---

# Delegate To Luna

Route one concrete implementation packet to `luna_worker`. This skill does not
authorize delegation; use it only when the user has explicitly requested Luna,
sub-agents, delegation, or parallel agent work.

## Workflow

1. Inspect the code locally first. Use a read-only `explorer` only when a
   specific ownership or location question remains.
2. Keep the immediate blocking task local. Delegate only a bounded task that
   can run independently without blocking the next local action.
3. Confirm the packet contains:
   - one concrete objective;
   - exact writable files or modules and target symbols;
   - decided behavior and invariants;
   - non-goals and prohibited files;
   - focused validation commands and required evidence;
   - stop conditions for scope expansion, conflicts, or unresolved decisions.
4. Dispatch exactly one `luna_worker` for that packet. Prefer the built-in
   default model and effort; only set an explicit model from the approved
   candidate list when capacity requires a fallback.
5. Tell Luna it is not alone in the worktree and must preserve concurrent edits.
6. Do not duplicate Luna's implementation locally. Continue only with
   non-overlapping work.
7. Review the returned changed files and validation evidence. Run the final
   task-level checks locally, then close the child.

## Rejection Rules

Do not dispatch `luna_worker` when the task still asks to investigate, decide,
find ownership, review the repository, design architecture, plan work, or
implement a whole plan. Resolve the missing fact locally or with `explorer`,
then construct a new bounded packet.

Do not use Luna to replace authenticated `coder-*`, librarian, or md-plans
gates. If `spawn_agent`, the `luna_worker` role, or every approved model
candidate is unavailable, report `blocked: capability unavailable` rather than
substituting another role silently.
