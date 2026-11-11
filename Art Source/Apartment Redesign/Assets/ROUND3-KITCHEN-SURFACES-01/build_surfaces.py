"""Unified worktops, sound ceramic edge topology and recessed painted plinths.

All originals stay immutable. Existing carcass triangles and UCX are retained
apart from the two explicitly replaced render material groups.
"""
from pathlib import Path
import bpy, bmesh, math, json, shutil, hashlib
from mathutils import Vector

R = Path(__file__).resolve().parent
A = R.parent
for d in ('models', 'textures', 'previews'): (R / d).mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.context.scene.unit_settings.system = 'METRIC'
parts = []
review = []
tile_layout = []


def material(name, color, rough, source=None):
    m = bpy.data.materials.new(name); m.use_nodes = True
    m.diffuse_color = (*color, 1)
    p = m.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Roughness'].default_value = rough
    if source:
        dst = R / 'textures' / source.name
        if not dst.exists(): shutil.copyfile(source, dst)
        image = bpy.data.images.load(str(dst), check_existing=True); image.pack()
        node = m.node_tree.nodes.new('ShaderNodeTexImage'); node.image = image
        m.node_tree.links.new(node.outputs['Color'], p.inputs['Base Color'])
    return m


paint = material('Joinery_Sage', (.30, .36, .20), .78,
                 A / 'CABINET-JOINERY-02/textures/T_Joinery_Sage.png')
inside = material('Joinery_Interior', (.36, .26, .18), .80,
                  A / 'CABINET-JOINERY-02/textures/T_Joinery_Interior.png')
counter = material('Counter_Ivory', (.75, .70, .58), .48,
                   A / 'KI-CABINET-02/textures/ivory-enamel.png')
ivory = material('Warm_ivory_ceramic', (.70, .62, .47), .56,
                 A / 'KI-BACKSPLASH-02/textures/glaze-ivory.png')
sage = material('Soft_sage_ceramic', (.43, .49, .37), .59,
                A / 'KI-BACKSPLASH-02/textures/glaze-sage.png')
grout = material('Warm_cream_grout', (.76, .70, .59), .90)
capmat = material('Cream_glazed_cap', (.74, .68, .57), .56,
                  A / 'KI-BACKSPLASH-02/textures/glaze-ivory.png')
unused_toe = material('Toe_Dark', (.08, .07, .05), .90)  # empty compatibility slot only


def active(obj):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True); bpy.context.view_layer.objects.active = obj


def bounds(points):
    return [[min(v[i] for v in points) for i in range(3)],
            [max(v[i] for v in points) for i in range(3)]]


def mesh_object(name, vs, fs, mat):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vs, [], fs); mesh.update()
    bm = bmesh.new(); bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    assert bm.calc_volume(signed=True) > 0, name
    assert all(e.is_manifold for e in bm.edges), name
    bm.to_mesh(mesh); bm.free(); mesh.update()
    obj = bpy.data.objects.new(name, mesh); bpy.context.collection.objects.link(obj)
    mesh.materials.append(mat); mesh.uv_layers.new(name='UVMap')
    return obj


def box(name, lo, hi, mat, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,
        location=tuple((a + b) / 2 for a, b in zip(lo, hi)))
    obj = bpy.context.object; obj.name = name
    obj.dimensions = tuple(b - a for a, b in zip(lo, hi))
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod = obj.modifiers.new('Small eased edge', 'BEVEL')
        mod.width = bevel; mod.segments = 3
        bpy.ops.object.modifier_apply(modifier=mod.name)
        mod = obj.modifiers.new('Weighted corner normals', 'WEIGHTED_NORMAL')
        bpy.ops.object.modifier_apply(modifier=mod.name)
    obj.data.materials.append(mat)
    if not obj.data.uv_layers: obj.data.uv_layers.new(name='UVMap')
    return obj


