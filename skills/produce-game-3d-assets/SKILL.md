---
name: produce-game-3d-assets
description: Produce or modify approved non-character static or rigid 3D game assets with editable mesh and node-material sources, measured scale and interfaces, and a reproducible downstream handoff. Use for bounded prop or simple module production; route character deformation, texture painting or baking, animation, and engine integration to their responsible capabilities.
---

# Produce Game 3D Assets

Turn an approved art brief into an editable asset and a verifiable handoff. The integration Candidate assigns method ownership to Art Director with invokable_skills=[]; ownership does not grant execution or automatic invocation. A named authorized task-scoped executor applies the method in the assigned workspace. Art Director retains visual intent and quality judgment; Engineering/TA receives technical interfaces; QA and Reviewer give independent evidence; Owner decides adoption. This Candidate file does not register, install, promote or approve itself.

Adopted scope is rigid/static only. Environment breadth, character, complete material/lookdev, rig and animation remain unsupported; node materials are not a complete lookdev pipeline. Before any 3D production write, read and follow [the current-process preflight consumer](references/blender-preflight.md). Engineering owns its mechanism/schema and technical verdict. The only authorized production entry is `scripts/blender_preflight.py`; the retained `blender_source.py` is its internal callee, and its bare CLI is not an authorized production entry. Missing, stale, invalid or mismatched reports stop the writer. Other generation/save/render operations need a separately routed guarded implementation and are not authorized by this helper.

## Establish the production contract

Read the minimum brief and source needed. Resolve intended use, identity, units, target dimensions and tolerances, viewing conditions, material response, state or assembly interfaces, editable deliverables, allowed changes and preserved parts. For a modification, bind the actual source version and hashes before editing. For generation, establish scale, pivot and assembly intent before detailing. Missing product decisions go back to the responsible designer or AD; unresolved engine budgets remain explicitly unverified.

Confirm the actual writable output root and permitted tool route. Use an existing DCC installation through an authorized execution mechanism. A background script may use a separate factory-startup process; a working background route does not authorize control of the user's open editor, installing dependencies, writing a game repository, or publishing. If the route is unavailable, return the concrete missing condition and remaining deliverables.

Before actual DCC writes, validate all save/render/export destinations together against the authorized absolute output root. Reject relative, out-of-root, duplicate and existing output paths before writing; record the resolved input and output paths. DCC-relative paths can resolve against the loaded document rather than the shell directory. Exercise rejection with dry-run or in-memory cases, never by actually writing outside the permitted root.

Freeze a small acceptance matrix tied to the brief: structural measurements, visual observations, edit invariants, source/export receipt and any requested reuse check. State which changes invalidate prior evidence. Preserve an explicitly agreed correction, experiment, cost or permission budget; the general rule does not renew it. For ordinary iteration, apply [controlled iteration](../studio-orchestrator/references/iteration-and-isolation.md#controlled-iteration): after two cause-based failed corrections of the same blocker, or no new useful evidence, pause the failed approach and reassess; new supporting evidence may justify a finite step within existing authority. Count neither files nor ordinary edits as correction rounds. Do not loosen requirements after seeing results.

## Task learning

When the user identifies an existing output below the requested bar, or an actual check shows a key production problem remains, and no remedy has been verified for that problem, read and apply [task learning](../studio-orchestrator/references/task-learning.md) before further production. Reuse applicable verified practice; when insufficient, inspect relevant experienced production methods and first-hand process, compare failure conditions, and translate the choice into a small authorized trial followed by inspection of its actual editable output. Learning grants no additional production entry, tool permission, write authority or capability scope: all preflight requirements and non-character rigid/static limits above and below still apply. Familiar small repairs with a verified remedy proceed directly; retain the source, decision, attempt and check in the existing production evidence.

## Build and edit the real source

Choose geometry appropriate to the brief. Establish silhouette, proportions, cavity/wall structure and interfaces before surface polish. For rigid states, derive each state from the same source and defined transforms; do not manufacture unrelated meshes for comparison images. For simple static modules, no hinge or state system is required.

Keep mesh, material nodes and relevant hierarchy editable. Apply or account for object scale deliberately; record both geometry and transforms. Model dimensional requirements in real units. Derive bounds from actual evaluated geometry in world space, with the scene's unit scale accounted for. Metadata, requested parameters and modifier settings describe intent; they are not measurements. Measure a bevel or wall at a meaningful cross-section when that is an acceptance item, rather than inferring it from a bounding box or radius in another plane.

For local changes, compare preserved geometry, transforms, hierarchy, material settings and viewing conditions to the frozen source. If a connected part must change to satisfy the brief, record why and keep the change within the authorized dependency scope. Do not silently move the camera, hide a seam or exchange the asset's identity to make a defect disappear.

Create node materials consistent with the art brief and actual export route. Record unsupported or changed material behavior. Texture authoring, UV production and baking are separate unverified branches unless explicitly implemented and tested under a suitable task; node materials alone do not prove those capabilities.

## Inspect, reopen and hand off

Measure required dimensions, pivot placement, state matrices, assembly contacts and allowed change boundaries. Inspect rotations through world/local matrices or correctly interpreted quaternions; Euler fields may be inactive after import. A parenting relationship does not prove a visible physical connection, and a rendered connection does not prove geometric or mechanical correctness.

Render the approved full-size and use-size views from the actual source, preserving specified camera, lighting and color management for comparisons. AD judges silhouette, material hierarchy, identity and connection/state readability from those images. Technical numerical compliance cannot substitute for that judgment. Preview renders are not engine, device or player evidence.

Save to a new version, then open it in a fresh DCC process and exercise the documented operation. Export only the intended asset objects and necessary hierarchy; exclude presentation cameras, lights and staging geometry unless requested. Import the exported asset into an empty scene, confirm the scene was empty first, and compare inventory, dimensions, materials and interfaces. Where useful inspect the export container's own node inventory. A default startup cube is not evidence of export content. State any format losses and downstream assumptions.

For a Blender `.blend` or static `.glb` route, use [the source-facts helper](references/blender-source.md) when a repeatable geometry/transform inventory or explicit-hierarchy export is useful. It reports facts, not artistic or dimensional acceptance; brief-specific thickness/contact measurements remain the executor and receiver's responsibility.

Deliver editable source, export files, material dependencies, fixed-view images, a short operation recipe, source/output hashes, executed scripts and raw logs, and the measured acceptance results. Keep specimen-specific generation or repair scripts with the task's fixtures, not as shared Skill defaults. Reusable scripts must accept the task's object sets and paths as inputs and be tested on a materially different asset.

Record provenance: source author or supplier, rights evidence or unknowns, tool and exposed version, AI-assisted inputs, edit chain and external dependencies. Do not convert tool availability into a licensing conclusion. Preserve failed versions and invalidated evidence alongside the new version's conclusions.

## Scope and completion

This version covers non-character static/rigid mesh production and bounded modification, node materials, scale/pivot/interface inspection, source reopening and static export handoff. It does not establish character sculpting or deformation, a complete Rig, authored animation, UV/texture painting or baking, real-time VFX, assembled production scenes, engine integration, performance, device behavior or commercial acceptance. Hand those requests to the corresponding responsible capability with the available source and missing requirements.

Report `ready_candidate`, `failed`, `blocked` or `needs_integration` according to the actual task evidence. Distinguish author checks, independent technical receipt, AD review, QA, Reviewer and Owner approval. A callable local method and successful specimen are not proof of formal plugin integration or broad artistic coverage.
