"""Place kitchen casework on the north wall run and the pantry on the east wall.

All kit parts were exported in assembly space; each part shares its body's transform.
Fronts import as +Y. North wall room face is y=6, east wall face x=1194.
Sink assembly (2.37 m incl. side cabinets) is centred under the window per the plan;
it replaces planned counter placeholders 08-10. Pantry yaw 90 so its doors face west.
"""
import unreal
R = '/Game/ICanFixHim/Environment/Redesign/'
load = unreal.EditorAssetLibrary.load_asset
A = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert L.load_level('/Game/ICanFixHim/Maps/L_Apartment_Redesign_Blockout')
FOLDER = 'Redesign/Imported Art/Kitchen Casework'
for a in A.get_all_level_actors():
    lab = a.get_actor_label()
    if str(a.get_folder_path()) == FOLDER or lab.startswith(('Placeholder_08_', 'Placeholder_09_', 'Placeholder_10_', 'Placeholder_11_')):
        A.destroy_actor(a)

# Repair-damage overlays are owned by build_redesign_gameplay.py once it has run (moved into the gameplay
# sublevel and attached to their malady). Never duplicate or recreate one that already exists in any level.
def _exists_anywhere(label):
    return any(a.get_actor_label() == label for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors())

def kit(folder, parts, loc, yaw, body, tags=None):
    for p in parts:
        if tags and p in tags and _exists_anywhere('Art_' + p): continue
        a = A.spawn_actor_from_object(load(R + folder + '/' + p), unreal.Vector(*loc), unreal.Rotator(0, 0, yaw))
        a.set_actor_label('Art_' + p); a.set_folder_path(FOLDER)
        if p != body: a.static_mesh_component.set_collision_profile_name('NoCollision')
        if tags and p in tags: a.tags = [unreal.Name(t) for t in tags[p]]

kit('KI_Sink', ['KI_SINK_body', 'KI_SINK_L_door', 'KI_SINK_R_door', 'KI_SINK_L_drawer', 'KI_SINK_R_drawer', 'KI_SINK_L_tap', 'KI_SINK_R_tap', 'KI_SINK_damage'],
    (855, 38, 0), 0, 'KI_SINK_body', tags={'KI_SINK_damage': ['RepairDamage', 'lukey']})
kit('KI_Cabinet', ['KI_Cabinet_body', 'KI_Cabinet_door', 'KI_Cabinet_drawer'], (1006, 38, 0), 0, 'KI_Cabinet_body')
kit('KI_Upper', ['KI_Upper_Body', 'KI_Upper_LeftDoor', 'KI_Upper_RightDoor'], (975, 22, 160), 0, 'KI_Upper_Body')
kit('KI_Pantry', ['KI_Pantry_Body', 'KI_Pantry_LeftDoor', 'KI_Pantry_RightDoor'], (1160.5, 62, 0), 90, 'KI_Pantry_Body')
for p in ['KI_Backsplash_Module_1m', 'KI_Backsplash_End_Left', 'KI_Backsplash_End_Right']:
    a = A.spawn_actor_from_object(load(R + 'KI_Backsplash/' + p), unreal.Vector(925, 6, 91), unreal.Rotator(0, 0, 0))
    a.set_actor_label('Art_' + p); a.set_folder_path(FOLDER); a.static_mesh_component.set_collision_profile_name('NoCollision')
assert L.save_current_level()
unreal.log('[Casework] saved')
