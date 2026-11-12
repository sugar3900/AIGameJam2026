"""Rev02 step 5x: give FrontDoor and Stove_Burner real art bodies instead of invisible click proxies.

The screen-space hover outline (UFixHimHoverOutlineSubsystem) rims the visible pixels of an interactable's own
meshes, so an invisible proxy body gets no outline. Like every other click action, these two now take their art
actor's mesh as Body (body_from_art: same world transform and materials; the art actor stays in the map as the
hidden, collision-free source):

  FrontDoor     <- Door_Entry_Leaf      (ARC-ENTRY-DOOR-03 leaf; Toggle None, so the leaf never moves)
  Stove_Burner  <- Art_KI_Range_Body    (the burners are part of the range body mesh; the oven door stays Oven_Door)

The Stove_Burner actor keeps its transform (the flame reveal and light sit on the front-right burner); only its
Body changes, so the whole range body (minus the oven door) is now the "Turn on stove" target.

OUTLINE_CHILDREN groups parts that sit in front of / inside an interactable into its hover silhouette, so they don't
get inner rims of their own: the stove's outline wraps range + oven door + kettle as one shape. One way: hovering
Oven_Door still outlines only the door.
Re-runnable on a furnished Rev02 map. Run with Tools/run_editor_script.py.
"""
import unreal
MAP = '/Game/ICanFixHim/Maps/L_Apartment_Rev02'
GLEVEL = 'L_Apartment_Rev02_Gameplay'
A = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

assert not L.is_in_play_in_editor(), 'stop PIE first'
assert L.load_level(MAP)
acts = {a.get_actor_label(): a for a in A.get_all_level_actors()}
PAIRS = (('FrontDoor', 'Door_Entry_Leaf'), ('Stove_Burner', 'Art_KI_Range_Body'))
OUTLINE_CHILDREN = {
    'Stove_Burner': ['Oven_Door', 'Art_KI_Kettle_KI_Kettle_Body', 'Art_KI_Kettle_KI_Kettle_Lid'],
    # Split light fixtures: the Body is one piece (shade / glass / pull chain); the rest is separate visible art.
    'BedLamp': ['Art_BR_Lamp_W_BR_LampBody', 'Art_BR_Lamp_W_BR_LampBulb'],
    'BedLamp_E': ['Art_BR_Lamp_E_BR_LampBody', 'Art_BR_Lamp_E_BR_LampBulb'],
    'FloorLamp': ['Art_LV_TableLamp_LV_TableLampBody', 'Art_LV_TableLamp_LV_TableLampBulb'],
    'FloorLamp_Office': ['Art_OF_FloorLamp_LV_LampBody', 'Art_OF_FloorLamp_LV_LampBulb'],
    'Sconce_Hall_1': ['Art_HA_Sconce01_HA_Sconce_Hardware', 'Art_HA_Sconce01_HA_Sconce_Bulb'],
    'Sconce_Hall_2': ['Art_HA_Sconce02_HA_Sconce_Hardware', 'Art_HA_Sconce02_HA_Sconce_Bulb'],
    'Sconce_Kitchen': ['Art_HA_Sconce01_HA_Sconce_Hardware_Kitchen', 'Art_HA_Sconce01_HA_Sconce_Bulb_Kitchen'],
    'CeilingLight_Bath': ['Art_CeilingLight_Bath_Hardware'],
    'CeilingLight_Bedroom': ['Art_CeilingLight_Bedroom_Hardware'],
    'CeilingLight_Living': ['Art_CeilingLight_Living_Hardware'],
    'CeilingLight_Office': ['Art_CeilingLight_Office_Hardware'],
    'CeilingLight_HallEast': ['Art_CeilingLight_HallEast_Hardware'],
    'CeilingLight_HallWest': ['Art_CeilingLight_HallWest_Hardware'],
    'Mirror_Sconces': ['Art_BA_Mirror_BA_Mirror_sconce'],
    'Light_Closet': ['Art_BR_ClosetLight01_Glass', 'Art_BR_ClosetLight01_Filament', 'Art_BR_ClosetLight01_Hardware'],
    # Wall switches: the toggle sits in front of the plate.
    'WallSwitch_bathroom': ['Art_BA_Switch_BA_Switch_Toggle'],
    'WallSwitch_bedroom': ['Art_BA_Switch_BA_Switch_Toggle_S068'],
    'WallSwitch_kitchen': ['Art_BA_Switch_BA_Switch_Toggle_S086'],
    'WallSwitch_office': ['Art_BA_Switch_BA_Switch_Toggle_S075'],
    'WallSwitch_closet': ['Art_WallSwitch_closet_Toggle'],
    'WallSwitch_entry_sconce': ['Art_WallSwitch_entry_sconce_Toggle'],
    'WallSwitch_hall': ['Art_WallSwitch_hall_Toggle'],
    'WallSwitch_living': ['Art_WallSwitch_living_Toggle'],
    # The TV's Body is the screen; the housing makes it read as the whole set.
    'TV': ['Art_LV_TV02_Housing'],
}
TOUCH_CM = 10.0   # a child must touch its parent; a distant piece would draw a second, separate outline
missing = [l for p in PAIRS for l in p if l not in acts]
missing += [l for k, v in OUTLINE_CHILDREN.items() for l in [k] + v if l not in acts]
assert not missing, 'missing actors %s' % missing
assert L.set_current_level_by_name(GLEVEL), 'cannot make gameplay sublevel current'


