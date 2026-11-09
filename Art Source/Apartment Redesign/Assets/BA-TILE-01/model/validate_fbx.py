import bpy, math, os
root=os.path.dirname(os.path.abspath(__file__))
for f in ('BA_Tile_1m_Module.fbx','BA_Tile_040_Extension.fbx','BA_Tile_Cap.fbx','BA_Tile_Damage.fbx'):
 bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.fbx(filepath=os.path.join(root,f))
 objs=[o for o in bpy.context.scene.objects if o.type=='MESH']; assert objs
 verts=tris=bad=zero=uvbad=uvmissing=0; xyz=[]
 for o in objs:
  m=o.data; m.calc_loop_triangles(); verts+=len(m.vertices); tris+=len(m.loop_triangles)
  if not m.uv_layers: uvmissing+=1
  for v in m.vertices:
   p=o.matrix_world @ v.co; xyz.append(p); bad+=not all(math.isfinite(c) for c in p)
  for t in m.loop_triangles:
   a,b,c=(o.matrix_world @ m.vertices[i].co for i in t.vertices); zero+=(b-a).cross(c-a).length<1e-12
  for uv in m.uv_layers:
   for t in uv.data: uvbad+=not all(math.isfinite(c) for c in t.uv)
 lo=tuple(round(min(v[i] for v in xyz),4) for i in range(3)); hi=tuple(round(max(v[i] for v in xyz),4) for i in range(3))
 print('FBX_CHECK',f,'objects',len(objs),'vertices',verts,'triangles',tris,'nonfinite',bad,'zero_area',zero,'bad_uv',uvbad,'missing_uv',uvmissing,'bounds',lo,hi)
 if bad or zero or uvbad or uvmissing: raise RuntimeError('Invalid export '+f)
 if f in ('BA_Tile_1m_Module.fbx','BA_Tile_040_Extension.fbx'):
  colored=[o for o in objs if len(o.data.materials)>=8]; assert len(colored)==1
  used=set(p.material_index for p in colored[0].data.polygons); print('GLAZE_SLOTS',f,len(colored[0].data.materials),'used',sorted(used)); assert len(used)==8
 if f=='BA_Tile_1m_Module.fbx': assert abs((hi[0]-lo[0])-1)<.001 and abs((hi[2]-lo[2])-1.1)<.001
 if f=='BA_Tile_040_Extension.fbx': assert abs((hi[0]-lo[0])-1)<.001 and abs((hi[2]-lo[2])-.4)<.001
 if f=='BA_Tile_Cap.fbx': assert abs((hi[0]-lo[0])-1)<.001 and abs((hi[2]-lo[2])-.05)<.001
 if f=='BA_Tile_Damage.fbx': assert 0<=lo[0]<=hi[0]<=1 and 0<=lo[2]<=hi[2]<=1.1
print('FBX_VALIDATION_OK')
