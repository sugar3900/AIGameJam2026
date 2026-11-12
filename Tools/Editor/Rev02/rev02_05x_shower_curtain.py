"""Rev02 step 5x (user feedback: shower curtain): the moving shower curtain draws closed across the tub instead of a
rigid 52 cm panel sliding 110 cm. Needs AFixHimMorphInteractable (C++). Run after rev02_05b / 05m / 05w. Re-runnable.

- Source: BA-TUB-01/model/BA_Curtain_Animated.fbx (see that folder's README): Curtain_panel_sliding on a one-bone rig
  with shape keys Closed, 0 = gathered at the east end by the rod's bend and the fixed return, 1 = drawn west to world
  x 490 (covers the tub x 496.5-663.5), and Closed_Mid, a halfway corrective driven at 4a(1-a). The cloth keeps 210 cm
  of width in every pose; the open bunch's deep folds tilt ~2 deg toward the room and hang straight below a knee at
  z ~65 so they clear the tub rim (>= ~2 cm through the draw). Imported as a skeletal mesh with its Closed morph target (no physics asset),
  slots Floral_cotton -> MI_Rev02_CurtainFloral (M_Rev02_TexPBR_UV + floral-albedo, source UVs; the imported
  Floral_cotton is Interchange plugin content without skeletal/morph usage) and Aged_chrome -> M_Rev02_AgedChrome
  (as the rod). Both masters gain the skeletal-mesh and morph-target usage flags.
  The asset's bounds are extended over the closed shape so the drawn curtain is not culled by its open bounds.
- Shower_Curtain becomes a FixHimMorphInteractable on the shared tub assembly transform (580, 907, 0) yaw 180 (the
  source mesh is authored in assembly space; the old +125 cm parking offset and 110 cm slide are gone). Off = open,
  on = drawn closed over ~0.9 s ("Close curtain" / "Open curtain", cloth rustle). Its hidden click proxy blends from
  the open bunch to the drawn curtain, so a drawn curtain also stops clicks reaching the taps behind it.
"""
import os, unreal
EAL = unreal.EditorAssetLibrary
A = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
tools = unreal.AssetToolsHelpers.get_asset_tools()
assert not L.is_in_play_in_editor(), 'Stop PIE first'
assert hasattr(unreal, 'FixHimMorphInteractable'), 'build the C++ module with AFixHimMorphInteractable first'
R2 = '/Game/ICanFixHim/Environment/Rev02/'; MATS = R2 + 'Materials/'; DEST = R2 + 'BA_CurtainAnimated'
SRC = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()),
                   'Art Source/Apartment Redesign/Assets/BA-TUB-01/model/BA_Curtain_Animated.fbx')
assert os.path.isfile(SRC), ('missing source: %s. Slim worktrees leave out Art Source/Apartment Redesign; run '
                             '`git sparse-checkout disable` (see AGENTS.md), then `git lfs pull`.' % SRC)
acts = {a.get_actor_label(): a for a in A.get_all_level_actors()}
assert 'Shower_Curtain' in acts and 'Art_BA_Tub_BA_Tub' in acts, 'wrong map loaded?'
log = []

# Assembly transform shared by every BA-TUB part; actor space x = 580 - world x, y = 907 - world y.
ORIGIN, YAW = unreal.Vector(580, 907, 0), 180.0
def local_box(wx0, wx1, wy0, wy1, z0, z1):
    return unreal.Box(unreal.Vector(580 - wx1, 907 - wy1, z0), unreal.Vector(580 - wx0, 907 - wy0, z1))
# Cloth bounds from the source README / curtain-validation.json (world cm), 1 cm margin.
# Open: the bunch tilts toward the room (y 856.2) to clear the tub rim; closed hangs near the rod (y 864.7).
PROXY_OPEN = local_box(621, 677.5, 855.2, 887.2, 21, 221)
PROXY_CLOSED = local_box(489, 677.5, 863.7, 887.2, 21, 221)

# ---------------- import ----------------
t = unreal.AssetImportTask(); t.filename = SRC; t.destination_path = DEST; t.destination_name = 'BA_Curtain_Animated'
t.automated = True; t.replace_existing = True; t.save = True
o = unreal.FbxImportUI(); o.import_mesh = True; o.import_as_skeletal = True; o.import_materials = False; o.import_textures = False
o.import_animations = False; o.create_physics_asset = False; o.mesh_type_to_import = unreal.FBXImportType.FBXIT_SKELETAL_MESH
o.skeletal_mesh_import_data.set_editor_property('import_morph_targets', True); t.options = o
tools.import_asset_tasks([t])
mesh = EAL.load_asset(DEST + '/BA_Curtain_Animated')
assert isinstance(mesh, unreal.SkeletalMesh), 'not skeletal: %s' % mesh
morphs = [m.get_name() for m in mesh.morph_targets]
assert {'Closed', 'Closed_Mid'} <= set(morphs), 'expected Closed + Closed_Mid morphs: %s' % morphs
# The imported Floral_cotton is an instance of the Interchange plugin's legacy Phong material, which is not flagged for
# skeletal meshes / morph targets (renders as the default checker in game) and is plugin content we do not modify.
# The cloth uses the project's textured master instead (same floral texture, source UVs as authored), and the
# project masters get the two usage flags.
MEL = unreal.MaterialEditingLibrary
for master in (MATS + 'M_Rev02_TexPBR_UV', MATS + 'M_Rev02_AgedChrome'):
    mm_ = EAL.load_asset(master)
    for usage in (unreal.MaterialUsage.MATUSAGE_SKELETAL_MESH, unreal.MaterialUsage.MATUSAGE_MORPH_TARGETS):
        MEL.set_material_usage(mm_, usage)
    assert EAL.save_loaded_asset(mm_, False)
