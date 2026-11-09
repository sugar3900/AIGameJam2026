import bpy, math
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
bpy.context.scene.unit_settings.system='METRIC'

def material(name, color, rough=.7, metal=0):
 m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal
 return m
paint=material('Ivory painted wood',(.77,.72,.62),.82)
texture=ROOT/'textures'/'ivory-window-a.png'
if texture.exists():
 n=paint.node_tree.nodes.new('ShaderNodeTexImage'); n.image=bpy.data.images.load(str(texture),check_existing=True)
 paint.node_tree.links.new(n.outputs['Color'],paint.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
brass=material('Aged brass',(.34,.23,.08),.4,.65)
glass=material('Glass placeholder',(.58,.74,.77),.12)
p=glass.node_tree.nodes.get('Principled BSDF'); p.inputs['Transmission Weight'].default_value=.8; p.inputs['IOR'].default_value=1.45

groups={'frame':[], 'upper_sash':[], 'lower_sash':[], 'upper_glass':[], 'lower_glass':[]}
def box(group,name,loc,dim,mat=paint,bevel=.004):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=dim
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(mat)
 if bevel:
  b=o.modifiers.new('soft edges','BEVEL'); b.width=bevel;b.segments=2
  bpy.context.view_layer.objects.active=o; bpy.ops.object.modifier_apply(modifier=b.name)
 groups[group].append(o);return o
# 1.10 x 1.40 opening; unchanged trim and muntin cross-sections.
for side in (-1,1):
 box('frame','Jamb', (side*.528,0,1.60),(.044,.12,1.40),bevel=0)
 box('frame','Casing', (side*.59,-.073,1.5925),(.095,.035,1.465))
for side in (-1,1): box('frame','Interior sash stop',(side*.495,-.005,1.60),(.035,.08,1.40),bevel=0)
box('frame','Jamb head',(0,0,2.278),(1.012,.12,.044),bevel=0)
box('frame','Jamb base',(0,0,.922),(1.012,.12,.044),bevel=0)
box('frame','Casing head',(0,-.073,2.37),(1.28,.035,.095))
box('frame','Header cap',(0,-.077,2.426),(1.33,.045,.018))
box('frame','Projecting sill',(0,-.085,.894),(1.32,.19,.045))
box('frame','Sill apron',(0,-.079,.828),(1.10,.033,.09))
# each sash has 3 columns x 2 rows; sashes overlap slightly at meeting rail.
def sash(group,glassgroup,z,y,h):
 w=.97; outer=.035
 for sx in (-1,1): box(group,'Sash stile',(sx*(w/2-outer/2),y,z),(outer,.036,h))
 for sz in (-1,1): box(group,'Sash rail',(0,y,z+sz*(h/2-outer/2)),(w-.07,.036,outer))
 for x in (-w/6,w/6): box(group,'Vertical muntin',(x,y-.002,z),(.018,.04,h-.07),bevel=.002)
 for x,width in ((-(w/3-.013),w/3-.044),(0,w/3-.018),(w/3-.013,w/3-.044)): box(group,'Horizontal muntin',(x,y-.002,z),(width,.04,.018),bevel=0)
 # transparent pane behind grid, deliberately single plane per sash for UE material flexibility
 box(glassgroup,'Glazing',(0,y+.005,z),(w-.07,.006,h-.07),glass,0)
sash('upper_sash','upper_glass',1.965,.015,.66)
sash('lower_sash','lower_glass',1.295,-.035,.70)
box('lower_sash','Latch plate',(0,-.060,1.638),(.10,.015,.028),brass,.002)
box('upper_sash','Latch catch',(0,-.010,1.643),(.05,.02,.022),brass,.002)
# Join each component and export with shared floor-center origin; Blender UVs retained.
for key,parts in groups.items():
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();ob=bpy.context.object;ob.name=key
 bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
 bpy.ops.export_scene.fbx(filepath=str(ROOT/'model'/('ARC_Window_'+key+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,axis_forward='-Y',axis_up='Z',bake_anim=False,add_leaf_bones=False)
# render front and angled studio views with a background wall that is not exported.
wall=material('Preview wall',(.52,.38,.32),.9)
# wall segments preserve opening
for name,loc,dim in [('left',(-1.10,.17,1.6),(1.1,.12,2.5)),('right',(1.10,.17,1.6),(1.1,.12,2.5)),('top',(0,.17,2.55),(1.1,.12,.5)),('bottom',(0,.17,.45),(1.1,.12,.9))]:box('frame','PREVIEW ONLY '+name,loc,dim,wall,0)
world=bpy.context.scene.world;world.color=(.22,.22,.22)
# Preview-only exterior color card; no exterior art or wall is exported.
card=material('Preview exterior',(.49,.58,.53),.9)
preview_card=box('frame','PREVIEW ONLY exterior card',(0,.65,1.60),(1.10,.01,1.40),card,0)
def area(name,loc,power,size):
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,1.6))-o.location).to_track_quat('-Z','Y').to_euler()
area('Key',(-3,-4,5),650,5);area('Fill',(4,-2,3),350,4)
bpy.ops.object.camera_add(location=(3.7,-6.4,3.2));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,1.62))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=3.4
scene=bpy.context.scene;scene.camera=cam;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.render.filepath=str(ROOT/'previews'/'window-three-quarter.png');bpy.ops.render.render(write_still=True)
cam.location=(0,-7,1.65);cam.rotation_euler=(Vector((0,0,1.65))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=3.0
scene.render.filepath=str(ROOT/'previews'/'window-front.png');bpy.ops.render.render(write_still=True)
# Open the lower sash and pane together for a 35 cm test pose; exports stay closed.
for key in ('lower_sash','lower_glass'): bpy.data.objects[key].location.z+=.35
scene.render.filepath=str(ROOT/'previews'/'window-front-open.png');bpy.ops.render.render(write_still=True)
for key in ('lower_sash','lower_glass'): bpy.data.objects[key].location.z-=.35
# Back view: hide the unexported exterior card so it does not obscure joinery.
preview_card.hide_render=True
cam.location=(0,7,1.65);cam.rotation_euler=(Vector((0,0,1.65))-cam.location).to_track_quat('-Z','Y').to_euler()
area('Back fill',(1,4,4),600,4)
scene.render.filepath=str(ROOT/'previews'/'window-back.png');bpy.ops.render.render(write_still=True)
preview_card.hide_render=False
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'model'/'ARC_WINDOW_NARROW_Source.blend'))
