# Vendor persona research

Source notes for the personas in this directory. Every quotation below was read
from the vendor's published prompt source on 2026-09-05, not reconstructed from
memory.

## Sources

| Vendor     | File                                    | What it defines                                                                             |
| ---------- | --------------------------------------- | ------------------------------------------------------------------------------------------- |
| Gemini CLI | `packages/core/src/prompts/snippets.ts` | `renderPreamble` identity, `renderCoreMandates`, delegation and context-efficiency guidance |
| Gemini CLI | `packages/core/src/core/prompts.ts`     | Thin wrapper delegating to `PromptProvider`                                                 |
| Qwen Code  | `packages/core/src/core/prompts.ts`     | `getDefaultCoreIdentitySentence`, Core Mandates, software-engineering workflow              |

Repositories: `openai/codex`, `google-gemini/gemini-cli`, and
`QwenLM/qwen-code`, all `main`.

## OpenAI Codex catalog

The per-model persona text lives in `codex-rs/models-manager/models.json`. Read
from live `openai/codex` on 2026-09-05; 11 models. Only three carry a
`{{ personality }}` placeholder and non-null `instructions_variables`:

| Model          | friendly   | pragmatic  |
| -------------- | ---------- | ---------- |
| `gpt-5.5`      | 1723 chars | 1598 chars |
| `gpt-5.4`      | 2419 chars | 1853 chars |
| `gpt-5.4-mini` | 2419 chars | 1853 chars |

`gpt-6-astra`, `gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna`,
`gpt-daybreak-blue-latest`, `gpt-daybreak-red-latest`, `gpt-5.2`, and
`codex-auto-review` all have `instructions_variables: null` and no placeholder,
so host personality text cannot reach them. Their voice comes from the shipped
base instructions instead.

Two conventions follow from this catalog and are reflected in the personas:

- `personality_default` is `""` in every model that has variants. The
  unselected case is deliberately blank upstream.
- Real variants are long and sectioned, using `## Values`,
  `## Interaction Style`, and `## Escalation`. The upstream pragmatic text is
  the source of the phrase this repository already ships in its local fallback:
  "You are a deeply pragmatic, effective software engineer."

A vendored copy of this catalog also exists under `tmp/codeagents/codex-main`,
but it predates `gpt-6-astra`; the live repository is the authority.

## Gemini CLI

Identity, from `renderPreamble`:

> You are Gemini CLI, an interactive CLI agent specializing in software
> engineering tasks. You are currently operating in **{mode}** mode. Your
> primary goal is to help users safely and effectively.

Distinctive traits, all from `renderCoreMandates` unless noted:

- **Context economy as a first-class mandate.** A whole `Context Efficiency`
  section instructs the agent to combine turns, search in parallel, and pass
  conservative limits and scopes. It states that "unnecessary turns are
  generally more expensive than other types of wasted context."
- **Inquiry versus Directive.** The agent must "assume all requests are
  Inquiries unless they contain an explicit instruction to perform a task," and
  must not modify files until a Directive is issued.
- **No suppression.** "NEVER use hacks like disabling or suppressing warnings,
  bypassing the type system."
- **Reproduce before fixing.** "For bug fixes, you must empirically reproduce
  the failure with a new test case or reproduction script before applying the
  fix."
- **Strategic orchestration.** `renderSubAgents` frames the context window as
  "your most precious resource" and delegation as compression, while forbidding
  parallel sub-agents that mutate the same files.

## Qwen Code

Identity, from `getDefaultCoreIdentitySentence`:

> You are Qwen Code, {role} developed by Alibaba Group, specializing in
> software engineering tasks. Your primary goal is to help users safely and
> efficiently.

Distinctive traits:

- **Momentum over completeness.** The stated Key Principle: "Start with a
  reasonable approach based on available information, then adapt as you learn.
  Users prefer seeing progress quickly rather than waiting for perfect
  understanding."
- **Anti-overbuilding, stated numerically.** "Three similar lines of code is
  better than a premature abstraction," plus explicit bans on error handling
  for impossible scenarios and helpers for one-time operations.
- **Comments default to none.** Only when the _why_ cannot be carried by naming
  or structure.
- **Faithful reporting.** "If you did not run a verification step, say that
  rather than implying it succeeded," and never "suppress failing checks to
  manufacture a green result."
- **Diagnose before switching tactics.** "Don't retry blindly, but don't
  abandon a viable approach after a single failure."
- **Preserve existing work.** Unrelated changes are user-owned and must not be
  reverted, which matches this repository's own baseline policy.

## What was adopted

These vendor mandates were folded into the persona files as _voice_, not as
policy. This repository already enforces the equivalent rules through
`AGENTS.md`, the repository baseline, and role definitions; a persona only
shapes how a model talks while following them.

| Vendor trait                     | Adopted into                              |
| -------------------------------- | ----------------------------------------- |
| Qwen momentum and adaptation     | `qwen.md` voice and pragmatic variants    |
| Qwen anti-overbuilding           | `qwen.md` grain                           |
| Qwen faithful reporting          | `qwen.md`, and reinforced in `gpt-5.6.md` |
| Gemini context economy           | `gemini.md` voice and grain               |
| Gemini Inquiry versus Directive  | `gemini.md` grain                         |
| Gemini reproduce-before-fix      | `gemini.md` grain                         |
| Gemini delegation-as-compression | `claude-fable.md` grain                   |

## What was deliberately not adopted

Vendor identity sentences are excluded. A persona that says "You are Gemini
CLI" would misidentify the product, and personality text is composed into
Ontocode's own instructions rather than replacing them.

Tool names, workflow scaffolding, and approval-mode language are excluded. They
describe another host's tool surface and would be false here.

Safety and permission mandates are excluded. They are enforced in code and by
repository policy; restating them in persona text would imply that editing a
host file could weaken them, which is not true.
