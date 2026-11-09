"""Give the redesign's imported art meshes collision the game can use.

The Blender FBX imports carry no simple collision. The player's click trace (FixHimPlayerController::UpdateHover,
ECC_Visibility, bTraceComplex=false) and the pawn's movement both use simple collision only, so without this
every art-body interactable (doors, drawers, lamps) is unclickable and the player walks through furniture.
Each mesh used by a visible actor in the redesign (environment map + streamed gameplay sublevel) that has no
simple shapes is switched to "use complex collision as simple": exact triangles, so open frames, cabinets and
closets keep their openings (a bounding box would seal a doorway). Meshes that already have simple shapes and
engine meshes (walls, the sky sphere, gameplay proxies) are left alone. Re-runnable; run again after re-importing art.
"""
import unreal
MAP = '/Game/ICanFixHim/Maps/L_Apartment_Redesign_Blockout'
ROOT = '/Game/ICanFixHim/Environment/Redesign/'
A = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
SM = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
assert L.load_level(MAP)

meshes = {}
for a in A.get_all_level_actors():
    comps = []
    if isinstance(a, unreal.FixHimInteractable):
        comps = [a.get_editor_property('body')]
    elif isinstance(a, unreal.StaticMeshActor) and not a.is_hidden_ed() and not a.actor_has_tag('GameplayBodySource'):
        comps = [a.static_mesh_component]
    for c in comps:
        m = c.static_mesh if c else None
        if m and m.get_path_name().startswith(ROOT):
            meshes[m.get_path_name()] = m

changed, kept = [], 0
for path, m in sorted(meshes.items()):
    bs = m.get_editor_property('body_setup')
    if SM.get_simple_collision_count(m) > 0 or (bs and bs.get_editor_property('collision_trace_flag') == unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE):
        kept += 1
        continue
    if not bs:
        unreal.log_warning('[Collision] %s has no body setup; skipped' % path)
        continue
    m.modify(); bs.modify()
    bs.set_editor_property('collision_trace_flag', unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
    # Changing the body setup through set_editor_property runs its PostEditChange, which rebuilds the cooked
    # physics data; saving makes it stick for the game and for other checkouts.
    assert unreal.EditorAssetLibrary.save_loaded_asset(m, False), path
    changed.append(m.get_name())
unreal.log('[Collision] complex-as-simple set on %d meshes (%d already had collision): %s' % (len(changed), kept, ', '.join(changed)))
