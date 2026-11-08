"""Masked decal material for alpha overlays (BR-CLOSET-01 mold, BR-WAINSCOT-01 lead paint).

Mirrors BR-CLOSET-01 build_closet.py: opacity = ramp(alpha, 0.08..0.60); colour = texture
tinted dark olive. Also restores the bedroom-facing closet shell faces (they sit 6 cm proud of
the closet body exterior and carry the sage finish/wainscot); only interior faces stay hidden.
"""
import os, unreal
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC = os.path.join(ROOT, 'Art Source/Apartment Redesign/Assets')
F = '/Game/ICanFixHim/Environment/Redesign/Finishes/'
EAL, MEL = unreal.EditorAssetLibrary, unreal.MaterialEditingLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
def imp(path, name):
    t = unreal.AssetImportTask(); t.filename = path; t.destination_path = F + 'Textures'; t.destination_name = name
    t.automated = True; t.replace_existing = True; t.save = True; tools.import_asset_tasks([t]); return EAL.load_asset(F + 'Textures/' + name)
mold_t = imp(os.path.join(SRC, 'BR-CLOSET-01/textures/mold-mask.png'), 'T_Mold_Mask')
lead_t = EAL.load_asset(F + 'Textures/T_Wainscot_Damage')

MP = F + 'M_Redesign_MaskedDecal'
if not EAL.does_asset_exist(MP):
    m = tools.create_asset('M_Redesign_MaskedDecal', F[:-1], unreal.Material, unreal.MaterialFactoryNew())
    m.set_editor_property('blend_mode', unreal.BlendMode.BLEND_MASKED)
    m.set_editor_property('opacity_mask_clip_value', 0.35)
    m.set_editor_property('two_sided', True)
    def sp(name, v, x, y):
        e = MEL.create_material_expression(m, unreal.MaterialExpressionScalarParameter, x, y)
        e.set_editor_property('parameter_name', name); e.set_editor_property('default_value', v); return e
    s = MEL.create_material_expression(m, unreal.MaterialExpressionTextureSampleParameter2D, -800, 0)
    s.set_editor_property('parameter_name', 'BaseTexture'); s.set_editor_property('texture', mold_t)
    tint = MEL.create_material_expression(m, unreal.MaterialExpressionVectorParameter, -800, 250)
    tint.set_editor_property('parameter_name', 'Tint'); tint.set_editor_property('default_value', unreal.LinearColor(1, 1, 1, 1))
    mul = MEL.create_material_expression(m, unreal.MaterialExpressionMultiply, -500, 0)
    MEL.connect_material_expressions(s, 'RGB', mul, 'A'); MEL.connect_material_expressions(tint, '', mul, 'B')
    MEL.connect_material_property(mul, '', unreal.MaterialProperty.MP_BASE_COLOR)
    lo, hi = sp('MaskLow', 0.08, -800, 400), sp('MaskHigh', 0.60, -800, 500)
    sub = MEL.create_material_expression(m, unreal.MaterialExpressionSubtract, -500, 350)
    MEL.connect_material_expressions(s, 'A', sub, 'A'); MEL.connect_material_expressions(lo, '', sub, 'B')
    rng = MEL.create_material_expression(m, unreal.MaterialExpressionSubtract, -500, 500)
    MEL.connect_material_expressions(hi, '', rng, 'A'); MEL.connect_material_expressions(lo, '', rng, 'B')
    div = MEL.create_material_expression(m, unreal.MaterialExpressionDivide, -300, 400)
    MEL.connect_material_expressions(sub, '', div, 'A'); MEL.connect_material_expressions(rng, '', div, 'B')
    sat = MEL.create_material_expression(m, unreal.MaterialExpressionSaturate, -150, 400)
    MEL.connect_material_expressions(div, '', sat, '')
    MEL.connect_material_property(sat, '', unreal.MaterialProperty.MP_OPACITY_MASK)
    MEL.connect_material_property(sp('Roughness', 1.0, -150, 250), '', unreal.MaterialProperty.MP_ROUGHNESS)
    MEL.recompile_material(m); EAL.save_asset(MP)
m = EAL.load_asset(MP)
def mi(name, tex, tint, lo=0.08, hi=0.60):
    path = F + name
    inst = EAL.load_asset(path) if EAL.does_asset_exist(path) else tools.create_asset(name, F[:-1], unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    MEL.set_material_instance_parent(inst, m)
    MEL.set_material_instance_texture_parameter_value(inst, 'BaseTexture', tex)
    MEL.set_material_instance_vector_parameter_value(inst, 'Tint', unreal.LinearColor(*tint, 1))
    MEL.set_material_instance_scalar_parameter_value(inst, 'MaskLow', lo); MEL.set_material_instance_scalar_parameter_value(inst, 'MaskHigh', hi)
    EAL.save_asset(path); return inst
mold_mi = mi('MI_Decal_Mold', mold_t, (0.16, 0.20, 0.09))
lead_mi = mi('MI_Decal_LeadPaint', lead_t, (1, 1, 1), 0.05, 0.5)

L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); A = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert L.load_level('/Game/ICanFixHim/Maps/L_Apartment_Redesign_Blockout')
shown = 0
for a in A.get_all_level_actors():
    lab = a.get_actor_label()
    if lab == 'Art_BR_Closet_Mold': a.static_mesh_component.set_material(0, mold_mi)
    elif lab == 'Damage_BR_LeadPaint': a.static_mesh_component.set_material(0, lead_mi)
    elif str(a.get_folder_path()).startswith('Redesign/Shell') and not a.static_mesh_component.is_visible() and not lab.endswith('_CollisionOnly'):
        o, e = a.get_actor_bounds(False)
        if o.x + e.x > 181.5 or o.y + e.y > 706.5:   # bedroom-facing closet halves
            a.static_mesh_component.set_visibility(True); shown += 1
assert L.save_current_level()
unreal.log('[Decal] done; re-shown closet exterior faces=%d' % shown)
