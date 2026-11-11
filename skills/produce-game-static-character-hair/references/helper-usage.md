# Helper usage

The helper runs inside a fresh Blender background process. It has no product paths, object names, dimensions, thresholds, target regions, or repair targets. Every supplied input, output, and report path must be absolute; output and report must be new and distinct from each other and from input.

```powershell
<blender> --background --factory-startup --disable-autoexec --python <skill>/scripts/static_hair_contact.py -- --help
<blender> --background --factory-startup --disable-autoexec --python <skill>/scripts/static_hair_contact.py -- --self-test
```

For a curve route, pass the actual editable input, declared mesh support surface, and one non-cyclic curve strand. The support can be the scalp or an existing hair foundation; inspect its artistic role before projecting a root. `contact-report` writes only when `--report` names a new file. `project-root` requires new `--output` and `--report` paths plus explicit non-negative `--root-depth` in the task's scene units. It moves the root center inward along the evaluated outward support normal. Choose depth from the actual circular end-cap size and intended views; no depth is embedded by this helper. `--align-neighbor-tangent` is optional and still does not change a curve's circular cross-section.

```text
--input ABS_INPUT_BLEND --scalp SCALP_OBJECT --strand CURVE_OBJECT --mode contact-report --root-end start --report ABS_NEW_REPORT_JSON
--input ABS_INPUT_BLEND --scalp SUPPORT_SURFACE_OBJECT --strand CURVE_OBJECT --mode project-root --root-end start --root-depth TASK_SCENE_UNIT_VALUE --output ABS_NEW_BLEND [--align-neighbor-tangent] --report ABS_NEW_REPORT_JSON
```

For a mesh hair or inner-layer route, every changed vertex and weight is explicit. Protected tip/outer vertices are supplied separately and cannot overlap selected vertices. A directional ray is mandatory: the helper never defaults to closest-point or radial projection. `--allowed-face-indices` is optional but verifies that a hit belongs to the task-selected scalp region when supplied. The signed offset is task input; no value is embedded. The target scalp and hair object must be static: shape keys, active animation data, and modifiers outside the helper's explicit static nondeforming allowlist return `unsupported` before editing.

```text
--input ABS_INPUT_BLEND --scalp SCALP_OBJECT --strand MESH_OBJECT --mode mesh-project --vertex-indices 0,1 --vertex-weights 1,0.5 --protected-indices 8,9 --ray-direction 0,0,1 --surface-offset TASK_VALUE --allowed-face-indices 3,4 --output ABS_NEW_BLEND --report ABS_NEW_REPORT_JSON
```

Each mesh vertex gets a diagnostic. A ray miss or an allowed-region mismatch retains that input coordinate, writes a create-only report with `diagnostic_miss_no_output`, and creates no output blend. This is intentional; do not retry by replacing the ray with a nearest-surface fallback.

The curve report records the requested depth using the sign convention that inward along an outward surface normal is negative, as well as every point or handle changed after reopen. It verifies the declared tip before saving and after reopening. A center placed on the support surface can still leave a thick circular cap exposed; a report cannot guarantee concealment. Review the saved source in normal material, neutral-gray clay, and elevated views.
