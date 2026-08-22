---
name: axel-plan-autopilot
description: Inspect and execute schema-valid Axel project plans through the strict manager loop. Use when the user asks what is left, lists open tasks, says continue, unblock tasks and continue, check space and continue, requests correction of rejected execution evidence, requests autonomous completion of a plan, or names a tracking Markdown file with a manager_loop block.
---

# Axel Plan Autopilot

Drive one repository tracking plan until completion or a recorded stop condition.

## Workflow

1. Confirm the tracking path is a Markdown file under `docs/` or `.memory-bank/`.
2. Read `AGENTS.md`, the plan's `manager_loop` block, and only the selected task packet. Do not repeatedly read the full plan.
3. Run `project_plan_validate` before dispatch. Stop on a structural validation failure and repair only when the task permits plan writes.
4. When the task declares a delegated worktree packet, verify its task ID,
   tracking path, base SHA, branch, worktree path, owner/reviewer, write sets,
   validation commands, and evidence directory before dispatch. Require
   `owner_files` to be contained by `allowed_write_set`. Worktree creation and
   repair belong to `mb-harness`; do not create an alternate packet here.
5. Call `manager_loop_advance` with `action: next`, `mode: strict`, and the current tracking path.
6. Follow the returned decision exactly:
   - `dispatch`: call `manager_loop_advance(action: dispatch)` with the returned task state.
   - `observe`: use `wait_agent` once, then authenticate the returned receipt.
   - `integrate`: call `manager_loop_advance(action: integrate)` with the exact task, revision, and receipt.
   - terminal or stop condition: report it with its recorded evidence.
7. Repeat `next -> dispatch -> observe -> integrate` without asking the user to say continue again.
8. After every integration, report the task ID and the next state in one short update.

## Recovery Accounting

For the active task, maintain these counts in its existing tracker evidence or task notes; do not create a parallel ledger:

- `evidence_corrections`
- `rejected_receipts`
- `consecutive_touches_without_completion`
- `disk_recoveries`
- `background_job_resumptions`

Increment a count only from a recorded manager outcome or completed recovery route. Reset `consecutive_touches_without_completion` when the task completes or advances to a different task. When the same task reaches three consecutive touches without completion, quote the repository stop condition, record the concrete blocker, and advance or stop as the owning plan requires. Do not polish or redispatch the task again without new failing evidence or an explicit user request.

## Recovery Rules

- Never hand-edit manager-loop state while a durable lease or receipt is active.
- On rejected execution evidence, preserve task scope and run only the validator-requested correction. Record the exact command and exit status, then resume with the manager tool's recorded token. Do not redispatch implementation that already exists.
- On stale revision, prompt-shape, dependency, or evidence failure, use only the resume token recorded by the manager tool after the stated correction exists.
- Route provider, authentication, quota, transport, null-result, schema, receipt, or budget failures to `ontocode-subagent-recovery`.
- Route `check space and continue` through `axel-disk-space-recovery`, then resume the same plan only after recovery evidence is complete.
- Route an already-running long build, validation, or index command through `axel-background-job-watch`; do not start a duplicate job. Resume the same manager-loop state after its terminal result is recorded.
- Treat model or capacity exhaustion as the recorded task outcome; do not substitute an unapproved local role.
- Treat transient read-only tooling as session state, not a project blocker. Continue read-only analysis and queue the bounded write.
- Do not infer work from prose task lists. Authority is the structured `manager_loop` and task status metadata.
- Do not reopen completed tasks unless a failing validation or explicit user request requires it.

## Completion Evidence

Report the final manager-loop state, completed task IDs, current active task if any, validation commands with exit status, recovery counts for touched tasks, and the exact blocker or stop condition. Never call a plan complete from prose alone.

## Routine Tool Ownership

This skill owns routine-tool operations 14-20 in
`~/.ontocode/skills/ontocode-routine-tools/references/tool-catalog.md`. These
helpers must enforce strict manager-loop ordering, preserve authenticated role
receipts, fail closed on lease ambiguity, and use the coordinator's shared
envelope without replacing an independent role gate with self-review.
