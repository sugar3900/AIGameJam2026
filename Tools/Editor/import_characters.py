"""
Imports the rigged hunk models into the project. Meshes come from SourceArt/Generated/Characters/<Folder>.fbx
(made from the Tripo exports in "Art Source/Character Art" by Tools/Art/prepare_characters.py in Blender);
textures come straight from the Tripo .fbm folders.

  /Game/ICanFixHim/Materials/M_Hunk                          PBR master: BaseColor/Normal/Roughness/Metallic textures
  /Game/ICanFixHim/Characters/<Folder>/SK_<Folder>           skeletal mesh (+ its own SK_<Folder>_Skeleton)
  /Game/ICanFixHim/Characters/<Folder>/MI_<Folder>           material instance of M_Hunk
  /Game/ICanFixHim/Characters/<Folder>/T_<Folder>_<Map>      textures
  /Game/ICanFixHim/Characters/<Folder>/IK_<Folder>           IK Rig (auto-generated retarget chains)
  /Game/ICanFixHim/Characters/<Folder>/RTG_<Folder>          IK Retargeter, Manny -> this character
  /Game/ICanFixHim/Characters/<Folder>/A_<Folder>_Idle       MM_Idle retargeted onto this character
  /Game/ICanFixHim/Characters/IK_Manny                       source IK Rig for the UE5 mannequin

The rigs use UE5 Mannequin bone *names* but different bone axes and proportions, so they can't share
SK_Mannequin. Each gets its own skeleton and the mannequin idle is retargeted onto it with an IK Retargeter.

A hunk uses its model when its dialogue JSON sets look.mesh / look.idle (Content/ICanFixHim/Data/Dialogue/*.json).

Run inside the editor (python3 Tools/run_in_editor.py Tools/Editor/import_characters.py). Idempotent.
"""
import glob
import os
import runpy
import unreal

MEL = unreal.MaterialEditingLibrary
ASSETS = unreal.AssetToolsHelpers.get_asset_tools()
EAL = unreal.EditorAssetLibrary
PROJECT_DIR = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())
SRC_DIR = os.path.join(PROJECT_DIR, "Art Source", "Character Art")
MESH_DIR = os.path.join(PROJECT_DIR, "SourceArt", "Generated", "Characters")
CHAR_DIR = "/Game/ICanFixHim/Characters"
MAT_DIR = "/Game/ICanFixHim/Materials"
MANNY_MESH = "/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple"
RETARGET_ANIMS = ["/Game/Characters/Mannequins/Anims/Unarmed/MM_Idle"]

# Source folder -> asset folder name.
CHARACTERS = {
    "Black Mold": "BlackMold",
    "Faulty Wiring": "FaultyWiring",
    "Lead Paint": "LeadPaint",
    "Leaky Pipes": "LeakyPipes",
    "Pink Tile": "PinkTile",
}

# (filename fragment, texture map name)
TEXTURE_MAPS = [("rgb", "BaseColor"), ("normal", "Normal"), ("roughness", "Roughness"), ("metallic", "Metallic")]
GRAYSCALE_MAPS = ("Roughness", "Metallic")

# Neutral engine textures used as M_Hunk defaults, so a character missing a map never inherits another's.
NEUTRAL_TEXTURES = {
    "BaseColor": "/Engine/EngineResources/DefaultTexture",
    "Normal": "/Engine/EngineMaterials/FlatNormal",
}
# Used when a character has no roughness map (M_Hunk blends to RoughnessConstant).
FALLBACK_ROUGHNESS = 0.6


class ImportError_(Exception):
    """A setup problem the user can fix; reported as one clear error instead of a traceback."""


