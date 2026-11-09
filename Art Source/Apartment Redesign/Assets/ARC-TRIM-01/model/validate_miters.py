import bpy
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parent
for family in ['Baseboard','Crown']:
 edges=[]
 for side in ['End','Start']:
  bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
  bpy.ops.import_scene.fbx(filepath=str(root/(family+'_Inside_'+side+'.fbx')))
  obj=next(o for o in bpy.context.scene.objects if o.type=='MESH')
  coords=[obj.matrix_world @ v.co for v in obj.data.vertices]
  if side=='End':
   edge=[v for v in coords if abs(v.x-v.y-1)<1e-5]
  else:
   edge=[Vector((1+v.y,-v.x,v.z)) for v in coords if abs(v.x+v.y)<1e-5]
  assert len(edge)>=8,(family,side,len(edge),[(tuple(v)) for v in coords[:4]])
  edges.append(edge)
 assert len(edges[0])==len(edges[1]),family
 for v in edges[0]:
  assert min((v-w).length for w in edges[1])<1e-5,(family,tuple(v))
 print('VALID MITER',family,len(edges[0]),'matching profile vertices after 90-degree rotation')
