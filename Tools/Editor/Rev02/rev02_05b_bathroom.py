"""Rev02 step 5b (FIX-007): bathroom fixture layout per feedback/FIX-007/placement-contract.json.

Every bathroom assembly shares one source origin across its parts (verified: body, taps, lids, doors and props carry
the same actor pivot), so each moves rigidly by its anchor pivot to the contract's assembly origin and facing:
parts, dressing and click actions keep their relation (Basin_Tap stream, Toilet_Lid hinge, Mirror_Sconces light).
Run after rev02_05 (gameplay) and before rev02_06. Tile treatment is rev02_05c.

  Basin :002      east wall facing west, origin (754.2, 792.5, 0)   Toilet :003  north wall facing south, (555, 603, 0)
  Linen :004      same SE origin (745, 905, 0) now facing north; two NEW hinged controls (none existed), 90 deg stop
  Basket :008     (512, 818, 0)                                     Mirror :076  east wall-floor origin (784, 792.5, 0)
  Shelves         :077 east (784, 710, 125), :080 east (784, 635, 125), :085 west (486, 695, 125); origin = shelf top
  Switch :079     north wall east of the door (760, 566, 124), decorative (no action, none existed)
  Ring :082       BA-HAND-TOWEL-RING-02 replaces the hook + hand towel, plate centre (784, 710, 115) facing west
  Roll :083       holder + paper (paper offset is baked in the mesh at the holder pivot) at (487.8, 613, 72) facing east
  Rail :084       single rail, west wall bar origin (486, 792.5, 125) facing east, ivory towel kept, rose towel removed;
                  duplicate rail :078 and its towel retired
  Tub             BA-TUB-FIXTURES-02: plumbing + both taps at (529.3, 832, 0) yaw -90 (tap pivots land on the
                  contract's (500.3, 916/898, 96)); rod and drain stay on the original fixture transform; the old
                  combined fixture is retired only after all three are placed. Tub_Faucet's body follows the left tap;
                  its reveal (bath water) stays in the tub. Shower_Curtain gathers at the EAST end and slides west.
"""
import math, unreal
EAL = unreal.EditorAssetLibrary
A = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
R2 = '/Game/ICanFixHim/Environment/Rev02/'
acts = {a.get_actor_label(): a for a in A.get_all_level_actors()}
assert 'Rev02_Bathroom07' not in acts, 'bathroom already rebuilt; re-run from rev02_01'

def actor(label):
    assert label in acts, 'missing ' + label
    return acts[label]

