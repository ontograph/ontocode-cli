# GPT-6 Astra

Family key `gpt-6-astra`. Covers `gpt-6-astra`.

The heaviest reasoning seat, offered at effort tiers up to `xhigh`. Astra is
for work whose cost of being wrong is high enough to justify the cost of
thinking longer.

## Personality source

This family has **no catalog personality variants**. In the upstream model
catalog its `instructions_variables` is `null` and its instruction template
carries no `{{ personality }}` placeholder, so host personality text cannot
reach it and `example.toml` declares no `gpt-6-astra` family.

Its voice comes from the shipped base instructions,
`ontocode-rs/protocol/src/prompts/base_instructions/default.md`, whose
`## Personality` and `## Technical communication` sections apply to every model
without catalog variants. The quotations below are from that file.

## Voice

> Your default personality and tone is concise, direct, and friendly. You
> communicate efficiently, always keeping the user clearly informed about
> ongoing actions without unnecessary detail.

Astra's depth shows in how it handles uncertainty, which the same file governs:

> When uncertainty could affect the answer or next action, state what is
> confirmed, what is inferred, and what remains unknown. Do not present
> inference as fact; name the smallest check that would resolve the
> uncertainty.

## Grain

Good at multi-file investigation, cross-cutting review, difficult diagnosis,
and long autonomous stretches where the work must hold together across many
steps. It is the right choice when a wrong answer costs more than a slow one.

Its failure mode is thoroughness applied to a trivial task. For a one-line fix
or an exact lookup it will spend real time confirming what was already known;
route those to `gpt-5.6` instead. Because it sustains long chains, state stop
conditions explicitly so it finishes rather than continuing to deepen.

Host personality text still applies to this family. Because the model ships no
`{{ personality }}` placeholder, the runtime synthesizes one, composes the text
ahead of the model's existing instructions, and logs a warning naming the slug.
The `gpt-6-astra` entry in `example.toml` is derived from the base-instructions
voice quoted above, which is the reference for any model without variants.
