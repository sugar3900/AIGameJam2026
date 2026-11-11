"""Rev02 step 2: import the fitted revision-02 art kits (Art Source, read-only) into /Game/.../Environment/Rev02/.

Each kit's FBXs carry authored UCX_ collision hulls, so automatic collision generation is off and the UCX hulls
are imported as simple collision. UE 5.8's Interchange FBX path drops UCX hulls (verified: 0 convex elements), so
this script imports through the legacy FBX importer (Interchange.FeatureFlags.Import.FBX off for the duration). Materials and textures come from the FBX; rev02_03 reassigns the approved,
already-tuned Unreal materials where a kit reuses an existing finish. Logs every mesh's bounds and simple-collision
count so axis conversion and pivots can be checked against each kit's assembly.json/manifest.json. Re-runnable.
"""
import os, unreal
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
SRC = os.path.join(ROOT, 'Art Source/Apartment Redesign/Assets')
DST = '/Game/ICanFixHim/Environment/Rev02/'
EAL = unreal.EditorAssetLibrary
SM = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
tools = unreal.AssetToolsHelpers.get_asset_tools()
assert not unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor(), 'Stop PIE first: editor-world actor queries are empty and asset saves race during PIE'

KITS = {
    'KI_Cabinet02': ('KI-CABINET-02/model', ['KI_CAB_0425_body', 'KI_CAB_0425_door', 'KI_CAB_0425_drawer',
                                             'KI_CAB_0775_body', 'KI_CAB_0775_door_L', 'KI_CAB_0775_door_R',
                                             'KI_CAB_0775_drawer_L', 'KI_CAB_0775_drawer_R',
                                             'KI_CAB_0450_body', 'KI_CAB_0450_door', 'KI_CAB_0450_drawer']),
    'KI_SinkNarrow': ('KI-SINK-NARROW-01/models', ['KI_SINK_NARROW_body', 'KI_SINK_NARROW_L_tap', 'KI_SINK_NARROW_R_tap',
                                                   'KI_SINK_NARROW_damage']),
    'ARC_WindowKitchen02': ('ARC-WINDOW-KITCHEN-02/model', ['ARC_Window_Kitchen_frame', 'ARC_Window_Kitchen_lower_sash',
                                                            'ARC_Window_Kitchen_upper_sash', 'ARC_Window_Kitchen_lower_glass',
                                                            'ARC_Window_Kitchen_upper_glass']),
    'BR_Closet02': ('BR-CLOSET-02/model', ['BR_Closet02_Trim', 'BR_Closet02_Door_L', 'BR_Closet02_Door_R', 'BR_Closet02_Shelf',
                                           'BR_Closet02_Bulb', 'BR_Closet02_Mold']),
    'KI_Fridge02': ('KI-FRIDGE-02/models', ['KI_FRIDGE_02_BODY', 'KI_FRIDGE_02_DOOR']),
    'ARC_Sliding02': ('ARC-SLIDING-CLOSET-02/model', ['ARC_Sliding02_Frame', 'ARC_Sliding02_LeftPanel', 'ARC_Sliding02_RightPanel']),
    'ARC_Door02': ('ARC-DOOR-02/model', ['ARC_Door02_Frame', 'ARC_Door02_Leaf']),
    'ARC_EntryDoor02': ('ARC-ENTRY-DOOR-02/model', ['ARC_Entry_Door02_Frame', 'ARC_Entry_Door02_Leaf']),
    'KI_WallTable02': ('KI-WALL-TABLE-02/model', ['KI_WALL_TABLE_02']),
    'KI_Stool02': ('KI-STOOL-02/model', ['KI_STOOL_02']),
    'ARC_ClosetStorage02': ('ARC-CLOSET-STORAGE-02/model', ['ARC_ClosetStorage02']),
    # Feedback source release 001-003 (FIX-001 mold planes, FIX-002 closet side storage, FIX-003 clean sink + pail).
    'BR_Mold02': ('BR-MOLD-02/model', ['BR_Mold02_Back', 'BR_Mold02_Return']),
    'BR_ClosetStorage03': ('BR-CLOSET-STORAGE-03/model', ['BR_ClosetStorage03_West', 'BR_ClosetStorage03_East']),
    'KI_Leak02': ('KI-LEAK-02/models', ['KI_LEAK_02_sink_body', 'KI_LEAK_02_bucket', 'KI_LEAK_02_bucket_water']),
    # FIX-005: rebuilt sofa, same floor-centre origin/-Y front/envelope as LV-SOFA-01; 13 UCX hulls.
    'LV_Sofa02': ('LV-SOFA-02/model', ['LV-SOFA-02']),
    # FIX-020: fitted 5 m runner + fringe, floor-centre origin, long axis X; no collision (the floor supplies it).
    'HA_Runner02': ('HA-RUNNER-02/model', ['HA_RUNNER_02']),
    # FIX-008: closed opal shade + hardware + bulb, same wall-plate origin as HA-SCONCE-01.
    'HA_Sconce02': ('HA-SCONCE-02/models', ['HA_Sconce02_Hardware', 'HA_Sconce02_Shade', 'HA_Sconce02_Bulb']),
    # FIX-016: one pair of slippers (two meshes, common floor-centre origin), no collision.
    'HA_Slippers01': ('HA-SLIPPERS-01/model', ['HA_SLIPPERS_01']),
    # FIX-010: entry door hardware moved onto the lock stile + latch/strike plates; same pivots, bounds and UCX as 02.
    'ARC_EntryDoor03': ('ARC-ENTRY-DOOR-03/model', ['ARC_Entry_Door03_Frame', 'ARC_Entry_Door03_Leaf']),
    # FIX-013: rebuilt armchair, LV-CHAIR-01's origin/facing/envelope; 15 UCX hulls.
    'LV_Armchair02': ('LV-ARMCHAIR-02/model', ['LV-ARMCHAIR-02']),
    # FIX-014: outward closed leaves, upward soil, closed pot; original pot origin; one convex pot UCX, no foliage collision.
    'LV_Plant02': ('LV-PLANT-02/model', ['LV_Plant02']),
    # FIX-018: dining chair with corrected concave back slats; KI-CHAIR-01 envelope/UVs; 26 UCX hulls.
    'KI_Chair02': ('KI-CHAIR-02/model', ['KI_CHAIR_02']),
    # FIX-019: six fitted office wainscot runs at the common office origin; decorative, no collision (complex only).
    'OF_Wainscot02': ('OF-WAINSCOT-02/model', ['OF_Wainscot02_' + k for k in ('N', 'CS', 'WF', 'E', 'S', 'W')]),
    # FIX-007: split tub fixtures (west-wall plumbing; rod and drain stay on the original fixture transform) and the
    # brass hand-towel ring + folded towel. All decorative, placed NoCollision.
    'BA_TubFixtures02': ('BA-TUB-FIXTURES-02/model', ['BA_TubFixture02_Plumbing', 'BA_TubFixture02_CurtainRod', 'BA_TubFixture02_Drain']),
    'BA_Ring02': ('BA-HAND-TOWEL-RING-02/model', ['BA_Ring02_Hardware', 'BA_Ring02_Towel']),
    # FIX-025: ARC-TRIM-01's door casing (never imported by A+), for the kitchen portal surround.
    'ARC_Trim01': ('ARC-TRIM-01/model', ['Casing_1m']),
    # FIX-023: rebuilt toilet (21 UCX body, 1 UCX lid with hinge stored in assembled space, static bowl water).
    'BA_Toilet02': ('BA-TOILET-02/model', ['BA_Toilet02_Body', 'BA_Toilet02_Lid', 'BA_Toilet02_Water']),
    # FIX-027: faucet-only rebuild of the clean sink body + coaxial L/R taps (1 UCX each), assembled-space pivots.
    'KI_Faucet02': ('KI-FAUCET-02/models', ['KI_FAUCET_02_sink_body', 'KI_FAUCET_02_L_tap', 'KI_FAUCET_02_R_tap']),
    # FIX-024: outside-corner mitre pairs (decorative, no collision); Trim_Cream assigned at placement.
    'ARC_Trim02': ('ARC-TRIM-02/model', ['Baseboard_Outside_End', 'Baseboard_Outside_Start', 'Crown_Outside_End', 'Crown_Outside_Start']),
    # FIX-030: aged-interior fuse shell (replaces only LV_FUSE_01_Shell; door and repair wires stay LV-FUSE-01).
    'LV_Fuse02': ('LV-FUSE-02/models', ['LV_Fuse02_Shell']),
    # FIX-029: pull-chain closet pendant; functional-pivot local exports (ceiling mount / chain top), chain has 1 UCX.
    'BR_ClosetLight01': ('BR-CLOSET-LIGHT-01/models', ['BR_ClosetLight01_Hardware', 'BR_ClosetLight01_Glass',
                                                       'BR_ClosetLight01_Filament', 'BR_ClosetLight01_Chain']),
    # FIX-035: KI-TABLE-01 with apron-only UV relayout (continuous lengthwise boards); geometry/other UVs identical.
    'KI_Table02': ('KI-TABLE-02/models', ['KI_TABLE_02']),
    # FIX-031/032: exact original stand + separate tabletop housing + one CRT screen, all on the LV-TV-01 floor origin.
    'LV_TV02': ('LV-TV-02/models', ['LV_TV02_Stand', 'LV_TV02_Housing', 'LV_TV02_Screen']),
    # batch 2 props/room: closet storage without baked hangers + single hanger + pan pair; sofa throw contact;
    # room corrections (slim baseboards, sliding frame gap, curved L rod + fixed return, pink bullnose, bed/daybed
    # bedding, books/plant); ARC-DOOR-03 (larger knobs, casing/header gap closed).
    'PropFit03': ('PROP-FIT-03/model', ['ARC_ClosetStorage03', 'HA_Hanger03', 'KI_PanPair03']),
    'LV_Sofa03': ('LV-SOFA-03/model', ['LV-SOFA-03']),
    'Room03': ('FEEDBACK-ROOM-03/model', ['ARC_Sliding03_Frame', 'BA_Curtain03_FixedReturn', 'BA_CurvedL_Rod', 'BA_PinkBullnose_1m',
                                         'BR_Bed03_Bedding', 'BR_Bed03_Frame', 'Baseboard_1m', 'Baseboard_Inside_End', 'Baseboard_Inside_Start',
                                         'Baseboard_Outside_End', 'Baseboard_Outside_Start', 'LV_Book03_Books', 'LV_Book03_Plant', 'OF_Daybed03_Bedding']),
    'ARC_Door03': ('ARC-DOOR-03/model', ['ARC_Door03_Frame', 'ARC_Door03_Leaf']),
    # round 3: ROUND3-PANTRY-01 leaves (4 mm meeting reveal, continuous paint UVs, authored 460 mm UCX slabs) and the
    # ROUND3-TUB-01 developed clawfoot body (no UCX: the integration step copies the original tub's collision)
    'Pantry03': ('ROUND3-PANTRY-01/models', ['KI_Pantry03_LeftDoor', 'KI_Pantry03_RightDoor']),
    'Tub03': ('ROUND3-TUB-01/model', ['BA_Tub03_Body']),
    # ROUND3-WINDOW-01 head-join frames (kitchen keeps its authored UCX; the others reuse installed collision) and the
    # ROUND3-PLANT-01 pot/saucer refinement (foliage unchanged)
    'Window03': ('ROUND3-WINDOW-01/model', ['ARC_Window_Narrow03_frame', 'ARC_Window_Office03_frame', 'ARC_Window_Bath03_frame',
                                            'ARC_Window_Kitchen03_frame', 'ARC_Window_Living03_Casing']),
    'Plant04': ('ROUND3-PLANT-01/model', ['LV_Book04_Plant']),
    # ROUND3-RANGE-03 developed range body/door (same origins/hinge; new Range03_* slots need explicit materials)
    'Range03': ('ROUND3-RANGE-03/model', ['KI_RANGE03_Body', 'KI_RANGE03_Door']),
    # ROUND3-KITCHEN-SURFACES-01: carcasses without embedded counter/black toe (U plinth, original UCX), one continuous slab
    # per run (1 UCX each), fitted backsplash bands (2 mm recessed grout, cropped 10 cm grid, outward bullnose)
    'KitchenSurf03': ('ROUND3-KITCHEN-SURFACES-01/models', ['KI_Cab06_0425_Body', 'KI_Cab06_0775_Body', 'KI_Cab06_0450_Body',
                      'KI_Counter03_A', 'KI_Counter03_B', 'KI_Counter03_C',
                      'KI_Backsplash03_A', 'KI_Backsplash03_B', 'KI_Backsplash03_Range', 'KI_Backsplash03_C']),
    # ROUND3-CLOSET-FRAME-01: closet frame matching the ARC-DOOR-03 casing/head/cap profile (3 UCX hulls unchanged)
    'ClosetFrame04': ('ROUND3-CLOSET-FRAME-01/model', ['ARC_ClosetFrame04']),
    # PROP-FIT-03 keeps only the pan rail body (the released assembly has the old hooks baked in).
    'KI_PanRail01': ('KI-PAN-RAIL-01/model', ['KI_Pan_Rail_Body']),
    # batch 2 kitchen: front fit (drawer = door widths, door tops .672), fitted backsplash bands + counter infills, range detail.
    'Joinery05': ('CABINET-JOINERY-04/models', ['KI_Cab05_%s' % p for p in ('0425_door', '0425_drawer', '0450_door', '0450_drawer',
                                                                         '0775_door_L', '0775_door_R', '0775_drawer_L', '0775_drawer_R')]),
    'KI_Backsplash02': ('KI-BACKSPLASH-02/models', ['KI_Backsplash02_A', 'KI_Backsplash02_B', 'KI_Backsplash02_C', 'KI_Backsplash02_Range',
                                                   'KI_CounterFiller02_EastEnd', 'KI_CounterFiller02_FridgeExtension', 'KI_CounterFiller02_Rear0425',
                                                   'KI_CounterFiller02_Rear0450', 'KI_CounterFiller02_Rear0775']),
    'KI_Range02': ('KI-RANGE-02/models', ['KI_RANGE02_Body', 'KI_RANGE02_Door']),
    # FIX-033 single-leaf patch: narrowed 0775 left leaf (hinge back to the old 271.7 line) + fixed hinge-side filler.
    'Joinery03': ('CABINET-JOINERY-03/models', ['KI_Cab04_0775_door_L', 'KI_Cab04_0775_Filler']),
    # FIX-033/034/036: true-frame doors, new hinge pivots (pivot-local), retained carcasses, shared sage/ivory finishes.
    'Joinery02': ('CABINET-JOINERY-02/models', [f'KI_Cab03_{w}_{p}' for w, ps in (('0425', ('Body', 'door', 'drawer')), ('0450', ('Body', 'door', 'drawer')),
                                                                                  ('0775', ('Body', 'door_L', 'door_R', 'drawer_L', 'drawer_R'))) for p in ps]
                  + ['KI_Upper02_Body', 'KI_Upper02_LeftDoor', 'KI_Upper02_RightDoor', 'KI_Pantry02_Body', 'KI_Pantry02_LeftDoor',
                     'KI_Pantry02_RightDoor', 'BA_Linen02_Body', 'BA_Linen02_LowerDoor', 'BA_Linen02_UpperDoor']),
}
# FIX-006: the 17 unique framed paintings (ART-REV02-001..017), one kit each, listed by the wall-art inventory.
import json as _json
ART_INV = os.path.join(ROOT, 'docs/03 Art & Audio/Apartment Design/layout-revision-02/feedback/FIX-006/wall-art-inventory.json')
ART = [it['source_art'] for it in _json.load(open(ART_INV))['items']]
for sa in ART:
    KITS[sa['asset'].replace('-', '_')] = (sa['asset'] + '/models', [sa['asset']])
