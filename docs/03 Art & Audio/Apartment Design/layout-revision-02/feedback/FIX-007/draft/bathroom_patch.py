"""FIX-007 staging data; imported by build_draft.py, never writes current files."""
from pathlib import Path
import json,math
HERE=Path(__file__).resolve().parent
BASE=HERE.parents[2]
REPO=BASE.parents[3]
ASSETS=REPO/'Art Source/Apartment Redesign/Assets'

PLAN_OBJECTS={
 'Basin':dict(rect=[7.262,7.605,.56,.64],facing='west',assembly_origin_plan=[7.542,7.925,0]),
 'WC':dict(rect=[5.23,5.685,.578,.713],facing='south',assembly_origin_plan=[5.55,6.03,0]),
 'Linen':dict(rect=[7.15,8.671,.60,.679],facing='north',assembly_origin_plan=[7.45,9.05,0],door_open_degrees=90,note='Same southeast-corner floor origin. North-facing; door knob included in planning footprint. Stop at90 degrees to clear east tile.'),
 'Towel basket':dict(rect=[4.8868,8.009,.4664,.342],assembly_origin_plan=[5.12,8.18,0],note='Moved under west towel rail; clears toilet approach.'),
}
OVERRIDES={
 'BA-BASIN-01:002':dict(rect=[7.262,7.605,.56,.64],h=.939,front='west',assembly_origin_plan=[7.542,7.925,0],source_to_plan='(7.542+sourceY,7.925+sourceX,sourceZ)',note='FIX-007: original body/taps rigidly move to former toilet area. Preserve Basin_Tap identity and convert both valve pivots.'),
 'BA-TOILET-01:003':dict(rect=[5.23,5.685,.578,.713],h=.932,front='south',assembly_origin_plan=[5.55,6.03,0],source_to_plan='(5.55+sourceX,6.03-sourceY,sourceZ)',note='FIX-007: north wall west of door; source cistern rear7mm in front of tile. Retain lid pivot and68-degree source open pose.'),
 'BA-LINEN-01:004':dict(rect=[7.15,8.671,.60,.679],front='north',assembly_origin_plan=[7.45,9.05,0],source_to_plan='(7.45-sourceX,9.05+sourceY,sourceZ)',door_open_degrees=90,note='FIX-007: same southeast corner, now facing north.90-degree sweep maxX7.793 clears east tileface7.822 by29mm;95/100 collide. Preserve both hinged labels; real open/close PIE diagnosis required.'),
 'BA-BASKET-01:008':dict(rect=[4.8868,8.009,.4664,.342],h=.2442,assembly_origin_plan=[5.12,8.18,0],note='FIX-007: west floor beneath retained bath rail, clear of north toilet/door route.'),
 'BA-MIRROR-01:076':dict(rect=[7.613,7.418,.245,1.014],z=1.176,h=.868,front='west',show='E',assembly_origin_plan=[7.84,7.925,0],source_to_plan='(7.84+sourceY,7.925+sourceX,sourceZ)',mirror_glass_width=.578,note='FIX-007: mirror+both sconces+globes move as one source assembly, preserving light labels. Datum is floor-height wall, not mirror bottom; globe pair1.014m wide.'),
 'ARC-WALL-SHELF-01:077':dict(rect=[7.69,6.775,.15,.65],z=1.25,h=.145,front='west',show='E',assembly_origin_plan=[7.84,7.10,1.25],geometry_z_bounds=[1.105,1.25],note='FIX-007: lowered east toiletries shelf beside basin; source origin is shelf top. New hand-towel ring hangs below center, between corbels.'),
 'BA-TOWEL-RAIL-01:078':dict(active=False,show='',state='retired intentionally',note='FIX-007: duplicate bath rail and its extra towel removed. Retain identity as retired record; do not place. One full rail remains at :084, ring replaces hook :082.'),
 'BA-SWITCH-01:079':dict(rect=[7.55,5.66,.10,.035],z=1.18,h=.12,front='south',show='N',assembly_origin_plan=[7.60,5.66,1.24],note='FIX-007: right/east of bathroom door, centered between casing edge7.36 and cornerface7.84. Preserve light interaction and toggle pivot.'),
 'ARC-WALL-SHELF-01:080':dict(rect=[7.69,6.025,.15,.65],z=1.25,h=.145,front='west',show='E',assembly_origin_plan=[7.84,6.35,1.25],geometry_z_bounds=[1.105,1.25],note='FIX-007: second lowered toiletries shelf now beside basin on east wall, north of :077; all source props follow rigidly.'),
 'BA-HOOK-01:082':dict(asset='BA-HAND-TOWEL-RING-02',kind='towelring',name='Hand-towel ring / folded cloth',rect=[7.73,6.97,.11,.26],z=.61,h=.575,front='west',show='E',children=[],assembly_origin_plan=[7.84,7.10,1.15],source_to_plan='(7.84+sourceY,7.10+sourceX,1.15+sourceZ)',source_exports=['Art Source/Apartment Redesign/Assets/BA-HAND-TOWEL-RING-02/model/BA_Ring02_Hardware.fbx','Art Source/Apartment Redesign/Assets/BA-HAND-TOWEL-RING-02/model/BA_Ring02_Towel.fbx'],note='FIX-007: actual circular brass ring and folded towel replace old hook/towel. Wall plate center1.15, ring directly below shelf :077; no cabinet-door sweep overlap.'),
 'BA-ROLL-01:083':dict(rect=[4.878,6.04,.118,.18],z=.631,h=.122,front='east',show='W',assembly_origin_plan=[4.878,6.13,.72],source_to_plan='(4.878-sourceY,6.13-sourceX,.72+sourceZ)',paper_source_pivot=[0,-.071,-.014],paper_plan_pivot=[4.949,6.13,.706],note='FIX-007: west wall within toilet reach. Reuse both holder AND actual BA_Roll_Paper; shared assembly transform retains paper pivot, roll axis along wall. Matte two-sided paper material required.'),
 'BA-TOWEL-RAIL-01:084':dict(rect=[4.86,7.36,.1492,1.13],z=.584,h=.706,front='east',show='W',assembly_origin_plan=[4.86,7.925,1.25],source_to_plan='(4.86-sourceY,7.925-sourceX,1.25+sourceZ)',children=['BA_Towel_Ivory.fbx'],note='FIX-007: one source-size1.13m rail, bar1.25. Retain ivory towel at original source offset; remove rose towel and duplicate rail :078. Ends before high-tile step8.50..8.55.'),
 'ARC-WALL-SHELF-01:085':dict(rect=[4.86,6.625,.15,.65],z=1.25,h=.145,front='east',show='W',assembly_origin_plan=[4.86,6.95,1.25],geometry_z_bounds=[1.105,1.25],note='FIX-007: folded towel/tin shelf lowered on west wall, north of bath rail; retain props.'),
}
# Source field has100mm tile pitch,18mm tile depth,50mm cap height.
TILES={'general_field_top':1.00,'general_cap_top':1.05,'ceiling':2.75,'pitch':.10,'tile_depth':.018,'cap_depth':.036,'high_transition_y':8.55,'vertical_transition_trim_y':[8.50,8.55],
 'panels':[
 {'wall':'N','plane':5.66,'span':[4.86,6.25],'z':[0,1.00],'front':'south'},
 {'wall':'N','plane':5.66,'span':[7.30,7.84],'z':[0,1.00],'front':'south'},
 {'wall':'W','plane':4.86,'span':[5.66,8.55],'z':[0,1.00],'front':'east'},
 {'wall':'E','plane':7.84,'span':[5.66,8.55],'z':[0,1.00],'front':'west'},
 {'wall':'W','plane':4.86,'span':[8.55,9.49],'z':[0,2.75],'front':'east'},
 {'wall':'E','plane':7.84,'span':[8.55,9.49],'z':[0,2.75],'front':'west'},
 {'wall':'S','plane':9.49,'span':[4.86,7.84],'z':[0,1.50],'front':'north'},
 {'wall':'S','plane':9.49,'span':[4.86,5.25],'z':[1.50,2.30],'front':'north'},
 {'wall':'S','plane':9.49,'span':[6.40,7.84],'z':[1.50,2.30],'front':'north'},
 {'wall':'S','plane':9.49,'span':[4.86,7.84],'z':[2.30,2.75],'front':'north'}],
 'notes':['Crop tile cells at boundaries; preserve100mm pitch and per-tileUVs rather than nonuniformly stretching1.10m source module. General field removes one100mmrow; original50mmcap reused at1.00.','Full-height field has no cap at1.00/1.50; terminate neatly at ceiling/crown. Vertical bullnose transition occupiesY8.50..8.55, Z1.00..2.75.','South window apertureX5.25..6.40,Z1.50..2.30 is preserved. Do not tile across glass or frame opening.','Keep continuous grout rows inZ,18mm wall projection; cap projects36mm. Clip mitres/perpendicular edges to avoid visible overlaps.','SW seam: ensure structural west/south wall volumes overlap at X4.74..4.86,Y9.49..9.61; tile facing intersects cleanly, no open slit. Diagnose geometry vs lighting in engine before adding any blocker.']}
