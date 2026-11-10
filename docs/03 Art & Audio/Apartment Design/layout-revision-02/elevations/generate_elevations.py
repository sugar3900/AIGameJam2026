"""Revision-02 dimensioned design elevations; no engine or source-art writes."""
from pathlib import Path
import json, math, html, textwrap, sys
P=Path(__file__).resolve().parent
STUDY='--kitchen-dining-study' in sys.argv
BASE=P.parent
PLAN=json.loads(((BASE/'kitchen-dining-study/approved-plan.json') if STUDY else BASE/'approved-plan.json').read_text())
if STUDY:
 P=BASE/'kitchen-dining-study/elevations';P.mkdir(parents=True,exist_ok=True)
ROOMS={'LV':('Living + entry',[5.5,0,6.5,5.6],'#e7ceb0'),'KI':('Kitchen / dining',[0,0,5.5,3.8],'#ded5b3'),'HA':('Hall',[2.2,3.8,9.8,1.8],'#e7d0b3'),'BR':('Bedroom',[0,5.6,4.8,3.95],'#dfc7b5'),'BA':('Bathroom',[4.8,5.6,3.1,3.95],'#e8d5bf'),'OF':('Office / guest',[7.9,5.6,4.1,3.95],'#d7d9c8'),'BC':('Mold closet',[0,3.8,2.2,1.8],'#c6bba6')}
if STUDY:
 ROOMS['LV']=('Living / dining + entry',[4.8,0,7.2,5.6],'#e7ceb0');ROOMS['KI']=('Compact kitchen',[0,0,4.8,3.8],'#ded5b3')
ROOMS['CT']=('Entry coat closet',[10.75,5.6,1.25,.8],'#d9ccb6')
ROOMS['WG']=('Guest wardrobe',[10.75,6.4,1.25,.75],'#e0d8c8')
ITEMS=[];OPEN=[]
def add(id,kind,name,rooms,rect,h,z=0,front=None,show='NESW',children=None,state='static',note='',tone=None):
 o=dict(instance=f'{id}:{len(ITEMS)+1:03}',asset=id,kind=kind,name=name,rooms=rooms.split(','),rect=rect,z=z,h=h,front=front,show=show,children=children or [],state=state,note=note,tone=tone);ITEMS.append(o);return o
# Furniture footprints are read from the selected plan, not retyped.
MAP={
'Sofa':('LV-SOFA-01','sofa',.98,['cushions','floral throw']),'Armchair':('LV-CHAIR-01','chair',.935,[]),'Coffee table':('LV-COFFEE-01','table',.453,['books','KI-MUG-01']),'TV / console':('LV-TV-01','tv',1.257,[]),'Bookcase':('LV-BOOK-01','bookcase',2.056,['shelf books','plant','tin']),'Side table':('LV-SIDE-TABLE-01','table',.54,['LV-TABLE-LAMP-01']),'Radiator':('LV-RADIATOR-01','radiator',.570,[]),'Plant':('LV-PLANT-01','plant',.7,['LV-PLANT-STAND-01']),
'Range':('KI-RANGE-01','range',1.07,['KI-KETTLE-01','KI-PAN-01','KI-RANGE-FLAME-01']),'Prep':('KI-CABINET-01','cabinet',.91,['KI-JAR-01']),'Counter':('KI-CABINET-01','cabinet',.91,['KI-BOWL-01']),'Prep / uppers':('KI-CABINET-01','cabinet',.91,['KI-MUG-01','KI-POTTERY-01']),'Sink / leak':('KI-SINK-NARROW-01','sink',1.343,['faucet','KI-BUCKET-01']),'Fridge':('KI-FRIDGE-01','fridge',1.68,[]),'Pantry':('KI-PANTRY-01','pantry',1.976,[]),'Dining table':('KI-TABLE-01','table',.74,['KI-BOWL-01']),'Chair':('KI-CHAIR-01','chair',.85,[]),
'Bed':('BR-BED-01','bed',1.179,['pillows','floral quilt']),'Nightstand':('BR-NIGHTSTAND-01','cabinet',.52,['BR-LAMP-01']),'Dresser / mirror':('BR-DRESSER-01','dresser',.925,['BR-PERFUME-01','tray']),'Bookcase from office':('OF-BOOKCASE-01','bookcase',.90,['books','plant','storage box']),
'Tub / crack':('BA-TUB-01','tub',.57,['BA-TUB-WATER-01','taps','shower riser','curtain']),'Basin':('BA-BASIN-01','basin',.85,['taps']),'WC':('BA-TOILET-01','toilet',.924,[]),'Linen':('BA-LINEN-01','pantry',1.742,[]),'Towel basket':('BA-BASKET-01','basket',.38,['rolled towels']),'Pedal bin':('BA-BIN-01','bin',.40,[]),
'Daybed':('OF-DAYBED-01','daybed',.83,['pillows','quilt']),'Desk':('OF-DESK-01','desk',.757,['OF-DESK-LAMP-01','OF-PAPERS-01','book']),'Office storage cabinet':('OF-CABINET-01','cabinet',.72,['box']),'Office floor lamp':('LV-LAMP-01','lamp',1.56,[]),
'Wall table':('KI-WALL-TABLE-02','table',.74,[]),'Tucked stool':('KI-STOOL-02','bench',.45,[]),'Dining chair':('KI-CHAIR-01','chair',.85,[]),
'Entry bench':('HA-BENCH-01','bench',.45,['HA-SHOES-01']),'Hall end cabinet':('HA-CABINET-01','cabinet',.7195,['HA-VASE-02']),'Hall side console':('HA-CONSOLE-01','table',.785,['HA-VASE-01','HA-FLOWERS-01'])}
for o in PLAN['objects']:
 if o['name'] not in MAP:continue
 n=o['name'];asset,kind,h,children=MAP[n];room=o['room'];front=o.get('facing');r=o['rect'];rooms=room
 if STUDY and asset=='KI-CABINET-01':asset='KI-CABINET-02'
 if room=='HA' and n!='Hall end cabinet':rooms='HA,LV'
 if n=='Radiator' and room=='KI':asset='LV-RADIATOR-01'
 if n=='Chair' and room=='OF':asset='OF-CHAIR-01'
 if not front:
  front={'Bed':'south','Nightstand':'north','Dresser / mirror':'west','Bookcase from office':'east','Range':'south','Prep':'east','Counter':'east','Sink / leak':'east','Prep / uppers':'east','Fridge':'south','Pantry':'south','Entry bench':'west','Basin':'east','WC':'west','Linen':'west','Daybed':'east','Desk':'north','Office storage cabinet':'east'}.get(n)
 state='static'
 if kind in ('cabinet','dresser','desk'):state='drawer / door candidate'
 if kind in ('fridge','pantry'):state='hinged doors'
 if kind=='tv':state='screen on/off; doors'
 if kind=='range':state='oven hinge; burner glow'
 if kind=='sink':state='Lukey leak / repaired'
 if kind=='tub':state='Tyler repair; water reveal'
 if kind=='toilet':state='lid hinge'
 note=''
 if n=='Pantry':note='Full-size 1.00 m source pantry reused beside fridge after user swap.'
 if n in ('Prep','Counter','Prep / uppers'):note='Fitted cabinet frontages; keep profiles and hardware at source scale.'
 if STUDY and n in ('Counter','Prep / uppers'):note='Full-width worktop over narrower carcass with recessed40mm range-side filler; use KI-CABINET-02 final manifest pivots. Full neighbour sweep checked.'
 add(asset,kind,n,rooms,r,h,z=.516 if n=='Plant' and room=='LV' else 0,front=front,children=children,state=state,note=note)
# Wall-attached dressing: all positions in the same plan coordinate system.
def wall(id,kind,name,room,side,u,z,w,h,children=None,state='static',note='',tone=None):
 _,(x,y,rw,rh),_=ROOMS[room];d={'shelf':.15,'closetshelf':.30,'upper':.365,'fuse':.12,'pans':.15,'sconce':.18,'towel':.08,'mirror':.07,'mold':.005,'lead':.005,'stain':.005,'crack':.005,'boxes':.253}.get(kind,.035)
 if side=='N':r=[x+u,y+.06,w,d]
 elif side=='S':r=[x+u,y+rh-.06-d,w,d]
 elif side=='E':r=[x+rw-.06-d,y+u,d,w]
 else:r=[x+.06,y+u,d,w]
 return add(id,kind,name,room,r,h,z,front={'N':'south','S':'north','E':'west','W':'east'}[side],show=side,children=children,state=state,note=note,tone=tone)
