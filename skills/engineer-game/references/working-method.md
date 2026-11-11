# Engineering working method

Use the sequence while doing the work, not as a retrospective checklist. Reuse the task's technical notes, source and evidence records; no new record format is required. Scale detail to the actual change. An unavailable independent reviewer is a missing review, not permission to self-certify.

## 1. Convert the input into executable work

- **Overall requirement:** trace player input through preparation/startup, rule/state changes, visible results and exit/restart. Identify relevant rejected, repeated, cancelled and partially failed operations before splitting implementation. Map each observable behavior to its state owner, entry/caller, dependency, implementation task and completion check. For a new project, distinguish proposed boundaries from inspected existing code. Do not decide a module count first.
- **New feature:** find the nearest existing flow, actual extension point, data writer, callers and cleanup path. Mark what remains shared and which responsibility is genuinely new.
- **Fix / hotfix:** reproduce through the real entry when available, trace the cause and state owner, and retain an observable failing case before the narrow fix. If reproduction is unavailable, distinguish hypothesis from confirmed cause. Existing emergency authorization still controls any allowed review deferral; do not invent one.

Tasks need a result and a finish condition, not just class names. Keep an atomic operation together even when several files are involved. Split work where ownership, dependencies or independently changeable rules justify it. Missing gameplay rules go back to their owner; Engineering may continue independent work, but cannot fill a material product gap with a convenient test value.

## 2. Make a code-checkable decision

Before implementation, record enough to answer these task-relevant questions:

- How does the feature start, become ready, run, stop and restart? Which caller reaches each transition? A short flow/sequence sketch is useful when several owners participate.
- Who owns each shared fact and who may mutate it? Which way do dependencies run? Presentation reads game facts; it does not become a second authoritative writer.
- For each affected resource or outstanding operation, who creates, holds, invalidates and releases it? Include subscriptions, timers and asynchronous results, not only visible objects. What happens on failed start, repeated cleanup, exit and a late completion after restart? Invalidate the old lifetime before a result can affect the new one; rejected successful results still need their owned resources released.
- Which collections fit the actual identity lookup, ordering, iteration and mutation needs? Consider size/frequency and measured allocation cost. A pool adds capacity, reset, stale-callback and retained-memory obligations; do not select it merely because objects are short-lived.
- For a project/module requirement, which existing architecture, engine/first-party facility or maintained ecosystem framework fits the current engine/package versions and platform? Check primary documentation, compatibility, maintenance and license evidence before selecting reuse, configuration, extension or a small adapter. Explain concrete gaps before a fork or custom replacement; changing vendor internals or adding a dependency requires the applicable task authority. Use [the framework/memory plan](module-framework-memory.md) rather than treating an individual API lookup as a module framework assessment.
- What are this engine's managed, native and resource allocation/release rules? Identify hot allocations and lifetime overlap; plan peak smoothing, capacity/retention limits and explicit release under success, cancellation, partial start and repeat entry. Record which frame-time, allocation, collection, peak and retained-memory measurements are needed on the actual target. Missing budgets or measurements remain unverified; pooling or incremental GC alone cannot certify them.
- Which approved next change should fit, and where should edits concentrate? If no relevant next change exists, say so. Do not invent future content to justify abstraction.

Tie facts to requirements, files/symbols or observations. For a real tradeoff, compare the simplest viable alternative, explain the cost of the chosen approach and identify evidence that would reverse it. No alternative essay is needed for a determined local fix. For example, an account writer committing a completion receipt can be checked against all balance writes and repeated completion; “clean architecture” cannot.

For a new engine-facing mechanism or a proposed manual replacement of an engine/package facility, include the current [capability check](engine-capability-check.md) result and its actual sources with this decision before implementing it. A passing report establishes source/version completeness only; a required source or probe that is missing or stale leaves the affected decision unresolved. Reuse an unchanged verified local decision rather than reopening research for every repair.

For ordinary technical uncertainty, use the uncertainty-reduction rule in the main Skill. When the observed-result and missing-verified-remedy trigger there applies, use [the shared task-learning method](../../studio-orchestrator/references/task-learning.md); it owns the general learning sequence. Engineering supplies the concrete technical question, source/version constraints and implementation consequence, and keeps the result in the same task evidence. Do not duplicate the learning steps or add a second report, review or retry loop for learning itself. Any probe still requires existing task authorization; neither route overrides a pause or a no-new-tests instruction.

The existing examples explain data-interaction boundaries, measured pooling and late-result ownership. Their references motivate choices; they do not prescribe a framework, topology or module count for another game. Prototype depth may be smaller than Production depth, but ownership and cleanup still apply.

## 3. Request technical review before the affected implementation

Use this step for the first overall/cross-module design, or a material change to state ownership, shared interfaces or asynchronous/resource lifetime. Reuse a previous review when its inputs, design and affected assumptions remain unchanged; do not review every file edit or routine feature addition again. A routine local repair retains its ordinary impact/self-check and adds no mandatory independent review; an explicit task review requirement still applies.

