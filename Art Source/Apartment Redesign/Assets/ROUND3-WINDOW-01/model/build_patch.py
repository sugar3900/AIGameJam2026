"""Close window head gaps; original released sources remain immutable."""
from pathlib import Path
import json, hashlib, sys
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent.parent
A=P.parent
(P/'previews').mkdir(exist_ok=True)
bpy.context.preferences.filepaths.save_version=0
CASES=[
 ('Narrow','ARC-WINDOW-NARROW-01','ARC_Window_frame',2.3225,2.292,1.10),
 ('Office','ARC-WINDOW-OFFICE-01','ARC_Window_frame',2.3225,2.292,1.40),
 ('Bath','ARC-WINDOW-BATH-01','ARC_Window_frame',2.3225,2.292,1.15),
 ('Kitchen','ARC-WINDOW-KITCHEN-02','ARC_Window_Kitchen_frame',1.155,1.142,1.60),
 ('Living','ARC-LIVING-WALL-01','ARC_Window_Casing_Sash',None,None,1.60)]
only_living="--only-living" in sys.argv
report=json.loads((P/"validation.json").read_text()) if only_living else {}

def bounds(o):
 return [[min((o.matrix_world@v.co)[i] for v in o.data.vertices) for i in range(3)],
         [max((o.matrix_world@v.co)[i] for v in o.data.vertices) for i in range(3)]]

def islands(bm):
 rest=set(bm.verts);out=[]
 while rest:
  seed=rest.pop();group={seed};todo=[seed]
  while todo:
   v=todo.pop()
   for edge in v.link_edges:
    q=edge.other_vert(v)
    if q in rest:rest.remove(q);group.add(q);todo.append(q)
  out.append(group)
 return out

def probe(obj,zs,width,start_y=-.25):
 bm=bmesh.new();bm.from_mesh(obj.data);tree=BVHTree.FromBMesh(bm);hits=[]
 for z in zs:
  for x in [-width*.40,0,width*.40]:
   pos,norm,face,dist=tree.ray_cast(Vector((x,start_y,z)),Vector((0,1,0)),.50)
   hits.append(pos is not None)
 bm.free();return hits

