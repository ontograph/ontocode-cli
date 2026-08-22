# Axel Worktree Task Packet

Use this profile only for bounded delegated Axel work.

## Required Packet

Record:

```text
task_id
tracking_path
base_sha
branch
worktree_path
owner
reviewer
owner_files
allowed_write_set
non_goals
validation_commands
evidence_directory
special_environment
```

For a mixed Rust/C++ issue, also record:

```text
rust_manifest
rust_package_or_target
rust_features
cpp_direct_caller
cpp_build_owner
abi_owner
focused_reproducer_command
expected_changed_files
expected_changed_symbols
```

Omit these fields for tasks that do not cross the Rust/C++ boundary.

## Setup

1. Read the task from its structured `manager_loop`; do not derive authority
   from prose sequencing.
2. Record the current base SHA before creating the worktree. Use a unique branch
   and path and refuse an existing conflicting worktree or branch.
3. Verify every `owner_files` entry is within `allowed_write_set`, dependencies
   are ready, and the write set does not overlap an active neighboring task.
4. Preserve dirty user work in the source tree. Never clean, reset, or relocate
   it to make setup easier.
5. Use the shared cache at `/home/er77/_wrk/.cache/ccache-axel`; do not create a
   per-worktree physical cache or disable `hash_dir`.
6. Add an idempotent `init.sh` beside the evidence directory only when the task
   needs more than the repository-default environment. Do not add one for
   ordinary commands.
7. Record exact validation commands, expected evidence, rollback, and stop
   conditions before dispatch.
8. For a mixed-boundary fix, ensure the reproducer reaches the affected ABI,
   expected files cover both authorized sides, and `abi_owner` names the single
   layer responsible for ownership and error conversion. Put fallback creation,
   broad engine redesign, and unrelated caller cleanup in `non_goals`.

## Verification

Before handoff, verify the worktree HEAD equals `base_sha`, the branch and path
match the packet, the evidence directory is writable, and no generated or
binary artifact is already staged. Return the packet to the owning execution
skill; worktree setup does not authorize implementation outside its write set.