def planar_uv(obj, origin=(0, 0, 0), mode='tile', cell=None):
    uv = obj.data.uv_layers.active
    for face in obj.data.polygons:
        axis = max(range(3), key=lambda i: abs(face.normal[i]))
        for li in face.loop_indices:
            v = obj.matrix_world @ obj.data.vertices[obj.data.loops[li].vertex_index].co
            if mode == 'counter':
                wx, wy, z = v.x + origin[0], -v.y + origin[1], v.z
                # One coordinate frame across all three slabs. Unfold the 5 cm
                # front/back edges from the top without separate strip resets.
                u = .03 + .94 * (wx - 1.121) / 3.619
                t = wy / .74
                vv = .08 + .82 * t
                if z < .05:
                    vv += (.05 - z) * (1.6 if t > .5 else -1.6)
                if axis == 0:
                    u += (.05 - z) * (.12 if face.normal.x > 0 else -.12)
                uv.data[li].uv = (u, vv)
            elif mode == 'plinth':
                uv.data[li].uv = (.08 + (v.x + .45) * .7,
                                      .12 + (v.z if axis != 2 else v.y + .30) * .8)
            elif cell:
                gx, gz, rotation = cell
                # Stable unique swatch offset; a cropped tile samples the same
                # region it would have used before the physical boundary cut.
                x = (v.x + origin[0]) / .10 - gx
                z = (v.z + origin[2]) / .10 - gz
                if rotation == 1: x, z = z, 1 - x
                elif rotation == 2: x, z = 1 - x, 1 - z
                elif rotation == 3: x, z = 1 - z, x
                ox = .08 + ((gx * 7 + gz * 3) % 5) * .08
                oz = .08 + ((gx * 3 + gz * 11) % 5) * .08
                uv.data[li].uv = (ox + .48 * x, oz + .48 * z)
            else:
                uv.data[li].uv = (v.x * .3 + .15, v.z * .8 + .15)


def join(parts_to_join, name):
    active(parts_to_join[0])
    for obj in parts_to_join: obj.select_set(True)
    if len(parts_to_join) > 1: bpy.ops.object.join()
    obj = bpy.context.object; obj.name = name
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return obj


def export(obj, name, origin_cm, hulls=(), role='', extras=None):
    active(obj)
    for i, hull in enumerate(hulls):
        hull.name = 'UCX_' + name + '_%02d' % i
        hull.select_set(True); hull.hide_render = True; hull.display_type = 'WIRE'
    obj.name = name
    assert Vector(obj.location).length < 1e-6
    assert Vector(obj.rotation_euler).length < 1e-6
    assert (obj.scale - Vector((1, 1, 1))).length < 1e-6
    bpy.ops.export_scene.fbx(filepath=str(R / 'models' / (name + '.fbx')),
        use_selection=True, object_types={'MESH'}, apply_unit_scale=True,
        add_leaf_bones=False, axis_forward='-Z', axis_up='Y', path_mode='RELATIVE')
    rec = {'file': name + '.fbx', 'role': role, 'world_origin_cm': list(origin_cm),
           'source_bounds_m': bounds([v.co for v in obj.data.vertices]),
           'slots': [m.name for m in obj.data.materials], 'ucx': len(hulls),
           'scale': [1, 1, 1], **(extras or {})}
    parts.append(rec)
    source_origin = Vector((origin_cm[0] / 100, -origin_cm[1] / 100, origin_cm[2] / 100))
    obj.location = source_origin
    for hull in hulls: hull.location += source_origin
    review.append(obj)
    return rec


