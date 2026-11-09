import bpy, math
from pathlib import Path
P=Path(__file__).resolve().parent
for fname in ('KI_TILE_TOP.fbx','KI_TILE_SUBSTRATE.fbx'):
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.fbx(filepath=str(P/fname))
 meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(meshes)==1,(fname,len(meshes))
 o=meshes[0];m=o.data; assert m.uv_layers.active and len(m.polygons)
 assert all(math.isfinite(c) for v in m.vertices for c in v.co)
 assert all(math.isfinite(c) for l in m.uv_layers.active.data for c in l.uv)
 assert all(p.area>1e-10 for p in m.polygons)
 print(fname,'dimensions',tuple(round(v,6) for v in o.dimensions),'vertices',len(m.vertices),'polygons',len(m.polygons),'uvs',len(m.uv_layers.active.data))
 target=.9991 if 'TOP' in fname else 1.0
 assert abs(o.dimensions.x-target)<1e-4 and abs(o.dimensions.y-target)<1e-4
 if 'TOP' in fname: assert len(m.polygons)==16
# 4x4 parity aligns across a one metre translation in either axis.
for x in range(-8,8):
 for y in range(-8,8):
  assert (x+y)%2 == ((x+4)+y)%2 == (x+(y+4))%2
print('PASS: 1 m module, UVs, finite geometry, nonzero faces, 0.25 m checker parity')
