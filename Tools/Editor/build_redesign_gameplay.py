"""Gameplay parity for the redesign map (see docs/.../Gameplay parity plan.md).

Spawns rooms, maladies, interactables, bed, front door, door start and title camera into the
streamed sublevel L_Apartment_Redesign_Gameplay, mirroring Tools/Editor/build_apartment.py.
Moving art parts become interactable bodies (their original actors stay in the persistent map,
hidden, as the re-runnable source). Malady damage overlays are moved into the gameplay sublevel
and attached to their malady so repair hides them. Re-runnable.

Conventions (as in build_apartment.py): interactable actors sit on their hinge/pivot; toggle
rotation is (yaw, pitch, roll); slide offset and malady hunk_spawn/talk_spot are in actor-local
space with +X pointing into the room.
"""
import math, unreal
A = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
UES = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
EAL = unreal.EditorAssetLibrary
PERSIST = '/Game/ICanFixHim/Maps/L_Apartment_Redesign_Blockout'
GLEVEL = 'L_Apartment_Redesign_Gameplay'
CUBE = unreal.load_asset('/Engine/BasicShapes/Cube')
CYL = unreal.load_asset('/Engine/BasicShapes/Cylinder')
INVISIBLE = unreal.load_asset('/Game/ICanFixHim/Materials/Palette/MI_Invisible')
T = unreal.InteractToggle

def rot(yaw=0.0, pitch=0.0, roll=0.0):
    return unreal.Rotator(roll=roll, pitch=pitch, yaw=yaw)

assert L.load_level(PERSIST)
world = UES.get_editor_world()
stream = unreal.GameplayStatics.get_streaming_level(world, GLEVEL)
assert stream, 'gameplay sublevel missing; run prepare_redesign_gameplay_level.py'
acts = {a.get_actor_label(): a for a in A.get_all_level_actors()}

# --- clean previous gameplay actors (keep damage overlays; detach them first)
DAMAGE = {'wyatt': ['Art_LV_Fuse_Wire_Damaged', 'Art_LV_Fuse_Wire_Repaired', 'Art_LV_Fuse_Plaster_Damage'],
          'lukey': ['Art_KI_SINK_damage', 'Art_KI_Wall_Stain'],
          'tyler': ['Damage_BA_CrackedTile'], 'malcolm': ['Art_BR_Closet_Mold']}
damage_labels = {l for v in DAMAGE.values() for l in v}
for a in list(acts.values()):
    if a.get_actor_label() in damage_labels:
        a.detach_from_actor(unreal.DetachmentRule.KEEP_WORLD, unreal.DetachmentRule.KEEP_WORLD, unreal.DetachmentRule.KEEP_WORLD)
for a in list(acts.values()):
    if str(a.get_folder_path()).startswith('Gameplay') and a.get_actor_label() not in damage_labels:
        A.destroy_actor(a)
if 'Review_PlayerStart' in acts:
    A.destroy_actor(acts['Review_PlayerStart'])
# move damage overlays into the gameplay sublevel (attachment cannot cross levels)
acts = {a.get_actor_label(): a for a in A.get_all_level_actors()}
to_move = [acts[l] for l in damage_labels if l in acts and acts[l].get_level().get_outermost().get_name() == PERSIST]
if to_move:
    unreal.EditorLevelUtils.move_actors_to_level(to_move, stream, False, False)
acts = {a.get_actor_label(): a for a in A.get_all_level_actors()}
assert L.set_current_level_by_name(GLEVEL), 'cannot make gameplay sublevel current'

def spawn(cls, label, loc, yaw=0.0, folder='Gameplay'):
    a = A.spawn_actor_from_class(cls, unreal.Vector(*loc), rot(yaw))
    a.set_actor_label(label); a.set_folder_path(folder)
    return a

def body_from_art(actor, art_label, authored=True):
    """Make the art actor's mesh this interactable's body at the art's exact world transform."""
    art = acts[art_label]
    src = art.static_mesh_component
    body = actor.get_editor_property('body')
    body.set_static_mesh(src.static_mesh)
    body.set_world_location_and_rotation(art.get_actor_location(), art.get_actor_rotation(), False, False)
    body.set_world_scale3d(art.get_actor_scale3d())
    for i in range(src.get_num_materials()):
        body.set_material(i, src.get_material(i))
    actor.set_editor_property('use_authored_body_materials', authored)
    # keep the source in the environment map, hidden, so this script can be re-run
    art.set_actor_hidden_in_game(True); src.set_visibility(False); src.set_collision_profile_name('NoCollision')
    art.tags = [unreal.Name('GameplayBodySource')]
    return body

