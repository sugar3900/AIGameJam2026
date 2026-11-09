"""Generate an approval-only floor plan; does not change approved A+ or engine files."""
import json, html, math, sys
from pathlib import Path
P=Path(__file__).resolve().parent
STUDY='--kitchen-dining-study' in sys.argv
old=json.loads((P.parent/'A-plus-candidate.json').read_text())
new=json.loads(json.dumps(old))
new['status']='APPROVED DESIGN — user selected living A and authorized revised elevations; engine validation pending'
new['revision']='02 — entrance living room / hall-end bedroom closet'
for room in new['rooms']: room.pop('wall_ids',None)
new['rooms'][0]['rect']=[5.5,0,6.5,3.8]
new['rooms'][1]['rect']=[0,0,5.5,3.8]
new['rooms'][2]['rect']=[2.2,3.8,9.8,1.8]
new['rooms'][2]['name']='Open entry and short private hall'
new['rooms'].append({'id':'BC','name':'Bedroom walk-in closet','rect':[0,3.8,2.2,1.8]})
new['open_portals']=[{'rooms':['LV','HA'],'axis':'h','x':5.5,'y':3.8,'width':6.5,'note':'Full-width opening after moving coat closet south of entry; retain overhead header and west return.'},{'rooms':['KI','LV'],'axis':'v','x':5.5,'y':2.35,'width':1.2,'note':'Doorless cased kitchen doorway, approximately 1.10 m finished clear.'}]
new['swing_doors']=[{'room':'BR','axis':'h','x':3.0,'y':5.6,'width':1.05,'opens':'down','hinge':'east'}, {'room':'BA','axis':'h','x':6.25,'y':5.6,'width':1.05,'opens':'down'}, {'room':'OF','axis':'h','x':9.45,'y':5.6,'width':1.05,'opens':'down'}, {'room':'ENTRY','axis':'v','x':12,'y':4.0,'width':1.05,'opens':'right'}]
new['windows'][0]={'room':'KI','axis':'h','x':1.35,'y':0,'width':1.6,'sill_height':0.9,'head_height':2.3}
new['windows'][1]={'room':'LV','axis':'h','x':7.75,'y':0,'width':1.6,'sill_height':0.9,'head_height':2.3}
new['windows'][2]['x']=3.3
new['fitted_closets'][0]={'name':'Bedroom hall-end walk-in','rect':[0,3.8,2.2,1.8],'opening_width':1.1,'opening_x':0.55,'door_type':'paired outward-hinged leaves; target 1.00 m finished clear total','door_swing_radius':0.5,'interior_repair':'black mold on north/back wall','ceiling_height':2.75,'light':'single dangling bare bulb','note':'New shell and wider doors needed; do not stretch existing assembly indiscriminately.'}
new['fitted_closets'][1]={'name':'Guestroom hanging wardrobe','rect':[10.75,6.4,1.25,.75],'sliding_opening_x':10.93,'opening_width':.9,'front':'south','door_type':'bypass sliding doors','usable_depth_target':.60,'note':'0.75 m nominal depth gives about 0.63 m between wall faces before trim/tracks; retain at least 0.60 m usable hanging depth when detailing.'}
new['fitted_closets'][2]={'name':'Entry coat closet','rect':[10.75,5.6,1.25,.8],'sliding_opening_x':10.93,'opening_width':.9,'front':'north','door_type':'bypass sliding doors','note':'Opens into entry; shared back partition with guest wardrobe at y=6.40. Remove original living-side coat enclosure.'}
new['objects']=[o for o in new['objects'] if o['room'] in ('BA','OF') and o['name']!='Office bookcase']
new['objects'] += [dict(name=n,rect=r,room=room) for room,n,r in [
('KI','Range',[.15,.15,.75,.732]),('KI','Prep',[.15,.90,.68,.45]),('KI','Sink / leak',[.15,1.35,.68,1.05]),('KI','Counter',[.15,2.4,.68,.6]),('KI','Prep / uppers',[.15,3.0,.68,.65]),('KI','Fridge',[4.5,.15,.77,.75]),('KI','Pantry',[3.25,.15,1.0,.678]),('KI','Radiator',[1.879,.15,.542,.254]),('KI','Dining table',[2.6,1.85,1.5,.85]),('KI','Chair',[2.05,2.02,.45,.5]),('KI','Chair',[4.25,2.02,.45,.5]),
('HA','Fusebox / Wyatt',[11.82,3.40,.12,.45]),
('HA','Entry bench',[11.6,2.70,.25,.65]),('HA','Hall end cabinet',[2.28,4.19,.2475,1.02]),('HA','Hall side console',[7.85,5.27,1.05,.25]),
('BR','Bookcase from office',[.15,6.45,.3,1.1]),('BR','Bed',[1.6,7.4,1.5,1.9]),('BR','Nightstand',[1.0,8.85,.45,.45]),('BR','Nightstand',[3.25,8.85,.45,.45]),('BR','Dresser / mirror',[4.25,7.35,.4,1.15]),
('BC','High shelf',[.12,4.0,.3,1.1]),('BC','Mold / Malcolm',[.65,3.89,.9,.04])]]
# User selected living option A; preserve its source-sized footprints and facing.
selected=json.loads((P/'living-options/options.json').read_text())['options']['A']
new['objects']=[o for o in new['objects'] if o['room']!='LV']
for o in selected['objects']:
 new['objects'].append(dict(name={'Coffee':'Coffee table','TV':'TV / console','Table + lamp':'Side table'}.get(o['name'],o['name']),rect=o['rect'],room='LV',facing={'E':'east','W':'west','N':'north','S':'south'}.get(o.get('front'))))
