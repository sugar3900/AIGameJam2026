"""Rev02 step 4: move the A+ furnishings of L_Apartment_Rev02 to the approved revision 02 positions and install the
fitted kits (KI-CABINET-02, KI-SINK-NARROW-01 + KI-LEAK-02, BR-CLOSET-02 + BR-MOLD-02 + BR-CLOSET-STORAGE-03, ARC-SLIDING-CLOSET-02 panels, ARC-CLOSET-STORAGE-02,
KI-WALL-TABLE-02, KI-STOOL-02).

Assemblies move rigidly: every part, the dressing on it and its gameplay actors (interactables with their lights,
maladies with their attached damage) get the same rotation about the assembly's current bounds centre plus a
translation to its plan centre, so tested hinges, slide axes, camera spots and reveal parts keep their relation to
the art. Targets are plan rect centres (approved-plan.json / elevation-schedule.json, metres x100); facing changes
are yaw deltas. Parts replaced by fitted kits are destroyed; replacements reuse the old labels where a gameplay
actor binds to them, so rev02_05 can re-bind bodies by label. Run once per fresh rev02_01 copy (it moves actors
relative to where they are, so it refuses to run twice).
"""
import math, unreal
MAP = '/Game/ICanFixHim/Maps/L_Apartment_Rev02'
R = '/Game/ICanFixHim/Environment/Redesign/'
R2 = '/Game/ICanFixHim/Environment/Rev02/'
F = R + 'Finishes/'
EAL = unreal.EditorAssetLibrary
A = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert L.load_level(MAP)
acts = {a.get_actor_label(): a for a in A.get_all_level_actors()}
assert 'Rev02_Furnished' not in acts, 'already furnished; re-run rev02_01 (fresh copy) and rev02_03 first'
FOLDER = 'Redesign/Imported Art/Rev02'

def actor(label):
    assert label in acts, 'missing actor ' + label
    return acts[label]

def bcenter(a):
    o, e = a.get_actor_bounds(False, True)
    return o

