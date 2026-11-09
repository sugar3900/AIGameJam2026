"""Import closet, sliding-front, curtain (skeletal + morphs), ceiling-light and radiator kits."""
import os, unreal
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC = os.path.join(ROOT, 'Art Source/Apartment Redesign/Assets')
R = '/Game/ICanFixHim/Environment/Redesign/'
EAL = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
STATIC = [('BR-CLOSET-01/model', ['BR_Closet_Body', 'BR_Closet_Door_L', 'BR_Closet_Door_R', 'BR_Closet_Mold'], 'BR_Closet'),
          ('ARC-SLIDING-CLOSET-01/model', ['ARC_Sliding_Frame', 'ARC_Sliding_LeftPanel', 'ARC_Sliding_RightPanel'], 'ARC_SlidingCloset'),
          ('ARC-CURTAINS-01/model', ['Curtain_Rod'], 'ARC_Curtains'),
          ('ARC-CEILING-LIGHT-01/model', ['ARC_CeilingLight_Hardware', 'ARC_CeilingLight_Glass'], 'ARC_CeilingLight'),
          ('LV-RADIATOR-01/model', ['LV_Radiator'], 'LV_Radiator')]
COLLIDE = {'BR_Closet_Door_L', 'BR_Closet_Door_R', 'ARC_Sliding_LeftPanel', 'ARC_Sliding_RightPanel', 'LV_Radiator'}
def task(path, dest, name):
    t = unreal.AssetImportTask(); t.filename = path; t.destination_path = dest; t.destination_name = name
    t.automated = True; t.replace_existing = True; t.save = True; return t
for src, parts, folder in STATIC:
    for p in parts:
        if EAL.does_asset_exist(R + folder + '/' + p): continue
        t = task(os.path.join(SRC, src, p + '.fbx'), R + folder, p)
        o = unreal.FbxImportUI(); o.import_mesh = True; o.import_as_skeletal = False; o.import_materials = True; o.import_textures = True
        o.static_mesh_import_data.combine_meshes = True; o.static_mesh_import_data.auto_generate_collision = p in COLLIDE; t.options = o
        tools.import_asset_tasks([t]); m = EAL.load_asset(R + folder + '/' + p)
        b = m.get_bounding_box()
        unreal.log('[CL] %s min=(%.1f,%.1f,%.1f) max=(%.1f,%.1f,%.1f) slots=%s' % (p, b.min.x, b.min.y, b.min.z, b.max.x, b.max.y, b.max.z,
                   [str(s.material_slot_name) for s in m.static_materials]))
for p in ['Curtain_Left', 'Curtain_Right']:
    t = task(os.path.join(SRC, 'ARC-CURTAINS-01/model', p + '.fbx'), R + 'ARC_Curtains', p)
    o = unreal.FbxImportUI(); o.import_mesh = True; o.import_as_skeletal = True; o.import_materials = True; o.import_textures = True
    o.mesh_type_to_import = unreal.FBXImportType.FBXIT_SKELETAL_MESH
    o.skeletal_mesh_import_data.set_editor_property('import_morph_targets', True); o.create_physics_asset = False; t.options = o
    tools.import_asset_tasks([t]); m = EAL.load_asset(R + 'ARC_Curtains/' + p)
    if not isinstance(m, unreal.SkeletalMesh): raise RuntimeError('not skeletal: %s %s' % (p, m))
    b = m.get_bounds()
    unreal.log('[CL] %s skeletal origin=%s extent=%s morphs=%s' % (p, b.origin, b.box_extent, [mt.get_name() for mt in m.morph_targets]))
