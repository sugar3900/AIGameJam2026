"""KI-LEAK-02; Blender 5.x, metres, assembly origin unchanged from narrow sink.
Run: Blender -b -t 2 --python-exit-code 1 --python build_leak.py
Only writes this directory. Loads original assembly read-only; never rebuilds its UVs.
"""
import bpy, bmesh, math, json, hashlib, shutil
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import numpy as np
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/'KI-SINK-NARROW-01/models/KI_SINK_NARROW_assembly.blend'
for d in ('models','textures','previews'): (ROOT/d).mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
sc=bpy.context.scene
body=bpy.data.objects['KI_SINK_NARROW_body']
original_hash=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
def components(me):
 adj=[[] for v in me.vertices]
 for e in me.edges:
  a,b=e.vertices;adj[a].append(b);adj[b].append(a)
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
def bounds(o):
 vs=[o.matrix_world@v.co for v in o.data.vertices]
 return {'min':[round(min(v[k] for v in vs),6) for k in range(3)],'max':[round(max(v[k] for v in vs),6) for k in range(3)]}
remove=[];removed=[];trap=None
for c in components(body.data):
 vs=[body.data.vertices[i].co for i in c]
 lo=[min(v[k] for v in vs) for k in range(3)];hi=[max(v[k] for v in vs) for k in range(3)]
 if lo[0]>-.30 and hi[0]<.06 and hi[2]<.37:
  remove.extend(c);removed.append({'vertices':len(c),'min':lo,'max':hi})
 if len(c)==1210:trap=c
assert sorted(x['vertices'] for x in removed)==[192,810],removed
assert trap is not None
trapset=set(trap)
trapverts=[body.matrix_world@v.co for v in body.data.vertices]
trapfaces=[tuple(p.vertices) for p in body.data.polygons if set(p.vertices)<=trapset]
trap_bvh=BVHTree.FromPolygons(trapverts,trapfaces)
def face_digest(me,exclude=set()):
 vals=[];uv=me.uv_layers.active.data
 for p in me.polygons:
  if any(i in exclude for i in p.vertices):continue
  loop=[]
  for li in p.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co
   loop.append(tuple(round(float(x),7) for x in (*v,*uv[li].uv)))
  vals.append((p.material_index,p.use_smooth,tuple(loop)))
 return hashlib.sha256(repr(sorted(vals)).encode()).hexdigest()
before=face_digest(body.data,set(remove))
bm=bmesh.new();bm.from_mesh(body.data);bm.verts.ensure_lookup_table()
bmesh.ops.delete(bm,geom=[bm.verts[i] for i in remove],context='VERTS');bm.to_mesh(body.data);bm.free()
after=face_digest(body.data);assert before==after,'Surviving source faces or UV changed'
body.name='KI_LEAK_02_sink_body'
bpy.data.objects.remove(bpy.data.objects['KI_SINK_NARROW_damage'],do_unlink=True)
for o in list(bpy.data.objects):
 if o.type in ('CAMERA','LIGHT'):bpy.data.objects.remove(o,do_unlink=True)
# Keep inherited texture dependencies portable and intact.
for img in bpy.data.images:
 if img.type=='IMAGE' and img.size[0]>0:
  name=Path(img.filepath).name
  if name:
   img.filepath_raw=str(ROOT/'textures'/name);img.save();img.filepath='//../textures/'+name
