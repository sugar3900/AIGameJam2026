import bpy, math, os, glob
from mathutils import Vector
p=os.path.dirname(os.path.abspath(__file__))
for f in sorted(glob.glob(os.path.join(p,'BA_Toilet*.fbx'))):
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.fbx(filepath=f)
 for o in bpy.context.selected_objects:
  if o.type!='MESH':continue
  m=o.data; bad=sum(not all(math.isfinite(v) for v in x.co) for x in m.vertices); uvbad=sum(not all(math.isfinite(v) for v in x.uv) for uv in m.uv_layers for x in uv.data); m.calc_loop_triangles(); deg=sum(t.area < 1e-10 for t in m.loop_triangles)
  print('CHECK',os.path.basename(f),'verts',len(m.vertices),'uv_layers',len(m.uv_layers),'nonfinite',bad,'bad_uv',uvbad,'degenerate_triangles',deg,'location',tuple(round(c,4) for c in o.location),'dimensions',tuple(round(c,4) for c in o.dimensions))
  if bad or uvbad or deg or not len(m.uv_layers): raise RuntimeError('invalid mesh '+f)
