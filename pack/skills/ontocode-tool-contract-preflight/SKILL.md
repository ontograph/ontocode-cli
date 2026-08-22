---
name: ontocode-tool-contract-preflight
description: Run a read-only preflight of Ontocode's required tool contract before substantive work. Use when injected instructions name unavailable tools, lean-ctx or hook routes fail, skill or workspace paths are unauthorized, Node or OntoIndex commands are missing, a model switch may have stale tool schemas, repeated tool calls fail before repository work begins, or an Axel native command is blocked before product code runs. Enforce product defect separation before source diagnosis.
---

# Ontocode Tool Contract Preflight

Verify that required instructions can be executed with the tools actually exposed in the current session.

## Workflow

1. Extract the tool names and command prerequisites required by active system, hook, skill, and repository instructions.
2. Compare them with the current callable tool surface. Treat aliases as equivalent only when their contract proves the same operation.
3. Run bounded read-only probes for the paths and executables needed by the task:
   - Workspace-relative and required installed-skill reads.
   - The documented lean-ctx route or callable replacement.
   - `node`, `npm`, and `ontoindex` only when the task needs them.
   - Repository validators or manager tools named by the requested workflow.
4. Classify mismatches:
   - `MISSING_TOOL`: required callable is absent.
   - `STALE_ROUTE`: tool exists but the active schema or route is obsolete.
   - `PATH_DENIED`: a required authorized path cannot be read.
   - `HOOK_CONFLICT`: a hook blocks the only advertised compliant route.
   - `MISSING_EXECUTABLE`: a required command is not on the effective path.
   - `CONTRACT_ERROR`: tool arguments or response shape contradict documented use.
5. Select the smallest documented fallback that is currently callable. Verify it with one harmless probe before substantive work.
6. If no compliant route exists, fail the affected step clearly. Continue unrelated read-only work when possible.

## Product Defect Separation

Before reporting a Rust, C++, Qt, or LibreOffice defect, prove that the intended
compiler, test, or application process started. A denied path, missing tool,
hook conflict, stale route, or policy rejection is a tooling outcome, not a
native product failure.

- Return the mismatch classification and the blocked product command.
- Retry only through one verified documented fallback.
- Resume the owning execution or diagnosis skill after the fallback works.
- Route a specific runtime, MCP, model-stream, dynamic-tool, or aborted-turn
  incident to `session-issue-diagnostics`; keep longitudinal pattern analysis in
  `ontocode-session-log-review`.

## Boundaries

- Keep preflight read-only. Do not edit hooks, global configuration, PATH initialization, plugin manifests, or tool registries unless the user explicitly requests a fix.
- Do not repeatedly call a route already proven absent or permanently denied.
- Do not claim a fallback is equivalent without testing the required path and operation.
- Do not turn a session tool mismatch into a repository blocker.
- Redact environment values, credentials, provider URLs, and unrelated filesystem details.

## Output

Return `READY`, `DEGRADED`, or `BLOCKED` for the requested workflow, followed by required versus available tools, successful probes, mismatch classifications, the selected fallback, and the exact step that cannot proceed. Keep product defects separate from caller errors and repository failures.

## Routine Tool Ownership

This skill owns routine-tool operations 6-8 in
`~/.ontocode/skills/ontocode-routine-tools/references/tool-catalog.md`. Keep
runtime probes deterministic, classify transport/config mismatches separately
from product defects, and return the coordinator's shared envelope for new tool
implementations.
