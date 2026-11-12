"""Import the reticle animation layers as UI textures (sRGB, alpha, no mips, bilinear).
First: python3 Tools/Art/Reticles/render_reticles.py
Then run in editor or UnrealEditor-Cmd -run=pythonscript -script=<this file>.
128px sources draw in a 64-unit box: 1:1 at 4K, 1.5x/2x minification at 1440p/1080p, where plain
bilinear is already correct and mips would only blend in a blurrier half-size level.
Unavailable remains a reserved SVG, with no runtime texture or state.
"""
from pathlib import Path
import unreal

source = Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())) / 'Art Source/UI/Reticles'
destination = '/Game/ICanFixHim/UI/Reticles'
LAYERS = ('Background', 'Ring', 'Dot', 'Icon_Inspect', 'Icon_Talk', 'Icon_Use', 'Icon_EndDay')
eal = unreal.EditorAssetLibrary
eal.make_directory(destination)
for layer in LAYERS:
    name = f'T_Reticle_{layer}'
    png = source / f'{name}.png'
    assert png.is_file(), f'Missing {png}; run render_reticles.py first'
    task = unreal.AssetImportTask()
    task.filename = str(png)
    task.destination_path = destination
    task.destination_name = name
    task.replace_existing = True
    task.automated = True
    task.save = False
    task.set_editor_property('async_', False)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    path = f'{destination}/{name}'
    texture = eal.load_asset(path) or unreal.load_object(None, f'{path}.{name}')
    assert texture, f'Import failed: {name}'
    texture.set_editor_property('lod_group', unreal.TextureGroup.TEXTUREGROUP_UI)
    texture.set_editor_property('compression_settings', unreal.TextureCompressionSettings.TC_EDITOR_ICON)
    texture.set_editor_property('mip_gen_settings', unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS)
    texture.set_editor_property('filter', unreal.TextureFilter.TF_BILINEAR)
    texture.set_editor_property('never_stream', False)
    texture.set_editor_property('srgb', True)
    assert unreal.EditorLoadingAndSavingUtils.save_packages([texture.get_outermost()], False)
    uasset = Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_content_dir())) / 'ICanFixHim/UI/Reticles' / f'{name}.uasset'
    assert uasset.is_file(), f'{name} did not save to disk'
    unreal.log(f'[Reticles] Imported {name}')
