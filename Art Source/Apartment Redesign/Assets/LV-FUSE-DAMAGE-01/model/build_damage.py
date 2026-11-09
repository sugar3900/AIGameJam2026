"""Build separate opaque, shallow fusebox plaster damage; metres, Z up, -Y toward room."""
import bpy, math, random
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1]
FUSE=P.parent/'LV-FUSE-01'/'exports'
for folder in ('model','previews'): (P/folder).mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
random.seed(8127)
def mat(name,col,rough=0.95):
 m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=rough
 return m
wall=mat('Preview wall',(0.55,0.43,0.32));plaster_edge=mat('Exposed plaster ochre',(.42,.31,.215));plaster_core=mat('Exposed plaster midtone',(.29,.20,.13));plaster_high=mat('Chipped light edge',(.51,.40,.30)); crack_dark=mat('Crevice brown',(.21,.145,.095)); crack_inner=mat('Hairline brown',(.31,.22,.15)); paint=mat('Preview green metal',(.25,.30,.25))
def mesh_object(name,verts,faces,material):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);me.materials.append(material)
 uv=me.uv_layers.new(name='UVMap')
 for poly in me.polygons:
  for i in poly.loop_indices:
   co=me.vertices[me.loops[i].vertex_index].co;uv.data[i].uv=((co.x+.6)/1.2,(co.z+.30)/1.4)
 return ob
parts=[]
age_ochre=mat('Age worn ochre',(.48,.375,.27))
age_grey=mat('Age worn grey',(.47,.39,.31))
def age_speckles():
 # Small, nonrectangular and non-repeating muted scuffs sit behind the cracks.
 rng=random.Random(91239)
 clusters=[(-.264,.61,.065,.075),(.271,.605,.064,.065),(-.275,-.02,.060,.075)]
 for c,(cx,cz,rx,rz) in enumerate(clusters):
  for i in range(24):
   x=cx+rng.gauss(0,rx*.45); z=cz+rng.gauss(0,rz*.40)
   if -.20<x<.20 and .02<z<.55: continue
   sx=rng.uniform(.002,.012); sz=rng.uniform(.001,.006);n=7;pts=[]
   for j in range(n):
    a=2*math.pi*j/n;scale=rng.uniform(.52,1.0)
    pts.append((x+sx*scale*math.cos(a),-.00065,z+sz*scale*math.sin(a)))
   parts.append(mesh_object('Faded uneven plaster scuff',[(x,-.00065,z)]+pts,[(0,1+j,1+(j+1)%n) for j in range(n)],age_ochre if i%3 else age_grey))
age_speckles()
def chip(name,center,radii,seed):
 rng=random.Random(seed);cx,cz=center;rx,rz=radii;rx*=.72;rz*=.72;n=15
 pts=[]
 for i in range(n):
  a=2*math.pi*i/n;k=rng.uniform(.45,1.08);pts.append((cx+rx*k*math.cos(a),-.0012,cz+rz*k*math.sin(a)))
 # fan in same plane, lighter underlay plus small darker center; no full rectangle or alpha texture
 ob=mesh_object(name,[(cx,-.0012,cz)]+pts,[(0,1+i,1+(i+1)%n) for i in range(n)],plaster_edge);parts.append(ob)
 pts2=[(cx+(x-cx)*.72,-.002,cz+(z-cz)*.72) for x,_,z in pts]
 ob=mesh_object(name+' shallow center',[(cx,-.002,cz)]+pts2,[(0,1+i,1+(i+1)%n) for i in range(n)],plaster_core);parts.append(ob)
 # isolated, narrow brighter broken plaster facets
 for a,b in [(0,1),(4,5),(7,8)]:
  x1,_,z1=pts[a];x2,_,z2=pts[b]
  verts=[(x1,-.0026,z1),(x2,-.0026,z2),(cx+(x2-cx)*.80,-.0026,cz+(z2-cz)*.80),(cx+(x1-cx)*.80,-.0026,cz+(z1-cz)*.80)]
  parts.append(mesh_object(name+' edge chip',verts,[(0,1,2,3)],plaster_high))
