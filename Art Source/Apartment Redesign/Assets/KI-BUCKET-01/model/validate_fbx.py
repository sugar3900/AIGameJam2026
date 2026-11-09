"""Round-trip validate each independent FBX using Blender background."""
import bpy,math,os
root=os.path.dirname(os.path.abspath(__file__))
for name in ('KI_Bucket_Body','KI_Bucket_Handle','KI_Bucket_Water'):
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.fbx(filepath=os.path.join(root,name+'.fbx'))
 meshes=[o for o in bpy.context.selected_objects if o.type=='MESH']
 if len(meshes)!=1:raise RuntimeError(name+' expected exactly one mesh')
 o=meshes[0];m=o.data;m.calc_loop_triangles()
 badv=sum(not all(math.isfinite(v) for v in p.co) for p in m.vertices)
 badn=sum(not all(math.isfinite(v) for v in p.normal) for p in m.polygons)
 baduv=sum(not all(math.isfinite(v) for v in uv.uv) for layer in m.uv_layers for uv in layer.data)
 deg=sum(t.area<1e-10 for t in m.loop_triangles)
 if badv or badn or baduv or deg or not m.uv_layers:raise RuntimeError(f'{name}: invalid v={badv} n={badn} uv={baduv} deg={deg} layers={len(m.uv_layers)}')
 print(f'VALID {name} verts={len(m.vertices)} triangles={len(m.loop_triangles)} bounds={tuple(round(x,4) for x in o.dimensions)} uv={len(m.uv_layers)}')
