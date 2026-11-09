"""Rev02 step 5: re-bind gameplay in L_Apartment_Rev02_Gameplay to the revision 02 layout.

rev02_04 already moved most interactables and maladies rigidly with their art. This step handles everything
whose art or geometry changed: kitchen click actions move onto KI-CABINET-02 fronts (pivots from its manifest),
the sink tap onto the narrow sink, the fridge onto its west hinge (KI-FRIDGE-01 imports west-hinged), the closet
doors onto BR-CLOSET-02, the sliding panels onto ARC-SLIDING-CLOSET-02; rooms, travel entry points, the front
door, door start and title camera follow the new plan. The 0450 cabinet's door and drawer get two new click
actions (Cabinet_Door_2, Kitchen_Drawer_2). Labels, room ids, prompts and repair identities are preserved.
Re-runnable on a furnished Rev02 map.
"""
import json, math, os, unreal
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
CAB = json.load(open(os.path.join(ROOT, 'Art Source/Apartment Redesign/Assets/KI-CABINET-02/model/manifest.json')))
MAP = '/Game/ICanFixHim/Maps/L_Apartment_Rev02'
GLEVEL = 'L_Apartment_Rev02_Gameplay'
A = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
UES = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
CYL = unreal.load_asset('/Engine/BasicShapes/Cylinder')
T = unreal.InteractToggle

def rot(yaw=0.0, pitch=0.0, roll=0.0):
    return unreal.Rotator(roll=roll, pitch=pitch, yaw=yaw)

assert L.load_level(MAP)
acts = {a.get_actor_label(): a for a in A.get_all_level_actors()}
assert 'Rev02_Furnished' in acts, 'run rev02_04_furnish first'
assert L.set_current_level_by_name(GLEVEL), 'cannot make gameplay sublevel current'

def actor(label):
    assert label in acts, 'missing actor ' + label
    return acts[label]

def body_from_art(a, art_label):
    """The art actor's mesh becomes this interactable's body at the art's world transform (source kept, hidden)."""
    art = actor(art_label); src = art.static_mesh_component
    body = a.get_editor_property('body')
    body.set_static_mesh(src.static_mesh)
    body.set_world_location_and_rotation(art.get_actor_location(), art.get_actor_rotation(), False, False)
    body.set_world_scale3d(art.get_actor_scale3d())
    for i in range(src.get_num_materials()): body.set_material(i, src.get_material(i))
    a.set_editor_property('use_authored_body_materials', True)
    art.modify(); src.modify()
    art.set_actor_hidden_in_game(True); src.set_visibility(False); src.set_collision_profile_name('NoCollision')
    art.tags = [unreal.Name('GameplayBodySource')]

def interactable(label, loc, yaw, room, toggle, off, on):
    """Reuse the existing interactable with this label (keeps its identity), else spawn a new one."""
    a = acts.get(label)
    if a is None:
        a = A.spawn_actor_from_class(unreal.FixHimInteractable, unreal.Vector(*loc), rot(yaw))
        a.set_actor_label(label); a.set_folder_path('Gameplay/Interactables/' + room); acts[label] = a
        a.set_editor_property('room_id', room); a.set_editor_property('toggle', toggle)
        a.set_editor_property('prompt_off', off); a.set_editor_property('prompt_on', on)
    a.modify()
    a.set_actor_location_and_rotation(unreal.Vector(*loc), rot(yaw), False, True)
    a.get_editor_property('pivot').set_relative_location(unreal.Vector(0, 0, 0), False, False)
    a.get_editor_property('pivot').set_relative_rotation(rot(0), False, False)
    return a

def bounds_center(label):
    o, _ = actor(label).get_actor_bounds(False, True)
    return (o.x, o.y, o.z)

def hinge_door(label, art, hinge, swing, room, what):
    a = interactable(label, hinge, 0, room, T.ROTATE, 'Open ' + what, 'Close ' + what)
    body_from_art(a, art); a.set_editor_property('toggle_rotation', rot(swing))
    return a

def drawer(label, art, yaw, dist, room):
    a = interactable(label, bounds_center(art), yaw, room, T.SLIDE, 'Open drawer', 'Close drawer')
    body_from_art(a, art); a.set_editor_property('toggle_offset', unreal.Vector(dist, 0, 0))
    return a

# ---------------- kitchen: KI-CABINET-02 fronts ----------------
# Manifest pivots are source metres (front -Y); imports keep X and flip Y, so a hinge is at body + (x, -y) * 100.
# Doors open about Z: source left -100 deg / right +100 deg -> Unreal yaw +100 / -100. Drawers slide out +Y 30 cm.
part = {(v['code'], k): p for v in CAB['variants'] for k, p in v['parts'].items()}
ORIGIN = {'0425': (141.25, 47.5), '0775': (306.25, 47.5), '0450': (442.5, 47.5)}
def cab_hinge(code, key):
    px, py, _ = part[(code, key)]['pivot']
    ox, oy = ORIGIN[code]
    return (ox + px * 100, oy - py * 100, 0)
