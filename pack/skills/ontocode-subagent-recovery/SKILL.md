---
name: ontocode-subagent-recovery
description: Diagnose and recover failed or interrupted Ontocode sub-agent dispatches without losing task integrity. Use when an agent is explicitly interrupted, returns null, errors on provider, authentication, quota, transport, result schema, or receipt validation, exhausts context or tokens, or needs an approved model fallback and bounded retry.
---

# Ontocode Subagent Recovery

Recover one failed dispatch without treating infrastructure failure as task completion.

## Workflow

1. Capture the task ID, agent ID, role, requested model, dispatch revision, receipt state, and exact terminal error. Do not infer success from an empty or null result.
2. Classify the failure:
   - `AUTH`: no credentials or authentication unavailable.
   - `QUOTA`: usage or capacity limit reached.
   - `PROVIDER`: unknown model, endpoint mismatch, unsupported protocol, or invalid provider response.
   - `TRANSPORT`: disconnect, timeout, or incomplete stream.
   - `NULL_RESULT`: task ended without a usable role result.
   - `SCHEMA`: contradictory or invalid role-result fields.
   - `RECEIPT`: stale revision, missing receipt, or failed receipt authentication.
   - `BUDGET`: token, context, or low-yield loop limit reached.
   - `INTERRUPTED`: the user, parent, or supervisor explicitly stopped the turn; do not misclassify it as transport failure.
3. Preserve the original task scope and manager-loop state. Never hand-edit a durable lease, revision, or receipt.
4. For `INTERRUPTED`, inspect current workspace state and capture the last verified evidence before deciding whether work remains. Do not retry merely because the turn stopped.
5. Apply the smallest valid recovery:
   - Correct a schema contradiction once using the validator's exact fields.
   - Retry a transient transport failure once when no authenticated result exists.
   - Use the next currently approved model after auth, quota, provider, or repeated transport failure. Respect same-day cooldown and repository model policy.
   - Return receipt or revision failures to the owning manager tool; do not fabricate replacement evidence.
   - Resume an interrupted task only when its scope remains open and no terminal result exists. Reuse the existing agent when supported; otherwise dispatch one bounded continuation under repository policy.
6. Keep retries bounded: one same-model transient retry, then one approved fallback unless the repository policy is stricter. Stop on repeated failure or unavailable approved models.
7. Enforce the task's token and time budget. Stop low-yield loops instead of repeatedly resending large context.
8. Accept completion only from a valid role result and authenticated receipt where required.

## Safety Rules

- Do not change task scope, write set, acceptance criteria, or role merely to obtain a pass.
- Do not reuse partial edits blindly after an agent failure; inspect current workspace state first.
- Do not report an infrastructure death as `BLOCKED` project work unless the plan's recorded stop condition requires that classification.
- Do not retry terminal auth, quota, or unsupported-model failures on the same model.
- Do not expose credentials or reproduce sensitive provider payloads.

## Output

Report the failure class, original dispatch identity, recovery attempted, model transition if any, retry count, receipt status, current task state, and exact remaining blocker. Distinguish recovered task evidence from infrastructure diagnostics.

For `INTERRUPTED`, also emit a compact resume packet: task and agent identity,
scope and write set, last verified evidence, current workspace state, receipt or
lease state, remaining work, and the single permitted resume action.

## Routine Tool Ownership

This skill owns routine-tool operations 23-24 in
`~/.ontocode/skills/ontocode-routine-tools/references/tool-catalog.md`. Recovery
routing and dispatch-packet generation must remain evidence-backed, scoped, and
compatible with the coordinator's shared envelope.