def rot2(v, deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return (v[0] * c - v[1] * s, v[0] * s + v[1] * c)

def move(labels, anchor, target, dyaw=0.0, dz=0.0):
    """Rigidly move actors: rotate by dyaw about the anchor's bounds centre, translate that centre to target (x, y)."""
    p = bcenter(actor(anchor))
    names = set(labels)
    for lab in labels:
        a = actor(lab)
        par = a.get_attach_parent_actor()
        if par and par.get_actor_label() in names: continue          # follows its parent
        if par: a.detach_from_actor(unreal.DetachmentRule.KEEP_WORLD, unreal.DetachmentRule.KEEP_WORLD, unreal.DetachmentRule.KEEP_WORLD)
        l, r = a.get_actor_location(), a.get_actor_rotation()
        d = rot2((l.x - p.x, l.y - p.y), dyaw)
        a.modify()
        a.set_actor_location_and_rotation(unreal.Vector(target[0] + d[0], target[1] + d[1], l.z + dz),
                                          unreal.Rotator(roll=r.roll, pitch=r.pitch, yaw=r.yaw + dyaw), False, True)
        if par: a.attach_to_actor(par, '', unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, False)

def place(label, center, dyaw=0.0):
    """Turn an actor by dyaw about its bounds centre and put that centre at center (x, y, z)."""
    a = actor(label); p = bcenter(a); l, r = a.get_actor_location(), a.get_actor_rotation()
    d = rot2((l.x - p.x, l.y - p.y), dyaw)
    a.modify()
    a.set_actor_location_and_rotation(unreal.Vector(center[0] + d[0], center[1] + d[1], center[2] + (l.z - p.z)),
                                      unreal.Rotator(roll=r.roll, pitch=r.pitch, yaw=r.yaw + dyaw), False, True)

def duplicate(label, new_label):
    """A second static instance of an existing dressing actor (same mesh, materials, scale, folder)."""
    a = actor(label); c = a.static_mesh_component
    b = A.spawn_actor_from_object(c.static_mesh, a.get_actor_location(), a.get_actor_rotation())
    b.set_actor_label(new_label); b.set_folder_path(str(a.get_folder_path())); b.set_actor_scale3d(a.get_actor_scale3d())
    for i in range(c.get_num_materials()): b.static_mesh_component.set_material(i, c.get_material(i))
    b.static_mesh_component.set_collision_profile_name(c.get_collision_profile_name())
    acts[new_label] = b
    return b

def destroy(*labels):
    for lab in labels:
        A.destroy_actor(actor(lab)); acts.pop(lab)

def spawn(path, loc, yaw, label, mats=None, collision=True, folder=FOLDER):
    m = EAL.load_asset(path); assert m, path
    a = A.spawn_actor_from_object(m, unreal.Vector(*loc), unreal.Rotator(0, 0, yaw))
    a.set_actor_label(label); a.set_folder_path(folder)
    c = a.static_mesh_component
    if not collision: c.set_collision_profile_name('NoCollision')
    for i, mt in enumerate(mats or []):
        if mt: c.set_material(i, mt)
    acts[label] = a
    return a

def mats_like(old_label):
    c = actor(old_label).static_mesh_component
    return [c.get_material(i) for i in range(c.get_num_materials())]

# ---------------- living / dining (north-east) ----------------
move(['Art_LV_Sofa'], 'Art_LV_Sofa', (852, 222))
# FIX-005: LV-SOFA-02 keeps LV-SOFA-01's origin, -Y front and envelope, so it swaps in at the actor's transform; its 13
# UCX hulls replace the old collision. Slot order comes from the imported mesh; materials per the README contract.
sofa = actor('Art_LV_Sofa'); sofa.modify()
sm2 = EAL.load_asset(R2 + 'LV_Sofa02/LV_SOFA_02'); sofa.static_mesh_component.set_static_mesh(sm2)
for i, slot in enumerate(sm2.static_materials):
    n = str(slot.material_slot_name); assert n.startswith('Sofa02_'), n
    sofa.static_mesh_component.set_material(i, EAL.load_asset(R2 + 'Materials/MI_' + n))
move(['Art_LV_Chair_03'], 'Art_LV_Chair_03', (977.45, 94.45))
# FIX-013: LV-ARMCHAIR-02 keeps LV-CHAIR-01's origin, facing and envelope; swap at the actor transform (identity kept).
if EAL.does_asset_exist(R2 + 'LV_Armchair02/LV_ARMCHAIR_02'):
    ch = actor('Art_LV_Chair_03'); ch.modify(); am = EAL.load_asset(R2 + 'LV_Armchair02/LV_ARMCHAIR_02')
    ch.static_mesh_component.set_static_mesh(am)
    for i, slot in enumerate(am.static_materials):
        ch.static_mesh_component.set_material(i, EAL.load_asset(R2 + 'Materials/MI_' + str(slot.material_slot_name)))
move(['Art_LV_Coffee_04'], 'Art_LV_Coffee_04', (970, 235), 90)
move(['Art_LV_Rug_LV_RUG_01'], 'Art_LV_Rug_LV_RUG_01', (985, 215), 90)       # FIX-005 rug rect [8.95,0.90,1.80,2.50]
move(['Art_LV_Book_LV_BOOK_CASE', 'Art_LV_Book_LV_BOOK_BOOKS', 'Art_LV_Book_LV_BOOK_PLANT', 'Art_LV_Book_LV_BOOK_TIN'],
     'Art_LV_Book_LV_BOOK_CASE', (515, 92.5), -90)
move(['Art_LV_TV_LV_TV_body', 'Art_LV_TV_LV_TV_left', 'Art_LV_TV_LV_TV_right', 'Art_LV_TV_LV_TV_screen_off', 'TV'],
     'Art_LV_TV_LV_TV_body', (1165, 205))
move(['Art_LV_SideTable_LV_SIDE_TABLE_BODY', 'Art_LV_SideTable_LV_SIDE_TABLE_DRAWER', 'Art_LV_TableLamp_LV_TableLampBody',
      'Art_LV_TableLamp_LV_TableLampBulb', 'Art_LV_TableLamp_LV_TableLampShade', 'FloorLamp'],
     'Art_LV_SideTable_LV_SIDE_TABLE_BODY', (848.5, 357.55))
move(['Art_HA_Plant', 'Art_HA_PlantStand_LV_Plant_Stand', 'Art_HA_PlantStand_Riser'], 'Art_HA_PlantStand_LV_Plant_Stand', (1105, 50))
# FIX-014: LV-PLANT-02 keeps the original pot origin, so it swaps in at the plant actor's transform; stand/riser untouched.
if EAL.does_asset_exist(R2 + 'LV_Plant02/LV_Plant02'):
    pl = actor('Art_HA_Plant'); pl.modify(); pm2 = EAL.load_asset(R2 + 'LV_Plant02/LV_Plant02')
    pl.static_mesh_component.set_static_mesh(pm2)
    for i, slot in enumerate(pm2.static_materials):
        n = ''.join(ch if ch.isalnum() else '_' for ch in str(slot.material_slot_name))
        pl.static_mesh_component.set_material(i, EAL.load_asset(R2 + 'Materials/MI_LVPlant02_' + n))
    so, se = actor('Art_HA_PlantStand_LV_Plant_Stand').get_actor_bounds(False)
    po, pe = pl.get_actor_bounds(False)
    unreal.log('[Rev02 plant] origin %.1f cm above stand floor (expect 51.1 with riser); foliage x %.1f-%.1f y %.1f-%.1f z %.1f-%.1f' % (
        pl.get_actor_location().z - (so.z - se.z), po.x - pe.x, po.x + pe.x, po.y - pe.y, po.y + pe.y, po.z - pe.z, po.z + pe.z))
move(['Art_LV_Radiator'], 'Art_LV_Radiator', (855, 27.7))
move(['Art_LV_Curtain_Rod', 'Art_LV_Curtain_Left', 'Art_LV_Curtain_Right'], 'Art_LV_Curtain_Rod', (855, 17))
destroy('Art_LV_Chest_LV_CHEST_BODY', 'Art_LV_Chest_LV_CHEST_LID')          # omitted to keep circulation open
# Dining group turns 90 deg about the table so the end chairs sit north/south.
move(['Art_KI_Table_12', 'Art_KI_Chair_13', 'Art_KI_Chair_14', 'Art_KI_Bowl_KI_Bowl', 'Art_KI_Bowl_Apple_A', 'Art_KI_Bowl_Apple_B',
      'Art_KI_Bowl_Lemon_A', 'Art_KI_Bowl_Lemon_B', 'Art_KI_Bowl_Pear', 'Art_KI_Mug_KI_Mug_01'], 'Art_KI_Table_12', (652.5, 250), 90)
place('Art_LV_Art04_LV_ART_04', (1192.25, 201, 178), 180)                     # landscape over TV
duplicate('Art_LV_Art04_LV_ART_04', 'Art_LV_Art04_Bookcase'); place('Art_LV_Art04_Bookcase', (487.75, 189.5, 169), 180)  # beside bookcase, faces east

# FIX-026: LV-SIDE-TABLE-01's FBX carries no texture (its walnut image ran through shader nodes the FBX exporter
# drops), so the import left flat Phong colours. Slots get the shared walnut finish (same PNG), a darker interior
# variant, and the source's edge/brass constants. Placement, drawer action and collision untouched.
_SLOT = {'aged_painterly_walnut': '/Game/ICanFixHim/Environment/Redesign/Finishes/MI_Walnut_MutedB',
         'fine_worn_wood_edges': R2 + 'Materials/MI_Rev02_WoodEdges', 'drawer_interior': R2 + 'Materials/MI_Rev02_DrawerInterior',
         'aged_brass': R2 + 'Materials/MI_Rev02_TableBrass'}
_norm = lambda n: ''.join(ch if ch.isalnum() else '_' for ch in n.lower()).strip('_')
for lab in ('Art_LV_SideTable_LV_SIDE_TABLE_BODY', 'Art_LV_SideTable_LV_SIDE_TABLE_DRAWER'):
    c = actor(lab).static_mesh_component; actor(lab).modify()
    for i, sl in enumerate(c.static_mesh.static_materials):
        k = _norm(str(sl.material_slot_name))
        assert k in _SLOT, (lab, k)
        c.set_material(i, EAL.load_asset(_SLOT[k]))

# ---------------- entry / hall ----------------
# Wyatt's fuse box (FIX-004): living north wall above the corner plant, facing south (was the living south wall facing
# north). Schedule :043 rect [10.825,0.06,0.45,0.14], box bottom 1.40 m: shell back on the north plaster face (y 6),
# centre x 11.05. The door, its interactable, the malady and its attached damage/wire states move rigidly with it,
# so the source's left hinge becomes the west hinge (opening away from the east corner).
FUSE = ['Art_LV_Fuse_Shell', 'Art_LV_Fuse_Door', 'FuseBox_Door', 'Malady_FuseBox']
fo, fe = actor('Art_LV_Fuse_Shell').get_actor_bounds(False, True)
move(FUSE, 'Art_LV_Fuse_Shell', (1105, 6 + 7), 180, dz=140 - (fo.z - fe.z))
move(['Art_HA_Bench_HA_BENCH_01', 'Art_HA_Shoes_HA_Oxford_1', 'Art_HA_Shoes_HA_Oxford_2', 'Art_HA_Shoes_HA_ShoeTray',
      'Art_HA_Shoes_HA_SlipOn_1', 'Art_HA_Shoes_HA_SlipOn_2'], 'Art_HA_Bench_HA_BENCH_01', (1172.5, 302.5), -90)
# Coat hooks + coat centred in the space freed between the TV and the entry (FIX-004, :042 y 2.94-3.66); bench stays.
move(['Art_HA_Hooks_HA_Hooks', 'Art_HA_Coat_HA_Coat'], 'Art_HA_Hooks_HA_Hooks', (1190.5, 330), 90)
move(['Art_HA_EndCabinet_HA_CABINET_BODY', 'Art_HA_EndCabinet_HA_CABINET_DOOR_L', 'Art_HA_EndCabinet_HA_CABINET_DOOR_R',
      'Art_HA_EndCabinet_HA_CABINET_DRAWER', 'Art_HA_Vase02_HA_VASE_02', 'HallCabinet_Door_L', 'HallCabinet_Door_R', 'HallCabinet_Drawer'],
     'Art_HA_EndCabinet_HA_CABINET_BODY', (240.4, 470))
place('Art_HA_Art09_HA_ART_09', (227.75, 469, 162.5))
move(['Art_HA_Console_HA_CONSOLE_BODY', 'Art_HA_Console_HA_CONSOLE_DRAWER', 'Art_HA_Flowers', 'Art_HA_Vase', 'Console_Drawer'],
     'Art_HA_Console_HA_CONSOLE_BODY', (837.5, 539.5), 180)
place('Art_HA_Art03_HA_ART_03', (832.5, 550.75, 161), 180)                     # above the side console
duplicate('Art_HA_Art03_HA_ART_03', 'Art_HA_Art03_Gallery'); place('Art_HA_Art03_Gallery', (376.5, 387.75, 174), 180)
place('Art_HA_Art02_HA_ART_02', (289, 387.75, 170.5))                          # small gallery print
duplicate('Art_HA_Art02_HA_ART_02', 'Art_HA_Art02_Hall'); place('Art_HA_Art02_Hall', (481, 550.75, 171.5), 180)
duplicate('Art_HA_Art02_HA_ART_02', 'Art_HA_Art02_Entry'); place('Art_HA_Art02_Entry', (1192.25, 56, 167.5), 90)
# Sconces: hall warm sconce (south-facing, kitchen/hall wall) and entry sconce (east wall, west-facing).
move(['Art_HA_Sconce01_HA_Sconce_Bulb', 'Art_HA_Sconce01_HA_Sconce_Hardware', 'Art_HA_Sconce01_HA_Sconce_Shade', 'Sconce_Hall_1'],
     'Art_HA_Sconce01_HA_Sconce_Hardware', (453, 391))
move(['Art_HA_Sconce02_HA_Sconce_Bulb', 'Art_HA_Sconce02_HA_Sconce_Hardware', 'Art_HA_Sconce02_HA_Sconce_Shade', 'Sconce_Hall_2'],
     'Art_HA_Sconce02_HA_Sconce_Hardware', (1189, 531), 90)
# Ceiling fixtures (elevation schedule): living, hall, kitchen keep the three clickable lights.
for name, xy in [('Living', (840, 280)), ('HallWest', (455, 470)), ('HallEast', (240, 190))]:
    move(['Art_CeilingLight_%s_Glass' % name, 'Art_CeilingLight_%s_Hardware' % name, 'CeilingLight_' + name],
         'Art_CeilingLight_%s_Hardware' % name, xy)
for name, xy in [('Bedroom', (240, 757.5)), ('Bath', (635, 757.5)), ('Office', (995, 757.5))]:   # static fixtures
    for part in ('Hardware', 'Glass'):
        b = duplicate('Art_CeilingLight_Living_' + part, 'Art_CeilingLight_%s_%s' % (name, part))
        b.set_actor_hidden_in_game(False); b.static_mesh_component.set_visibility(True)
        b.set_actor_location(unreal.Vector(xy[0], xy[1], 275), False, True)

# ---------------- kitchen (west) ----------------
move(['Art_KI_Fridge_Body', 'Art_KI_Fridge_Door', 'Fridge_Door'], 'Art_KI_Fridge_Body', (73.5, 52.5))
move(['Art_KI_Range_Body', 'Art_KI_Range_Door', 'Oven_Door', 'Stove_Burner', 'Art_KI_Kettle_KI_Kettle_Body', 'Art_KI_Kettle_KI_Kettle_Lid'],
     'Art_KI_Range_Body', (382.5, 51.6))
move(['Art_KI_Pantry_Body', 'Art_KI_Pantry_LeftDoor', 'Art_KI_Pantry_RightDoor', 'Pantry_Door_L', 'Pantry_Door_R'],
     'Art_KI_Pantry_Body', (48.9, 285), 180)
move(['Art_KI_Upper_Body', 'Art_KI_Upper_LeftDoor', 'Art_KI_Upper_RightDoor', 'Cupboard_Door_L', 'Cupboard_Door_R'],
     'Art_KI_Upper_Body', (458, 75), 90)
move(['Art_KI_PanRail_KI_Pan_Rail_Assembly', 'Art_KI_Pan_A_KI_Pan_Body', 'Art_KI_Pan_A_KI_Pan_Handle', 'Art_KI_Pan_B_KI_Pan_Body',
      'Art_KI_Pan_B_KI_Pan_Handle'], 'Art_KI_PanRail_KI_Pan_Rail_Assembly', (470.5, 170), 90)
place('Art_KI_Art01_KI_ART_01', (244.5, 372.25, 160), 90)                      # breakfast still life, south wall

# Sink: KI-SINK-NARROW-01 at plan x=2.15, rear-bound aligned (origin plan y=0.4605, window sink-fit validation).
SINK = (215, 46.05, 0)
sage = EAL.load_asset(F + 'MI_Cabinet_Sage')
old_sink = actor('Art_KI_SINK_body').get_actor_location()
# FIX-003 (KI-LEAK-02): the clean body replaces the old body with its baked-in pail; same origin, slots and approved
# materials. The vintage pail and its still water are separate, baked at the same assembly origin, and stay after
# Lukey's repair (environment level); the pail keeps its 13 UCX hulls, the water has no collision.
old_body = EAL.load_asset(R2 + 'KI_SinkNarrow/KI_SINK_NARROW_body')
by_slot = {str(sm.material_slot_name): sm.material_interface for sm in old_body.static_materials}
# FIX-027: KI-FAUCET-02 is the clean body with only the faucet rebuilt (same origin, slots, non-faucet faces).
BODY = R2 + ('KI_Faucet02/KI_FAUCET_02_sink_body' if EAL.does_asset_exist(R2 + 'KI_Faucet02/KI_FAUCET_02_sink_body') else 'KI_Leak02/KI_LEAK_02_sink_body')
body = spawn(BODY, SINK, 0, 'Art_KI_SinkNarrow_body')
for i, sm in enumerate(EAL.load_asset(BODY).static_materials):
    assert str(sm.material_slot_name) in by_slot, sm.material_slot_name
    body.static_mesh_component.set_material(i, by_slot[str(sm.material_slot_name)])
MATS = R2 + 'Materials/'
pail = spawn(R2 + 'KI_Leak02/KI_LEAK_02_bucket', SINK, 0, 'Art_KI_Leak_Bucket',
             mats=[EAL.load_asset(MATS + n) for n in ('MI_Rev02_Zinc', 'MI_Rev02_ZincSeams', 'MI_Rev02_IronBail')])
water = spawn(R2 + 'KI_Leak02/KI_LEAK_02_bucket_water', SINK, 0, 'Art_KI_Leak_BucketWater', collision=False,
              mats=[EAL.load_asset(MATS + 'MI_Rev02_BucketWater')])
water.static_mesh_component.set_cast_shadow(False)
for a in (body, pail, water): a.static_mesh_component.set_editor_property('receives_decals', False)
for side in ('L', 'R'):
    if EAL.does_asset_exist(R2 + 'KI_Faucet02/KI_FAUCET_02_%s_tap' % side):   # FIX-027 coaxial taps, pivots baked in assembly space
        tap = spawn(R2 + 'KI_Faucet02/KI_FAUCET_02_%s_tap' % side, SINK, 0, 'Art_KI_SinkNarrow_%s_tap' % side)
        _old = EAL.load_asset(R2 + 'KI_SinkNarrow/KI_SINK_NARROW_body')
        _bs = {str(m.material_slot_name): m.material_interface for m in _old.static_materials}
        for i, sl in enumerate(tap.static_mesh_component.static_mesh.static_materials):
            if str(sl.material_slot_name) in _bs: tap.static_mesh_component.set_material(i, _bs[str(sl.material_slot_name)])
    else:
        spawn(R2 + 'KI_SinkNarrow/KI_SINK_NARROW_%s_tap' % side, SINK, 0, 'Art_KI_SinkNarrow_%s_tap' % side)
# Lukey: the malady keeps its offset from the sink origin; its overlays (sink damage, wall stain) follow and are
# then set to the new sink's damage mesh and the scheduled stain position (north wall x 3.12-3.82, z 1.20-1.67).
mal = actor('Malady_Sink'); ml = mal.get_actor_location()
mal.modify(); mal.set_actor_location(unreal.Vector(SINK[0] + ml.x - old_sink.x, SINK[1] + ml.y - old_sink.y, ml.z), False, True)
# The old static damage mesh (beads + opaque puddle) is retired; Art_KI_SINK_damage becomes the residual-spill decal
# (T_Leak_Puddle_Mask, 68.2221 x 86.1652 cm, centre UE-local (-8.29865, 29.8254, 0.4) in sink assembly space). It keeps
# the label, RepairDamage/lukey tags and the attachment to Lukey's malady, and adds AuthoredLeakDamage,
# which tells AFixHimMalady to skip its procedural floor cylinder and sphere drop (rev02_05 sets the drip points).
old = actor('Art_KI_SINK_damage'); tags = list(old.tags) + [unreal.Name('AuthoredLeakDamage')]
folder = str(old.get_folder_path()); destroy('Art_KI_SINK_damage')
assert L.set_current_level_by_name('L_Apartment_Rev02_Gameplay')
dmg = A.spawn_actor_from_class(unreal.DecalActor, unreal.Vector(SINK[0] - 8.29865, SINK[1] + 29.8254, SINK[2] + 0.4),
                               unreal.Rotator(roll=0, pitch=-90, yaw=0))
assert L.set_current_level_by_name('L_Apartment_Rev02')
dmg.set_actor_label('Art_KI_SINK_damage'); dmg.set_folder_path(folder); dmg.tags = tags
dc = dmg.decal
dc.set_decal_material(EAL.load_asset(MATS + 'M_Rev02_LeakPuddleDecal'))
# pitch -90 projects down: decal local Z lies along world +X (image width), local Y along world Y (image height).
dc.set_editor_property('decal_size', unreal.Vector(3.0, 86.1652 / 2, 68.2221 / 2))
dc.set_editor_property('sort_order', 1)
dmg.attach_to_actor(mal, '', unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, False)
acts['Art_KI_SINK_damage'] = dmg
# wet sheen: roughness-only decal on the same mask/transform (see rev02_02b), same repair tags and attachment
assert L.set_current_level_by_name('L_Apartment_Rev02_Gameplay')
wet = A.spawn_actor_from_class(unreal.DecalActor, dmg.get_actor_location(), dmg.get_actor_rotation())
assert L.set_current_level_by_name('L_Apartment_Rev02')
wet.set_actor_label('Art_KI_SINK_damage_Wet'); wet.set_folder_path(folder); wet.tags = tags
wet.decal.set_decal_material(EAL.load_asset(MATS + 'M_Rev02_LeakPuddleWet'))
wet.decal.set_editor_property('decal_size', dc.get_editor_property('decal_size')); wet.decal.set_editor_property('sort_order', 2)
wet.attach_to_actor(mal, '', unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, False)
acts['Art_KI_SINK_damage_Wet'] = wet
place('Art_KI_Wall_Stain', (347, 6.25, 143.5))
destroy('Art_KI_SINK_body', 'Art_KI_SINK_L_door', 'Art_KI_SINK_R_door', 'Art_KI_SINK_L_drawer', 'Art_KI_SINK_R_drawer',
        'Art_KI_SINK_L_tap', 'Art_KI_SINK_R_tap')

# KI-CABINET-02 fitted base cabinets (assembly-space parts share each body's floor-centre origin; front +Y = south).
cab_mats = mats_like('Art_KI_Cabinet_body')
for code, x in [('0425', 141.25), ('0775', 306.25), ('0450', 442.5)]:
    parts = ['body', 'door', 'drawer'] if code != '0775' else ['body', 'door_L', 'door_R', 'drawer_L', 'drawer_R']
    for p in parts:
        a = spawn(R2 + 'KI_Cabinet02/KI_CAB_%s_%s' % (code, p), (x, 47.5, 0), 0, 'Art_KI_Cab%s_%s' % (code, p))
        a.static_mesh_component.set_material(0, sage)          # verified sage cabinet finish; other slots keep source mats
destroy('Art_KI_Cabinet_body', 'Art_KI_Cabinet_door', 'Art_KI_Cabinet_drawer')
# Counter dressing: worktop now 91 cm (was 96).
place('Art_KI_Jar_KI_Jar_Body', (141.25, 40, 101)); place('Art_KI_Jar_KI_Jar_Lid', (141.25, 40, 113.5))
place('Art_KI_Pottery_KI_Pottery_01', (442.5, 38, 103)); place('Art_KI_Geranium_KI_Geranium', (330, 40, 110))
# Backsplash (KI-BACKSPLASH-01): x 1.20-1.625 and 2.675-4.65 on the north wall, 0.91-1.15 m (kept under the apron).
mod, endl, endr = actor('Art_KI_Backsplash_Module_1m'), actor('Art_KI_Backsplash_End_Left'), actor('Art_KI_Backsplash_End_Right')
def seat(a, x0, x1, z0, z1, sx):
    """Scale and place a backsplash piece so its bounds span x0..x1, z0..z1 (yaw 0, against the wall)."""
    a.modify(); a.set_actor_scale3d(unreal.Vector(sx, 1, (z1 - z0) / 56.0))
    o, e = a.get_actor_bounds(False); l = a.get_actor_location()
    a.set_actor_location(unreal.Vector(l.x + (x0 + x1) / 2 - o.x, l.y, l.z + (z0 + z1) / 2 - o.z), False, True)
segs = [(120, 162.5), (267.5, 366.25), (366.25, 465)]
for i, (x0, x1) in enumerate(segs):
    a = mod if i == 0 else duplicate('Art_KI_Backsplash_Module_1m', 'Art_KI_Backsplash_Module_%d' % i)
    seat(a, x0, x1, 91, 115, (x1 - x0) / 100.0)
for i, (x0, x1) in enumerate([(118.5, 121.5), (161, 164), (266, 269), (463.5, 466.5)]):
    a = (endl if i == 0 else endr if i == 3 else duplicate('Art_KI_Backsplash_End_Left', 'Art_KI_Backsplash_End_%d' % i))
    seat(a, x0, x1, 91, 115, 1.0)
# Breakfast wall table and tucked stool (south wall, front north).
tm = mats_like('Art_KI_Table_12')
spawn(R2 + 'KI_WallTable02/KI_WALL_TABLE_02', (245, 345.5, 0), 180, 'Art_KI_WallTable02')
spawn(R2 + 'KI_Stool02/KI_STOOL_02', (245, 350, 0), 180, 'Art_KI_Stool02')

# ---------------- bedroom / walk-in closet ----------------
move(['Art_BR_Bed', 'Bed'], 'Art_BR_Bed', (235, 835))
for side, xy in [('W', (122.5, 907.5)), ('E', (347.5, 907.5))]:
    move(['Art_BR_Nightstand_%s_BR_NIGHTSTAND_BODY' % side, 'Art_BR_Nightstand_%s_BR_NIGHTSTAND_DRAWER' % side,
          'Art_BR_Lamp_%s_BR_LampBody' % side, 'Art_BR_Lamp_%s_BR_LampBulb' % side, 'Art_BR_Lamp_%s_BR_LampShade' % side,
          'Nightstand_Drawer_' + side, 'BedLamp' if side == 'W' else 'BedLamp_E'],
         'Art_BR_Nightstand_%s_BR_NIGHTSTAND_BODY' % side, xy)
move(['Art_BR_Dresser_BR_Dresser_body', 'Art_BR_Dresser_BR_Dresser_drawer1', 'Art_BR_Dresser_BR_Dresser_drawer2',
      'Art_BR_Dresser_BR_Dresser_drawer3', 'Art_BR_Dresser_BR_Dresser_mirror', 'Art_BR_Perfume_BR_Perfume_Body',
      'Art_BR_Perfume_BR_Perfume_Stopper', 'Dresser_Drawer', 'Dresser_Drawer_1', 'Dresser_Drawer_2'], 'Art_BR_Dresser_BR_Dresser_body', (445, 792.5))
move(['Art_OF_Bookcase_OF_BOOKCASE_BODY'], 'Art_OF_Bookcase_OF_BOOKCASE_BODY', (30, 700), 180)
place('Art_BR_ArtFloral_BR_ART_FLORAL_01', (227, 567.75, 167.5))
for lab, c, dyaw in [('Art_BR_ArtFloral_Bookcase', (7.75, 679, 162.5), -90), ('Art_BR_ArtFloral_Dresser', (472.25, 637.5, 170), 90),
                     ('Art_BR_ArtFloral_Headboard', (214, 947.25, 181), 180)]:
    duplicate('Art_BR_ArtFloral_BR_ART_FLORAL_01', lab); place(lab, c, dyaw)
# BR-CLOSET-02 walk-in kit at the hall end; assembly origin plan (1.10, 4.70). No shell (rev02_03 built it).
CL = (110, 470, 0)
for p in ('Trim', 'Bulb'):
    spawn(R2 + 'BR_Closet02/BR_Closet02_' + p, CL, 0, 'Art_BR_Closet02_' + p, collision=(p != 'Bulb'))
# FIX-002: BR-CLOSET-STORAGE-03 full-length west/east shelf + rail + hooked hangers (14 UCX each; hangers have none)
# supersede BR_Closet02_Shelf, which is no longer placed.
for side in ('West', 'East'):
    spawn(R2 + 'BR_ClosetStorage03/BR_ClosetStorage03_' + side, CL, 0, 'Art_BR_ClosetStorage03_' + side)
destroy('Art_BR_Closet_Body', 'Art_BR_Closet_Door_L', 'Art_BR_Closet_Door_R')
# Doors keep the old labels (Wardrobe_Door_L/R bind to them); hinge-local meshes at assembly offsets (-/+50, +97.8).
spawn(R2 + 'BR_Closet02/BR_Closet02_Door_L', (CL[0] - 50, CL[1] + 97.8, 0), 0, 'Art_BR_Closet_Door_L')
spawn(R2 + 'BR_Closet02/BR_Closet02_Door_R', (CL[0] + 50, CL[1] + 97.8, 0), 0, 'Art_BR_Closet_Door_R')
# Malcolm: the malady keeps its relation to the mold overlay, which becomes the new kit's mold on the north wall.
mold = actor('Art_BR_Closet_Mold'); old_mold = bcenter(mold)
mm = actor('Malady_Mold'); l = mm.get_actor_location()
mm.modify(); mm.set_actor_location(unreal.Vector(l.x + 110 - old_mold.x, l.y + 386.3 - old_mold.y, l.z + 130 - old_mold.z), False, True)
# FIX-001 (BR-MOLD-02): two charcoal planes at the closet origin replace the central mold - the back plane keeps the
# Art_BR_Closet_Mold label/tags, the east return is a second overlay with the same tags, both attached to Malcolm so
# repair hides them. Matte neutral-charcoal material (rev02_02b); no collision, no shadow.
mold02 = EAL.load_asset(R2 + 'Materials/M_Rev02_Mold02')
mold.modify(); mold.static_mesh_component.set_static_mesh(EAL.load_asset(R2 + 'BR_Mold02/BR_Mold02_Back'))
mold.static_mesh_component.set_material(0, mold02)
assert L.set_current_level_by_name('L_Apartment_Rev02_Gameplay')
ret = spawn(R2 + 'BR_Mold02/BR_Mold02_Return', CL, 0, 'Art_BR_Closet_Mold_Return', mats=[mold02], collision=False,
            folder=str(mold.get_folder_path()))
assert L.set_current_level_by_name('L_Apartment_Rev02')
ret.tags = list(mold.tags)
for a in (mold, ret):
    c = a.static_mesh_component
    c.set_mobility(unreal.ComponentMobility.MOVABLE); c.set_collision_profile_name('NoCollision'); c.set_cast_shadow(False)
mold.set_actor_location_and_rotation(unreal.Vector(*CL), unreal.Rotator(0, 0, 0), False, True)
ret.attach_to_actor(actor('Malady_Mold'), '', unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, False)
bulb = actor('Bulb_Closet'); bulb.modify(); bulb.set_actor_location(unreal.Vector(114, 468, 200), False, True)
# FIX-021 (Malcolm): the closet bulb hangs ~39 cm above his face in dialogue; as a 2 cm point source it painted sharp
# white specular streaks on brow/eyelids. A frosted-bulb source (8 cm) with reduced specular keeps the closet lit
# without facial hotspots. Only this light changes.
# User request: a much dimmer, warmly glowing incandescent bulb - 60 lm at 2300 K (was 200 lm near-neutral), and the
# bulb glass gets a soft warm emissive so the bulb itself reads as lit.
for _lc in bulb.get_components_by_class(unreal.PointLightComponent):
    _lc.set_editor_property('source_radius', 8.0); _lc.set_editor_property('specular_scale', 0.35)
    _lc.set_editor_property('intensity', 60.0); _lc.set_editor_property('use_temperature', True)
    _lc.set_editor_property('temperature', 2300.0); _lc.set_editor_property('light_color', unreal.Color(255, 255, 255, 255))
_bm = actor('Art_BR_Closet02_Bulb').static_mesh_component
for _i, _sl in enumerate(_bm.static_mesh.static_materials):
    if str(_sl.material_slot_name) == 'Warm_Bulb': _bm.set_material(_i, EAL.load_asset(R2 + 'Materials/M_Rev02_BulbGlow'))
move(['Art_BR_ClosetBox_BR_BOX_BODY', 'Art_BR_ClosetBox_BR_BOX_LID'], 'Art_BR_ClosetBox_BR_BOX_BODY', (21, 435), 90)

# ---------------- coat closet + guest wardrobe (ARC-SLIDING-CLOSET-02 panels, ARC-CLOSET-STORAGE-02) ----------------
for room, y, yaw in [('Coat', 560, 180), ('Office', 715, 0)]:
    destroy('Art_%sCloset_LeftPanel' % room, 'Art_%sCloset_RightPanel' % room)
    for side, off in [('Left', (-22, 2.8)), ('Right', (22, -2.8))]:
        d = rot2(off, yaw)
        spawn(R2 + 'ARC_Sliding02/ARC_Sliding02_%sPanel' % side, (1138 + d[0], y + d[1], 0), yaw, 'Art_%sCloset_%sPanel' % (room, side))
spawn(R2 + 'ARC_ClosetStorage02/ARC_ClosetStorage02', (1137.5, 634, 0), 180, 'Art_CoatCloset_Storage')
spawn(R2 + 'ARC_ClosetStorage02/ARC_ClosetStorage02', (1137.5, 646, 0), 0, 'Art_OfficeCloset_Storage')

# ---------------- office art ----------------
place('Art_OF_ArtLandscape_OF_ART_LANDSCAPE_01', (882.5, 567.75, 172), 90)
place('Art_OF_ArtBotanical_OF_ART_BOTANICAL_01', (797.75, 795, 172), 180)
# East botanical bottom at 1.65 m (not the first schedule's 1.50 m), so it clears the east display shelf below it.
duplicate('Art_OF_ArtBotanical_OF_ART_BOTANICAL_01', 'Art_OF_ArtBotanical_East'); place('Art_OF_ArtBotanical_East', (1192.25, 797.5, 165 + 27.5), 180)

marker = A.spawn_actor_from_class(unreal.Note, unreal.Vector(0, 0, -500)); marker.set_actor_label('Rev02_Furnished'); marker.set_folder_path(FOLDER)
assert L.save_all_dirty_levels()
unreal.log('[Rev02 furnish] saved')
