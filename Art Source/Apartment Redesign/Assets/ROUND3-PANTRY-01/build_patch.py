"""Narrow pantry correction: 4 mm meeting reveal and nonrepeating UV0.

Uses released CABINET-JOINERY-02 editable geometry. Only meeting stiles, their
knobs and horizontal spans change; both hinge origins and outer edges stay put.
"""
from pathlib import Path
import bpy, bmesh, math, json, hashlib, shutil
from mathutils import Vector

R = Path(__file__).resolve().parent
A = R.parent
for d in ('models', 'textures', 'previews'):
    (R / d).mkdir(exist_ok=True)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.open_mainfile(filepath=str(A / 'CABINET-JOINERY-02/models/Pantry.blend'))
src = A / 'CABINET-JOINERY-02/textures/T_Joinery_Sage.png'
shutil.copyfile(src, R / 'textures/T_Joinery_Sage.png')
paint_image = bpy.data.images.load(str(R / 'textures/T_Joinery_Sage.png'), check_existing=True)
paint_image.pack()
for m in bpy.data.materials:
    if m.use_nodes:
        for node in m.node_tree.nodes:
            if node.type == 'TEX_IMAGE' and node.image:
                if 'Joinery_Sage' in node.image.name:
                    node.image = paint_image
                else:
                    p = A / 'CABINET-JOINERY-02/textures' / Path(node.image.filepath).name
                    if p.exists():
                        node.image = bpy.data.images.load(str(p), check_existing=True)
                        node.image.pack()


def bounds(points):
    return [[min(v[i] for v in points) for i in range(3)],
            [max(v[i] for v in points) for i in range(3)]]


def islands(mesh):
    graph = [[] for v in mesh.vertices]
    for e in mesh.edges:
        a, b = e.vertices
        graph[a].append(b); graph[b].append(a)
    remaining = set(range(len(mesh.vertices)))
    while remaining:
        seed = remaining.pop(); group = {seed}; stack = [seed]
        while stack:
            for n in graph[stack.pop()]:
                if n in remaining:
                    remaining.remove(n); group.add(n); stack.append(n)
        yield group


parts = []
doors = []
for side, old, pivot in [('L', 'KI_Pantry02_LeftDoor', (-.470, -.318, 1.02)),
                         ('R', 'KI_Pantry02_RightDoor', (.470, -.318, 1.02))]:
    obj = bpy.data.objects[old]
    pv = Vector(pivot)
    assert (obj.location - pv).length < 1e-6
    assert Vector(obj.rotation_euler).length < 1e-6
    before = bounds([v.co + pv for v in obj.data.vertices])
    paint_index = next(i for i, m in enumerate(obj.data.materials) if m.name == 'Joinery_Sage')
    direction = 1 if side == 'L' else -1
    delta = .006 * direction
    component_for_vertex = {}
    component_meta = []
    for group in islands(obj.data):
        ps = [obj.data.vertices[i].co + pv for i in group]
        lo, hi = bounds(ps); width = hi[0] - lo[0]; height = hi[2] - lo[2]
        fs = [p for p in obj.data.polygons if p.vertices[0] in group]
        painted = all(f.material_index == paint_index for f in fs)
        label = 'hardware'
        if painted:
            if width > .20:
                label = 'rail' if height < .06 else 'field'
                # Keep hinge-side tongue fixed and extend only the latch side.
                anchor = lo[0] if side == 'L' else hi[0]
                for i in group:
                    x = obj.data.vertices[i].co.x + pv.x
                    f = abs(x - anchor) / width
                    obj.data.vertices[i].co.x += delta * f
            elif (lo[0] + hi[0]) * .5 * direction > -.235:
                label = 'meeting_stile'
                for i in group: obj.data.vertices[i].co.x += delta
            else:
                label = 'hinge_stile'
        elif (lo[0] + hi[0]) * .5 * direction > -.10:
            # Complete knob assembly moves with the meeting stile; hinge metal stays.
            for i in group: obj.data.vertices[i].co.x += delta
            label = 'knob'
        idx = len(component_meta)
        for i in group: component_for_vertex[i] = idx
        component_meta.append({'kind': label, 'vertices': len(group)})
    obj.data.update()
    # Paint fields and stiles share one full-height coordinate system, without
    # resetting at each field or crossing a wrap boundary. The right leaf uses a
    # distinct crop and reversed brush order. Rails rotate this grain mapping.
    uv = obj.data.uv_layers.active
    assert uv is not None
    u0, u1 = (.08, .28) if side == 'L' else (.64, .84)
    for f in obj.data.polygons:
        if f.material_index != paint_index: continue
        kind = component_meta[component_for_vertex[f.vertices[0]]]['kind']
        for li in f.loop_indices:
            v = obj.data.vertices[obj.data.loops[li].vertex_index].co + pv
            xnorm = (v.x + .462) / .460 if side == 'L' else (v.x - .002) / .460
            znorm = (v.z - .195) / 1.650
            if kind == 'rail':
                # Horizontal brushing on rails; each rail samples a different
                # band by its assembly height, with no field texture restart.
                u = (.32 if side == 'L' else .91) + .035 * znorm
                vtex = .06 + .28 * xnorm if side == 'L' else .92 - .28 * xnorm
            else:
                u = u0 + (u1 - u0) * xnorm
                vtex = .05 + .90 * znorm if side == 'L' else .95 - .90 * znorm
            # Thin edge and end faces need a depth coordinate: X/Z alone
            # collapses their UV area. Keep the full-height front crops intact.
            if abs(f.normal.x) > max(abs(f.normal.y), abs(f.normal.z)):
                u = u0 + .02 + .10 * (v.y + .36) / .10
                vtex = .05 + .90 * znorm if side == 'L' else .95 - .90 * znorm
            elif abs(f.normal.z) > abs(f.normal.y):
                u = u0 + (u1 - u0) * xnorm
                vtex = .35 + .10 * (v.y + .36) / .10
            uv.data[li].uv = (u, vtex)
    name = 'KI_Pantry03_' + ('LeftDoor' if side == 'L' else 'RightDoor')
    obj.name = name
    # Slab hull follows the widened visual leaf. Hinge hardware remains outside
    # this unchanged-depth hull, matching the prior interaction policy.
    bpy.ops.mesh.primitive_cube_add(size=1, location=(direction * -.232, -.329, 1.02))
    hull = bpy.context.object; hull.name = 'UCX_' + name + '_00'
    hull.dimensions = (.460, .022, 1.650)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for v in hull.data.vertices: v.co += hull.location - pv
    hull.location = (0, 0, 0); hull.hide_render = True; hull.display_type = 'WIRE'
    obj.location = (0, 0, 0)
    bpy.ops.object.select_all(action='DESELECT'); obj.select_set(True); hull.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.export_scene.fbx(filepath=str(R / 'models' / (name + '.fbx')),
        use_selection=True, object_types={'MESH'}, apply_unit_scale=True,
        add_leaf_bones=False, axis_forward='-Z', axis_up='Y', path_mode='RELATIVE')
    after = bounds([v.co + pv for v in obj.data.vertices])
    obj.location = pv
    hull.location = pv
    parts.append({'file': name + '.fbx', 'replaces': old + '.fbx',
                  'pivot_source_m': list(pivot), 'assembly_min': after[0],
                  'assembly_max': after[1], 'original_bounds': before,
                  'slots': [m.name for m in obj.data.materials], 'ucx': 1,
                  'engine_swing_sign': direction, 'source_swing_sign': -direction,
                  'max_angle_deg': 100, 'component_changes': component_meta,
                  'paint_uv_crop': [u0, u1, .05, .95]})
    doors.append(obj)

