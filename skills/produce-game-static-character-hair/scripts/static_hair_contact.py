"""Small Blender helper for static coarse hair-root contact work.

The curve route handles one editable non-cyclic POLY or BEZIER curve.  The
mesh route changes only caller-declared vertices by explicit ray projection.
No product object names, dimensions, thresholds, or repair targets are embedded.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any


class Unsupported(RuntimeError):
    pass


STATIC_NONDEFORMING_MODIFIERS = {
    "BEVEL", "BOOLEAN", "DECIMATE", "EDGE_SPLIT", "MIRROR", "NORMAL_EDIT",
    "SCREW", "SOLIDIFY", "SUBSURF", "TRIANGULATE", "WEIGHTED_NORMAL", "WELD",
}


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description="Inspect a coarse curve root or directionally project caller-declared static mesh vertices onto an evaluated scalp.")
    value.add_argument("--self-test", action="store_true", help="Run finite frame-transport controls in Blender; no blend file is opened.")
    value.add_argument("--input", type=Path, help="Existing editable .blend input.")
    value.add_argument("--scalp", help="Mesh object name for the declared support surface (scalp or existing hair foundation).")
    value.add_argument("--strand", help="Curve or mesh hair object name.")
    value.add_argument("--mode", choices=("inspect", "contact-report", "project-root", "mesh-project"), help="Requested operation.")
    value.add_argument("--root-end", choices=("start", "end"), default="start", help="Which curve end is the root.")
    value.add_argument("--align-neighbor-tangent", action="store_true", help="For project-root only, move the adjacent curve point tangentially while preserving its root distance.")
    value.add_argument("--output", type=Path, help="New .blend output required by project-root.")
    value.add_argument("--report", type=Path, help="New JSON report path; existing files are never overwritten.")
    value.add_argument("--root-depth", type=float, help="Explicit non-negative scene-unit depth inward from the support surface; required by project-root.")
    value.add_argument("--vertex-indices", help="Comma-separated mesh vertex indices to change; required by mesh-project.")
    value.add_argument("--vertex-weights", help="Comma-separated per-vertex blend weights; required by mesh-project.")
    value.add_argument("--protected-indices", help="Comma-separated protected mesh indices, or 'none'; required by mesh-project.")
    value.add_argument("--ray-direction", help="Explicit global ray direction as x,y,z; required by mesh-project.")
    value.add_argument("--allowed-face-indices", help="Optional comma-separated evaluated scalp face indices that a ray hit must belong to.")
    value.add_argument("--surface-offset", type=float, help="Caller-selected signed offset from the ray hit surface; required by mesh-project.")
    return value


def runtime() -> None:
    global bpy, Vector, BVHTree
    try:
        import bpy  # type: ignore
        from mathutils import Vector  # type: ignore
        from mathutils.bvhtree import BVHTree  # type: ignore
    except ImportError as exc:
        raise Unsupported("This helper must run through Blender Python.") from exc


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def unit(value):
    if value.length <= 1e-10:
        raise Unsupported("Degenerate vector prevents a coherent local frame.")
    return value.normalized()


def project_to_plane(value, tangent):
    return value - tangent * value.dot(tangent)


def fallback_normal(tangent):
    axes = (Vector((1.0, 0.0, 0.0)), Vector((0.0, 1.0, 0.0)), Vector((0.0, 0.0, 1.0)))
    return unit(min(axes, key=lambda axis: abs(axis.dot(tangent))).cross(tangent))


def rodrigues(value, axis, angle):
    return value * math.cos(angle) + axis.cross(value) * math.sin(angle) + axis * axis.dot(value) * (1.0 - math.cos(angle))


def transport_normal(previous_tangent, next_tangent, previous_normal):
    """Parallel-transport one normal with a deterministic antiparallel fallback."""
    previous_tangent = unit(previous_tangent)
    next_tangent = unit(next_tangent)
    dot = max(-1.0, min(1.0, previous_tangent.dot(next_tangent)))
    axis = previous_tangent.cross(next_tangent)
    if axis.length <= 1e-10:
        moved = rodrigues(previous_normal, fallback_normal(previous_tangent), math.pi) if dot < 0.0 else previous_normal.copy()
    else:
        moved = rodrigues(previous_normal, unit(axis), math.acos(dot))
    flattened = project_to_plane(moved, next_tangent)
    return fallback_normal(next_tangent) if flattened.length <= 1e-10 else unit(flattened)


def tangents(points):
    if len(points) < 2:
        raise Unsupported("A strand needs at least two editable points.")
    result = []
    for index in range(len(points)):
        direction = points[1] - points[0] if index == 0 else points[-1] - points[-2] if index == len(points) - 1 else points[index + 1] - points[index - 1]
        result.append(unit(direction))
    return result


def coherent_frames(points, seed_normal):
    local_tangents = tangents(points)
    first = project_to_plane(seed_normal, local_tangents[0])
    normal = fallback_normal(local_tangents[0]) if first.length <= 1e-10 else unit(first)
    frames = []
    for index, tangent in enumerate(local_tangents):
        if index:
            normal = transport_normal(local_tangents[index - 1], tangent, normal)
        binormal = unit(tangent.cross(normal))
        frames.append({"tangent": tangent, "normal": normal, "binormal": binormal})
    return frames


def named_object(name: str):
    obj = bpy.data.objects.get(name)
    if obj is None:
        raise Unsupported(f"Object is missing: {name}")
    return obj


def guard_static_object(obj, role: str):
    """Reject time-varying or deforming inputs before any source edit."""
    animation = obj.animation_data
    if animation and (animation.action or animation.drivers or animation.nla_tracks):
        raise Unsupported(f"{role} has animation data and is outside static repair.")
    shape_keys = getattr(obj.data, "shape_keys", None)
    if shape_keys and len(shape_keys.key_blocks) > 1:
        raise Unsupported(f"{role} has shape keys and is outside static repair.")
    for modifier in obj.modifiers:
        if modifier.type not in STATIC_NONDEFORMING_MODIFIERS:
            raise Unsupported(f"{role} modifier {modifier.type} is not an explicitly static nondeforming modifier.")


def guard_scene(scalp_name: str, strand_name: str):
    if any(obj.type == "ARMATURE" for obj in bpy.context.scene.objects):
        raise Unsupported("Armatures are outside static hair root repair.")
    scalp = named_object(scalp_name)
    strand = named_object(strand_name)
    if scalp.type != "MESH":
        raise Unsupported("The scalp input must be a mesh object.")
    if strand.type != "CURVE":
        raise Unsupported("Ring-mesh and non-curve strands are unsupported by this helper.")
    guard_static_object(scalp, "scalp")
    guard_static_object(strand, "curve hair")
    splines = list(strand.data.splines)
    if len(splines) != 1:
        raise Unsupported("Only one-spline coarse curves are supported.")
    spline = splines[0]
    if spline.use_cyclic_u or spline.type not in {"POLY", "BEZIER"}:
        raise Unsupported("Cyclic or non-POLY/non-BEZIER curves are unsupported.")
    count = len(spline.bezier_points) if spline.type == "BEZIER" else len(spline.points)
    if count < 2:
        raise Unsupported("A curve needs at least two points.")
    return scalp, strand, spline


def guard_mesh_scene(scalp_name: str, strand_name: str):
    if any(obj.type == "ARMATURE" for obj in bpy.context.scene.objects):
        raise Unsupported("Armatures are outside static hair root repair.")
    scalp = named_object(scalp_name)
    strand = named_object(strand_name)
    if scalp.type != "MESH":
        raise Unsupported("The scalp input must be a mesh object.")
    if strand.type != "MESH":
        raise Unsupported("mesh-project requires an editable mesh hair or inner-layer object.")
    guard_static_object(scalp, "scalp")
    guard_static_object(strand, "mesh hair")
    if not strand.data.vertices or not strand.data.polygons:
        raise Unsupported("The mesh hair input needs vertices and topology.")
    return scalp, strand


def curve_world_points(strand, spline):
    if spline.type == "BEZIER":
        return [strand.matrix_world @ point.co for point in spline.bezier_points]
    return [strand.matrix_world @ Vector(point.co[:3]) for point in spline.points]


def set_curve_world_point(strand, spline, index: int, world):
    local = strand.matrix_world.inverted() @ world
    if spline.type == "BEZIER":
        spline.bezier_points[index].co = local
    else:
        spline.points[index].co = (local.x, local.y, local.z, 1.0)


def curve_control_snapshot(spline):
    """Return editable controls exactly enough to expose automatic-handle side effects."""
    if spline.type == "BEZIER":
        return [
            {
                "index": index,
                "co": as_list(point.co),
                "handle_left": as_list(point.handle_left),
                "handle_right": as_list(point.handle_right),
                "handle_left_type": point.handle_left_type,
                "handle_right_type": point.handle_right_type,
            }
            for index, point in enumerate(spline.bezier_points)
        ]
    return [
        {"index": index, "co": as_list(point.co[:3]), "weight": float(point.co[3])}
        for index, point in enumerate(spline.points)
    ]


def changed_curve_controls(before, after):
    if len(before) != len(after):
        raise Unsupported("Curve control count changed during a declared local repair.")
    changed = []
    for old, new in zip(before, after):
        if old["index"] != new["index"]:
            raise Unsupported("Curve control ordering changed during a declared local repair.")
        fields = [field for field in old if field != "index" and old[field] != new[field]]
        if fields:
            changed.append({"index": old["index"], "changed_fields": fields})
    return changed


def require_root_depth(value):
    if value is None or not math.isfinite(value) or value < 0.0:
        raise Unsupported("project-root requires finite non-negative --root-depth in scene units.")
    return float(value)


def scalp_surface(scalp):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = scalp.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        vertices = [evaluated.matrix_world @ vertex.co for vertex in mesh.vertices]
        polygons = [tuple(polygon.vertices) for polygon in mesh.polygons]
        if not polygons:
            raise Unsupported("The evaluated scalp has no surface polygons.")
        return BVHTree.FromPolygons(vertices, polygons, all_triangles=False)
    finally:
        evaluated.to_mesh_clear()


def root_indices(point_count: int, root_end: str):
    return (0, 1) if root_end == "start" else (point_count - 1, point_count - 2)


def contact_data(scalp, strand, spline, root_end: str):
    points = curve_world_points(strand, spline)
    root_index, neighbor_index = root_indices(len(points), root_end)
    nearest = scalp_surface(scalp).find_nearest(points[root_index])
    if nearest is None:
        raise Unsupported("The evaluated scalp query returned no nearest surface point.")
    location, normal, face_index, distance = nearest
    normal = unit(normal)
    frames = coherent_frames(points, normal)
    return {
        "points": points,
        "root_index": root_index,
        "neighbor_index": neighbor_index,
        "surface_location": location,
        "surface_normal": normal,
        "surface_face_index": int(face_index),
        "distance": float(distance),
        "frames": frames,
    }


def as_list(vector):
    return [float(component) for component in vector]


def parse_indices(value: str | None, label: str, allow_none: bool = False):
    if value is None:
        raise Unsupported(f"{label} is required.")
    if allow_none and value.strip().lower() == "none":
        return []
    try:
        result = [int(part.strip()) for part in value.split(",") if part.strip()]
    except ValueError as exc:
        raise Unsupported(f"{label} must be comma-separated integers.") from exc
    if not result or len(result) != len(set(result)) or any(index < 0 for index in result):
        raise Unsupported(f"{label} must be non-empty, unique, and non-negative.")
    return result


def parse_weights(value: str | None, count: int):
    if value is None:
        raise Unsupported("--vertex-weights is required by mesh-project.")
    try:
        result = [float(part.strip()) for part in value.split(",") if part.strip()]
    except ValueError as exc:
        raise Unsupported("--vertex-weights must be comma-separated numbers.") from exc
    if len(result) != count or any(not math.isfinite(weight) or weight < 0.0 or weight > 1.0 for weight in result):
        raise Unsupported("--vertex-weights must match vertex indices and remain within 0..1.")
    return result


def parse_direction(value: str | None):
    if value is None:
        raise Unsupported("mesh-project requires explicit --ray-direction; nearest or radial fallback is forbidden.")
    try:
        direction = Vector(tuple(float(part.strip()) for part in value.split(",")))
    except ValueError as exc:
        raise Unsupported("--ray-direction must be x,y,z.") from exc
    if len(direction) != 3:
        raise Unsupported("--ray-direction must be x,y,z.")
    return unit(direction)


def mesh_snapshot(mesh_object):
    return {
        "vertex_count": len(mesh_object.data.vertices),
        "polygons": [tuple(polygon.vertices) for polygon in mesh_object.data.polygons],
        "world_vertices": [mesh_object.matrix_world @ vertex.co for vertex in mesh_object.data.vertices],
    }


def directional_hit(surface, origin, direction, allowed_faces):
    hit = surface.ray_cast(origin, direction)
    if hit is None or hit[0] is None:
        return {"status": "ray_miss", "origin": origin.copy(), "target": None}
    location, normal, face_index, _distance = hit
    if allowed_faces and int(face_index) not in allowed_faces:
        return {"status": "outside_allowed_region", "origin": origin.copy(), "target": None, "face_index": int(face_index)}
    return {"status": "hit", "origin": origin.copy(), "target": location, "normal": unit(normal), "face_index": int(face_index)}


def report_payload(input_path: Path, scalp, strand, spline, root_end: str, contact: dict[str, Any], mode: str):
    point_count = len(contact["points"])
    tip_index = point_count - 1 if contact["root_index"] == 0 else 0
    return {
        "schema_version": "static-character-hair-contact-report-v1",
        "status": "observed" if mode != "project-root" else "projected",
        "source_sha256": sha256(input_path),
        "scalp_object": scalp.name,
        "strand_object": strand.name,
        "strand_representation": spline.type,
        "root_end": root_end,
        "root_index": contact["root_index"],
        "tip_index": tip_index,
        "root_to_surface_distance": contact["distance"],
        "support_surface_role": "caller-declared; may be scalp or existing hair foundation",
        "surface_normal": as_list(contact["surface_normal"]),
        "frame_count": len(contact["frames"]),
        "frame_sign_policy": "parallel_transport_with_deterministic_antiparallel_fallback",
        "acceptance_threshold": "not_embedded; distance is diagnostic only",
        "cross_section_edit": "not_performed_by_curve_helper",
        "cap_visibility_guarantee": "not_guaranteed; inspect saved normal, neutral-gray, and elevated views",
        "runtime_verified": "not_verified",
        "device_or_player_verified": "not_verified",
    }


def mesh_project_payload(input_path: Path, scalp, strand, selected, protected, direction, offset, diagnostics, status):
    return {
        "schema_version": "static-character-hair-mesh-projection-report-v1",
        "status": status,
        "source_sha256": sha256(input_path),
        "scalp_object": scalp.name,
        "strand_object": strand.name,
        "strand_representation": "MESH",
        "selected_vertex_indices": selected,
        "protected_vertex_indices": protected,
        "ray_direction": as_list(direction),
        "surface_offset": offset,
        "projection_policy": "explicit_direction_only_no_nearest_or_radial_fallback",
        "diagnostics": diagnostics,
        "topology_preserved": "not_run" if status != "projected" else True,
        "unselected_vertices_preserved": "not_run" if status != "projected" else True,
        "runtime_verified": "not_verified",
        "device_or_player_verified": "not_verified",
    }


def project_mesh_vertices(args, scalp, strand):
    selected = parse_indices(args.vertex_indices, "--vertex-indices")
    protected = parse_indices(args.protected_indices, "--protected-indices", allow_none=True)
    weights = parse_weights(args.vertex_weights, len(selected))
    direction = parse_direction(args.ray_direction)
    if args.surface_offset is None or not math.isfinite(args.surface_offset):
        raise Unsupported("mesh-project requires finite caller-selected --surface-offset.")
    vertex_count = len(strand.data.vertices)
    if any(index >= vertex_count for index in selected + protected):
        raise Unsupported("Declared mesh index is outside the hair mesh.")
    if set(selected) & set(protected):
        raise Unsupported("Selected vertices cannot include declared protected tips or geometry.")
    allowed_faces = set(parse_indices(args.allowed_face_indices, "--allowed-face-indices", allow_none=True)) if args.allowed_face_indices else set()
    snapshot = mesh_snapshot(strand)
    surface = scalp_surface(scalp)
    diagnostics = []
    proposals = []
    for index, weight in zip(selected, weights):
        origin = snapshot["world_vertices"][index]
        hit = directional_hit(surface, origin, direction, allowed_faces)
        item = {"vertex_index": index, "weight": weight, "status": hit["status"], "origin_retained": hit["status"] != "hit"}
        if hit["status"] == "hit":
            target = hit["target"] + hit["normal"] * args.surface_offset
            item["face_index"] = hit["face_index"]
            proposals.append((index, origin.lerp(target, weight)))
        elif "face_index" in hit:
            item["face_index"] = hit["face_index"]
        diagnostics.append(item)
    if any(item["status"] != "hit" for item in diagnostics):
        return mesh_project_payload(args.input, scalp, strand, selected, protected, direction, args.surface_offset, diagnostics, "diagnostic_miss_no_output"), None
    for index, target in proposals:
        strand.data.vertices[index].co = strand.matrix_world.inverted() @ target
    return mesh_project_payload(args.input, scalp, strand, selected, protected, direction, args.surface_offset, diagnostics, "projected"), snapshot


def verify_mesh_reopen(output_path: Path, scalp_name: str, strand_name: str, before, selected):
    bpy.ops.wm.open_mainfile(filepath=str(output_path), load_ui=False)
    _scalp, strand = guard_mesh_scene(scalp_name, strand_name)
    after = mesh_snapshot(strand)
    if after["vertex_count"] != before["vertex_count"] or after["polygons"] != before["polygons"]:
        raise Unsupported("Mesh topology changed during a declared point-only projection.")
    selected_set = set(selected)
    unchanged = all(before_vertex == after_vertex for index, (before_vertex, after_vertex) in enumerate(zip(before["world_vertices"], after["world_vertices"])) if index not in selected_set)
    if not unchanged:
        raise Unsupported("A non-selected mesh vertex changed during point-only projection.")
    return True


def write_json_create_only(path: Path, payload: dict[str, Any]):
    if path.exists():
        raise Unsupported(f"Refusing to overwrite report: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(payload, stream, ensure_ascii=False, indent=2, sort_keys=True)
        stream.write("\n")


def validate_paths(args):
    if args.input is None or args.scalp is None or args.strand is None or args.mode is None:
        raise Unsupported("--input, --scalp, --strand, and --mode are required unless --self-test is used.")
    if not args.input.is_absolute():
        raise Unsupported("Input blend path must be absolute.")
    if not args.input.is_file():
        raise Unsupported(f"Input blend is missing: {args.input}")
    if args.report is not None:
        if not args.report.is_absolute() or args.report.exists() or args.report.resolve() == args.input.resolve():
            raise Unsupported("Report must be a new absolute path distinct from input.")
    if args.mode == "project-root":
        if args.output is None or args.report is None:
            raise Unsupported("project-root requires new --output and --report paths.")
        if not args.output.is_absolute() or args.output.resolve() == args.input.resolve() or args.output.exists():
            raise Unsupported("Output must be a new absolute path distinct from input.")
        if args.output.resolve() == args.report.resolve():
            raise Unsupported("Output and report must be different paths.")
        require_root_depth(args.root_depth)
    if args.mode == "mesh-project":
        if args.output is None or args.report is None:
            raise Unsupported("mesh-project requires new --output and --report paths.")
        if not args.output.is_absolute() or args.output.resolve() == args.input.resolve() or args.output.exists():
            raise Unsupported("mesh-project output must be a new absolute path distinct from input.")
        if args.output.resolve() == args.report.resolve():
            raise Unsupported("mesh-project output and report must be different paths.")


def self_test():
    x, y, z = Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))
    opposite = transport_normal(x, -x, y)
    if opposite.length <= 1e-8 or abs(opposite.dot(-x)) > 1e-7:
        raise AssertionError("antiparallel transport lost orthogonality")
    frames = coherent_frames([Vector((0, 0, 0)), Vector((1, 0, 0)), Vector((1, 1, 0)), Vector((1, 1, 1))], z)
    if len(frames) != 4 or any(abs(frame["tangent"].dot(frame["normal"])) > 1e-7 for frame in frames):
        raise AssertionError("coherent frame control failed")
    # The nearer plane is intentionally the wrong side.  Directional projection
    # must reach the declared front face instead of falling back to nearest/radial.
    vertices = [Vector((-1, -1, 0)), Vector((1, -1, 0)), Vector((1, 1, 0)), Vector((-1, 1, 0)), Vector((-1, -1, 1)), Vector((1, -1, 1)), Vector((1, 1, 1)), Vector((-1, 1, 1))]
    surface = BVHTree.FromPolygons(vertices, [(0, 1, 2, 3), (4, 5, 6, 7)], all_triangles=False)
    origin = Vector((0, 0, 0.2))
    nearest = surface.find_nearest(origin)
    front = directional_hit(surface, origin, Vector((0, 0, 1)), {1})
    miss = directional_hit(surface, origin, Vector((1, 0, 0)), {1})
    if nearest is None or int(nearest[2]) != 0 or front["status"] != "hit" or front["face_index"] != 1:
        raise AssertionError("front/back directional projection control failed")
    if miss["status"] != "ray_miss" or miss["target"] is not None:
        raise AssertionError("ray miss must not use a nearest fallback")
    for invalid_depth in (-0.01, float("nan"), float("inf")):
        try:
            require_root_depth(invalid_depth)
        except Unsupported:
            continue
        raise AssertionError("invalid root depth was accepted")
    # Evaluate a thick capped curve, not just its centerline: moving the root
    # center inward places the actual circular end cap below a planar support.
    cap_curve = bpy.data.curves.new("self_test_buried_cap_curve", "CURVE")
    cap_curve.dimensions = "3D"
    cap_curve.resolution_u = 1
    cap_curve.bevel_depth = 0.2
    cap_curve.resolution_u = 1
    cap_curve.resolution_v = 1
    cap_curve.bevel_resolution = 1
    cap_curve.use_fill_caps = True
    cap_spline = cap_curve.splines.new("POLY")
    cap_spline.points.add(1)
    cap_spline.points[0].co = (0.0, 0.0, -0.25, 1.0)
    cap_spline.points[1].co = (0.0, 0.0, 1.0, 1.0)
    cap_object = bpy.data.objects.new("self_test_buried_cap_object", cap_curve)
    bpy.context.collection.objects.link(cap_object)
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated_cap = cap_object.evaluated_get(depsgraph)
    cap_mesh = evaluated_cap.to_mesh()
    try:
        cap_min_z = min((evaluated_cap.matrix_world @ vertex.co).z for vertex in cap_mesh.vertices)
        if not cap_mesh.vertices or not cap_curve.use_fill_caps or cap_min_z >= 0.0:
            raise AssertionError("coarse curve cap was not buried below the support plane")
    finally:
        evaluated_cap.to_mesh_clear()
        bpy.data.objects.remove(cap_object, do_unlink=True)
        bpy.data.curves.remove(cap_curve)
    def rejected_before_edit(obj, label):
        try:
            guard_static_object(obj, label)
        except Unsupported:
            return
        raise AssertionError(f"{label} was not rejected before modification")
    shape_mesh = bpy.data.meshes.new("self_test_shape_mesh")
    shape_mesh.from_pydata([(0, 0, 0), (1, 0, 0), (0, 1, 0)], [], [(0, 1, 2)])
    shape_object = bpy.data.objects.new("self_test_shape_object", shape_mesh)
    bpy.context.collection.objects.link(shape_object)
    shape_object.shape_key_add(name="Basis")
    shape_object.shape_key_add(name="StaticTestKey")
    rejected_before_edit(shape_object, "shape-key target")
    bpy.data.objects.remove(shape_object, do_unlink=True)
    bpy.data.meshes.remove(shape_mesh)
    animated_mesh = bpy.data.meshes.new("self_test_animation_mesh")
    animated_mesh.from_pydata([(0, 0, 0), (1, 0, 0), (0, 1, 0)], [], [(0, 1, 2)])
    animated_object = bpy.data.objects.new("self_test_animation_object", animated_mesh)
    bpy.context.collection.objects.link(animated_object)
    animated_object.keyframe_insert(data_path="location", frame=1)
    rejected_before_edit(animated_object, "animated target")
    bpy.data.objects.remove(animated_object, do_unlink=True)
    bpy.data.meshes.remove(animated_mesh)
    return {"status": "passed", "controls": ["antiparallel_transport", "curved_frame_orthogonality", "explicit_front_surface_over_nearest_back_surface", "ray_miss_no_fallback", "root_depth_rejections", "coarse_curve_cap_buried", "shape_key_rejected_before_edit", "animated_target_rejected_before_edit"], "blend_opened": False}


def run(args):
    runtime()
    if args.self_test:
        if any(value is not None for value in (args.input, args.scalp, args.strand, args.mode, args.output, args.report)):
            raise Unsupported("--self-test does not accept task inputs or output paths.")
        return self_test()
    validate_paths(args)
    bpy.ops.wm.open_mainfile(filepath=str(args.input), load_ui=False)
    if args.mode == "mesh-project":
        scalp, strand = guard_mesh_scene(args.scalp, args.strand)
        payload, before = project_mesh_vertices(args, scalp, strand)
        if before is None:
            write_json_create_only(args.report, payload)
            return payload
        args.output.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(args.output), check_existing=False)
        payload["output_sha256"] = sha256(args.output)
        payload["reopen_verified"] = verify_mesh_reopen(args.output, args.scalp, args.strand, before, payload["selected_vertex_indices"])
        write_json_create_only(args.report, payload)
        return payload
    scalp, strand, spline = guard_scene(args.scalp, args.strand)
    contact = contact_data(scalp, strand, spline, args.root_end)
    payload = report_payload(args.input, scalp, strand, spline, args.root_end, contact, args.mode)
    if args.mode == "project-root":
        root_depth = require_root_depth(args.root_depth)
        controls_before = curve_control_snapshot(spline)
        tip_index = payload["tip_index"]
        tip_before = controls_before[tip_index]
        target_root = contact["surface_location"] - contact["surface_normal"] * root_depth
        set_curve_world_point(strand, spline, contact["root_index"], target_root)
        if args.align_neighbor_tangent:
            direction = contact["points"][contact["neighbor_index"]] - target_root
            tangent = project_to_plane(direction, contact["surface_normal"])
            if tangent.length <= 1e-10:
                raise Unsupported("Adjacent point cannot define a scalp-tangent direction.")
            set_curve_world_point(strand, spline, contact["neighbor_index"], target_root + unit(tangent) * direction.length)
        controls_before_save = curve_control_snapshot(spline)
        if controls_before_save[tip_index] != tip_before:
            raise Unsupported("Declared tip changed before save; refusing to hide an automatic handle side effect.")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(args.output), check_existing=False)
        payload["output_sha256"] = sha256(args.output)
        bpy.ops.wm.open_mainfile(filepath=str(args.output), load_ui=False)
        reopened_scalp, reopened_strand, reopened_spline = guard_scene(args.scalp, args.strand)
        controls_after_reopen = curve_control_snapshot(reopened_spline)
        if controls_after_reopen[tip_index] != tip_before:
            raise Unsupported("Declared tip changed after reopen; output cannot be claimed as protected.")
        reopened_contact = contact_data(reopened_scalp, reopened_strand, reopened_spline, args.root_end)
        payload["reopen_verified"] = True
        payload["root_to_surface_distance_after_reopen"] = reopened_contact["distance"]
        payload["root_projection"] = "performed"
        payload["neighbor_tangent_alignment"] = bool(args.align_neighbor_tangent)
        payload["root_depth_scene_units"] = root_depth
        payload["signed_depth_along_outward_support_normal"] = -root_depth
        payload["depth_sign_convention"] = "negative means inward from the evaluated support-surface outward normal"
        payload["support_surface_role"] = "caller-declared; may be scalp or existing hair foundation"
        payload["tip_protected_before_save"] = True
        payload["tip_protected_after_reopen"] = True
        payload["changed_curve_controls"] = changed_curve_controls(controls_before, controls_after_reopen)
        payload["cap_visibility_guarantee"] = "not_guaranteed; review saved normal, neutral-gray, and elevated views"
    if args.report is not None:
        write_json_create_only(args.report, payload)
    return payload


def main() -> int:
    import sys
    tool_args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    args = parser().parse_args(tool_args)
    try:
        result = run(args)
    except Unsupported as exc:
        print(json.dumps({"status": "unsupported", "reason": str(exc)}, ensure_ascii=False))
        return 3
    except Exception as exc:  # surface actual DCC failures without claiming a repair
        print(json.dumps({"status": "failed", "reason": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
