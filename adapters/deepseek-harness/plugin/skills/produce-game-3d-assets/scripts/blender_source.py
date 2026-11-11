"""Blender-only source facts and explicitly selected static GLB export.
Run with --background --factory-startup --python-exit-code 1 --python ... --
--input SOURCE --output-root ABS_ROOT --report ABS_NEW_JSON [--root OBJECT --export NEW_GLB].
Does not judge dimensions, thickness, style, rights, or engine readiness.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path
import bpy


def sha256(path):
    with open(path, 'rb') as stream:
        h = hashlib.file_digest(stream, 'sha256')
    return h.hexdigest()


def object_facts(obj, depsgraph):
    result = {'type': obj.type, 'parent': obj.parent.name if obj.parent else None,
              'matrix_local': [list(row) for row in obj.matrix_local],
              'matrix_world': [list(row) for row in obj.matrix_world],
              'rotation_mode': obj.rotation_mode,
              'local_quaternion_wxyz': list(obj.matrix_local.to_quaternion()),
              'world_quaternion_wxyz': list(obj.matrix_world.to_quaternion()),
              'scale': list(obj.scale)}
    if obj.type == 'MESH':
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        try:
            coords = [list(evaluated.matrix_world @ v.co) for v in mesh.vertices]
            result['evaluated_world_bounds'] = {
                'min': [min(v[i] for v in coords) for i in range(3)],
                'max': [max(v[i] for v in coords) for i in range(3)],
                'dimensions': [max(v[i] for v in coords)-min(v[i] for v in coords) for i in range(3)]
            } if coords else None
            bounds = result['evaluated_world_bounds']
            result['evaluated_bounds_meters'] = {key: [x * bpy.context.scene.unit_settings.scale_length for x in values] for key, values in bounds.items()} if bounds else None
            mesh.calc_loop_triangles()
            result['evaluated_counts'] = {'vertices': len(mesh.vertices), 'polygons': len(mesh.polygons), 'triangles': len(mesh.loop_triangles)}
            raw = {'vertices': [list(v.co) for v in obj.data.vertices], 'faces': [list(p.vertices) for p in obj.data.polygons]}
            result['source_geometry_sha256'] = hashlib.sha256(json.dumps(raw, sort_keys=True).encode()).hexdigest()
            result['materials'] = [m.name if m else None for m in obj.data.materials]
        finally:
            evaluated.to_mesh_clear()
    if obj.type == 'CAMERA':
        result['camera'] = {'type': obj.data.type, 'ortho_scale': obj.data.ortho_scale, 'lens': obj.data.lens}
    if obj.type == 'LIGHT':
        result['light'] = {'type': obj.data.type, 'energy': obj.data.energy, 'color': list(obj.data.color), 'size': getattr(obj.data, 'size', None)}
    return result


def inspect_scene():
    bpy.context.view_layer.update()
    scene = bpy.context.scene
    mats = {}
    for mat in bpy.data.materials:
        nodes = []
        if mat.use_nodes:
            for node in mat.node_tree.nodes:
                record = {'type': node.type, 'name': node.name}
                if node.type == 'BSDF_PRINCIPLED':
                    for name in ('Base Color', 'Roughness', 'Metallic', 'Alpha', 'Transmission Weight'):
                        value = node.inputs[name].default_value
                        record[name] = list(value) if name == 'Base Color' else value
                nodes.append(record)
        mats[mat.name] = {'nodes': nodes, 'links': [(x.from_node.name, x.from_socket.name, x.to_node.name, x.to_socket.name) for x in mat.node_tree.links] if mat.use_nodes else []}
    return {'blender': bpy.app.version_string,
            'objects': {o.name: object_facts(o, bpy.context.evaluated_depsgraph_get()) for o in sorted(scene.objects, key=lambda o: o.name)},
            'materials': mats,
            'scene': {'units': scene.unit_settings.system, 'scale_length': scene.unit_settings.scale_length,
                      'camera': scene.camera.name if scene.camera else None, 'render_engine': scene.render.engine,
                      'resolution': [scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage],
                      'view_transform': scene.view_settings.view_transform, 'look': scene.view_settings.look,
                      'exposure': scene.view_settings.exposure, 'gamma': scene.view_settings.gamma,
                      'transparent': scene.render.film_transparent}}


def export_hierarchy(root_name, path):
    root = bpy.context.scene.objects.get(root_name)
    if root is None:
        raise ValueError('Selected asset root does not exist: ' + root_name)
    selected = [root] + list(root.children_recursive)
    if any(o.type not in {'MESH', 'EMPTY'} for o in selected):
        raise ValueError('Static export requires only MESH/EMPTY in selected hierarchy')
    bpy.ops.object.select_all(action='DESELECT')
    for obj in selected:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = root
    bpy.ops.export_scene.gltf(filepath=str(path), export_format='GLB', use_selection=True, export_animations=False, export_cameras=False, export_lights=False)
    return sorted(o.name for o in selected)


def validate_output_paths(output_root, paths):
    """Preflight explicit absolute outputs before any DCC file-writing operation."""
    output_root = Path(output_root)
    paths = [Path(path) for path in paths if path is not None]
    if not output_root.is_absolute() or any(not path.is_absolute() for path in paths):
        raise ValueError('Output root and all outputs must be absolute paths')
    root = output_root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError('Output root must be an existing approved directory')
    resolved = [path.resolve() for path in paths]
    if len(set(resolved)) != len(resolved):
        raise ValueError('Output paths must differ')
    for path in resolved:
        if not path.is_relative_to(root) or path == root:
            raise ValueError('Output is outside the approved output root: ' + str(path))
        if path.exists():
            raise ValueError('Output must be a new path: ' + str(path))
    return resolved

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--report', required=True, type=Path)
    parser.add_argument('--output-root', required=True, type=Path)
    parser.add_argument('--root')
    parser.add_argument('--export', type=Path)
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    source = args.input.resolve(strict=True)
    validated = validate_output_paths(args.output_root, [args.report, args.export])
    args.report = validated[0]
    args.export = validated[1] if args.export else None
    if source in validated:
        raise ValueError('Input cannot be an output')
    if args.export and (not args.root or args.export.suffix.lower() != '.glb'):
        raise ValueError('Export needs an explicit root and .glb output')
    before = sha256(source)
    preimport = None
    if source.suffix.lower() == '.blend':
        bpy.ops.wm.open_mainfile(filepath=str(source))
    elif source.suffix.lower() == '.glb':
        preimport = sorted(o.name for o in bpy.context.scene.objects)
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)
        if len(bpy.context.scene.objects):
            raise RuntimeError('Import scene was not empty')
        bpy.ops.import_scene.gltf(filepath=str(source))
    else:
        raise ValueError('Supported inputs: .blend, .glb')
    report = inspect_scene()
    report.update({'input': str(source), 'input_sha256': before, 'preimport_removed_objects': preimport})
    if args.export:
        args.export.parent.mkdir(parents=True, exist_ok=True)
        report['exported_objects'] = export_hierarchy(args.root, args.export)
        report['export_sha256'] = sha256(args.export)
    if sha256(source) != before:
        raise RuntimeError('Input bytes changed')
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print('SOURCE_FACTS_COMPLETE', str(args.report))


if __name__ == '__main__':
    main()
