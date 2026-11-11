"""Round-three shelf pot repair; source metres, assembly origin 0, default FBX -Z/Y."""
import bpy, bmesh, math, json, hashlib
from pathlib import Path
from collections import Counter
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT.parent
MODEL, PREVIEW = ROOT / 'model', ROOT / 'previews'
PREVIEW.mkdir(exist_ok=True)
SOURCE = ASSETS / 'FEEDBACK-ROOM-03/model/BooksPlant03.blend'
REPORT = {'input': str(SOURCE.relative_to(ASSETS)), 'input_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest()}
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
bpy.context.preferences.filepaths.save_version = 0
foliage = [o for o in bpy.context.scene.objects if o.type == 'MESH' and o.name.startswith(('Plant03 branching petiole', 'Plant03 curved pointed leaf'))]
oldpots = [o for o in bpy.context.scene.objects if o.type == 'MESH' and o.name.startswith(('tapered ceramic pot', 'pot lip', 'soil', 'pot botanical'))]
assert len(foliage) == 38
assert len([o for o in oldpots if o.name.startswith('pot botanical')]) == 4
REPORT['removed_accents'] = [{'name': o.name, 'location': list(o.location), 'scale': list(o.scale)} for o in oldpots if o.name.startswith('pot botanical')]
for o in list(bpy.context.scene.objects):
    if o not in foliage + oldpots:
        bpy.data.objects.remove(o, do_unlink=True)


def leaf_signature(objects):
    result = Counter()
    for o in objects:
        uv = o.data.uv_layers.active
        for p in o.data.polygons:
            mat = o.data.materials[p.material_index].name
            for li in p.loop_indices:
                v = o.matrix_world @ o.data.vertices[o.data.loops[li].vertex_index].co
                tex = tuple(round(float(x), 6) for x in uv.data[li].uv) if uv else (0., 0.)
                result[(tuple(round(float(x), 6) for x in v), tex, mat)] += 1
    return result


original_foliage = leaf_signature(foliage)
REPORT['original_foliage_objects'] = len(foliage)
REPORT['original_foliage_corners'] = sum(original_foliage.values())
leaf, light, clay, soil = [bpy.data.materials[n] for n in ('Plant_Leaf', 'Plant_Leaf_Light', 'Ceramic_Pot', 'Pot_Soil')]
for m in (leaf, light): m.use_backface_culling = False
for m in (clay, soil): m.use_backface_culling = True
soil.use_nodes=True
soil.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.10,.07,.035,1)
soil.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.95


def render(name, close=False, workbench=False):
    sc = bpy.context.scene
    for o in list(sc.objects):
        if o.type in {'CAMERA','LIGHT'}: bpy.data.objects.remove(o, do_unlink=True)
    target = Vector((-.33, -.08, 1.59 if close else 1.685))
    loc = target + Vector((.43, -.69, .27 if close else .32))
    bpy.ops.object.camera_add(location=loc)
    cam = bpy.context.object
    cam.rotation_euler = (target-loc).to_track_quat('-Z','Y').to_euler()
    cam.data.type = 'ORTHO'; cam.data.ortho_scale = .285 if close else .65
    sc.camera = cam
    for offset, power, size in [((.4,-.6,.8),35,.7),((-.5,.1,.35),16,.6)]:
        pos = target + Vector(offset)
        bpy.ops.object.light_add(type='AREA', location=pos)
        o=bpy.context.object; o.data.energy=power; o.data.size=size
        o.rotation_euler=(target-pos).to_track_quat('-Z','Y').to_euler()
    sc.render.engine = 'BLENDER_WORKBENCH' if workbench else 'CYCLES'
    sc.cycles.samples = 24
    sc.render.threads_mode = 'FIXED'; sc.render.threads = 2
    sc.display.shading.light = 'STUDIO'; sc.display.shading.color_type='MATERIAL'
    sc.display.shading.show_backface_culling=True
    sc.display.shading.show_cavity=True
    sc.render.resolution_x=sc.render.resolution_y=1000
    sc.render.resolution_percentage=100; sc.render.film_transparent=True
    sc.render.image_settings.file_format='PNG'
    sc.render.filepath=str(PREVIEW/(name+'.png'))
    sc.world.use_nodes=True
    sc.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.25
    bpy.ops.render.render(write_still=True)


render('plant-before')
for o in oldpots: bpy.data.objects.remove(o, do_unlink=True)


