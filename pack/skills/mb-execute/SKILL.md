---
name: mb-execute
description: >
  Execute one TASK-* with a reproducible protocol, quality gates, and Memory Bank sync. Use the bounded issue-fix loop for Axel Rust/C++ fixes with a focused failing command.
---

# mb-execute — Execution loop (code → gates → verify → light MB-SYNC)

- **What it does:** implements one scoped task with reproducible verification and minimal protocol overhead.
- **Use it when:** `TASK-*` already exists and you want a clean, resumable implementation flow.
- **Input:** `TASK_ID` plus links to the driving feature, requirement, and backlog entry.
- **Output:** code changes, protocol artifacts, verification inputs, and synchronized Memory Bank state.

## Goal
Turn a backlog item into a **reproducible, verifiable code change**:
- bounded implementation
- deterministic gates
- recorded verification
- lightweight Memory Bank sync

## Inputs
Orchestrator must provide:
- `TASK_ID` (e.g. `TASK-123`)
- link to the driving spec(s):
  - `.memory-bank/features/FT-*/...` and/or
  - `.memory-bank/requirements.md` (REQ IDs)
  - `.memory-bank/tasks/backlog.md` entry
  - related ADR docs under `docs/` if the task depends on architecture decisions (`docs/adr/**/*.md`, `docs/adrs/**/*.md`)

## Required artifacts
Always keep:
- `.protocols/<TASK_ID>/progress.md`
- `.protocols/<TASK_ID>/verification.md`
- `.tasks/<TASK_ID>/`

Create only when needed:
- `.protocols/<TASK_ID>/context.md` (complex scope/onboarding)
- `.protocols/<TASK_ID>/plan.md` (multi-step or high-risk changes)
- `.protocols/<TASK_ID>/handoff.md` (paused or transferred work)

## Process

### 1) Prime context (cheap-to-prime)
Read only what you need:
- `AGENTS.md`
- `.memory-bank/index.md`
- the specific `FT-*` / `REQ-*` relevant to `TASK_ID`
- relevant ADR docs under `docs/` when the task depends on architectural constraints

### 2) Write a task brief (keep it lightweight)
Before touching code, ensure there is a short scoped brief in either:
- `.protocols/<TASK_ID>/progress.md` (default), or
- `.protocols/<TASK_ID>/plan.md` (optional for non-trivial tasks)

Include:
- goal + non-goals
- touched files/modules (hypotheses allowed, mark as such)
- constraints/invariants
- quality gates to run

### 3) Implementation (fan-out allowed)
If work is non-trivial:
- spawn subagents (max depth=2)
- give each worker a narrow scope (≤3–5 files)
- workers write details to `.tasks/<TASK_ID>/...`

Recommended role split (optional):
- **Implementer**: changes code/tests — `./agents/shared-implementer.md`
- **Secretary**: keeps `progress.md` updated — `./agents/shared-secretary.md`

### 3.1) Fresh Codex session per task (optional, clean context)
If you want the implementation to run in a **fresh Codex session** (clean context), run it via shell:

```bash
codex exec --ephemeral --full-auto -m gpt-5.2-high \
  'TASK_ID=TASK-123. Read AGENTS.md and .protocols/TASK-123/progress.md. If context/plan files exist, read them too. Implement only scoped changes. Write report to .tasks/TASK-123/TASK-123-S-IMPL-final-report-code-01.md. Update .protocols/TASK-123/progress.md.'
```

Then run verification in another fresh session:

```bash
codex exec --ephemeral --full-auto -m gpt-5.2-high \
  'TASK_ID=TASK-123. Read .protocols/TASK-123/progress.md and acceptance criteria. If context/plan files exist, use them. Fill .protocols/TASK-123/verification.md and put evidence in .tasks/TASK-123/. VERDICT: PASS/FAIL.'
```

### 3.2) Fresh Claude session per task (required when working in Claude Code)
If you are running inside **Claude Code**, enforce clean context by executing each `TASK-XXX` in a **fresh Claude session**:

Run implementer in a fresh session via shell (new session, clean context):

```bash
claude -p --no-session-persistence --permission-mode acceptEdits --model opus \
  'TASK_ID=TASK-123. Read AGENTS.md, .protocols/TASK-123/progress.md, and acceptance criteria docs. If context/plan files exist, use them. Implement only scoped changes. Update .protocols/TASK-123/progress.md. Write report to .tasks/TASK-123/TASK-123-S-IMPL-final-report-code-01.md.'
```

Then run verifier in another fresh session:

```bash
claude -p --no-session-persistence --permission-mode acceptEdits --model opus \
  'TASK_ID=TASK-123. Read .protocols/TASK-123/progress.md + acceptance criteria docs. If context/plan files exist, use them. Fill .protocols/TASK-123/verification.md and store evidence in .tasks/TASK-123/. VERDICT: PASS/FAIL/NEEDS-CLARIFICATION.'
```

### 3.3) Sequencing rule (dependencies)
- If tasks are **independent** (no dependency and no shared files), you MAY run them in separate clean sessions in parallel.
- If tasks have a **dependency chain** (TASK-B requires outputs from TASK-A), run them **sequentially**, one after another, each in its own clean session.
- If tasks touch the same files, treat them as dependent unless you isolate via worktrees/branches.

### 4) Quality gates (deterministic)
Run the repo’s canonical gates (from `AGENTS.md`). Minimum:
- lint / typecheck
- unit tests
- integration/e2e when relevant

For Axel Rust, C++, Qt, or LibreOffice work, read
`references/axel-native-iteration.md` before running native commands. Use its
focused target, profile-preservation, ccache, and job-routing rules; do not
invent a second native build procedure in the task notes.

If any gate is flaky, record it in `progress.md` and (if needed) file a bug doc in `.memory-bank/bugs/`.

### 5) Verification handoff
Do not self-validate beyond sanity checks.
- Hand off to `mb-verify` (fresh-ish context) to fill `verification.md`.

### 6) MB-SYNC (required, lightweight, last step)
After verification is complete:
- update `.memory-bank/tasks/backlog.md`
- append `.memory-bank/changelog.md`
- update extra `.memory-bank/` docs only when behavior/architecture actually changed
- mark the backlog task with the correct state (`done` / `failed` / `blocked`)

## Definition of done
- Required protocol files exist (`progress.md`, `verification.md`).
- Gates pass (or failures are explicitly recorded + bug filed).
- `verification.md` contains evidence links to `.tasks/<TASK_ID>/`.
- Memory Bank is synced + changelog updated.
