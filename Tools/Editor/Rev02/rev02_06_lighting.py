"""Rev02 step 6: move the layout-dependent parts of the A+ lighting rig (build_redesign_lighting.py) to revision 02.

Fill lights follow the room centres; the painted window-view cards follow the windows (kitchen and living swapped
sides; the bedroom window moved 25 cm west); the bedroom window's sun spot follows its window. Sun, sky, grade
and intensities are unchanged. Positions are absolute, so this is re-runnable.
"""
import unreal
MAP = '/Game/ICanFixHim/Maps/L_Apartment_Rev02'
A = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert L.load_level(MAP)
acts = {a.get_actor_label(): a for a in A.get_all_level_actors()}
def put(label, loc):
    a = acts[label]; a.modify(); a.set_actor_location(unreal.Vector(*loc), False, True)

# FIX-021: room fills sat at head height (z 150) in the room centres; Fill_Kitchen was 57 cm from Lukey's head and
# Fill_Bath 71 cm from Tyler's, blowing out faces with a warm hot spot. Those two move up near the ceiling and away from
# the encounter spots (~1.4-1.5 m from the faces); the other fills are already >2.7 m from any hunk and stay as tuned.
put('Fill_Living', (840, 190, 150)); put('Fill_Kitchen', (300, 235, 245)); put('Fill_Bath', (680, 720, 245)); put('Fill_Hall', (720, 470, 150))
# User feedback (window disk): the shadowless room fills are 40 cm spheres; mirrored in the near-mirror window glass
# (roughness .04) they read as large soft white disks (isolated in PIE with the view cards hidden: present at
# specular 1, gone at 0). Fills only add ambient warmth, so their specular contribution is removed; diffuse unchanged.
for _l in [l for l in acts if l.startswith('Fill_')]:
    _c = acts[_l].light_component; _c.modify(); _c.set_editor_property('specular_scale', 0.0)
# Window views: card centre (x, wall y + 140 outward, (sill + head) / 2 + 20) as in build_redesign_lighting.py.
# FIX-012: clear panes use the Rev02 window glass (see rev02_02b); the bathroom's frosted glass stays.
_glass = unreal.load_asset('/Game/ICanFixHim/Environment/Rev02/Materials/M_Rev02_WindowGlass')
for _a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    _l = _a.get_actor_label()
    if (_l.endswith('_glass') and _l.startswith('Win_') and not _l.startswith('Win_BA_')) or _l == 'Kit_LV_N_Glazing':
        _a.modify(); _a.static_mesh_component.set_material(0, _glass)
put('WindowView_KI', (215, -140, (125 + 240) / 2 + 20))
put('WindowView_LV', (855, -140, (90 + 230) / 2 + 20))
put('WindowView_BR', (385, 1095, (90 + 230) / 2 + 20))
put('WindowSun_BR', (385 - 60, 955 + 260, 230 + 170))
# Batch 2 (night window slits): the WindowSun_* spots stayed at full 14000 at night. Tag them so the player
# controller's daylight update fades them with the window-view curve (1 by day -> 0 at night).
for _l in [l for l in acts if l.startswith('WindowSun_')]:
    _a = acts[_l]; _a.modify()
    _a.tags = [t for t in _a.tags if str(t) != 'WindowSun'] + [unreal.Name('WindowSun')]
# User feedback (exposed view-card edges at close oblique/downward views). Coverage needed grows with the card's
# distance behind the glass: from a 40 cm eye standing at a 1.6 m window, rays reach ~window_half + 4 x distance
# sideways and ~1.8 x distance down. At the old 1.4 m that needs a 6.4 m half-width, overlapping the neighbouring
# card on the same facade (kitchen/living 6.4 m apart, bedroom/office 6.55 m). So each card moves to 0.55 m behind
# its wall and its painting shrinks to 0.81 (same apparent size from ~3 m inside the room); M_Rev02_WindowViewWide
# then extends coverage 1.4x across / 1.6x vertically by mirror-filling only the outer band. Half-width stays under
# half the facade spacing (no overlap); WindowView tag and controller WindowBrightness unchanged.
_wide = unreal.load_asset('/Game/ICanFixHim/Environment/Rev02/Materials/MI_Rev02_WindowViewWide')
CARD_D, CARD_S, KU, KV = 55.0, 0.81, 1.4, 1.6
for _l, _wall, _out in (('WindowView_KI', 0, -1), ('WindowView_LV', 0, -1), ('WindowView_BR', 955, 1), ('WindowView_OF', 955, 1)):
    if _l not in acts: continue
    _a = acts[_l]; _a.modify(); _p = _a.get_actor_location()
    _a.set_actor_location(unreal.Vector(_p.x, _wall + _out * CARD_D, _p.z), False, True)
    _a.set_actor_scale3d(unreal.Vector(5.6 * CARD_S * KU, 3.2 * CARD_S * KV, 1)); _a.static_mesh_component.set_material(0, _wide)
# The bath window is frosted (no clear view): its card keeps the original size, distance and material.
if 'WindowView_BA' in acts:
    _a = acts['WindowView_BA']; _a.modify(); _a.set_actor_scale3d(unreal.Vector(5.6, 3.2, 1))
    _a.static_mesh_component.set_material(0, unreal.load_asset('/Game/ICanFixHim/Environment/Redesign/Finishes/MI_WindowView'))
assert L.save_current_level()
unreal.log('[Rev02 lighting] saved')
