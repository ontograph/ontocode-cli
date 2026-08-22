---
name: scaffold-evaluation
description: Evaluate a prompt, skill, memory-policy, or role-prompt candidate against a baseline and record the offline evidence. Use when a scaffold change needs a fixed-task comparison, held-out transfer check, regression accounting, cost comparison, and independent acceptance review.
---

# Scaffold Evaluation

Evaluate one candidate as an ordinary reviewed diff. This skill produces evidence only; it never activates, promotes, or commits the candidate.

## Procedure

1. Identify the baseline and candidate artifacts by repository-relative path and immutable revision or content hash. Stop if either identity is ambiguous.
2. Freeze the task sets before running the candidate:
   - `fixed`: tasks used to verify the intended behavior;
   - `held_out`: curated transfer tasks that were not used to design or tune the candidate.
3. Run the baseline and candidate under the same inputs, environment, model configuration, limits, and deterministic checks. Record unavailable controls as limitations rather than silently changing them.
4. Record success for every task before and after the change. Count regressions only from tasks that passed on the baseline and failed on the candidate.
5. Record aggregate tokens, tool calls, and wall time for both runs. Keep missing metrics explicit.
6. Run the repository's deterministic checks first. Then obtain an independent review from someone other than the candidate proposer. Policy or permission changes also require human review.
7. Write a dated Markdown record using the format below. Accept only when the checks pass, regressions are understood and approved, held-out results support transfer, and the independent reviewer accepts the evidence.

The proposer is never the sole acceptance gate. A candidate remains an inactive, ordinary reviewed diff until the normal review process accepts it.

## Record Format

```markdown
# Scaffold Evaluation: <candidate>

Date: YYYY-MM-DD
Decision: accept | reject | revise

## Artifacts

- Baseline: <path and immutable revision or hash>
- Candidate: <path and immutable revision or hash>
- Proposer: <identity>
- Independent reviewer: <identity>

## Task Sets

- Fixed: <task identities>
- Held-out: <curated task identities and confirmation they were not used for tuning>

## Results

| Set | Task | Baseline success | Candidate success | Regression |
| --- | --- | --- | --- | --- |
| fixed | <id> | pass/fail | pass/fail | yes/no |

## Cost

| Metric | Baseline | Candidate | Delta |
| --- | ---: | ---: | ---: |
| Tokens | <value or unavailable> | <value or unavailable> | <value or unavailable> |
| Tool calls | <value or unavailable> | <value or unavailable> | <value or unavailable> |
| Wall time | <value or unavailable> | <value or unavailable> | <value or unavailable> |

## Checks

- Deterministic checks: <commands and results>
- Previously passing regressions: <count and task ids>
- Limitations: <missing controls or metrics>

## Independent Review

- Reviewer decision: accept | reject | revise
- Rationale: <evidence-based reason>
- Human review for policy or permissions: required/not-required and result
```

The record is complete only when every field is populated or explicitly marked unavailable, every baseline pass has a candidate result, and the independent-review decision is recorded.
