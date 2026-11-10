from pathlib import Path
import bpy,json,math
from mathutils import Matrix,Vector
P=Path(__file__).resolve().parent.parent
source=P.parent/'BA-TUB-01/model/BA-TUB-01.blend'
bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.preferences.filepaths.save_version=0
plumbing=[o for o in bpy.context.scene.objects if o.name.startswith(('Tap_backplate','Tap_stem','Mixer_','Tub_spout','Shower_'))]
rod=[o for o in bpy.context.scene.objects if o.name.startswith(('Curtain_rod','Rod_finial'))]
assert plumbing and len(rod)==3
material=plumbing[0].data.materials[0]
# 25mm mounting spacers support the inherited backplates and bring every pipe
# in front of the new tile. Original riser extends toY.4117; wall datum isY.415.
for x in [-.84,-.66]:
 bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=.034,depth=.025,location=(x,.4025,.96),rotation=(math.pi/2,0,0));o=bpy.context.object;o.name='Valve wall standoff';o.data.materials.append(material);bpy.ops.object.transform_apply(location=False,rotation=True,scale=True);mod=o.modifiers.new('Soft spacer edge','BEVEL');mod.width=.001;mod.segments=2;bpy.ops.object.modifier_apply(modifier=mod.name);plumbing.append(o)
def join(parts,name):
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();o=parts[0];o.name=name;bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');return o
plumb=join(plumbing,'BA_TubFixture02_Plumbing');rail=join(rod,'BA_TubFixture02_CurtainRod')
exports=[]
for o in [plumb,rail]:
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
 bpy.ops.export_scene.fbx(filepath=str(P/'model'/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,add_leaf_bones=False)
 pp=[o.matrix_world@v.co for v in o.data.vertices];exports.append({'file':'model/'+o.name+'.fbx','mesh':o.name,'origin':[0,0,0],'min':[min(v[i] for v in pp) for i in range(3)],'max':[max(v[i] for v in pp) for i in range(3)],'materials':[m.name for m in o.data.materials]})
(P/'assembly.json').write_text(json.dumps({'asset':'BA-TUB-FIXTURES-02','units':'metres','up':'+Z','front':'-Y','source_origin':'unchanged BA-TUB-01 assembly floor origin','exports':exports,'plumbing_plan_origin':[5.293,8.32,0],'plumbing_mapping':'plan=(5.293-sourceY,8.32-sourceX,sourceZ)','plumbing_ue_yaw_degrees':-90,'wall_mount_source_y':.415,'wall_tile_face_x':4.878,'new_source_geometry':'Two25mm chrome standoff disks behind existing valve backplates; remaining original plumbing and rod geometry preserved.','rod_placement':'Use exact original Art_BA_Tub_BA_TubFixtures actor transform; rod remains aligned with unchanged curtain, not the new plumbing transform.','tap_parts':[{'file':'../BA-TUB-01/model/BA_TapLeft.fbx','source_pivot':[-.84,.29,.96],'plan_pivot':[5.003,9.16,.96]},{'file':'../BA-TUB-01/model/BA_TapRight.fbx','source_pivot':[-.66,.29,.96],'plan_pivot':[5.003,8.98,.96]}],'tap_motion':'Preserve imported valve local axis and action; transform both pivot position and axis with plumbing. Valve axis line becomes world X; preserve the imported action sign and verify travel, since the source-to-plan mapping includes reflection.','fill_effect_plan_start':[5.113,9.07,.73],'fill_effect_plan_end':[5.113,9.07,.44],'preserve':['BA_Tub.fbx body','BA_Curtain.fbx and Shower_Curtain action','BA-TUB-WATER-01 fill mesh at existing tub transform','Tyler malady identity and repair overlay'],'collision':'Decorative plumbing/rod: no new blocking collision; preserve interactable valve collision.'},indent=2)+'\n')
# Context duplicates only: exported parts stay in original source coordinates.
T=Matrix.Translation(Vector((-.507,.75,0)))@Matrix.Rotation(math.pi/2,4,'Z')
for o in [plumb]+[o for o in bpy.context.scene.objects if o.name.startswith('Tap_handle')]:
 if o==plumb:
  duplicate=o.copy();duplicate.data=o.data.copy();bpy.context.collection.objects.link(duplicate);duplicate.name='Preview_West_Plumbing';o.hide_render=True;o.hide_set(True);duplicate.matrix_world=T@o.matrix_world
 else:o.matrix_world=T@o.matrix_world
# The wall is preview-only; actual shell/tile is engine-owned.
m=bpy.data.materials.new('Preview pink tile wall');m.use_nodes=True;m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.47,.28,.24,1);m.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.7
bpy.ops.mesh.primitive_cube_add(size=1,location=(-.94,0,1.35));wall=bpy.context.object;wall.name='Preview west tile wall';wall.dimensions=(.036,1.8,2.75);wall.data.materials.append(m)
for o in bpy.context.scene.objects:
 if o.name.startswith('Curtain_panel'):o.hide_render=True
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True;scene.render.resolution_x=1200;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
camera=scene.camera
camera.data.type='PERSP';camera.data.lens=42;camera.location=(2.4,-3.0,2.4);camera.rotation_euler=(Vector((-.30,0,1.10))-camera.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(P/'previews/west-end-context.png');bpy.ops.render.render(write_still=True)
for image in bpy.data.images:
 if image.source=='FILE':
  try:image.pack()
  except RuntimeError:pass
bpy.ops.wm.save_as_mainfile(filepath=str(P/'model/BA-TUB-FIXTURES-02.blend'))
print('Split fixtures complete; old combined fixture must be replaced by both separate groups.')

# Drain stays in the basin; a wall-plumbing transform would lift/misplace it.
import runpy
runpy.run_path(str(P/'model/export_drain.py'), run_name='__main__')
