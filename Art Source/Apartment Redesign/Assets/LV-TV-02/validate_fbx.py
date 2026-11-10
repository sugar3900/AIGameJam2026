from pathlib import Path
import bpy,bmesh,json,math
R=Path(__file__).resolve().parent

def read(p):
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(p));return next(o for o in bpy.context.scene.objects if o.type=='MESH')

def faces(o,stand=False):
 m=o.data;keys=[]
 for p in m.polygons:
  if stand and max((o.matrix_world@m.vertices[i].co).z for i in p.vertices)>.66:continue
  vs=[]
  for li in p.loop_indices:
   v=o.matrix_world@m.vertices[m.loops[li].vertex_index].co;uv=m.uv_layers.active.data[li].uv;vs.append(tuple(round(float(t),5) for t in (*v,*uv)))
  keys.append((m.materials[p.material_index].name,tuple(sorted(vs))))
 return set(keys)
old=read(R.parent/'LV-TV-01/model/LV_TV_body.fbx');original=faces(old,True)
stand=read(R/'models/LV_TV02_Stand.fbx');assert original==faces(stand),('stand geometry or UV mismatch',len(original-faces(stand)),len(faces(stand)-original))
reports=[]
for name in ('Stand','Housing','Screen'):
 o=read(R/'models'/('LV_TV02_'+name+'.fbx'));m=o.data;xyz=[o.matrix_world@v.co for v in m.vertices]
 assert all(math.isfinite(c) for v in xyz for c in v)
 assert m.uv_layers and all(math.isfinite(c) for uv in m.uv_layers.active.data for c in uv.uv)
 assert all(p.area>1e-12 for p in m.polygons),name
 lo=[min(v[i] for v in xyz) for i in range(3)];hi=[max(v[i] for v in xyz) for i in range(3)]
 if name=='Housing':assert abs(lo[2]-.6475)<1e-5 and hi[2]<1.45 and lo[0]>=-.55 and hi[0]<=.55 and lo[1]>=-.23 and hi[1]<=.22
 if name=='Screen':
  assert lo[1]>-.200 and hi[1]<-.12
  bm=bmesh.new();bm.from_mesh(m);bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=1e-7);assert not any(e.is_boundary for e in bm.edges);assert bm.calc_volume(signed=True)>0;bm.free()
  # Centre face points toward room (-Y), not culled from the front.
  front=[p for p in m.polygons if p.center.y<-.181];assert front and all(p.normal.y<0 for p in front)
 reports.append({'mesh':o.name,'min':lo,'max':hi,'slots':[slot.name for slot in o.material_slots],'triangles':sum(len(p.vertices)-2 for p in m.polygons)})
(R/'fbx-validation.json').write_text(json.dumps({'status':'passed','checks':['exact original stand face positions/UVs/material slots within10um','fresh FBX imports','finite UVs and nondegenerate faces','cabinet rests64.75cm and fits stand/art envelope','screen closed positive volume and outward front normals','screen fully behind front bezel'],'exports':reports},indent=2)+'\n');print('FIX031 VALIDATION PASS')
