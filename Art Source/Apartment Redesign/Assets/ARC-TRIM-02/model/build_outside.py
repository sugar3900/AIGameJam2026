"""Additive ARC-TRIM-01-compatible outside mitres. Blender --background --python thisfile."""
from pathlib import Path
import ast, bpy, bmesh, math, json, hashlib
from mathutils import Vector
ROOT=Path(__file__).resolve().parent.parent
OLD=ROOT.parent/'ARC-TRIM-01'
# Extract the released profile literals: any future original change is explicit evidence.
tree=ast.parse((OLD/'model/build_trim.py').read_text())
PROFILES={}
for node in ast.walk(tree):
 if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=='molding' and len(node.args)>1 and isinstance(node.args[0],ast.Constant):
  name=node.args[0].value
  if name in ('Baseboard_1m','Crown_1m'):PROFILES[name.split('_')[0]]=ast.literal_eval(node.args[1])
assert set(PROFILES)=={'Baseboard','Crown'}
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
mat=bpy.data.materials.new('AgedIvoryPaint');mat.use_nodes=True
n=mat.node_tree.nodes;l=mat.node_tree.links;p=n.get('Principled BSDF')
t=n.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(ROOT/'textures/paint-selected.png'));t.image.colorspace_settings.name='sRGB'
m=n.new('ShaderNodeMixRGB');m.blend_type='MIX';m.inputs[0].default_value=.36;m.inputs[2].default_value=(.82,.76,.65,1)
l.new(t.outputs['Color'],m.inputs[1]);l.new(m.outputs[0],p.inputs['Base Color']);p.inputs['Roughness'].default_value=.84

def strip(family,side,profile):
 name=f'{family}_Outside_{side}';count=len(profile)
 # Convex/outside corner: length extends past wall corner by its projection.
 vertices=[((y if side=='Start' else 0),y,z) for y,z in profile]+[((1-y if side=='End' else 1),y,z) for y,z in profile]
 faces=[tuple(reversed(range(count))),tuple(range(count,2*count))]+[(i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count)]
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update()
 ob=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(ob)
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bmesh.ops.triangulate(bm,faces=bm.faces[:]);bm.to_mesh(mesh);bm.free()
 uv=mesh.uv_layers.new(name='UVMap')
 for face in mesh.polygons:
  for li in face.loop_indices:
   v=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=(v.x,(v.z+v.y)*2.5)
 mesh.materials.append(mat)
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
 bpy.ops.export_scene.fbx(filepath=str(ROOT/'model'/f'{name}.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,axis_forward='-Y',axis_up='Z',add_leaf_bones=False,path_mode='RELATIVE')
 return ob
objs={}
for family,prof in PROFILES.items():
 for side in ('End','Start'):objs[(family,side)]=strip(family,side,prof)
# Compact outside-corner studio. End from x=0 to1; Start at x1, +90 degree Z.
for (family,side),ob in objs.items():
 ob.location.z=1.1 if family=='Crown' else 0
 if side=='Start':ob.location.x=1;ob.rotation_euler.z=math.pi/2

def plain(name,col):
 a=bpy.data.materials.new(name);a.diffuse_color=(*col,1);a.use_nodes=True;a.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*col,1);a.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.9;return a
wall=plain('PreviewWarmPlaster',(.47,.32,.20));floor=plain('PreviewFloor',(.16,.10,.065))
def box(name,loc,dim,material):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);ob=bpy.context.object;ob.name=name;ob.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);ob.data.materials.append(material)
box('PreviewSolidCorner',(.5,.5,.6),(1,1,1.2),wall)
box('PreviewFloor',(.6,.35,-.025),(2.4,2.2,.05),floor)
def aim(ob,target):ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(2.5,-1.5,1.25));cam=bpy.context.object;aim(cam,(.90,.10,.6));cam.data.type='ORTHO';cam.data.ortho_scale=1.6;scene.camera=cam
for loc,power,size in [((2,-3,3),220,2),((3,2,2),160,2)]:
 bpy.ops.object.light_add(type='AREA',location=loc);ob=bpy.context.object;ob.data.energy=power;ob.data.size=size;aim(ob,(1,0,.6))
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=20;scene.cycles.use_denoising=True
scene.render.threads_mode='FIXED';scene.render.threads=2
scene.render.resolution_x=640;scene.render.resolution_y=640;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.world.color=(.17,.17,.17)
scene.view_settings.view_transform='AgX'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'model/ARC-TRIM-02.blend'))
for name,target,loc,scale in [('outside-junction',(.9,.1,.6),(2.5,-1.5,1.25),1.6),('baseboard-outside-close',(1,0,.075),(1.55,-.55,.38),.30),('crown-outside-close',(1,0,1.15),(1.55,-.55,1.37),.30)]:
 cam.location=loc;aim(cam,target);cam.data.ortho_scale=scale;scene.render.filepath=str(ROOT/'previews'/f'{name}.png');bpy.ops.render.render(write_still=True)
(ROOT/'profiles.json').write_text(json.dumps({'source':'ARC-TRIM-01/model/build_trim.py','source_sha256':hashlib.sha256((OLD/'model/build_trim.py').read_bytes()).hexdigest(),'profiles_m':PROFILES,'outside_end_plane':'x+y=1','outside_start_plane':'x-y=0','unchanged_uv_formula':'u=x, v=(z+y)*2.5'},indent=2)+'\n')
