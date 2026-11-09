import bpy, math
from pathlib import Path
root=Path(__file__).resolve().parent
for name in ('Curtain_Rod.fbx','Curtain_Left.fbx','Curtain_Right.fbx'):
 path=root/name
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.fbx(filepath=str(path));obs=[o for o in bpy.context.selected_objects if o.type=='MESH'];assert obs,path
 for o in obs:
  m=o.data;m.calc_loop_triangles();assert m.uv_layers,(name,'no UV')
  if name!='Curtain_Rod.fbx':
   assert any(x.type=='ARMATURE' for x in bpy.context.selected_objects),(name,'missing armature')
   keys=m.shape_keys;assert keys and 'Closed' in keys.key_blocks,(name,'missing morph target');assert len(keys.key_blocks['Closed'].data)==len(m.vertices),(name,'topology mismatch')
   for k in keys.key_blocks:
    for v in k.data:assert all(math.isfinite(c) for c in v.co),(name,'nonfinite morph coordinate')
   for val in (0,.5,1):
    keys.key_blocks['Closed'].value=val;bpy.context.view_layer.update();ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());em=ev.to_mesh();em.calc_loop_triangles()
    for t in em.loop_triangles:
     a,b,c=(em.vertices[i].co for i in t.vertices);assert (b-a).cross(c-a).length>1e-10,(name,val,'zero triangle');assert all(math.isfinite(c) for c in t.normal),(name,val,'nonfinite normal')
    ev.to_mesh_clear()
  else:
   for v in m.vertices:assert all(math.isfinite(c) for c in v.co),(name,'nonfinite vertex')
   for t in m.loop_triangles:
    a,b,c=(m.vertices[i].co for i in t.vertices);assert (b-a).cross(c-a).length>1e-10,(name,'zero triangle')
  for layer in m.uv_layers:
   for uv in layer.data:assert all(math.isfinite(c) for c in uv.uv),(name,'nonfinite UV')
 print('VALID',name,'meshes',len(obs),'vertices',sum(len(o.data.vertices) for o in obs),'morph',name!='Curtain_Rod.fbx')
