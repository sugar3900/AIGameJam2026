import bpy, math, random
from mathutils import Vector
from pathlib import Path
BASE=Path(__file__).resolve().parent.parent
random.seed(241)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for m in list(bpy.data.materials): bpy.data.materials.remove(m)
def material(name,c,texture=None):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*c,1);bs.inputs['Roughness'].default_value=.86
 if texture:
  n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=bpy.data.images.load(str(BASE/'textures'/texture),check_existing=True);n.image.filepath='//../textures/'+texture;m.node_tree.links.new(n.outputs['Color'],bs.inputs['Base Color'])
 return m
clay=material('Aged terracotta',(.54,.24,.12),'terracotta.png');leaf=material('Painted geranium leaves',(.27,.37,.12),'geranium-leaf.png'); stem=material('Stems',(.26,.32,.09));soil=material('Soil',(.07,.04,.025));rose=material('Dusty rose petals',(.50,.12,.13));rose2=material('Soft pale rose petals',(.68,.24,.24)); yellow=material('Flower centers',(.8,.55,.2))
def lathe(name,profile,mat,n=48):
 verts=[];faces=[]
 for radius,z in profile:
  for j in range(n):
   a=2*math.pi*j/n;verts.append((radius*math.cos(a),radius*math.sin(a),z))
 for i in range(len(profile)-1):
  for j in range(n):faces.append((i*n+j,i*n+(j+1)%n,(i+1)*n+(j+1)%n,(i+1)*n+j))
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);ob.data.materials.append(mat);uv=me.uv_layers.new(name='UVMap')
 for p in me.polygons:
  p.use_smooth=True
  for li in p.loop_indices:
   vi=me.loops[li].vertex_index;j=vi%n;i=vi//n;u=j/n
   if j==0 and any(me.loops[l].vertex_index%n==n-1 for l in p.loop_indices):u=1
   uv.data[li].uv=(u,profile[i][1]/.13)
 return ob
pot=lathe('Pot',[(.042,0),(.049,.004),(.059,.104),(.067,.107),(.068,.118),(.064,.123),(.054,.123),(.052,.112)],clay)
lathe('Soil',[(.0001,.109),(.053,.109)],soil)
def tube(name,points,radius,mat):
 cv=bpy.data.curves.new(name,'CURVE');cv.dimensions='3D';cv.resolution_u=2;cv.bevel_depth=radius;cv.bevel_resolution=1
 sp=cv.splines.new('BEZIER');sp.bezier_points.add(len(points)-1)
 for p,co in zip(sp.bezier_points,points):p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
 sp.resolution_u=3;ob=bpy.data.objects.new(name,cv);bpy.context.collection.objects.link(ob);ob.data.materials.append(mat);return ob
def round_leaf(name,center,r,tilt):
 # Scalloped radial discs, modeled and UV mapped; gentle center ridge.
 n=32;verts=[Vector(center)+Vector((0,0,.003))];uvs=[(.5,.5)];faces=[]
 for i in range(n):
  a=2*math.pi*i/n;rad=r*(.91+.09*math.cos(8*a));x=rad*math.cos(a);y=rad*math.sin(a)
  verts.append(Vector(center)+Vector((x,y,tilt*x-.002)));uvs.append((.5+.46*x/r,.5+.46*y/r))
 for i in range(n):faces.append((0,i+1,(i+1)%n+1))
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);ob.data.materials.append(leaf);uv=me.uv_layers.new(name='UVMap')
 for p in me.polygons:
  p.use_smooth=True
  for li in p.loop_indices: uv.data[li].uv=uvs[me.loops[li].vertex_index]
 return ob
# Individual petioles and overlapping rounded, zoned leaves in compact tiers.
for i in range(25):
 a=i*2.39996+random.uniform(-.15,.15);r=random.uniform(.035,.070);z=random.uniform(.142,.225)
 end=Vector((r*math.cos(a),r*math.sin(a),z));start=Vector((.012*math.cos(a),.012*math.sin(a),.110));tube('Leaf stem',[start,(start+end)*.5+Vector((0,0,.013)),end],.0012,stem)
 round_leaf('Scalloped leaf',end,random.uniform(.025,.038),random.uniform(-.35,.35))
