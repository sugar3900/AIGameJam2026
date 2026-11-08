"""Reimport exported FBXs in Blender and check geometry, UVs and bounds."""
import bpy, os, math
ROOT=os.path.dirname(os.path.abspath(__file__))
for name in ('KI_FRIDGE_BODY','KI_FRIDGE_DOOR'):
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.fbx(filepath=os.path.join(ROOT,'models',name+'.fbx'))
 meshes=[o for o in bpy.context.selected_objects if o.type=='MESH']
 if not meshes: raise RuntimeError(name+' missing mesh')
 for o in meshes:
  mesh=o.data; mesh.calc_loop_triangles()
  bad=sum(not all(math.isfinite(c) for c in v.co) for v in mesh.vertices)
  uvbad=sum(not all(math.isfinite(c) for c in loop.uv) for layer in mesh.uv_layers for loop in layer.data)
  degenerate=sum(t.area<1e-10 for t in mesh.loop_triangles)
  if bad or uvbad or degenerate or not mesh.uv_layers:
   raise RuntimeError(f'{name}: nonfinite={bad}, uv_nonfinite={uvbad}, degenerate={degenerate}, UV layers={len(mesh.uv_layers)}')
  print('VALID',name,'vertices',len(mesh.vertices),'triangles',len(mesh.loop_triangles),'bounds',tuple(round(v,3) for v in o.dimensions),'origin',tuple(round(v,3) for v in o.location))
