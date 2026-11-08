"""Correct imported furniture's front directions after Blender FBX axis conversion."""
import unreal
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
if not levels.load_level('/Game/ICanFixHim/Maps/L_Apartment_Redesign_Blockout'):
    raise RuntimeError('Could not load redesign')
rotations = {'Art_LV_Sofa': 90, 'Art_BR_Bed': 180, 'Art_LV_Chair_03': 0,
             'Art_KI_Chair_13': -90, 'Art_KI_Chair_14': 90, 'Art_OF_Daybed_23': -90}
found = set()
for a in actors.get_all_level_actors():
    label = a.get_actor_label()
    if label in rotations:
        a.set_actor_rotation(unreal.Rotator(0,0,rotations[label]),False)
        found.add(label)
if found != set(rotations):
    raise RuntimeError('Missing actors: '+str(set(rotations)-found))
if not levels.save_current_level():
    raise RuntimeError('Could not save redesign')
