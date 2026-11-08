"""Period wall shelf; metres, front -Y, origin at wall plane / shelf top."""
import bpy, math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent.parent; M=P/'model'; T=P/'textures'; O=P/'previews'
for p in (M,T,O): p.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
def mat(name,color,rough=.8,metal=0):
 m=bpy.data.materials.new(name); m.diffuse_color=(*color,1);m.use_nodes=True;s=m.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=(*color,1);s.inputs['Roughness'].default_value=rough;s.inputs['Metallic'].default_value=metal;return m
wood=mat('Muted painterly walnut',(.3,.14,.07),.86)
s=wood.node_tree.nodes.get('Principled BSDF'); tex=wood.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(T/'walnut-muted-b.png'));tex.image.pack();h=wood.node_tree.nodes.new('ShaderNodeHueSaturation');h.inputs['Saturation'].default_value=.68;h.inputs['Value'].default_value=1.35;wood.node_tree.links.new(tex.outputs['Color'],h.inputs['Color']);wood.node_tree.links.new(h.outputs['Color'],s.inputs['Base Color'])
brass=mat('Aged brass screw',(.30,.20,.08),.48,.7)
def uv_project(o):
 uv=o.data.uv_layers.active or o.data.uv_layers.new(name='UVMap')
 for poly in o.data.polygons:
  n=poly.normal
  for li in poly.loop_indices:
   v=o.data.vertices[o.data.loops[li].vertex_index].co
   if abs(n.z)>.7: a,b=v.x,v.y
   elif abs(n.y)>.7: a,b=v.x,v.z
   else: a,b=v.y,v.z
   uv.data[li].uv=(a/.65+.5,b/.65+.5)
def box(name,loc,dim,material,bevel=.003):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  mod=o.modifiers.new('Softly worn edges','BEVEL');mod.width=bevel;mod.segments=3;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 o.data.materials.append(material);uv_project(o);return o
parts=[]
parts.append(box('Shelf plank',(0,-.075,-.0125),(.65,.15,.025),wood,.004))
# Front rounded lip beneath the plank, with a distinct period profile.
parts.append(box('Soft front bead',(0,-.145,-.023),(.635,.010,.012),wood,.003))
# Concave corbel profile in YZ, extruded in X. Back edge is against wall.
profile=[(-.137,-.024),(-.136,-.040),(-.122,-.043),(-.104,-.049),(-.088,-.060),(-.074,-.076),(-.063,-.095),(-.056,-.116),(-.047,-.135),(-.033,-.145),(-.012,-.145),(-.012,-.024)]
def corbel(x):
 verts=[(x+dx,y,z) for dx in (-.012,.012) for y,z in profile];n=len(profile)
 # Reverse faces to preserve outward winding, triangulate concave polygons later.
 faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
 for i in range(n):j=(i+1)%n;faces.append((i,j,n+j,n+i))
 me=bpy.data.meshes.new('CorbelMesh');me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new('Sculpted corbel',me);bpy.context.collection.objects.link(o);o.data.materials.append(wood)
 # Triangulation of end caps is robust for concave profiles.
 bpy.context.view_layer.objects.active=o;o.select_set(True);mod=o.modifiers.new('Cap triangulation','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=mod.name);o.select_set(False);uv_project(o);return o
for x in (-.225,.225):
 parts.append(corbel(x))
 # Back plates extend beyond corbel on each side, giving visible fixings.
 parts.append(box('Wall fixing plate',(x,-.007,-.085),(.047,.014,.12),wood,.002))
 # Two brass screw heads face toward the room, just outside the corbel edges.
 for dx,z in ((-.018,-.049),(.018,-.12)):
  bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=.0035,depth=.0015,location=(x+dx,-.0155,z),rotation=(math.pi/2,0,0));o=bpy.context.object;o.name='Slotted brass fastener';o.data.materials.append(brass);parts.append(o)
# Join while retaining the wall-face/top origin and per-mesh UVs.
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();shelf=bpy.context.object;shelf.name='ARC_WALL_SHELF_01'
bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
bpy.ops.export_scene.fbx(filepath=str(M/'ARC_WALL_SHELF_01.fbx'),use_selection=True,object_types={'MESH'},add_leaf_bones=False,apply_unit_scale=True,path_mode='AUTO')
# Studio wall exists only for preview, and is not exported.
wall=mat('Preview plaster',(.47,.40,.34),.95)
box('Preview wall',(0,.035,-.065),(1,.07,.6),wall,0)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.render.resolution_x=1200;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False;scene.world.color=(.22,.20,.18)
for loc,energy,size in [((-.8,-1.8,2),180,2.0),((1.6,-.4,1.2),90,1.5)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=energy;o.data.size=size
bpy.ops.object.light_add(type='AREA',location=(0,-1.5,-.45));fill=bpy.context.object;fill.data.energy=35;fill.data.size=1.5;fill.rotation_euler=(Vector((0,-.03,-.08))-fill.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(1.35,-2.15,1.2));cam=bpy.context.object;cam.rotation_euler=(Vector((0,-.045,-.07))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.95;scene.camera=cam
scene.render.filepath=str(O/'shelf-perspective.png');bpy.ops.render.render(write_still=True)
cam.location=(0,-2,0);cam.rotation_euler=(Vector((0,0,-.06))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.82;scene.render.filepath=str(O/'shelf-front.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(M/'ARC-WALL-SHELF-01.blend'))
print('BOUNDS',*[round(v,5) for v in shelf.dimensions])
