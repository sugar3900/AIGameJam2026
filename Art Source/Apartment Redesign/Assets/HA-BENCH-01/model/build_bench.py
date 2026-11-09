"""HA-BENCH-01: shallow hall bench, metres, Z-up, floor-centred origin."""
import bpy, math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent.parent; M=P/'model'; T=P/'textures'; O=P/'previews'
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
wood=bpy.data.materials.new('Muted painterly walnut'); wood.diffuse_color=(.28,.17,.11,1); wood.use_nodes=True
bs=wood.node_tree.nodes.get('Principled BSDF'); bs.inputs['Roughness'].default_value=.83
im=wood.node_tree.nodes.new('ShaderNodeTexImage'); im.image=bpy.data.images.load(str(T/'walnut-muted-b.png')); im.image.pack()
h=wood.node_tree.nodes.new('ShaderNodeHueSaturation'); h.inputs['Saturation'].default_value=.68; h.inputs['Value'].default_value=1.35
wood.node_tree.links.new(im.outputs['Color'],h.inputs['Color']); wood.node_tree.links.new(h.outputs['Color'],bs.inputs['Base Color'])
wear=bpy.data.materials.new('Localized rubbed edges'); wear.diffuse_color=(.40,.28,.17,1); wear.use_nodes=True; wb=wear.node_tree.nodes.get('Principled BSDF'); wb.inputs['Base Color'].default_value=wear.diffuse_color; wb.inputs['Roughness'].default_value=.9
parts=[]
def box(name,loc,dim,material=wood,bevel=.002):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=dim; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  m=o.modifiers.new('Worn rounded edges','BEVEL');m.width=bevel;m.segments=3; bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=m.name)
 o.data.materials.append(material); uv=o.data.uv_layers.active or o.data.uv_layers.new(name='UVMap')
 for face in o.data.polygons:
  for li in face.loop_indices:
   v=o.data.vertices[o.data.loops[li].vertex_index].co;n=face.normal
   if abs(n.z)>.7: xy=(v.x/.62+.5,v.y/.25+.5)
   elif abs(n.y)>.7: xy=(v.z/.45+.5,v.x/.62+.5) if name.startswith('Splayed') else (v.x/.62+.5,v.z/.45+.5)
   else: xy=(v.z/.45+.5,v.y/.25+.5) if name.startswith('Splayed') else (v.y/.25+.5,v.z/.45+.5)
   uv.data[li].uv=xy
 parts.append(o);return o
# Seat 620 × 250 × 35 mm: outer face is the depth limit.
box('Solid seat',(0,0,.4325),(.62,.2495,.035),bevel=.006)
box('Seat under lip',(0,0,.411),(.593,.228,.008),bevel=.002)
# Legs splay gently in X/Y without projecting past seat footprint.
for x in (-.258,.258):
 for y in (-.079,.079):
  leg=box('Splayed tapered leg',(x,y,.205),(.037,.034,.41),bevel=.002)
  for v in leg.data.vertices:
   t=max(0,min(1,(v.co.z+.205)/.41)); f=.78+.22*t
   v.co.x*=f;v.co.y*=f
   v.co.x += (1-t)*(.010 if x>0 else -.010)
   v.co.y += (1-t)*(.008 if y>0 else -.008)
# Front and back apron plus side aprons, as in the sheet.
for y in (-.073,.073): box('Long apron',(0,y,.375),(.49,.022,.064),bevel=.002)
for x in (-.252,.252): box('End apron',(x,0,.375),(.022,.14,.064),bevel=.002)
# Interlocking lower supports: one longitudinal stretcher and two end crossbars.
box('Long lower stretcher',(0,0,.13),(.49,.026,.027),bevel=.002)
for x in (-.254,.254): box('End lower stretcher',(x,0,.13),(.026,.16,.026),bevel=.002)
# Tiny selective rubbed edges rather than broad physical paint strokes.
for x,ln in [(-.245,.035),(-.04,.024),(.16,.031)]: box('Front edge rub',(x,-.1249,.435),(ln,.0002,.0016),wear,.00005)
for x in (-.274,.274): box('Foot edge rub',(x,-.103,.05),(.0012,.0003,.018),wear,.00005)
# Combine into one mesh and set floor origin; all visible protrusions remain within limits.
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join(); bench=bpy.context.object;bench.name='HA_BENCH_01';bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
bpy.ops.export_scene.fbx(filepath=str(M/'HA_BENCH_01.fbx'),use_selection=True,object_types={'MESH'},add_leaf_bones=False,apply_unit_scale=True)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.render.resolution_x=1200;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=True;scene.world.color=(.17,.15,.13)
for loc,energy,size in [((2,-3,3),260,4),((-2,2,2),110,3)]:
 bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.data.energy=energy;l.data.size=size
bpy.ops.object.camera_add(location=(1.4,-2.3,1.35));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.225))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.98;scene.camera=cam
scene.render.filepath=str(O/'bench-perspective.png');bpy.ops.render.render(write_still=True)
cam.location=(0,-2,.225);cam.rotation_euler=(Vector((0,0,.225))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.85
scene.render.filepath=str(O/'bench-front.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(M/'HA-BENCH-01.blend'))
print('BENCH_BOUNDS',tuple(round(v,6) for v in bench.dimensions))
