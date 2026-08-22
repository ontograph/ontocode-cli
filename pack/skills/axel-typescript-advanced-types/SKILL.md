---
name: axel-typescript-advanced-types
description: Apply advanced TypeScript types in Axel only when simpler project-compatible types cannot encode a proven invariant. Use for difficult generic inference, conditional or mapped types, discriminated unions, type guards, and compiler errors that ordinary interfaces and utility types cannot resolve in the owning package's TypeScript version.
---

# Axel Advanced TypeScript Types

Start with the simplest type that works. Advanced typing is a last rung, not a default style.

## Decision ladder

1. Reuse an existing project type.
2. Use an interface, union, literal type, overload, or built-in utility type.
3. Narrow `unknown` with an existing runtime check or a small type guard.
4. Use one generic constraint when it removes duplication without hiding behavior.
5. Only then use a conditional, mapped, template-literal, or recursive type.

Stop when a higher rung holds. Do not add branded primitives, `Deep*` utility families, builder-state type machines, or general-purpose type libraries for a single caller.
- For finite states, prefer discriminated unions plus an exhaustive switch whose final branch assigns to `never`.

## Constraints

- Stay compatible with the owning scope. Shipped `browser/src` uses the TypeScript 4.4.2 binary with strict mode, ES5 output, and no modules; Mocha tests use that compiler through a non-strict ES2020 CLI build; `qt/test` uses TypeScript 5.x with ESM. Do not use post-4.4-only syntax such as `satisfies` or const type parameters in shipped browser code.
- Preserve runtime validation at untrusted boundaries; compile-time types do not validate messages, JSON, DOM state, or protocol data.
- Prefer discriminated unions for finite states and exhaustive switches where the surrounding code supports them.
- Avoid distributive conditional types and recursive mapped types unless their compiler cost and error messages stay acceptable.
- Do not copy a utility from an upstream skill or blog. Prove it against the actual Axel call sites and keep it local unless multiple existing consumers need it.
- Comment only the non-obvious invariant or compatibility constraint.
- When rejecting invalid states matters, add one focused negative check with `@ts-expect-error`; do not build a large parallel type-test framework for one invariant.

## Validate

- Compile through the owning path: `cd browser && npm run build-tests` for test-visible code, `scripts/select-gates.sh --run` for selected gates, and the configured browser build so `tscompile.done` runs for a shipped-source type change. A Mocha bundle pass does not prove strict browser compilation.
- Add a focused regression check only when it would fail if the invariant regressed.
- If type-check time may materially change, measure the same owning compile before and after with the installed compiler (`browser/node_modules/typescript/bin/tsc`). Do not recommend compiler flags carried over from another project.

Use `$axel-typescript-development` for implementation and `$axel-typescript-testing` for behavioral coverage.
