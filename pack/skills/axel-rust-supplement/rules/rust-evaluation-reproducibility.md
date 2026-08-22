# Make Rust Evaluations Reproducible

Freeze identical inputs and candidate output before hidden evaluation. Rank
valid implementation and correctness before elapsed time.

## Required Checks

- Copy fixtures into isolated candidate directories and record SHA-256 hashes
  before dispatch; verify every candidate receives byte-identical inputs.
- Freeze candidate source before revealing or running hidden tests.
- Run the same visible and hidden command matrix for every candidate.
- Record source hash, toolchain, commands, exit codes, elapsed time, and changed
  files under a deterministic run ID.
- Enforce the allowed write scope. Disqualify invalid or unchanged-source
  submissions regardless of reported speed.
- Score compilation and hidden correctness before performance.

This rule governs comparative evaluation integrity. Use
`measure-before-optimize` for ordinary production performance work.
