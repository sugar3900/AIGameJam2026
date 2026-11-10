"""FIX-018: preserve original chair; replace reversed/vertical ladder slats only."""
from pathlib import Path
import bpy,math,json,shutil,bmesh,sys,hashlib
from mathutils import Vector,Matrix
from mathutils.geometry import interpolate_bezier
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];OLD=ROOT.parent/'KI-CHAIR-01'
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
for name in ('wood-selected-v2.png','vinyl.png'):shutil.copyfile(OLD/'textures'/name,ROOT/'textures'/name)
bpy.ops.import_scene.fbx(filepath=str(OLD/'model/KI_CHAIR_01.fbx'))
original=bpy.context.selected_objects[0];bpy.context.view_layer.objects.active=original
# Split closed source members without moving or remodeling preserved geometry.
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.separate(type='LOOSE');bpy.ops.object.mode_set(mode='OBJECT')
source=bpy.data.collections.new('KI-CHAIR-02_SOURCE');bpy.context.scene.collection.children.link(source)
parts=[];posts={};removed=[];kept_signature=[]
def bounds(ob):
 vs=[ob.matrix_world@v.co for v in ob.data.vertices]
 return [min(v[k] for v in vs) for k in range(3)],[max(v[k] for v in vs) for k in range(3)]
for ob in list(bpy.data.objects):
 if ob.type!='MESH':continue
 mn,mx=bounds(ob);size=[b-a for a,b in zip(mn,mx)]
 is_slat=size[0]>.30 and mn[2]>.55 and size[2]<.14
 is_peg=max(size)<.015 and mn[2]>.55
 if is_slat or is_peg:
  removed.append({'kind':'slat' if is_slat else 'peg','min':mn,'max':mx});bpy.data.objects.remove(ob,do_unlink=True);continue
 if size[2]>.75 and size[0]<.10:
  sign=1 if (mn[0]+mx[0])>0 else -1;ob.name='Original rear post '+('R' if sign>0 else 'L');posts[sign]=ob
 else:ob.name='Preserved original member'
 for c in list(ob.users_collection):c.objects.unlink(ob)
 source.objects.link(ob);parts.append(ob)
 for v in ob.data.vertices:kept_signature.append(tuple(round(x,7) for x in ob.matrix_world@v.co))
assert len(posts)==2 and sum(x['kind']=='slat' for x in removed)==3 and sum(x['kind']=='peg' for x in removed)==6
# Restore the exact original material contract with self-contained texture paths.
def material(name,color,texture=None):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1);m.node_tree.nodes.clear()
 p=m.node_tree.nodes.new('ShaderNodeBsdfPrincipled');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=.65
 out=m.node_tree.nodes.new('ShaderNodeOutputMaterial');m.node_tree.links.new(p.outputs[0],out.inputs['Surface'])
 if texture:
  t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(ROOT/'textures'/texture),check_existing=True);t.image.pack();m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
 return m
wood=material('Chair_Walnut',(.32,.12,.045),'wood-selected-v2.png');vinyl=material('Chair_Rust_Vinyl',(.45,.11,.065),'vinyl.png');piping=material('Chair_Piping',(.25,.075,.035))
# Recover the original AUTO-Bezier post centreline from its source control points.
cu=bpy.data.curves.new('Original post centreline','CURVE');cu.dimensions='3D';s=cu.splines.new('BEZIER');s.bezier_points.add(3)
for p,co in zip(s.bezier_points,[(.205,.24,.015),(.19,.19,.41),(.19,.205,.64),(.205,.255,.89)]):p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
helper=bpy.data.objects.new('Centreline helper',cu);bpy.context.collection.objects.link(helper);bpy.context.view_layer.update();samples=[]
for a,b in zip(s.bezier_points[:-1],s.bezier_points[1:]):samples.extend(interpolate_bezier(a.co,a.handle_right,b.handle_left,b.co,256))
bpy.data.objects.remove(helper,do_unlink=True)
def post_at(z):
 if z <= samples[0].z+1e-6:return samples[0].copy()
 if z >= samples[-1].z-1e-6:return samples[-1].copy()
 for a,b in zip(samples,samples[1:]):
  if a.z<=z<=b.z:
   t=(z-a.z)/max(1e-9,b.z-a.z);return a.lerp(b,t)
 raise ValueError(z)
def surface(x,z,bow):
 p=post_at(z);half=p.x-.006
 return p.y+bow*(1-(x/half)**2)
