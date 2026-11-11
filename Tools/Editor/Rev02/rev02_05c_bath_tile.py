"""Rev02 step 5c (FIX-007): bathroom tile treatment per placement-contract.json tile_treatment.

Ordinary field 0-1.00 m with the 50 mm plum cap at 1.00-1.05; full-height field around the bath (west/east walls from
y 8.55, the whole south wall cut around the window x 5.25-6.40 / z 1.50-2.30) with a vertical 50 mm bullnose at
y 8.50-8.55, z 1.00-2.75. The old stretched 1 m modules (x-scaled up to 1.39) are replaced.

No cell is stretched: each contract panel is built from unscaled BA_Tile_1m_Module copies laid on one grid per wall
(10 cm pitch, rows from the floor) and cropped with Geometry Script plane cuts at the panel edges, so grout rows and
columns stay continuous between panels of a wall and every tile keeps its own UVs. Removing the top 10 cm row of a
1.10 m module gives the 1.00 m field. Cap and vertical bullnose are the FEEDBACK-ROOM-03 pink 18 mm quarter-round stock,
rotated and plane-cropped the same way (no stretch). Decorative, no collision.
Run after rev02_05b.
"""
import json, os, unreal
G = unreal
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
CONTRACT = os.path.join(ROOT, 'docs/03 Art & Audio/Apartment Design/layout-revision-02/feedback/FIX-007/placement-contract.json')
EAL = unreal.EditorAssetLibrary
A = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
DST = '/Game/ICanFixHim/Environment/Rev02/BA_Tile07/'
FOLDER = 'Redesign/Wall Finishes/Bath'
MOD = unreal.load_asset('/Game/ICanFixHim/Environment/Redesign/BA_Tile/BA_Tile_1m_Module')
tt = json.load(open(CONTRACT))['tile_treatment']
# User feedback (crown intersecting the full-height tile): the ARC-TRIM crown is z 2.65-2.75 at the wall face, so
# full-height fields (and the vertical bullnose) stop at the crown's underside; the crown then sits on plaster.
CROWN_UNDERSIDE = 265.0

# Wall frames: actor location/yaw so local +X runs along the wall from one end and local +Y faces the room.
FRAME = {'N': ((486, 566, 0), 0, lambda x, y: x - 486), 'S': ((784, 949, 0), 180, lambda x, y: 784 - x),
         'W': ((486, 949, 0), -90, lambda x, y: 949 - y), 'E': ((784, 566, 0), 90, lambda x, y: y - 566)}

def to_dm(sm):
    dm = unreal.DynamicMesh()
    G.GeometryScript_AssetUtils.copy_mesh_from_static_mesh(sm, dm, G.GeometryScriptCopyMeshFromAssetOptions(), G.GeometryScriptMeshReadLOD())
    return dm
MOD_DM = to_dm(MOD)
CUT = G.GeometryScriptMeshPlaneCutOptions(); CUT.set_editor_property('fill_holes', True)

def crop(dm, u0, u1, z0, z1):
    # a plane cut removes the side the frame's +Z points to
    for frame in (unreal.Transform(unreal.Vector(u1, 0, 0), unreal.Rotator(pitch=-90, yaw=0, roll=0)),
                  unreal.Transform(unreal.Vector(u0, 0, 0), unreal.Rotator(pitch=90, yaw=0, roll=0)),
                  unreal.Transform(unreal.Vector(0, 0, z1), unreal.Rotator(0, 0, 0)),
                  unreal.Transform(unreal.Vector(0, 0, z0), unreal.Rotator(pitch=0, yaw=0, roll=180))):
        G.GeometryScript_MeshBooleans.apply_mesh_plane_cut(dm, frame, CUT)

