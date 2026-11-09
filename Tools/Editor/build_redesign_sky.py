"""ENV-SKY-01: painted equirectangular sky on a large unlit sphere around the redesign apartment.

README: top = zenith, horizon at v=0.5, painted sun at u=0.5014 / 37.85 deg elevation. The scene sun
(build_redesign_lighting.py: yaw 108, pitch -38) sits at azimuth -72 deg / 38 deg elevation, so the
material rotates longitude by SunYawDeg=-72 to line the painted sun up with the light. The sphere does
not cast shadows, collide or feed Lumen/indirect lighting, so the tuned interior lighting is unchanged.
Re-runnable."""
import os, unreal
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
F = '/Game/ICanFixHim/Environment/Redesign/Finishes'
EAL, MEL = unreal.EditorAssetLibrary, unreal.MaterialEditingLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
A = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
SUN_YAW = globals().get('SUN_YAW', -72.0)

src = os.path.join(ROOT, 'Art Source/Apartment Redesign/Assets/ENV-SKY-01/textures/ENV-SKY-01_painterly_2k.png')
if not os.path.isfile(src): raise RuntimeError('missing ' + src)
t = unreal.AssetImportTask(); t.filename = src; t.destination_path = F + '/Textures'; t.destination_name = 'T_Env_Sky'
t.automated = True; t.replace_existing = True; t.save = True; tools.import_asset_tasks([t])
tex = EAL.load_asset(F + '/Textures/T_Env_Sky')
tex.set_editor_property('mip_gen_settings', unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS)  # no seam at the longitude wrap
EAL.save_asset(F + '/Textures/T_Env_Sky')

path = F + '/M_Redesign_Sky'
if EAL.does_asset_exist(path):
    m = EAL.load_asset(path); MEL.delete_all_material_expressions(m)
else:
    m = tools.create_asset('M_Redesign_Sky', F, unreal.Material, unreal.MaterialFactoryNew())
m.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_UNLIT)
m.set_editor_property('two_sided', True)
wp = MEL.create_material_expression(m, unreal.MaterialExpressionWorldPosition, -900, 0)
op = MEL.create_material_expression(m, unreal.MaterialExpressionObjectPositionWS, -900, 150)
yaw = MEL.create_material_expression(m, unreal.MaterialExpressionScalarParameter, -900, 300)
yaw.set_editor_property('parameter_name', 'SunYawDeg'); yaw.set_editor_property('default_value', SUN_YAW)
cu = MEL.create_material_expression(m, unreal.MaterialExpressionCustom, -600, 100)
cu.set_editor_property('output_type', unreal.CustomMaterialOutputType.CMOT_FLOAT2)
cu.set_editor_property('code', 'float3 d = normalize(P - C);\nfloat u = atan2(d.y, d.x) / 6.2831853 + 0.5 - Yaw / 360.0;\nfloat v = acos(clamp(d.z, -1.0, 1.0)) / 3.14159265;\nreturn float2(frac(u), v);')
def _ci(n):
    c = unreal.CustomInput(); c.set_editor_property('input_name', n); return c
cu.set_editor_property('inputs', [_ci('P'), _ci('C'), _ci('Yaw')])
MEL.connect_material_expressions(wp, '', cu, 'P'); MEL.connect_material_expressions(op, '', cu, 'C'); MEL.connect_material_expressions(yaw, '', cu, 'Yaw')
smp = MEL.create_material_expression(m, unreal.MaterialExpressionTextureSampleParameter2D, -300, 0)
smp.set_editor_property('parameter_name', 'SkyTexture'); smp.set_editor_property('texture', tex)
MEL.connect_material_expressions(cu, '', smp, 'UVs')
br = MEL.create_material_expression(m, unreal.MaterialExpressionScalarParameter, -300, 250)
br.set_editor_property('parameter_name', 'Brightness'); br.set_editor_property('default_value', 1.0)
mul = MEL.create_material_expression(m, unreal.MaterialExpressionMultiply, -80, 50)
MEL.connect_material_expressions(smp, 'RGB', mul, 'A'); MEL.connect_material_expressions(br, '', mul, 'B')
MEL.connect_material_property(mul, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
MEL.recompile_material(m); EAL.save_asset(path)

assert L.load_level('/Game/ICanFixHim/Maps/L_Apartment_Redesign_Blockout')
for a in A.get_all_level_actors():
    if a.get_actor_label() == 'SkySphere_ENV_SKY_01': A.destroy_actor(a)
s = A.spawn_actor_from_object(unreal.load_asset('/Engine/BasicShapes/Sphere'), unreal.Vector(600, 477.5, 0))
s.set_actor_label('SkySphere_ENV_SKY_01'); s.set_folder_path('Redesign/Lighting/Sky')
s.set_actor_scale3d(unreal.Vector(800, 800, 800))   # 400 m radius
c = s.static_mesh_component
c.set_material(0, m); c.set_collision_profile_name('NoCollision'); c.set_cast_shadow(False)
for prop, val in (('affect_distance_field_lighting', False), ('affect_dynamic_indirect_lighting', False), ('visible_in_ray_tracing', False)):
    try: c.set_editor_property(prop, val)
    except Exception as e: unreal.log_warning('sky: %s not set (%s)' % (prop, e))
assert L.save_current_level()
unreal.log('[Sky] ENV-SKY-01 placed, SunYawDeg=%.1f' % SUN_YAW)
