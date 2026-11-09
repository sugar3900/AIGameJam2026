"""Fitted kitchen double-hung window. Metres, Z-up, front -Y, opening sill origin."""
import bpy, math, json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene; scene.unit_settings.system='METRIC'; scene.unit_settings.scale_length=1
bpy.context.preferences.filepaths.save_version=0

def material(name,color,rough=.8,metal=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;return m
paint=material('Ivory painted wood',(.77,.72,.62))
t=paint.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(ROOT/'textures/ivory-window-a.png'));t.image.pack();paint.node_tree.links.new(t.outputs['Color'],paint.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
brass=material('Aged brass',(.34,.23,.08),.4,.65)
glass=material('Glass placeholder',(.58,.74,.77),.12);p=glass.node_tree.nodes.get('Principled BSDF');p.inputs['Transmission Weight'].default_value=.8;p.inputs['IOR'].default_value=1.45
parts={};coll={};joined={}
def box(group,name,loc,size,mat=paint,bevel=.003,collision=True):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat)
 if bevel:
  b=o.modifiers.new('Soft joinery edge','BEVEL');b.width=min(bevel,min(size)*.2);b.segments=3;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=b.name)
 parts.setdefault(group,[]).append(o)
 if collision:
  bpy.ops.mesh.primitive_cube_add(size=1,location=loc);c=bpy.context.object;c.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);coll.setdefault(group,[]).append(c);c.hide_render=True;c.display_type='WIRE'
 return o
# Rough aperture X[-.8,.8], Z[0,1.15]. Jambs fill outside 44 mm strip.
for side in (-1,1):
 box('frame','Jamb',(side*.778,0,.575),(.044,.12,1.15),bevel=0)
 box('frame','Casing',(side*.84,-.077,.570),(.095,.034,1.170))
 box('frame','Interior sash stop',(side*.745,-.025,.575),(.025,.04,1.062),bevel=.001)
box('frame','Head jamb',(0,0,1.128),(1.512,.12,.044),bevel=0)
box('frame','Base jamb',(0,0,.022),(1.512,.12,.044),bevel=0)
box('frame','Casing head',(0,-.077,1.2025),(1.78,.034,.095))
box('frame','Header cap',(0,-.08,1.259),(1.83,.044,.018))
box('frame','Shallow sill',(0,-.075,-.0025),(1.82,.19,.045))
box('frame','Short apron',(0,-.078,-.0475),(1.60,.03,.045))
# Sash outer width 1.47; distinct front/back tracks so the closed meeting rails overlap in Z only.
def sash(key,z,y,h=.537):
 w=1.47;r=.035
 for side in (-1,1):box(key,'Sash stile',(side*(w/2-r/2),y,z),(r,.028,h))
 for side in (-1,1):box(key,'Sash rail',(0,y,z+side*(h/2-r/2)),(w-.07,.028,r))
 for x in (-w/6,w/6):box(key,'Vertical muntin',(x,y,z),(.018,.028,h-.07),bevel=.002)
 for x,width in ((-.477,.446),(0,.472),(.477,.446)):box(key,'Horizontal muntin',(x,y,z),(width,.028,.018),bevel=.001)
 box(key.replace('sash','glass'),'Glazing',(0,y+.004,z),(w-.07,.005,h-.07),glass,0,False)
sash('upper_sash',.838,.023)
sash('lower_sash',.310,-.028)
box('lower_sash','Latch plate',(0,-.051,.568),(.10,.014,.022),brass,.002)
box('lower_sash','Latch lever',(.018,-.062,.577),(.05,.012,.008),brass,.001)
box('upper_sash','Latch catch',(0,.001,.58),(.05,.012,.015),brass,.002)
# Mesh names are stable and collision hulls are named per their render mesh.
manifest={}
for key,objects in parts.items():
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();o=bpy.context.object;o.name='ARC_Window_Kitchen_'+key
 bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');joined[key]=o
 # Preserve primitive UVs through joining; each painted joinery piece samples the generated surface.
 bounds=[o.matrix_world@Vector(c) for c in o.bound_box]
 manifest[key]={'mesh':o.name,'bounds_min':[min(v[i] for v in bounds) for i in range(3)],'bounds_max':[max(v[i] for v in bounds) for i in range(3)],'collision_hulls':len(coll.get(key,[]))}
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True)
 for i,c in enumerate(coll.get(key,[])):
  c.name=f'UCX_{o.name}_{i:02}';c.select_set(True)
 bpy.context.view_layer.objects.active=o
 bpy.ops.export_scene.fbx(filepath=str(ROOT/'model'/f'{o.name}.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,axis_forward='-Y',axis_up='Z',bake_anim=False,add_leaf_bones=False,path_mode='RELATIVE')
 for c in coll.get(key,[]):c.hide_set(True)
(ROOT/'model/dimensions.json').write_text(json.dumps(manifest,indent=2)+'\n')
# Studio-only wall and muted garden backdrop. Not included in any export.
wall=material('PREVIEW warm plaster',(.48,.40,.29),.95)
for name,loc,size in [('left',(-1.2,.01,.575),(.8,.12,3.0)),('right',(1.2,.01,.575),(.8,.12,3.0)),('above',(0,.01,1.6125),(1.6,.12,.925)),('below',(0,.01,-.4625),(1.6,.12,.925))]:box('preview','PREVIEW '+name,loc,size,wall,0,False)
card=material('PREVIEW exterior',(.35,.43,.29),.95)
box('preview','PREVIEW exterior card',(0,.50,.575),(1.60,.01,1.15),card,0,False)
# Counter height proxy is intentionally not part of the exported fitted window.
stone=material('PREVIEW ivory counter',(.70,.65,.53),.8)
box('preview','PREVIEW sink upstand clearance',(0,-.26,-.2275),(1.05,.05,.225),stone,.003,False)
scene.world.color=(.18,.17,.15)
def area(name,loc,power,size):
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,.55))-o.location).to_track_quat('-Z','Y').to_euler()
area('Key',(-3,-4,4),450,4);area('Fill',(3,-2,2),180,3)
bpy.ops.object.camera_add(location=(2.7,-5,2.2));cam=bpy.context.object;cam.name='PREVIEW camera';cam.rotation_euler=(Vector((0,0,.55))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.75
scene.camera=cam;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.render.resolution_x=1100;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
scene.view_settings.view_transform='AgX'
scene.render.filepath=str(ROOT/'previews/window-perspective.png');bpy.ops.render.render(write_still=True)
cam.location=(0,-5,.6);cam.rotation_euler=(Vector((0,0,.6))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=2.55
scene.render.filepath=str(ROOT/'previews/window-front.png');bpy.ops.render.render(write_still=True)
for k in ('lower_sash','lower_glass'):joined[k].location.z+=.48
scene.render.filepath=str(ROOT/'previews/window-open.png');bpy.ops.render.render(write_still=True)
for k in ('lower_sash','lower_glass'):joined[k].location.z-=.48
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'model/ARC-WINDOW-KITCHEN-02.blend'))
print('FITTED_WINDOW_COMPLETE')
