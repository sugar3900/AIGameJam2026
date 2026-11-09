import bpy, math, random
from pathlib import Path
from mathutils import Vector
D=Path(__file__).resolve().parent.parent
random.seed(18)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene; scene.unit_settings.system='METRIC'
def material(name,color,rough=.8,texture=None):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough
 if texture:
  t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(texture));t.image.pack();m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
 return m
rose=material('Dusty_Rose_Painterly',(.64,.31,.28),texture=D/'textures/petals-painterly.png')
cream=material('Warm_Ivory_Petal',(.82,.72,.56)); stem=material('Dried_Stems',(.23,.17,.09));leafmat=material('Muted_Sage_Leaves',(.30,.35,.21));center=material('Warm_Flower_Centres',(.58,.39,.16))
objects=[]
def rod(name,a,b,r,mat):
 a,b=Vector(a),Vector(b);v=b-a
 bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=r,depth=v.length,location=(a+b)*.5);o=bpy.context.object;o.name=name;o.rotation_euler=v.to_track_quat('Z','Y').to_euler();o.data.materials.append(mat);objects.append(o)
 for p in o.data.polygons:p.use_smooth=True
 return o
def flower(pos,scale,mat,angle):
 # Individual petal fans form true concave, lightly curved petals with UVs.
 pos=Vector(pos);normal=Vector((.25*math.cos(angle),.25*math.sin(angle),.96)).normalized();u=normal.cross(Vector((0,1,0))).normalized();v=normal.cross(u).normalized();verts=[];faces=[]
 for i in range(5):
  th=2*math.pi*i/5+angle;rad=u*math.cos(th)+v*math.sin(th);side=-u*math.sin(th)+v*math.cos(th);q=pos+rad*scale*.52
  pts=[pos+rad*scale*.13,q-side*scale*.35,q+rad*scale*.56-side*scale*.23+normal*scale*.14,q+rad*scale*.70+normal*scale*.17,q+rad*scale*.56+side*scale*.23+normal*scale*.14,q+side*scale*.35]
  st=len(verts);verts.extend([tuple(p) for p in pts]);faces.append(tuple(st+j for j in range(6)))
 mesh=bpy.data.meshes.new('petals');mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new('Blossom',mesh);scene.collection.objects.link(o);mesh.materials.append(mat);uv=mesh.uv_layers.new(name='UVMap')
 for poly in mesh.polygons:
  for li in poly.loop_indices:
   idx=mesh.loops[li].vertex_index%6;uv.data[li].uv=((.15,.15),(.25,.3),(.4,.6),(.6,.8),(.75,.6),(.8,.3))[idx]
 objects.append(o)
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=scale*.21,location=pos+normal*scale*.08);o=bpy.context.object;o.name='FlowerCentre';o.data.materials.append(center);objects.append(o)
def leaf(a,b,width):
 a,b=Vector(a),Vector(b);axis=b-a; side=axis.cross(Vector((0,1,0))).normalized()*width;mid=(a+b)*.5
 verts=[a,a.lerp(b,.25)+side*.72,mid+side,a.lerp(b,.8)+side*.58,b,a.lerp(b,.8)-side*.58,mid-side,a.lerp(b,.25)-side*.72,mid+Vector((0,-.003,.003))];faces=[(i,(i+1)%8,8) for i in range(8)]
 mesh=bpy.data.meshes.new('Leaf');mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new('SageLeaf',mesh);scene.collection.objects.link(o);o.data.materials.append(leafmat);uv=mesh.uv_layers.new(name='UVMap')
 for p in mesh.polygons:
  for li in p.loop_indices:
   co=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=((co.x+.14)/.28,(co.z+.12)/.4)
 objects.append(o)
