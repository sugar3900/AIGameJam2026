"""Rev02 step 4c: later feedback-release swaps on existing actors (identities kept for reconciliation).

FIX-006: swap every scheduled wall-art instance to its unique ART-REV02 painting and frame.

The 17 instances keep their engine labels (rev02_08 maps them by instance ID). Each source FBX has a bottom-centre,
rear-wall-plane pivot, so the actor goes exactly to the manifest's engine_placement wall datum (plan metres x 100)
with its UE yaw and unit scale. Materials are the per-slot instances built by rev02_02b. :058 is the enlarged 1.30 x
0.90 hall painting centred between the bath and bedroom doors.
FIX-020: the hall runner actor takes HA-RUNNER-02 (5 m body + fringe) at its assembly.json origin, so its west fringe
stops ~14 cm before the hall cabinet front and its east end stays at 7.80 m. Run after rev02_04b, before rev02_05.
"""
import json, os, unreal
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
R2 = '/Game/ICanFixHim/Environment/Rev02/'
EAL = unreal.EditorAssetLibrary
A = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
inv = json.load(open(os.path.join(ROOT, 'docs/03 Art & Audio/Apartment Design/layout-revision-02/feedback/FIX-006/wall-art-inventory.json')))
LABEL = {'LV-ART-04:040': 'Art_LV_Art04_LV_ART_04', 'HA-ART-02:041': 'Art_HA_Art02_Entry', 'LV-ART-04:045': 'Art_LV_Art04_Bookcase',
         'HA-ART-09:056': 'Art_HA_Art09_HA_ART_09', 'HA-ART-03:057': 'Art_HA_Art03_HA_ART_03', 'HA-ART-02:058': 'Art_HA_Art02_Hall',
         'HA-ART-02:060': 'Art_HA_Art02_HA_ART_02', 'HA-ART-03:061': 'Art_HA_Art03_Gallery',
         'BR-ART-FLORAL-01:062': 'Art_BR_ArtFloral_BR_ART_FLORAL_01', 'BR-ART-FLORAL-01:064': 'Art_BR_ArtFloral_Bookcase',
         'BR-ART-FLORAL-01:066': 'Art_BR_ArtFloral_Dresser', 'BR-ART-FLORAL-01:067': 'Art_BR_ArtFloral_Headboard',
         'OF-ART-LANDSCAPE-01:070': 'Art_OF_ArtLandscape_OF_ART_LANDSCAPE_01', 'OF-ART-BOTANICAL-01:071': 'Art_OF_ArtBotanical_OF_ART_BOTANICAL_01',
         'OF-ART-BOTANICAL-01:073': 'Art_OF_ArtBotanical_East', 'BA-ART-01:081': 'Art_BA_Art01_BA_ART_01', 'KI-ART-01:082': 'Art_KI_Art01_KI_ART_01'}
acts = {a.get_actor_label(): a for a in A.get_all_level_actors()}
assert len(inv['items']) == len(LABEL) == 17
for it in inv['items']:
    sa = it['source_art']; kit = sa['asset'].replace('-', '_'); a = acts[LABEL[it['instance']]]
    mesh = EAL.load_asset(R2 + kit + '/' + kit); assert isinstance(mesh, unreal.StaticMesh), kit
    c = a.static_mesh_component; a.modify()
    c.set_static_mesh(mesh)
    for i in range(c.get_num_materials()): c.set_material(i, None)
    for i, slot in enumerate(mesh.static_materials):
        want = next(m for m in sa['materials'] if m['name'] == str(slot.material_slot_name))
        c.set_material(i, EAL.load_asset(R2 + 'Materials/MI_' + want['name'].replace('-', '_')))
    ep = sa['engine_placement']; x, y, z = [v * 100 for v in ep['wall_datum_center_plan_m']]
    a.set_actor_scale3d(unreal.Vector(*ep['scale']))
    a.set_actor_location_and_rotation(unreal.Vector(x, y, z), unreal.Rotator(0, 0, ep['ue_local_yaw_degrees']), False, True)
    o, e = a.get_actor_bounds(False)
    unreal.log('[Rev02 wall art] %s %s -> %s at (%.1f,%.1f,%.1f) yaw %d; bounds x %.1f-%.1f y %.1f-%.1f z %.1f-%.1f' % (
        it['instance'], a.get_actor_label(), sa['asset'], x, y, z, ep['ue_local_yaw_degrees'], o.x - e.x, o.x + e.x, o.y - e.y, o.y + e.y, o.z - e.z, o.z + e.z))