# Keep every other source carcass polygon and original hull. Only the worktop
# and solid dark toe block render groups are replaced. Empty old slots stay in
# their previous order for binding compatibility.
for code, origin in [('0425', (141.25, 47.5, 0)), ('0775', (306.25, 47.5, 0)),
                     ('0450', (442.5, 47.5, 0))]:
    before = set(bpy.context.scene.objects)
    old_name = 'KI_Cab03_' + code + '_Body'
    bpy.ops.import_scene.fbx(filepath=str(A / 'CABINET-JOINERY-02/models' / (old_name + '.fbx')))
    imported = [o for o in set(bpy.context.scene.objects) - before if o.type == 'MESH']
    obj = next(o for o in imported if not o.name.startswith('UCX_'))
    hulls = [o for o in imported if o.name.startswith('UCX_')]
    slots = [m.name.removesuffix('.001').removesuffix('.002').removesuffix('.003') for m in obj.data.materials]
    assert slots == ['Joinery_Sage', 'Joinery_Interior', 'Toe_Dark', 'Counter_Ivory'], slots
    toe_index = slots.index('Toe_Dark'); counter_index = slots.index('Counter_Ivory')
    toe_vertices = {i for f in obj.data.polygons if f.material_index == toe_index for i in f.vertices}
    lo, hi = bounds([obj.data.vertices[i].co for i in toe_vertices])
    removed = {slot: sum(f.material_index == slots.index(slot) for f in obj.data.polygons)
               for slot in ('Toe_Dark', 'Counter_Ivory')}
    bm = bmesh.new(); bm.from_mesh(obj.data)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.material_index in (toe_index, counter_index)], context='FACES')
    bm.to_mesh(obj.data); bm.free(); obj.data.update()
    obj.data.materials[0] = paint; obj.data.materials[1] = inside
    obj.data.materials[2] = unused_toe; obj.data.materials[3] = counter
    # Recessed U-plinth: thin painted front and side returns, open back and
    # interior. The old footprint/front plane and load-bearing height remain.
    t = .018
    front = box('Recessed painted plinth front', lo, (hi[0], lo[1] + t, hi[2]), paint, .0012)
    left = box('Plinth left return', (lo[0], lo[1] + t, lo[2]), (lo[0] + t, hi[1], hi[2]), paint, .0012)
    right = box('Plinth right return', (hi[0] - t, lo[1] + t, lo[2]), hi, paint, .0012)
    for panel in (front, left, right): planar_uv(panel, mode='plinth')
    obj = join([obj, front, left, right], 'KI_Cab06_' + code + '_Body')
    export(obj, obj.name, origin, hulls, 'carcass without embedded counter or dark toe block',
           {'replaces': old_name, 'removed_render_face_counts': removed,
            'plinth_original_local_bounds_m': [lo, hi], 'original_ucx_preserved': True,
            'retained_slots': slots, 'plinth_panel_thickness_m': t})


# Three continuous 5 cm slabs replace all embedded worktops and five fillers.
for label, x0, x1 in [('A', 112.1, 162.5), ('B', 267.5, 345), ('C', 420, 474)]:
    w, depth = (x1 - x0) / 100, .74
    obj = box('One piece enamel slab', (0, -depth, 0), (w, 0, .05), counter, .0025)
    planar_uv(obj, (x0 / 100, 0, .86), 'counter')
    obj = join([obj], 'KI_Counter03_' + label)
    hull = box('Slab UCX', (0, -depth, 0), (w, 0, .05), counter)
    active(hull); bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    export(obj, obj.name, (x0, 6, 86), [hull], 'continuous counter slab',
           {'world_bounds_cm': [[x0, 6, 86], [x1, 80, 91]],
            'edge_bevel_m': .0025, 'uv_frame': 'one world-coordinate frame shared by A/B/C'})


def extrusion(name, profile, x0, x1, h0):
    # Clockwise YZ quarter-disk, explicitly reoriented by mesh_object.
    n = len(profile)
    vs = [(x, y, z + h0) for x in (x0, x1) for y, z in profile]
    fs = [tuple(reversed(range(n))), tuple(range(n, 2 * n))]
    fs += [(i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n)]
    obj = mesh_object(name, vs, fs, capmat)
    for f in obj.data.polygons: f.use_smooth = len(f.vertices) == 4 and abs(f.normal.y) > .01 and abs(f.normal.z) > .01
    planar_uv(obj)
    return obj


def vertical_cap(h, radius):
    # Left exposed edge turns from the tile face back to the wall.
    xy = [(radius, 0), (0, 0)] + [(radius - radius * math.cos(i * math.pi / 2 / 16),
                                  -radius * math.sin(i * math.pi / 2 / 16)) for i in range(1, 17)]
    n = len(xy); vs = [(x, y, z) for z in (0, h) for x, y in xy]
    fs = [tuple(reversed(range(n))), tuple(range(n, 2 * n))]
    fs += [(i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n)]
    obj = mesh_object('Fridge exposed end bullnose', vs, fs, capmat)
    for f in obj.data.polygons: f.use_smooth = len(f.vertices) == 4 and f.normal.x < -.01 and f.normal.y < -.01
    planar_uv(obj)
    return obj


