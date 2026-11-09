"""Capture eye-height review views via SceneCapture2D. NOTE: scene captures do NOT render Lumen GI
in this project (verified 2026-11-08); use Tools/capture_redesign_viewport.py for lighting review."""
import math, os, unreal
OUT = globals().get('OUT') or os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'Saved/ApartmentProgress/review'))
SHOTS = [('living', (470, 340, 160), (120, 0, 140)), ('kitchen', (640, 340, 160), (1120, 20, 120)),
         ('hall', (1150, 470, 160), (0, 470, 140)), ('bedroom', (120, 910, 160), (474, 566, 110)),
         ('bath', (750, 600, 160), (520, 949, 100)), ('office', (830, 600, 160), (1194, 949, 110)),
         ('bedroom_window', (240, 600, 160), (410, 955, 130)), ('kitchen_window', (855, 330, 160), (855, 0, 150)),
         ('living_tv', (180, 120, 150), (544, 200, 80)), ('living_fuse', (330, 120, 150), (312, 380, 140)),
         ('hall_west', (950, 470, 160), (0, 470, 100)), ('office_east', (880, 700, 160), (1194, 780, 80)),
         ('living_window', (330, 300, 150), (180, 0, 150)), ('bedroom_closet', (300, 850, 160), (60, 700, 120)),
         ('closet_inside', (90, 695, 165), (90, 566, 180)), ('hall_east', (300, 470, 160), (1200, 420, 110)),
         ('office_closet', (1000, 900, 160), (1138, 680, 110)),
         ('living_wide', (520, 345, 150), (120, 90, 90)),
         ('bath_west', (720, 760, 160), (486, 727, 140)), ('kitchen_pantry', (980, 260, 150), (1126, 62, 100)),
         ('hall_endcab', (130, 470, 140), (29, 469, 40)), ('hall_console', (252, 530, 150), (252, 399, 60)), ('hall_coat', (1100, 520, 160), (1135, 380, 110)),
         ('office_west', (1000, 700, 150), (810, 634, 40)), ('office_desk', (1058, 760, 150), (1058, 905, 60)), ('sky_sun', (600, 477.5, 700), (844, -272, 1316)), ('sky_window', (215, 120, 110), (215, -300, 420)), ('bath_north', (660, 820, 160), (700, 566, 130)),
         ('kitchen_table', (895, 340, 150), (895, 200, 70)), ('hall_entry', (980, 470, 150), (1110, 545, 20)), ('bath_toilet', (600, 700, 165), (740, 800, 50)),
         ('bedroom_dresser', (240, 760, 160), (450, 772, 60)), ('closet_doors', (300, 900, 165), (90, 710, 100)), ('bedroom_north', (330, 880, 160), (230, 566, 140)),
         ('hall_north', (560, 530, 160), (760, 386, 150)), ('living_west', (430, 230, 150), (6, 120, 110)), ('bedroom_wide', (440, 620, 155), (150, 940, 80)),
         ('kitchen_upper', (900, 260, 165), (975, 30, 175)), ('kitchen_oven', (780, 250, 130), (690, 60, 40)),
         ('pantry_front', (930, 62, 150), (1126, 62, 100)),
         ('door_bath_hall', (560, 470, 165), (690, 560, 150)), ('door_bath_close', (660, 520, 120), (636, 560, 120)),
         ('living_sofa', (420, 200, 160), (60, 180, 60)),
         ('door_coat_closet', (1000, 470, 160), (1135, 380, 150)), ('door_entry', (1000, 470, 160), (1200, 442, 140))]
only = globals().get('ONLY')
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
A = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for name, eye, tgt in SHOTS:
    if only and name not in only: continue
    dx, dy, dz = (t - e for t, e in zip(tgt, eye))
    yaw = math.degrees(math.atan2(dy, dx)); pitch = math.degrees(math.atan2(dz, math.hypot(dx, dy)))
    a = A.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector(*eye), unreal.Rotator(roll=0, pitch=pitch, yaw=yaw), transient=True)
    c = a.get_component_by_class(unreal.SceneCaptureComponent2D)
    rt = unreal.RenderingLibrary.create_render_target2d(world, 1200, 800, unreal.TextureRenderTargetFormat.RTF_RGBA8)
    c.texture_target = rt; c.fov_angle = 90
    c.capture_source = unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR; c.capture_every_frame = False
    c.capture_scene()
    unreal.RenderingLibrary.export_render_target(world, rt, OUT, name + '.png')
    A.destroy_actor(a)