def material(name,color,metal=.0,rough=.5):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1)
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 return m
zinc=material('KI_LEAK_02_Painted_Zinc',(.45,.49,.50),.72,.49)
img=bpy.data.images.load(str(ROOT/'textures/T_Bucket_Zinc_BaseColor.png'),check_existing=True)
img.pack();n=zinc.node_tree.nodes;t=n.new('ShaderNodeTexImage');t.image=img;p=n.get('Principled BSDF');zinc.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
# Derived material channels, not baked illumination. Non-color maps are portable.
pix=np.empty(len(img.pixels),dtype=np.float32);img.pixels.foreach_get(pix);rgba=pix.reshape((-1,4))
lum=(rgba[:,:3]*np.array([.2126,.7152,.0722])).sum(axis=1)
for name,values in [('Roughness',np.clip(.65-lum*.24,.43,.62)),('Metallic',np.full_like(lum,.72))]:
 im=bpy.data.images.new('T_Bucket_Zinc_'+name,width=img.size[0],height=img.size[1]);im.colorspace_settings.name='Non-Color'
 a=np.ones_like(rgba);a[:,:3]=values[:,None];im.pixels.foreach_set(a.ravel());im.filepath_raw=str(ROOT/'textures'/('T_Bucket_Zinc_'+name+'.png'));im.file_format='PNG';im.save();im.pack()
 node=n.new('ShaderNodeTexImage');node.image=im;zinc.node_tree.links.new(node.outputs['Color'],p.inputs[name])
edge=material('KI_LEAK_02_Dark_Worn_Seams',(.21,.235,.245),.64,.55)
wiremat=material('KI_LEAK_02_Worn_Iron_Bail',(.16,.175,.18),.74,.42)
parts=[];cx=-.12;cy=-.055
def mesh(name,verts,faces,mat):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);o.data.materials.append(mat);return o
def activate(o):
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
def smart(o):
 activate(o);bpy.ops.object.transform_apply(location=False,rotation=True,scale=True);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT')
N=96
# Thin pressed sheet, genuinely hollow. Slight broad dents; no chunky faceting.
profile=[(.008,.114),(.013,.115),(.025,.117),(.052,.122),(.10,.131),(.15,.139),(.18,.144),(.215,.149),(.228,.150),(.228,.1482),(.215,.1472),(.18,.1422),(.15,.1372),(.10,.1292),(.052,.1202),(.025,.1152),(.013,.1122)]
verts=[]
for z,r in profile:
 for i in range(N):
  a=2*math.pi*i/N;dent=.0012*math.sin(3*a+.4)*math.sin(math.pi*(z-.008)/.22)**2
  dent-=.0018*math.exp(-((a-4.5)/.27)**2-((z-.13)/.07)**2)
  verts.append((cx+(r+dent)*math.cos(a),cy+(r+dent)*math.sin(a),z))
faces=[]
for j in range(len(profile)-1):
 for i in range(N):faces.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i))
faces.extend([tuple(reversed(range(N))),tuple((len(profile)-1)*N+i for i in range(N))])
shell=mesh('Pressed zinc shell',verts,faces,zinc);parts.append(shell)
uv=shell.data.uv_layers.new(name='UVMap')
for poly in shell.data.polygons:
 poly.use_smooth=True
 if poly.index<(len(profile)-1)*N:
  row=poly.index//N;i=poly.index%N
  # Continuous cylindrical unwrap with explicit seam. Interior uses same map scale.
  for li,(u,v) in zip(poly.loop_indices,[(i/N,profile[row][0]/.23),((i+1)/N,profile[row][0]/.23),((i+1)/N,profile[row+1][0]/.23),(i/N,profile[row+1][0]/.23)]):uv.data[li].uv=(u,v)
 else:
  for li in poly.loop_indices:
   co=shell.data.vertices[shell.data.loops[li].vertex_index].co;uv.data[li].uv=((co.x-cx)/.3+.5,(co.y-cy)/.3+.5)
def torus(name,r,minor,z,mat):
 bpy.ops.mesh.primitive_torus_add(major_radius=r,minor_radius=minor,major_segments=96,minor_segments=10,location=(cx,cy,z));o=bpy.context.object;o.name=name;o.data.materials.append(mat)
 for p in o.data.polygons:p.use_smooth=True
 parts.append(o);return o