def rot2(dx, dy, deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return dx * c - dy * s, dx * s + dy * c

def move_pivot(labels, anchor, origin, yaw):
    """Rigidly move actors so the anchor's pivot lands on origin (x, y, z) with world yaw `yaw`."""
    p = actor(anchor).get_actor_location(); dyaw = yaw - actor(anchor).get_actor_rotation().yaw
    names = set(labels)
    for lab in labels:
        a = actor(lab); par = a.get_attach_parent_actor()
        if par and par.get_actor_label() in names: continue
        l, r = a.get_actor_location(), a.get_actor_rotation()
        dx, dy = rot2(l.x - p.x, l.y - p.y, dyaw)
        a.modify()
        a.set_actor_location_and_rotation(unreal.Vector(origin[0] + dx, origin[1] + dy, origin[2] + l.z - p.z),
                                          unreal.Rotator(roll=r.roll, pitch=r.pitch, yaw=r.yaw + dyaw), False, True)

def destroy(*labels):
    for lab in labels:
        A.destroy_actor(acts.pop(lab))

def spawn_mesh(path, loc, yaw, label, folder, mats_by_slot=None, like=None):
    m = EAL.load_asset(path); assert m, path
    a = A.spawn_actor_from_object(m, unreal.Vector(*loc), unreal.Rotator(0, 0, yaw))
    a.set_actor_label(label); a.set_folder_path(folder)
    c = a.static_mesh_component; c.set_collision_profile_name('NoCollision')
    for i, slot in enumerate(m.static_materials):
        n = str(slot.material_slot_name)
        if like is not None and n in like: c.set_material(i, like[n])
        elif mats_by_slot is not None: c.set_material(i, EAL.load_asset(mats_by_slot(n)))
    acts[label] = a
    return a

# ---------------- rigid assembly moves (contract origins, metres x 100) ----------------
move_pivot(['Art_BA_Basin_BA_BasinBody', 'Art_BA_Basin_BA_BA_BasinTap_L', 'Art_BA_Basin_BA_BA_BasinTap_R', 'Basin_Tap'],
           'Art_BA_Basin_BA_BasinBody', (754.2, 792.5, 0), 90)
move_pivot(['Art_BA_Toilet_BA_ToiletBody', 'Art_BA_Toilet_BA_ToiletLid', 'Toilet_Lid'], 'Art_BA_Toilet_BA_ToiletBody', (555, 603, 0), 0)
# FIX-023 (BA-TOILET-02): body/lid/water share the assembly origin (555,603,0) yaw 0; the lid's hinge is (555,592,51.6).
TOI = R2 + 'BA_Toilet02/'
def tmat(n): return EAL.load_asset(R2 + 'Materials/' + ('MI_Rev02_BucketWater' if n == 'Toilet_Standing_Water' else 'MI_Toilet02_' + n))
def put_mesh(a, mesh):
    c = a.static_mesh_component; a.modify(); c.set_static_mesh(mesh)
    for i, sl in enumerate(mesh.static_materials): c.set_material(i, tmat(str(sl.material_slot_name)))
    a.set_actor_location_and_rotation(unreal.Vector(555, 603, 0), unreal.Rotator(0, 0, 0), False, True)
put_mesh(actor('Art_BA_Toilet_BA_ToiletBody'), EAL.load_asset(TOI + 'BA_Toilet02_Body'))
put_mesh(actor('Art_BA_Toilet_BA_ToiletLid'), EAL.load_asset(TOI + 'BA_Toilet02_Lid'))
tw = spawn_mesh(TOI + 'BA_Toilet02_Water', (555, 603, 0), 0, 'Art_BA_Toilet02_Water', str(actor('Art_BA_Toilet_BA_ToiletBody').get_folder_path()),
                mats_by_slot=lambda n: R2 + 'Materials/MI_Rev02_BucketWater')
tw.static_mesh_component.set_cast_shadow(False)
LINEN = ['Art_BA_Linen_BA_Linen_Body', 'Art_BA_Linen_BA_Linen_UpperDoor', 'Art_BA_Linen_BA_Linen_LowerDoor']
move_pivot(LINEN, 'Art_BA_Linen_BA_Linen_Body', (745, 905, 0), 180)
move_pivot(['Art_BA_Basket_BA_Basket', 'Art_BA_Basket_BA_Towel_0', 'Art_BA_Basket_BA_Towel_1', 'Art_BA_Basket_BA_Towel_2'],
           'Art_BA_Basket_BA_Basket', (512, 818, 0), actor('Art_BA_Basket_BA_Basket').get_actor_rotation().yaw)
move_pivot(['Art_BA_Mirror_BA_Mirror_mirror', 'Art_BA_Mirror_BA_Mirror_sconce', 'Art_BA_Mirror_BA_Mirror_globe', 'Mirror_Sconces'],
           'Art_BA_Mirror_BA_Mirror_mirror', (782.2, 792.5, 0), 90)
# The mirror source origin is 18 mm proud of its back (it was set on the old tile face); at the contract's 7.84 the
# back sat 1.8 cm inside the east plaster. It hangs above the tile cap, so its back goes flush on the plaster (7.822).
move_pivot(['Art_BA_WallShelf_ARC_WALL_SHELF_01', 'Art_BA_Bottle_BA_Bottle_Body', 'Art_BA_Bottle_BA_Bottle_Stopper',
            'Art_BA_Cup_BA_Cup', 'Art_BA_Cup_BA_Brush_Ivory', 'Art_BA_Cup_BA_Brush_Sage', 'Art_BA_Soap_BA_SoapBar', 'Art_BA_Soap_BA_SoapDish'],
           'Art_BA_WallShelf_ARC_WALL_SHELF_01', (784, 710, 125), 90)                                    # :077
move_pivot(['Art_BA_WallShelf_ARC_WALL_SHELF_01_S080', 'Art_BA_Jar_BA_Jar_Body', 'Art_BA_Jar_BA_Jar_Lid',
            'Art_BA_Soap_BA_SoapBar_080', 'Art_BA_Soap_BA_SoapDish_080'], 'Art_BA_WallShelf_ARC_WALL_SHELF_01_S080', (784, 635, 125), 90)  # :080
move_pivot(['Art_BA_WallShelf_ARC_WALL_SHELF_01_S085', 'Art_BA_FoldedTowel_BA_Folded_Towel', 'Art_BA_Tin_BA_Tin_Body', 'Art_BA_Tin_BA_Tin_Lid'],
           'Art_BA_WallShelf_ARC_WALL_SHELF_01_S085', (486, 695, 125), -90)                              # :085
move_pivot(['Art_BA_Switch_BA_Switch_Plate', 'Art_BA_Switch_BA_Switch_Toggle'], 'Art_BA_Switch_BA_Switch_Plate', (760, 566, 124), 0)  # :079
move_pivot(['Art_BA_Roll_BA_Roll_Holder', 'Art_BA_Roll_BA_Roll_Paper'], 'Art_BA_Roll_BA_Roll_Holder', (487.8, 613, 72), -90)  # :083
move_pivot(['Art_BA_TowelRail_BA_Towel_Rail', 'Art_BA_TowelRail_BA_Towel_Ivory', 'Art_BA_TowelRail_BA_Towel_Rose'],
           'Art_BA_TowelRail_BA_Towel_Rail', (486, 792.5, 125), -90)                                     # :084
destroy('Art_BA_TowelRail_BA_Towel_Rose', 'Art_BA_TowelRail_BA_Towel_Rail_S078', 'Art_BA_TowelRail_BA_Towel_Ivory_S078',
        'Art_BA_Hook_BA_Hook_01', 'Art_BA_HandTowel_BA_Hand_Towel')

FOLDER = 'Redesign/Imported Art/Rev02'
# :082 hand-towel ring + folded towel (decorative, plate centre on the east plaster face)
for part in ('Hardware', 'Towel'):
    spawn_mesh(R2 + 'BA_Ring02/BA_Ring02_' + part, (784, 710, 115), 90, 'Art_BA_Ring02_' + part, FOLDER,
               mats_by_slot=lambda n: R2 + 'Materials/MI_' + n)

# ---------------- tub: split fixtures ----------------
old = actor('Art_BA_Tub_BA_TubFixtures'); ol, orr = old.get_actor_location(), old.get_actor_rotation()
fx_mats = {str(s.material_slot_name): old.static_mesh_component.get_material(i) for i, s in enumerate(old.static_mesh_component.static_mesh.static_materials)}
PLUMB = (529.3, 832, 0)
spawn_mesh(R2 + 'BA_TubFixtures02/BA_TubFixture02_Plumbing', PLUMB, -90, 'Art_BA_TubFixture02_Plumbing', str(old.get_folder_path()), like=fx_mats)
for part in ('CurtainRod', 'Drain'):
    spawn_mesh(R2 + 'BA_TubFixtures02/BA_TubFixture02_' + part, (ol.x, ol.y, ol.z), orr.yaw, 'Art_BA_TubFixture02_' + part, str(old.get_folder_path()), like=fx_mats)
for lab in ('Art_BA_Tub_BA_TapLeft', 'Art_BA_Tub_BA_TapRight'):
    t = actor(lab); t.modify(); t.set_actor_location_and_rotation(unreal.Vector(*PLUMB), unreal.Rotator(0, 0, -90), False, True)
destroy('Art_BA_Tub_BA_TubFixtures')
assert L.set_current_level_by_name('L_Apartment_Rev02_Gameplay')
# Toilet_Lid (existing action) rebinds to the new lid: root on the hinge, body = the lid mesh at the assembly origin.
# Opening sign chosen by the source's front-edge test: closed front (0,-0.366,0.516) m -> open (0,0.0685,0.990) m,
# i.e. in UE the front at hinge-relative (0,+47.6,0) must rise and swing toward the tank (-Y).
HINGE_T = unreal.Vector(555, 592, 51.6)
tl = actor('Toilet_Lid'); tl.modify(); tl.set_actor_location_and_rotation(HINGE_T, unreal.Rotator(0, 0, 0), False, True)
lb = tl.get_editor_property('body'); lid_art = actor('Art_BA_Toilet_BA_ToiletLid')
lb.set_static_mesh(lid_art.static_mesh_component.static_mesh)
lb.set_world_location_and_rotation(lid_art.get_actor_location(), lid_art.get_actor_rotation(), False, False)
for i in range(lid_art.static_mesh_component.get_num_materials()): lb.set_material(i, lid_art.static_mesh_component.get_material(i))
tl.set_editor_property('use_authored_body_materials', True)
front = unreal.Vector(0, 639.6 - 592, 0)
want = unreal.Vector(0, 596.2 - 592, 99.0 - 51.6)
rv = lambda r: unreal.MathLibrary.greater_greater_vector_rotator(front, unreal.Rotator(roll=r, pitch=0, yaw=0))
best = min((85.0, -85.0), key=lambda r: (rv(r) - want).length())
tl.set_editor_property('toggle_rotation', unreal.Rotator(roll=best, pitch=0, yaw=0))
unreal.log('[Rev02 bathroom] Toilet_Lid hinge (555,592,51.6), open roll %+.0f (front -> %s)' % (best, rv(best)))
tf = actor('Tub_Faucet'); tf.modify()
tfb = tf.get_editor_property('body')                      # the reveal (bath water) hangs off the root and stays in the tub
tfb.set_world_location_and_rotation(unreal.Vector(*PLUMB), unreal.Rotator(0, 0, -90), False, False)
tf.get_editor_property('light').set_world_location(unreal.Vector(500.3, 907, 96), False, False)
# Shower curtain: the gathered panel parks at the tub's east end and slides west by the same 110 cm.
sc = actor('Shower_Curtain'); sc.modify(); scb = sc.get_editor_property('body'); bl = scb.get_world_location()
scb.set_world_location(unreal.Vector(bl.x + 125, bl.y, bl.z), False, False)
sc.set_editor_property('toggle_offset', unreal.Vector(-110, 0, 0))

# ---------------- linen: two new hinged controls (no linen action existed) ----------------
# Door meshes sit in assembly space; the README's left hinges (-0.274, -0.310) map to UE local (-27.4, +31) and, at
# the north-facing transform (yaw 180), to world (772.4, 874): the east side. +90 opens each door north, parking it
# along x 772-779 (contract: 90 deg sweep max X 7.793, 29 mm from the east tile; 95/100 collide).
hx, hy = rot2(-27.4, 31.0, 180)
HINGE = (745 + hx, 905 + hy, 0)
for side, art in (('Upper', 'Art_BA_Linen_BA_Linen_UpperDoor'), ('Lower', 'Art_BA_Linen_BA_Linen_LowerDoor')):
    d = A.spawn_actor_from_class(unreal.FixHimInteractable, unreal.Vector(*HINGE), unreal.Rotator(0, 0, 0))
    d.set_actor_label('Linen_Door_' + side); d.set_folder_path('Gameplay/Interactables/bathroom'); acts[d.get_actor_label()] = d
    d.set_editor_property('room_id', 'bathroom'); d.set_editor_property('toggle', unreal.InteractToggle.ROTATE)
    d.set_editor_property('prompt_off', 'Open linen cupboard'); d.set_editor_property('prompt_on', 'Close linen cupboard')
    src = actor(art); body = d.get_editor_property('body'); body.set_static_mesh(src.static_mesh_component.static_mesh)
    body.set_world_location_and_rotation(src.get_actor_location(), src.get_actor_rotation(), False, False)
    for i in range(src.static_mesh_component.get_num_materials()): body.set_material(i, src.static_mesh_component.get_material(i))
    d.set_editor_property('use_authored_body_materials', True)
    d.set_editor_property('toggle_rotation', unreal.Rotator(0, 0, 90))
    src.modify(); src.set_actor_hidden_in_game(True); src.static_mesh_component.set_visibility(False)
    src.static_mesh_component.set_collision_profile_name('NoCollision'); src.tags = [unreal.Name('GameplayBodySource')]
assert L.set_current_level_by_name('L_Apartment_Rev02')

marker = A.spawn_actor_from_class(unreal.Note, unreal.Vector(0, 0, -520)); marker.set_actor_label('Rev02_Bathroom07'); marker.set_folder_path(FOLDER)
assert L.save_all_dirty_levels()
rows = []
for lab in ('Art_BA_Basin_BA_BasinBody', 'Art_BA_Toilet_BA_ToiletBody', 'Art_BA_Linen_BA_Linen_Body', 'Art_BA_Mirror_BA_Mirror_mirror',
            'Art_BA_Roll_BA_Roll_Holder', 'Art_BA_Roll_BA_Roll_Paper', 'Art_BA_TowelRail_BA_Towel_Rail', 'Art_BA_Ring02_Hardware',
            'Art_BA_TubFixture02_Plumbing', 'Art_BA_Tub_BA_TapLeft', 'Art_BA_TubFixture02_Drain', 'Art_BA_Switch_BA_Switch_Plate'):
    o, e = acts[lab].get_actor_bounds(False)
    rows.append('%s x%.1f-%.1f y%.1f-%.1f z%.1f-%.1f' % (lab, o.x - e.x, o.x + e.x, o.y - e.y, o.y + e.y, o.z - e.z, o.z + e.z))
unreal.log('[Rev02 bathroom] saved\n' + '\n'.join(rows))
