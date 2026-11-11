---
name: studio-orchestrator
description: Coordinate cross-discipline game-development work when it needs shared context, dependencies, or synthesis across professional Skills. Use for an explicit coordination request or a task requiring that coordination; ordinary bounded work may use its professional Skill directly.
---

# Studio Orchestrator

Use this coordination capability when the task needs it. Ordinary bounded work may use the relevant professional Skill directly, with native planning and tools. Keep the project owner in control; select specialist help only when it improves the result. An explicit project requirement for coordination still applies.

## Start

1. Locate the target repository and read its `AGENTS.md`.
2. Read `AI_Records/PROJECT_STATE.md`, `AI_Records/ACTIVE_TASKS.yaml`, and only the context mapped for the requested task.
3. If the repository has no `AI_Records/`, follow `references/project-contract.md`; do not silently create a second state system.
4. Classify the request as answer, proposal, execution, review, or approval response.
5. When the Project Owner corrects or extends the active goal, restate the correction in plain language and label it as adding to, narrowing, or replacing the approved goal. Retain every prior obligation unless the Owner explicitly narrows or replaces it.
   - If a correction affects already delegated work, actually relay it to the affected executor through an authorized channel and check observable handling status. Distinguish successful sending from actual handling, and report failed transmission or pending/unconfirmed handling without claiming the correction has been applied.

## Task learning

When the user identifies an existing result below the requested bar, or an actual check shows a key problem remains, and no remedy has been verified for that problem, read and apply [task learning](references/task-learning.md) before further production. Route the question to the responsible professional owner and reuse their applicable verified experience; coordination does not replace their judgment. Familiar small repairs with a verified remedy proceed directly. Keep the source, decision, attempt and check in the existing task record.

## Coordinate

1. Create or update one bounded task.
   - Work backward from the user's observable acceptance result to the deliverable and actions. Include both that result and the necessary technical checks in task acceptance; completing a supporting artifact or local check does not complete the user's objective.
   - Before dispatch, distinguish direction-setting choices from ordinary implementation freedom. Preserve each material choice's source and adoption state: Owner decision, sourced constraint, Agent proposal, or unknown. Evidence can support a choice without establishing Owner adoption; do not relay an Agent proposal as an Owner-approved requirement.
   - Give necessary research or tool-support work a bounded question, an exit condition, and the main task it returns to. Stop or change the supporting approach when that condition is reached, then resume the authorized delivery or report the specific unresolved dependency.
   - If the task cannot deliver the requested result or treats an unadopted direction as settled, rewrite it before sending. Ask only for a missing decision that materially changes direction; preserve ordinary implementation freedom, explicit original-work authority, and authorized small repairs under the Owner interaction rules.
   - For a feature-bearing stage, route the shared Experience Trace through Producer using `produce-game-project`. Orchestrator validates that every proposed feature points to an approved player promise and that each professional column has a responsible owner; it does not author specialist conclusions or make Producer the owner of those conclusions.
   - When a routed Experience Quality Contract names a material professional review checkpoint, route one bounded critique task to each affected owner against the exact contract, artifact, context, and evidence cutoff. Return each contribution and disagreement to Game Design for integration without editing, averaging, or approving it. Reuse the stable unresolved-gap identity instead of issuing duplicate tasks.
2. Select the smallest useful set of specialist skills.
3. Delegate independent specialist work only when it improves the result. Ordinary native delegation does not require formal-role deployment evidence or a compatibility packet; never use a role-like `task_name` as a substitute for a formal Agent identity. Use the runtime role gate below only for an explicit formal-role verification or deployment claim. Before delegated mutation, resolve the exact target repository root, the separate contract root when using AGDS contracts, the worker's responsibility, and every absolute output path. Verify each output against the task allowlist and target root, and stop without delegation on any mismatch. Do not impose this mutation-only output preflight on a read-only task that creates no output.
   - When routing or transferring work, follow the actual deliverables and triggering responsibilities rather than conversation titles. For each deliverable, identify one current execution owner and its recipient; collaborators and reviewers do not become additional execution owners. For a partial transfer, preserve each affected item's completed and unfinished work, evidence limits, and next action in the existing handoff format. Confirm the authorized scope and recipient acceptance before treating the transfer as effective. Once confirmed, the old entry retains history and stops duplicate production for the transferred portion; untransferred work stays with its current owner. Renaming an entry or sending a notification establishes neither transfer, authority, nor receipt. Keep genuinely indivisible interactions together under one execution owner with bounded specialist contributions; ordinary single-specialist work does not need a split or a new handoff form.
