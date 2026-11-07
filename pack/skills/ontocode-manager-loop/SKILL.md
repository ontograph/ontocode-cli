---
name: ontocode-manager-loop
description: Manager-loop dispatch, tracking, result-envelope, wait-state, and retry rules. Use for project-plan execution, coder-role dispatch, sub-agent orchestration, or structured session-log review.
---

# Manager Loop

For all development tasks in this repository, default to a bounded manager loop
using OntoIndex.

- Do not redefine sub-agent role/model bindings here; use the active tracking
  file, task prompt, or `$ONTOCODE_HOME/agents/*.toml` role definitions as
  the authority for sub-agent dispatch.
- When overriding agent type, model, or effort, disable history forking using
  the active tool schema (`fork_turns: none` when offered). Full-history forks
  inherit these fields and may reject overrides. Do not invent unsupported arguments.
- `tool_search` metadata for `spawn_agent` is not dispatch capability by itself.
  If `spawn_agent` is not exposed as a callable tool, treat `dispatch_mode:
  sub-agent` as `blocked: capability unavailable`; for `dispatch_mode: human`,
  continue by emitting dispatch-ready prompts for the main conversation or human
  runner, and record roles as `not dispatched` with reason `spawn_agent
  unavailable; human dispatch required`.
- If `spawn_agent` reports the configured child-agent cap, close completed,
  failed, or cancelled agents, then retry once before calling dispatch blocked.
- Immediately after a successful manager-loop spawn, persist the returned child
  identity, observed effective model, dispatched preflight result, and cleared
  wait state in the active task before waiting or ending the turn. If tracking
  cannot be updated, keep that child open and report its identity; never spawn a
  replacement for the same packet.
- Prefer `manager_loop_advance(action=dispatch)` with `task_id`, `agent_id`,
  `expected_revision`, and `receipt_id` null. That one call reserves the lease,
  spawns the child, and returns `dispatch_id`, `scope_sha256`, and
  `dispatch_revision`. Do not invent a partial three-field manager_loop binding.
- If `manager_loop_advance(action=dispatch)` returns
  `error_code: manager_loop_no_dispatch`, do not reserve a lease, spawn, retry,
  or mutate tracking. Use `recommended_action`, `reason`, and `reopen_gate` as
  the legal next step. The typed `no-dispatch` write-handoff result remains a
  separate capability-mismatch path.
- Reopen a terminal result only with the token its classification requires:
  `dependency-cleared:<receipt>` for `blocked: dependency gate`, and
  `fresh-evidence:<receipt>` for `needs-rework` only after the task scope
  changed. When no coder-manager is open, dispatch runs bootstrap, which
  rejects `resume_revision`; run `action=bootstrap` first, then dispatch with
  the token.
- Nested manager spawn depth-limit is parent-dispatch mode, not a task failure.
  If `spawn_agent` or `manager_loop_advance(action=dispatch)` returns
  `error_code: agent_depth_limit`, do not retry spawn or dispatch. Return
  `parent-dispatch-required` with `parent_dispatch_packet` so the parent can
  dispatch. If neither nested spawn nor parent harvest is available, stop with
  `blocked: capability unavailable` instead of free-hand tracking edits.
- After `wait_agent`, require `role_result_receipts.<agent_id>.receipt_id` and
  integrate only through `manager_loop_integrate` or
  `manager_loop_advance(action=integrate)`. A completed child without a receipt
  is not authority to hand-write PASS into the plan.
- Do not call `close_agent` until `wait_agent` has minted that receipt. A
  structured `error_code: manager_loop_validation_required` response means the
  agent remains open; `wait_agent` is still mandatory.
- Never free-form edit task status, leases, `role_results`, or
  `active_next_task` outside those integrate/advance tools.
- Never terminate a manager process that holds an in-flight or completed but
  unharvested child. Role-result receipts are minted only inside the dispatching
  parent's own `wait_agent` call, and the validated role status that authorizes
  acceptance is registry-only and is rebuilt as `None` for a persisted agent.
  Once that process exits, a completed child projects as
  `CompletedPendingValidation`, whose observe action is `WaitAgent`, so its
  result can never be integrated and the task strands with `wait_state:
  child-terminal-result` and an active lease. Wait in the process that
  dispatched; a `wait_agent` timeout neither cancels the child nor voids the
  binding, so call it again on the same thread.
- Treat `observe expected_revision is stale` and `observe agent binding does not
  match the current task` as argument-level errors, not proof of a dead binding.
  Re-read the current `tracking_revision` with `manager_loop_next` and retry
  `observe` from the same parent thread. Only the original parent thread can
  observe a completed child; cross-thread recovery is limited to
  capacity-flavored route failures.

## Action Budgets And Recovery Evidence

Apply the repository's declared execution budget to the whole task, including
delegated work. Allocate child budgets from the parent allowance; parallelism,
tool changes, compaction and repeated continuation messages do not reset it.
Record each allocation before dispatch and reconcile actual usage from the
child's execution evidence; never assume an interrupted child used nothing.

