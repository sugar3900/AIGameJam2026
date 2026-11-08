"""
Imports the dialogue portraits: "Art Source/Portraits/T_Portrait_<Name>.png" -> /Game/ICanFixHim/UI/Portraits/T_Portrait_<Name>
(UI texture settings, same as T_Heart: UI LOD group, TC_EDITOR_ICON, no mips). Only the portrait textures are touched.

The PNGs are made by Tools/Art/Portraits/render_portraits.py. A hunk shows his portrait when his dialogue JSON sets
look.portrait (Content/ICanFixHim/Data/Dialogue/*.json); the player's is PlayerPortraitTexture in Config/DefaultGame.ini.
/Game/ICanFixHim/UI/Portraits is always cooked (Config/DefaultGame.ini), since only JSON strings reference most of them.

Run inside the editor (python3 Tools/run_in_editor.py Tools/Editor/import_portraits.py), or headless:
    UnrealEditor-Cmd ICanFixHim.uproject -run=pythonscript -script=Tools/Editor/import_portraits.py -unattended -nullrhi
Idempotent.
"""
import glob
import os

import unreal

ASSETS = unreal.AssetToolsHelpers.get_asset_tools()
EAL = unreal.EditorAssetLibrary
PROJECT_DIR = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())
SRC_DIR = os.path.join(PROJECT_DIR, "Art Source", "Portraits")
DEST_DIR = "/Game/ICanFixHim/UI/Portraits"


def main():
    EAL.make_directory(DEST_DIR)
    sources = sorted(glob.glob(os.path.join(SRC_DIR, "T_Portrait_*.png")))
    if not sources:
        unreal.log_warning(f"[FixHim] no portraits in {SRC_DIR}; run Tools/Art/Portraits/render_portraits.py")
        return
    tasks = []
    for src in sources:
        t = unreal.AssetImportTask()
        t.set_editor_property("filename", src)
        t.set_editor_property("destination_path", DEST_DIR)
        t.set_editor_property("destination_name", os.path.splitext(os.path.basename(src))[0])
        t.set_editor_property("replace_existing", True)
        t.set_editor_property("automated", True)
        t.set_editor_property("save", False)
        tasks.append(t)
    ASSETS.import_asset_tasks(tasks)
    for src in sources:
        name = os.path.splitext(os.path.basename(src))[0]
        tex = EAL.load_asset(f"{DEST_DIR}/{name}")
        if not tex:
            unreal.log_error(f"[FixHim] failed to import {src}")
            continue
        tex.set_editor_property("lod_group", unreal.TextureGroup.TEXTUREGROUP_UI)
        tex.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_EDITOR_ICON)
        tex.set_editor_property("mip_gen_settings", unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS)
        EAL.save_loaded_asset(tex, only_if_is_dirty=False)
        unreal.log(f"[FixHim] imported {DEST_DIR}/{name}")
    unreal.log("[FixHim] import_portraits done")


main()
