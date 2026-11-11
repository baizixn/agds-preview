# Experience Delivery Ledger

Use one compact ledger for the active stage. Producer owns coverage, owner recording, scope state, and decision timing; Orchestrator alone routes work to the recorded owners. Each specialist owns the truth of its contribution. Do not let coordination authority replace design, art, audio, engineering, or QA judgment.

## Experience Trace

Each material Must or proposed feature uses one row:

| Trace row ID | Player promise | Mechanic or interaction | Professional presentation | Engineering observation point | QA or human evidence | Field owners | Scope state |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Immutable non-content identity | Approved contract reference | Responsible design input | Responsible art/audio/UI input | State, event, interface, or measurement supplied by Engineering | Automated, expert, device, or human method and current result | Named owner for every populated field | Must, Should, Could, or Explicitly Deferred |

Missing professional input stays unknown; Producer must not fill it with plausible text. If a proposed feature cannot route to an approved player promise, keep it Deferred until scope authority changes.

## Sparse professional critique return

Use this sub-record only when the approved stage decision needs current professional experience-quality input. Do not create periodic meetings or fill every field for every row.

| Field | Required meaning and owner |
| --- | --- |
| Critique record ID | Immutable record identity. Producer may maintain the index but may not reuse the ID. |
| Trace row ID | Stable link to the Experience Trace row; rename or scope text changes do not silently change identity. |
| Checkpoint instance | Exact decision attempt plus an approved checkpoint kind such as direction freeze, first playable, core experience observable, or feature freeze. The task may override these defaults. |
| Responsibility and routed owner | Responsibility slot and Orchestrator route identity. Missing routing remains `unknown`; Producer does not assign a specialist. |
| Claim references | References to the Experience Quality Contract or approved criteria; never copied or invented quality text. |
| Decision snapshot | Exact artifact, scope, contract revision, and environment under decision. |
| Owner-supplied relation | `Supports`, `Falsifies`, `Inconclusive`, or `Not Run`, written only by the responsible professional owner for its contribution. |
| Evidence state | Evidence reference, class, observation time, QA validity or limits, and `current`, `stale`, or `unknown` freshness. |
| Conflict state | `none`, `open`, `routed`, or `owner_approval_required`; retain all conflicting records. |
| Update identity | Source update ID and record revision for idempotent upsert and concurrent-change detection. |

`Supports` covers only the named contribution and claim. `Falsifies` records a conflict with the claim but does not choose a fix or change direction. `Inconclusive` means an observation exists but evidence, authority, environment, or specialist conclusions conflict. `Not Run` means no valid observation completed. Never average, vote, or collapse these states into a universal score or overall Pass.

Evidence is `current` only when the claim, contract, artifact, environment, and decision snapshot identities match. A known mismatch is `stale`; a missing required identity is `unknown`. Do not invent a universal expiry time. A late critique cannot retroactively satisfy a closed gate; create or reopen an authorized checkpoint instance.

Upsert by the immutable critique record ID. The trace row and responsibility slot cannot change. Replaying the same source update and payload is a no-op; the same source update with a different payload is a conflict, not last-write-wins. Reject an old record revision. A material artifact or contract change creates a new checkpoint instance and leaves prior evidence stale unless the responsible owner explicitly confirms reuse.

At a material checkpoint, Producer freezes the decision snapshot, creates only the Must-row and affected-responsibility obligations, asks Orchestrator to route them, then reports coverage, freshness, open conflicts, and missing inputs. Specialists own their relations and conclusions; QA owns evidence validity; Game Design may integrate routed professional states; Owner retains quality-bar, scope, direction, waiver, and gate decisions. Missing current input makes coverage incomplete, not failed or passed.

When `Supports` and `Falsifies` target the same claim/snapshot, or QA invalidates evidence behind a professional relation, keep every source record, set the integrated state `Inconclusive`, withhold impact sizing, and route the dispute through Orchestrator to QA and the responsible specialist. Escalate target-player, core-promise, platform, quality-floor, stage-policy, scope, or milestone changes to the Owner.

## Diagnostic class and impact radius

Evidence-gate and classify before proposing a fix. A second oracle or minimal reproduction that does not reproduce the first report creates an evidence dispute; it does not by itself prove that the first test is wrong. Until evidence supports one class, record `classification: Inconclusive`, preserve both plausible explanations, and withhold impact sizing, test invalidation, and product revision.

- `test`: independent evidence reproduces a fault in the test or establishes that the original oracle is invalid; repair or invalidate that test before product work.
- `local`: the approved rule is unchanged and one responsibility surface contains the mechanism-level defect.
- `system`: individually valid responsibilities fail at a shared state, lifecycle, or interface boundary.
- `experience`: functions work, but observed behavior falsifies the approved experience hypothesis; stop content growth and compare a bounded alternative.
- `direction`: target player, platform, core promise, quality floor, or approved scope changed; stop for Project Owner decision.

Assess the smallest defensible radius using responsibility surfaces, core state or lifecycle, data/interface contracts, asset volume, evidence invalidation, and causal uncertainty. Record `small`, `medium`, or `large` only as a task-specific decision with reasons; there is no universal file-count or numeric threshold. Engineering supplies technical impact, QA supplies evidence invalidation and test-source classification, and the responsible design or presentation owner supplies experience impact.

## Default overridable budget checkpoints

| Checkpoint | Required observation | Default action when absent |
| --- | --- | --- |
| 25% | A playable change or the first approved observable/durable artifact exists. | Shrink scope and protect the shortest path to observable value. |
| 50% | The core experience behavior can be observed; evidence may still be incomplete. | Pause content and presentation expansion; repair the observation path. |
| 80% | Feature scope is frozen. | Allow only fixes, presentation integration, and validation. |
| 100% | Current playable or observable result, gaps, and next decision are returned. | Do not silently extend the task. |

These ratios are planning defaults that the approved task may override. Record stage start, first playable or first durable artifact, and validation freeze. Record exact token use only when the runtime exposes it; otherwise use `unknown`.
