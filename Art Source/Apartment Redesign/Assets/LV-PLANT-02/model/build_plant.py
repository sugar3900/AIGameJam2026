import bpy,bmesh,math,random,json,hashlib,shutil
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
BASE=Path(__file__).resolve().parent.parent
OLD=BASE.parent/'LV-PLANT-01'
random.seed(1414)
for p in (OLD/'textures').glob('*.png'): shutil.copy2(p,BASE/'textures'/p.name)
bpy.ops.wm.open_mainfile(filepath=str(OLD/'model/LV-PLANT-01.blend'))
scene=bpy.context.scene
materials={m.name:m for m in bpy.data.materials}
clay=materials['Painted weathered terracotta']; leafmat=materials['Variegated pothos painted leaf']; stemmat=materials['Olive green stems'];soilmat=materials['Dark potting soil'];cream=materials['Worn cream slip decoration']
for m in [clay,leafmat,stemmat,soilmat,cream]:
    m.use_backface_culling=True
    for n in m.node_tree.nodes:
        if n.type=='TEX_IMAGE' and n.image: n.image.filepath=str(BASE/'textures'/Path(n.image.filepath).name);n.image.reload()
keep=[o for o in scene.objects if o.type=='MESH' and o.data.materials and o.data.materials[0] in [clay,soilmat,cream]]
def fingerprint(o):
    return hashlib.sha256(json.dumps({'verts':[list(v.co) for v in o.data.vertices],'faces':[list(p.vertices) for p in o.data.polygons],'uv':[[list(d.uv) for d in l.data] for l in o.data.uv_layers]}).encode()).hexdigest()
audit={'old_preserved_groups':{o.name:fingerprint(o) for o in keep},'corrections':['Vines rise over rim before descending outside it','Every leaf has a closed 0.45 mm shell and outward normals','Pot underside capped; original visible vertices, polygons and UV coordinates retained','Source origin preserved; stand seating uses +0.511 m plant origin']}
for o in list(scene.objects):
    if o not in keep: bpy.data.objects.remove(o,do_unlink=True)
pot=next(o for o in keep if o.data.materials[0]==clay)
# Add underside only. Preserve old face ordering/UVs using bmesh, validate prefix below.
oldverts=[list(v.co) for v in pot.data.vertices]; oldfaces=[list(p.vertices) for p in pot.data.polygons]; olduv=[list(d.uv) for d in pot.data.uv_layers[0].data]
bm=bmesh.new();bm.from_mesh(pot.data);bm.verts.ensure_lookup_table();f=bm.faces.new([bm.verts[i] for i in reversed(range(64))]);uv=bm.loops.layers.uv.active
for l in f.loops:l[uv].uv=(.5+l.vert.co.x/.14,.5+l.vert.co.y/.14)
bm.to_mesh(pot.data);bm.free();pot.data.update()
assert oldverts==[list(v.co) for v in pot.data.vertices][:len(oldverts)]
assert oldfaces==[list(p.vertices) for p in pot.data.polygons][:len(oldfaces)]
assert olduv==[list(d.uv) for d in pot.data.uv_layers[0].data][:len(olduv)]
audit['pot_added_bottom_faces']=1
soil=next(o for o in keep if o.data.materials[0]==soilmat)
bm=bmesh.new();bm.from_mesh(soil.data);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(soil.data);bm.free();soil.data.update()
assert all(p.normal.z>.99 for p in soil.data.polygons)
audit['soil_correction']='Original soil disk faced downward. Reversed face winding only, preserving vertex positions and per-corner UV mapping; now faces +Z.'
src=(OLD/'model/build_plant.py').read_text()
exec(src[src.index('def curve('):src.index('# Pale narrow')])
exec(src[src.index('def heart_leaf('):src.index('# Layered radial')])
leaves=[];roots=[]
def leaf(name,attach,direction,w,l,roll):
    ob=heart_leaf(name,attach,direction,w,l,roll)
    bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
    mod=ob.modifiers.new('Closed leaf lamina 0.45 mm','SOLIDIFY');mod.thickness=.00045;mod.offset=0;mod.use_rim=True
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=bm.faces)
    assert all(e.is_manifold for e in bm.edges),name
    bm.to_mesh(ob.data);bm.free();leaves.append(ob);roots.append(list(attach));return ob
