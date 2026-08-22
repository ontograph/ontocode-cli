---
name: gitnexus-intensive-codebase-auditor
description: Audit a codebase or verify an audit report with GitNexus using freshness checks, lifecycle verification, stale-claim detection, systems-audit tools, root-cause dedupe, conflict-safe bundles, and concrete worker prompts grounded in current target HEAD evidence.
---

# GitNexus Intensive Codebase Auditor

Use this skill when a user wants a serious codebase audit, a report re-check against current code, stale-finding cleanup, systems-risk review, bundle planning, or worker dispatch prompts backed by current target HEAD evidence.

Default stance: audit first, classify with proof, bundle only verified work, and do not modify product code unless the user explicitly asks for implementation.

## Core Rules To Encode

1. Start every audit with target context:
   - repo path
   - branch
   - target HEAD
   - dirty worktree
   - indexed HEAD
   - GitNexus freshness
   - tool availability
2. Run GitNexus freshness and health checks first:
   - `gn_help({})`
   - `gn_diagnose({repo, checkIndexFreshness: true, checkEmbeddings: true, checkLsp: true})`
   - `gn_ensure_fresh({repo, autoAnalyze: false})`
   - If stale and the user authorized refresh: `gn_ensure_fresh({repo, autoAnalyze: true})`
3. Never mark a finding `OPEN` unless:
   - evidence is from current target HEAD
   - file or symbol still exists
   - claim is directly verified
   - fix history was checked for repeated or stale issues
4. If evidence is missing, classify as:
   - `NEEDS-VERIFY`
   - `NEEDS-REVERIFY`
   - `HOLD`
5. Always check fix history before repeating old claims:
   - `gn_fix_history({repo, path, patterns, targetHead})`
6. Prefer symbol identity and graph fingerprints over stale line numbers.
7. Collapse duplicates by root cause before implementation planning.
8. Treat runtime-only claims as `HOLD` unless runtime evidence exists.
9. Generate implementation work only from verified `OPEN` or approved `PARTIAL` findings.
10. Before dispatch:
    - run bundle conflict checks
    - produce one concrete prompt per bundle
    - do not leave placeholders like `<ISSUE_ID>`
11. After worker edits:
    - run scope guard
    - run required tests
    - report changed files, changed symbols, and tests
12. Do not invent evidence. If GitNexus cannot prove it, say so.

## 1. Default Intensive Audit Workflow

1. **Read governance files**
   - Read `AGENTS.md`
   - Read `CLAUDE.md`
   - Read project-specific memory or docs if relevant to the target area

2. **Lock target**
   - `git rev-parse --abbrev-ref HEAD`
   - `git rev-parse HEAD`
   - `git status --short`
   - `gn_help({})`
   - `gn_diagnose({repo, checkIndexFreshness: true, checkEmbeddings: true, checkLsp: true})`
   - `gn_ensure_fresh({repo, autoAnalyze: false})`
   - If tool availability is in doubt, also run `gn_tool_contract({})`
   - If the index is stale, stop unless the user authorized refresh
   - If authorized, refresh with `gn_ensure_fresh({repo, autoAnalyze: true})`
   - Record repo path, branch, target HEAD, dirty worktree state, indexed HEAD, freshness, and tool limitations before making claims

3. **Discover**
   - `gn_explore({repo, query, depth: "balanced"})`
   - `gn_explain_module({repo, filePath})`
   - `gn_find_related({repo, symbol})`

4. **Run broad GitNexus audits**
   - `audit({repo, action: "tech_debt"})`
   - `audit({repo, action: "cycles"})`
   - `audit({repo, action: "patterns"})`
   - `audit({repo, action: "coverage"})`
   - `audit({repo, action: "drift"})`

5. **Run systems audit tools for risky code**
   - `gn_audit_logic`
   - `gn_resource_trace`
   - `gn_path_verify`
   - `gn_trace_boundary`
   - `gn_extract_fsm`
   - `gn_taint_trace`
   - `gn_concurrency_audit`
   - `gn_error_topology`
   - `gn_abi_diff`
   - `gn_pressure_impact`
   - `gn_simulate_fault`
   - `gn_test_suggestions`

6. **Verify findings**
   - Inspect the exact file, symbol, and current code
   - Check fix history
   - Classify each finding
   - Downgrade analyzer-only claims until manually verified
   - Use `HOLD` for runtime-only claims without runtime evidence

7. **Bundle**
   - Group by root cause
   - Cap bundle size
   - List likely files and required tests
   - Check conflicts before dispatch

8. **Dispatch and review**
   - Produce worker prompts
   - Run scope guard after edits
   - Rerun required tests

## 2. Audit Report Verification Workflow

For a supplied audit report:

1. `gn_audit_ingest({repo, sourcePath/sourceText, targetRef})`
2. `gn_audit_session_lock({session, action: "create"})`
3. `gn_audit_verify({repo, session})`
4. `gn_fix_history({repo, path, patterns, targetHead})` for repeated or stale claims
5. `gn_audit_dedupe({session, strategy: "root-cause"})`
6. `gn_audit_bundle({session})`
7. `gn_audit_lint({session})`
8. `gn_audit_export({session, format: "both"})`

If lifecycle tools are unavailable, fall back to manual classification, say that lifecycle automation is unavailable, and do not claim lifecycle-backed verification.

## 3. Status Classification

