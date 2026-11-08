"""LV-COFFEE-01: metric floor-origin vintage table, Blender background build."""
import bpy, math, os
from mathutils import Vector
from pathlib import Path
HERE=Path(__file__).resolve().parent.parent
MODELS=HERE/'model'; PREV=HERE/'previews'; TEX=HERE/'textures'
for p in (MODELS,PREV): p.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def texture(name, path):
 m=bpy.data.materials.new(name); m.diffuse_color=(.55,.32,.13,1); m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Roughness'].default_value=.8
 n=m.node_tree.nodes.new('ShaderNodeTexImage'); n.image=bpy.data.images.load(str(path),check_existing=True); n.image.pack(); m.node_tree.links.new(n.outputs['Color'],bs.inputs['Base Color']); return m
wood=texture('Table_Wood_Painted',TEX/'walnut-candidate-b.png'); sage=texture('Table_Sage_Painted',TEX/'walnut-candidate-b.png')

def meshobj(name,verts,faces,mat,uvkind='xy'):
 m=bpy.data.meshes.new(name); m.from_pydata(verts,[],faces); m.update(); o=bpy.data.objects.new(name,m); bpy.context.collection.objects.link(o); m.materials.append(mat)
 uv=m.uv_layers.new(name='UVMap')
 for p in m.polygons:
  for li in p.loop_indices:
   v=m.vertices[m.loops[li].vertex_index].co
   uv.data[li].uv=((v.x+1.5)/3.0,(v.y+.85)/1.7) if uvkind=='xy' else ((v.x+.75)/1.5,(v.z+.1)/.9)
 return o

def ring(rx,ry,r,z):
 pts=[]
 for cx,cy,start in [(rx-r,ry-r,0),(-rx+r,ry-r,90),(-rx+r,-ry+r,180),(rx-r,-ry+r,270)]:
  for i in range(9):
   a=math.radians(start+i*90/8); pts.append((cx+r*math.cos(a),cy+r*math.sin(a),z))
 return pts
# Four concentric profiles create a rounded horizontal rim without invalid bevels.
profiles=[(.733,.408,.10,.690),(.750,.425,.11,.702),(.750,.425,.11,.728),(.738,.413,.10,.740)]
rings=[ring(*p) for p in profiles]; n=len(rings[0]); verts=[v for r in rings for v in r]; faces=[]
for k in range(len(rings)-1):
 for i in range(n):
  j=(i+1)%n; faces.append((k*n+i,k*n+j,(k+1)*n+j,(k+1)*n+i))
# triangle fans; use distinct centers for top/bottom
verts.extend([(0,0,.690),(0,0,.740)]); bottom=len(verts)-2; top=bottom+1
for i in range(n):
 j=(i+1)%n; faces.append((bottom,j,i)); faces.append((top,3*n+i,3*n+j))
tabletop=meshobj('Rounded tabletop',verts,faces,wood)
# Unwrap the rim as a continuous strip rather than projecting the horizontal top.
# The seam is at the back-right corner; each profile uses the same perimeter U.
uv=tabletop.data.uv_layers.active.data
perimeter=[0.0]
for i in range(n):
 a=Vector(rings[1][i]); b=Vector(rings[1][(i+1)%n]); perimeter.append(perimeter[-1]+(b-a).length)
for k in range(3):
 for i in range(n):
  poly=tabletop.data.polygons[k*n+i]; u0=perimeter[i]/perimeter[-1]; u1=perimeter[i+1]/perimeter[-1]
  v0=.24+k*.12; v1=.24+(k+1)*.12
  for li,coord in zip(poly.loop_indices,[(u0,v0),(u1,v0),(u1,v1),(u0,v1)]): uv[li].uv=coord


def box(name,loc,dims,mat,bevel=.004):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  mod=o.modifiers.new('Small edge rounding','BEVEL');mod.width=bevel;mod.segments=2;mod.limit_method='ANGLE';bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 o.data.materials.append(mat);return o
# Genuine four-sided apron leaves an open underside; no solid block underneath.
for y in (-.327,.327): box('Walnut long apron',(0,y,.645),(1.28,.035,.09),sage)
for x in (-.622,.622): box('Walnut end apron',(x,0,.645),(.035,.62,.09),sage)
# Individually splayed tapered legs meet apron corners; feet remain inside footprint.
for sx in (-1,1):
 for sy in (-1,1):
  a=Vector((sx*.696,sy*.372,.015)); b=Vector((sx*.603,sy*.285,.651)); d=b-a
  bpy.ops.mesh.primitive_cone_add(vertices=20,radius1=.025,radius2=.046,depth=d.length,location=(a+b)/2);o=bpy.context.object;o.name='Tapered timber leg';o.rotation_euler=d.to_track_quat('Z','Y').to_euler();o.data.materials.append(wood)
  # Smooth sides only, retain flat ends.
  for p in o.data.polygons: p.use_smooth=len(p.vertices)==4