ROUTES={'entry':[[6.775,5.35],[6.775,6.90],[6.775,7.10]],'toilet':[[6.775,7.10],[5.55,7.10],[5.55,6.90]],'basin':[[6.775,7.10],[6.80,7.925]],'tub':[[6.775,7.10],[5.80,7.10],[5.80,8.20]],'cabinet':[[6.775,7.10],[6.85,8.35]]}

def apply_plan(plan):
 for o in plan['objects']:
  if o['room']=='BA' and o['name'] in PLAN_OBJECTS:o.update(PLAN_OBJECTS[o['name']])
 plan['circulation_paths']+=list(ROUTES.values())
 plan['bathroom_feedback']={'id':'FIX-007','status':'draft pending source/context and engine validation','tile_treatment':TILES,'capsule_radius':.38,'local_routes':ROUTES,'note':'No shell layout/opening changes; source-sized fixtures moved; linen remains same southeast corner.'}
 return plan

def apply_items(items):
 for o in items:
  if o['instance'] in OVERRIDES:o.update(OVERRIDES[o['instance']])
  if o['instance']=='BA-TUB-01:001':
   o['note']='FIX-007: tub, curtain/water and Tyler overlay stay. Old combined fixture split: stationary rod retains old transform; plumbing moves to west end. Preserve tap action IDs and transform axes/pivots.'
   o['children']=['BA-TUB-WATER-01','BA-TUB-FIXTURES-02','taps','curtain'];o['plumbing_plan_origin']=[5.293,8.32,0]
 return items

