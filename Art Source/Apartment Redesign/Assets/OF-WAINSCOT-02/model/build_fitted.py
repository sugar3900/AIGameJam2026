from pathlib import Path
import bpy,bmesh,math,json
from mathutils import Vector,Matrix
from mathutils.geometry import tessellate_polygon
P=Path(__file__).resolve().parent.parent;A=P.parent
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
ORIGIN=(7.96,5.66,0)
def src(p):return (p[0]-ORIGIN[0],ORIGIN[1]-p[1],p[2])
def mat(name,color,rough=.8,texture=None):
 m=bpy.data.materials.new(name);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*color,1);b.inputs['Roughness'].default_value=rough
 if texture:
  t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(texture),check_existing=True);t.image.pack();m.node_tree.links.new(t.outputs['Color'],b.inputs['Base Color'])
 m.diffuse_color=(*color,1);return m
paint=mat('OF02_Painterly_Ivory',(.8,.76,.65),.8,P/'textures/painted-ivory.png')
# Six wall faces, in plan metres. End slopes form exact continuous 45-degree joints.
RUNS={
'N':dict(axis='x',plane=5.66,normal=1,a=7.96,b=10.69,start=1,end=-1),
'CS':dict(axis='y',plane=10.69,normal=-1,a=5.66,b=7.21,start=1,end=1),
'WF':dict(axis='x',plane=7.21,normal=1,a=10.69,b=11.94,start=-1,end=-1),
'E':dict(axis='y',plane=11.94,normal=-1,a=7.21,b=9.49,start=1,end=-1),
'S':dict(axis='x',plane=9.49,normal=-1,a=7.96,b=11.94,start=1,end=-1),
'W':dict(axis='y',plane=7.96,normal=1,a=5.66,b=9.49,start=1,end=-1)}
GROUPS={k:[] for k in RUNS};front_depth=.007

def pos(k,u,d,z):
 r=RUNS[k];p=(u,r['plane']+r['normal']*d,z) if r['axis']=='x' else (r['plane']+r['normal']*d,u,z)
 return src(p)
def shape(k,name,verts,faces,bevel=0):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);me.materials.append(paint)
 # Recalculate normals after plan-to-source reflection; triangulation remains reproducible.
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 if bevel:
  bpy.context.view_layer.objects.active=o;o.select_set(True);b=o.modifiers.new('Tiny painted edge easing','BEVEL');b.width=bevel;b.segments=2;bpy.ops.object.modifier_apply(modifier=b.name);o.select_set(False)
 uv=me.uv_layers.new(name='WorldPaint') if not me.uv_layers else me.uv_layers[0]
 for f in me.polygons:
  for li in f.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co
   # Along-wall and vertical UVs retain the original paint texture scale.
   uv.data[li].uv=(v.x if RUNS[k]['axis']=='x' else -v.y,v.z)
 GROUPS[k].append(o);return o

