"""Validate exported FBXs by importing each into an empty Blender scene."""
import bpy, math
from pathlib import Path
from mathutils.geometry import area_tri
root = Path(__file__).resolve().parent
failed = False
for path in sorted(root.glob('BA_Mirror_*.fbx')):
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.fbx(filepath=str(path))
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    issues = []
    triangles = 0
    for obj in meshes:
        mesh = obj.data
        if not mesh.uv_layers:
            issues.append(f'{obj.name}: missing UV layer')
        if any(not all(math.isfinite(v) for v in vertex.co) for vertex in mesh.vertices):
            issues.append(f'{obj.name}: non-finite vertex')
        mesh.calc_loop_triangles()
        triangles += len(mesh.loop_triangles)
        bad = sum(area_tri(*(mesh.vertices[i].co for i in t.vertices)) < 1e-12 for t in mesh.loop_triangles)
        if bad:
            issues.append(f'{obj.name}: {bad} degenerate triangles')
    if not meshes:
        issues.append('no mesh objects imported')
    print(f'VALIDATION {path.name}: {len(meshes)} objects, {triangles} triangles; ' + ('; '.join(issues) if issues else 'PASS'))
    failed |= bool(issues)
if failed:
    raise SystemExit('FBX validation failed')
