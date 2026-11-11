'''Create the original exercise geometry or export the current editable source.'''

import argparse
from pathlib import Path
import struct
import sys
import zlib
import bpy

ROOT = Path(__file__).resolve().parents[1]
PALETTE = [(146, 97, 62), (199, 143, 89), (75, 119, 119), (45, 73, 77)]
FACES = ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
         (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7))


def box(bounds):
    x0, x1, y0, y1, z0, z1 = bounds
    return [(x, y, z) for z in (z0, z1)
            for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]


def roof(side, width=1.50):
    inner = [(0, y, z) for z in (2.43, 2.50) for y in (-1.0, 1.0)]
    outer = [(side * width, y, z) for z in (2.01, 2.08) for y in (-1.0, 1.0)]
    v = [outer[0], inner[0], inner[1], outer[1], outer[2], inner[2], inner[3], outer[3]]
    return v if side < 0 else [v[i] for i in (1, 0, 3, 2, 5, 4, 7, 6)]


def mesh_object(collection, name, pieces, material):
    vertices, faces, colors = [], [], []
    for coords, color in pieces:
        start = len(vertices)
        vertices.extend((-x, -y, z) for x, y, z in coords)
        faces.extend(tuple(start + i for i in face) for face in FACES)
        colors.extend([color] * len(FACES))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    uv_layer = mesh.uv_layers.new(name="Palette")
    for face in mesh.polygons:
        u = (colors[face.index] + 0.5) / len(PALETTE)
        for i, loop_index in enumerate(face.loop_indices):
            uv_layer.data[loop_index].uv = (u + (i % 2 - 0.5) * 0.13, 0.23 + (i // 2) * 0.54)
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj.data.materials.append(material)
    return obj


def create_source(palette):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    material = bpy.data.materials.new("ShelterPalette")
    material.use_nodes = True
    image = material.node_tree.nodes.new("ShaderNodeTexImage")
    image.image = bpy.data.images.load(str(palette))
    image.image.pack()
    image.image.filepath = "//../UnityProject/Assets/FishingShelter/Models/ShelterPalette.png"
    material.node_tree.links.new(image.outputs["Color"], material.node_tree.nodes["Principled BSDF"].inputs["Base Color"])
    columns = [(box((x - 0.07, x + 0.07, y - 0.07, y + 0.07, 0.0, 2.07)), 0)
               for x in (-1.29, 1.29) for y in (-0.83, 0.83)]
    beams = [(box((-1.36, 1.36, y - 0.06, y + 0.06, 1.91, 2.05)), 0)
             for y in (-0.83, 0.83)]
    for level in (0, 1):
        collection = bpy.data.collections.new(f"LOD{level}")
        scene.collection.children.link(collection)
        mesh_object(collection, f"Frame_LOD{level}", columns + beams, material)
        if level == 0:
            boards = [(box((-1.32, 1.32, 0.84, 0.93, z, z + 0.143)), i % 2)
                      for i, z in enumerate(0.06 + 0.153 * k for k in range(12))]
            for x in (-1.30, 1.30):
                boards.extend((box((x - 0.05, x + 0.05, -0.81, 0.85, z, z + 0.13)), i % 2)
                              for i, z in enumerate(0.10 + 0.15 * k for k in range(6)))
        else:
            boards = [(box((-1.32, 1.32, 0.84, 0.93, 0.06, 1.90)), 1)]
            boards.extend((box((x - 0.05, x + 0.05, -0.81, 0.85, 0.10, 1.90)), 0)
                          for x in (-1.30, 1.30))
        mesh_object(collection, f"Cladding_LOD{level}", boards, material)
        mesh_object(collection, f"Roof_LOD{level}", [(roof(-1), 2), (roof(1), 2)], material)
        if level == 0:
            details = [(box((-1.49, 1.49, y - 0.012, y + 0.012, 2.015, 2.086)), 3)
                       for y in (-0.98, 0.98)]
            mesh_object(collection, "EaveTrim_LOD0", details, material)


def write_palette(path):
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
    size = 256
    rows = []
    for y in range(size):
        row = bytearray([0])
        for x in range(size):
            rgb = PALETTE[x // 64]
            grain = (x * 23 + y * 7 + ((y // 3) % 4) * 13) % 15 - 7
            row.extend(max(0, min(255, channel + grain)) for channel in rgb)
        rows.append(bytes(row))
    data = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0))
    path.write_bytes(data + chunk(b"IDAT", zlib.compress(b"".join(rows))) + chunk(b"IEND", b""))


def append_for_export(source):
    # The FBX writer records the current .blend pathname even without optional
    # metadata. Append the editable collections into an unsaved scratch scene.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    with bpy.data.libraries.load(str(source), link=False) as (available, exported):
        exported.collections = [name for name in ("LOD0", "LOD1") if name in available.collections]
    if len(exported.collections) != 2:
        raise ValueError("Both source LOD collections are required.")
    for collection in exported.collections:
        bpy.context.scene.collection.children.link(collection)
    bpy.context.scene.unit_settings.system = "METRIC"
    for material in bpy.data.materials:
        if material.node_tree:
            for node in material.node_tree.nodes:
                if node.type == "TEX_IMAGE":
                    node.image = None  # Unity's shared material binds the palette separately.


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--create", action="store_true")
    parser.add_argument("--verify-roof-extension", action="store_true")
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
    models = (ROOT / "UnityProject/Assets/FishingShelter/Models").resolve()
    source = (ROOT / "Blender/Shelter.blend").resolve()
    outputs = [models / f"Shelter_LOD{level}.fbx" for level in (0, 1)]
    palette = models / "ShelterPalette.png"
    for destination in (*outputs, source, palette):
        if not destination.is_relative_to(ROOT):
            raise ValueError(f"Destination outside exercise: {destination}")
    models.mkdir(parents=True, exist_ok=True)
    if args.create:
        if any(p.exists() for p in (source, palette, *outputs)):
            raise FileExistsError("Create requires new source, palette and exports.")
        write_palette(palette)
        create_source(palette)
        bpy.ops.wm.save_as_mainfile(filepath=str(source), relative_remap=False)
    elif Path(bpy.data.filepath).resolve() != source:
        raise ValueError("Open Blender/Shelter.blend before exporting.")
    append_for_export(source)
    if args.verify_roof_extension:
        for level in (0, 1):
            for vertex in bpy.data.objects[f"Roof_LOD{level}"].data.vertices:
                vertex.co.x *= 1.06
    for level, destination in enumerate(outputs):
        bpy.ops.object.select_all(action="DESELECT")
        objects = sorted(bpy.data.collections[f"LOD{level}"].objects, key=lambda obj: obj.name)
        for obj in objects:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = objects[0]
        triangles = 0
        for obj in objects:
            obj.data.calc_loop_triangles()
            triangles += len(obj.data.loop_triangles)
        if triangles > (1500, 600)[level]:
            raise ValueError(f"LOD{level} exceeds its triangle budget: {triangles}")
        bpy.ops.export_scene.fbx(filepath=str(destination), use_selection=True, object_types={"MESH"},
                                 use_triangles=True, axis_forward="-Z", axis_up="Y", bake_anim=False,
                                 path_mode="STRIP", use_metadata=False)
        print(f"SHELTER_LOD{level}_TRIANGLES={triangles}")


if __name__ == "__main__":
    main()
