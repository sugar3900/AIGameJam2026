from pathlib import Path
import bpy,json,math
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(ROOT.parent/'KI-CHAIR-01/model/KI_CHAIR_01.fbx'))
allv=[];components=[]
for ob in [o for o in bpy.data.objects if o.type=='MESH']:
 mesh=ob.data;vs=[ob.matrix_world@v.co for v in mesh.vertices];allv+=vs;parent=list(range(len(vs)))
 def root(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 for e in mesh.edges:
  a,b=(root(i) for i in e.vertices);parent[b]=a
 groups={}
 for i,v in enumerate(vs):groups.setdefault(root(i),[]).append(v)
 for verts in groups.values():
  mn=[min(v[k] for v in verts) for k in range(3)];mx=[max(v[k] for v in verts) for k in range(3)];size=[b-a for a,b in zip(mn,mx)]
  if size[0]>.30 and mn[2]>.55 and size[2]<.14:
   centre=[v for v in verts if abs(v.x)<.03];edges=[v for v in verts if abs(v.x)>.9*max(abs(mn[0]),abs(mx[0]))]
   ym=sum(v.y for v in centre)/len(centre);ye=sum(v.y for v in edges)/len(edges)
   low=[v for v in centre if v.z<mn[2]+.012];high=[v for v in centre if v.z>mx[2]-.012]
   loY=sum(v.y for v in low)/len(low);hiY=sum(v.y for v in high)/len(high)
   components.append({'bounds':{'min':mn,'max':mx},'centre_z':(mn[2]+mx[2])/2,'centre_y_mean':ym,'edge_y_mean':ye,'centre_minus_edge_y':ym-ye,'upper_minus_lower_y':hiY-loY,'measured_recline_degrees':math.degrees(math.atan2(hiY-loY,size[2]-.012)),'vertices':len(verts)})
result={'source':'KI-CHAIR-01/model/KI_CHAIR_01.fbx','source_front':'-Y','bounds':{'min':[min(v[k] for v in allv) for k in range(3)],'max':[max(v[k] for v in allv) for k in range(3)]},'slats':sorted(components,key=lambda x:x['centre_z']),'interpretation':'Negative centre-minus-edge Y means slats bulge toward the sitter (convex front); desired concave front requires positive Y at centre. Individual slats are vertical despite their stepped centre positions.'}
(ROOT/'original-diagnosis.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
