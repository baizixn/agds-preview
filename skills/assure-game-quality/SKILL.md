---
name: assure-game-quality
description: Plan, execute, and review evidence-based functional, performance, comfort, usability, regression, and player-experience validation for games. Use for test plans, test cases, bug triage, log or video analysis, build acceptance, device validation, or independent critique of a candidate result.
---

# Assure Game Quality

Validate one bounded target against approved requirements and risks. Produce evidence and a recommendation; do not become the final release authority or the owner of another discipline's fix.

## Frame the validation

1. Restate the approved objective, lifecycle stage, target build or artifact identity, acceptance criteria, risks, required environments, available evidence, and prohibited decisions.
2. If the target, acceptance basis, required environment, evidence authority, or lifecycle stage needed to choose meaningful depth is missing, return a compact missing-input record and stop before inventing a test oracle.
3. Build a trace from each material requirement to its risk, test, environment, evidence, and result. Explicitly list approved criteria that remain untested.
4. Choose the smallest proportionate mix of scripted, automated, exploratory, human, device, and external-platform evidence. Do not run every category by default.

When the target is known but a local criterion is unclear, within already approved analysis scope, separate known facts from competing hypotheses, formulate one question, identify the minimum distinguishing evidence and the authority responsible for the criterion, then stop. Keep formal judgment without its required basis stopped under step 2; this analysis grants no new access, execution, or decision authority.

## Match validation to the lifecycle

1. At concept stage, review vision, mechanics, constraints, risk, testability, and the evidence needed to falsify experience claims. Produce strategy and environment needs, not runtime-pass claims.
2. At pre-production, review requirements and prototypes, refine the risk model, entry and exit criteria, environment matrix, test data, observability, and automation candidates.
3. During production and pre-release, execute applicable functional, integration, exploratory, regression, performance, stability, compatibility, device, accessibility, usability, comfort, and player checks against identified builds.
4. During post-release or live operation, validate updates, migrations, regressions, current external reports, and player-reported anomalies against the affected build and environment. Telemetry and reports identify investigation targets; they are not a `Pass` by themselves.
5. Record why the selected depth fits the stage and risk. Do not demand release-level completeness from a prototype or treat prototype evidence as release evidence.

## Route game-specific coverage

For every routed risk, mark each applicable vector `selected`, `deferred`, or `not_applicable` with a reason. Select only vectors supported by the task basis:

- gameplay mechanics, rules, state transitions, progression, economy, and interaction combinations;
- client, server, multiplayer, network interruption, reconnection, synchronization, and recovery;
- levels, content, save/load, persistence, migration, install, update, rollback, and data integrity;
- graphics, camera, animation, collision, UI, text readability, visual cues, and rendering comparison;
- audio, music, voice, spatial cues, mixing, interruption, and output-device compatibility;
- input, remapping, controller, keyboard, mouse, touch, motion, haptics, device, and form factor;
- localization, internationalization, text expansion, fonts, layout, regional formats, and cultural review authority;
- operating-system, hardware, middleware, store, platform, certification, and external compatibility criteria explicitly routed for the task;
- performance, frame pacing, resource use, load time, stability, stress, soak, thermal, and power behavior;
- accessibility, usability, comfort, safety, and observed player experience.

Do not turn this router into an exhaustive checklist. Art, audio, design, engineering, legal, security, privacy, certification, and release authorities still own their criteria and fixes.

## Execute and preserve evidence

1. Record build or artifact identity, configuration, platform or device, test data, setup, steps, expected result, actual result, attempt count, and raw evidence for material checks.
2. Report every assertion as `Pass`, `Fail`, `Inconclusive`, or `Not Run`. Missing, stale, incomparable, wrong-build, or wrong-environment evidence is never `Pass`.
3. Keep automated or static coverage, local execution, runtime, real-device, measured performance, comfort, usability, accessibility, and observed player evidence separate. State what each evidence level cannot prove.
4. Keep functional correctness, performance, compatibility, stability, comfort, usability, accessibility, and player experience as separate claims. Never infer human or real-device claims from automation alone. Never infer comfort, usability, accessibility, fun, or player understanding from functional automation alone.
5. When a formal budget or threshold is absent, report measurements descriptively, preserve comparable conditions, request the missing authority, and leave that claim `Inconclusive` or `Not Run`; never invent a cross-project threshold.
6. Invalidate or scope prior results when the build, configuration, requirement, environment, data, dependency, external compatibility criteria, or test implementation changes. A reproduced result on one build does not automatically transfer to another.

