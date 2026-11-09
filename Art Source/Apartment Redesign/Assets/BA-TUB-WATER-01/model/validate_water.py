import bpy, math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(P.parent/'BA-TUB-01/model/BA_Tub.fbx'))
shell=bpy.data.objects.get('Tub_shell_hollow');bpy.context.view_layer.update()
tree=BVHTree.FromPolygons([shell.matrix_world@v.co for v in shell.data.vertices],[tuple(p.vertices) for p in shell.data.polygons],all_triangles=False)
pre=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=str(P/'model/BA_TUB_WATER_Surface.fbx'))
water=[o for o in bpy.data.objects if o not in pre and o.type=='MESH'];assert len(water)==1
obj=water[0];bpy.context.view_layer.update();me=obj.data; me.calc_loop_triangles()
assert me.uv_layers and len(me.polygons)>0
v=[obj.matrix_world@x.co for x in me.vertices]
assert all(math.isfinite(z) for xyz in v for z in xyz)
assert all(math.isfinite(z) for loop in me.uv_layers.active.data for z in loop.uv)
area=min((v[t.vertices[1]]-v[t.vertices[0]]).cross(v[t.vertices[2]]-v[t.vertices[0]]).length*.5 for t in me.loop_triangles)
assert area>1e-10, area
worst=10
for p in v:
 r=math.hypot(p.x,p.y)
 if r<1e-6: continue
 hit,normal,idx,d=tree.ray_cast(Vector((0,0,p.z)),Vector((p.x/r,p.y/r,0)),2)
 assert hit is not None
 worst=min(worst,d-r)
assert worst>.014, f'basin radial clearance {worst}'
assert max(p.z for p in v)<.57 and min(p.z for p in v)>.22
out=f'PASS: {len(water)} mesh, {len(v)} vertices, {len(me.loop_triangles)} triangles; finite UV/vertices; min triangle area {area:.9f} m²; minimum sampled wall clearance {worst:.6f} m; z range {min(p.z for p in v):.6f}..{max(p.z for p in v):.6f} m; local origin {tuple(obj.location)}\n'
print(out)
(P/'model/validation.txt').write_text(out)
