# Flat multi-leg locomotion: executable slice

Use this route when the approved engineering task needs a neutral Unity prototype of an articulated six-leg or eight-leg actor walking on a fixed horizontal plane. First inspect the existing rig and movement owner. Retain a working project solver when it meets the actual requirement; do not replace it merely because a template exists.

## What the template does

`../templates/flat_multileg/Runtime/FlatMultiLegKinematicController.cs` provides explicit two-segment leg bindings, world-space planted contacts, reachable movement, coordinated swing, and lifecycle release. The Editor fixture beside it constructs neutral demonstration rigs. These are editable source files, not an installed Unity package or an automatically registered game system.

A planted foot remembers a world position while the body moves. Before translation or turning, the controller checks whether planted legs can still reach their contacts. If it limits movement, stepping must continue so the actor can exchange support and resume progress. Moving the foot along with the body hides overstretch but creates sliding; freezing the body hides sliding but is also a failed walk. Measure both contact error and actual progress.

This solves a kinematic integration problem. It does not author a character mesh, animation clips, a game-specific state machine, footstep audio, terrain queries, navigation, collision response or physical balance. A minimum support count is not proof that the centre of mass lies inside a support polygon. Artistically convincing gait, body motion, silhouette and reference similarity need their own review.

## Rig and configuration preflight

1. Confirm an approved horizontal ground plane, a world-up convention, a fixed supported scale, and explicit movement/pose ownership. Read the runtime configuration validator for its exact supported limits. Record rig dimensions, velocity, turn rate, time-step envelope and acceptance tolerances as task inputs.
2. Bind each leg's upper pivot, lower pivot and toe Transform explicitly. Bone names are not a contract. Measure both segment lengths from the actual hierarchy. Do not use an empty pivot's bounds as the endpoint or reconstruct lengths from a renderer bounding box.
3. Use a direct two-segment hierarchy under the controlled root. Check distinct, non-null chains, finite values, non-zero lengths and a feasible neutral contact on the plane. Do not silently skip a missing leg or partially initialize a rig.
4. Start from the intended neutral pose, configure the component, and call `TryInitialize(out reason)`. Treat a false result as an actionable unsupported input. Resolve the reported binding/geometry/configuration issue before driving movement.
5. Decide who owns the root and each leg. This template owns root movement while active. Do not simultaneously run a NavMeshAgent, Rigidbody motor, root-motion writer or another IK solver on those transforms. Supporting a different ordering requires a new integration check; do not guess that two writers will cooperate.

Two feasibility settings deserve attention. `minimumNeutralReachReserve` is the allowed leg extension still available after `reachMargin` at the initial ground contact; a nearly straight leg may be reachable yet have no useful room to walk. Choose that reserve for the intended rig and motion, and retain the validator's reason if the pose fails. `landingPredictionSeconds` must cover at least `swingDuration`, because the body continues moving while a foot is airborne. The sample values are examples, not transferable art or gait standards. Landing is checked again against the current hip before planting.

## Install and drive

Copy the `templates/flat_multileg` directory into a new, approved `Assets` subdirectory of the target Unity project. Check that the destination does not exist first; never overwrite a project's existing implementation. Preserve the `Runtime` and `Editor` separation. The prototype has no XR or third-party package dependency. Record the exact Unity version actually used by the receiver rather than assuming all versions are compatible.

In the Editor, choose **Tools > AGDS > Flat Multi-Leg > Create Neutral Demonstration**, then Play. The demonstration driver is the sole manual step caller for its rigs; it sequences movement, turning and stops as an editable example. It is not production input or behavior logic. The demo primitive builder and JSON report use Unity's built-in physics and JSON serialization modules. Screenshot validation additionally needs the built-in image-conversion module.

For the included author-owned smoke check, invoke `AGDS.Engineering.FlatMultiLeg.Editor.FlatMultiLegNeutralFixture.RunBatchValidation` with Unity's `-executeMethod`, an isolated `-projectPath`, `-batchmode`, and `-flatMultilegReport <output.json>` plus `-logFile <output.log>`. The runner exits with its report result. It must be followed by an independent receiver/rig check before claiming transfer.

Use the included neutral Editor fixture to see the explicit binding construction and configuration fields. Then bind the intended rig separately. Call `SetMotion(planarWorldVelocity, yawDegreesPerSecond)`. The default `autoStep=true` drives `Step(Time.deltaTime)` in Update, and `autoInitialize=true` initializes in Start. For deterministic/manual stepping, explicitly set both options false, initialize once and drive `Step(deltaTime)` from exactly one caller. Do not combine automatic and manual stepping. Inspect false returns and `LastError` rather than continuing after invalid input. The template supplies no game-specific state machine.

Use `Stop()` for zero desired motion while keeping the controller available. Use `Release(...)` before another system takes pose ownership. Check the restore option against the receiver's captured-pose contract; a pose restore must not overwrite a newer authoritative animation pose. Use the documented reset/teleport API to discard old world anchors after repositioning. Do not retain contacts from the actor's previous location.

Expose a useful scene entry, motion inputs and diagnostic readout to the receiver. A recipient should be able to reproduce a failure without reading the solver internals. Keep task-specific model dimensions, motion tuning and scene paths in the target project.

## Finite validation before handoff

- Reproduce a contact defect with a naive root-follow or unguarded motion baseline on the same neutral fixture. Keep that failing result alongside the candidate result.
- Exercise forward movement, left/right turns, low speed, stop/restart and rotation in place at the task's chosen frame rates. Measure actual toe positions, planted-anchor error, reachable segment lengths, finite transforms, minimum support and body displacement. A zero-motion workaround must fail the progress check.
- Check release to another pose owner, disabling/re-enabling and reset/teleport. Once released, subsequent stepping must not mutate the other owner's pose. Invalid bindings must return a reason before partial pose mutation.
- Construct a materially different neutral rig and repeat the integration from minimal instructions. Reusing source code is intended; renaming the same model is not transfer evidence. Keep the input geometry/configuration, source hashes and actual runtime output.
- Run the frozen input in a fresh process and compare outcomes and numeric metrics with declared tolerances. Preserve compiler, engine and test errors; do not filter a global error into a whole-run pass.

Use a camera view that shows every foot during translation and turning. Inspect actual frames as well as metrics. Separately report deterministic Editor stepping, live Play execution, visual judgment, target-device/player and performance evidence. A desktop harness proves none of the unrun levels.

Stop at the finite registered acceptance gate. If the model, platform, terrain or animation ownership exceeds the template's demonstrated scope, retain the candidate as a limited example and assess the new requirement explicitly. Do not expand its advertised capabilities to match an unsupported request.
