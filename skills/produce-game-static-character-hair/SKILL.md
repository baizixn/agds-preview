---
name: produce-game-static-character-hair
description: Repair editable static coarse character-hair root and crown continuity from an existing scalp and curve or mesh hair source. Use for bounded static contact and silhouette work; exclude rigs, animation, full-character modeling, texture painting, and runtime integration.
---

# Produce Static Character Hair

Turn an approved static hair repair brief into a small editable Candidate. Art Director owns visual intent and critique; a named task-scoped executor performs the edit; Engineering receives technical receipts; QA verifies independently; Reviewer reviews; Project Owner adopts. Ownership does not authorize self-execution or approval.

## Entry and scope

Require the actual editable scalp and hair source, intended viewing conditions, protected geometry, permitted local change area, rights/provenance, output allowlist, and receiver. First inspect the real hierarchy and identify the scalp, any existing inner layer, and the separate responsibilities of root, crown, and fringe. State which existing mesh is the support surface for each repaired root: it can be scalp or an existing hair foundation, so upper roots must not be forced onto bare skin. Do not diagnose a continuity defect by adding flat cards or unrelated layers over it.

Record each strand's root and tip as explicit control indices or vertex sets, and name the complete intact objects. A first control point is not inherently a root, and unsigned surface distance cannot establish which end is attached. Check these declarations against the source and images before editing. If the task is ambiguous or its protected object is visibly defective, return the precise contract conflict instead of guessing an endpoint or altering the protected object. A blind test may withhold acceptance measurements, but not the authorized edit boundary or semantic root/tip identity.

This Working method covers static coarse curve or mesh hair root/inner-layer continuity. The helper has two deliberately limited routes:

- one non-cyclic `CURVE` strand with one `POLY` or `BEZIER` spline: inspect, contact report, and local root projection;
- one editable mesh hair or inner-layer object: project only caller-declared vertices with caller-declared weights, explicit ray direction, signed surface offset, and an optional allowed scalp-face region.

The helper does not represent the whole method or automatically create a hairstyle. Unsupported curve topology, Armatures, shape keys, active animation data, a non-allowlisted modifier, or a missing scalp mesh return `unsupported` before any source edit. The explicit static modifier allowlist is intentionally small; an uncertain modifier is unsupported. A mesh route does not infer an allowed region, choose all vertices, or silently turn a directional miss into nearest/radial projection.

The method excludes rigging, animation, deformation, complete character production, texture painting or baking, full material/lookdev, engine integration, runtime, device/player, and performance claims.

## Repair method

1. Freeze the user-approved proportion, visible silhouette, intact inner layer, and declared tips. Do not freeze defective root topology merely because it is original.
2. Query the evaluated scalp at the actual repair point. For mesh projection, require an explicit target ray direction; add an allowed face set whenever the task needs a verified target region. A ray miss or non-region hit is a diagnostic, not an invitation to choose a closer surface.
3. Make the smallest local source edit that restores continuity. Preserve the exterior silhouette while changing an authorized inner layer when that is the real cause. For a thick curve end, its center on a surface does not prove the circular cap is hidden. `project-root` therefore requires a caller-selected non-negative scene-unit root depth and moves the root inward along the evaluated outward support normal. Choose that depth from the actual cap size and intended review views; the helper embeds no default.
4. At the root, orient the local section to the scalp tangent, use a flattened contact section when the editable representation supports it, and grow volume gradually toward the crown. Keep frame signs coherent along the strand so an opposite-axis transition cannot collapse the local orientation.
5. Review the actual saved source in normal material, neutral-gray clay, and an elevated view. Fixed cameras must still show the same asset, not hide the failure. Distance is diagnosis only; Art Director judges visible continuity and silhouette.

Curve projection does not reshape cross-sections or invent a crown/fringe solution. Mesh projection changes only the declared non-protected vertices; local volume, section shape, and artistic continuity remain an authorized editor decision.

When a thick capped mesh root still reads as a cut stump after contact is restored, use the separately authorized [root-prefix topology method](references/root-prefix-flow.md). It replaces the defective prefix while retaining a declared seam and the original middle/tip; it is a manual construction method, not an operation implemented by the projection helper. Do not keep deepening projection or inflating the foundation to hide a topology defect.

## Source and evidence

Use absolute, distinct input, output, and report paths. Save a new editable output, reopen it in a fresh DCC process, and record source/output identities, protected geometry checks, actual review views, tool version, and helper report. The curve route records its requested signed depth, all controls changed after reopen (including automatic Bezier handles), and verifies the declared tip before save and after reopen. The mesh route compares topology and all non-selected vertices after reopen. On an individual directional miss, it writes a create-only diagnostic report and creates no output blend, retaining the input coordinates.

Preserve failures and invalidated outputs. Keep private acceptance measurements out of the executor-visible brief when the task uses a blind transfer test. Read [helper usage](references/helper-usage.md) before invoking the script. Run `--help` before first use and `--self-test` after changing the helper. A later independent forward test must use an abstract fixture that the author did not repair.

The helper's depth and contact report does not guarantee cap concealment or visual continuity. Review the saved source in normal material, neutral gray, and elevated views before reporting `ready_candidate`, `failed`, `blocked`, or `needs_topology_route` from actual evidence. A valid helper run, static render, or reopened file does not prove character quality, broad hair coverage, engine behavior, or formal plugin adoption.
