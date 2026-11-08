"""Golden-hour lighting + grade for the redesign map, matching
Art Source/Environment Concepts/painterly-fixer-upper.png: warm low sun streaming through
windows, sunny painted exterior views, warm lamp pools, soft warm (never black) shadows,
low-contrast saturated colour. All tunables are in CFG; rerun to iterate.
"""
import unreal
CFG = dict(
    sun_yaw=108, sun_pitch=-38, sun_lux=230.0, sun_color=(255, 206, 150),
    sky_intensity=1.5, sky_color=(255, 246, 236),
    south_spot_lm=14000, south_color=(255, 222, 176),
    fixture_lm=260, fill_lm=120, lamp_lm=380, bulb_lm=200, lamp_color=(255, 222, 186),
    window_view_brightness=0.9,
    exposure_bias=0.3, ev_min=-1.0, ev_max=3.0,
    saturation=1.08, contrast=0.97, gain=(1.0, 1.0, 0.98), shadow_gain=(1.03, 1.0, 0.96),
    shadow_offset=(0.012, 0.009, 0.005), bloom=0.45, vignette=0.25, white_temp=6500,
    # Filmic tonemapper (UE defaults: slope .88, toe .55, shoulder .26, black clip 0, white clip .04)
    film_slope=0.86, film_toe=0.52, film_shoulder=0.28, film_black_clip=0.0, film_white_clip=0.04,
    # Per-range grading toward the reference: warm saturated sienna shadows, golden creamy highlights
    sh_sat=(1.12, 1.06, 0.96), sh_gain=(1.06, 0.99, 0.90), sh_gamma=(1.0, 1.0, 1.0),
    mid_sat=(1.08, 1.05, 1.0), mid_gamma=(1.02, 1.0, 0.98),
    hi_sat=(0.96, 0.96, 0.92), hi_gain=(1.03, 1.0, 0.93),
)
CFG.update(globals().get('OVERRIDE', {}))
A = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
EAL, MEL = unreal.EditorAssetLibrary, unreal.MaterialEditingLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
assert L.load_level('/Game/ICanFixHim/Maps/L_Apartment_Redesign_Blockout')
FOLDER = 'Redesign/Lighting'
for a in A.get_all_level_actors():
    lab = a.get_actor_label()
    if str(a.get_folder_path()).startswith(FOLDER) or lab.startswith('ReviewLight_'):
        A.destroy_actor(a)
C = lambda c: unreal.Color(r=c[0], g=c[1], b=c[2], a=255)
LC = lambda c: unreal.LinearColor(c[0], c[1], c[2], 1)

def spawn(cls, label, loc, rot=(0, 0, 0), sub=''):
    a = A.spawn_actor_from_class(cls, unreal.Vector(*loc), unreal.Rotator(roll=rot[0], pitch=rot[1], yaw=rot[2]))
    a.set_actor_label(label); a.set_folder_path(FOLDER + sub)
    lc = a.get_component_by_class(unreal.LightComponentBase) if hasattr(unreal, 'LightComponentBase') else None
    if lc: lc.set_mobility(unreal.ComponentMobility.MOVABLE)   # no baked lighting: fully dynamic + Lumen
    return a

# Sun + sky.
sun = spawn(unreal.DirectionalLight, 'Sun', (600, 470, 800), (0, CFG['sun_pitch'], CFG['sun_yaw']))
sc = sun.get_component_by_class(unreal.DirectionalLightComponent)
sc.set_editor_property('intensity', CFG['sun_lux']); sc.set_editor_property('light_color', C(CFG['sun_color']))
sc.set_editor_property('atmosphere_sun_light', True); sc.set_editor_property('light_source_angle', 0.8)
spawn(unreal.SkyAtmosphere, 'SkyAtmosphere', (600, 470, 0))
sky = spawn(unreal.SkyLight, 'SkyLight', (600, 470, 400))
slc = sky.get_component_by_class(unreal.SkyLightComponent)
slc.set_editor_property('real_time_capture', True); slc.set_editor_property('intensity', CFG['sky_intensity'])
slc.set_editor_property('light_color', C(CFG['sky_color']))

# Roof slab so the sun cannot pass the one-sided ceiling modules; ground outside.
cube = unreal.load_asset('/Engine/BasicShapes/Cube')
for label, loc, scale in [('Roof', (600, 477.5, 290), (12.6, 10.15, 0.2)), ('Ground', (600, 477.5, -40), (40, 40, 0.5))]:
    r = A.spawn_actor_from_object(cube, unreal.Vector(*loc)); r.set_actor_label(label); r.set_folder_path(FOLDER + '/Envelope')
    r.set_actor_scale3d(unreal.Vector(*scale)); r.static_mesh_component.set_collision_profile_name('NoCollision')

