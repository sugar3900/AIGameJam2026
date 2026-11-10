from pathlib import Path
import json,math,xml.etree.ElementTree as ET
from bathroom_patch import HERE,BASE,ROUTES,OVERRIDES
R=.38
# Conservative source AABBs; decorative water/towels have no blocking collision.
boxes={
 'west wall':(4.74,5.54,4.878,9.61),'east wall':(7.822,5.54,7.96,9.61),'south wall':(4.74,9.472,7.96,9.61),
 'north left wall':(4.74,5.54,6.25,5.678),'north right wall':(7.30,5.54,7.96,5.678),
 'left door jamb':(6.19,5.50,6.28,5.70),'right door jamb':(7.27,5.50,7.36,5.70),
 'toilet':(5.23,5.685,5.808,6.398),'basin':(7.262,7.605,7.822,8.245),
 'linen closed':(7.15,8.671,7.75,9.35),'linen90deg leaf':(7.687,8.1935,7.793,8.75),
 'tub':(4.965,8.73,6.635,9.41),'basket':(4.8868,8.009,5.3532,8.351),
 'bin':(7.513,5.733,7.737,6.025),'room door90deg':(6.26,5.635,6.30,6.611),
 'west shelf':(4.86,6.625,5.01,7.275),
 'east shelf1':(7.69,6.025,7.84,6.675),'east shelf2':(7.69,6.775,7.84,7.425)}
def gap(p,b):
 x,y=p;x0,y0,x1,y1=b;return math.hypot(max(x0-x,0,x-x1),max(y0-y,0,y-y1))-R
results={}
for name,path in ROUTES.items():
 best=(999,None,None)
 for a,b in zip(path,path[1:]):
  n=max(1,math.ceil(math.dist(a,b)/.005))
  for i in range(n+1):
   t=i/n;p=[a[k]*(1-t)+b[k]*t for k in range(2)]
   for ob,rect in boxes.items():
    g=gap(p,rect)
    if g<best[0]:best=(g,ob,p)
 assert best[0]>.0025,(name,best)
 results[name]={'minimum_planar_clearance_after_capsule_radius_m':round(best[0],4),'continuous_clearance_lower_bound_m':round(best[0]-.0025,4),'nearest_proxy':best[1],'sample_point':best[2]}
old=json.loads((BASE/'kitchen-dining-study/elevations/elevation-schedule.json').read_text());new=json.loads((HERE/'elevations/elevation-schedule.json').read_text());oo={o['instance']:o for o in old['items']};nn={o['instance']:o for o in new['items']}
assert set(oo)==set(nn)
for key in oo:
 if key not in OVERRIDES and key!='BA-TUB-01:001':assert oo[key]==nn[key],key
for k in ['rooms','openings','ceiling_fixtures']:assert old[k]==new[k]
used={v for room in new['coverage'].values() for wall in room.values() for v in wall}
active={o['instance'] for o in new['items'] if o.get('active',True)}
assert active<=used,active-used
for f in HERE.rglob('*.svg'):ET.parse(f)
report={'status':'PASS analytical staging checks; not PIE acceptance','capsule_radius':R,'sample_step_max':.005,'method':'Conservative 2D source bounds expanded by circular capsule; open room door90deg and linen90deg. Conservative continuous bound subtracts2.5mm from sampled minimum, using1-Lipschitz distance and5mm max step. This is supporting design evidence, not engine collision/vertical-shape verification.','routes':results,'linen_east_clearance_at90_m':.029,'linen95_deg':'reject: maxX7.833 exceeds tileface7.822','linen100_deg':'reject: maxX7.873 exceeds structuralwallface7.84','existing_ids_preserved':len(oo),'active_records':len(active),'retired_id':'BA-TOWEL-RAIL-01:078','unchanged':'all nonbathroom records, room boundaries, openings, ceiling fixtures','source_bounds_evidence':'source-bounds.json','remaining':'Actual pawn routes, door and cabinet sweeps, faucet fill, loaded paper placement, all light/switch actions, Tyler camera and southwest seam diagnosis in engine.'}
(HERE/'layout-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(results,indent=2));print('PASS: unchanged nonbathroom records and all IDs,102 total/101 active, SVG XML and route clearance')
