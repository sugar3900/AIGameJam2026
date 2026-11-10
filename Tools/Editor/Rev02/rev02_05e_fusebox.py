"""Rev02 step 5e (FIX-030): Wyatt's fuse box mostly embedded in the living-room north wall.

Audited datums (FIX-004 site, world cm): north wall plaster face y 6, exterior face y -6; LV-FUSE-01 case outline
x 1083.2-1128.2, z 152.2-210.2, case back on its origin, front 12.8 cm proud; external wire stubs (part of the Shell
mesh, same slots as the internal wiring) at y 10.0-14.3 above z 210.2 and below z 152.2.

1. Recess RECESS cm: the case, both door meshes, the FuseBox_Door hinge pivot, the damaged/repaired wires, Wyatt's
   inspect proxy and glow light move rigidly toward the wall. Malady root, hunk spawn, talk spot, dialogue camera,
   tags and repair identity are untouched. The external stubs end up inside the wall solid, behind the plaster face.
2. Niche: an instance-only copy of the wall module (the shared ARC_Living_SolidWall_2m is untouched) with a pocket
   boolean-subtracted 0.5 cm inside the case outline, so no plaster covers the open interior and the plaster edge
   hides inside the case walls. The North_8_0 collision cubes are split around the case (the case's own complex
   collision fills the niche), so clicks keep the old trace order.
3. Soot: two procedural feathered charcoal decals (M_Rev02_FuseSoot, rev02_02b) above and below the case where the
   wires leave it, RepairDamage-tagged and attached to Malady_FuseBox so repair hides them. The case, door and wires
   do not receive decals.
Re-runnable: the recess is computed from the case's current back face, the niche asset is rebuilt from the original
module, collision pieces are re-shaped and the decals respawned. Run after rev02_05d.
"""
import unreal
G = unreal
EAL = unreal.EditorAssetLibrary
A = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
L = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
R2 = '/Game/ICanFixHim/Environment/Rev02/'
WALL_FACE, RECESS = 6.0, 10.0
CASE = (1083.2, 1128.2, 152.2, 210.2)                  # x0, x1, z0, z1 of the case outline
acts = {a.get_actor_label(): a for a in A.get_all_level_actors()}
def actor(label):
    assert label in acts, label
    return acts[label]

# ---------------- 1. rigid recess ----------------
shell = actor('Art_LV_Fuse_Shell')
o, e = shell.get_actor_bounds(False, True)
dy = (WALL_FACE - RECESS) - (o.y - e.y)
mal = actor('Malady_FuseBox')
if abs(dy) > 0.05:
    for l in ('Art_LV_Fuse_Shell', 'Art_LV_Fuse_Door', 'FuseBox_Door', 'Art_LV_Fuse_Wire_Damaged', 'Art_LV_Fuse_Wire_Repaired'):
        a = actor(l); a.modify(); a.set_actor_location(a.get_actor_location() + unreal.Vector(0, dy, 0), False, True)
    mal.modify()
    for cn in ('body', 'glow_light'):
        c = mal.get_editor_property(cn); c.modify(); c.set_world_location(c.get_world_location() + unreal.Vector(0, dy, 0), False, False)
# LV-FUSE-02 (FIX-030 source): replaces only the shell mesh, same origin; external stubs/clamps are gone from source.
# Slots per its README: olive paint and brass keep LV-FUSE-01's existing materials, the aged interior slots get local
# MI_Fuse02_* instances, legacy Wire_* slots (no visible polygons) keep the old materials. Door and repair wires stay.
NEW_SHELL = R2 + 'LV_Fuse02/LV_Fuse02_Shell'
if EAL.does_asset_exist(NEW_SHELL):
    old_mats = {str(x.material_slot_name): x.material_interface for x in
                EAL.load_asset('/Game/ICanFixHim/Environment/Redesign/LV_FUSE/LV_FUSE_01_Shell').static_materials}
    new = EAL.load_asset(NEW_SHELL); sc = shell.static_mesh_component; shell.modify(); sc.set_static_mesh(new)
    for i, x in enumerate(new.static_materials):
        n = str(x.material_slot_name); mi = R2 + 'Materials/MI_Fuse02_' + n
        sc.set_material(i, EAL.load_asset(mi) if EAL.does_asset_exist(mi) else old_mats[n])