# Living: uncluttered window; art supplies views at the other walls.
wall('LV-ART-04','art','Landscape over TV','LV','E',1.65,1.52,.72,.52)
wall('HA-ART-02','art','Small portrait','LV','E',.35,1.40,.42,.55)
wall('HA-HOOKS-01','hooks','Coat hooks over bench','LV','E',2.72,1.52,.60,.12,children=['HA-COAT-01'])
wall('LV-FUSE-01','fuse','Entry fusebox / Wyatt','LV','E',3.40,1.12,.45,.65,children=['LV-FUSE-DAMAGE-01'],state='hinged cover; repair damage hidden',note='Wall position from selected plan; use 0.45 m source panel; keep damage off entry casing.')
wall('HA-SCONCE-01','sconce','Entry sconce','LV','E',5.22,1.82,.16,.30,state='light')
wall('LV-ART-04','art','Landscape beside bookcase','LV','W',1.62,1.44,.55,.50,note='Reused frame; distinct artwork variant.')
wall('ARC-WALL-SHELF-01','shelf','Display shelf + pottery','LV','N',.65,1.55,.65,.145,children=['KI-POTTERY-01','books'])
# Kitchen north/west functional runs, east/south collected domestic detail.
wall('KI-UPPER-01','upper','Upper cupboard','KI','W',2.525,1.60,1.0,.5455,state='paired doors')
wall('KI-PAN-RAIL-01','pans','Rail + two pans','KI','W',.88,1.62,.42,.50,children=['KI-PAN-01'],note='Short rail variant above prep; keep pan bottoms clear of worktop.')
wall('KI-WALL-STAIN-01','stain','Optional water stain','KI','W',1.55,1.15,.70,.47,state='separate optional overlay',note='No mold identity; restrained old water mark.')
wall('ARC-WALL-SHELF-01','shelf','Sink shelf / jars','KI','W',1.55,1.94,.65,.145,children=['KI-JAR-01','KI-MUG-01'])
wall('KI-ART-01','art','Still life','KI','S',2.15,1.35,.60,.48)
wall('ARC-WALL-SHELF-01','shelf','Mugs and pottery','KI','S',3.50,1.58,.65,.145,children=['KI-MUG-01','KI-POTTERY-01'])
wall('KI-ART-01','art','Small kitchen print','KI','E',.85,1.40,.55,.44,note='Artwork variation using existing frame.')
wall('ARC-WALL-SHELF-01','shelf','Kitchen east shelf','KI','E',1.50,1.65,.65,.145,children=['KI-JAR-01','KI-PLANT-01'])
wall('BA-SWITCH-01','switch','Kitchen switch','KI','E',3.65,1.08,.10,.12,state='light')
# Hall: retain the user's focal group, move side console as a complete group.
wall('HA-ART-09','art','Focal landscape','HA','W',.44,1.30,.90,.65)
wall('HA-ART-03','art','Landscape above side console','HA','S',5.80,1.35,.65,.52)
wall('HA-ART-02','art','Hall portrait','HA','S',2.40,1.44,.42,.55)
wall('HA-SCONCE-01','sconce','Hall warm sconce','HA','N',1.95,1.85,.16,.30,state='light')
wall('HA-ART-02','art','Small gallery print','HA','N',.48,1.43,.42,.55)
wall('HA-ART-03','art','Gallery landscape','HA','N',1.14,1.48,.65,.52)
# Shared hall south pieces also appear in the combined living south elevation.
for o in list(ITEMS):
 if o['rooms']==['HA'] and o['show']=='S' and o['rect'][0]>=5.5:o['rooms'].append('LV')
# Bedroom: plaster replaces wainscot; loose furniture and pictures carry the warmth.
wall('BR-ART-FLORAL-01','art','Floral print between doors','BR','N',1.98,1.40,.58,.55)
wall('ARC-WALL-SHELF-01','shelf','Bedroom display shelf','BR','E',3.10,1.62,.65,.145,children=['keepsake','small books'])
wall('BR-ART-FLORAL-01','art','Botanical above moved bookcase','BR','W',.90,1.35,.58,.55)
wall('ARC-WALL-SHELF-01','shelf','Books and vase','BR','W',2.38,1.65,.65,.145,children=['books','HA-VASE-01'])
wall('BR-ART-FLORAL-01','art','Print near dresser','BR','E',.50,1.45,.55,.50)
wall('BR-ART-FLORAL-01','art','Headboard picture','BR','S',1.78,1.55,.72,.52,note='Distinct artwork variant in reused frame.')
wall('BA-SWITCH-01','switch','Bedroom switch','BR','N',2.76,1.08,.10,.12,state='light')
# Office now owns white wainscoting and separate lead-paint condition.
wall('BR-WAINSCOT-01','lead','Lead-paint condition','OF','N',.75,.55,.55,.30,state='damaged / sealed; separate future gameplay',note='Keep separate from Malcolm; wainscot module reuse, clipped panel variant around openings.')
wall('OF-ART-LANDSCAPE-01','art','North-wall landscape','OF','N',.60,1.47,.65,.50)
wall('OF-ART-BOTANICAL-01','art','Botanical over daybed','OF','W',2.05,1.42,.60,.60)
wall('ARC-WALL-SHELF-01','shelf','Daybed shelf','OF','W',1.00,1.65,.65,.145,children=['books','KI-PLANT-01'])
wall('OF-ART-BOTANICAL-01','art','East botanical','OF','E',2.10,1.65,.55,.58)
wall('ARC-WALL-SHELF-01','shelf','East display shelf','OF','E',1.62,1.45,.65,.145,children=['small pot','books'],note='No floor furniture in wardrobe approach.')
wall('BA-SWITCH-01','switch','Office switch','OF','N',1.32,1.08,.10,.12,state='light')
# Bathroom keeps footprint, with layered but localized dressing.
wall('BA-MIRROR-01','mirror','Mirror and paired globes','BA','W',1.40,1.16,.58,.80,children=['opal globe lights'],state='light')
wall('ARC-WALL-SHELF-01','shelf','Basin toiletries shelf','BA','W',2.20,1.28,.65,.145,children=['BA-BOTTLE-01','BA-CUP-01','BA-SOAP-01'])
wall('BA-TOWEL-RAIL-01','towel','Hand towel rail','BA','W',.45,1.02,.55,.50,children=['BA-HAND-TOWEL-01'])
wall('BA-SWITCH-01','switch','Bath switch','BA','W',.15,1.18,.10,.12,state='light')
wall('ARC-WALL-SHELF-01','shelf','North toiletries shelf','BA','N',.45,1.55,.65,.145,children=['BA-JAR-01','BA-SOAP-01'])
wall('BA-ART-01','art','Small botanical','BA','N',.55,1.95,.46,.50)
wall('BA-HOOK-01','towel','Hook + hand towel','BA','N',2.65,1.10,.22,.55,children=['BA-HAND-TOWEL-01'])
wall('BA-ROLL-01','roll','Toilet roll','BA','E',1.28,.66,.18,.18)
wall('BA-TOWEL-RAIL-01','towel','Bath towel rail','BA','E',.38,1.12,.65,.60,children=['BA-HAND-TOWEL-01'])
wall('ARC-WALL-SHELF-01','shelf','Folded towel and tin','BA','E',1.55,1.65,.65,.145,children=['BA-FOLDED-TOWEL-01','BA-TIN-01'])
wall('BA-TILE-01','crack','Tyler cracked tile','BA','S',.82,.88,.45,.48,state='broken / restored',note='Patch below window; curtain parks at tub east end to keep it visible.')
if STUDY:
 # Explicitly relocate kitchen wall dressing after the bigger layout change.
 ITEMS[:]=[o for o in ITEMS if not(o['rooms']==['KI'] and o['show']!='NESW')]
 wall('KI-WALL-STAIN-01','stain','Water tide beside sink window','KI','N',3.12,1.20,.70,.47,state='hide on Lukey repair',note='Offset clear of right window casing; no collision, preserve existing repair linkage.')
 wall('KI-BACKSPLASH-01','tile','North counter backsplash left','KI','N',1.20,.91,.425,.24)
 wall('KI-BACKSPLASH-01','tile','North counter backsplash right','KI','N',2.675,.91,1.975,.24)
 wall('KI-UPPER-01','upper','East return cupboard','KI','E',.25,1.60,1.0,.5455,state='paired doors',note='Clear of burners; wall front faces west. Verify open leaves against window trim.')
 wall('KI-ART-01','art','Breakfast still life','KI','S',2.12,1.35,.65,.50)
 wall('ARC-WALL-SHELF-01','shelf','Breakfast mugs / pottery','KI','S',3.35,1.65,.65,.145,children=['KI-MUG-01','KI-POTTERY-01'])
 wall('HA-SCONCE-01','sconce','Breakfast sconce','KI','S',1.50,1.75,.16,.30,state='light')
 wall('KI-PAN-RAIL-01','pans','Pan rail','KI','E',1.40,1.65,.60,.48,children=['KI-PAN-01'])
 wall('BA-SWITCH-01','switch','Kitchen switch','KI','E',3.61,1.08,.10,.12,state='decorative',note='FIX-009/025: recentered after kitchen casing; y3.61..3.71 leaves3cm each side between casing3.58 and corner3.74. Decorative plate/toggle only; no bound interaction.')
 # Hall north opens earlier; gallery pieces are fitted on the shorter wall.
 for o in ITEMS:
  if o['name']=='Hall warm sconce':o['rect'][0]=4.45
  if o['name']=='Gallery landscape':o['rect'][0]=3.44
  if o['name']=='Pantry':o['note']='Full-size pantry on west wall, facing east.'
  if o['name']=='Fridge':o['note']='North wall beside prep, facing south. West gap0.29 m; nominal left-hinge105-degree sweep, validate hardware and shelves in3D.'
  if o['name']=='Wall table':o['note']='New 0.90 x0.45 m wall-table variant; stool tucks below.'
if STUDY:
 for o in ITEMS:
  if o['asset']=='BR-CLOSET-01':o['asset']='BR-CLOSET-02'
# Architectural openings: dimensions correspond to plan axis starts.
for w in PLAN['windows']:
 side='N' if w['y']==0 else 'S';rid=w['room'];OPEN.append(dict(room=rid,side=side,kind='window',u=w['x']-ROOMS[rid][1][0],width=w['width'],sill=w['sill_height'],head=w['head_height']))
