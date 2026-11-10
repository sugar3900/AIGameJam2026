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
assert L.save_current_level()
unreal.log('[Rev02 lighting] saved')
