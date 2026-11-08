import bpy, math, os
from mathutils import Vector
from pathlib import Path
P=Path(__file__).resolve().parents[1]; os.chdir(P)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def material(name, image=None, color=(.8,.7,.6,1), rough=.6):
 m=bpy.data.materials.new(name); m.diffuse_color=color; m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Roughness'].default_value=rough
 if image:
  tx=m.node_tree.nodes.new('ShaderNodeTexImage'); tx.image=bpy.data.images.load(str(P/'textures'/image),check_existing=True); m.node_tree.links.new(tx.outputs['Color'],bs.inputs['Base Color'])
 else: bs.inputs['Base Color'].default_value=color
 return m
floral=material('Floral ceramic','ceramic-floral.png'); glaze=material('Ivory glaze','ceramic.png'); rim=material('Ochre rim',color=(.31,.14,.055,1),rough=.65)
apple=material('Apple skin','apple.png'); lemon=material('Lemon skin','lemon.png'); pear=material('Pear skin','pear.png'); stem=material('Stem',color=(.12,.055,.022,1),rough=.9)
# A continuous revolved thick-walled oval dish; the extra inner rings form the real hollow.
N=96
profile=[(.38,.006),(.40,.010),(.43,.019),(.48,.025),(.57,.030),(.68,.043),(.78,.061),(.88,.084),(.97,.109),(1.00,.126),(.995,.132),(.97,.132),(.955,.122),(.90,.105),(.82,.085),(.72,.068),(.60,.055),(.47,.048),(.32,.044),(.05,.043)]
verts=[]
for j,(r,z) in enumerate(profile):
 for i in range(N):
  a=2*math.pi*i/N-math.pi*1.5
  scallop=1+0.018*math.cos(8*a)*max(0,(z-.08)/.05)
  verts.append((.15*r*scallop*math.cos(a),.125*r*scallop*math.sin(a),z+(.0015*math.cos(8*a) if z>.12 else 0)))
faces=[]
for j in range(len(profile)-1):
 for i in range(N): faces.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i))
faces.append(tuple(reversed(tuple(range(N))))); faces.append(tuple((len(profile)-1)*N+i for i in range(N)))
mesh=bpy.data.meshes.new('Vessel_mesh'); mesh.from_pydata(verts,[],faces); mesh.update(); bowl=bpy.data.objects.new('Bowl',mesh); bpy.context.collection.objects.link(bowl)
bowl.data.materials.clear(); [bowl.data.materials.append(m) for m in (floral,glaze,rim)]
uv=mesh.uv_layers.new(name='UVMap')
for f in mesh.polygons:
 j=f.index//N; i=f.index%N
 f.material_index=0 if j<9 else (2 if j==10 else 1)
 f.use_smooth=True
 if f.index < (len(profile)-1)*N:
  for li,(uu,vv) in zip(f.loop_indices,[(i/N,profile[j][1]/.132),((i+1)/N,profile[j][1]/.132),((i+1)/N,profile[j+1][1]/.132),(i/N,profile[j+1][1]/.132)]): uv.data[li].uv=(uu,vv)
 else:
  for li in f.loop_indices:
   co=mesh.vertices[mesh.loops[li].vertex_index].co; uv.data[li].uv=(.5+co.x/.30,.5+co.y/.25)
# bottom / rim band needs UV on caps; small geometrically separate brown ceramic bead.
def sphere(name,loc,scale,mat,kind='sphere'):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=40,ring_count=24,location=loc); ob=bpy.context.object; ob.name=name
 for v in ob.data.vertices:
  z=v.co.z
  if kind=='apple':
   v.co.x*=1-.20*max(z,0)**5; v.co.y*=1-.20*max(z,0)**5; v.co.z-=.12*max(z,0)**12
  elif kind=='pear':
   f=1-.43*max(0,z+.15); v.co.x*=f; v.co.y*=f
 ob.scale=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 ob.data.materials.append(mat)
 for f in ob.data.polygons: f.use_smooth=True
 return ob
fruit=[]
def create_fruit(name,loc,sc,mat,kind,stalk=False):
 ob=sphere(name,loc,sc,mat,kind)
 if stalk:
  bpy.ops.mesh.primitive_cone_add(vertices=12,radius1=.0024,radius2=.0015,depth=.016,location=(loc[0],loc[1],loc[2]+sc[2]+.004)); st=bpy.context.object; st.name=name+'_stem'; st.data.materials.append(stem)
  bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True); st.select_set(True); bpy.context.view_layer.objects.active=ob; bpy.ops.object.join()
 fruit.append(ob)
create_fruit('Apple_A',(-.066,.028,.100),(.036,.034,.032),apple,'apple',True)
create_fruit('Apple_B',(.067,.027,.100),(.036,.034,.032),apple,'apple',True)
create_fruit('Pear',(0,.037,.110),(.041,.040,.052),pear,'pear',True)
create_fruit('Lemon_A',(-.038,-.051,.090),(.044,.029,.029),lemon,'sphere')
create_fruit('Lemon_B',(.041,-.050,.090),(.044,.029,.029),lemon,'sphere')
# Lightly round, solid end tips typical of a lemon.
for ob in fruit[-2:]:
 for v in ob.data.vertices:
  v.co.x*=1.0+.16*abs(v.co.x/.044)**6
# Export selected objects individually. Fruit origins stay at fruit center and dimensions are in metres.
def export(ob, name):
 bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True); bpy.context.view_layer.objects.active=ob
 bpy.ops.export_scene.fbx(filepath=str(P/'model'/name),use_selection=True,object_types={'MESH'},apply_unit_scale=True,axis_forward='-Y',axis_up='Z',add_leaf_bones=False,path_mode='AUTO')
export(bowl,'KI_Bowl.fbx')
for ob in fruit: export(ob,ob.name+'.fbx')
# Preview scene
bpy.ops.object.camera_add(location=(.53,-.70,.50)); cam=bpy.context.object; cam.name='Camera'; cam.rotation_euler=(Vector((0,0,.10))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=.49; bpy.context.scene.camera=cam
for name, loc, power, size in [('Key',(0,-.7,1.1),13,1.2),('Fill',(.7,.3,.6),5,.9),('Rim',(-.6,.3,.8),7,.8)]:
 bpy.ops.object.light_add(type='AREA',location=loc); l=bpy.context.object; l.name=name; l.data.energy=power; l.data.shape='DISK'; l.data.size=size; l.rotation_euler=(Vector((0,0,.08))-l.location).to_track_quat('-Z','Y').to_euler()
scene=bpy.context.scene; scene.render.engine='CYCLES'; scene.cycles.samples=48; scene.render.resolution_x=1000; scene.render.resolution_y=1000; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=True
scene.world.color=(.15,.15,.15); scene.view_settings.view_transform='AgX'
for im in bpy.data.images:
 if im.source=='FILE': im.filepath='//../textures/'+Path(im.filepath).name
bpy.ops.wm.save_as_mainfile(filepath=str(P/'model'/'KI-BOWL-01.blend'))
scene.render.filepath=str(P/'previews'/'bowl-three-quarter.png'); bpy.ops.render.render(write_still=True)
