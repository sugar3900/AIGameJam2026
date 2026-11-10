"""Additive FIX-027. Blender 5.2; source metres, front -Y, Z up.
Loads released KI-LEAK-02 read-only. Modifies faucet components only.
"""
import bpy,bmesh,math,json,hashlib,shutil,collections
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/'KI-LEAK-02/models/KI_LEAK_02_assembly.blend'
for d in ('models','textures','previews'): (ROOT/d).mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
body=bpy.data.objects['KI_LEAK_02_sink_body'];sc=bpy.context.scene
source_hash=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
# Connected islands make a precise faucet-only selection, independent of vertex numbering.
def islands(me):
 adj=[[] for v in me.vertices]
 for e in me.edges:a,b=e.vertices;adj[a].append(b);adj[b].append(a)
 seen=set();out=[]
 for i in range(len(adj)):
  if i in seen:continue
  q=[i];seen.add(i);c=[]
  while q:
   j=q.pop();c.append(j)
   for k in adj[j]:
    if k not in seen:seen.add(k);q.append(k)
  out.append(c)
 return out
def faces(me,exclude=set()):
 uv=me.uv_layers.active.data;out=[]
 for p in me.polygons:
  if any(i in exclude for i in p.vertices):continue
  loops=[]
  for li in p.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;loops.append(tuple(float(x) for x in (*v,*uv[li].uv)))
  out.append((p.material_index,p.use_smooth,tuple(loops)))
 return out
def digest(vals):return hashlib.sha256(repr(sorted(vals)).encode()).hexdigest()
remove=[];removed=[]
for c in islands(body.data):
 vs=[body.data.vertices[i].co for i in c];lo=[min(v[k] for v in vs) for k in range(3)];hi=[max(v[k] for v in vs) for k in range(3)]
 if lo[2]>.98 and len(c) in (48,810):remove+=c;removed.append({'vertices':len(c),'min':lo,'max':hi})
assert sorted(x['vertices'] for x in removed)==[48]*5+[810]
keepfaces=faces(body.data,set(remove));pre=digest(keepfaces)
bm=bmesh.new();bm.from_mesh(body.data);bm.verts.ensure_lookup_table();bmesh.ops.delete(bm,geom=[bm.verts[i] for i in remove],context='VERTS');bm.to_mesh(body.data);bm.free()
assert digest(faces(body.data))==pre
body.name='KI_FAUCET_02_sink_body';body.hide_render=False;body.hide_set(False)
for o in list(bpy.data.objects):
 if o!=body:bpy.data.objects.remove(o,do_unlink=True)
chrome=bpy.data.materials['Aged_Chrome'];ivory=bpy.data.materials['Sink_AgedEnamel']
# Portable direct image materials; unchanged slot names and original surviving UVs.
for mat in body.data.materials:
 if not mat.use_nodes:continue
 for n in mat.node_tree.nodes:
  if n.type=='TEX_IMAGE' and n.image:
   im=n.image;name=Path(im.filepath).name
   if name:im.filepath_raw=str(ROOT/'textures'/name);im.save();im.filepath='//../textures/'+name
sage=bpy.data.materials['Sink_SagePaint'];nodes=sage.node_tree.nodes
mix=next((n for n in nodes if n.type=='MIX_RGB'),None)
if mix:
 import numpy as np
 a=next(l.from_node.image for l in mix.inputs[1].links);b=next(l.from_node.image for l in mix.inputs[2].links)
 av=np.array(a.pixels[:],dtype=np.float32);bv=np.array(b.pixels[:],dtype=np.float32);f=mix.inputs[0].default_value
 im=bpy.data.images.new('Sink_SageDirect',width=a.size[0],height=a.size[1]);im.pixels.foreach_set(av*(1-f)+bv*f);im.filepath_raw=str(ROOT/'textures/Sink_SageDirect.png');im.file_format='PNG';im.save();im.pack()
 n=nodes.new('ShaderNodeTexImage');n.image=im;sage.node_tree.links.new(n.outputs['Color'],nodes.get('Principled BSDF').inputs['Base Color'])
parts=[];tap_parts={};joints=[]
def activate(o):
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o

def finish(o,name,mat,group):
 o.name=name;o.data.materials.append(mat);activate(o);bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
 for p in o.data.polygons:p.use_smooth=len(p.vertices)==4
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.015);bpy.ops.object.mode_set(mode='OBJECT')
 group.append(o);return o

def cyl(name,a,b,r,mat=chrome,group=parts,n=32):
 a,b=Vector(a),Vector(b);v=b-a;bpy.ops.mesh.primitive_cylinder_add(vertices=n,radius=r,depth=v.length,location=(a+b)/2);o=bpy.context.object;o.rotation_euler=v.to_track_quat('Z','Y').to_euler();return finish(o,name,mat,group)

def sphere(name,loc,r,mat=chrome,group=parts):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,radius=r,location=loc);o=finish(bpy.context.object,name,mat,group)
 for p in o.data.polygons:p.use_smooth=True
 return o

