import bpy, os, math
ROOT=os.path.dirname(os.path.abspath(__file__))
for fname in ('ARC_Kitchen_Plaster_Wall_2m.fbx','ARC_Kitchen_Optional_Hairlines.fbx'):
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.fbx(filepath=os.path.join(ROOT,fname))
 meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert meshes
 for o in meshes:
  assert o.data.uv_layers.active, 'missing UVs'
  for v in o.data.vertices: assert all(math.isfinite(x) for x in v.co)
  for poly in o.data.polygons:
   assert poly.area>1e-10
   assert all(math.isfinite(x) for i in poly.loop_indices for x in o.data.uv_layers.active.data[i].uv)
  print(fname,o.name,'bounds',tuple(round(x,4) for x in o.dimensions),'verts',len(o.data.vertices),'polygons',len(o.data.polygons))
  if 'Wall_2m' in fname: assert all(abs(a-b)<.002 for a,b in zip(o.dimensions,(2,.12,2.75)))
print('VALIDATION OK: finite vertices/UVs, nonzero faces, wall bounds')
