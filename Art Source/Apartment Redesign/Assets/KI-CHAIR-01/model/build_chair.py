import bpy, math, os
from mathutils import Vector
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def mat(name, color, texture=None, rough=.65):
 m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=rough
 if texture and (ROOT/'textures'/texture).exists():
  im=m.node_tree.nodes.new('ShaderNodeTexImage'); im.image=bpy.data.images.load(str(ROOT/'textures'/texture)); im.image.filepath='//../textures/'+texture; m.node_tree.links.new(im.outputs['Color'],bs.inputs['Base Color'])
 return m
wood=mat('Chair_Walnut',(.32,.12,.045),'wood-selected-v2.png'); vinyl=mat('Chair_Rust_Vinyl',(.45,.11,.065),'vinyl.png'); piping=mat('Chair_Piping',(.25,.075,.035))

def uv(o):
 bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active=o
 if o.type=='MESH':
  if not o.data.uv_layers: o.data.uv_layers.new(name='UVMap')
  bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.uv.smart_project(island_margin=.02); bpy.ops.object.mode_set(mode='OBJECT')
 return o


def wood_uv(o,axis):
 # Align texture U with length of each piece, not the circumference. This
 # keeps the painterly grain horizontal on rails and vertical on uprights.
 mesh=o.data
 if not mesh.uv_layers: mesh.uv_layers.new(name='UVMap')
 layer=mesh.uv_layers.active.data
 coords=[v.co for v in mesh.vertices]; lo=min(v[axis] for v in coords); hi=max(v[axis] for v in coords); span=max(hi-lo,1e-6)
 cross=[i for i in range(3) if i != axis]; vals=[v[cross[0]]+v[cross[1]] for v in coords]; vlo=min(vals); vspan=max(max(vals)-vlo,1e-6)
 for loop in mesh.loops:
  q=mesh.vertices[loop.vertex_index].co
  layer[loop.index].uv=(.08+.84*(q[axis]-lo)/span,.08+.84*((q[cross[0]]+q[cross[1]])-vlo)/vspan)
 return o

def rounded(name,loc,dims,material,bevel):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=dims; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 b=o.modifiers.new('Rounded edges','BEVEL'); b.width=bevel; b.segments=4; b.affect='EDGES'; b.limit_method='ANGLE'
 bpy.context.view_layer.objects.active=o; bpy.ops.object.modifier_apply(modifier=b.name); o.data.materials.append(material); uv(o); return o

def curved(name,points,radius,material):
 cu=bpy.data.curves.new(name,'CURVE'); cu.dimensions='3D'; cu.resolution_u=16; cu.bevel_depth=radius; cu.bevel_resolution=4
 sp=cu.splines.new('BEZIER'); sp.bezier_points.add(len(points)-1)
 for bp,co in zip(sp.bezier_points,points): bp.co=co; bp.handle_left_type='AUTO'; bp.handle_right_type='AUTO'
 o=bpy.data.objects.new(name,cu); bpy.context.collection.objects.link(o); bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active=o; bpy.ops.object.convert(target='MESH'); o.data.materials.append(material); uv(o);
 if name=='Back upright': wood_uv(o,2)
 return o

def bar(name,a,b,r,material):
 a,b=Vector(a),Vector(b); d=b-a; bpy.ops.mesh.primitive_cone_add(vertices=20,radius1=r*.85,radius2=r,depth=d.length,location=(a+b)*.5); o=bpy.context.object; o.name=name; o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); o.data.materials.append(material); uv(o); wood_uv(o,2); return o
# Seat base and cushion: modest rounded bevels below half-thickness, no self-intersection.
rounded('Seat timber frame',(0,0,.418),(.44,.43,.055),wood,.012)
rounded('Soft vinyl cushion',(0,-.005,.462),(.46,.45,.075),vinyl,.032)
# piping along top seat perimeter, a shallow seam rather than stand-off bars
for y in (-.212,.202): curved('Cushion seam', [(-.19,y,.452),(0,y,.448),(.19,y,.452)],.0025,piping)
for x in (-.215,.215): curved('Cushion seam', [(x,-.18,.452),(x,0,.448),(x,.17,.452)],.0025,piping)
# Slight splay of front legs, gently curved rear uprights continue into back posts
for x in (-1,1):
 bar('Front tapered leg',(x*.205,-.22,.015),(x*.18,-.18,.415),.021,wood)
 curved('Back upright',[(x*.205,.24,.015),(x*.19,.19,.41),(x*.19,.205,.64),(x*.205,.255,.89)],.020,wood)
