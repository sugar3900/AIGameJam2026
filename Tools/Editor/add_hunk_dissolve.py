"""
Adds the materialise / dematerialise effect to the shared character master /Game/ICanFixHim/Materials/M_Hunk
(every MI_<Character> inherits it), without disturbing the PBR graph made by import_characters.py:

    UnrealEditor-Cmd ICanFixHim.uproject -ExecutePythonScript=<abs>/Tools/Editor/add_hunk_dissolve.py -unattended -nullrhi

M_Hunk becomes Masked. A pixel is drawn when it lies below a noisy, rising threshold, so Dissolve 0 -> 1 builds the
character from the feet up (and 1 -> 0 takes him apart from the head down). Defaults leave the material looking exactly
as before (Dissolve = 1 = fully formed). AFixHimHunk drives the parameters per instance:

  Dissolve    0..1   how much of him exists
  FormHeight  cm     world-space height the sweep covers (his height * scale)
  EdgeColor          colour of the front of the sweep (electric blue-white, smoky black, ...)
  EdgeGlow           emissive strength of the front (0 for smoke)
  ArcAmount          crackling electric lines just behind the front (0 for smoke)
  EdgeDark           how far the front and its trail are darkened toward black (smoke)

Idempotent: does nothing if the material already has a Dissolve parameter.
"""
import unreal

MEL = unreal.MaterialEditingLibrary
EAL = unreal.EditorAssetLibrary
PATH = "/Game/ICanFixHim/Materials/M_Hunk"

HLSL = """
// Value noise, inlined (a Custom node body cannot declare functions).
float3 p0 = WorldPos * 0.07;
float3 i0 = floor(p0);
float3 f0 = frac(p0);
f0 = f0 * f0 * (3.0 - 2.0 * f0);
float n0 = 0.0;
[unroll] for (int k = 0; k < 8; k++)
{
    float3 o = float3(k & 1, (k >> 1) & 1, (k >> 2) & 1);
    float hv = frac(sin(dot(i0 + o, float3(127.1, 311.7, 74.7))) * 43758.5453);
    float3 w = lerp(1.0 - f0, f0, o);
    n0 += hv * w.x * w.y * w.z;
}
float3 p1 = WorldPos * 0.33 + float3(0.0, 0.0, Time * 6.0);
float3 i1 = floor(p1);
float3 f1 = frac(p1);
f1 = f1 * f1 * (3.0 - 2.0 * f1);
float n1 = 0.0;
[unroll] for (int m = 0; m < 8; m++)
{
    float3 o = float3(m & 1, (m >> 1) & 1, (m >> 2) & 1);
    float hv = frac(sin(dot(i1 + o, float3(127.1, 311.7, 74.7))) * 43758.5453);
    float3 w = lerp(1.0 - f1, f1, o);
    n1 += hv * w.x * w.y * w.z;
}
float h = saturate((WorldPos.z - ObjPos.z) / max(FormHeight, 1.0));
float v = h + (n0 - 0.5) * 0.4;
float front = Dissolve * 1.5 - 0.25;
float formed = Dissolve >= 0.999 ? 1.0 : step(v, front);
float d = front - v;
float edge = Dissolve >= 0.999 ? 0.0 : saturate(1.0 - abs(d) / 0.07) * step(0.001, Dissolve);
float trail = Dissolve >= 0.999 ? 0.0 : saturate(1.0 - max(d, 0.0) / 0.3) * step(0.0, d) * step(0.001, Dissolve);
float arcs = pow(saturate(1.0 - abs(n1 - 0.5) * 9.0), 3.0) * trail;
return float4(formed, edge, trail, arcs);
"""


def inp(name):
    ci = unreal.CustomInput()
    ci.set_editor_property("input_name", name)
    return ci


def expr(mat, cls, x, y, **props):
    e = MEL.create_material_expression(mat, cls, x, y)
    for k, v in props.items():
        e.set_editor_property(k, v)
    return e


