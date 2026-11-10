from pathlib import Path
import bpy, math, json, bmesh
from mathutils import Vector
P=Path(__file__).resolve().parent.parent
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.preferences.filepaths.save_version=0

def material(name,tex,tint,metal,rough):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;b=n.get('Principled BSDF');b.inputs['Metallic'].default_value=metal;b.inputs['Roughness'].default_value=rough
 t=n.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(P/'textures'/tex));t.image.pack();mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[2].default_value=(*tint,1);l.new(t.outputs['Color'],mix.inputs[1]);l.new(mix.outputs[0],b.inputs['Base Color']);m.diffuse_color=(*tint,1);return m
brass=material('Ring02_Aged_Brass','aged-brass.png',(.80,.75,.56),.68,.48)
ivory=material('Ring02_Ivory_Terry','terry.png',(.94,.91,.84),0,.94)
rose=material('Ring02_Rose_Border','terry.png',(.61,.32,.30),0,.94)
def finish(o,name,mat):
 o.name=name;o.data.materials.append(mat)
 if not o.data.uv_layers:
  bpy.context.view_layer.objects.active=o;bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT')
 for f in o.data.polygons:f.use_smooth=True
 return o
def cyl(name,r,depth,loc,rot=(math.pi/2,0,0)):
 bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=r,depth=depth,location=loc,rotation=rot);o=bpy.context.object;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);mod=o.modifiers.new('Rounded brass edge','BEVEL');mod.width=.0015;mod.segments=3;bpy.ops.object.modifier_apply(modifier=mod.name);return finish(o,name,brass)
parts=[cyl('Wall rosette',.035,.010,(0,-.005,0)),cyl('Raised boss',.018,.016,(0,-.018,0)),cyl('Short swivel stem',.009,.033,(0,-.041,-.012))]
# Torus in XZ, 21 cm ring with solid round wire. Back of hardware clears wall.
bpy.ops.mesh.primitive_torus_add(major_segments=96,minor_segments=12,location=(0,-.060,-.120),rotation=(math.pi/2,0,0),major_radius=.105,minor_radius=.007)
parts.append(finish(bpy.context.object,'Hanging circular ring',brass))
for zz in [-.023,.023]:
 parts.append(cyl('Round fixing screw',.004,.002,(0,-.0115,zz)))
for ob in parts:
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();hardware=parts[0];hardware.name='BA_Ring02_Hardware';bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
bm=bmesh.new();bm.from_mesh(hardware.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-8);bm.to_mesh(hardware.data);bm.free();hardware.data.update()
# Continuous folded towel: front, over-ring curved fold, and shorter rear leaf.
verts=[];faces=[];uv=[];slots=[];NX=40;NZ=52

def cross_z(x):return -.120-math.sqrt(.105**2-x*x)
def panel(back=False):
 start=len(verts)
 for j in range(NZ+1):
  v=j/NZ;half=.045+.085*(math.sin(v*math.pi/2)**.70)
  for i in range(NX+1):
   u=i/NX;xn=u*2-1;x=xn*half
   z=cross_z(xn*.045)-(.245 if back else .310)*v + .004*math.sin(u*15+.3)*v*v
   y=(-.048 if back else -.072) + (.018*math.sin(u*math.pi*6)*math.sqrt(math.sin(v*math.pi/2))-.006*v)
   verts.append((x,y,z));uv.append((u,1-v))
 for j in range(NZ):
  for i in range(NX):
   a=start+j*(NX+1)+i;face=(a,a+1,a+NX+2,a+NX+1)
   faces.append(face if back else tuple(reversed(face)));v=(j+.5)/NZ;slots.append(1 if (.82<v<.85 or .89<v<.92) else 0)
 return start
front=panel();back=panel(True)
# Bridge follows the curved lower arc of the ring, maintaining 12 mm radial offset.
start=len(verts);NF=12
for j in range(NF+1):
 t=j/NF*math.pi
 for i in range(NX+1):
  u=i/NX;x=(u*2-1)*.045;verts.append((x,-.060-.012*math.cos(t),cross_z(x)+.012*math.sin(t)));uv.append((u,1+j/NF*.06))
for j in range(NF):
 for i in range(NX):
  a=start+j*(NX+1)+i;faces.append((a,a+1,a+NX+2,a+NX+1));slots.append(0)
