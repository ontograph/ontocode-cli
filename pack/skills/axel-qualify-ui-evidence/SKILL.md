---
name: axel-qualify-ui-evidence
description: Audit Axel UI/UX evidence and issue PASS, FAIL, or HOLD. Use for automation profiles, matrix coverage, native screenshots, platform qualification, accessibility rows, and two-reviewer human UX review.
---
# Qualify Axel UI/UX Evidence

Read `.memory-bank/ui-ux-assurance/TEST-ARCHITECTURE.md`, then the relevant matrix or human-review protocol. Treat implementation plans as status authority and consolidation reviews as historical evidence.

## Verify supported evidence contracts

From the Axel repository root, confirm `scripts/uiux/assurance.py` exists and run:

```bash
python3 scripts/uiux/assurance.py verify <summary-or-bundle-or-jsonl>
```

The command validates profile summaries, cell-interaction bundles, visual manifests, platform packets, and human-review records through their repository contracts. Exit `0` is `PASS`, `1` is `FAIL`, and `2` is `HOLD`. A validate-only profile summary is always `HOLD`, never runtime proof. Profile verification is scoped to runnable automation; its `PASS` does not clear required physical, accessibility, platform, or human-review gates.

## Audit the packet

Check that it identifies:

- Claim, matrix row/scenario, owner layer, and required evidence level.
- Exact HEAD, binary/assets, fixture hash/format, environment, locale, theme, scale/DPR, and profile.
- Exact commands, exit codes, scenario/action/state records, launcher logs, and artifact paths.
- Semantic state for behavior, visible artifact for visual claims, clean close, and structured readback for persistence.
- Browser-grid retirement and absence of crash, fallback, blank/red grid, or `Unspecified Application Error`.
- Every required automation row once for `ui-complete`; skips of runnable required rows fail closed.

## Physical and human gates

Capture a platform packet only from evidence that already passes its underlying verifier:

```bash
python3 scripts/uiux/assurance.py platform-packet capture \
  --matrix-id <id> --variant <variant> --evidence <evidence> \
  --capability <capability> --host-manifest <host.json> \
  --output <platform-packet.json>
python3 scripts/uiux/assurance.py platform-packet verify <platform-packet.json>
```

The packet hashes its referenced evidence. Physical PASS requires `physical=true`, at least one capability, and complete host, OS, session, QPA, display, GPU, monitor, input-device, locale, IME, theme, scale, and accessibility identity. Missing identity is `HOLD`; contradictory synthetic or emulated identity is `FAIL`.

Initialize human review records without inventing judgments or signatures:

```bash
python3 scripts/uiux/assurance.py human-review init \
  --candidate-sha <sha> --reviewer-id <id> --output <review.json>
python3 scripts/uiux/assurance.py human-review verify <review.json>
python3 scripts/uiux/assurance.py human-review merge \
  <review-a.json> <review-b.json> --output <merged.json>
```

`init` intentionally returns `2/HOLD`. Reviewers must supply the fixed action observations, artifacts, verdicts, platform, source/executable/assets/fixture hashes, findings, and their own signature state. Merge requires distinct reviewers and matching candidate, protocol, and provenance. Observation or verdict disagreement remains `HOLD` without a real adjudication record; severity 1 or 2 findings fail.

- Emulation cannot promote physical Wayland, touchpad, IME, scaling/theme, forced-colors, or Orca rows.
- Physical evidence must name the real host, OS/session/QPA, GPU/monitor/input/accessibility stack, scale, locale/IME, hashes, screenshots, semantic result, and clean close.
- Human completion requires two real independent identity-bearing reviewers running the unchanged bounded protocol. Keep automated evidence separate, compare observations, and lifecycle every negative finding.
- If a required host, capability, identity, or second reviewer is absent, return `HOLD`; never synthesize a result.

## Verdict rules

- `PASS`: all required evidence is present and every required runnable assertion passes.
- `FAIL`: authoritative evidence disproves the claim or a required runnable gate fails.
- `HOLD`: required physical, human, environment, fixture, or provenance evidence is unavailable.

List missing evidence and the exact next gate. A feature is covered only when its matrix row has a runnable owner-layer test plus every required boundary oracle; aggregate test counts are insufficient.

