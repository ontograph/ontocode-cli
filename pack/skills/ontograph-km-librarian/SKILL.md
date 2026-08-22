---
name: ontograph-km-librarian
description: Route local Ontograph Knowledge Module work through the librarian manager, worker, and reviewer roles. Use for creating, curating, querying, validating, consolidating, healing, importing, withdrawing, or inspecting KM packages and stores.
---

# Ontograph KM Librarian

Route KM work through the existing librarian chain. Do not perform KM package
or store mutations directly.

## Workflow

1. Dispatch `librarian-manager` with the user request, exact project/store
   scope, permitted output paths, and the local-only boundary.
2. Read its `librarian_manager_result`. Dispatch the returned worker prompt to
   exactly one `librarian-worker`.
3. Require the worker to use only wired deterministic KM verbs, normally
   beginning with `health`, and return exact commands, paths, structured
   results, artifacts, blockers, and residual risk.
4. Dispatch exactly one `librarian-reviewer` with the worker result and fresh
   artifacts. Treat deterministic verb output and `km.rs` validation as
   authority, not worker prose.
5. Accept only `APPROVED`. On `NEEDS_REWORK`, send only the reviewer's bounded
   fix scope to a worker. Count a review round only for a receipt-bound
   `NEEDS_REWORK` verdict. Provider, capacity, timeout, transport,
   malformed-result, format-correction, artifact, receipt, and reviewer-dispatch
   failures are dispatch retries; resume from the latest valid checkpoint.
   Stop after two `NEEDS_REWORK` verdicts.

## Boundaries

- Keep Ontograph local-only. Never route through app-server, daemon, shipped
  extension, hosted service, external checkout, or hidden download.
- Never bypass KM caps, validation, provenance, citations, conflict records, or
  active/obsolete state.
- Keep draft artifacts distinct from imported, active, or gold state. Never
  hand-edit the active index.
- Do not substitute coder roles, generic workers, explorers, direct shell/file
  writes, or the main conversation for librarian-owned KM work.
- If a required librarian role, local Ontograph entrypoint, or deterministic KM
  capability is unavailable, stop with `blocked: capability unavailable`.
- Product-source changes to the KM framework remain coder-owned. Any KM package
  or store operation accompanying them still uses this librarian workflow.