def build_master_material(grayscale_defaults):
    """
    Texture parameter defaults must match their sampler type. Colour and normal use neutral engine textures;
    the grayscale samplers need a grayscale texture, so they borrow an imported one. That borrowed default is
    never visible: an instance missing that map turns it off (RoughnessMapWeight / MetallicScale = 0).
    """
    defaults = {name: unreal.load_asset(path) for name, path in NEUTRAL_TEXTURES.items()}
    defaults.update(grayscale_defaults)
    path = f"{MAT_DIR}/M_Hunk"
    mat = EAL.load_asset(path) if EAL.does_asset_exist(path) else None
    if mat:
        # delete_all_material_expressions can leave orphaned nodes behind, and a leftover parameter node
        # with the same name silently wins. Delete one by one and start over if anything survives.
        for e in MEL.get_material_expressions(mat):
            MEL.delete_material_expression(mat, e)
        if MEL.get_material_expressions(mat):
            EAL.delete_asset(path)
            mat = None
    if not mat:
        mat = ASSETS.create_asset("M_Hunk", MAT_DIR, unreal.Material, unreal.MaterialFactoryNew())
    mat.set_editor_property("used_with_skeletal_mesh", True)

    def tex_param(name, sampler, x, y):
        e = MEL.create_material_expression(mat, unreal.MaterialExpressionTextureSampleParameter2D, x, y)
        e.set_editor_property("parameter_name", name)
        e.set_editor_property("texture", defaults[name])
        e.set_editor_property("sampler_type", sampler)
        return e

    def scalar(name, default, x, y):
        e = MEL.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, x, y)
        e.set_editor_property("parameter_name", name)
        e.set_editor_property("default_value", default)
        return e

    def mul(x, y):
        return MEL.create_material_expression(mat, unreal.MaterialExpressionMultiply, x, y)

    base = tex_param("BaseColor", unreal.MaterialSamplerType.SAMPLERTYPE_COLOR, -700, -200)
    normal = tex_param("Normal", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL, -700, 50)
    rough = tex_param("Roughness", unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_GRAYSCALE, -700, 300)
    metal = tex_param("Metallic", unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_GRAYSCALE, -700, 550)
    rough_scale = scalar("RoughnessScale", 1.0, -450, 380)
    metal_scale = scalar("MetallicScale", 1.0, -450, 630)

    rough_mul = mul(-250, 320)
    MEL.connect_material_expressions(rough, "R", rough_mul, "A")
    MEL.connect_material_expressions(rough_scale, "", rough_mul, "B")
    # Roughness = lerp(RoughnessConstant, map * RoughnessScale, RoughnessMapWeight).
    rough_const = scalar("RoughnessConstant", FALLBACK_ROUGHNESS, -450, 200)
    rough_weight = scalar("RoughnessMapWeight", 1.0, -450, 460)
    rough_out = MEL.create_material_expression(mat, unreal.MaterialExpressionLinearInterpolate, -100, 300)
    MEL.connect_material_expressions(rough_const, "", rough_out, "A")
    MEL.connect_material_expressions(rough_mul, "", rough_out, "B")
    MEL.connect_material_expressions(rough_weight, "", rough_out, "Alpha")
    metal_mul = mul(-250, 570)
    MEL.connect_material_expressions(metal, "R", metal_mul, "A")
    MEL.connect_material_expressions(metal_scale, "", metal_mul, "B")

    # Gentle rim light in the base colour so the hunks pop against the dim house (matches M_FlatColor).
    fres = MEL.create_material_expression(mat, unreal.MaterialExpressionFresnel, -700, 800)
    fres.set_editor_property("exponent", 3.0)
    fres.set_editor_property("base_reflect_fraction", 0.0)
    rim = mul(-450, 800)
    MEL.connect_material_expressions(fres, "", rim, "A")
    MEL.connect_material_expressions(base, "RGB", rim, "B")
    rim_amt = scalar("Rim", 0.2, -450, 950)
    rim_scaled = mul(-250, 850)
    MEL.connect_material_expressions(rim, "", rim_scaled, "A")
    MEL.connect_material_expressions(rim_amt, "", rim_scaled, "B")

    MEL.connect_material_property(base, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)
    MEL.connect_material_property(normal, "RGB", unreal.MaterialProperty.MP_NORMAL)
    MEL.connect_material_property(rough_out, "", unreal.MaterialProperty.MP_ROUGHNESS)
    MEL.connect_material_property(metal_mul, "", unreal.MaterialProperty.MP_METALLIC)
    MEL.connect_material_property(rim_scaled, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    MEL.layout_material_expressions(mat)
    MEL.recompile_material(mat)
    EAL.save_loaded_asset(mat)
    unreal.log(f"[FixHim] built {mat.get_path_name()}")
    return mat


def import_textures(fbm_dir, dest, folder):
    textures = {}
    for path in sorted(glob.glob(os.path.join(fbm_dir, "*"))):
        lower = os.path.basename(path).lower()
        map_name = next((m for key, m in TEXTURE_MAPS if key in lower), None)
        if not map_name or map_name in textures:
            continue
        name = f"T_{folder}_{map_name}"
        t = unreal.AssetImportTask()
        t.set_editor_property("filename", path)
        t.set_editor_property("destination_path", dest)
        t.set_editor_property("destination_name", name)
        t.set_editor_property("replace_existing", True)
        t.set_editor_property("automated", True)
        t.set_editor_property("save", False)
        ASSETS.import_asset_tasks([t])
        tex = EAL.load_asset(f"{dest}/{name}")
        if not tex:
            unreal.log_warning(f"[FixHim] failed to import {path}")
            continue
        if map_name == "Normal":
            tex.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP)
            tex.set_editor_property("srgb", False)
        elif map_name in ("Roughness", "Metallic"):
            tex.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_GRAYSCALE)
            tex.set_editor_property("srgb", False)
        tex.set_editor_property("lod_group", unreal.TextureGroup.TEXTUREGROUP_CHARACTER)
        EAL.save_loaded_asset(tex)
        textures[map_name] = tex
    return textures


