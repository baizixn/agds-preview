---
name: produce-game-realtime-art
description: Produce versioned, editable realtime VFX or lighting source packs from an approved art brief and event or scene contract, with engine-interface handoff and honest static-versus-runtime evidence. Use for concrete VFX particle authoring and lighting-state production; do not use for art direction, gameplay code, shader architecture, engine integration, or runtime acceptance.
---

# Produce Game Realtime Art

Create a bounded production Candidate that another owner can wire into the routed engine. This Skill turns an approved Art brief plus GD/Engineering interfaces into editable source and a traceable handoff; it does not choose the visual direction or claim that offline previews ran in-engine.

## Entry gate

Require a task and revision, intended use, viewing context, approved Art brief, GD event or state semantics, engine/renderer/version interface, exact read and write roots, executor and receiver, rights state, finite acceptance, and stop conditions. If the Art or event meaning is missing, stop that mode. If engine access is missing, author the source and static handoff only and mark all runtime claims `Not Run`.

Work only inside the task allowlist. Do not install packages, download substitute assets, edit gameplay code, change render-pipeline settings, or open a game project without separate authorization. An Art Director owns visual intent and professional critique; a task-scoped VFX or lighting producer owns source production; Engineering owns engine mapping and lifecycle implementation; QA owns validation; Reviewer and Owner retain their gates.

## Choose the mode

- For a particle VFX event, read [VFX authoring and N5 handoff](references/vfx-authoring.md).
- For a small-scene lighting-state task, read [Lighting authoring and handoff](references/lighting-authoring.md).
- When delivering either mode, read [Evidence and handoff](references/evidence-and-handoff.md).

Use the smallest mode set named by the task. VFX and lighting require separate source identities, technical receipts, professional results and evidence states even when one task exercises both.

## Production invariants

1. Preserve the approved first read, phase/state meaning, focal subject, non-color cue, surface hierarchy, fixed viewing conditions and protection order. Do not replace them with a brighter or more decorative result.
2. Store authoring values in separate editable sources. Bind only canonical editable leaves into a detached source manifest, then bind that manifest from the derived definition. Never place a JSON file's own impossible self-hash inside itself.
3. Record a stable creator identity, AI-contribution class, tool/model/version (use `unknown` when unavailable), hashed input ingredients, revision steps, license/rights state, intended use and cleanup. Keep provenance outside the canonical editable-leaf set but bind it from the final outer package manifest. Unknown rights block production use.
4. Keep timing, emission, lifetime, size, color, curves, scene layout, material response, camera and light states editable and versioned. Do not use only a flattened image or video as source.
5. Generate fixed offline views or diagrams when useful for Art review. Label them `offline_reference_only`; they cannot prove engine mapping, animation, recycling, concurrency, exposure stability, performance, device response, accessibility or player understanding.
6. Run deterministic schema/hash checks and the finite normal/negative matrix before handoff. A complete source-integrity claim additionally requires distinct stale-detached, stale-definition, stale-HANDOFF and outer-self-inclusion counterexamples; if the routed Engineering fixture does not cover them, preserve its `revise` state. A static failure blocks the handoff. A static pass only supports source/interface conformance.
7. Revise at most twice for the preregistered failure classes. Record unrelated hardening separately rather than widening acceptance indefinitely.

## Exit packet

Deliver the Skill revision, editable sources, derived definitions/configs, fixed-view references, source/rights manifest, non-self-referential hash manifest, raw static-check logs, normal and bounded negative fixtures, professional Art review, Engineering interface receipt, independent QA, independent Reviewer report, and an explicit unverified table.

State the narrowest supported claim. A complete offline packet is `static_handoff_ready`, never `runtime_ready`. Owner adoption, shared registration, installation, publication and deployment remain separate decisions.