def profile(k,name,a,b,poly,sm=None,em=None):
 # Closed polygon in depth/height extruded along a wall; miter all profile layers together.
 r=RUNS[k];sm=(r['start'] if abs(a-r['a'])<1e-6 else 0) if sm is None else sm;em=(r['end'] if abs(b-r['b'])<1e-6 else 0) if em is None else em
 verts=[pos(k,a+sm*d,d,z) for d,z in poly]+[pos(k,b+em*d,d,z) for d,z in poly];n=len(poly)
 faces=[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 return shape(k,name,verts,faces)
def bar(k,name,a,b,z0,z1,d0=.001,d1=.012,sm=None,em=None):return profile(k,name,a,b,[(d0,z0),(d1,z0),(d1,z1),(d0,z1)],sm,em)
def backing(k,name,outline):
 # Non-rectangular backing fits window sill/apron without compressed profiles.
 r=RUNS[k];verts=[pos(k,u+(r['start']*d if abs(u-r['a'])<1e-8 else r['end']*d if abs(u-r['b'])<1e-8 else 0),d,z) for d in (.001,.007) for u,z in outline];n=len(outline)
 faces=[]
 for offset in (0,n):
  vv=[Vector((u,z,0)) for u,z in outline]
  for tri in tessellate_polygon([vv]):faces.append(tuple(offset+(q if isinstance(q,int) else next(i for i,v in enumerate(vv) if (v-q).length<1e-8)) for q in tri))
 faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 return shape(k,name,verts,faces)
def railset(k,a,b,h,base=True):
 if base:
  profile(k,'Continuous skirting',a,b,[(.001,0),(.018,0),(.018,.115),(.016,.132),(.012,.140),(.001,.140)])
  profile(k,'Continuous base bead',a,b,[(.001,.140),(.014,.140),(.016,.145),(.014,.151),(.001,.151)])
  bar(k,'Continuous lower rail',a,b,.160,.240)
 bar(k,'Continuous top rail',a,b,h-.140,h-.060)
 profile(k,'Continuous chair lower',a,b,[(.001,h-.060),(.014,h-.060),(.017,h-.050),(.017,h-.037),(.001,h-.037)])
 profile(k,'Continuous chair cap',a,b,[(.001,h-.037),(.019,h-.037),(.022,h-.030),(.022,h-.008),(.019,h),(.001,h)])
def bays(k,a,b,h,preferred=.53):
 # Fixed60mm stiles, independent of bay width. Tiny returns remain plain rather than crushed panels.
 length=b-a
 if length<.20:
  bar(k,'Plain fitted narrow return',a,b,.240,h-.140,.007,.012);return
 count=max(1,round(length/preferred));cuts=[a+(b-a)*j/count for j in range(count+1)]
 if k=='N' and a<8.0:cuts=[a,8.60,b]
 count=len(cuts)-1;w=.060
 for j in range(count+1):
  c=cuts[j];lo=a if j==0 else b-w if j==count else c-w/2;hi=b if j==count else a+w if j==0 else c+w/2
  bar(k,'Fixed60mm stile',lo,hi,.240,h-.140,.007,.012)
 for j in range(count):
  lo=cuts[j]+(w if j==0 else w/2)+.020;hi=cuts[j+1]-(w if j==count-1 else w/2)-.020
  z0=.267;z1=h-.167
  if hi-lo<.08 or z1-z0<.08:continue
  for u in [lo,hi-.012]:bar(k,'Inset vertical bead',u,u+.012,z0,z1,.007,.014,0,0)
  for zz in [z0,z1-.012]:bar(k,'Inset horizontal bead',lo+.012,hi-.012,zz,zz+.012,.007,.014,0,0)
# North door outer casing edges9.390..10.560. Wardrobe casing10.840..11.920.
segments={'N':[(7.96,9.388),(10.562,10.69)],'CS':[(5.66,7.21)],'WF':[(10.69,10.838),(11.922,11.94)],'E':[(7.239,9.49)],'W':[(5.66,9.49)]}
for k,segs in segments.items():
 for a,b in segs:
  if k=='WF' and a>11.9:
   bar(k,'Plain7mm wardrobe corner return',a,b,0,1.10,.001,.007);continue
  bar(k,'Fitted backing',a,b,0,1.10,.001,.007);railset(k,a,b,1.10);bays(k,a,b,1.10)
# South fitted opening. Casing edges9.6125/11.1875; sill edges9.59/11.21, bottom.8715/top.9165.
a,b=7.96,11.94;l,r=9.6105,11.1895;sl,sr=9.588,11.212;low=.778
outline=[(a,0),(b,0),(b,1.10),(r,1.10),(r,.9185),(sr,.9185),(sr,.8695),(r,.8695),(r,low),(l,low),(l,.8695),(sl,.8695),(sl,.9185),(l,.9185),(l,1.10),(a,1.10)]
backing('S','Continuous notched south backing',outline)
# Base/lower rails stay continuous across the whole window wall.
profile('S','Continuous skirting',a,b,[(.001,0),(.018,0),(.018,.115),(.016,.132),(.012,.140),(.001,.140)])
profile('S','Continuous base bead',a,b,[(.001,.140),(.014,.140),(.016,.145),(.014,.151),(.001,.151)])
bar('S','Continuous lower rail',a,b,.160,.240)
for aa,bb,h in [(a,l,1.10),(l,r,low),(r,b,1.10)]:railset('S',aa,bb,h,base=False);bays('S',aa,bb,h)
# Sill relief cuts affect backing/stiles/beads, not rail proportions; exact source bounds plus2mm.
def cut(o,lo,hi):
 c0=Vector(src(lo));c1=Vector(src(hi));bpy.ops.mesh.primitive_cube_add(size=1,location=(c0+c1)/2);c=bpy.context.object;c.dimensions=[abs(c1[i]-c0[i]) for i in range(3)];bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 bpy.context.view_layer.objects.active=o;mod=o.modifiers.new('Exact sill relief','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=c;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(c,do_unlink=True)
for o in list(GROUPS['S']):
 if 'backing' in o.name:continue
 bounds=[o.matrix_world@Vector(c) for c in o.bound_box];xs=[v.x+7.96 for v in bounds];zs=[v.z for v in bounds]
 if min(xs)<sr and max(xs)>sl and min(zs)<.9185 and max(zs)>.8695:cut(o,(sl,9.30,.8695),(sr,9.50,.9185))
# Material UV layers survive joins and Boolean relief. Exports use a common floor origin.
exports=[]
for k,parts in GROUPS.items():
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();o=parts[0];o.name='OF_Wainscot02_'+k;bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-8);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
 bpy.ops.export_scene.fbx(filepath=str(P/'model'/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,add_leaf_bones=False)
 vv=[v.co for v in o.data.vertices];exports.append(dict(file='model/'+o.name+'.fbx',wall=k,origin=[0,0,0],min=[min(v[i] for v in vv) for i in range(3)],max=[max(v[i] for v in vv) for i in range(3)]))
# Import the actual source frame meshes as preview/fit evidence, excluding collision.
def context_fbx(path,origin,angle,label):
 before=set(bpy.context.scene.objects);bpy.ops.import_scene.fbx(filepath=str(path));T=Matrix.Translation(Vector(src(origin)))@Matrix.Rotation(angle,4,'Z');created=[]
 for o in set(bpy.context.scene.objects)-before:
  if o.type!='MESH' or o.name.startswith('UCX_'):bpy.data.objects.remove(o,do_unlink=True);continue
  o.matrix_world=T@o.matrix_world;o.name='Context_'+label+'_'+o.name;created.append(o)
 return created
context=[]
context+=context_fbx(A/'ARC-DOOR-02/model/ARC_Door02_Frame.fbx',(9.975,5.60,0),0,'Door')
context+=context_fbx(A/'ARC-SLIDING-CLOSET-02/model/ARC_Sliding02_Frame.fbx',(11.38,7.15,0),0,'Wardrobe')
context+=context_fbx(A/'ARC-WINDOW-OFFICE-01/model/ARC_Window_frame.fbx',(10.40,9.55,0),math.pi,'Window')
# Preview plaster wall surfaces and warm floor, excluded from exports.
plaster=mat('Context warm plaster',(.49,.37,.23),.91);floor=mat('Context old wood',(.22,.11,.045),.85)
def cube(name,center,size,m):
 bpy.ops.mesh.primitive_cube_add(size=1,location=src(center));o=bpy.context.object;o.name=name;o.dimensions=size;o.data.materials.append(m);return o
for k,r in RUNS.items():
 # Only upper plaster; viewable context does not hide window/door openings.
 for aa,bb in ([(7.96,9.45),(10.50,10.69)] if k=='N' else [(10.72,10.90),(11.86,11.94)] if k=='WF' else [(r['a'],9.70),(11.10,r['b'])] if k=='S' else [(r['a'],r['b'])]):
  if r['axis']=='x':cube('Context plaster '+k,((aa+bb)/2,r['plane']-r['normal']*.015,1.35),(bb-aa,.03,2.70),plaster)
  else:cube('Context plaster '+k,(r['plane']-r['normal']*.015,(aa+bb)/2,1.35),(.03,bb-aa,2.70),plaster)
cube('Context wall above window',(10.40,9.505,2.50),(1.40,.03,.40),plaster)
cube('Context wall below window',(10.40,9.505,.45),(1.624,.03,.90),plaster)
cube('Context floor',(9.9,7.6,-.025),(4.5,4.5,.05),floor)
# Add reference overlay at same identity region, reprojected to new recessed face.
context_fbx(A/'BR-WAINSCOT-01/model/BR_Wainscot_Damage.fbx',(0,0,0),0,'LeadPaint')
lead=[o for o in bpy.context.scene.objects if o.name.startswith('Context_LeadPaint')][0]
lead.scale.x*=1.49;bpy.context.view_layer.update()
# This overlay is world-baked in its source coordinates; centre it without scaling its pattern.
bounds=[lead.matrix_world@Vector(c) for c in lead.bound_box];center=sum(bounds,Vector())/8;lead.location+=Vector(src((8.925,5.668,.70)))-center
# Resolve FBX absolute-path duplication for preview materials without changing original kits.
for im in bpy.data.images:
 if im.source=='FILE' and not Path(bpy.path.abspath(im.filepath)).exists():
  matches=list(A.rglob(Path(im.filepath).name))
  if matches:im.filepath=str(matches[0]);im.reload()
scene=bpy.context.scene;scene.world=bpy.data.worlds.new('Context World');scene.world.color=(.30,.30,.30);scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True;scene.render.resolution_x=1400;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
for pos0,energy,size in [((9.7,7.6,3.3),210,3),((8.3,8.7,2.0),100,2)]:
 bpy.ops.object.light_add(type='AREA',location=src(pos0));l=bpy.context.object;l.data.energy=energy;l.data.size=size;l.rotation_euler=(Vector(src((9.9,7.6,.8)))-l.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add();cam=bpy.context.object;cam.data.type='PERSP';cam.data.lens=34;scene.camera=cam
views=[('north-door-corner',(8.2,8.0,1.70),(9.80,5.8,.85)),('wardrobe-outside-corner',(8.8,8.55,1.6),(10.75,6.9,.65)),('under-window',(9.5,6.5,1.60),(10.30,9.48,.72)),('tight-wardrobe-corner',(10.9,8.1,1.25),(11.90,7.24,.92))]
for name,eye,target in views:
 cam.location=src(eye);cam.rotation_euler=(Vector(src(target))-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(P/'previews'/(name+'.png'));bpy.ops.render.render(write_still=True)
manifest=dict(asset='OF-WAINSCOT-02',units='metres',up='+Z',source_to_plan='(7.96+sourceX,5.66-sourceY,sourceZ)',common_origin_plan=[7.96,5.66,0],ue_import='X kept / Y flipped; all six exports at (796,566,0)cm, yaw0, scale1',max_projection_m=.022,engine_corner_shell_check=dict(bounds_plan_min=[10.69,7.15,0],bounds_plan_max=[10.75,7.21,2.75],note='Existing Rev02 shell generator leaves this60mm outer quadrant uncovered; verify current map and extend one wall or fill with matching plaster. Source trim assumes square corner at10.69,7.21.'),end_treatment='Closed painted profile end caps at casing gaps; no open extrusion ends.',wardrobe_east_corner=dict(plain_return_x=[11.922,11.94],plain_return_depth=.007,east_run_start_y=7.239,casing_front_y=7.237,gap=.002,note='22mm full cap cannot fit the20mm casing-to-wall sliver; plain backing return and casing-aware east termination avoid overlap.'),exports=exports,wall_faces=RUNS,door_casing_x=[9.390,10.560],wardrobe_casing_x=[10.840,11.920],window_casing_x=[9.6125,11.1875],window_sill_x=[9.59,11.21],window_sill_z=[.8715,.9165],window_apron_bottom_z=.783,under_window_cap_z=.778,gaps=dict(casing=.002,sill=.002,apron=.005),lead_paint=dict(preserve_label='Damage_BR_LeadPaint',center_plan=[8.925,5.668,.70],surface_plane_y=5.667,overlay_offset_m=.001,clear_recess_x=[8.662,9.296],expected_patch_width_m=.4619,expected_patch_height_m=.22,preserve='Existing overlay texture, alpha material, tags and identity; only reproject to thinner north face. Source patch width/height and current engine scale remain.'),collision='No new blocking collision; existing structural wall supplies collision.',material=dict(texture='textures/painted-ivory.png',srgb=True,base_color='direct texture; no multiply',roughness=.8,metallic=0))
(P/'assembly.json').write_text(json.dumps(manifest,indent=2)+'\n')
for im in bpy.data.images:
 if im.source=='FILE':
  try:im.pack()
  except RuntimeError:pass
bpy.ops.wm.save_as_mainfile(filepath=str(P/'model/OF-WAINSCOT-02.blend'));print('OF-WAINSCOT-02 built and rendered')
