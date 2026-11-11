---
name: ontocode-docs
description: Documentation style for Markdown authored in this repo.
disable-model-invocation: true
---

## Documentation Style

Write documentation so it stands on its own. State directly what each thing is
and what it does. Remove content that does not serve the reader's current task.

- Document what would surprise an experienced Rust engineer who knows Cargo,
  Just, Bazel and the repository layout: hidden constraints, non-obvious owners,
  ordering requirements, and decisions with a reason. Leave out what the code,
  the filename, or the command already says.
- Describe the current state. Do not write "this is not X, it is actually Y",
  "this used to be X", "this looks like a mismatch between versions", or
  "possibly legacy".
- When existing text is wrong, replace it. Do not leave the wrong version in
  place alongside an explanation of why it was wrong.
- When asked to update docs or comments, bring them in sync with the code:
  remove stale statements, update surprises, and delete what has become obvious.
- Cite verifiable facts: metadata, `file:line`, or a closed issue such as
  `#1234`. Do not cite PR or iteration numbers as the source of truth.
- Name files descriptively, so a directory listing explains the tree.
- Refer to a repository file by its name in backticks when the name is unique,
  and by its repo-root-relative path otherwise. The reader can grep and follow
  the reference; do not restate a command or a code path in prose.
- Do not wrap lines by hand in Markdown.
- Use a table only for comparisons or mappings that read worse as prose, and
  where a plan template or tool contract requires one.

### Scope

Decision records, migration and provenance notes, and archived history describe
superseded state because that record is their purpose. This style governs
reference documentation, READMEs, skills, plans, and reports.

Plans and trackers follow `PROJECT_PLAN_AUTHORING_TEMPLATE.md` for structure,
including its tables and YAML. Machine-read fields stay explicit even when a
person would find them obvious.
