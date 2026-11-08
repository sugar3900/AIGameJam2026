"""Round-trip check exported rug geometry and UVs in Blender."""
import bpy, math
from pathlib import Path
p=Path(__file__).resolve().parent/'LV_RUG_01.fbx'
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(p)); meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert meshes, 'No meshes'
for o in meshes:
 m=o.data; m.calc_loop_triangles()
 assert all(all(math.isfinite(c) for c in v.co) for v in m.vertices), 'Non-finite vertex'
 assert all(math.isfinite(t.area) and t.area>1e-12 for t in m.loop_triangles), 'Zero-area triangle'
 assert m.uv_layers, 'Missing UVs'
 assert all(all(math.isfinite(c) for c in x.uv) for layer in m.uv_layers for x in layer.data), 'Non-finite UV'
 print(o.name, 'vertices',len(m.vertices),'triangles',len(m.loop_triangles),'dimensions',tuple(round(x,4) for x in o.dimensions))
print('RUG VALIDATION PASSED')
