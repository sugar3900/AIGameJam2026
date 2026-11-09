import bpy, math
from mathutils import Vector
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; M=ROOT/'model'; P=ROOT/'previews'; T=ROOT/'textures'; M.mkdir(exist_ok=True); P.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
def material(name,color,metallic=0,rough=.7,tex=None):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Metallic'].default_value=metallic;bs.inputs['Roughness'].default_value=rough
 if tex:
  n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=bpy.data.images.load(str(tex),check_existing=True);m.node_tree.links.new(n.outputs['Color'],bs.inputs['Base Color'])
 return m
fabric=material('Curtain_Floral',(.75,.55,.42),tex=T/'floral-candidate-a.png'); brass=material('Aged_Brass',(.48,.27,.09),.65,.37)
def cylinder(name,loc,radius,depth,rotation=(0,0,0)):
 bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=radius,depth=depth,location=loc,rotation=rotation);o=bpy.context.object;o.name=name;o.data.materials.append(brass);bpy.ops.object.shade_smooth();return o
def sphere(name,loc,r):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=10,radius=r,location=loc);o=bpy.context.object;o.name=name;o.data.materials.append(brass);bpy.ops.object.shade_smooth();return o
rod=[cylinder('Rod',(0,0,2.27),.017,2.18,(0,math.pi/2,0))]
for x in [-1.1,1.1]:rod.extend([sphere('Finial',(x,0,2.27),.037),cylinder('Bracket',(x*.89,.07,2.27),.012,.16,(math.pi/2,0,0))])
# A continuous topology with shape key: Open (Basis) -> Closed.  Seven rings are part of the same mesh and move along with fabric.
def coords(side,closed,nx=64,nz=30):
 lo,hi=((-0.80,0.0) if closed else (-.99,-.57)) if side=='Left' else ((0,.80) if closed else (.57,.99))
 verts=[]
 for j in range(nz+1):
  v=j/nz
  for i in range(nx+1):
   u=i/nx;x=lo+(hi-lo)*u
   # Rounded folds change modestly with height; a gentle rather than serrated hem.
   phase=u*math.pi*10+.12*math.sin(v*math.pi*1.4+u*3)
   y=(.038+.014*(1-v))*math.sin(phase)+.004*math.sin(u*math.pi*4+v*3)
   z=.18+2.03*v+.004*math.sin(u*math.pi*2)*(1-v)**3
   verts.append((x,y,z))
 for k in range(7):
  x=lo+(hi-lo)*(k+.5)/7
  for a in range(16):
   th=2*math.pi*a/16
   for b in range(8):
    ph=2*math.pi*b/8; rr=.027+.004*math.cos(ph)
    verts.append((x+.004*math.sin(ph),rr*math.sin(th),2.245+rr*math.cos(th)))
 return verts
panels=[]
def panel(side):
 nx,nz=64,30; verts=coords(side,False,nx,nz); closed=coords(side,True,nx,nz);assert len(verts)==len(closed)
 faces=[]
 for j in range(nz):
  for i in range(nx):
   a=j*(nx+1)+i;faces.append((a,a+1,a+nx+2,a+nx+1))
 fabricfaces=len(faces); offset=(nx+1)*(nz+1)
 for k in range(7):
  base=offset+k*16*8
  for a in range(16):
   for b in range(8):
    a1=(a+1)%16;b1=(b+1)%8;faces.append((base+a*8+b,base+a1*8+b,base+a1*8+b1,base+a*8+b1))
 mesh=bpy.data.meshes.new('Curtain_'+side);mesh.from_pydata(verts,[],faces);mesh.update();uv=mesh.uv_layers.new(name='UVMap')
 for p in mesh.polygons:
  p.use_smooth=True
  if p.index>=fabricfaces:p.material_index=1
  for li in p.loop_indices:
   index=mesh.loops[li].vertex_index
   uv.data[li].uv=((index%(nx+1))/nx,(index//(nx+1))/nz) if index<offset else (0.5,0.5)
 obj=bpy.data.objects.new('Curtain_'+side,mesh);bpy.context.collection.objects.link(obj);mesh.materials.append(fabric);mesh.materials.append(brass)
 obj.shape_key_add(name='Basis'); key=obj.shape_key_add(name='Closed')
 for i,c in enumerate(closed):key.data[i].co=c
 return obj
panels=[panel('Left'),panel('Right')]
def export(name,objects):
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0]
 bpy.ops.export_scene.fbx(filepath=str(M/(name+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,add_leaf_bones=False,bake_anim=False,path_mode='AUTO')
export('Curtain_Rod',rod)
# Bind each panel to a single neutral root so Unreal can import FBX as a skeletal mesh with its morph target.
for o in panels:
 bpy.ops.object.select_all(action='DESELECT')
 bpy.ops.object.armature_add(enter_editmode=True,location=(0,0,0)); arm=bpy.context.object;arm.name=o.name+'_Rig'; bone=arm.data.edit_bones[0];bone.name='CurtainRoot';bone.head=(0,0,0);bone.tail=(0,0,0.3);bpy.ops.object.mode_set(mode='OBJECT')
 group=o.vertex_groups.new(name='CurtainRoot');group.add(list(range(len(o.data.vertices))),1.0,'REPLACE');mod=o.modifiers.new('Skin','ARMATURE');mod.object=arm;o.parent=arm
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);arm.select_set(True);bpy.context.view_layer.objects.active=arm
 bpy.ops.export_scene.fbx(filepath=str(M/(o.name+'.fbx')),use_selection=True,object_types={'MESH','ARMATURE'},apply_unit_scale=True,add_leaf_bones=False,bake_anim=False,path_mode='AUTO')
world=bpy.context.scene.world or bpy.data.worlds.new('World');bpy.context.scene.world=world;world.color=(.18,.16,.14)
bpy.ops.object.camera_add(location=(3,-5,2.9));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,1.25))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=3.05;bpy.context.scene.camera=cam
for loc,power,size in [((1,-4,5),700,4),((-3,-2,3),300,3)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,1.2))-o.location).to_track_quat('-Z','Y').to_euler()
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=32;s.render.resolution_x=s.render.resolution_y=1200;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.film_transparent=True
for value,name in [(0,'open'),(.5,'halfway'),(1,'closed')]:
 for obj in panels:obj.data.shape_keys.key_blocks['Closed'].value=value
 s.render.filepath=str(P/('curtains-'+name+'.png'));bpy.ops.render.render(write_still=True)
for obj in panels:obj.data.shape_keys.key_blocks['Closed'].value=0
for im in bpy.data.images:
 if im.filepath:im.filepath=bpy.path.relpath(im.filepath,start=str(M))
bpy.ops.wm.save_as_mainfile(filepath=str(M/'ARC-CURTAINS-01.blend'))