def body_proxy(actor, mesh, world_loc, size_cm, rel_rot=(0, 0, 0), invisible=False):
    body = actor.get_editor_property('body')
    body.set_static_mesh(mesh)
    body.set_world_location(unreal.Vector(*world_loc), False, False)
    body.set_relative_rotation(rot(*rel_rot), False, False)
    body.set_relative_scale3d(unreal.Vector(*(v / 100.0 for v in size_cm)))
    if invisible:
        actor.set_editor_property('use_authored_body_materials', True)
        body.set_material(0, INVISIBLE); body.set_cast_shadow(False)
    return body

def interactable(label, loc, yaw, room, toggle, off, on, cls=None):
    a = spawn(cls or unreal.FixHimInteractable, label, loc, yaw, 'Gameplay/Interactables/' + room)
    a.set_editor_property('room_id', room); a.set_editor_property('toggle', toggle)
    a.set_editor_property('prompt_off', off); a.set_editor_property('prompt_on', on)
    return a

def light(a, world_loc, color, intensity):
    lc = a.get_editor_property('light')
    lc.set_world_location(unreal.Vector(*world_loc), False, False)
    lc.set_editor_property('light_color', unreal.Color(r=color[0], g=color[1], b=color[2], a=255))
    a.set_editor_property('light_intensity_on', intensity)

def bounds(label):
    o, e = acts[label].get_actor_bounds(False)
    return (o.x - e.x, o.y - e.y, o.z - e.z), (o.x + e.x, o.y + e.y, o.z + e.z), (o.x, o.y, o.z)

# ---------------- rooms (plan rectangles, cm) ----------------
ROOMS = [('living', 'Living Room', (0, 0, 550, 380), (450, 320, 180 + 90), (0.85, 0.55, 0.42)),
         ('kitchen', 'Kitchen', (550, 0, 1200, 380), (665, 320, 270), (0.62, 0.78, 0.6)),
         ('hall', 'Hall', (0, 380, 1200, 560), (1120, 442.5, 180), (0.86, 0.74, 0.56)),
         ('bedroom', 'Bedroom', (0, 560, 480, 955), (360, 625, 90), (0.72, 0.62, 0.82)),
         ('bathroom', 'Bathroom', (480, 560, 790, 955), (680, 625, 90), (0.9, 0.62, 0.7)),
         ('office', 'Office', (790, 560, 1200, 955), (1010, 625, 90), (0.6, 0.72, 0.86))]
for rid, name, (x0, y0, x1, y1), (ex, ey, eyaw), color in ROOMS:
    r = spawn(unreal.FixHimRoom, 'Room_' + rid, ((x0 + x1) / 2, (y0 + y1) / 2, 150), 0, 'Gameplay/Rooms')
    r.set_editor_property('room_id', rid); r.set_editor_property('display_name', name)
    r.set_editor_property('map_color', unreal.LinearColor(*color, 1))
    r.get_editor_property('bounds').set_box_extent(unreal.Vector((x1 - x0) / 2, (y1 - y0) / 2, 150), True)
    ep = r.get_editor_property('entry_point')
    ep.set_world_location(unreal.Vector(ex, ey, 100), False, False); ep.set_world_rotation(rot(eyaw), False, False)

# ---------------- maladies ----------------
def malady(label, hunk, style, loc, yaw, room, proxy_size, proxy_rel=(2, 0, 0), fx=(0, 0, 0), hunk_spawn=(140, 0, 0), talk=(300, 0, 0)):
    a = interactable(label, loc, yaw, room, T.NONE, 'Inspect', 'Inspect', cls=unreal.FixHimMalady)
    a.set_folder_path('Gameplay/Maladies')
    a.set_editor_property('hunk_id', hunk); a.set_editor_property('style', style)
    a.set_editor_property('fx_offset', unreal.Vector(*fx))
    c, s = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    world = (loc[0] + proxy_rel[0] * c - proxy_rel[1] * s, loc[1] + proxy_rel[0] * s + proxy_rel[1] * c, loc[2] + proxy_rel[2])
    body_proxy(a, CUBE, world, proxy_size, invisible=True)
    for comp, rel in (('hunk_spawn', hunk_spawn), ('talk_spot', talk)):
        sc = a.get_editor_property(comp)
        sc.set_relative_location(unreal.Vector(*rel), False, False)
        sc.set_relative_rotation(rot(180 if comp == 'talk_spot' else 0), False, False)
    for dl in DAMAGE[hunk]:
        d = acts[dl]
        d.static_mesh_component.set_mobility(unreal.ComponentMobility.MOVABLE)
        d.static_mesh_component.set_collision_profile_name('NoCollision')
        d.set_folder_path('Gameplay/Damage')
        d.attach_to_actor(a, '', unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, False)
    return a

