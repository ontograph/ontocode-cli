# Vendored axel-chrome-devtools-testing

Chrome DevTools testing skill vendored per the monorepo external-dependency
policy in `CLAUDE.md`.

Upstream: https://github.com/justfinethanku/cc_chrome_devtools_mcp_skill
License: MIT (see `LICENSE`)
Pinned ref: `96840c73dc36c420e57341180013889e21d5932e` (`main`, vendored 2026-08-22)

## Local Changes

Kept minimal so the vendored skill stays diffable against upstream:

1. Renamed the `SKILL.md` frontmatter `name:` from
   `cc_chrome_devtools_mcp_skill` to `axel-chrome-devtools-testing` and added
   `vendored_from`, `vendored_ref`, and `vendored_on` provenance keys.
2. Added an "Axel Scope" section: applies to the `browser/` web client only,
   not the Qt desktop client; repeatable regressions stay in the committed
   Playwright suite; isolated mode is required so runs never touch the user's
   logged-in Chrome profile.
3. Upstream `README.md` installation sections are Claude Code-specific
   (`/plugin` commands); in this repository the skill is deployed through
   `scripts/sync-skills.sh` and drives the already-mounted `chrome_devtools`
   MCP tools.
4. Removed upstream `.claude-plugin/` (Claude Code plugin marketplace
   manifest) and upstream `.gitignore`; both are upstream distribution
   plumbing, not skill content.
5. Regenerated the tool contract against the mounted `chrome_devtools` MCP
   surface (2026-08-22, 28 tools): `TOOLS.md` rewritten as a surface-verified
   reference (adds `lighthouse_audit`, `take_heapsnapshot`, `type_text`;
   fixes `pageId` vs `pageIdx`; documents the merged `emulate` tool);
   `SKILL.md` tool lists, use-case parameters, and Quick Start updated the
   same way, plus a stale-UID re-snapshot rule, `./run.sh` serve instructions,
   a `$faster-chrome-devtools-skill` fallback note, and evidence `filePath`
   guidance. Upstream documented chrome-devtools-mcp v0.5.1; `WORKFLOWS.md`
   keeps the upstream narratives behind an explicit version-drift banner that
   defers to `TOOLS.md`.

## Updating

Refresh only from the pinned upstream repository, reapply the renames and the
Axel Scope section above, and update the provenance keys plus this file.
