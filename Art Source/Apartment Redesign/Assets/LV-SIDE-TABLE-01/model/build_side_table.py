"""Living side table; metres, floor at z=0, drawer slides toward -Y."""
import bpy, math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent.parent;M=P/'model';T=P/'textures';O=P/'previews'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def mat(n,c,rough=.8,metal=0):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;s=m.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=(*c,1);s.inputs['Roughness'].default_value=rough;s.inputs['Metallic'].default_value=metal;return m
wood=mat('Aged painterly walnut',(.26,.11,.055),.83);s=wood.node_tree.nodes.get('Principled BSDF');t=wood.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(T/'walnut-muted-b.png'));t.image.pack();h=wood.node_tree.nodes.new('ShaderNodeHueSaturation');h.inputs['Saturation'].default_value=.68;h.inputs['Value'].default_value=1.35;wood.node_tree.links.new(t.outputs['Color'],h.inputs['Color']);wood.node_tree.links.new(h.outputs['Color'],s.inputs['Base Color'])
inside=mat('Drawer interior',(.38,.22,.12),.86); brass=mat('Aged brass',(.34,.22,.09),.6,.65); wear=mat('Fine worn wood edges',(.39,.27,.15),.93)
# Lightly unfinished interior retains wood grain without matching the dark exterior varnish.
it=inside.node_tree.nodes.new('ShaderNodeTexImage');it.image=t.image
blend=inside.node_tree.nodes.new('ShaderNodeMixRGB');blend.blend_type='MIX';blend.inputs[0].default_value=.40;blend.inputs[1].default_value=(.42,.26,.15,1)
inside.node_tree.links.new(it.outputs['Color'],blend.inputs[2]);inside.node_tree.links.new(blend.outputs[0],inside.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
def box(n,loc,dim,ma,bevel=.002):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=n;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  md=o.modifiers.new('Rounded edges','BEVEL');md.width=bevel;md.segments=3;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=md.name)
 o.data.materials.append(ma); uv=o.data.uv_layers.active or o.data.uv_layers.new(name='UVMap')
 for f in o.data.polygons:
  for li in f.loop_indices:
   v=o.data.vertices[o.data.loops[li].vertex_index].co;n=f.normal
   uv.data[li].uv=(v.x/.45+.5,v.y/.45+.5) if abs(n.z)>.7 else ((v.x/.45+.5,v.z/.45+.5) if abs(n.y)>.7 else (v.y/.45+.5,v.z/.45+.5))
 return o
def lathe(n,x,y):
 # Straight, gently tapered square legs, distinct from the bedroom turned profile.
 o=box(n,(x,y,.165),(.035,.035,.33),wood,.001)
 for v in o.data.vertices:
  t=max(0.0,min(1.0,(v.co.z+.165)/.33)); factor=.67+.33*t
  v.co.x*=factor;v.co.y*=factor
 return o
def cyl(n,loc,r,depth,ma,rot=(0,0,0)):
 bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=r,depth=depth,location=loc,rotation=rot);o=bpy.context.object;o.name=n;o.data.materials.append(ma);return o
def merge(name,parts):
 bpy.ops.object.select_all(action='DESELECT')
 for p in parts:p.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();o=bpy.context.object;o.name=name;bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');return o
body=[]
body.append(box('Overhanging top',(0,0,.501),(.45,.45,.038),wood,.006))
body.append(box('Molded top lip',(0,0,.478),(.435,.435,.010),wood,.003))
body.append(box('Lower shelf',(0,0,.092),(.36,.36,.022),wood,.003))
for x in (-.185,.185):
 for y in (-.185,.185):
  body.append(lathe('Turned leg',x,y));body.append(box('Upper square leg',(x,y,.397),(.045,.045,.16),wood,.003))
