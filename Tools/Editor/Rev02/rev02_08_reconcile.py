"""Rev02 step 8 (verification): reconcile L_Apartment_Rev02 against every instance and child of the revision 02
elevation schedule, and list every imported-art actor the schedule does not account for.

For each scheduled instance: the actor(s) that realise it, their measured placement against the scheduled rect
(xy centre; bottom height for wall-mounted items), and each child as an actor or an intentional omission with its
reason. Writes docs/03 Art & Audio/Apartment Design/Rev02 engine reconciliation.md. Read-only on the map.
"""
import json, os, unreal
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
SCHED = os.path.join(ROOT, 'docs/03 Art & Audio/Apartment Design/layout-revision-02/kitchen-dining-study/elevations/elevation-schedule.json')
OUT = os.path.join(ROOT, 'docs/03 Art & Audio/Apartment Design/Rev02 engine reconciliation.md')
MAP = '/Game/ICanFixHim/Maps/L_Apartment_Rev02'
A = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert L.load_level(MAP)
acts = {a.get_actor_label(): a for a in A.get_all_level_actors()}
sched = json.load(open(SCHED))['items']

NO_ASSET = 'omitted: no source prop asset for this generic child'
SPARSE = ('intentional sparse dressing: LV-BOOK-01 book parts are placed on the bedroom bookcase and shelf :063; '
          'omitted from this placement to keep the composition uncluttered')