new['selected_living_option']={'id':'A','status':'selected by user','description':'Floating sofa faces east; east-wall TV faces west; chair faces south at north end of rug.'}
new['decorative_floor_items']=[{'name':'Living rug','rect':selected['rug'],'asset_id':'LV-RUG-01','blocking':False}]
for o in new['objects']:
 if o['room']=='KI' and o['name']=='Pantry':o['facing']='south'
 if o['room']=='KI' and o['name']=='Prep / uppers':o['facing']='east'
 if o['name']=='Hall end cabinet':o.update(asset_id='HA-CABINET-01',facing='east',note='Preserve at new hallway terminus against relocated bedroom closet wall; retain picture and vase grouping.')
 if o['name']=='Hall side console':o.update(asset_id='HA-CONSOLE-01',facing='north',note='Hall-facing wall between bathroom and office doorways; 0.55 m nominal gap to either doorway.')
new['repairs']={'LV':'Wyatt: east wall immediately north of the apartment entry, x=11.82, y=3.40–3.85 m; faces west. Preserve living/Wyatt gameplay identity despite entry-side placement.','KI':'Lukey: west-wall sink; clear approach from dining aisle.','BA':'Tyler: south wall above tub, unchanged.','BR':'Malcolm: north interior wall of relocated walk-in closet; paired doors conceal him.','OF_LEAD':'Separate lead-paint condition on office / guestroom white wainscoting; north wall between storage cabinet and room doorway, x=8.65–9.20 m. Keep approach clear of door swing.'}
new['wall_finishes']={'BR':'Painterly aged plaster with baseboard and crown; no wainscoting.','OF':'White wainscoting with painterly plaster above; localized lead-paint condition on north wall.','BC':'Closet interior plaster with separate concealed mold.'}
new['clearance_notes']=[
'White wainscoting and its associated lead-paint feature move from bedroom to office / guestroom per user direction. Detail panels around office window, closet and doorway after layout approval.',
'Nominal 0.12 m centre-line walls; clearance dimensions below deduct these where relevant but not trim, frame stops, protrusions or camera/capsule.',
'New closet interior approximately 2.08 x 1.68 m before trim; 0.30 m high side shelving leaves central floor open. 1.10 m rough opening targets approximately 1.00 m clear with paired leaves.',
'Measured closet hinge axis is y=5.678 and open-leaf tips reach y=6.181. Cross-bedroom route uses y=6.65; the 0.38 m radius player clears leaves by 0.089 m and actual bed north edge y=7.399 by 0.369 m. Real PIE movement tested in both directions. Main bedroom entry has a separate approach east of closet.',
'Bed east edge x=3.10 to dresser front x=4.25 gives 1.15 m nominal aisle. Bed west edge x=1.60 to west wall face x=0.06 gives 1.54 m, except localized nightstand near headboard.',
'Kitchen southern circulation between table edge y=2.70 and wall face y=3.74 is 1.04 m before trim. North prep front y=0.80 to table y=1.85 gives 1.05 m.',
'Kitchen west chair x=2.05 to sink face x=0.83 leaves 1.22 m while chair is parked; pulling a chair out reduces local width. Southern route must remain clear.',
'Private hall remains 1.68 m clear before trim; end cabinet occupies x=2.28–2.5275 at the new west terminus. Side console is on the south wall between bath/office doors at x=7.85–8.90, with 0.55 m nominal to either doorway and 0.02 m rear gap to wall face; closed front leaves 1.41 m to the former north-wall face (living is open here). Coat closet now opens north into the entry from the office-side footprint. Entry bench moves to the east wall north of the front door.',
'Living/hall opening 6.50 m nominal; kitchen/living portal 1.20 m nominal, approximately 1.10 m finished clear. No swing leaf on kitchen portal.',
'Bedroom, bath and office rough openings enlarged to 1.05 m; entry also proposed 1.05 m. Final clear widths depend on chosen frames.',
'Living window widened to 1.60 m at the existing opening centre; former living window retained for kitchen. Bedroom window shifted 0.25 m west to avoid east-wall trim collision.',
'Sink relocates to west wall, avoiding window-sill/worktop interference. Use KI-SINK-NARROW-01 rotated 90 degrees, not the full sink/cabinet assembly. Wet-service route is a new design assumption.',
'Living/kitchen exchange requires new flooring, wall finishes, lighting, repair/room volumes and transforms. Existing furniture dimensions are approximate source footprints, not collision guarantees.',
'Bathroom and office room boundaries remain. Guest wardrobe moves 0.80 m south and reduces nominal depth from 1.20 to 0.75 m. Coat and guest closets share a back partition; bypass doors avoid floor sweeps. Guest wardrobe has a reserved 0.90 m front approach.',
'Office doorway shifts 0.15 m west, leaving 0.25 m nominal between its east jamb and the coat closet side. Check casing before construction.',
'Fusebox moves to east wall immediately north of entry; bench ends y=3.35 and fusebox spans y=3.40–3.85. Resolve casing and separable damage extents in elevation, preserving a clear west-facing interaction approach and living/Wyatt gameplay identity.',
'Office bookcase moves to bedroom west wall at x=0.15, y=6.45. Its front is 1.15 m from the bed west edge where their lengths overlap; the closet approach remains clear.',
'Living furniture option A selected by user and incorporated; other revision-02 decisions preserved. User authorized revised elevations after selecting A; engine reservation remains in force.',
'Technical fit adjustment during elevation handoff: range total depth includes controls at 0.732 m; adjacent west prep begins y=0.90 with 0.45 m frontage to avoid overlap. User swapped pantry and prep/uppers: use full-size 1.00 m pantry on north wall at x=3.25, and west prep at y=3.00; existing 1.00 m upper spans y=2.525–3.525 above the two adjacent west counter sections. Short prep cabinets need fitted-width variants.',
'Living option A uses source-sized sofa, chair, TV, coffee table, bookcase and end table; sofa faces east, TV faces west, chair faces south. Seat-to-screen approximately 2.90 m; sofa-to-table gap 0.46 m. Keep the existing rug at 2.50 x 1.80 m, rotated north-south.',
'Kitchen approach now passes west of the floating sofa at x=7.05; use the east side of the coffee table for the TV approach. These replace the previous route through the new sofa footprint.'
]
new['circulation_paths']=[[[12,4.65],[9.7,4.65],[6.8,4.65],[3.55,4.65],[3.55,6.65],[1.1,6.65],[1.1,4.75]],[[7.05,4.65],[7.05,3.1],[5.1,3.1],[1.55,3.1],[1.55,1.85]],[[6.8,4.65],[6.8,6.8]],[[9.975,4.65],[9.975,6.95]],[[11.35,4.65],[11.35,5.15]]]
new['circulation_paths'] += [[[10.8,4.65],[10.8,2.2]],[[11.2,4.65],[11.2,3.7]]]
new['approach_zones']=[{'name':'Guest wardrobe access','rect':[10.75,7.21,1.19,.90],'note':'Keep free of furniture; bypass doors do not swing into this zone.'}]
if STUDY:
 new['status']='KITCHEN / DINING ALTERNATIVE — awaiting selection; preserves living A and other user decisions'
 new['revision']='02-KD — compact kitchen / dining between kitchen and sofa'
 new['rooms'][0]['rect']=[4.8,0,7.2,3.8]
 new['rooms'][0]['name']='Living / dining'
 new['rooms'][1]['rect']=[0,0,4.8,3.8]
 new['rooms'][1]['name']='Kitchen'
 new['open_portals'][0].update(x=4.8,width=7.2)
 new['open_portals'][1]['x']=4.8
 new['objects']=[o for o in new['objects'] if o['room']!='KI']
 for o in new['objects']:
  if o['room']=='LV' and o['name']=='Bookcase':o['rect'][0]=4.95
 new['objects'] += [dict(name=n,room=room,rect=r,facing=front) for room,n,r,front in [
 ('KI','Prep',[1.20,.15,.425,.65],'south'),('KI','Sink / leak',[1.625,.15,1.05,.65],'south'),('KI','Counter',[2.675,.15,.775,.65],'south'),('KI','Range',[3.45,.15,.75,.732],'south'),('KI','Prep / uppers',[4.2,.15,.45,.65],'south'),
 ('KI','Fridge',[.35,.15,.77,.75],'south'),('KI','Pantry',[.15,2.35,.678,1.0],'east'),
 ('KI','Wall table',[2.0,3.23,.90,.45],'north'),('KI','Tucked stool',[2.30,3.35,.30,.30],'north'),
 ('LV','Dining table',[6.1,1.75,.85,1.5],None),('LV','Dining chair',[6.275,1.15,.50,.50],'south'),('LV','Dining chair',[6.275,3.35,.50,.50],'north')]]
 for obj in new['objects']:
  if obj['room']=='KI' and obj['name'] in ('Counter','Prep / uppers'):
   is_wide=obj['name']=='Counter'
   obj.update(asset_id='KI-CABINET-02',module_width=.775 if is_wide else .450,carcass_width=.735 if is_wide else .410,carcass_offset_x=-.020 if is_wide else .020,range_filler_width=.040,range_filler_side='east' if is_wide else 'west',note='Continuous full-width worktop; recessed filler clears range-neighbour door swing. Use final source manifest pivots.')
  if obj['room']=='KI' and obj['name']=='Range':obj.update(closed_handle_front_y=.926,note='Rectangle is body planning footprint; actual oven handle projects to planY=.926. Keep body rear alignedY=.15; do not recenter from handle bounds.')
 new['windows'][0].update(sill_height=1.25,head_height=2.40,note='New counter-height window variant: short apron stays above 1.18 m; sill projects no more than 0.12 m from finished wall. Keep faucet in front of glazing, verify sash travel.')
 new['wall_mounted_fittings']=[dict(asset_id='KI-UPPER-01',wall='KI-E',u=.25,z=1.60,width=1.00,height=.5455,note='Cupboard on east return; clear of range footprint, no cupboard directly over burners.')]
 new['dining_zone']={'rect':[5.2,1.0,2.7,3.0],'note':'Shared living/dining space, not an enclosed room. Table rotates 90 degrees; end chairs pull north/south.'}
 new['repairs']['KI']='Lukey: north-wall sink centred at x=2.15 under the window; clear approach from open kitchen centre.'
 new['circulation_paths']=[[[12,4.65],[9.7,4.65],[6.8,4.65],[3.55,4.65],[3.55,6.65],[1.1,6.65],[1.1,4.75]],[[5.5,4.65],[5.5,2.9],[3.45,2.9],[3.45,1.5],[2.15,1.5]],[[7.5,4.65],[7.5,.70],[6.5,.70]],[[6.8,4.65],[6.8,6.8]],[[9.975,4.65],[9.975,6.95]],[[11.35,4.65],[11.35,5.15]],[[10.8,4.65],[10.8,2.2]],[[11.2,4.65],[11.2,3.7]]]
 new['clearance_notes']=[n for n in new['clearance_notes'] if not any(t in n for t in ('Kitchen southern','Kitchen west chair','Sink relocates','Technical fit adjustment','Kitchen approach now','Living/hall opening'))]
 new['clearance_notes'] += [
 'Kitchen/living partition shifts 0.70 m west to x=4.80. Kitchen doorway stays y=2.35–3.55, and the open hall span grows to 7.20 m.',
 'Kitchen worktop runs along north wall from x=1.20 to4.65. Fridge faces south beside prep at x=.35, with .29 m to west finished wall and .08 m to prep. Left-hinge door has nominal space for105 degrees; verify shelves, handle and collision in3D. Pantry remains west-facing east. Sink stays centred x=2.15 under window.',
 'The sink upstand reaches about1.135 m and faucet1.343 m. Proposed sill1.25/head2.40 with short apron bottom>=1.18 and sill projection<=0.12 m requires a new window variant, not merely raising the existing kit. Validate faucet/glass/sash depths in 3D.',
 'Dining table rotates north-south in the expanded living/dining space. West side gap to kitchen wall face1.24 m; east side gap to sofa back1.15 m. Chairs are at north/south ends, not in those side aisles.',
 'South dining chair ends y=3.85 parked; a0.40 m pullback reaches4.25, leaving0.40 m to the primary route centreline4.65. Verify actual capsule and chair sweeps.',
 'Optional wall table0.90x0.45 m has a stool tucked under it; this is an intentional overlap below the tabletop. It is a new small table/stool variant, not the full dining table scaled down.',
 'Upper cupboard moves to east return y=.25–1.25, bottom1.60. Keep its depth and doors clear of range and window trim.'
 ]
 new['status']='APPROVED DESIGN — compact kitchen/dining with north-wall fridge; user approval 2026-11-09; engine validation pending'
 new['approval_date']='2026-11-09'
 for door in new['swing_doors']:door.update(width_semantics='rough',clear_width=.99,rough_head=2.14,frame_asset='ARC-ENTRY-DOOR-02' if door['room']=='ENTRY' else 'ARC-DOOR-02')
 P=P/'kitchen-dining-study';P.mkdir(exist_ok=True)
