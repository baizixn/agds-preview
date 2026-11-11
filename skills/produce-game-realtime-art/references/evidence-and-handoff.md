# Evidence and handoff

## Evidence tiers

Record each claim at exactly the evidence tier obtained:

- `static_source`: schema, bounds, source/hash, rights, file structure and deterministic offline reference generation.
- `offline_visual_reference`: fixed diagrams or renders for professional review; not engine output.
- `engine_receipt`: imported/mapped artifact and receipt identity in the routed engine.
- `runtime`: event binding, transitions, stop/recycle, concurrency, lighting state change and exposure behavior.
- `device_or_player`: hardware rendering, comfort, accessibility, usability or player understanding.

A lower tier cannot fill a higher tier. Missing runtime permission is not a static failure; mark runtime claims `Not Run` and name the receiver/checkpoint.

## Handoff identity

Use a stable `handoff_id` and `asset_revision`. Keep editable leaves separate from the derived definition. In the N5 v1/r4 route, a future definition carries both `source_manifest_sha256` and `legacy_source_sha256`; both are the raw-byte SHA-256 of detached `source-manifest.json`. A legacy `source_sha256`, when retained for compatibility, must equal the same value. Canonical editable sources remain individually bound by manifest leaf `path`, `byte_size`, `sha256` and `role`; provenance and derived references are not canonical editable leaves. The detached manifest excludes itself.

Rebuild in this exact order: leaf entries, detached manifest, definition bindings, HANDOFF revision/identity, then the self-excluding outer package manifest last. A complete integrity fixture must independently reject stale detached, stale definition, stale HANDOFF and outer self-inclusion states. The current N5 r4 mapping is usable for offline binding, but its independent integrity review remains `revise`; do not restate it as a complete integrity pass.

The package must identify executor, Art brief/revision, GD event/revision, Engineering interface/revision/hash, creator and rights state, generated/derived files, validation command and exit status, attempted corrections, protected files/roots, receiver, and invalidation triggers.

## Finite failure matrix

Select only failures routed by the task. For each, pair one normal control with one discriminating static/structural counterexample where that layer can decide. Runtime-only failures such as real event binding, actual instance recycling, concurrency legibility, exposure adaptation, flicker and performance must not be converted into static passes.
