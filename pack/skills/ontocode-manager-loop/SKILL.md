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
- When passing explicit `agent_type`, `model`, or `reasoning_effort` to
  `spawn_agent`, do not use full-history forking: omit `fork_context` or set
  `fork_context: false`. Full-history forked agents inherit those fields and
  reject overrides.
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

## Agent Addressing

`spawn_agent` returns the only handle the agent tools accept: a UUID. Capture it
at spawn time and pass exactly that value to `wait_agent`, `send_input`,
`close_agent`, and `resume_agent`.

These are display labels, not handles, and every one of them fails to parse:

- the nickname shown in the environment context (for example `Noether`)
- the `task_name` you supplied at spawn (for example `pilot_0545_copyrange`)
- any internal identifier such as an `ml_<hash>` string
- an uninterpolated template placeholder such as `{target}`

The failure is `invalid agent id <value>: Error(ParseChar { .. })`. It means the
string was not a UUID; it does not mean the agent is missing, dead, or busy. Do
not retry with a second label or conclude anything about the agent's state.

If you no longer hold the UUID, do not guess. Determine liveness from evidence
the child leaves behind - its written artifacts, receipts, and file mtimes -
and re-dispatch only when the packet is genuinely unclaimed.

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
- At every terminal state (`wait`, `no_dispatch`, `complete`, `invalid_tracking`),
  carry the iteration's reusable lesson forward as a bounded `knowledge_handoff`
  entry in `evidence`: the lesson, the exact runtime signal that produced it, the
  target skill file under `$ONTOCODE_HOME/skills/`, and the proposed delta. Blocked and
  no-dispatch iterations carry the most reusable knowledge; do not restrict capture
  to successful closeout.
- Propose a `knowledge_handoff` delta only when the lesson is not already covered
  by the target skill. Otherwise record `knowledge_handoff: none` and cite the
  existing rule, so repeated blockers do not accumulate as near-duplicate entries.
- A `knowledge_handoff` is a proposal, not authority to write. Applying it to a
  skill file is parent/user-owned work and must not widen a read-only role's
  `changed_files`.
