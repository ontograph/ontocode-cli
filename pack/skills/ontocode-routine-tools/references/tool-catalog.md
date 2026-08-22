# Routine Tool Catalog

Status meaning:

- `CONTRACTED`: owner and shared envelope are assigned; runtime implementation remains outstanding.
- `IMPLEMENTED`: the owner has a runnable tool, fixtures, and documentation.

All operations are currently `CONTRACTED`.

| ID | Operation | Primary owner | Phase |
|---:|---|---|---:|
| 1 | `SESSION_REVIEW_WINDOW` | `ontocode-session-log-review` | 0 |
| 2 | `SESSION_OPERATION_CLUSTERS` | `ontocode-session-log-review` | 0 |
| 3 | `LOG_SCHEMA_AUDIT` | `ontocode-session-log-review` | 0 |
| 4 | `PROMPT_FAMILY_CLASSIFIER` | `ontocode-session-log-review` | 0 |
| 5 | `ABORT_ROLE_REPORT` | `ontocode-session-log-review` | 0 |
| 6 | `TOOL_CONTRACT_PREFLIGHT` | `ontocode-tool-contract-preflight` | 0 |
| 7 | `LEAN_CTX_ROUTE_PROBE` | `ontocode-tool-contract-preflight` | 0 |
| 8 | `MCP_SURFACE_INVENTORY` | `ontocode-tool-contract-preflight` | 0 |
| 9 | `REPO_STATE_SNAPSHOT` | `mb-harness` | 0 |
| 10 | `CHANGED_SCOPE_INVENTORY` | `mb-harness` | 0 |
| 11 | `DIFF_PATCH_REVIEWER` | `mb-harness` | 1 |
| 12 | `COMMITTED_REVISION_PROOF` | `mb-harness` | 1 |
| 13 | `WORKTREE_PACKET_MANAGER` | `mb-harness` | 1 |
| 14 | `PLAN_TASK_EXTRACTOR` | `axel-plan-autopilot` | 1 |
| 15 | `PLAN_STATE_VALIDATOR` | `axel-plan-autopilot` | 1 |
| 16 | `PLAN_PYTHON_EDIT_GUARD` | `axel-plan-autopilot` | 1 |
| 17 | `MANAGER_NEXT_TASK_CHAIN` | `axel-plan-autopilot` | 1 |
| 18 | `MANAGER_ADVANCE_GUARD` | `axel-plan-autopilot` | 1 |
| 19 | `RECEIPT_INTEGRITY_CHECKER` | `axel-plan-autopilot` | 1 |
| 20 | `LEASE_ORPHAN_REPORT` | `axel-plan-autopilot` | 1 |
| 21 | `AGENT_POOL_SNAPSHOT` | `ontocode-agent-pool-supervisor` | 2 |
| 22 | `BOUNDED_AGENT_WAIT` | `ontocode-agent-pool-supervisor` | 2 |
| 23 | `AGENT_RECOVERY_ROUTER` | `ontocode-subagent-recovery` | 2 |
| 24 | `DISPATCH_PACKET_BUILDER` | `ontocode-subagent-recovery` | 2 |
| 25 | `BACKGROUND_JOB_MONITOR` | `mb-harness` | 2 |
| 26 | `TEST_MATRIX_SELECTOR` | `mb-harness` | 2 |
| 27 | `NORMALIZED_TEST_RUNNER` | `mb-harness` | 2 |
| 28 | `BUILD_FAILURE_CLASSIFIER` | `diagnosing-bugs` | 2 |
| 29 | `STATIC_GATE_RUNNER` | `mb-verify` | 2 |
| 30 | `POSTEDIT_VERIFY_DIFF` | `mb-verify` | 2 |
| 31 | `DISK_PRESSURE_TRIAGE` | `axel-disk-space-recovery` | 3 |
| 32 | `PROCESS_PORT_OWNER_REPORT` | `axel-disk-space-recovery` | 3 |
| 33 | `ARTIFACT_CHECKSUM_MANIFEST` | `mb-verify` | 3 |
| 34 | `RELEASE_CONTAINER_PROBE` | `qt-perf-monitor` | 3 |
| 35 | `QT_NATIVE_EVIDENCE_COLLECTOR` | `qt-perf-monitor` | 3 |
| 36 | `BROWSER_UI_EVIDENCE_CAPTURE` | `axel-browser-client` | 3 |
| 37 | `PLAYWRIGHT_FAILURE_TRIAGER` | `axel-debug-playwright-reports` | 3 |
| 38 | `EXCEL_WORKBOOK_INVENTORY` | `excel` | 3 |
| 39 | `ONTOINDEX_FRESH_GATE` | `ontoindex-cli` | 3 |
| 40 | `SKILL_LIFECYCLE_AUDITOR` | `ontocode-session-log-review` | 3 |