# instance -> (anchor labels, {child: labels | 'omitted: reason'})
M = {
 'BA-TUB-01:001': (['Art_BA_Tub_BA_Tub'], {'BA-TUB-WATER-01': ['Tub_Faucet'], 'taps': ['Art_BA_Tub_BA_TapLeft', 'Art_BA_Tub_BA_TapRight'],
                   'shower riser': ['Art_BA_TubFixture02_Plumbing'], 'curtain': ['Art_BA_Tub_BA_BA_Curtain', 'Shower_Curtain', 'Art_BA_Curtain03_FixedReturn'],
                   'BA-TUB-FIXTURES-02': ['Art_BA_TubFixture02_Plumbing', 'Art_BA_TubFixture02_CurtainRod', 'Art_BA_TubFixture02_Drain']}),
 'BA-BASIN-01:002': (['Art_BA_Basin_BA_BasinBody'], {'taps': ['Art_BA_Basin_BA_BA_BasinTap_L', 'Art_BA_Basin_BA_BA_BasinTap_R', 'Basin_Tap']}),
 'BA-TOILET-01:003': (['Art_BA_Toilet_BA_ToiletBody'], {}),
 'BA-LINEN-01:004': (['Art_BA_Linen_BA_Linen_Body'], {}),
 'OF-DAYBED-01:005': (['Art_OF_Daybed_23'], {'pillows': 'part of the OF-DAYBED-01 mesh', 'quilt': 'part of the OF-DAYBED-01 mesh'}),
 'OF-DESK-01:006': (['Art_OF_Desk_OF_DESK_BODY'], {'OF-DESK-LAMP-01': ['Art_OF_DeskLamp_OF_DeskLamp_Body', 'DeskLamp'],
                    'OF-PAPERS-01': ['Art_OF_Papers_OF_PAPERS_01'], 'book': SPARSE}),
 'OF-CHAIR-01:007': (['Art_OF_Chair_OF_CHAIR_01'], {}),
 'BA-BASKET-01:008': (['Art_BA_Basket_BA_Basket'], {'rolled towels': ['Art_BA_Basket_BA_Towel_0', 'Art_BA_Basket_BA_Towel_1', 'Art_BA_Basket_BA_Towel_2']}),
 'BA-BIN-01:009': (['Art_BA_Bin_Bin_body'], {}),
 'LV-LAMP-01:010': (['Art_OF_FloorLamp_LV_LampBody'], {}),
 'OF-CABINET-01:011': (['Art_OF_Cabinet_OF_CABINET_BODY'], {'box': 'omitted: would sit inside the closed cabinet, never visible'}),
 'HA-BENCH-01:012': (['Art_HA_Bench_HA_BENCH_01'], {'HA-SHOES-01': ['Art_HA_Slippers01'] if 'Art_HA_Slippers01' in acts else ['Art_HA_Shoes_HA_ShoeTray', 'Art_HA_Shoes_HA_Oxford_1', 'Art_HA_Shoes_HA_Oxford_2', 'Art_HA_Shoes_HA_SlipOn_1', 'Art_HA_Shoes_HA_SlipOn_2'],
                                                 'HA-SLIPPERS-01': ['Art_HA_Slippers01'] if 'Art_HA_Slippers01' in acts else 'pending FIX-016 import'}),
 'HA-CABINET-01:013': (['Art_HA_EndCabinet_HA_CABINET_BODY'], {'HA-VASE-02': ['Art_HA_Vase02_HA_VASE_02']}),
 'HA-CONSOLE-01:014': (['Art_HA_Console_HA_CONSOLE_BODY'], {'HA-VASE-01': ['Art_HA_Vase'], 'HA-FLOWERS-01': ['Art_HA_Flowers']}),
 'OF-BOOKCASE-01:015': (['Art_OF_Bookcase_OF_BOOKCASE_BODY'], {'books': [l for l in acts if l.startswith(('Art_Book_OFLow_', 'Art_Book_OFHigh_', 'Art_Book03_OFLow_', 'Art_Book03_OFHigh_'))],
                        'plant': ['Art_LV_Book_LV_BOOK_PLANT_OFTop'], 'storage box': ['Art_BR_ClosetBox_BR_BOX_BODY_OFTop']}),
 'BR-BED-01:016': (['Art_BR_Bed'], {'pillows': 'part of the BR-BED-01 mesh', 'floral quilt': 'part of the BR-BED-01 mesh'}),
 'BR-NIGHTSTAND-01:017': (['Art_BR_Nightstand_W_BR_NIGHTSTAND_BODY'], {'BR-LAMP-01': ['Art_BR_Lamp_W_BR_LampBody', 'BedLamp']}),
 'BR-NIGHTSTAND-01:018': (['Art_BR_Nightstand_E_BR_NIGHTSTAND_BODY'], {'BR-LAMP-01': ['Art_BR_Lamp_E_BR_LampBody', 'BedLamp_E']}),
 'BR-DRESSER-01:019': (['Art_BR_Dresser_BR_Dresser_body'], {'BR-PERFUME-01': ['Art_BR_Perfume_BR_Perfume_Body'], 'tray': NO_ASSET}),
 'LV-SOFA-01:020': (['Art_LV_Sofa'], {'cushions': 'part of the LV-SOFA-01 mesh', 'floral throw': 'part of the LV-SOFA-01 mesh'}),
 'LV-COFFEE-01:021': (['Art_LV_Coffee_04'], {'books': SPARSE, 'KI-MUG-01': ['Art_KI_Mug_KI_Mug_01_Coffee']}),
 'LV-TV-01:022': (['Art_LV_TV02_Housing', 'TV'] if 'Art_LV_TV02_Housing' in acts else ['Art_LV_TV_LV_TV_body', 'TV'], {}),
 # FIX-031/032: the kept stand (rev02_05g relabels the old combined body) with its two bound cabinet doors
 'LV-TV-STAND-01:103': (['Art_LV_TV02_Stand'], {'TVCabinet_Door_L': ['TVCabinet_Door_L'], 'TVCabinet_Door_R': ['TVCabinet_Door_R']}),
 'LV-CHAIR-01:023': (['Art_LV_Chair_03'], {}),
 'LV-BOOK-01:024': (['Art_LV_Book_LV_BOOK_CASE'], {'shelf books': ['Art_LV_Book_LV_BOOK_BOOKS'], 'plant': ['Art_LV_Book_LV_BOOK_PLANT'], 'tin': ['Art_LV_Book_LV_BOOK_TIN']}),
 'LV-SIDE-TABLE-01:025': (['Art_LV_SideTable_LV_SIDE_TABLE_BODY'], {'LV-TABLE-LAMP-01': ['Art_LV_TableLamp_LV_TableLampBody', 'FloorLamp']}),
 'LV-PLANT-01:026': (['Art_HA_Plant'], {'LV-PLANT-STAND-01': ['Art_HA_PlantStand_LV_Plant_Stand', 'Art_HA_PlantStand_Riser']}),
 'LV-RADIATOR-01:027': (['Art_LV_Radiator'], {}),
 'KI-CABINET-02:028': (['Art_KI_Cab0425_body'], {'KI-JAR-01': ['Art_KI_Jar_KI_Jar_Body']}),
 'KI-SINK-NARROW-01:029': (['Art_KI_SinkNarrow_body', 'Malady_Sink'], {'faucet': 'part of the KI_LEAK_02_sink_body mesh'}),
 # FIX-003 additions (KI-LEAK-02): the pail and its still water stay after repair; the spill decal is Lukey's damage.
 'KI-LEAK-02:100': (['Art_KI_Leak_Bucket'], {}),
 'KI-LEAK-02:101': (['Art_KI_Leak_BucketWater'], {}),
 'KI-LEAK-02:102': (['Art_KI_SINK_damage'], {}),                      # + Art_KI_SINK_damage_Wet (sheen layer, same mask)
 'KI-CABINET-02:030': (['Art_KI_Cab0775_body'], {'KI-BOWL-01': ['Art_KI_Bowl_KI_Bowl_Counter']}),
 'KI-RANGE-01:031': (['Art_KI_Range_Body'], {'KI-KETTLE-01': ['Art_KI_Kettle_KI_Kettle_Body'], 'KI-RANGE-FLAME-01': ['Stove_Burner'],
                     'KI-PAN-01': 'omitted on the range: both pan props hang on the scheduled pan rail (KI-PAN-RAIL-01:085)'}),
 'KI-CABINET-02:032': (['Art_KI_Cab0450_body'], {'KI-MUG-01': ['Art_KI_Mug_KI_Mug_01_Prep'], 'KI-POTTERY-01': ['Art_KI_Pottery_KI_Pottery_01']}),
 'KI-FRIDGE-01:033': (['Art_KI_Fridge_Body'], {}),
 'KI-PANTRY-01:034': (['Art_KI_Pantry_Body'], {}),
 'KI-WALL-TABLE-02:035': (['Art_KI_WallTable02'], {}),
 'KI-STOOL-02:036': (['Art_KI_Stool02'], {}),
 'KI-TABLE-01:037': (['Art_KI_Table_12'], {'KI-BOWL-01': ['Art_KI_Bowl_KI_Bowl', 'Art_KI_Bowl_Apple_A', 'Art_KI_Bowl_Pear']}),
 'KI-CHAIR-01:038': (['Art_KI_Chair_13'], {}),
 'KI-CHAIR-01:039': (['Art_KI_Chair_14'], {}),
 'LV-ART-04:040': (['Art_LV_Art04_LV_ART_04'], {}),
 'HA-ART-02:041': (['Art_HA_Art02_Entry'], {}),
 'HA-HOOKS-01:042': (['Art_HA_Hooks_HA_Hooks'], {'HA-COAT-01': ['Art_HA_Coat_HA_Coat']}),
 'LV-FUSE-01:043': (['Art_LV_Fuse_Shell', 'FuseBox_Door', 'Malady_FuseBox'], {'LV-FUSE-DAMAGE-01': ['Art_LV_Fuse_Plaster_Damage', 'Art_LV_Fuse_Wire_Damaged', 'Art_LV_Fuse_Wire_Repaired']}),
 'HA-SCONCE-01:044': (['Art_HA_Sconce02_HA_Sconce_Hardware', 'Art_HA_Sconce02_HA_Sconce_Shade', 'Art_HA_Sconce02_HA_Sconce_Bulb'], {}),
 'LV-ART-04:045': (['Art_LV_Art04_Bookcase'], {}),
 'ARC-WALL-SHELF-01:046': (['Art_BA_WallShelf_ARC_WALL_SHELF_01_S046'], {'KI-POTTERY-01': ['Art_KI_Pottery_KI_Pottery_01_046'], 'books': SPARSE}),
 'HA-ART-09:056': (['Art_HA_Art09_HA_ART_09'], {}),
 'HA-ART-03:057': (['Art_HA_Art03_HA_ART_03'], {}),
 'HA-ART-02:058': (['Art_HA_Art02_Hall'], {}),
 'HA-SCONCE-01:059': (['Art_HA_Sconce01_HA_Sconce_Hardware', 'Art_HA_Sconce01_HA_Sconce_Shade', 'Art_HA_Sconce01_HA_Sconce_Bulb'], {}),
 'HA-ART-02:060': (['Art_HA_Art02_HA_ART_02'], {}),
 'HA-ART-03:061': (['Art_HA_Art03_Gallery'], {}),
 'BR-ART-FLORAL-01:062': (['Art_BR_ArtFloral_BR_ART_FLORAL_01'], {}),
 'ARC-WALL-SHELF-01:063': (['Art_BA_WallShelf_ARC_WALL_SHELF_01_S063'], {'keepsake': ['Art_LV_Book_LV_BOOK_TIN_063'],
                           'small books': [l for l in acts if l.startswith(('Art_Book_S063_', 'Art_Book03_S063_'))]}),
 'BR-ART-FLORAL-01:064': (['Art_BR_ArtFloral_Bookcase'], {}),
 'ARC-WALL-SHELF-01:065': (['Art_BA_WallShelf_ARC_WALL_SHELF_01_S065'], {'books': SPARSE, 'HA-VASE-01': ['Art_HA_Vase_065']}),
 'BR-ART-FLORAL-01:066': (['Art_BR_ArtFloral_Dresser'], {}),
 'BR-ART-FLORAL-01:067': (['Art_BR_ArtFloral_Headboard'], {}),
 'BA-SWITCH-01:068': (['Art_BA_Switch_BA_Switch_Plate_S068'], {}),
 'BR-WAINSCOT-01:069': (['Damage_BR_LeadPaint'], {}),
 'OF-ART-LANDSCAPE-01:070': (['Art_OF_ArtLandscape_OF_ART_LANDSCAPE_01'], {}),
 'OF-ART-BOTANICAL-01:071': (['Art_OF_ArtBotanical_OF_ART_BOTANICAL_01'], {}),
 'ARC-WALL-SHELF-01:072': (['Art_BA_WallShelf_ARC_WALL_SHELF_01_S072'], {'books': SPARSE, 'KI-PLANT-01': ['Art_KI_Geranium_KI_Geranium']}),
 'OF-ART-BOTANICAL-01:073': (['Art_OF_ArtBotanical_East'], {}),
 'ARC-WALL-SHELF-01:074': (['Art_BA_WallShelf_ARC_WALL_SHELF_01_S074'], {'small pot': ['Art_KI_Pottery_KI_Pottery_01_074'], 'books': SPARSE}),
 'BA-SWITCH-01:075': (['Art_BA_Switch_BA_Switch_Plate_S075'], {}),
 'BA-MIRROR-01:076': (['Art_BA_Mirror_BA_Mirror_mirror'], {'opal globe lights': ['Art_BA_Mirror_BA_Mirror_globe', 'Mirror_Sconces']}),
 'ARC-WALL-SHELF-01:077': (['Art_BA_WallShelf_ARC_WALL_SHELF_01'], {'BA-BOTTLE-01': ['Art_BA_Bottle_BA_Bottle_Body'], 'BA-CUP-01': ['Art_BA_Cup_BA_Cup'], 'BA-SOAP-01': ['Art_BA_Soap_BA_SoapDish']}),
 'BA-TOWEL-RAIL-01:078': (['Art_BA_TowelRail_BA_Towel_Rail_S078'], {'BA-HAND-TOWEL-01': ['Art_BA_TowelRail_BA_Towel_Ivory_S078']}),
 'BA-SWITCH-01:079': (['Art_BA_Switch_BA_Switch_Plate'], {}),
 'ARC-WALL-SHELF-01:080': (['Art_BA_WallShelf_ARC_WALL_SHELF_01_S080'], {'BA-JAR-01': ['Art_BA_Jar_BA_Jar_Body'], 'BA-SOAP-01': ['Art_BA_Soap_BA_SoapDish_080']}),
 'BA-ART-01:081': (['Art_BA_Art01_BA_ART_01'], {}),
 'BA-HOOK-01:082': (['Art_BA_Ring02_Hardware'], {'BA-HAND-TOWEL-01': ['Art_BA_Ring02_Towel']}),        # FIX-007 ring replaces hook
 'BA-ROLL-01:083': (['Art_BA_Roll_BA_Roll_Holder'], {}),
 'BA-TOWEL-RAIL-01:084': (['Art_BA_TowelRail_BA_Towel_Rail'], {'BA-HAND-TOWEL-01': ['Art_BA_TowelRail_BA_Towel_Ivory'],
                                                               'BA_Towel_Ivory.fbx': ['Art_BA_TowelRail_BA_Towel_Ivory']}),
 'ARC-WALL-SHELF-01:085': (['Art_BA_WallShelf_ARC_WALL_SHELF_01_S085'], {'BA-FOLDED-TOWEL-01': ['Art_BA_FoldedTowel_BA_Folded_Towel'], 'BA-TIN-01': ['Art_BA_Tin_BA_Tin_Body']}),
 'BA-TILE-01:086': (['Damage_BA_CrackedTile', 'Malady_PinkTile'], {}),
 'KI-WALL-STAIN-01:078': (['Art_KI_Wall_Stain'], {}),
 'KI-BACKSPLASH-01:079': (['Art_KI_Backsplash02_A'], {}),                      # KI-BACKSPLASH-02 fitted band (batch 2)
 'KI-BACKSPLASH-01:080': (['Art_KI_Backsplash02_B', 'Art_KI_Backsplash02_Range', 'Art_KI_Backsplash02_C'], {}),
 'KI-UPPER-01:081': (['Art_KI_Upper_Body'], {}),
 'KI-ART-01:082': (['Art_KI_Art01_KI_ART_01'], {}),
 'ARC-WALL-SHELF-01:083': (['Art_BA_WallShelf_ARC_WALL_SHELF_01_S083'], {'KI-MUG-01': ['Art_KI_Mug_KI_Mug_01_083'], 'KI-POTTERY-01': ['Art_KI_Pottery_KI_Pottery_01_083']}),
 'HA-SCONCE-01:084': (['Art_HA_Sconce01_HA_Sconce_Hardware_Kitchen', 'Art_HA_Sconce01_HA_Sconce_Shade_Kitchen', 'Art_HA_Sconce01_HA_Sconce_Bulb_Kitchen'], {}),
 'KI-PAN-RAIL-01:085': (['Art_KI_PanRail_KI_Pan_Rail_Assembly'], {'KI-PAN-01': ['Art_KI_PanPair03']}),    # PROP-FIT-03: both pans + engaged S-hooks on the rail body
 'BA-SWITCH-01:086': (['Art_BA_Switch_BA_Switch_Plate_S086'], {}),
 'ARC-SLIDING-CLOSET-01:087': (['Art_OfficeCloset_Frame', 'Art_OfficeCloset_LeftPanel', 'Art_OfficeCloset_RightPanel'], {}),
 'ARC-CLOSET-RETURN:088': ([l for l in acts if l.startswith('ClosetSide_')], {}),
 'BR-CLOSET-01:089': (['Art_BR_Closet_Mold', 'Malady_Mold'], {}),                      # BR-MOLD-02 back plane (FIX-001)
 'BR-MOLD-02:098': (['Art_BR_Closet_Mold_Return'], {}),                                  # BR-MOLD-02 east return
 'BR-CLOSET-01:090': (['Art_BR_ClosetStorage03_West'], {'hooked empty hangers': 'part of the BR_ClosetStorage03_West mesh'}),
 'BR-CLOSET-STORAGE-03:099': (['Art_BR_ClosetStorage03_East'], {'hooked empty hangers': 'part of the BR_ClosetStorage03_East mesh'}),
 'BR-CLOSET-BOX-01:091': (['Art_BR_ClosetBox_BR_BOX_BODY'], {}),
 'BR-CLOSET-01:092': (['Art_BR_ClosetLight01_Hardware', 'Light_Closet'] if 'Light_Closet' in acts else ['Art_BR_Closet02_Bulb', 'Bulb_Closet'], {}),
 'CHAR-MALCOLM:093': ([], {}),
 'ARC-CLOSET-STORAGE-02:094': (['Art_CoatCloset_Storage'], {'hangers': [l for l in acts if l.startswith('Art_HA_Hanger03_Coat_')]}),
 'BR-CLOSET-BOX-01:095': (['Art_BR_ClosetBox_BR_BOX_BODY_S095'], {}),
 'ARC-CLOSET-STORAGE-02:096': (['Art_OfficeCloset_Storage'], {'hangers': [l for l in acts if l.startswith('Art_HA_Hanger03_Office_')]}),
 'BR-CLOSET-BOX-01:097': (['Art_BR_ClosetBox_BR_BOX_BODY_S097'], {}),
}
# How an instance is measured when its rect does not describe the actor's own bounds:
#   with_kids: the scheduled assembly includes the listed children (towels hang from their rails/hook)
#   kit:       a fitted source kit placed at its documented assembly origin; the scheduled rect describes one member
#              (shelf board), while the mesh bounds include hangers, so only xy is compared
#   front_edge:the rect is the closet footprint; the actor is its front frame, which must sit on the rect's front edge
#   patch:     the overlay mesh is the damage patch itself; its centre must be on the scheduled patch centre (6 cm)
MODE = {'ARC-WALL-SHELF-01:077': 'top', 'ARC-WALL-SHELF-01:080': 'top', 'ARC-WALL-SHELF-01:085': 'top',
        'BA-TOWEL-RAIL-01:078': 'with_kids', 'BA-TOWEL-RAIL-01:084': 'with_kids', 'BA-HOOK-01:082': 'with_kids',
        'KI-PAN-RAIL-01:085': 'with_kids', 'BR-CLOSET-01:090': 'kit', 'BR-CLOSET-STORAGE-03:099': 'kit', 'ARC-CLOSET-STORAGE-02:094': 'kit',
        'ARC-CLOSET-STORAGE-02:096': 'kit', 'ARC-SLIDING-CLOSET-01:087': 'front_edge', 'BR-WAINSCOT-01:069': 'patch'}