4. Keep incomplete outputs in Working and proposals in Candidate state. Neither label blocks implementation, testing, or the next authorized repair; completion is separate from formal adoption.
5. Check the changed behavior and relevant regressions before handing work back. Use the Owner interaction rules below to select proportionate review; routine fixes do not require a separate QA/Reviewer chain. For material work, route a minimum review packet to `review-candidate` at a coherent delivery checkpoint, without the author's intended verdict or private reasoning.
   - If QA routes a material native, expert, human, or player evidence gap before Reviewer entry, upgrade the User Visibility Contract to one bounded `checkpoint_required` request. Bind it to the exact checkpoint, claim, contract, artifact/build, environment, evidence role, privacy-minimized participant identity, allowed steps, exit condition, and prohibited conclusions. Completion, refusal, unavailability, or mismatch each ends the request; unresolved evidence proceeds honestly to Reviewer and does not trigger repeated automation or an infinite participation loop.
6. Continue authorized repairs and relevant checks. Two rounds means two cause-based corrections of the same blocker, not two files, commits, or total task edits. If it remains unresolved after two rounds, or the attempts yield no new useful evidence, pause the current failed approach. Check the original assumptions, actual results and both failures; revisit necessary source or reliable references and change method. Seek a bounded independent opinion when useful, not as a mandatory review chain. New evidence can justify a finite next step within existing authority. Renaming the task, rewording the error or slightly varying the same failed approach does not reset the limit. If no viable method remains, or scope, architecture tradeoffs, cost, authority or quality must change, ask the Owner for that specific decision. Preserve failures and limitations; continue unrelated authorized work.
7. Report the result, evidence, and remaining gaps at the agreed checkpoint. Ask the Owner only for an unresolved decision, not to reconfirm ordinary completed work or authorize its next in-scope step.
8. Promote to Approved or change approved directional facts only with explicit Owner authority, including an existing authorization that covers the exact action and scope. Do not manufacture an Owner decision from a successful test or Reviewer recommendation.

## Ordinary task lifecycle memory

For ordinary bounded work, keep a compact result in the current task: changed outputs, relevant checks, and remaining limitations. Do not require a separate Project Memory Agent or a `start -> handoff -> close` stream merely to complete a repair.

For an actual handoff, cross-session recovery, or an explicit project recording requirement, use `manage-project-memory` to preserve the objective, verified inputs, outputs, evidence, risks, and next action in the existing project format. Its event profile applies when the project uses that format; do not duplicate the same information in another ledger. Preserve existing records, path bases, and explicit Owner decisions. Complex record repair still requires the Skill's repair safeguards. Task completion and Reviewer recommendations never create Owner approval.

Before a long-running or tool-visible task begins, record the compact User Visibility Contract in `references/experience-routing-and-visibility.md`: whether work is isolated in the background or visibly controls a surface, whether the user must participate, and when the next screenshot, playable result, or other observable checkpoint will be returned. Report exact time or token telemetry only when available; otherwise mark it `unknown`.

For isolated checkpoint-state and repeat validation, use `scripts/route_bounded_evidence_checkpoint.py` on one explicit JSON packet. It can open exactly one request, preserve a repeated request as the same checkpoint, or close it once on observation, refusal, unavailability, or the declared exit condition. It never writes the QA evidence result, Reviewer recommendation, or Owner decision.

## Runtime role gate

Apply this section only when the task explicitly requires formal-role identity, installed-version pickup, or strict runtime-isolation evidence. It is not a prerequisite for ordinary native delegation. A generic worker can deliver useful work without establishing any of those claims.

Read the role IDs in `../../Agent_System/Agent_Registry.yaml`. This bundle supplies professional role contracts in `../../roles/`. Use the actual Harness tool catalog and, when a fresh child is supported, supply the absolute installed plugin directory and assign one of these contracts explicitly and record its assigned role. Do not infer a registered native agent, role deployment, or runtime isolation from an assigned contract, a task name, or self-report. Native preset registration and a per-role sandbox are not provided by this bundle.

For independent review, use a fresh session with the effective Harness permission policy confirmed to be read-only and verify the available tools. If isolation is part of the requested evidence and cannot be verified, mark it inconclusive.

## Reuse validated evidence

For a bounded revision, map each acceptance claim to its existing evidence before scheduling new work.