# The inspect proxy's inflated hover shell poked ~1 cm past the case walls; recessed, that read as a glowing slit
# around the case. Kept inside the case walls (interior opening x 1085.8-1125.6): 35 x 52 cm instead of 40 x 56.
pb = mal.get_editor_property('body'); pb.modify(); pb.set_relative_scale3d(unreal.Vector(0.008, 0.35, 0.52))
# Wyatt's breathing-glow overlay renders on this proxy; as an 8 cm box its side faces read as pink vertical strips
# through the open case. A 0.8 cm slab just behind the door plane (y 7.4-8.2: in front of the fuse fronts at <= 7.2,
# behind the gasket/door) keeps the click target and leaves only a soft face glow over the opening.
_pl = pb.get_world_location(); pb.set_world_location(unreal.Vector(_pl.x, 7.8, _pl.z), False, False)
# Its inverted-hull hover shell would be a flat unlit plane in front of the fuses (a white-out on hover); like
# Malcolm's mold proxy (FIX-001 option a) this invisible proxy skips the shell. Trace, click, prompt, glow unchanged.
mal.set_editor_property('hover_outline', False)
for l in ('Art_LV_Fuse_Shell', 'Art_LV_Fuse_Door', 'Art_LV_Fuse_Wire_Damaged', 'Art_LV_Fuse_Wire_Repaired'):
    actor(l).static_mesh_component.set_editor_property('receives_decals', False)
actor('FuseBox_Door').get_editor_property('body').set_editor_property('receives_decals', False)
# The mended wire (RepairFixed) is shown by AFixHimMalady::RefreshRepairState only once repaired (hidden in game until
# then); its component itself must be visible for that to work (it had been left invisible).
_wr = actor('Art_LV_Fuse_Wire_Repaired'); _wr.modify(); _wr.set_actor_hidden_in_game(True); _wr.static_mesh_component.set_visibility(True)

# ---------------- 2. niche in an instance copy of the wall module + collision split ----------------
wall = actor('Kit_LV_N_Solid_E'); wc = wall.static_mesh_component
SRC = EAL.load_asset('/Game/ICanFixHim/Environment/Redesign/ARC_LivingWall/ARC_Living_SolidWall_2m')
over = [wc.get_material(i) for i in range(len(SRC.static_materials))]
dm = unreal.DynamicMesh()
G.GeometryScript_AssetUtils.copy_mesh_from_static_mesh(SRC, dm, G.GeometryScriptCopyMeshFromAssetOptions(), G.GeometryScriptMeshReadLOD())
tool = unreal.DynamicMesh()
wl = wall.get_actor_location(); assert abs(wall.get_actor_rotation().yaw) < 0.1
x0, x1, z0, z1 = CASE[0] + 0.5, CASE[1] - 0.5, CASE[2] + 0.5, CASE[3] - 0.5
y0, y1 = WALL_FACE - RECESS - 0.2, WALL_FACE + 3.0
G.GeometryScript_Primitives.append_box(
    tool, G.GeometryScriptPrimitiveOptions(),
    unreal.Transform(unreal.Vector((x0 + x1) / 2 - wl.x, (y0 + y1) / 2 - wl.y, (z0 + z1) / 2 - wl.z)),
    x1 - x0, y1 - y0, z1 - z0, 0, 0, 0, G.GeometryScriptPrimitiveOriginMode.CENTER)
G.GeometryScript_MeshBooleans.apply_mesh_boolean(dm, unreal.Transform(), tool, unreal.Transform(),
                                                 G.GeometryScriptBooleanOperation.SUBTRACT, G.GeometryScriptMeshBooleanOptions())
NICHE = R2 + 'FuseNiche/SM_Kit_LV_N_Solid_E_FuseNiche'
if EAL.does_asset_exist(NICHE):
    sm = EAL.load_asset(NICHE)
