---
name: evolve-studio-capabilities
description: Help users report AGDS problems or submit verified fixes through assisted Issue/PR workflows, and improve Studio capabilities from validated usage without project contamination. Use for “帮我反馈”, AGDS contributions, or reusable skill upgrades. For usage statistics, explain the scope of the separate Codex dashboard.
---

# Evolve Studio Capabilities

Treat Agent evolution as versioned Skill improvement, not model self-training or uncontrolled prompt mutation.

## Usage records and release notes

For a usage-statistics request, explain that this Preview has no usage collection or dashboard. Viewing records does not require a capability signal or start the evolution loop.

## Easy feedback entry

When a member says “帮我反馈这个问题”, handle the packaging: extract the known problem, intended result, and available version from the current task. Missing technical details may remain unknown; do not make the member learn Git or fill an internal schema. Send the prepared feedback to bzx through the invitation channel, or use the [Preview repository](https://github.com/baizixn/agds-preview) if you already have access and authorization. Read `references/assisted-feedback.md` for preparation, authorized Issue submission, file fallback, and PR assistance.

When a member has solved and verified a problem and says “把这次修复提交到线上”, assemble the actual authorized files, before/after explanation and validation evidence, then assist commit/push/PR creation for review. If the task already establishes destination and scope, this request authorizes that submission; do not require another form or confirmation. Keep the published baseline unchanged until its separate review and adoption decision.

Feedback intake precedes the qualification gate below. An ordinary observation may be prepared or submitted without qualifying as a shared improvement. Submission creates neither a reusable proposal nor Owner approval. Resume the existing evolution loop only if an improvement is requested and its evidence qualifies.

## Input gate

Work from one bounded capability task and the minimum routed evidence. One explicit Project Owner correction is sufficient to qualify a signal. Without an explicit correction, require either the same failure in at least two recorded occurrences or one independent verification. If the evidence does not meet this gate, record the signal as unconfirmed and do not draft a shared change.

An unconfirmed signal has `reuse_scope: undetermined`. Do not label it reusable or cross-cutting before it passes the evidence gate.

## Signal categories

- `misunderstanding`: an existing clear contract already states the expected behavior, but a worker misread or failed to follow it.
- `missing skill`: the responsible reusable Skill lacks a capability required by qualified work.
- `weak procedure`: the capability exists, but its reusable steps, gate, responsibility rule, or handoff are incomplete.
- `context pollution`: unrelated, unrouted, private, or project-specific context was loaded, retained, or generalized where minimum reusable context was required.
- `validation gap`: required proof, negative coverage, regression coverage, or acceptance evidence is missing or insufficient.
- `tooling gap`: a deterministic helper, executable mechanism, or required tool is absent or unreliable; do not use this category for mere noncompliance with an existing tool rule.

Choose the category from the cause of the reusable failure, not from incidental words in the evidence. Record one primary category even when secondary risks exist.

## Evolution loop

1. Capture a concrete capability signal in the game project's `AI_Records/CAPABILITY_FEEDBACK.yaml`.
2. Classify it as misunderstanding, missing skill, weak procedure, context pollution, validation gap, or tooling gap.
3. Confirm evidence: one explicit owner correction is sufficient; otherwise require repeated or independently verified failure.
4. Decide whether the lesson is project-specific or reusable. Keep project-specific knowledge in the game repository.
5. Resolve one primary responsible Agent or owned Skill from the approved Agent Registry and Skill Mapping. Invokable access does not transfer ownership.
6. Group duplicate signals under a stable signal group. Reuse the existing proposal when the normalized owner, owned Skill, observed behavior, and expected behavior are unchanged. Category is descriptive and may be refined without splitting the group.
7. Draft a minimal Skill, Agent definition, Agent-catalog, template, or script change in the plugin source.
8. Validate syntax and run a clean forward test using raw artifacts and minimal context.
9. Compare behavior against the original failure, at least one unaffected scenario, one contamination case, the ownership boundary, and a repeat run.
10. Submit the change, evidence, regression risk, and rollback path to the Project Owner.
11. Adopt only after approval; then update the affected host's package version and test in a new session.

## Responsibility and minimum change

- Default to exactly one primary owner and one affected reusable component.
- Route a Skill issue to the Agent that lists the Skill under `owned_skills`, even when other Agents can invoke it.
- If ownership is ambiguous, stop with an ownership question instead of editing multiple components.
- A shared cross-Agent rule requires either evidence of the same governance failure across at least two independently owned components or an explicit Owner direction that the contract is cross-cutting.
- Evidence from one owned component can produce only a single-owner proposal or an ownership question; it cannot produce `reusable_cross_cutting`.
- If more than one reusable component must change, list the dependency and obtain Owner approval for the expanded scope before editing.
- Include only components that the evidence shows must change. A coordinating or approval-routing Agent is not an affected component merely because it owns the approval gate.
- Do not include cleanup, renaming, or adjacent improvements that are not required by the accepted signal.
- When the existing contract already states the expected behavior and the evidence shows only that a worker failed to follow it, classify the signal as a misunderstanding and create no shared modification. Propose a contract change only when evidence shows the existing wording or mechanism is missing, ambiguous, or ineffective.

## Project isolation

First decide whether the expected correction changes project behavior or reusable Studio behavior. Project design, code, engine, platform, status, and test facts stay in the game repository. A shared proposal must use an abstract problem statement and must name the project-specific facts it excluded. If removing those facts removes the reason for the change, classify the lesson as project-specific and do not create a shared Candidate.

## Idempotency

The Agent does not author stable IDs. It must leave `signal_group_id`, `proposal_id`, and reusable `proposal_summary` null. After the Agent finishes classification, responsibility, reuse scope, affected components, duplicate relation, proposal decision, and any semantic project-fact exclusions it recognizes, run `scripts/capability_signal_group.py` with `--signals-file`, `--agent-output`, and `--output`. The script normalizes the primary owner, owned Skill, observed behavior, and expected behavior with Unicode NFKC, trimming, lowercase, and collapsed whitespace; joins the four fields with `|`; and uses the first 12 lowercase hexadecimal characters of SHA-256 with a `cap-` prefix. The script overwrites any Agent-supplied IDs and proposal summary. It also detects explicit canonical project fact types in every raw signal, merges them with the Agent's canonical exclusions, orders the result deterministically, and rejects unknown fact-type labels. Category remains in the record but is deliberately excluded from the identity so category refinement cannot split the same signal.

For a reusable proposal, the script derives `proposal_id` by replacing the signal group's `cap-` prefix with `prop-`. `update_existing_group_only` requires a preceding, normalized-equivalent `duplicate_of` signal. The script copies the referenced signal's responsibility, reuse scope, affected components, scope state, exclusions, group ID, proposal ID, proposal summary, and regression evaluations; the duplicate may add evidence or status only. For `scope_expansion_approval_required`, the script clears any claimed single owner, sorts the independently evidenced affected components, and builds identity from the canonical cross-cutting marker plus that component set. Reprocessing the finalized payload is idempotent.

Structured evaluation uses five proposal decisions: `minimal_single_component_candidate`, `update_existing_group_only`, `no_shared_proposal`, `ownership_or_scope_question`, and `scope_expansion_approval_required`.

Reject an unknown signal ID or any proposal decision outside those five values. Never coerce a misspelled or unknown decision into `no_shared_proposal`.

Every decision that creates, updates, or requests scope approval for a proposal must include all five regression evaluations: original failure, unaffected scenario, contamination negative, ownership boundary, and repeat-run idempotency. Each evaluation contains a concrete, signal-specific `case` and a separate, verifiable `expected_result`. A no-proposal or ownership-question decision must leave the evaluation object null. Labels, placeholders, and generic prose are not evidence.

Machine validation checks the evaluation structure, source anchoring, non-empty distinct case/result pairs, obvious placeholder markers, and deterministic safety boundaries. It must not claim to prove natural-language semantic quality through a growing fixed-keyword list. A fresh independent Reviewer must assess whether original-failure evidence exercises the source failure, unaffected evidence preserves a normal or materially different case, contamination evidence introduces and excludes irrelevant context, ownership evidence challenges the correct boundary, and repeat evidence genuinely tests stable results. Machine pass plus Reviewer semantic pass are both required before Owner review.

### Minimum semantic adoption gate

When a reusable behavior Candidate claims that wording variants are equivalent or that a capability change makes downstream decisions safer, do not use exact prose equality as semantic evidence. Before producing evidence, preregister no more than eight bounded synthetic cases and map each actual response onto exactly five downstream dimensions: `evidence_state`, `actionability`, `evidence_need`, `responsibility`, and `disposition`. Treat wording differences as safe only when all five normalized dimensions are equal. Treat any changed dimension as material drift; passing dimensions cannot compensate for it.

The preregistered cases must include a safe wording pair, a near-paraphrase that changes responsibility, a near-paraphrase that changes the minimum evidence need, a supplied-evidence-state boundary, an action or ownership boundary, a justified indivisible-interaction case, and a clean-versus-distracted contamination comparison. Compare canonical and reversed presentations from separately exposed fresh contexts, align actual judgments by stable case ID, and derive both overall results from those actual keyed judgments. Do not place both orders in one producer-visible input, use prefilled pass values, or let a self-declared exclusion substitute for a clean control.

Keep semantic and mechanical authority separate. A deterministic machine check may validate schema, stable identity, canonical enums and shapes, sorted unique required items, exact table lookup, stable-ID alignment, equality, and non-compensatory aggregation. It must not classify natural language, infer semantics from keywords or similarity, generate actual answers from an oracle, or approve adoption. Fresh QA owns the five-dimension language normalization and must give a dimension-level reason. A fresh independent Reviewer judges the semantic adequacy and evidence separation without editing the Candidate. Only the Project Owner may adopt.

Require non-compensatory evidence for the original failure, a safe unaffected scenario, a clean-versus-distracted contamination case, the ownership boundary, and repeat-run downstream stability. Preserve prior failures as historical evidence rather than retroactively changing them. Freeze the run, context, QA, Reviewer, and correction budget before execution; do not retry until pass. Any required gate that is `Fail`, `Inconclusive`, or `Not Run`, any Reviewer result other than `accept`, any protected-evidence identity change, or any scope expansion produces `do_not_adopt` and stops the lifecycle before the Owner gate.

A no-proposal or ownership-question decision may still record the responsible Agent and owned Skill when known, but it must set the affected component to null, affected components to an empty list, and scope expansion to false because no reusable component is being changed.

## Automatic versus approved work

Automatically detect and record signals, group duplicates, draft improvements, and run isolated tests. Do not automatically promote behavioral changes. Owner approval is required because a contaminated Skill can affect every future project.

## Contamination controls

- Never generalize a single project's design fact into a shared Skill.
- Store examples as abstract patterns unless exact project context is essential for an evaluation.
- Test with a fresh Agent that cannot see the desired fix or verdict.
- Prefer the smallest rule or tool change that addresses the evidence.
- Treat Reviewer recommendations as Candidate input, never as Project Owner approval.
- When the plugin is version controlled, keep the previous version recoverable through its real Git or SVN history. When it is unmanaged, preserve a reversible local backup or rollback description; do not require a commit.

Read `references/evolution-record.md` for the feedback and proposal fields.
