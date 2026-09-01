---
name: ontocode-rust
description: Repository Rust conventions, dependency and Bazel synchronization, module sizing, MCP ownership, and crate-local API rules. Use before editing Rust, Cargo, or Bazel-owned files under ontocode-rs.
---

# Rust Conventions

Apply these rules in `ontocode-rs`:

- Current source names may still use the legacy `codex-*` prefix, but the active
  rename goal is to move them to `ontocode-*` as compatibility allows.
- Treat `codex-core` -> `ontocode-core` as an active migration target. Do not
  introduce new `codex-core` references unless a compatibility boundary still
  requires the old name.
- Inline variables into `format!` braces when possible.
- Never add or modify code related to
  `CODEX_SANDBOX_NETWORK_DISABLED_ENV_VAR` or `CODEX_SANDBOX_ENV_VAR`.
- Collapse nested `if` statements, inline `format!` arguments, and use method
  references instead of redundant closures where Clippy supports it.
- Avoid bool or ambiguous `Option` parameters that produce calls such as
  `foo(false)` or `bar(None)`. Prefer enums, named methods, or newtypes.
- When an opaque positional literal remains necessary, add an exact
  `/*param_name*/` comment before booleans, `None`, and numeric literals. The
  name must match the callee signature. String and char literals are exempt
  unless a comment adds real clarity. Use `just argument-comment-lint` when
  local proof is required; CI checks all platforms.
- Prefer exhaustive `match` statements without wildcard arms.
- Add doc comments to new traits explaining their role and implementation
  contract.
- Do not use `#[async_trait]` or `#[allow(async_fn_in_trait)]`. Prefer native
  RPITIT methods with explicit `Send` bounds:
  `fn foo(&self, ...) -> impl std::future::Future<Output = T> + Send;`.
  Implementations may use `async fn` when they satisfy that contract.
- Prefer whole-object equality assertions in tests.
- Do not add general product documentation under `docs/`; app-server API
  documentation follows the app-server skill.
- Prefer private modules and explicitly exported public crate APIs.
- After changing `ConfigToml` or nested config types, run
  `just write-config-schema` to update `ontocode-rs/core/config.schema.json`.
- For MCP tool-call mutation, prefer
  `ontocode-rs/ontocode-mcp/src/connection_manager.rs` and existing abstractions.
  Do not call `reset_client_session` unless incremental checks require it.
- After changing Rust dependencies, run `just bazel-lock-update` and
  `just bazel-lock-check` from the repository root; include
  `MODULE.bazel.lock` changes.
- When adding compile-time file reads such as `include_str!`, `include_bytes!`,
  or `sqlx::migrate!`, update the crate's `BUILD.bazel` compile/build/test data.
- Do not create one-use helper methods.
- Prefer new modules over growing large ones. Target Rust modules under 500
  lines excluding tests. If a file is around 800 lines, add new functionality
  in a new module unless a strong documented reason prevents it. Move related
  tests and docs with extracted ownership. Avoid new standalone methods in
  `tui/src/chatwidget.rs` unless trivial.
- Never kill Rust commands by PID; artifact-lock waits are expected.

## Core Crate

Resist adding new concepts to `ontocode-rs/core`. Before adding code there,
check whether an existing narrower crate owns it or whether a new workspace
crate is justified. Push back on reviews that grow core without necessity.