_, _, fc = bounds('Art_LV_Fuse_Shell')
malady('Malady_FuseBox', 'wyatt', unreal.MaladyStyle.WIRING, (fc[0], 362, fc[2]), -90, 'living', (16, 56, 84),
       proxy_rel=(4, 0, 0), fx=(18, 0, -20), hunk_spawn=(110, 80, -40), talk=(260, 30, -40))
malady('Malady_Sink', 'lukey', unreal.MaladyStyle.LEAK, (855, 62, 82), 90, 'kitchen', (16, 100, 30),
       proxy_rel=(4, 0, 0), fx=(8, 0, -45), hunk_spawn=(75, 0, 28), talk=(235, 0, 28))
_, _, tc = bounds('Damage_BA_CrackedTile')
malady('Malady_PinkTile', 'tyler', unreal.MaladyStyle.TILE, (tc[0], 946, tc[2]), -90, 'bathroom', (4, 40, 50),
       proxy_rel=(1, 0, 0), fx=(2, 0, 0), hunk_spawn=(140, 0, 0), talk=(300, 0, 0))
_, _, mc = bounds('Art_BR_Closet_Mold')
mold = malady('Malady_Mold', 'malcolm', unreal.MaladyStyle.MOLD, (mc[0], 567.5, mc[2]), 90, 'bedroom', (3, 106, 112),
              proxy_rel=(1, 0, 0), fx=(2, 0, 0), hunk_spawn=(65, 0, -70), talk=(250, 0, -70))
acts['Art_BR_Closet_Mold'].tags = [unreal.Name('RepairDamage'), unreal.Name('AuthoredMoldDamage'), unreal.Name('malcolm')]

# ---------------- interactables ----------------
WARM = (255, 200, 150)
lamp = interactable('FloorLamp', (23.5, 40, 95), 0, 'living', T.LIGHT, 'Turn on lamp', 'Turn off lamp')
body_from_art(lamp, 'Art_LV_TableLamp_LV_TableLampShade'); light(lamp, (23.5, 40, 93), WARM, 1800)

tv = interactable('TV', (498, 172, 96), 180, 'living', T.LIGHT, 'Turn on TV', 'Turn off TV')
body_from_art(tv, 'Art_LV_TV_LV_TV_screen_off', authored=False)
tv.set_editor_property('body_color', unreal.LinearColor(0.04, 0.05, 0.06, 1))
tv.set_editor_property('on_emissive', unreal.LinearColor(0.6, 1.2, 3.0, 1)); light(tv, (455, 172, 96), (120, 170, 255), 1500)

(fx0, fy0, _), (fx1, fy1, _), _ = bounds('Art_KI_Fridge_Door')
fridge = interactable('Fridge_Door', (fx1 - 1, fy1 - 2, 0), 0, 'kitchen', T.ROTATE, 'Open fridge', 'Close fridge')
body_from_art(fridge, 'Art_KI_Fridge_Door'); fridge.set_editor_property('toggle_rotation', rot(-100))

# Stove: invisible click target over the front-right burner; KI-RANGE-FLAME-01 is the lit part.
# README burner offset (Blender) (+0.18, -0.15, 0.931) m from the range origin -> Unreal (+18, +15, 93.1) cm.
rng = acts['Art_KI_Range_Body'].get_actor_location()
flame_loc = (rng.x + 18, rng.y + 15, 93.1)
burner = interactable('Stove_Burner', flame_loc, 0, 'kitchen', T.LIGHT, 'Turn on stove', 'Turn off stove')
body_proxy(burner, CYL, flame_loc, (20, 20, 5), invisible=True)
fl = burner.get_editor_property('reveal_part')
fl.set_static_mesh(unreal.load_asset('/Game/ICanFixHim/Environment/Redesign/KI_Range/KI_Range_Flame'))
fl.set_world_location(unreal.Vector(*flame_loc), False, False); fl.set_world_rotation(rot(0), False, False)
fl.set_world_scale3d(unreal.Vector(1, 1, 1)); fl.set_cast_shadow(False)
burner.set_editor_property('reveal_color', unreal.LinearColor(0.25, 0.6, 1.6, 1)); burner.set_editor_property('reveal_opacity', 0.85)
light(burner, (flame_loc[0], flame_loc[1], flame_loc[2] + 12), (120, 170, 255), 600)