DEVIATION = {'ARC-CLOSET-RETURN:088': 'closet return built on the 10.75 m centre-line (face 10.81). Centred on the rect '
             '(10.81) its face would be at 10.87 m and collide with the sliding frame (ARC-SLIDING-CLOSET-02 outer 10.84 m).',
             'LV-FUSE-01:043': 'FIX-030 (approved): the case is recessed 10 cm into the north wall (back y -0.04 m) and LV-FUSE-02 '
                               'removed the external wire stubs, so the union bottom is the case bottom 1.522 m instead of the old stub end.',
             'BR-CLOSET-01:092': 'FIX-029 (approved): BR-CLOSET-LIGHT-01 short pendant (canopy 2.75 m, glass bottom 2.46 m, chain to '
                                 '2.015 m) replaces the old 0.69 m drop pendant.',
             'HA-BENCH-01:012': 'batch 2 user feedback (approved): the shoe bench is centred under the full coat rack (HA-HOOKS-01 '
                                'board centre y 3.30 m), slippers directly in front of it.',
             'BA-SWITCH-01:086': 'batch 2 user feedback (approved): the kitchen switch moved to the left of the kitchen portal, '
                                 'plate y 2.12-2.22 m, 10 cm clear of the north casing (rev02_09 KITCHEN_SWITCH_Y).'}
