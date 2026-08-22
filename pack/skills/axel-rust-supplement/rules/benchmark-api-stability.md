# Preserve Benchmark Public-API Stability

Comparative Rust work is invalid when a candidate widens the allowed public
surface to make implementation easier.

## Required Checks

- Freeze the allowed public items before dispatch: structs, enums, traits,
  functions, methods, fields, visibility, generic bounds, and error types.
- Keep helper functions private unless the task contract explicitly allows a new
  public item.
- Diff each candidate against the frozen API baseline and reject added,
  removed, renamed, retyped, or newly visible items.
- Install hidden tests only after candidate source is frozen; verify every
  candidate receives byte-identical tests.
- Score API compliance, compilation, and hidden correctness before elapsed time.

Use `rust-evaluation-reproducibility` for fixture identity, command matrix, and
run evidence.
