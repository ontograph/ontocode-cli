---
name: ontocode-memory-bank
description: Project memory-bank startup, authority, plan-template, status-update, archival, and secret-handling rules. Read at the start of every non-trivial repository task.
---

# Memory Bank

Use `.memory-bank/` as the project memory layer.

- At the start of a non-trivial task, read `.memory-bank/MEMORY.md`, then read
  `project_plan-current.md` and `project_pending-tasks.md` only when current plan
  or queue state is needed. Open only active files explicitly linked by them.
- Keep `MEMORY.md` as an active-only router capped at 100 lines. It may link
  authorities and plans whose `manager_loop.status` is `in-progress`, `waiting`,
  or `blocked`; do not add closed plans or routine closeout history.
- Do not glob, bulk-read, or use `.memory-bank/archive/` during ordinary work.
  Read an archived file only for an explicit historical audit or when an active
  plan names that exact path as required evidence.
- Treat `CLAUDE_CODE_APPROACHES_FOR_CODEBASE_TRACKING.md` as the authoritative
  legacy dispatch/status file where an active plan still delegates to it.
  Memory files route context; they do not replace tracking, ADRs, or OntoIndex.
- Use `PROJECT_PLAN_AUTHORING_TEMPLATE.md` when creating, converting,
  normalizing, or reviewing a project plan, task plan, implementation plan,
  tracking plan, task queue, pending list, or other task-list Markdown. Small
  files must still preserve manager tracking, status, dependencies, owner files,
  allowed writes, validation, evidence, blockers, and closeout state.
- Update `project_plan-current.md` and `project_pending-tasks.md` when plan status,
  counts, next steps, or dispatch order changes. Update
  `project_architecture.md` when an owner, flow, or change-home rule changes.
- Add `audit_session-YYYY-MM-DD-*.md` for major closure, verification, or decision
  events. Keep only recent closeouts at the top level. Move older closeouts and
  plans with `manager_loop.status: closed` under `archive/`, preserving relative
  subdirectories, unless a non-DONE task in an active plan still names the file
  in `owner_files` or `allowed_write_set`. Record history in
  `archive/MEMORY_ARCHIVE.md`.
- Move ADRs whose current `## Status` is `Rejected` under `archive/`, preserving
  relative subdirectories. Update active exact-path references and record each
  archived ADR in `archive/MEMORY_ARCHIVE.md`.
- Keep updates factual and compact. Do not paste long logs, full diffs, or raw
  test output.
- Never store secrets, tokens, credentials, cookies, authorization headers,
  keychain paths, or raw private user data.
- When memory conflicts with code, OntoIndex, ADRs, or tracking, verify the
  authoritative source and update the stale memory entry.