for d in PLAN['swing_doors']:
 if d['room']=='ENTRY':OPEN.append(dict(room='LV',side='E',kind='door',u=d['y'],width=d['width'],head=2.14,name='Entry / outward'))
 else:
  rid=d['room'];OPEN.append(dict(room=rid,side='N',kind='door',u=d['x']-ROOMS[rid][1][0],width=d['width'],head=2.14,name=rid+' door'))
  OPEN.append(dict(room='HA',side='S',kind='door',u=d['x']-2.2,width=d['width'],head=2.14,name=rid+' door'))
  if d['x']>=5.5:OPEN.append(dict(room='LV',side='S',kind='door',u=d['x']-ROOMS['LV'][1][0],width=d['width'],head=2.14,name=rid+' door'))
OPEN += [dict(room='HA',side='E',kind='door',u=.2,width=1.05,head=2.14,name='Entry / outward'),dict(room='KI',side='E',kind='portal',u=2.35,width=1.2,head=2.30,name='To living'),dict(room='LV',side='W',kind='portal',u=2.35,width=1.2,head=2.30,name='To kitchen'),dict(room='LV',side='W',kind='open',u=3.8,width=1.8,head=2.45,name='Hall continuation'),dict(room='HA',side='N',kind='open',u=3.3,width=6.5,head=2.45,name='Open to living'),dict(room='BR',side='N',kind='paired',u=.55,width=1.1,head=2.14,name='Mold closet'),dict(room='BC',side='S',kind='paired',u=.55,width=1.1,head=2.14,name='Bedroom'),dict(room='LV',side='S',kind='sliding',u=10.90-5.5,width=.96,head=2.18,name='Coat closet'),dict(room='HA',side='S',kind='sliding',u=10.90-2.2,width=.96,head=2.18,name='Coat closet')]
if STUDY:
 for o in OPEN:
  if o['kind']=='portal' and o['room'] in ('KI','LV'):o.update(rough_u=2.35,rough_width=1.20,rough_head=2.30,u=2.40,width=1.10,head=2.25,finished_clear=True,note='FIX-025: finished opening after5cm jamb/head lining; casing both faces.')
  if o['room']=='HA' and o['side']=='N' and o['kind']=='open':o.update(u=2.6,width=7.2)
  if o['room']=='LV' and o['side']=='S' and o['kind']=='sliding':o['u']=10.90-4.8
 OPEN[0]['note']='Counter-height kitchen window requires shortened sash/apron; verify faucet and sill depth.'
# Office closet face is a projection, 1.55 m into the room; north wall behind it is hidden.
add('ARC-SLIDING-CLOSET-01','wardrobe','Guest wardrobe front','OF',[10.75,6.40,1.25,.75],2.75,front='south',show='N',state='bypass slide',note='Front at y=7.15; 0.90 m clear / 0.96 m rough; 0.60 m usable hanging depth target.')
add('ARC-CLOSET-RETURN','return','Closet side / shared coat volume','OF',[10.75,5.6,.12,1.55],2.75,front='west',show='E',note='Projected exposed west face of paired storage, not a new exterior wall.')
# Mold closet: tall clear centre, shallow storage on west only.
wall('BR-CLOSET-01','mold','Malcolm mold on back wall','BC','N',.65,.75,.9,1.10,state='hidden by closed doors; repaired = clean wall')
wall('BR-CLOSET-01','closetshelf','High side shelf / hangers','BC','W',.22,2.15,1.05,.10,children=['empty hangers'],note='0.30 m deep; keep central standing volume clear.')
wall('BR-CLOSET-BOX-01','boxes','Low west box','BC','W',.40,0,.30,.181,note='Source-size .30x.253 box centered at plan(.21,4.35); no low storage across doorway.')
add('BR-CLOSET-01','bulb','Single bare bulb','BC',[1.06,4.60,.16,.16],.69,2.06,show='NESW',state='light',note='Cord reaches ceiling; lowest bulb point 2.06 m above floor.')
add('CHAR-MALCOLM','human','Standing clearance reference','BC',[.80,4.25,.60,.60],1.80,show='NESW',note='Dashed proxy only; use actual character and encounter camera for final clearance.')
for rid,side in [('CT','S'),('WG','N')]:
 storage=wall('ARC-CLOSET-STORAGE-02','closetshelf','Shelf / hanging rail',rid,side,.15,1.95,.95,.035,children=['hangers'],note='Separate shelf/rail kit; floor origin at shared rear face, shelf .30 deep and complete hanger envelope .49 deep. Source shelf z1.95..1.985. Never substitute door-front kit.')
 storage['rect']=[10.90,5.85 if rid=='CT' else 6.46,.95,.49]
 storage['assembly_origin_plan']=[11.375,6.34 if rid=='CT' else 6.46,0]
 wall('BR-CLOSET-BOX-01','boxes','Storage box',rid,side,.20,.08,.30,.181,note='Single source-size box; do not stretch to fill closet width.')
OPEN += [dict(room='CT',side='N',kind='sliding',u=.15,width=.96,head=2.18,name='Entry-facing doors'),dict(room='WG',side='S',kind='sliding',u=.15,width=.96,head=2.18,name='Office-facing doors')]
if STUDY:
 for o in ITEMS:
  if o['asset']=='BR-CLOSET-01':o['asset']='BR-CLOSET-02'
  if o['asset']=='ARC-SLIDING-CLOSET-01':o['asset']='ARC-SLIDING-CLOSET-02'
for o in ITEMS:
 if o['name']=='Low west box':o['rect'][0]=.0835
# Source-feedback replacements happen after legacy records are allocated, preserving
# every existing instance key. Extra physical pieces append unique new keys.
RETIRED=[]
if STUDY:
 ASSETS=BASE.parents[3]/'Art Source/Apartment Redesign/Assets'
 def fitted_record(record,asset,mesh,manifest,side):
  export=next(e for e in manifest['exports'] if e['mesh']==mesh)
  bounds=export.get('source_bounds')
  if bounds is None:bounds=[export['bounds']['min'],export['bounds']['max']]
  lo,hi=bounds;origin=manifest.get('plan_origin_m',manifest.get('plan_origin'))
  record.update(asset=asset,rect=[round(origin[0]+lo[0],6),round(origin[1]-hi[1],6),round(hi[0]-lo[0],6),round(hi[1]-lo[1],6)],z=round(lo[2],6),h=round(hi[2]-lo[2],6),assembly_origin_plan=origin,source_mesh=mesh,source_export=f'Art Source/Apartment Redesign/Assets/{asset}/'+export['file'],source_up='+Z',source_front='-Y',source_to_plan='X kept; Y flipped; Z kept',assembly_rotation_plan_deg=[0,0,0],assembly_scale=[1,1,1],show=side,front={'N':'south','E':'west','W':'east'}[side[0]])
  return record
 mold=json.loads((ASSETS/'BR-MOLD-02/assembly.json').read_text())
 storage=json.loads((ASSETS/'BR-CLOSET-STORAGE-03/assembly.json').read_text())
 back=next(o for o in ITEMS if o['instance']=='BR-CLOSET-01:089')
 west=next(o for o in ITEMS if o['instance']=='BR-CLOSET-01:090')
 for old in (back,west):
  RETIRED.append(dict(instance=old['instance'],old_asset=old['asset'],old_name=old['name'],disposition='Source component retired; stable instance key reassigned to replacement. Do not place legacy mesh.'))
 fitted_record(back,'BR-MOLD-02','BR_Mold02_Back',mold,'N')
 back.update(name='Upper-right charcoal mold / back',state='Malcolm repair: hide both overlays',note='Stable :089 replaces old central green patch. Neutral charcoal; coverage includes texture alpha, luminance and vertex alpha. Preserve encounter child transforms.',repair_tags=['RepairDamage','AuthoredMoldDamage'],inspect_target_plan=mold['suggested_inspect_world_m'])
 fitted_record(west,'BR-CLOSET-STORAGE-03','BR_ClosetStorage03_West',storage,'WNS')
 west.update(name='West full-length shelf / rail / hangers',children=['hooked empty hangers'],note='Stable :090 replaces old high short shelf. Full 1.67 m side run, 0.40 m board depth; hanger envelope included in footprint.',shelf_top=storage['shelf_top'],shelf_thickness=storage['shelf_thickness'],rail_z=storage['rail_z'])
 ret=add('BR-MOLD-02','mold','Corner charcoal mold / east return','BC',[0,0,0,0],0,state=back['state'],note='Second plane wraps corner; fades out through vertex alpha. Remove together with :089.',tone='#252423')
 fitted_record(ret,'BR-MOLD-02','BR_Mold02_Return',mold,'E');ret['repair_tags']=back['repair_tags']
 east=add('BR-CLOSET-STORAGE-03','closetshelf','East full-length shelf / rail / hangers','BC',[0,0,0,0],0,children=['hooked empty hangers'],note='Both assemblies share floor origin; do not recenter individual bounds.')
 fitted_record(east,'BR-CLOSET-STORAGE-03','BR_ClosetStorage03_East',storage,'ENS')
 east.update(shelf_top=storage['shelf_top'],shelf_thickness=storage['shelf_thickness'],rail_z=storage['rail_z'])
 # FIX-003: retain the sink record and tap identities; split the old baked bucket out.
 leak=json.loads((ASSETS/'KI-LEAK-02/validation.json').read_text())
 leak_manifest={'plan_origin':[2.15,.4605,0],'exports':[dict(mesh=mesh,file='models/'+mesh+'.fbx',bounds=bounds) for mesh,bounds in leak['exports'].items()]}
 sink=next(o for o in ITEMS if o['instance']=='KI-SINK-NARROW-01:029')
 fitted_record(sink,'KI-LEAK-02','KI_LEAK_02_sink_body',leak_manifest,'NESW')
 sink.update(children=['faucet'],note='FIX-003: unchanged sink assembly transform; old embedded bucket removed. Preserve original taps, Sink_Tap identity, materials and Lukey state. No static beads.',retained_taps={side:dict(source_export='Art Source/Apartment Redesign/Assets/KI-SINK-NARROW-01/models/KI_SINK_NARROW_'+side+'.fbx',source_pivot=pivot) for side,pivot in leak['tap_pivots'].items()},runtime_effects=dict(kind='intermittent falling drops into pail',source_start=leak['leak_point'],source_catch=leak['bucket_catch_point'],plan_start=[2.05,.4605,.243],plan_catch=[2.05,.4605,.115],repair_behavior='stop and hide on Lukey repair; ordinary Sink_Tap water unchanged'))
 RETIRED.append(dict(instance=sink['instance'],old_asset='KI-SINK-NARROW-01',old_mesh='KI_SINK_NARROW_body embedded bucket + KI_SINK_NARROW_damage',disposition='Replace body, retain original tap controls; retire entire static damage mesh and authored-leak runtime BuildBrokenFx cylinder/drop fallback.'))
 for mesh,kind,name,state in [('KI_LEAK_02_bucket','bucket','Vintage galvanized leak pail','persistent after repair'),('KI_LEAK_02_bucket_water','water','Water inside leak pail','optional water; stop ripple/hide on Lukey repair'),('KI_LEAK_02_puddle','water','Residual floor spill','optional mesh OR decal; hide on Lukey repair')]:
  record=add('KI-LEAK-02',kind,name,'KI',[0,0,0,0],0,state=state)
  fitted_record(record,'KI-LEAK-02',mesh,leak_manifest,'NESW')
  record['collision']='legacy UCX, 13 hulls' if kind=='bucket' else 'none'
  record['note']='Same floor assembly origin as sink; position already baked into geometry. Do not add bounds center offset.'
  if mesh.endswith('puddle'):record.update(decal_alternative=leak['puddle_mask'],note='Use optional mesh OR padded alpha-mask decal, never both. Transparent water, no white albedo or static drops. Residual spill predates bucket.')
 # FIX-004: move existing sets; all gameplay/asset identities remain stable.
 fuse=next(o for o in ITEMS if o['instance']=='LV-FUSE-01:043')
 fuse.update(name='North-wall fusebox / Wyatt',rect=[10.825,.06,.45,.14],z=1.40,h=.58,front='south',show='N',assembly_origin_plan=[11.05,.06,1.40],assembly_rotation_plan_deg=[0,0,0],assembly_scale=[1,1,1],note='FIX-004: move complete shell/door/damaged wire/repaired wire/plaster damage set; preserve pivots and labels. Box over corner plant, source shell lower-edge origin. Re-derive Wyatt talk/camera in engine; pending click/door/capsule validation.')
 hooks=next(o for o in ITEMS if o['instance']=='HA-HOOKS-01:042')
 hooks.update(rect=[11.873,2.94,.067,.72],note='FIX-004: measured source rail0.72 m centered y3.30 between TV and entry; move existing coat with rack, retain relative/vertical anchor. Validate actual bounds and casing in engine.')
 for record in ITEMS:
  if record['kind']=='art':record['note']+=((' ' if record['note'] else '')+'FIX-006 pending: unique image and frame per physical instance; preserve this instance ID for forthcoming art assignment.')
  if record['instance']=='HA-ART-02:058':
   record.update(rect=[4.50,5.505,1.30,.035],z=1.12,h=.90)
   record['note']+=' FIX-006 target outer frame1.30x0.90 m, centerX5.15 between casing edges4.11 and6.19;0.39 m side margins. Back-plane wall datumY5.54; actual new frame depth from source handoff. Asset assignment pending.'
 assert len({o['instance'] for o in ITEMS})==len(ITEMS)