def contract():
 return {'fix':'FIX-007','status':'draft; source fit and engine review pending','plan_objects':PLAN_OBJECTS,'schedule_overrides':OVERRIDES,'tile_treatment':TILES,'capsule_radius':.38,'routes':ROUTES,'plumbing':{'asset':'BA-TUB-FIXTURES-02','source_origin_plan':[5.293,8.32,0],'source_to_plan':'(5.293-sourceY,8.32-sourceX,sourceZ)','left_tap_pivot_plan':[5.003,9.16,.96],'right_tap_pivot_plan':[5.003,8.98,.96],'valve_source_axis':'Y','valve_plan_axis':'-X','fill_effect_start':[5.113,9.07,.73],'fill_effect_end':[5.113,9.07,.44],'stationary_rod':'Exact old BA_TubFixtures transform; do not rotate with plumbing.','retire':'Old combined BA_TubFixtures replaced by new plumbing + stationary rod only. Keep original tub/taps/curtain source files.'},'intentional_retirements':['Duplicate rail :078 plus its ivory towel','Rose towel on retained bath rail :084','Old hook and hook-hung towel :082 replaced by real ring+folded cloth','Old combined BA_TubFixtures once both split groups are placed'], 'preserve':['all original schedule keys','Basin_Tap','Tub_Faucet','Shower_Curtain','all bath light and cabinet interaction labels','Tyler identity/repair overlay','original bath window and door rough openings','same southeast linen floor origin']}
if __name__=='__main__':(HERE/'placement-contract.json').write_text(json.dumps(contract(),indent=2)+'\n')