new_slats=[];joint_report=[]
post_trees={side:BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[p.vertices for p in ob.data.polygons],all_triangles=False) for side,ob in posts.items()}
def slat(name,zc,height,bow):
 nx=32;nz=10;row=nx+1;verts=[];faces=[]
 for side in (-1,1):
  for j in range(nz+1):
   z=zc-height/2+height*j/nz;half=post_at(z).x-.006
   for i in range(nx+1):
    x=half*(-1+2*i/nx);verts.append((x,surface(x,z,bow)+side*.010,z))
 count=(nx+1)*(nz+1)
 for side in range(2):
  for j in range(nz):
   for i in range(nx):
    a=side*count+j*row+i;f=(a,a+1,a+1+row,a+row)
    if side:f=tuple(reversed(f))
    faces.append(f)
 for i in range(nx):
  faces.append((i,count+i,count+i+1,i+1));a=nz*row+i;faces.append((a+1,count+a+1,count+a,a))
 for j in range(nz):
  a=j*row;faces.append((a+row,count+a+row,count+a,a));a=j*row+nx;faces.append((a,count+a,count+a+row,a+row))
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();ob=bpy.data.objects.new(name,mesh);source.objects.link(ob);ob.data.materials.append(wood)
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
 bevel=ob.modifiers.new('Soft worn slat edges','BEVEL');bevel.width=.0028;bevel.segments=3;bpy.ops.object.modifier_apply(modifier=bevel.name)
 for f in ob.data.polygons:f.use_smooth=True
 # Longitudinal grain follows the slat; no changes to existing frame/seat UVs.
 uv=ob.data.uv_layers.new(name='UVMap');mn,mx=bounds(ob)
 for face in ob.data.polygons:
  dominant=max(range(3),key=lambda k:abs(face.normal[k]))
  for li in face.loop_indices:
   v=ob.data.vertices[ob.data.loops[li].vertex_index].co
   if dominant==1:u,w=(v.x-mn[0])/(mx[0]-mn[0]),(v.z-mn[2])/(mx[2]-mn[2])
   elif dominant==2:u,w=(v.x-mn[0])/(mx[0]-mn[0]),(v.y-mn[1])/.065
   else:u,w=(v.y-mn[1])/.065,(v.z-mn[2])/(mx[2]-mn[2])
   uv.data[li].uv=(.08+.84*u,.08+.84*w)
 norm=ob.modifiers.new('Weighted wooden corner normals','WEIGHTED_NORMAL');norm.keep_sharp=True;bpy.ops.object.modifier_apply(modifier=norm.name)
 parts.append(ob);new_slats.append(ob)
 for sign in (-1,1):
  depths=[]
  for v in ob.data.vertices:
   q=v.co;p=post_at(q.z)
   if sign*q.x>p.x-.0095:
    hit,normal,idx,d=post_trees[sign].find_nearest(q);signed=(q-hit).dot(normal);depths.append(-signed)
  assert depths and min(depths)>.003,(name,sign,min(depths))
  joint_report.append({'slat':name,'post':'R' if sign>0 else 'L','minimum_endpoint_embed_m':min(depths),'samples':len(depths)})
 # Original peg styling, now seated and aligned to the sloping/curved front face.
 for sign in (-1,1):
  x=sign*(post_at(zc).x-.022);y=surface(x,zc,bow)-.010
  eps=.0001;dx=(surface(x+eps,zc,bow)-surface(x-eps,zc,bow))/(2*eps);dz=(surface(x,zc+eps,bow)-surface(x,zc-eps,bow))/(2*eps)
  normal=Vector((dx,-1,dz)).normalized();pos=Vector((x,y,zc))+normal*.0004
  bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=.004,depth=.002,location=pos);peg=bpy.context.object;peg.name='Recessed aligned slat peg';peg.rotation_euler=normal.to_track_quat('Z','Y').to_euler();peg.data.materials.append(piping)
  for c in list(peg.users_collection):c.objects.unlink(peg)
  source.objects.link(peg);parts.append(peg)
 return ob
slat('Concave lower back slat',.615,.065,.012)
slat('Concave middle back slat',.715,.065,.012)
slat('Concave upper broad slat',.835,.105,.008)
# Author per-member convex collision; retain openings rather than one whole-chair box.
coll=[]
def box_hull(loc,dims,rotation=None):coll.append((Vector(loc),Vector(dims),rotation or Vector((0,0,0))))
def beam_hull(a,b,r):
 a,b=Vector(a),Vector(b);d=b-a;box_hull((a+b)/2,(r*2,r*2,d.length),d.to_track_quat('Z','Y').to_euler())
box_hull((0,-.002,.446),(.46,.45,.108))
for sign in (-1,1):
 beam_hull((sign*.205,-.22,.015),(sign*.18,-.18,.415),.021)
 for za,zb in zip((.015,.22,.41,.58,.75),(.22,.41,.58,.75,.89)):
  a,b=post_at(za),post_at(zb);a.x*=sign;b.x*=sign;beam_hull(a,b,.020)