torus('Rolled upper rim',.150,.0032,.228,zinc)
torus('Folded base bead',.115,.0027,.009,zinc)
for z,r in [(.045,.1206),(.177,.1435),(.187,.1454)]:torus('Pressed reinforcing bead',r,.0013,z,zinc)
torus('Dark base joint',.114,.0008,.015,edge)
def pipe(name,pts,r,mat):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=8;cu.bevel_depth=r;cu.bevel_resolution=3;sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
 for p,co in zip(sp.points,pts):p.co=(*co,1)
 o=bpy.data.objects.new(name,cu);bpy.context.collection.objects.link(o);activate(o);bpy.ops.object.convert(target='MESH');o.data.materials.append(mat);smart(o)
 for p in o.data.polygons:p.use_smooth=True
 parts.append(o);return o
# Seam at left/rear side, subtle enough not to become a painted stripe.
pipe('Folded vertical zinc seam',[(cx-.115,cy+.003,.018),(cx-.132,cy+.003,.11),(cx-.149,cy+.003,.220)],.0011,edge)
for sign in (-1,1):
 x=cx+sign*.147
 # Stamped eye loops stand proud of body; bail goes through the loop.
 pts=[(x+sign*.003,cy+.009*math.cos(2*math.pi*i/32),.203+.013*math.sin(2*math.pi*i/32)) for i in range(33)]
 pipe('Bail mounting eye',pts,.0025,zinc)
 for z in (.186,.218):
  bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=6,radius=.004,location=(x,cy,z));o=bpy.context.object;o.name='Riveted attachment';o.scale=(.5,1,1);o.data.materials.append(edge);smart(o);parts.append(o)
pts=[]
for i in range(97):
 a=math.pi*i/96;pts.append((cx+.156*math.cos(a),cy-.150*math.sin(a),.203-.090*math.sin(a)))
bail=pipe('Forward folded wire bail',pts,.0023,wiremat)
# Short hooks return through the eyes, rather than terminating in midair.
for sign in (-1,1):pipe('Bail curled end',[(cx+sign*.156,cy,.203),(cx+sign*.156,cy+.006,.192),(cx+sign*.147,cy+.009,.190),(cx+sign*.146,cy+.004,.200)],.0023,wiremat)
for o in parts:
 if not o.data.uv_layers:smart(o)
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=shell;bpy.ops.object.join();bucket=bpy.context.object;bucket.name='KI_LEAK_02_bucket';sc.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
# Mesh intersection check against the original trap, plus nearest surface distances.
def bvh(o):return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])
overlap=bvh(bucket).overlap(trap_bvh);assert not overlap,'Bucket overlaps original P trap'
min_gap=min(trap_bvh.find_nearest(bucket.matrix_world@v.co)[3] for v in bucket.data.vertices)
# Real transparent water preview material. Engine should assign its shared water shader.
water=material('KI_LEAK_02_Water_REPLACE_IN_UE',(.94,.98,1),0,.075);p=water.node_tree.nodes.get('Principled BSDF');p.inputs['Transmission Weight'].default_value=1;p.inputs['IOR'].default_value=1.333
waterverts=[(cx,cy,.115)]+[(cx+.129*math.cos(2*math.pi*i/96),cy+.129*math.sin(2*math.pi*i/96),.115) for i in range(96)]
surface=mesh('KI_LEAK_02_bucket_water',waterverts,[(0,1+i,1+(i+1)%96) for i in range(96)],water)
def planar(o):
 u=o.data.uv_layers.new(name='UVMap');b=bounds(o)
 for p in o.data.polygons:
  for li in p.loop_indices:
   v=o.data.vertices[o.data.loops[li].vertex_index].co;u.data[li].uv=((v.x-b['min'][0])/(b['max'][0]-b['min'][0]),(v.y-b['min'][1])/(b['max'][1]-b['min'][1]))
planar(surface)
# Low spill mostly forward of bucket, organic perimeter. Floor remains readable.
pc=(-.10,-.24);pv=[(*pc,.004)]
for i in range(128):
 a=2*math.pi*i/128;r=1+.12*math.sin(3*a+.7)+.065*math.sin(7*a-1)+.032*math.sin(11*a)
 pv.append((pc[0]+.265*r*math.cos(a),pc[1]+.36*r*math.sin(a),.004))
