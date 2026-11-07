"""
Creates / refreshes the procedural assets the game code expects (see Config/DefaultGame.ini):

  /Game/ICanFixHim/Materials/M_FlatColor     lit, BaseColor / Emissive / Roughness params
  /Game/ICanFixHim/Materials/M_Translucent   unlit translucent, BaseColor / Opacity params
  /Game/ICanFixHim/Materials/M_Sparkle       unlit additive twinkle sprite, Color param
  /Game/ICanFixHim/Materials/M_UI_Portrait   UI material for scene-capture portraits
  /Game/ICanFixHim/UI/T_Pointer, T_Heart     imported from SourceArt/Generated (Tools/Art/*.svg)

Run inside the editor (Python console, MCP, or -ExecutePythonScript). Idempotent.
"""
import os
import unreal

MEL = unreal.MaterialEditingLibrary
ASSETS = unreal.AssetToolsHelpers.get_asset_tools()
EAL = unreal.EditorAssetLibrary
MAT_DIR = "/Game/ICanFixHim/Materials"
UI_DIR = "/Game/ICanFixHim/UI"
PROJECT_DIR = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())


def fresh_material(name):
    path = f"{MAT_DIR}/{name}"
    if EAL.does_asset_exist(path):
        mat = EAL.load_asset(path)
        MEL.delete_all_material_expressions(mat)
        return mat
    return ASSETS.create_asset(name, MAT_DIR, unreal.Material, unreal.MaterialFactoryNew())


def expr(mat, cls, x, y, **props):
    e = MEL.create_material_expression(mat, cls, x, y)
    for k, v in props.items():
        e.set_editor_property(k, v)
    return e


def vec_param(mat, name, default, x, y):
    return expr(mat, unreal.MaterialExpressionVectorParameter, x, y,
                parameter_name=name, default_value=unreal.LinearColor(*default))


def scalar_param(mat, name, default, x, y):
    return expr(mat, unreal.MaterialExpressionScalarParameter, x, y, parameter_name=name, default_value=default)


def finish(mat):
    MEL.layout_material_expressions(mat)
    MEL.recompile_material(mat)
    EAL.save_loaded_asset(mat)
    unreal.log(f"[FixHim] built {mat.get_path_name()}")


