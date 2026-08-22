---
name: ontoindex-dev-report
description: Create evidence-first incident, defect, lifecycle, or design-review reports for the OntoIndex engineering team. Use when asked to report findings to OntoIndex developers, revise an OntoIndex incident report, separate current-source defects from historical observations, or prepare engineering review material from diagnostics, session logs, source inspection, and proposed contracts.
---

# OntoIndex Dev Report

Turn supplied findings and artifacts into one review-ready Markdown report.
Do not diagnose a specific runtime incident from scratch when
`session-issue-diagnostics` owns that work, and do not perform longitudinal log
mining when `ontocode-session-log-review` owns it.

## Workflow

1. Record the report date, audience, subject, package/build identity, repository
   identity, source commit, and MCP server identity when available. State every
   missing identity explicitly.
2. Inventory the supplied evidence before drawing conclusions. Preserve raw
   request IDs, timestamps, job IDs, digests, generation IDs, and sanitized
   artifact paths.
3. Verify current-source claims against the identified implementation. Cite
   package version plus file, symbol, and line. Treat deterministic control flow
   as source evidence even when runtime reproduction is pending.
4. Classify each claim using exactly one primary evidence class:
   - `VERIFIED CURRENT SOURCE`: current implementation establishes the behavior.
   - `VERIFIED CURRENT RUNTIME`: an identified build reproduced the behavior
     with retained raw artifacts.
   - `UNVERIFIED HISTORICAL`: reported behavior lacks enough preserved evidence
     to verify the historical incident.
   - `DESIGN DECISION`: proposed lifecycle, recovery, authority, or API policy.
5. Add a qualifier such as `RUNTIME REPRODUCTION PENDING` when useful, but do
   not downgrade deterministic current-source evidence merely because a live
   reproduction is absent.
6. Separate unlike state dimensions. For managed analysis, report submission
   outcomes, job phases, and recovery outcomes independently. Never describe
   `SUBMISSION_FAILED` or `LOCK_CONFLICT` as job states when no durable job
   exists.
7. Challenge proof claims:
   - Process exit success does not prove publication or freshness.
   - Observing active metadata does not prove which job published it.
   - Job completion does not replace a capability-aware final freshness check.
   - Historical observations do not become current defects without source or
     identified-runtime evidence.
8. Require publication proof to use an analyzer-produced receipt bound to job
   ID, repository identity, target HEAD, options digest, source-manifest digest,
   generation ID, analyzer contract version, and publication timestamp.
9. Define focused regression requirements for every verified source gap and
   every preserved historical scenario. Keep unreproduced historical cases as
   regression requirements, not verified defects.
10. Write or revise only the requested report. Do not modify OntoIndex product
    code, lifecycle state, locks, jobs, or active-generation metadata.

## Report Structure

Use this order:

1. Title, date, audience, and status.
2. Executive summary.
3. Evidence classes and identity limitations.
4. Evidence-status matrix.
5. Current-source findings with citations.
6. Current-runtime findings with raw artifact references.
7. Unverified historical observations.
8. Proposed contract decisions.
9. Required regression coverage.
10. Evidence needed for incident-level verification.
11. Final assessment and recommended review status.

Use `DESIGN REVIEW / PARTIALLY VERIFIED` when source findings are verified but
the historical incident lacks complete artifacts. Use `EVIDENCE-COMPLETE
INCIDENT` only when the identified runtime, raw requests and responses,
lifecycle records, publication proof, and final postcondition evidence are all
preserved.

## Managed-Analysis Vocabulary

When relevant, keep these dimensions separate:

- Submission outcomes: `SUBMITTED`, `SUBMISSION_FAILED`, `LOCK_CONFLICT`.
- Job phases: `QUEUED`, `RUNNING`, `PUBLISHING`, `CANCELLED`, `STALLED`.
- Recovery outcomes: `REFRESHED`, `RECOVERY_BLOCKED`, `FAILED`,
  `FRESHNESS_UNCONFIRMED`.

Use `FAILED` for submission, execution, or publication failure. Use
`FRESHNESS_UNCONFIRMED` when execution and apparent publication finish but the
required publication receipt or final authority postcondition cannot be proven.

## Validation

For a new untracked report, run:

```bash
git diff --check --no-index /dev/null <report-path>
```

For a tracked report, run `git diff --check -- <report-path>`. Report the actual
exit status and whether the file is tracked. Do not claim product tests passed
unless they were executed against the identified OntoIndex build.