OMIT = {'CHAR-MALCOLM:093': 'not an actor: standing-clearance reference for Malcolm; checked as the Malady_Mold hunk spawn/talk clearance'}

def ubox(labels):
    mn, mx = [1e9] * 3, [-1e9] * 3
    for lab in labels:
        a = acts[lab]
        if isinstance(a, (unreal.FixHimInteractable, unreal.Light)): continue
        o, e = a.get_actor_bounds(False, True)
        for i, (c, h) in enumerate(((o.x, e.x), (o.y, e.y), (o.z, e.z))):
            mn[i] = min(mn[i], c - h); mx[i] = max(mx[i], c + h)
    return mn, mx

rows, problems, used = [], [], set()
for it in sched:
    inst = it['instance']
    if it.get('active') is False:                     # intentionally retired records (FIX-007 :078) are not placed
        rows.append('| %s | %s | — | retired record: %s |' % (inst, it['name'], it.get('note', ''))); continue
    if inst in OMIT:
        rows.append('| %s | %s | — | intentional: %s |' % (inst, it['name'], OMIT[inst])); continue
    assert inst in M, 'unmapped schedule instance ' + inst
    labels, kids = M[inst]
    missing = [l for l in labels if l not in acts]
    status = []
    if missing:
        problems.append('%s missing %s' % (inst, missing)); status.append('MISSING ' + ', '.join(missing))
    else:
        used.update(labels)
        mode = MODE.get(inst)
        meas = labels + ([l for v in kids.values() if not isinstance(v, str) for l in v if l in acts] if mode == 'with_kids' else [])
        mn, mx = ubox(meas)
        x, y, w, d = [v * 100 for v in it['rect']]; cx, cy = x + w / 2, y + d / 2
        dx, dy = (mn[0] + mx[0]) / 2 - cx, (mn[1] + mx[1]) / 2 - cy
        dz = mn[2] - it.get('z', 0) * 100
        wall = it.get('z', 0) > 0.05 and mode != 'kit'
        tol = 15 if wall or mode == 'kit' else 22
        if mode == 'front_edge':
            fy = y + d if it.get('front') == 'south' else y
            dy = (mn[1] + mx[1]) / 2 - fy
            ok = abs(dx) <= tol and abs(dy) <= tol
            txt = 'front frame Δx %+.0f cm, Δ to front edge %+.0f cm' % (dx, dy)
        elif mode == 'patch':
            dzc = (mn[2] + mx[2]) / 2 - (it.get('z', 0) + it['h'] / 2) * 100
            ok = abs(dx) <= 6 and abs(dy) <= 6 and abs(dzc) <= 6
            txt = 'patch centre Δ (%+.0f, %+.0f, %+.0f) cm; overlay x %.0f..%.0f, z %.0f..%.0f' % (dx, dy, dzc, mn[0], mx[0], mn[2], mx[2])
        elif mode == 'top':
            dzt = mx[2] - it.get('z', 0) * 100
            ok = abs(dx) <= tol and abs(dy) <= tol and abs(dzt) <= 3
            txt = 'Δxy (%+.0f, %+.0f) cm, Δtop %+.1f cm (schedule z is the shelf-top datum)' % (dx, dy, dzt)
        else:
            ok = abs(dx) <= tol and abs(dy) <= tol and (not wall or abs(dz) <= 12)
            txt = 'Δxy (%+.0f, %+.0f) cm%s%s' % (dx, dy, ', Δbottom %+.0f cm' % dz if wall else '',
                                               ' (kit at its assembly origin; xy only)' if mode == 'kit' else '')
        if inst in DEVIATION:
            ok = True; txt += '; intentional deviation: ' + DEVIATION[inst]
        status.append(('ok ' if ok else 'CHECK ') + txt)
        if not ok: problems.append('%s %s' % (inst, status[-1]))
    kid_txt = []
    for child in it.get('children', []):
        v = kids.get(child)
        if v is None:
            problems.append('%s child %s unmapped' % (inst, child)); kid_txt.append('%s: UNMAPPED' % child)
        elif isinstance(v, str):
            kid_txt.append('%s: %s' % (child, v))
        else:
            miss = [l for l in v if l not in acts]
            if miss: problems.append('%s child %s missing %s' % (inst, child, miss))
            used.update(l for l in v if l in acts)
            shown = ', '.join('`%s`' % l for l in v) if len(v) <= 6 else '%d actors (`%s` ... `%s`)' % (len(v), v[0], v[-1])
            if not v: problems.append('%s child %s has no actors' % (inst, child))
            kid_txt.append('%s: %s' % (child, shown + (' MISSING ' + str(miss) if miss else '')))
    rows.append('| %s | %s | %s | %s%s |' % (inst, it['name'], ', '.join('`%s`' % l for l in labels), '; '.join(status),
                                             ('<br>' + '<br>'.join(kid_txt)) if kid_txt else ''))