# Loose textures for engine-built materials: (kit folder, source path, sRGB).
TEXTURES = {
    'BR_Mold02': [('BR-MOLD-02/textures/mold-colonies-rgba.png', False)],
    'LV_Sofa02': [('LV-SOFA-02/textures/sofa-floral.png', True), ('LV-SOFA-02/textures/pillow-teal-needlepoint.png', True),
                  ('LV-SOFA-02/textures/pillow-coral-embroidery.png', True), ('LV-SOFA-02/textures/throw-wool.png', True)],
    'HA_Runner02': [('HA-RUNNER-02/textures/runner-albedo.png', True)],
    'HA_Sconce02': [('HA-SCONCE-02/textures/aged-brass.png', True), ('HA-SCONCE-02/textures/opal-glass.png', True)],
    'HA_Slippers01': [('HA-SLIPPERS-01/textures/T_Slipper_Quilt.png', True), ('HA-SLIPPERS-01/textures/T_Slipper_Velvet.png', True)],
    'OF_Wainscot02': [('OF-WAINSCOT-02/textures/painted-ivory.png', True)],
    'BA_Ring02': [('BA-HAND-TOWEL-RING-02/textures/aged-brass.png', True), ('BA-HAND-TOWEL-RING-02/textures/terry.png', True)],
    'BA_Toilet02': [('BA-TOILET-02/textures/painted-ivory.png', True)],
    'KI_Chair02': [('KI-CHAIR-02/textures/wood-selected-v2.png', True), ('KI-CHAIR-02/textures/vinyl.png', True)],
    'LV_Plant02': [('LV-PLANT-02/textures/terracotta.png', True), ('LV-PLANT-02/textures/pothos-leaf.png', True)],
    'LV_Armchair02': [('LV-ARMCHAIR-02/textures/rust-jacquard.png', True), ('LV-ARMCHAIR-02/textures/walnut-painted.png', True),
                      ('LV-ARMCHAIR-02/textures/ivory-thread.png', True)],
    # FIX-038 glaze data maps (linear; the normal is DirectX tangent space) + BA-TILE-01 candidate-b glaze colour field
    'KI_Backsplash02': [('KI-BACKSPLASH-02/textures/glaze-ivory.png', True, 'T_Backsplash02_GlazeIvory'), ('KI-BACKSPLASH-02/textures/glaze-sage.png', True, 'T_Backsplash02_GlazeSage'),
                        ('KI-BACKSPLASH-02/textures/ivory-enamel.png', True, 'T_Backsplash02_IvoryEnamel')],
    'KI_Range02': [('KI-RANGE-02/textures/range-enamel-v2.png', True, 'T_Range02_Enamel')],
    'BR_ClosetBox': [('BR-CLOSET-BOX-01/textures/sage-linen.png', True, 'T_ClosetBox_SageLinen')],
    # BR-BED-01 README: walnut painterly albedo for the frame (the installed slot was a flat 0.8 Phong = white)
    'BR_Bed03': [('BR-BED-01/textures/walnut-painted.png', True, 'T_Bed_WalnutPainted')],
    # round 3: BA-TOWEL-RAIL-01 README aged-brass albedo (the rail slot was flat FBX Phong = white)
    'BA_TowelRail': [('BA-TOWEL-RAIL-01/textures/aged-brass.png', True, 'T_TowelRail_AgedBrass')],
    # round 3: the shared painterly walnut grain every ART-REV02 frame was baked from (one image, identical in all 17 kits)
    'ArtFrames': [('ART-REV02-001/textures/T_Frame_Grain.png', True, 'T_Frame_Grain')],
    'KitchenSurf03': [('ROUND3-KITCHEN-SURFACES-01/textures/ivory-enamel.png', True, 'T_KitchenSurf03_IvoryEnamel')],
    'Range03': [('ROUND3-RANGE-03/textures/aged-steel.png', True, 'T_Range03_AgedSteel'), ('ROUND3-RANGE-03/textures/iron-grain.png', True, 'T_Range03_IronGrain'),
                ('ROUND3-RANGE-03/textures/range-enamel.png', True, 'T_Range03_Enamel')],
    'Tub03': [('ROUND3-TUB-01/textures/enamel-albedo.png', True, 'T_Tub03_EnamelAlbedo'), ('ROUND3-TUB-01/textures/enamel-brush.png', True, 'T_Tub03_EnamelBrush'),
              ('ROUND3-TUB-01/textures/aged-metal.png', True, 'T_Tub03_AgedMetal')],
    'BA_TileGlaze02': [('BA-TILE-GLAZE-02/textures/T_BathGlaze_NormalDX.png', False), ('BA-TILE-GLAZE-02/textures/T_BathGlaze_Roughness.png', False),
                       ('BA-TILE-01/textures/candidate-b.png', True, 'T_BathTile_GlazeB')],
    'Joinery02': [('CABINET-JOINERY-02/textures/T_Joinery_Sage.png', True), ('CABINET-JOINERY-02/textures/T_Joinery_Ivory.png', True),
                  ('CABINET-JOINERY-02/textures/T_Joinery_Interior.png', True), ('CABINET-JOINERY-02/textures/toe-dark.png', True, 'T_Joinery_ToeDark'),
                  ('CABINET-JOINERY-02/textures/ivory-enamel.png', True, 'T_Joinery_IvoryEnamel')],
    'LV_TV02': [('LV-TV-02/textures/T_TV02_Walnut.png', True), ('LV-TV-02/textures/T_TV02_SpeakerWeave.png', True),
                ('LV-TV-01/textures/walnut-painted.png', True, 'T_TV01_WalnutPainted')],  # name clashes with the FBX's Walnut_Painted material
    'LV_Fuse02': [('LV-FUSE-02/textures/T_Fuse02_Interior.png', True), ('LV-FUSE-02/textures/T_Fuse02_Bakelite.png', True),
                  ('LV-FUSE-02/textures/T_Fuse02_AgedCeramic.png', True), ('LV-FUSE-02/textures/T_Fuse02_Cloth.png', True)],
    'KI_Leak02': [('KI-LEAK-02/textures/T_Leak_Puddle_Mask.png', False),
                  ('KI-LEAK-02/textures/T_Bucket_Zinc_BaseColor.png', True),
                  ('KI-LEAK-02/textures/T_Bucket_Zinc_Metallic.png', False),
                  ('KI-LEAK-02/textures/T_Bucket_Zinc_Roughness.png', False)],
}
for sa in ART:
    TEXTURES[sa['asset'].replace('-', '_')] = sorted({(sa['asset'] + '/' + m['base_color_texture'], bool(m.get('texture_srgb', True)))
                                                    for m in sa['materials'] if m.get('base_color_texture')})
