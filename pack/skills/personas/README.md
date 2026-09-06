# Model personas

Each file here describes the working voice of one model family, in the register
the model itself reads: second person, present tense, concrete.

These documents are the human-readable source. The runtime consumes personality
text through `personality_instructions_file`, described in
[ADR 0004](../adr/0004-explicit-soul-activation-and-session-snapshots.md). A
persona file is not loaded directly; copy the variants you want into that TOML
file, keyed by model family.

[example.toml](example.toml) is every persona in this directory already
assembled in that format. Point `personality_instructions_file` at a copy of it
to load them, or edit it down to the families you care about.

## When changes take effect

The file is read while configuration is constructed, so an edit reaches a
session started or reloaded afterward. Editing the file does not change a
session that is already running, and no ordinary turn, tool call, retry, or
status request re-reads it.

## Reaching a client host

These files ship in the published content pack as the `personas` skill, listed
in `scripts/content_pack_allowlist.toml`. Installing the pack places them at
`$ONTOCODE_HOME/skills/personas/`, so a host can load them without copying
anything by hand:

```toml
personality_instructions_file = "~/.ontocode/skills/personas/example.toml"
```

The copy in this repository is the editing source. After changing a persona
here, mirror it into `$ONTOCODE_HOME/skills/personas/` so the next content pack
exports the change; the pack builds from the home directory, not from `docs/`.

In a client/server deployment the runtime host owns file loading, so the file
must exist on the server. A remote client cannot supply a local path.

## Files

| Persona                         | Family key     | Catalog slugs                                                  |
| ------------------------------- | -------------- | -------------------------------------------------------------- |
| [Grok](grok.md)                 | `grok-4`       | `grok-4`, `grok-4.5`, `grok-4.6`                               |
| [Claude Opus](claude-opus.md)   | `claude-opus`  | `claude-opus-4-6-thinking`, `claude-opus-4-8`, `claude-opus-5` |
| [Claude Fable](claude-fable.md) | `claude-fable` | `claude-fable`, `claude-fable-*`                               |
| [GPT-6 Astra](gpt-6-astra.md)   | none           | `gpt-6-astra`                                                  |
| [GPT-5.6](gpt-5.6.md)           | none           | `gpt-5.6-sol`, `gpt-5.6-luna`                                  |
| [Gemini](gemini.md)             | `gemini`       | `gemini-3.8-flash-high`, other `gemini*`                       |
| [Qwen](qwen.md)                 | `qwen`         | `qwen/qwen3.7-flash`, other `qwen*`                            |

A family key matches a slug by longest declared prefix after any provider
qualifier is stripped, so `gpt-5.6` covers both `gpt-5.6-sol` and
`openai/gpt-5.6-luna`. Declaring `gpt-5` and `gpt-5.6` together sends
`gpt-5.6-sol` to the more specific entry.

A prefix has to end on a slug boundary, so `gpt-5` covers `gpt-5.6-sol` but not
an unrelated `gpt-500`. A key ending in a letter still covers a version digit,
which is how `qwen` reaches `qwen3.7-flash`.

The Gemini and Qwen personas are derived from those vendors' own published CLI
prompts. [vendor-research.md](vendor-research.md) records the exact sources,
the traits taken, and what was deliberately left out.

## Models without catalog personality variants

A model can compose personality text only if its instruction template carries a
`{{ personality }}` placeholder. In the upstream `openai/codex` catalog, only
`gpt-5.5`, `gpt-5.4`, and `gpt-5.4-mini` do. `gpt-6-astra`, `gpt-5.6-*`,
`gpt-daybreak-*`, `gpt-5.2`, and `codex-auto-review` ship none, and an unknown
slug ships no model messages at all.

Declaring a family for one of those models is still supported. The runtime
synthesizes a template, placing the personality text ahead of the instructions
that model would otherwise have used, and logs a warning naming the slug:

```text
Model gpt-6-astra ships no personality placeholder; applying host personality
text on top of its existing instructions.
```

The warning exists so this path is diagnosable. Without it, host text would
pass validation and then vanish during composition with nothing to inspect.

For these families the reference voice is the shipped base instructions in
`ontocode-rs/protocol/src/prompts/base_instructions/default.md`. Its
`## Personality` and `## Technical communication` sections describe how any
model without its own variants already speaks, so persona text for such a
family should extend that voice rather than invent a different one. The
`gpt-6-astra` and `gpt-5.6` entries in `example.toml` are written that way.

## Structure

Every persona states:

- **Voice** — the register used when no personality is explicitly selected.
- **Friendly** — the `friendly` variant.
- **Pragmatic** — the `pragmatic` variant.
- **Grain** — what this family does well and where it needs a shorter leash.

Voice, Friendly, and Pragmatic map to `default`, `friendly`, and `pragmatic`.
Grain is guidance for whoever assigns work; it is not loaded.

Personas for families without a loadable key state a **Personality source**
section instead, naming the base-instructions text that governs them.

Note that upstream ships `personality_default` as an empty string for every
model that has variants, so the unselected case is deliberately blank there. A
`default` value in this directory is an addition, not a replacement.

## Writing rules

Write variants in second person, matching the catalog's own phrasing such as
"You are a deeply pragmatic, effective software engineer."

Upstream variants are substantial: 1,598 to 2,419 characters, organized under
headings like `## Values`, `## Interaction Style`, and `## Escalation`. The
short entries in `example.toml` are deliberately compact starting points, not a
house style. Expand them toward that structure when a family needs a genuinely
distinct voice; the 32 KiB per-variant limit leaves ample room.

Describe communication style only. Personality text cannot grant tool access,
change permissions, or alter role authority, and text that attempts it is
ignored by every enforcement path.

Selecting `Personality::None` yields empty text regardless of what a persona
declares.
