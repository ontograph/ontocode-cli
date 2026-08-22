---
name: upstream-codex-sync
description: Compare this Ontocode fork against upstream https://github.com/openai/codex, identify new upstream commits/features/fixes, decide what should be merged, and safely port or cherry-pick upstream changes into the current fork. Use when the user asks to check upstream Codex, sync from openai/codex, merge new upstream work, review what changed upstream, or keep the fork current.
---

# Upstream Codex Sync

Use this skill to inspect upstream `openai/codex`, classify useful changes, and merge them into this fork without undoing local Ontocode migration work.

## Rules

- Prefer a reviewable branch or sibling worktree for upstream sync work.
- Do not run destructive commands such as `git reset --hard` or `git checkout --` unless the user explicitly asks.
- Do not implement upstream sync in a dirty checkout. Review mode may inspect a dirty checkout, but implementation mode must use a clean branch or sibling worktree.
- Preserve Ontocode rename decisions. Map upstream legacy paths and names onto local targets when needed:
  - `codex-rs/` -> `ontocode-rs/`
  - `codex-cli/` -> `ontocode-cli/`
  - Rust package/binary targets should prefer `ontocode-*` / `ontocode`
- Keep upstream public compatibility names only where the fork already preserves them intentionally, such as npm `@openai/codex` compatibility.
- Confirm OntoIndex is reachable and fresh before edits that depend on code intelligence. Stop if OntoIndex MCP is unreachable.
- Use OntoIndex before editing code symbols. Refresh OntoIndex after accepted sync slices.
- Run scoped verification with `CARGO_BUILD_JOBS=8` for Rust builds/tests.

## Workflow

1. Choose mode:

- Review mode: fetch upstream, classify changes, and produce a merge plan. Do not edit files.
- Implementation mode: apply one selected upstream slice. Use a clean branch or sibling worktree.

2. Inspect local state:

```bash
git status --short
git branch --show-current
git remote -v
```

If the worktree is dirty, do one of these:

- For review only: continue without edits.
- For implementation: create a sibling worktree or ask the user to checkpoint local work.

```bash
git worktree add ../ontocode-upstream-sync-$(date +%Y%m%d) HEAD
```

3. Classify remotes before fetching:

```bash
git remote -v
git remote get-url origin
```

Identify:

- upstream OpenAI remote: normally `https://github.com/openai/codex.git`
- fork remote: the writable Ontocode fork, if configured
- missing fork remote: report before implementation if only upstream OpenAI is configured

Then add or update the OpenAI upstream remote only if no existing remote already points at it:

```bash
git remote get-url upstream-openai >/dev/null 2>&1 || git remote add upstream-openai https://github.com/openai/codex.git
git fetch upstream-openai --tags
```

If `origin` already points at OpenAI upstream, use `origin/main` as the upstream ref instead of adding a duplicate remote.

4. Confirm OntoIndex readiness before implementation edits:

```bash
ontoindex status
```

If OntoIndex MCP or CLI is unavailable, stop and report repair steps before editing.

5. Find what upstream has that this fork does not:

```bash
git merge-base HEAD upstream-openai/main
git log --oneline --decorate --cherry --right-only HEAD...upstream-openai/main
git diff --stat HEAD...upstream-openai/main
git range-diff HEAD...upstream-openai/main
```

Use `git show --name-status <sha>` for specific commits. Group upstream changes by area:

- security or correctness fixes
- build/release/tooling fixes
- dependency updates
- app-server/protocol/schema changes
- CLI/TUI user-visible changes
- provider/auth/MCP/shell/runtime changes
- docs/tests only
- possibly already ported under Ontocode names

6. Decide merge strategy:

- Use cherry-pick for small independent commits.
- Use manual porting for commits touching renamed paths or large local divergence.
- Avoid raw merge when upstream still uses `codex-rs/` or `codex-cli/` paths that this fork already renamed.
- Do not cherry-pick commits that touch `codex-rs/`, `codex-cli/`, package identity, generated schema paths, release packaging, or persisted state until path mapping and compatibility impact are reviewed.
- Skip upstream changes that only revert or conflict with accepted Ontocode identity migration unless the user explicitly wants upstream parity over fork identity.

7. Before editing code symbols, run OntoIndex impact for affected symbols/modules. If risk is HIGH or CRITICAL, report it and narrow the slice.

8. Apply one small slice at a time.

Cherry-pick only when the commit does not touch renamed roots and the diff is expected to apply to current paths:

```bash
git cherry-pick -n <sha>
```

If paths conflict because of local renames, abort the cherry-pick and port manually:

```bash
git cherry-pick --abort
git show --stat <sha>
git show <sha> -- <upstream-path>
```

Then edit the corresponding local path, usually under `ontocode-rs/` or `ontocode-cli/`.

9. Verify the slice by touched surface:

- For Rust formatting: `cd ontocode-rs && CARGO_BUILD_JOBS=8 just fmt`
- For changed Rust crates: `cd ontocode-rs && CARGO_BUILD_JOBS=8 just test -p <package>`
- For CLI build: `cd ontocode-rs && CARGO_BUILD_JOBS=8 cargo build -p ontocode-cli --bin ontocode`
- For npm wrapper changes: `corepack pnpm list --depth -1` and a staging smoke if relevant:

```bash
python3 ontocode-cli/scripts/build_npm_package.py --version 0.0.0-test --staging-dir tmp/ontocode-cli-stage-smoke
rm -rf tmp/ontocode-cli-stage-smoke
```

- For Python SDK changes: run the narrow `uv run --frozen --project sdk/python ...` command used by nearby tests or scripts.
- For TypeScript SDK changes: run the package's existing `pnpm`/test command through `corepack pnpm`.
- For app-server protocol/schema changes: run `cd ontocode-rs && CARGO_BUILD_JOBS=8 just write-app-server-schema` and `just test -p ontocode-app-server-protocol`.
- For dependency changes: run the repo-required Bazel lock update/check commands.
- For docs or memory-bank moves: run link/path checks and `git diff --check`.

10. Refresh OntoIndex after an accepted implementation slice:

```bash
ontoindex analyze --skills --skip-agents-md
ontoindex status
```

## Output

When reporting, include:

- upstream range inspected
- selected commits or areas
- skipped commits with reason
- files changed
- verification commands run
- remaining conflicts or blocked decisions

For build/binary tasks, include exact user-facing command, working directory, and artifact path.