(P/'proposed-plan.json').write_text(json.dumps(new,indent=2)+'\n')
(P/'approved-plan.json').write_text(json.dumps(new,indent=2)+'\n')

S=75; OX=78; OY=92
X=lambda v: OX+v*S
Y=lambda v: OY+v*S
E=html.escape
colors={'LV':'#edcaa1','KI':'#d9dfb8','HA':'#eadcc5','BR':'#d9d0df','BA':'#eac8c3','OF':'#c7d9d5','BC':'#c8bbce'}
def render(data,proposed=True):
 split=4.8 if STUDY and proposed else 5.5
 out=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1120 965" role="img" aria-label="Apartment proposed floor plan" style="font-family:Arial,sans-serif">', '<defs><marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0L10 5L0 10" fill="none" stroke="#287d77" stroke-width="2"/></marker></defs>', '<rect width="1120" height="965" fill="#faf6ed"/>']
 def text(x,y,t,size=12,fill='#3f3932',anchor='middle',weight='normal'):
  out.append(f'<text x="{x:.2f}" y="{y:.2f}" text-anchor="{anchor}" font-size="{size}" font-weight="{weight}" fill="{fill}">{E(t)}</text>')
 def line(x1,y1,x2,y2,c='#544a40',w=9,dash=''):
  out.append(f'<line x1="{X(x1):.2f}" y1="{Y(y1):.2f}" x2="{X(x2):.2f}" y2="{Y(y2):.2f}" stroke="{c}" stroke-width="{w}" '+(f'stroke-dasharray="{dash}"' if dash else '')+'/>')
 def rect(r,fill,stroke='#8c7965',sw=1,rx=0):
  x,y,w,h=r;out.append(f'<rect x="{X(x):.2f}" y="{Y(y):.2f}" width="{w*S:.2f}" height="{h*S:.2f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" rx="{rx}"/>')
 text(78,34,('APPROVED KITCHEN + DINING · LIVING A' if STUDY else 'APPROVED LAYOUT · REVISION 02 / LIVING A') if proposed else 'CURRENT A+ DESIGN · DOCUMENTED BASELINE',20,anchor='start',weight='bold')
 text(78,59,'Design approved'+' · same 12.00 × 9.55 m envelope · north ↑ · dimensions in metres',13,anchor='start')
 for r in data['rooms']: rect(r['rect'],colors[r['id']],sw=0)
 if proposed: rect([split,3.8,12-split,1.8],colors['LV'],sw=0)
 # Rug and loose furniture.
 if proposed:
  rect(data['decorative_floor_items'][0]['rect'],'#ba9581','#ad8a76',1,6)
  for z in data.get('approach_zones',[]):
   x,y,w,h=z['rect'];out.append(f'<rect x="{X(x)}" y="{Y(y)}" width="{w*S}" height="{h*S}" fill="none" stroke="#287d77" stroke-width="1.5" stroke-dasharray="4 3"/>')
 for o in data['objects']:
  n=o['name'];r=o['rect'];x,y,w,h=r
  if n=='Mold / Malcolm':rect(r,'#5c6953',sw=0);continue
  fill='#fcf6e8'
  if n in ('Bed','Sofa','Daybed','Armchair'):fill='#bb9084' if n!='Bed' else '#aa91aa'
  if n in ('Tub / crack','Basin','WC'):fill='#fff8ee'
  rect(r,fill,rx=3)
  if n=='Bed':
   rect([x+.12,y+h-.48,.54,.30],'#f2e6db',rx=4);rect([x+.84,y+h-.48,.54,.3],'#f2e6db',rx=4)
  if n=='Sofa':
   for v in (y+.16,y+.78,y+1.4):rect([x+.18 if o.get('facing')=='east' else x+.08,v,.56,.54],'#d4ae96',rx=3)
   if o.get('facing')=='east':
    rect([x+.04,y+.08,.08,h-.16],'#936a5b',sw=0)
    line(x+w+.07,y+h/2,x+w+.29,y+h/2,'#654b3f',2)
    line(x+w+.29,y+h/2,x+w+.21,y+h/2-.07,'#654b3f',2)
    line(x+w+.29,y+h/2,x+w+.21,y+h/2+.07,'#654b3f',2)
  if n=='TV / console' and o.get('facing')=='west':line(x,y+.12,x,y+h-.12,'#725075',3)
  if n=='Armchair' and o.get('facing')=='south':rect([x+.06,y+.04,w-.12,.07],'#936a5b',sw=0)
  if n=='Side table' and o['room']=='LV':out.append(f'<circle cx="{X(x+w/2)}" cy="{Y(y+h/2)}" r="8" fill="#e6c27b" stroke="#937847"/>')
  if n=='Sink / leak': rect([x+.12,y+.22,w-.24,h-.44],'#abc1bf',rx=5)
  if n=='Range':
   for dx in (.2,.55):
    for dy in (.18,.5):out.append(f'<circle cx="{X(x+dx)}" cy="{Y(y+dy)}" r="6" fill="#746958"/>')
  if (w>=.6 and h>=.35) or (STUDY and proposed and n=='Prep') or n in ('TV / console','Dresser / mirror','High shelf','Bookcase from office','Entry bench','Hall end cabinet','Hall side console','Bookcase'):
   label={'Dining table':'Dining','Coffee table':'Coffee','Dresser / mirror':'Dresser','TV / console':'TV','Prep / uppers':'Prep + uppers','Sink / leak':'Sink','Tub / crack':'Tub','Office bookcase':'Books','Office storage cabinet':'Storage','Hall console':'Console','Bookcase from office':'Bookcase','Entry bench':'Bench','Hall end cabinet':'End cabinet','Hall side console':'Side console'}.get(n,n)
   if h>w*1.3:
    out.append(f'<text transform="translate({X(x+w/2):.2f} {Y(y+h/2):.2f}) rotate(-90)" text-anchor="middle" font-size="11" fill="#463b32">{E(label)}</text>')
   else:text(X(x+w/2),Y(y+h/2)+4,label,11)
 # Closets.
 for i,c in enumerate(data['fitted_closets']):
  if proposed and i==0:continue
  rect(c['rect'],'#c4b39a','#756858',2)
  x,y,w,h=c['rect'];text(X(x+w/2),Y(y+h/2),'Coats' if i==2 else (('Wardrobe' if proposed else 'Storage') if i==1 else 'Closet'),11)
  start=c.get('sliding_opening_x',c.get('opening_x',x+.1));width=c['opening_width']
  front_y=y if c.get('front')=='north' else y+h
  line(start,front_y,start+width,front_y,'#faf6ed',9);line(start,front_y,start+width,front_y,'#9c7557',2)
  if proposed and i==1:text(X(x+w/2),Y(y+h/2)+14,'0.75 m deep',9)
 # Walls: cut apertures explicitly.
 for a in [(0,0,12,0),(0,0,0,9.55),(12,0,12,9.55),(0,9.55,12,9.55),(0,5.6,12,5.6),(4.8,5.6,4.8,9.55),(7.9,5.6,7.9,9.55),(split,0,split,3.8)]:line(*a)
 if proposed:
  line(0,3.8,split,3.8);line(2.2,3.8,2.2,5.6)
  line(split,3.8,12,3.8,'#998168',2,'6 5')
  line(10.75,5.6,10.75,7.15);line(10.75,6.4,12,6.4);line(10.75,7.15,12,7.15)
  for c in data['fitted_closets'][1:]:
   x,y,w,h=c['rect'];fy=y if c['front']=='north' else y+h;start=c['sliding_opening_x'];width=c['opening_width']
   line(start,fy,start+width,fy,'#faf6ed',11)
   line(start,fy-.025,start+width*.56,fy-.025,'#9c7557',2)
   line(start+width*.44,fy+.025,start+width,fy+.025,'#9c7557',2)
 else:line(0,3.8,12,3.8)
 for w in data['windows']:
  x,y,ww=w['x'],w['y'],w['width'];line(x,y,x+ww,y,'#b7d2d5',10);line(x,y,x+ww,y,'#f9ffff',2)
 for d in data['swing_doors']:
  x,y,w=d['x'],d['y'],d['width'];R=w*S
  if d['axis']=='h':
   line(x,y,x+w,y,colors[d['room']],11)
   sign=1 if d['opens']=='down' else -1
   hinge=x+w if d.get('hinge')=='east' else x
   end=x if d.get('hinge')=='east' else x+w
   sweep=(1 if sign>0 else 0) if hinge==x else (0 if sign>0 else 1)
   line(hinge,y,hinge,y+sign*w,'#9c7557',2)
   out.append(f'<path d="M {X(end)} {Y(y)} A {R} {R} 0 0 {sweep} {X(hinge)} {Y(y+sign*w)}" fill="none" stroke="#9c7557" stroke-width="1.4"/>')
  else:
   line(x,y,x,y+w,'#faf6ed',11);line(x,y,x+w,y,'#9c7557',2)
   out.append(f'<path d="M {X(x)} {Y(y+w)} A {R} {R} 0 0 0 {X(x+w)} {Y(y)}" fill="none" stroke="#9c7557" stroke-width="1.4"/>')
 if proposed:
  line(split,2.35,split,3.55,colors['KI'],12)
  line(.55,5.6,1.65,5.6,colors['BR'],12)
  for x,sgn in ((.6,1),(1.6,-1)):
   # Measured fitted hinge offset and 95-degree leaf sweep, not wall-centreline radius.
   hinge_y=5.678; leaf_length=.505
   tip_x=x+sgn*leaf_length*math.cos(math.radians(95))
   tip_y=hinge_y+leaf_length*math.sin(math.radians(95))
   line(x,hinge_y,tip_x,tip_y,'#9c7557',2)
   out.append(f'<path d="M {X(x+sgn*leaf_length)} {Y(hinge_y)} A {leaf_length*75} {leaf_length*75} 0 0 {1 if sgn==1 else 0} {X(tip_x)} {Y(tip_y)}" fill="none" stroke="#9c7557" stroke-width="1.4"/>')
  # Standing figure and bulb shown as planning symbols, not furniture.
  out.append(f'<circle cx="{X(1.14)}" cy="{Y(4.68)}" r="21" fill="none" stroke="#6d6370" stroke-dasharray="4 3"/>')
  out.append(f'<circle cx="{X(1.14)}" cy="{Y(4.68)}" r="5" fill="#e9c567" stroke="#6d6370"/>')
  out.append('<g class="routes" fill="none" stroke="#287d77" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" opacity=".78">')
  for path in data['circulation_paths']:
   pts=' '.join(f'{X(x):.2f},{Y(y):.2f}' for x,y in path)
   out.append(f'<polyline points="{pts}" marker-end="url(#arr)"/>')
  out.append('</g>')
  # Room titles are deliberately placed in free floor areas.
  labels=[((2.5 if STUDY else 2.9),1.25,('KITCHEN' if STUDY else 'KITCHEN / DINING'),('4.80 × 3.80' if STUDY else '5.50 × 3.80')),(8.8,3.90,('LIVING / DINING + ENTRY' if STUDY else 'LIVING + OPEN ENTRY'),('7.20 × 5.60 gross zone' if STUDY else '6.50 × 5.60 gross zone')),(1.1,4.2,'WALK-IN','2.20 × 1.80'),(3.5,4.32,'PRIVATE HALL','closet ends the old corridor'),(2.65,7.0,'BEDROOM','aged plaster walls'),(6.35,6.55,'BATHROOM','existing layout'),(9.7,7.45,'OFFICE / GUEST','white wainscoting')]
  for x,y,t,sub in labels:
   text(X(x),Y(y),t,14,weight='bold');text(X(x),Y(y)+17,sub,11)
  text(X(1.13),Y(5.2),'stand + single bulb',10)
  text(X(.65),Y(3.72),'MOLD ON INSIDE BACK WALL',9,anchor='start')
  text(X(1.1),Y(6.38),'1.00 m clear door target',10)
  text(X(3.67),Y(8.7),'1.15 m aisle',10)
  if not STUDY:text(X(2.8),Y(3.48),'1.04 m passage',10)
  text(X(8.15),Y(4.26),('7.20 m cased opening' if STUDY else '6.50 m cased opening'),11)
  text(X(11.345),Y(8.0),'0.90 m approach',9)
  text(X(split)+10,Y(2.2),'Kitchen entry',11,anchor='start')
  text(X(12)+8,Y(5.28),'ENTRY',12,anchor='start',weight='bold')
  text(X(11.65),Y(3.75),'Fuse / Wyatt',10,anchor='end')
  # Lead paint moves with the wainscoting to the office north wall.
  line(8.65,5.67,9.2,5.67,'#9a6d85',4)
  text(X(8.925),Y(5.95),'lead paint',10)
 else:
  for r in data['rooms']:
   x,y,w,h=r['rect'];text(X(x+w/2),Y(y+h/2),r['name'].upper(),15,weight='bold')
  text(X(12)+8,Y(5.28),'ENTRY',12,anchor='start',weight='bold')
 text(78,849,'Teal = walking routes    ·    Dashed wall line = retained overhead header    ·    Blue = exterior windows',12,anchor='start')
 text(78,875,'APPROVED DESIGN.'+' Clearances still require game-capsule and dialogue-camera validation.',12,anchor='start',weight='bold')
 text(78,899,'Wall lines use the existing centre-line datum. Closet and opening dimensions are nominal unless marked clear.',12,anchor='start')
 text(78,923,'Revised elevations follow this layout. Art exports, Unreal maps and gameplay are unchanged.',12,anchor='start')
 out.append('</svg>');return ''.join(out)
