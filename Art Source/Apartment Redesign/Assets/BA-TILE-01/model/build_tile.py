"""Build repeatable 1 m bathroom tile modules and removable damage in Blender background mode."""
import bpy, math, os, random
from mathutils import Vector
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL=os.path.join(ROOT,'model'); PRE=os.path.join(ROOT,'previews'); TEX=os.path.join(ROOT,'textures')
for p in (MODEL,PRE,TEX): os.makedirs(p,exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def material(name,color,rough=.8,texture=None):
 m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=rough
 if texture:
  t=m.node_tree.nodes.new('ShaderNodeTexImage'); t.image=bpy.data.images.load(texture,check_existing=True); t.extension='REPEAT'; m.node_tree.links.new(t.outputs['Color'],bs.inputs['Base Color'])
 return m
# Each material slot is a subtle glaze variation; assignments are carried by FBX.
palette=[(.92,.48,.49),(.78,.37,.41),(.90,.50,.48),(.75,.36,.40),(.86,.43,.47),(.89,.44,.42),(.80,.42,.46),(.92,.52,.51)]
pinks=[]
for index,tint in enumerate(palette):
 m=material('Pink glaze %02d'%index,(.65,.34,.37),.66,os.path.join(TEX,'candidate-b.png'))
 nodes=m.node_tree.nodes; bs=nodes.get('Principled BSDF'); tex=next(n for n in nodes if n.type=='TEX_IMAGE'); mix=nodes.new('ShaderNodeMixRGB'); mix.blend_type='MIX'; mix.inputs[0].default_value=.40; mix.inputs[2].default_value=(*tint,1); m.node_tree.links.new(tex.outputs['Color'],mix.inputs[1]); m.node_tree.links.new(mix.outputs['Color'],bs.inputs['Base Color']); pinks.append(m)
grout=material('Warm ivory grout',(.92,.81,.68)); capmat=material('Aged plum cap',(.30,.105,.14),.65)
crack=material('Crack inner shadow',(.095,.045,.032)); edge=material('Chipped ceramic edge',(.62,.43,.39)); substrate=material('Exposed old plaster',(.20,.11,.065))

def block(name,loc,dims,mat,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o=bpy.context.object; o.name=name; o.dimensions=dims; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(mat)
 if bevel:
  mod=o.modifiers.new('Soft worn profile','BEVEL'); mod.width=bevel; mod.segments=3; bpy.context.view_layer.objects.active=o; bpy.ops.object.modifier_apply(modifier=mod.name)
 return o
# Local X along wall, -Y into room, Z up; module repeats at 1.000 m.
base=[]
base.append(block('Grout backing',(.5,-.0088,.55),(1,.018,1.1),grout))
# Tiles are distinct gently eased bodies, with the same 100mm pitch across seams.
random.seed(301)
verts=[]; faces=[]; uvs=[]; assignments=[]
for row in range(11):
 for col in range(10):
  x=col*.1+.0015; z=row*.1+.0015; w=.097; y=-.018
  i=len(verts); verts += [(x,y,z),(x+w,y,z),(x+w,y,z+w),(x,y,z+w),(x,-.008,z),(x+w,-.008,z),(x+w,-.008,z+w),(x,-.008,z+w)]
  fs=[(0,1,2,3),(5,4,7,6),(4,0,3,7),(1,5,6,2),(3,2,6,7),(4,5,1,0)]
  ox=.05+random.random()*.48; oz=.05+random.random()*.48; s=.40
  tile_uv=[(ox,oz),(ox+s,oz),(ox+s,oz+s),(ox,oz+s)]; turn=random.randrange(4); tile_uv=tile_uv[turn:]+tile_uv[:turn]; slot=random.randrange(len(pinks))
  for f in fs:
   faces.append(tuple(i+n for n in f)); uvs.append(tile_uv); assignments.append(slot)
mesh=bpy.data.meshes.new('Tile field mesh'); mesh.from_pydata(verts,[],faces); mesh.update(); tiles=bpy.data.objects.new('Individual ceramic tile field',mesh); bpy.context.collection.objects.link(tiles); [mesh.materials.append(mat) for mat in pinks]
uv=mesh.uv_layers.new(name='Tile UV')
for poly,faceuv,slot in zip(mesh.polygons,uvs,assignments):
 poly.material_index=slot
 for li,coord in zip(poly.loop_indices,faceuv): uv.data[li].uv=coord
mod=tiles.modifiers.new('Minute eased ceramic edges','BEVEL'); mod.width=.001; mod.segments=2; bpy.context.view_layer.objects.active=tiles; tiles.select_set(True); bpy.ops.object.modifier_apply(modifier=mod.name); tiles.select_set(False)
base.append(tiles)
cap=[block('Plum upper cap',(.5,-.014,.025),(1,.044,.05),capmat,.003)]
# A 0.40 m high extension can be stacked below the top cap in the tub surround.
ext=[]
ext.append(block('Extension grout',(.5,-.0088,.2),(1,.018,.4),grout))
# Duplicate first 4 tile rows preserving UVs and pitch; separate extension export.
verts2=[]; faces2=[]; uvs2=[]; slots2=[]
for p in mesh.polygons:
 coords=[mesh.vertices[mesh.loops[i].vertex_index].co for i in p.loop_indices]
 if all(v.z <= .40001 for v in coords):
  start=len(verts2); verts2.extend([tuple(v) for v in coords]); faces2.append(tuple(range(start,start+len(coords)))); uvs2.append([tuple(mesh.uv_layers.active.data[i].uv) for i in p.loop_indices]); slots2.append(p.material_index)
m2=bpy.data.meshes.new('Extension tile field mesh'); m2.from_pydata(verts2,[],faces2); m2.update(); e=bpy.data.objects.new('Tub surround extra tiles',m2); bpy.context.collection.objects.link(e); [m2.materials.append(mat) for mat in pinks]
uv2=m2.uv_layers.new(name='Tile UV')
for p,vals,slot in zip(m2.polygons,uvs2,slots2):
 p.material_index=slot
 for li,coord in zip(p.loop_indices,vals): uv2.data[li].uv=coord
ext.append(e)
# Removable, shallow geometric damage patch: fissures + small chipped center. All positions in module space.
def polygon(name,pts,mat,y=-.0181):
 m=bpy.data.meshes.new(name); m.from_pydata([(x,y,z) for x,z in pts],[],[tuple(range(len(pts)))]); m.update(); ob=bpy.data.objects.new(name,m); bpy.context.collection.objects.link(ob); m.materials.append(mat); return ob
def ribbon(name,pts,width,mat,y=-.0181):
 vs=[]; fs=[]
 for (x,z),(a,b) in zip(pts[:-1],pts[1:]):
  dx=a-x; dz=b-z; ll=math.hypot(dx,dz); px=-dz/ll*width/2; pz=dx/ll*width/2; i=len(vs); vs += [(x+px,y,z+pz),(x-px,y,z-pz),(a-px,y,b-pz),(a+px,y,b+pz)]; fs.append((i,i+1,i+2,i+3))
 m=bpy.data.meshes.new(name); m.from_pydata(vs,[],fs); m.update(); ob=bpy.data.objects.new(name,m); bpy.context.collection.objects.link(ob); m.materials.append(mat); return ob
damage=[]
# Asymmetric broken edges and small missing slivers span several tiles, avoiding a round impact mark.
damage.append(polygon('Main irregular chip rim',[(.452,.593),(.462,.609),(.479,.610),(.487,.624),(.504,.621),(.514,.631),(.529,.614),(.519,.606),(.528,.596),(.514,.585),(.499,.59),(.487,.577),(.473,.589),(.461,.584)],edge))
damage.append(polygon('Main exposed tile bed',[(.458,.595),(.466,.605),(.481,.605),(.489,.619),(.505,.616),(.515,.624),(.523,.615),(.512,.606),(.521,.597),(.513,.590),(.498,.594),(.487,.583),(.475,.594),(.463,.590)],substrate,y=-.0182))
damage.append(polygon('Upper shard rim',[(.478,.668),(.488,.675),(.495,.689),(.487,.695),(.471,.689),(.465,.681)],edge))
damage.append(polygon('Upper missing fragment',[(.479,.672),(.486,.678),(.49,.686),(.485,.690),(.474,.686)],substrate,y=-.0182))
damage.append(polygon('Lower chipped grout rim',[(.52,.526),(.53,.532),(.541,.527),(.547,.515),(.536,.51),(.528,.515)],edge))
damage.append(polygon('Lower missing fragment',[(.525,.525),(.531,.528),(.538,.524),(.542,.517),(.536,.514),(.53,.519)],substrate,y=-.0182))
paths=[[(.50,.61),(.485,.63),(.487,.654),(.478,.672),(.49,.693),(.486,.718),(.476,.727),(.478,.744),(.466,.76),(.465,.782),(.454,.803),(.459,.827),(.45,.845)],[(.50,.61),(.515,.627),(.525,.647),(.54,.654),(.544,.67),(.559,.679),(.56,.701),(.572,.714),(.575,.737),(.588,.751)],[(.50,.61),(.481,.594),(.468,.586),(.462,.568),(.451,.56),(.447,.546),(.429,.535),(.425,.518),(.413,.502),(.416,.48),(.406,.457)],[(.50,.61),(.512,.597),(.515,.579),(.527,.567),(.525,.546),(.535,.53),(.53,.512),(.545,.496),(.547,.474),(.555,.463),(.552,.443),(.562,.422)],[(.478,.672),(.465,.68),(.461,.694),(.446,.70),(.439,.718)],[(.535,.53),(.55,.536),(.559,.548),(.58,.548),(.589,.56)],[(.476,.727),(.459,.737),(.45,.75)],[(.559,.679),(.573,.68),(.588,.692)],[(.447,.546),(.433,.55),(.423,.558)]]
for i,p in enumerate(paths): damage.append(ribbon('Crack branch %02d'%i,p,.0016 if i<4 else .0008,crack,y=-.0183))
# Every exported object has a common local origin, so the overlay and cap align at origin (0,0,0).
def origin_zero(objects):
 bpy.context.scene.cursor.location=(0,0,0)
 for o in objects:
  bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active=o; bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
def export(name,objects):
 for o in objects:
  if not o.data.uv_layers:
   uv=o.data.uv_layers.new(name='UVMap')
   for loop in o.data.loops:
    v=o.data.vertices[loop.vertex_index].co; uv.data[loop.index].uv=(v.x,v.z)
 origin_zero(objects); bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0]; bpy.ops.export_scene.fbx(filepath=os.path.join(MODEL,name+'.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,add_leaf_bones=False,mesh_smooth_type='FACE')
export('BA_Tile_1m_Module',base); export('BA_Tile_040_Extension',ext); export('BA_Tile_Cap',cap); export('BA_Tile_Damage',damage)
# Preview cap placed on the 1.10 m tile field; original cap FBX starts at z=0.
for o in cap:o.location.z+=1.1
# Extension stays out of the contextual sample; a second tile module demonstrates one repeat seam.
for o in ext:o.hide_render=True
for o in base+cap:
 d=o.copy(); d.data=o.data.copy(); bpy.context.collection.objects.link(d); d.location.x+=1
plaster=material('Preview plaster',(.68,.48,.42)); floor=material('Preview floor',(.32,.24,.22))
block('Preview plaster above',(1,.02,1.55),(2.5,.04,.85),plaster)
block('Preview floor',(1,-.3,-.025),(2.5,.8,.05),floor)
bpy.ops.object.camera_add(location=(2.85,-4.4,1.85)); cam=bpy.context.object; cam.rotation_euler=(Vector((1,0,.75))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=2.85; bpy.context.scene.camera=cam
bpy.ops.object.light_add(type='AREA',location=(.25,-3,3.4)); light=bpy.context.object; light.data.energy=380; light.data.shape='DISK'; light.data.size=3; light.data.color=(1,.80,.68); light.rotation_euler=(Vector((1,0,.7))-light.location).to_track_quat('-Z','Y').to_euler()
scene=bpy.context.scene; scene.world.color=(.29,.26,.24); scene.render.engine='CYCLES'; scene.cycles.samples=32; scene.render.resolution_x=1200; scene.render.resolution_y=900; scene.render.resolution_percentage=100; scene.view_settings.view_transform='AgX'; scene.render.image_settings.file_format='PNG'
scene.render.filepath=os.path.join(PRE,'tile-before.png'); bpy.ops.render.render(write_still=True)
for o in damage:o.hide_render=True
scene.render.filepath=os.path.join(PRE,'tile-after.png'); bpy.ops.render.render(write_still=True)
for o in damage:o.hide_render=False
# Close orthographic proof of individual colored tiles and removable chips.
cam.location=(.5,-2.8,.67); cam.rotation_euler=(Vector((.5,0,.67))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.ortho_scale=.75
scene.render.filepath=os.path.join(PRE,'tile-detail-before.png'); bpy.ops.render.render(write_still=True)
for o in damage:o.hide_render=True
scene.render.filepath=os.path.join(PRE,'tile-detail-after.png'); bpy.ops.render.render(write_still=True)
for o in damage:o.hide_render=False
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(MODEL,'BA-TILE-01.blend'))
print('TILE_BUILD_OK')
