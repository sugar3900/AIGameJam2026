"""Fresh FBX round trip; original comparison, closed-volume and radial tests."""
import bpy
import bmesh
import json
from collections import Counter
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT.parent
REPORT = {}


def extract(path, kind, center):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(path))
    objects = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    assert len(objects) == 1, (path, len(objects))
    obj = objects[0]
    me = obj.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.faces.ensure_lookup_table()
    bm.verts.ensure_lookup_table()
    left = set(bm.verts)
    islands = []
    while left:
        start = left.pop()
        group = {start}
        stack = [start]
        while stack:
            v = stack.pop()
            for e in v.link_edges:
                w = e.other_vert(v)
                if w in left:
                    left.remove(w)
                    stack.append(w)
                    group.add(w)
        faces = {f for v in group for f in v.link_faces}
        edges = {e for v in group for e in v.link_edges}
        islands.append((group, faces, all(e.is_manifold for e in edges)))
    nbody = 288 if kind == 'towel' else 256
    matches = [x for x in islands if len(x[0]) == nbody]
    assert len(matches) == 1, [(len(v), len(f), c) for v, f, c in islands]
    vertices, faces, closed = matches[0]
    assert closed
    me.calc_loop_triangles()
    face_ids = {f.index for f in faces}
    volume = sum(me.vertices[t.vertices[0]].co.dot(
        me.vertices[t.vertices[1]].co.cross(me.vertices[t.vertices[2]].co)) / 6
        for t in me.loop_triangles if t.polygon_index in face_ids)
    radial = []
    bore = []
    cap_signs = []
    center = Vector(center)
    axis = 1 if kind == 'towel' else 0
    for f in faces:
        coords = [v.co for v in f.verts]
        along = [v[axis] for v in coords]
        normal = f.normal
        if max(along) - min(along) < 1e-6:
            axiscenter = sum(along) / len(along)
            cap_signs.append(normal[axis] * (1 if axiscenter > center[axis] else -1))
            continue
        r = f.calc_center_median() - center
        r[axis] = 0
        dot = normal.dot(r.normalized())
        if kind == 'paper' and r.length < .03:
            bore.append(dot)
        else:
            radial.append(dot)
    corners = Counter((tuple(round(float(x), 6) for x in me.vertices[loop.vertex_index].co),
        tuple(round(float(x), 6) for x in me.uv_layers.active.data[loop.index].uv),
        p.material_index) for p in me.polygons for loop in (me.loops[i] for i in p.loop_indices))
    # Original/patched exports must retain every corner's UV/material assignment.
    serial = {'vertices': len(me.vertices), 'polygons': len(me.polygons),
        'triangles': len(me.loop_triangles), 'body_closed': closed, 'body_volume_m3': volume,
        'outward_radial_min': min(radial), 'outward_radial_max': max(radial),
        'cap_outward_min': min(cap_signs), 'materials': [m.name for m in me.materials],
        'matrix_world': [list(row) for row in obj.matrix_world],
        'bounds_local': [[min(v.co[i] for v in me.vertices), max(v.co[i] for v in me.vertices)] for i in range(3)]}
    if bore:
        serial['bore_radial_min'] = min(bore)
        serial['bore_radial_max'] = max(bore)
    if kind == 'paper':
        tailmatch = [x for x in islands if len(x[0]) == 247]
        assert len(tailmatch) == 1
        serial['tail_normal_y_max'] = max(f.normal.y for f in tailmatch[0][1])
        serial['tail_normal_y_min'] = min(f.normal.y for f in tailmatch[0][1])
    bm.free()
    return serial, corners


cases = [(f'BA_Towel_{i}.fbx', 'BA-BASKET-01', 'towel', c) for i,c in
    enumerate([(-.125,.005,.165), (0,.012,.173), (.123,.008,.165)])]
cases.append(('BA_Roll_Paper.fbx', 'BA-ROLL-01', 'paper', (0,0,0)))
for filename, kit, kind, center in cases:
    original, original_corners = extract(ASSETS / kit / 'model' / filename, kind, center)
    fixed, fixed_corners = extract(ROOT / 'model' / filename, kind, center)
    assert original_corners == fixed_corners, filename + ': corner mapping changed'
    for key in ('vertices', 'polygons', 'triangles', 'materials', 'matrix_world', 'bounds_local'):
        assert original[key] == fixed[key], (filename, key, original[key], fixed[key])
    assert original['body_volume_m3'] < 0 < fixed['body_volume_m3']
    assert original['outward_radial_max'] < 0 < fixed['outward_radial_min']
    assert fixed['cap_outward_min'] > .99
    if kind == 'paper':
        assert fixed['bore_radial_max'] < -.99
        assert fixed['tail_normal_y_max'] < -.9
    REPORT[filename] = {'before': original, 'after': fixed,
        'unchanged_positions_uv_materials_topology_transform': True, 'status': 'PASS'}
(ROOT / 'model' / 'fbx-validation.json').write_text(json.dumps(REPORT, indent=2) + '\n')
print('ROUND3_FBX_PASS', json.dumps(REPORT))
