"""Build BA-BASIN-01; metres, Z up, basin front -Y. Blender 5.2."""
import bpy, math, os
from mathutils import Vector
P=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for m in list(bpy.data.materials): bpy.data.materials.remove(m)

def material(name,color,rough=.6,metal=0,image=None):
 m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal
 if image and os.path.isfile(image):
  tex=m.node_tree.nodes.new('ShaderNodeTexImage'); tex.image=bpy.data.images.load(image,check_existing=True)
  m.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color'])
 return m
ivory=material('Painted_Ivory_Enamel',(.78,.66,.51),.4,image=os.path.join(P,'textures','ivory-enamel-v2.png'))
chrome=material('Aged_Chrome',(.42,.39,.34),.31,.7); dark=material('Drain_Holes',(.07,.057,.043),.7)

def mesh(name, verts, faces, mat):
 me=bpy.data.meshes.new(name); me.from_pydata(verts,[],faces); me.update(); o=bpy.data.objects.new(name,me); bpy.context.collection.objects.link(o); me.materials.append(mat)
 bpy.context.view_layer.objects.active=o; o.select_set(True)
 bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.uv.smart_project(island_margin=.02); bpy.ops.object.mode_set(mode='OBJECT'); o.select_set(False)
 for poly in me.polygons: poly.use_smooth=True
 return o

def rings_mesh(name,rings,mat,n=64,rounded=False,caps=True):
 verts=[]
 for rx,ry,z in rings:
  for i in range(n):
   t=2*math.pi*i/n + math.pi/2; c,s=math.cos(t),math.sin(t)
   if rounded: c=math.copysign(abs(c)**.45,c); s=math.copysign(abs(s)**.45,s)
   verts.append((rx*c,ry*s,z))
 faces=[]
 for j in range(len(rings)-1):
  for i in range(n): a=j*n+i;b=j*n+(i+1)%n;faces.append((a,b,b+n,a+n))
 if caps:
  faces.append(tuple(reversed(range(n))));faces.append(tuple((len(rings)-1)*n+i for i in range(n)))
 o=mesh(name,verts,faces,mat)
 # Continuous ring unwrap places the unavoidable seam at the rear (+Y).
 uv=o.data.uv_layers.active.data
 for k,poly in enumerate(o.data.polygons[:(len(rings)-1)*n]):
  j,i=divmod(k,n); coords=[(i/n,j/(len(rings)-1)),((i+1)/n,j/(len(rings)-1)),((i+1)/n,(j+1)/(len(rings)-1)),(i/n,(j+1)/(len(rings)-1))]
  for li,co in zip(poly.loop_indices,coords): uv[li].uv=co
 return o

def box(name,loc,dims,mat,bevel=.01):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dims; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); mod=o.modifiers.new('edge softness','BEVEL');mod.width=bevel;mod.segments=3;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name);o.data.materials.append(mat);return o

def cyl(name,loc,radius,depth,mat,vertices=32):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=loc);o=bpy.context.object;o.name=name;o.data.materials.append(mat)
 for p in o.data.polygons:p.use_smooth=True
 return o

def sphere(name,loc,scale,mat):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,location=loc);o=bpy.context.object;o.name=name;o.scale=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat)
 for p in o.data.polygons:p.use_smooth=True
 return o

def tube(name,points,radius,mat):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=18;cu.bevel_depth=radius;cu.bevel_resolution=4
 sp=cu.splines.new('BEZIER');sp.bezier_points.add(len(points)-1)
 for bp,co in zip(sp.bezier_points,points):bp.co=co;bp.handle_left_type='AUTO';bp.handle_right_type='AUTO'
 o=bpy.data.objects.new(name,cu);bpy.context.collection.objects.link(o);o.data.materials.append(mat); bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False);return o

