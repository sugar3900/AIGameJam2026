"""
Creates / refreshes the procedural assets the game code expects (see Config/DefaultGame.ini):

  /Game/ICanFixHim/Materials/M_FlatColor     lit, BaseColor / Emissive / Roughness params
  /Game/ICanFixHim/Materials/M_Translucent   unlit translucent, BaseColor / Opacity params
  /Game/ICanFixHim/Materials/M_Sparkle       unlit additive twinkle sprite for the hunks' appear / pop puffs, Color param
  /Game/ICanFixHim/Materials/M_Shine         additive overlay material: a shine band that wipes across a mesh + a soft rim glow
  /Game/ICanFixHim/Materials/M_HoverOutline  post process: fixed-pixel rim around the visible pixels of the hovered
                                             interactable (custom depth + stencil, UFixHimHoverOutlineSubsystem)
  /Game/ICanFixHim/Materials/M_UI_Portrait   UI material for scene-capture portraits
  /Game/ICanFixHim/UI/T_Heart, T_PlayerSilhouette              imported from SourceArt/Generated (Tools/Art/*.svg)

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


SHINE_HLSL = """
// Overlay drawn on top of an interactable's own material (UMeshComponent::SetOverlayMaterial).
// Bounds = (centre.xyz, radius); Sweep runs 0..1 while a shine crosses the object (negative = no shine).
float3 rel = (WorldPos - Bounds.xyz) / max(Bounds.w, 1.0);
float t = dot(rel, normalize(float3(0.75, 0.55, 0.35)));
float centre = lerp(-1.5, 1.5, saturate(Sweep));
float d = (t - centre) / 0.2;
float band = exp(-d * d) * step(0.0, Sweep);
float rim = pow(1.0 - saturate(dot(normalize(Normal), normalize(CamVec))), 2.2);
return band * ShineStrength + Glow * (0.22 + rim);
"""


def build_shine():
    mat = fresh_material("M_Shine")
    mat.set_editor_property("blend_mode", unreal.BlendMode.BLEND_ADDITIVE)
    mat.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
    wpos = expr(mat, unreal.MaterialExpressionWorldPosition, -800, 0)
    normal = expr(mat, unreal.MaterialExpressionVertexNormalWS, -800, 120)
    cam = expr(mat, unreal.MaterialExpressionCameraVectorWS, -800, 240)
    bounds = vec_param(mat, "Bounds", (0, 0, 0, 100), -800, 360)
    sweep = scalar_param(mat, "Sweep", -1.0, -800, 500)
    strength = scalar_param(mat, "ShineStrength", 0.5, -800, 580)
    glow = scalar_param(mat, "Glow", 0.0, -800, 660)
    custom = expr(mat, unreal.MaterialExpressionCustom, -450, 200,
                  code=SHINE_HLSL, output_type=unreal.CustomMaterialOutputType.CMOT_FLOAT1, description="Shine")
    inputs = []
    for n in ("WorldPos", "Normal", "CamVec", "Bounds", "Sweep", "ShineStrength", "Glow"):
        ci = unreal.CustomInput()
        ci.set_editor_property("input_name", n)
        inputs.append(ci)
    custom.set_editor_property("inputs", inputs)
    MEL.connect_material_expressions(wpos, "", custom, "WorldPos")
    MEL.connect_material_expressions(normal, "", custom, "Normal")
    MEL.connect_material_expressions(cam, "", custom, "CamVec")
    MEL.connect_material_expressions(bounds, "RGBA", custom, "Bounds")
    MEL.connect_material_expressions(sweep, "", custom, "Sweep")
    MEL.connect_material_expressions(strength, "", custom, "ShineStrength")
    MEL.connect_material_expressions(glow, "", custom, "Glow")
    color = vec_param(mat, "Color", (1.0, 0.85, 0.95, 1), -450, 450)
    out = expr(mat, unreal.MaterialExpressionMultiply, -150, 300)
    MEL.connect_material_expressions(custom, "", out, "A")
    MEL.connect_material_expressions(color, "RGB", out, "B")
    MEL.connect_material_property(out, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    finish(mat)


HOVER_OUTLINE_HLSL = """
// Screen-space hover rim. Runs before TSR at render resolution, so every offset lands on a texel centre and TSR
// anti-aliases the result. A pixel is "object" when it carries the outline stencil AND the hovered object is the
// visible surface there (its custom depth matches the scene depth, i.e. nothing is in front of it).
// Outside rim: non-object pixels within WidthPx of an object pixel. Inside rim: object pixels within WidthPx of a
// non-object pixel. Returns rim coverage with a one-pixel anti-aliased falloff.
struct FHoverRim
{
    float Ref;
    float Tol;
    float IsObject(FMaterialPixelParameters Parameters, float2 Offset)
    {
        if (abs(SceneTextureFetch(PPI_CustomStencil, Offset).r - Ref) > 0.5) return 0.0;
        float Custom = SceneTextureFetch(PPI_CustomDepth, Offset).r;
        float Scene = SceneTextureFetch(PPI_SceneDepth, Offset).r;
        return Custom <= Scene + max(Tol, Scene * 0.002) ? 1.0 : 0.0;
    }
};
FHoverRim Rim;
Rim.Ref = StencilRef;
Rim.Tol = DepthTolerance;
// WidthPx is in display pixels; this pass runs at render resolution (screen percentage / TSR upscale).
float W = clamp(WidthPx * View.ResolutionFractionAndInv.x, 0.5, 8.0);
float Want = Inside > 0.5 ? 0.0 : 1.0;
if (Rim.IsObject(Parameters, float2(0, 0)) == Want) return 0.0;
int R = (int)ceil(W);
float Best2 = (W + 0.5) * (W + 0.5);
float Found = 0.0;
[loop] for (int y = -R; y <= R; ++y)
{
    [loop] for (int x = -R; x <= R; ++x)
    {
        float D2 = float(x * x + y * y);
        if (D2 == 0.0 || D2 >= Best2) continue;
        if (Rim.IsObject(Parameters, float2(x, y)) == Want) { Best2 = D2; Found = 1.0; }
    }
}
return Found * saturate(W + 0.5 - sqrt(Best2));
"""


def custom_node(mat, x, y, code, out_type, desc, names):
    node = expr(mat, unreal.MaterialExpressionCustom, x, y, code=code, output_type=out_type, description=desc)
    inputs = []
    for n in names:
        ci = unreal.CustomInput()
        ci.set_editor_property("input_name", n)
        inputs.append(ci)
    node.set_editor_property("inputs", inputs)
    return node


def build_hover_outline():
    mat = fresh_material("M_HoverOutline")
    mat.set_editor_property("material_domain", unreal.MaterialDomain.MD_POST_PROCESS)
    # Before TSR (render resolution): the stencil/depth reads are texel-exact and the rim gets temporal AA. After the
    # tonemapper the colour would be exact, but the game renders at ~50% and the rim is rebuilt from jittered
    # render-resolution buffers: 2-px stair steps and 11-16% of rim pixels flicker per frame (tested 2026-11-12).
    mat.set_editor_property("blendable_location", unreal.BlendableLocation.BL_SCENE_COLOR_AFTER_DOF)

    # SceneTexture nodes wired into unused Custom inputs make the shader bind those buffers.
    scene_tex = {}
    for i, (pin, tex_id) in enumerate((("SD", unreal.SceneTextureId.PPI_SCENE_DEPTH),
                                       ("CD", unreal.SceneTextureId.PPI_CUSTOM_DEPTH),
                                       ("CS", unreal.SceneTextureId.PPI_CUSTOM_STENCIL))):
        scene_tex[pin] = expr(mat, unreal.MaterialExpressionSceneTexture, -900, -300 + i * 120, scene_texture_id=tex_id)
    params = {
        "WidthPx": scalar_param(mat, "WidthPx", 4.0, -900, 100),
        "Inside": scalar_param(mat, "Inside", 0.0, -900, 180),
        "StencilRef": scalar_param(mat, "StencilRef", 1.0, -900, 260),
        "DepthTolerance": scalar_param(mat, "DepthTolerance", 1.0, -900, 340),
    }
    custom = custom_node(mat, -550, 0, HOVER_OUTLINE_HLSL,
                         unreal.CustomMaterialOutputType.CMOT_FLOAT1, "HoverRim", list(params) + list(scene_tex))
    for n, e in params.items():
        MEL.connect_material_expressions(e, "", custom, n)
    for n, e in scene_tex.items():
        MEL.connect_material_expressions(e, "Color", custom, n)

    # Rim colour in display terms: divide out exposure so auto-exposure never dims or blows out the outline.
    color = vec_param(mat, "Color", (1.0, 1.0, 1.0, 1), -550, 250)
    intensity = scalar_param(mat, "Intensity", 1.5, -550, 380)
    eye = expr(mat, unreal.MaterialExpressionEyeAdaptation, -550, 460)
    tinted = expr(mat, unreal.MaterialExpressionMultiply, -350, 300)
    MEL.connect_material_expressions(color, "RGB", tinted, "A")
    MEL.connect_material_expressions(intensity, "", tinted, "B")
    rim_color = expr(mat, unreal.MaterialExpressionDivide, -200, 350)
    MEL.connect_material_expressions(tinted, "", rim_color, "A")
    MEL.connect_material_expressions(eye, "", rim_color, "B")

    scene = expr(mat, unreal.MaterialExpressionSceneTexture, -550, -450,
                 scene_texture_id=unreal.SceneTextureId.PPI_POST_PROCESS_INPUT0)
    scene_rgb = expr(mat, unreal.MaterialExpressionComponentMask, -350, -450, r=True, g=True, b=True, a=False)
    MEL.connect_material_expressions(scene, "Color", scene_rgb, "")
    out = expr(mat, unreal.MaterialExpressionLinearInterpolate, -50, 0)
    MEL.connect_material_expressions(scene_rgb, "", out, "A")
    MEL.connect_material_expressions(rim_color, "", out, "B")
    MEL.connect_material_expressions(custom, "", out, "Alpha")
    MEL.connect_material_property(out, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    finish(mat)


CEL_HLSL = """
// Stylised still: tone-mapped scene colour flattened into hard light bands, with an ink outline on the silhouette
// and on strong internal creases. Returns (rgb, coverage). The capture's alpha is inverse opacity.
float2 w = float2(OutlineWidth, OutlineWidth);
float4 c0 = Texture2DSample(Tex, TexSampler, UV);
float3 hdr = c0.rgb * Exposure;
float3 col = hdr / (hdr + 0.6) * 1.5;
float L = dot(col, float3(0.299, 0.587, 0.114));
float cover = 1.0 - c0.a;

