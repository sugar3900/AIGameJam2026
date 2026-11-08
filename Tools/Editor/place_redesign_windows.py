"""Import ARC-WINDOW-NARROW/BATH/OFFICE kits and seat them in the shell openings.

Kits share a floor-centred origin with the aperture centred on X; their room side
imports as +Y in Unreal (Blender -Y). North-wall windows use yaw 0, south-wall 180.
"""
import os, unreal
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC = os.path.join(ROOT, 'Art Source/Apartment Redesign/Assets')
R = '/Game/ICanFixHim/Environment/Redesign/'
F = R + 'Finishes/'
EAL, MEL = unreal.EditorAssetLibrary, unreal.MaterialEditingLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
A = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
PARTS = ['ARC_Window_frame', 'ARC_Window_upper_sash', 'ARC_Window_lower_sash', 'ARC_Window_upper_glass', 'ARC_Window_lower_glass']

# Frosted variant for the bathroom.
FP = F + 'M_Redesign_GlassFrosted'
if not EAL.does_asset_exist(FP):
    g = tools.create_asset('M_Redesign_GlassFrosted', F[:-1], unreal.Material, unreal.MaterialFactoryNew())
    g.set_editor_property('blend_mode', unreal.BlendMode.BLEND_TRANSLUCENT); g.set_editor_property('two_sided', True)
    c = MEL.create_material_expression(g, unreal.MaterialExpressionConstant3Vector, -300, 0)
    c.set_editor_property('constant', unreal.LinearColor(0.9, 0.92, 0.93, 1))
    MEL.connect_material_property(c, '', unreal.MaterialProperty.MP_BASE_COLOR)
    for prop, val, y in [(unreal.MaterialProperty.MP_OPACITY, 0.72, 120), (unreal.MaterialProperty.MP_ROUGHNESS, 0.55, 220)]:
        k = MEL.create_material_expression(g, unreal.MaterialExpressionConstant, -300, y); k.set_editor_property('r', val)
        MEL.connect_material_property(k, '', prop)
    MEL.recompile_material(g); EAL.save_asset(FP)
glass, frosted, trim = EAL.load_asset(F + 'MI_Window_Glass'), EAL.load_asset(FP), EAL.load_asset(F + 'MI_Trim_Cream')

def kit(src, folder):
    out = {}
    for p in PARTS:
        t = unreal.AssetImportTask(); t.filename = os.path.join(SRC, src, 'model', p + '.fbx')
        t.destination_path = R + folder; t.destination_name = p; t.automated = True; t.replace_existing = True; t.save = True
        o = unreal.FbxImportUI(); o.import_mesh = True; o.import_as_skeletal = False; o.import_materials = True; o.import_textures = True
        o.static_mesh_import_data.combine_meshes = True; o.static_mesh_import_data.auto_generate_collision = False; t.options = o
        tools.import_asset_tasks([t])
        m = EAL.load_asset(R + folder + '/' + p)
        if not m: raise RuntimeError(src + p)
        b = m.get_bounding_box()
        unreal.log('[Window] %s/%s min=(%.1f,%.1f,%.1f) max=(%.1f,%.1f,%.1f)' % (folder, p, b.min.x, b.min.y, b.min.z, b.max.x, b.max.y, b.max.z))
        out[p] = m
    return out

kits = {'Narrow': kit('ARC-WINDOW-NARROW-01', 'ARC_WindowNarrow'), 'Bath': kit('ARC-WINDOW-BATH-01', 'ARC_WindowBath'),
        'Office': kit('ARC-WINDOW-OFFICE-01', 'ARC_WindowOffice')}
assert L.load_level('/Game/ICanFixHim/Maps/L_Apartment_Redesign_Blockout')
for a in A.get_all_level_actors():
    if str(a.get_folder_path()).startswith('Redesign/Wall Finishes/Windows'): A.destroy_actor(a)
for room, k, x, y, yaw in [('KI', 'Narrow', 855, 0, 0), ('BR', 'Narrow', 410, 955, 180),
                           ('BA', 'Bath', 582.5, 955, 180), ('OF', 'Office', 1040, 955, 180)]:
    for p, m in kits[k].items():
        a = A.spawn_actor_from_object(m, unreal.Vector(x, y, 0), unreal.Rotator(0, 0, yaw))
        a.set_actor_label('Win_%s_%s' % (room, p.replace('ARC_Window_', ''))); a.set_folder_path('Redesign/Wall Finishes/Windows')
        c = a.static_mesh_component; c.set_collision_profile_name('NoCollision')
        if 'glass' in p:
            c.set_material(0, frosted if k == 'Bath' else glass); c.set_cast_shadow(False)
        else:
            for i in range(c.get_num_materials()): c.set_material(i, trim)
assert L.save_current_level()
