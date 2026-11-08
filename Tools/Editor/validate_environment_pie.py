"""Run while PIE is active; checks spawned hunks, cameras and moving props."""
import unreal
worlds = unreal.EditorLevelLibrary.get_pie_worlds(False)
if not worlds:
    raise RuntimeError('Start PIE before running this validation')
w = worlds[0]
interactables = unreal.GameplayStatics.get_all_actors_of_class(w, unreal.FixHimInteractable)
by = {a.get_actor_label(): a for a in interactables}
hunks = unreal.GameplayStatics.get_all_actors_of_class(w, unreal.FixHimHunk)
if len(hunks) != 4:
    raise RuntimeError('Expected four spawned hunks; got %d' % len(hunks))
for hunk in hunks:
    if not 60 < hunk.get_actor_location().z < 240:
        raise RuntimeError('Unexpected hunk height: ' + str(hunk.get_actor_location()))
for label in ('Fridge_Door', 'Wardrobe_Door', 'Dresser_Drawer', 'Kitchen_Drawer'):
    actor = by[label]
    body = actor.get_editor_property('body')
    materials = [body.get_material(i).get_path_name() for i in range(body.get_num_materials())]
    if len(set(materials)) < 2:
        raise RuntimeError(label + ' lost authored material variety')
    pivot = actor.get_editor_property('pivot')
    old = actor.get_editor_property('is_on')
    before = pivot.get_relative_transform()
    actor.set_on(not old, True)
    after = pivot.get_relative_transform()
    actor.set_on(old, True)
    if before == after:
        raise RuntimeError(label + ' did not move')
unreal.log('[Environment PIE validation] hunk heights and moving material meshes passed')
by_hunk = {h.get_editor_property('hunk_id'): h for h in hunks}
for malady in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.FixHimMalady):
    hunk = by_hunk.get(malady.get_editor_property('hunk_id'))
    if not hunk:
        raise RuntimeError('Missing hunk for ' + malady.get_name())
    head = hunk.get_actor_location() + unreal.Vector(0, 0, 62)
    camera = malady.get_editor_property('dialogue_camera').get_world_location()
    hit = unreal.SystemLibrary.line_trace_single(w, head, camera, unreal.TraceTypeQuery.ECC_VISIBILITY,
                                                False, [malady, hunk], unreal.DrawDebugTrace.NONE, True)
    if hit is not None:
        obstruction = hit.to_dict()['hit_actor']
        raise RuntimeError('Dialogue sightline obstructed for %s by %s' %
                           (malady.get_editor_property('hunk_id'), obstruction.get_name() if obstruction else 'unknown'))
unreal.log('[Environment PIE validation] dialogue sightlines passed')
for label in ('FloorLamp', 'BedLamp'):
    lamp = by[label]
    was_on = lamp.get_editor_property('is_on')
    lamp.set_on(True, True)
    if lamp.get_editor_property('light').get_editor_property('intensity') <= 0:
        raise RuntimeError(label + ' did not turn on')
    lamp.set_on(was_on, True)
bed = by['Bed']
if not bed.get_editor_property('use_authored_body_materials'):
    raise RuntimeError('Bed did not preserve its authored quilt material')
unreal.log('[Environment PIE validation] floor lamp and authored bed passed')

for label in ('Toilet_Lid',):
    actor = by[label]
    pivot = actor.get_editor_property('pivot')
    old = actor.get_editor_property('is_on')
    before = pivot.get_relative_transform()
    actor.set_on(not old, True)
    after = pivot.get_relative_transform()
    actor.set_on(old, True)
    if before == after:
        raise RuntimeError(label + ' did not move')
faucet = by['Tub_Faucet']
old = faucet.get_editor_property('is_on')
faucet.set_on(True, True)
if not faucet.get_editor_property('reveal_part').is_visible():
    raise RuntimeError('Tub faucet did not reveal water')
faucet.set_on(old, True)
unreal.log('[Environment PIE validation] toilet lid and tub faucet passed')
