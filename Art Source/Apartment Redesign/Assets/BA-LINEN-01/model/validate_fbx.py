import bpy, math, os, glob
root=os.path.dirname(os.path.abspath(__file__))
failed=False
for f in sorted(glob.glob(os.path.join(root,'*.fbx'))):
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.fbx(filepath=f)
 objs=[o for o in bpy.context.selected_objects if o.type=='MESH']
 if not objs:print('FAIL no mesh',f);failed=True;continue
 for o in objs:
  m=o.data;m.calc_loop_triangles()
  bad=sum(not all(math.isfinite(c) for c in v.co) for v in m.vertices)
  badnorm=sum(not all(math.isfinite(c) for c in p.normal) for p in m.polygons)
  uvbad=sum(not all(math.isfinite(c) for c in l.uv) for u in m.uv_layers for l in u.data)
  badtri=sum(t.area<1e-10 for t in m.loop_triangles)
  print(os.path.basename(f),'verts',len(m.vertices),'tris',len(m.loop_triangles),'nonfinite',bad,'badnormal',badnorm,'badUV',uvbad,'zeroarea',badtri,'UVlayers',len(m.uv_layers),'bounds',tuple(round(x,4) for x in o.dimensions),'origin',tuple(round(x,4) for x in o.location))
  failed |= bool(bad or badnorm or uvbad or badtri or not m.uv_layers)
if failed:raise RuntimeError('Invalid exported cabinet geometry')
