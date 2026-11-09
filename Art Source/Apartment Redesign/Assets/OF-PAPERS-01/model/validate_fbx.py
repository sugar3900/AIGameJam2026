import bpy, math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(P/'OF_PAPERS_01.fbx'))
objs=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert len(objs)==5, f'expected five sheets, got {len(objs)}'
verts=faces=zero=uvzero=bad=0
points=[]
for o in objs:
 m=o.data;m.calc_loop_triangles();assert m.uv_layers.active is not None
 for v in m.vertices:
  xyz=o.matrix_world@v.co; points.append(xyz);bad+=not all(math.isfinite(q) for q in xyz);verts+=1
 for t in m.loop_triangles:
  a,b,c=[m.vertices[i].co for i in t.vertices];zero+=((b-a).cross(c-a)).length<1e-12;faces+=1
  uv=m.uv_layers.active.data;u,v,w=[Vector(uv[i].uv) for i in t.loops];uvzero+=abs((v.x-u.x)*(w.y-u.y)-(v.y-u.y)*(w.x-u.x))<1e-12
  bad+=not all(math.isfinite(q) for vv in (u,v,w) for q in vv)
bounds=[max(p[i] for p in points)-min(p[i] for p in points) for i in range(3)]
print('Objects:',len(objs),'vertices:',verts,'triangles:',faces,'zero geometry:',zero,'zero UV triangles:',uvzero,'nonfinite:',bad,'bounds meters:',[round(n,5) for n in bounds])
assert not zero and not uvzero and not bad
assert .20<bounds[0]<.36 and .20<bounds[1]<.36 and bounds[2]<.04
