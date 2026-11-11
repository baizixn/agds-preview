# Spatial reconstruction: use evidence to choose geometry

Apply to fidelity work; do not redesign an approved reference target. Reference access does not imply asset extraction or redistribution rights. Matching an image, recovering multi-view relationships and reproducing a traversable scene are separate claims.

## The minimal spatial worksheet

Keep the worksheet in the product workspace, not a shared Skill repository. Reuse it during assembly and comparison. Add only rows that decide the work:

| Record | Required decision content |
|---|---|
| Shot | source/path and frame/time; region; viewport/aspect/crop; projection; observed or estimated pose/FOV/eye height |
| Anchor/relation | stable IDs; observation versus inference versus unknown; supporting/contradicting shots; confidence reason; relevant relative distance, occlusion, contact or orientation |
| Scale | known metric provenance or provisional unit; uncertainty interval; alternative explanation; no invented real dimensions |
| Terrain section | plan line tied to anchors; terrace/slope/break/cliff/waterline heights as observed or inferred; which side view constrains each transition |
| Hypothesis test | competing camera/geometry explanations; coarse edit; predicted effect in every affected view; rejection condition |
| Spatial receipt | exact scene/camera revision; inspected captures; essential relations and preset tolerances; unresolved relations; judge; permitted next refinement |

For example, “the pier hides the lower hull in V1” is an observation; “the hull lies behind the pier” is an inference to test in V2; the submerged keel depth remains unknown. If no metric is known, use relative units and mark the scene's absolute scale provisional. Character proportions are not a reliable ruler without corroboration in stylized art.

## Camera calibration and shared graybox

1. Check crop, lens/perspective versus orthographic, horizon and roll before pose. Screen capture may contain UI or a shifted principal point; do not assume every image is a centered uncropped camera. Use reliable straight/parallel edges where available. Near-parallel image lines, non-right-angle geometry and heavily distorted views weaken vanishing-point solutions.
2. Choose tools from the image: manual camera fitting for organic/ambiguous scenes; a camera-matching tool such as fSpy only when its perspective/orthogonal-axis assumptions hold and the tool is available. It estimates camera parameters, not hidden geometry or absolute scale. Do not force stylized edges to be perpendicular to make the solver return a number.
3. Fit salient anchors with simple masses and voids. Use shared geometry across all views and carry the camera hypothesis ranges. Hold out a useful second/oblique view from initial fitting where coverage permits, then check it; this is a disconfirmation test, not a universal required number of cameras.
4. Draw a top-down relationship map for location/connectivity and cross-sections for terrain breaks. A plan contour cannot resolve a terrace versus smooth mound. Do not cover an unresolved bank with vegetation, foam or global terrain noise.
5. Compare normalized image anchor residuals only as diagnostics. Set meaningful tolerances with the brief/source precision before evaluating; no universal pixel percentage proves fidelity. Review silhouettes, negative space and contact visually as well. An aggregate score cannot compensate for one failed essential relation.

If every camera hypothesis fails the same local relation, inspect geometry; if many unrelated objects shift similarly, inspect the camera. This is a diagnostic clue, not an automatic classifier. Freeze the comparison settings when sufficient; a later justified recalibration invalidates the affected comparisons and retains the old evidence.

## Separate transform from shape

For a wall-mounted or adjacent cabinet, test world location, cabinet facing, cabinet depth/shape, inset screen-plane inclination, wall clearance and floor contact independently. A screen's trapezoid in a shot may arise from perspective, facing or real panel tilt; rotating the whole cabinet cannot repair an incorrect panel normal without affecting its feet and side silhouette.

For a vessel or similarly tilted object, distinguish world position, heading (bow direction), roll (side tilt), pitch (bow up/down), hull shape and waterline/draft. Record local axes and pivot so edits mean the same thing after import. A narrow visible side can mean rotation or foreshortening, not necessarily a narrow hull. Use shoreline/occlusion anchors and views at different positions to discriminate; lock/unlock only the uncertain variables. Time-varying reference motion must not be mistaken for inconsistent static geometry.

For an apparent water/contact gap, inspect actual transformed surface geometry before moving the object. Bounds only provide a coarse test; triangle-plane intersections and signed distances can distinguish crossing, touching and separation. A real crossing does not establish correct draft or reference pose. Diagnose only as far as source access and evidence permit.

Before fine modeling, test the proxy in all essential views. Missing evidence requires a specific extra side/oblique/time observation, or an explicitly bounded provisional hypothesis; it never permits a fabricated exact measurement. Continue independent supported work while that dependency waits.
