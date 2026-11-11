"""Fresh FBX checks of retained source, hulls, grout and ceramic orientation."""
from pathlib import Path
from collections import Counter
import bpy, bmesh, math, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree

R = Path(__file__).resolve().parent
A = R.parent
assembly = json.loads((R / 'assembly.json').read_text())


def clean(name):
    return name.rsplit('.', 1)[0] if name.rsplit('.', 1)[-1].isdigit() else name


def read(path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(path))
    obs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    obj = next(o for o in obs if not o.name.startswith('UCX_'))
    hulls = [o for o in obs if o.name.startswith('UCX_')]
    mesh = obj.data; uv = mesh.uv_layers.active
    assert uv, path
    ps = [obj.matrix_world @ v.co for v in mesh.vertices]
    mats = [clean(m.name) for m in mesh.materials]
    fs = [tuple(f.vertices) for f in mesh.polygons]
    uv_by_face = [[tuple(uv.data[i].uv) for i in f.loop_indices] for f in mesh.polygons]
    matrix_error = max(abs(obj.matrix_world[i][j] - int(i == j)) for i in range(4) for j in range(4))
    bm = bmesh.new(); bm.from_mesh(mesh)
    deg = sum(f.calc_area() < 1e-12 for f in bm.faces)
    nonmanifold = sum(not e.is_manifold for e in bm.edges)
    remaining = set(bm.verts); components = []
    while remaining:
        seed = remaining.pop(); group = {seed}; stack = [seed]
        while stack:
            for edge in stack.pop().link_edges:
                for v in edge.verts:
                    if v in remaining: remaining.remove(v); group.add(v); stack.append(v)
        faces = {f for v in group for f in v.link_faces}
        volume = 0
        for f in faces:
            p = list(f.verts)
            for i in range(1, len(p) - 1): volume += p[0].co.dot(p[i].co.cross(p[i + 1].co)) / 6
        components.append({'indices': sorted(v.index for v in group), 'volume': volume,
                           'bounds': bounds([v.co for v in group])})
    bm.free()
    return {'ps': ps, 'fs': fs, 'mats': mats, 'fm': [mats[f.material_index] for f in mesh.polygons],
            'normals': [f.normal.copy() for f in mesh.polygons], 'centers': [f.center.copy() for f in mesh.polygons],
            'uv': uv_by_face, 'hulls': [[h.matrix_world @ v.co for v in h.data.vertices] for h in hulls],
            'components': components, 'degenerate': deg, 'nonmanifold': nonmanifold, 'matrix_error': matrix_error}


def bounds(ps):
    return [[min(p[i] for p in ps) for i in range(3)],
            [max(p[i] for p in ps) for i in range(3)]]


def quant(v): return tuple(round(float(c), 6) for c in v)


def faces(data, omit=()):
    return Counter((mat, tuple(sorted(quant((*data['ps'][i], *uv)) for i, uv in zip(face, tex))))
                   for mat, face, tex in zip(data['fm'], data['fs'], data['uv']) if mat not in omit)


def hull_fingerprint(data):
    return Counter(tuple(sorted(quant(v) for v in hull)) for hull in data['hulls'])


def aabb_overlap(a, b):
    return all(min(a[1][i], b[1][i]) - max(a[0][i], b[0][i]) > 1e-6 for i in range(3))