Use exactly these statuses:

- `OPEN`: proven against current target HEAD and actionable
- `PARTIAL`: mitigation exists but residual risk remains
- `RESOLVED-ALREADY`: current code contradicts the claim; include negative evidence and fix commit if possible
- `FALSE-POSITIVE`: claim is structurally impossible or based on the wrong path
- `NEEDS-VERIFY`: plausible but not proven
- `NEEDS-REVERIFY`: previously proven, but target HEAD changed
- `HOLD`: needs runtime, telemetry, privileged container, production fixture, or ops evidence
- `DUPLICATE`: same root cause as another finding

## 4. Systems Audit Playbook

- **FD and resource leaks**
  - Use `gn_resource_trace`
  - Verify acquire, transfer, and release paths
  - Distinguish analyzer limitations from real bugs
  - `SCM_RIGHTS` claims require boundary evidence from `gn_trace_boundary`

- **Fork and exec safety**
  - Check `pipe2(O_CLOEXEC)` vs `pipe()+fcntl`
  - Check `dup2` return values
  - Check child-side async-signal-unsafe work
  - Check env mutation after `fork`
  - Check `exec` `envp` stability

- **Signal and process lifecycle**
  - Check `SIGTERM` and `SIGKILL` grace handling
  - Check `waitpid` blocking paths
  - Check `pidfd` fallback
  - Check parent-death signal handling
  - Check orphan and zombie paths

- **Cgroup and resource isolation**
  - Check create/addPid/remove lifecycle
  - Check `docId` sanitizer behavior
  - Check `memory.max`, `memory.high`, and `cpu.max`
  - Check `EBUSY` cleanup and retry behavior

- **Protocol and ABI**
  - Use `gn_abi_diff`
  - Check C++, Rust, JSON, and TypeScript field drift
  - Check version tokens and numeric precision

- **Error topology**
  - Use `gn_error_topology`
  - Find swallowed exceptions
  - Find unchecked syscall returns
  - Find generic error codes that erase cause

- **FSM**
  - Use `gn_extract_fsm`
  - Verify missing state guards
  - Verify terminal states cannot restart accidentally

## 5. Output Format

```markdown
## Audit Result

Target:
- Repo:
- Branch:
- Target HEAD:
- GitNexus freshness:
- Tool limitations:

Findings:
- OPEN:
- PARTIAL:
- RESOLVED-ALREADY:
- FALSE-POSITIVE:
- NEEDS-VERIFY:
- NEEDS-REVERIFY:
- HOLD:
- DUPLICATE:

Bundles:
- Ready:
- Blocked:
- Conflict risk:

Evidence:
- Fresh evidence:
- Negative evidence:
- Fix history:
- Runtime evidence:
- Tests:

Next Actions:
1.
2.
3.
```

## 6. Worker Prompt Rules

Worker prompts must:

- assign exactly one issue or bundle
- include repo root and target HEAD
- include scope and non-scope
- include exact files likely touched
- include required GitNexus checks
- include exact tests
- include stop conditions
- require a final report with files changed, tests, and residual risk
- contain no placeholders

Generate worker prompts only from verified `OPEN` or approved `PARTIAL` findings. Before parallel dispatch, run conflict checks. Prefer `gn_dispatch_prompt({session, bundleId})` when lifecycle tools are available.

## 7. Failure / Stop Conditions

Stop or downgrade when:

- GitNexus index is stale and refresh is not authorized
- MCP transport closes
- advertised tools are not callable
- target HEAD changes mid-audit
- source file or symbol no longer exists
- analyzer only provides heuristic evidence
- claim needs runtime evidence that is not available
- required tests cannot run
- worktree has unrelated dirty files that would be affected

## Tool Selection Table

| Task | Tools |
|---|---|
| Health/freshness | `gn_diagnose`, `gn_ensure_fresh`, `gn_tool_contract` |
| Architecture discovery | `gn_explore`, `gn_explain_module`, `gn_find_related` |
| Audit report verification | `gn_audit_ingest`, `gn_audit_verify`, `gn_fix_history` |
| Stale finding detection | `gn_fix_history`, `gn_audit_lint`, `gn_audit_replay` |
| Dedupe | `gn_audit_dedupe` |
| Bundles | `gn_audit_bundle`, `gn_bundle_conflicts` |
| Worker prompts | `gn_dispatch_prompt` |
| Scope review | `gn_scope_guard`, `gn_pre_commit_audit`, `gn_diff_impact` |
| Resource/FD audit | `gn_resource_trace`, `gn_trace_boundary`, `gn_path_verify` |
| FSM | `gn_extract_fsm`, `gn_path_verify` |
| Taint | `gn_taint_trace`, `gn_trace_boundary` |
| Concurrency | `gn_concurrency_audit`, `gn_simulate_fault` |
| Error handling | `gn_error_topology` |
| ABI/schema | `gn_abi_diff` |
| Pressure/load | `gn_pressure_impact`, `gn_simulate_fault` |

## Validation

Run validation if available:

```bash
python /home/er77/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  "${CODEX_HOME:-$HOME/.codex}/skills/gitnexus-intensive-codebase-auditor"
```

If that script is unavailable, manually verify:

- valid YAML frontmatter
- required name and description
- no placeholder text
- no README, changelog, or extra docs
- concise body
- consistent tool names
- output format is present
- failure conditions are present
