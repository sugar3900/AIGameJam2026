"""Fresh legacy FBX roundtrip and closed-shell checks; run after build_faucet.py."""
import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Matrix
ROOT=Path(__file__).resolve().parent
ref=json.loads((ROOT/'validation.json').read_text())
result={}
for name,expected in ref['exports'].items():
 bpy.ops.wm.read_factory_settings(use_empty=True)
 bpy.ops.import_scene.fbx(filepath=str(ROOT/'models'/f'{name}.fbx'))
 meshes=[o for o in bpy.data.objects if o.type=='MESH'];visual=[o for o in meshes if not o.name.startswith('UCX_')]
 assert len(visual)==1, (name,'visual count',len(visual))
 o=visual[0];vs=[o.matrix_world@v.co for v in o.data.vertices]
 bounds={k:[f(v[i] for v in vs) for i in range(3)] for k,f in [('min',min),('max',max)]}
 error=max(abs(bounds[k][i]-expected[k][i]) for k in bounds for i in range(3));assert error<.000002,(name,error)
 slots=[m.name.split('.')[0] for m in o.data.materials];assert slots==expected['materials'],slots
 uv=o.data.uv_layers.active;assert uv and len(uv.data)==len(o.data.loops)
 assert all(math.isfinite(c) for d in uv.data for c in d.uv)
 assert all(p.area>1e-12 for p in o.data.polygons)
 hulls=[h for h in meshes if h.name.startswith('UCX_')]
 assert len(hulls)==(0 if name.endswith('body') else 1)
 hr=[]
 for h in hulls:
  bm=bmesh.new();bm.from_mesh(h.data)
  assert all(e.is_manifold for e in bm.edges),h.name
  volume=bm.calc_volume(signed=True);assert volume>0,h.name
  hr.append({'name':h.name,'vertices':len(bm.verts),'closed':True,'positive_volume_m3':volume});bm.free()
 textures={}
 for m in o.data.materials:
  links=m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].links
  textures[m.name]=[l.from_node.image.name for l in links if l.from_node.type=='TEX_IMAGE']
 if name.endswith('body'):assert textures['Sink_SagePaint'] and textures['Sink_AgedEnamel']
 else:assert textures['Sink_AgedEnamel']
 result[name]={'bounds':bounds,'max_bounds_error_m':error,'UVs_finite':True,'slots':slots,'direct_basecolor_images':textures,'UCX':hr,'origin':list(o.location),'polygon_count':len(o.data.polygons)}
# Source checks separate from FBX. Source origin reflects actual animation datum;
# exporters may bake transforms, so preserve explicit assembly.json pivot contract.
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'models/KI_FAUCET_02_assembly.blend'))
body=bpy.data.objects['KI_FAUCET_02_sink_body'];parts={}
for side in ('L','R'):
 o=bpy.data.objects['KI_FAUCET_02_'+side+'_tap'];wanted=ref['tap_pivots'][side]['source_pivot'];assert max(abs(o.location[i]-wanted[i]) for i in range(3))<1e-6
 bm=bmesh.new();bm.from_mesh(o.data);assert all(e.is_manifold for e in bm.edges);assert bm.calc_volume(signed=True)>0;bm.free()
 # 0..90 degree pivot sweep: any tap vertex behind upstand front must be above its top.
 clearance=[]
 for degree in range(91):
  r=Matrix.Rotation(math.radians(degree),4,'Z')
  pts=[o.location+r@v.co for v in o.data.vertices]
  behind=[v.z-1.135 for v in pts if v.y>=.2345]
  clearance.append(min(behind) if behind else 1)
 assert min(clearance)>.012,clearance
 parts[side]={'source_origin':list(o.location),'closed_shells':True,'tap_sweep_0_to_90_min_upstand_clearance_m':min(clearance)}
# New faucet connected islands above .98 only, not original lower trap/supports.
bm=bmesh.new();bm.from_mesh(body.data);newverts=[v for v in bm.verts if v.co.z>.98]
# Check whole body nonmanifold count for context; originals intentionally inherited.
edge_count=sum(not e.is_manifold for e in bm.edges);bm.free()
# All new connected shells (minimum Z above .98) must have outward normals and no open edges.
me=body.data;adj=[[] for v in me.vertices]
for e in me.edges:
 a,b=e.vertices;adj[a].append(b);adj[b].append(a)
seen=set();closed_new=0
for i in range(len(adj)):
 if i in seen:continue
 q=[i];seen.add(i);ids=[]
 while q:
  j=q.pop();ids.append(j)
  for k in adj[j]:
   if k not in seen:seen.add(k);q.append(k)
 if min(me.vertices[j].co.z for j in ids)<=.98:continue
 chosen=set(ids);verts=[tuple(me.vertices[j].co) for j in ids];mapping={j:k for k,j in enumerate(ids)}
 polys=[tuple(mapping[j] for j in p.vertices) for p in me.polygons if all(j in chosen for j in p.vertices)]
 temp=bpy.data.meshes.new('ValidationShell');temp.from_pydata(verts,[],polys)
 bm=bmesh.new();bm.from_mesh(temp);assert all(e.is_manifold for e in bm.edges);assert bm.calc_volume(signed=True)>0
 bm.free();bpy.data.meshes.remove(temp);closed_new+=1
bpy.ops.wm.open_mainfile(filepath=str(ROOT.parent/'KI-LEAK-02/models/KI_LEAK_02_assembly.blend'))
bm=bmesh.new();bm.from_mesh(bpy.data.objects['KI_LEAK_02_sink_body'].data)
original_edges=sum(not e.is_manifold for e in bm.edges);bm.free()
assert original_edges>=edge_count,(original_edges,edge_count) # old faucet itself also had open edges; all new islands checked closed above
out={'status':'PASS','fbx':result,'tap_source_checks':parts,'body_inherited_nonmanifold_edges':edge_count,'original_body_nonmanifold_edges':original_edges,'new_body_faucet_closed_positive_volume_islands':closed_new,'engine_validation_pending':['Use existing body actor transform; verify source outlet against existing stream','Rebind tap Body/pivot/rotation axis without changing Sink_Tap identity','Real open/close/toggle and no stream jump in PIE','Recheck leak/repair and window clearance in integrated scene']}
(ROOT/'fbx-validation.json').write_text(json.dumps(out,indent=2)+'\n')
print('FBX_VALIDATION_PASS',json.dumps(out))
