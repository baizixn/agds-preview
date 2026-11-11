# Scene craft: choose by the problem

These are decision aids, not a universal sequence. Examples are synthetic and introduce no project defaults.

## Layout and composition

Make a coarse top-down relationship map and a few player-eye views serve different purposes: the map checks connectivity, the views check perceived scale, occlusion and visual hierarchy. Distinguish a designed dead end from an accidental blockage. An art change that alters usable width, jump reach, cover, line of sight or an interaction boundary needs the design owner to resolve the changed behavior.

Check the largest silhouette at thumbnail size, then near/mid/far separation and local tangencies at use size. Move through approach, arrival and return views; a framed entrance can become invisible from the return direction. In an open space several landmarks may compete legitimately: judge their hierarchy by the current player task, not a mandatory single focal point everywhere.

If the image feels flat, test overlapping masses and value separation before adding clutter. If it feels empty, check whether the missing element is a mid-scale group or a landmark; increasing tiny prop count may make the same flat space noisier. A hero shot is useful but cannot alone validate an explorable environment.

## Terrain, ground and water boundaries

Choose mesh terrain, height-field terrain or a mixture from topology, editing needs and supported tools. Do not prescribe one tool for every environment. Block height differences and drainage/shore profiles before high-frequency noise. Check how the surface meets structures and whether the actual character can traverse intended slopes and steps.

Establish material regions at believable scale; use localized blending, decals or transition geometry when the engine/material route supports them. Inspect at grazing angles for floating edges and intersecting planes. A water plane is a visual placeholder unless the requested water rendering and interaction behavior are implemented. Neither fog nor vegetation should conceal an unresolved structural seam in acceptance views.

## Modular architecture

Treat a kit as an interoperable system rather than a collection of attractive parts. Record units, transforms, attachment plane, mesh/collider bounds and material alignment. Trial a turn, stacked interface, closure or other actual layout stress point. If the kit cannot close a loop without stretching, correct its interface or request a transition piece; do not disguise the error with a camera crop.

Use consistent repeatable structure, then vary silhouette, grouping, wear and transitions where the reference or brief supports it. Uniform random rotation of functional architecture is usually less credible than intentional variation. A custom landmark is justified by its contribution, not by a rule that every scene needs one.

## Vegetation and dressing

Place dominant tree/rock masses and route buffers manually before any scatter. Define a small number of distribution reasons: slope, shade, moisture, ground type, exposure or human activity, as appropriate to the art direction. Exclusion zones around traversable routes and interactions are first-class inputs. Preserve recognizable species/shape groups; vary their scale and orientation within plausible limits.

Check clusters, gaps and silhouettes from the moving camera. If more grass hides all surface transitions, inspect the transitions without grass before accepting. Roots, feet and props need credible ground contact. Dirt and debris should suggest a cause or use pattern; do not distribute every small asset uniformly.

Instancing, transparency coverage, shadow cost and culling are technical choices with visual consequences. Test a representative dense patch in-engine before expanding it. Reduce measured cost through the relevant mechanism; do not copy another engine's density or draw-call numbers.

## Materials and lighting

Make material families distinguishable through value, roughness and scale as well as hue. Keep texel scale consistent unless a deliberate exception serves the brief. In stylized work, authored simplification may take priority over physical detail; neither universal photorealism nor universal low-poly geometry is a default.

Use large lighting relationships to establish time, depth and emphasis. Investigate exposure, light direction, material response and local shadow before changing all of them at once. Lock the comparison settings while judging revisions. Do not hide scale or silhouette errors under bloom, depth of field, fog or color grading.

The diagnostic order is usually camera/scale → masses and voids → major value/color → materials/light → local detail. It is a causal aid, not a prohibition on early lighting or returning to a previous stage.
