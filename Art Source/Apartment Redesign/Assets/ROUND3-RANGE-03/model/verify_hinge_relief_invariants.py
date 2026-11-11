"""Compare a retained pair of pre-pocket FBXs against the settled replacement.
Pass -- --before-body <FBX> --before-door <FBX> to Blender.
"""
import bpy,json,hashlib,sys,argparse
from pathlib import Path
from collections import Counter
A=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--before-body',type=Path,required=True);ap.add_argument('--before-door',type=Path,required=True)
args=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
def norm(s):
 return s.rsplit('.',1)[0] if '.' in s and s.rsplit('.',1)[1].isdigit() else s
def load(p):
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(p));o=[o for o in bpy.data.objects if o.type=='MESH'][0];me=o.data;uv=me.uv_layers.active
 points=Counter(tuple(round(float(c),7) for c in o.matrix_world@v.co) for v in me.vertices)
 corners=Counter();front=Counter();nonframe=Counter()
 for poly in me.polygons:
  name=norm(me.materials[poly.material_index].name)
  isfront=name=='Enamel_Painted' and all((o.matrix_world@me.vertices[vi].co).y<-.38 for vi in poly.vertices)
  for li in poly.loop_indices:
   v=o.matrix_world@me.vertices[me.loops[li].vertex_index].co
   key=(tuple(round(float(c),7) for c in v),tuple(round(float(c),7) for c in uv.data[li].uv),name)
   corners[key]+=1
   if isfront:front[key]+=1
   if name!='Enamel_Painted':nonframe[key]+=1
 return points,corners,front,nonframe
def uvdelta(a,b):
 from collections import defaultdict
 aa=defaultdict(list);bb=defaultdict(list)
 for (p,uv,m),n in a.items():aa[p,m].extend([uv]*n)
 for (p,uv,m),n in b.items():bb[p,m].extend([uv]*n)
 assert aa.keys()==bb.keys()
 delta=0.
 for key in aa:
  av,bv=sorted(aa[key]),sorted(bb[key]);assert len(av)==len(bv)
  delta=max(delta,max(abs(x-y) for uv0,uv1 in zip(av,bv) for x,y in zip(uv0,uv1)))
 assert delta<=2e-7,delta
 return delta
R={}
for part in ['Body','Door']:
 oldfile=args.before_body if part=='Body' else args.before_door;newfile=A/'model'/f'KI_RANGE03_{part}.fbx'
 old,new=load(oldfile),load(newfile)
 if part=='Body':
  assert old[0]==new[0]
  delta=uvdelta(old[1],new[1])
 else:
  assert old[2]==new[2], ('front UV/geometry changed',sum((old[2]-new[2]).values()),sum((new[2]-old[2]).values()))
  delta=uvdelta(old[3],new[3])
 R[part]={'before_sha256':hashlib.sha256(oldfile.read_bytes()).hexdigest(),'after_sha256':hashlib.sha256(newfile.read_bytes()).hexdigest(),
 'all_body_positions_materials_unchanged':part=='Body','max_other_uv_component_delta':delta,'other_uv_tolerance':2e-7,'front_enamel_uv_geometry_corners_unchanged':sum(old[2].values()) if part=='Door' else None,
 'non_enamel_door_positions_materials_unchanged_corners':sum(old[3].values()) if part=='Door' else None,'status':'PASS'}
for part,data in R.items():
 if part=='Body':
  data.pop('front_enamel_uv_geometry_corners_unchanged');data.pop('non_enamel_door_positions_materials_unchanged_corners')
 else:data.pop('all_body_positions_materials_unchanged')
(A/'hinge-relief-fbx-invariants.json').write_text(json.dumps(R,indent=2)+'\n');print('RANGE_RELIEF_INVARIANTS_PASS',R)
