"""Rev02 step 5i (FIX-033/034/036): CABINET-JOINERY-02 replaces the kitchen base cabinets (KI-CABINET-02 0425/0450/0775),
the upper cupboard (KI-UPPER-01), the pantry (KI-PANTRY-01) and the bathroom linen cabinet (BA-LINEN-01).

assembly.json contract: every export is identity. Bodies and drawers keep assembly-origin vertices, so they swap in
place (same actor transforms, the drawers keep their roots, slide axis and travel; their Body keeps its closed-pose
world transform). Doors are pivot-local: each door interactable's root goes to the assembly transform applied to
(100x, -100y, 100z) of its NEW pivot_source_m (hinge axis on the back plane at the hinge edge), with the assembly's
rotation and its Body at identity; the old pivot offsets are not reused. Swing travel per the README table (linen
lower 60 to clear the basin, upper 90, others 100). Labels, prompts, rooms and SFX are kept. Every slot is mapped
explicitly (MI_Joinery_*); Counter_Ivory keeps the installed engine finish. Hidden art source copies are updated
to match. Upper/pantry/linen bodies keep complex collision (no UCX). Re-runnable. Run after rev02_05h.
"""
import unreal
EAL = unreal.EditorAssetLibrary
A = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
R2 = '/Game/ICanFixHim/Environment/Rev02/'
KIT, MATS = R2 + 'Joinery02/', R2 + 'Materials/'
acts = {a.get_actor_label(): a for a in A.get_all_level_actors()}
log = []

def actor(l):
    assert l in acts, l
    return acts[l]

def dress(comp, sm, counter=None):
    for i, s in enumerate(sm.static_materials):
        n = str(s.material_slot_name)
        if n == 'Counter_Ivory':
            assert counter is not None; comp.set_material(i, counter)
        elif n == 'Toe_Dark':
            comp.set_material(i, EAL.load_asset(MATS + 'MI_Joinery_ToeDark'))
        else:
            assert n.startswith('Joinery_'), n
            comp.set_material(i, EAL.load_asset(MATS + 'MI_' + n))

BODIES = {'0425': 'Art_KI_Cab0425_body', '0450': 'Art_KI_Cab0450_body', '0775': 'Art_KI_Cab0775_body',
          'Upper': 'Art_KI_Upper_Body', 'Pantry': 'Art_KI_Pantry_Body', 'Linen': 'Art_BA_Linen_BA_Linen_Body'}
BODY_MESH = {'0425': 'KI_Cab03_0425_Body', '0450': 'KI_Cab03_0450_Body', '0775': 'KI_Cab03_0775_Body',
             'Upper': 'KI_Upper02_Body', 'Pantry': 'KI_Pantry02_Body', 'Linen': 'BA_Linen02_Body'}
# assembly transforms are the (unchanged) body actors' transforms
ASM = {k: actor(v).get_actor_transform() for k, v in BODIES.items()}
for k, l in BODIES.items():
    b = actor(l); c = b.static_mesh_component; old = c.static_mesh
    counter = None
    if old:
        for i, s in enumerate(old.static_materials):
            if str(s.material_slot_name) == 'Counter_Ivory': counter = c.get_material(i)
    sm = EAL.load_asset(KIT + BODY_MESH[k]); b.modify(); c.set_static_mesh(sm); dress(c, sm, counter)
    log.append('%s body -> %s' % (l, BODY_MESH[k]))

DOORS = [  # label, hidden art copy, kit, mesh, pivot_source_m, engine yaw travel
    ('Cabinet_Door', 'Art_KI_Cab0425_door', '0425', 'KI_Cab03_0425_door', (-0.2025, -0.253, 0.0), 100),
    ('Cabinet_Door_2', 'Art_KI_Cab0450_door', '0450', 'KI_Cab03_0450_door', (-0.175, -0.253, 0.0), 100),
    # CABINET-JOINERY-03 single-leaf patch: leaf narrowed 32 mm on the hinge side, hinge back on the old 271.7 line, with
    # a fixed filler (static art below). TRAVEL is set from the installed sweep (see SINK_L_TRAVEL).
    ('Sink_Door_L', 'Art_KI_Cab0775_door_L', '0775', R2 + 'Joinery03/KI_Cab04_0775_door_L', (-0.3455, -0.253, 0.0), 'SINK_L_TRAVEL'),
    ('Sink_Door_R', 'Art_KI_Cab0775_door_R', '0775', 'KI_Cab03_0775_door_R', (0.3375, -0.253, 0.0), -100),
    ('Cupboard_Door_L', 'Art_KI_Upper_LeftDoor', 'Upper', 'KI_Upper02_LeftDoor', (-0.472, -0.167, 0.265), 100),
    ('Cupboard_Door_R', 'Art_KI_Upper_RightDoor', 'Upper', 'KI_Upper02_RightDoor', (0.472, -0.167, 0.265), -100),
    ('Pantry_Door_L', 'Art_KI_Pantry_LeftDoor', 'Pantry', 'KI_Pantry02_LeftDoor', (-0.47, -0.318, 1.02), 100),
    ('Pantry_Door_R', 'Art_KI_Pantry_RightDoor', 'Pantry', 'KI_Pantry02_RightDoor', (0.47, -0.318, 1.02), -100),
    ('Linen_Door_Lower', 'Art_BA_Linen_BA_Linen_LowerDoor', 'Linen', 'BA_Linen02_LowerDoor', (-0.278, -0.305, 0.565), 60),
    ('Linen_Door_Upper', 'Art_BA_Linen_BA_Linen_UpperDoor', 'Linen', 'BA_Linen02_UpperDoor', (-0.278, -0.305, 1.295), 90)]
