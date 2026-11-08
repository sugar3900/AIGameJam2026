import bpy, math
from pathlib import Path
from mathutils import Vector
p=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(p/'LV_Plant.fbx'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert meshes, 'No meshes imported'
vertices=faces=tris=missing_uv=bad=degenerate=0
bounds=[]
for ob in meshes:
    vertices+=len(ob.data.vertices); faces+=len(ob.data.polygons)
    ob.data.calc_loop_triangles(); tris+=len(ob.data.loop_triangles)
    if not ob.data.uv_layers: missing_uv+=1
    for v in ob.data.vertices:
        co=ob.matrix_world@v.co; bounds.append(co)
        if not all(math.isfinite(x) for x in co): bad+=1
    for poly in ob.data.polygons:
        if poly.area<1e-12: degenerate+=1
    for layer in ob.data.uv_layers:
        for uv in layer.data:
            if not all(math.isfinite(x) for x in uv.uv): bad+=1
mn=[min(v[i] for v in bounds) for i in range(3)]; mx=[max(v[i] for v in bounds) for i in range(3)]
print('VALIDATION meshes',len(meshes),'vertices',vertices,'faces',faces,'triangles',tris,'missing_uv',missing_uv,'nonfinite',bad,'degenerate',degenerate)
print('VALIDATION bounds_min',mn,'bounds_max',mx,'dimensions',[mx[i]-mn[i] for i in range(3)])
assert not (missing_uv or bad or degenerate)