svg=render(new)
(P/'proposed-plan.svg').write_text(svg)
(P/'approved-plan.svg').write_text(svg)
comparison_svg=(Path(__file__).resolve().parent/'approved-plan.svg').read_text() if STUDY else render(old,False)
(P/'current-plan-comparison.svg').write_text(comparison_svg)
page='''<!doctype html><html><head><meta charset="utf-8"><style>
body {font-family:var(--font-sans,Arial,sans-serif);color:var(--foreground);margin:0} .controls{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 12px}button{font:inherit;padding:8px 12px;background:var(--secondary);color:var(--foreground);border:1px solid var(--border);border-radius:var(--radius,8px);cursor:pointer}button.active{background:var(--primary);color:var(--primary-foreground)}.plan{border-radius:var(--radius,8px);overflow:hidden}.plan svg{display:block;width:100%;height:auto}.notes{font-size:14px;line-height:1.5}.notes p{margin:10px 0}.hidden{display:none} .off .routes{display:none}.plan.zoom{overflow:auto}.plan.zoom svg{width:1120px;max-width:none}
</style></head><body><div class="controls"><button class="active" id="propose" onclick="show(true)">Proposed layout</button><button id="baseline" onclick="show(false)">Previous documented plan</button><button onclick="document.getElementById('proposal').classList.toggle('off')">Toggle walking routes</button><button onclick="document.querySelectorAll('.plan').forEach(p=>p.classList.toggle('zoom'))">Zoom plan</button></div><div class="plan" id="proposal">'''+svg+'''</div><div class="plan hidden" id="previous">'''+comparison_svg+'''</div><div class="notes"><p><strong>Living option A selected:</strong> the sofa faces east toward the east-wall TV; the chair faces south at the north end of the rug. The kitchen route passes behind the sofa, and the TV approach stays to the east of the coffee table.</p><p><strong>Apartment layout:</strong> swap the two north rooms, open the living room to the entrance/hall, and give the kitchen a wide doorway onto the living room.</p><p>The bedroom closet moves entirely into the former hall end. Its doors face the bedroom; the bed stays clear of their swing. The hidden mold and one dangling bulb remain in the closet. White wainscoting and its lead-paint feature move to the office/guestroom; the bedroom uses aged plaster.</p><p>Coats now open into the entry from its south side. A shallower guest wardrobe sits behind them, opening into the office. The office bookcase moves to the bedroom west wall; the entry bench moves north of the front door. The fusebox sits immediately beside the entrance on the east wall, with its repair approach kept clear.</p><p>The end cabinet stays at the shortened hall’s western end, against the closet wall. The narrow side console moves between the bathroom and office doorways.</p><p><strong>Tradeoff:</strong> the kitchen is smaller, services move to the west wall, and the living room becomes part of the main circulation. Bathroom and office doors face the open living/entry zone.</p><p><strong>Floor plan selected; revised elevations authorized.</strong> Engine changes remain with the integration team.</p></div><script>function show(p){document.getElementById('proposal').classList.toggle('hidden',!p);document.getElementById('previous').classList.toggle('hidden',p);document.getElementById('propose').classList.toggle('active',p);document.getElementById('baseline').classList.toggle('active',!p)}</script></body></html>'''
if STUDY:
 page=page.replace('Previous documented plan','Previous approved layout')
 page=page.replace('Proposed layout','Approved layout').replace('services move to the west wall','services move to the north wall')
 page=page.replace('<strong>Apartment layout:</strong> swap the two north rooms, open the living room to the entrance/hall, and give the kitchen a wide doorway onto the living room.', '<strong>Kitchen/dining change:</strong> the kitchen shrinks by 0.70 m. Sink and counter run along the north window wall; the fridge sits beside the prep counter and the pantry stays on the west wall. The dining table rotates into the space between kitchen and sofa, leaving 1.24 m on its west side and 1.15 m on its east side. A small wall table and tucked stool give the kitchen a breakfast spot.')
(P/'review.html').write_text(page)
print('Generated proposal JSON, SVG, baseline comparison and review HTML.')
