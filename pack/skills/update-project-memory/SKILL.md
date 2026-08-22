---
name: update-project-memory
description: Verify and update durable project memory after a work stage reaches a terminal state. Use only when explicitly invoked after authoritative tracking integration; never infer completion from a worker claim alone.
---

# Update Project Memory

Update durable project memory only when the repository defines its memory
architecture and an active tracking plan can be identified.

1. Read the repository instructions and memory index.
2. Identify the active tracking plan and task from its structured
   `manager_loop` block. Treat that tracking plan as the source of truth.
3. Verify claims against task-scoped source, Git changes, applicable ADRs, and
   validation executed after the final edit.
4. Confirm the authoritative tracking plan already records the terminal status,
   completed work, changed files, executed validation, blockers, residual risks,
   exact reopen gate, and dependency-ready next steps. If it does not, make no
   memory changes and route the gap back to the tracking owner.
5. Update current or pending projections only when their represented state
   changed. Update the memory index only when its routing changed.
6. Create an audit-session record only for a significant closeout or accepted
   technical decision. Reference plans, diffs, and logs instead of copying them.
7. Use a temporary handoff outside the workspace when only conversational
   transfer is needed.

Do not include unsupported conclusions, unrelated concurrent changes, complete
logs, credentials, authorization data, keychain paths, or private user data.

If the memory contract, active plan, task ownership, authenticated terminal
state, or final-edit validation cannot be established, make no memory changes
and report the exact missing authority or gate.