# low stretchers between legs
bar('Front stretcher',(-.18,-.21,.18),(.18,-.21,.18),.011,wood)
bar('Rear stretcher',(-.18,.205,.19),(.18,.205,.19),.011,wood)
for x in (-.185,.185): bar('Side stretcher',(x,-.20,.20),(x,.20,.20),.011,wood)
# Curved ladder slats: surfaces are curved in depth for a comfortable back.
def slat(name,z,width,height):
 n=16; verts=[]; faces=[]
 for yy in (-.012,.012):
  for zz in (-height/2,height/2):
   for i in range(n+1):
    x=width*(i/n-.5); y=.205 + .052*((z-.5)/.39) - .023*(1-(2*x/width)**2)+yy
    verts.append((x,y,z+zz))
 row=n+1
 for side in range(2):
  start=side*2*row
  for i in range(n): faces.append((start+i,start+i+1,start+row+i+1,start+row+i) if side==0 else (start+i+1,start+i,start+row+i,start+row+i+1))
 for i in range(n):
  faces.append((i,2*row+i,2*row+i+1,i+1)); faces.append((row+i+1,3*row+i+1,3*row+i,row+i))
 faces.extend([(0,row,3*row,2*row),(n,2*row+n,3*row+n,row+n)])
 mesh=bpy.data.meshes.new(name); mesh.from_pydata(verts,[],faces); mesh.update(); o=bpy.data.objects.new(name,mesh); bpy.context.collection.objects.link(o); o.data.materials.append(wood)
 mod=o.modifiers.new('Soft edges','BEVEL'); mod.width=.004; mod.segments=3; bpy.context.view_layer.objects.active=o; bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.ops.object.modifier_apply(modifier=mod.name); uv(o); wood_uv(o,0); return o
slat('Upper broad back slat',.835,.37,.105); slat('Middle back slat',.715,.37,.065); slat('Lower back slat',.615,.37,.065)
for sign in (-1,1):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=10,radius=.020,location=(sign*.205,.255,.89)); cap=bpy.context.object; cap.name='Rounded post cap'; cap.data.materials.append(wood); uv(cap); wood_uv(cap,2)
 for z in (.615,.715,.835):
  y=.205+.052*((z-.5)/.39)-.023*(1-(2*(sign*.17)/.37)**2)-.013
  bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=.004,depth=.002,location=(sign*.17,y,z),rotation=(math.pi/2,0,0)); peg=bpy.context.object; peg.name='Recessed slat peg'; peg.data.materials.append(piping); uv(peg)

# Export all meshes as a single cohesive static asset, with floor origin and UV/material slots.
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']; bpy.ops.object.select_all(action='DESELECT')
for o in meshes: o.select_set(True)
bpy.context.view_layer.objects.active=meshes[0]; bpy.ops.object.join(); obj=bpy.context.object; obj.name='KI_CHAIR_01'
bpy.context.scene.cursor.location=(0,0,0); bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
for face in obj.data.polygons: face.use_smooth=True
weighted=obj.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL'); weighted.keep_sharp=True; weighted.weight=50
bpy.context.view_layer.objects.active=obj; bpy.ops.object.modifier_apply(modifier=weighted.name)
bpy.ops.export_scene.fbx(filepath=str(ROOT/'model/KI_CHAIR_01.fbx'),use_selection=True,object_types={'MESH'},add_leaf_bones=False,apply_unit_scale=True)
# Render with neutral warm studio light, preserving exported origin.
scene=bpy.context.scene; scene.render.engine='CYCLES'; scene.cycles.samples=32; scene.render.resolution_x=1100; scene.render.resolution_y=1100; scene.render.resolution_percentage=100; scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=True
scene.world.color=(.22,.20,.18)
def aim(o,p): o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.light_add(type='AREA',location=(2,-3,4)); light=bpy.context.object; light.data.energy=430; light.data.shape='DISK'; light.data.size=4; aim(light,(0,0,.45))
bpy.ops.object.light_add(type='AREA',location=(-2,-1,2)); light=bpy.context.object; light.data.energy=150; light.data.color=(1,.75,.53); light.data.size=3; aim(light,(0,0,.45))
bpy.ops.object.camera_add(location=(1.6,-2.6,1.45)); cam=bpy.context.object; cam.data.type='ORTHO'; cam.data.ortho_scale=1.35; aim(cam,(0,0,.46)); scene.camera=cam
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'model/KI-CHAIR-01.blend'))
scene.render.filepath=str(ROOT/'previews/chair-three-quarter.png'); bpy.ops.render.render(write_still=True)
for label,loc in [('front',(0,-3,.46)),('back',(0,3,.46)),('left',(-3,0,.46)),('right',(3,0,.46))]:
 cam.location=loc; aim(cam,(0,0,.46)); scene.render.filepath=str(ROOT/('previews/chair-'+label+'.png')); bpy.ops.render.render(write_still=True)
print('CHAIR_DONE bounds',tuple(round(x,4) for x in obj.dimensions))