def build_flat():
    mat = fresh_material("M_FlatColor")
    mat.set_editor_property("used_with_skeletal_mesh", True)
    mat.set_editor_property("used_with_static_lighting", True)
    base = vec_param(mat, "BaseColor", (0.8, 0.8, 0.8, 1), -600, -100)
    emis = vec_param(mat, "Emissive", (0, 0, 0, 1), -600, 100)
    rough = scalar_param(mat, "Roughness", 0.6, -600, 300)

    # Soft stylized rim light: a whisper of the base colour on grazing angles.
    fres = expr(mat, unreal.MaterialExpressionFresnel, -600, 450, exponent=3.0, base_reflect_fraction=0.0)
    rim = expr(mat, unreal.MaterialExpressionMultiply, -350, 400)
    MEL.connect_material_expressions(fres, "", rim, "A")
    MEL.connect_material_expressions(base, "RGB", rim, "B")
    rim_scale = expr(mat, unreal.MaterialExpressionMultiply, -200, 400, const_b=0.25)
    MEL.connect_material_expressions(rim, "", rim_scale, "A")
    add = expr(mat, unreal.MaterialExpressionAdd, -100, 150)
    MEL.connect_material_expressions(emis, "RGB", add, "A")
    MEL.connect_material_expressions(rim_scale, "", add, "B")

    MEL.connect_material_property(base, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)
    MEL.connect_material_property(add, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    MEL.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
    finish(mat)


CHARACTER_HLSL = """
// Paint a stylized outfit onto the mannequin by reference-pose position (mesh space: Z up, +Y forward).
float3 c = Shirt;
if (Pos.z < Waist) c = Pants;
if (Pos.z < ShoeZ) c = Shoes;
if (Pos.z > Neck || abs(Pos.x) > HandX) c = Skin;
if (Pattern > 0.5 && all(c == Shirt))
{
    float a = step(0.5, frac(Pos.x * 0.09));
    float b = step(0.5, frac(Pos.z * 0.09));
    c *= 0.72 + 0.28 * abs(a - b);
}
return c;
"""


def build_character():
    mat = fresh_material("M_Character")
    mat.set_editor_property("used_with_skeletal_mesh", True)
    pos = expr(mat, unreal.MaterialExpressionPreSkinnedPosition, -900, 0)
    params = [
        ("Skin", (0.80, 0.58, 0.47, 1)), ("Shirt", (0.2, 0.35, 0.6, 1)),
        ("Pants", (0.15, 0.18, 0.28, 1)), ("Shoes", (0.12, 0.09, 0.07, 1)),
    ]
    scalars = [("Waist", 97.0), ("Neck", 151.0), ("ShoeZ", 9.0), ("HandX", 41.0), ("Pattern", 0.0)]
    custom = expr(mat, unreal.MaterialExpressionCustom, -400, 0, code=CHARACTER_HLSL,
                  output_type=unreal.CustomMaterialOutputType.CMOT_FLOAT3, description="Outfit")
    inputs = []
    for n in ["Pos"] + [p[0] for p in params] + [s[0] for s in scalars]:
        ci = unreal.CustomInput()
        ci.set_editor_property("input_name", n)
        inputs.append(ci)
    custom.set_editor_property("inputs", inputs)
    # PreSkinnedPosition only exists in the vertex shader; interpolate it to the pixel shader.
    interp = expr(mat, unreal.MaterialExpressionVertexInterpolator, -650, 0)
    MEL.connect_material_expressions(pos, "", interp, "")
    MEL.connect_material_expressions(interp, "", custom, "Pos")
    y = 100
    for name, default in params:
        v = vec_param(mat, name, default, -800, y)
        MEL.connect_material_expressions(v, "RGB", custom, name)
        y += 120
    for name, default in scalars:
        sp = scalar_param(mat, name, default, -800, y)
        MEL.connect_material_expressions(sp, "", custom, name)
        y += 80
    rough = scalar_param(mat, "Roughness", 0.6, -400, 400)
    emis = vec_param(mat, "Emissive", (0, 0, 0, 1), -400, 500)
    MEL.connect_material_property(custom, "", unreal.MaterialProperty.MP_BASE_COLOR)
    MEL.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
    MEL.connect_material_property(emis, "RGB", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    finish(mat)


def build_translucent():
    mat = fresh_material("M_Translucent")
    mat.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
    mat.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
    mat.set_editor_property("two_sided", True)
    base = vec_param(mat, "BaseColor", (0.4, 0.7, 1.0, 1), -500, 0)
    opacity = scalar_param(mat, "Opacity", 0.5, -500, 200)
    MEL.connect_material_property(base, "RGB", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    MEL.connect_material_property(opacity, "", unreal.MaterialProperty.MP_OPACITY)
    finish(mat)


SPARKLE_HLSL = """
float2 p = UV - 0.5;
float d = length(p);
float core = saturate(1.0 - d * 5.0);
core = core * core * core;
float rx = saturate(1.0 - abs(p.x) * 22.0) * saturate(1.0 - abs(p.y) * 2.1);
float ry = saturate(1.0 - abs(p.y) * 22.0) * saturate(1.0 - abs(p.x) * 2.1);
float seed = frac(dot(Pos, float3(0.0123, 0.0171, 0.0137)));
float tw = saturate(0.35 + 0.65 * sin(Time * 2.7 + seed * 6.2831));
return (core * 1.4 + (rx + ry) * 0.9) * tw;
"""


def build_sparkle():
    mat = fresh_material("M_Sparkle")
    mat.set_editor_property("blend_mode", unreal.BlendMode.BLEND_ADDITIVE)
    mat.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
    mat.set_editor_property("two_sided", True)
    uv = expr(mat, unreal.MaterialExpressionTextureCoordinate, -700, 0)
    time = expr(mat, unreal.MaterialExpressionTime, -700, 150)
    pos = expr(mat, unreal.MaterialExpressionObjectPositionWS, -700, 300)
    custom = expr(mat, unreal.MaterialExpressionCustom, -400, 100,
                  code=SPARKLE_HLSL, output_type=unreal.CustomMaterialOutputType.CMOT_FLOAT1, description="Sparkle")
    inputs = []
    for n in ("UV", "Time", "Pos"):
        ci = unreal.CustomInput()
        ci.set_editor_property("input_name", n)
        inputs.append(ci)
    custom.set_editor_property("inputs", inputs)
    MEL.connect_material_expressions(uv, "", custom, "UV")
    MEL.connect_material_expressions(time, "", custom, "Time")
    MEL.connect_material_expressions(pos, "", custom, "Pos")
    color = vec_param(mat, "Color", (1.0, 0.8, 0.95, 1), -400, 350)
    intensity = scalar_param(mat, "Intensity", 7.0, -400, 500)
    m1 = expr(mat, unreal.MaterialExpressionMultiply, -150, 200)
    MEL.connect_material_expressions(custom, "", m1, "A")
    MEL.connect_material_expressions(color, "RGB", m1, "B")
    m2 = expr(mat, unreal.MaterialExpressionMultiply, 0, 250)
    MEL.connect_material_expressions(m1, "", m2, "A")
    MEL.connect_material_expressions(intensity, "", m2, "B")
    MEL.connect_material_property(m2, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    finish(mat)


def build_portrait():
    mat = fresh_material("M_UI_Portrait")
    mat.set_editor_property("material_domain", unreal.MaterialDomain.MD_UI)
    mat.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
    # Default must be a linear (HDR) texture to match the scene-capture render targets.
    rt_path = f"{UI_DIR}/RT_PortraitDefault"
    if EAL.does_asset_exist(rt_path):
        default_tex = EAL.load_asset(rt_path)
    else:
        default_tex = ASSETS.create_asset("RT_PortraitDefault", UI_DIR, unreal.TextureRenderTarget2D, unreal.TextureRenderTargetFactoryNew())
        default_tex.set_editor_property("render_target_format", unreal.TextureRenderTargetFormat.RTF_RGBA16F)
        default_tex.set_editor_property("size_x", 64)
        default_tex.set_editor_property("size_y", 64)
        EAL.save_loaded_asset(default_tex)
    tex = expr(mat, unreal.MaterialExpressionTextureSampleParameter2D, -900, 0,
               parameter_name="Portrait", texture=default_tex,
               sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR)
    # SceneColorHDR capture stores *inverse* opacity in alpha.
    alpha = expr(mat, unreal.MaterialExpressionOneMinus, -650, 150)
    MEL.connect_material_expressions(tex, "A", alpha, "")
    # The capture is raw scene radiance (no eye adaptation): expose, then a gentle Reinhard-ish curve.
    exposure = scalar_param(mat, "Exposure", 0.08, -900, -250)
    exposed = expr(mat, unreal.MaterialExpressionMultiply, -700, -150)
    MEL.connect_material_expressions(tex, "RGB", exposed, "A")
    MEL.connect_material_expressions(exposure, "", exposed, "B")
    plus = expr(mat, unreal.MaterialExpressionAdd, -650, -100, const_b=0.6)
    MEL.connect_material_expressions(exposed, "", plus, "A")
    div = expr(mat, unreal.MaterialExpressionDivide, -500, -50)
    MEL.connect_material_expressions(exposed, "", div, "A")
    MEL.connect_material_expressions(plus, "", div, "B")
    toned = expr(mat, unreal.MaterialExpressionMultiply, -380, -50, const_b=1.5)
    MEL.connect_material_expressions(div, "", toned, "A")

    sil_amt = scalar_param(mat, "Silhouette", 0.0, -650, 300)
    sil_col = vec_param(mat, "SilhouetteColor", (0.06, 0.01, 0.05, 1), -650, 420)
    sil = expr(mat, unreal.MaterialExpressionLinearInterpolate, -250, 0)
    MEL.connect_material_expressions(toned, "", sil, "A")
    MEL.connect_material_expressions(sil_col, "RGB", sil, "B")
    MEL.connect_material_expressions(sil_amt, "", sil, "Alpha")

    bg = vec_param(mat, "Background", (0.32, 0.09, 0.27, 1), -650, 560)
    over_bg = expr(mat, unreal.MaterialExpressionLinearInterpolate, -60, 50)
    MEL.connect_material_expressions(bg, "RGB", over_bg, "A")
    MEL.connect_material_expressions(sil, "", over_bg, "B")
    MEL.connect_material_expressions(alpha, "", over_bg, "Alpha")

    transparent = scalar_param(mat, "Transparent", 0.0, -650, 700)
    opacity = expr(mat, unreal.MaterialExpressionLinearInterpolate, -60, 300, const_a=1.0)
    MEL.connect_material_expressions(alpha, "", opacity, "B")
    MEL.connect_material_expressions(transparent, "", opacity, "Alpha")

    MEL.connect_material_property(over_bg, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    MEL.connect_material_property(opacity, "", unreal.MaterialProperty.MP_OPACITY)
    finish(mat)


def import_textures():
    src_dir = os.path.join(PROJECT_DIR, "SourceArt", "Generated")
    tasks = []
    for name in ("T_Pointer", "T_Heart"):
        src = os.path.join(src_dir, name + ".png")
        if not os.path.exists(src):
            unreal.log_warning(f"[FixHim] missing {src}; run Tools/render_icons.sh")
            continue
        t = unreal.AssetImportTask()
        t.set_editor_property("filename", src)
        t.set_editor_property("destination_path", UI_DIR)
        t.set_editor_property("destination_name", name)
        t.set_editor_property("replace_existing", True)
        t.set_editor_property("automated", True)
        t.set_editor_property("save", False)
        tasks.append(t)
    ASSETS.import_asset_tasks(tasks)
    for name in ("T_Pointer", "T_Heart"):
        tex = EAL.load_asset(f"{UI_DIR}/{name}")
        if tex:
            tex.set_editor_property("lod_group", unreal.TextureGroup.TEXTUREGROUP_UI)
            tex.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_EDITOR_ICON)
            tex.set_editor_property("mip_gen_settings", unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS)
            EAL.save_loaded_asset(tex)


def main():
    for d in (MAT_DIR, UI_DIR, "/Game/ICanFixHim/Maps"):
        EAL.make_directory(d)
    build_flat()
    build_character()
    build_translucent()
    build_sparkle()
    build_portrait()
    import_textures()
    unreal.log("[FixHim] create_assets done")


main()