- Record limits and used counts for builds, test runs, app launches and
  measurement samples in existing task evidence, or conversation evidence when
  there is no tracker. Count each started invocation, including failed runs;
  a suite invocation counts as one test run and its samples are counted
  separately. A launch-only receipt is enough to consume a launch. A confirmed
  pre-execution rejection consumes no execution, but still records the failure.
- Retain the returned action/job identity and terminal evidence. An uncertain
  launch reserves its budget slot until reconciliation establishes whether it
  started; do not create a replacement while that outcome remains unknown.
- Read the relevant first failure before a retry. The same failure recurring
  under unchanged preconditions requires a corrected cause, not another run.
  For a patch with missing output, read the target or diff before retrying; a
  second editor or tool does not make an unreconciled retry safe.
- Exhaustion stops further budgeted execution. Record any proposed increase,
  its reason and the explicit authorization before using it; retain original
  limits, consumed counts and any overrun. New failing evidence can justify a
  retry within remaining budget, but cannot expand the budget by itself.
- After three consecutive recovery attempts with neither new evidence nor
  observable progress, stop autonomous recovery, cite the stop condition and
  concrete blocker, and state the exact reopening condition. Preserve recovery
  counts across turns. A task making progress or awaiting a running child is
  not a failed recovery attempt. Observations use the existing polling limit
  and do not grant additional recovery attempts. Keep dependent work gated by
  its prerequisite.
- Keep this accounting in existing evidence; it introduces no parser fields or
  runtime enforcement. Never hand-edit tool-owned attempts, leases, receipts,
  task status or role results to record a budget amendment. If a runtime cap
  also blocks execution, use its supported amendment path or report that exact
  capability as unavailable. Exhaustion still permits reconciliation and
  harvesting already-started work under existing wait and mailbox limits.

## Artifact Acceptance

- Match successful command claims to runtime receipts, then check the expected
  result's content or behavior. Workspace input digests establish input
  integrity; they do not establish generated-output correctness. A correct
  no-op can pass without changed bytes when acceptance permits it.
- Give each costly capture or measurement attempt a distinct evidence location
  through the existing run owner. Preserve failed evidence; never overwrite a
  previous attempt. Ordinary source reads do not require separate directories.
- Cite figures from observed source evidence. Reuse across turns or agents is
  allowed with the immutable artifact reference, content hash and extraction
  method; reread mutable sources when freshness matters. Unsupported memory,
  expected values and another agent's unsupported assertion are not evidence.
- Package or test produced outputs only after harvesting the producer's
  terminal success and confirming the expected artifact. Retain launch-only
  results as pending execution evidence.
- At closeout, report changed paths, executed validation with actual exit
  codes, omitted checks and reasons, budget used versus declared, and any
  loop-rule violation. Put these details inside the required role-result
  envelope for roles that require one; do not append incompatible prose.

## Agent Addressing

Retain the handle returned by `spawn_agent` and use the active tool schema.
Some interfaces require a UUID; others accept a canonical task path or relative
task name. Use only the forms that interface documents. Never substitute a display
nickname, internal lease ID, or template placeholder.

An invalid-handle error is an argument error, not evidence that the child died.
Recover its handle from the spawn result or agent listing before another action;
never redispatch while ownership of an existing child remains unresolved.

## Waiting

Call `wait_agent` when you are blocked on the result, and give it a deadline
that matches the work. One long wait is correct; a loop of short waits is not.

- Do not poll at the 10s floor. A child doing real work will not finish there,
  so the call returns nothing and costs a turn.
- Prefer minutes for implementation packets. The timeout neither cancels the
  child nor voids the binding, so a long wait is safe.
- While a child runs, do disjoint local work instead of re-waiting on reflex.
- Re-waiting is warranted after a timeout, not as a status heartbeat.

## Harvest Or Cancel

Background shell jobs deserve the same discipline as child agents: whatever you
start, you finish.

- Keep the `job_id` returned at launch and read the result with
  `background_action: "status"`. It answers immediately.
- Never poll with `sleep`. Waiting in the shell costs wall clock and proves
  nothing about progress.
- Cancel a job you no longer need instead of abandoning it, and never launch a
  replacement for a job you have not harvested.
- An unharvested job is not evidence. Do not report a build or test as passing
  on the strength of a launch that returned a `job_id`; terminal output or a
  receipt is the authority.
- Sub-agent role definitions in `$ONTOCODE_HOME/agents/*.toml` are cached at server
  startup. Editing a role's model mid-session does not change routing for the
  running session, and killing a client process does not reload them. When a
  role fails envelope validation twice, correct the role definition and restart
  the server; do not kill live manager processes in pursuit of a new route.
