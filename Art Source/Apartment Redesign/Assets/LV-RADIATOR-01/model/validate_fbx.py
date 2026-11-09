import bpy, math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(P/'LV_Radiator.fbx'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert meshes, 'No meshes imported'
verts=faces=0
points=[]
for o in meshes:
    assert len(o.data.uv_layers)>0, f'{o.name}: no UV layer'
    assert len(o.data.vertices)>0 and len(o.data.polygons)>0, f'{o.name}: empty geometry'
    assert all(p.area>1e-11 for p in o.data.polygons), f'{o.name}: zero-area polygon'
    for uv in o.data.uv_layers.active.data: assert math.isfinite(uv.uv.x) and math.isfinite(uv.uv.y), f'{o.name}: invalid UV'
    points.extend(o.matrix_world@v.co for v in o.data.vertices);verts+=len(o.data.vertices);faces+=len(o.data.polygons)
lo=[min(p[i] for p in points) for i in range(3)];hi=[max(p[i] for p in points) for i in range(3)]
print('VALIDATED meshes',len(meshes),'vertices',verts,'faces',faces,'bounds meters', [round(hi[i]-lo[i],3) for i in range(3)],'min',lo,'max',hi)
