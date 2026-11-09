import bpy, math
from pathlib import Path
from mathutils import Vector
p=Path(__file__).resolve().parent/'KI_Range_Flame.fbx'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(p))
obs=[o for o in bpy.context.selected_objects if o.type=='MESH']
assert len(obs)==1, f'Expected 1 independent flame mesh, got {len(obs)}'
materials=set();bounds=[];triangles=0
for o in obs:
 assert o.data.uv_layers, f'{o.name} missing UV'
 assert all(math.isfinite(c) for v in o.data.vertices for c in v.co)
 assert all(math.isfinite(c) for loop in o.data.uv_layers.active.data for c in loop.uv)
 assert (o.location-Vector((0,0,0))).length < 1e-5, (o.name,o.location[:])
 materials.update(m.name for m in o.data.materials if m)
 o.data.calc_loop_triangles()
 for t in o.data.loop_triangles:
  v=[o.data.vertices[i].co for i in t.vertices]
  assert (v[1]-v[0]).cross(v[2]-v[0]).length>1e-12, f'{o.name} degenerate triangle'
  triangles+=1
 bounds.extend(o.matrix_world@v.co for v in o.data.vertices)
lo=[min(v[i] for v in bounds) for i in range(3)];hi=[max(v[i] for v in bounds) for i in range(3)]
assert all(abs(v)<.055 for v in [lo[0],hi[0],lo[1],hi[1]]),(lo,hi)
assert abs(lo[2])<1e-6 and .029<hi[2]<.031,(lo,hi)
assert any('Outer' in m for m in materials), materials
for o in obs:
 attrs=list(o.data.color_attributes)
 assert attrs, f'{o.name} missing vertex colors'
 values=[c.color[3] for a in attrs for c in a.data]
 assert min(values)<.05 and max(values)>.80, (min(values),max(values))
 print('vertex color',[(a.name,a.domain) for a in attrs],'alpha range',min(values),max(values))
print('PASS meshes',len(obs),'triangles',triangles,'materials',sorted(materials),'metre bounds',lo,hi,'origins burner center')
