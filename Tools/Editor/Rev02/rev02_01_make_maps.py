"""Rev02 step 1: make the Rev02 map pair as fresh copies of the A+ redesign maps.

The approved revision 02 layout (docs/03 Art & Audio/Apartment Design/layout-revision-02/README.md) is built by
deriving it from the shipped A+ maps: every later Rev02 step operates on these copies, so the A+ maps (the game's
current default) stay untouched until the Rev02 review is accepted. Re-running starts over from the A+ maps.

    L_Apartment_Redesign_Blockout  -> L_Apartment_Rev02           (environment)
    L_Apartment_Redesign_Gameplay  -> L_Apartment_Rev02_Gameplay  (streamed, always loaded)
"""
import unreal
EAL = unreal.EditorAssetLibrary
L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
UES = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
M = '/Game/ICanFixHim/Maps/'
SRC_ENV, SRC_GAME = M + 'L_Apartment_Redesign_Blockout', M + 'L_Apartment_Redesign_Gameplay'
ENV, GAME = M + 'L_Apartment_Rev02', M + 'L_Apartment_Rev02_Gameplay'

assert L.load_level(SRC_ENV)          # never hold a Rev02 map open while replacing it
unreal.SystemLibrary.collect_garbage()   # a previously open Rev02 world lingers in memory (blocking deletion) until collected
import os
CONTENT = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_content_dir())
for path in (ENV, GAME):
    if EAL.does_asset_exist(path):
        EAL.delete_asset(path)
    if EAL.does_asset_exist(path):
        # In -unattended sessions delete_asset can report success yet keep the package (its confirmation is
        # auto-cancelled). These maps are generated outputs and not loaded at this point, so remove the files.
        assert unreal.find_object(None, path + '.' + path.split('/')[-1]) is None, path + ' is still loaded'
        os.remove(os.path.join(CONTENT, path[len('/Game/'):] + '.umap'))
unreal.AssetRegistryHelpers.get_asset_registry().scan_paths_synchronous(['/Game/ICanFixHim/Maps'], True)
assert not EAL.does_asset_exist(ENV) and not EAL.does_asset_exist(GAME), 'old Rev02 maps still present'
assert EAL.duplicate_asset(SRC_GAME, GAME) and EAL.duplicate_asset(SRC_ENV, ENV)
EAL.save_asset(GAME, False); EAL.save_asset(ENV, False)

# The copied environment map still streams the A+ gameplay sublevel; point it at the Rev02 copy.
assert L.load_level(ENV)
world = UES.get_editor_world()
for lvl in unreal.EditorLevelUtils.get_levels(world):
    if lvl.get_outermost().get_name().endswith('/L_Apartment_Redesign_Gameplay'):
        assert unreal.EditorLevelUtils.remove_level_from_world(lvl)
world = UES.get_editor_world()
unreal.EditorLevelUtils.add_level_to_world(world, GAME, unreal.LevelStreamingAlwaysLoaded)
world = UES.get_editor_world()
names = [l.get_outermost().get_name() for l in unreal.EditorLevelUtils.get_levels(world)]
assert names.count(ENV) == 1 and names.count(GAME) == 1 and not any(n.endswith('Redesign_Gameplay') for n in names), names
assert L.save_all_dirty_levels()
unreal.log('[Rev02] maps ready: %s' % names)
