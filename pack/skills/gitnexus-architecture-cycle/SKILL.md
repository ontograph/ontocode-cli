---
name: gitnexus-architecture-cycle
description: Use when reviewing or evolving GitNexus architecture proposals, ADRs, external architecture inspirations, or "review, extend, challenge" loops. The skill forces evidence-first review with GitNexus, separates implemented functionality from speculative ideas, narrows proposals to GitNexus-native core surfaces, and produces implementable integration paths with validation and stop criteria.
---

# GitNexus Architecture Cycle

Use this skill when the user asks to review, challenge, extend, narrow, or turn an architecture idea into reusable GitNexus work. The goal is to stop circular novelty loops and keep only functionality that can be implemented against current GitNexus evidence.

## Core Rule

Do not let an architecture review become a feature wish list. Every kept proposal must map to existing GitNexus code, a plausible integration symbol, validation tests, and a stop condition.

## Required Workflow

1. **Frame the cycle**
   - State the active source: ADR, external repo, audit report, or user proposal.
   - State the intended output: review only, ADR edit, implementation plan, or code change.
   - If the user did not ask for code changes, do not edit production code.

2. **Check repo state**
   - Run `git status --short`.
   - Run local GitNexus status:
     `node /home/er77/_wrk/GitNexus/gitnexus/dist/cli/index.js status`
   - If the index is stale, treat GitNexus query/impact as directional and cross-check current files before making claims.

3. **Use GitNexus first**
   - Query for existing surfaces before proposing new ones.
   - Use `context` for key symbols before naming them as integration points.
   - Use `impact` before recommending edits to existing symbols.
   - Never use `npx gitnexus`; use the local CLI path above.

4. **Classify each idea**
   - **Keep** only if it extends existing GitNexus natural core.
   - **Gate** if it may be valuable but needs evidence, tests, or lower-risk precursor work.
   - **Reject** if it clones an external product, creates a new backend/analyzer, weakens citations, or expands UI/product scope without codebase evidence.

5. **Narrow to implemented functionality**
   Keep proposals only when they can be tied to one of:
   - CLI report/export surfaces;
   - review/diff-impact surfaces;
   - docs/ADR sidecars;
   - evidence diagnostics;
   - indexed graph/process evidence;
   - MCP attachment after lower-risk CLI/export behavior is proven.

6. **Demand integration details**
   For every kept path, name:
   - target file;
   - target symbol or new symbol;
   - expected behavior;
   - why this route is lower risk;
   - required tests;
   - explicit stop condition.

7. **Challenge MCP and UI scope**
   - MCP changes are later-stage unless the impact is low and the behavior is already proven elsewhere.
   - New MCP tools require stronger justification than optional fields on existing results.
   - Web UI/dashboard work is out of scope unless the user explicitly asks for UI implementation and current UI code supports it.

8. **Preserve evidence authority**
   - Every kept behavior must cite source files, symbols, processes, diagnostics, docs sidecars, or review evidence.
   - LLM summaries, if present, are presentation only.
   - Docs-only evidence is advisory unless linked to code evidence.

## Rejection Heuristics

Reject or remove proposals that require:

- replacing GitNexus graph/index storage;
- a parallel generated graph artifact as source of truth;
- LLM-first or multi-agent extraction as the analyzer;
- broad uncited chat/search;
- dashboard-first or UI-heavy scope;
- persona modes before the evidence model is proven;
- auto-update hooks that create hidden generated artifacts;
- implementation without fresh impact checks.

## Output Shape For ADR Edits

When editing an ADR, prefer this structure:

```text
Context
GitNexus Review Evidence
Challenge Findings
Decision
Integration Paths To Implement
Implementation Order
Acceptance Gates
Stop Conditions
```

For each integration path, use:

```text
### N. <Path Name>
- File: <path>
- Symbol(s): <symbols>
- Behavior: <one concrete behavior>
- Why this route: <evidence/risk>
- Tests: <test files/cases>
- Stop: <condition>
```

## Validation

For docs-only changes:

- Check trailing whitespace.
- Run `git diff --check` when the file is tracked. For new untracked docs, use whitespace search if diff-check is noisy because of `/dev/null`.

For code proposals:

- Require fresh GitNexus impact checks before implementation.
- Name focused tests next to each integration path.
- Do not claim tests pass unless actually run in the current worktree.

## Final Response

Report:

- what was challenged;
- what was kept;
- what was rejected;
- GitNexus status and impact caveats;
- exact file changed, if any;
- validation performed.
