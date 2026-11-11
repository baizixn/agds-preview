---
name: integrate-interactive-audio
description: Implement, connect, debug, profile, and hand off a bounded interactive game-audio slice across middleware or engine events, gameplay parameters, spatial audio, music states, dialogue playback, UI audio, dynamic mixing, streaming, and platform-aware asset settings. Use when the assistant must do concrete runtime audio integration and technical verification rather than create source assets or define final audio direction.
---

# Integrate Interactive Audio

Execute one approved interactive-audio integration task. Produce a working implementation Candidate and raw evidence where the routed tools and project access permit it; otherwise return an explicit blocked or design-only result.

## Require inputs

Require the approved cue or system behavior, event and state contract, source-asset identity and version, integration target, gameplay owner, platform or device context, routed performance and quality budgets, fallback behavior, acceptance oracle, and allowed tools and paths. Stop before implementation when the target project or mutation authority is absent.

## Implement

1. Map gameplay events, states, parameters, priorities, concurrency or virtualization, variation, transitions, persistence, interruption, and failure behavior.
2. Import or reference approved assets and implement the smallest maintainable event graph, middleware structure, engine component, data binding, script, or code change.
3. Configure only routed spatialization, attenuation, obstruction or occlusion, listener behavior, routing, buses, snapshots, ducking, dynamic range, music states, dialogue priority, UI routing, streaming, compression, and platform overrides.
4. Preserve accessibility hooks such as independent category controls, critical-cue alternatives, caption or subtitle identifiers, narration coordination, and non-audio fallback routing where required.
5. Exercise success, missing-asset, rapid-repeat, overlap, interruption, state-transition, pause/resume, device-change, localization-length, and fallback paths proportionally to risk.
6. Capture available authoring, editor, runtime, profiler, log, trace, bank/build, CPU, memory, voice, streaming, and error evidence. Separate local/editor evidence from standalone, target-device, performance, accessibility, localization, and player evidence.

## Deliver

Return:

- implementation diff or integration manifest with event, parameter, state, bus, asset, and code ownership;
- runtime mix and system behavior matrix with priority, transitions, spatial role, fallback, and accessibility hooks;
- build or bank output identity and source-asset/version dependencies;
- raw logs, traces, profiler captures, reproduction steps, test environment, and evidence state;
- performance observations against routed budgets, without inventing thresholds or declaring QA acceptance;
- handoff packet for Audio Director review, Engineering ownership, QA validation, and Owner decisions.

## Protect boundaries

- Follow the approved direction and event contract; do not approve final audio direction, rewrite gameplay or narrative semantics, create missing source assets by pretending, or change scope, budget, platform, or quality bar.
- Do not replace Composer, Sound Designer, Dialogue/Voice Director, Audio Director, Engineering, QA, Legal, Producer, or Project Owner conclusions.
- Route production-code ownership and architecture changes to Engineering. Make only authorized changes and keep the implementation reviewable and reversible.
- Do not claim target-device, performance, accessibility, localization, usability, player, or release Pass from editor audition, a profiler estimate, or missing evidence.
- Do not treat one engine, middleware, codec, platform, or numeric budget as universal.
- Do not access a real game project, modify formal Studio baselines, promote the Candidate, deploy, install, stage, commit, or push without separate authorization.
