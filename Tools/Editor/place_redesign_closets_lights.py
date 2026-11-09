"""Place BR-CLOSET-01, ARC-SLIDING-CLOSET-01 (coat + office), ARC-CURTAINS-01,
ARC-CEILING-LIGHT-01 and LV-RADIATOR-01. Fronts import as +Y (Blender -Y).

BR closet body is a complete room (walls, floor to -7 cm, ceiling at 275) centred on its
plan footprint [0,560,180,145]; overlapping shell faces inside the footprint are hidden
but keep collision; body is lifted 0.3 cm so its floor/walls win over the room floor.
Sliding panels: Blender offsets (-0.22,-0.028)/(0.22,0.028) -> Unreal (-22,+2.8)/(22,-2.8).
Curtains: rod raised 14 cm above the README height to clear the living-window casing (top 237.5).
"""
import unreal
R = '/Game/ICanFixHim/Environment/Redesign/'
load = unreal.EditorAssetLibrary.load_asset
A = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert L.load_level('/Game/ICanFixHim/Maps/L_Apartment_Redesign_Blockout')
FOLDER = 'Redesign/Imported Art/Closets Lights'
for a in A.get_all_level_actors():
    if str(a.get_folder_path()) == FOLDER: A.destroy_actor(a)

def put(path, loc, yaw=0, label=None, collide=False, tags=()):
    m = load(R + path)
    a = A.spawn_actor_from_object(m, unreal.Vector(*loc), unreal.Rotator(0, 0, yaw))
    a.set_actor_label(label or 'Art_' + path.split('/')[-1]); a.set_folder_path(FOLDER)
    comp = a.get_component_by_class(unreal.PrimitiveComponent)
    if not collide: comp.set_collision_profile_name('NoCollision')
    if tags: a.tags = [unreal.Name(t) for t in tags]
    return a

# Repair-damage overlays are owned by build_redesign_gameplay.py once it has run (moved into the gameplay
# sublevel and attached to their malady). Never duplicate or recreate one that already exists in any level.
def _exists_anywhere(label):
    return any(a.get_actor_label() == label for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors())

# Bedroom mold closet (Malcolm).
hidden = 0
for a in A.get_all_level_actors():
    if not str(a.get_folder_path()).startswith('Redesign/Shell'): continue
    o, e = a.get_actor_bounds(False)
    if o.x - e.x >= -7 and o.x + e.x <= 187 and o.y - e.y >= 553 and o.y + e.y <= 712:
        a.static_mesh_component.set_visibility(False); hidden += 1
put('BR_Closet/BR_Closet_Body', (90, 632.5, 0.3), label='Art_BR_Closet_Body')
put('BR_Closet/BR_Closet_Door_L', (90, 632.5, 0.3), label='Art_BR_Closet_Door_L', collide=True)
put('BR_Closet/BR_Closet_Door_R', (90, 632.5, 0.3), label='Art_BR_Closet_Door_R', collide=True)
mold = None if _exists_anywhere('Art_BR_Closet_Mold') else put('BR_Closet/BR_Closet_Mold', (90, 632.5, 0.3), label='Art_BR_Closet_Mold', tags=('RepairDamage', 'malcolm'))
if mold: mold.static_mesh_component.set_cast_shadow(False)

# Sliding bypass fronts: coat closet (hall, wall y=380) and office closet (wall y=680), both facing +Y.
for room, cx, y in [('Coat', 1135, 380), ('Office', 1138, 680)]:
    put('ARC_SlidingCloset/ARC_Sliding_Frame', (cx, y, 0), label='Art_%sCloset_Frame' % room)
    put('ARC_SlidingCloset/ARC_Sliding_LeftPanel', (cx - 22, y + 2.8, 0), label='Art_%sCloset_LeftPanel' % room, collide=True)
    put('ARC_SlidingCloset/ARC_Sliding_RightPanel', (cx + 22, y - 2.8, 0), label='Art_%sCloset_RightPanel' % room, collide=True)

# Living window curtains (window centre x=215; casing front y=16).
put('ARC_Curtains/Curtain_Rod', (215, 23, 14), label='Art_LV_Curtain_Rod')
for side in ('Left', 'Right'):
    a = put('ARC_Curtains/Curtain_' + side, (215, 23, 14), label='Art_LV_Curtain_' + side)
    a.skeletal_mesh_component.set_morph_target('Closed', 0.0, True)  # 0 = gathered open

# Flush ceiling lights (origin at ceiling attachment, pointing down).
for name, x, y in [('Living', 275, 190), ('HallWest', 300, 470), ('HallEast', 900, 470)]:
    put('ARC_CeilingLight/ARC_CeilingLight_Hardware', (x, y, 275), label='Art_CeilingLight_%s_Hardware' % name)
    put('ARC_CeilingLight/ARC_CeilingLight_Glass', (x, y, 275), label='Art_CeilingLight_%s_Glass' % name)

# Radiator under the living window, east of the armchair (chair x 120-195); back at wall face y=6.
put('LV_Radiator/LV_Radiator', (245, 6 + 15.9, 0), label='Art_LV_Radiator', collide=True)
assert L.save_current_level()
unreal.log('[CL] saved; hidden closet shell faces=%d' % hidden)