# Imported-art actors the schedule does not name (shell, finishes, floors, doors, windows and lighting excluded).
SKIP = ('Redesign/Shell', 'Redesign/Wall Finishes', 'Redesign/Floor', 'Redesign/Ceiling', 'Redesign/Doors', 'Redesign/Lighting', 'Gameplay/Rooms', 'Gameplay/Start')
plan = json.load(open(os.path.join(os.path.dirname(SCHED), '..', 'approved-plan.json')))
fixtures = json.load(open(SCHED))['ceiling_fixtures']
def asset_key(lab):
    t = lab.split('_')
    return '_'.join(t[:3]) if lab.startswith('Art_') else None
used_keys = {asset_key(l) for l in used if asset_key(l)}
groups = {'parts': [], 'actions': [], 'fixtures': [], 'textiles': [], 'other': []}
for lab, a in sorted(acts.items()):
    fp = str(a.get_folder_path())
    if lab in used or fp.startswith(SKIP) or not fp or a.actor_has_tag('GameplayBodySource') or isinstance(a, unreal.Note): continue
    o, _ = a.get_actor_bounds(False, True)
    # rev02_09_controls: room wall switches (incl. their duplicated plate/rocker art) and overhead-light fixtures are gameplay controls
    if fp.startswith(('Gameplay/Interactables', 'Gameplay/Structure', 'Gameplay/Maladies', 'Gameplay/WallSwitches', 'Gameplay/OverheadLights')):
        groups['actions'].append('`%s`' % lab)
    elif lab.startswith('Art_CeilingLight_'):
        near = min(fixtures, key=lambda f: (f['position'][0] * 100 - o.x) ** 2 + (f['position'][1] * 100 - o.y) ** 2)
        d = ((near['position'][0] * 100 - o.x) ** 2 + (near['position'][1] * 100 - o.y) ** 2) ** 0.5
        groups['fixtures'].append('`%s`: %s ceiling fixture, %.0f cm from its scheduled position' % (lab, near['room'], d))
    elif any(k in lab for k in ('Rug', 'Runner', 'Mat_', 'Curtain')):
        groups['textiles'].append('`%s`' % lab)
    elif asset_key(lab) in used_keys or lab in ('Art_BR_Closet02_Trim', 'Art_KI_SinkNarrow_R_tap', 'Art_KI_SINK_damage_Wet', 'Art_KI_SINK_damage_Film', 'Art_KI_SinkSplash', 'Art_BA_Toilet02_Water') or lab.startswith(('Art_KI_Backsplash_End', 'Art_KI_CounterFiller02_')):
        groups['parts'].append('`%s`' % lab)
    else:
        groups['other'].append('`%s` (%s)' % (lab, fp))
