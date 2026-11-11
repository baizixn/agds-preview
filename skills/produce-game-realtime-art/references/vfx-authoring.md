# VFX authoring and N5 handoff

Use this mode only when an approved event contract defines what `telegraph`, `impact` and `dissipate` mean.

## Source and phase design

Create one editable authoring source that names the effect/revision, event binding, visual grammar, each phase's duration, emission, particle lifetime, size, color and normalized size-curve points, plus the stop/recycle intent. Keep `loop=false`. Use shape, timing, motion or value change as a non-color cue. Create a detached `source-manifest.json` that lists this source and its leaf-file SHA-256; the manifest must not list or hash itself.

The source-derived `n4-vfx-definition.json` for the N5 v1 route has this minimum shape:

```json
{
  "schema_version": "n4-particle-definition-v1",
  "effect_id": "string",
  "asset_revision": "string",
  "source_sha256": "SHA-256 of detached source-manifest.json",
  "renderer_route": "builtin-particlesystem-proposed",
  "phases": {
    "telegraph": {"duration_seconds": 0.1, "emission_rate": 1, "start_lifetime_seconds": 0.1, "start_size": 1, "color": "#RRGGBBAA", "size_curve_points": [{"t": 0, "value": 1}]},
    "impact": {"duration_seconds": 0.1, "emission_rate": 1, "start_lifetime_seconds": 0.1, "start_size": 1, "color": "#RRGGBBAA", "size_curve_points": [{"t": 0, "value": 1}]},
    "dissipate": {"duration_seconds": 0.1, "emission_rate": 0, "start_lifetime_seconds": 0.1, "start_size": 1, "color": "#RRGGBBAA", "size_curve_points": [{"t": 0, "value": 1}]}
  },
  "loop": false,
  "lifetime_seconds": 0.3,
  "rights_state": "string"
}
```

Every phase duration, particle lifetime and start size is positive; emission is non-negative; every curve is non-empty with `t` in `[0,1]` and positive values; color is `#RRGGBBAA`. The top-level lifetime must cover the three phase durations or the handoff must name a compatible stop strategy. N5 maps fields into native Unity `ParticleSystem`; the JSON is not a runtime component.

## Scope boundary

For the frozen first route, do not require URP/HDRP, VFX Graph, third-party shaders, fonts or downloaded textures. Optional original texture or mesh authoring may remain a non-runtime exploration attachment only when the task requests it; label it unmapped until Engineering accepts a format. Do not let such an attachment silently become a dependency of the N5 v1 receipt.

Static rejection covers a missing phase, invalid/empty curve, `loop=true`, missing or mismatched detached-manifest or leaf hash, unsafe manifest path, non-positive lifetime/size/duration, invalid color, or absent stop/recycle intent. Whether emission actually stops, instances recycle, events bind, or concurrent effects remain legible requires N5 runtime evidence and stays `Not Run` before that evidence exists.
