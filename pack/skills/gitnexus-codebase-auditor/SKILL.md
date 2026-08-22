---
name: gitnexus-codebase-auditor
description: Audit codebases with GitNexus MCP/frontier tools, verify audit reports, find stale findings, dedupe root causes, prepare implementation bundles and worker prompts, review scope after worker edits, and perform systems audits for resource lifecycles, FD leaks, fork/signal safety, taint, FSM, concurrency, error topology, ABI drift, and fault handling.
---

# GitNexus Codebase Auditor

Use this skill when a user asks to audit a codebase with GitNexus, verify an audit report, find stale findings, turn findings into implementation bundles, prepare worker prompts, review worker scope, or audit systems risks such as FD/resource leaks, fork safety, signal safety, taint, FSM bugs, concurrency, error swallowing, ABI mismatches, and fault handling.

Default stance: audit first, classify with evidence, then bundle verified work. Do not modify product code unless the user explicitly asks for implementation.

## Core Rules

- Never mark a finding `OPEN` without fresh evidence at the target HEAD.
- No audit result is valid without a `sessionId` from `gn_audit_ingest` and a valid `gn_audit_session_lock`.
- No `OPEN` finding is valid unless `gn_audit_verify` produced it for the locked session.
- If fresh evidence is missing, classify as `NEEDS-VERIFY` or `NEEDS-REVERIFY`.
- Always check fix history before repeating an old finding.
- Collapse duplicates by root cause before creating implementation bundles.
- Treat runtime-only claims as `HOLD` unless runtime evidence exists.
- Prefer symbol identity, fingerprints, and graph evidence over stale line numbers.
- Require negative evidence for `RESOLVED-ALREADY` and `FALSE-POSITIVE`.
- Generate implementation work only from verified bundles.
- Before parallel dispatch, check bundle conflicts.
- After worker edits, run scope guard and required tests.
- Do not invent evidence. If GitNexus cannot prove it, say so.
- Do not write primary audit reports manually. Use `gn_audit_export({session, format: "both"})` for canonical JSON and generated Markdown.

## Default Audit Workflow

1. **Lock Target**
   - Record repo, branch, target HEAD, dirty worktree state, and audit source.
   - Read repository governance files before recommending edits.

2. **Discover**
   - Run `gn_help({})` when tool availability is unknown.
   - Set `gn_quality_mode({level: "balanced"})`.
   - Use `gn_explore({query: "..."})` for architecture and flow discovery.
   - Use `gn_find_related({symbol: "..."})` for neighboring symbols.
   - Use `gn_explain_module({filePath: "..."})` for unfamiliar files.

3. **Ingest and Verify**
   - `gn_audit_ingest({sourcePath})`
   - `gn_audit_session_lock({session, action: "create"})`
   - Before every lifecycle step, validate with `gn_audit_session_lock({session, action: "validate"})`.
   - `gn_audit_verify({session})`
   - For repeated or suspicious claims, run `gn_fix_history({symbol, claimPattern})`.
   - Classify every finding before producing work.

4. **Dedupe and Bundle**
   - `gn_audit_dedupe({session, strategy: "root-cause"})`
   - `gn_audit_bundle({session})`
   - `gn_audit_lint({session})`

5. **Dispatch and Review**
   - `gn_bundle_conflicts({session})` before parallel work.
   - `gn_dispatch_prompt({session, bundleId})` for one concrete worker bundle.
   - After edits, run `gn_scope_guard({session, bundleId, changedFiles, changedSymbols, executedTests})`.

6. **Manager Loop**
   - Ingest -> lock -> verify -> dedupe -> bundle -> dispatch -> review -> export -> redo failed bundle.
   - Re-run verification when HEAD changes.
   - Move blocked runtime or telemetry claims to `HOLD` with a reopen trigger.
   - Use `gn_audit_replay({session})` after HEAD changes and `gn_audit_diff({sessionA, sessionB})` between audit rounds.

## Status Classification

- `OPEN`: Current target HEAD proves the behavior exists and it is actionable.
- `RESOLVED-ALREADY`: Current HEAD contradicts the finding; include negative evidence and fix history when available.
- `FALSE-POSITIVE`: The claim is structurally wrong or impossible in the current code; include negative evidence.
- `NEEDS-VERIFY`: Plausible, but not proven in current code.
- `NEEDS-REVERIFY`: Previously verified, but target HEAD or symbol changed.
- `PARTIAL`: Some mitigation exists; residual risk remains.
- `DECISION-GATED`: Requires product, security, operations, or compatibility decision.
- `HOLD`: Needs runtime environment, telemetry, privileged container, production fixture, or external dependency.