# Heavy integral basin with genuinely hollow curved inside and rolled rim.
body=[]
body.append(rings_mesh('Porcelain hollow basin',[(.22,.18,.635),(.29,.245,.69),(.32,.28,.78),(.32,.28,.84),(.305,.265,.86),(.27,.23,.858),(.255,.215,.84),(.24,.2,.79),(.20,.16,.73),(.13,.10,.70),(.045,.045,.695)],ivory,rounded=True))
# Rolled ceramic lip and a shallow, flat-backed integral splash guard.
body.append(rings_mesh('Rolled enamel lip',[(.302,.261,.842),(.317,.276,.852),(.318,.277,.862),(.307,.266,.871),(.28,.238,.872),(.266,.222,.862),(.263,.219,.848)],ivory,rounded=True,caps=False))
body.append(box('Integral back splash', (0,.246,.885),(.57,.045,.08),ivory,.012))
# ring-profile pedestal includes spreading base and crown supporting bowl
body.append(rings_mesh('Pedestal',[(.13,.13,.01),(.152,.152,.02),(.152,.152,.045),(.14,.14,.055),(.14,.14,.068),(.125,.125,.078),(.105,.105,.105),(.092,.092,.52),(.102,.102,.57),(.12,.12,.59),(.12,.12,.605),(.145,.145,.62),(.16,.16,.635),(.16,.16,.65)],ivory))
body.append(cyl('Drain rim',(0,-.045,.705),.037,.006,chrome))
# Three small recessed overflow slots on the inside of the back wall.
for x in [-.018,0,.018]: body.append(sphere('Overflow slot',(x,.194,.808),(.005,.002,.013),dark))
for x,y in [(0,0),(-.014,0),(.014,0),(0,-.014),(0,.014)]:body.append(cyl('Drain aperture',(x,-.045+y,.71),.0045,.002,dark,16))
# two fitted spouts; cross handles are separate for runtime rotation
handles=[]
for side,x in [('L',-.18),('R',.18)]:
 y=.185;body.append(cyl(side+' tap foot',(x,y,.862),.034,.014,chrome));body.append(cyl(side+' valve stem',(x,y,.886),.020,.04,chrome));
 body.append(tube(side+' curved spout',[(x,y-.006,.891),(x,y-.05,.891),(x,y-.104,.881),(x,y-.125,.856)],.012,chrome))
 body.append(cyl(side+' spout end',(x,y-.125,.855),.013,.008,chrome))
 h=[];h.append(cyl(side+' handle hub',(x,y,.922),.013,.025,chrome))
 for dx,dy in [(.025,0),(-.025,0),(0,.025),(0,-.025)]:
  h.append(tube(side+' handle arm',[(x,y,.93),(x+dx,y+dy,.93)],.006,chrome));h.append(sphere(side+' handle ball',(x+dx,y+dy,.93),(.009,.009,.009),chrome))
 handles.append((side,h,(x,y,.922)))

def combine(name,objs,origin):
 bpy.ops.object.select_all(action='DESELECT')
 for o in objs:o.select_set(True)
 bpy.context.view_layer.objects.active=objs[0];bpy.ops.object.join();o=bpy.context.object;o.name=name
 bpy.context.scene.cursor.location=origin;bpy.ops.object.origin_set(type='ORIGIN_CURSOR');return o
base=combine('BA_BasinBody',body,(0,0,0)); parts=[base]
for side,objs,origin in handles:parts.append(combine('BA_BasinTap_'+side,objs,origin))
# Export each part with pivot retained at FBX origin; don't mutate assembled scene.
for obj in parts:
 bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
 bpy.ops.export_scene.fbx(filepath=os.path.join(P,'model',obj.name+'.fbx'),use_selection=True,object_types={'MESH'},add_leaf_bones=False,apply_unit_scale=True,bake_space_transform=False)
# preview setup
world=bpy.context.scene.world;world.color=(.23,.18,.14)
bpy.ops.object.camera_add(location=(1.8,-2.6,1.65));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.48))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=1.4;bpy.context.scene.camera=cam
for loc,energy,size in [((1,-2,2.6),180,3),((-1,-.5,1.8),85,2)]:
 bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.data.energy=energy;l.data.shape='DISK';l.data.size=size;l.rotation_euler=(Vector((0,0,.5))-l.location).to_track_quat('-Z','Y').to_euler()
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=32;s.render.resolution_x=1100;s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.film_transparent=True
s.view_settings.view_transform='AgX';s.render.filepath=os.path.join(P,'previews','basin-three-quarter.png');bpy.ops.wm.save_as_mainfile(filepath=os.path.join(P,'model','BA-BASIN-01.blend'));bpy.ops.render.render(write_still=True)
cam.location=(1.5,-2.1,3.0);cam.rotation_euler=(Vector((0,0,.55))-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=os.path.join(P,'previews','basin-overhead.png');bpy.ops.render.render(write_still=True)
