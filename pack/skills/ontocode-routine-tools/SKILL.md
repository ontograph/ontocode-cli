---
name: ontocode-routine-tools
description: Route the 40-item Ontocode routine-tool program to existing skill owners and enforce one shared typed result envelope. Use when implementing, reviewing, or assigning routine-tool operations such as session review, repository snapshots, plan-loop guards, agent supervision, verification evidence, or lifecycle audits.
---

# Ontocode Routine Tools

This is a routing and contract coordinator. It does not replace a domain skill
when the user asks for that domain's ordinary work. Use it when the task is to
select, implement, review, or standardize one of the cataloged routine-tool
operations.

## Routing

1. Read [references/tool-catalog.md](references/tool-catalog.md) and find the operation ID or owner skill.
2. Route implementation and execution to that one owner. Do not create a parallel implementation in another skill.
3. Before implementing an operation, read [references/tool-envelope.md](references/tool-envelope.md).
4. Return the shared envelope even for a partial, denied, timed-out, or failed operation.
5. Mark an operation implemented only when its owner has a runnable implementation, fixtures, and documentation. Routing ownership alone is not implementation.

If the user names an existing domain skill, use that skill directly and apply the
catalog only for routine-tool contract requirements.

## Ownership Rules

- One operation has one primary owner.
- Another skill may consume an owner's result, but must not duplicate its parser or mutation logic.
- Domain skills may add fields to `data`, but must not rename or omit shared envelope fields.
- Mutating operations default to dry run and require explicit approval for execution.
- Manager-loop, receipt, lease, and freshness operations must fail closed; they never bypass role gates or invent authenticated state.

## Current Status

The catalog records ownership and implementation status. Operations in the
`CONTRACTED` state have ownership and contract requirements assigned, but may not
yet have a runtime tool or owner script. Do not represent `CONTRACTED` as
callable product functionality.
