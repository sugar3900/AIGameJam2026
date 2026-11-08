import bpy,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
bounds=[]
for name in ('BODY','DRAWER','DOOR_L','DOOR_R'):
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.fbx(filepath=str(P/f'HA_CABINET_{name}.fbx'))
 obs=[o for o in bpy.context.selected_objects if o.type=='MESH']; assert len(obs)==1
 o=obs[0]; p=o.matrix_world.translation
 print(name,'origin',tuple(round(v,5) for v in p))
 if name.startswith('DOOR'):
  expected=-.465 if name.endswith('L') else .465
  assert abs(p.x-expected)<.001 and abs(p.y+.11)<.001
 for v in o.data.vertices: bounds.append(o.matrix_world@v.co)
mins=[min(p[i] for p in bounds) for i in range(3)];maxs=[max(p[i] for p in bounds) for i in range(3)]
dims=[maxs[i]-mins[i] for i in range(3)]
print('ASSEMBLY BOUNDS',mins,maxs,'DIMENSIONS',dims)
assert dims[0]<=1.021 and dims[1]<=.250 and dims[2]<=.722
print('PASS')