Engineering prepares a technical-plan Candidate and routes a real request to the registered Reviewer through supported delegation, or asks the orchestrator to route it. Engineering does not execute the Reviewer's owned Skill itself. Provide the existing review contract's minimum packet:

- Review/Candidate IDs; original objective; approved acceptance and constraints; relevant approved facts and unresolved product decisions.
- Public technical decision, task dependencies and finite normal/failure cases; existing source/call paths needed to judge them, or explicit greenfield absence.
- An immutable identity covering the plan and routed source, such as a content-hash manifest; a mutable path or task name is insufficient. No Git repository is required.
- Raw inspection or validation evidence already available, with unrun items marked; prohibited decisions and the authorized edit boundary. Do not supply a desired verdict, private reasoning or unrelated history.

Ask the Reviewer to assess requirement-to-task coverage, feasibility, state/dependency boundaries, relevant extension cost and lifecycle exits against those sources. It must not demand implementation results for an explicitly pre-implementation review.

Wait for the independent result before implementing the gated design. Preserve its run reference, reviewed identity and raw output. Resolve in-scope blockers and re-review only affected content; a material scope/cost/authority change goes to the Owner under existing rules. Non-blocking advice does not become a new approval gate. If dispatch or identity verification is unavailable, record the precise pending review and continue only independent work; do not substitute an author “reviewed” label. A technical review allows work within the existing task authorization, not adoption or release.

## 4. Implement in dependency order

Establish the actual owner and contracts, implement domain behavior, connect the normal entry, and complete the relevant failure and cleanup paths. Keep authoritative writes together and reuse existing extension points. If source facts contradict the reviewed decision, revise the decision before extending the mistaken design; send only a materially changed boundary back to technical review.

Retain the first decision and its actual sequence. A decision written after the code is retrospective explanation, not evidence of pre-code analysis. Record assistance or corrective reminders when they occur; do not turn prompted completion into unaided execution.

## 5. Verify actual use and the relevant next change

Run the finite cases derived from the requirement and mechanism through the normal entry and real dependency path available in the project. Include relevant repeated entry, invalid input, partial failure and lifetime transitions. A direct helper test, build or animation playback does not replace integration. Use controllable timing only at the dependency seam needed to exercise actual cancellation/late-result handling, within the authorized project work.

When the task includes an approved second configuration/content type, compare actual changes with the expected extension point and rerun the first content's affected behavior. Shared-code edits are not automatically wrong: explain whether the new requirement changed a real boundary or exposed avoidable coupling. When the next change is not authorized, inspect the expected change footprint and label it a prediction; do not implement an extra feature or claim extensibility was demonstrated.

For lifecycle work, preserve relevant state/resource observations before, during and after restart/exit and subsequent use. Check cleanup on partial creation as well as success, and that old callbacks cannot write new-lifetime state. A finite clean run does not prove zero leaks or universal callback safety. Missing environment or budget remains explicit; comparable measurements are required for performance claims.

## 6. Request final source review

For material work or an explicit task review requirement, route the final Candidate review to a fresh independent Reviewer at a coherent delivery checkpoint after self-checks. Routine bounded repairs stop after their proportionate checks and compact result unless the task explicitly requires review. Provide the original task/criteria, public decision and technical-review record when applicable, exact source/diff with verifiable identity, affected callers and cleanup paths, actual raw validation, remaining limits and prohibited decisions. Do not send an author-supplied expected verdict. Source must be readable; a report about source is not its replacement.

Ask the Reviewer to compare:

- Required behavior and decomposed tasks against actual entry/caller and state-write paths.
- Chosen ownership/dependencies and relevant resource/late-callback exits against the implementation, including failure paths.
- Claimed extension points against the actual authorized change footprint, or an explicitly untested prediction.
- Completion claims against raw normal-entry and regression evidence, separating author tests, independent QA, runtime/device and performance levels.

Preserve the independent run reference, reviewed version and original report. Record each in-scope finding's disposition: linked fix and affected verification, retained non-blocking risk, or explicit Owner scope decision. A later change invalidates review coverage of that changed content; do not silently reuse an earlier approval or rerun unrelated reviews. If the Reviewer cannot read/bind the source, keep review pending/withheld. No actual run means `not_reviewed`, even if the author filled every field.

Use the finite acceptance and correction budget already agreed for the task. Do not open a new adversarial matrix after every review. After at most two corrective rounds on a repeated blocker, consolidate the cause and return the unresolved scope decision. Reviewer advice is not Owner adoption. Candidate completion, independent review, source adoption and installed pickup remain separate.

## 7. Leave a small observation for the next real task

In the existing task record retain only what helps assess execution: decision before or after editing; actual review run/identity; user reminders; omission-driven rework; unexpected change spread; normal-entry results and unverified limits. Record the cause and evidence, not a score derived from document length, interface counts or checkmarks. Keep task-specific facts in the project. Neither this method's presence nor one successful task establishes general engineering improvement.
