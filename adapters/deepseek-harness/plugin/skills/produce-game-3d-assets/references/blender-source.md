# Blender source helper

This optional helper runs in an existing Blender installation. It does not install tools, repair geometry, set design thresholds, or replace independent acceptance.

Integration entry rule: this exact N0 leaf is retained as an internal implementation. Its bare CLI below documents legacy mechanics only and is not an authorized production entry. Use [the Engineering-owned current-process consumer](blender-preflight.md), which verifies task/source/tool/process/schema identity and exact output allowlist before calling it. A previous process report cannot authorize writes. The inherited N0 local evidence was not rerun by this integration; runtime/device/player/performance remains not_verified.

```text
blender --background --factory-startup --python-exit-code 1 --python /absolute/path/scripts/blender_source.py -- --output-root /absolute/approved/root --input /absolute/path/source.blend --report /absolute/path/new-report.json
blender --background --factory-startup --python-exit-code 1 --python /absolute/path/scripts/blender_source.py -- --output-root /absolute/approved/root --input /absolute/path/source.blend --report /absolute/path/new-export-report.json --root AssetRoot --export /absolute/path/new-asset.glb
```

Inputs are an editable `.blend` or a static `.glb`; GLB import deletes factory startup objects and verifies the scene is empty first. `--root` is the caller's exact object name. An exported hierarchy accepts only MESH and EMPTY objects and excludes animations, lights and cameras. Root selection is not a substitute for inspecting helper meshes already parented to that root.

The required `--output-root` must be the existing, approved write directory. It and every output path must be absolute. `validate_output_paths(output_root, paths)` resolves paths, rejects paths outside that root (including existing symlink resolution), existing paths and duplicate paths before file operations. Fixture save/render/export operations can reuse this preflight. All output paths must be new, mutually different, and different from the input. Existing files are refused before opening the input or exporting. No source file is saved. Missing roots fail with a nonzero Blender exit when `--python-exit-code 1` is supplied. An export failure may leave an incomplete new GLB: inspect the process exit and do not consume partial outputs. Use fresh output paths for a deliberate retry; do not suppress failures.

The report records input SHA256, Blender version, editable mesh topology hash, evaluated vertex world bounds in Blender units, scene `scale_length`, converted bounds in meters, triangle counts, parent names, local/world matrices, and quaternions derived from those matrices. Blender quaternion order is WXYZ. Rotation mode and an unused Euler channel are not proof of actual rotation. Negative/nonuniform scale remains visible in matrices and scale; matrix-derived quaternion alone does not encode scale or reflection.

The report includes scene/material facts and removed startup object names for GLB. Its bounding box cannot prove wall thickness, bevel radius, local clearance or visual quality. Those need task-specific section/ray/vertex measurements and real image inspection, performed outside the generic helper. The script does not interpret custom properties as measurements or assert acceptance.

After export, run a separate factory-startup invocation on the GLB and inspect the result. Native process exit, report, selected inventory and input hash belong together. Source creation/save/reopen and engine import are distinct evidence levels. Supported execution is bounded static/rigid assets; rigs, animation, simulations and unknown dependencies require separately routed work.
