import bpy, os, math
from mathutils import Vector
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
mat=bpy.data.materials.new('Walnut_Painterly'); mat.use_nodes=True
bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.88
tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(os.path.join(ROOT,'textures','walnut-muted-b.png'),check_existing=True);h=mat.node_tree.nodes.new('ShaderNodeHueSaturation');h.inputs['Saturation'].default_value=.68;h.inputs['Value'].default_value=1.35;mat.node_tree.links.new(tex.outputs['Color'],h.inputs['Color']);mat.node_tree.links.new(h.outputs['Color'],bs.inputs['Base Color'])
wear=bpy.data.materials.new('Fine_Edge_Wear');wear.diffuse_color=(.39,.27,.15,1);wear.use_nodes=True;wear.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.39,.27,.15,1);wear.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.93
parts=[]
def box(name,loc,dim,bevel=.003, material=None):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  m=o.modifiers.new('worn soft edges','BEVEL');m.width=min(bevel,min(dim)*.2);m.segments=3;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=m.name)
 o.data.materials.append(material or mat);parts.append(o);return o
# 1.10m across X, 0.30m depth Y, 0.90m high. Front is -Y.
box('back',(0,.133,.47),(1.02,.018,.79))
for x in [-.515,.515]:
 box('side',(x,0,.47),(.035,.28,.79))
 box('front stile',(x,-.1375,.47),(.042,.025,.79))
for z in [.105,.465,.825]:
 box('shelf' if z<.8 else 'case top',(0,-.002,z),(1.02,.28,.028))
 box('shelf front lip',(0,-.136,z-.005),(1.02,.016,.030))
# Period plinth and stepped cap, compatible with living case.
box('plinth front',(0,-.125,.045),(1.07,.04,.09))
for x in [-.505,.505]:box('plinth return',(x,0,.045),(.06,.27,.09))
box('cap base',(0,0,.851),(1.06,.29,.024))
box('cap molding',(0,0,.875),(1.08,.30,.024))
box('cap top',(0,0,.894),(1.10,.30,.012))
# Sparse, understated rubbed edges placed independently from the reusable texture.
for x,z,length in [(-.42,.895,.037),(.34,.895,.048),(-.23,.471,.026),(.26,.471,.032),(-.34,.11,.035)]:
 y=-.1504 if z>.8 else -.1444
 box('localized edge rub',(x,y,z),(length,.0008,.002),.0002,wear)
for x,z in [(-.525,.61),(.525,.31)]:box('stile edge rub',(x,-.1504,z),(.002,.0008,.015),.0002,wear)
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();case=bpy.context.object;case.name='OF_BOOKCASE_BODY';bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
bpy.ops.export_scene.fbx(filepath=os.path.join(ROOT,'model','OF_BOOKCASE_BODY.fbx'),use_selection=True,object_types={'MESH'},add_leaf_bones=False,apply_unit_scale=True)
world=bpy.context.scene.world or bpy.data.worlds.new('World');bpy.context.scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.20,.17,.13,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.5
for loc,energy,color,size in [((2,-4,5),450,(1,.82,.66),4),((-3,-2,3),190,(1,.91,.8),4)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=energy;o.data.color=color;o.data.shape='DISK';o.data.size=size
bpy.ops.object.camera_add(location=(2,-3,1.8));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.45))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=1.65;bpy.context.scene.camera=cam
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=32;sc.render.resolution_x=1100;sc.render.resolution_y=1100;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.film_transparent=True
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'model','OF-BOOKCASE-01.blend'));sc.render.filepath=os.path.join(ROOT,'previews','bookcase-three-quarter.png');bpy.ops.render.render(write_still=True)
