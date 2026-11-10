"""Fresh FBX import; independently compare preserved geometry, UVs, materials and fit."""
from pathlib import Path
from collections import Counter
import bpy,math,json,hashlib,bmesh
from mathutils.kdtree import KDTree
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];OLD=ROOT.parent/'KI-CHAIR-01'
bpy.ops.wm.read_factory_settings(use_empty=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def groups(ob):
 parent=list(range(len(ob.data.vertices)))
 def root(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 for e in ob.data.edges:
  a,b=(root(i) for i in e.vertices);parent[b]=a
 g={}
 for i in range(len(parent)):g.setdefault(root(i),[]).append(i)
 return list(g.values())
def bounds(vs):return {'min':[min(v[k] for v in vs) for k in range(3)],'max':[max(v[k] for v in vs) for k in range(3)]}
def classification(ob,ids):
 vs=[ob.matrix_world@ob.data.vertices[i].co for i in ids];bb=bounds(vs);sz=[b-a for a,b in zip(bb['min'],bb['max'])]
 if sz[0]>.30 and bb['min'][2]>.55 and sz[2]<.14:return 'slat'
 if max(sz)<.015 and bb['min'][2]>.55:return 'peg'
 return 'preserved'
def signatures(ob,ids):
 uv=ob.data.uv_layers.active;out=[]
 for p in ob.data.polygons:
  mat=ob.data.materials[p.material_index].name.split('.')[0]
  for li in p.loop_indices:
   vi=ob.data.loops[li].vertex_index
   if vi not in ids:continue
   v=ob.matrix_world@ob.data.vertices[vi].co
   out.append(tuple(v)+tuple(uv.data[li].uv)+(mat,))
 return Counter(out)
bpy.ops.import_scene.fbx(filepath=str(OLD/'model/KI_CHAIR_01.fbx'))
old=[o for o in bpy.context.selected_objects if o.type=='MESH'][0];old_groups=groups(old);old_ids={i for g in old_groups if classification(old,g)=='preserved' for i in g};old_sig=signatures(old,old_ids);old_bb=bounds([old.matrix_world@v.co for v in old.data.vertices])
bpy.ops.import_scene.fbx(filepath=str(ROOT/'model/KI_CHAIR_02.fbx'))
new_objects=[o for o in bpy.context.selected_objects if o.type=='MESH'];renders=[o for o in new_objects if not o.name.startswith('UCX_')];ucx=[o for o in new_objects if o.name.startswith('UCX_')]
assert len(renders)==1 and len(ucx)==26
ob=renders[0];vs=[ob.matrix_world@v.co for v in ob.data.vertices];bb=bounds(vs);assert max(abs(bb[k][i]-old_bb[k][i]) for k in ('min','max') for i in range(3))<1e-6
assert all(math.isfinite(c) for v in vs for c in v)
gs=groups(ob);ids={i for g in gs if classification(ob,g)=='preserved' for i in g};new_sig=signatures(ob,ids)
old_keys=list(old_sig);tree=KDTree(len(old_keys))
for i,k in enumerate(old_keys):tree.insert(k[:3],i)
tree.balance();remaining=old_sig.copy();max_position_error=0;max_uv_error=0
for key,count in new_sig.items():
 for point,i,distance in tree.find_range(key[:3],1e-6):
  old_key=old_keys[i]
  if old_key[-1]!=key[-1] or max(abs(a-b) for a,b in zip(key[3:5],old_key[3:5]))>1e-6:continue
  take=min(count,remaining[old_key])
  if take:
   remaining[old_key]-=take;count-=take;max_position_error=max(max_position_error,distance);max_uv_error=max(max_uv_error,max(abs(a-b) for a,b in zip(key[3:5],old_key[3:5])))
  if count==0:break
 assert count==0,('Preserved corner mismatch',key,count)
assert not sum(remaining.values())

assert len(ids)==len(old_ids)==3668
ob.data.calc_loop_triangles();uv=ob.data.uv_layers.active;assert uv
zero=[];uvzero=[];newslatids={i for g in gs if classification(ob,g)=='slat' for i in g}
for t in ob.data.loop_triangles:
 a,b,c=[vs[i] for i in t.vertices]
 if (b-a).cross(c-a).length<1e-12:zero.append(t.index)
 u,v,w=[uv.data[i].uv for i in t.loops];area=abs((v.x-u.x)*(w.y-u.y)-(v.y-u.y)*(w.x-u.x))
 if area<1e-12:uvzero.append({'triangle':t.index,'new_slat':t.vertices[0] in newslatids})
assert not zero,zero[:10]
assert not any(x['new_slat'] for x in uvzero),uvzero[:10]
assert all(math.isfinite(c) for d in uv.data for c in d.uv)
assert all(math.isfinite(c) for p in ob.data.polygons for c in p.normal)
slats=[]
for g in gs:
 if classification(ob,g)!='slat':continue
 vv=[vs[i] for i in g];sb=bounds(vv);zc=(sb['min'][2]+sb['max'][2])/2
 mid=[v for v in vv if abs(v.z-zc)<.0005];cent=[v.y for v in mid if abs(v.x)<.005];edge=[v.y for v in mid if abs(v.x)>.90*max(abs(sb['min'][0]),abs(sb['max'][0]))]
 recess=sum(cent)/len(cent)-sum(edge)/len(edge);assert recess>.006
 centre=[v for v in vv if abs(v.x)<.005];lo=min(v.z for v in centre);hi=max(v.z for v in centre)
 low=[v.y for v in centre if abs(v.z-lo)<.0001];high=[v.y for v in centre if abs(v.z-hi)<.0001]
 angle=math.degrees(math.atan2(sum(high)/len(high)-sum(low)/len(low),hi-lo));assert 6<angle<14
 slats.append({'centre_z':zc,'measured_centre_minus_outer_band_y_m':recess,'measured_recline_deg':angle,'bounds':sb})
assert len(slats)==3
for c in ucx:
 bm=bmesh.new();bm.from_mesh(c.data);assert len(bm.verts)<=8 and all(e.is_manifold for e in bm.edges);assert bm.calc_volume()>0
 for face in bm.faces:
  centre=face.calc_center_median()
  assert all((v.co-centre).dot(face.normal)<1e-6 for v in bm.verts)
 bm.free()
cb=bounds([c.matrix_world@v.co for c in ucx for v in c.data.vertices])
assert all(cb['min'][k]>=old_bb['min'][k]-1e-6 and cb['max'][k]<=old_bb['max'][k]+1e-6 for k in range(3))
textures=[]
for name in ('wood-selected-v2.png','vinyl.png'):
 h=sha(ROOT/'textures'/name);assert h==sha(OLD/'textures'/name);textures.append({'file':'textures/'+name,'sha256':h,'matches_original':True})
manifest=json.loads((ROOT/'assembly.json').read_text());assert min(j['minimum_endpoint_embed_m'] for j in manifest['joint_checks'])>.006
report={'status':'PASS','fbx_sha256':sha(ROOT/'model/KI_CHAIR_02.fbx'),'original_fbx_sha256':sha(OLD/'model/KI_CHAIR_01.fbx'),'render_meshes':len(renders),'vertices':len(vs),'triangles':len(ob.data.loop_triangles),'ucx_hulls':len(ucx),'render_bounds':bb,'original_bounds':old_bb,'collision_bounds':bounds([c.matrix_world@v.co for c in ucx for v in c.data.vertices]),'preserved_vertices':len(ids),'preserved_geometry_uv_material_corners_match_within_1e6':True,'maximum_preserved_position_error_m':max_position_error,'maximum_preserved_uv_error':max_uv_error,'preserved_corner_count':sum(old_sig.values()),'finite_positions_normals_uvs':True,'zero_area_geometry_triangles':len(zero),'zero_area_uv_triangles_in_new_slats':0,'inherited_zero_area_uv_triangles':len(uvzero),'slats':sorted(slats,key=lambda x:x['centre_z']),'source_joint_checks':manifest['joint_checks'],'material_slots':[m.name.split('.')[0] for m in ob.data.materials],'textures':textures,'limitations':['Source/FBX validation only; Unreal legacy importer and real-map collision still require integration verification.','Inherited chair lowest geometry is 0.01237964 m above origin; this revision intentionally preserves the old actor fit.']}
(ROOT/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
