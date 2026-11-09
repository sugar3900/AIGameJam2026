import bpy,math,os
root=os.path.dirname(os.path.abspath(__file__))
for name in ('KI_Kettle_Body','KI_Kettle_Lid'):
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.fbx(filepath=os.path.join(root,name+'.fbx'))
 objects=[o for o in bpy.context.selected_objects if o.type=='MESH']
 if not objects: raise RuntimeError(name+' has no meshes')
 for o in objects:
  m=o.data;m.calc_loop_triangles();badv=sum(not all(math.isfinite(v) for v in p.co) for p in m.vertices);badn=sum(not all(math.isfinite(v) for v in p.normal) for p in m.polygons);baduv=sum(not all(math.isfinite(v) for v in uv.uv) for layer in m.uv_layers for uv in layer.data);deg=sum(t.area<1e-12 for t in m.loop_triangles)
  if badv or badn or baduv or deg or not m.uv_layers: raise RuntimeError(f'{name}/{o.name}: badv={badv}, badn={badn}, baduv={baduv}, deg={deg}, layers={len(m.uv_layers)}')
 print(f'VALID {name} meshes={len(objects)} vertices={sum(len(o.data.vertices) for o in objects)}')