hinge_door('Sink_Door_L', 'Art_KI_Cab0775_door_L', cab_hinge('0775', 'door_L'), 100, 'kitchen', 'cabinet')
# The range-side hinges sit behind 40 mm recessed fillers (KI-CABINET-02 range-fit revision), so these doors clear
# KI-RANGE-01's side panels through the full swing (verified by rev02 neighbour sweeps).
hinge_door('Sink_Door_R', 'Art_KI_Cab0775_door_R', cab_hinge('0775', 'door_R'), -100, 'kitchen', 'cabinet')
drawer('Sink_Drawer_L', 'Art_KI_Cab0775_drawer_L', 90, 30, 'kitchen')
drawer('Sink_Drawer_R', 'Art_KI_Cab0775_drawer_R', 90, 30, 'kitchen')
hinge_door('Cabinet_Door', 'Art_KI_Cab0425_door', cab_hinge('0425', 'door'), 100, 'kitchen', 'cabinet')
drawer('Kitchen_Drawer', 'Art_KI_Cab0425_drawer', 90, 30, 'kitchen')
hinge_door('Cabinet_Door_2', 'Art_KI_Cab0450_door', cab_hinge('0450', 'door'), 100, 'kitchen', 'cabinet')   # range-side hinge, see above
drawer('Kitchen_Drawer_2', 'Art_KI_Cab0450_drawer', 90, 30, 'kitchen')

# Fridge (KI-FRIDGE-01): hinge barrels at body-local (-38, +33.5) on the west side; plan allows a 105 deg swing.
fh = actor('Art_KI_Fridge_Body').get_actor_transform().transform_location(unreal.Vector(-38, 33.5, 0))
hinge_door('Fridge_Door', 'Art_KI_Fridge_Door', (fh.x, fh.y, 0), 105, 'kitchen', 'fridge')
acts['Fridge_Door'].set_editor_property('prompt_off', 'Open fridge'); acts['Fridge_Door'].set_editor_property('prompt_on', 'Close fridge')

# Sink tap: the narrow sink's left tap control; the water falls from the faucet spout into the basin.
tap = interactable('Sink_Tap', bounds_center('Art_KI_SinkNarrow_L_tap'), 0, 'kitchen', T.REVEAL, 'Turn on the tap', 'Turn off the tap')
body_from_art(tap, 'Art_KI_SinkNarrow_L_tap')
# Measured from the KI_SINK_NARROW_body mesh: spout tip at body-local (0, +4, 122) cm, basin floor ~69 cm under it.
SPOUT = (215, 46.05 + 4, 121)
BASIN = 70
rp = tap.get_editor_property('reveal_part'); rp.set_static_mesh(CYL)
h = SPOUT[2] - BASIN
rp.set_world_location(unreal.Vector(SPOUT[0], SPOUT[1], BASIN + h / 2), False, False); rp.set_world_rotation(rot(0), False, False)
rp.set_world_scale3d(unreal.Vector(0.014, 0.014, h / 100.0)); rp.set_cast_shadow(False)
tap.set_editor_property('reveal_color', unreal.LinearColor(0.55, 0.78, 0.9, 1)); tap.set_editor_property('reveal_opacity', 0.55)

# Breakfast sconce (rev02_04b dressing): clickable like the two hall sconces.
sc = interactable('Sconce_Kitchen', bounds_center('Art_HA_Sconce01_HA_Sconce_Bulb_Kitchen'), 0, 'kitchen', T.LIGHT, 'Turn on sconce', 'Turn off sconce')
body_from_art(sc, 'Art_HA_Sconce01_HA_Sconce_Shade_Kitchen')
lc = sc.get_editor_property('light'); lc.set_world_location(unreal.Vector(*bounds_center('Art_HA_Sconce01_HA_Sconce_Bulb_Kitchen')), False, False)
lc.set_editor_property('light_color', unreal.Color(r=255, g=200, b=150, a=255)); sc.set_editor_property('light_intensity_on', 900)

# ---------------- bedroom walk-in: BR-CLOSET-02 doors (hinge-local meshes; open -95 / +95 source -> +95 / -95) ----------------
for side, swing in (('L', 95), ('R', -95)):
    art = actor('Art_BR_Closet_Door_' + side); l = art.get_actor_location()
    hinge_door('Wardrobe_Door_' + side, 'Art_BR_Closet_Door_' + side, (l.x, l.y, 0), swing, 'bedroom', 'closet')

# ---------------- sliding closets: ARC-SLIDING-CLOSET-02 panels slide +/-44 cm along the frame ----------------
for label, room, art_room, y, yaw in (('CoatCloset', 'hall', 'Coat', 560, 180), ('OfficeCloset', 'office', 'Office', 715, 0)):
    for side, dist in (('Left', 44), ('Right', -44)):
        a = interactable('%s_%s' % (label, side), (1138, y, 0), yaw, room, T.SLIDE, 'Slide closet door', 'Slide closet door')
        body_from_art(a, 'Art_%sCloset_%sPanel' % (art_room, side)); a.set_editor_property('toggle_offset', unreal.Vector(dist, 0, 0))

