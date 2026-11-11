"""Rev02 step 5l (batch 2, kitchen source releases): CABINET-JOINERY-04 fronts, KI-BACKSPLASH-02 + counter infills,
KI-RANGE-02, and the closet-box cloth binding. Re-runnable; run after rev02_05k.

- CABINET-JOINERY-04: only the four lower doors and four drawers change (KI_Cab05_*). Every pivot is unchanged from
  JOINERY-02/03, so the installed interactable roots, swing travel (Sink_Door_L 100 incl.), drawer roots/slide and
  the 0775 stationary filler stay; bodies swap mesh in place. Drawer slot names carry exporter suffixes (_002...),
  mapped to the same MI_Joinery_* finishes.
- KI-BACKSPLASH-02: the stretched KI-BACKSPLASH-01 modules and every end cap are retired; four fitted bands and five
  ivory counter infills are placed at their assembly.json world_origin_cm, yaw 0, scale 1 (native 10 cm square
  tiles, cropped boundaries, top bullnose + fridge-side end only). Decorative, NoCollision. Tiles -> glazed
  MI_Backsplash02_*, grout keeps the installed grout material, infills -> the installed Counter_Ivory finish.
- KI-RANGE-02: body/door meshes swap in place on Art_KI_Range_Body / Oven_Door (same export convention, same hinge
  root); existing materials per slot and complex-as-simple collision, like KI-RANGE-01. Burner, flame, kettle,
  controls untouched.
- BR-CLOSET-BOX-01 'Sage_woven_cloth' -> source sage-linen texture, body and lid, all installed boxes.
"""
import json, os, re, unreal
EAL = unreal.EditorAssetLibrary
A = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
SRC = os.path.join(ROOT, 'Art Source/Apartment Redesign/Assets')
R2 = '/Game/ICanFixHim/Environment/Rev02/'; MATS = R2 + 'Materials/'
acts = {a.get_actor_label(): a for a in A.get_all_level_actors()}
log = []
def mi(n): return EAL.load_asset(MATS + n)

def joinery_mat(slot):
    return mi('MI_' + re.sub(r'_\d+$', '', slot))

# ---- CABINET-JOINERY-04 fronts ----
FRONTS = {'Cabinet_Door': '0425_door', 'Cabinet_Door_2': '0450_door', 'Sink_Door_L': '0775_door_L', 'Sink_Door_R': '0775_door_R',
          'Kitchen_Drawer': '0425_drawer', 'Kitchen_Drawer_2': '0450_drawer', 'Sink_Drawer_L': '0775_drawer_L', 'Sink_Drawer_R': '0775_drawer_R'}
ART = {'0425_door': 'Art_KI_Cab0425_door', '0450_door': 'Art_KI_Cab0450_door', '0775_door_L': 'Art_KI_Cab0775_door_L', '0775_door_R': 'Art_KI_Cab0775_door_R',
       '0425_drawer': 'Art_KI_Cab0425_drawer', '0450_drawer': 'Art_KI_Cab0450_drawer', '0775_drawer_L': 'Art_KI_Cab0775_drawer_L', '0775_drawer_R': 'Art_KI_Cab0775_drawer_R'}
for label, part in FRONTS.items():
    sm = EAL.load_asset(R2 + 'Joinery05/KI_Cab05_' + part)
    for comp, owner in ((acts[label].get_editor_property('body'), acts[label]), (acts[ART[part]].static_mesh_component, acts[ART[part]])):
        owner.modify(); comp.set_static_mesh(sm)
        for i, s in enumerate(sm.static_materials): comp.set_material(i, joinery_mat(str(s.material_slot_name)))
    log.append('%s -> KI_Cab05_%s' % (label, part))