def make_material_instance(dest, folder, master, textures):
    name = f"MI_{folder}"
    path = f"{dest}/{name}"
    mi = EAL.load_asset(path) if EAL.does_asset_exist(path) else ASSETS.create_asset(
        name, dest, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    mi.set_editor_property("parent", master)
    # Start from the master's defaults every run so overrides from an earlier import can't linger.
    MEL.clear_all_material_instance_parameters(mi)
    for map_name, tex in textures.items():
        MEL.set_material_instance_texture_parameter_value(mi, map_name, tex)
    missing = [m for _, m in TEXTURE_MAPS if m not in textures]
    if "Roughness" in missing:
        MEL.set_material_instance_scalar_parameter_value(mi, "RoughnessMapWeight", 0.0)
    if "Metallic" in missing:
        MEL.set_material_instance_scalar_parameter_value(mi, "MetallicScale", 0.0)
    if missing:
        # BaseColor -> grey checker, Normal -> flat, Roughness -> constant, Metallic -> 0.
        unreal.log_warning(f"[FixHim] {folder} has no {', '.join(missing)} map; using neutral fallbacks")
    MEL.update_material_instance(mi)
    EAL.save_loaded_asset(mi)
    return mi


def import_mesh(fbx, dest, folder):
    # Start clean so the mesh always gets its own fresh skeleton (reimports can't change skeletons).
    for name in (f"SK_{folder}", f"SK_{folder}_Skeleton", f"A_{folder}_Idle", f"RTG_{folder}", f"IK_{folder}"):
        if EAL.does_asset_exist(f"{dest}/{name}"):
            EAL.delete_asset(f"{dest}/{name}")
    pipe = unreal.InterchangeGenericAssetsPipeline()
    common = pipe.get_editor_property("common_skeletal_meshes_and_animations_properties")
    common.set_editor_property("try_auto_select_skeleton", False)
    pipe.get_editor_property("common_meshes_properties").set_editor_property(
        "force_all_mesh_as_type", unreal.InterchangeForceMeshType.IFMT_SKELETAL_MESH)
    mesh_pipe = pipe.get_editor_property("mesh_pipeline")
    mesh_pipe.set_editor_property("create_physics_asset", False)
    mesh_pipe.set_editor_property("import_static_meshes", False)
    pipe.get_editor_property("animation_pipeline").set_editor_property("import_animations", False)
    # Textures + material instance are built by this script instead (Tripo exports a legacy Phong material).
    mat_pipe = pipe.get_editor_property("material_pipeline")
    mat_pipe.set_editor_property("import_materials", False)
    mat_pipe.get_editor_property("texture_pipeline").set_editor_property("import_textures", False)

    params = unreal.ImportAssetParameters()
    params.set_editor_property("is_automated", True)
    params.set_editor_property("replace_existing", True)
    params.set_editor_property("destination_name", f"SK_{folder}")
    params.set_editor_property("override_pipelines", [unreal.SoftObjectPath(pipe.get_path_name())])
    mgr = unreal.InterchangeManager.get_interchange_manager_scripted()
    mgr.import_asset(dest, unreal.InterchangeManager.create_source_data(fbx), params)

    for a in EAL.list_assets(dest, recursive=False):
        obj = EAL.load_asset(a)
        if isinstance(obj, unreal.Skeleton) and obj.get_name() != f"SK_{folder}_Skeleton":
            EAL.rename_asset(obj.get_path_name(), f"{dest}/SK_{folder}_Skeleton")
        elif isinstance(obj, unreal.SkeletalMesh) and obj.get_name() != f"SK_{folder}":
            EAL.rename_asset(obj.get_path_name(), f"{dest}/SK_{folder}")
    return EAL.load_asset(f"{dest}/SK_{folder}") if EAL.does_asset_exist(f"{dest}/SK_{folder}") else None


def make_ik_rig(dest, name, mesh):
    path = f"{dest}/{name}"
    if EAL.does_asset_exist(path):
        EAL.delete_asset(path)
    rig = ASSETS.create_asset(name, dest, unreal.IKRigDefinition, unreal.IKRigDefinitionFactory())
    ctrl = unreal.IKRigController.get_controller(rig)
    ctrl.set_skeletal_mesh(mesh)
    # Recognises the UE5 mannequin bone naming and builds the standard retarget chains.
    ctrl.apply_auto_generated_retarget_definition()
    EAL.save_loaded_asset(rig)
    return rig


def retarget_idle(dest, folder, mesh, source_rig):
    target_rig = make_ik_rig(dest, f"IK_{folder}", mesh)
    rtg = ASSETS.create_asset(f"RTG_{folder}", dest, unreal.IKRetargeter, unreal.IKRetargetFactory())
    ctrl = unreal.IKRetargeterController.get_controller(rtg)
    ctrl.set_ik_rig(unreal.RetargetSourceOrTarget.SOURCE, source_rig)
    ctrl.set_ik_rig(unreal.RetargetSourceOrTarget.TARGET, target_rig)
    ctrl.add_default_ops()
    ctrl.assign_ik_rig_to_all_ops(unreal.RetargetSourceOrTarget.SOURCE, source_rig)
    ctrl.assign_ik_rig_to_all_ops(unreal.RetargetSourceOrTarget.TARGET, target_rig)
    ctrl.auto_map_chains(unreal.AutoMapChainType.EXACT, True)
    # Match the target's rest pose to the mannequin's so A-pose differences don't leak into the animation.
    ctrl.auto_align_all_bones(unreal.RetargetSourceOrTarget.TARGET)
    EAL.save_loaded_asset(rtg)

    inputs = unreal.IKRetargetBatchOperationInputs()
    inputs.set_editor_property("assets_to_retarget", [EAL.find_asset_data(a) for a in RETARGET_ANIMS])
    inputs.set_editor_property("source_mesh", unreal.load_asset(MANNY_MESH))
    inputs.set_editor_property("target_mesh", mesh)
    inputs.set_editor_property("ik_retarget_asset", rtg)
    inputs.set_editor_property("include_referenced_assets", False)
    inputs.set_editor_property("overwrite_existing_files", True)
    inputs.set_editor_property("prefix", f"{folder}_")
    inputs.set_editor_property("use_source_path", False)
    inputs.set_editor_property("target_path", dest)
    results = unreal.IKRetargetBatchOperation.run_batch_retarget(inputs)
    # Setting up the IK rig / retarget touches the skeleton (preview mesh etc.); keep it saved.
    EAL.save_asset(f"{dest}/SK_{folder}_Skeleton", only_if_is_dirty=True)
    for data in results:
        obj = data.get_asset()
        if isinstance(obj, unreal.AnimSequence):
            new_name = "A_" + obj.get_name().replace("MM_", "")  # A_<Folder>_Idle
            EAL.rename_asset(obj.get_path_name(), f"{dest}/{new_name}")
            EAL.save_asset(f"{dest}/{new_name}", only_if_is_dirty=False)
            unreal.log(f"[FixHim] retargeted {dest}/{new_name}")
        else:
            unreal.log_warning(f"[FixHim] retarget also produced {obj.get_path_name()}")


def find_sources(src_name, folder):
    """(prepared mesh FBX, Tripo texture folder) or None."""
    fbx = os.path.join(MESH_DIR, folder + ".fbx")
    tripo = glob.glob(os.path.join(SRC_DIR, src_name, "*", "*.fbx"))
    if not os.path.exists(fbx) or not tripo:
        unreal.log_warning(f"[FixHim] missing {fbx} or Tripo export for {src_name}; run Tools/Art/prepare_characters.py")
        return None
    return fbx, os.path.splitext(tripo[0])[0] + ".fbm"


def import_character(fbx, folder, master, textures, source_rig):
    dest = f"{CHAR_DIR}/{folder}"
    mi = make_material_instance(dest, folder, master, textures)
    mesh = import_mesh(fbx, dest, folder)
    if not mesh:
        unreal.log_error(f"[FixHim] mesh import failed for {fbx}")
        return
    # Iterating a struct array yields copies; write each modified element back by index.
    mats = mesh.get_editor_property("materials")
    for i in range(len(mats)):
        m = mats[i]
        m.set_editor_property("material_interface", mi)
        mats[i] = m
    mesh.modify()
    mesh.set_editor_property("materials", mats)
    EAL.save_loaded_asset(mesh, only_if_is_dirty=False)
    unreal.log(f"[FixHim] imported {mesh.get_path_name()} bounds={mesh.get_bounds().box_extent}")
    retarget_idle(dest, folder, mesh, source_rig)


def main():
    try:
        run()
    except ImportError_ as e:
        unreal.log_error(f"[FixHim] import_characters: {e}")


def run():
    assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(), 'Stop PIE before importing characters'
    # Keep the selected comparison look when reimporting character assets.
    selected_style = "matte"
    existing = EAL.load_asset(f"{CHAR_DIR}/PinkTile/MI_PinkTile")
    if existing:
        parent_name = existing.get_base_material().get_name()
        selected_style = {"M_Hunk": "original", "M_Hunk_Illustrated": "illustrated",
                          "M_Hunk_Cel": "cel"}.get(parent_name, "matte")
    EAL.make_directory(CHAR_DIR)
    imported = []
    for src_name, folder in CHARACTERS.items():
        sources = find_sources(src_name, folder)
        if sources:
            fbx, fbm = sources
            EAL.make_directory(f"{CHAR_DIR}/{folder}")
            textures = import_textures(fbm, f"{CHAR_DIR}/{folder}", folder)
            imported.append((fbx, folder, textures))
    if not imported:
        raise ImportError_(
            f"no prepared character FBXs in {MESH_DIR}. Run the Blender step first: "
            "/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup --python Tools/Art/prepare_characters.py")
    grayscale_defaults = {}
    for name in GRAYSCALE_MAPS:
        tex = next((t[name] for _, _, t in imported if name in t), None)
        if not tex:
            raise ImportError_(f"no character has a {name} map, so M_Hunk can't be built (check the .fbm folders)")
        grayscale_defaults[name] = tex
    master = build_master_material(grayscale_defaults)
    source_rig = make_ik_rig(CHAR_DIR, "IK_Manny", unreal.load_asset(MANNY_MESH))
    for fbx, folder, textures in imported:
        import_character(fbx, folder, master, textures, source_rig)
    editor_dir = os.path.dirname(os.path.abspath(__file__))
    runpy.run_path(os.path.join(editor_dir, "add_hunk_dissolve.py"))
    runpy.run_path(os.path.join(editor_dir, "style_characters.py"),
                   init_globals={"STYLE": selected_style})
    unreal.log("[FixHim] import_characters done")


main()