report = {'units': 'metres; -Y source front, exported -Z forward / Y up, matching Joinery02',
          'export': 'pivot-local vertices, identity transforms; retain installed hinge actor transforms',
          'centre_reveal_before_m': .016, 'centre_reveal_after_m': .004,
          'body': 'unchanged KI_Pantry02_Body', 'parts': parts,
          'materials': {'Joinery_Sage': {'texture': 'T_Joinery_Sage.png', 'roughness': .78, 'metallic': 0},
                        'Joinery_AgedBrass': 'retain installed MI_Joinery_AgedBrass',
                        'Joinery_KnobIvory': 'retain installed MI_Joinery_KnobIvory'}}
(R / 'assembly.json').write_text(json.dumps(report, indent=2) + '\n')

# Retain an editable assembled scene; collision hulls never render.
scene = bpy.context.scene
scene.render.engine = 'CYCLES'; scene.cycles.samples = 16
scene.render.threads_mode = 'FIXED'; scene.render.threads = 2
scene.render.resolution_x = 1000; scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
camera = scene.camera
camera.location = (1.7, -3.8, 2.1)
camera.rotation_euler = (Vector((0, -.1, 1.0)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.ortho_scale = 2.30
scene.render.filepath = str(R / 'previews/Pantry-closed.png')
bpy.ops.render.render(write_still=True)
for obj, sign in zip(doors, [-1, 1]): obj.rotation_euler.z = math.radians(sign * 100)
camera.data.ortho_scale = 2.70
scene.render.filepath = str(R / 'previews/Pantry-open.png')
bpy.ops.render.render(write_still=True)
for obj in doors: obj.rotation_euler.z = 0
camera.data.ortho_scale = 2.30
bpy.ops.wm.save_as_mainfile(filepath=str(R / 'models/Pantry03.blend'))
(R / 'file-manifest.json').write_text(json.dumps({str(f.relative_to(R)):
    hashlib.sha256(f.read_bytes()).hexdigest() for d in ('models', 'textures')
    for f in sorted((R / d).iterdir()) if f.suffix in ('.fbx', '.png')}, indent=2) + '\n')
print('ROUND3 PANTRY BUILT: 4 mm centre reveal, original hinge axes, full-height nonwrapping UV0')
