# Production assembly

Use for a production decomposition or engine-ready environment delivery, not every small placement correction. Match the approved delivery stage: offline models, an engine prototype and replacement of the original scene have different acceptance boundaries.

## Choose the runtime parts before producing them

Classify fixed structure, independently operated props, repeated instances, collision proxies and effects. Decide reuse, temporary proxy or specialist production. Keep functional independence even when parts share a parent: a door, tool or display may need a separate source and pivot. Do not weld a semantic prop merely because it is nearby.

Consider consolidating nearby fixed parts with compatible materials. Compare that choice with independent renderers, instancing or applicable batching; account for visibility/culling, LOD, collision, editing and lifetime. Whole-scene merging can render much more invisible geometry. An entire object can move as one rigid unit while its fixed parts share a mesh. A Prefab or FBX is a packaging unit, not a promise of one draw call; material slots, submeshes, passes and the active rendering path still matter.

Art Director owns visual/assembly requirements. The 3D producer owns editable geometry, material-face mapping and agreed consolidation; scene assembly owns placement/contact; Engineering owns import, Prefab/runtime wiring and measurement; QA checks the requested behavior and evidence. A missing assignee remains a named responsibility gap. Do not expand another specialist's Skill to compensate for absent capability.

## Native asset to engine scene

Retain editable source pieces separately from the production export collection. Specify units, pivots, axes, material mapping, dependencies and permitted semantic splits. Compare triangles and their material assignment in one agreed coordinate space and unit system, using the same degeneracy tolerances. Differences between mesh-local scales are not evidence of importer data loss. Preserve import-root coordinate/unit conversions unless a measured conversion replaces them. Report absent UVs or unverified shader behavior rather than implying they were authored.

Freshly reopen the DCC source and receive the exchange file in an empty scene when those deliverables are required. DCC round-trip evidence does not establish engine import or shading. For approved engine integration, deliver reusable Prefabs with their required collision and functional children, place them in the named target scene and reopen that scene in a fresh engine process. An isolated preview or hierarchy group does not fulfill an authorized original-scene replacement. Conversely, do not replace an original scene when only offline work was authorized.

Load a reusable child independently to check it carries its promised collision. Test support continuity, openings, obstacles and the approved route with explicit probe dimensions, not just Collider counts. Keep blocked centerline and passing bypass results distinct. Raycasts/sweeps establish those static probes; actual controller behavior requires its own run. Use the final saved inventory and reopen evidence, not stale counts from an intermediate tool.

## Effects are a separate runtime system

Classify fire, smoke and similar features by the visual/time behavior needed, not by whether they use meshes. A particle renderer can use meshes; a script that animates meshes must be described as that actual implementation. Neither label establishes visual quality.

Give the realtime-art producer and Engineering a shared interface: attachment transform, local/world simulation space, expected motion, trigger/stop, loop/duration, disable/destroy and reuse/reset behavior as applicable. Validate visibility/occlusion, bounds and relevant transparency cost. Separate source-effect production from actual engine integration. Sample ignition, natural stop, restart and instance independence when relevant; do not claim every motion path from a parent-transform assertion alone.

## Costs and recoverability

Engineering should check that the chosen profiler can return valid counters before running the full comparison. Bind platform/build, camera/path, workload, warmup and baseline; unavailable or zero-only counters remain unavailable. Compare actual rendering submissions and CPU/GPU times when claiming rendering improvement; renderer count or CPU submission duration alone does not prove GPU or whole-frame benefit. Keep visible appearance and functionality comparable.

Before import/build automation, establish a restorable snapshot of files that may be touched, or a verified isolated copy containing the approved current state. Hashes detect changes but cannot restore unknown prior bytes. Inspect outputs and protected paths afterward, including generated files outside the requested asset directory. If a boundary changed, preserve the observation and stop dependent adoption; do not guess old content, delete unknown generated files or rerun to hide the failure. Recovery authority and evidence remain with Engineering and the project owner.

Official Unity references: [mesh combination and culling](https://docs.unity3d.com/6000.5/Documentation/Manual/combining-meshes.html), [particle renderer modes](https://docs.unity3d.com/6000.5/Documentation/Manual/PartSysRendererModule.html). Verify the actual installed engine/pipeline before applying version-specific details.