# Painted exterior views behind every window (non-shadow-casting, unlit).
base = EAL.load_asset('/Game/ICanFixHim/Materials/Environment/M_WindowView')
vpath = '/Game/ICanFixHim/Environment/Redesign/Finishes/MI_WindowView'
vmi = EAL.load_asset(vpath) if EAL.does_asset_exist(vpath) else tools.create_asset('MI_WindowView', '/Game/ICanFixHim/Environment/Redesign/Finishes', unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
MEL.set_material_instance_parent(vmi, base)
MEL.set_material_instance_scalar_parameter_value(vmi, 'WindowBrightness', CFG['window_view_brightness']); EAL.save_asset(vpath)
plane = unreal.load_asset('/Engine/BasicShapes/Plane')
# (label, centre x, wall y, outward sign, sill, head, width)
WINDOWS = [('LV', 215, 0, -1, 90, 230, 160), ('KI', 855, 0, -1, 90, 230, 110), ('BR', 410, 955, 1, 90, 230, 110),
           ('BA', 582.5, 955, 1, 150, 230, 115), ('OF', 1040, 955, 1, 90, 230, 140)]
for label, x, y, out, sill, head, w in WINDOWS:
    card = A.spawn_actor_from_object(plane, unreal.Vector(x, y + out * 140, (sill + head) / 2 + 20),
                                     unreal.Rotator(roll=0, pitch=-90, yaw=90 if out < 0 else -90))
    card.set_actor_scale3d(unreal.Vector(3.2, 5.6, 1)); card.set_actor_label('WindowView_' + label)
    card.set_folder_path(FOLDER + '/Window Views')
    m = card.static_mesh_component; m.set_material(0, vmi); m.set_cast_shadow(False); m.set_collision_profile_name('NoCollision')
    m.set_editor_property('affect_distance_field_lighting', False)
    if out > 0:   # south windows: warm "sun" spot from outside, through the opening onto the floor
        s = spawn(unreal.SpotLight, 'WindowSun_' + label, (x - 60, y + 260, head + 170), (0, -38, -100))
        c = s.get_component_by_class(unreal.SpotLightComponent)
        c.set_editor_property('intensity_units', unreal.LightUnits.LUMENS); c.set_editor_property('intensity', CFG['south_spot_lm'])
        c.set_editor_property('light_color', C(CFG['south_color'])); c.set_editor_property('outer_cone_angle', 30)
        c.set_editor_property('inner_cone_angle', 18); c.set_editor_property('attenuation_radius', 900); c.set_editor_property('source_radius', 2)

def point(label, loc, lm, radius=500, src=6, shadows=True):
    p = spawn(unreal.PointLight, label, loc, sub='/Lamps')
    c = p.get_component_by_class(unreal.PointLightComponent)
    c.set_editor_property('intensity_units', unreal.LightUnits.LUMENS); c.set_editor_property('intensity', lm)
    c.set_editor_property('light_color', C(CFG['lamp_color'])); c.set_editor_property('attenuation_radius', radius)
    c.set_editor_property('source_radius', src); c.set_editor_property('cast_shadows', shadows)
for n, x, y in [('Living', 275, 190), ('HallWest', 300, 470), ('HallEast', 900, 470)]:
    point('Fixture_' + n, (x, y, 225), CFG['fixture_lm'], 520, 20)
point('Lamp_OfficeFloor', (1172.7, 834, 130), CFG['lamp_lm'], 420, 4)
point('Fill_Living', (300, 230, 150), CFG['fill_lm'], 600, 40, False)
point('Fill_Hall', (600, 470, 150), CFG['fill_lm'] * 0.7, 700, 40, False)
point('Bulb_Closet', (90, 632.5, 225), CFG['bulb_lm'], 260, 2)
point('Fill_Kitchen', (875, 230, 150), CFG['fill_lm'], 650, 40, False)
point('Fill_Bath', (635, 760, 150), CFG['fill_lm'] * 0.8, 450, 40, False)
point('Fill_Bedroom', (240, 760, 150), CFG['fill_lm'] * 0.8, 500, 40, False)
point('Fill_Office', (995, 760, 150), CFG['fill_lm'] * 0.8, 500, 40, False)

# Grade.
ppv = spawn(unreal.PostProcessVolume, 'PostProcess_Golden', (600, 470, 150))
ppv.set_editor_property('unbound', True)
s = ppv.get_editor_property('settings')
def S(k, v):
    s.set_editor_property('override_' + k, True); s.set_editor_property(k, v)
S('auto_exposure_method', unreal.AutoExposureMethod.AEM_HISTOGRAM)
S('auto_exposure_min_brightness', CFG['ev_min']); S('auto_exposure_max_brightness', CFG['ev_max'])
S('auto_exposure_bias', CFG['exposure_bias'])
S('white_temp', CFG['white_temp'])
S('color_saturation', unreal.Vector4(*([CFG['saturation']] * 3), 1)); S('color_contrast', unreal.Vector4(*([CFG['contrast']] * 3), 1))
S('color_gain', unreal.Vector4(*CFG['gain'], 1))
S('color_offset_shadows', unreal.Vector4(*CFG['shadow_offset'], 0))
S('bloom_intensity', CFG['bloom']); S('vignette_intensity', CFG['vignette'])
for k in ('film_slope', 'film_toe', 'film_shoulder', 'film_black_clip', 'film_white_clip'): S(k, CFG[k])
V = lambda c: unreal.Vector4(c[0], c[1], c[2], 1)
S('color_saturation_shadows', V(CFG['sh_sat'])); S('color_gain_shadows', V(CFG['sh_gain'])); S('color_gamma_shadows', V(CFG['sh_gamma']))
S('color_saturation_midtones', V(CFG['mid_sat'])); S('color_gamma_midtones', V(CFG['mid_gamma']))
S('color_saturation_highlights', V(CFG['hi_sat'])); S('color_gain_highlights', V(CFG['hi_gain']))
ppv.set_editor_property('settings', s)
assert L.save_current_level()
unreal.log('[Light] built %s' % CFG)
