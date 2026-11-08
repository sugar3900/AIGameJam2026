"""Rebuild fabric covered closet storage box, metres / +Z up / front -Y."""
import bpy, math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent.parent; M=P/'model'; O=P/'previews'; T=P/'textures'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def mat(name,col,rough=.84,metal=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True;s=m.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=(*col,1);s.inputs['Roughness'].default_value=rough;s.inputs['Metallic'].default_value=metal;return m
cloth=mat('Sage woven cloth',(.36,.34,.20));s=cloth.node_tree.nodes.get('Principled BSDF');t=cloth.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(T/'sage-linen.png'));t.image.pack();cloth.node_tree.links.new(t.outputs['Color'],s.inputs['Base Color'])
trim=mat('Worn ivory binding',(.68,.57,.40),.9); thread=mat('Ivory stitch',(.78,.71,.56),.96); lining=mat('Warm linen interior',(.48,.40,.30),.94); brass=mat('Aged brass',(.31,.21,.09),.57,.58);label=mat('Blank paper',(.73,.66,.51),.96)
def box(name,loc,dim,material,b=.0015):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if b:
  q=o.modifiers.new('soft edge','BEVEL');q.width=min(b, min(dim)*0.20);q.segments=2;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=q.name)
 o.data.materials.append(material)
 uv=o.data.uv_layers.active or o.data.uv_layers.new(name='UVMap')
 for poly in o.data.polygons:
  n=poly.normal
  for li in poly.loop_indices:
   v=o.data.vertices[o.data.loops[li].vertex_index].co
   uv.data[li].uv=((v.x/.30+.5,v.y/.30+.5) if abs(n.z)>.7 else ((v.x/.30+.5,v.z/.30+.5) if abs(n.y)>.7 else (v.y/.30+.5,v.z/.30+.5)))
 return o
def join(name,objects,origin):
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();o=bpy.context.object;o.name=name;bpy.context.scene.cursor.location=origin;bpy.ops.object.origin_set(type='ORIGIN_CURSOR');return o
body=[]
body.append(box('Bottom',(0,0,.004),(.288,.238,.008),lining,.001))
for x in (-.141,.141):body.append(box('Side walls',(x,0,.077),(.006,.238,.142),cloth))
for y in (-.116,.116):body.append(box('Front and back walls',(0,y,.077),(.276,.006,.142),cloth))
# A light binding wraps the rim, corners and base edge.
for x in (-.143,.143):
 for y in (-.118,.118):body.append(box('Vertical canvas binding',(x,y,.076),(.005,.005,.145),trim,.001))
for z in (.008,.148):
 for y in (-.119,.119):body.append(box('Front-back binding',(0,y,z),(.291,.005,.005),trim,.001))
 for x in (-.145,.145):body.append(box('Side binding',(x,0,z),(.005,.239,.005),trim,.001))
# Blank brass label frame and insert, visually separate from the body cloth.
body.append(box('Brass label back',(0,-.1215,.084),(.072,.003,.031),brass,.002))
body.append(box('Blank label',(0,-.1234,.084),(.060,.001,.021),label,.001))
for x in (-.034,.034):body.append(box('Label rivet',(x,-.1237,.084),(.003,.001,.003),brass,.0007))
# Sewn strokes along front binding, kept subtle at prop scale.
for i in range(25):
 x=-.132+i*.011
 for z in (.009,.147):body.append(box('Stitch',(x,-.1221,z),(.004,.0008,.0008),thread,.0002))
body=join('BR_BOX_BODY',body,(0,0,0))
lid=[]
lid.append(box('Lid top',(0,0,.176),(.300,.250,.008),cloth,.002))
for x in (-.146,.146):lid.append(box('Lid side skirt',(x,0,.164),(.008,.250,.022),cloth,.0015))
for y in (-.121,.121):lid.append(box('Lid front skirt',(0,y,.164),(.284,.008,.022),cloth,.0015))
for z in (.154,.179):
 for y in (-.124,.124):lid.append(box('Lid front binding',(0,y,z),(.30,.004,.004),trim,.0008))
 for x in (-.148,.148):lid.append(box('Lid side binding',(x,0,z),(.004,.247,.004),trim,.0008))
for i in range(25):
 x=-.132+i*.011
 lid.append(box('Lid stitch',(x,-.1263,.158),(.004,.0008,.0008),thread,.0002))
lid=join('BR_BOX_LID',lid,(0,0,.155))
def export(o):
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
 bpy.ops.export_scene.fbx(filepath=str(M/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},add_leaf_bones=False,apply_unit_scale=True,path_mode='AUTO')
for o in (body,lid):export(o)
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=32;sc.render.resolution_x=1100;sc.render.resolution_y=1000;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.film_transparent=True;sc.world.color=(.18,.16,.14)
for loc,power,size,col in [((1,-3,4),400,4,(1,.9,.8)),((-3,2,2),120,3,(1,.86,.76))]:
 bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.data.energy=power;l.data.size=size;l.data.color=col
bpy.ops.object.camera_add(location=(1,-1.6,1.1));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.11))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.52;sc.camera=cam
sc.render.filepath=str(O/'box-closed.png');bpy.ops.render.render(write_still=True)
lid.location.x=.21;lid.location.z=.195;lid.rotation_euler.y=math.radians(18)
cam.data.ortho_scale=.72;cam.rotation_euler=(Vector((.08,0,.11))-cam.location).to_track_quat('-Z','Y').to_euler()
sc.render.filepath=str(O/'box-open.png');bpy.ops.render.render(write_still=True)
lid.location=(0,0,.155);lid.rotation_euler=(0,0,0)
bpy.ops.wm.save_as_mainfile(filepath=str(M/'BR-CLOSET-BOX-01.blend'))
