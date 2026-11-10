"""FIX-002: full-length bilateral closet shelves, supported rails and real hooked hangers.
Only the Storage_W/E groups are exported; original closet is a read-only preview source.
"""
from pathlib import Path
import bpy, math, json, sys
from mathutils import Vector, Matrix
ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT.parent
bpy.ops.wm.open_mainfile(filepath=str(ASSETS/'BR-CLOSET-02/model/BR-CLOSET-02.blend'))
sc=bpy.context.scene
sc.render.engine='CYCLES';sc.cycles.samples=40
sc.render.resolution_x=1200;sc.render.resolution_y=1100;sc.render.resolution_percentage=100
bpy.context.preferences.filepaths.save_version=0
old_prefix=('West high shelf','Shelf front apron','Shelf wall cleat','Triangular shelf bracket','West hanging rail','Hanger hook','Hanger shoulder','Hanger bar','Mold decal','CLEARANCE')
for o in list(bpy.data.objects):
 if o.name.startswith(old_prefix):bpy.data.objects.remove(o,do_unlink=True)

def mat(name,color,tex=None,metal=0,rough=.8):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 if tex:
  t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(ROOT/'textures'/tex),check_existing=True);t.image.pack();m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
 return m
white=mat('CS03_PaintedIvory',(.78,.74,.64),'white-wood.png')
wood=mat('CS03_HangerWood',(.31,.16,.065),'hanger-wood.png')
metal=mat('CS03_AgedSteel',(.31,.29,.25),metal=.72,rough=.48)
groups={};hulls={};hanger_objects=[]
def reg(o,g,m):o.data.materials.clear();o.data.materials.append(m);groups.setdefault(g,[]).append(o);return o
def box(name,loc,dims,g,m=white,bevel=.002,collision=True):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  mod=o.modifiers.new('Soft used edges','BEVEL');mod.width=bevel;mod.segments=3;bpy.ops.object.modifier_apply(modifier=mod.name)
 reg(o,g,m)
 if collision:hulls.setdefault(g,[]).append((tuple(loc),tuple(dims),(0,0,0)))
 return o
def tube(name,pts,r,g,m=metal,collision=False):
 bpy.ops.object.select_all(action='DESELECT')
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=1;cu.bevel_depth=r;cu.bevel_resolution=3;cu.use_fill_caps=True
 sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
 for p,co in zip(sp.points,pts):p.co=(*co,1)
 ob=bpy.data.objects.new(name,cu);bpy.context.collection.objects.link(ob);bpy.context.view_layer.objects.active=ob;ob.select_set(True)
 bpy.ops.object.convert(target='MESH');ob=bpy.context.object;reg(ob,g,m)
 if collision:
  a,b=Vector(pts[0]),Vector(pts[-1]);hulls.setdefault(g,[]).append((tuple((a+b)/2),(2*r,2*r,(b-a).length),tuple((b-a).to_track_quat('Z','Y').to_euler())))
 return ob
for side,g in [(-1,'West'),(1,'East')]:
 # 5 mm end clearance; board is a normal thin plank, no deep front apron.
 box(g+' shelf',(side*.84,0,1.8625),(.4,1.67,.035),g)
 box(g+' wall cleat',(side*1.023,0,1.815),(.034,1.66,.06),g)
 for yy in (-.75,.04,.75):
  # Brackets at spare rail intervals; rail mounts hang below board at the ends.
  box(g+' bracket wall pad',(side*1.014,yy,1.756),(.035,.036,.17),g)
  tube(g+' bracket diagonal',[(side*1.008,yy,1.681),(side*.665,yy,1.833)],.009,g,metal,True)
  box(g+' bracket top arm',(side*.837,yy,1.833),(.362,.028,.018),g,metal,.002)
 railx=side*.76; railz=1.73
 tube(g+' rail',[(railx,-.82,railz),(railx,.82,railz)],.014,g,metal,True)
 for yy in (-.76,.76):
  tube(g+' rail support',[(railx,yy,1.842),(railx,yy,1.751)],.007,g,metal,True)
  # Split-collar shape connects support to rod without oversized geometry.
  pts=[(railx+.018*math.cos(a),yy,railz+.018*math.sin(a)) for a in [i*math.tau/40 for i in range(41)]]
  tube(g+' rail collar',pts,.004,g,metal)
 for i,(yy,ang) in enumerate([(-.55,-4),(-.33,3),(.27,-2),(.49,4)]):
  # Hooks lie in XZ, perpendicular to longitudinal Y rail. Inner apex rests at rod top.
  # The center offset makes the hook internally tangent to the rod, rather than floating above it.
  rot=math.radians(ang); cx=railx; cz=railz-.0065
  def point(x,z):return (cx+x*math.cos(rot),yy+x*math.sin(rot),z)
  points=[point(.024*math.cos(math.radians(a)),cz+.024*math.sin(math.radians(a))) for a in range(-35,226,5)]
  points += [point(-.012,railz-.037),point(-.004,railz-.052),point(0,railz-.068),point(0,1.616)]
  hanger_objects.append(tube(g+f' hook {i+1}',points,.0035,g,metal))
  # Rounded wooden shoulders and a trouser bar; stem enters the shoulder apex, not the rail.
  shape=[point(-.205,1.493),point(-.201,1.508),point(-.095,1.571),point(-.025,1.610),point(0,1.617),point(.025,1.610),point(.095,1.571),point(.201,1.508),point(.205,1.493)]
  hanger_objects.append(tube(g+f' hanger shoulders {i+1}',shape,.009,g,wood))
  hanger_objects.append(tube(g+f' hanger bar {i+1}',[point(-.205,1.493),point(.205,1.493)],.007,g,wood))
  tube(g+f' hook ferrule {i+1}',[point(0,1.609),point(0,1.624)],.006,g,metal)

