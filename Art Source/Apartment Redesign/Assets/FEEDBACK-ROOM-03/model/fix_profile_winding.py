"""Repair released profile assets without rebuilding unrelated room furniture.

Run headless Blender with --python-exit-code 1. The primary builder also contains
the corrected winding. This migration is idempotent and verifies fresh FBXs.
"""
from pathlib import Path
import hashlib
import json
import bpy
import bmesh

P = Path(__file__).resolve().parent.parent
bpy.context.preferences.filepaths.save_version = 0
NAMES = ['Baseboard_' + k for k in
         ['1m', 'Inside_Start', 'Inside_End', 'Outside_Start', 'Outside_End']]
report = {}


def inspect(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    result = {'signed_volume_m3': bm.calc_volume(signed=True),
              'nonmanifold_edges': sum(not e.is_manifold for e in bm.edges)}
    bm.free()
    result['bounds'] = [[min(v.co[i] for v in obj.data.vertices) for i in range(3)],
                        [max(v.co[i] for v in obj.data.vertices) for i in range(3)]]
    # Position-keyed UV multiset detects changes despite reversed loop ordering.
    result['uv_by_position'] = sorted(tuple(round(float(x), 7) for x in
        (*obj.data.vertices[obj.data.loops[l.index].vertex_index].co,
         *obj.data.uv_layers.active.data[l.index].uv)) for l in obj.data.loops)
    result['material_slots'] = [m.name for m in obj.data.materials]
    return result


def repair_scene(blend, names):
    bpy.ops.wm.open_mainfile(filepath=str(P / 'model' / blend))
    for name in names:
        obj = bpy.data.objects[name]
        before = inspect(obj)
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        assert bm.calc_volume(signed=True) > 0, name
        bm.to_mesh(obj.data)
        bm.free()
        obj.data.update()
        after = inspect(obj)
        for key in ['bounds', 'uv_by_position', 'material_slots']:
            assert before[key] == after[key], (name, key)
        assert after['nonmanifold_edges'] == 0, name
        location = obj.location.copy()
        obj.location = (0, 0, 0)  # Saved baseboard scene uses display offsets.
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.export_scene.fbx(filepath=str(P / 'model' / (name + '.fbx')),
            use_selection=True, object_types={'MESH'}, apply_unit_scale=True,
            add_leaf_bones=False, axis_forward='-Y', axis_up='Z')
        obj.location = location
        report[name] = {'before_signed_volume_m3': before['signed_volume_m3'],
                        **{k: v for k, v in after.items() if k != 'uv_by_position'},
                        'bounds_uv_materials_unchanged': True}
    bpy.ops.wm.save_as_mainfile(filepath=str(P / 'model' / blend))


repair_scene('SlimBaseboards.blend', NAMES)
repair_scene('PinkBullnose.blend', ['BA_PinkBullnose_1m'])

for name in report:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(P / 'model' / (name + '.fbx')))
    obs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    assert len(obs) == 1, name
    obj = obs[0]
    actual = inspect(obj)
    assert actual['signed_volume_m3'] > 0, (name, actual)
    assert actual['nonmanifold_edges'] == 0, (name, actual)
    assert all(abs(a - b) < 1e-6 for aa, bb in
        zip(actual['bounds'], report[name]['bounds']) for a, b in zip(aa, bb)), name
    # Every baseboard front face must face the room (-Y); the wall back is +Y.
    if name.startswith('Baseboard_'):
        front = [f for f in obj.data.polygons if abs(f.center.y + .0107) < 1e-5
                 and .001 < f.center.z < .104 and f.area > .001]
        assert front and all(f.normal.y < -.99 for f in front), name
    else:
        curved = [f for f in obj.data.polygons if .001 < f.center.x < .0179
                  and -.0179 < f.center.y < -.001 and abs(f.normal.z) < .01]
        assert curved and all(f.normal.x > 0 and f.normal.y < 0 for f in curved), name
    report[name]['fresh_fbx_outward_normals'] = True

(P / 'profile-winding-validation.json').write_text(json.dumps(report, indent=2) + '\n')
(P / 'file-manifest.json').write_text(json.dumps({str(f.relative_to(P)):
    hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted((P / 'model').glob('*.fbx'))}, indent=2) + '\n')
print('PROFILE WINDING PASS:', len(report), 'fresh FBXs, manifold/outward; bounds, UVs and slots preserved')