rug = next(i for i in plan['decorative_floor_items'] if i['asset_id'] == 'LV-RUG-01')
ro, re_ = acts['Art_LV_Rug_LV_RUG_01'].get_actor_bounds(False)
rx, ry, rw, rd = [v * 100 for v in rug['rect']]
extra = (['**Members of scheduled assemblies** (lids, stoppers, toggles, bulbs, handles, doors, ends, kit trim, the second '
          'narrow-sink tap): ' + ', '.join(groups['parts']), '',
          '**Click actions and maladies** (each moves with the assembly it belongs to; bodies are the hidden source art): ' + ', '.join(groups['actions']), '',
          '**Ceiling fixtures** (elevation schedule `ceiling_fixtures`):'] + ['  - ' + f for f in groups['fixtures']] +
         ['', '**Textiles / surfaces** ("surface / textile; see floor plan" in the asset schedule): ' + ', '.join(groups['textiles']) +
          '. Living rug footprint x %.0f..%.0f, y %.0f..%.0f cm vs. plan LV-RUG-01 x %.0f..%.0f, y %.0f..%.0f.' % (
              ro.x - re_.x, ro.x + re_.x, ro.y - re_.y, ro.y + re_.y, rx, rx + rw, ry, ry + rd), '',
          '**Not accounted for:** ' + (', '.join(groups['other']) if groups['other'] else 'none')])
