"""Import only the five runtime reticles as UI textures (no mips, sRGB, alpha).
First: python3 Tools/Art/Reticles/render_reticles.py
Then run in editor or UnrealEditor-Cmd -run=pythonscript -script=<this file>.
Unavailable remains a reserved SVG, with no runtime texture or state.
"""
from pathlib import Path
import unreal

source = Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())) / 'Art Source/UI/Reticles'
destination = '/Game/ICanFixHim/UI/Reticles'
eal = unreal.EditorAssetLibrary
eal.make_directory(destination)
for state in ('Default', 'Inspect', 'Talk', 'Use', 'EndDay'):
    name = f'T_Reticle_{state}'
    png = source / f'{name}.png'
    assert png.is_file(), f'Missing {png}; run render_reticles.py first'
    task = unreal.AssetImportTask()
    task.filename = str(png)
    task.destination_path = destination
    task.destination_name = name
    task.replace_existing = True
    task.automated = True
    task.save = False
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    texture = eal.load_asset(f'{destination}/{name}')
    assert texture, f'Import failed: {name}'
    texture.set_editor_property('lod_group', unreal.TextureGroup.TEXTUREGROUP_UI)
    texture.set_editor_property('compression_settings', unreal.TextureCompressionSettings.TC_EDITOR_ICON)
    texture.set_editor_property('mip_gen_settings', unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS)
    texture.set_editor_property('srgb', True)
    assert eal.save_loaded_asset(texture, only_if_is_dirty=False)
    unreal.log(f'[Reticles] Imported {name}')