# Localized hand-painted edge-wear marks lie flush on the top, with no raised paint.
# They use a muted honey color and irregular silhouettes; less than 1 mm offset avoids z-fighting.
wear=bpy.data.materials.new('Table_Edge_Wear'); wear.diffuse_color=(.52,.27,.09,1); wear.use_nodes=True
wear.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.52,.27,.09,1)
wear.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.9
for sx,sy,length in [(-.48,-.399,.068),(-.21,-.397,.041),(.18,-.398,.055),(.47,-.398,.032),(-.51,.399,.045),(.33,.399,.060)]:
 z=.7402; h=.0035 if sy>0 else -.0035
 meshobj('Painted edge scuff',[(sx,sy,z),(sx+length,sy,z),(sx+length*.77,sy+h,z),(sx+length*.20,sy+h*1.6,z)],[(0,1,2),(0,2,3)],wear)
# small corner join blocks and fasteners, visible from under table
for x in (-.56,.56):
 for y in (-.27,.27): box('Underside corner block',(x,y,.654),(.12,.10,.055),wood,.003)
# Low fitted shelf ties the four legs; fabricated before the dimensional scale below.
box('Lower shelf',(0,0,.32),(1.20,.57,.04),wood,.012)
for x in (-.605,.605): box('Shelf end support',(x,0,.275),(.18,.57,.05),wood,.005)
# Scale the validated dining-table base to the coffee-table design size (1.20 x .60 x .46 m).
for ob in list(bpy.context.scene.objects):
 if ob.type == 'MESH':
  ob.location.x *= .8; ob.location.y *= .6/.85; ob.location.z *= .62
  ob.scale.x *= .8; ob.scale.y *= .6/.85; ob.scale.z *= .62

# Select geometry and bake world-relative transforms on export, preserving floor origin.
models=list(bpy.context.scene.objects)
bpy.ops.object.select_all(action='DESELECT')
for o in models:o.select_set(True)
bpy.context.view_layer.objects.active=models[0]
bpy.ops.object.join(); table=bpy.context.object; table.name='LV_COFFEE_01'; bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
bpy.ops.export_scene.fbx(filepath=str(MODELS/'LV_COFFEE_01.fbx'),use_selection=True,object_types={'MESH'},add_leaf_bones=False,apply_unit_scale=True,path_mode='AUTO')
# Lighting for reviews; backdrop is a studio world, not exported.
scene=bpy.context.scene; scene.render.engine='CYCLES';scene.cycles.samples=32;scene.render.resolution_x=1200;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.world.color=(.16,.14,.12); scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=True
bpy.ops.object.light_add(type='AREA',location=(2,-4,5)); l=bpy.context.object;l.data.energy=550;l.data.color=(1.0,.88,.75);l.data.shape='DISK';l.data.size=5
bpy.ops.object.light_add(type='AREA',location=(-3,2,3));l=bpy.context.object;l.data.energy=200;l.data.color=(1,.82,.65);l.data.size=4
bpy.ops.object.camera_add(location=(2.55,-3.65,2.45));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.23))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=1.8;scene.camera=cam
scene.render.filepath=str(PREV/'coffee-three-quarter.png');bpy.ops.render.render(write_still=True)
cam.location=(0,-4,1.2);cam.rotation_euler=(Vector((0,0,.23))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.6;scene.render.filepath=str(PREV/'coffee-front.png');bpy.ops.render.render(write_still=True)
# Review from each axis and below to expose apron and leg joins.
for name, loc, target, scale in [
 ('coffee-back.png',(0,4,1.2),(0,0,.23),1.95),
 ('coffee-left.png',(-4,0,1.2),(0,0,.23),1.45),
 ('coffee-right.png',(4,0,1.2),(0,0,.23),1.45),
 ('coffee-underside.png',(2,-3,-1.7),(0,0,.32),2.20)]:
 cam.location=loc; cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.ortho_scale=scale; scene.render.filepath=str(PREV/name); bpy.ops.render.render(write_still=True)
# Save complete editable source including packed maps and lights.
bpy.ops.wm.save_as_mainfile(filepath=str(MODELS/'LV-COFFEE-01.blend'))
print('TABLE COMPLETE',tuple(round(x,4) for x in table.dimensions))
