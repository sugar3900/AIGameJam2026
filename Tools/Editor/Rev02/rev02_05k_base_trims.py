"""Rev02 step 5k (user feedback): baseboard runs stop at the outer edge of every door/closet/portal casing.

rev02_03 laid the straight Baseboard_1m runs to the rough openings, but the casings extend past the openings (e.g.
the ARC-DOOR-02 casing outer edge is 7 cm beyond the 1.05 m rough width), so run ends crossed the casing faces. For
each straight run (square ends; mitred inside/outside corner pieces are never touched), the along-wall interval
occupied by any overlapping casing footprint at floor level is subtracted and the run keeps the longest remaining
segment: the run's square end butts the casing's outer edge. Length changes only scale X (the strip's length axis),
never the profile. Re-runnable (already-clear runs are unchanged). Run after rev02_05j.
"""
import unreal
A = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
acts = A.get_all_level_actors()
OBST = ('Door_BR_Frame', 'Door_BA_Frame', 'Door_OF_Frame', 'Door_Entry_Frame', 'Casing_KI_N', 'Casing_KI_S',
        'Casing_LV_N', 'Casing_LV_S', 'Art_CoatCloset_Frame', 'Art_OfficeCloset_Frame', 'Art_BR_Closet02_Trim')
def box(a):
    o, e = a.get_actor_bounds(False); return (o.x - e.x, o.x + e.x, o.y - e.y, o.y + e.y, o.z - e.z, o.z + e.z)
obs = [(a.get_actor_label(), box(a)) for a in acts if a.get_actor_label() in OBST]
log = []
for a in acts:
    if not isinstance(a, unreal.StaticMeshActor): continue
    sm = a.static_mesh_component.static_mesh
    if not sm or sm.get_name() != 'Baseboard_1m': continue
    b = box(a); yaw = round(a.get_actor_rotation().yaw) % 360
    axis = 0 if yaw in (0, 180) else 1                      # world axis along the run
    sign = 1 if yaw in (0, 90) else -1                      # local +X direction along that axis
    lo, hi = (b[0], b[1]) if axis == 0 else (b[2], b[3])
    segs = [(lo, hi)]
    for n, c in obs:
        if not (b[0] < c[1] - 0.05 and b[1] > c[0] + 0.05 and b[2] < c[3] - 0.05 and b[3] > c[2] + 0.05 and b[4] < 15):
            continue
        c0, c1 = (c[0], c[1]) if axis == 0 else (c[2], c[3])
        segs = [s for seg in segs for s in ((seg[0], min(seg[1], c0)), (max(seg[0], c1), seg[1])) if s[1] - s[0] > 0.05]
    if segs == [(lo, hi)]: continue
    if not segs:
        a.modify(); a.set_actor_hidden_in_game(True); a.static_mesh_component.set_visibility(False)
        log.append('%s fully inside a casing: hidden' % a.get_actor_label()); continue
    s0, s1 = max(segs, key=lambda s: s[1] - s[0])
    p = a.get_actor_location(); start = s0 if sign > 0 else s1
    newp = unreal.Vector(start, p.y, p.z) if axis == 0 else unreal.Vector(p.x, start, p.z)
    a.modify(); a.set_actor_location(newp, False, True)
    sc = a.get_actor_scale3d(); a.set_actor_scale3d(unreal.Vector((s1 - s0) / 100.0, sc.y, sc.z))
    log.append('%s %s %.1f-%.1f -> %.1f-%.1f' % (a.get_actor_label(), 'xy'[axis], lo, hi, s0, s1))
assert L.save_all_dirty_levels()
unreal.log('[Rev02 base trims]\n' + '\n'.join(log))
