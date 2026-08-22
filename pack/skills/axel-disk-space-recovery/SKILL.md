---
name: axel-disk-space-recovery
description: Diagnose and recover disk space for Axel work without deleting authoritative source, evidence, or the shared ccache. Use when a build or plan is blocked by low disk space, the user says check space and continue, or generated build artifacts must be cleaned before resuming work.
---

# Axel Disk Space Recovery

Recover only the space needed, then resume the interrupted task.

## Workflow

1. Identify the interrupted task, its working directory, and the minimum free-space target needed to continue.
2. Measure filesystem capacity and summarize the largest consumers under the Axel workspace, build trees, temporary directories, and caches. Do not follow unrelated mounts or broad home-directory trees unless needed.
3. Classify candidates:
   - `PROTECTED`: tracked source, uncommitted work, plan files, logs or screenshots cited as evidence, release artifacts, golden-oracle data, and `/home/er77/_wrk/.cache/ccache-axel`.
   - `REGENERABLE`: obsolete build outputs, stale temporary extraction directories, superseded scratch artifacts, and completed job intermediates whose provenance is known.
   - `UNKNOWN`: anything whose ownership or reproducibility is not proven.
4. Present the candidate paths, sizes, expected recovery, and regeneration cost before deletion.
5. Require explicit user approval for destructive cleanup. A request to "check space" is not deletion approval. If the user already explicitly authorized cleanup in the current conversation, delete only the listed approved paths.
6. Re-measure free space and verify protected paths still exist.
7. Resume the interrupted command or plan through its owning skill when the required space is available.

## Safety Rules

- Never delete tracked files, dirty worktree content, evidence referenced by a tracker, sealed oracle fixtures, or provisioned release assets.
- Never clear or relocate the shared Axel ccache. Prune it only when the user explicitly names the cache and accepts the rebuild cost.
- Prefer removing one large proven-regenerable directory over many uncertain files.
- Do not use destructive wildcard commands, `git clean`, or recursive deletion at a parent directory.
- Stop if a candidate contains unknown files, active process output, or the only copy of evidence.

## Evidence

Report capacity before and after, approved paths removed, bytes recovered, protected-path checks, the resumed task or command, and any remaining blocker. Do not claim recovery from estimated sizes alone.

## Routine Tool Ownership

This skill owns routine-tool operations 31-32 in
`~/.ontocode/skills/ontocode-routine-tools/references/tool-catalog.md`. Disk and
process reports are read-only by default; deletion or termination requires an
explicit approved target set and must use the coordinator's shared envelope.
