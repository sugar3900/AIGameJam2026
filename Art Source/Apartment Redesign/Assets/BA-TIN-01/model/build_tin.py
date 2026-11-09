"""BA-TIN-01; Blender metres, Z up, front -Y."""
import bpy, math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1]; M=P/'model'; T=P/'textures'; V=P/'previews'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def material(name,color,rough=.65,metal=.0,image=None):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*color,1);b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=metal
 if image:
  node=m.node_tree.nodes.new('ShaderNodeTexImage');node.image=bpy.data.images.load(str(T/image),check_existing=True);m.node_tree.links.new(node.outputs['Color'],b.inputs['Base Color'])
 return m
ivory=material('Warm_Ivory_Enamel',(.82,.76,.65),.62,.12,'ivory-enamel.png');floral=material('Painterly_Floral_Front',(.82,.76,.65),.64,.08,'tin-floral.png');edge=material('Aged_Enamel_Edge',(.34,.24,.18),.64,.45);interior=material('Warm_Interior',(.66,.60,.52),.72,.18)
def cube(name,loc,size,mat,bevel=.0015,front=False,top=False):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 mod=o.modifiers.new('Soft_Worn_Edges','BEVEL');mod.width=bevel;mod.segments=3;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 o.data.materials.append(mat)
 if front or top:o.data.materials.append(floral)
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.01);bpy.ops.object.mode_set(mode='OBJECT')
 if front or top:
  uv=o.data.uv_layers.active
  for p in o.data.polygons:
   if (front and p.normal.y < -.999) or (top and p.normal.z > .999):
    p.material_index=1
    for li in p.loop_indices:
     v=o.data.vertices[o.data.loops[li].vertex_index].co
     uv.data[li].uv=(v.x/size[0]*.55+.5,(v.z/size[2] if front else v.y/size[1])*.55+.5)
 return o
def join(name,obs,origin):
 bpy.ops.object.select_all(action='DESELECT')
 for o in obs:o.select_set(True)
 bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();o=bpy.context.object;o.name=name;bpy.context.scene.cursor.location=origin;bpy.ops.object.origin_set(type='ORIGIN_CURSOR');return o
parts=[cube('Front',(0,-.043,.0725),(.116,.004,.141),ivory,front=True),cube('Back',(0,.043,.0725),(.116,.004,.141),ivory),cube('Left',(-.058,0,.0725),(.004,.082,.141),ivory),cube('Right',(.058,0,.0725),(.004,.082,.141),ivory),cube('Bottom',(0,0,.003),(.116,.082,.006),interior)]
# Four restrained rolled rim edges.
for loc,size in [((0,-.044,.142),(.12,.003,.003)),((0,.044,.142),(.12,.003,.003)),((-.059,0,.142),(.003,.085,.003)),((.059,0,.142),(.003,.085,.003))]:parts.append(cube('Rim',loc,size,edge,.001))
body=join('BA_Tin_Body',parts,(0,0,0))
lid_parts=[cube('LidTop',(0,0,.154),(.120,.090,.008),ivory,.003,top=True),cube('LidFront',(0,-.043,.149),(.118,.003,.009),ivory,.001),cube('LidBack',(0,.043,.149),(.118,.003,.009),ivory,.001),cube('LidLeft',(-.058,0,.149),(.003,.083,.009),ivory,.001),cube('LidRight',(.058,0,.149),(.003,.083,.009),ivory,.001)]
lid_parts.append(cube('LidEdge',(0,-.044,.146),(.117,.002,.002),edge,.0008))
lid=join('BA_Tin_Lid',lid_parts,(0,0,.145))
for ob,name in [(body,'BA_Tin_Body.fbx'),(lid,'BA_Tin_Lid.fbx')]:
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.export_scene.fbx(filepath=str(M/name),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,add_leaf_bones=False)
bpy.ops.object.select_all(action='DESELECT');bpy.ops.object.camera_add(location=(.30,-.46,.30));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.08))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.26;bpy.context.scene.camera=cam
for pos,power,size in [((-.3,-.4,.5),3,.4),((.3,.1,.35),1.8,.35)]:
 bpy.ops.object.light_add(type='AREA',location=pos);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,.08))-o.location).to_track_quat('-Z','Y').to_euler()
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=32;sc.render.resolution_x=900;sc.render.resolution_y=900;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.film_transparent=True;sc.world.color=(.14,.12,.1)
bpy.ops.wm.save_as_mainfile(filepath=str(M/'BA-TIN-01.blend'));sc.render.filepath=str(V/'tin-closed.png');bpy.ops.render.render(write_still=True)
lid.location.x+=.115;lid.location.z+=.018;lid.rotation_euler[1]=math.radians(22);cam.data.ortho_scale=.34;cam.rotation_euler=(Vector((.045,0,.09))-cam.location).to_track_quat('-Z','Y').to_euler();sc.render.filepath=str(V/'tin-open.png');bpy.ops.render.render(write_still=True)
