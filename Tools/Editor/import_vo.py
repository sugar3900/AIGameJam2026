"""
Import the generated voice-over WAVs into /Game/ICanFixHim/Audio/VO/<script>/.

    python3 Tools/run_in_editor.py Tools/Editor/import_vo.py

Re-imports every clip (they're small, so it's quick), and deletes clips whose WAV no longer exists (lines that
were cut or reworded into silence). Source WAVs come from Tools/Audio/generate_vo.py.
"""
import json
import os

import unreal

ROOT = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())
SRC = os.path.join(ROOT, "Art Source/Audio/VO")
DEST = "/Game/ICanFixHim/Audio/VO"

with open(os.path.join(SRC, "manifest.json"), encoding="utf-8") as f:
    manifest = json.load(f)

eal = unreal.EditorAssetLibrary
tasks = []
wanted = set()
for rel in manifest:
    script, filename = rel.split("/")
    name = os.path.splitext(filename)[0]
    folder = f"{DEST}/{script}"
    wanted.add(f"{folder}/{name}")
    src = os.path.join(SRC, rel)
    task = unreal.AssetImportTask()
    task.set_editor_property("filename", src)
    task.set_editor_property("destination_path", folder)
    task.set_editor_property("destination_name", name)
    task.set_editor_property("automated", True)
    task.set_editor_property("replace_existing", True)
    task.set_editor_property("save", True)
    tasks.append(task)

unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)

# Drop clips for lines that were cut or are no longer voiced.
removed = 0
for path in eal.list_assets(DEST, recursive=True, include_folder=False):
    obj_path = path.split(".")[0]
    if obj_path not in wanted:
        eal.delete_asset(obj_path)
        # With git source control on, delete_asset can drop the package from memory but leave a
        # newly added .uasset on disk (it then reappears on the next scan), so remove the file too.
        leftover = unreal.Paths.convert_relative_path_to_full(
            unreal.Paths.project_content_dir() + obj_path[len("/Game/"):] + ".uasset")
        if os.path.exists(leftover):
            os.remove(leftover)
        removed += 1

unreal.log(f"import_vo: {len(tasks)} clips imported, {removed} orphans removed")