float Lq = L < 0.14 ? 0.30 : (L < 0.32 ? 0.52 : (L < 0.58 ? 0.74 : 0.96));
float3 hue = min(col / max(L, 0.05), 3.0);
float3 cel = hue * Lq;
cel = lerp(float3(Lq, Lq, Lq), cel, 1.2);

float2 offs[8] = { float2(1,0), float2(-1,0), float2(0,1), float2(0,-1), float2(0.7,0.7), float2(-0.7,0.7), float2(0.7,-0.7), float2(-0.7,-0.7) };
float silh = 0.0;
float crease = 0.0;
[unroll] for (int i = 0; i < 8; i++)
{
    float4 n = Texture2DSample(Tex, TexSampler, UV + offs[i] * w);
    float nc = 1.0 - n.a;
    silh = max(silh, saturate((cover - nc) * 4.0));
    float3 nh = n.rgb * Exposure;
    float3 ncol = nh / (nh + 0.6) * 1.5;
    float nL = dot(ncol, float3(0.299, 0.587, 0.114));
    crease = max(crease, smoothstep(0.16, 0.34, abs(nL - L)) * saturate(nc * 4.0));
}
float edge = saturate(max(silh, crease * 0.85)) * saturate(cover * 4.0);
return float4(lerp(cel, float3(0.045, 0.015, 0.06), edge), cover);
"""


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
    tex = expr(mat, unreal.MaterialExpressionTextureObjectParameter, -900, 0,
               parameter_name="Portrait", texture=default_tex,
               sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR)
    uv = expr(mat, unreal.MaterialExpressionTextureCoordinate, -900, -120)
    # The capture is raw scene radiance (no eye adaptation): expose, tone-map and cel-shade it in one pass.
    exposure = scalar_param(mat, "Exposure", 0.08, -900, -250)
    outline_w = scalar_param(mat, "OutlineWidth", 0.009, -900, -330)
    cel = expr(mat, unreal.MaterialExpressionCustom, -600, -100, code=CEL_HLSL,
               output_type=unreal.CustomMaterialOutputType.CMOT_FLOAT4, description="CelShade")
    inputs = []
    for n in ("Tex", "UV", "Exposure", "OutlineWidth"):
        ci = unreal.CustomInput()
        ci.set_editor_property("input_name", n)
        inputs.append(ci)
    cel.set_editor_property("inputs", inputs)
    MEL.connect_material_expressions(tex, "", cel, "Tex")
    MEL.connect_material_expressions(uv, "", cel, "UV")
    MEL.connect_material_expressions(exposure, "", cel, "Exposure")
    MEL.connect_material_expressions(outline_w, "", cel, "OutlineWidth")
    # rgb = cel-shaded colour, a = coverage (the SceneColorHDR capture stores *inverse* opacity in alpha).
    toned = expr(mat, unreal.MaterialExpressionComponentMask, -380, -50, r=True, g=True, b=True, a=False)
    MEL.connect_material_expressions(cel, "", toned, "")
    alpha = expr(mat, unreal.MaterialExpressionComponentMask, -380, 150, r=False, g=False, b=False, a=True)
    MEL.connect_material_expressions(cel, "", alpha, "")

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


UI_TEXTURES = ("T_Heart", "T_PlayerSilhouette")


def import_textures():
    src_dir = os.path.join(PROJECT_DIR, "SourceArt", "Generated")
    tasks = []
    for name in UI_TEXTURES:
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
    for name in UI_TEXTURES:
        tex = EAL.load_asset(f"{UI_DIR}/{name}")
        if tex:
            tex.set_editor_property("lod_group", unreal.TextureGroup.TEXTUREGROUP_UI)
            tex.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_EDITOR_ICON)
            tex.set_editor_property("mip_gen_settings", unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS)
            EAL.save_loaded_asset(tex)


STEPS = {
    "flat": lambda: build_flat(),
    "character": lambda: build_character(),
    "translucent": lambda: build_translucent(),
    "sparkle": lambda: build_sparkle(),
    "shine": lambda: build_shine(),
    "hover_outline": lambda: build_hover_outline(),
    "portrait": lambda: build_portrait(),
    "textures": lambda: import_textures(),
}


def main():
    for d in (MAT_DIR, UI_DIR, "/Game/ICanFixHim/Maps"):
        EAL.make_directory(d)
    # Rebuild a subset without re-saving the rest:
    #   python3 Tools/run_editor_script.py Tools/Editor/create_assets.py --set "ONLY=['hover_outline']"
    only = globals().get("ONLY")
    for name, step in STEPS.items():
        if not only or name in only:
            step()
    unreal.log("[FixHim] create_assets done")


main()
