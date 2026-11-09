"""Create a repeatable bedroom wainscot bay and separate repair overlay. Blender background."""
import bpy, math, os, random
from mathutils import Vector
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL=os.path.join(ROOT,'model'); PRE=os.path.join(ROOT,'previews'); TEX=os.path.join(ROOT,'textures')
for p in (MODEL,PRE,TEX): os.makedirs(p,exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def paint(name,color,rough=.78,texture=None):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    nodes=m.node_tree.nodes; bs=nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=rough
    if texture:
        t=nodes.new('ShaderNodeTexImage'); t.image=bpy.data.images.load(texture,check_existing=True); t.interpolation='Linear'; m.node_tree.links.new(t.outputs['Color'],bs.inputs['Base Color'])
    return m
ivory=paint('Painted Ivory',(0.78,.72,.62),texture=os.path.join(TEX,'candidate-d-brush-ivory.png'))
shadow=paint('Inset cream',(0.68,.62,.53),texture=os.path.join(TEX,'candidate-d-brush-ivory.png'))
wood=paint('Exposed wood shadow',(.34,.255,.18)); mid=paint('Aged substrate',(.49,.40,.31)); light=paint('Paint flake edges',(.75,.69,.58));

def block(name, loc, dims, mat, bevel=.002):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=dims; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        mod=o.modifiers.new('Edge easing','BEVEL'); mod.width=bevel; mod.segments=2; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL'); bpy.context.view_layer.objects.active=o
        for m in list(o.modifiers): bpy.ops.object.modifier_apply(modifier=m.name)
    o.data.materials.append(mat); return o
# Local X along wall, local -Y is visible face, Z up; one-metre repeat, floor at Z=0.
bpy.ops.object.select_all(action='DESELECT')
block('Panel backing',(.5,.0,.55),(1,.028,1.10),shadow)
# Separate shallow moulding profiles; edges meet or slightly overlap cleanly.
block('Skirting',(.5,-.024,.070),(1,.032,.14),ivory,.004)
block('Base bead',(.5,-.042,.145),(1,.016,.012),ivory,.002)
block('Lower rail',(.5,-.024,.205),(1,.028,.10),ivory,.003)
block('Top rail',(.5,-.024,.995),(1,.028,.09),ivory,.003)
block('Chair cap lower',(.5,-.037,1.050),(1,.040,.025),ivory,.003)
block('Chair cap upper',(.5,-.046,1.080),(1,.052,.040),ivory,.004)
for x,w in ((.0175,.035),(.5,.07),(.9825,.035)): block('Stile', (x,-.023,.60),(w,.026,.75),ivory,.003)
# inset frames: subtle shallow strips around flat recessed paint surface
for cx in (.2675,.7325):
    for x in (cx-.183,cx+.183): block('Inset vertical bead',(x,-.019,.60),(.014,.017,.65),ivory,.002)
    for z in (.275,.925): block('Inset horizontal bead',(cx,-.019,z),(.38,.017,.014),ivory,.002)
base_objects=list(bpy.context.scene.objects)
# One small local patch with thin irregular silhouettes, no physical paint buildup or dark halo.
# Transparent generated color/alpha overlay. Damage is separate and is hidden after repair.
damage_mat=bpy.data.materials.new('Lead Paint Damage RGBA'); damage_mat.use_nodes=True
bs=damage_mat.node_tree.nodes.get('Principled BSDF'); bs.inputs['Roughness'].default_value=.85
tex=damage_mat.node_tree.nodes.new('ShaderNodeTexImage'); tex.image=bpy.data.images.load(os.path.join(TEX,'paint-damage-selected.png'),check_existing=True)
damage_mat.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color']); damage_mat.node_tree.links.new(tex.outputs['Alpha'],bs.inputs['Alpha'])
damage_mat.surface_render_method='DITHERED'
bpy.ops.mesh.primitive_plane_add(size=1,location=(.73,-.016,.40),rotation=(math.pi/2,0,0)); damage_obj=bpy.context.object; damage_obj.name='LeadPaintDamage'; damage_obj.scale=(.31,.22,1); bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); damage_obj.data.materials.append(damage_mat); bpy.context.scene.cursor.location=(0,0,0); bpy.ops.object.origin_set(type='ORIGIN_CURSOR'); damage=[damage_obj]
# Joining without altering the source object names makes UE import straightforward.
def export_set(name, objects):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects: o.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    bpy.ops.export_scene.fbx(filepath=os.path.join(MODEL,name+'.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,add_leaf_bones=False,mesh_smooth_type='FACE')
export_set('BR_Wainscot_Module',base_objects); export_set('BR_Wainscot_Damage',damage)
# Neutral upper wall and floor for contextual preview only; never exported.
upper=paint('Preview warm sage plaster',(.40,.41,.28)); floor=paint('Preview warm wood',(.28,.14,.07))
block('Preview wall',(.5,.027,1.70),(2.6,.04,1.2),upper,0)
block('Preview floor',(.5,-.38,-.025),(2.6,.8,.05),floor,0)
# Camera, ambient and directional light; enough contrast to assess both intact and damaged states.
bpy.ops.object.camera_add(location=(1.48,-2.8,1.38)); cam=bpy.context.object; cam.name='Preview Camera'; cam.rotation_euler=(Vector((.50,0,.68))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=1.8; bpy.context.scene.camera=cam
bpy.ops.object.light_add(type='AREA',location=(-.7,-2.5,2.8)); key=bpy.context.object; key.data.energy=310; key.data.shape='DISK'; key.data.size=3; key.data.color=(1,.80,.58); key.rotation_euler=(Vector((.5,0,.5))-key.location).to_track_quat('-Z','Y').to_euler()
world=bpy.context.scene.world; world.color=(.32,.30,.27)
scene=bpy.context.scene; scene.render.engine='CYCLES'; scene.cycles.samples=32; scene.render.resolution_x=1000; scene.render.resolution_y=1000; scene.render.resolution_percentage=100; scene.view_settings.view_transform='AgX'; scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=False
scene.render.filepath=os.path.join(PRE,'wainscot-before.png'); bpy.ops.render.render(write_still=True)
for o in damage: o.hide_render=True
scene.render.filepath=os.path.join(PRE,'wainscot-after.png'); bpy.ops.render.render(write_still=True)
for o in damage: o.hide_render=False
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(MODEL,'BR-WAINSCOT-01.blend'))
print('WAINSCOT_BUILD_DONE',len(base_objects),'base objects',len(damage),'damage shapes')
