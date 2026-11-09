import bpy, math
from pathlib import Path
P=Path(__file__).resolve().parent
for name in ['LV_SIDE_TABLE_BODY.fbx','LV_SIDE_TABLE_DRAWER.fbx']:
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.fbx(filepath=str(P/name))
 a=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(a)==1
 o=a[0];m=o.data; assert m.uv_layers.active
 assert all(math.isfinite(c) for v in m.vertices for c in v.co)
 assert all(math.isfinite(c) for uv in m.uv_layers.active.data for c in uv.uv)
 m.calc_loop_triangles();assert all(t.area>1e-10 for t in m.loop_triangles)
 assert all(abs(c)<1e-5 for c in o.location),o.location
 if 'BODY' in name: assert all(abs(a-b)<1e-3 for a,b in zip(o.dimensions,(.37,.35,.54)))
 print(name, 'vertices',len(m.vertices),'triangles',len(m.loop_triangles),'dimensions',tuple(round(v,4) for v in o.dimensions),'origin',tuple(o.location))
print('PASS finite geometry, UVs, triangle area, expected size and common origin')
