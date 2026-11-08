import bpy, math
from pathlib import Path
root=Path(__file__).resolve().parent
for name in ('ARC_CeilingLight_Hardware.fbx','ARC_CeilingLight_Glass.fbx'):
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.fbx(filepath=str(root/name))
 meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']; assert meshes,name
 for ob in meshes:
  assert len(ob.data.uv_layers)>0, (name,ob.name,'missing UV')
  assert all(math.isfinite(c) for v in ob.data.vertices for c in v.co), (name,'nonfinite')
  assert all(p.area>1e-12 for p in ob.data.polygons),(name,'degenerate')
  assert all(math.isfinite(c) for uv in ob.data.uv_layers.active.data for c in uv.uv),(name,'invalid UV')
  print(name, ob.name, 'verts',len(ob.data.vertices),'faces',len(ob.data.polygons),'dimensions', tuple(round(x,4) for x in ob.dimensions),'origin',tuple(round(x,4) for x in ob.location))
print('PASS finite geometry, nonzero faces, UVs, and bounds')