floral = EAL.load_asset(MATS + 'MI_Rev02_CurtainFloral') or tools.create_asset(
    'MI_Rev02_CurtainFloral', MATS[:-1], unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
MEL.set_material_instance_parent(floral, EAL.load_asset(MATS + 'M_Rev02_TexPBR_UV'))
MEL.set_material_instance_texture_parameter_value(floral, 'BaseColorMap', EAL.load_asset('/Game/ICanFixHim/Environment/Redesign/BA_Tub/floral-albedo'))
for k, v in (('Swap', 0.0), ('SU', 1.0), ('SV', 1.0), ('Roughness', 0.85), ('Metallic', 0.0)):
    MEL.set_material_instance_scalar_parameter_value(floral, k, v)
assert EAL.save_loaded_asset(floral, False)
mats = {'floral_cotton': floral, 'aged_chrome': EAL.load_asset(MATS + 'M_Rev02_AgedChrome')}
# Editing the SkeletalMaterial structs in place does not persist; build fresh entries per slot.
slots = []
for s in mesh.get_editor_property('materials'):
    name = s.get_editor_property('material_slot_name'); key = str(name).lower()
    assert key in mats and mats[key], 'unexpected slot ' + key
    n = s.copy()                      # keeps the (unexposed) imported slot name and UV channel data
    n.set_editor_property('material_interface', mats[key])
    slots.append(n)
mesh.set_editor_property('materials', slots)
got = [m.get_editor_property('material_interface') for m in mesh.get_editor_property('materials')]
assert got == [mats[str(s.get_editor_property('material_slot_name')).lower()] for s in slots], 'materials not applied: %s' % got
# Imported bounds are the open (Basis) pose; grow them over the drawn curtain (+X in mesh space).
b = mesh.get_bounds(); hi = b.origin.x + b.box_extent.x - mesh.get_editor_property('positive_bounds_extension').x   # re-runs keep the old extension
mesh.set_editor_property('positive_bounds_extension', unreal.Vector(max(0.0, PROXY_CLOSED.max.x + 3 - hi), 0, 0))
assert EAL.save_loaded_asset(mesh, False)
log.append('imported %s morphs %s, open bounds x %.1f..%.1f (+%.1f to cover closed)' % (mesh.get_path_name(), morphs, b.origin.x - b.box_extent.x, hi,
           mesh.get_editor_property('positive_bounds_extension').x))

# ---------------- actor ----------------
old = acts.pop('Shower_Curtain')
lvl = old.get_outer().get_outer().get_name(); folder = str(old.get_folder_path()); room = old.get_editor_property('room_id')
A.destroy_actor(old)
assert L.set_current_level_by_name(lvl)
sc = A.spawn_actor_from_class(unreal.FixHimMorphInteractable, ORIGIN, unreal.Rotator(0, 0, YAW))
sc.set_actor_label('Shower_Curtain'); sc.set_folder_path(folder); acts['Shower_Curtain'] = sc
sc.set_editor_property('room_id', room)
sc.set_editor_property('prompt_off', 'Close curtain'); sc.set_editor_property('prompt_on', 'Open curtain')
sc.set_editor_property('interact_sfx', 'BedRustle'); sc.set_editor_property('interact_sfx_off', 'BedRustle')
sc.set_editor_property('morph_target', 'Closed')
sc.set_editor_property('proxy_off', PROXY_OPEN); sc.set_editor_property('proxy_on', PROXY_CLOSED)
mm = sc.get_editor_property('morph_mesh'); mm.set_skeletal_mesh_asset(mesh)
sc.rerun_construction_scripts() if hasattr(sc, 'rerun_construction_scripts') else None
log.append('Shower_Curtain -> FixHimMorphInteractable in %s at %s yaw %.0f; proxy open %s closed %s' % (lvl, ORIGIN, YAW, PROXY_OPEN, PROXY_CLOSED))

assert L.set_current_level_by_name('L_Apartment_Rev02')
assert L.save_all_dirty_levels()
unreal.log('[Rev02 shower curtain]\n' + '\n'.join(log))
