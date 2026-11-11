# Lighting authoring and handoff

Use this mode for one approved synthetic scene, fixed camera and finite lighting states. Do not infer a product's lighting language from the sample.

## Editable source

Version the scene layout, primitive or mesh source, material groups, fixed camera, background variants, light states, ambient contribution and exposure policy. Each material group must state the surface distinction it protects. Each light state must name the intended focal read and the unchanged scene/material identities.

For a built-in-renderer candidate with no new package, prefer ordinary directional/point/spot-light parameters, material albedo/emission choices and a fixed manual camera/render policy. Do not depend on pipeline-specific volume profiles or automatic exposure. If the approved brief uses the word exposure, express it as a fixed art intent and identify the exact Engineering mapping as proposed or unresolved; never imply that an uninstalled post-process feature exists.

The N4 handoff may propose `n4-lighting-source.json` containing source identity/hash, renderer route, fixed camera, backgrounds, surface groups and named lighting states. Before N5 confirms a mapping, label it `pending_n5_lighting_format_confirmation`; after a routed N5 addendum exists, add a separate receipt-binding file that identifies that exact addendum rather than rewriting the artistic source. Its `source_sha256` hashes a detached source manifest, not this JSON. The editable scene geometry and material source must remain separately inspectable and listed as manifest leaves.

For the current N5 built-in mapping, imported OBJ vertices are the sole future runtime geometry and the Unity root transform stays identity: position and rotation zero, scale one. `scene-layout.json` is bounds/anchor/material/camera identity evidence only; do not rebuild its primitives or apply its object transforms again to the OBJ. A receipt-binding counterexample that reapplies layout transforms must be rejected. Source colors are sRGB hex, light intensity is only `builtin_relative_intensity`, and the no-postprocess policy means no invented exposure control. The mapping itself was accepted at N5 r2; the separate N5 r4 source-integrity fixture remains `revise`, so this Skill may bind an offline package but must not claim a native receipt or complete integrity-fixture pass.

## Review and evidence

Generate the same camera framing for every state/background comparison. Protect focal subject, foreground/midground/background separation, major material distinctions and non-color cues. Test one normal source plus bounded static counterexamples such as a missing state, changed camera, clipped/merged surface group or a state whose declared focus differs from its configuration.

An offline diagram can support configuration review but cannot prove Unity lighting, shadowing, tone/exposure stability, material response, flicker, performance or device output. Those claims remain `Not Run` until N5 maps the source into the frozen engine and records them.
