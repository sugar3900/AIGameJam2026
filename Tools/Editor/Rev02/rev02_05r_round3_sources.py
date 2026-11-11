"""Rev02 step 5r (user feedback round 3): install the round-3 source releases on their existing placements. Re-runnable;
run after rev02_02 imports Pantry03 / Tub03 / Window03 / Plant04 (rev02_02b need not be re-run: this step builds its own
round-3 materials).

ROUND3-TUB-01: BA_Tub03_Body on Art_BA_Tub_BA_Tub (580,907,0) yaw 180, scale 1 (exact original bounds). No UCX: the
  original BA_Tub collision (simple elements + trace flag) is copied; no auto-convex. Separate drain, plumbing, taps,
  water plane and both curtains are untouched. README material contract: enamel slots = lerp(enamel-albedo, enamel-brush,
  blend) x tint (exterior .60 / rough .36, interior .30 x (1.08,1.08,1.06) / .23, rim .45 x (1.05,1.04,1.01) / .26),
  cast metal aged-metal x (.38,.42,.42) metallic .68 rough .48, raised metal x (.67,.64,.56) .72/.39, overflow flat
  (.035,.027,.018) rough .5.
ROUND3-PANTRY-01: KI_Pantry03_Left/RightDoor (4 mm meeting reveal, continuous paint UVs, authored 460 mm UCX slab) swap in
  place on Pantry_Door_L/R and their hidden art copies; hinge roots, +-100 travel and the three slot bindings unchanged.
ROUND3-WINDOW-01: head-join frames on Win_BR/OF/BA/KI_frame and Kit_LV_N_Casing at their actors (paint bindings kept).
  South/LV frames keep the originals' complex-as-simple collision (no hulls generated); the kitchen keeps its 12 UCX.
ROUND3-PLANT-01: LV_Book04_Plant on both plant instances; slots map to MI_Plant03_Leaf/LeafLight/CeramicPot/PotSoil
  (Pot_Botanical dropped with the floating dots).
"""
import os, unreal
G = unreal
EAL = unreal.EditorAssetLibrary; MEL = unreal.MaterialEditingLibrary; MP = unreal.MaterialProperty
A = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
SM = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
tools = unreal.AssetToolsHelpers.get_asset_tools()
E = '/Game/ICanFixHim/Environment/'; R2 = E + 'Rev02/'; MATS = R2 + 'Materials/'
acts = {a.get_actor_label(): a for a in A.get_all_level_actors()}
assert not unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor(), 'Stop PIE first: editor-world actor queries are empty and asset saves race during PIE'
_missing = [l for l in ['Art_BA_Tub_BA_Tub', 'Pantry_Door_L', 'Pantry_Door_R', 'Art_KI_Pantry_LeftDoor', 'Art_KI_Pantry_RightDoor', 'Win_BR_frame', 'Win_OF_frame', 'Win_BA_frame', 'Win_KI_frame', 'Kit_LV_N_Casing', 'Art_LV_Book_LV_BOOK_PLANT', 'Art_LV_Book_LV_BOOK_PLANT_OFTop', 'Art_CoatCloset_Frame', 'Art_OfficeCloset_Frame', 'Door_BR_Frame'] if l not in acts]
assert not _missing, 'required actors missing (wrong map loaded?): %s' % _missing
log = []

def find(p):
    return EAL.load_asset(p) if EAL.does_asset_exist(p) else unreal.load_object(None, p + '.' + p.split('/')[-1])
def load(p):
    o = find(p); assert o, p; return o
def on_disk(obj):
    rel = obj.get_outermost().get_name()[len('/Game/'):] + '.uasset'
    return os.path.isfile(os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_content_dir()), rel))
def save(obj):
    if not EAL.save_loaded_asset(obj, False):          # assets created this session may not be registry-indexed yet
        unreal.EditorLoadingAndSavingUtils.save_packages([obj.get_outermost()], False)
    assert on_disk(obj), 'not written to disk: ' + obj.get_path_name()   # never trust an in-memory-only asset (lost on restart)

