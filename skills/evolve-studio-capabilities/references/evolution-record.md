# Evolution record

## Capability signal

- `id`
- `signal_group_id`
- `date`
- `project`
- `agent_or_skill`
- `category`
- `observed_behavior`
- `expected_behavior`
- `evidence`
- `owner_correction`
- `evidence_eligibility`: `owner_correction`, `repeated`, `independently_verified`, or `unconfirmed`
- `responsible_agent`
- `responsible_owned_skill`
- `ownership_basis`
- `reuse_scope`: `undetermined`, `project_specific`, `reusable_single_owner`, or `reusable_cross_cutting`
- `duplicate_of`
- `status`

## Improvement proposal

- `proposal_id`
- `signal_group_id`
- `affected_reusable_component`
- `responsible_agent`
- `generalizable_problem_statement`
- `excluded_project_specific_facts`
- `minimal_proposed_change`
- `scope_expansion`: affected dependencies and approval state, or `none`
- `original_failure_evaluation`
- `unaffected_scenario_regression_evaluation`
- `contamination_negative_evaluation`
- `ownership_boundary_evaluation`
- `repeat_run_idempotency_evaluation`
- `risks_and_rollback`
- `review_status`
- `owner_approval`: `not_decided`, `approved`, `revise`, `rejected`, or `deferred`
- `adopted_plugin_version`: empty until approved and deployed

## Stable grouping rule

The Agent must leave `signal_group_id`, `proposal_id`, and reusable `proposal_summary` unset. Finalize the record with `scripts/capability_signal_group.py --signals-file <raw.json> --agent-output <agent.json> --output <final.json>`. The script overwrites IDs and summaries from the normalized primary owner, owned Skill, observed behavior, and expected behavior. Category is recorded but excluded from identity so a category correction does not split an otherwise identical group. Repeated evidence updates the existing group and must not create a second proposal while the affected component and expected correction remain unchanged.

## Proposal gate

Do not create a shared improvement proposal when `evidence_eligibility` is `unconfirmed` or `reuse_scope` is `project_specific`. Do not leave `excluded_project_specific_facts` blank when the source evidence came from a game project. More than one affected reusable component requires an explicit `scope_expansion` approval before editing.

For structured evaluation, use the stable Skill identifier, such as `review-candidate`, as `affected_reusable_component`. An unconfirmed signal must use `reuse_scope: undetermined`. List each project fact type present in the input under `excluded_project_specific_facts`; do not replace the list with a generic statement. Apply this check to every signal, not only signals already classified as context pollution or project-specific.

During finalization, the deterministic helper scans every raw signal for explicit canonical project fact types and merges them with the Agent's canonical list. This is a minimum safety net for missed explicit types, not permission to skip semantic contamination analysis. Unknown fact-type labels fail closed.

The script derives `proposal_id` by replacing the related `signal_group_id` prefix `cap-` with `prop-`. Duplicate signals receive the referenced proposal ID and proposal summary and may only add evidence or update signal status.

`update_existing_group_only` is invalid without a preceding normalized-equivalent `duplicate_of`. Finalization copies all stable responsibility, scope, component, exclusion, identity, summary, and regression fields from the referenced proposal so a duplicate cannot widen or redirect the change.

Use one of these `proposal_decision` values:

- `minimal_single_component_candidate`
- `update_existing_group_only`
- `no_shared_proposal`
- `ownership_or_scope_question`
- `scope_expansion_approval_required`

Finalization must fail closed for any other decision value or any signal ID absent from the routed raw input.

For reusable proposals, the script sets `proposal_summary` to the normalized reusable `expected_behavior`. This keeps repeat runs and duplicate grouping comparable without embedding an answer key for individual signals.

Structured behavior evidence stores the five evaluation fields together under `regression_evaluations`. Each evaluation is an object with a concrete signal-specific `case` and separate verifiable `expected_result`; repeating only the field name, a placeholder, or generic prose is invalid. `minimal_single_component_candidate`, `update_existing_group_only`, and `scope_expansion_approval_required` require this object. `no_shared_proposal` and `ownership_or_scope_question` require null. Duplicate finalization copies the original proposal's evaluation object.

The machine gate validates structure and deterministic invariants but does not approve natural-language semantics. A fresh independent Reviewer must read every proposal-bearing evaluation and explicitly pass or fail its five semantic purposes. The Project Owner receives the Candidate only after both gates pass.

When no proposal is created or ownership remains a question, `affected_reusable_component` is null, the affected-components list is empty, and scope expansion is false. Responsibility fields may remain populated when the owner is known; they identify the source boundary, not a planned modification.

For a cross-cutting scope request, no single responsible Agent or owned Skill is recorded before approval. Finalization sorts the evidenced affected-component set and uses a canonical cross-cutting identity plus that set, so coordinator selection cannot change the signal or proposal ID.
