# Axel Native Build Triage

Use this reference only in the Axel repository.

## Classify The First Owning Error

Capture the exact failing command and the first substantive error. Classify it
before changing source:

| Class | Check first |
|---|---|
| Test assertion | Exact assertion, expected versus actual value, and whether the intended product path was reached |
| Patch or task scope | Allowed write set, expected files, patch conflict, and unrelated dirty work; do not classify these as product failures |
| Tool contract or policy | Missing/denied tool, hook or path block, and whether the compiler or test process ever started |
| Rust compile/test | Owning `Cargo.toml`, package/feature selection, and the focused Cargo command |
| C ABI or Rust/C++ boundary | Export declaration, status/error conversion, pointer ownership, allocator symmetry, and the direct C++ caller |
| Automake/native linkage | Translation unit membership, library ordering, generated configure state, and the unresolved symbol's actual owner |
| Qt compile/link | Qt-enabled build tree, Qt include paths, moc/generated state, and `qt/Makefile.am` wiring |
| Compile database | Whether merged data contains the changed file and whether the winning entry came from a Qt-enabled or server tree |
| LibreOffice | Active `runtime` versus `tiled-test` profile, requested gbuild target, preserved workdir/instdir, and shared ccache settings |
| Package/runtime | Packaged dependency and loader evidence; do not infer package correctness from the developer host |

Ignore downstream cascades until the first owning error is explained. Do not
start with a clean or full build: reproduce with the smallest Cargo package,
translation unit, gbuild target, or named test that still fails.

If the command never reached the compiler, linker, test binary, or application,
route the failure to `ontocode-tool-contract-preflight`. A patch conflict or
write-set violation requires task correction, not a product-code hypothesis.
Only enter native compile/link diagnosis after those classes are excluded.

## Routing

- If the failure is readiness, ownership, rollback, or engine-selection policy,
  route to `axel-rust-engine-seam-audit`.
- If a long command is already running, route to
  `axel-background-job-watch`.
- If a concrete Ontocode runtime, MCP, stream, or aborted-turn incident remains
  after preflight, route it to `session-issue-diagnostics`.
- If the compile database is absent, generate it only from existing configured
  trees; do not configure or build merely to make diagnosis look green.
- After the root cause is fixed, hand source qualification to `mb-verify`.
