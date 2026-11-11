"""Match ARC-DOOR-03 casing sections around the existing sliding opening."""
from pathlib import Path
import bpy,bmesh,math,json,shutil
from mathutils import Vector
P=Path(__file__).resolve().parent.parent;A=P.parent
bpy.context.preferences.filepaths.save_version=0
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
shutil.copyfile(A/'ARC-DOOR-03/textures/paint-selected.png',P/'textures/paint-selected.png')
paint=bpy.data.materials.new('Painted warm ivory');paint.use_nodes=True;paint.diffuse_color=(.77,.69,.56,1);paint.use_backface_culling=True;ns=paint.node_tree.nodes;ln=paint.node_tree.links;bs=ns['Principled BSDF'];bs.inputs['Roughness'].default_value=.78
t=ns.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(P/'textures/paint-selected.png'));mix=ns.new('ShaderNodeMixRGB');mix.inputs[0].default_value=.35;mix.inputs[2].default_value=(.85,.79,.68,1);ln.new(t.outputs['Color'],mix.inputs[1]);ln.new(mix.outputs[0],bs.inputs['Base Color'])
track=bpy.data.materials.new('Aged track');track.use_nodes=True;track.diffuse_color=(.25,.22,.18,1);bs=track.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.25,.22,.18,1);bs.inputs['Roughness'].default_value=.58;bs.inputs['Metallic'].default_value=.45
parts=[];records=[]
def box(name,loc,dims,mat,bevel=.002):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  mod=o.modifiers.new('Same eased edge as regular casing','BEVEL');mod.width=bevel;mod.segments=2;bpy.ops.object.modifier_apply(modifier=mod.name)
 o.data.materials.append(mat);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.015);bpy.ops.object.mode_set(mode='OBJECT')
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert bm.calc_volume(signed=True)>0;assert all(e.is_manifold for e in bm.edges);bm.to_mesh(o.data);bm.free();parts.append(o);records.append({'name':name,'center_m':list(loc),'dimensions_m':list(dims)});return o
# Structural 90cm opening, 14cm partition and guide channels are unchanged.
for x in [-.465,.465]:
 box('Jamb',(x,0,1.075),(.03,.14,2.15),paint,.003)
 for y in [-.082,.082]:box('Vertical casing',(-.495 if x<0 else .495,y,1.08125),(.09,.025,2.1625),paint,.002)
box('Head jamb',(0,0,2.165),(.96,.14,.03),paint,.003)
# Exactly the regular casing's 75mm head + 22mm shallow cap, on both faces.
# Width adapts to the smaller opening; no extra fascia/cornice is added.
for y in [-.082,.082]:
 box('Head casing',(0,y,2.20),(1.08,.028,.075),paint,.003)
 box('Head cap',(0,y,2.248),(1.10,.038,.022),paint,.003)
for y in [-.028,.028]:
 box('Top guide track',(0,y,2.126),(.9,.026,.012),track,.001)
 box('Bottom guide track',(0,y,.014),(.9,.026,.012),track,.001)
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();frame=bpy.context.object;frame.name='ARC_ClosetFrame04';bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
hulls=[]
for i,(center,dims) in enumerate([((-.465,0,1.075),(.03,.14,2.15)),((.465,0,1.075),(.03,.14,2.15)),((0,0,2.165),(.96,.14,.03))]):
 bpy.ops.mesh.primitive_cube_add(size=1,location=center);o=bpy.context.object;o.name=f'UCX_ARC_ClosetFrame04_{i:02}';o.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.hide_render=True;hulls.append(o)
bpy.ops.object.select_all(action='DESELECT');frame.select_set(True)
for o in hulls:o.select_set(True)
bpy.context.view_layer.objects.active=frame
bpy.ops.export_scene.fbx(filepath=str(P/'model/ARC_ClosetFrame04.fbx'),use_selection=True,object_types={'MESH'},add_leaf_bones=False,apply_unit_scale=True,axis_forward='-Y',axis_up='Z',path_mode='RELATIVE')
for o in hulls:o.hide_set(True)
(P/'assembly.json').write_text(json.dumps({'asset':'ROUND3-CLOSET-FRAME-01','units':'metres','axes':['-Y','Z'],'pivot_m':[0,0,0],'file':'model/ARC_ClosetFrame04.fbx','replaces':'FEEDBACK-ROOM-03/model/ARC_Sliding03_Frame.fbx','bounds_m':[[-.55,-.101,0],[.55,.101,2.259]],'floor_casing_bounds_m':[[-.54,-.0945,0],[.54,.0945,.13]],'clear_jamb_opening_m':[.90,2.15],'rough_opening_m':[.96,2.18],'unchanged_panel_origins_m':{'LeftPanel':[-.22,-.028,0],'RightPanel':[.22,.028,0]},'unchanged_panel_travel_m':{'LeftPanel':.44,'RightPanel':-.44},'collision_hulls':'same three jamb/head boxes as ARC-SLIDING-CLOSET-02; included with matching UCX names','material_slots':['Painted warm ivory','Aged track'],'components':records,'casing_profile_from':'ARC-DOOR-03; section dimensions and paint graph match, width/opening adapted; Y centers shifted +10mm to retain contact with 14cm wall rather than 12cm wall'},indent=2)+'\n')
# Existing panels are display references only, never included in this export.
with bpy.data.libraries.load(str(A/'ARC-SLIDING-CLOSET-02/model/ARC-SLIDING-CLOSET-02.blend'),link=False) as (src,dst):dst.objects=[n for n in src.objects if n in ['ARC_Sliding02_LeftPanel','ARC_Sliding02_RightPanel']]
panels=[]
for o in dst.objects:
 if o:bpy.context.collection.objects.link(o);panels.append(o)
for o in panels:
 for i,m in enumerate(o.data.materials):
  if m.name.startswith('Ivory painted wood'):o.data.materials[i]=paint
sc=bpy.context.scene
if sc.world is None:sc.world=bpy.data.worlds.new('Studio')
sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.55
for loc,power,size in [((2,-4,5),450,4),((-3,-1,3),200,3),((0,3,4),220,3)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.size=size;o.rotation_euler=(Vector((0,0,1.1))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(2.7,-4.8,2.4));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,1.1))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.6;sc.camera=cam;sc.render.engine='CYCLES';sc.cycles.samples=20;sc.render.threads_mode='FIXED';sc.render.threads=2;sc.render.resolution_x=850;sc.render.resolution_y=1000;sc.render.resolution_percentage=100;sc.render.film_transparent=True;sc.render.image_settings.file_format='PNG'
for im in bpy.data.images:
 if im.source=='FILE':
  try:im.pack()
  except RuntimeError:pass
bpy.ops.wm.save_as_mainfile(filepath=str(P/'model/ROUND3-CLOSET-FRAME-01.blend'))
sc.render.filepath=str(P/'previews/closet-frame-closed.png');bpy.ops.render.render(write_still=True)
left=next(o for o in panels if 'LeftPanel' in o.name);left.location.x+=.44;sc.render.filepath=str(P/'previews/closet-frame-open.png');bpy.ops.render.render(write_still=True)
print('CLOSET FRAME04 EXPORTED',records)
