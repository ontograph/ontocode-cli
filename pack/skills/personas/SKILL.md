---
name: personas
description: Model-family persona text for host-editable personality instructions. Use when configuring personality_instructions_file, choosing a voice for a model family, or deciding which family suits a task.
---

# Model Personas

Persona text for each model family, in the format the runtime loads.

`example.toml` in this directory is a ready `personality_instructions_file`.
Point `config.toml` at a copy to change how models speak on this host, with no
binary rebuild:

```toml
personality_instructions_file = "~/.ontocode/skills/personas/example.toml"
```

Edit that file to change the text. Changes take effect for sessions configured
after the edit; a running session keeps the text captured when it started.

## Files

| Persona | Family key | Covers |
| --- | --- | --- |
| `grok.md` | `grok-4` | `grok-4`, `grok-4.5`, `grok-4.6` |
| `claude-opus.md` | `claude-opus` | `claude-opus-4-6-thinking`, `claude-opus-4-8`, `claude-opus-5` |
| `claude-fable.md` | `claude-fable` | `claude-fable`, `claude-fable-*` |
| `gpt-6-astra.md` | none | `gpt-6-astra` |
| `gpt-5.6.md` | none | `gpt-5.6-sol`, `gpt-5.6-luna` |
| `gemini.md` | `gemini` | `gemini-3.8-flash-high`, other `gemini*` |
| `qwen.md` | `qwen` | `qwen/qwen3.7-flash`, other `qwen*` |

`gpt-6-astra` and `gpt-5.6` have no catalog personality placeholder, but host
text can still reach them. The runtime synthesizes a personality section ahead
of their existing instructions and logs a warning naming the model slug. Their
persona text should extend the voice in the shipped base instructions rather
than replace it.

Each document states Voice, Friendly, and Pragmatic, which map to the
`default`, `friendly`, and `pragmatic` keys, plus a Grain section describing
where that family fits. Grain is guidance for assigning work and is not loaded.

`vendor-research.md` records the published vendor prompts the Gemini and Qwen
personas were derived from, and what was deliberately excluded.

## File format

```toml
version = 1

[families."gpt-5"]
default = "Measured, concrete, low ceremony."
pragmatic = "Direct. Lead with the outcome."
```

A family key matches a model slug by longest declared prefix, after any
provider qualifier is stripped, so `gpt-5` covers `gpt-5.6-sol` and
`openai/gpt-5`. Declaring both `gpt-5` and `gpt-5.6` sends `gpt-5.6-sol` to the
more specific entry. Prefix matching is boundary-aware, and a key ending in a
letter can cover a following version digit, as with `qwen` and `qwen3.7-flash`.
A variant left unset keeps its built-in text.

Limits are 256 KiB per file, 64 families, and 32 KiB per variant. Unknown keys,
unknown versions, empty family keys, normalized duplicate family keys, and
empty variants are rejected when the file loads, rather than being silently
ignored.

## Boundaries

Keep variants to one to three sentences of direct address. Long prose competes
with the base instructions for attention.

Persona text describes communication style only. It cannot grant tool access,
change permissions, or alter role authority; those restrictions are enforced
independently of prompt text. In particular, Claude Fable's read-only tool set
is enforced in code and no persona wording widens it.

Selecting the `none` personality yields empty text regardless of what a persona
declares. Hosts without this file keep built-in behavior unchanged.
