# Continuous mesh root prefix

Use only for an authorized static mesh edit when an exposed root cap or abrupt shoulder remains visible. This recipe does not infer a hairstyle, choose the support surface, or supply artistic coordinates. The projection helper does not execute it.

## Declare the editable boundary

Identify the existing root cap, prefix faces, an ordered seam ring, and the next protected ring. Freeze the seam, middle/tip, unrelated objects, materials and viewing conditions. Record vertex and face mappings. If the source has UVs, custom normals, attributes or deformation data, explicitly preserve their mapped data or route the unsupported reconstruction; never discard them silently. Do not apply a ring recipe to an unstructured mesh by guessing indices.

## Construct the connection

1. Pick a support location from the actual crown or hair foundation. Place a small root start inside that support, with burial chosen from local section size and visible overlap. Do not force an upper root to bare scalp.
2. Remove the defective root cap and prefix faces. Retain all faces beyond the seam and their mapped data. A buried old cap is not evidence that it was removed.
3. Build a centerline from the start to the seam center. A cubic Hermite curve can match an explicit start tangent and the existing seam-to-next-ring tangent. Its basis is `(2t³-3t²+1)P0 + (t³-2t²+t)M0 + (-2t³+3t²)P1 + (t³-t²)M1`; tangents are derivatives over the same parameter interval, not unscaled neighboring-point differences.
4. Grow a flattened section gradually from the narrow start to the exact seam section. Keep orientation signs coherent; do not interpolate opposing frames through zero. Match individual seam vertex directions as well as the centerline so a smooth centerline does not conceal a surface shoulder. Inspect section size progression for a bulge or pinch rather than assuming a cubic interpolation is monotonic.
5. Connect the new rings and root pole with consistent winding. Keep the original seam and all protected vertices exact. Verify boundary edges, finite coordinates, retained face mappings and source attributes in a fresh reopened file. Closed topology does not prove the absence of self-intersection.
6. Where an existing inner layer needs local support, wrap that patch along the actual side surface and blend its border. Check the neighboring outer locks. A broad plane pushed forward can create a visible board or intersecting wrinkle even when it closes a gap.

## Judge the saved result

Use normal material and neutral clay at fixed front, side and elevated views. Reject an exposed cut cap, abrupt shoulder, open support gap, broad exposed helmet band, pinch or intersecting patch. Distinguish intentional overlapping locks from these defects. Regress the original head/face proportions and exterior silhouette.

Keep this static source evidence separate from rigging, shading fidelity, engine integration, performance and full-character capability. The recipe needs a task-specific executor and independent checks; registration alone does not establish transfer to arbitrary topology.
