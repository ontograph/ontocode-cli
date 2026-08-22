---
name: ontocode-architecture
description: Existing-owner reuse, public-surface gates, security/context constraints, third-party migration, and Ontocode rename policy. Use before provider, auth, MCP, hooks, shell, session/context, diagnostics, external-agent import, donor-code migration, or rename work.
---

# Architecture Reuse

Treat a proposed change as invalid until it passes both checks:

1. It adds real functionality, behavior, safety, compatibility, or operational
   value rather than cosmetic churn or duplicate plumbing.
2. It extends the existing solution and owner instead of creating a parallel
   owner or side stack.

If either check fails, inline the change into the existing owner, redesign it,
or drop it. When both pass, implement the full requested scope in the existing
owner when reasonably possible; do not shrink valid work solely to reduce the
diff or validation effort.

- Reuse existing architecture. Do not create a second provider factory,
  provider registry, model catalog, runtime stream abstraction, capability
  resolver, OAuth parser, credential store, redactor, MCP status pipeline, hook
  matcher/registry, policy evaluator, shell permission parser/launcher, context
  injection path, or external-agent import service.
- Use OntoIndex context on the target owner and impact before editing symbols.
- Extend the existing owner: provider work belongs in `model-provider`; OAuth
  persistence in auth/login or provider auth; MCP work in `rmcp-client`,
  `codex-mcp`, or existing processors; hook work in `hooks`; shell/sandbox work
  beside existing runtime modules; context work in session/context modules;
  external-agent imports in existing migration/import services.
- Add a module only when the current owner would become too large or mix
  unrelated concepts. The module must plug into the existing owner.
- Prefer existing test harnesses and fixtures. Document why a new helper is
  necessary when existing helpers cannot express the case.
- Public config keys, app-server APIs, SDK behavior, schemas, dashboards,
  wizards, support bundles, and export paths require an ADR and compatibility
  tests before implementation.
- Security-sensitive diagnostics must reuse shared sanitization/redaction.
  Tests must fail if tokens, cookies, authorization headers, keychain paths, or
  raw credentials appear.
- Model-context injection must use bounded context fragments with hard caps.

## Third-Party Migration

The project goal is to remove runtime dependencies on third-party tools and
upstream projects. Donor repositories are source evidence only unless this
repository adopts the minimum required code.

- Do not add required runtime dependencies on external CLIs, daemons, packages,
  hosted services, checkouts, or release streams.
- Adopt required legacy code into a repo-owned plugin or existing backend owner.
  The maintained path must not shell out to an external checkout, depend on the
  donor remaining available, or hide a normal-use download step.
- Keep the plugin boundary unless an ADR assigns the functionality to an
  existing native owner. Do not copy donor runtimes into `ontocode-core`.
- Remove donor features that require external accounts, telemetry, update
  channels, background services, broad shell execution, or unrelated package
  managers unless an ADR approves them.
- Preserve required compatibility shims and provenance while making the
  Ontocode-owned path authoritative.

## Rename Policy

- `Ontocode` / `ontocode` is the target identity. Prefer it for crates, modules,
  types, functions, commands, package metadata, docs, and user-visible surfaces
  unless compatibility requires the old name.
- The active goal includes `codex-core` -> `ontocode-core`.
- Never rename code objects with broad find-and-replace. Use OntoIndex
  rename/impact analysis and preserve compatibility for integrations, persisted
  state, config keys, CLI commands, APIs, package names, and rollout data.
- Before removing an old-name alias, document the migration path and verify the
  affected execution flows with OntoIndex change detection.