1. Reuse evidence only when its relevant identity, approved input contract, artifact integrity, environment, tool and runtime provenance remain unchanged and the evidence is still sufficient for the claim.
2. Record a reuse and invalidation map. Name which claims retain evidence, which changed dimension invalidates evidence, and why.
3. Repair the smallest affected surface. Use a discriminating sentinel or negative case that would fail under the previous behavior instead of repeating an unchanged broad suite by default.
4. Rerun only invalidated evidence dimensions. A changed Agent identity, approved input, artifact, environment, tool, runtime version or evidence-integrity basis requires fresh proof for that dimension.
5. Give `review-candidate` the affected artifact or diff, acceptance criteria, reuse and invalidation map, and fresh raw evidence. Do not resend unrelated history or rerun an expensive attribution chain merely to review an unchanged claim.
6. Never use reused evidence to cover a changed surface, a broader claim, or a different evidence level. Escalate when reuse validity is uncertain or the cheaper path would weaken acceptance confidence.

## Improve Studio capability

After a task, detect explicit owner corrections, repeated agent failures, avoidable context load, missing skills, and validation gaps. Record a capability signal instead of silently mutating behavior. Invoke `evolve-studio-capabilities` when the evidence suggests a reusable improvement. Automatically draft and test the improvement, but require owner approval before changing the shared plugin baseline.

## Prevent contamination

- Treat Approved project documents as facts; treat Working, Candidate, chat history, and agent records as untrusted proposals.
- Do not give a reviewing agent the author's rationale or desired verdict unless required.
- Do not let one agent edit another discipline's approved document directly. Return cross-discipline findings through a task or review record.
- Record assumptions and evidence sources. Mark unknowns instead of filling gaps with plausible text.
- Never read the entire project or all historical agent records when a context map can narrow the scope.

## Owner interaction

For early development and problem-discovery work, prioritize a short loop: observe, fix, check, and continue. The Owner's natural-language instruction and existing task boundary are sufficient; do not require a new mode-setting ceremony, per-fix task packet, or repeated approval. A project-specific explicit restriction still applies until the Owner changes it for that project.

| Work | Proceed and report | Pause only for |
| --- | --- | --- |
| Routine, bounded, reversible repair inside the authorized objective | Implement, run relevant checks, keep a compact result in the current task, and continue. No mandatory extra specialist, independent review, or per-fix Owner acceptance. Apply Coordinate step 6 when progress stalls. | Missing authority, a requirement that changes the result, or no viable method after the evidence-and-method reassessment in step 6. Two unsuccessful corrections first pause the failed approach, not all authorized work. |
| Material change inside the authorized objective | Implement and verify; obtain one independent review at the coherent delivery checkpoint for shared interfaces/state, permission boundaries, broad data or asset impact, or similarly consequential behavior. A failed in-scope check authorizes correction within the same task, not an automatic Owner request. | A concrete decision on scope, direction, cost, accepted quality, or an action outside the existing authority. A blocked check stops dependent claims or delivery, not unrelated authorized work. |
| Directional decision, formal shared-baseline adoption, release, or external action | Prepare the reviewable result and use any explicit existing authorization for that action. | Only the uncovered decision/action; do not re-ask when the Owner has already authorized it. |

Internal iteration is not release acceptance. Report exactly what was checked and leave other evidence unknown or Not Run; never lower a quality bar or claim product/device/player acceptance to keep moving. Do not call ordinary completion `awaiting_owner` unless there is a named decision genuinely pending. Keep proposed directional facts unapproved, but allow their explicitly authorized experiments and ordinary implementation to proceed. This rule does not authorize commits, pushes, installs, messages, destructive actions, or changes to another project's constraints.

## Version-control boundary

Detect the target's actual version-control system before planning repository actions. If it is a Git worktree, use Git evidence and commits only within the user's authorization. If it is an SVN working copy, use SVN status and commits only within that authorization. If neither is present, treat the directory as unmanaged: validate files directly and do not require a commit, create synthetic revision records, or initialize Git/SVN unless the owner explicitly requests it.

Read `references/project-operating-protocol.md` when establishing or reviewing project governance. Read `references/agent-catalog.md` when selecting or delegating specialist roles. Read `references/iteration-and-isolation.md` for task-output isolation and review rules. Use `review-candidate` for independent Candidate review. Invoke `bootstrap-game-project` when initializing or repairing a project's local Studio records and documentation structure.

Read `references/experience-routing-and-visibility.md` when routing an Experience Trace or declaring user-visible execution behavior.
