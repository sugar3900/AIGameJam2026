"""Front-fit revision. Existing pivot locations and 100-degree travel preserved."""
from pathlib import Path
import bpy,json,math
from mathutils import Vector
R=Path(__file__).resolve().parent;A=R.parent
ns={'__file__':str(A/'CABINET-JOINERY-02/build_joinery.py')}
exec((A/'CABINET-JOINERY-02/build_joinery.py').read_text().split("for kit in ('Base0425'")[0],ns)
ns['R']=R;ns['REPORT']=[];ns['RENDER']=False
original_preview=ns['preview']
def small_preview(*args):
 original_preview(*args)
ns['preview']=small_preview
for d in ('models','textures','previews'):(R/d).mkdir(exist_ok=True)
bpy.context.preferences.filepaths.save_version=0
old=json.loads((A/'CABINET-JOINERY-02/assembly.json').read_text())['parts']
patch=json.loads((A/'CABINET-JOINERY-03/assembly.json').read_text())['parts'][0]
records=[]
for code in ('0425','0775','0450'):
 bpy.ops.wm.read_factory_settings(use_empty=True)
 bpy.context.scene.render.threads_mode='FIXED';bpy.context.scene.render.threads=1
 paint=ns['material']('Joinery_Sage',(.30,.36,.20),.78,image=bpy.data.images.load(str(A/'CABINET-JOINERY-02/textures/T_Joinery_Sage.png')))
 brass=ns['material']('Joinery_AgedBrass',(.32,.22,.085),.42,.65)
 kit='Base'+code; moving=[]
 bodyrec=next(x for x in old if x['kit']==kit and '_Body' in x['file'])
 ob,hs=ns['load'](A/'CABINET-JOINERY-02/models'/bodyrec['file'])
 for h in hs:bpy.data.objects.remove(h,do_unlink=True)
 if code=='0775':
  ob,hs=ns['load'](A/'CABINET-JOINERY-03/models/KI_Cab04_0775_Filler.fbx')
  for h in hs:bpy.data.objects.remove(h,do_unlink=True)
 for key in (('door_L','door_R') if code=='0775' else ('door',)):
  rec=next(x for x in old if x['kit']==kit and x['file'].endswith('_'+key+'.fbx'))
  if code=='0775' and key=='door_L':rec=patch
  pv=rec['pivot_source_m']; side=1 if key=='door_R' else -1
  # Nominal painted frame bounds, excluding the hinge barrel.
  w=(.393 if code=='0425' else .378 if code=='0450' else .3165 if key=='door_L' else .3485)
  cx=(0 if code=='0425' else .020 if code=='0450' else (-.3425-.026)/2 if key=='door_L' else .17725-.020)
  # right 0775 frame spans -.020+.003 to -.020+.3515
  if code=='0775' and key=='door_R':cx=.15725
  lo=.1355;hi=.672;parts=[]
  ns['framed'](cx,-.264,(lo+hi)/2,w,hi-lo,.040,paint,parts)
  ns['pull'](cx-side*(w/2-.020),-.275,.440,True,brass,parts)
  ns['hinge'](pv,(.24,.53),side,brass,parts)
  name='KI_Cab05_'+code+'_'+key
  o=ns['export'](name,parts,pv,[ns['hull']((cx,-.264,(lo+hi)/2),(w,.022,hi-lo))],kit);moving.append((o,100 if side==1 else -100))
  ns['REPORT'][-1].update(replaces=rec['file'],frame_min_x=cx-w/2,frame_max_x=cx+w/2,door_top_m=hi)
  dk=key.replace('door','drawer');dr=next(x for x in old if x['kit']==kit and x['file'].endswith('_'+dk+'.fbx'))
  o,hs=ns['load'](A/'CABINET-JOINERY-02/models'/dr['file'])
  # Only stretch the painted front; drawer box and all slide roots remain untouched.
  ids=set()
  for p in o.data.polygons:
   if 'Sage' in o.data.materials[p.material_index].name:ids.update(p.vertices)
  xmin=min(o.data.vertices[i].co.x for i in ids);xmax=max(o.data.vertices[i].co.x for i in ids)
  for i in ids:
   v=o.data.vertices[i];v.co.x=cx-w/2+(v.co.x-xmin)/(xmax-xmin)*w
  # Replace existing handle so it remains centered on its new front.
  ns['strip_material'](o,lambda n:'brass' in n.lower())
  for h in hs:
   if h.dimensions.z>.15 and h.dimensions.y<.05:
    mn=min(v.co.x for v in h.data.vertices);mx=max(v.co.x for v in h.data.vertices)
    for v in h.data.vertices:v.co.x=cx-w/2+(v.co.x-mn)/(mx-mn)*w
  parts=[o];ns['pull'](cx,-.275,.765,False,brass,parts)
  o=ns['export']('KI_Cab05_'+code+'_'+dk,parts,(0,0,0),hs,kit);moving.append((o,None))
  ns['REPORT'][-1].update(replaces=dr['file'],front_width_m=w,front_center_x=cx)
 ns['preview'](kit,moving,1.20 if code=='0775' else 1.05,.45)
(R/'assembly.json').write_text(json.dumps({'units':'metres; source -Y front, Unreal flips Y','parts':ns['REPORT'],'unchanged':'JOINERY02 bodies, JOINERY03 stationary filler, all functional pivots and drawer boxes','door_top_m':.672,'drawer_bottom_m':.675},indent=2)+'\n')
print('FRONT_FIT_COMPLETE')
