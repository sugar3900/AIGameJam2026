"""
Import the generated background music into /Game/ICanFixHim/Audio/BGM/.

    UnrealEditor-Cmd ICanFixHim.uproject -ExecutePythonScript=<abs>/Tools/Editor/import_bgm.py -unattended -nullrhi

Source WAVs come from Tools/Audio/generate_bgm.py. Every track is imported as BGM_<Name>, flagged Looping, and set to
load on demand (music is long, so it is not kept resident). Orphaned assets (WAV deleted) are removed. The game
finds them by name via FixHimMusicSubsystem.
"""
import json
import os

import unreal

ROOT = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())
SRC = os.path.join(ROOT, "Art Source/Audio/BGM")
DEST = "/Game/ICanFixHim/Audio/BGM"

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


def try_set(wave, prop, value):
    try:
        wave.set_editor_property(prop, value)
        return True
    except Exception as e:  # property absent in this engine version
        unreal.log_warning(f"import_bgm: could not set {prop}: {e}")
        return False


for obj_path in sorted(wanted):
    wave = eal.load_asset(obj_path)
    if not wave:
        unreal.log_error(f"import_bgm: {obj_path} failed to import")
        continue
    try_set(wave, "looping", True)
    try_set(wave, "loading_behavior", unreal.SoundWaveLoadingBehavior.LOAD_ON_DEMAND)
    try_set(wave, "compression_quality", 60)
    eal.save_loaded_asset(wave)

removed = 0
if eal.does_directory_exist(DEST):
    for path in eal.list_assets(DEST, recursive=True, include_folder=False):
        obj_path = path.split(".")[0]
        if obj_path not in wanted:
            eal.delete_asset(obj_path)
            removed += 1

# Re-open from disk state and report what stuck.
for obj_path in sorted(wanted):
    wave = eal.load_asset(obj_path)
    if wave:
        unreal.log(f"import_bgm: {obj_path} looping={wave.get_editor_property('looping')} "
                   f"loading_behavior={wave.get_editor_property('loading_behavior')}")
unreal.log(f"import_bgm: {len(tasks)} tracks imported, {removed} orphans removed")
