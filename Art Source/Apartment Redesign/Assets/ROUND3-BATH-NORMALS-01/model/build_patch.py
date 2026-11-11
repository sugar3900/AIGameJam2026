"""Correct original bath roll winding, preserving all positions, UVs and slots.

Run in Blender 5.2: blender -b --threads 2 --python-exit-code 1 --python build_patch.py
The original BA-BASKET-01 and BA-ROLL-01 masters are immutable inputs.
"""
import bpy
import bmesh
import hashlib
import json
from collections import Counter
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT.parent
MODEL = ROOT / 'model'
PREVIEW = ROOT / 'previews'
PREVIEW.mkdir(exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
REPORT = {'inputs': {}, 'meshes': {}}


def corners(mesh):
    """Face-corner mapping ignores order while retaining UV/material association."""
    return Counter((tuple(round(float(x), 8) for x in mesh.vertices[loop.vertex_index].co),
                    tuple(round(float(x), 8) for x in mesh.uv_layers.active.data[loop.index].uv),
                    poly.material_index)
                   for poly in mesh.polygons for loop in (mesh.loops[i] for i in poly.loop_indices))


def signed_volume(mesh, ids):
    mesh.calc_loop_triangles()
    return sum(mesh.vertices[t.vertices[0]].co.dot(
        mesh.vertices[t.vertices[1]].co.cross(mesh.vertices[t.vertices[2]].co)) / 6
        for t in mesh.loop_triangles if t.polygon_index in ids)


def reverse(mesh, ids):
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.faces.ensure_lookup_table()
    bmesh.ops.reverse_faces(bm, faces=[bm.faces[i] for i in ids])
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


def radial(mesh, ids, axis, center):
    center = Vector(center)
    result = []
    for i in ids:
        p = mesh.polygons[i]
        r = p.center - center
        r[axis] = 0
        if r.length > 1e-8:
            result.append(p.normal.dot(r.normalized()))
    return {'min': min(result), 'max': max(result), 'count': len(result)}


def export(obj, filename):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.export_scene.fbx(filepath=str(MODEL / filename), use_selection=True,
        object_types={'MESH'}, apply_unit_scale=True, axis_forward='-Y', axis_up='Z',
        bake_space_transform=False, mesh_smooth_type='FACE', add_leaf_bones=False)


def preview(name):
    scene = bpy.context.scene
    old_engine = scene.render.engine
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.display.shading.light = 'STUDIO'
    scene.display.shading.color_type = 'MATERIAL'
    scene.display.shading.show_backface_culling = True
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    scene.render.resolution_x = scene.render.resolution_y = 1000
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = str(PREVIEW / (name + '.png'))
    bpy.ops.render.render(write_still=True)
    scene.render.engine = old_engine


def open_master(kit):
    source = ASSETS / kit / 'model' / (kit + '.blend')
    REPORT['inputs'][str(source.relative_to(ASSETS))] = hashlib.sha256(source.read_bytes()).hexdigest()
    bpy.ops.wm.open_mainfile(filepath=str(source))
    bpy.context.preferences.filepaths.save_version = 0


open_master('BA-BASKET-01')
preview('basket-before-backface-culling')
for idx, center in enumerate([(-.125, .005, .165), (0, .012, .173), (.123, .008, .165)]):
    obj = bpy.data.objects['Towel_' + str(idx)]
    mesh = obj.data
    before = corners(mesh)
    coords = [tuple(v.co) for v in mesh.vertices]
    transform = [list(row) for row in obj.matrix_world]
    slots = [m.name for m in mesh.materials]
    # First 240 quads and two 48-gon caps are the generated towel body.
    ids = set(range(242))
    assert all(len(mesh.polygons[i].vertices) == 4 for i in range(240))
    assert all(len(mesh.polygons[i].vertices) == 48 for i in (240, 241))
    old_volume = signed_volume(mesh, ids)
    old_radial = radial(mesh, range(240), 1, center)
    assert old_volume < 0 and old_radial['max'] < 0
    reverse(mesh, ids)
    volume = signed_volume(mesh, ids)
    side = radial(mesh, range(240), 1, center)
    assert volume > 0 and side['min'] > 0
    assert mesh.polygons[240].normal.y < -.99
    assert mesh.polygons[241].normal.y > .99
    assert corners(mesh) == before
    assert [tuple(v.co) for v in mesh.vertices] == coords
    assert [list(row) for row in obj.matrix_world] == transform
    assert [m.name for m in mesh.materials] == slots
    REPORT['meshes'][obj.name] = {'flipped_polygons': 242, 'volume_before_m3': old_volume,
        'volume_after_m3': volume, 'radial_before': old_radial, 'radial_after': side,
        'matrix_world': transform, 'materials': slots, 'vertices': len(mesh.vertices),
        'polygons': len(mesh.polygons), 'unchanged_positions_uv_materials': True}
    export(obj, 'BA_Towel_' + str(idx) + '.fbx')
preview('basket-after-backface-culling')
bpy.ops.file.make_paths_absolute()
bpy.ops.wm.save_as_mainfile(filepath=str(MODEL / 'BA-BASKET-ROUND3.blend'))
bpy.ops.file.make_paths_relative()
bpy.ops.wm.save_as_mainfile(filepath=str(MODEL / 'BA-BASKET-ROUND3.blend'))

open_master('BA-ROLL-01')
preview('paper-before-backface-culling')
obj = bpy.data.objects['Paper roll']
mesh = obj.data
before = corners(mesh)
coords = [tuple(v.co) for v in mesh.vertices]
transform = [list(row) for row in obj.matrix_world]
slots = [m.name for m in mesh.materials]
# The roll origin is at its axis. Body four surfaces interleaved per angular step.
body = set(range(256))
outer = list(range(0, 256, 4))
bore = list(range(1, 256, 4))
tail = list(range(256, 256 + 216))
old_volume = signed_volume(mesh, body)
old_outer = radial(mesh, outer, 0, (0, 0, 0))
old_bore = radial(mesh, bore, 0, (0, 0, 0))
assert old_volume < 0 and old_outer['max'] < 0 and old_bore['min'] > 0
assert all(mesh.polygons[i].normal.y > .9 for i in tail)
reverse(mesh, body | set(tail))
volume = signed_volume(mesh, body)
out = radial(mesh, outer, 0, (0, 0, 0))
inner = radial(mesh, bore, 0, (0, 0, 0))
assert volume > 0 and out['min'] > .99 and inner['max'] < -.99
assert all(mesh.polygons[i].normal.y < -.9 for i in tail)
assert all(mesh.polygons[i].normal.x < -.99 for i in range(2, 256, 4))
assert all(mesh.polygons[i].normal.x > .99 for i in range(3, 256, 4))
assert corners(mesh) == before
assert [tuple(v.co) for v in mesh.vertices] == coords
assert [list(row) for row in obj.matrix_world] == transform
assert [m.name for m in mesh.materials] == slots
REPORT['meshes'][obj.name] = {'flipped_polygons': 472, 'volume_before_m3': old_volume,
    'volume_after_m3': volume, 'outer_radial_before': old_outer, 'outer_radial_after': out,
    'bore_radial_before': old_bore, 'bore_radial_after': inner, 'tail_front_normal_y_max':
    max(mesh.polygons[i].normal.y for i in tail), 'matrix_world': transform,
    'materials': slots, 'vertices': len(mesh.vertices), 'polygons': len(mesh.polygons),
    'unchanged_positions_uv_materials': True}
export(obj, 'BA_Roll_Paper.fbx')
preview('paper-after-backface-culling')
bpy.ops.file.make_paths_absolute()
bpy.ops.wm.save_as_mainfile(filepath=str(MODEL / 'BA-ROLL-ROUND3.blend'))
bpy.ops.file.make_paths_relative()
bpy.ops.wm.save_as_mainfile(filepath=str(MODEL / 'BA-ROLL-ROUND3.blend'))
(MODEL / 'source-validation.json').write_text(json.dumps(REPORT, indent=2) + '\n')
print('ROUND3_SOURCE_PASS', json.dumps(REPORT['meshes']))
