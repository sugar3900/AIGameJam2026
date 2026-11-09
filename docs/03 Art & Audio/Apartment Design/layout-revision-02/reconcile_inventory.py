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
'KI-SINK-01':('replace','Full sink assembly omitted; approved narrow KI-SINK-NARROW-01 preserves leak/repair.'),
'LV-CHEST-01':('omit','Old living south-wall chest has no assigned place in open living/hall arrangement. Do not obstruct kitchen/dining circulation to force it in; retain source for future use.'),
'LV-PLANT-STAND-01':('reuse','Relocate from old hall to support living plant at plan(11.05,0.50); stand top0.480, riser0.036, plant origin0.516. Fit .451x.351 footprint around same center.'),
'KI-CABINET-01':('replace','Three base frontages replaced by source-style KI-CABINET-02 variants .425/.775/.450m; preserve sage profiles/hardware scale.'),
'BR-CLOSET-01':('replace','Old undersized shell replaced by fitted BR-CLOSET-02 interior/door kit and new shell. Reuse mold texture, bulb and trim style; preserve Malcolm.'),
'ARC-SLIDING-CLOSET-01':('modify','Front kits/rails fitted to new entry coat and guest wardrobe, back-to-back shared wall; no duplicate shells.'),
'BR-WAINSCOT-01':('modify','Relocate white panels and lead paint to office. Fit widths around door, closet return and window; bedroom uses plaster.'),
'KI-WALL-TABLE-02':('new','Small south-wall table .90x.45x.74; source-style fitted piece.'),
'KI-STOOL-02':('new','Matching stool .30x.30x.45 tucked below wall table.'),
'ARC-CLOSET-STORAGE-02':('new','Separate coat/guest shelf, hanging rail and empty hangers; twice, mounted at shared back wall. No front panels included.'),
'ARC-DOOR-02':('new','Fitted .99clear/1.05rough room door, retained five-panel style and hardware.'),
'ARC-ENTRY-DOOR-02':('new','Fitted .99clear/1.05rough walnut entrance leaf and ivory frame.'),
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
md+=['','## Remaining validation','','- Integration team must reconcile live actor instances, including repeated lamps, chairs, shelves, framed art, rugs and children of moving assemblies.','- Preserve all repair, reveal and click actions; no implicit deletion of gameplay-linked assets.','- Only the full sink, undersized closet/cabinets and unplaced chest are explicitly replaced or omitted. The kitchen radiator placement is omitted; the same radiator asset remains in living.','- New fitted variants require inspected renders and FBX round-trip validation before import.','- All original source assets remain on disk. No existing export was deleted or overwritten.']
(ROOT/'Inventory reconciliation.md').write_text('\n'.join(md)+'\n')
assert not report['unresolved'],report['unresolved']
print('Reconciled',len(rows),'existing/planned asset IDs; no unresolved source folders.')
