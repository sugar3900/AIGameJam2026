import bpy, math, os, glob
root=os.path.join(os.path.dirname(os.path.abspath(__file__)),'models')
fail=False
for f in sorted(glob.glob(os.path.join(root,'*.fbx'))):
 bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.fbx(filepath=f)
 objs=[o for o in bpy.context.selected_objects if o.type=='MESH']
 if not objs: print('FAIL',f,'no meshes'); fail=True;continue
 for o in objs:
  m=o.data; bad=sum(not all(math.isfinite(c) for c in v.co) for v in m.vertices); deg=sum(p.area<1e-10 for p in m.polygons); uvbad=sum(not all(math.isfinite(c) for c in l.uv) for u in m.uv_layers for l in u.data); print(os.path.basename(f),'verts',len(m.vertices),'faces',len(m.polygons),'nonfinite',bad,'degenerate',deg,'badUV',uvbad,'uvlayers',len(m.uv_layers),'bounds',tuple(round(v,3) for v in o.dimensions)); fail |= bool(bad or deg or uvbad or not m.uv_layers)
if fail: raise RuntimeError('Validation failed')
