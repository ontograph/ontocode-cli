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
4. Dispatch exactly one file-bounded implementation packet containing:
   - one concrete objective;
   - exact writable files or modules and target symbols;
   - decided behavior and invariants;
   - non-goals and stop conditions;
   - the smallest focused validation commands;
   - required evidence and rollback guidance.
5. Do not duplicate Luna's assigned work locally. While it runs, perform only
   useful work with a disjoint write set. Never dispatch overlapping workers.
6. Review Luna's changed files and claimed validation, run final scoped
   verification locally, then close the child agent.

Skip `explorer` when the target and behavior are already known. Keep work local
when discovery blocks the immediate next action, the write set cannot be made
exact, or the task would require Luna to leave its assigned files. Reuse one
Luna child sequentially only for closely related follow-up fixes in the same
ownership scope; use a fresh child when the subsystem or write set changes.
