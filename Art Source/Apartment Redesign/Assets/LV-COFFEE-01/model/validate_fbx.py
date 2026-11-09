import bpy, math, os
from pathlib import Path
p=Path(__file__).resolve().parent/'LV_COFFEE_01.fbx'
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(p))
objs=[o for o in bpy.context.selected_objects if o.type=='MESH']
assert objs, 'FBX has no meshes'
for o in objs:
 m=o.data; m.calc_loop_triangles()
 bad=sum(not all(math.isfinite(v) for v in vert.co) for vert in m.vertices)
 baduv=sum(not all(math.isfinite(v) for v in loop.uv) for u in m.uv_layers for loop in u.data)
 badnorm=sum(not all(math.isfinite(v) for v in p.normal) for p in m.polygons)
 tiny=sum(p.area<1e-10 for p in m.polygons)
 tri_tiny=0
 for t in m.loop_triangles:
  a,b,c=(m.vertices[i].co for i in t.vertices)
  if (b-a).cross(c-a).length < 1e-10: tri_tiny+=1
 print('VALIDATE',o.name,'verts',len(m.vertices),'faces',len(m.polygons),'bad vertex/uv/norm',bad,baduv,badnorm,'tiny polygons/triangles',tiny,tri_tiny,'dimensions',tuple(round(x,4) for x in o.dimensions),'slots',[x.name for x in m.materials])
 assert m.uv_layers and bad==baduv==badnorm==tiny==tri_tiny==0
 assert abs(o.dimensions.x-1.2)<.015 and abs(o.dimensions.y-.60)<.015 and .42<o.dimensions.z<.48
print('PASS')