# The mold planes fade their outer edge through vertex-colour alpha (BR-MOLD-02 README): import colours as Replace.
VERTEX_COLOR_REPLACE = {'BR_Mold02_Back', 'BR_Mold02_Return'}
# Sources exported without UCX hulls. The legacy importer still gives these one generated box, which would seal
# the basin and block clicks on Lukey's leak, so their simple collision is replaced by complex-as-simple. The
# closet bulb and mold also have no UCX; their placed actors use NoCollision.
NO_UCX = {'KI_SINK_NARROW_body', 'KI_SINK_NARROW_L_tap', 'KI_SINK_NARROW_R_tap', 'KI_SINK_NARROW_damage',
          'BR_Closet02_Bulb', 'BR_Closet02_Mold',
          # FIX-003: the clean body keeps the narrow sink's complex-as-simple policy; the pail water has no collision
          # (placed NoCollision). The mold planes are NoCollision art. The pail itself carries 13 UCX hulls.
          'KI_LEAK_02_sink_body', 'KI_LEAK_02_bucket_water', 'BR_Mold02_Back', 'BR_Mold02_Return', 'HA_RUNNER_02',
          # sconce parts keep the old sconce policy (the shade is the click body); slippers are placed NoCollision
          'HA_Sconce02_Hardware', 'HA_Sconce02_Shade', 'HA_Sconce02_Bulb', 'HA_SLIPPERS_01'} | {'OF_Wainscot02_' + k for k in ('N', 'CS', 'WF', 'E', 'S', 'W')} \
         | {'BA_TubFixture02_Plumbing', 'BA_TubFixture02_CurtainRod', 'BA_TubFixture02_Drain', 'BA_Ring02_Hardware', 'BA_Ring02_Towel', 'Casing_1m', 'BA_Toilet02_Water', 'KI_FAUCET_02_sink_body',
                                                  'Baseboard_Outside_End', 'Baseboard_Outside_Start', 'Crown_Outside_End', 'Crown_Outside_Start',
                                                  # FIX-030 shell keeps LV-FUSE-01's complex-as-simple policy; FIX-029
                                                  # hardware/glass/filament are placed NoCollision (only the chain has a UCX)
                                                  'LV_Fuse02_Shell', 'KI_TABLE_02', 'KI_Backsplash02_A', 'KI_Backsplash02_B', 'KI_Backsplash02_C', 'KI_Backsplash02_Range', 'KI_Upper02_Body', 'KI_Pantry02_Body', 'BA_Linen02_Body', 'LV_TV02_Stand', 'LV_TV02_Housing', 'LV_TV02_Screen', 'BR_ClosetLight01_Hardware', 'BR_ClosetLight01_Glass', 'BR_ClosetLight01_Filament', 'KI_Pan_Rail_Body'}