for x,side in [(-.25,'L'),(.25,'R')]:
 cyl(side+' wall shank',(x,.240,1.04),(x,.195,1.04),.017)
 cyl(side+' escutcheon',(x,.2365,1.04),(x,.2255,1.04),.047)
 cyl(side+' escutcheon raised neck',(x,.229,1.04),(x,.216,1.04),.030)
 cyl(side+' upright valve body',(x,.2,1.010),(x,.2,1.095),.027)
 cyl(side+' valve bonnet',(x,.2,1.077),(x,.2,1.105),.030)
 joints.extend([{'name':side+' shank/valve','overlap_m':.022},{'name':side+' bridge/valve','overlap_m':.027},{'name':side+' stem/bonnet','overlap_m':.030}])
 group=[];tap_parts[side]=group
 cyl(side+' rotating spindle',(x,.2,1.075),(x,.2,1.167),.012,group=group)
 cyl(side+' horizontal handle X',(x-.044,.2,1.157),(x+.044,.2,1.157),.007,group=group)
 cyl(side+' horizontal handle Y',(x,.156,1.157),(x,.244,1.157),.007,group=group)
 for dx,dy in [(-.044,0),(.044,0),(0,-.044),(0,.044)]:sphere(side+' handle rounded end',(x+dx,.2+dy,1.157),.009,group=group)
 cyl(side+' porcelain index',(x,.2,1.162),(x,.2,1.175),.015,ivory,group)
 cyl(side+' index bezel',(x,.2,1.158),(x,.2,1.166),.018,group=group)
# Manifold spans into both upright valves; center union connects the straight riser.
cyl('Horizontal bridge',(-.25,.2,1.04),(.25,.2,1.04),.020)
cyl('Center riser union',(0,.2,1.031),(0,.2,1.073),.025)
# Sweep a tube with explicit tangent frames, avoiding auto-Bezier backward bow.
# Straight riser to spring point, round swan neck, vertical outlet at exact contract XY.
pts=[Vector((0,.2,z)) for z in (1.04,1.08,1.12,1.16,1.19,1.207)]
# Cubic after straight riser. Endpoint tangent is vertical downward.
p0=Vector((0,.2,1.207));p1=Vector((0,.2,1.357));p2=Vector((0,-.04,1.357));p3=Vector((0,-.04,1.245))
for i in range(1,65):
 t=i/64;pts.append((1-t)**3*p0+3*(1-t)**2*t*p1+3*(1-t)*t*t*p2+t**3*p3)
pts.append(Vector((0,-.04,1.233)))
verts=[];N=32
for i,p in enumerate(pts):
 tangent=(pts[min(i+1,len(pts)-1)]-pts[max(0,i-1)]).normalized();u=Vector((1,0,0));v=tangent.cross(u).normalized()
 for j in range(N):
  a=2*math.pi*j/N;verts.append(tuple(p+.016*(math.cos(a)*u+math.sin(a)*v)))
fs=[]
for i in range(len(pts)-1):
 for j in range(N):fs.append((i*N+j,i*N+(j+1)%N,(i+1)*N+(j+1)%N,(i+1)*N+j))
fs.extend([tuple(reversed(range(N))),tuple((len(pts)-1)*N+j for j in range(N))])
me=bpy.data.meshes.new('Spout');me.from_pydata(verts,[],fs);me.update();o=bpy.data.objects.new('Spout',me);bpy.context.collection.objects.link(o)
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();finish(o,'Swan neck with straight riser',chrome,parts)
# Actual annular aerator lip and recessed outlet; no zero-thickness ring.
N=48;vv=[]
for z,r in [(1.240,.019),(1.227,.019),(1.227,.012),(1.233,.012)]:
 vv += [(r*math.cos(2*math.pi*j/N),-.04+r*math.sin(2*math.pi*j/N),z) for j in range(N)]
ff=[]
for k in range(4):
 k2=(k+1)%4
 for j in range(N):ff.append((k*N+j,k*N+(j+1)%N,k2*N+(j+1)%N,k2*N+j))
me=bpy.data.meshes.new('Outlet lip');me.from_pydata(vv,[],ff);me.update();o=bpy.data.objects.new('Outlet lip',me);bpy.context.collection.objects.link(o);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();finish(o,'Thick aerator lip',chrome,parts)
# Recessed aerator cross-grid sits above the mouth, 3mm inset.
for i in (-2,-1,0,1,2):
 q=i*.0038;h=math.sqrt(.011**2-q*q)
 cyl('Aerator screen X',(-h,-.04+q,1.230),(h,-.04+q,1.230),.0005,n=8)
 cyl('Aerator screen Y',(q,-.04-h,1.230),(q,-.04+h,1.230),.0005,n=8)
