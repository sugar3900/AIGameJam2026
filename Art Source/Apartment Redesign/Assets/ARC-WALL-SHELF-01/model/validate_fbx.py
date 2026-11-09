import bpy,math
from pathlib import Path
p=Path(__file__).resolve().parent/'ARC_WALL_SHELF_01.fbx'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.fbx(filepath=str(p));objs=[o for o in bpy.context.selected_objects if o.type=='MESH'];assert objs
for o in objs:
 m=o.data;m.calc_loop_triangles();bad=sum(not all(math.isfinite(x) for x in v.co) for v in m.vertices);badnorm=sum(not all(math.isfinite(x) for x in f.normal) for f in m.polygons);baduv=sum(not all(math.isfinite(x) for x in uv.uv) for layer in m.uv_layers for uv in layer.data);zero=sum(f.area<1e-10 for f in m.polygons);ztri=sum((m.vertices[t.vertices[1]].co-m.vertices[t.vertices[0]].co).cross(m.vertices[t.vertices[2]].co-m.vertices[t.vertices[0]].co).length<1e-10 for t in m.loop_triangles)
 print(o.name,'verts',len(m.vertices),'triangles',len(m.loop_triangles),'bad positions/normals/UVs',bad,badnorm,baduv,'degenerate faces/triangles',zero,ztri,'UV layers',len(m.uv_layers),'bounds',tuple(round(d,5) for d in o.dimensions))
 assert m.uv_layers and bad==badnorm==baduv==zero==ztri==0
 assert all(abs(a-b)<.002 for a,b in zip(o.dimensions,(.65,.15,.145)))
print('PASS')