for label,kit,old,old_bottom,new_bottom,width in CASES:
 if only_living and label!='Living':continue
 bpy.ops.wm.read_factory_settings(use_empty=True)
 bpy.context.preferences.filepaths.save_version=0
 bpy.ops.import_scene.fbx(filepath=str(A/kit/'model'/(old+'.fbx')))
 obs=[o for o in bpy.context.scene.objects if o.type=='MESH']
 visible=[o for o in obs if not o.name.startswith('UCX_')]
 assert len(visible)==1,(label,[o.name for o in visible])
 obj=visible[0];name='ARC_Window_'+label+'03_'+('Casing' if label=='Living' else 'frame')
 baseline=bounds(obj);slots=[m.name for m in obj.data.materials]
 bm=bmesh.new();bm.from_mesh(obj.data)
 if old_bottom is not None:
  choices=[]
  for group in islands(bm):
   lo=[min(v.co[i] for v in group) for i in range(3)];hi=[max(v.co[i] for v in group) for i in range(3)]
   if abs(lo[2]-old_bottom)<1e-5 and hi[0]-lo[0]>width and .08<hi[2]-lo[2]<.11:choices.append(group)
  assert len(choices)==1,(label,len(choices))
  group=choices[0];mid=(max(v.co.z for v in group)+min(v.co.z for v in group))/2
  zs=[old_bottom-(old_bottom-new_bottom)*f for f in [.1,.2,.3]]
  before=probe(obj,zs,width)
  for v in group:
   if v.co.z<mid:v.co.z-=old_bottom-new_bottom
  bm.to_mesh(obj.data);bm.free();obj.data.update()
  after=probe(obj,zs,width)
  assert not any(before) and all(after),(label,before,after)
  report[label]={'old_header_bottom_m':old_bottom,'new_header_bottom_m':new_bottom,
                 'gap_rays_before':sum(before),'gap_rays_after':sum(after),'rays':len(after)}
 else:
  bm.free()
  # Existing living casing overlaps the sash in elevation but has no head reveal
  # return between their two depth planes. Add a proper wooden head liner.
  zs=[2.290,2.294,2.298]
  before=probe(obj,zs,width,-.055)
  bpy.ops.mesh.primitive_cube_add(size=1,location=(0,-.0305,2.294))
  liner=bpy.context.object;liner.name='Head reveal liner';liner.dimensions=(1.60,.069,.024)
  bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
  liner.data.materials.append(obj.data.materials[0])
  uv=liner.data.uv_layers.active
  for f in liner.data.polygons:
   for li in f.loop_indices:
    v=liner.data.vertices[liner.data.loops[li].vertex_index].co+liner.location
    n=f.normal
    if abs(n.y)>=max(abs(n.x),abs(n.z)):u,w=v.x,v.z
    elif abs(n.x)>=abs(n.z):u,w=v.y,v.z
    else:u,w=v.x,v.y
    uv.data[li].uv=((u+1.6)/3.2,w/3.2)
  liner.data.calc_loop_triangles()
  for tri in liner.data.loop_triangles:
   a,b,c=[uv.data[i].uv for i in tri.loops]
   assert abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))>1e-12,'head liner collapsed UV'
  bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);liner.select_set(True)
  bpy.context.view_layer.objects.active=obj;bpy.ops.object.join()
  after=probe(obj,zs,width,-.055)
  assert all(after),(label,before,after)
  report[label]={'head_liner_m':{'min':[-.80,-.065,2.282],'max':[.80,.004,2.306]},
                 'reveal_rays_before':sum(before),'reveal_rays_after':sum(after),'rays':len(after)}
 assert all(abs(a-b)<1e-6 for aa,bb in zip(baseline,bounds(obj)) for a,b in zip(aa,bb)),(label,baseline,bounds(obj),list(obj.rotation_euler))
 assert [m.name for m in obj.data.materials]==slots,label
 # Render mesh name and matching custom collision names remain stable for reimport.
 bpy.ops.object.select_all(action='DESELECT')
 for o in obs:o.select_set(True)
 bpy.context.view_layer.objects.active=obj
 axes=('-Z','Y') if label=='Living' else ('-Y','Z')
 export=P/'model'/(name+'.fbx')
 bpy.ops.export_scene.fbx(filepath=str(export),use_selection=True,object_types={'MESH'},apply_unit_scale=True,
  axis_forward=axes[0],axis_up=axes[1],bake_anim=False,add_leaf_bones=False)
 report[label].update({'export':str(export.relative_to(P)),'original':kit+'/model/'+old+'.fbx',
  'axes':list(axes),'bounds_m':baseline,'materials':slots,'collision_hulls':sum(o.name.startswith('UCX_') for o in obs),
  'pivot_m':[float(x) for x in obj.location],'bounds_materials_preserved':True})
 bpy.ops.wm.save_as_mainfile(filepath=str(P/'model'/(name+'.blend')))
 # Fresh round trip, including outward winding on every disconnected closed component.
 bpy.ops.wm.read_factory_settings(use_empty=True)
 bpy.ops.import_scene.fbx(filepath=str(export))
 obj=next(o for o in bpy.context.scene.objects if o.type=='MESH' and not o.name.startswith('UCX_'))
 bm=bmesh.new();bm.from_mesh(obj.data);volumes=[]
 for group in islands(bm):
  faces={f for v in group for f in v.link_faces}
  if not faces:continue
  assert all(e.is_manifold for v in group for e in v.link_edges),label
  vol=sum(f.verts[0].co.dot(f.verts[i].co.cross(f.verts[i+1].co))/6 for f in faces for i in range(1,len(f.verts)-1))
  assert vol>0,(label,vol)
  volumes.append(vol)
 bm.free()
 assert all(probe(obj,zs,width,-.055 if label=='Living' else -.25)),label
 assert obj.data.uv_layers.active and all(all(abs(x)<1e6 for x in q.uv) for q in obj.data.uv_layers.active.data),label
 report[label]['fresh_fbx_closed_outward_components']=len(volumes)
 report[label]['fresh_fbx_rays_pass']=True
(P/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
(P/'file-manifest.json').write_text(json.dumps({str(f.relative_to(P)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted((P/'model').glob('*.fbx'))},indent=2)+'\n')
print('WINDOW HEADS PASS',len(report))