For an approved spatial or navigation claim, when relevant, fix the target, observation point and direction, coordinates, version, and task-approved arrival or obstruction criteria. Select only evidence required by the approved claim, and record static visibility, path query, actual entity displacement and arrival, and relevant blocked-state recovery separately when applicable; none substitutes for another, and teleportation does not prove the journey. Compare before and after only under materially matching conditions. A local controlled check does not prove natural player, multiplayer, or performance behavior. Derive expectations from the approved task, never invent thresholds. A visibility-only claim does not require navigation queries or traversal. Without product access, assess supplied evidence or request it from the responsible executor; do not modify the game or perform another role's fix.

## Use exploratory and automated evidence deliberately

1. Use a time-boxed exploratory charter when emergent mechanics, state combinations, content interactions, or weak specifications make scripted coverage insufficient. Record the objective, risk focus, setup, data, time box, notes, coverage observations, anomalies, evidence, and debrief outcome.
2. Exploratory evidence complements traceable scripted checks; it does not excuse a missing oracle for a claim that requires one.
3. For automation, record execution location, build, environment, seed or test data, isolation, setup, teardown, state cleanup, order assumptions, retries, and artifacts. Tests must not silently depend on prior order or leaked state. For browser validation, create a dedicated QA-owned profile outside the evidence allowlist; record the exact QA-owned processes, tabs, listeners, and cleanup targets; and clean only targets whose QA ownership is proven. Do not inspect, reuse, or close unrelated user browsing state. If ownership cannot be proven, fail closed and leave the target untouched.
4. Distinguish product failure, test failure, infrastructure failure, and suspected flaky behavior. A retry may characterize reproducibility but may not erase the original failure or manufacture a pass.
5. Before routing a stable finding that would trigger downstream product revision, reproduce it with a matching independent oracle or a minimal reproducer. When that check shows the original test or oracle was wrong, preserve an invalidation record, retain the unchanged target identity, and do not route a product revision.
6. For routed performance work, record configuration metadata, warm-up, repetitions or sample window, metric and aggregation, variability, capture tool, and raw samples. Compare only materially comparable conditions and retain approved budgets as external authority.
7. Before a broad or long browser flow relies on native form events, key edges, focus transitions, reload, or persistence semantics, run one bounded sentinel through the same browser/runtime, QA-owned profile, driver path, and approved semantic contract. Record the contract reference, environment, driver input, raw event or state observation, attempts, and cleanup. A sentinel `Pass` proves only that this route is evidence-eligible for the named semantics; it does not prove the product or experience. A `Fail` or `Inconclusive` is a test or infrastructure limitation, leaves every dependent product assertion `Inconclusive` or `Not Run`, and cannot support product `Pass` or revision. Rerun when the browser, driver, profile, fixture, event contract, or persistence path changes.
8. For an isolated deterministic sentinel-state check, use `scripts/evaluate_native_semantics_sentinel.py` on one explicit JSON packet. The helper never drives a browser: it validates route identity, declared observations, dependent-result eligibility, and QA-owned cleanup scope. Real browser evidence still requires the actual routed tool and environment.

When multiple evidence batches, recurring reports, or competing test investments require a choice, compare build, environment, test and infrastructure changes, denominators, and sampling windows before inferring a trend. Describe incomparable signals without ranking quality; defect counts and pass rates alone do not establish quality. Recommend one bounded next check or evidence request, explaining expected risk reduction and effort, then stop. When considering automation, weigh expected reuse and avoided manual effort against implementation and maintenance cost, reliable assertions, observability, and result trust. QA owns test strategy, assertions, and evidence trust; an already authorized executor may maintain lightweight tests within the assigned scope. Engineering owns authorized framework, engine-interface, and CI integration work. Choose automation only where that tradeoff supports the next evidence need; existing task permissions still govern execution.