def field(u0, u1, z0, z1):
    dm = unreal.DynamicMesh()
    i, row = int(u0 // 100), 0
    while i * 100 < u1:
        z = 0
        while z < z1:
            if z + 110 > z0: G.GeometryScript_MeshEdits.append_mesh(dm, MOD_DM, unreal.Transform(unreal.Vector(i * 100, 0, z)))
            z += 110
        i += 1
    crop(dm, u0, u1, z0, z1)
    return dm

def pink_cap_run(u0, u1, z):
    """FEEDBACK-ROOM-03 pink bullnose laid along the wall on the field top: its length (local Z) runs along +u, its
    backs sit on the wall face (local X=0 -> wall plane) and on the tile top (local Y=0 -> z), so the 18 mm quarter
    round starts flush with the 18 mm tile face and rolls back onto the plaster."""
    dm = unreal.DynamicMesh(); i = int(u0 // 100)
    rot = unreal.MathLibrary.make_rot_from_xz(unreal.Vector(0, 1, 0), unreal.Vector(1, 0, 0))
    while i * 100 < u1:
        G.GeometryScript_MeshEdits.append_mesh(dm, PINK_DM, unreal.Transform(unreal.Vector(i * 100, 0, z), rot)); i += 1
    crop(dm, u0, u1, z - 0.5, z + PINK_R + 0.5)
    return dm

def pink_bullnose(u_edge, toward, z0, z1):
    """Vertical pink bullnose against the exposed end face (u = u_edge) of a full-height field, rolling from the tile
    face back to the wall on the ordinary-field side (toward = +1 or -1 in u), z0..z1."""
    dm = unreal.DynamicMesh(); z = z0
    if toward > 0: rot, dz = unreal.Rotator(0, 0, 0), 0.0           # local X -> +u, Y -> wall normal, Z -> up
    else: rot, dz = unreal.MathLibrary.make_rot_from_xz(unreal.Vector(-1, 0, 0), unreal.Vector(0, 0, -1)), 100.0
    while z < z1:
        G.GeometryScript_MeshEdits.append_mesh(dm, PINK_DM, unreal.Transform(unreal.Vector(u_edge, 0, z + dz), rot)); z += 100
    lo, hi = sorted((u_edge, u_edge + toward * PINK_R))
    crop(dm, lo - 0.5, hi + 0.5, z0, z1)
    return dm

def bake(dm, name, src, mats=None):
    path = DST + name
    if mats: names = [unreal.Name(n) for n, _ in mats]; mats = [m for _, m in mats]
    else: mats = [s.material_interface for s in src.static_materials]; names = [s.material_slot_name for s in src.static_materials]
    if EAL.does_asset_exist(path):
        sm = EAL.load_asset(path)
    else:
        o = G.GeometryScriptCreateNewStaticMeshAssetOptions(); o.set_editor_property('enable_collision', False)
        sm, _ = G.GeometryScript_NewAssetUtils.create_new_static_mesh_asset_from_mesh(dm, path, o)
    co = G.GeometryScriptCopyMeshToAssetOptions()
    co.set_editor_property('replace_materials', True); co.set_editor_property('new_materials', mats)
    co.set_editor_property('new_material_slot_names', names)
    G.GeometryScript_AssetUtils.copy_mesh_to_static_mesh(dm, sm, co, G.GeometryScriptMeshWriteLOD())
    assert EAL.save_loaded_asset(sm, False), path
    return sm

def place(sm, wall, label):
    loc, yaw, _ = FRAME[wall]
    a = A.spawn_actor_from_object(sm, unreal.Vector(*loc), unreal.Rotator(0, 0, yaw))
    a.set_actor_label(label); a.set_folder_path(FOLDER)
    c = a.static_mesh_component; c.set_collision_profile_name('NoCollision')
    for i, s in enumerate(sm.static_materials): c.set_material(i, s.material_interface)
    return a

# retire the old stretched modules, caps and extensions (crown, tub, damage overlay untouched)
old = [a for a in A.get_all_level_actors() if a.get_actor_label().startswith(('Tile_BA_', 'Tile07_BA_'))]   # re-runnable
for a in old: A.destroy_actor(a)

def urange(wall, span):
    f = FRAME[wall][2]; a, b = span[0] * 100, span[1] * 100
    if wall in ('N', 'S'): u = sorted((f(a, 0), f(b, 0)))
    else: u = sorted((f(0, a), f(0, b)))
    return u

out = []
for n, p in enumerate(tt['panels']):
    w = p['wall']; u0, u1 = urange(w, p['span']); z0, z1 = p['z'][0] * 100, min(p['z'][1] * 100, CROWN_UNDERSIDE)
    name = 'SM_BA_Tile07_%s_%d' % (w, n)
    a = place(bake(field(u0, u1, z0, z1), name, MOD), w, 'Tile07_BA_%s_%d' % (w, n))
    o, e = a.get_actor_bounds(False); out.append('%s u %.1f-%.1f z %.0f-%.0f -> x%.1f-%.1f y%.1f-%.1f z%.1f-%.1f' % (name, u0, u1, z0, z1, o.x-e.x, o.x+e.x, o.y-e.y, o.y+e.y, o.z-e.z, o.z+e.z))
# FEEDBACK-ROOM-03 (user: plum cap / bullnose read wrong): the 50 mm plum BA_Tile_Cap strips are retired for the pink
# glazed 18 mm quarter-round BA_PinkBullnose_1m (radius = the 18 mm tile projection, so it is flush with the tile face).
# Ordinary-field caps sit on the 1.00 m field top, ending at the door casing and at the full-height field's end face
# (y 8.55); the vertical bullnose closes that exposed end face from the field top up to the crown underside.
PINK = unreal.load_asset('/Game/ICanFixHim/Environment/Rev02/Room03/BA_PinkBullnose_1m')
PINK_DM, PINK_R = to_dm(PINK), 1.8
PINK_MAT = [('Pink_Glazed_Bullnose', EAL.load_asset('/Game/ICanFixHim/Environment/Rev02/Materials/MI_Rev02_PinkGlaze_02'))]
for k, (w, span) in enumerate([('N', (4.86, 6.25)), ('N', (7.30, 7.84)), ('W', (5.66, 8.55)), ('E', (5.66, 8.55))]):
    u0, u1 = urange(w, span)
    a = place(bake(pink_cap_run(u0, u1, 100), 'SM_BA_Tile07_Cap_%s_%d' % (w, k), PINK, PINK_MAT), w, 'Tile07_BA_Cap_%s_%d' % (w, k))
    o, e = a.get_actor_bounds(False); out.append('pink cap %s_%d x%.1f-%.1f y%.1f-%.1f z%.1f-%.1f' % (w, k, o.x-e.x, o.x+e.x, o.y-e.y, o.y+e.y, o.z-e.z, o.z+e.z))
# W wall: full-height field is u 0..94 (y 9.49..8.55), ordinary field beyond -> bullnose rolls toward +u;
# E wall: ordinary field u 0..289, full-height beyond -> rolls toward -u.
for w, (u_edge, toward) in (('W', (urange('W', (8.55, 8.55))[0], 1)), ('E', (urange('E', (8.55, 8.55))[0], -1))):
    a = place(bake(pink_bullnose(u_edge, toward, 100, CROWN_UNDERSIDE), 'SM_BA_Tile07_Bullnose_' + w, PINK, PINK_MAT), w, 'Tile07_BA_Bullnose_' + w)
    o, e = a.get_actor_bounds(False); out.append('pink bullnose %s x%.1f-%.1f y%.1f-%.1f z%.1f-%.1f' % (w, o.x-e.x, o.x+e.x, o.y-e.y, o.y+e.y, o.z-e.z, o.z+e.z))
assert L.save_all_dirty_levels()
unreal.log('[Rev02 bath tile] removed %d old tile actors; built:\n%s' % (len(old), '\n'.join(out)))
