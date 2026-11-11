"""Vintage range detailing within the established body/door envelope."""
import bpy,math,json,shutil
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent;A=R.parent
for d in ('models','textures','previews'):(R/d).mkdir(exist_ok=True)
ns={'__file__':str(A/'KI-RANGE-01/model/build_range.py')}
exec((A/'KI-RANGE-01/model/build_range.py').read_text().split('# Join export groups')[0],ns)
box=ns['box'];cyl=ns['cyl'];bar=ns['bar'];steel=ns['steel'];iron=ns['iron'];gasket=ns['gasket'];enamel=ns['enamel']
bpy.context.preferences.filepaths.save_version=0
# Pressed drip-bowl rims and dark concentric wells beneath each existing grate.
for x in (-.18,.18):
 for y in (-.15,.15):
  bpy.ops.mesh.primitive_torus_add(major_radius=.068,minor_radius=.0022,major_segments=40,minor_segments=8,location=(x,y,.915))
  o=bpy.context.object;o.name='Rolled drip bowl rim';o.data.materials.append(steel);ns['add']('Body',o)
  cyl('Body','Dark recessed burner well',(x,y,.914),.065,.0015,iron,verts=48)
  for yy in (-.063,.063):
   for xx in (-.063,.063):box('Body','Grate foot',(x+xx,y+yy,.929),(.012,.012,.031),iron,.0015)
# Local dial scales and clear white indicator marks, all inside previous fascia extent.
for x in (-.24,-.08,.08,.24):
 for j in range(9):
  a=math.radians(-135+j*270/8);cx=x+.029*math.sin(a);cz=.807+.029*math.cos(a)
  o=box('Body','Enamel dial graduation',(cx,-.356,cz),(.0014,.0015,.005),iron,.0002);o.rotation_euler.y=a
# Narrow dark louvres beneath the control strip rather than a flat blank apron.
for x in [i*.032 for i in range(-8,9)]:box('Body','Oven cooling louvre',(x,-.350,.738),(.020,.002,.005),gasket,.0007)
# Backguard raised inset, slim moulding and ceramic period badge.
box('Body','Backguard inset',(0,.254,1.005),(.53,.004,.066),steel,.002)
box('Body','Badge enamel',(0,.250,1.006),(.105,.003,.033),enamel,.002)
for x in (-.045,.045):cyl('Body','Badge rivet',(x,.247,1.006),.002,.002,steel,(math.pi/2,0,0),12)
# Small oven-door vents and a fitted inner seal on the existing moving door.
for x in [i*.031 for i in range(-7,8)]:box('Door','Door lower ventilation',(x,-.389,.275),(.018,.0018,.005),gasket,.0008)
for x in (-.302,.302):bar('Door','Vertical heat seal',(x,-.331,.252),(x,-.331,.700),.003,gasket)
for z in (.252,.700):bar('Door','Horizontal heat seal',(-.302,-.331,z),(.302,-.331,z),.003,gasket)
records=[];joined={}
for group,obs in ns['groups'].items():
 bpy.ops.object.select_all(action='DESELECT')
 for o in obs:o.select_set(True)
 bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();o=bpy.context.object;o.name='KI_RANGE02_'+group
 bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
 pv=Vector((0,-.363,.23)) if group=='Door' else Vector((0,0,0))
 # Keep the same authored origin convention as original mesh, verified by FBX round trip.
 bpy.context.scene.cursor.location=pv;bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.01);bpy.ops.object.mode_set(mode='OBJECT')
 for m in o.data.materials:
  if m and m.use_nodes:
   for n in m.node_tree.nodes:
    if n.type=='TEX_IMAGE' and n.image:
     src=Path(n.image.filepath);dst=R/'textures'/src.name
     if src.exists() and src.resolve()!=dst.resolve():shutil.copyfile(src,dst)
     n.image.filepath=str(dst);n.image.pack()
 bpy.ops.export_scene.fbx(filepath=str(R/'models'/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},add_leaf_bones=False)
 vv=[o.matrix_world@v.co for v in o.data.vertices]
 records.append({'file':o.name+'.fbx','replaces':'KI_RANGE_'+group+'.fbx','source_pivot':list(pv),'source_min':[min(v[i] for v in vv) for i in range(3)],'source_max':[max(v[i] for v in vv) for i in range(3)],'slots':[m.name for m in o.data.materials],'collision':'preserve existing range collision and interactive door settings'})
 joined[group]=o
(R/'assembly.json').write_text(json.dumps({'units':'metres','parts':records,'placement':'same body/door transforms and import settings as KI-RANGE-01; no changes to burner/flame/kettle coordinates or oven hinge/open angle'},indent=2)+'\n')
s=bpy.context.scene
if s.world is None:s.world=bpy.data.worlds.new('Studio')
s.render.engine='CYCLES';s.cycles.samples=12;s.render.threads_mode='FIXED';s.render.threads=1;s.render.resolution_x=800;s.render.resolution_y=800;s.render.resolution_percentage=100;s.world.color=(.20,.20,.20);s.render.image_settings.file_format='PNG'
bpy.ops.object.camera_add(location=(1.5,-2.6,1.8));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.53))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=1.40;s.camera=cam
bpy.ops.object.light_add(type='AREA',location=(0,-3,4));bpy.context.object.data.energy=400;bpy.context.object.data.size=4
s.render.filepath=str(R/'previews/range-closed.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/KI-RANGE-02.blend'))
joined['Door'].rotation_euler.x=math.radians(82);s.render.filepath=str(R/'previews/range-open.png');bpy.ops.render.render(write_still=True)
print('RANGE_DETAIL_COMPLETE')
