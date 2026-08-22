# Preserve Semantic Boundary Values

Equal Rust representations do not make values interchangeable. Absence is not
permission to invent a value.

## Required Checks

- Decode boundary input into named fields or existing domain types before use.
- Never substitute cursor, selection start, active cell, requested sheet, or
  similar fields merely because their primitive types match.
- Preserve unspecified input as `None`; reject absence when the contract
  requires a value.
- Apply a default only when the contract explicitly defines it. Do not invent
  `A1`, sheet `0`, empty text, or zero to continue processing.
- Validate the typed operation completely before mutation.

See the base rules `api-newtype-safety`, `api-parse-dont-validate`,
`type-newtype-validated`, and `type-option-nullable`.