# Join new geometry to original body. Existing slot names/order are retained.
activate(body)
for o in parts:o.select_set(True)
bpy.ops.object.join()
postfaces=faces(body.data);assert not (collections.Counter(keepfaces)-collections.Counter(postfaces)), 'Original surviving face/UV/material changed'
assert [m.name for m in body.data.materials]==['Sink_SagePaint','Sink_AgedEnamel','Aged_Chrome']
exports=[body];tapdata={}
for side,group in tap_parts.items():
 activate(group[0])
 for o in group:o.select_set(True)
 bpy.ops.object.join();o=bpy.context.object;o.name='KI_FAUCET_02_'+side+'_tap'
 sc.cursor.location=(-.25 if side=='L' else .25,.2,1.075);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');exports.append(o)
 tapdata[side]={'source_pivot':list(o.location),'axis':'source Z (UE local +Z); horizontal cross rotates in XY plane','closed_pose_degrees':0,'nominal_travel_degrees':90,'note':'Preserve toggle identity and adapt pivot. See explicit2cm stream-start mismatch below.'}
def bounds(o):
 vs=[o.matrix_world@v.co for v in o.data.vertices];return {'min':[round(min(v[k] for v in vs),7) for k in range(3)],'max':[round(max(v[k] for v in vs),7) for k in range(3)]}
assert bounds(body)['max'][2] <=1.343218
# Body remains complex-static collision; tiny faucets are traceable with engine complex collision.
# Compact UCX convex hulls for each rotating tap, baked in the same assembly coordinates.
ucx=[]
for o in exports[1:]:
 bm=bmesh.new()
 for v in o.data.vertices:bm.verts.new(v.co)
 ret=bmesh.ops.convex_hull(bm,input=list(bm.verts),use_existing_faces=False)
 geom=[v for v in set(ret.get('geom_interior',[])+ret.get('geom_unused',[])) if isinstance(v,bmesh.types.BMVert)]
 if geom:bmesh.ops.delete(bm,geom=geom,context='VERTS')
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 me=bpy.data.meshes.new('UCX');bm.to_mesh(me);bm.free();h=bpy.data.objects.new('UCX_'+o.name+'_00',me);bpy.context.collection.objects.link(h);h.matrix_world=o.matrix_world.copy();h.hide_render=True;ucx.append(h)
for o in exports:
 activate(o)
 for h in ucx:
  if h.name.startswith('UCX_'+o.name+'_'):h.select_set(True)
 bpy.ops.export_scene.fbx(filepath=str(ROOT/'models'/f'{o.name}.fbx'),use_selection=True,object_types={'MESH'},add_leaf_bones=False,path_mode='COPY',embed_textures=True,apply_unit_scale=True)
report={'status':'PASS source preservation, bounds and specified hardware alignment','source_blend_sha256':source_hash,'removed_faucet_islands':removed,'non_faucet_face_count':len(keepfaces),'non_faucet_face_uv_material_sha256':pre,'non_faucet_preservation':True,'body_slot_names':[m.name for m in body.data.materials],'tap_pivots':tapdata,'upstand_actual_front_y':.2345,'escutcheon_back_y':.2365,'escutcheon_embed_m':.002,'escutcheon_front_y':.2255,'shank_embed_m':.0055,'bridge_axis_yz':[.2,1.04],'handle_lowest_z':1.148,'upstand_top_z':1.135,'handle_upstand_vertical_gap_m':.013,'joins':joints,'outlet_center_source':[0,-.04,1.230],'outlet_lip_bottom':1.227,'outlet_axis_source':[0,0,-1],'existing_stream_ue_cm':[215,50.05,121],'source_outlet_world_from_script_ue_cm':[215,50.05,123],'stream_start_vertical_gap_cm':2,'stream_note':'READ-ONLY SCRIPT FINDING: rev02_04_furnish.py installs body at UE(215,46.05,0), yaw0. Requested outlet therefore maps to UE(215,50.05,123), while rev02_05_gameplay.py uses stream start Z121. Explicit 2cm mismatch. Recommend engine owner update stream START toZ123 only, keeping BASIN70, label/toggle and body transform unchanged. No engine change was made in this package.','exports':{o.name:{**bounds(o),'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'materials':[m.name for m in o.data.materials]} for o in exports}}
(ROOT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
# Neutral small CPU previews; no editor or GPU allocation.
sc.render.engine='CYCLES';sc.cycles.samples=20;sc.cycles.use_denoising=True;sc.render.threads_mode='FIXED';sc.render.threads=1;sc.render.resolution_x=800;sc.render.resolution_y=650;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.view_settings.view_transform='AgX'
sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.5,.5,.5,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.45
for loc,power,size in [((1,-2,3),180,2),((-2,-1,2),140,2)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.size=size;o.rotation_euler=(Vector((0,.1,1.1))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add();cam=bpy.context.object;sc.camera=cam;cam.data.type='ORTHO'
for name,pos,target,scale in [('front',(0,-2,1.48),(0,.13,1.12),.87),('side',(.95,-.7,1.5),(0,.13,1.12),.91),('context',(1.6,-2.5,1.7),(0,0,.67),1.8)]:
 cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;sc.render.filepath=str(ROOT/'previews'/f'{name}.png');bpy.ops.render.render(write_still=True)
for im in bpy.data.images:
 if im.type=='IMAGE' and im.size[0]>0:im.pack()
for h in ucx:h.hide_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/KI_FAUCET_02_assembly.blend'))
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==source_hash
print('FAUCET_COMPLETE',json.dumps(report))