## Preserve experience-quality evidence and bounded human checkpoints

1. For every routed Experience Quality Contract claim, record the contract and claim identity, target artifact/build and revision, configuration, environment and player/use context, oracle, evidence authority, evidence class, setup, observation, result, limits, and invalidation triggers.
2. Keep conformance, experience hypothesis, expert evidence, human/player evidence, and automated semantic-fidelity claims separate. QA does not invent a quality dimension, observable behavior, sample rule, or threshold. A qualitative claim without an approved falsifier or observation rule remains `Inconclusive`.
3. Expert critique may support the named professional contribution; it does not replace target-player, affected-player, real-device, comfort, usability, accessibility, or listening evidence when the approved claim requires that evidence. Functional automation never fills those human evidence fields.
4. When semantic fidelity is `Fail` or `Inconclusive`, or an approved claim requires native-device, expert, human, or player evidence that is unavailable, route one bounded evidence-checkpoint request through Orchestrator before Reviewer entry. Include checkpoint ID, claim and contract, exact target/environment, evidence role and qualification authority, privacy-minimized participant binding, consent or participation state, bounded steps and exit condition, evidence requested, and prohibited conclusions.
5. A valid checkpoint updates only the applicable evidence state. A refused, unavailable, mismatched-identity, wrong-target, wrong-environment, or incomplete checkpoint closes with the gap still `Inconclusive` or `Not Run` and proceeds to Reviewer as unresolved risk; it must not loop indefinitely or manufacture a `Pass`. The participant supplies observations, QA owns evidence state, Reviewer owns independent assessment, and Owner retains acceptance, waiver, and quality-bar decisions.

## Manage findings through a lifecycle

1. Give every material anomaly a stable identifier, concise title, observation date, target and environment identity, linked test or charter, reproduction, expected and actual behavior, evidence, confidence, severity, affected scope, and recommended owner.
2. Classify whether the anomaly is a product defect, duplicate, change request, test issue, infrastructure issue, or unresolved observation. Do not decide another role's fix.
3. Track status such as `open`, `deferred`, `duplicate`, `awaiting_fix`, `awaiting_confirmation`, `reopened`, `closed`, `rejected`, or `inconclusive`, plus affected build, fixed build when claimed, confirmation result, and regression scope.
4. Confirmation proves only the claimed fix on the tested build and environment. Close only when the approved closure basis is met; reopen when the anomaly remains or recurs under that basis.
5. Separate evidence-backed severity from business priority. QA may recommend deferral or waiver, but Producer or Project Owner retains priority, accepted residual risk, waiver, schedule, quality-bar, and release decisions.

## Preserve accessibility evidence levels

1. Use only approved accessibility criteria or guidelines as the test basis and record which criteria were actually evaluated.
2. Separate static checklist review, automated checks, simulation or assistive-tool checks, expert evaluation, and evaluation with players with disabilities.
3. Simulation and tooling can expose risks but cannot replace evidence from affected players when that evidence is required. None of these levels proves legal compliance unless the applicable legal criteria and authority were explicitly routed.

## Complete and recommend

1. Report planned versus executed coverage, deviations, impediments, untested criteria, unresolved findings, evidence freshness, residual risk, and whether entry and exit conditions were met.
2. Preserve reusable testware and raw evidence links, and identify what must be rerun after a build, requirement, environment, data, dependency, or criteria change.
3. Define focused confirmation, regression scope, negative coverage, and an evidence-based build-acceptance recommendation. The recommendation is not approval.
4. If asked to review the QA Candidate itself, route a minimum packet to a fresh `review-candidate` Reviewer; QA Lead does not independently approve its own work.

## Preserve scope and truth

- Use only routed approved requirements, target artifacts, environments, and raw evidence. Do not import unrelated project history or another game's facts.
- Keep project-specific builds, devices, thresholds, defects, status, and evidence in the game project, not in this reusable Skill.
- Do not modify design, code, art, audio, production work, or another Agent's Candidate unless assigned a separate bounded task.
- Do not promote Agent or Skill authority, update plugin versions, deploy, install, stage, commit, push, or perform irreversible actions without separate approval.
