"""Import the shared licensed fonts and icons. Run prepare_assets.py first. Safe to rerun."""
from pathlib import Path
import unreal
root=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()))
source=root/'Art Source/UI/Design'
e=unreal.EditorAssetLibrary
for kind,pattern in [('Fonts','*.ttf'),('Icons','*.png'),('Brand','*.png')]:
    destination='/Game/ICanFixHim/UI/Design/'+kind
    e.make_directory(destination)
    for p in (source/kind).glob(pattern):
        task=unreal.AssetImportTask()
        task.filename=str(p); task.destination_path=destination; task.destination_name=p.stem
        task.automated=True; task.replace_existing=True; task.save=False
        if kind=='Fonts':
            factory=unreal.FontFileImportFactory()
            factory.set_editor_property('batch_create_font_asset',unreal.BatchCreateFontAsset.NO)
            task.factory=factory
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
        asset=e.load_asset(destination+'/'+p.stem)
        assert asset, f'Missing imported asset {p}'
        if kind in ('Icons','Brand'):
            asset.set_editor_property('lod_group',unreal.TextureGroup.TEXTUREGROUP_UI)
            asset.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_EDITOR_ICON)
            asset.set_editor_property('mip_gen_settings',unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS)
            asset.set_editor_property('filter',unreal.TextureFilter.TF_BILINEAR)
            asset.set_editor_property('srgb',True)
        assert e.save_loaded_asset(asset)
        unreal.log(f'[DesignSystem] {asset.get_path_name()} ({asset.get_class().get_name()})')
if '-DesignSystemImportAndQuit' in unreal.SystemLibrary.get_command_line():
    unreal.SystemLibrary.quit_editor()
