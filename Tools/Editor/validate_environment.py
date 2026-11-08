"""Validate saved apartment's critical click paths in an open editor."""
import unreal
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.load_level('/Game/ICanFixHim/Maps/L_Apartment')
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
by = {a.get_actor_label(): a for a in actors}
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
for parent, child in (('Malady_FuseBox','FuseWallAge'), ('Malady_FuseBox','BrokenFuseDetails'), ('Malady_FuseBox','FusePlasterDamage'), ('Malady_PinkTile','DamagedPinkTile'), ('Malady_Mold','MoldDamage'), ('Malady_Sink','SinkFloorWear'), ('Malady_Sink','SinkWallStain')):
    if child not in [a.get_actor_label() for a in by[parent].get_attached_actors()]:
        raise RuntimeError(child + ' is not attached to ' + parent)
for label in ('FloorLamp', 'BedLamp', 'TV', 'Fridge_Door', 'Stove_Burner', 'Kitchen_Drawer', 'Wardrobe_Door', 'Dresser_Drawer', 'Toilet_Lid', 'Tub_Faucet', 'Bed', 'Malady_Sink', 'Malady_FuseBox', 'Malady_PinkTile', 'Malady_Mold'):
    actor = by[label]
    body = actor.get_editor_property('body')
    target = unreal.MathLibrary.transform_location(body.get_world_transform(), body.get_editor_property('static_mesh').get_bounds().origin)
    start = target + actor.get_actor_forward_vector() * 150
    trace = unreal.SystemLibrary.line_trace_single(world, start, target, unreal.TraceTypeQuery.ECC_VISIBILITY, False, [], unreal.DrawDebugTrace.NONE, True)
    if trace is None:
        raise RuntimeError(label + ' trace hit nothing')
    result = trace.to_dict()
    hit = result['hit_actor']
    if hit != actor:
        raise RuntimeError('%s trace hit %s' % (label, hit.get_actor_label() if hit else 'nothing'))
unreal.log('[Environment validation] critical visibility traces and repair attachments passed')
# Room thresholds must admit the player capsule after art changes.
for label, start, end in (
    ('living-kitchen', (720,540,100), (880,540,100)),
    ('bed-bath', (720,910,100), (880,910,100)),
    ('living-bedroom', (620,570,100), (620,730,100)),
    ('kitchen-bath', (1100,570,100), (1100,730,100)),
):
    hit = unreal.SystemLibrary.capsule_trace_single_for_objects(
        world, unreal.Vector(*start), unreal.Vector(*end), 34, 88,
        [unreal.ObjectTypeQuery.ECC_WORLD_STATIC], False, [], unreal.DrawDebugTrace.NONE, True)
    if hit is not None:
        a = hit.to_dict()['hit_actor']
        raise RuntimeError('%s doorway obstructed by %s' % (label, a.get_actor_label() if a else 'unknown'))
unreal.log('[Environment validation] doorway capsule sweeps passed')