beam_hull((-.18,-.21,.18),(.18,-.21,.18),.011);beam_hull((-.18,.205,.19),(.18,.205,.19),.011)
for x in (-.185,.185):beam_hull((x,-.20,.20),(x,.20,.20),.011)
for z,h,bow in ((.615,.065,.012),(.715,.065,.012),(.835,.105,.008)):
 half=post_at(z).x-.006
 for lo,hi in ((-half,-half/3),(-half/3,half/3),(half/3,half)):
  x=(lo+hi)/2;y=surface(x,z,bow);tilt=math.atan2(post_at(z+.001).y-post_at(z-.001).y,.002)
  box_hull((x,y,z),(hi-lo,.024,h),Vector((-tilt,0,0)))
# Combined assembly and self-contained export.
bpy.ops.object.select_all(action='DESELECT');copies=[]
for ob in parts:
 c=ob.copy();c.data=ob.data.copy();source.objects.link(c);c.select_set(True);copies.append(c)
bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();joined=bpy.context.object;joined.name='KI_CHAIR_02';bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
ucx=[];render_min,render_max=bounds(joined)
for i,(loc,dims,rot) in enumerate(coll):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc,rotation=rot);ob=bpy.context.object;ob.name=f'UCX_KI_CHAIR_02_{i:02d}';ob.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 # Convex clipping keeps new simple collision inside the original placement envelope.
 inv=ob.matrix_world.inverted();points=[]
 for v in ob.data.vertices:
  q=ob.matrix_world@v.co
  points.append(inv@Vector([min(render_max[k],max(render_min[k],q[k])) for k in range(3)]))
 bm=bmesh.new()
 for q in points:bm.verts.new(q)
 bmesh.ops.convex_hull(bm,input=list(bm.verts),use_existing_faces=False);bm.to_mesh(ob.data);bm.free();ob.data.update();ucx.append(ob)
bpy.ops.object.select_all(action='DESELECT');joined.select_set(True)
for ob in ucx:ob.select_set(True)
bpy.context.view_layer.objects.active=joined
bpy.ops.export_scene.fbx(filepath=str(ROOT/'model/KI_CHAIR_02.fbx'),use_selection=True,object_types={'MESH'},add_leaf_bones=False,apply_unit_scale=True,axis_forward='-Y',axis_up='Z',path_mode='RELATIVE',bake_anim=False)
mn,mx=bounds(joined)
slat_measure=[]
for z,h,bow in ((.615,.065,.012),(.715,.065,.012),(.835,.105,.008)):
 dy=post_at(z+h/2).y-post_at(z-h/2).y
 slat_measure.append({'centre_z':z,'centre_recess_m':bow,'recline_degrees':math.degrees(math.atan2(dy,h)),'height':h})
manifest={'asset':'KI-CHAIR-02','replaces':'KI-CHAIR-01','units':'metres','front':'-Y','up':'+Z','origin':[0,0,0],'bounds':{'min':mn,'max':mx},'preserved_vertex_count':len(kept_signature),'preserved_vertex_signature_sha256':hashlib.sha256(json.dumps(sorted(kept_signature)).encode()).hexdigest(),'removed_members':removed,'slats':slat_measure,'joint_checks':joint_report,'ucx_hulls':len(ucx),'materials':[m.name for m in joined.data.materials]}
(ROOT/'assembly.json').write_text(json.dumps(manifest,indent=2)+'\n')
for ob in [joined]+ucx:bpy.data.objects.remove(ob,do_unlink=True)
# Warm studio context only; no changes to original seat height or chair footprint.
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=28;sc.render.resolution_x=1100;sc.render.resolution_y=1100;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.film_transparent=False
preview=bpy.data.collections.new('PREVIEW_ONLY');sc.collection.children.link(preview)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,.011));floor=bpy.context.object;floor.name='PREVIEW floor';floor.data.materials.append(material('PREVIEW warm floor',(.19,.105,.046)))
for c in list(floor.users_collection):c.objects.unlink(floor)
preview.objects.link(floor)
world=bpy.data.worlds.new('Neutral warm world');sc.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.28,.24,.19,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.5
for loc,power,size in [((2,-3,3),350,3),((-2,-1,2),140,2.5),((0,2,3),160,2)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.size=size;o.rotation_euler=(Vector((0,0,.45))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(1.5,-2.3,1.35));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.46))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=1.20;sc.camera=cam
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'model/KI-CHAIR-02.blend'))
if '--no-render' not in sys.argv:
 sc.render.filepath=str(ROOT/'previews/chair-context.png');bpy.ops.render.render(write_still=True)
print('Dining chair corrected and source saved.')
