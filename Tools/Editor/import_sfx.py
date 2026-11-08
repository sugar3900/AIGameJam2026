"""
Import the generated sound effects into /Game/ICanFixHim/Audio/SFX/.

    python3 Tools/run_in_editor.py Tools/Editor/import_sfx.py

Re-imports every file (they're tiny) and deletes assets whose WAV no longer exists. Source WAVs come from
Tools/Audio/generate_sfx.py. The game finds them by name (SFX_<Name>[_<n>]) via FixHimSfxSubsystem.
"""
import json
import os

import unreal

ROOT = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())
SRC = os.path.join(ROOT, "Art Source/Audio/SFX")
DEST = "/Game/ICanFixHim/Audio/SFX"

with open(os.path.join(SRC, "manifest.json"), encoding="utf-8") as f:
    manifest = json.load(f)

eal = unreal.EditorAssetLibrary
tasks = []
wanted = set()
for filename in manifest:
    name = os.path.splitext(filename)[0]
    wanted.add(f"{DEST}/{name}")
    task = unreal.AssetImportTask()
    task.set_editor_property("filename", os.path.join(SRC, filename))
    task.set_editor_property("destination_path", DEST)
    task.set_editor_property("destination_name", name)
    task.set_editor_property("automated", True)
    task.set_editor_property("replace_existing", True)
    task.set_editor_property("save", True)
    tasks.append(task)

unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)

removed = 0
if eal.does_directory_exist(DEST):
    for path in eal.list_assets(DEST, recursive=True, include_folder=False):
        obj_path = path.split(".")[0]
        if obj_path not in wanted:
            eal.delete_asset(obj_path)
            removed += 1

unreal.log(f"import_sfx: {len(tasks)} sounds imported, {removed} orphans removed")
