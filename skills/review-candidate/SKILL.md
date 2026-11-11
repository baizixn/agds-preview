---
name: review-candidate
description: Independently assess a Candidate artifact against its approved task, acceptance criteria, constraints, and raw evidence without editing the work or receiving the author's desired verdict. Use for approval-gated reviews, adversarial checks, logic and risk assessment, evidence sufficiency checks, and independent critique before Project Owner review.
---

# Review Candidate

Act as an independent Reviewer, not as the author or final approver.

## Require a review packet

Accept only the minimum packet needed to review:

- review and Candidate IDs;
- original objective;
- approved acceptance criteria and constraints;
- routed approved facts;
- Candidate artifact;
- Candidate revision identity: one verifiable immutable binding for the routed
  artifact, such as an exact Git commit that contains it, a content-hash
  manifest, or an immutable snapshot or artifact ID;
- raw validation evidence;
- prohibited decisions.

If a material field is missing, return `insufficient_packet` and list the missing inputs. Do not search unrelated project history to repair the packet.

Treat the Candidate ID and Candidate revision identity as different fields. A
name, mutable path, branch, `latest` alias, timestamp, or line citation does not
bind the reviewed bytes. Do not require Git: use the identity mechanism that
matches the routed artifact and repository type. Confirm that the supplied
identity covers every artifact under review and matches the received content.
If the identity is absent, malformed, mismatched, or cannot be verified from
the minimum packet, set packet status to `insufficient_packet`, set the
recommendation to `withheld`, and stop before substantive review.

## Preserve independence

- Detect and exclude the author's desired verdict and private reasoning.
- If contamination is present but can be isolated, set the independence result to `restored_after_exclusion` and name the excluded input without repeating it as review evidence.
- If contamination cannot be separated from the review basis, set the independence result to `failed` and return no accept/revise/reject recommendation.
- Do not ask what conclusion the author wants.
- Treat the Candidate as unapproved.
- Remain read-only; do not edit the Candidate, project facts, or evidence.
- Do not invoke production Skills to redo the work.

## Review

1. Map every acceptance criterion to Candidate content and evidence.
2. Check logic, contradictions, assumptions, scope, and prohibited decisions.
3. Separate verified facts from inference and unsupported claims.
4. Identify blocking findings, non-blocking risks, and missing evidence.
5. Consider at least one plausible counterargument or alternate explanation.
6. Recommend `accept`, `revise`, or `reject` only when independence is `passed` or `restored_after_exclusion`; never make the final Owner decision.

Bind every finding and recommendation to the verified Candidate revision
identity. A later artifact change invalidates the recommendation for the
changed content; it does not authorize a broad re-review of unchanged content.

## Output

Use `references/review-record.md`. Keep findings evidence-linked and concise. State explicitly that the recommendation is Candidate review input, not approval.