_, _, dc = bounds('Art_KI_Cabinet_drawer')
kdrawer = interactable('Kitchen_Drawer', dc, 90, 'kitchen', T.SLIDE, 'Open drawer', 'Close drawer')
body_from_art(kdrawer, 'Art_KI_Cabinet_drawer'); kdrawer.set_editor_property('toggle_offset', unreal.Vector(30, 0, 0))

_, _, tapc = bounds('Art_BA_Tub_BA_TapLeft')
tap = interactable('Tub_Faucet', tapc, 180, 'bathroom', T.REVEAL, 'Run the bath', 'Turn off the water')
body_from_art(tap, 'Art_BA_Tub_BA_TapLeft')
rp = tap.get_editor_property('reveal_part')   # BA-TUB-WATER-01 shares the tub's assembly origin
tub = acts['Art_BA_Tub_BA_Tub']
rp.set_static_mesh(unreal.load_asset('/Game/ICanFixHim/Environment/Redesign/BA_Tub/BA_TUB_WATER_Surface'))
rp.set_world_location(tub.get_actor_location(), False, False); rp.set_world_rotation(tub.get_actor_rotation(), False, False)
rp.set_world_scale3d(unreal.Vector(1, 1, 1)); rp.set_cast_shadow(False)
tap.set_editor_property('reveal_color', unreal.LinearColor(0.42, 0.68, 0.82, 1)); tap.set_editor_property('reveal_opacity', 0.6)

lid = interactable('Toilet_Lid', (752.5, 792.5, 50.5), 90, 'bathroom', T.ROTATE, 'Lift the lid', 'Put the lid down')
body_from_art(lid, 'Art_BA_Toilet_BA_ToiletLid'); lid.set_editor_property('toggle_rotation', rot(0, 0, -68))  # README: -68 deg about local X

bed = interactable('Bed', (265, 850, 56), 0, 'bedroom', T.NONE, 'Go to bed', 'Go to bed', cls=unreal.FixHimBed)
body_from_art(bed, 'Art_BR_Bed')

blamp = interactable('BedLamp', (162.5, 926.5, 88), 0, 'bedroom', T.LIGHT, 'Turn on lamp', 'Turn off lamp')
body_from_art(blamp, 'Art_BR_Lamp_W_BR_LampShade'); light(blamp, (162.5, 926.5, 87), WARM, 1400)

for side, hinge_x, swing in (('L', 44.5, 100), ('R', 135.5, -100)):
    d = interactable('Wardrobe_Door_' + side, (hinge_x, 707, 0), 0, 'bedroom', T.ROTATE, 'Open closet', 'Close closet')
    body_from_art(d, 'Art_BR_Closet_Door_' + side); d.set_editor_property('toggle_rotation', rot(swing))

_, _, ddc = bounds('Art_BR_Dresser_BR_Dresser_drawer3')
ddrawer = interactable('Dresser_Drawer', ddc, 180, 'bedroom', T.SLIDE, 'Open drawer', 'Close drawer')
body_from_art(ddrawer, 'Art_BR_Dresser_BR_Dresser_drawer3'); ddrawer.set_editor_property('toggle_offset', unreal.Vector(30, 0, 0))

# Front door (east hall wall): invisible click slab inside the authored walnut leaf.
door = interactable('FrontDoor', (1192, 442.5, 0), 180, 'hall', T.NONE, 'Leave the apartment', 'Leave the apartment', cls=unreal.FixHimDoor)
door.set_folder_path('Gameplay/Structure')
body_proxy(door, CUBE, (1192, 442.5, 105), (10, 92, 210), invisible=True)
door.get_editor_property('body').set_editor_property('hidden_in_game', True)

# ---------------- start + title camera ----------------
ps = spawn(unreal.PlayerStart, 'PlayerStart_Door', (1120, 442.5, 100), 180, 'Gameplay/Start')
ps.tags = [unreal.Name('DoorStart')]
cam = spawn(unreal.CameraActor, 'TitleCamera', (520, 345, 165), 0, 'Gameplay/Start')
dx, dy, dz = 150 - 520, 110 - 345, 110 - 165
cam.set_actor_rotation(rot(math.degrees(math.atan2(dy, dx)), math.degrees(math.atan2(dz, math.hypot(dx, dy)))), False)
cam.tags = [unreal.Name('TitleCamera')]
cam.camera_component.set_editor_property('field_of_view', 70.0)

L.save_all_dirty_levels()
n = sum(1 for a in A.get_all_level_actors() if str(a.get_folder_path()).startswith('Gameplay'))
unreal.log('[Gameplay] built %d gameplay actors in %s' % (n, GLEVEL))