def main():
    mat = EAL.load_asset(PATH)
    if not mat:
        unreal.log_error(f"[FixHim] {PATH} not found; run Tools/Editor/import_characters.py first")
        return
    if "Dissolve" in [str(n) for n in MEL.get_scalar_parameter_names(mat)]:
        unreal.log("[FixHim] M_Hunk already has the dissolve")
        return

    base_node = MEL.get_material_property_input_node(mat, unreal.MaterialProperty.MP_BASE_COLOR)
    base_out = MEL.get_material_property_input_node_output_name(mat, unreal.MaterialProperty.MP_BASE_COLOR)
    emis_node = MEL.get_material_property_input_node(mat, unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    emis_out = MEL.get_material_property_input_node_output_name(mat, unreal.MaterialProperty.MP_EMISSIVE_COLOR)

    mat.set_editor_property("blend_mode", unreal.BlendMode.BLEND_MASKED)
    mat.set_editor_property("opacity_mask_clip_value", 0.5)

    x, y = -1500, 1200
    wpos = expr(mat, unreal.MaterialExpressionWorldPosition, x, y)
    opos = expr(mat, unreal.MaterialExpressionObjectPositionWS, x, y + 120)
    time = expr(mat, unreal.MaterialExpressionTime, x, y + 240)
    dissolve = expr(mat, unreal.MaterialExpressionScalarParameter, x, y + 360, parameter_name="Dissolve", default_value=1.0)
    height = expr(mat, unreal.MaterialExpressionScalarParameter, x, y + 440, parameter_name="FormHeight", default_value=190.0)
    custom = expr(mat, unreal.MaterialExpressionCustom, x + 400, y + 200, code=HLSL,
                  output_type=unreal.CustomMaterialOutputType.CMOT_FLOAT4, description="Materialise")
    custom.set_editor_property("inputs", [inp(n) for n in ("WorldPos", "ObjPos", "Time", "Dissolve", "FormHeight")])
    MEL.connect_material_expressions(wpos, "", custom, "WorldPos")
    MEL.connect_material_expressions(opos, "", custom, "ObjPos")
    MEL.connect_material_expressions(time, "", custom, "Time")
    MEL.connect_material_expressions(dissolve, "", custom, "Dissolve")
    MEL.connect_material_expressions(height, "", custom, "FormHeight")

    def mask(channel, ty):
        m = expr(mat, unreal.MaterialExpressionComponentMask, x + 650, ty,
                 r=channel == "r", g=channel == "g", b=channel == "b", a=channel == "a")
        MEL.connect_material_expressions(custom, "", m, "")
        return m

    formed, edge, trail, arcs = mask("r", y), mask("g", y + 100), mask("b", y + 200), mask("a", y + 300)

    edge_color = expr(mat, unreal.MaterialExpressionVectorParameter, x + 650, y + 450, parameter_name="EdgeColor",
                      default_value=unreal.LinearColor(0.45, 0.8, 1.0, 1.0))
    edge_glow = expr(mat, unreal.MaterialExpressionScalarParameter, x + 650, y + 550, parameter_name="EdgeGlow", default_value=14.0)
    arc_amount = expr(mat, unreal.MaterialExpressionScalarParameter, x + 650, y + 630, parameter_name="ArcAmount", default_value=6.0)
    edge_dark = expr(mat, unreal.MaterialExpressionScalarParameter, x + 650, y + 710, parameter_name="EdgeDark", default_value=0.0)

    # emissive += EdgeColor * (edge * EdgeGlow + trail^2 * EdgeGlow * 0.2 + arcs * ArcAmount)
    e_edge = expr(mat, unreal.MaterialExpressionMultiply, x + 900, y + 100)
    MEL.connect_material_expressions(edge, "", e_edge, "A")
    MEL.connect_material_expressions(edge_glow, "", e_edge, "B")
    trail_sq = expr(mat, unreal.MaterialExpressionMultiply, x + 900, y + 220)
    MEL.connect_material_expressions(trail, "", trail_sq, "A")
    MEL.connect_material_expressions(trail, "", trail_sq, "B")
    e_trail = expr(mat, unreal.MaterialExpressionMultiply, x + 1050, y + 220)
    MEL.connect_material_expressions(trail_sq, "", e_trail, "A")
    MEL.connect_material_expressions(edge_glow, "", e_trail, "B")
    e_trail2 = expr(mat, unreal.MaterialExpressionMultiply, x + 1200, y + 220, const_b=0.2)
    MEL.connect_material_expressions(e_trail, "", e_trail2, "A")
    e_arcs = expr(mat, unreal.MaterialExpressionMultiply, x + 900, y + 340)
    MEL.connect_material_expressions(arcs, "", e_arcs, "A")
    MEL.connect_material_expressions(arc_amount, "", e_arcs, "B")
    s1 = expr(mat, unreal.MaterialExpressionAdd, x + 1350, y + 160)
    MEL.connect_material_expressions(e_edge, "", s1, "A")
    MEL.connect_material_expressions(e_trail2, "", s1, "B")
    s2 = expr(mat, unreal.MaterialExpressionAdd, x + 1500, y + 220)
    MEL.connect_material_expressions(s1, "", s2, "A")
    MEL.connect_material_expressions(e_arcs, "", s2, "B")
    surge = expr(mat, unreal.MaterialExpressionMultiply, x + 1650, y + 300)
    MEL.connect_material_expressions(s2, "", surge, "A")
    MEL.connect_material_expressions(edge_color, "RGB", surge, "B")
    if emis_node:
        total = expr(mat, unreal.MaterialExpressionAdd, x + 1800, y + 300)
        MEL.connect_material_expressions(emis_node, emis_out, total, "A")
        MEL.connect_material_expressions(surge, "", total, "B")
        MEL.connect_material_property(total, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    else:
        MEL.connect_material_property(surge, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)

    # base colour darkened toward black across the front and its trail (smoke): lerp(base, 0, saturate(edge+trail) * EdgeDark)
    dark_amt = expr(mat, unreal.MaterialExpressionAdd, x + 900, y + 460)
    MEL.connect_material_expressions(edge, "", dark_amt, "A")
    MEL.connect_material_expressions(trail, "", dark_amt, "B")
    dark_sat = expr(mat, unreal.MaterialExpressionSaturate, x + 1050, y + 460)
    MEL.connect_material_expressions(dark_amt, "", dark_sat, "")
    dark = expr(mat, unreal.MaterialExpressionMultiply, x + 1200, y + 460)
    MEL.connect_material_expressions(dark_sat, "", dark, "A")
    MEL.connect_material_expressions(edge_dark, "", dark, "B")
    smoked = expr(mat, unreal.MaterialExpressionLinearInterpolate, x + 1350, y + 460, const_b=0.0)
    MEL.connect_material_expressions(base_node, base_out, smoked, "A")
    MEL.connect_material_expressions(dark, "", smoked, "Alpha")
    MEL.connect_material_property(smoked, "", unreal.MaterialProperty.MP_BASE_COLOR)

    MEL.connect_material_property(formed, "", unreal.MaterialProperty.MP_OPACITY_MASK)
    MEL.recompile_material(mat)
    EAL.save_loaded_asset(mat)
    unreal.log("[FixHim] added the dissolve to M_Hunk")


main()
