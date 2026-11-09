"""Import kitchen casework kits (sink, base cabinet, upper, pantry, backsplash) and log bounds."""
import os, unreal
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC = os.path.join(ROOT, 'Art Source/Apartment Redesign/Assets')
R = '/Game/ICanFixHim/Environment/Redesign/'
tools = unreal.AssetToolsHelpers.get_asset_tools()
KITS = [('KI-SINK-01/models', ['KI_SINK_body', 'KI_SINK_L_door', 'KI_SINK_R_door', 'KI_SINK_L_drawer', 'KI_SINK_R_drawer', 'KI_SINK_L_tap', 'KI_SINK_R_tap', 'KI_SINK_damage'], 'KI_Sink'),
        ('KI-CABINET-01/model', ['KI_Cabinet_body', 'KI_Cabinet_door', 'KI_Cabinet_drawer'], 'KI_Cabinet'),
        ('KI-UPPER-01/model', ['KI_Upper_Body', 'KI_Upper_LeftDoor', 'KI_Upper_RightDoor'], 'KI_Upper'),
        ('KI-PANTRY-01/model', ['KI_Pantry_Body', 'KI_Pantry_LeftDoor', 'KI_Pantry_RightDoor'], 'KI_Pantry'),
        ('KI-BACKSPLASH-01/model', ['KI_Backsplash_Module_1m', 'KI_Backsplash_End_Left', 'KI_Backsplash_End_Right'], 'KI_Backsplash')]
BODY = ('KI_SINK_body', 'KI_Cabinet_body', 'KI_Upper_Body', 'KI_Pantry_Body')
for src, parts, folder in KITS:
    for p in parts:
        t = unreal.AssetImportTask(); t.filename = os.path.join(SRC, src, p + '.fbx'); t.destination_path = R + folder
        t.destination_name = p; t.automated = True; t.replace_existing = True; t.save = True
        o = unreal.FbxImportUI(); o.import_mesh = True; o.import_as_skeletal = False; o.import_materials = True; o.import_textures = True
        o.static_mesh_import_data.combine_meshes = True; o.static_mesh_import_data.auto_generate_collision = p in BODY; t.options = o
        tools.import_asset_tasks([t]); m = unreal.EditorAssetLibrary.load_asset(R + folder + '/' + p)
        if not m: raise RuntimeError(p)
        b = m.get_bounding_box()
        unreal.log('[KC] %s min=(%.1f,%.1f,%.1f) max=(%.1f,%.1f,%.1f) nmat=%d' % (p, b.min.x, b.min.y, b.min.z, b.max.x, b.max.y, b.max.z, len(m.static_materials)))
