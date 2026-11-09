import bpy, math, json
from pathlib import Path
from mathutils import Vector
p=Path(__file__).resolve().parent/'LV_Fuse_Plaster_Damage.fbx'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(p));meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert len(meshes)==1, len(meshes)
o=meshes[0];me=o.data;assert me.uv_layers.active
assert all(math.isfinite(v) for v in o.matrix_world for v in v)
for v in me.vertices:
 assert all(math.isfinite(x) for x in v.co)
for v in me.uv_layers.active.data:
 assert all(math.isfinite(x) for x in v.uv)
assert all(p.area>1e-12 for p in me.polygons)
world=[o.matrix_world@v.co for v in me.vertices]
bounds=[[min(v[i] for v in world),max(v[i] for v in world)] for i in range(3)]
assert bounds[0][0]<-.35 and bounds[0][1]>.35 and bounds[2][0]<-.14 and bounds[2][1]>.75
print(json.dumps({'meshes':len(meshes),'vertices':len(me.vertices),'faces':len(me.polygons),'bounds_m':bounds,'object_location_m':list(o.location),'material_slots':[s.material.name if s.material else None for s in o.material_slots], 'uv':'present and finite', 'zero_area_faces':0}))
