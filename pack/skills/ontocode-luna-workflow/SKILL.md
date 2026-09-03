---
name: ontocode-luna-workflow
description: Regular-chat Luna delegation workflow for bounded implementation tasks. Use when the user authorizes sub-agent delegation or explicitly requests Luna.
---

# Regular-Chat Luna Workflow

Use this workflow only when the user has authorized sub-agent delegation. It
does not replace the registered coder, librarian, or md-plans chains.

1. Resolve the intended behavior and existing owner locally. Check OntoIndex
   freshness, locate the owner and test surface, verify exact source, and run
   impact analysis for symbols that may change.
2. Use one read-only `explorer` only when owner files, target symbols, the
   existing helper to reuse, or the focused validation command remain unknown.
   The explorer must return those facts without editing or building.
3. Review the discovery result locally. Do not dispatch `luna_worker` while an
   architecture, compatibility, security, public-API, or ownership decision is
   unresolved.
4. Dispatch exactly one file-bounded implementation packet, written in Gherkin:

   ```gherkin
   Scenario: <one concrete outcome>
     Given <verified current state and the target symbols>
     When <the decided change is applied>
     Then <observable result>
     And <focused validation command passes>

   Write set: <exact writable files or modules>
   Non-goals: <prohibited files and expansions>
   Stop when: <scope expansion, conflict, or unresolved decision>
   ```

   Add required evidence and rollback guidance under the scenario when the task
   needs them. `worker` and `luna_worker` reject a packet with no scenario, an
   empty `Then`, or an empty `Write set:`.
5. Do not duplicate Luna's assigned work locally. While it runs, perform only
   useful work with a disjoint write set. Never dispatch overlapping workers.
6. Review Luna's changed files and claimed validation, run final scoped
   verification locally, then close the child agent.

Skip `explorer` when the target and behavior are already known. Keep work local
when discovery blocks the immediate next action, the write set cannot be made
exact, or the task would require Luna to leave its assigned files. Reuse one
Luna child sequentially only for closely related follow-up fixes in the same
ownership scope; use a fresh child when the subsystem or write set changes.

## Agent Addressing

Record the UUID `spawn_agent` returns and address the child by that value in
every later call. The nickname shown in the environment context and the
`task_name` you chose are display labels; passing either yields
`invalid agent id <value>: Error(ParseChar { .. })`.

That error is a malformed argument, not a verdict on the agent. If the UUID is
lost, judge the child from its artifacts on disk rather than probing with
another label.

## Waiting

Wait once, with a deadline sized to the packet, and only when the result blocks
your next step. Repeated short waits burn turns without advancing anything; a
timeout leaves the child running, so a longer deadline costs nothing.

## Path Discipline

A subagent does not inherit your working directory. Use the absolute
`SKILL.md` path exactly as the skills catalog lists it, and pass absolute paths
in the dispatch packet. Relative forms such as `.ontocode/skills/<name>/SKILL.md`
resolve against the child's cwd and fail with `No such file or directory`.