if STUDY:
 sys.path.insert(0,str(BASE/'feedback/FIX-007'))
 from bathroom_layout import apply_items
 ITEMS=apply_items(ITEMS)
 for record in ITEMS:
  if record['kind']=='switch':record['state']='decorative'
 RETIRED.append(dict(instance='BA-TOWEL-RAIL-01:078',disposition='FIX-007 intentional duplicate rail removal; record retained but inactive.'))
# Ceiling fixtures are listed once per physical room, not duplicated through wall projections.
CEILING=[dict(room=r,asset='ARC-CEILING-LIGHT-01',position=[sum((ROOMS[r][1][0],ROOMS[r][1][2]/2)),sum((ROOMS[r][1][1],ROOMS[r][1][3]/2)),2.75],note='Warm low-glare ceiling light; keep pendant bottom above 2.20 m.') for r in ('LV','KI','BR','BA','OF')]
CEILING.append(dict(room='HA',asset='ARC-CEILING-LIGHT-01',position=[4.55,4.7,2.75],note='Hall fixture; living fixture covers open eastern zone.'))
# ---------------- vector drawing ----------------
E=html.escape
WOOD='#946c4f';IVORY='#eee2cb';SAGE='#a4ad8c';INK='#5e5145'
class View:
 def __init__(self,rid,side,row):
  self.rid=rid;self.side=side;self.room=ROOMS[rid];self.x,self.y,self.rw,self.rh=self.room[1];self.width=self.rw if side in 'NS' else self.rh
  self.scale=min(126,940/self.width);self.ox=65;self.floor=440+row*560;self.top=self.floor-2.75*self.scale;self.rev=side in 'SW';self.a=[];self.legend=[];self.used=[]
  self.text_px(65,row*560+32,f'{rid}-{side}  |  {self.room[0]} · facing '+{'N':'north','E':'east','S':'south','W':'west'}[side],22,weight='bold')
  self.text_px(65,row*560+58,f'{self.width:.2f} m nominal wall span · 2.75 m ceiling · '+('east → west' if side=='S' else 'south → north' if side=='W' else 'west → east' if side=='N' else 'north → south'),12)
  self.R(0,0,self.width,2.75,self.room[2],sw=2)
  self.R(0,0,self.width,.13,'#d8c3a8',sw=.6);self.R(0,2.65,self.width,.10,IVORY,sw=.6)
  if rid=='OF':
   if STUDY and side=='S':
    self.panels(0,1.7105);self.panels(1.7105,1.579,.778);self.panels(3.2895,self.width-3.2895)
   else:self.panels(0,self.width)
  if rid=='BA' and not STUDY:self.tiles(0,self.width,1.15 if side!='S' else 1.5)
  if rid=='BA' and STUDY:
   self.bath_tiles(0,self.width,2.75 if side=='S' else 1.05,cap=side!='S')
   if side in 'EW':
    self.bath_tiles(2.95,self.width-2.95,2.75,cap=False)
    self.R(2.90,1.00,.05,1.75,'#a47871',sw=.5)

  if rid=='KI' and ((STUDY and side=='N') or (not STUDY and side=='W')):
   lo,hi=(1.0,4.65) if STUDY else (.85,3.65)
   for i in range(math.ceil((hi-lo)/.15)):
    for j in range(3):self.R(lo+i*.15,.91+j*.15,min(.15,hi-lo-i*.15),.15,['#d9c5a4','#bda98b'][(i+j)%2],sw=.5,stroke='#eee1c8')
  self.L(0,-.18,self.width,-.18,'#a77961',1)
  self.T(self.width/2,-.35,f'{self.width:.2f} m | elevations are from inside the room',11)
 def xp(self,u):return self.ox+(self.width-u if self.rev else u)*self.scale
 def yp(self,z):return self.floor-z*self.scale
 def text_px(self,x,y,t,size=11,anchor='start',weight='normal',fill=INK):self.a.append(f'<text x="{x:.2f}" y="{y:.2f}" font-family="Arial,sans-serif" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" fill="{fill}">{E(str(t))}</text>')
 def T(self,u,z,t,size=11):self.text_px(self.xp(u),self.yp(z),t,size,'middle')
 def R(self,u,z,w,h,fill,sw=1,stroke=INK,rx=0,extra=''):
  left=self.width-u-w if self.rev else u
  self.a.append(f'<rect x="{self.ox+left*self.scale:.2f}" y="{self.yp(z+h):.2f}" width="{w*self.scale:.2f}" height="{h*self.scale:.2f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" rx="{rx}" {extra}/>')
 def L(self,u,z,v,zz,color=INK,sw=1,extra=''):self.a.append(f'<line x1="{self.xp(u):.2f}" y1="{self.yp(z):.2f}" x2="{self.xp(v):.2f}" y2="{self.yp(zz):.2f}" stroke="{color}" stroke-width="{sw}" {extra}/>')
 def C(self,u,z,r,fill,stroke=INK):self.a.append(f'<circle cx="{self.xp(u):.2f}" cy="{self.yp(z):.2f}" r="{r*self.scale:.2f}" fill="{fill}" stroke="{stroke}" stroke-width="1"/>')
 def panels(self,u,w,h=1.1):
  self.R(u,0,w,h,'#f2eadc',sw=.6)
  n=max(1,round(w/.52));pw=w/n
  for i in range(n):self.R(u+i*pw+.055,.19,pw-.11,h-.35,'#e3d9c7',sw=.7);self.R(u+i*pw+.08,.215,pw-.16,h-.40,'#f2eadc',sw=.5)
  self.R(u,h-.06,w,.06,'#fff5e5',sw=.7)
 def tiles(self,u,w,h):
  self.R(u,0,w,h,'#cfa29d',sw=.6)
  for i in range(1,math.ceil(w/.20)):self.L(u+i*.2,0,u+i*.2,h,'#e8ccc1',.7)
  for z in (.2,.4,.6,.8,1.,1.2,1.4):
   if z<h:self.L(u,z,u+w,z,'#e8ccc1',.7)
  self.R(u,h-.05,w,.05,'#a47871',sw=.7)
 def bath_tiles(self,u,w,h,cap=True):
  field=h-.05 if cap else h
  self.R(u,0,w,field,'#cfa29d',sw=.5)
  for i in range(1,math.ceil(w/.10)):self.L(u+i*.1,0,u+i*.1,field,'#e8ccc1',.4)
  for i in range(1,math.ceil(field/.10)):self.L(u,i*.1,u+w,i*.1,'#e8ccc1',.4)
  if cap:self.R(u,field,w,.05,'#a47871',sw=.5)
 def mark(self,u,z,num):
  z=min(2.5,max(.18,z));self.C(u,z,.075,'#fbf5e8');self.text_px(self.xp(u),self.yp(z)+4,num,10,'middle',weight='bold')
 def opening(self,o):
  u,w,h=o['u'],o['width'],o['head'];k=o['kind'];z=o.get('sill',0)
  self.R(u,z,w,h-z,'#b0b2a1',sw=1)
  if k=='window':
   self.R(u-.08,z-(.07 if STUDY and self.rid=='KI' else .08),w+.16,h-z+.15,IVORY,sw=1)
   self.R(u,z,w,h-z,'#b2c6be',sw=1)
   # Soft distant skyline, not a photo decal.
   for i in range(max(1,int(w/.2))):self.R(u+i*.2,z+.05,min(.18,w-i*.2),.18+(i%3)*.06,'#aaa28b',sw=0)
   self.L(u+w/2,z,u+w/2,h,IVORY,5);self.L(u,(z+h)/2,u+w,(z+h)/2,IVORY,4)
   self.R(u-.10,z-.07,w+.20,.06,IVORY)
   if self.rid!='BA':
    self.L(u-.16,h+.12,u+w+.16,h+.12,WOOD,3)
    for xx in (u-.14,u+w-.03):
     self.R(xx,z-.01,.17,h-z+.08,'#ba8b80',sw=.6)
     for d in (.035,.085,.135):self.L(xx+d,z+.03,xx+d,h+.05,'#e8c5ab',.7)
   self.legend.append(f'Window {w:.2f} m; sill {z:.2f}, head {h:.2f}. '+('Frosted glass.' if self.rid=='BA' else 'Sash, casing, drapes and rod.'))
   return
  if k in ('open','portal'):
   self.R(u,0,w,h,'#e9e2d1',sw=1)
   self.R(u,h-.06,w,.06,IVORY,sw=.5)
   if k=='portal':self.R(u-.07,0,.07,h+.07,IVORY);self.R(u+w,0,.07,h+.07,IVORY)
   self.T(u+w/2,h/2,o['name'],12);self.legend.append(f"{o['name']}: {w:.2f} m span, {h:.2f} m head; no leaf.");return
  clear=w-(.10 if k=='paired' else .06)
  self.R(u-.08,0,w+.16,h+.08,IVORY,sw=1)
  self.R(u+.03,.015,w-.06,h-.045,'#d7c4a8',sw=1)
  leaves=2 if k in ('paired','sliding') else 1
  for i in range(leaves):
   a=u+.04+i*(w-.08)/leaves;ww=(w-.08)/leaves
   for zz,hh in ((.16,.72),(1.02,.78)):self.R(a+.05,zz,ww-.10,hh,'#e7d8bf',sw=.7)
   self.C(a+ww-.055,.98,.02,'#b08e55')
  if k=='sliding':self.L(u+w*.48,.04,u+w*.48,h-.03,'#9d8b72',2)
  self.legend.append(f"{o['name']}: {w:.2f} rough / {clear:.2f} clear target; head {h:.2f}. "+('Paired outward leaves.' if k=='paired' else 'Bypass sliders.' if k=='sliding' else 'Wider frame/leaf variant.'))
 def project(self,o):
  x,y,w,d=o['rect']
  if self.side in 'NS':return x-self.x,w,(y-self.y if self.side=='N' else self.y+self.rh-y-d)
  return y-self.y,d,(x-self.x if self.side=='W' else self.x+self.rw-x-w)
 def item(self,o,num,projections=False,repaired=False):
  u,w,dist=self.project(o);z=o['z'];h=o['h'];k=o['kind']
  if u<-.01 or u+w>self.width+.01:return
  facing={'N':'south','E':'west','S':'north','W':'east'}[self.side];front=o.get('front');face=(front==facing or front is None)
  # Background furniture appears in muted projection; full wall-attached elevations stay opaque.
  ghost=(dist>.85 and o['show']=='NESW')
  if ghost and not projections:return
  if repaired and (k in ('mold','lead','crack','stain') or (o['asset']=='KI-LEAK-02' and k=='water')):return
  self.a.append('<g'+(' opacity=".47"' if ghost else '')+'>')
  if k in ('cabinet','pantry','dresser','fridge','upper','bookcase','tv','wardrobe'):
   color=SAGE if o['asset'].startswith('KI') else WOOD
   if k=='fridge':color='#e8dcc0'
   if k=='wardrobe':color=IVORY
   self.R(u,z,w,h,color,rx=4 if k=='fridge' else 0)
   if any('LAMP' in a for a in o['children']):self.lamp(u+w*.5,z+h,.47)
   if any('VASE' in a for a in o['children']):self.vase(u+w*.42,z+h,min(.22,w*.4),.30)
   if k=='bookcase' and 'plant' in o['children']:self.vase(u+w*.65,z+h,.15,.20,True)
   if k=='bookcase' and face:
    for zz in [.12+i*(h-.2)/4 for i in range(5)]:
     self.R(u+.04,z+zz,w-.08,.045,'#6c503e',sw=.5)
     if zz<h-.24:
      for j in range(max(1,int((w-.12)/.095))):self.R(u+.065+j*.095,z+zz+.045,.07,min(.23,h-zz-.09),['#ac7f64','#bdae82','#7e927f','#9c7774'][j%4],sw=.4)
   elif k=='fridge' and face:
    self.R(u+.045,z+.07,w-.09,h-.14,'#eee2c9',rx=10)
    hx=u+.08 if self.rev else u+w-.12
    self.R(hx,z+h*.48,.035,.31,'#a4a08f',rx=3);self.C(u+w*.5,z+h*.84,.045,'#c2b38e')
   elif k=='tv' and face:
    self.R(u+.06,z+.68,w-.12,h-.75,'#5d6865',rx=12);self.R(u+.07,z+.15,(w-.18)/2,.40,'#ad8060');self.R(u+w/2+.02,z+.15,(w-.18)/2,.40,'#ad8060')
   elif k=='wardrobe':
    self.R(u+.155,0,.94,2.18,'#bdaf96');self.R(u+.18,.05,.46,2.105,'#e4d8c4');self.R(u+.62,.05,.46,2.105,'#f2e6d0');self.L(u+.62,.05,u+.62,2.15)
   elif face:
    if k=='dresser':
     for zz in (.12,.38,.64):self.R(u+.05,z+zz,w-.10,.22,'#b18463');self.C(u+w/2,z+zz+.11,.02,'#c8ab71')
    else:
     for xx in (u+.05,u+w/2+.015):self.R(xx,z+.1,w/2-.065,max(.2,h-.22),'none',sw=.7)
     self.C(u+w*.45,z+h*.55,.02,'#d8c38f');self.C(u+w*.55,z+h*.55,.02,'#d8c38f')
   if k=='dresser':
    self.R(u+.14,z+h+.03,max(.12,w-.28),.63,'#d1d4c5',stroke='#88694c',sw=3);self.vase(u+w*.72,z+h,.12,.20)
  elif k in ('table','desk','bench'):
   top=h-.055;self.R(u,z+top,w,.055,WOOD)
   self.R(u+.04,z,.055,top,WOOD);self.R(u+w-.095,z,.055,top,WOOD)
   if k=='desk':self.R(u+.06,z+h-.20,w-.12,.14,'#ad8060');self.C(u+w/2,z+h-.13,.018,'#c6a66e')
   if 'BOWL' in ' '.join(o['children']).upper():self.R(u+w*.35,z+h,w*.30,.12,'#c4a56f',rx=9);self.C(u+w*.45,z+h+.15,.05,'#bc8e56')
   if any('LAMP' in a for a in o['children']):self.lamp(u+w*.5,z+h,.44)
   if any('VASE' in a for a in o['children']):self.vase(u+w*.4,z+h,min(.22,w*.35),.30,True)
   if 'OF-PAPERS-01' in o['children']:self.R(u+w*.18,z+h,.25,.045,'#f7ebd1')
  elif k=='bed':
   self.R(u+.06,z+.40,w-.12,h-.44,IVORY,rx=18)
   self.R(u+.15,z+.78,w-.30,.28,'#ded3bd',rx=14)
   for xx in (u+.04,u+w-.09):self.R(xx,z,.05,h-.035,IVORY);self.C(xx+.025,z+h-.015,.035,IVORY)
   self.R(u+.08,z+.30,w-.16,.25,'#c8a38b',rx=5)
   self.R(u+.08,z+.53,w-.16,.13,'#d2b68f',rx=4)
   for i in range(2):self.R(u+.15+i*(w-.28)/2,z+.66,(w-.36)/2,.19,'#ebdfc6',rx=7)
   for i in range(7):self.C(u+.16+i*(w-.32)/6,z+.58,.022,'#ad8e71',stroke='none')
  elif k in ('sofa','chair','daybed'):
   col='#b9897c' if k!='bed' else '#c4a7a2'
   self.R(u+.04,z+.10,w-.08,min(.42,h-.16),'#a78168',rx=8)
   self.R(u,z+.48,w,max(.16,h-.48),col,rx=9)
   if k in ('bed','daybed'):self.R(u+.04,z+.36,w-.08,.18,'#d5bd9f',rx=7)
   if face or k in ('bed','daybed'):
    n=max(1,round(w/.55))
    for i in range(n):
     ww=(w-.12)/n;self.R(u+.06+i*ww,z+.52,ww-.025,min(.25,h-.55),'#d5b29b',rx=6)
     for j in range(3):self.C(u+.14+i*ww+j*.08,z+.63,.015,'#a47b6b',stroke='none')
   self.R(u+.05,z,.05,.12,WOOD);self.R(u+w-.10,z,.05,.12,WOOD)
  elif k=='range':
   self.R(u,z,w,.93,IVORY,rx=4);self.R(u+.06,z+.16,w-.12,.42,'#677069',rx=4);self.R(u,z+.91,w,.035,'#726c5b');self.R(u,z+.94,w,.13,IVORY)
   for i in range(4):self.C(u+.12+i*(w-.24)/3,z+.79,.024,'#b09569')
   if face:self.vase(u+w*.55,z+.95,.16,.18)
  elif k=='sink':
   if o['asset']=='KI-LEAK-02':
    self.R(u+.03,z,.045,.77,SAGE);self.R(u+w-.075,z,.045,.77,SAGE)
    self.R(u,z+.70,w,.07,SAGE);self.L(u+w*.40,.75,u+w*.40,.26,'#938d74',3)
   else:self.R(u,z,w,.77,SAGE)
   self.R(u,z+.77,w,.14,IVORY,rx=6);self.R(u+.04,z+.91,w-.08,.225,IVORY,sw=.7);self.L(u+w*.65,z+1.075,u+w*.65,z+1.343,'#8f948c',4);self.L(u+w*.65,z+1.343,u+w*.45,z+1.343,'#8f948c',4)
   if face and o['asset']!='KI-LEAK-02':self.R(u+.08,.03,.20,.25,'#a6b1a8',rx=5);self.L(u+w*.6,.65,u+w*.6,.26,'#938d74',3)
  elif k=='bucket':
   self.R(u,z,w,h,'#a5b1b4',rx=5);self.R(u-.008,z+h-.018,w+.016,.018,'#c0c8ca',sw=.5)
   for frac in (.25,.60):self.L(u+.015,z+h*frac,u+w-.015,z+h*frac,'#7b898d',1)
  elif k=='water':
   self.R(u,z,w,.006,'#8ca6a9',sw=.4,extra='opacity=".45"')
  elif k=='radiator':
   self.R(u,z+.06,w,h-.08,'#e0d3b8',rx=5)
   for i in range(max(2,int(w/.09))):self.L(u+.04+i*.09,z+.1,u+.04+i*.09,z+h-.04,'#aa9d84',2)
  elif k=='lamp':self.lamp(u+w/2,z,h)
  elif k=='plant':self.vase(u+w*.25,z,w*.5,.22,True)
  elif k=='tub':
   self.R(u,z+.15,w,h-.15,'#f0e5ce',rx=20);self.R(u-.025,z+h-.035,w+.05,.04,'#fff4df',rx=4);self.R(u+.12,z,.06,.17,WOOD);self.R(u+w-.18,z,.06,.17,WOOD)
  elif k=='basin':
   self.R(u+w*.40,z,.20,h-.12,IVORY,rx=10);self.R(u,z+h-.17,w,.17,'#f3e8d3',rx=13);self.L(u+w*.3,z+h,u+w*.3,z+h+.10,'#9b9b8a',3)
  elif k=='toilet':
   self.R(u+w*.60,z+.38,w*.37,h-.38,IVORY,rx=5);self.R(u+.03,z+.22,w*.8,.25,'#f2e8d5',rx=14);self.R(u+w*.25,z,w*.40,.26,IVORY,rx=8)
  elif k in ('basket','bin','boxes'):
   self.R(u,z,w,h,'#b69471' if k!='bin' else IVORY,rx=5)
   if k=='basket':
    for zz in (.05,.10,.15,.20,.25,.30):self.L(u,z+zz,u+w,z+zz,'#d1b28c',1)
  elif k=='art':
   self.R(u,z,w,h,WOOD,sw=2);self.R(u+.035,z+.035,w-.07,h-.07,'#ddc58f',sw=.6)
   self.R(u+.065,z+.065,w-.13,h-.13,'#c0b58a',sw=0)
   if 'BOTANICAL' in o['asset'] or 'FLORAL' in o['asset']:
    self.L(u+w*.5,z+.10,u+w*.5,z+h-.12,'#758a69',2)
    for dx,dz in [(-.10,.22),(.10,.33),(-.06,.40)]:self.L(u+w*.5,z+dz-.04,u+w*.5+dx,z+dz,'#80916d',4);self.C(u+w*.5+dx,z+dz+.03,.025,'#b78c7f',stroke='none')
   else:
    self.L(u+.08,z+h*.35,u+w*.45,z+h*.52,'#7e956f',7);self.L(u+w*.45,z+h*.52,u+w-.08,z+h*.31,'#a18d66',7)
    self.L(u+w*.2,z+.09,u+w*.6,z+h*.42,'#d4c7a2',3)
  elif k=='closetshelf':
   if o['asset']=='BR-CLOSET-STORAGE-03':
    top=o['shelf_top'];thick=o['shelf_thickness'];rail=o['rail_z']
    # Shelf footprint is 0.40 m; remaining inward reach belongs to hangers.
    board_u=u if o['front']=='east' or self.side in 'EW' else u+w-.40
    board_w=w if self.side in 'EW' else .40
    self.R(board_u,top-thick,board_w,thick,WOOD,sw=.6)
    if self.side in 'EW':
     self.L(u+.025,rail,u+w-.025,rail,'#806b54',2)
     for i in range(6):
      mid=u+.15+i*(w-.30)/5
      self.C(mid,rail-.025,.022,'none',stroke='#75644e')
      self.L(mid,rail-.047,mid,rail-.09,'#75644e',1)
      self.L(mid,rail-.09,mid-.055,rail-.22,WOOD,2);self.L(mid-.055,rail-.22,mid+.055,rail-.22,WOOD,2);self.L(mid+.055,rail-.22,mid,rail-.09,WOOD,2)
    else:
     mid=board_u+(.28 if o['front']=='east' else .12)
     self.C(mid,rail,.014,'#806b54');self.L(mid,rail-.02,mid,rail-.07,'#75644e',1)
     self.L(mid,rail-.07,u+.01,rail-.22,WOOD,2);self.L(u+.01,rail-.22,u+w-.01,rail-.22,WOOD,2);self.L(u+w-.01,rail-.22,mid,rail-.07,WOOD,2)
   else:
    self.R(u,z,w,.05,WOOD);self.L(u+.04,z-.14,u+w-.04,z-.14,'#a48a66',2)
    for i in range(3):
     mid=u+.18+i*.25;self.L(mid,z-.14,mid-.10,z-.30,'#9b866b',1.5);self.L(mid-.10,z-.30,mid+.10,z-.30,'#9b866b',1.5);self.L(mid+.10,z-.30,mid,z-.14,'#9b866b',1.5)
  elif k=='shelf':
   self.R(u,z-.04,w,.04,WOOD);self.R(u+.08,z-.145,.035,.11,WOOD);self.R(u+w-.115,z-.145,.035,.11,WOOD)
   for i in range(3):self.R(u+.05+i*.07,z,.055,.18+(i%2)*.04,['#ad8265','#a9a984','#d4be92'][i],sw=.5)
   self.vase(u+w-.20,z,.14,.20,any('PLANT' in x for x in o['children']))
  elif k=='mirror' and self.rid=='BA' and STUDY:
   mid=u+w/2;mw=.578
   self.R(mid-mw/2,z,mw,h,'#a4aea4',stroke='#927655',sw=4,rx=15)
   for xx in (mid-.43,mid+.43):
    self.C(xx,1.65,.035,'#ad8a5e');self.L(xx,1.65,xx,1.78,'#ad8a5e',3);self.C(xx,1.825,.077,'#f2e3be')
  elif k=='mirror':
   self.R(u,z,w,h,'#a4aea4',stroke='#927655',sw=4,rx=15)
   for xx in (u-.10,u+w+.10):self.C(xx,z+h*.7,.07,'#f2e3be')
  elif k=='fuse':
   self.R(u,z,w,h,'#a2a090');self.R(u+.03,z+.03,w-.06,h-.06,'#c2b9a5');self.C(u+w-.065,z+h*.45,.023,'#997c52')
   self.L(u+.12,z+h,u+.12,2.38,'#897664',3)
   self.L(u-.035,z+.03,u-.09,z-.06,'#9c7b66',1);self.L(u-.09,z-.06,u-.07,z-.14,'#9c7b66',1)
  elif k=='hooks':
   self.R(u,z,w,.08,WOOD)
   for i in range(4):self.C(u+.07+i*(w-.14)/3,z-.035,.025,'#ba9a62')
   self.R(u+.12,z-.52,.24,.47,'#9b8770',rx=5)
  elif k=='pans':
   self.L(u,z+h,u+w,z+h,'#806a54',3)
   for xx in (u+w*.28,u+w*.72):self.L(xx,z+h,xx,z+.23,'#806a54',3);self.C(xx,z+.16,.12,'#9c8b70')
  elif k=='towelring':
   mid=u+w/2;mount=1.15
   self.C(mid,mount,.035,'#ad8a5e');self.C(mid,mount-.120,.105,'none',stroke='#ad8a5e')
   self.R(mid-.13,.615,.26,.31,'#e7d7bd',rx=4)
   for zz in (.655,.675):self.L(mid-.12,zz,mid+.12,zz,'#bb8b86',2)
  elif o['instance']=='BA-TOWEL-RAIL-01:084' and STUDY:
   self.L(u,1.25,u+w,1.25,'#ae8d61',3)
   self.R(7.931-self.y,.584,.432,.687,'#e7d7bd',rx=3)
  elif k in ('towel','roll'):
   self.L(u,z+h,u+w,z+h,'#ae8d61',3);self.R(u+.03,z,w-.06,h-.035,'#e7d7bd',rx=3)
   for xx in (u+w*.3,u+w*.6):self.L(xx,z+.04,xx,z+h-.06,'#bca58a',1)
  elif k=='switch':self.R(u,z,w,h,IVORY,rx=2);self.R(u+w*.4,z+h*.35,w*.2,h*.3,'#a78d6c')
  elif k=='sconce':self.R(u+w*.4,z,w*.2,h*.8,'#ad8a5e');self.C(u+w*.5,z+h*.7,w*.55,'#f4dfad')
  elif k in ('mold','stain','lead','crack'):
   if k=='stain':
    self.R(u+.08,z+.10,w-.16,h-.20,'#b69c78',sw=0,rx=18,extra='opacity=".22"')
    for i in range(7):self.L(u+.10+i*.07,z+.12,u+.13+i*.07,z+h-.13,'#b49d7f',.5)
   elif k=='mold':
    if o['asset']=='BR-MOLD-02':
     # Schematic colony stippling follows upper corner rather than a central mass.
     for i in range(110):
      a=((i*37)%109)/109;b=((i*67+19)%113)/113
      t=1-a*a if self.side=='N' else a*a
      v=1-b*b
      if (self.side=='N' and t<.45 and v<.68) or (self.side=='E' and t>.70 and v<.48):continue
      self.C(u+.012+t*(w-.024),z+.02+v*(h-.04),.006+(i%5)*.005,'#292826',stroke='none')
    else:
     for i in range(17):
      xx=u+.09+(i*37%83)/100*(w-.14);zz=z+.08+(i*29%79)/100*(h-.14)
      self.C(xx,zz,.045+(i%3)*.025,'#596a53',stroke='none')
   elif k=='lead':
    for i in range(12):self.R(u+.03+(i*13%40)/100,z+.02+(i*7%20)/100,.055,.04,'#ac9c84',sw=.4)
   else:
    pts=[(u+w*.5,z+h),(u+w*.4,z+h*.7),(u+w*.6,z+h*.5),(u+w*.35,z+h*.2),(u+w*.5,z)]
    for a,b in zip(pts,pts[1:]):self.L(*a,*b,'#80665c',2)
  elif k=='bulb':self.L(u+w/2,z+.14,u+w/2,2.75,'#625950',2);self.C(u+w/2,z+.07,.07,'#f1ce80')
  elif k=='human':
   self.R(u+.08,z+.12,w-.16,h-.48,'none',stroke='#766e65',extra='stroke-dasharray="5 4"',rx=15);self.C(u+w/2,z+h-.14,.14,'none')
  elif k=='return':self.R(u,z,w,h,'#d6d4c3');self.panels(u,w)
  self.a.append('</g>');self.mark(u+w/2,min(2.48,z+h+.10),num)
  self.used.append(o['instance']);self.legend.append(f'{num}. {o["name"]}'+(' [projection]' if ghost else '')+f' — {o["asset"]}'+(' · '+o['state'] if o['state']!='static' else ''))
  if o['children']:self.legend.append('   + '+', '.join(o['children']))
 def vase(self,u,z,w,h,plant=False):
  self.R(u,z,w,h,'#c7a478',rx=8);self.R(u+w*.35,z+h,w*.30,.045,'#b29068')
  if plant:
   self.L(u+w*.5,z+h,u+w*.5,z+h+.34,'#6e805d',2)
   for dx,dz in [(-.1,.12),(.1,.20),(-.08,.28)]:self.L(u+w*.5,z+h+dz-.06,u+w*.5+dx,z+h+dz,'#809169',5)
 def lamp(self,mid,z,h):
  self.R(mid-.1,z,.2,.035,'#a98c60');self.L(mid,z+.035,mid,z+h-.19,'#a98c60',3);self.R(mid-.14,z+h-.20,.28,.20,'#edcf94',rx=6)
 def finish(self,row,notes):
  yy=row*560+98;self.text_px(1060,yy,'ITEMS / STATES',12,weight='bold');yy+=23
  for line in self.legend:
   for part in textwrap.wrap(line,width=48):self.text_px(1060,yy,part,10);yy+=14
  # Keep notes outside the room drawing, below dimensions.
  for j,t in enumerate(textwrap.wrap(notes,width=145)[:3]):self.text_px(65,row*560+505+j*16,t,11)
  return ''.join(self.a)

