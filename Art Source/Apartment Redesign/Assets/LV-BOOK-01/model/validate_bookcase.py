import bpy, os, glob, math
from mathutils import Vector
root=os.path.dirname(os.path.abspath(__file__))
for p in sorted(glob.glob(os.path.join(root,'LV_BOOK_*.fbx'))):
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.fbx(filepath=p)
 objs=[o for o in bpy.context.scene.objects if o.type=='MESH']; bad=deg=uvbad=0; tris=0
 for o in objs:
  m=o.data;m.calc_loop_triangles()
  bad+=sum(not all(math.isfinite(c) for c in v.co) for v in m.vertices)
  uvbad+=sum(not all(math.isfinite(c) for c in l.uv) for uv in m.uv_layers for l in uv.data)
  for t in m.loop_triangles:
   a,b,c=(m.vertices[i].co for i in t.vertices);tris+=1
   if (b-a).cross(c-a).length<1e-10:deg+=1
 print(os.path.basename(p),'meshes',len(objs),'triangles',tris,'bad_vertices',bad,'bad_uvs',uvbad,'degenerate',deg)
 if bad or uvbad or deg or not objs: raise RuntimeError('Invalid export')
