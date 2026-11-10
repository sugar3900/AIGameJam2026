"""Rev02 step 5g (FIX-031/032): LV-TV-02 tabletop television on the kept LV-TV-01 stand, real materials, cabinet doors.

LV-TV-02 (README): Stand (exact original stand faces/UVs/slots), Housing and one Screen share the LV-TV-01 floor-centre
origin, placed like LV-TV-01 at (1165.1,205,0) yaw 90. The combined LV_TV_body becomes the stand-only mesh (same actor,
relabelled Art_LV_TV02_Stand), the housing is a new actor, and the 'TV' interactable keeps its label, room, prompts
and TvOn/TvOff cues with the screen as its Body (assembly-origin vertices, so the body sits at the assembly
transform and the root moves to the screen centre). The screen's one material (M_Rev02_TVScreen) is faded by the
existing Light toggle through GlowActors (GlowStrength 0 off .. authored value on); the local light is a modest
warm-white fill in front of the set instead of the old 1500-unitless blue wash.

FIX-032: every stand/door slot gets an explicit engine material (painted walnut texture x README tint etc.), and the
two original hinged doors (hinge-local pivots) become ROTATE interactables. Re-runnable. Run after rev02_05f.
"""
import unreal
EAL = unreal.EditorAssetLibrary
A = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
R2 = '/Game/ICanFixHim/Environment/Rev02/'
KIT, MATS = R2 + 'LV_TV02/', R2 + 'Materials/'
ORIGIN, YAW = unreal.Vector(1165.1, 205.0, 0.0), 90.0
SCREEN_CENTRE = unreal.Vector(1146.8, 194.5, 99.2)
acts = {a.get_actor_label(): a for a in A.get_all_level_actors()}

def actor(*labels):
    for l in labels:
        if l in acts: return acts[l]
    raise AssertionError('missing ' + str(labels))

def mat(slot):
    for prefix in ('MI_TV02_', 'MI_TV01_'):
        p = MATS + prefix + slot.replace('TV02_', '')
        if EAL.does_asset_exist(p): return EAL.load_asset(p)
    raise AssertionError('no material for slot ' + slot)

def dress(comp, sm):
    for i, s in enumerate(sm.static_materials):
        n = str(s.material_slot_name)
        comp.set_material(i, EAL.load_asset(MATS + 'MI_TV02_Screen') if n == 'TV02_CRTGlass' else mat(n))

# ---- stand: the old combined body actor keeps its place, becomes the stand-only mesh ----
stand = actor('Art_LV_TV02_Stand', 'Art_LV_TV_LV_TV_body'); stand.modify()
stand.set_actor_label('Art_LV_TV02_Stand'); acts['Art_LV_TV02_Stand'] = stand
assert (stand.get_actor_location() - ORIGIN).length() < 0.2 and abs(stand.get_actor_rotation().yaw - YAW) < 0.1
sm = EAL.load_asset(KIT + 'LV_TV02_Stand'); stand.static_mesh_component.set_static_mesh(sm); dress(stand.static_mesh_component, sm)
# ---- housing (persistent level, static, complex collision like the old body) ----
if 'Art_LV_TV02_Housing' in acts: A.destroy_actor(acts.pop('Art_LV_TV02_Housing'))
assert L.set_current_level_by_name('L_Apartment_Rev02')
sm = EAL.load_asset(KIT + 'LV_TV02_Housing')
hs = A.spawn_actor_from_object(sm, ORIGIN, unreal.Rotator(0, 0, YAW))
hs.set_actor_label('Art_LV_TV02_Housing'); hs.set_folder_path(str(stand.get_folder_path())); acts['Art_LV_TV02_Housing'] = hs
hs.static_mesh_component.set_collision_profile_name('BlockAll'); dress(hs.static_mesh_component, sm)
# ---- the old LV-TV-01 screen art is retired (one screen, no overlay) ----
for l in ('Art_LV_TV_LV_TV_screen_off',):
    if l in acts: A.destroy_actor(acts.pop(l))
# ---- door materials (original meshes, hinge-local pivots kept) ----
for l in ('Art_LV_TV_LV_TV_left', 'Art_LV_TV_LV_TV_right'):
    d = actor(l); d.modify(); dress(d.static_mesh_component, d.static_mesh_component.static_mesh)

