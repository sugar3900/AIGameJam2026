"""Rev02 step 5h: material-only feedback passes (no geometry, placement or collision changes). Re-runnable.

FIX-035  dining table (KI-TABLE-01): the sage apron/rail slot (Table_Sage_Painted) takes the top's own wood texture
         (table-wood-v2) through MI_Table_ApronWood, which swaps/rescales the apron UVs so the grain runs lengthwise
         (see rev02_02b). Top, legs, edge wear and the chairs are untouched.
FIX-037  furniture that rendered as flat FBX Phong colours gets the authored walnut finish its README names (the
         engine MI_Walnut_MutedB already used by the FIX-028 nightstands), brass/drawer-interior MIs, on every placed
         component including interactable bodies (doors, drawers): floating shelves (ARC-WALL-SHELF-01), office cabinet
         (OF-CABINET-01), hall-end cabinet (HA-CABINET-01); the hall console keeps its README walnut-b image as PBR.
         The shoe bench and plant stand stay white painted (user), now ivory paint over a faint grain with wood-tone
         rubbed edges, instead of a flat untextured white.
"""
import unreal
EAL = unreal.EditorAssetLibrary
A = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
MATS = '/Game/ICanFixHim/Environment/Rev02/Materials/'
log = []

def set_slot(mesh_path, slot, mat_path):
    """Assign mat to the named slot on every placed component (actors and interactable bodies) using mesh_path."""
    mat = EAL.load_asset(mat_path); n = 0
    for a in A.get_all_level_actors():
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            sm = c.static_mesh
            if sm is None or sm.get_path_name().split('.')[0] != mesh_path: continue
            for i, s in enumerate(sm.static_materials):
                if str(s.material_slot_name) == slot:
                    a.modify(); c.set_material(i, mat); n += 1
    log.append('%s[%s] -> %s on %d components' % (mesh_path.split('/')[-1], slot, mat_path.split('/')[-1], n))
    return n

# FIX-035: KI-TABLE-02 (apron-only UV relayout) replaces the table mesh in place; every slot keeps its material.
_t = [a for a in A.get_all_level_actors() if a.get_actor_label() == 'Art_KI_Table_12'][0]; _c = _t.static_mesh_component
_new = EAL.load_asset('/Game/ICanFixHim/Environment/Rev02/KI_Table02/KI_TABLE_02')
if _c.static_mesh != _new:
    _keep = {str(s.material_slot_name): _c.get_material(i) for i, s in enumerate(_c.static_mesh.static_materials)}
    _t.modify(); _c.set_static_mesh(_new)
    for i, s in enumerate(_new.static_materials): _c.set_material(i, _keep[str(s.material_slot_name)])
log.append('table mesh: ' + _c.static_mesh.get_name())
assert set_slot('/Game/ICanFixHim/Environment/Rev02/KI_Table02/KI_TABLE_02', 'Table_Sage_Painted', MATS + 'MI_Table_ApronWood') >= 1

# FIX-037
BRASS, INSIDE, EDGES = MATS + 'MI_Rev02_TableBrass', MATS + 'MI_Rev02_DrawerInterior', MATS + 'MI_Rev02_WoodEdges'
WAL = '/Game/ICanFixHim/Environment/Redesign/Finishes/MI_Walnut_MutedB'
R = '/Game/ICanFixHim/Environment/Redesign/'
set_slot(R + 'ARC_WALL_SHELF/ARC_WALL_SHELF_01', 'Muted_painterly_walnut', WAL)
set_slot(R + 'ARC_WALL_SHELF/ARC_WALL_SHELF_01', 'Aged_brass_screw', BRASS)
for kit, parts in (('OF_CABINET', ('OF_CABINET_BODY', 'OF_CABINET_DOOR_L', 'OF_CABINET_DOOR_R', 'OF_CABINET_DRAWER')),
                   ('HA_CABINET', ('HA_CABINET_BODY', 'HA_CABINET_DOOR_L', 'HA_CABINET_DOOR_R', 'HA_CABINET_DRAWER'))):
    for p in parts:
        set_slot(R + kit + '/' + p, 'Console_walnut_painted', WAL)
        set_slot(R + kit + '/' + p, 'Aged_brass', BRASS)
        set_slot(R + kit + '/' + p, 'Drawer_wood_inside', INSIDE)
for p in ('HA_CONSOLE_BODY', 'HA_CONSOLE_DRAWER'):
    set_slot(R + 'HA_CONSOLE/' + p, 'Console_walnut_painted', MATS + 'MI_Rev02_ConsoleWalnutB')
    set_slot(R + 'HA_CONSOLE/' + p, 'Aged_brass', BRASS)
    set_slot(R + 'HA_CONSOLE/' + p, 'Drawer_wood_inside', INSIDE)
set_slot(R + 'HA_BENCH/HA_BENCH_01', 'Muted_painterly_walnut', MATS + 'MI_Rev02_WhitePaintGrain')
set_slot(R + 'HA_BENCH/HA_BENCH_01', 'Localized_rubbed_edges', EDGES)
for p in ('LV_Plant_Stand', 'LV_Plant_Stand_Riser'):
    set_slot(R + 'LV_PLANT_STAND/' + p, 'Muted_aged_walnut', MATS + 'MI_Rev02_WhitePaintGrain')
    set_slot(R + 'LV_PLANT_STAND/' + p, 'Subtle_edge_wear', EDGES)
# FIX-038: the eight Pink_glaze slots on every fitted tile panel (Tile07_*; the old module is no longer placed).
# Grout, plum cap/bullnose and Tyler's crack (separate actor/materials) are untouched.
for a in A.get_all_level_actors():
    if not a.get_actor_label().startswith('Tile07_BA_'): continue
    c = a.static_mesh_component; sm = c.static_mesh
    for i, s_ in enumerate(sm.static_materials):
        n = str(s_.material_slot_name)
        if n.startswith('Pink_glaze_'):
            a.modify(); c.set_material(i, EAL.load_asset(MATS + 'MI_Rev02_PinkGlaze_' + n[-2:]))
log.append('FIX-038 pink glaze MIs on %d tile panels' % len([a for a in A.get_all_level_actors() if a.get_actor_label().startswith('Tile07_BA_') and 'Cap' not in a.get_actor_label() and 'Bullnose' not in a.get_actor_label()]))
# interactable bodies must keep these authored slots (not the flat-colour body MID)
for a in A.get_all_level_actors():
    if isinstance(a, unreal.FixHimInteractable):
        b = a.get_editor_property('body'); sm = b.static_mesh
        if sm and any(k in sm.get_path_name() for k in ('OF_CABINET', 'HA_CABINET', 'HA_CONSOLE')) and not a.get_editor_property('use_authored_body_materials'):
            a.modify(); a.set_editor_property('use_authored_body_materials', True); log.append('authored body on ' + a.get_actor_label())

assert L.save_all_dirty_levels()
unreal.log('[Rev02 materials]\n' + '\n'.join(log))