# ---------------- FIX-020 hall runner ----------------
if EAL.does_asset_exist(R2 + 'HA_Runner02/HA_RUNNER_02'):       # applies once the FIX-020 kit is imported
    asm = json.load(open(os.path.join(ROOT, 'Art Source/Apartment Redesign/Assets/HA-RUNNER-02/assembly.json')))
    run = acts['Art_HA_Runner_HA_RUNNER_01']; c = run.static_mesh_component; run.modify()
    mesh = EAL.load_asset(R2 + 'HA_Runner02/HA_RUNNER_02'); c.set_static_mesh(mesh)
    for i, slot in enumerate(mesh.static_materials):
        c.set_material(i, EAL.load_asset(R2 + 'Materials/MI_' + str(slot.material_slot_name)))
    c.set_collision_profile_name('NoCollision')
    pl = asm['placement']; x, y, z = [v * 100 for v in pl['origin_plan_m']]
    run.set_actor_scale3d(unreal.Vector(*pl['scale']))
    run.set_actor_location_and_rotation(unreal.Vector(x, y, z), unreal.Rotator(0, 0, pl['yaw_degrees']), False, True)
    o, e = run.get_actor_bounds(False)
    unreal.log('[Rev02 runner] HA-RUNNER-02 at (%.2f,%.2f,%.4f): x %.2f-%.2f y %.2f-%.2f z %.3f-%.3f (expect x %.1f-%.1f)' % (
        x, y, z, o.x - e.x, o.x + e.x, o.y - e.y, o.y + e.y, o.z - e.z, o.z + e.z, pl['expected_fringe_x_extent_m'][0] * 100, pl['expected_fringe_x_extent_m'][1] * 100))
# ---------------- FIX-008 HA-SCONCE-02: same plate origin, so the three parts swap in place on all three sconces ----------------
if EAL.does_asset_exist(R2 + 'HA_Sconce02/HA_Sconce02_Shade'):
    for inst in ('Art_HA_Sconce01_HA_Sconce_%s', 'Art_HA_Sconce02_HA_Sconce_%s', 'Art_HA_Sconce01_HA_Sconce_%s_Kitchen'):
        for part in ('Hardware', 'Shade', 'Bulb'):
            a = acts[inst % part]; c = a.static_mesh_component; a.modify()
            mesh = EAL.load_asset(R2 + 'HA_Sconce02/HA_Sconce02_' + part); c.set_static_mesh(mesh)
            for i, slot in enumerate(mesh.static_materials):
                c.set_material(i, EAL.load_asset(R2 + 'Materials/MI_' + str(slot.material_slot_name)))
    unreal.log('[Rev02 sconce] HA-SCONCE-02 swapped on 3 sconces (9 parts)')

# ---------------- FIX-018 KI-CHAIR-02: every actor sharing the KI-CHAIR-01 mesh, at its own transform ----------------
if EAL.does_asset_exist(R2 + 'KI_Chair02/KI_CHAIR_02'):
    old = acts['Art_KI_Chair_13'].static_mesh_component.static_mesh
    new = EAL.load_asset(R2 + 'KI_Chair02/KI_CHAIR_02'); n = 0
    for lab, a in acts.items():
        if isinstance(a, unreal.StaticMeshActor) and a.static_mesh_component.static_mesh == old:
            c = a.static_mesh_component; a.modify(); c.set_static_mesh(new)
            for i, slot in enumerate(new.static_materials):
                c.set_material(i, EAL.load_asset(R2 + 'Materials/MI_' + str(slot.material_slot_name)))
            n += 1
    unreal.log('[Rev02 chairs] KI-CHAIR-02 swapped on %d actors' % n)

# ---------------- FIX-016 HA-SLIPPERS-01: one pair replaces the shoe tray and four shoes ----------------
if EAL.does_asset_exist(R2 + 'HA_Slippers01/HA_SLIPPERS_01'):
    sasm = json.load(open(os.path.join(ROOT, 'Art Source/Apartment Redesign/Assets/HA-SLIPPERS-01/assembly.json')))
    pp = sasm['proposed_placement']
    for lab in ('Art_HA_Shoes_HA_ShoeTray', 'Art_HA_Shoes_HA_Oxford_1', 'Art_HA_Shoes_HA_Oxford_2', 'Art_HA_Shoes_HA_SlipOn_1', 'Art_HA_Shoes_HA_SlipOn_2'):
        A.destroy_actor(acts.pop(lab))
    mesh = EAL.load_asset(R2 + 'HA_Slippers01/HA_SLIPPERS_01')
    sl = A.spawn_actor_from_object(mesh, unreal.Vector(*pp['unreal_location_cm']), unreal.Rotator(0, 0, pp['yaw_degrees']))
    sl.set_actor_label('Art_HA_Slippers01'); sl.set_folder_path('Redesign/Imported Art/Rev02'); acts['Art_HA_Slippers01'] = sl
    c = sl.static_mesh_component; c.set_collision_profile_name('NoCollision')
    for i, slot in enumerate(mesh.static_materials):
        c.set_material(i, EAL.load_asset(R2 + 'Materials/MI_' + str(slot.material_slot_name)))
    o, e = sl.get_actor_bounds(False)
    unreal.log('[Rev02 slippers] x %.2f-%.2f y %.2f-%.2f z %.2f-%.2f (expect x 1155.11-1184.89, y 349.23-374.77)' % (
        o.x - e.x, o.x + e.x, o.y - e.y, o.y + e.y, o.z - e.z, o.z + e.z))
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_all_dirty_levels()
unreal.log('[Rev02 wall art] 17 instances swapped and saved')