NOTES={
'LV':{'N':'Window and radiator stay readable. Chair is south-facing foreground; sofa/rug are floating, not attached to this wall.','E':'TV at y=1.50–2.60; bench y=2.70–3.35; fusebox y=3.40–3.85. Entry is farther south. Keep repair damage and conduit clear of casing.','S':'Actual southern boundary of combined living/entry: bathroom, office and coats. Hall console is shared, not duplicated.','W':'Bookcase on kitchen partition. Kitchen portal at y=2.35–3.55; below that the hall continues through an open span.'},
'KI':{'N':'Range at northwest corner; source depth includes controls. Window remains clear of counter/sink. Full-size pantry sits beside fridge after the user swap.','E':'Kitchen opens directly to living. Display shelf and print stay north of the portal; no new tall furniture in the doorway.','S':'Former hallway doorway is closed. Table and chairs are projected foreground; wall art and pottery add interest without narrowing the passage.','W':'Sink and prep run face east. Prep widths 0.45, 0.60 and 0.65 m; existing 1.00 m upper spans the southern two sections. Pantry is now north beside fridge.'},
'HA':{'N':'Short gallery wall ends at x=5.50; the rest is an opening into living. No side console remains on this wall.','E':'Entry opens outward. Fusebox and bench are immediately north of this cropped hall view; see LV-E for the complete entry composition.','S':'Bedroom, bath and office doors open into their rooms. Side console and flowers sit between bath and office; coat doors face this hall.','W':'Preserve the existing end cabinet, landscape and vase grouping against the relocated closet wall; this is the new hall terminus.'},
'BR':{'N':'Both closet and room door are on this wall. Closet doors open outward onto clear floor; the room door hinges at its east jamb.','E':'Dresser and mirror retain the 1.15 m bed-side aisle. Bedroom is aged plaster, with no white wainscoting or lead-paint patch.','S':'Bed head faces south. Window moved 0.25 m west to clear casing. Nightstands/lamps and quilt provide the warm layered character.','W':'Moved office bookcase fills the wall beside the closet approach. Shelf and print sit above; preserve access to the closet doors.'},
'BA':{'N':'North shelf, botanical and towel hook frame the door without covering its casing.','E':'Keep towel/roll reach clear of toilet lid. Linen cabinet is at the south end; shelf stays above toilet/towel zone.','S':'Tub, shower and frosted window. Keep Tyler crack visible below the sill; curtain parks at the east end and water fill is a separate reveal.','W':'Mirror/globes centred on basin, with toiletries shelf and hand towel nearby. Scale source mirror assembly and sconces only after dimension review.'},
'OF':{'N':'White wainscoting and lead-paint condition moved here. Wardrobe front is projected 1.55 m from the original north line, with coat storage behind it.','E':'Closet side return occupies first 1.55 m. No bookcase on this wall now; keep wardrobe approach open. White panels continue around the exposed return.','S':'Desk beneath window. Wainscot stops around window/apron: do not run the 1.10 m rail through the 0.90 m sill. Desk/lamp/papers remain.','W':'Daybed and small storage cabinet remain. Shelf, botanical and white wainscoting give this room its new finish identity.'},
'BC':{'N':'Mold belongs to interior back wall only. Centre is reserved for standing Malcolm; no low storage across this wall.','E':'Keep east side plain and unobstructed. Single bulb and dashed standing proxy are projections, not extra repeated objects.','S':'View back toward paired doors opening into bedroom. Closed leaves conceal encounter and prompt; repair preserves doors and bulb.','W':'High shallow shelf and low boxes stay on west side. Keep hanging clothes and storage outside the character/door/camera volume.'}}
NOTES['CT']={s:'Coat storage opens north into entry. Hanging rail/shelf and boxes are contained behind sliding doors; back wall is shared with guest wardrobe.' for s in 'NESW'}
NOTES['WG']={s:'Guest wardrobe opens south into office. Target 0.60 m usable depth after tracks/trim; no duplicated wall between the two storage volumes.' for s in 'NESW'}
if STUDY:
 NOTES['LV']['N']='FIX-004: fuse box now faces south above corner plant, center x11.05, box bottom1.40 m. Move all wire/door/damage states; validate click and Wyatt approach. Window/chair unchanged.'
 NOTES['LV']['E']='TV and existing pictures retained. Coat rack shifts right/south to center y3.30, actual0.72 m rail y2.94..3.66. Former fusebox area is clear; entry casing remains untouched.'
 NOTES['LV']['S']+=' FIX-006: unique artwork/frame assignments pending, preserve every physical instance ID.'
 NOTES['HA']['E']='Entry remains outward-opening; fuse box moved to north living wall above corner plant. Coat rack shifted in freed east-wall space.'
 NOTES['HA']['S']+=' FIX-006: :058 grows to1.30x0.90 m, centerX5.15, bottomZ1.12 between bedroom/bath casings; unique artwork/frame assignments pending.'
 NOTES['BC'].update(N='Charcoal mold rises into upper-right north/east corner, top 2.64 m below crown. Both side shelves project into this view at 1.88 m; central 1.094 m hanger-to-hanger aisle stays open.',E='Full-length east shelf: 1.67 m run, 0.40 m depth, 35 mm board at 1.88 m. Rail at 1.73 m with hooked hanging hangers. Narrow mold return remains visible above and behind storage.',W='Matching full-length west shelf and rail at the same lower heights; no tall fascia. Existing low box retained. Keep encounter and door routes clear.',S='Paired doors conceal Malcolm; both side shelves stop at sidewall ends. Retain single dangling bulb. Repair removes both corner overlays, preserving storage.')
 NOTES['KI'].update(N='Fridge beside prep on north wall. Sink centred below window; sill1.25/head2.40 requires a shortened counter-height window and apron. Faucet top1.343 stays in front of glass. FIX-003 replaces only sink body/bucket; preserve taps and Lukey identity. Intermittent drops land inside pail, no static beads.',W='Pantry faces east from west wall. Fridge is now on north wall facing south, with0.29 m hinge-side wall clearance. Prep starts x=1.20; validate open-door sweeps.',S='Small wall table and tucked stool replace the full dining table here. Main dining is between the kitchen and sofa.',E='Upper cupboard on east return, not over burners. Portal opens directly to the expanded dining/living area.')
 NOTES['LV']['W']='Kitchen partition shifted west0.70 m. Bookcase follows it; dining table stands between this wall and the floating sofa, with end chairs north/south.'
 NOTES['HA']['N']='Gallery wall now ends at x=4.80; opening to living/dining spans7.20 m. Keep artwork and sconce on the remaining plaster.'
