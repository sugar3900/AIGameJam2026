"""Rev02 step 5v (user feedback round 3): ROUND3-KITCHEN-SURFACES-01 counters, backsplash and cabinet plinths. Re-runnable;
run after rev02_05l / rev02_05s.

- Carcasses KI_Cab06_0425/0775/0450_Body swap in place on Art_KI_Cab0425/0775/0450_body (same origins): the embedded
  Counter_Ivory worktops and the solid black Toe_Dark blocks are gone; an 18 mm sage-painted U plinth (front at y 74, 11 cm,
  6 cm recess) replaces each toe block. Original UCX hulls (11/14/12) imported unchanged; slots bound by name to the
  installed MI_Joinery_Sage / MI_Joinery_Interior.
- One continuous 5 cm slab per run, KI_Counter03_A/B/C at (x start, 6, 86) cm, top 91, one authored UCX each, BlockAll like
  the carcass counters were; 'Counter_Ivory' -> the kit's ivory-enamel image, roughness .48 (one world UV frame).
  All five KI_CounterFiller02_* strips are removed.
- Backsplash KI_Backsplash03_A/B/Range/C at their world origins replace the four KI_Backsplash02 bands; NoCollision.
  Tiles keep MI_Backsplash02_Ivory/_Sage/_Cap; 'Warm_cream_grout' -> opaque warm ivory (.76,.70,.59), roughness .90
  (2 mm joints recessed to y 7.6 behind tile faces at y 7.8).
"""
import unreal
EAL = unreal.EditorAssetLibrary; MEL = unreal.MaterialEditingLibrary
A = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
tools = unreal.AssetToolsHelpers.get_asset_tools()
assert not L.is_in_play_in_editor(), 'Stop PIE first: editor-world actor queries are empty and asset saves race during PIE'
R2 = '/Game/ICanFixHim/Environment/Rev02/'; MATS = R2 + 'Materials/'; KIT = R2 + 'KitchenSurf03/'
acts = {a.get_actor_label(): a for a in A.get_all_level_actors()}
_missing = [l for l in ('Art_KI_Cab0425_body', 'Art_KI_Cab0775_body', 'Art_KI_Cab0450_body') if l not in acts]
assert not _missing, 'required actors missing (wrong map loaded?): %s' % _missing
log = []

def find(p): return EAL.load_asset(p) if EAL.does_asset_exist(p) else unreal.load_object(None, p + '.' + p.split('/')[-1])
def load(p):
    o = find(p); assert o, p; return o
def save(o):
    if not EAL.save_loaded_asset(o, False): assert unreal.EditorLoadingAndSavingUtils.save_packages([o.get_outermost()], False), o.get_path_name()
