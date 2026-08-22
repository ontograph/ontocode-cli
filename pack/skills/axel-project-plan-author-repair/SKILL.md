---
name: axel-project-plan-author-repair
description: Author, review, or repair schema-valid Axel project-plan Markdown using the repository authoring rule, current source and OntoIndex evidence, and project_plan_validate. Use for requests to create an Axel refactor or migration plan, fix validator failures, challenge plan assumptions, update a plan document, or make plan tasks dispatch-ready. Do not use to execute an already-valid plan; use axel-plan-autopilot for execution.
---

# Axel Project Plan Author Repair

Produce a dispatch-ready plan grounded in the live Axel repository. Treat the repository rule and validator as authority; do not reconstruct their schema from memory.

## Workflow

1. Confirm the Axel repository root and read its `AGENTS.md` instructions.
2. Read `docs/refactor/project-plan-authoring-rule.md` in full before creating or changing a plan. If repairing an existing plan, read the entire plan and preserve valid status, evidence, and unrelated user edits.
3. Identify every architectural, path, symbol, command, dependency, and ownership claim that controls the proposed work.
4. Challenge those claims against current source and a fresh OntoIndex graph:
   - Check graph freshness before relying on it; coordinate and refresh once when stale.
   - Use semantic search to find the owning flow, inspect relevant symbol context, and verify claims directly in source.
   - Mark claims provisional when current evidence cannot resolve them. Do not invent paths, symbols, test targets, or runtime seams.
5. Apply the smallest useful plan change. Reject speculative tasks and parallel architecture that do not deliver current spreadsheet functionality, concrete shrink, or measured quality improvement.
6. Follow the authoring rule exactly. Pay particular attention to:
   - `manager_loop`, `active_next_task`, task status, dependency order, and valid classification values.
   - Owner and reviewer, `owner_files`, `allowed_write_set`, non-goals, validation, rollback, stop conditions, and closeout evidence.
   - `outcome_hypothesis`, `change_mode`, `agent_class`, and the exact Required Traceability table shape.
   - A stop condition closes a task as `BLOCKED` or `HOLD`, never `DONE`.
7. Run `project_plan_validate` as soon as the first complete structure exists. Repair one reported structural cause at a time and rerun until it passes.
8. Run the narrow Markdown or changed-file checks required by `AGENTS.md`. For a new untracked Markdown file, use the repository's no-index whitespace check rule.

## Repair Rules

- Repair validator failures without silently redesigning valid task content.
- Keep `owner_files` within the declared write set and make task boundaries conflict-safe.
- Use reproducible commands and expected evidence, not statements that tests "should" pass.
- Keep rollback operational and measurable. For engine swaps, preserve the old path until the replacement has held as default and include golden-oracle recording before replacement.
- Do not add `cargo miri` as a default gate on Axel's stable toolchain.
- Do not dispatch tasks from an invalid plan.

## Output

Report:

- The plan path and whether it was created, reviewed, or repaired.
- Source or graph assumptions confirmed, contradicted, or left provisional.
- `project_plan_validate` result and any remaining repository checks.
- The exact blocker when validation or source grounding cannot complete.

Hand execution of a validated plan to `axel-plan-autopilot`.