problems += ['unaccounted actor ' + o for o in groups['other']]

md = ['# Rev02 engine reconciliation', '',
      'Generated by `Tools/Editor/Rev02/rev02_08_reconcile.py` from `L_Apartment_Rev02` against the revision 02 '
      '[elevation schedule](layout-revision-02/kitchen-dining-study/elevations/elevation-schedule.json). '
      'Placement deltas compare the actors\' union bounds centre with the scheduled rect centre (tolerance 15 cm for wall-mounted '
      'items, whose bottom must also be within 12 cm of the scheduled height; 22 cm for floor items, whose meshes differ from '
      'planning footprints). Gameplay actors listed with an item are the click actions or maladies that move with it.', '',
      '**Result:** %d scheduled instances; %s.' % (len(sched), 'no problems' if not problems else '%d to check' % len(problems)), '']
if problems:
    md += ['## To check', ''] + ['- ' + p for p in problems] + ['']
md += ['## Instances', '', '| Instance | Name | Actors | Placement / children |', '|---|---|---|---|'] + rows + ['',
       '## Every other placed actor', '',
       'Placed art and gameplay actors outside the shell/finish/door/window/lighting folders that no scheduled instance or child '
       'names directly, classified. Hidden gameplay body sources (whose meshes are the click-action bodies) are excluded.', ''] + extra
open(OUT, 'w').write('\n'.join(md) + '\n')
unreal.log('[Rev02 reconcile] %d instances, %d problems, %d unaccounted actors -> %s' % (len(sched), len(problems), len(groups['other']), OUT))
for p in problems: unreal.log('[Rev02 reconcile] CHECK ' + p)
