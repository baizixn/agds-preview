#!/usr/bin/env python3
"""Static validator for N4 realtime-art source packs.

This validates editable data and source identity only. It never claims Unity,
runtime, lifecycle, performance, device, or player evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from pathlib import Path


COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{8}$")
SHA_RE = re.compile(r"^[0-9A-F]{64}$")


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("root must be an object")
    return data


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def require_number(value, label: str, errors: list[str], *, positive=False, nonnegative=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        errors.append(f"{label}: expected number")
        return
    if not math.isfinite(value):
        errors.append(f"{label}: must be finite")
        return
    if positive and value <= 0:
        errors.append(f"{label}: must be > 0")
    if nonnegative and value < 0:
        errors.append(f"{label}: must be >= 0")


def source_manifest_claim(definition: dict, errors: list[str]) -> str | None:
    """Resolve legacy or future detached-manifest binding without self-hashing."""
    legacy = definition.get("source_sha256")
    explicit = definition.get("source_manifest_sha256")
    compatible = definition.get("legacy_source_sha256")
    has_future = explicit is not None or compatible is not None
    if has_future:
        for key, value in (
            ("source_manifest_sha256", explicit),
            ("legacy_source_sha256", compatible),
        ):
            if not isinstance(value, str) or not SHA_RE.fullmatch(value):
                errors.append(f"{key}: expected 64 uppercase hexadecimal characters")
        if isinstance(explicit, str) and isinstance(compatible, str) and explicit != compatible:
            errors.append("source manifest bindings: future fields must be equal")
        if isinstance(legacy, str) and isinstance(explicit, str) and legacy != explicit:
            errors.append("source_sha256: compatibility value must equal source_manifest_sha256")
        return explicit if isinstance(explicit, str) and SHA_RE.fullmatch(explicit) else None
    if not isinstance(legacy, str) or not SHA_RE.fullmatch(legacy):
        errors.append("source binding: expected future dual fields or legacy source_sha256")
        return None
    return legacy


def validate_source_manifest(definition: dict, manifest: dict, manifest_path: Path, errors: list[str]):
    claimed = source_manifest_claim(definition, errors)
    if claimed is None:
        return
    actual = sha256(manifest_path)
    if claimed != actual:
        errors.append(f"source_sha256: mismatch, actual={actual}")
    manifest_version = manifest.get("manifest_schema_version")
    if manifest_version not in {"n4-source-manifest-v1", "n4-source-manifest-v2"}:
        errors.append("source-manifest.manifest_schema_version: unsupported")
    if manifest_version == "n4-source-manifest-v2":
        if manifest.get("path_semantics") != "package_root_relative_posix":
            errors.append("source-manifest.path_semantics: must be package_root_relative_posix")
        if manifest.get("hash_semantics") != "sha256_of_raw_file_bytes_no_normalization":
            errors.append("source-manifest.hash_semantics: unsupported")
        if manifest.get("self_reference_policy") != "detached_manifest_not_listed_as_leaf":
            errors.append("source-manifest.self_reference_policy: must exclude the detached manifest")
        base = manifest_path.parent.parent.resolve()
    else:
        if manifest.get("self_reference_policy") != "manifest_excluded_from_its_own_files":
            errors.append("source-manifest.self_reference_policy: must exclude the manifest itself")
        base = manifest_path.parent.resolve()
    files = manifest.get("files")
    if not isinstance(files, list) or not files:
        errors.append("source-manifest.files: expected non-empty array")
        return
    if manifest_version == "n4-source-manifest-v2" and manifest.get("canonical_leaf_count") != len(files):
        errors.append("source-manifest.canonical_leaf_count: does not match files")
    seen: set[str] = set()
    for index, entry in enumerate(files):
        label = f"source-manifest.files[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{label}: expected object")
            continue
        rel = entry.get("path")
        claimed_leaf = entry.get("sha256")
        claimed_bytes = entry.get("byte_size")
        role = entry.get("role")
        provenance = entry.get("provenance")
        if not isinstance(rel, str) or not rel or "\\" in rel or Path(rel).is_absolute() or ".." in Path(rel).parts:
            errors.append(f"{label}.path: must be a safe relative POSIX path")
            continue
        if rel in seen:
            errors.append(f"{label}.path: duplicate")
        seen.add(rel)
        leaf = (base / rel).resolve()
        try:
            leaf.relative_to(base)
        except ValueError:
            errors.append(f"{label}.path: escapes manifest directory")
            continue
        if leaf == manifest_path.resolve():
            errors.append(f"{label}.path: manifest must not hash itself")
            continue
        if not leaf.is_file():
            errors.append(f"{label}.path: leaf missing")
            continue
        if isinstance(claimed_bytes, bool) or not isinstance(claimed_bytes, int) or claimed_bytes < 0:
            errors.append(f"{label}.byte_size: expected non-negative integer")
        elif claimed_bytes != leaf.stat().st_size:
            errors.append(f"{label}.byte_size: mismatch")
        if not isinstance(claimed_leaf, str) or not SHA_RE.fullmatch(claimed_leaf):
            errors.append(f"{label}.sha256: expected 64 uppercase hexadecimal characters")
        elif claimed_leaf != sha256(leaf):
            errors.append(f"{label}.sha256: mismatch")
        if not isinstance(role, str) or not role:
            errors.append(f"{label}.role: expected non-empty string")
        elif not role.startswith("editable"):
            errors.append(f"{label}.role: detached manifest may contain canonical editable leaves only")
        if not isinstance(provenance, str) or not provenance:
            errors.append(f"{label}.provenance: expected non-empty string")


def validate_vfx(definition: dict, source: dict, manifest: dict, manifest_path: Path) -> list[str]:
    errors: list[str] = []
    expected_top = {
        "schema_version",
        "effect_id",
        "asset_revision",
        "renderer_route",
        "phases",
        "loop",
        "lifetime_seconds",
        "rights_state",
    }
    missing = sorted(expected_top - set(definition))
    if missing:
        errors.append(f"top-level: missing {', '.join(missing)}")
    allowed_top = expected_top | {
        "source_sha256",
        "source_manifest_sha256",
        "legacy_source_sha256",
        "source_manifest_path",
        "handoff_revision",
        "source_integrity_contract",
    }
    unexpected = sorted(set(definition) - allowed_top)
    if unexpected:
        errors.append(f"top-level: unsupported extension fields {', '.join(unexpected)}")
    if definition.get("schema_version") != "n4-particle-definition-v1":
        errors.append("schema_version: unsupported")
    if definition.get("renderer_route") != "builtin-particlesystem-proposed":
        errors.append("renderer_route: must be builtin-particlesystem-proposed")
    if definition.get("source_manifest_path") not in {None, "source-manifest.json", "vfx/source-manifest.json"}:
        errors.append("source_manifest_path: unexpected VFX detached manifest path")
    if definition.get("loop") is not False:
        errors.append("loop: must be false")
    for key in ("effect_id", "asset_revision", "rights_state"):
        if not isinstance(definition.get(key), str) or not definition[key].strip():
            errors.append(f"{key}: expected non-empty string")
    require_number(definition.get("lifetime_seconds"), "lifetime_seconds", errors, positive=True)

    phases = definition.get("phases")
    required_phases = ("telegraph", "impact", "dissipate")
    if not isinstance(phases, dict):
        errors.append("phases: expected object")
        phases = {}
    if set(phases) != set(required_phases):
        errors.append("phases: must contain exactly telegraph, impact, dissipate")
    phase_total = 0.0
    for phase_name in required_phases:
        phase = phases.get(phase_name)
        if not isinstance(phase, dict):
            errors.append(f"phases.{phase_name}: missing object")
            continue
        for key in ("duration_seconds", "start_lifetime_seconds", "start_size"):
            require_number(phase.get(key), f"phases.{phase_name}.{key}", errors, positive=True)
        require_number(phase.get("emission_rate"), f"phases.{phase_name}.emission_rate", errors, nonnegative=True)
        duration = phase.get("duration_seconds")
        if isinstance(duration, (int, float)) and not isinstance(duration, bool) and duration > 0:
            phase_total += float(duration)
        color = phase.get("color")
        if not isinstance(color, str) or not COLOR_RE.fullmatch(color):
            errors.append(f"phases.{phase_name}.color: expected #RRGGBBAA")
        curve = phase.get("size_curve_points")
        if not isinstance(curve, list) or not curve:
            errors.append(f"phases.{phase_name}.size_curve_points: expected non-empty array")
            continue
        previous_t = -1.0
        for index, point in enumerate(curve):
            label = f"phases.{phase_name}.size_curve_points[{index}]"
            if not isinstance(point, dict):
                errors.append(f"{label}: expected object")
                continue
            t = point.get("t")
            value = point.get("value")
            require_number(t, f"{label}.t", errors)
            require_number(value, f"{label}.value", errors, positive=True)
            if isinstance(t, (int, float)) and not isinstance(t, bool):
                if not 0 <= t <= 1:
                    errors.append(f"{label}.t: must be in [0,1]")
                if t < previous_t:
                    errors.append(f"{label}.t: curve points must be ordered")
                previous_t = float(t)

    lifetime = definition.get("lifetime_seconds")
    if isinstance(lifetime, (int, float)) and not isinstance(lifetime, bool) and lifetime + 1e-9 < phase_total:
        errors.append("lifetime_seconds: must cover sum of phase durations for this v1 handoff")

    validate_source_manifest(definition, manifest, manifest_path, errors)
    if source.get("source_schema_version") != "n4-vfx-authoring-source-v1":
        errors.append("source_schema_version: unsupported VFX source")
    if source.get("phase_order") != list(required_phases):
        errors.append("source.phase_order: must be telegraph, impact, dissipate")
    lifecycle = source.get("lifecycle")
    if not isinstance(lifecycle, dict):
        errors.append("source.lifecycle: expected object")
    else:
        if lifecycle.get("stop_emission_after_phase") != "dissipate":
            errors.append("source.lifecycle.stop_emission_after_phase: must be dissipate")
        if lifecycle.get("recycle_policy") != "release_after_max_particle_lifetime":
            errors.append("source.lifecycle.recycle_policy: unsupported or missing")
    if not isinstance(source.get("event_contract_ref"), str) or not source["event_contract_ref"].strip():
        errors.append("source.event_contract_ref: expected non-empty string")
    return errors


def validate_lighting(definition: dict, source: dict, manifest: dict, manifest_path: Path) -> list[str]:
    errors: list[str] = []
    required = {
        "schema_version",
        "scene_id",
        "asset_revision",
        "renderer_route",
        "interface_state",
        "fixed_camera",
        "backgrounds",
        "focal_object",
        "surface_groups",
        "exposure_policy",
        "states",
        "rights_state",
    }
    missing = sorted(required - set(definition))
    if missing:
        errors.append(f"top-level: missing {', '.join(missing)}")
    if definition.get("schema_version") != "n4-lighting-definition-v1":
        errors.append("schema_version: unsupported")
    if definition.get("renderer_route") != "builtin-lighting-proposed":
        errors.append("renderer_route: must be builtin-lighting-proposed")
    if definition.get("interface_state") not in {
        "pending_n5_lighting_format_confirmation",
        "proposed_n5_builtin_lighting_receipt_v1",
        "mapping_candidate_accepted_at_r2_source_integrity_fixture_r4_revise",
    }:
        errors.append("interface_state: unsupported lighting handoff state")
    if definition.get("source_manifest_path") not in {"source-manifest.json", "lighting/source-manifest.json"}:
        errors.append("source_manifest_path: unexpected lighting detached manifest path")
    for key in ("scene_id", "asset_revision", "focal_object", "rights_state"):
        if not isinstance(definition.get(key), str) or not definition[key].strip():
            errors.append(f"{key}: expected non-empty string")
    camera = definition.get("fixed_camera")
    if not isinstance(camera, dict):
        errors.append("fixed_camera: expected object")
    else:
        for key in ("projection", "position", "look_at", "vertical_fov_degrees"):
            if key not in camera:
                errors.append(f"fixed_camera.{key}: missing")
        require_number(camera.get("vertical_fov_degrees"), "fixed_camera.vertical_fov_degrees", errors, positive=True)
    backgrounds = definition.get("backgrounds")
    if not isinstance(backgrounds, list) or len(backgrounds) != 2:
        errors.append("backgrounds: expected exactly two variants")
    else:
        ids = [entry.get("id") for entry in backgrounds if isinstance(entry, dict)]
        if len(set(ids)) != 2 or any(not isinstance(value, str) or not value for value in ids):
            errors.append("backgrounds: expected two unique non-empty ids")
    groups = definition.get("surface_groups")
    if not isinstance(groups, list) or len(groups) < 3:
        errors.append("surface_groups: expected at least three protected groups")
    exposure = definition.get("exposure_policy")
    if not isinstance(exposure, dict):
        errors.append("exposure_policy: expected object")
    else:
        if exposure.get("mode") != "manual_fixed_no_postprocess":
            errors.append("exposure_policy.mode: must avoid unowned automatic/postprocess exposure")
        if exposure.get("auto_exposure") is not False:
            errors.append("exposure_policy.auto_exposure: must be false")
    states = definition.get("states")
    if not isinstance(states, list) or len(states) != 2:
        errors.append("states: expected exactly two lighting states")
    else:
        state_ids = []
        for index, state in enumerate(states):
            if not isinstance(state, dict):
                errors.append(f"states[{index}]: expected object")
                continue
            state_ids.append(state.get("id"))
            if state.get("focus_target") != definition.get("focal_object"):
                errors.append(f"states[{index}].focus_target: must preserve focal_object")
            lights = state.get("lights")
            if not isinstance(lights, list) or not lights:
                errors.append(f"states[{index}].lights: expected non-empty array")
        if len(set(state_ids)) != 2 or any(not isinstance(value, str) or not value for value in state_ids):
            errors.append("states: expected two unique non-empty ids")
    validate_source_manifest(definition, manifest, manifest_path, errors)
    if source.get("source_schema_version") != "n4-lighting-authoring-source-v1":
        errors.append("source_schema_version: unsupported lighting source")
    if source.get("fixed_camera_id") != definition.get("fixed_camera", {}).get("id"):
        errors.append("source.fixed_camera_id: does not match definition")
    if source.get("scene_id") != definition.get("scene_id"):
        errors.append("source.scene_id: does not match definition")
    return errors


def validate_lighting_binding(binding: dict, definition: dict) -> list[str]:
    errors: list[str] = []
    if binding.get("schema_version") != "n5-lighting-receipt-binding-v1":
        errors.append("binding.schema_version: unsupported")
    if binding.get("binding_state") != "static_contract_bound_runtime_not_run":
        errors.append("binding.binding_state: must preserve runtime Not Run")
    geometry = binding.get("geometry_ingestion")
    if not isinstance(geometry, dict):
        errors.append("binding.geometry_ingestion: expected object")
    else:
        transform = geometry.get("root_transform")
        if transform != {
            "position": [0, 0, 0],
            "rotation_euler_degrees": [0, 0, 0],
            "scale": [1, 1, 1],
        }:
            errors.append("binding.geometry_ingestion.root_transform: must be identity")
        if geometry.get("scene_layout_usage") != "bounds_anchor_material_camera_identity_validation_only":
            errors.append("binding.geometry_ingestion.scene_layout_usage: must be validation only")
        if geometry.get("rebuild_primitives") is not False:
            errors.append("binding.geometry_ingestion.rebuild_primitives: must be false")
        if geometry.get("reapply_layout_transform") is not False:
            errors.append("binding.geometry_ingestion.reapply_layout_transform: must be false")
    source_identity = binding.get("source_identity")
    if not isinstance(source_identity, dict):
        errors.append("binding.source_identity: expected object")
    else:
        if source_identity.get("legacy_source_sha256_semantics") != "source_manifest_sha256":
            errors.append("binding.source_identity.legacy_source_sha256_semantics: unsupported")
        if source_identity.get("source_manifest_path") != "lighting/source-manifest.json":
            errors.append("binding.source_identity.source_manifest_path: unexpected")
        definition_claim = definition.get("source_manifest_sha256", definition.get("source_sha256"))
        if source_identity.get("source_manifest_sha256") != definition_claim:
            errors.append("binding.source_identity.source_manifest_sha256: does not match definition")
        if source_identity.get("outer_package_manifest_policy") != "n5_compute_from_final_outer_manifest":
            errors.append("binding.source_identity.outer_package_manifest_policy: unsupported")
    render = binding.get("render_mapping")
    if not isinstance(render, dict):
        errors.append("binding.render_mapping: expected object")
    else:
        if render.get("source_color_encoding") != "sRGB_hex":
            errors.append("binding.render_mapping.source_color_encoding: must be sRGB_hex")
        if render.get("intensity_unit") != "builtin_relative_intensity":
            errors.append("binding.render_mapping.intensity_unit: unsupported")
        if render.get("exposure_control") != "none_no_postprocess_package":
            errors.append("binding.render_mapping.exposure_control: unsupported")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kind", choices=("vfx", "lighting"), required=True)
    parser.add_argument("--definition", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--binding", type=Path)
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()

    try:
        definition = load_json(args.definition)
        source = load_json(args.source)
        manifest = load_json(args.manifest)
        errors = (
            validate_vfx(definition, source, manifest, args.manifest)
            if args.kind == "vfx"
            else validate_lighting(definition, source, manifest, args.manifest)
        )
        if args.binding:
            if args.kind != "lighting":
                errors.append("binding: only supported for lighting")
            else:
                binding = load_json(args.binding)
                errors.extend(validate_lighting_binding(binding, definition))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors = [f"input: {exc}"]

    result = {
        "kind": args.kind,
        "definition": str(args.definition.resolve()),
        "source": str(args.source.resolve()),
        "manifest": str(args.manifest.resolve()),
        "binding": str(args.binding.resolve()) if args.binding else None,
        "evidence_tier": "static_source",
        "valid": not errors,
        "errors": errors,
        "runtime_verified": False,
    }
    output = json.dumps(result, ensure_ascii=False, indent=2)
    print(output)
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(output + "\n", encoding="utf-8")
    return 0 if not errors else 2


if __name__ == "__main__":
    sys.exit(main())