else:
    opt = G.GeometryScriptCreateNewStaticMeshAssetOptions(); opt.set_editor_property('enable_collision', False)
    sm, _ = G.GeometryScript_NewAssetUtils.create_new_static_mesh_asset_from_mesh(dm, NICHE, opt)
co = G.GeometryScriptCopyMeshToAssetOptions()
co.set_editor_property('replace_materials', True)
co.set_editor_property('new_materials', [s.material_interface for s in SRC.static_materials])
co.set_editor_property('new_material_slot_names', [s.material_slot_name for s in SRC.static_materials])
G.GeometryScript_AssetUtils.copy_mesh_to_static_mesh(dm, sm, co, G.GeometryScriptMeshWriteLOD())
assert EAL.save_loaded_asset(sm, False), NICHE
wall.modify(); wc.set_static_mesh(sm)
for i, m in enumerate(over): wc.set_material(i, m)

PIECES = {'L': (1075.0, CASE[0], 0.0, 275.0), 'R': (CASE[1], 1200.0, 0.0, 275.0),
          'B': (CASE[0], CASE[1], 0.0, CASE[2]), 'T': (CASE[0], CASE[1], CASE[3], 275.0)}
for side, (ya, yb) in (('P', (0.0, 6.0)), ('N', (-6.0, 0.0))):
    base = 'North_8_0_%s_CollisionOnly' % side
    have = {k: acts.get(base + '_' + k) for k in PIECES}
    if base in acts:
        have['L'] = acts[base]; have['L'].set_actor_label(base + '_L')
    tmpl = next(a for a in have.values() if a)
    for k in PIECES:
        if not have[k]:
            have[k] = A.duplicate_actor(tmpl); have[k].set_actor_label(base + '_' + k)
        px0, px1, pz0, pz1 = PIECES[k]; a = have[k]; a.modify()
        a.set_actor_location(unreal.Vector((px0 + px1) / 2, (ya + yb) / 2, (pz0 + pz1) / 2), False, True)
        a.set_actor_scale3d(unreal.Vector((px1 - px0) / 100, (yb - ya) / 100, (pz1 - pz0) / 100))

# ---------------- 3. soot decals (gameplay level, RepairDamage, attached to Wyatt's malady) ----------------
for l in ('Art_LV_Fuse_Soot_Above', 'Art_LV_Fuse_Soot_Below'):
    if l in acts: A.destroy_actor(acts.pop(l))
tags = [unreal.Name('RepairDamage'), unreal.Name('wyatt')]
MATS = R2 + 'Materials/'
assert L.set_current_level_by_name('L_Apartment_Rev02_Gameplay')
for l, mi, zc, hw, hz in (('Art_LV_Fuse_Soot_Above', 'MI_Rev02_FuseSoot_Above', CASE[3] + 17.0, 30.0, 18.0),
                          ('Art_LV_Fuse_Soot_Below', 'MI_Rev02_FuseSoot_Below', CASE[2] - 12.0, 24.0, 13.0)):
    d = A.spawn_actor_from_class(unreal.DecalActor, unreal.Vector(1106, WALL_FACE, zc), unreal.Rotator(roll=0, pitch=0, yaw=-90))
    d.set_actor_label(l); d.set_folder_path('Gameplay/Damage'); d.tags = tags
    # yaw -90: the decal projects along -Y into the wall; local Y spans world x, local Z world z
    d.decal.set_decal_material(EAL.load_asset(MATS + mi))
    d.decal.set_editor_property('decal_size', unreal.Vector(3.0, hw, hz))
    d.decal.set_editor_property('sort_order', 1)
    d.attach_to_actor(mal, '', unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, False)
assert L.set_current_level_by_name('L_Apartment_Rev02')
assert L.save_all_dirty_levels()
o, e = shell.get_actor_bounds(False, True)
unreal.log('[Rev02 fusebox] recess dy %.2f -> case y %.1f-%.1f; niche %s; collision split; soot decals placed'
           % (dy, o.y - e.y, o.y + e.y, NICHE))