def bounds(obs):
 vs=[o.matrix_world@Vector(c) for o in obs for c in o.bound_box]
 return {'min':[min(v[i] for v in vs) for i in range(3)],'max':[max(v[i] for v in vs) for i in range(3)]}
manifest={'asset_id':'BR-CLOSET-STORAGE-03','units':'metres','source_up':'+Z','source_front':'-Y','plan_origin':[1.10,4.70,0],
 'mapping':'planX=1.10+sourceX; planY=4.70-sourceY; planZ=sourceZ','shelf_top':1.88,'shelf_thickness':.035,'shelf_depth':.40,'shelf_length':1.67,'rail_z':1.73,'rail_wall_offset':.28,
 'hanger_hook':'open curved steel hook, internal apex tangent to 28mm diameter rail; triangle bodies perpendicular to rail','exports':[]}
for g,obs in groups.items():
 for o in obs:
  if not o.data.uv_layers:
   bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.01);bpy.ops.object.mode_set(mode='OBJECT')
 bpy.ops.object.select_all(action='DESELECT');copies=[]
 for o in obs:
  c=o.copy();c.data=o.data.copy();bpy.context.collection.objects.link(c);c.select_set(True);copies.append(c)
 bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();ob=bpy.context.object;ob.name='BR_ClosetStorage03_'+g
 sc.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');ob.location=(0,0,0);meshname=ob.name;coll=[]
 for i,(loc,dims,rot) in enumerate(hulls[g]):
  bpy.ops.mesh.primitive_cube_add(size=1,location=loc,rotation=rot);h=bpy.context.object;h.name=f'UCX_{meshname}_{i:02d}';h.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);coll.append(h)
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True)
 for h in coll:h.select_set(True)
 bpy.context.view_layer.objects.active=ob
 f=ROOT/'model'/f'{meshname}.fbx';bpy.ops.export_scene.fbx(filepath=str(f),use_selection=True,object_types={'MESH'},add_leaf_bones=False,apply_unit_scale=True,axis_forward='-Y',axis_up='Z',path_mode='RELATIVE')
 manifest['exports'].append({'file':'model/'+f.name,'mesh':meshname,'origin':[0,0,0],'bounds':bounds(obs),'ucx_hulls':len(coll)})
 for o in [ob]+coll:bpy.data.objects.remove(o,do_unlink=True)
west=manifest['exports'][0]['bounds']['max'][0];east=manifest['exports'][1]['bounds']['min'][0]
manifest['clear_central_aisle']=east-west;manifest['capsule_radius']=.38;manifest['centered_capsule_side_margin']=(east-west-.76)/2
(ROOT/'assembly.json').write_text(json.dumps(manifest,indent=2)+'\n')
# Preview-only existing closet doors open around their actual hinge offsets.
for side,g,angle in [(-1,'Door_L',-95),(1,'Door_R',95)]:
 pivot=Vector((side*.5,-.978,0));R=Matrix.Translation(pivot)@Matrix.Rotation(math.radians(angle),4,'Z')@Matrix.Translation(-pivot)
 # Original door objects identified from the leaf plane, not the preview shell.
 for o in list(bpy.data.objects):
  if o.type!='MESH' or o.name.startswith(('PREVIEW','BR_ClosetStorage')):continue
  if any(o in obs for obs in groups.values()):continue
  bb=bounds([o]);mn,mx=bb['min'],bb['max']
  if mn[1]<-.92 and mx[1]<-.90 and mn[0]>=-.515 and mx[0]<=.515 and (mn[0]+mx[0])*side>0:
   o.matrix_world=R@o.matrix_world
# Append new FIX-001 mold when available, without editing its source.
moldblend=ASSETS/'BR-MOLD-02/model/BR-MOLD-02.blend'
if moldblend.exists():
 with bpy.data.libraries.load(str(moldblend),link=False) as (src,dst):dst.objects=[n for n in src.objects if n in ('BR_Mold02_Back','BR_Mold02_Return')]
 for ob in dst.objects:
  if ob and ob.type=='MESH':bpy.context.collection.objects.link(ob)
cam=sc.camera
def camera(loc,target,lens):cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens
def render(name):
 if '--exports-only' in sys.argv:return
 sc.render.filepath=str(ROOT/'previews'/name);bpy.ops.render.render(write_still=True)
camera((.02,-1.65,1.55),(0,.35,1.78),18);render('closet-both-sides.png')
camera((.35,-.55,1.60),(-.79,.05,1.70),29);render('shelf-hangers-detail.png')
camera((.18,-.62,1.77),(-.76,-.33,1.70),54);render('hook-closeup.png')
camera((.02,-1.65,1.55),(0,.35,1.78),18)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'model/BR-CLOSET-STORAGE-03.blend'))
print('BR-CLOSET-STORAGE-03 source exports and previews complete.')
