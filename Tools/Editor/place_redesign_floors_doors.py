"""Lay floor/ceiling modules per room and seat interior/entry doors.

Modules are tiled in whole counts per room with a uniform per-room scale closest to 1
(no per-tile rotation, so folded/mirrored UVs stay continuous). Blockout floor boxes are
kept hidden as collision. Doors: frame centred in the opening; leaf hinge at frame-local
x=-45 cm. Interior leaves are posed open 80 deg into their rooms for review.
"""
import unreal
R = '/Game/ICanFixHim/Environment/Redesign/'
F = R + 'Finishes/'
load = unreal.EditorAssetLibrary.load_asset
A = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
assert L.load_level('/Game/ICanFixHim/Maps/L_Apartment_Redesign_Blockout')
for a in A.get_all_level_actors():
    fp = str(a.get_folder_path())
    if fp.startswith(('Redesign/Floor Finishes', 'Redesign/Ceiling', 'Redesign/Doors')): A.destroy_actor(a)
    elif fp.startswith('Redesign/Floors'):
        a.static_mesh_component.set_visibility(False)   # keep as floor collision

def spawn(m, loc, yaw, scale, label, folder, mats, collision=False):
    a = A.spawn_actor_from_object(m, unreal.Vector(*loc), unreal.Rotator(0, 0, yaw))
    a.set_actor_scale3d(unreal.Vector(*scale)); a.set_actor_label(label); a.set_folder_path(folder)
    c = a.static_mesh_component
    if not collision: c.set_collision_profile_name('NoCollision')
    for i, mt in enumerate(mats):
        if mt: c.set_material(i, mt)
    return a

def best(L, w):
    return min(range(1, 20), key=lambda n: abs(L / (n * w) - 1))

def grid(tag, m, rect, w, h, mats, origin='center', z=0.0, folder='Redesign/Floor Finishes'):
    x0, y0, W, D = rect
    nx, ny = best(W, w), best(D, h)
    sx, sy = W / (nx * w), D / (ny * h)
    for i in range(nx):
        for j in range(ny):
            if origin == 'center':
                loc = (x0 + (i + .5) * w * sx, y0 + (j + .5) * h * sy, z)
            else:  # corner origin, mesh spans +X and -Y
                loc = (x0 + i * w * sx, y0 + (j + 1) * h * sy, z)
            spawn(m, loc, 0, (sx, sy, 1), '%s_%d_%d' % (tag, i, j), folder, mats)
    unreal.log('[Floors] %s %dx%d scale %.3f,%.3f' % (tag, nx, ny, sx, sy))

wood = load(R + 'ARC_FloorWood/ARC_Floor_Wood_2m')
wm = [load(F + 'MI_FloorWood_Subfloor')] + [load(F + 'MI_FloorWood_%d' % i) for i in range(6)]
for tag, rect in [('LV', (0, 0, 550, 380)), ('HA', (0, 380, 1200, 180)), ('BR', (0, 560, 480, 395)), ('OF', (790, 560, 410, 395))]:
    grid('Floor_Wood_' + tag, wood, rect, 200, 200, wm)
grid('Floor_KI_Top', load(R + 'KI_Tile/KI_TILE_TOP'), (550, 0, 650, 380), 100, 100, [load(F + 'MI_KitchenChecker')])
grid('Floor_KI_Sub', load(R + 'KI_Tile/KI_TILE_SUBSTRATE'), (550, 0, 650, 380), 100, 100, [load(F + 'MI_KitchenSubstrate')])
grid('Floor_BA_Hex', load(R + 'BA_Floor/BA_FLOOR_MODULE'), (480, 560, 310, 395), 90, 103.923, 
     [load(F + 'MI_BathGrout'), load(F + 'MI_BathHex_Ivory'), load(F + 'MI_BathHex_Rose')], origin='corner')
grid('Ceiling', load(R + 'ARC_Ceiling/ARC_Ceiling_Module_2m'), (0, 0, 1200, 955), 200, 200, [load(F + 'MI_Ceiling_UV')],
     origin='corner', z=275.0, folder='Redesign/Ceiling')

# Doors
paint, brass, edge, walnut = (load(F + n) for n in ('MI_Door_Paint', 'MI_Door_Brass', 'MI_Door_EdgeWood', 'MI_Entry_Walnut'))
frame, leaf = load(R + 'ARC_Door/ARC_Door_Frame'), load(R + 'ARC_Door/ARC_Door_Leaf')
for room, cx, y, swing in [('LV', 450, 380, -80), ('KI', 665, 380, -80), ('BR', 360, 560, 80), ('BA', 680, 560, 80), ('OF', 1010, 560, 80)]:
    spawn(frame, (cx, y, 0), 0, (1, 1, 1), 'Door_%s_Frame' % room, 'Redesign/Doors', [paint, brass])
    spawn(leaf, (cx - 45, y, 0), swing, (1, 1, 1), 'Door_%s_Leaf' % room, 'Redesign/Doors', [paint, brass, edge])
# Entry on east wall (opening y 397.5-487.5), closed, blocking.
spawn(load(R + 'ARC_EntryDoor/ARC_Entry_Door_Frame'), (1200, 442.5, 0), 90, (1, 1, 1), 'Door_Entry_Frame', 'Redesign/Doors', [paint, brass])
spawn(load(R + 'ARC_EntryDoor/ARC_Entry_Door_Leaf'), (1200, 397.5, 0), 90, (1, 1, 1), 'Door_Entry_Leaf', 'Redesign/Doors', [walnut, brass, edge], collision=True)
assert L.save_current_level()
unreal.log('[Floors] saved')