for x in (-.164,.164):body.append(box('Side panel',(x,0,.393),(.018,.332,.16),wood,.002))
body.append(box('Back panel',(0,.164,.393),(.31,.018,.16),wood,.002))
for z in (.316,.468):body.append(box('Front rail',(0,-.194,z),(.325,.028,.018),wood,.002))
# Front apron silhouette has gentle shaped curves like the selected period design.
# It sits just below the drawer rail, between the upper leg blocks.
def shaped_apron():
 xs=[-.162,-.13,-.09,-.055,0,.055,.09,.13,.162]
 bottom=[.278,.285,.292,.291,.283,.291,.292,.285,.278]
 y0,y1=-.208,-.185
 verts=[(x,y,z) for y in (y0,y1) for x,z in zip(xs,bottom)]
 verts += [(x,y,.311) for y in (y0,y1) for x in xs]
 n=len(xs);faces=[]
 for i in range(n-1):
  faces.extend([(i,i+1,2*n+i+1,2*n+i), (n+i,3*n+i,3*n+i+1,n+i+1), (i,n+i,n+i+1,i+1), (2*n+i,2*n+i+1,3*n+i+1,3*n+i)])
 faces += [(0,2*n,3*n,n),(n-1,2*n-1,4*n-1,3*n-1)]
 mesh=bpy.data.meshes.new('Shaped apron mesh');mesh.from_pydata(verts,[],faces);mesh.update();mesh.materials.append(wood)
 uv=mesh.uv_layers.new(name='UVMap')
 for face in mesh.polygons:
  for li in face.loop_indices:
   v=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=(v.x/.45+.5,v.z/.45+.1)
 o=bpy.data.objects.new('Shaped front apron',mesh);bpy.context.collection.objects.link(o);return o
body.append(shaped_apron())
# Fine edge rubs follow the front lip and high-touch leg corners.
for x,length in [(-.18,.025),(-.055,.018),(.17,.022)]: body.append(box('Top lip rubbed edge',(x,-.2254,.502),(length,.0008,.0018),wear,.0002))
for x,z in [(-.207,.364),(.207,.449)]: body.append(box('Leg corner rubbed edge',(x,-.208,.0+z),(.0015,.0008,.014),wear,.0002))
body=merge('LV_SIDE_TABLE_BODY',body)
d=[];d.append(box('Drawer front',(0,-.211,.393),(.319,.020,.13),wood,.003))
d.append(box('Bottom',(0,-.025,.334),(.28,.35,.012),inside,.001))
for x in (-.142,.142):d.append(box('Side',(x,-.025,.385),(.012,.35,.095),inside,.001))
d.append(box('Rear',(0,.145,.385),(.28,.012,.095),inside,.001))
d.append(cyl('Brass knob base',(0,-.226,.399),.011,.008,brass,(math.pi/2,0,0)))
bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,radius=1,location=(0,-.235,.399));o=bpy.context.object;o.name='Brass knob';o.scale=(.011,.009,.011);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(brass);d.append(o)
for x,length in [(-.12,.018),(.10,.024)]: d.append(box('Drawer edge rub',(x,-.2214,.454),(length,.0008,.0015),wear,.0002))
drawer=merge('LV_SIDE_TABLE_DRAWER',d)
for obj in (body,drawer):
 obj.scale=(.37/.45,.35/.45,.54/.52)
 bpy.context.view_layer.objects.active=obj
 bpy.ops.object.select_all(action='DESELECT');obj.select_set(True)
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
for obj in (body,drawer):
 bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj;bpy.ops.export_scene.fbx(filepath=str(M/(obj.name+'.fbx')),use_selection=True,object_types={'MESH'},add_leaf_bones=False,apply_unit_scale=True)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=True;scene.world.color=(.17,.15,.13)
bpy.ops.object.light_add(type='AREA',location=(2,-3,3));l=bpy.context.object;l.data.energy=260;l.data.size=4
bpy.ops.object.light_add(type='AREA',location=(-2,2,2));l=bpy.context.object;l.data.energy=100;l.data.size=3
bpy.ops.object.camera_add(location=(1.5,-2.3,1.4));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.25))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.78;scene.camera=cam
scene.render.filepath=str(O/'side-table-closed.png');bpy.ops.render.render(write_still=True)
drawer.location.y=-.18;scene.render.filepath=str(O/'side-table-open.png');bpy.ops.render.render(write_still=True);drawer.location.y=0
bpy.ops.wm.save_as_mainfile(filepath=str(M/'LV-SIDE-TABLE-01.blend'))
print('BODY BOUNDS',tuple(round(x,4) for x in body.dimensions))
