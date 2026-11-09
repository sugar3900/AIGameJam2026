"""Import the gameplay-parity art (LV-FUSE-DAMAGE-01, KI-WALL-STAIN-01, KI-RANGE-FLAME-01,
BA-TUB-WATER-01), build the stain material per its README, and place the two damage overlays in
the environment map. build_redesign_gameplay.py then moves them into the gameplay sublevel,
attaches them to their maladies and wires the flame/water as interactable reveal parts."""
import os, unreal
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC = os.path.join(ROOT, 'Art Source/Apartment Redesign/Assets')
R = '/Game/ICanFixHim/Environment/Redesign/'
F = R + 'Finishes/'
EAL, MEL = unreal.EditorAssetLibrary, unreal.MaterialEditingLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
A = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

def imp(path, dest, name, mesh=True):
    t = unreal.AssetImportTask(); t.filename = path; t.destination_path = dest; t.destination_name = name
    t.automated = True; t.replace_existing = True; t.save = True
    if mesh:
        o = unreal.FbxImportUI(); o.import_mesh = True; o.import_as_skeletal = False; o.import_materials = True; o.import_textures = True
        o.static_mesh_import_data.combine_meshes = True; o.static_mesh_import_data.auto_generate_collision = False; t.options = o
    tools.import_asset_tasks([t]); a = EAL.load_asset(dest + '/' + name)
    if mesh:
        b = a.get_bounding_box()
        unreal.log('[Parity] %s min=(%.1f,%.1f,%.1f) max=(%.1f,%.1f,%.1f)' % (name, b.min.x, b.min.y, b.min.z, b.max.x, b.max.y, b.max.z))
    return a

fuse = imp(os.path.join(SRC, 'LV-FUSE-DAMAGE-01/model/LV_Fuse_Plaster_Damage.fbx'), R + 'LV_FUSE', 'LV_Fuse_Plaster_Damage')
stain = imp(os.path.join(SRC, 'KI-WALL-STAIN-01/model/KI_Wall_Stain.fbx'), R + 'KI_WallStain', 'KI_Wall_Stain')
imp(os.path.join(SRC, 'KI-RANGE-FLAME-01/model/KI_Range_Flame.fbx'), R + 'KI_Range', 'KI_Range_Flame')
imp(os.path.join(SRC, 'BA-TUB-WATER-01/model/BA_TUB_WATER_Surface.fbx'), R + 'BA_Tub', 'BA_TUB_WATER_Surface')
tex = imp(os.path.join(SRC, 'KI-WALL-STAIN-01/textures/stain-candidate-b.png'), F + 'Textures', 'T_Wall_Stain', mesh=False)

# README: RGB * (0.58, 0.46, 0.31); opacity = clamp((alpha - 0.008) * 1.25) -> mask ramp 0.008..0.808
path = F + 'MI_Decal_WallStain'
mi = EAL.load_asset(path) if EAL.does_asset_exist(path) else tools.create_asset('MI_Decal_WallStain', F[:-1], unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
MEL.set_material_instance_parent(mi, EAL.load_asset(F + 'M_Redesign_MaskedDecal'))
MEL.set_material_instance_texture_parameter_value(mi, 'BaseTexture', tex)
MEL.set_material_instance_vector_parameter_value(mi, 'Tint', unreal.LinearColor(0.58, 0.46, 0.31, 1))
MEL.set_material_instance_scalar_parameter_value(mi, 'MaskLow', 0.008); MEL.set_material_instance_scalar_parameter_value(mi, 'MaskHigh', 0.808)
EAL.save_asset(path)

assert L.load_level('/Game/ICanFixHim/Maps/L_Apartment_Redesign_Blockout')
acts = {a.get_actor_label(): a for a in A.get_all_level_actors()}
for lab in ('Art_LV_Fuse_Plaster_Damage', 'Art_KI_Wall_Stain'):
    if lab in acts: A.destroy_actor(acts[lab])
shell = acts['Art_LV_Fuse_Shell']   # README: same origin as LV_FUSE_01_Shell
d = A.spawn_actor_from_object(fuse, shell.get_actor_location(), shell.get_actor_rotation())
d.set_actor_label('Art_LV_Fuse_Plaster_Damage'); d.set_folder_path('Gameplay/Damage')
d.static_mesh_component.set_collision_profile_name('NoCollision'); d.tags = [unreal.Name('RepairDamage'), unreal.Name('wyatt')]
# Stain: clear plaster west of the kitchen window, under the pan rail, 2 mm proud of the north wall face (y=6).
s = A.spawn_actor_from_object(stain, unreal.Vector(745, 6.2, 150), unreal.Rotator(0, 0, 0))
s.set_actor_label('Art_KI_Wall_Stain'); s.set_folder_path('Gameplay/Damage')
c = s.static_mesh_component; c.set_collision_profile_name('NoCollision'); c.set_material(0, mi); c.set_cast_shadow(False)
s.tags = [unreal.Name('RepairDamage'), unreal.Name('lukey')]
L.save_all_dirty_levels()
unreal.log('[Parity] placed fuse damage + wall stain')
