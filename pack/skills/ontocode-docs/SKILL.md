---
name: ontocode-docs
description: Documentation style for Markdown authored in this repo.
disable-model-invocation: true
---

## Documentation Style

Write documentation so it stands on its own. State directly what each thing is
and what it does. Remove content that does not serve the reader's current task.

- Describe the current state. Do not write "this is not X, it is actually Y",
  "this used to be X", "this looks like a mismatch between versions", or
  "possibly legacy".
- When existing text is wrong, replace it. Do not leave the wrong version in
  place alongside an explanation of why it was wrong.
- Cite verifiable facts: metadata, `file:line`, or a closed issue such as
  `#1234`. Do not cite PR or iteration numbers as the source of truth.

### Scope

Decision records, migration and provenance notes, and archived history describe
superseded state because that record is their purpose. This style governs
reference documentation, READMEs, skills, plans, and reports.
