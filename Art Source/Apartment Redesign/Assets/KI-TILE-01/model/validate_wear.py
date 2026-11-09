import bpy, math
from pathlib import Path
P=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(P/'KI_TILE_WEAR_4x3.fbx'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(meshes)==1
m=meshes[0]; assert m.data.uv_layers.active
assert abs(m.dimensions.x-4)<1e-5 and abs(m.dimensions.y-3)<1e-5
assert all(math.isfinite(v) for p in m.data.vertices for v in p.co)
assert all(math.isfinite(v) and -1e-5<=v<=1.00001 for p in m.data.uv_layers.active.data for v in p.uv)
assert all(p.area>1e-9 for p in m.data.polygons)
print('PASS overlay',tuple(m.dimensions),len(m.data.polygons),'faces UVs valid')
