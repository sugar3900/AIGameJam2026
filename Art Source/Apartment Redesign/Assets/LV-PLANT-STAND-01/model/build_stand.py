"""Build the plant stand. Coordinates in metres, Z up, front -Y, floor origin."""
import bpy, math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent.parent
M=P/'model'; T=P/'textures'; O=P/'previews'
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
wood=bpy.data.materials.new('Muted aged walnut'); wood.diffuse_color=(.30,.18,.12,1);wood.use_nodes=True
bs=wood.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.86
tex=wood.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(T/'walnut-muted-b.png'));tex.image.pack()
h=wood.node_tree.nodes.new('ShaderNodeHueSaturation');h.inputs['Saturation'].default_value=.68;h.inputs['Value'].default_value=1.35
wood.node_tree.links.new(tex.outputs['Color'],h.inputs['Color']);wood.node_tree.links.new(h.outputs['Color'],bs.inputs['Base Color'])
wear=bpy.data.materials.new('Subtle edge wear');wear.diffuse_color=(.43,.29,.18,1);wear.use_nodes=True;wear.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.43,.29,.18,1);wear.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.95
parts=[]
def box(n,loc,dim,mat=wood,bevel=.002):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object;o.name=n;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  m=o.modifiers.new('soft edge','BEVEL');m.width=bevel;m.segments=3;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=m.name)
 o.data.materials.append(mat);uv=o.data.uv_layers.active or o.data.uv_layers.new(name='UVMap')
 for f in o.data.polygons:
  for li in f.loop_indices:
   v=o.data.vertices[o.data.loops[li].vertex_index].co; norm=f.normal
   uv.data[li].uv=(v.x/.45+.5,v.y/.35+.5) if abs(norm.z)>.7 else ((v.x/.45+.5,v.z/.48+.5) if abs(norm.y)>.7 else (v.y/.35+.5,v.z/.48+.5))
 parts.append(o);return o
box('Rounded top',(0,0,.463),(.45,.35,.034),wood,.009)
box('Molded lip',(0,0,.442),(.433,.333,.01),wood,.003)
box('Inset lower shelf',(0,0,.105),(.344,.244,.018),wood,.003)
for x in (-.187,.187):
 for y in (-.137,.137):
  leg=box('Gently tapered leg',(x,y,.217),(.035,.035,.434),wood,.0015)
  for v in leg.data.vertices:
   t=max(0,min(1,(v.co.z+.217)/.434));f=.72+.28*t;v.co.x*=f;v.co.y*=f
  for face in leg.data.polygons:
   if abs(face.normal.z)<.7:
    for li in face.loop_indices:
     v=leg.data.vertices[leg.data.loops[li].vertex_index].co
     cross=v.x if abs(face.normal.y)>.7 else v.y
     leg.data.uv_layers.active.data[li].uv=(v.z/.48+.5,cross/.035+.5)
# Side aprons and sculpted front/back apron.
for x in (-.184,.184):box('Side apron',(x,0,.405),(.022,.25,.065),wood,.002)
def apron(y):
 xs=[-.17,-.145,-.11,-.075,-.04,0,.04,.075,.11,.145,.17]
 bot=[.375,.383,.391,.389,.383,.379,.383,.389,.391,.383,.375]
 ys=(y-.009,y+.009);verts=[(x,q,z) for q in ys for x,z in zip(xs,bot)]+[(x,q,.438) for q in ys for x in xs]
 n=len(xs);faces=[]
 for i in range(n-1):faces.extend([(i,i+1,2*n+i+1,2*n+i),(n+i,3*n+i,3*n+i+1,n+i+1),(i,n+i,n+i+1,i+1),(2*n+i,2*n+i+1,3*n+i+1,3*n+i)])
 faces.extend([(0,2*n,3*n,n),(n-1,2*n-1,4*n-1,3*n-1)])
 mesh=bpy.data.meshes.new('Curved apron');mesh.from_pydata(verts,[],faces);mesh.update();mesh.materials.append(wood);uv=mesh.uv_layers.new(name='UVMap')
 for f in mesh.polygons:
  for li in f.loop_indices:
   v=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=(v.x/.45+.5,v.z/.48)
 o=bpy.data.objects.new('Shaped apron',mesh);bpy.context.collection.objects.link(o);parts.append(o)
apron(-.137);apron(.137)
# restrained localized rubs on the exposed high-contact top lip.
for x,w in [(-.165,.025),(-.035,.016),(.163,.019)]:box('Worn front lip',(x,-.1752,.462),(w,.0007,.0015),wear,.0002)
for y,w in [(-.09,.018),(.1,.025)]:box('Worn right lip',(.2252,y,.462),(.0007,w,.0014),wear,.0002)
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();stand=bpy.context.object;stand.name='LV_PLANT_STAND_01'
bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
bpy.ops.export_scene.fbx(filepath=str(M/'LV_Plant_Stand.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,add_leaf_bones=False)
# Optional small wooden riser prevents the plant's low trailing leaves from crossing the top.
bpy.ops.object.select_all(action='DESELECT');bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=.078,depth=.036,location=(0,0,.498))
riser=bpy.context.object;riser.name='Optional pot riser';riser.data.materials.append(wood)
md=riser.modifiers.new('Soft riser edge','BEVEL');md.width=.002;md.segments=3;bpy.context.view_layer.objects.active=riser;bpy.ops.object.modifier_apply(modifier=md.name)
bpy.context.scene.cursor.location=(0,0,.48);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
bpy.ops.export_scene.fbx(filepath=str(M/'LV_Plant_Stand_Riser.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,add_leaf_bones=False)
riser.hide_render=True
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=True;scene.world.color=(.18,.16,.14)
for loc,power,size in [((2,-3,3),260,4),((-2,2,2),100,3)]:
 bpy.ops.object.light_add(type='AREA',location=loc);bpy.context.object.data.energy=power;bpy.context.object.data.size=size
bpy.ops.object.camera_add(location=(1.5,-2.3,1.35));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.24))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.78;scene.camera=cam
scene.render.filepath=str(O/'stand-perspective.png');bpy.ops.render.render(write_still=True)
cam.location=(0,-3,.29);cam.rotation_euler=(Vector((0,0,.24))-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(O/'stand-front.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(M/'LV-PLANT-STAND-01.blend'))
print('STAND BOUNDS',tuple(round(v,5) for v in stand.dimensions))
