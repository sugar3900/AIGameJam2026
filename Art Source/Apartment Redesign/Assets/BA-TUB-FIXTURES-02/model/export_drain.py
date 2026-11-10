"""Add the omitted basin drain without rebuilding the released wall plumbing/rod."""
from pathlib import Path
import bpy
import json
import math

ROOT = Path(__file__).resolve().parent.parent
bpy.ops.wm.open_mainfile(filepath=str(ROOT.parent / 'BA-TUB-01/model/BA-TUB-01.blend'))
bpy.context.preferences.filepaths.save_version = 0
parts = [o for o in bpy.context.scene.objects if o.name.startswith(('Drain_rim', 'Drain_insert'))]
assert len(parts) == 2, [o.name for o in parts]
bpy.ops.object.select_all(action='DESELECT')
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
drain = bpy.context.object
drain.name = 'BA_TubFixture02_Drain'
bpy.context.scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

def bounds(obj):
    points = [obj.matrix_world @ v.co for v in obj.data.vertices]
    return [[min(p[i] for p in points) for i in range(3)],
            [max(p[i] for p in points) for i in range(3)]]

expected = bounds(drain)
materials = [m.name for m in drain.data.materials]
vertices = len(drain.data.vertices)
path = ROOT / 'model/BA_TubFixture02_Drain.fbx'
bpy.ops.export_scene.fbx(filepath=str(path), use_selection=True, object_types={'MESH'},
    axis_forward='-Y', axis_up='Z', apply_unit_scale=True, add_leaf_bones=False)
# Keep an editable, drain-only source. Original assembly coordinates are retained.
for obj in list(bpy.context.scene.objects):
    if obj != drain:
        bpy.data.objects.remove(obj, do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'model/BA-TUB-FIXTURES-02-drain.blend'))
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(path))
meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
assert len(meshes) == 1
obj = meshes[0]
actual = bounds(obj)
error = max(abs(a-b) for row_a, row_b in zip(expected, actual) for a, b in zip(row_a, row_b))
assert error < 1e-6, error
assert len(obj.data.vertices) == vertices
assert [m.name for m in obj.data.materials] == materials
assert obj.location.length < 1e-6
assert all(math.isfinite(c) for v in obj.data.vertices for c in v.co)
assert obj.data.uv_layers
assert all(math.isfinite(c) for uv in obj.data.uv_layers.active.data for c in uv.uv)
obj.data.calc_loop_triangles()
degenerate = sum(t.area < 1e-12 for t in obj.data.loop_triangles)
assert degenerate == 0, degenerate
result = {'status': 'PASS', 'export': str(path.relative_to(ROOT)),
    'bounds_m': {'min': actual[0], 'max': actual[1]}, 'vertices': vertices,
    'triangles': len(obj.data.loop_triangles), 'degenerate_triangles': degenerate,
    'materials': materials, 'max_bounds_error_m': error,
    'origin': [0, 0, 0], 'collision': 'none',
    'placement': 'Exact original tub/combined-fixture transform; never west-wall plumbing transform.'}
(ROOT / 'model/drain-validation.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))

assembly_path = ROOT / 'assembly.json'
assembly = json.loads(assembly_path.read_text())
assembly['exports'] = [e for e in assembly['exports'] if e['mesh'] != 'BA_TubFixture02_Drain']
assembly['exports'].append({'file': 'model/BA_TubFixture02_Drain.fbx', 'mesh': 'BA_TubFixture02_Drain', 'origin': [0,0,0], 'min': actual[0], 'max': actual[1], 'materials': materials})
assembly['drain_placement'] = result['placement']
assembly['curtain_placement'] = 'Reuse curtain source and Shower_Curtain identity; gather at east end, re-pose SLIDE endpoints and validate full travel against rod and linen cabinet.'
assembly_path.write_text(json.dumps(assembly, indent=2) + '\n')
