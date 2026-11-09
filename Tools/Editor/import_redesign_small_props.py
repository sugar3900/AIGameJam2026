"""Import the small dressing props (re-runnable: existing assets are kept) and log their bounds."""
import os, unreal
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC = os.path.join(ROOT, 'Art Source/Apartment Redesign/Assets')
R = '/Game/ICanFixHim/Environment/Redesign/'
EAL = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
PROPS = {
    'HA-VASE-02': ['HA_VASE_02'], 'BR-PERFUME-01': ['BR_Perfume_Body', 'BR_Perfume_Stopper'],
    'BR-CLOSET-BOX-01': ['BR_BOX_BODY', 'BR_BOX_LID'], 'BA-BOTTLE-01': ['BA_Bottle_Body', 'BA_Bottle_Stopper'],
    'BA-CUP-01': ['BA_Cup', 'BA_Brush_Sage', 'BA_Brush_Ivory'], 'BA-FOLDED-TOWEL-01': ['BA_Folded_Towel'],
    'BA-HAND-TOWEL-01': ['BA_Hand_Towel'], 'BA-HOOK-01': ['BA_Hook_01'], 'BA-JAR-01': ['BA_Jar_Body', 'BA_Jar_Lid'],
    'BA-ROLL-01': ['BA_Roll_Holder', 'BA_Roll_Paper'], 'BA-SOAP-01': ['BA_SoapDish', 'BA_SoapBar'],
    'BA-SWITCH-01': ['BA_Switch_Plate', 'BA_Switch_Toggle'], 'BA-TIN-01': ['BA_Tin_Body', 'BA_Tin_Lid'],
    'KI-PAN-01': ['KI_Pan_Body', 'KI_Pan_Handle'], 'KI-BOWL-01': ['KI_Bowl', 'Apple_A', 'Apple_B', 'Lemon_A', 'Lemon_B', 'Pear'],
    'KI-JAR-01': ['KI_Jar_Body', 'KI_Jar_Lid'], 'KI-MUG-01': ['KI_Mug_01'], 'KI-PLANT-01': ['KI_Geranium'],
    'KI-POTTERY-01': ['KI_Pottery_01'], 'OF-PAPERS-01': ['OF_PAPERS_01'],
    'HA-SHOES-01': ['HA_ShoeTray', 'HA_Oxford_1', 'HA_Oxford_2', 'HA_SlipOn_1', 'HA_SlipOn_2'],
    'ARC-WALL-SHELF-01': ['ARC_WALL_SHELF_01'],
}
def folder(d): return R + d.replace('-01', '').replace('-02', '_02').replace('-', '_')
def find_fbx(d, part):
    for root, _, files in os.walk(os.path.join(SRC, d)):
        if part + '.fbx' in files: return os.path.join(root, part + '.fbx')
    raise RuntimeError('missing source %s/%s' % (d, part))
def mesh(d, part):
    name = part
    if EAL.does_asset_exist(folder(d) + '/' + part) and not isinstance(EAL.load_asset(folder(d) + '/' + part), unreal.StaticMesh):
        name = 'SM_' + part   # e.g. KI-BOWL-01's 'Pear' mesh collides with its own 'Pear' material
    path = folder(d) + '/' + name
    if not EAL.does_asset_exist(path):
        t = unreal.AssetImportTask(); t.filename = find_fbx(d, part); t.destination_path = folder(d); t.destination_name = name
        t.automated = True; t.replace_existing = True; t.save = True
        o = unreal.FbxImportUI(); o.import_mesh = True; o.import_as_skeletal = False; o.import_materials = True; o.import_textures = True
        o.static_mesh_import_data.combine_meshes = True; o.static_mesh_import_data.auto_generate_collision = False; t.options = o
        tools.import_asset_tasks([t])
        if not t.get_editor_property('imported_object_paths'): raise RuntimeError('import produced nothing: ' + part)
    m = EAL.load_asset(path)
    if not isinstance(m, unreal.StaticMesh): raise RuntimeError('not a static mesh: ' + path)
    return m
if __name__ == '__main__':
    for d, parts in PROPS.items():
        for p in parts:
            b = mesh(d, p).get_bounding_box()
            unreal.log('[Props] %-18s min=(%.1f,%.1f,%.1f) max=(%.1f,%.1f,%.1f)' % (p, b.min.x, b.min.y, b.min.z, b.max.x, b.max.y, b.max.z))
