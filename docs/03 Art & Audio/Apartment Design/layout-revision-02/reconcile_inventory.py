"""Reconcile source-folder assets against approved design; no export-readiness claim."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[3]
ASSETS=REPO/'Art Source/Apartment Redesign/Assets'
S=ROOT/'kitchen-dining-study/elevations'
d=json.loads((S/'elevation-schedule.json').read_text())
uses={}
for o in d['items']:
 for aid in [o['asset']]+o['children']:
  uses.setdefault(aid,[]).append(o['name']+' ('+'/'.join(o['rooms'])+')')
for o in d['ceiling_fixtures']:uses.setdefault(o['asset'],[]).append('Ceiling '+o['room'])
for aid in re.findall(r'^\| ([A-Z][A-Z0-9-]+) \|', (S/'Asset schedule.md').read_text(),re.M):uses.setdefault(aid,[]).append('Finish / surface schedule')
explicit={
'KI-CHAIR-01':('replace','FIX-018 parent-approved KI-CHAIR-02 replaces dining-chair source; retain original files and follow new assembly contract.'),
'OF-WAINSCOT-02':('source ready; engine pending','FIX-019: six fitted common-origin office runs, max22mm projection, fixed profiles, casing/mitre/sill fits. All at(796,566,0)cm/yaw0; keep old lead overlay at planeY5.668. Verify60mm shell quadrant from README.'),
'ARC-ENTRY-DOOR-03':('source ready; engine pending','FIX-010 approved fitted entry hardware/frame correction; preserve existing02 actor transforms and exit action; original source kits retained.'),
'LV-ARMCHAIR-02':('source ready; engine pending','FIX-013 approved replacement for LV-CHAIR-01; preserve actor transform and original envelope, use validated fifteen UCX hulls.'),
'LV-PLANT-02':('source ready; engine pending','FIX-014 approved rim-safe pothos; replace plant only, retain stand/riser and actor placement; exact material mapping in manifest.json.'),
'HA-SLIPPERS-01':('source ready; engine pending','FIX-016 approved single pair, proposed(1170,362,0)cm/yaw90; replaces four shoes and tray, preserving bench/entry. Verify actual engine sweeps.'),
'KI-CHAIR-02':('source ready; engine pending','FIX-018 parent-approved dining-chair replacement, all21 release-manifest hashes independently verified; preserve existing placement and follow source assembly/material contract.'),
'LV-CHAIR-01':('replace','FIX-013 source-reviewed LV-ARMCHAIR-02 replaces this chair at unchanged actor transform/envelope.'),
'LV-PLANT-01':('replace','FIX-014 source-reviewed LV-PLANT-02 replaces plant geometry; stand/riser and placement remain.'),
'HA-SHOES-01':('replace','FIX-016 source-reviewed HA-SLIPPERS-01 replaces four shoes plus tray; preserve hall bench and entry.'),
'HA-RUNNER-01':('replace','FIX-020 source-reviewed HA-RUNNER-02 shortens runner and adds soft binding/fringe; exact placement in new assembly.json.'),
'HA-SCONCE-01':('replace','FIX-008 source-reviewed HA-SCONCE-02 replaces hardware/shade/bulb at unchanged origins; preserve light toggle labels.'),
'HA-RUNNER-02':('source ready; engine pending','FIX-020: approved5m runner, floor origin(5.234,4.70,.00118546), yaw0, fringeX2.668..7.80; source assembly.json is authoritative.'),
'HA-SCONCE-02':('source ready; engine pending','FIX-008: corrected closed opal shade and connected hardware; replace original three parts at unchanged wall-plate origins, preserve all light toggles. Read refreshed manifest before import.'),
'BA-HAND-TOWEL-RING-02':('new','FIX-007: real ring and folded hand towel replace old hook assembly at stable :082; plate origin(7.84,7.10,1.15), west-facing. Source roundtrip and17mm tile-cap clearance verified.'),
'BA-TUB-FIXTURES-02':('new','FIX-007: original combined fixture split into west-end plumbing and stationary curtain rod; preserve original tub/taps/curtain and bath-water sources.'),
'BA-HOOK-01':('omit','FIX-007: old bathroom hook replaced by BA-HAND-TOWEL-RING-02 at stable :082; original source retained.'),
'BA-HAND-TOWEL-01':('omit','FIX-007: old hook-hung cloth replaced by folded ring towel; original source retained.'),
'BA-TOWEL-RAIL-01':('partial reuse','FIX-007: retain1.13m rail :084 with ivory cloth west of bath; retire duplicate :078 and rose cloth.'),
'ART-REV02-COLLECTION':('reference','FIX-006 collection catalog; each physical frame is tracked by its dedicated ART-REV02 source folder and wall-art inventory. Source approval remains separate.'),
'ARC-BEDROOM-PLASTER-01':('reuse','Bedroom and office upper plaster; fitted shell uses existing surface, not old cut walls.'),
'ARC-KITCHEN-PLASTER-01':('reuse','Kitchen plaster; new north window and east portal cuts.'),
'ARC-LIVING-WALL-01':('modify','Reuse living/hall plaster appearance; rebuild shell partitions/openings, do not import old fixed wall-window assembly.'),
'ARC-DOOR-01':('modify','Room frames and leaves fitted to approved openings; rough width clear+0.06m, head2.14m.'),
'ARC-ENTRY-DOOR-01':('modify','East entry y4.00..5.05; fit frame/leaf width to new opening, retain outward swing.'),
'ARC-WINDOW-01':('modify','Living north1.60m window; kitchen replaced by new ARC-WINDOW-KITCHEN-02 counter-height kit.'),
'ARC-WINDOW-NARROW-01':('reuse','Bedroom south opening x3.30..4.40, sill0.90/head2.30; move with opening.'),
'ARC-WINDOW-BATH-01':('reuse','Bathroom south frosted window; follow approved aperture.'),
'ARC-WINDOW-OFFICE-01':('reuse','Office south window; terminate relocated panel rail/apron around opening.'),
'ENV-SKY-01':('reuse','Exterior painted sky and skyline retained; rotate to golden sun/window direction.'),
'KI-FRIDGE-01':('reuse','Imported geometry already has west/-X hinge. Correct old click-action pivot to actual hinge;105-degree sweep beside north prep.'),
'KI-SINK-NARROW-01':('partial replace','FIX-003: KI-LEAK-02 replaces body with old embedded bucket removed. Retain original L/R taps and Sink_Tap action; retire old damage beads/puddle.'),
'KI-BUCKET-01':('omit','Old sink child reference superseded by separate KI-LEAK-02 vintage pail; preserve unrelated copies only if explicitly reconciled.'),
'BR-MOLD-02':('new','FIX-001: two charcoal corner overlays share closet floor origin; both hide on Malcolm repair.'),
'BR-CLOSET-STORAGE-03':('new','FIX-002: bilateral full-length side shelves/rails/hangers; common floor origin, shelf tops1.88m.'),
'KI-LEAK-02':('new','FIX-003: clean sink body, persistent galvanized pail, optional water/puddle and dynamic-drop handoff. Preserve tap/state identities.'),
'KI-SINK-01':('replace','Full sink assembly omitted; approved narrow KI-SINK-NARROW-01 preserves leak/repair.'),
'LV-SOFA-02':('source ready; engine pending','FIX-005 approved replacement sofa; preserve current footprint/facing and consult source manifest for materials/collision.'),
'LV-CHEST-01':('omit','Old living south-wall chest has no assigned place in open living/hall arrangement. Do not obstruct kitchen/dining circulation to force it in; retain source for future use.'),
'LV-PLANT-STAND-01':('reuse','Relocate from old hall to support living plant at plan(11.05,0.50); stand top0.480, riser0.036, plant origin0.516. Fit .451x.351 footprint around same center.'),
'KI-CABINET-01':('replace','Three base frontages replaced by source-style KI-CABINET-02 variants .425/.775/.450m; preserve sage profiles/hardware scale.'),
'BR-CLOSET-01':('replace','Old undersized shell replaced by fitted BR-CLOSET-02 interior/door kit and new shell. Retain bulb/trim style; superseded mold and short shelf replaced by BR-MOLD-02 and BR-CLOSET-STORAGE-03; preserve Malcolm.'),
'ARC-SLIDING-CLOSET-01':('modify','Front kits/rails fitted to new entry coat and guest wardrobe, back-to-back shared wall; no duplicate shells.'),
'BR-WAINSCOT-01':('partial reuse','FIX-019 replaces module runs with OF-WAINSCOT-02. Retain original lead-paint mesh/material/identity/scale; move its visible plane toY5.668 at centreX8.925,Z.70.'),
'KI-WALL-TABLE-02':('new','Small south-wall table .90x.45x.74; source-style fitted piece.'),
'KI-STOOL-02':('new','Matching stool .30x.30x.45 tucked below wall table.'),
'ARC-CLOSET-STORAGE-02':('new','Separate coat/guest shelf, hanging rail and empty hangers; twice, mounted at shared back wall. No front panels included.'),
'ARC-DOOR-02':('new','Fitted .99clear/1.05rough room door, retained five-panel style and hardware.'),
'ARC-ENTRY-DOOR-02':('replace','FIX-010 ARC-ENTRY-DOOR-03 preserves this fitted opening/envelope and placement while correcting hardware and casing joints.'),
'KI-FRIDGE-02':('omit','Unused opposite-hinge variant: imported +X is east. Original KI-FRIDGE-01 is correct; false report traced to old gameplay pivot.'),
'KI-CABINET-02':('new','Three fitted cabinet widths; parent review/FBX validation before import.'),
'BR-CLOSET-02':('new','Hall-end closet doors/interior kit; shell assembled separately.'),
'ARC-WINDOW-KITCHEN-02':('new','Counter-height1.60x1.15 opening, sill1.25/head2.40; apron bottom>=1.18.'),
'ARC-SLIDING-CLOSET-02':('new','Rebuilt .90m-clear bypass front for shared coat/guest closets; cabinet depth remains shell-controlled.'),
}
rows=[]
for folder in sorted(ASSETS.iterdir()):
 if not folder.is_dir():continue
 aid=folder.name
 if aid in explicit:action,note=explicit[aid]
 elif aid.startswith('ART-REV02-'):action,note='source ready; engine pending','FIX-006 all17 images/frames released and approved; exact mapping in feedback/FIX-006/wall-art-inventory.json and verified collection file-manifest.json. Preserve original physical instance IDs.'
 elif aid in uses:action,note='reuse','; '.join(dict.fromkeys(uses[aid]))
 else:action,note='UNRESOLVED','No approved placement or disposition recorded.'
 rows.append(dict(asset=aid,action=action,destination=note,source_fbx=[str(f.relative_to(folder)) for f in folder.rglob('*.fbx')],source_readme=(folder/'README.md').exists()))
for aid in ('KI-WALL-TABLE-02','KI-STOOL-02','KI-CABINET-02','BR-CLOSET-02','ARC-WINDOW-KITCHEN-02','ARC-SLIDING-CLOSET-02','ARC-CLOSET-STORAGE-02'):
 if not any(r['asset']==aid for r in rows):
  action,note=explicit[aid];rows.append(dict(asset=aid,action=action,destination=note,source_fbx=[],source_readme=False))
report={'date':'2026-11-09','scope':'Source folders and approved drawing schedule; engine instance reconciliation remains separate. FBX presence is not visual approval.','rows':rows,'unresolved':[r['asset'] for r in rows if r['action']=='UNRESOLVED']}
(ROOT/'inventory-reconciliation.json').write_text(json.dumps(report,indent=2)+'\n')
md=['# Approved-layout inventory reconciliation','','Snapshot: 2026-11-09. Every existing source folder receives a placement or disposition. This is a design/source audit; it does not prove that every current engine actor has been migrated. FBX presence is not review approval.','','| Asset | Decision | Destination / required work |','|---|---|---|']
for r in rows:md.append(f"| {r['asset']} | {r['action']} | {r['destination']} |")
md+=['','## Remaining validation','','- Integration team must reconcile live actor instances, including repeated lamps, chairs, shelves, framed art, rugs and children of moving assemblies.','- Preserve all repair, reveal and click actions; no implicit deletion of gameplay-linked assets.','- Explicit replacements and omissions are listed per asset above. FIX-007 also retires the old hook/hand towel, duplicate bath rail, rose bath towel and combined tub fixture; original source folders remain. The kitchen radiator placement is omitted; the same radiator asset remains in living.','- New fitted variants require inspected renders and FBX round-trip validation before import.','- All original source assets remain on disk. No existing export was deleted or overwritten.']
(ROOT/'Inventory reconciliation.md').write_text('\n'.join(md)+'\n')
assert not report['unresolved'],report['unresolved']
print('Reconciled',len(rows),'existing/planned asset IDs; no unresolved source folders.')
