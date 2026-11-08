import bpy, math
from pathlib import Path
from mathutils import Vector
D=Path(__file__).resolve().parent.parent
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(D/'model/HA_VASE_02.fbx'))
objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert len(objects)==1, f'expected one mesh: {len(objects)}'
o=objects[0];m=o.data;m.calc_loop_triangles();assert m.uv_layers.active
bad=bad_uv=nonfinite=0
for v in m.vertices:
 if not all(math.isfinite(c) for c in v.co): nonfinite+=1
for t in m.loop_triangles:
 a,b,c=[m.vertices[i].co for i in t.vertices]
 if (b-a).cross(c-a).length<1e-10:bad+=1
 uv=[m.uv_layers.active.data[i].uv for i in t.loops]
 if abs((uv[1].x-uv[0].x)*(uv[2].y-uv[0].y)-(uv[1].y-uv[0].y)*(uv[2].x-uv[0].x))<1e-12:bad_uv+=1
assert not (bad or bad_uv or nonfinite), f'degenerate={bad} uv={bad_uv} nonfinite={nonfinite}'
coords=[o.matrix_world@v.co for v in m.vertices]
dims=[max(c[i] for c in coords)-min(c[i] for c in coords) for i in range(3)]
assert all(abs(a-b)<.002 for a,b in zip(dims,[.22,.18,.268])),dims
# An open mouth means the central top-down ray hits the inner bottom rather than a cap at the lip.
inv=o.matrix_world.inverted();origin=inv@Vector((0,0,.35));direction=(inv.to_3x3()@Vector((0,0,-1))).normalized()
hit,loc,normal,index=o.ray_cast(origin,direction)
assert hit and (o.matrix_world@loc).z < .05, f'mouth blocked or cavity missing: hit={hit}, loc={loc}'
print(f'PASS meshes={len(objects)} vertices={len(m.vertices)} triangles={len(m.loop_triangles)} size_m={dims} zero_area={bad} zero_uv={bad_uv} nonfinite={nonfinite} cavity_bottom_z={(o.matrix_world@loc).z}')