## Tool Selection

| Task | Preferred GitNexus tools |
|---|---|
| Discover architecture | `gn_help`, `gn_quality_mode`, `gn_explore`, `gn_explain_module` |
| Understand symbol neighborhood | `gn_find_related`, `gn_explore` |
| Verify audit report | `gn_audit_ingest`, `gn_audit_verify`, `gn_fix_history` |
| Lock audit session | `gn_audit_session_lock` |
| Find stale findings | `gn_audit_verify`, `gn_fix_history`, `gn_audit_lint` |
| Avoid known deferred repeats | `gn_audit_pr_marker_scan` |
| Compare/replay audit rounds | `gn_audit_diff`, `gn_audit_replay` |
| Export audit artifact | `gn_audit_export({format: "both"})` |
| Collapse duplicates | `gn_audit_dedupe({strategy: "root-cause"})` |
| Prepare implementation work | `gn_audit_bundle`, `gn_dispatch_prompt` |
| Check parallel safety | `gn_bundle_conflicts` |
| Review worker scope | `gn_scope_guard` |
| Resource/FD lifecycle | `gn_resource_trace`, `gn_trace_boundary`, `gn_path_verify` |
| Logic/security audit | `gn_audit_logic`, `gn_path_verify`, `gn_test_suggestions` |
| FSM bugs | `gn_extract_fsm`, `gn_path_verify` |
| Taint/source-sink flow | `gn_taint_trace`, `gn_trace_boundary` |
| Concurrency/fork/signal | `gn_concurrency_audit`, `gn_resource_trace`, `gn_simulate_fault` |
| Error swallowing | `gn_error_topology`, `gn_path_verify` |
| ABI/schema mismatch | `gn_abi_diff` |
| Load/pressure risk | `gn_pressure_impact`, `gn_simulate_fault` |

## Systems-Auditor Workflow

For FD leaks, resource leaks, fork safety, signal safety, cgroups, sockets, subprocesses, taint, FSM, concurrency, ABI, or fault-handling claims:

1. Identify the resource or boundary: fd, pid, pidfd, socket, pipe, cgroup, lock, env, signal, JSON schema, ABI, taint source/sink.
2. Run `gn_audit_logic({path, category})` for the file/category.
3. Run `gn_resource_trace({path})` for ownership and acquire/release paths.
4. Run `gn_trace_boundary({resource, start, end})` when data or ownership crosses a process/module boundary.
5. Run `gn_path_verify({symbol, when, must, mustNot})` for branch-sensitive claims.
6. Use deep analyzers as needed:
   - `gn_extract_fsm`
   - `gn_taint_trace`
   - `gn_concurrency_audit`
   - `gn_error_topology`
   - `gn_abi_diff`
   - `gn_pressure_impact`
   - `gn_simulate_fault`
7. Ask `gn_test_suggestions({findingId, symbol, risk})` for the narrowest useful tests.

## Output Format

```markdown
## Audit Result

Target:
- Repo:
- Target HEAD:
- Session:

Findings:
- OPEN:
- RESOLVED-ALREADY:
- NEEDS-VERIFY:
- FALSE-POSITIVE:
- HOLD:

Bundles:
- Ready:
- Blocked:
- Conflict risk:

Evidence:
- Fresh evidence:
- Negative evidence:
- Fix history:
- Tests:

Next Actions:
1.
2.
3.
```

## Failure and Stop Conditions

Stop or downgrade the finding when:

- GitNexus cannot resolve the target repo, HEAD, symbol, module, or audit session.
- The index is stale and the user has not authorized re-indexing.
- `gn_audit_session_lock({action: "validate"})` returns `STALE_SESSION`.
- A claim depends on runtime-only evidence that is not available.
- Fix history indicates the finding was already resolved and current code still satisfies the fix invariant.
- Bundle conflicts are high and the user requested parallel dispatch.
- Scope guard reports unexpected changed symbols/files after worker edits.
- Required tests cannot run; report the exact blocker instead of inventing validation.

## Worker Dispatch Rules

Worker prompts must assign exactly one concrete bundle or issue. Do not leave placeholders such as `<ISSUE_ID>`.

Every prompt should include:

- repo root and target HEAD,
- assigned bundle ID,
- scope and non-scope,
- required GitNexus checks,
- exact tests,
- stop conditions,
- final report requirements.

Implementation work should be generated only from `OPEN` or approved `PARTIAL` findings inside a verified bundle.
