# GPT-5.6

Family key `gpt-5.6`. Covers `gpt-5.6-sol` and `gpt-5.6-luna`.

The everyday workhorse. This family carries most bounded execution in this
repository and is bound to several `cdr-*` roles, including the auditor, debug,
and performance seats. Sol is the reliable generalist; Luna is the faster,
cheaper variant.

## Personality source

This family has **no catalog personality variants**. Upstream, all three
`gpt-5.6` entries have `instructions_variables: null` and no
`{{ personality }}` placeholder in their instruction template, so they have no personality variants of
their own.

Its voice comes from the shipped base instructions,
`ontocode-rs/protocol/src/prompts/base_instructions/default.md`. The
quotations below are from that file.

## Voice

> Your default personality and tone is concise, direct, and friendly. You
> communicate efficiently, always keeping the user clearly informed about
> ongoing actions without unnecessary detail. You always prioritize actionable
> guidance, clearly stating assumptions, environment prerequisites, and next
> steps.

For the execution work this family carries, two rules from the same file
matter most:

> Lead with the outcome or the next actionable step, and keep the response
> focused on moving the task forward.

> When reporting an error, give the cause, the supporting evidence, and the
> fix.

## Grain

Good at bounded implementation, focused validation, diagnostics, and audit
work where the target is already identified. It follows an explicit write set
closely, which is exactly what routine execution needs.

It performs best on a decided task. Give it the owner file, the intended
change, and the validation command; open-ended discovery is a weaker fit than
for the larger reasoning families. Luna trades some depth for speed, so prefer
Sol when the change touches shared behavior.

Hold it to faithful reporting, in Qwen Code's phrasing: if a verification step
was not run, it should say so rather than implying success, and never
characterize incomplete work as done. That is the failure mode worth watching
in a fast execution seat.

Host personality text still applies to this family. Because the model ships no
`{{ personality }}` placeholder, the runtime synthesizes one, composes the text
ahead of the model's existing instructions, and logs a warning naming the slug.
The `gpt-5.6` entry in `example.toml` is derived from the base-instructions
voice quoted above, which is the reference for any model without variants.
