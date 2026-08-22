---
name: ontocode-dev-report
description: Create sanitized, evidence-first incident, diagnostics, workflow, or design-review reports for the Ontocode development team. Use when asked to make, revise, or answer questions about an Ontocode dev-team report from supplied diagnostics, local session-log findings, current source inspection, tool records, and retained artifacts. Use session-issue-diagnostics for diagnosing one specific incident and ontocode-session-log-review for mining a date range; this skill packages their evidence into an engineering-ready report.
---

# Ontocode Dev Report

Turn already-collected evidence into one review-ready Markdown report. Keep
collection, interpretation, and design recommendations visibly separate.

## Routing

- Use `session-issue-diagnostics` to interpret one submitted sanitized
  `/diagnostics` incident.
- Use `ontocode-session-log-review` to analyze rollout logs across a date range.
- Use this skill to consolidate those results, retained artifacts, and verified
  source findings for the Ontocode development team.

Do not duplicate either owner's parser or diagnostic procedure. Do not claim
that assistant-accessible local logs are equivalent to a user-submitted
sanitized `/diagnostics` report.

## Workflow

1. Record the report date, audience, subject, timezone, requested evidence
   window, Ontocode version/build, source commit, model/provider, and relevant
   tool or server versions. Mark unavailable identities explicitly.
2. Inventory evidence before drawing conclusions. Preserve sanitized session
   IDs, turn IDs, timestamps, request IDs, commands, exit statuses, artifact
   paths, and hashes when available.
3. Count genuine human requests only from records that establish user origin,
   preferably `event_msg/user_message` with `origin: client_submission`.
   Exclude injected instructions, environment context, memories, compacted
   summaries, dispatch packets, and quoted prompt copies.
4. Correlate each request with its own assistant messages, terminal event,
   abort record, and artifact writes. Do not infer failure from repeated text
   alone: a re-ask may be a retry, refinement, or request to persist prior work.
5. Classify every material claim using one primary evidence class:
   - `VERIFIED SESSION RECORD`: parsed event or tool records directly establish
     the observation.
   - `VERIFIED ARTIFACT`: a retained report, diagnostic output, source file, or
     validation result directly establishes it.
   - `VERIFIED CURRENT SOURCE`: identified current implementation establishes
     the behavior; note when runtime reproduction remains pending.
   - `UNVERIFIED HISTORICAL`: the observation lacks retained identity or raw
     evidence needed for verification.
   - `DESIGN RECOMMENDATION`: a proposed product, lifecycle, schema, or workflow
     change rather than an observed defect.
6. State the narrowest supported conclusion. A `turn_aborted` reason of
   `interrupted` proves the recorded terminal reason, not whether the user,
   host, provider, or product caused it. Missing output does not prove that
   generation never started unless another record establishes that fact.
7. Separate occurrence counts from affected root sessions and distinct
   requests. Rank recurrence by distinct root sessions first; report delegated
   and unknown origins separately.
8. For every defect claim, include the expected behavior, observed behavior,
   evidence locator, affected identity/window, confidence, and smallest
   reproducible verification step. Label desired tests separately from tests
   actually executed.
9. Sanitize secrets, credentials, private prompt bodies, and irrelevant local
   paths. Quote only short user-authored phrases needed to identify a workflow.
10. Write only the requested report. Do not modify Ontocode source,
    configuration, sessions, diagnostics state, or retained evidence.

## Report Structure

Use this order unless the requester supplies a template:

1. Title, date, audience, subject, and review status.
2. Executive summary.
3. Identity and evidence limitations.
4. Corpus or incident scope and collection method.
5. Evidence-status matrix.
6. Verified findings, ordered by user impact.
7. Unverified historical observations.
8. Design recommendations.
9. Reproduction and regression requirements.
10. Open evidence requests.
11. Final assessment.

Use `EVIDENCE-COMPLETE INCIDENT` only when build identity, raw triggering and
terminal records, relevant artifacts, and postcondition evidence are retained.
Use `PARTIALLY VERIFIED` when some findings are direct but material incident
claims remain unverified. Use `DESIGN REVIEW` when the output is principally a
proposed contract or workflow.

## Finding Format

For each finding, report:

- **Status:** one evidence class, plus an optional qualifier.
- **Impact:** the user-visible or operational consequence.
- **Evidence:** sanitized record or artifact locators and exact timestamps.
- **Assessment:** only what the evidence proves.
- **Verification:** the smallest current-build reproduction or regression test.

When a report corrects an earlier claim, preserve the old claim as historical
context and state why its evidence class changed.

## Validation

For a tracked Markdown report, run:

```bash
git diff --check -- <report-path>
```

For an untracked report, run:

```bash
git diff --check --no-index /dev/null <report-path>
```

Report the command and exit status. Do not claim Ontocode product tests passed
unless they were executed against the identified build.