def instance(name, parent, scalars=None, vectors=None, textures=None):
    path = MATS + name
    mi = find(path) or tools.create_asset(name, MATS[:-1], unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    MEL.set_material_instance_parent(mi, parent)
    for k, v in (scalars or {}).items(): MEL.set_material_instance_scalar_parameter_value(mi, k, v)
    for k, v in (vectors or {}).items(): MEL.set_material_instance_vector_parameter_value(mi, k, unreal.LinearColor(*v))
    for k, v in (textures or {}).items(): MEL.set_material_instance_texture_parameter_value(mi, k, v)
    save(mi); return mi

def blend_material():
    """M_Rev02_TexBlendPBR: lerp(TexA, TexB, Blend) x Tint, Roughness, Metallic (UV0). Built once (kept if present)."""
    path = MATS + 'M_Rev02_TexBlendPBR'
    if find(path):
        m = load(path)
        if not on_disk(m): MEL.recompile_material(m); save(m)        # created but never written by an earlier run
        return m
    m = tools.create_asset('M_Rev02_TexBlendPBR', MATS[:-1], unreal.Material, unreal.MaterialFactoryNew())
    def tp(name, tex, x, y):
        e = MEL.create_material_expression(m, unreal.MaterialExpressionTextureSampleParameter2D, x, y)
        e.set_editor_property('parameter_name', name); e.set_editor_property('texture', tex)
        e.set_editor_property('sampler_type', unreal.MaterialSamplerType.SAMPLERTYPE_COLOR); return e
    def sp(name, v, x, y):
        e = MEL.create_material_expression(m, unreal.MaterialExpressionScalarParameter, x, y)
        e.set_editor_property('parameter_name', name); e.set_editor_property('default_value', float(v)); return e
    a = tp('TexA', load(R2 + 'Tub03/T_Tub03_EnamelAlbedo'), -900, 0); b = tp('TexB', load(R2 + 'Tub03/T_Tub03_EnamelBrush'), -900, 250)
    lp = MEL.create_material_expression(m, unreal.MaterialExpressionLinearInterpolate, -600, 100)
    assert MEL.connect_material_expressions(a, 'RGB', lp, 'A'); assert MEL.connect_material_expressions(b, 'RGB', lp, 'B')
    assert MEL.connect_material_expressions(sp('Blend', 0.6, -900, 500), '', lp, 'Alpha')
    tint = MEL.create_material_expression(m, unreal.MaterialExpressionVectorParameter, -600, 300)
    tint.set_editor_property('parameter_name', 'Tint'); tint.set_editor_property('default_value', unreal.LinearColor(1, 1, 1, 1))
    mul = MEL.create_material_expression(m, unreal.MaterialExpressionMultiply, -350, 100)
    assert MEL.connect_material_expressions(lp, '', mul, 'A'); assert MEL.connect_material_expressions(tint, '', mul, 'B')
    MEL.connect_material_property(mul, '', MP.MP_BASE_COLOR)
    MEL.connect_material_property(sp('Roughness', 0.36, -350, 300), '', MP.MP_ROUGHNESS)
    MEL.connect_material_property(sp('Metallic', 0.0, -350, 380), '', MP.MP_METALLIC)
    MEL.recompile_material(m); save(m)
    return m

def swap(owner, comp, sm, override=None, keep_old=True):
    old = {}
    if keep_old and comp.static_mesh:
        old = {str(s.material_slot_name).lower().replace(' ', '_'): comp.get_material(i) for i, s in enumerate(comp.static_mesh.static_materials)}
    owner.modify(); comp.set_static_mesh(sm)
    for i, s in enumerate(sm.static_materials):
        n = str(s.material_slot_name).lower().replace(' ', '_')
        m = (override or {}).get(n, old.get(n))
        if m is not None: comp.set_material(i, m)

def copy_collision(src, dst):
    col = G.GeometryScript_Collision.get_simple_collision_from_static_mesh(src)
    if G.GeometryScript_Collision.get_simple_collision_shape_count(col): G.GeometryScript_Collision.set_simple_collision_of_static_mesh(col, dst, G.GeometryScriptSetSimpleCollisionOptions())
    else: SM.remove_collisions(dst)
    bs = dst.get_editor_property('body_setup'); bs.modify()
    bs.set_editor_property('collision_trace_flag', src.get_editor_property('body_setup').get_editor_property('collision_trace_flag'))
    save(dst)

# ---------------- tub ----------------
texpbr = load(MATS + 'M_Rev02_TexPBR'); cpbr = load(MATS + 'M_Rev02_ConstPBR'); bm = blend_material()
TA, TB, TM = load(R2 + 'Tub03/T_Tub03_EnamelAlbedo'), load(R2 + 'Tub03/T_Tub03_EnamelBrush'), load(R2 + 'Tub03/T_Tub03_AgedMetal')
TUBM = {
 'tub03_exterior_enamel': instance('MI_Tub03_ExteriorEnamel', bm, {'Blend': 0.60, 'Roughness': 0.36, 'Metallic': 0.0}, {'Tint': (1, 1, 1, 1)}, {'TexA': TA, 'TexB': TB}),
 'tub03_interior_enamel': instance('MI_Tub03_InteriorEnamel', bm, {'Blend': 0.30, 'Roughness': 0.23, 'Metallic': 0.0}, {'Tint': (1.08, 1.08, 1.06, 1)}, {'TexA': TA, 'TexB': TB}),
 'tub03_rolled_rim': instance('MI_Tub03_RolledRim', bm, {'Blend': 0.45, 'Roughness': 0.26, 'Metallic': 0.0}, {'Tint': (1.05, 1.04, 1.01, 1)}, {'TexA': TA, 'TexB': TB}),
 'tub03_aged_castmetal': instance('MI_Tub03_AgedCastMetal', texpbr, {'Roughness': 0.48, 'Metallic': 0.68}, {'Tint': (0.38, 0.42, 0.42, 1)}, {'BaseColorMap': TM}),
 'tub03_raised_metal': instance('MI_Tub03_RaisedMetal', texpbr, {'Roughness': 0.39, 'Metallic': 0.72}, {'Tint': (0.67, 0.64, 0.56, 1)}, {'BaseColorMap': TM}),
 'tub03_overflow_dark': instance('MI_Tub03_OverflowDark', cpbr, {'Roughness': 0.50, 'Metallic': 0.0}, {'BaseColor': (0.035, 0.027, 0.018, 1)}),
}
TUB = load(R2 + 'Tub03/BA_Tub03_Body'); copy_collision(load(E + 'Redesign/BA_Tub/BA_Tub'), TUB)
tub = acts['Art_BA_Tub_BA_Tub']; swap(tub, tub.static_mesh_component, TUB, TUBM, keep_old=False)
o, e = tub.get_actor_bounds(False)
log.append('tub -> BA_Tub03_Body x%.1f-%.1f y%.1f-%.1f z%.1f-%.1f, collision from BA_Tub (%s)' % (o.x-e.x, o.x+e.x, o.y-e.y, o.y+e.y, o.z-e.z, o.z+e.z,
           TUB.get_editor_property('body_setup').get_editor_property('collision_trace_flag')))

# ---------------- pantry ----------------
for side, art in (('Left', 'Art_KI_Pantry_LeftDoor'), ('Right', 'Art_KI_Pantry_RightDoor')):
    sm = load(R2 + 'Pantry03/KI_Pantry03_%sDoor' % side); ia = acts['Pantry_Door_%s' % side[0]]
    swap(ia, ia.get_editor_property('body'), sm); swap(acts[art], acts[art].static_mesh_component, sm)
    b = unreal.SystemLibrary.get_component_bounds(ia.get_editor_property('body')); c, x = b[0], b[1]
    log.append('Pantry_Door_%s -> %s closed y%.2f-%.2f (travel %+.0f)' % (side[0], sm.get_name(), c.y - x.y, c.y + x.y, ia.get_editor_property('toggle_rotation').yaw))

# ---------------- windows ----------------
WIN = {'Win_BR_frame': ('ARC_Window_Narrow03_frame', E + 'Redesign/ARC_WindowNarrow/ARC_Window_frame'),
       'Win_OF_frame': ('ARC_Window_Office03_frame', E + 'Redesign/ARC_WindowOffice/ARC_Window_frame'),
       'Win_BA_frame': ('ARC_Window_Bath03_frame', E + 'Redesign/ARC_WindowBath/ARC_Window_frame'),
       'Win_KI_frame': ('ARC_Window_Kitchen03_frame', None),
       'Kit_LV_N_Casing': ('ARC_Window_Living03_Casing', E + 'Redesign/ARC_LivingWall/ARC_Window_Casing_Sash')}
for lab, (new, old) in WIN.items():
    sm = load(R2 + 'Window03/' + new)
    if old: copy_collision(load(old), sm)
    a = acts[lab]; swap(a, a.static_mesh_component, sm)
    log.append('%s -> %s (%s)' % (lab, new, 'collision from original' if old else 'authored UCX kept'))

# ---------------- closet frames (ROUND3-CLOSET-FRAME-01) ----------------
# Same floor origin/poses; the paint slot now carries the regular ARC-DOOR-03 name, so it takes the regular door paint
# explicitly (the installed door frames' 'Painted warm ivory' MI); the track keeps its current material. 3 UCX imported.
CF = find(R2 + 'ClosetFrame04/ARC_ClosetFrame04')
if CF:
    df = acts['Door_BR_Frame'].static_mesh_component
    door_paint = next(df.get_material(i) for i, s_ in enumerate(df.static_mesh.static_materials) if str(s_.material_slot_name).lower().replace(' ', '_') == 'painted_warm_ivory')
    for lab in ('Art_CoatCloset_Frame', 'Art_OfficeCloset_Frame'):
        a = acts[lab]; c = a.static_mesh_component
        track = next(c.get_material(i) for i, s_ in enumerate(c.static_mesh.static_materials) if 'track' in str(s_.material_slot_name).lower())
        swap(a, c, CF, {'painted_warm_ivory': door_paint, 'aged_track': track}, keep_old=False)
        log.append('%s -> ARC_ClosetFrame04 (paint %s, track %s)' % (lab, door_paint.get_name(), track.get_name()))

# ---------------- plant ----------------
PL = load(R2 + 'Plant04/LV_Book04_Plant')
PM = {'plant_leaf': load(MATS + 'MI_Plant03_Leaf'), 'plant_leaf_light': load(MATS + 'MI_Plant03_LeafLight'),
      'ceramic_pot': load(MATS + 'MI_Plant03_CeramicPot'), 'pot_soil': load(MATS + 'MI_Plant03_PotSoil')}
for lab in ('Art_LV_Book_LV_BOOK_PLANT', 'Art_LV_Book_LV_BOOK_PLANT_OFTop'):
    a = acts[lab]; swap(a, a.static_mesh_component, PL, PM, keep_old=False)
log.append('plant -> LV_Book04_Plant on both instances')

assert L.save_all_dirty_levels()
unreal.log('[Rev02 round3 sources]\n' + '\n'.join(log))