# Origin at vase mouth centre; lower stems descend 0.13 m inside.
tips=[(-.098,-.025,.19),(-.054,.024,.245),(.0,.0,.258),(.058,-.02,.218),(.095,.027,.188)]
for i,t in enumerate(tips):
 start=Vector(((i-2)*.002,0,-.13)); tip=Vector(t);mid=start.lerp(tip,.65)+Vector((.003*math.sin(i),.004,.006));rod('MainStem',start,mid,.0017,stem);rod('MainStem',mid,tip,.00135,stem)
 for j in range(6):
  k=.65+j*.065;base=mid.lerp(tip,(k-.65)/.35); ang=i*1.7+j*2.4; offset=Vector((math.cos(ang)*(.018+j*.002),math.sin(ang)*(.012+j*.001),.008+j*.003));end=base+offset;rod('Branch',base,end,.00075,stem)
  for n in range(3):
   loc=end+Vector((math.cos(ang+n*2)*.006,math.sin(ang+n*2)*.006,n*.003));flower(loc,.007+(i%2)*.0005,rose if (i+j)%3 else cream,ang+n)
 for n in range(4):
  a=n*math.tau/4;flower(tip+Vector((math.cos(a)*.007,math.sin(a)*.007,.002)),.007,rose if i%2 else cream,a)
 for j in range(2):
  q=start.lerp(tip,.56+j*.14);off=Vector(((-1 if (i+j)%2 else 1)*(.035+j*.005),.010*math.sin(i+j),.018));rod('LeafStalk',q,q+off*.3,.00065,stem);leaf(q+off*.3,q+off,.009)
# Join by material, preserve UVs and shared origin.
for mat in (stem,leafmat,rose,cream,center):
 bpy.ops.object.select_all(action='DESELECT');group=[o for o in scene.objects if o.type=='MESH' and not o.name.startswith('Flowers_') and o.data.materials and o.data.materials[0]==mat]
 for o in group:o.select_set(True)
 bpy.context.view_layer.objects.active=group[0];bpy.ops.object.join();o=bpy.context.object;o.name='Flowers_'+mat.name
 bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');
# Save/export selected authored objects only.
flowers=[o for o in scene.objects if o.name.startswith('Flowers_')]
bpy.ops.object.select_all(action='DESELECT')
for o in flowers:o.select_set(True)
bpy.context.view_layer.objects.active=flowers[0]
bpy.ops.export_scene.fbx(filepath=str(D/'model/HA_FLOWERS_01.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,add_leaf_bones=False)
# Add previously authored vase as preview only; its packed material is retained.
vasefile=D.parent/'HA-VASE-01/model/HA-VASE-01.blend'
with bpy.data.libraries.load(str(vasefile),link=False) as (src,dst):dst.objects=['HA_VASE_01']
vase=dst.objects[0];scene.collection.objects.link(vase);vase.location.z=-.26
world=bpy.data.worlds.new('Studio');scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.19,.18,.17,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.6
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
def light(name,loc,power,size):
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=loc;aim(o,(0,0,0))
light('Key',(.4,-.65,.8),18,.8);light('Fill',(-.7,-.1,.4),8,.8);light('Rim',(.3,.5,.6),10,.6)
d=bpy.data.cameras.new('Camera');cam=bpy.data.objects.new('Camera',d);scene.collection.objects.link(cam);cam.location=(.46,-.83,.40);aim(cam,(0,0,-.015));d.type='ORTHO';d.ortho_scale=.68;scene.camera=cam
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.render.resolution_x=1024;scene.render.resolution_y=1024;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=True;scene.view_settings.view_transform='AgX'
bpy.ops.wm.save_as_mainfile(filepath=str(D/'model/HA-FLOWERS-01.blend'))
scene.render.filepath=str(D/'previews/flowers-in-vase.png');bpy.ops.render.render(write_still=True)
vase.hide_render=True;cam.location=(0,-.8,.23);aim(cam,(0,0,.06));d.ortho_scale=.43;scene.render.filepath=str(D/'previews/flowers-front.png');bpy.ops.render.render(write_still=True)
