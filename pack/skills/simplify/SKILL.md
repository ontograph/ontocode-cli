---
name: simplify
description: Review recent code changes for small safe cleanup opportunities, then apply only local low-risk improvements with focused validation.
---

# Simplify Recent Changes

Use this skill when the user asks for a post-implementation cleanup pass, pre-PR polish, or simplification of recent code changes.

## Scope

1. Inspect the current git diff and recent untracked files.
2. If the scope is unclear or empty, stop and say there is nothing concrete to simplify.
3. Prefer no change over speculative cleanup.

## What To Fix

Apply only straightforward local improvements:

- remove duplicated code when an existing helper clearly covers it
- simplify obvious control flow
- remove redundant state, wrappers, or comments
- align touched code with nearby conventions
- narrow overly broad checks or scans when the narrower form is clearly equivalent

Skip uncertain, cross-owner, architectural, or broad refactor findings. Do not add new dependencies, configuration keys, public APIs, command runtimes, schedulers, or loader/schema fields.

## Verification

After edits, run the smallest focused check that covers the changed path. If no focused check exists, run a targeted build, typecheck, lint, or explain why validation was skipped.

Report changed files, checks run, and any skipped cleanup ideas.
