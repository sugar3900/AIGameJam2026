"""
Blender script: re-exports the Tripo character FBXs from "Art Source/Character Art" as UE-friendly FBXs
in SourceArt/Generated/Characters/<Folder>.fbx (then run Tools/Editor/import_characters.py in the editor).

Why: Tripo exports in metres and stores the unit conversion as a 100x scale on the root bone. Unreal keeps
that scale in the skeleton's reference pose, and any animation (which keys the root at scale 1) collapses
the body to a few centimetres. Round-tripping through Blender bakes the units into the bones, and we also
scale the model to mannequin height (Tripo normalizes everything to 1m tall).

    /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup --python Tools/Art/prepare_characters.py
"""
import glob
import os

import bpy
from mathutils import Vector

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC_DIR = os.path.join(ROOT, "Art Source", "Character Art")
OUT_DIR = os.path.join(ROOT, "SourceArt", "Generated", "Characters")
TARGET_HEIGHT_M = 1.8

# Source folder -> output name (keep in sync with Tools/Editor/import_characters.py).
CHARACTERS = {
    "Black Mold": "BlackMold",
    "Faulty Wiring": "FaultyWiring",
    "Lead Paint": "LeadPaint",
    "Leaky Pipes": "LeakyPipes",
    "Pink Tile": "PinkTile",
}


def convert(src, dst):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    # Work in centimetres so the exported FBX needs no unit conversion in Unreal.
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 0.01
    bpy.ops.import_scene.fbx(filepath=src)

    arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
    meshes = [o for o in bpy.data.objects if o.type == "MESH"]
    arm.name = "Armature"  # Unreal skips an armature node with this name instead of adding an extra bone

    bpy.context.view_layer.update()
    zs = [(o.matrix_world @ Vector(c)).z for o in meshes for c in o.bound_box]
    height = max(zs) - min(zs)
    factor = TARGET_HEIGHT_M * 100.0 / height  # scene units are centimetres
    arm.scale = [s * factor for s in arm.scale]

    bpy.ops.object.select_all(action="DESELECT")
    for o in [arm] + meshes:
        o.select_set(True)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

    os.makedirs(os.path.dirname(dst), exist_ok=True)
    bpy.ops.export_scene.fbx(
        filepath=dst,
        use_selection=False,
        object_types={"ARMATURE", "MESH"},
        apply_unit_scale=True,
        apply_scale_options="FBX_SCALE_NONE",
        global_scale=1.0,
        axis_forward="-Z",
        axis_up="Y",
        add_leaf_bones=False,
        use_armature_deform_only=False,
        bake_anim=False,
        path_mode="STRIP",
        embed_textures=False,
        mesh_smooth_type="FACE",
    )
    print(f"[prepare_characters] {os.path.relpath(src, ROOT)} -> {os.path.relpath(dst, ROOT)} "
          f"(imported height {height:.1f} units, scaled x{factor:.3f}, armature scale {tuple(arm.scale)})")


def main():
    for src_name, out_name in CHARACTERS.items():
        fbxs = glob.glob(os.path.join(SRC_DIR, src_name, "*", "*.fbx"))
        if not fbxs:
            print(f"[prepare_characters] no FBX for {src_name}")
            continue
        convert(fbxs[0], os.path.join(OUT_DIR, out_name + ".fbx"))


main()
