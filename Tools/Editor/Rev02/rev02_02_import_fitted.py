"""Rev02 step 2: import the fitted revision-02 art kits (Art Source, read-only) into /Game/.../Environment/Rev02/.

Each kit's FBXs carry authored UCX_ collision hulls, so automatic collision generation is off and the UCX hulls
are imported as simple collision. UE 5.8's Interchange FBX path drops UCX hulls (verified: 0 convex elements), so
this script imports through the legacy FBX importer (Interchange.FeatureFlags.Import.FBX off for the duration). Materials and textures come from the FBX; rev02_03 reassigns the approved,
already-tuned Unreal materials where a kit reuses an existing finish. Logs every mesh's bounds and simple-collision
count so axis conversion and pivots can be checked against each kit's assembly.json/manifest.json. Re-runnable.
"""
import os, unreal
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
SRC = os.path.join(ROOT, 'Art Source/Apartment Redesign/Assets')
DST = '/Game/ICanFixHim/Environment/Rev02/'
EAL = unreal.EditorAssetLibrary
SM = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
tools = unreal.AssetToolsHelpers.get_asset_tools()

KITS = {
    'KI_Cabinet02': ('KI-CABINET-02/model', ['KI_CAB_0425_body', 'KI_CAB_0425_door', 'KI_CAB_0425_drawer',
                                             'KI_CAB_0775_body', 'KI_CAB_0775_door_L', 'KI_CAB_0775_door_R',
                                             'KI_CAB_0775_drawer_L', 'KI_CAB_0775_drawer_R',
                                             'KI_CAB_0450_body', 'KI_CAB_0450_door', 'KI_CAB_0450_drawer']),
    'KI_SinkNarrow': ('KI-SINK-NARROW-01/models', ['KI_SINK_NARROW_body', 'KI_SINK_NARROW_L_tap', 'KI_SINK_NARROW_R_tap',
                                                   'KI_SINK_NARROW_damage']),
    'ARC_WindowKitchen02': ('ARC-WINDOW-KITCHEN-02/model', ['ARC_Window_Kitchen_frame', 'ARC_Window_Kitchen_lower_sash',
                                                            'ARC_Window_Kitchen_upper_sash', 'ARC_Window_Kitchen_lower_glass',
                                                            'ARC_Window_Kitchen_upper_glass']),
    'BR_Closet02': ('BR-CLOSET-02/model', ['BR_Closet02_Trim', 'BR_Closet02_Door_L', 'BR_Closet02_Door_R', 'BR_Closet02_Shelf',
                                           'BR_Closet02_Bulb', 'BR_Closet02_Mold']),
    'KI_Fridge02': ('KI-FRIDGE-02/models', ['KI_FRIDGE_02_BODY', 'KI_FRIDGE_02_DOOR']),
    'ARC_Sliding02': ('ARC-SLIDING-CLOSET-02/model', ['ARC_Sliding02_Frame', 'ARC_Sliding02_LeftPanel', 'ARC_Sliding02_RightPanel']),
    'ARC_Door02': ('ARC-DOOR-02/model', ['ARC_Door02_Frame', 'ARC_Door02_Leaf']),
    'ARC_EntryDoor02': ('ARC-ENTRY-DOOR-02/model', ['ARC_Entry_Door02_Frame', 'ARC_Entry_Door02_Leaf']),
    'KI_WallTable02': ('KI-WALL-TABLE-02/model', ['KI_WALL_TABLE_02']),
    'KI_Stool02': ('KI-STOOL-02/model', ['KI_STOOL_02']),
    'ARC_ClosetStorage02': ('ARC-CLOSET-STORAGE-02/model', ['ARC_ClosetStorage02']),
}
# Sources exported without UCX hulls. The legacy importer still gives these one generated box, which would seal
# the basin and block clicks on Lukey's leak, so their simple collision is replaced by complex-as-simple. The
# closet bulb and mold also have no UCX; their placed actors use NoCollision.
NO_UCX = {'KI_SINK_NARROW_body', 'KI_SINK_NARROW_L_tap', 'KI_SINK_NARROW_R_tap', 'KI_SINK_NARROW_damage',
          'BR_Closet02_Bulb', 'BR_Closet02_Mold'}
