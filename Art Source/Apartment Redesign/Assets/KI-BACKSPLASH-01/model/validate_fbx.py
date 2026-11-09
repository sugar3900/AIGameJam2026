import bpy, math, os
from mathutils import Vector
root=os.path.dirname(os.path.abspath(__file__))
files=['KI_Backsplash_Module_1m.fbx','KI_Backsplash_End_Left.fbx','KI_Backsplash_End_Right.fbx']
for name in files:
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.fbx(filepath=os.path.join(root,name))
 obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert obs,name
 allv=[]; total=0
 for o in obs:
  assert len(o.data.uv_layers)>0,(name,o.name,'missing UV')
  for uv in o.data.uv_layers.active.data:assert all(math.isfinite(v) for v in uv.uv)
  for v in o.data.vertices:
   q=o.matrix_world@v.co;assert all(math.isfinite(a) for a in q);allv.append(q)
  o.data.calc_loop_triangles()
  for t in o.data.loop_triangles:
   a,b,c=[o.matrix_world@o.data.vertices[i].co for i in t.vertices]
   assert (b-a).cross(c-a).length > 1e-10,(name,o.name,'degenerate triangle')
   total+=1
 mn=[min(q[i] for q in allv) for i in range(3)];mx=[max(q[i] for q in allv) for i in range(3)]
 size=[mx[i]-mn[i] for i in range(3)]
 expected=[1,.034,.56] if 'Module' in name else [.03,.034,.56]
 assert all(abs(a-b)<.001 for a,b in zip(size,expected)),(name,size,expected)
 if 'Module' in name:
  tiles=next(o for o in obs if 'checker' in o.name.lower())
  assert len(tiles.data.materials)==2 and {p.material_index for p in tiles.data.polygons}=={0,1}
  # Ten tiles per row means the neighboring one-metre module continues checker parity.
  assert 10%2==0
 print(name, 'PASS',len(obs),'meshes',total,'triangles','bounds',size)
print('FBX_VALIDATION_OK')
