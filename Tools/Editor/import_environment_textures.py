"""Import generated environment textures and create simple materials.

Run Tools/Art/Environment/generate_aged_textures.py in headless Blender first,
then run this script in the environment project's Unreal editor. Tile materials
use world-space UVs in centimetres; overlays use regular mesh UVs, translucent
alpha, and should be put on non-colliding planes just in front of the surface.
"""
import os
import unreal

DEST = '/Game/ICanFixHim/Materials/Environment'
ROOT = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())
SOURCE = os.path.join(ROOT, 'Art Source', 'Environment Textures')
ASSETS = unreal.AssetToolsHelpers.get_asset_tools()
EAL = unreal.EditorAssetLibrary
MEL = unreal.MaterialEditingLibrary
TEXTURES = ('T_Floorboards', 'T_AgedSagePaint', 'T_PinkTile', 'T_WaterStain_Overlay', 'T_TileCrack_Overlay', 'T_KitchenChecker', 'T_FloralWallpaper', 'T_FloralRug', 'T_PaintedPlaster', 'T_KitchenCheckerPainted', 'T_RoseQuilt', 'T_IvoryPillow', 'T_Mold_Overlay', 'T_KitchenBacksplash', 'T_CabinetSage', 'T_FloralWallpaperWorn', 'T_LinoleumWear_Overlay', 'T_BathMosaic', 'T_SinkStain_Overlay', 'T_IvoryEnamel', 'T_WarmWood')


def node(mat, cls, x, y, **properties):
    n = MEL.create_material_expression(mat, cls, x, y)
    for key, value in properties.items():
        n.set_editor_property(key, value)
    return n


def run():
    tasks = []
    for name in TEXTURES:
        filename = os.path.join(SOURCE, name + '.png')
        if not os.path.isfile(filename):
            raise RuntimeError('Missing environment texture: ' + filename)
        t = unreal.AssetImportTask()
        t.filename = filename
        t.destination_path = DEST
        t.destination_name = name
        t.automated = True
        t.replace_existing = True
        t.save = True
        tasks.append(t)
    ASSETS.import_asset_tasks(tasks)
    for name in TEXTURES:
        tex = EAL.load_asset(DEST + '/' + name)
        if not tex:
            raise RuntimeError('Texture import failed: ' + name)
        if name in ('T_FloralWallpaper', 'T_FloralRug', 'T_PaintedPlaster', 'T_KitchenCheckerPainted', 'T_RoseQuilt', 'T_IvoryPillow', 'T_Mold_Overlay', 'T_KitchenBacksplash', 'T_CabinetSage', 'T_FloralWallpaperWorn', 'T_BathMosaic', 'T_IvoryEnamel', 'T_WarmWood'):
            tex.set_editor_property('power_of_two_mode', unreal.TexturePowerOfTwoSetting.STRETCH_TO_POWER_OF_TWO)
            EAL.save_loaded_asset(tex)
        overlay = name.endswith('_Overlay')
        matname = 'M_' + name[2:]
        path = DEST + '/' + matname
        if EAL.does_asset_exist(path):
            mat = EAL.load_asset(path)
            MEL.delete_all_material_expressions(mat)
        else:
            mat = ASSETS.create_asset(matname, DEST, unreal.Material, unreal.MaterialFactoryNew())
        if name in ('T_PinkTile', 'T_KitchenBacksplash'):
            mat.set_editor_property('two_sided', True)
        if overlay:
            mat.set_editor_property('blend_mode', unreal.BlendMode.BLEND_TRANSLUCENT)
            mat.set_editor_property('two_sided', True)
        sample = node(mat, unreal.MaterialExpressionTextureSample, -200, 0, texture=tex)
        if not overlay and name not in ('T_FloralRug', 'T_RoseQuilt', 'T_IvoryPillow'):
            # Map each texture tile over 200cm; dominant face projection avoids
            # stretching when the engine cube is scaled into a wall or floor.
            pos = node(mat, unreal.MaterialExpressionWorldPosition, -1000, -100)
            normal = node(mat, unreal.MaterialExpressionPixelNormalWS, -1000, 80)
            scale = ('48.0' if name == 'T_BathMosaic' else
                     '120.0' if name in ('T_KitchenChecker', 'T_KitchenCheckerPainted') else
                     '160.0' if name in ('T_IvoryEnamel', 'T_WarmWood') else
                     '60.0' if name in ('T_PinkTile', 'T_KitchenBacksplash') else '200.0')
            projection = 'float3 n=abs(N); float2 uv=(n.z>=max(n.x,n.y)?P.xy:(n.x>=n.y?P.yz:P.xz))/' + scale + ';'
            projection += 'return abs(frac(uv*0.5)*2.0-1.0);' if name in ('T_FloralWallpaper', 'T_PaintedPlaster', 'T_CabinetSage', 'T_FloralWallpaperWorn', 'T_IvoryEnamel', 'T_WarmWood') else 'return uv;'
            uv = node(mat, unreal.MaterialExpressionCustom, -600, 0,
                      code=projection,
                      output_type=unreal.CustomMaterialOutputType.CMOT_FLOAT2,
                      description='World-projected surface UV')
            inputs = []
            for input_name in ('P','N'):
                inp = unreal.CustomInput()
                inp.set_editor_property('input_name', input_name)
                inputs.append(inp)
            uv.set_editor_property('inputs', inputs)
            MEL.connect_material_expressions(pos, '', uv, 'P')
            MEL.connect_material_expressions(normal, '', uv, 'N')
            MEL.connect_material_expressions(uv, '', sample, 'UVs')
        MEL.connect_material_property(sample, 'RGB', unreal.MaterialProperty.MP_BASE_COLOR)
        rough_value = .58 if name == 'T_IvoryEnamel' else (.76 if name == 'T_WarmWood' else .82)
        rough = node(mat, unreal.MaterialExpressionConstant, -200, 250, r=rough_value)
        MEL.connect_material_property(rough, '', unreal.MaterialProperty.MP_ROUGHNESS)
        if overlay:
            MEL.connect_material_property(sample, 'A', unreal.MaterialProperty.MP_OPACITY)
        MEL.layout_material_expressions(mat)
        MEL.recompile_material(mat)
        EAL.save_loaded_asset(mat)
        unreal.log('[FixHim] Created ' + path)


if __name__ == '__main__':
    run()