pf=[(0,1+i,1+(i+1)%128) for i in range(128)];centers={0}
for x,y,rx,ry in [(-.39,-.43,.014,.024),(.22,-.36,.018,.013),(-.21,-.69,.011,.018)]:
 j=len(pv);centers.add(j);pv.append((x,y,.004))
 for i in range(24):
  a=2*math.pi*i/24;r=1+.06*math.sin(3*a);pv.append((x+rx*r*math.cos(a),y+ry*r*math.sin(a),.004))
 for i in range(24):pf.append((j,j+1+i,j+1+(i+1)%24))
puddle=mesh('KI_LEAK_02_puddle',pv,pf,water);planar(puddle)
# Rim-to-centre falloff is an engine vertex color mask, independent of base color.
ca=puddle.data.color_attributes.new(name='WaterEdge',type='FLOAT_COLOR',domain='POINT')
for i,c in enumerate(ca.data):c.color=(1,1,1,1) if i in centers else (0,0,0,1)
exports=[body,bucket,surface,puddle]
ucx=[]
for i in range(12):
 a=2*math.pi*i/12;b=2*math.pi*(i+1)/12
 vs=[]
 for z,r in [(.008,.118),(.230,.154),(.008,.108),(.230,.142)]:
  for angle in (a,b):vs.append((cx+r*math.cos(angle),cy+r*math.sin(angle),z))
 hull=mesh(f'UCX_KI_LEAK_02_bucket_{i:02d}',vs,[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)],edge);hull.hide_render=True;ucx.append(hull)
bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=.116,depth=.008,location=(cx,cy,.010));hull=bpy.context.object;hull.name='UCX_KI_LEAK_02_bucket_12';hull.hide_render=True;ucx.append(hull)
def export(o):
 activate(o)
 if o==bucket:
  for h in ucx:h.select_set(True)
 bpy.ops.export_scene.fbx(filepath=str(ROOT/'models'/f'{o.name}.fbx'),use_selection=True,object_types={'MESH'},add_leaf_bones=False,path_mode='AUTO',apply_unit_scale=True)
