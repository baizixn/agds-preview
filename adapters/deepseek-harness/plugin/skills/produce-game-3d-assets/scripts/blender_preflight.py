"""Engineering-owned current-process gate and rigid/static Blender consumer.

Only this CLI is the authorized production entry. Run in a fresh Blender 5.1.2
background factory process. The legacy source helper is an internal callee.
No report from a previous process is a write permit. No tool install or UI use.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import secrets
import sys
import time

SCHEMA_VERSION = "2.0.0"
PROCESS_NONCE = secrets.token_hex(32)
HERE = Path(__file__).resolve()
SCHEMA = HERE.parent.parent / "schema/blender_preflight_report.schema.json"
WRITER = HERE.parent / "blender_source.py"
# Exact LF bytes retained in Git and the release; never normalize at this gate.
LEGACY_WRITER_SHA256 = "5e05c312c7eff748d0e2ded4a988e9fa9800ecc7c2e906dd99e3e20a4c658270"


class GateError(ValueError):
    pass


def require(value, detail):
    if not value:
        raise GateError(detail)


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def absolute(raw):
    path = Path(raw)
    require(path.is_absolute(), "absolute path required")
    require(".." not in path.parts, "parent traversal refused")
    for item in (path, *path.parents):
        if item.exists() or item.is_symlink():
            require(not item.is_symlink() and not (getattr(item.lstat(), "st_file_attributes", 0) & 1024),
                    "linked/reparse path refused")
    return path.resolve()


def schema_check(value, schema, label="report"):
    """Validate the closed JSON Schema subset used by the shipped report schema.

    Unsupported keywords fail closed; this is not a general JSON Schema engine.
    """
    supported = {"$schema", "$id", "title", "description", "type", "properties", "required",
                 "additionalProperties", "items", "enum", "const", "pattern", "minimum",
                 "exclusiveMinimum", "minLength", "minItems"}
    require(not set(schema) - supported, "unsupported schema keyword")
    kinds = {"object": dict, "array": list, "string": str, "boolean": bool,
             "integer": int, "number": (int, float)}
    kind = schema.get("type")
    if kind:
        require(kind in kinds and isinstance(value, kinds[kind]), label + ": wrong type")
        if kind in {"number", "integer"}:
            require(not isinstance(value, bool) and math.isfinite(value), label + ": invalid number")
    if "const" in schema:
        require(type(value) is type(schema["const"]) and value == schema["const"], label + ": wrong constant")
    if "enum" in schema:
        require(value in schema["enum"], label + ": unsupported value")
    if "pattern" in schema:
        require(isinstance(value, str) and re.fullmatch(schema["pattern"], value), label + ": pattern")
    for key, ok in (("minimum", lambda x: value >= x), ("exclusiveMinimum", lambda x: value > x),
                    ("minLength", lambda x: len(value) >= x), ("minItems", lambda x: len(value) >= x)):
        if key in schema:
            require(ok(schema[key]), label + ": " + key)
    if kind == "object":
        require(not set(schema.get("required", [])) - set(value), label + ": missing fields")
        props = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            require(not set(value) - set(props), label + ": unknown fields")
        for key in value:
            if key in props:
                schema_check(value[key], props[key], label + "." + key)
    if kind == "array":
        for item in value:
            schema_check(item, schema["items"], label + "[]")


def read_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "duplicate JSON key")
            result[key] = value
        return result
    return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=unique,
                      parse_constant=lambda value: (_ for _ in ()).throw(GateError("non-finite JSON")))


def contract(task_root, allow, requirements_path):
    root = absolute(task_root)
    require(root.is_dir(), "task root must exist")
    req_path = absolute(requirements_path)
    require(req_path.is_relative_to(root) and req_path.is_file(), "requirements outside task or missing")
    req = read_json(req_path)
    require(isinstance(req, dict) and set(req) == {"schema_version", "task_id", "mode", "source",
            "report", "canary", "facts", "export", "asset_root", "max_report_age_seconds"}, "requirements schema")
    require(req["schema_version"] == SCHEMA_VERSION and req["mode"] == "rigid_static", "unsupported mode/schema")
    require(isinstance(req["task_id"], str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}", req["task_id"]), "task identity")
    require(isinstance(req["asset_root"], str) and req["asset_root"].strip(), "asset root required")
    age = req["max_report_age_seconds"]
    require(isinstance(age, (int, float)) and not isinstance(age, bool) and math.isfinite(age) and age > 0, "explicit report age required")
    paths = {key: absolute(req[key]) for key in ("source", "report", "canary", "facts", "export")}
    allowed = [absolute(p) for p in allow]
    outputs = [paths[key] for key in ("report", "canary", "facts", "export")]
    require(len(allowed) == len(set(allowed)) == len(outputs) and set(allowed) == set(outputs), "exact output allowlist required")
    all_paths = [req_path, *paths.values()]
    for index, path in enumerate(all_paths):
        require(path != root and path.is_relative_to(root), "path escapes task root")
        for other in all_paths[index + 1:]:
            require(path != other and path not in other.parents and other not in path.parents,
                    "ENG-PROTECTION-001: path role overlap")
    require(paths["source"].is_file() and paths["source"].suffix.lower() in {".blend", ".glb"}, "source missing/format")
    require(paths["canary"].suffix.lower() == paths["export"].suffix.lower() == ".glb", "GLB route only")
    require(paths["report"].suffix.lower() == paths["facts"].suffix.lower() == ".json", "JSON reports required")
    for path in outputs:
        require(path.parent.is_dir(), "output parent must already exist")
    return root, req_path, req, paths, outputs


def snapshot(root, req_path, req, paths, outputs, backend):
    tool = backend.identity()
    require(set(tool) == {"version", "build_hash", "executable", "executable_sha256", "background", "factory_startup"}, "tool identity schema")
    require(tool["version"] == "5.1.2" and tool["background"] is True and tool["factory_startup"] is True,
            "Blender 5.1.2 fresh background factory process required")
    require(digest(WRITER) == LEGACY_WRITER_SHA256, "legacy writer bytes changed")
    return {"task_id": req["task_id"], "task_root": str(root), "requirements_path": str(req_path),
            "requirements_sha256": digest(req_path), "source_path": str(paths["source"]),
            "source_sha256": digest(paths["source"]), "helper_sha256": digest(HERE),
            "writer_sha256": digest(WRITER), "schema_sha256": digest(SCHEMA),
            "tool": tool, "pid": os.getpid(), "process_nonce": PROCESS_NONCE,
            "allowlist": sorted(str(path) for path in outputs)}


def callability(backend, canary):
    """QA-TEST-001: attempts and dependent blockage are distinct facts."""
    facts = []
    for name in ("export", "import"):
        item = {"operator": name, "rna_registered": False, "poll": False,
                "call_attempted": False, "callability": "blocked", "detail": ""}
        facts.append(item)
        if name == "import" and facts[0]["callability"] != "condition_satisfied":
            item["detail"] = "dependency_export_failed"
            continue
        try:
            item["rna_registered"], item["poll"] = backend.probe(name)
            if not item["rna_registered"] or not item["poll"]:
                item["detail"] = "registration_or_poll_failed"
                continue
            item["call_attempted"] = True
            backend.canary(name, canary)
            item["callability"] = "condition_satisfied"
        except Exception as exc:
            item["callability"] = "condition_failed" if item["call_attempted"] else "blocked"
            item["detail"] = type(exc).__name__ + ": " + str(exc)
    return facts


def preflight(task_root, allow, requirements_path, backend):
    root, req_path, req, paths, outputs = contract(task_root, allow, requirements_path)
    require(all(not p.exists() for p in outputs), "existing output/partial retry refused")
    identity = snapshot(root, req_path, req, paths, outputs, backend)
    operators = callability(backend, paths["canary"])
    passed = all(item["callability"] == "condition_satisfied" for item in operators)
    report = {"schema_version": SCHEMA_VERSION, "identity": identity, "created_monotonic": time.monotonic(),
              "status": "pass" if passed else "fail", "exit_code": 0 if passed else 3,
              "operators": operators, "mode": "rigid_static", "production_write_performed": False,
              "canary_sha256": digest(paths["canary"]) if paths["canary"].is_file() else "",
              "runtime_verified": "not_verified", "device_or_player_verified": "not_verified",
              "performance_verified": "not_verified", "owner_decision": "not_decided"}
    schema_check(report, read_json(SCHEMA))
    # Recheck every path before the only evidence write. Never overwrite reports.
    contract(task_root, allow, requirements_path)
    require(snapshot(root, req_path, req, paths, outputs, backend) == identity, "identity drift during preflight")
    with paths["report"].open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    return report["exit_code"]


def consume(task_root, allow, requirements_path, backend, exit_code, writer):
    root, req_path, req, paths, outputs = contract(task_root, allow, requirements_path)
    require(type(exit_code) is int and exit_code == 0, "nonzero preflight result")
    report = read_json(paths["report"])
    schema_check(report, read_json(SCHEMA))
    require(report["status"] == "pass" and report["exit_code"] == 0, "failed preflight")
    require(report["identity"] == snapshot(root, req_path, req, paths, outputs, backend), "current identity mismatch")
    age = time.monotonic() - report["created_monotonic"]
    require(0 <= age <= req["max_report_age_seconds"], "stale preflight")
    require(len(report["operators"]) == 2 and [x["operator"] for x in report["operators"]] == ["export", "import"], "operator roster mismatch")
    require(all(x["rna_registered"] and x["poll"] and x["call_attempted"] and x["callability"] == "condition_satisfied" for x in report["operators"]), "incomplete canary")
    require(paths["canary"].is_file() and digest(paths["canary"]) == report["canary_sha256"], "canary identity mismatch")
    require(not paths["facts"].exists() and not paths["export"].exists(), "production target exists; use fresh revision")
    writer(req, paths, root)
    require(digest(paths["source"]) == report["identity"]["source_sha256"], "source changed during writer")
    require(paths["facts"].is_file() and paths["export"].is_file() and paths["export"].stat().st_size > 0, "writer incomplete")
    return {"status": "completed", "facts_sha256": digest(paths["facts"]), "export_sha256": digest(paths["export"])}


class BlenderBackend:
    def __init__(self):
        import bpy
        self.bpy = bpy

    def identity(self):
        app = self.bpy.app
        executable = absolute(app.binary_path)
        return {"version": ".".join(str(x) for x in app.version), "build_hash": app.build_hash.decode(),
                "executable": str(executable), "executable_sha256": digest(executable),
                "background": bool(app.background), "factory_startup": "--factory-startup" in sys.argv}

    def operator(self, name):
        return self.bpy.ops.export_scene.gltf if name == "export" else self.bpy.ops.import_scene.gltf

    def probe(self, name):
        op = self.operator(name)
        op.get_rna_type()
        return True, bool(op.poll())

    def canary(self, name, path):
        bpy = self.bpy
        if name == "export":
            require(not path.exists(), "canary exists")
            cube = bpy.data.objects.get("Cube")
            require(cube is not None and cube.type == "MESH", "factory Cube missing")
            bpy.ops.object.select_all(action="DESELECT")
            cube.select_set(True)
            bpy.context.view_layer.objects.active = cube
            result = self.operator(name)(filepath=str(path), export_format="GLB", use_selection=True,
                                         export_animations=False, export_cameras=False, export_lights=False)
            require("FINISHED" in result and path.is_file() and path.stat().st_size > 0, "canary export failed")
        else:
            bpy.ops.object.select_all(action="SELECT")
            bpy.ops.object.delete(use_global=False)
            require(len(bpy.context.scene.objects) == 0, "canary import scene not empty")
            result = self.operator(name)(filepath=str(path))
            require("FINISHED" in result and len(bpy.context.scene.objects) > 0, "canary import failed")


def legacy_writer(req, paths, root):
    spec = importlib.util.spec_from_file_location("agds_rigid_source", WRITER)
    module = importlib.util.module_from_spec(spec)
    previous = sys.argv
    previous_bytecode = sys.dont_write_bytecode
    try:
        # Blender may ignore PYTHONDONTWRITEBYTECODE. Keep tool files read-only.
        sys.dont_write_bytecode = True
        spec.loader.exec_module(module)
        sys.argv = [str(WRITER), "--", "--input", str(paths["source"]), "--output-root", str(root),
                    "--report", str(paths["facts"]), "--root", req["asset_root"], "--export", str(paths["export"])]
        module.main()
    finally:
        sys.argv = previous
        sys.dont_write_bytecode = previous_bytecode


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task-root", required=True)
    parser.add_argument("--allow", required=True, action="append")
    parser.add_argument("--requirements", required=True)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:])
    backend = BlenderBackend()
    exit_code = preflight(args.task_root, args.allow, args.requirements, backend)
    result = consume(args.task_root, args.allow, args.requirements, backend, exit_code, legacy_writer)
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"status": "refused_or_failed", "error": type(exc).__name__ + ": " + str(exc)}), file=sys.stderr)
        raise SystemExit(2)