# ---- TV interactable: screen body, root at the screen centre, warm-white glow + modest fill ----
assert L.set_current_level_by_name('L_Apartment_Rev02_Gameplay')
tv = actor('TV'); tv.modify()
tv.set_actor_location_and_rotation(SCREEN_CENTRE, unreal.Rotator(0, 0, 180), False, True)
body = tv.get_editor_property('body'); scr = EAL.load_asset(KIT + 'LV_TV02_Screen')
body.set_static_mesh(scr); body.set_world_location_and_rotation(ORIGIN, unreal.Rotator(0, 0, YAW), False, False)
dress(body, scr)
tv.set_editor_property('use_authored_body_materials', True)
tv.set_editor_property('glow_actors', [tv]); tv.set_editor_property('glow_param', 'GlowStrength')
lt = tv.get_editor_property('light'); lt.modify()
lt.set_world_location(unreal.Vector(1100.0, 194.5, 99.0), False, False)       # ~47 cm into the room, facing the set
lt.set_editor_property('intensity_units', unreal.LightUnits.LUMENS)
lt.set_editor_property('light_color', unreal.Color(r=255, g=232, b=200, a=255))   # warm white, not orange, not blue
lt.set_editor_property('attenuation_radius', 260.0); lt.set_editor_property('source_radius', 20.0)
lt.set_editor_property('specular_scale', 0.3)
tv.set_editor_property('light_intensity_on', 30.0)

# ---- FIX-032 cabinet doors: hinge-local pivots at the source hinge origins (+/-0.483, -0.218) ----
def door(label, art_label, hinge_src, swing):
    art = actor(art_label)
    hinge = ORIGIN + unreal.Vector(100 * hinge_src[1], 100 * hinge_src[0], 0)   # yaw 90 + Y flip: offset = (100y, 100x)
    a = acts.get(label)
    if a is None:
        a = A.spawn_actor_from_class(unreal.FixHimInteractable, hinge, unreal.Rotator(0, 0, 0))
        a.set_actor_label(label); a.set_folder_path('Gameplay/Interactables/living'); acts[label] = a
    a.modify(); a.set_actor_location_and_rotation(hinge, unreal.Rotator(0, 0, 0), False, True)
    for k, v in (('room_id', 'living'), ('toggle', unreal.InteractToggle.ROTATE), ('prompt_off', 'Open cabinet'),
                 ('prompt_on', 'Close cabinet'), ('use_authored_body_materials', True), ('toggle_rotation', unreal.Rotator(0, 0, swing))):
        a.set_editor_property(k, v)
    a.get_editor_property('pivot').set_relative_location(unreal.Vector(0, 0, 0), False, False)
    a.get_editor_property('pivot').set_relative_rotation(unreal.Rotator(0, 0, 0), False, False)
    src = art.static_mesh_component; b = a.get_editor_property('body')
    b.set_static_mesh(src.static_mesh)
    b.set_world_location_and_rotation(art.get_actor_location(), art.get_actor_rotation(), False, False)
    for i in range(src.get_num_materials()): b.set_material(i, src.get_material(i))
    art.modify(); src.modify(); art.set_actor_hidden_in_game(True); src.set_visibility(False)
    src.set_collision_profile_name('NoCollision'); art.tags = [unreal.Name('GameplayBodySource')]
    return a
# The door meshes import with assembly-space vertices (actor at the assembly origin), so the pivot is placed at the
# documented hinge origin and the body keeps the art transform. Swing signs verified by the sweep in validation
# (source -90/+90 invert under the Y flip: +90 left / -90 right open outward into the room).
door('TVCabinet_Door_L', 'Art_LV_TV_LV_TV_left', (-0.483, -0.218), 90.0)
door('TVCabinet_Door_R', 'Art_LV_TV_LV_TV_right', (0.483, -0.218), -90.0)
assert L.set_current_level_by_name('L_Apartment_Rev02')
assert L.save_all_dirty_levels()
unreal.log('[Rev02 tv] stand/housing/screen installed; TV root at screen centre; cabinet doors bound')