SINK_L_TRAVEL = globals().get('SINK_L_TRAVEL', 100)   # 0-100 installed sweep clean (sink, filler, carcass, neighbours)
for label, art, kit, mesh, ps, yaw in DOORS:
    if yaw == 'SINK_L_TRAVEL': yaw = SINK_L_TRAVEL
    t = ASM[kit]; pivot = t.transform_location(unreal.Vector(100 * ps[0], -100 * ps[1], 100 * ps[2]))
    rot = t.rotation.rotator(); sm = EAL.load_asset(mesh if mesh.startswith('/') else KIT + mesh)
    a = actor(label); a.modify()
    a.set_actor_location_and_rotation(pivot, rot, False, True)
    pv = a.get_editor_property('pivot'); pv.set_relative_location(unreal.Vector(0, 0, 0), False, False)
    pv.set_relative_rotation(unreal.Rotator(0, 0, 0), False, False)
    b = a.get_editor_property('body'); b.set_static_mesh(sm)
    b.set_relative_location(unreal.Vector(0, 0, 0), False, False); b.set_relative_rotation(unreal.Rotator(0, 0, 0), False, False)
    b.set_relative_scale3d(unreal.Vector(1, 1, 1)); dress(b, sm)
    a.set_editor_property('toggle_rotation', unreal.Rotator(0, 0, float(yaw)))
    a.set_editor_property('use_authored_body_materials', True)
    h = actor(art); h.modify(); h.set_actor_location_and_rotation(pivot, rot, False, True)
    h.static_mesh_component.set_static_mesh(sm); dress(h.static_mesh_component, sm)
    log.append('%s pivot (%.1f,%.1f,%.1f) yaw %.0f travel %+d -> %s' % (label, pivot.x, pivot.y, pivot.z, rot.yaw, yaw, mesh.split('/')[-1]))

# fixed hinge-side filler for the 0775 left leaf: static art at the body assembly, never on the rotating door
if 'Art_KI_Cab0775_Filler' in acts: A.destroy_actor(acts.pop('Art_KI_Cab0775_Filler'))
assert L.set_current_level_by_name('L_Apartment_Rev02')
_fsm = EAL.load_asset(R2 + 'Joinery03/KI_Cab04_0775_Filler'); _t = ASM['0775']
_f = A.spawn_actor_from_object(_fsm, _t.translation, _t.rotation.rotator())
_f.set_actor_label('Art_KI_Cab0775_Filler'); _f.set_folder_path(str(actor(BODIES['0775']).get_folder_path())); acts['Art_KI_Cab0775_Filler'] = _f
dress(_f.static_mesh_component, _fsm); log.append('Art_KI_Cab0775_Filler static at the 0775 assembly')

DRAWERS = [('Kitchen_Drawer', 'Art_KI_Cab0425_drawer', 'KI_Cab03_0425_drawer'), ('Kitchen_Drawer_2', 'Art_KI_Cab0450_drawer', 'KI_Cab03_0450_drawer'),
           ('Sink_Drawer_L', 'Art_KI_Cab0775_drawer_L', 'KI_Cab03_0775_drawer_L'), ('Sink_Drawer_R', 'Art_KI_Cab0775_drawer_R', 'KI_Cab03_0775_drawer_R')]
for label, art, mesh in DRAWERS:
    sm = EAL.load_asset(KIT + mesh); a = actor(label); a.modify()
    b = a.get_editor_property('body'); h = actor(art)
    # closed assembly pose: same world transform as the hidden art copy (assembly origin), root/slide unchanged
    b.set_static_mesh(sm); b.set_world_location_and_rotation(h.get_actor_location(), h.get_actor_rotation(), False, False); dress(b, sm)
    a.set_editor_property('use_authored_body_materials', True)
    h.modify(); h.static_mesh_component.set_static_mesh(sm); dress(h.static_mesh_component, sm)
    log.append('%s body -> %s (root/slide kept)' % (label, mesh))

assert L.save_all_dirty_levels()
unreal.log('[Rev02 joinery]\n' + '\n'.join(log))