for i in range(32):
    a=i*2.399963+random.uniform(-.12,.12);r=random.uniform(.025,.09);z=random.uniform(.25,.34)
    start=Vector((.025*math.cos(a),.025*math.sin(a),.175));end=Vector((r*math.cos(a),r*math.sin(a),z))
    curve('Canopy stem %02d'%i,[start,(start+end)*.5+Vector((0,0,.02)),end],.0014,stemmat)
    leaf('Canopy leaf %02d'%i,end,(math.cos(a),math.sin(a),random.uniform(-.1,.55)),random.uniform(.06,.082),random.uniform(.075,.10),random.uniform(-.6,.6))
for i in range(12):
    a=i*2.399963;r=random.uniform(.065,.08);start=Vector((.018*math.cos(a),.018*math.sin(a),.176));end=Vector((r*math.cos(a),r*math.sin(a),.248+random.uniform(0,.012)))
    curve('Low stem %02d'%i,[start,(start+end)*.5+Vector((0,0,.01)),end],.0014,stemmat)
    leaf('Low leaf %02d'%i,end,(math.cos(a),math.sin(a),random.uniform(-.1,.1)),random.uniform(.052,.073),random.uniform(.06,.08),random.uniform(-.5,.5))
for i in range(7):
    a=2*math.pi*i/7+random.uniform(-.15,.15)
    profile=[(.025,.175),(.050,.222),(.105,.231),(.132,.213),(.15,.163),(.167,.115),(.18,.080)]
    points=[Vector((r*math.cos(a+.12*j/6),r*math.sin(a+.12*j/6),z)) for j,(r,z) in enumerate(profile)]
    curve('Trailing vine %02d'%i,points,.0018,stemmat)
    for k in [3,4,6]:
        angle=a+.12*k/6;out=Vector((math.cos(angle),math.sin(angle),0));attach=points[k]+out*.012+Vector((0,0,.006))
        curve('Petiole %02d-%02d'%(i,k),[points[k],attach],.0012,stemmat)
        leaf('Trailing leaf %02d-%02d'%(i,k),attach,out*.45+Vector((0,0,-.85)),random.uniform(.047,.064),random.uniform(.052,.064),random.uniform(-.65,.65))
for o in list(scene.objects):
    if o.type=='CURVE':
        o.data.use_fill_caps=True;bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH')
    if o.type=='MESH' and not o.data.uv_layers:
        bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
        bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project();bpy.ops.object.mode_set(mode='OBJECT')
def tree(obs):
    verts=[];faces=[]
    for ob in obs:
        offset=len(verts);verts.extend([ob.matrix_world@v.co for v in ob.data.vertices]);faces.extend([tuple(offset+i for i in p.vertices) for p in ob.data.polygons])
    return BVHTree.FromPolygons(verts,faces)
pottree=tree([pot]);stems=[o for o in scene.objects if o.type=='MESH' and o.data.materials[0]==stemmat]
leafhits=[(o.name,len(pottree.overlap(tree([o])))) for o in leaves if pottree.overlap(tree([o]))]
stemhits=[(o.name,len(pottree.overlap(tree([o])))) for o in stems if pottree.overlap(tree([o]))]
audit['leaf_pot_intersections']=leafhits;audit['stem_pot_intersections']=stemhits
assert not leafhits and not stemhits,(leafhits,stemhits)
audit['leaf_count']=len(leaves);audit['lowest_leaf_z']=min(v.co.z for o in leaves for v in o.data.vertices)
assert audit['lowest_leaf_z']>.015
st=tree(stems);audit['largest_leaf_root_to_stem_surface_distance']=max(st.find_nearest(Vector(r))[3] for r in roots)
assert audit['largest_leaf_root_to_stem_surface_distance']<.003
production=[]
for mat,name in [(clay,'Pot'),(leafmat,'Leaves'),(stemmat,'Stems'),(soilmat,'Soil'),(cream,'Decoration')]:
    group=[o for o in scene.objects if o.type=='MESH' and o.data.materials[0]==mat]
    bpy.ops.object.select_all(action='DESELECT')
    for o in group:o.select_set(True)
    bpy.context.view_layer.objects.active=group[0]
    if len(group)>1:bpy.ops.object.join()
    ob=bpy.context.object;ob.name='LV_Plant02_'+name;production.append(ob)
