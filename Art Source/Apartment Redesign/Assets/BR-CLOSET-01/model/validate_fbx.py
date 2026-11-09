import bpy, math, os, glob
root=os.path.dirname(os.path.abspath(__file__))
for path in sorted(glob.glob(os.path.join(root,'BR_Closet_*.fbx'))):
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.fbx(filepath=path)
 objects=[o for o in bpy.context.selected_objects if o.type=='MESH']; assert objects,path
 for o in objects:
  mesh=o.data
  bad=sum(not all(math.isfinite(v) for v in p.co) for p in mesh.vertices)
  deg=sum(poly.area<1e-10 for poly in mesh.polygons)
  uvbad=sum(not all(math.isfinite(v) for v in loop.uv) for uv in mesh.uv_layers for loop in uv.data)
  print(os.path.basename(path),'verts',len(mesh.vertices),'bad',bad,'degenerate',deg,'bad_uv',uvbad,'bounds',tuple(round(v,3) for v in o.dimensions))
  assert not (bad or deg or uvbad)