- When a role returns `prompt-shape error`, resume with the
  `prompt-shape:<last_progress_revision>` token. Do not reach for
  `manager_loop_advance(action=recover)`; recover is for stranded gates, and on
  the plan-gate path it clears the accepted architect result, forcing a full
  re-review for no gain.
- When MultiAgentV2 is enabled, `coder-worker` must post mid-execution discoveries
  that affect a sibling slice, contradict the dispatched plan, or close off an
  approach; the terminal `role_result` envelope remains unchanged.
- When MultiAgentV2 is disabled and the shared observation budget is exhausted
  while that child remains non-terminal, preserve `active_next_task`, child
  identity, attempts, and route metadata; set `manager_loop.status: waiting` and
  `dispatch.wait_state: child-terminal-result`. Do not record `blocked: worker
  result unavailable`. A validated terminal coder-role notification resumes the
  existing read-only parent continuation exactly once; collect the durable result
  and advance the same task without redispatching the completed role.
- When MultiAgentV2 is enabled, suspend that 3-poll budget and the `blocked:
  worker result unavailable` wait state for the session; rely on mailbox delivery
  without spending a manager step.
- For log-review tasks, parse structured session records by event timestamp rather
  than file mtime, exclude the current analysis turn, and do not count embedded
  system prompts or command output echoes as fresh behavioral evidence.
- Do not treat `response_item` records with `role: user` as proof of a fresh human
  instruction. That role is also used for model-visible context and automatic
  continuation content. Correlate it with `event_msg` records, task boundaries,
  and explicit origin/client metadata when available; otherwise classify sender
  provenance as unknown.
- Do not repeat an unchanged failed tool call with identical arguments and
  unchanged preconditions. Retry only after correcting the invocation or after a
  concrete state change that can affect the result; otherwise record the exact
  blocker or terminal outcome.
- Continue in this order:
  - if `active_next_task` exists, execute it;
  - else if the last decision was no-dispatch, reply with the exact reopen gate;
  - else refuse to rewrite tracking without new evidence.
- Close with an exact outcome label such as `blocked: dependency gate`, `blocked:
  capability unavailable`, `blocked: model/capacity`, `no-dispatch: no eligible
  task`, `prompt-shape error`, or `interrupted by user`; do not collapse these
  into generic sub-agent failure.
- When a coder role must return a structured `role_result`, its final assistant
  message must consist solely of one fenced YAML `role_result` document. Put
  summaries, blockers, reopen gates, and dispatch details inside that envelope;
  do not add prose, links, headings, or additional fences before or after it.
- Known worker failure modes from session-log review; check these before any
  retry after a rejected envelope or failed patch:
  - Fabricated validation claims: a worker asserts PASS without an executed
    command or cites evidence for code it never wrote. Treat undeclared
    validation as NEEDS_REWORK, not PASS.
  - Flat envelope trap: the result must be one fenced ```yaml block whose
    top-level key is exactly `role_result:`. A bare YAML map without that
    wrapper fails before field validation.
  - apply_patch header trap: patch text must start with exactly
    `*** Begin Patch`; trailing asterisks (`*** Begin Patch ***`) or a leading
    blank line fail verification. The verifier error now echoes the offending
    first line — require the child to read it before retrying.
- The manager must validate that envelope before accepting the child result or
  updating tracking. On malformed output, request one format-only correction; if
  it remains invalid, record `prompt-shape error` and do not infer a result from
  surrounding prose.
- Any edit after a validation command invalidates that command as completion
  evidence for the affected scope. After the final edit, rerun the smallest
  relevant checks before claiming completion or closing tracking.
- Include a bounded `knowledge_handoff` only for a new reusable lesson not already
  covered by the target skill. Name its runtime signal, target skill, and proposed
  delta. Otherwise omit it; routine terminal states need no learning paperwork.
- A `knowledge_handoff` is a proposal, not authority to write. Applying it to a
  skill file is parent/user-owned work and must not widen a read-only role's
  `changed_files`.

## File-Scoped Fan-Out For Multi-File Tasks

Use for changes spanning several files (cross-file API, config, or test
coupling). Skip for single-file edits.

1. Select scope with OntoIndex `impact`/`inspect/explore`: target files plus callers,
   configuration and tests. Record it in the task as the write set.
2. Give each file (or tightly coupled group) one bounded packet with a disjoint
   write set. Editors may use the cheaper model; selection and diagnosis stay
   on the stronger model.
3. Each editor returns, besides its change, a short list of neighbor requests
   (`<path>: what changed; what to update/check`). A request never widens the
   recipient's write set; the manager routes it as a new packet. Record
   pending requests in the recipient task's optional `neighbor_requests` list
   (inline entries must not contain commas). It is routing data only and does
   not change the task scope hash.
4. Run the repository validation, then diagnose with `validation-diagnosis`
   (per-file recommendations).
5. Re-select scope from that diagnosis for the next round. At most three
   rounds after the first attempt unless the task declares another limit; count
   them in the tracker. Stop on repeated unchanged failure.