mesh=bpy.data.meshes.new('Folded terry continuous surface');mesh.from_pydata(verts,[],faces);mesh.update();towel=bpy.data.objects.new('BA_Ring02_Towel',mesh);bpy.context.collection.objects.link(towel);mesh.materials.append(ivory);mesh.materials.append(rose);layer=mesh.uv_layers.new(name='TerryUV')
for f,slot in zip(mesh.polygons,slots):
 f.material_index=slot;f.use_smooth=True
 for li in f.loop_indices:layer.data[li].uv=uv[mesh.loops[li].vertex_index]
bpy.context.view_layer.objects.active=towel;bpy.ops.object.select_all(action='DESELECT');towel.select_set(True)
# Weld the fold to both leaves using coincident vertices, then real fabric thickness.
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.remove_doubles(threshold=.0001);bpy.ops.object.mode_set(mode='OBJECT')
sol=towel.modifiers.new('Cloth thickness 2 mm','SOLIDIFY');sol.thickness=.002;sol.offset=0;bpy.ops.object.modifier_apply(modifier=sol.name)
# Verify cloth does not penetrate the brass ring; compare source vertices to torus centreline.
dist=min(math.sqrt((math.sqrt(v.co.x*v.co.x+(v.co.z+.120)**2)-.105)**2+(v.co.y+.060)**2) for v in towel.data.vertices)
assert dist>.0075,dist
exports=[]
for o in [hardware,towel]:
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
 bpy.ops.export_scene.fbx(filepath=str(P/'model'/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,add_leaf_bones=False)
 points=[o.matrix_world@v.co for v in o.data.vertices];exports.append({'file':'model/'+o.name+'.fbx','mesh':o.name,'origin':[0,0,0],'min':[min(v[i] for v in points) for i in range(3)],'max':[max(v[i] for v in points) for i in range(3)],'triangles':sum(len(f.vertices)-2 for f in o.data.polygons)})
(P/'assembly.json').write_text(json.dumps({'asset':'BA-HAND-TOWEL-RING-02','units':'metres','up':'+Z','front':'-Y','source_wall_plane':'Y=0','source_origin':'wall plate center','plan_mount':[7.84,7.10,1.15],'plan_facing':'west','source_to_plan':'(7.84+sourceY,7.10+sourceX,1.15+sourceZ)','exports':exports,'cloth_vertex_to_ring_centerline_min':dist,'ring_wire_radius':.007,'collision':'none; decorative, not moving interaction','materials':{'Ring02_Aged_Brass':{'texture':'textures/aged-brass.png','multiply':[.8,.75,.56],'metallic':.68,'roughness':.48},'Ring02_Ivory_Terry':{'texture':'textures/terry.png','multiply':[.94,.91,.84],'roughness':.94},'Ring02_Rose_Border':{'texture':'textures/terry.png','multiply':[.61,.32,.30],'roughness':.94}}},indent=2)+'\n')
# Preview-only wall and light, excluded from exports.
wallmat=bpy.data.materials.new('Preview warm plaster');wallmat.diffuse_color=(.64,.52,.38,1);wallmat.use_nodes=True;wallmat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.64,.52,.38,1)
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,.045,-.23));wall=bpy.context.object;wall.name='Preview wall';wall.dimensions=(1.2,.08,1.1);wall.data.materials.append(wallmat)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True;scene.render.resolution_x=1000;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('Preview World');scene.world.color=(.22,.22,.22)
for loc,power,size in [((-.6,-.8,1),80,1),((.8,-.3,.3),35,.8)]:
 bpy.ops.object.light_add(type='AREA',location=loc);bpy.context.object.data.energy=power;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=size;bpy.context.object.rotation_euler=(Vector((0,0,-.22))-bpy.context.object.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add();camera=bpy.context.object;scene.camera=camera;camera.data.type='ORTHO';camera.data.ortho_scale=.72
for name,pos in [('front',(0,-1.7,-.25)),('three-quarter',(.65,-1.4,.10))]:
 camera.location=pos;camera.rotation_euler=(Vector((0,-.04,-.25))-camera.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(P/'previews'/(name+'.png'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'model/BA-HAND-TOWEL-RING-02.blend'))
print('Ring kit complete; ring/cloth clearance',dist-.007)