def fracture(name,points,width,material=crack_dark):
 rng=random.Random(name)
 detailed=[]
 for i in range(len(points)-1):
  a=Vector(points[i]);b=Vector(points[i+1]);delta=b-a;direction=delta.normalized();normal=Vector((-direction.y,direction.x))
  detailed.append(tuple(a))
  for f in (.25,.5,.75):
   bend=rng.uniform(-.0015,.0015);q=a.lerp(b,f)+normal*bend;detailed.append(tuple(q))
 detailed.append(points[-1]);points=detailed
 verts=[];n=len(points)
 for i,(x,z) in enumerate(points):
  a=Vector(points[max(i-1,0)]);b=Vector(points[min(i+1,n-1)]); tangent=(b-a).normalized();normal=Vector((-tangent.y,tangent.x))
  w=width*(1-i/(n-0.3))+.00022
  verts.extend([(x+normal.x*w/2,-.0032,z+normal.y*w/2),(x-normal.x*w/2,-.0032,z-normal.y*w/2)])
 parts.append(mesh_object(name,verts,[(2*i,2*i+1,2*i+3,2*i+2) for i in range(n-1)],material))
# Fuse lower edge Z=0, side edges +/-0.225 and top Z=.58. Keep marks behind body and project outward.
chip('Upper left flake',(-.229,.581),(.052,.050),12)
chip('Upper right flake',(.232,.573),(.048,.043),18)
chip('Lower left flake',(-.23,-.015),(.042,.038),25)
fracture('Upper left main',[(-.238,.608),(-.266,.633),(-.276,.670),(-.315,.688),(-.326,.733),(-.357,.753),(-.372,.790),(-.405,.810)],.0034)
fracture('Upper left branch',[(-.316,.688),(-.348,.701),(-.362,.723),(-.389,.728)],.0020,crack_inner)
fracture('Upper right main',[(.248,.602),(.276,.624),(.290,.650),(.321,.662),(.339,.695),(.375,.710),(.396,.737)],.0030)
fracture('Upper right branch',[(.322,.662),(.345,.652),(.370,.659),(.388,.650)],.0018,crack_inner)
fracture('Lower left main',[(-.249,-.029),(-.266,-.050),(-.302,-.063),(-.315,-.096),(-.350,-.112),(-.361,-.145),(-.390,-.163)],.0034)
fracture('Lower left branch',[(-.317,-.096),(-.350,-.091),(-.371,-.103)],.0018,crack_inner)
fracture('Lower right main',[(.244,-.009),(.269,-.027),(.280,-.058),(.309,-.067),(.320,-.097)],.0020,crack_inner)
# Join selectable damage group into one mesh, triangulate deterministically, and preserve UV layers.
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();damage=bpy.context.object;damage.name='LV_Fuse_Plaster_Damage';damage.visible_shadow=False
bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
mod=damage.modifiers.new('Triangulate','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.object.select_all(action='DESELECT');damage.select_set(True);bpy.context.view_layer.objects.active=damage
bpy.ops.export_scene.fbx(filepath=str(P/'model'/'LV_Fuse_Plaster_Damage.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,add_leaf_bones=False)
# Non-exported preview: load original fusebox and fit against wall. Scene is saved for inspection.
bpy.ops.import_scene.fbx(filepath=str(FUSE/'LV_FUSE_01_Shell.fbx'))
bpy.ops.import_scene.fbx(filepath=str(FUSE/'LV_FUSE_01_Door.fbx'))
for ob in list(bpy.context.selected_objects): pass
# FBX nodes may refer to local files; reconnect known diffuse texture by material name if necessary.
for m in bpy.data.materials:
 if 'Painted_Olive' in m.name:
  m.diffuse_color=(.27,.32,.26,1)
  if m.use_nodes:
   bs=m.node_tree.nodes.get('Principled BSDF')
   if bs and not bs.inputs['Base Color'].is_linked:bs.inputs['Base Color'].default_value=(.27,.32,.26,1)
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,.045,.30));w=bpy.context.object;w.name='PREVIEW ONLY wall';w.dimensions=(1.4,.09,1.6);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);w.data.materials.append(wall)
world=bpy.context.scene.world;world.color=(.18,.18,.18)
def area(loc,power,size):
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,.28))-o.location).to_track_quat('-Z','Y').to_euler()
area((-.8,-2,2),125,2.5);area((1,-1,.5),45,2)
bpy.ops.object.camera_add(location=(.85,-2.8,1.0));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.30))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=1.25;bpy.context.scene.camera=cam
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=24;sc.render.resolution_x=1000;sc.render.resolution_y=1000;sc.render.resolution_percentage=100;sc.view_settings.view_transform='AgX';sc.render.image_settings.file_format='PNG';sc.render.film_transparent=False
sc.render.filepath=str(P/'previews'/'fuse-damaged.png');bpy.ops.render.render(write_still=True)
damage.hide_render=True;sc.render.filepath=str(P/'previews'/'fuse-repaired.png');bpy.ops.render.render(write_still=True);damage.hide_render=False
bpy.ops.wm.save_as_mainfile(filepath=str(P/'model'/'LV-FUSE-DAMAGE-01.blend'))
