from pathlib import Path
import bpy,math,json,hashlib,ast
from mathutils import Vector
P=Path(__file__).resolve().parent.parent; A=P.parent
bpy.context.preferences.filepaths.save_version=0

def render(name,target,loc,scale):
 sc=bpy.context.scene
 for o in list(sc.objects):
  if o.type in {'CAMERA','LIGHT'}:bpy.data.objects.remove(o,do_unlink=True)
 bpy.ops.object.camera_add(location=loc);cam=bpy.context.object;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=scale;sc.camera=cam
 for xyz,power in [(loc,300),((0,2,4),180)]:
  bpy.ops.object.light_add(type='AREA',location=xyz);o=bpy.context.object;o.data.energy=power;o.data.size=3;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
 sc.render.engine='CYCLES';sc.cycles.samples=12;sc.cycles.use_denoising=True;sc.render.threads_mode='FIXED';sc.render.threads=2;sc.render.resolution_x=640;sc.render.resolution_y=640;sc.render.resolution_percentage=100;sc.render.film_transparent=True;sc.render.image_settings.file_format='PNG';sc.render.filepath=str(P/'previews'/f'{name}.png');bpy.ops.render.render(write_still=True)
def export(obs,name,axes=True):
 bpy.ops.object.select_all(action='DESELECT')
 for o in obs:o.select_set(True)
 bpy.context.view_layer.objects.active=obs[0]
 bpy.ops.export_scene.fbx(filepath=str(P/'model'/f'{name}.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,add_leaf_bones=False,axis_forward='-Y' if axes else '-Z',axis_up='Z' if axes else 'Y')
 report[name]={'objects':len(obs),'bounds':[[min((o.matrix_world@v.co)[i] for o in obs for v in o.data.vertices) for i in range(3)],[max((o.matrix_world@v.co)[i] for o in obs for v in o.data.vertices) for i in range(3)]],'axes':['-Y','Z'] if axes else ['-Z','Y']}
report={}
# Slim baseboard all five end conditions; profiles remain exactly matched.
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
mat=bpy.data.materials.new('AgedIvoryPaint');mat.use_nodes=True;p=mat.node_tree.nodes['Principled BSDF'];p.inputs['Roughness'].default_value=.84
tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(A/'ARC-TRIM-01/textures/paint-selected.png'));mat.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color'])
profile=[(0,0),(-.0107,0),(-.0107,.105),(-.014,.105),(-.014,.116),(-.0117,.124),(-.007,.130),(0,.130)]
for kind in ['1m','Inside_Start','Inside_End','Outside_Start','Outside_End']:
 name='Baseboard_'+kind;n=len(profile);verts=[]
 for end in [0,1]:
  for y,z in profile:
   x=float(end)
   if kind=='Inside_Start' and end==0:x=-y
   if kind=='Inside_End' and end==1:x=1+y
   if kind=='Outside_Start' and end==0:x=y
   if kind=='Outside_End' and end==1:x=1-y
   verts.append((x,y,z))
 faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);me.materials.append(mat);uv=me.uv_layers.new()
 for f in me.polygons:
  for li in f.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v.x,(v.z+v.y)*2.5)
 export([ob],name);ob.location.y=len(report)*.06
render('baseboard-profiles',(.5,.15,.06),(1,-1,.55),1.2)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'model/SlimBaseboards.blend'))
# Sliding frame header correction: extend vertical casing to exact underside.
bpy.ops.wm.open_mainfile(filepath=str(A/'ARC-SLIDING-CLOSET-02/model/ARC-SLIDING-CLOSET-02.blend'))
o=bpy.data.objects['ARC_Sliding02_Frame']
# Connected casing islands separately retain eased ends; scale their Z to meet header.
import bmesh
bm=bmesh.new();bm.from_mesh(o.data);remaining=set(bm.verts)
while remaining:
 seed=remaining.pop();island={seed};stack=[seed]
 while stack:
  v=stack.pop()
  for e in v.link_edges:
   q=e.other_vert(v)
   if q in remaining:remaining.remove(q);island.add(q);stack.append(q)
 lo=[min(v.co[i] for v in island) for i in range(3)];hi=[max(v.co[i] for v in island) for i in range(3)]
 if hi[2]-lo[2]>2 and hi[0]-lo[0]>.08 and hi[1]-lo[1]<.03:
  for v in island:v.co.z=lo[2]+(v.co.z-lo[2])*(2.1625-lo[2])/(hi[2]-lo[2])
bm.to_mesh(o.data);bm.free();export([o],'ARC_Sliding03_Frame')
render('sliding-frame',(0,0,1.1),(3,-5,2.8),2.8)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'model/SlidingFrame.blend'))
# Curved L rod; source floor origin and old transform retained.
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
chrome=bpy.data.materials.new('Aged_Chrome');chrome.use_nodes=True;p=chrome.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.45,.42,.36,1);p.inputs['Metallic'].default_value=1;p.inputs['Roughness'].default_value=.27
pts=[(.96,-.35,2.18),(-.84,-.35,2.18)]+[(-.84-.12*math.sin(i*math.pi/2/24),-.23-.12*math.cos(i*math.pi/2/24),2.18) for i in range(1,25)]+[(-.96,.402,2.18)]
cu=bpy.data.curves.new('Smooth curved L rail','CURVE');cu.dimensions='3D';cu.bevel_depth=.012;cu.bevel_resolution=4;sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
for p,xyz in zip(sp.points,pts):p.co=(*xyz,1)
o=bpy.data.objects.new('BA_CurvedL_Rod',cu);bpy.context.collection.objects.link(o);cu.materials.append(chrome);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');parts=[bpy.context.object]
for loc,rot in [((.96,-.35,2.18),(0,math.pi/2,0)),((-.96,.402,2.18),(math.pi/2,0,0))]:
 bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=.032,depth=.008,location=loc,rotation=rot);o=bpy.context.object;o.data.materials.append(chrome);parts.append(o)