def corner(radius, h0):
    # Closed spherical octant. It meets the top and vertical quarter-rounds
    # edge-for-edge, without two intersecting extrusions or coincident skins.
    n = 16; vs = []
    for j in range(n):
        theta = j * math.pi / 2 / n
        for i in range(n + 1):
            phi = i * math.pi / 2 / n
            vs.append((radius - radius * math.cos(theta) * math.cos(phi),
                       -radius * math.cos(theta) * math.sin(phi), h0 + radius * math.sin(theta)))
    pole = len(vs); vs.append((radius, 0, h0 + radius))
    center = len(vs); vs.append((radius, 0, h0))
    fs = []
    for j in range(n - 1):
        for i in range(n):
            k = j * (n + 1) + i
            fs.append((k, k + 1, k + n + 2, k + n + 1))
    for i in range(n): fs.append(((n - 1) * (n + 1) + i, (n - 1) * (n + 1) + i + 1, pole))
    fs.append(tuple([center] + list(range(n, -1, -1))))
    fs.append(tuple([center] + [j * (n + 1) for j in range(n)] + [pole]))
    fs.append(tuple([center] + [pole] + [j * (n + 1) + n for j in reversed(range(n))]))
    obj = mesh_object('Fridge top spherical corner', vs, fs, capmat)
    for f in obj.data.polygons: f.use_smooth = len(f.vertices) <= 4
    planar_uv(obj)
    return obj


radius = .018; joint = .002
profile = [(0, 0), (-radius, 0)] + [(-radius * math.cos(i * math.pi / 2 / 16),
                                                  radius * math.sin(i * math.pi / 2 / 16)) for i in range(1, 17)]
for label, start, end, bottom in [('A', 112.1, 162.5, 91), ('B', 267.5, 345, 91),
                                 ('Range', 345, 420, 107), ('C', 420, 474, 91)]:
    w = (end - start) / 100; h = (117.5 - bottom) / 100
    field_h = h - radius; field_x = radius if label == 'A' else 0
    substrate = box('Recessed grout substrate', (field_x, -.016, 0), (w, 0, field_h), grout)
    planar_uv(substrate)
    obs = [substrate]
    xstart, xend = start / 100 + field_x, end / 100
    zstart, zend = bottom / 100, 1.175 - radius
    for gx in range(math.floor(xstart / .1), math.ceil(xend / .1)):
        for gz in range(math.floor(zstart / .1), math.ceil(zend / .1)):
            x0 = max(xstart + joint / 2, gx * .1 + joint / 2)
            x1 = min(xend - joint / 2, (gx + 1) * .1 - joint / 2)
            z0 = max(zstart + joint / 2, gz * .1 + joint / 2)
            z1 = min(zend - joint / 2, (gz + 1) * .1 - joint / 2)
            assert min(x1 - x0, z1 - z0) > .02, (label, gx, gz, x1 - x0, z1 - z0)
            mat = ivory if (gx + gz) % 2 == 0 else sage
            tile = box('Cropped square ceramic', (x0 - start / 100, -.018, z0 - zstart),
                       (x1 - start / 100, -.016, z1 - zstart), mat, .00035)
            planar_uv(tile, (start / 100, 0, zstart), 'tile', (gx, gz, (gx * 3 + gz) % 4))
            obs.append(tile)
            tile_layout.append({'band': label, 'grid': [gx, gz], 'world_xz_m': [x0, x1, z0, z1],
                                'tile_depth_world_y_m': [.076, .078], 'grout_front_world_y_m': .076,
                                'material': mat.name})
    obs.append(extrusion('Top quarter round', profile, field_x, w, field_h))
    if label == 'A':
        obs.append(vertical_cap(field_h, radius)); obs.append(corner(radius, field_h))
    obj = join(obs, 'KI_Backsplash03_' + label)
    export(obj, obj.name, (start, 6, bottom), (), 'fitted backsplash with recessed grout',
           {'world_bounds_cm': [[start, 6, bottom], [end, 7.8, 117.5]],
            'joint_m': joint, 'grout_recess_m': .002, 'bullnose_radius_m': radius,
            'top_bullnose': True, 'fridge_end_bullnose': label == 'A',
            'other_end_trim': False})


assembly = {'units': 'metres; source front -Y, Unreal +Y; FBX forward -Z/up Y',
            'export': 'identity meshes; use world_origin_cm and yaw0, scale1; body origins unchanged',
            'parts': parts, 'tile_layout': tile_layout, 'global_tile_pitch_m': .1,
            'counter_top_cm': 91, 'counter_bottom_cm': 86,
            'backsplash_top_cm': 117.5, 'window_apron_bottom_cm': 118,
            'replace': 'Remove old embedded Counter_Ivory/Toe_Dark render groups via supplied carcasses, all five CounterFiller02 actors and all four Backsplash02 bands. Keep appliances and interactable roots unchanged.'}