ONLY = globals().get('ONLY')            # optional subset of kit names, e.g. --set "ONLY=['KI_Fridge02']"
PARTS = globals().get('PARTS')          # optional subset of part names within those kits (targeted source re-releases)

def collision_elems(m):
    ag = m.get_editor_property('body_setup').get_editor_property('agg_geom')
    return sum(len(ag.get_editor_property(k)) for k in ('convex_elems', 'box_elems', 'sphere_elems', 'sphyl_elems'))

CVAR = 'Interchange.FeatureFlags.Import.FBX'
was_interchange = unreal.SystemLibrary.get_console_variable_bool_value(CVAR)
unreal.SystemLibrary.execute_console_command(None, CVAR + ' false')
try:
  for kit, (sub, parts) in KITS.items():
      if ONLY and kit not in ONLY: continue
      folder = DST + kit
      for part in parts:
          if PARTS and part not in PARTS: continue
          src = os.path.join(SRC, sub, part + '.fbx')
          assert os.path.isfile(src), src
          t = unreal.AssetImportTask(); t.filename = src; t.destination_path = folder; t.destination_name = part.replace('-', '_')
          t.automated = True; t.replace_existing = True; t.save = True
          o = unreal.FbxImportUI(); o.import_mesh = True; o.import_as_skeletal = False
          o.import_materials = True; o.import_textures = True
          o.static_mesh_import_data.combine_meshes = True
          o.static_mesh_import_data.auto_generate_collision = False     # use the authored UCX hulls
          o.static_mesh_import_data.one_convex_hull_per_ucx = True
          if part in VERTEX_COLOR_REPLACE:
              o.static_mesh_import_data.vertex_color_import_option = unreal.VertexColorImportOption.REPLACE
          t.options = o
          tools.import_asset_tasks([t])
          _paths = [str(x) for x in t.get_editor_property('imported_object_paths')]
          assert any(x.split('.')[0] == folder + '/' + part.replace('-', '_') for x in _paths), 'import produced no %s (got %s)' % (part, _paths)
          m = EAL.load_asset(folder + '/' + part.replace('-', '_'))
          if not isinstance(m, unreal.StaticMesh):        # a brand-new folder may not be registry-scanned yet
              unreal.AssetRegistryHelpers.get_asset_registry().scan_paths_synchronous([folder], True)
              m = EAL.load_asset(folder + '/' + part.replace('-', '_')) or unreal.load_object(None, '%s/%s.%s' % (folder, part.replace('-', '_'), part.replace('-', '_')))
          assert isinstance(m, unreal.StaticMesh), 'import failed: ' + src
          # the import result must be this source file (never a stale asset of the same name)
          ad = m.get_editor_property('asset_import_data')
          assert ad and os.path.normpath(ad.get_first_filename()) == os.path.normpath(src), (part, ad.get_first_filename() if ad else None)
          if part in NO_UCX:
              SM.remove_collisions(m)
              bs = m.get_editor_property('body_setup'); bs.modify()
              bs.set_editor_property('collision_trace_flag', unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
              assert EAL.save_loaded_asset(m, False), part
          b = m.get_bounding_box()
          unreal.log('[Rev02 import] %s/%s min=(%.1f,%.1f,%.1f) max=(%.1f,%.1f,%.1f) collision=%d%s mats=%s' % (
              kit, part, b.min.x, b.min.y, b.min.z, b.max.x, b.max.y, b.max.z, collision_elems(m), ' (complex)' if part in NO_UCX else '',
              [str(s.material_slot_name) for s in m.static_materials]))
  for kit, texs in TEXTURES.items():
      if ONLY and kit not in ONLY: continue
      for rel, srgb, *dest in texs:
          src = os.path.join(SRC, rel); assert os.path.isfile(src), src
          name = dest[0] if dest else os.path.splitext(os.path.basename(src))[0].replace('-', '_')
          t = unreal.AssetImportTask(); t.filename = src; t.destination_path = DST + kit; t.destination_name = name
          t.automated = True; t.replace_existing = True; t.save = True
          try: t.set_editor_property('async_', False)           # Interchange texture imports can otherwise finish after return
          except Exception: pass
          tools.import_asset_tasks([t])
          unreal.AssetRegistryHelpers.get_asset_registry().scan_paths_synchronous([DST + kit], True)
          tex = EAL.load_asset(DST + kit + '/' + name) or unreal.load_object(None, '%s%s/%s.%s' % (DST, kit, name, name))
          assert isinstance(tex, unreal.Texture2D), src
          tex.set_editor_property('srgb', srgb)
          if not srgb:
              tex.set_editor_property('compression_settings', unreal.TextureCompressionSettings.TC_NORMALMAP if 'Normal' in name
                                      else unreal.TextureCompressionSettings.TC_DEFAULT)
          if not EAL.save_loaded_asset(tex, False):        # registry-unindexed new folder: save through the package API
              assert unreal.EditorLoadingAndSavingUtils.save_packages([tex.get_outermost()], False), name
          unreal.log('[Rev02 import] texture %s/%s srgb=%s' % (kit, name, srgb))
  # LV-BOOK-01's shelf books are many separate objects (README: "intentionally detachable"). Imported uncombined,
  # each book is its own mesh in the bookcase's model space, so rev02_04b can lay out new runs on other shelves.
  if not ONLY or 'LV_BookParts' in ONLY:
      t = unreal.AssetImportTask(); t.filename = os.path.join(SRC, 'LV-BOOK-01/model/LV_BOOK_BOOKS.fbx')
      t.destination_path = DST + 'LV_BookParts'; t.automated = True; t.replace_existing = True; t.save = True
      o = unreal.FbxImportUI(); o.import_mesh = True; o.import_as_skeletal = False; o.import_materials = False; o.import_textures = False
      o.static_mesh_import_data.combine_meshes = False; o.static_mesh_import_data.auto_generate_collision = False
      t.options = o
      tools.import_asset_tasks([t])
      books = [p for p in EAL.list_assets(DST + 'LV_BookParts', False, False) if isinstance(EAL.load_asset(p), unreal.StaticMesh)]
      unreal.log('[Rev02 import] LV_BookParts: %d book meshes' % len(books))
  # FEEDBACK-ROOM-03 books, uncombined the same way (one mesh per cover/spine/pages/edge/gilt object, LV model space);
  # rev02_05m merges each book's parts into one engine mesh for the shelf runs laid out away from the LV bookcase.
  if not ONLY or 'LV_Book03Parts' in ONLY:
      t = unreal.AssetImportTask(); t.filename = os.path.join(SRC, 'FEEDBACK-ROOM-03/model/LV_Book03_Books.fbx')
      t.destination_path = DST + 'LV_Book03Parts'; t.automated = True; t.replace_existing = True; t.save = True
      o = unreal.FbxImportUI(); o.import_mesh = True; o.import_as_skeletal = False; o.import_materials = False; o.import_textures = False
      o.static_mesh_import_data.combine_meshes = False; o.static_mesh_import_data.auto_generate_collision = False
      t.options = o
      tools.import_asset_tasks([t])
      books = [p for p in EAL.list_assets(DST + 'LV_Book03Parts', False, False) if isinstance(EAL.load_asset(p), unreal.StaticMesh)]
      unreal.log('[Rev02 import] LV_Book03Parts: %d book part meshes' % len(books))
finally:
    unreal.SystemLibrary.execute_console_command(None, CVAR + (' true' if was_interchange else ' false'))