ONLY = globals().get('ONLY')            # optional subset of kit names, e.g. --set "ONLY=['KI_Fridge02']"

def collision_elems(m):
    ag = m.get_editor_property('body_setup').get_editor_property('agg_geom')
    return sum(len(ag.get_editor_property(k)) for k in ('convex_elems', 'box_elems', 'sphere_elems', 'sphyl_elems'))

CVAR = 'Interchange.FeatureFlags.Import.FBX'
was_interchange = unreal.SystemLibrary.get_console_variable_bool_value(CVAR)
unreal.SystemLibrary.execute_console_command(None, CVAR + ' false')
try:
  for kit, (sub, parts) in KITS.items():
      if ONLY and kit not in ONLY: continue
      folder = DST + kit
      for part in parts:
          src = os.path.join(SRC, sub, part + '.fbx')
          assert os.path.isfile(src), src
          t = unreal.AssetImportTask(); t.filename = src; t.destination_path = folder; t.destination_name = part
          t.automated = True; t.replace_existing = True; t.save = True
          o = unreal.FbxImportUI(); o.import_mesh = True; o.import_as_skeletal = False
          o.import_materials = True; o.import_textures = True
          o.static_mesh_import_data.combine_meshes = True
          o.static_mesh_import_data.auto_generate_collision = False     # use the authored UCX hulls
          o.static_mesh_import_data.one_convex_hull_per_ucx = True
          t.options = o
          tools.import_asset_tasks([t])
          m = EAL.load_asset(folder + '/' + part)
          assert isinstance(m, unreal.StaticMesh), 'import failed: ' + src
          # the import result must be this source file (never a stale asset of the same name)
          ad = m.get_editor_property('asset_import_data')
          assert ad and os.path.normpath(ad.get_first_filename()) == os.path.normpath(src), (part, ad.get_first_filename() if ad else None)
          if part in NO_UCX:
              SM.remove_collisions(m)
              bs = m.get_editor_property('body_setup'); bs.modify()
              bs.set_editor_property('collision_trace_flag', unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
              assert EAL.save_loaded_asset(m, False), part
          b = m.get_bounding_box()
          unreal.log('[Rev02 import] %s/%s min=(%.1f,%.1f,%.1f) max=(%.1f,%.1f,%.1f) collision=%d%s mats=%s' % (
              kit, part, b.min.x, b.min.y, b.min.z, b.max.x, b.max.y, b.max.z, collision_elems(m), ' (complex)' if part in NO_UCX else '',
              [str(s.material_slot_name) for s in m.static_materials]))
  # LV-BOOK-01's shelf books are many separate objects (README: "intentionally detachable"). Imported uncombined,
  # each book is its own mesh in the bookcase's model space, so rev02_04b can lay out new runs on other shelves.
  if not ONLY or 'LV_BookParts' in ONLY:
      t = unreal.AssetImportTask(); t.filename = os.path.join(SRC, 'LV-BOOK-01/model/LV_BOOK_BOOKS.fbx')
      t.destination_path = DST + 'LV_BookParts'; t.automated = True; t.replace_existing = True; t.save = True
      o = unreal.FbxImportUI(); o.import_mesh = True; o.import_as_skeletal = False; o.import_materials = False; o.import_textures = False
      o.static_mesh_import_data.combine_meshes = False; o.static_mesh_import_data.auto_generate_collision = False
      t.options = o
      tools.import_asset_tasks([t])
      books = [p for p in EAL.list_assets(DST + 'LV_BookParts', False, False) if isinstance(EAL.load_asset(p), unreal.StaticMesh)]
      unreal.log('[Rev02 import] LV_BookParts: %d book meshes' % len(books))
finally:
    unreal.SystemLibrary.execute_console_command(None, CVAR + (' true' if was_interchange else ' false'))