(R / 'assembly.json').write_text(json.dumps(assembly, indent=2) + '\n')

# Source review scene with released cabinet fronts in their closed assembly pose.
for code, origin, front_files in [
    ('0425', (1.4125, -.475, 0), ['KI_Cab05_0425_door', 'KI_Cab05_0425_drawer']),
    ('0775', (3.0625, -.475, 0), ['KI_Cab05_0775_door_L', 'KI_Cab05_0775_door_R', 'KI_Cab05_0775_drawer_L', 'KI_Cab05_0775_drawer_R']),
    ('0450', (4.425, -.475, 0), ['KI_Cab05_0450_door', 'KI_Cab05_0450_drawer'])]:
    source_rec = json.loads((A / 'CABINET-JOINERY-04/assembly.json').read_text())['parts']
    for file in front_files:
        rec = next(r for r in source_rec if r['file'] == file + '.fbx')
        before = set(bpy.context.scene.objects)
        bpy.ops.import_scene.fbx(filepath=str(A / 'CABINET-JOINERY-04/models' / (file + '.fbx')))
        imported = [o for o in set(bpy.context.scene.objects) - before if o.type == 'MESH']
        for obj in imported:
            obj.location += Vector(origin) + Vector(rec['pivot_source_m'])
            if obj.name.startswith('UCX_'): obj.hide_render = True; obj.display_type = 'WIRE'
            else:
                for i, m in enumerate(obj.data.materials):
                    if m.name.startswith('Joinery_Sage'): obj.data.materials[i] = paint
                    elif m.name.startswith('Joinery_Interior'): obj.data.materials[i] = inside

scene = bpy.context.scene
scene.world = bpy.data.worlds.new('Neutral source review'); scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[0].default_value = (.19, .19, .19, 1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value = .50
scene.render.engine = 'CYCLES'; scene.cycles.samples = 16
scene.render.threads_mode = 'FIXED'; scene.render.threads = 2
scene.render.resolution_x = 1600; scene.render.resolution_y = 700
scene.render.resolution_percentage = 100; scene.render.image_settings.file_format = 'PNG'
bpy.ops.object.camera_add(location=(3.0, -4.5, 2.5)); camera = bpy.context.object
camera.rotation_euler = (Vector((2.93, -.35, .62)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'; camera.data.ortho_scale = 4.25; scene.camera = camera
for pos, energy in [((2, -3, 4), 400), ((5, -.5, 3), 250)]:
    bpy.ops.object.light_add(type='AREA', location=pos); obj = bpy.context.object
    obj.data.energy = energy; obj.data.size = 4
    obj.rotation_euler = (Vector((2.93, -.3, .8)) - obj.location).to_track_quat('-Z', 'Y').to_euler()
scene.render.filepath = str(R / 'previews/Complete-runs.png'); bpy.ops.render.render(write_still=True)
camera.location = (2.8, -1.2, 1.45)
camera.rotation_euler = (Vector((3.02, -.1, 1.04)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.ortho_scale = .95
scene.render.resolution_x = 1200; scene.render.resolution_y = 700
scene.render.filepath = str(R / 'previews/Tile-grout-and-slab.png'); bpy.ops.render.render(write_still=True)
camera.location = (1.23, -.65, 1.32)
camera.rotation_euler = (Vector((1.19, -.065, 1.10)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.ortho_scale = .40
scene.render.resolution_x = 800; scene.render.resolution_y = 800
scene.render.filepath = str(R / 'previews/Fridge-corner.png'); bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(R / 'models/KitchenSurfaces03.blend'))
(R / 'file-manifest.json').write_text(json.dumps({str(f.relative_to(R)): hashlib.sha256(f.read_bytes()).hexdigest()
    for d in ('models', 'textures') for f in sorted((R / d).iterdir()) if f.suffix in ('.fbx', '.png')}, indent=2) + '\n')
print('ROUND3 KITCHEN SURFACES BUILT:', len(parts), 'FBXs')
