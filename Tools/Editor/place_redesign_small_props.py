"""Place the small dressing props (positions from the elevation notes; see the gameplay parity plan).
Re-runnable: everything in its folder is replaced. Props have no collision."""
import os, unreal
exec(open(os.path.join(os.path.dirname(__file__), 'import_redesign_small_props.py')).read().split("if __name__ == '__main__':")[0])
A = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
FOLDER = 'Redesign/Imported Art/Small Props'
Y = lambda yaw: unreal.Rotator(roll=0, pitch=0, yaw=yaw)
# Hanging pan: handle (local +X) points up, pan interior (local +Z) faces the room (+Y).
HANG = unreal.MathLibrary.make_rot_from_xz(unreal.Vector(0, 0, 1), unreal.Vector(0, 1, 0))
ITEMS = [  # label, asset dir, parts, location (cm), rotation
    # Bath west wall shelf (top at z=130) with toiletries; front faces +X into the room.
    ('BA_WallShelf', 'ARC-WALL-SHELF-01', ['ARC_WALL_SHELF_01'], (486, 620, 130), Y(-90)),
    ('BA_Bottle', 'BA-BOTTLE-01', ['BA_Bottle_Body', 'BA_Bottle_Stopper'], (493.5, 598, 130), Y(-90)),
    ('BA_Cup', 'BA-CUP-01', ['BA_Cup', 'BA_Brush_Sage', 'BA_Brush_Ivory'], (493.5, 613, 130), Y(-90)),
    ('BA_Jar', 'BA-JAR-01', ['BA_Jar_Body', 'BA_Jar_Lid'], (493.5, 628, 130), Y(-90)),
    ('BA_Soap', 'BA-SOAP-01', ['BA_SoapDish', 'BA_SoapBar'], (493.5, 643, 130), Y(-90)),
    # Linen cabinet top (z=174.2), cabinet faces west.
    ('BA_FoldedTowel', 'BA-FOLDED-TOWEL-01', ['BA_Folded_Towel'], (754, 893, 174.2), Y(90)),
    ('BA_Tin', 'BA-TIN-01', ['BA_Tin_Body', 'BA_Tin_Lid'], (754, 921, 174.2), Y(90)),
    # Bath north wall (face y=566): hook + hand towel east of the door, switch west of the door casing.
    ('BA_Hook', 'BA-HOOK-01', ['BA_Hook_01'], (770, 566, 150), Y(0)),
    ('BA_HandTowel', 'BA-HAND-TOWEL-01', ['BA_Hand_Towel'], (770, 566, 150), Y(0)),
    ('BA_Switch', 'BA-SWITCH-01', ['BA_Switch_Plate', 'BA_Switch_Toggle'], (612, 566, 120), Y(0)),
    # Toilet roll on the bath east wall (face x=784) just north of the toilet.
    ('BA_Roll', 'BA-ROLL-01', ['BA_Roll_Holder', 'BA_Roll_Paper'], (784, 745, 70), Y(90)),
    # Kitchen: pans hanging on the rail (hooks ~186 cm), bowl + mug on the table, jar/pottery on the cabinet, geranium by the sink.
    ('KI_Pan_A', 'KI-PAN-01', ['KI_Pan_Body', 'KI_Pan_Handle'], (725, 9, 151), HANG),
    ('KI_Pan_B', 'KI-PAN-01', ['KI_Pan_Body', 'KI_Pan_Handle'], (755, 9, 151), HANG),
    ('KI_Bowl', 'KI-BOWL-01', ['KI_Bowl', 'Apple_A', 'Apple_B', 'Lemon_A', 'Lemon_B', 'Pear'], (895, 227.5, 74), Y(0)),
    ('KI_Mug', 'KI-MUG-01', ['KI_Mug_01'], (848, 212, 74), Y(30)),
    ('KI_Jar', 'KI-JAR-01', ['KI_Jar_Body', 'KI_Jar_Lid'], (994, 32, 95.5), Y(0)),
    ('KI_Pottery', 'KI-POTTERY-01', ['KI_Pottery_01'], (1021, 30, 95.5), Y(0)),
    ('KI_Geranium', 'KI-PLANT-01', ['KI_Geranium'], (781, 36, 91), Y(0)),
    # Office papers on the desk.
    ('OF_Papers', 'OF-PAPERS-01', ['OF_PAPERS_01'], (1080, 905, 75.8), Y(10)),
    # Hall: shoe tray beside the bench (back to the south wall), second vase on the end cabinet.
    ('HA_Shoes', 'HA-SHOES-01', ['HA_ShoeTray', 'HA_Oxford_1', 'HA_Oxford_2', 'HA_SlipOn_1', 'HA_SlipOn_2'], (1080, 540.6, 0), Y(180)),
    ('HA_Vase02', 'HA-VASE-02', ['HA_VASE_02'], (17.8, 469, 72), Y(-90)),
    # Bedroom: perfume on the dresser (faces west); a storage box in the closet's back-left corner,
    # clear of Malcolm's stand spot (90, 632), the doorway and the mold sightline.
    ('BR_Perfume', 'BR-PERFUME-01', ['BR_Perfume_Body', 'BR_Perfume_Stopper'], (448, 815, 92.5), Y(90)),
    ('BR_ClosetBox', 'BR-CLOSET-BOX-01', ['BR_BOX_BODY', 'BR_BOX_LID'], (28, 588, 0.3), Y(0)),
]
assert L.load_level('/Game/ICanFixHim/Maps/L_Apartment_Redesign_Blockout')
for a in A.get_all_level_actors():
    if str(a.get_folder_path()) == FOLDER: A.destroy_actor(a)
n = 0
for label, d, parts, loc, rot in ITEMS:
    for p in parts:
        a = A.spawn_actor_from_object(mesh(d, p), unreal.Vector(*loc), rot)
        a.set_actor_label('Art_%s_%s' % (label, p)); a.set_folder_path(FOLDER)
        a.static_mesh_component.set_collision_profile_name('NoCollision'); n += 1
assert L.save_current_level()
unreal.log('[SmallProps] placed %d actors' % n)
