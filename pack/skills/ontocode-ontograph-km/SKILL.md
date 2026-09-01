---
name: ontocode-ontograph-km
description: Ontograph local-only boundary and mandatory librarian workflow for Knowledge Module packages, stores, inventories, curation, validation, import, withdrawal, and KM artifacts. Use for ontocode-rs/ext/ontograph, knowledge_modules, .ontocode/ontograph/km, or .memory-bank/knowledge-hub work.
---

# Ontograph Boundary

- Treat Ontograph as a local-only native extension owned by
  `ontocode-rs/ext/ontograph`.
- Do not register it in app-server threads, shipped/default extension bundles,
  release artifacts, daemon paths, or customer-facing hosts unless an accepted
  ADR changes the boundary.
- Local hardening may continue for bounded read/diagnostic workflows. It does
  not approve host exposure, write/refactor actions, donor-runtime restoration,
  external-checkout or MCP fallbacks, or a second graph backend.

# Knowledge Module Workflow

All Knowledge Module package content, inventories, concept maps, curation,
health, catalog, query, consolidation, healing, validation, import, withdrawal,
and KM-store state must use the librarian chain. This includes
`knowledge_modules/**`, `.ontocode/ontograph/km/**`, and KM-specific artifacts
under `.memory-bank/knowledge-hub/**`.

On the embedded host the model's own Ontograph surface is read-only: only
`km_context` is installed by default. The three agent authoring verbs
(`km_author`, `km_list`, `km_withdraw`) stay behind the default-off
`agent_authored_project_knowledge` feature, so plan KM work through the
librarian chain rather than direct agent authoring calls.

- Route every KM task through `librarian-manager`. The main conversation is the
  only dispatcher: dispatch exactly one `librarian-worker` from the manager's
  bounded prompt, then exactly one `librarian-reviewer` over the fresh artifacts
  and deterministic evidence.
- On `NEEDS_REWORK`, send only the reviewer's bounded fix scope to a
  `librarian-worker`. Count a review round only for a receipt-bound reviewer
  `NEEDS_REWORK`; provider, capacity, timeout, transport, malformed result,
  correction, artifact, receipt, or reviewer-dispatch failures are retries.
  Resume from the latest valid checkpoint. Stop after two `NEEDS_REWORK`
  verdicts with `blocked: librarian review`.
- Do not substitute coder roles, generic workers, explorers, the main
  conversation, or hand-written mutations. If a required librarian capability
  is unavailable, stop with `blocked: capability unavailable`.
- Use real local Ontograph/KM entrypoints, preserve `km.rs` caps and provenance,
  keep drafts distinct from active/gold state, and remain local-only. Never
  hand-edit active index state or claim draft import/promotion.
- Product-source changes to the KM framework remain coder-owned because
  librarian roles may not edit product source, tests, or config. Any associated
  KM package/store operation still requires the librarian chain.