if STUDY:
 NOTES['OF']['N']+=' FIX-019: fitted22mm trim stops2mm from actual casing; lead overlay remains centeredX8.925/Z.70 on planeY5.668.'
 NOTES['OF']['E']+=' FIX-019: tight wardrobe corner has7mm plain return, capped east run startsY7.239,2mm beyond casing face. Verify shell quadrant in kit README.'
 NOTES['OF']['S']+=' FIX-019: purpose-built under-apron cap top.778m; actual apron bottom.783. Fixed-size profiles, continuous lower rails,2mm sill/casing relief; use OF-WAINSCOT-02 manifest.'
 NOTES['OF']['W']+=' FIX-019: fitted continuous rails and mitred corners,22mm maximum wall projection; existing paint texture retained.'
if STUDY:NOTES['BA']={
'N':'FIX-007: toilet west/left of doorway; switch centered east/right of casing. Loaded paper holder is on west wall within reach. Lower tile field1.00+cap.05. Door opening stays unchanged.',
'E':'Basin at former toilet area, mirror and paired lights centeredY7.925. Two toiletries shelves top1.25; real hand-towel ring below shelf :077. Linen stays southeast but faces north;90-degree doors. High tile startsY8.55.',
'S':'Tub, bath water, Tyler repair and existing window unchanged. Full-height tile wraps shower corner and fits window aperture. Curtain and rod remain aligned; no south-wall plumbing now.',
'W':'Single source-size1.13m bath rail at bar1.25, one ivory bath towel; extra rail/rose towel retired. Lower folded-towel shelf. Shower/faucet moved here atY9.07. High tile beginsY8.55, cap transition finished vertically.'}
VIEWS={};coverage={};REVIEW=[]
for rid in ROOMS:
 rows=[];coverage[rid]={}
 for row,side in enumerate('NESW'):
  for projection in (False,True):
   v=View(rid,side,row)
   for o in OPEN:
    if o['room']==rid and o['side']==side:v.opening(o)
   selected=[]
   for num,o in enumerate(ITEMS,1):
    if rid not in o['rooms'] or side not in o['show']:continue
    u,w,dist=v.project(o)
    if u>=-.01 and u+w<=v.width+.01:selected.append((dist,num,o))
   for _,num,o in sorted(selected,key=lambda a:a[0]):v.item(o,num,projection)
   if rid=='BA' and side=='W' and STUDY:
    v.L(3.47,.79,3.47,2.13,'#8c938d',3);v.R(3.375,2.01,.19,.08,'#a99b81',sw=.8)
    v.L(3.38,.96,3.56,.96,'#8c938d',3);v.C(3.38,.96,.035,'#ad9a7f');v.C(3.56,.96,.035,'#ad9a7f')
    v.legend.append('Separate west-end plumbing atY9.07; taps retain original pivots/action. Curtain rod stays with curtain.')
   if rid=='BA' and side=='S' and not STUDY:
    v.L(.24,.58,.24,2.12,'#8c938d',4);v.L(.24,2.12,.48,2.12,'#8c938d',4)
   if rid=='BA' and side=='S':
    v.L(.15,2.22,1.95,2.22,'#8c938d',2);v.R(1.73,.45,.20,1.72,'#b59185',sw=.6)
    v.legend.append('Tub and curtain unchanged; plumbing moved to west wall. Separate rod replaces old combined fixture. Full-height tile cut around existing window.' if STUDY else 'Tub fixtures + curtain: parked east; keep repair patch visible.')
   if rid in ('KI','BR','BA','OF','LV') and side=='N':
    v.L(v.width/2,2.75,v.width/2,2.52,'#947d61',1.5);v.R(v.width/2-.16,2.42,.32,.13,'#ead3a2',rx=8)
    v.legend.append('Ceiling: ARC-CEILING-LIGHT-01; one physical fixture, not a copy per wall.')
   body=v.finish(row,NOTES[rid][side]);suffix='-projected' if projection else ''
   (P/f'{rid.lower()}-{side.lower()}{suffix}.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 {row*560} 1410 560"><rect x="0" y="{row*560}" width="1410" height="560" fill="#f7f1e5"/>'+body+'</svg>')
   cropw=max(510,130+v.width*v.scale)
   (P/f'{rid.lower()}-{side.lower()}{suffix}-drawing.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 {row*560} {cropw} 495"><rect x="0" y="{row*560}" width="{cropw}" height="560" fill="#f7f1e5"/>'+body+'</svg>')
   if not projection:
    rows.append(body);REVIEW.append(dict(room=rid,side=side,title=f'{rid}-{side} / {ROOMS[rid][0]}',notes=NOTES[rid][side],legend=v.legend,clean=f'{rid.lower()}-{side.lower()}-drawing.svg',projected=f'{rid.lower()}-{side.lower()}-projected-drawing.svg'))
   else:coverage[rid][side]=v.used;REVIEW[-1]['projection_legend']=v.legend
 width=1410;height=4*560+60
 doc=f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}"><rect width="100%" height="100%" fill="#f7f1e5"/>'+''.join(rows)+f'<text x="65" y="{height-22}" font-family="Arial" font-size="12" fill="#655347">Revision02 / living A · walls and nearby furniture shown; optional projected views show floating/opposite furniture.</text></svg>'
 (P/f'{rid.lower()}-elevations.svg').write_text(doc);VIEWS[rid]=doc