for o in exports:export(o)
pb=bounds(puddle);pw=pb['max'][0]-pb['min'][0]+.04;ph=pb['max'][1]-pb['min'][1]+.04
report={'units':'metres','source_blend_sha256':original_hash,'source_origin':[0,0,0],'source_axis':'Z up, front -Y; importer keeps X, flips Y','removed_original_bucket_components':removed,'unchanged_sink_face_uv_material_sha256':before,'preservation_verified':before==after,'trap_intersections':len(overlap),'bucket_trap_nearest_vertex_gap_m':round(min_gap,6),'bucket_ucx_hulls':13,'exports':{o.name:{**bounds(o),'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'materials':[m.name for m in o.data.materials]} for o in exports},'tap_pivots':{s:list(bpy.data.objects['KI_SINK_NARROW_'+s].location) for s in ('L_tap','R_tap')},'leak_point':[-.10,0,.243],'bucket_catch_point':[-.10,0,.115],'bucket_floor_center':[cx,cy,.006],'puddle_mask':{'file':'textures/T_Leak_Puddle_Mask.png','center_m':[(pb['max'][0]+pb['min'][0])/2,(pb['max'][1]+pb['min'][1])/2,.004],'size_m':[pw,ph],'image_right':'+X','image_up':'+Y','channel':'RGBA white with feathered alpha; not an albedo','story':'Recently placed bucket catches active drips. Residual spill escaped earlier; no perpetual floor-impact rings.'},'note':'No static drops exported. Replace both original damage FBX and runtime cylinder/drop. Water visual acceptance is engine-owned.'}
(ROOT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
# Moderate preview budget on shared 16GB workstation.
sc.render.engine='CYCLES';sc.cycles.samples=32;sc.cycles.use_denoising=True;sc.render.threads_mode='FIXED';sc.render.threads=2
sc.render.resolution_x=960;sc.render.resolution_y=960;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.view_settings.view_transform='AgX'
sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.33,.37,.42,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.35
floor=material('PREVIEW warm floor',(.20,.13,.08),0,.68)
bpy.ops.mesh.primitive_plane_add(size=200);ground=bpy.context.object;ground.name='PREVIEW_GROUND';ground.data.materials.append(floor)
bpy.ops.object.camera_add();cam=bpy.context.object;sc.camera=cam;cam.data.type='ORTHO'
def camera(pos,target,scale):cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale
for loc,power,size,color in [((1,-2,3),180,2,(1,.87,.71)),((-2,-.5,2),130,2,(.78,.87,1))]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.size=size;o.data.color=color;o.rotation_euler=(Vector((0,0,.3))-o.location).to_track_quat('-Z','Y').to_euler()
for o in (body,bpy.data.objects['KI_SINK_NARROW_L_tap'],bpy.data.objects['KI_SINK_NARROW_R_tap'],puddle):o.hide_render=True
camera((.53,-1.1,.72),(cx,cy,.14),.57)
sc.render.filepath=str(ROOT/'previews/bucket-three-quarter.png');bpy.ops.render.render(write_still=True)
for o in (body,bpy.data.objects['KI_SINK_NARROW_L_tap'],bpy.data.objects['KI_SINK_NARROW_R_tap'],puddle):o.hide_render=False
camera((1.45,-2.6,1.55),(0,0,.58),1.65)
sc.render.filepath=str(ROOT/'previews/sink-context.png');bpy.ops.render.render(write_still=True)
camera((.4,-1.2,.70),(-.10,0,.25),.8)
sc.render.filepath=str(ROOT/'previews/under-sink-clearance.png');bpy.ops.render.render(write_still=True)
ground.hide_render=True;ground.hide_viewport=True
# Native silhouette -> usable transparent decal mask. Only water geometry is rendered.
saved_visibility={o:o.hide_render for o in sc.objects}
for o in sc.objects:o.hide_render=o!=puddle
mask=bpy.data.materials.new('PREVIEW mask');mask.use_nodes=True;nd=mask.node_tree.nodes;nd.clear();out=nd.new('ShaderNodeOutputMaterial');mix=nd.new('ShaderNodeMixShader');trans=nd.new('ShaderNodeBsdfTransparent');em=nd.new('ShaderNodeEmission');em.inputs[0].default_value=(1,1,1,1);attr=nd.new('ShaderNodeVertexColor');attr.layer_name='WaterEdge';mul=nd.new('ShaderNodeMath');mul.operation='MULTIPLY';mul.inputs[1].default_value=24;mul.use_clamp=True
lk=mask.node_tree.links;lk.new(attr.outputs['Color'],mul.inputs[0]);lk.new(mul.outputs[0],mix.inputs[0]);lk.new(trans.outputs[0],mix.inputs[1]);lk.new(em.outputs[0],mix.inputs[2]);lk.new(mix.outputs[0],out.inputs['Surface'])
puddle.data.materials[0]=mask
mc=report['puddle_mask']['center_m'];camera((mc[0],mc[1],2),(mc[0],mc[1],0),max(pw,ph));cam.rotation_euler=(0,0,0)
sc.render.resolution_x=round(1024*pw/max(pw,ph));sc.render.resolution_y=round(1024*ph/max(pw,ph));sc.render.film_transparent=True;sc.view_settings.view_transform='Standard';sc.render.image_settings.color_mode='RGBA';sc.render.filepath=str(ROOT/'textures/T_Leak_Puddle_Mask.png');bpy.ops.render.render(write_still=True)
puddle.data.materials[0]=water
for o,h in saved_visibility.items():o.hide_render=h
sc.render.film_transparent=False;sc.view_settings.view_transform='AgX';sc.render.resolution_x=960;sc.render.resolution_y=960
camera((1.45,-2.6,1.55),(0,0,.58),1.65)
for h in ucx:h.hide_set(True)
for im in bpy.data.images:
 if im.type=='IMAGE' and im.size[0]>0:im.pack()
sc.render.filepath='//../previews/sink-context.png';bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/KI_LEAK_02_assembly.blend'))
print('KI_LEAK_02_COMPLETE',json.dumps(report))
