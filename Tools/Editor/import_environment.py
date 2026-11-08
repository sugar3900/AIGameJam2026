"""Import authored environment meshes. Run in the isolated project's editor."""
import os
import unreal
root = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())
source = os.path.join(root, 'Art Source', 'Environment Models')
if unreal.EditorLevelLibrary.get_pie_worlds(False):
    raise RuntimeError('Stop PIE before importing environment assets')
tools = unreal.AssetToolsHelpers.get_asset_tools()
for name in ('SM_VintageFridgeBody', 'SM_VintageRange', 'SM_VintageSofa', 'SM_ClawfootTub', 'SM_VintageBed', 'SM_VintageDresser', 'SM_VintageWardrobe', 'SM_VintageToiletBody', 'SM_PedestalSink', 'SM_KitchenSinkCabinet', 'SM_RetroFridgeDoor', 'SM_EnamelKettle', 'SM_RepairBucket', 'SM_FramedPicture', 'SM_GatheredCurtains', 'SM_VintageFloorLamp', 'SM_OldBookshelf', 'SM_OldRadiator', 'SM_WovenRug', 'SM_TowelRail', 'SM_BathMirror', 'SM_CrackedPinkTilePanel', 'SM_BedsideLamp', 'SM_TowelBasket', 'SM_DampStain', 'SM_WardrobeDoor', 'SM_DresserDrawer', 'SM_PlaidCushion', 'SM_FoldedThrow', 'SM_StackedBooks', 'SM_RepairCaddy', 'SM_VintageTableLamp', 'SM_DamagedFuseboxOverlay', 'SM_PlasterDamage', 'SM_RumpledQuilt', 'SM_VintageNightstand', 'SM_BaseCabinet96', 'SM_BaseCabinet86', 'SM_KitchenDrawer', 'SM_UpperKitchenCabinet', 'SM_HangingPans', 'SM_VintageCoffeeTable', 'SM_VintageTVStand', 'SM_VintageTVFrame', 'SM_FloorLampBase', 'SM_FloorLampShade', 'SM_LeafyPottedPlant', 'SM_VintageDiningTable', 'SM_VintageDiningChair', 'SM_FruitBowl', 'SM_ToiletLid', 'SM_TubFaucet', 'SM_MoldedFrontDoor'):
    task = unreal.AssetImportTask()
    task.filename = os.path.join(source, name + '.fbx')
    task.destination_path = '/Game/ICanFixHim/Environment/Meshes'
    task.destination_name = name
    task.automated = True
    task.replace_existing = True
    task.save = True
    options = unreal.FbxImportUI()
    options.import_mesh = True
    options.import_materials = False
    options.import_textures = False
    options.import_as_skeletal = False
    options.static_mesh_import_data.set_editor_property('auto_generate_collision', True)
    task.options = options
    tools.import_asset_tasks([task])
    mesh = unreal.EditorAssetLibrary.load_asset(task.destination_path + '/' + name)
    if not mesh:
        raise RuntimeError('Failed to import ' + name)
    unreal.log('[Environment] %s bounds %s slots %s' % (name, mesh.get_bounds().box_extent, [str(x.material_slot_name) for x in mesh.static_materials]))
