---
name: axel-select-uiux-tests
description: Select the smallest authoritative Axel UI/UX test packet for a change, defect, claim, or release gate. Use when deciding between source gates, unit tests, browser-owned chrome tests, native Qt scenarios, persistence readback, platform qualification, and human review.
---
# Select Axel UI/UX Tests

Work from the Axel repository root. Read `.memory-bank/ui-ux-assurance/TEST-ARCHITECTURE.md` first; it overrides proposal-era commands and status in the other UI/UX documents. Use the tracker matrix matching the requested behavior for row-level requirements.

## Resolve the existing packet

Confirm `scripts/uiux/assurance.py` exists, then use it as the deterministic view of existing profile manifests and matrix rows:

```bash
python3 scripts/uiux/assurance.py select --profile ui-smoke
python3 scripts/uiux/assurance.py select --profile ui-complete --matrix-id CI-SEL-001
```

Use the returned owner, status, runner, execution key, evidence level, command, environment, and artifact globs when building the packet. `select` validates and reports existing contracts; it does not execute tests or replace `scripts/run-ui-assurance.sh`. An unknown profile, manifest, or matrix row fails closed.

Use the same CLI for recurring packets outside profile rows:

- Route unscripted native-grid exploration to `$axel-run-qt-ui-scenarios` for a deterministic `explore` plan.
- Route physical platform and human release evidence to `$axel-qualify-ui-evidence` for `platform-packet` and `human-review` workflows.
- Route baseline/current evidence comparison to the owning execution skill or `$axel-debug-uiux-tests`.
- When no spec covers an L2 browser-owned claim, route authoring to `$axel-generate-playwright-specs` (rules from `$axel-author-playwright-specs`) and require a `$axel-review-e2e-specs` pass plus `scripts/check-e2e-spec-smells.sh` before the spec backs a matrix row.

## Route the claim

1. Split compound requests into independently provable claims, then name each claim and the layer that owns its truth. For persistence, name the exact state that must survive reopen; do not let a formula-save scenario stand in for active-cell, selection, view, or preference persistence.
2. Select the lowest evidence level that can prove it:
   - L0: source/build/static gate.
   - L1: owner-layer unit or focused regression.
   - L2: component or browser-route boundary; Playwright is browser-owned chrome only.
   - L3: native grid, real input/focus, visible repaint, cross-surface workflow, or desktop lifecycle.
   - L4: save/reopen, package readback, formula/value parity, or engine equivalence.
   - L5: hardening, performance, physical platform, accessibility, or human release evidence.
3. Add only the next boundary whose behavior is otherwise unproven. Stop when one owner-layer test plus all genuinely required boundaries prove the claim.
4. Route execution:
   - L0-L2 to `$axel-run-owner-ui-tests`.
   - L3 to `$axel-run-qt-ui-scenarios`.
   - L4 to `$axel-verify-ui-persistence`.
   - L5 or an evidence audit to `$axel-qualify-ui-evidence`.
   - A reproducible red result to `$axel-debug-uiux-tests`.
5. Use `compare` only for matching evidence contracts and provenance. Incomparable evidence or provenance mismatch is `HOLD`, not a regression claim.

## Guardrails

- Never assert native-grid pixels, input, selection, focus, or rendering through browser DOM, including through raw Chrome DevTools Protocol on `:59222`. CDP reaches the Qt WebEngine renderer only and stays L2.
- Never use a screenshot as semantic proof or a saved package as visible-rendering proof.
- Keep Qt shell/profile settings, browser preferences, and Calc document state as separate authorities.
- Do not introduce another testing framework unless current architecture documents a measured gap.
- Required unavailable physical or human evidence is `HOLD`, never `PASS`.
- Treat historical consolidation reviews as evidence snapshots, not current status authority.

## Return a test packet

Report each claim, owner, matrix row or scenario, L0-L5 levels, exact runners, fixtures, required environment, expected artifacts, pass/fail/hold criteria, and the first blocking prerequisite. If no existing scenario proves the exact action/state sequence, say so and propose only a bounded extension to the existing declarative scenario harness. Do not execute tests unless requested.

