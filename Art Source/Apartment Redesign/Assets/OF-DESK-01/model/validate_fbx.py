import bpy,math
from pathlib import Path
root=Path(__file__).resolve().parent
for p in sorted(root.glob('OF_DESK_*.fbx')):
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.fbx(filepath=str(p));objs=[o for o in bpy.context.selected_objects if o.type=='MESH'];assert objs
 for o in objs:
  m=o.data;m.calc_loop_triangles();bad=sum(not all(math.isfinite(x) for x in v.co) for v in m.vertices);badnorm=sum(not all(math.isfinite(x) for x in poly.normal) for poly in m.polygons);baduv=sum(not all(math.isfinite(x) for x in uv.uv) for layer in m.uv_layers for uv in layer.data);zero=sum(poly.area<1e-10 for poly in m.polygons);ztri=sum((m.vertices[t.vertices[1]].co-m.vertices[t.vertices[0]].co).cross(m.vertices[t.vertices[2]].co-m.vertices[t.vertices[0]].co).length<1e-10 for t in m.loop_triangles);print(p.name,'bad',bad,badnorm,baduv,'zero',zero,ztri,'uv',len(m.uv_layers));assert m.uv_layers and bad==badnorm==baduv==zero==ztri==0
print('PASS')
