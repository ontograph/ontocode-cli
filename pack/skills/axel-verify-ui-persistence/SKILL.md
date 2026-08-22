---
name: axel-verify-ui-persistence
description: Verify Axel UI mutations through save, clean close, reopen, and the correct structured oracle. Use for cell edits, formulas, formatting, selection/view state, preferences, and workbook round-trip claims.
---
# Verify Axel UI Persistence

Read `.memory-bank/ui-ux-assurance/TEST-ARCHITECTURE.md` and `trackers/UI-UX-SETTINGS-PERSISTENCE-MATRIX.md`. Name the authority and the exact state that must persist before executing. A scenario that persists a formula does not prove active-cell, selection, view, formatting, or preference persistence.

For a profile or persistence matrix row, confirm `scripts/uiux/assurance.py` exists and run `python3 scripts/uiux/assurance.py preflight --profile <profile> --matrix-id <matrix-id>` before execution. This checks the existing contract and prerequisites but does not perform the mutation, save, close, reopen, or readback.

## Separate authorities

- Qt shell/profile settings belong to the desktop profile and launcher.
- Browser preferences belong to the stable WebEngine origin and browser store.
- Calc document/view state belongs to the workbook package and application engine.

Never invent a generic settings service or use one authority to prove another.

## Required chain

1. Copy the mutable fixture and record its hash, format, source revision, binary, engine, locale, and profile identity.
2. Confirm the scenario performs the exact mutation and reopen assertion requested. If it does not, stop and propose a bounded extension to the existing declarative scenario harness.
3. Perform the real UI mutation through the owning scenario.
4. Capture live semantic state and visible state when the claim is visual.
5. Save successfully, close cleanly, and prove document release.
6. Reopen in a fresh process or the exact restart/profile mode required by the matrix.
7. Reassert the visible/runtime state.
8. Use structured readback for the named claim: package structure, cell/formula value, style, view state, or engine parity.
9. Qualify a generated profile summary, cell-interaction bundle, or visual manifest with `python3 scripts/uiux/assurance.py verify <evidence>`. Treat exit `0` as `PASS`, `1` as `FAIL`, and `2` as `HOLD`; validate-only evidence remains `HOLD`.

Current differential helpers include:

```bash
scripts/formula-differential.py verify
scripts/check-workbook-roundtrip.py --corpus build-scratch/formula-corpus
scripts/compare-xlsx-probe-paths.py --corpus build-scratch/formula-corpus
scripts/check-rust-oracle-parity.sh
```

Use only the helper matching the claim. Structural equality is not value equality; a saved package is not visual proof; screenshots are not persistence proof.

CLI verification authenticates the supported evidence contract and required artifacts. It does not replace the claim-specific save-close-reopen chain or its structured oracle.

## Verdict

Return exact commands/exits, pre/post hashes, action and save records, close/reopen identities, visible artifacts, structured readback, and `PASS`, `FAIL`, or `HOLD`. Fail on mutation of a committed fixture, save/reopen mismatch, wrong authority, crash, fallback, or unclean close.

