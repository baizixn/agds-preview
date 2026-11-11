# Candidate review record

Use this format for independent review output.

```markdown
# Candidate Review

- Review ID:
- Candidate ID:
- Candidate revision identity: method + immutable value + covered artifact(s)
- Identity verification: matched | mismatched | not_verified
- Reviewer Agent: reviewer
- Independence check: passed | restored_after_exclusion | failed
- Excluded contaminating inputs: none | list input labels
- Packet status: complete | insufficient_packet
- Recommendation: accept | revise | reject | withheld
- Approval status: not_decided

If identity verification is `mismatched` or `not_verified`, packet status is
`insufficient_packet`, recommendation is `withheld`, and no substantive
acceptance-criteria judgment follows.

## Acceptance criteria

| Criterion | Result | Evidence | Notes |
| --- | --- | --- | --- |

## Blocking findings

- None, or evidence-linked findings.

## Non-blocking risks

- None, or evidence-linked risks.

## Missing evidence

- None, or specific missing evidence.

## Counterargument or alternate explanation

- At least one plausible challenge to the Candidate conclusion.

## Scope and permission check

- Confirm the review remained read-only and within routed context.

## Owner decision required

This recommendation is Candidate review input. It is not final approval or rejection.
```