def instance(name, parent, scalars=None, vectors=None, textures=None):
    mi = find(MATS + name) or tools.create_asset(name, MATS[:-1], unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    MEL.set_material_instance_parent(mi, parent)
    for k, v in (scalars or {}).items(): MEL.set_material_instance_scalar_parameter_value(mi, k, v)
    for k, v in (vectors or {}).items(): MEL.set_material_instance_vector_parameter_value(mi, k, unreal.LinearColor(*v))
    for k, v in (textures or {}).items(): MEL.set_material_instance_texture_parameter_value(mi, k, v)
    save(mi); return mi

counter_mi = instance('MI_KitchenSurf03_Counter', load(MATS + 'M_Rev02_TexPBR'), {'Roughness': 0.48, 'Metallic': 0.0}, {'Tint': (1, 1, 1, 1)},
                      {'BaseColorMap': load(KIT + 'T_KitchenSurf03_IvoryEnamel')})
grout_mi = instance('MI_KitchenSurf03_Grout', load(MATS + 'M_Rev02_ConstPBR'), {'Roughness': 0.90, 'Metallic': 0.0}, {'BaseColor': (0.76, 0.70, 0.59, 1)})
# The glaze instances named by the release (MI_Backsplash02_Ivory/_Sage/_Cap) never existed in Content: the batch-2 bands
# silently fell back to their flat FBX Phong ceramics. Created here as glaze-image PBR (KI-BACKSPLASH-02 glaze textures).
texpbr = load(MATS + 'M_Rev02_TexPBR'); B2 = R2 + 'KI_Backsplash02/'
TILE = {'warm_ivory_ceramic': instance('MI_Backsplash02_Ivory', texpbr, {'Roughness': 0.32, 'Metallic': 0.0}, {'Tint': (1, 1, 1, 1)}, {'BaseColorMap': load(B2 + 'T_Backsplash02_GlazeIvory')}),
        'soft_sage_ceramic': instance('MI_Backsplash02_Sage', texpbr, {'Roughness': 0.32, 'Metallic': 0.0}, {'Tint': (1, 1, 1, 1)}, {'BaseColorMap': load(B2 + 'T_Backsplash02_GlazeSage')}),
        'cream_glazed_cap': instance('MI_Backsplash02_Cap', texpbr, {'Roughness': 0.28, 'Metallic': 0.0}, {'Tint': (1, 1, 1, 1)}, {'BaseColorMap': load(B2 + 'T_Backsplash02_GlazeIvory')}),
        'warm_cream_grout': grout_mi}
def norm(n): return str(n).lower().replace(' ', '_')

# carcasses
for code in ('0425', '0775', '0450'):
    a = acts['Art_KI_Cab%s_body' % code]; c = a.static_mesh_component; sm = load(KIT + 'KI_Cab06_%s_Body' % code)
    old = {norm(s.material_slot_name): c.get_material(i) for i, s in enumerate(c.static_mesh.static_materials)}
    a.modify(); c.set_static_mesh(sm)
    for i, s in enumerate(sm.static_materials): c.set_material(i, old[norm(s.material_slot_name)])
    ncol = len(sm.get_editor_property('body_setup').get_editor_property('agg_geom').get_editor_property('convex_elems'))
    log.append('Art_KI_Cab%s_body -> %s (%d UCX, %s)' % (code, sm.get_name(), ncol, c.get_collision_profile_name()))

# retire fillers and old bands, place slabs and new bands
folder = 'Redesign/Imported Art/Furnishing'
gone = [l for l in acts if l.startswith(('Art_KI_CounterFiller02_', 'Art_KI_Backsplash02_', 'Art_KI_Counter03_', 'Art_KI_Backsplash03_'))]
for l in gone: A.destroy_actor(acts.pop(l))
log.append('removed %d old filler/band (or previous-run) actors' % len(gone))
assert L.set_current_level_by_name('L_Apartment_Rev02')
PLACE = [('KI_Counter03_A', (112.1, 6, 86), 'BlockAll'), ('KI_Counter03_B', (267.5, 6, 86), 'BlockAll'), ('KI_Counter03_C', (420.0, 6, 86), 'BlockAll'),
         ('KI_Backsplash03_A', (112.1, 6, 91), 'NoCollision'), ('KI_Backsplash03_B', (267.5, 6, 91), 'NoCollision'),
         ('KI_Backsplash03_Range', (345.0, 6, 107), 'NoCollision'), ('KI_Backsplash03_C', (420.0, 6, 91), 'NoCollision')]
for name, loc, col in PLACE:
    sm = load(KIT + name)
    a = A.spawn_actor_from_object(sm, unreal.Vector(*loc), unreal.Rotator(0, 0, 0))
    a.set_actor_label('Art_' + name); a.set_folder_path(folder); acts['Art_' + name] = a
    c = a.static_mesh_component; c.set_collision_profile_name(col)
    for i, s in enumerate(sm.static_materials):
        m = counter_mi if norm(s.material_slot_name) == 'counter_ivory' else TILE.get(norm(s.material_slot_name))
        assert m is not None, (name, s.material_slot_name)
        c.set_material(i, m)
    o, e = a.get_actor_bounds(False)
    log.append('Art_%s x%.1f-%.1f y%.1f-%.1f z%.1f-%.1f %s' % (name, o.x-e.x, o.x+e.x, o.y-e.y, o.y+e.y, o.z-e.z, o.z+e.z, col))
assert L.save_all_dirty_levels()
unreal.log('[Rev02 kitchen surfaces]\n' + '\n'.join(log))