# ---- KI-BACKSPLASH-02 ----
old = [l for l in acts if l.startswith(('Art_KI_Backsplash_', 'Art_KI_Backsplash02_', 'Art_KI_CounterFiller02_'))]
grout = EAL.load_asset('/Game/ICanFixHim/Environment/Redesign/KI_Backsplash/Warm_cream_grout')
counter = None
for i, s in enumerate(acts['Art_KI_Cab0425_body'].static_mesh_component.static_mesh.static_materials):
    if str(s.material_slot_name) == 'Counter_Ivory': counter = acts['Art_KI_Cab0425_body'].static_mesh_component.get_material(i)
folder = 'Redesign/Imported Art/Furnishing'
for l in old: A.destroy_actor(acts.pop(l))
SLOT = {'Warm cream grout': grout, 'Warm_cream_grout': grout, 'Warm ivory ceramic': mi('MI_Backsplash02_Ivory'), 'Warm_ivory_ceramic': mi('MI_Backsplash02_Ivory'),
        'Soft sage ceramic': mi('MI_Backsplash02_Sage'), 'Soft_sage_ceramic': mi('MI_Backsplash02_Sage'), 'Cream glazed cap': mi('MI_Backsplash02_Cap'),
        'Cream_glazed_cap': mi('MI_Backsplash02_Cap'), 'Counter_Ivory': counter}
asm = json.load(open(os.path.join(SRC, 'KI-BACKSPLASH-02/assembly.json')))
assert L.set_current_level_by_name('L_Apartment_Rev02')
for p in asm['parts']:
    name = os.path.splitext(p['file'])[0]; sm = EAL.load_asset(R2 + 'KI_Backsplash02/' + name)
    a = A.spawn_actor_from_object(sm, unreal.Vector(*p['world_origin_cm']), unreal.Rotator(0, 0, 0))
    a.set_actor_label('Art_' + name); a.set_folder_path(folder); acts['Art_' + name] = a
    c = a.static_mesh_component; c.set_collision_profile_name('NoCollision')
    for i, s in enumerate(sm.static_materials): c.set_material(i, SLOT[str(s.material_slot_name)])
    o, e = a.get_actor_bounds(False)
    log.append('Art_%s x%.1f-%.1f y%.1f-%.1f z%.1f-%.1f' % (name, o.x - e.x, o.x + e.x, o.y - e.y, o.y + e.y, o.z - e.z, o.z + e.z))

# ---- KI-RANGE-02 ----
for new, owners in (('KI_RANGE02_Body', ('Art_KI_Range_Body', None)), ('KI_RANGE02_Door', ('Art_KI_Range_Door', 'Oven_Door'))):
    sm = EAL.load_asset(R2 + 'KI_Range02/' + new)
    bs = sm.get_editor_property('body_setup'); bs.set_editor_property('collision_trace_flag', unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
    EAL.save_loaded_asset(sm, False)
    comps = [(acts[owners[0]], acts[owners[0]].static_mesh_component)] + ([(acts[owners[1]], acts[owners[1]].get_editor_property('body'))] if owners[1] else [])
    for owner, c in comps:
        names = {str(s.material_slot_name): c.get_material(i) for i, s in enumerate(c.static_mesh.static_materials)}
        owner.modify(); c.set_static_mesh(sm)
        for i, s in enumerate(sm.static_materials): c.set_material(i, names[str(s.material_slot_name)])
    log.append('%s -> %s' % (owners, new))

# ---- closet boxes: Sage_woven_cloth -> sage-linen ----
cloth = mi('MI_ClosetBox_SageLinen'); n = 0
for a in A.get_all_level_actors():
    if not isinstance(a, unreal.StaticMeshActor) or not a.static_mesh_component.static_mesh: continue
    if '/BR_CLOSET_BOX/' not in a.static_mesh_component.static_mesh.get_path_name(): continue
    c = a.static_mesh_component
    for i, s in enumerate(c.static_mesh.static_materials):
        if str(s.material_slot_name) == 'Sage_woven_cloth': a.modify(); c.set_material(i, cloth); n += 1
log.append('closet box cloth slots bound: %d' % n)
assert L.save_all_dirty_levels()
unreal.log('[Rev02 kitchen fit]\n' + '\n'.join(log))