def lathe(name, profile, material, n=96):
    # Standard CCW XY rings; profile ascends exterior and descends interior.
    vertices=[(-.33+r*math.cos(math.tau*i/n), -.08+r*math.sin(math.tau*i/n), z)
              for r,z in profile for i in range(n)]
    faces=[]
    for j in range(len(profile)-1):
        for i in range(n):
            k=(i+1)%n
            faces.append((j*n+i,j*n+k,(j+1)*n+k,(j+1)*n+i))
    faces.extend([tuple(reversed(range(n))),tuple((len(profile)-1)*n+i for i in range(n))])
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(vertices,[],faces);mesh.update()
    obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj)
    mesh.materials.append(material);uv=mesh.uv_layers.new(name='UVMap')
    distance=[0.]
    for (r0,z0),(r1,z1) in zip(profile,profile[1:]):
        distance.append(distance[-1]+math.hypot(r1-r0,z1-z0))
    for p in mesh.polygons:
        p.use_smooth=len(p.vertices)==4
        for li in p.loop_indices:
            vi=mesh.loops[li].vertex_index; row,i=divmod(vi,n)
            if len(p.vertices)==4:
                # Arc-length V keeps horizontal rim/foot bands from collapsing.
                u=i/n
                if (p.index%n)==n-1 and i==0:u=1
                uv.data[li].uv=(u,distance[row]/.18)
            else:
                v=mesh.vertices[vi].co
                uv.data[li].uv=((v.x+.33)/.22+.5,(v.y+.08)/.22+.5)
    bm=bmesh.new();bm.from_mesh(mesh)
    assert all(e.is_manifold for e in bm.edges)
    volume=bm.calc_volume(signed=True)
    assert volume>0,(name,volume)
    bm.free()
    REPORT[name]={'vertices':len(mesh.vertices),'polygons':len(mesh.polygons),
                  'closed_manifold':True,'signed_volume_m3':volume,
                  'radial_segments':n,'smooth_side_faces':sum(p.use_smooth for p in mesh.polygons)}
    return obj


pot=lathe('Plant04 closed terracotta vessel',[
    (.060,1.496),(.066,1.497),(.068,1.500),(.0686,1.507),(.074,1.536),(.081,1.573),
    (.088,1.609),(.093,1.637),(.096,1.638),(.103,1.639),(.106,1.642),(.107,1.646),
    (.107,1.654),(.106,1.658),(.103,1.6615),(.100,1.6625),(.095,1.6625),
    (.092,1.6605),(.0905,1.657),(.090,1.650),(.089,1.640),(.086,1.620),
    (.078,1.580),(.070,1.540),(.063,1.516),(.061,1.512),(.058,1.511)],clay)
saucer=lathe('Plant04 closed terracotta saucer',[
    (.075,1.490),(.085,1.4905),(.089,1.492),(.091,1.495),(.091,1.500),
    (.090,1.502),(.087,1.503),(.083,1.5015),(.079,1.498),(.070,1.496),(.060,1.496)],clay)
# Soil top is recessed 6.2 mm below lip. Keep the original foliage roots unchanged,
# joining them to the soil with one short central green continuation.
bpy.ops.mesh.primitive_cylinder_add(vertices=96,radius=.0887,depth=.006,location=(-.33,-.08,1.6533))
soilobj=bpy.context.object;soilobj.name='Plant04 recessed soil';soilobj.data.materials.append(soil)
for p in soilobj.data.polygons:p.use_smooth=len(p.vertices)==4
bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=.0015,depth=.0115,location=(-.33,-.08,1.66125))
root=bpy.context.object;root.name='Plant04 stem root continuation';root.data.materials.append(leaf)
for p in root.data.polygons:p.use_smooth=len(p.vertices)==4
assert leaf_signature(foliage)==original_foliage
REPORT['foliage_positions_uv_materials_preserved']=True
REPORT['assembly_origin']=[0,0,0]
REPORT['pot_max_radius_m']=.107
REPORT['shelf_base_z_m']=1.49
REPORT['rim_top_z_m']=1.6625
REPORT['soil_top_z_m']=1.6563

# Keep material slots explicit, foliage double-sided separately from the vessel.
parts=foliage+[pot,saucer,soilobj,root]
for o in parts:
    for uv in o.data.uv_layers:uv.name='UVMap'
    if not o.data.uv_layers:o.data.uv_layers.new(name='UVMap')
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=pot
bpy.ops.object.join();combined=bpy.context.object;combined.name='LV_Book04_Plant'
bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
slotmats=[leaf,light,clay,soil]
indices={m.name:i for i,m in enumerate(slotmats)}
face_materials=[indices[combined.data.materials[p.material_index].name] for p in combined.data.polygons]
combined.data.materials.clear()
for m in slotmats:combined.data.materials.append(m)
for p,i in zip(combined.data.polygons,face_materials):p.material_index=i
REPORT['materials']=[m.name for m in combined.data.materials]
bpy.ops.export_scene.fbx(filepath=str(MODEL/'LV_Book04_Plant.fbx'),use_selection=True,
    object_types={'MESH'},apply_unit_scale=True,add_leaf_bones=False,axis_forward='-Z',axis_up='Y',mesh_smooth_type='FACE')
render('plant-after')
render('pot-close',close=True)
render('pot-close-single-sided',close=True,workbench=True)
bpy.ops.file.make_paths_absolute()
bpy.ops.wm.save_as_mainfile(filepath=str(MODEL/'ROUND3-PLANT-01.blend'))
bpy.ops.file.make_paths_relative()
bpy.ops.wm.save_as_mainfile(filepath=str(MODEL/'ROUND3-PLANT-01.blend'))
(MODEL/'source-validation.json').write_text(json.dumps(REPORT,indent=2)+'\n')
print('ROUND3_PLANT_SOURCE_PASS',json.dumps(REPORT))
