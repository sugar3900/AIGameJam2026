from pathlib import Path
import bpy,json
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parent
R=next(p for p in P.parents if (p/'ICanFixHim.uproject').exists())
A=R/'Art Source/Apartment Redesign/Assets'
out={}
for aid in ['BA-TOILET-01','BA-BASIN-01','BA-MIRROR-01','BA-LINEN-01','BA-TUB-01','BA-ROLL-01','BA-TOWEL-RAIL-01','BA-BASKET-01','BA-BIN-01']:
 out[aid]={}
 for f in sorted((A/aid/'model').glob('*.fbx')):
  bpy.ops.wm.read_factory_settings(use_empty=True)
  bpy.ops.import_scene.fbx(filepath=str(f))
  objects=[o for o in bpy.context.scene.objects if o.type=='MESH' and not o.name.startswith('UCX_')]
  pts=[o.matrix_world@v.co for o in objects for v in o.data.vertices]
  out[aid][f.name]={'min':[min(v[i] for v in pts) for i in range(3)],'max':[max(v[i] for v in pts) for i in range(3)],'objects':[{'name':o.name,'origin':list(o.location),'vertices':len(o.data.vertices)} for o in objects]}
  if aid=='BA-LINEN-01' and 'Door' in f.name:
   ob=objects[0];sweeps={}
   for deg in [80,85,90,95,100]:
    m=Matrix.Rotation(-deg*3.141592653589793/180,4,'Z')
    pp=[ob.location+m@v.co for v in ob.data.vertices]
    sweeps[str(deg)]={'plan_x_min':min(7.45-v.x for v in pp),'plan_x_max':max(7.45-v.x for v in pp),'plan_y_min':min(9.05+v.y for v in pp)}
   out[aid][f.name]['north_facing_sweep_at_7_45_9_05']=sweeps
(P/'source-bounds.json').write_text(json.dumps(out,indent=2)+'\n')
print('Saved source-bounds.json')
