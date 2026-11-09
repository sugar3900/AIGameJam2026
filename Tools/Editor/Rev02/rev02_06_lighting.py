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

put('Fill_Living', (840, 190, 150)); put('Fill_Kitchen', (240, 190, 150)); put('Fill_Hall', (720, 470, 150))
# Window views: card centre (x, wall y + 140 outward, (sill + head) / 2 + 20) as in build_redesign_lighting.py.
put('WindowView_KI', (215, -140, (125 + 240) / 2 + 20))
put('WindowView_LV', (855, -140, (90 + 230) / 2 + 20))
put('WindowView_BR', (385, 1095, (90 + 230) / 2 + 20))
put('WindowSun_BR', (385 - 60, 955 + 260, 230 + 170))
assert L.save_current_level()
unreal.log('[Rev02 lighting] saved')