export(parts,'BA_CurvedL_Rod');render('curved-L-rod',(0,0,2.18),(2,-3,4),2.4);bpy.ops.wm.save_as_mainfile(filepath=str(P/'model/CurvedL_Rod.blend'))
# Fixed return curtain follows the return; main straight curtain retains its existing sliding root.
with bpy.data.libraries.load(str(A/'BA-TUB-01/model/BA-TUB-01.blend'),link=False) as (src,dst):
 dst.materials=[n for n in src.materials if n=='Floral_cotton']
fabric=next((m for m in dst.materials if m),None)
if fabric:
 for nd in fabric.node_tree.nodes:
  if nd.type=='TEX_IMAGE' and nd.image:
   nd.image.filepath=str(A/'BA-TUB-01/textures/floral-albedo.png');nd.image.reload();nd.image.pack()
if fabric is None:
 fabric=bpy.data.materials.new('Curtain_Return_Fabric');fabric.diffuse_color=(.62,.52,.40,1)
vs=[];fs=[];nx,nz=48,32
for j in range(nz+1):
 v=j/nz
 for i in range(nx+1):
  u=i/nx;y=-.215+u*.598;x=-.96+.018*math.sin(u*math.pi*14)+.006*math.sin(v*9+u*8);z=2.135-v*1.78+.008*math.sin(u*24)*v
  vs.append((x,y,z))
for j in range(nz):
 for i in range(nx):
  q=j*(nx+1)+i;fs.append((q,q+1,q+nx+2,q+nx+1))
me=bpy.data.meshes.new('Return curtain drape');me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new('BA_Curtain03_FixedReturn',me);bpy.context.collection.objects.link(o);me.materials.append(fabric);uv=me.uv_layers.new()
for f in me.polygons:
 f.use_smooth=True
 for li in f.loop_indices:
  q=me.loops[li].vertex_index;uv.data[li].uv=(q%(nx+1)/nx,q//(nx+1)/nz)
parts=[o]
for y in [-.205,-.11,-.01,.09,.19,.29,.38]:
 bpy.ops.mesh.primitive_torus_add(major_segments=24,minor_segments=8,major_radius=.022,minor_radius=.003,location=(-.96,y,2.173),rotation=(math.pi/2,0,0));o=bpy.context.object;o.data.materials.append(chrome);parts.append(o)
# Seven metal header clips bridge each ring to the actual top-fold position.
for i,y in enumerate([-.205,-.11,-.01,.09,.19,.29,.38]):
 u=(y+.215)/.598;x=-.96+.018*math.sin(u*math.pi*14)+.006*math.sin(u*8)
 c=bpy.data.curves.new('Curtain header clip','CURVE');c.dimensions='3D';c.bevel_depth=.0023;c.bevel_resolution=2;c.use_fill_caps=True
 sp=c.splines.new('POLY');sp.points.add(2)
 for point,co in zip(sp.points,[(-.96,y,2.153),(-.96,y,2.143),(x,y,2.130)]):point.co=(*co,1)
 ob=bpy.data.objects.new('Ring_to_header_clip_%02d'%i,c);bpy.context.collection.objects.link(ob);bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.convert(target='MESH');ob=bpy.context.object;ob.data.materials.append(chrome)
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.01);bpy.ops.object.mode_set(mode='OBJECT');parts.append(ob)
export(parts,'BA_Curtain03_FixedReturn');render('rod-and-return-curtain',(-.2,0,1.25),(2,-3,3.5),2.5);bpy.ops.wm.save_as_mainfile(filepath=str(P/'model/CurvedL_Rod_ReturnCurtain.blend'))

# Pink glazed quarter-round profiles, unit run Z length, local mounting back Y0.
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
pink=bpy.data.materials.new('Pink_Glazed_Bullnose');pink.use_nodes=True;p=pink.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(.56,.30,.27,1);p.inputs['Roughness'].default_value=.27
prof=[(0,0)]+[(.018*math.cos(i*math.pi/2/16),-.018*math.sin(i*math.pi/2/16)) for i in range(17)]
n=len(prof);vs=[(x,y,z) for z in (0,1) for x,y in prof];fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
me=bpy.data.meshes.new('Curved pink bullnose');me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new('BA_PinkBullnose_1m',me);bpy.context.collection.objects.link(o);me.materials.append(pink);uv=me.uv_layers.new()
for f in me.polygons:
 f.use_smooth=len(f.vertices)==4
 for li in f.loop_indices:
  v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(math.atan2(-v.y,v.x)/(math.pi/2),v.z)
export([o],'BA_PinkBullnose_1m');render('pink-bullnose',(.01,-.01,.5),(.3,-.4,.7),1.1);bpy.ops.wm.save_as_mainfile(filepath=str(P/'model/PinkBullnose.blend'))
(P/'validation.json').write_text(json.dumps(report,indent=2))
(P/'file-manifest.json').write_text(json.dumps({str(f.relative_to(P)):hashlib.sha256(f.read_bytes()).hexdigest() for f in (P/'model').glob('*.fbx')},indent=2))
