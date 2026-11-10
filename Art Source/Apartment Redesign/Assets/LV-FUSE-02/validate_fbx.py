from pathlib import Path
import bpy,bmesh,json,math
R=Path(__file__).resolve().parent

def read(p):
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(p));return next(o for o in bpy.context.scene.objects if o.type=='MESH')

def faces(o,exclude=False):
 m=o.data;remove=set()
 if exclude:
  adj={v.index:set() for v in m.vertices}
  for e in m.edges:a,b=e.vertices;adj[a].add(b);adj[b].add(a)
  left=set(adj)
  while left:
   a=left.pop();part={a};q=[a]
   while q:
    for b in adj[q.pop()]:
     if b in left:left.remove(b);q.append(b);part.add(b)
   zs=[(o.matrix_world@m.vertices[i].co).z for i in part]
   if min(zs)<-.00001 or max(zs)>.58001:remove.update(part)
  for p in m.polygons:
   if m.materials[p.material_index].name in ('Wire_Brick_Red','Wire_Navy'):remove.update(p.vertices)
 keys=[]
 for p in m.polygons:
  if any(v in remove for v in p.vertices):continue
  vs=[]
  for li in p.loop_indices:
   v=o.matrix_world@m.vertices[m.loops[li].vertex_index].co;uv=m.uv_layers.active.data[li].uv;vs.append(tuple(round(float(t),5) for t in (*v,*uv)))
  keys.append((m.materials[p.material_index].name,tuple(sorted(vs))))
 return set(keys)
old=read(R.parent/'LV-FUSE-01/exports/LV_FUSE_01_Shell.fbx');original=faces(old,True)
new=read(R/'models/LV_Fuse02_Shell.fbx');current=faces(new)
missing=original-current
assert not missing,('original faces/UVs changed',len(missing),list(missing)[:1])
m=new.data;assert all(math.isfinite(c) for v in m.vertices for c in v.co)
assert m.uv_layers and all(math.isfinite(c) for uv in m.uv_layers.active.data for c in uv.uv)
assert all(p.area>1e-12 for p in m.polygons)
xyz=[new.matrix_world@v.co for v in m.vertices];assert min(v.z for v in xyz)>-.00001 and max(v.z for v in xyz)<.58001
newslots={p.material_index for p in m.polygons if m.materials[p.material_index].name.startswith('Fuse02_')}
for p in m.polygons:
 if p.material_index in newslots:
  for i in p.vertices:
   v=xyz[i];assert v.y>=-.120 and not(abs(v.x)<.11 and .206<v.z<.409 and v.y<-.112)
r={'status':'passed','checks':['fresh FBX import','all retained original case/fuse/hinge polygon positions and UVs match within10um','finite nondegenerate faces and UVs','external stubs absent','new wiring behind door/gasket and fuse faces'],'retained_face_keys':len(original),'polygons':len(m.polygons),'triangles':sum(len(p.vertices)-2 for p in m.polygons),'min':[min(v[i] for v in xyz) for i in range(3)],'max':[max(v[i] for v in xyz) for i in range(3)]}
(R/'fbx-validation.json').write_text(json.dumps(r,indent=2)+'\n');print('FIX030 VALIDATION PASS',r)
