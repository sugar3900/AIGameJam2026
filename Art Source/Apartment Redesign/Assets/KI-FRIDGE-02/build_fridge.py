"""Opposite-handed source geometry; no negative transforms in the resulting assets."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/'KI-FRIDGE-01/models/KI-FRIDGE-01.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
bpy.context.preferences.filepaths.save_version=0
for o in list(bpy.data.objects):
 if o.name not in ('KI_FRIDGE_BODY','KI_FRIDGE_DOOR'):bpy.data.objects.remove(o,do_unlink=True)
for im in bpy.data.images:
 if im.source=='FILE':
  im.filepath=str(ROOT/'textures/ivory-enamel-v2.png')
  if not im.packed_file:im.pack()
mirror=Matrix.Diagonal((-1,1,1,1));objects={};manifest={}
for key in ('BODY','DOOR'):
 o=bpy.data.objects['KI_FRIDGE_'+key];old=o.matrix_world.copy();origin=mirror@old.translation
 transform=Matrix.Translation(-origin)@mirror@old
 o.data=o.data.copy();o.data.transform(transform);o.data.flip_normals();o.data.update()
 o.matrix_world=Matrix.Translation(origin);o.name='KI_FRIDGE_02_'+key;objects[key]=o
 assert o.matrix_world.determinant()>0
 # Cache exact reflected positions so validation can compare reimported bounds.
 pts=[o.matrix_world@v.co for v in o.data.vertices]
 manifest[key]={'mesh':o.name,'origin_m':list(origin),'closed_bounds_min':[min(p[i] for p in pts) for i in range(3)],'closed_bounds_max':[max(p[i] for p in pts) for i in range(3)],'determinant':o.matrix_world.determinant(),'vertices':len(o.data.vertices),'uv_layers':len(o.data.uv_layers)}
# Simple convex component hulls, kept separate to preserve the body's open cavity.
hulls={'BODY':[],'DOOR':[]}
def hull(key,loc,dim):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 o.name=f'UCX_{objects[key].name}_{len(hulls[key]):02}'
 bpy.context.scene.cursor.location=objects[key].location;bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
 o.hide_render=True;o.display_type='WIRE';hulls[key].append(o)
for x in (-.34,.34):hull('BODY',(x,.035,.88),(.07,.62,1.30))
hull('BODY',(0,.3225,.89),(.60,.045,1.38))
hull('BODY',(0,.035,1.63),(.55,.62,.10));hull('BODY',(0,.035,.155),(.60,.62,.07))
hull('BODY',(0,.02,.045),(.72,.64,.075))
hull('BODY',(0,.08,1.37),(.53,.39,.24));hull('BODY',(0,.035,.30),(.54,.44,.19))
for z in (.53,.79,1.05):hull('BODY',(0,.015,z),(.55,.44,.012))
for z in (.36,1.42):hull('BODY',(.38,-.335,z),(.034,.034,.16))
hull('DOOR',(0,-.315,.895),(.72,.07,1.51))
hull('DOOR',(0,-.271,.895),(.63,.025,1.39))
for z in (.48,.83,1.19):
 hull('DOOR',(0,-.205,z),(.54,.13,.025));hull('DOOR',(0,-.137,z+.072),(.54,.018,.15))
 for x in (-.26,.26):hull('DOOR',(x,-.205,z+.072),(.018,.13,.15))
hull('DOOR',(-.185,-.386,1.10),(.24,.035,.035))
for key,o in objects.items():
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True)
 for h in hulls[key]:h.select_set(True)
 bpy.context.view_layer.objects.active=o
 bpy.ops.export_scene.fbx(filepath=str(ROOT/'models'/f'{o.name}.fbx'),use_selection=True,object_types={'MESH'},add_leaf_bones=False,apply_unit_scale=True,path_mode='AUTO',axis_forward='-Z',axis_up='Y',bake_anim=False)
 manifest[key]['collision_hulls']=len(hulls[key])
 for h in hulls[key]:h.hide_set(True)
manifest['animation']={'door_axis':'local Z','source_closed_degrees':0,'source_open_degrees':105,'body_origin':[0,0,0],'door_pivot_offset_from_body':[.38,-.335,0]}
manifest['export']={'axis_forward':'-Z','axis_up':'Y','unit':'metres','geometry_mirrored_axis':'source world X','positive_scale':True}
(ROOT/'models/manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
# Matching studio camera on opposite side exposes mirrored hinge and interior.
s=bpy.context.scene
bpy.ops.object.camera_add(location=(-3,-5,2.8));cam=bpy.context.object;cam.rotation_euler=(Vector((.08,0,.84))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.55;s.camera=cam
for loc,power,size in [((-3,-4,5),520,4),((3,-2,3.4),320,3.5)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.data.color=(1,.87,.72);o.rotation_euler=(Vector((0,0,.8))-o.location).to_track_quat('-Z','Y').to_euler()
s.render.engine='CYCLES';s.cycles.samples=24;s.world.color=(.21,.19,.17);s.render.resolution_x=1000;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.render.image_settings.file_format='PNG';s.render.film_transparent=True
s.render.filepath=str(ROOT/'previews/fridge-closed.png');bpy.ops.render.render(write_still=True)
objects['DOOR'].rotation_euler.z=math.radians(105)
s.render.filepath=str(ROOT/'previews/fridge-open.png');bpy.ops.render.render(write_still=True)
objects['DOOR'].rotation_euler.z=0
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/KI-FRIDGE-02.blend'))
print('MIRRORED_FRIDGE_COMPLETE')