# ---------------- rooms ----------------
ROOMS = [('living', 'Living Room', (480, 0, 1200, 380), (760, 340, -60)),
         ('kitchen', 'Kitchen', (0, 0, 480, 380), (400, 300, -150)),
         ('hall', 'Hall', (220, 380, 1200, 560), (1120, 452.5, 180)),
         ('bedroom', 'Bedroom', (0, 560, 480, 955), (352.5, 625, 90)),
         ('bathroom', 'Bathroom', (480, 560, 790, 955), (677.5, 625, 90)),
         ('office', 'Office', (790, 560, 1200, 955), (997.5, 625, 90))]
def room(label, rid, name, rect, entry, color=None, sub=False):
    (x0, y0, x1, y1), (ex, ey, eyaw) = rect, entry
    r = acts.get(label)
    if r is None:
        r = A.spawn_actor_from_class(unreal.FixHimRoom, unreal.Vector(0, 0, 150), rot(0))
        r.set_actor_label(label); r.set_folder_path('Gameplay/Rooms'); acts[label] = r
        r.set_editor_property('map_color', unreal.LinearColor(*color, 1))
    r.modify()
    r.set_editor_property('room_id', rid); r.set_editor_property('display_name', name); r.set_editor_property('sub_volume', sub)
    r.set_actor_location(unreal.Vector((x0 + x1) / 2, (y0 + y1) / 2, 150), False, True)
    r.get_editor_property('bounds').set_box_extent(unreal.Vector((x1 - x0) / 2, (y1 - y0) / 2, 150), True)
    ep = r.get_editor_property('entry_point')
    ep.set_world_location(unreal.Vector(ex, ey, 100), False, False); ep.set_world_rotation(rot(eyaw), False, False)
for rid, name, rect, entry in ROOMS:
    room('Room_' + rid, rid, name, rect, entry)
# The walk-in mold closet opens off the bedroom: a 'bedroom' sub-volume (AFixHimRoom::bSubVolume) keeps Malcolm
# "in his room" there, without its own floor-plan status or a travel button.
room('Room_bedroom_closet', 'bedroom', 'Closet', (0, 380, 220, 560), (110, 520, -90), (0.72, 0.62, 0.82), sub=True)

# ---------------- encounter clearance ----------------
# The rigid moves keep each malady's hunk/talk offsets, but Rev02 furniture crowds two talk spots: Wyatt's sat 30 cm
# from the sofa and Lukey's on the new wall table (player capsule radius 38 cm). These replacements were found by
# a capsule search: clear of a 48 cm capsule, inside the malady's room, 130-175 cm from the hunk, with a clear sight
# line to his head; the closest qualifying spot to the original was taken. Hunk spawns already clear.
for label, (x, y) in {'Malady_FuseBox': (942, 343), 'Malady_Sink': (185, 275)}.items():
    ts = actor(label).get_editor_property('talk_spot'); z = ts.get_world_location().z
    actor(label).modify(); ts.set_world_location(unreal.Vector(x, y, z), False, False)

# Malcolm's glow light sits on the malady root, ~1.5 cm from the closet's back wall, which blows a white hotspot
# into the mold; 35 cm out into the closet (local +X) it lights the mold evenly.
mg = actor('Malady_Mold'); mg.modify()
mg.get_editor_property('glow_light').set_relative_location(unreal.Vector(35, 0, 0), False, False)

# ---------------- front door, door start, title camera ----------------
fd = actor('FrontDoor'); fd.modify(); fd.set_actor_location(unreal.Vector(1192, 452.5, 0), False, True)
ps = actor('PlayerStart_Door'); ps.modify(); ps.set_actor_location(unreal.Vector(1120, 452.5, 100), False, True)
cam = actor('TitleCamera'); cam.modify()
eye, tgt = (600, 470, 175), (980, 180, 95)   # hall centreline: the title drift (+/-60 cm in y) stays clear of the walls
cam.set_actor_location(unreal.Vector(*eye), False, True)
dx, dy, dz = tgt[0] - eye[0], tgt[1] - eye[1], tgt[2] - eye[2]
cam.set_actor_rotation(rot(math.degrees(math.atan2(dy, dx)), math.degrees(math.atan2(dz, math.hypot(dx, dy)))), False)
# Without this tag the player controller replaces the camera with a view tuned for the original L_Apartment, which
# in this layout frames a wall edge beside the kitchen portal.
cam.tags = [unreal.Name('TitleCamera'), unreal.Name('TitleCameraAsPlaced')]
# The hall's east ceiling light now hangs in the kitchen.
acts['CeilingLight_HallEast'].set_editor_property('room_id', 'kitchen')

assert L.save_all_dirty_levels()
n = sum(1 for a in A.get_all_level_actors() if str(a.get_folder_path()).startswith('Gameplay'))
unreal.log('[Rev02 gameplay] saved; gameplay actors=%d' % n)
