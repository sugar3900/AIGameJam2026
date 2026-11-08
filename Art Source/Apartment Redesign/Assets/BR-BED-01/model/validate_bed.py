import bpy, math, os, sys
from mathutils import Vector
root=os.path.dirname(os.path.abspath(__file__))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=os.path.join(root,sys.argv[-1] if '--' in sys.argv else 'BR_Bed_Complete.fbx'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];bad=deg=uvbad=0; mins=[float('inf')]*3;maxs=[-float('inf')]*3
for o in meshes:
 for v in o.data.vertices:
  p=o.matrix_world@v.co
  bad+=not all(math.isfinite(x) for x in p)
  for k in range(3): mins[k]=min(mins[k],p[k]);maxs[k]=max(maxs[k],p[k])
 for p in o.data.polygons: deg+=p.area<1e-10
 for layer in o.data.uv_layers:
  for l in layer.data: uvbad+=not all(math.isfinite(v) for v in l.uv)
 if not o.data.uv_layers: print('MISSING_UV',o.name);bad+=1
print('CHECK','meshes',len(meshes),'bad',bad,'degenerate',deg,'bad_uv',uvbad,'bounds',[(round(mins[k],3),round(maxs[k],3)) for k in range(3)])
if bad or deg or uvbad: raise RuntimeError('FBX geometry validation failed')