# Closed convex pot-only collision. Foliage is intentionally non-blocking.
bpy.ops.mesh.primitive_cone_add(vertices=12,radius1=.066,radius2=.099,depth=.190,location=(0,0,.100));ucx=bpy.context.object;ucx.name='UCX_LV_Plant02_Pot_00'
bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);ucx.hide_render=True
bpy.ops.object.select_all(action='DESELECT')
for o in production+[ucx]:o.select_set(True)
bpy.context.view_layer.objects.active=pot
bpy.ops.export_scene.fbx(filepath=str(BASE/'model/LV_Plant02.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,add_leaf_bones=False,mesh_smooth_type='FACE',path_mode='AUTO')
def bounds(obs):
    points=[o.matrix_world@v.co for o in obs for v in o.data.vertices]
    return {'min':[min(v[i] for v in points) for i in range(3)],'max':[max(v[i] for v in points) for i in range(3)]}
manifest={'asset':'LV-PLANT-02','source_axes':{'front':'-Y','up':'+Z','units':'metres'},'origin':'Original pot origin unchanged; base is Z +0.005 m','fbx':'model/LV_Plant02.fbx','parts':[],'stand_fit':{'stand':'LV-PLANT-STAND-01','stand_top_z':.480,'riser_top_z':.516,'plant_origin_z_for_exact_seating':.511,'delta_from_old_documented_placement_m':-.005,'pot_base_radius':.065,'riser_radius':.078,'lowest_leaf_above_stand_top_m':.511+audit['lowest_leaf_z']-.480},'bounds':bounds(production),'engine_material_contract':'Opaque leaf shells, alpha 1, transmission 0. No Two Sided workaround needed. No leaf/stem collision. Preserve original painted texture colour; do not multiply texture by base fallback colour.'}
for o in production:
    m=o.data.materials[0];bs=m.node_tree.nodes.get('Principled BSDF');textures=[Path(n.image.filepath).name for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image]
    manifest['parts'].append({'node':o.name,'material':m.name,'slot':0,'base_color_linear':list(bs.inputs['Base Color'].default_value),'roughness':bs.inputs['Roughness'].default_value,'metallic':bs.inputs['Metallic'].default_value,'base_color_texture':('textures/'+textures[0]) if textures else None,'bounds':bounds([o]),'triangles':sum(len(p.vertices)-2 for p in o.data.polygons),'collision':ucx.name if o==pot else None})
(BASE/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');(BASE/'source-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
world=bpy.data.worlds.new('Plant studio');scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.13,.15,1);world.node_tree.nodes['Background'].inputs[1].default_value=.5
for name,loc,energy,size in [('Key',(-1,-2,2.5),85,2),('Fill',(1.5,-1,1.2),45,1.5),('Rim',(0,1.6,2),55,1)]:
    d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,.2))-o.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('Camera');cam=bpy.data.objects.new('Camera',d);scene.collection.objects.link(cam);scene.camera=cam;d.type='ORTHO'
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.render.threads_mode='FIXED';scene.render.threads=2;scene.render.resolution_x=1100;scene.render.resolution_y=1100;scene.render.resolution_percentage=100;scene.render.film_transparent=True;scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG'
def render(name,loc,target,scale):
    cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();d.ortho_scale=scale;scene.render.filepath=str(BASE/'previews'/name);bpy.ops.render.render(write_still=True)
for image in bpy.data.images:
    if image.source=='FILE' and image.filepath:
        try:image.pack()
        except:pass
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'model/LV-PLANT-02.blend'))
render('plant-three-quarter.png',(.7,-1.1,.75),(0,0,.19),.58)
render('plant-top.png',(0,-.0001,1),(0,0,.18),.50)
render('plant-side.png',(.9,-.03,.21),(0,0,.19),.55)
render('plant-underside.png',(.55,-.9,-.15),(0,0,.16),.55)
with bpy.data.libraries.load(str(BASE.parent/'LV-PLANT-STAND-01/model/LV-PLANT-STAND-01.blend'),link=False) as (fr,to):to.objects=[n for n in fr.objects if n in ['LV_PLANT_STAND_01','Optional pot riser']]
for ob in to.objects:scene.collection.objects.link(ob);ob.hide_render=False;ob.hide_viewport=False
for ob in production:ob.location.z+=.511
render('plant-stand-context.png',(.9,-1.4,1.25),(0,0,.43),1.04)
print('PLANT_COMPLETE',json.dumps(audit))
