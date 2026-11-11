"""Fresh FBX fit, UV, hull and full-travel triangle checks for pantry release."""
from pathlib import Path
import bpy, bmesh, math, json
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

R = Path(__file__).resolve().parent
A = R.parent
assembly = json.loads((R / 'assembly.json').read_text())


def read(path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(path))
    objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    obj = next(o for o in objs if not o.name.startswith('UCX_'))
    hulls = [o for o in objs if o.name.startswith('UCX_')]
    ps = [obj.matrix_world @ v.co for v in obj.data.vertices]
    fs = [tuple(f.vertices) for f in obj.data.polygons]
    slots = [m.name for m in obj.data.materials]
    paint = slots.index('Joinery_Sage') if 'Joinery_Sage' in slots else None
    paint_faces = [f for f in obj.data.polygons if f.material_index == paint]
    painted = {i for f in paint_faces for i in f.vertices}
    uv = [tuple(obj.data.uv_layers.active.data[i].uv) for f in paint_faces for i in f.loop_indices]
    obj.data.calc_loop_triangles()
    collapsed_paint_uv = 0
    for tri in obj.data.loop_triangles:
        if obj.data.polygons[tri.polygon_index].material_index != paint: continue
        a,b,c = [obj.data.uv_layers.active.data[i].uv for i in tri.loops]
        collapsed_paint_uv += abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x)) < 1e-12
    bm = bmesh.new(); bm.from_mesh(obj.data)
    degenerate = sum(f.calc_area() < 1e-12 for f in bm.faces)
    nonmanifold = sum(not e.is_manifold for e in bm.edges)
    bm.free()
    return {'positions': ps, 'faces': fs, 'slots': slots, 'painted': painted,
            'uv': uv, 'hulls': [[h.matrix_world @ v.co for v in h.data.vertices] for h in hulls],
            'degenerate': degenerate, 'nonmanifold': nonmanifold, 'collapsed_paint_uv': collapsed_paint_uv,
            'identity_transform': all(abs(obj.matrix_world[i][j] - int(i == j)) < 1e-5
                                      for i in range(4) for j in range(4))}


def bounds(ps):
    return [[min(v[i] for v in ps) for i in range(3)],
            [max(v[i] for v in ps) for i in range(3)]]


def tree(ps, fs):
    return BVHTree.FromPolygons(ps, fs, epsilon=0)


meshes = []
files = []
old_leaf_bounds = []
new_leaf_bounds = []
for rec in assembly['parts']:
    old = read(A / 'CABINET-JOINERY-02/models' / rec['replaces'])
    new = read(R / 'models' / rec['file'])
    pv = Vector(rec['pivot_source_m'])
    old_b = bounds([old['positions'][i] + pv for i in old['painted']])
    new_b = bounds([new['positions'][i] + pv for i in new['painted']])
    old_leaf_bounds.append(old_b); new_leaf_bounds.append(new_b)
    whole = bounds([p + pv for p in new['positions']])
    errors = [abs(whole[k][i] - rec[['assembly_min', 'assembly_max'][k]][i])
              for k in range(2) for i in range(3)]
    assert max(errors) < 1e-6, rec['file']
    assert old['slots'] == new['slots'] == rec['slots'], rec['file']
    assert len(new['hulls']) == 1, rec['file']
    assert new['identity_transform'], rec['file']
    assert new['degenerate'] == 0 and new['nonmanifold'] == 0, rec['file']
    assert new['collapsed_paint_uv'] == 0, rec['file']
    assert all(math.isfinite(c) for p in new['positions'] for c in p), rec['file']
    assert all(0 <= c <= 1 for uv in new['uv'] for c in uv), rec['file']
    # UV0 has no repeated full-height cycles; each leaf uses less than one image.
    span = [max(uv[i] for uv in new['uv']) - min(uv[i] for uv in new['uv']) for i in range(2)]
    assert max(span) < 1 and span[1] > .89, (rec['file'], span)
    # Y/Z and the outward edge retain the original bounds; only centre edge moves.
    assert all(abs(old_b[k][i] - new_b[k][i]) < 1e-6 for k in range(2) for i in (1, 2))
    k = 0 if 'LeftDoor' in rec['file'] else 1
    assert abs(old_b[k][0] - new_b[k][0]) < 1e-6, rec['file']
    hb = bounds([p + pv for p in new['hulls'][0]])
    assert max(abs(hb[k][i] - new_b[k][i]) for k in range(2) for i in range(3)) < 1e-6
    files.append({'file': rec['file'], 'fresh_fbx': True, 'bounds_error_m': max(errors),
                  'ucx': 1, 'identity_transform': True, 'slots_unchanged': True,
                  'degenerate_faces': 0, 'nonmanifold_edges': 0, 'paint_uv_span': span,
                  'painted_leaf_assembly_bounds_m': new_b, 'hull_matches_leaf_bounds': True})
    meshes.append(new)

gap_before = old_leaf_bounds[1][0][0] - old_leaf_bounds[0][1][0]
gap_after = new_leaf_bounds[1][0][0] - new_leaf_bounds[0][1][0]
assert abs(gap_before - .016) < 1e-6
assert abs(gap_after - .004) < 1e-6
body = read(A / 'CABINET-JOINERY-02/models/KI_Pantry02_Body.fbx')
bt = tree(body['positions'], body['faces'])


def door_tree(index, degrees):
    rec = assembly['parts'][index]; mesh = meshes[index]
    rot = Matrix.Rotation(math.radians(degrees * rec['source_swing_sign']), 3, 'Z')
    return tree([rot @ p + Vector(rec['pivot_source_m']) for p in mesh['positions']], mesh['faces'])


hits = []
poses = []
for step in range(21):
    degrees = step * 5
    left, right = door_tree(0, degrees), door_tree(1, degrees)
    pairs = [('left_carcass', left, bt), ('right_carcass', right, bt),
             ('left_other_closed', left, door_tree(1, 0)),
             ('right_other_closed', right, door_tree(0, 0)), ('both_opening', left, right)]
    for name, a, b in pairs:
        contacts = len(a.overlap(b))
        if contacts: hits.append({'test': name, 'angle_deg': degrees, 'triangle_pairs': contacts})
    poses.append(degrees)
report = {'passed': not hits, 'closed_gap_before_m': gap_before,
          'closed_gap_after_m': gap_after, 'fresh_imports': files,
          'sweep_poses_deg': poses, 'sweep_comparisons': 105, 'sweep_contacts': hits,
          'limits': 'Triangle surface tests against source pantry carcass and opposite door, including each door alone and together. Installed neighbours, real clicks, hover and engine material appearance require Unreal checks.'}
(R / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
assert report['passed'], 'pantry sweep contacts'