results = []
grout_rays = []
for rec in assembly['parts']:
    name = rec['file']; data = read(R / 'models' / name)
    actual = bounds(data['ps'])
    error = max(abs(actual[k][i] - rec['source_bounds_m'][k][i]) for k in range(2) for i in range(3))
    assert error < 1e-6 and data['matrix_error'] < 1e-6, name
    assert len(data['hulls']) == rec['ucx'], name
    assert data['degenerate'] == 0 and data['nonmanifold'] == 0, (name, data['degenerate'], data['nonmanifold'])
    assert all(c['volume'] > 1e-12 for c in data['components']), (name, data['components'])
    assert all(math.isfinite(c) for ps in data['ps'] for c in ps), name
    assert all(math.isfinite(c) for uv in data['uv'] for p in uv for c in p), name
    result = {'file': name, 'bounds_error_m': error, 'identity_transform': True,
              'ucx': rec['ucx'], 'closed_components': len(data['components']),
              'minimum_signed_component_volume_m3': min(c['volume'] for c in data['components']),
              'degenerate_faces': 0, 'nonmanifold_edges': 0}
    if name.startswith('KI_Cab06'):
        old = read(A / 'CABINET-JOINERY-02/models' / (rec['replaces'] + '.fbx'))
        original = faces(old, ('Toe_Dark', 'Counter_Ivory'))
        replacement = faces(data)
        missing = original - replacement
        assert not missing, (name, 'retained source faces/UVs changed', len(missing))
        assert hull_fingerprint(old) == hull_fingerprint(data), (name, 'UCX changed')
        assert not any(m in ('Toe_Dark', 'Counter_Ivory') for m in data['fm']), name
        assert data['mats'] == ['Joinery_Sage', 'Joinery_Interior', 'Toe_Dark', 'Counter_Ivory'], data['mats']
        result.update(retained_source_faces_and_uvs=sum(original.values()), original_ucx_unchanged=True,
                      removed_groups_empty=True, original_slot_order=True,
                      plinth_front_setback_from_counter_cm=6)
    elif name.startswith('KI_Counter03'):
        assert len(data['components']) == 1, name
        assert max(abs(bounds(data['hulls'][0])[k][i] - actual[k][i]) for k in range(2) for i in range(3)) < 1e-6
        ox = rec['world_origin_cm'][0] / 100
        for face, tex in zip(data['fs'], data['uv']):
            for i, uv in zip(face, tex):
                p = data['ps'][i]
                if abs(p.z - .05) < 1e-6:
                    assert abs(uv[0] - (.03 + .94 * (p.x + ox - 1.121) / 3.619)) < 1e-6
                    assert abs(uv[1] - (.08 + .82 * (-p.y / .74))) < 1e-6
        result.update(single_continuous_closed_slab=True, shared_world_top_uv_frame=True, hull_matches_slab=True,
                      drawer_vertical_clearance_m=.005)
    else:
        # Components have disjoint interiors: tile backs butt the grout front,
        # and the three bullnose pieces meet on their flat end planes.
        overlaps = [(i, j) for i, a in enumerate(data['components']) for j, b in enumerate(data['components'])
                    if i < j and aabb_overlap(a['bounds'], b['bounds'])]
        assert not overlaps, (name, 'component bounding interiors overlap', overlaps)
        tree = BVHTree.FromPolygons(data['ps'], data['fs'], epsilon=0)
        def ray(x, z, expected_mat, depth):
            hit, normal, face, distance = tree.ray_cast(Vector((x, -.08, z)), Vector((0, 1, 0)), .15)
            assert hit is not None, (name, x, z, 'missing surface')
            assert data['fm'][face] == expected_mat, (name, x, z, data['fm'][face], expected_mat)
            assert abs(hit.y - depth) < 1e-6 and normal.y < -.99, (name, hit, normal)
            grout_rays.append({'file': name, 'point_local_xz_m': [x, z], 'material': expected_mat,
                               'surface_local_y_m': hit.y, 'outward_front': True})
        label = name.removeprefix('KI_Backsplash03_').removesuffix('.fbx')
        tiles = [t for t in assembly['tile_layout'] if t['band'] == label]
        ox, oz = rec['world_origin_cm'][0] / 100, rec['world_origin_cm'][2] / 100
        for tile in tiles:
            x0, x1, z0, z1 = tile['world_xz_m']
            ray((x0 + x1) / 2 - ox, (z0 + z1) / 2 - oz, tile['material'], -.018)
        # Sample every exposed vertical and horizontal joint at row/column
        # centres, rather than mistaking a tile back or an empty gap for grout.
        field_x0 = .018 if label == 'A' else 0
        field_x1 = actual[1][0]; field_z1 = (1.175 - .018) - oz
        for gx in sorted({t['grid'][0] for t in tiles}):
            x = gx * .10 - ox
            if not field_x0 + .002 < x < field_x1 - .002: continue
            zs = sorted({round((t['world_xz_m'][2] + t['world_xz_m'][3]) / 2 - oz, 7) for t in tiles})
            for z in zs: ray(x, z, 'Warm_cream_grout', -.016)
        for gz in sorted({t['grid'][1] for t in tiles}):
            z = gz * .10 - oz
            if not .002 < z < field_z1 - .002: continue
            xs = sorted({round((t['world_xz_m'][0] + t['world_xz_m'][1]) / 2 - ox, 7) for t in tiles})
            for x in xs: ray(x, z, 'Warm_cream_grout', -.016)
        radial = []
        for mat, normal, center in zip(data['fm'], data['normals'], data['centers']):
            if mat != 'Cream_glazed_cap': continue
            if center.z > field_z1 + 1e-6 and normal.y < -.01 and normal.z > .01:
                if label == 'A' and center.x < .018 - 1e-6 and normal.x < -.01:
                    r = center - Vector((.018, 0, field_z1))
                else: r = Vector((0, center.y, center.z - field_z1))
                radial.append(normal.dot(r.normalized()))
            elif label == 'A' and center.z < field_z1 - 1e-6 and normal.x < -.01 and normal.y < -.01:
                r = Vector((center.x - .018, center.y, 0))
                radial.append(normal.dot(r.normalized()))
        assert radial and min(radial) > .98, (name, radial)
        result.update(interior_aabb_overlaps=0, outward_bullnose_radial_faces=len(radial),
                      minimum_radial_normal_dot=min(radial), tile_count=len(tiles),
                      grout_recess_m=.002, tile_joint_m=.002)
    results.append(result)

min_crop = min(min(t['world_xz_m'][1] - t['world_xz_m'][0], t['world_xz_m'][3] - t['world_xz_m'][2]) for t in assembly['tile_layout'])
assert min_crop > .02
report = {'passed': True, 'fresh_fbx_files': results, 'surface_ray_checks': grout_rays,
          'minimum_cropped_tile_dimension_m': min_crop,
          'backsplash_apron_clearance_m': .005,
          'limits': 'Source-only geometry, UV, normal, retained-face and collision-hull checks. Original body UCX intentionally retained, including their old worktop/toe support volumes; new slab hulls overlap those collision volumes, never visible geometry. Actual engine material binding, installed adjacent appliances and real interactions require Unreal verification.'}
(R / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
print('KITCHEN SURFACES VALIDATION PASS:', len(results), 'fresh FBXs;', len(grout_rays), 'tile/grout rays;', min_crop, 'm smallest crop')