(P/'elevation-schedule.json').write_text(json.dumps(dict(status='Approved compact kitchen/dining; fitted source kits reconciled; engine validation pending' if STUDY else 'Reworked elevations from approved revision02; engine fit checks pending',architectural_assignments=json.loads((BASE/'architectural-assignments.json').read_text()) if STUDY else {},rooms=ROOMS,items=ITEMS,retired_components=RETIRED,openings=OPEN,ceiling_fixtures=CEILING,coverage=coverage,review=REVIEW),indent=2)+'\n')
# Repaired interior comparison: same room geometry, damage overlay omitted.
for rid,side in [('BC','N'),('OF','N'),('BA','S')]+([('BC','E'),('KI','N')] if STUDY else []):
 v=View(rid,side,0)
 for o in OPEN:
  if o['room']==rid and o['side']==side:v.opening(o)
 for num,o in enumerate(ITEMS,1):
  if rid in o['rooms'] and side in o['show']:v.item(o,num,False,True)
 if rid=='BA':
  if not STUDY:v.L(.24,.58,.24,2.12,'#8c938d',4);v.L(.24,2.12,.48,2.12,'#8c938d',4)
  v.L(.15,2.22,1.95,2.22,'#8c938d',2);v.R(1.73,.45,.20,1.72,'#b59185',sw=.6)
 if rid=='OF':v.L(v.width/2,2.75,v.width/2,2.52,'#947d61',1.5);v.R(v.width/2-.16,2.42,.32,.13,'#ead3a2',rx=8)
 body=v.finish(0,'Repaired-state design: remove only the localized damage. Preserve room surfaces and storage. No gameplay implementation is implied.')
 (P/f'{rid.lower()}-{side.lower()}-repaired.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1410 560"><rect width="1410" height="560" fill="#f7f1e5"/>'+body+'</svg>')
print(f'Generated {len(ROOMS)} room/storage sheets, {len(ROOMS)*4} walls with optional furniture projections, {len(ITEMS)} physical assembly records.')