def body_from_art(a, art_label):
    """The art actor's mesh becomes this interactable's body at the art's world transform (source kept, hidden)."""
    art = acts[art_label]; src = art.static_mesh_component
    body = a.get_editor_property('body')
    a.modify(); body.modify()
    body.set_static_mesh(src.static_mesh)
    body.set_world_location_and_rotation(art.get_actor_location(), art.get_actor_rotation(), False, False)
    body.set_world_scale3d(art.get_actor_scale3d())
    for i in range(src.get_num_materials()):
        body.set_material(i, src.get_material(i))
    # Undo the invisible-proxy setup (hidden slab / MI_Invisible cylinder).
    body.set_visibility(True)
    body.set_editor_property('hidden_in_game', False)
    body.set_collision_profile_name('BlockAll')
    a.set_editor_property('use_authored_body_materials', True)
    a.set_editor_property('hover_outline', True)
    art.modify(); src.modify()
    art.set_actor_hidden_in_game(True); src.set_visibility(False); src.set_collision_profile_name('NoCollision')
    art.tags = [unreal.Name('GameplayBodySource')]
    return body


log = []
for label, art_label in PAIRS:
    body = body_from_art(acts[label], art_label)
    log.append('%s body <- %s (%s, %d slots)' % (label, art_label, body.static_mesh.get_name(), body.get_num_materials()))
    assert not any(m and 'Invisible' in m.get_name() for m in body.get_materials()), label

def box(actor, comps=None):
    lo = [1e9] * 3; hi = [-1e9] * 3
    for c in comps or actor.get_components_by_class(unreal.StaticMeshComponent):
        if not c.static_mesh:
            continue
        o, e, _ = unreal.SystemLibrary.get_component_bounds(c)
        for i, (oi, ei) in enumerate(((o.x, e.x), (o.y, e.y), (o.z, e.z))):
            lo[i] = min(lo[i], oi - ei); hi[i] = max(hi[i], oi + ei)
    return lo, hi


def touches(a, b, gap):
    return all(a[0][i] - gap <= b[1][i] and b[0][i] <= a[1][i] + gap for i in range(3))


skipped = []
for label, children in OUTLINE_CHILDREN.items():
    a = acts[label]
    parent = box(a, [a.get_editor_property('body')])
    keep = []
    for c in children:   # a hidden body source would add nothing to the silhouette
        assert not acts[c].is_hidden_ed() and 'GameplayBodySource' not in [str(t) for t in acts[c].tags], c
        if touches(parent, box(acts[c]), TOUCH_CM):
            keep.append(c)
        else:
            skipped.append('%s -> %s (not touching)' % (label, c))
    a.modify()
    a.set_editor_property('outline_children', [acts[c] for c in keep])
    log.append('%s outline children: %s' % (label, ', '.join(keep) or '(none)'))
if skipped:
    log.append('SKIPPED: ' + '; '.join(skipped))

assert L.save_all_dirty_levels()
unreal.log('[Rev02 outline bodies]\n' + '\n'.join(log))