def flower(center,scale,angle):
 # Five soft rounded petals: flattened ellipsoids, grouped later by material.
 for j in range(5):
  a=angle+j*2*math.pi/5;bpy.ops.mesh.primitive_uv_sphere_add(segments=8,ring_count=4,location=(center.x+scale*.48*math.cos(a),center.y+scale*.48*math.sin(a),center.z+random.uniform(-.001,.001)))
  ob=bpy.context.object;ob.name='Flower petal';ob.scale=(scale*.63,scale*.35,scale*.11);ob.rotation_euler=(.46,.18,a);ob.data.materials.append(rose if j%2 else rose2)
  bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
  for p in ob.data.polygons:p.use_smooth=True
 bpy.ops.mesh.primitive_uv_sphere_add(segments=8,ring_count=5,radius=scale*.16,location=center+Vector((0,0,.001)));bpy.context.object.name='Flower center';bpy.context.object.data.materials.append(yellow)
# Flower heads visibly distinct, modest heights for sill use.
for h in range(4):
 a=[.35,2.6,4.6,5.5][h];rad=[.028,.045,.035,.052][h];top=Vector((rad*math.cos(a),rad*math.sin(a),[.365,.325,.338,.30][h]));start=Vector((0,0,.11));tube('Flower stalk',[start,(start+top)*.5,top],.0018,stem)
 for f in range(11):
  q=f*2.39996; rr=.013*(f%3);c=top+Vector((rr*math.cos(q),rr*math.sin(q),.010*math.cos(q)))
  flower(c,random.uniform(.010,.014),q)
# Convert curves and UV any shapes missing UVs, then join by material.
for ob in list(bpy.context.scene.objects):
 if ob.type=='CURVE':
  bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.convert(target='MESH')
for ob in list(bpy.context.scene.objects):
 if ob.type=='MESH' and not ob.data.uv_layers:
  bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project();bpy.ops.object.mode_set(mode='OBJECT')
for mat in [clay,soil,leaf,stem,rose,rose2,yellow]:
 group=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.data.materials and o.data.materials[0]==mat]
 if len(group)>1:
  bpy.ops.object.select_all(action='DESELECT')
  for o in group:o.select_set(True)
  bpy.context.view_layer.objects.active=group[0];bpy.ops.object.join()
production=[o for o in bpy.context.scene.objects if o.type=='MESH'];bpy.ops.object.select_all(action='DESELECT')
for o in production:o.select_set(True)
bpy.context.view_layer.objects.active=pot
bpy.ops.export_scene.fbx(filepath=str(BASE/'model'/'KI_Geranium.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,add_leaf_bones=False,mesh_smooth_type='FACE')
world=bpy.context.scene.world;world.color=(.15,.15,.15)
def area(name,loc,energy,size):
 data=bpy.data.lights.new(name,'AREA');data.energy=energy;data.shape='DISK';data.size=size;ob=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector((0,0,.2))-ob.location).to_track_quat('-Z','Y').to_euler()
area('Key',(-1,-2,2.5),80,2);area('Fill',(1.5,-1,1.2),45,1.5);area('Rim',(0,1.6,2),55,1)
camdata=bpy.data.cameras.new('Camera');cam=bpy.data.objects.new('Camera',camdata);bpy.context.collection.objects.link(cam);cam.location=(.7,-1.1,.65);cam.rotation_euler=(Vector((0,0,.19))-cam.location).to_track_quat('-Z','Y').to_euler();camdata.type='ORTHO';camdata.ortho_scale=.49;bpy.context.scene.camera=cam
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.render.resolution_x=900;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.film_transparent=True;scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG';scene.render.filepath=str(BASE/'previews'/'geranium-perspective.png')
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'model'/'KI-PLANT-01.blend'));bpy.ops.render.render(write_still=True)
