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
         ('door_coat_closet', (1000, 470, 160), (1135, 380, 150)), ('door_entry', (1000, 470, 160), (1200, 442, 140)),
         # Rev02 (L_Apartment_Rev02) review cameras
         ('r2_kitchen', (420, 330, 165), (150, 40, 100)), ('r2_kitchen_west', (330, 200, 165), (30, 285, 100)),
         ('r2_living', (560, 330, 165), (1000, 150, 90)), ('r2_dining', (1100, 330, 170), (600, 220, 80)),
         ('r2_entry', (880, 470, 165), (1195, 400, 120)), ('r2_hall_west', (900, 470, 165), (230, 470, 110)),
         ('r2_closet', (110, 760, 160), (110, 450, 130)), ('r2_bedroom', (420, 690, 170), (130, 860, 70)),
         ('r2_office', (850, 900, 170), (1130, 650, 100)), ('r2_coat', (1040, 450, 160), (1138, 560, 110)),
         ('r2_bedroom_west', (300, 760, 160), (15, 720, 100)), ('r2_bedroom_east', (170, 780, 165), (470, 860, 140)),
         ('r2_office_alt', (1160, 780, 170), (860, 860, 80)), ('r2_office_east', (900, 780, 165), (1195, 770, 150)),
         ('r2_kitchen_east', (180, 230, 165), (470, 100, 140)), ('r2_bath_north', (640, 900, 165), (620, 566, 140)),
         ('r2_bath_west', (720, 760, 165), (486, 760, 130)), ('r2_hall_end', (620, 470, 165), (226, 470, 110)),
         ('r2_closet_inside', (200, 520, 160), (60, 386, 140)), ('r2_closet_open', (300, 760, 160), (110, 520, 120)),
         ('r2_kitchen_open', (330, 290, 160), (250, 60, 70)),
         ('r2_title_code', (600, 430, 185), (345, 283, 128)), ('r2_title_map', (600, 500, 175), (980, 180, 95)),
         # Feedback-batch review cameras (FIX-001..020)
         ('f_puddle_top', (207, 77, 170), (207, 76, 0)), ('f_sink', (215, 210, 95), (205, 50, 25)),
         ('f_mold_door', (110, 620, 160), (182, 389, 216)), ('f_closet_in', (110, 520, 165), (190, 395, 215)),
         ('f_closet_shelves', (110, 545, 150), (110, 390, 160)), ('f_fuse', (1010, 250, 160), (1105, 6, 180)),
         ('f_coat', (1050, 330, 160), (1194, 330, 130)), ('f_hall_art', (515, 470, 160), (515, 554, 157)),
         ('f_entry_door', (1080, 452, 150), (1196, 480, 105)), ('f_sofa', (1100, 230, 150), (850, 220, 50)),
         ('f_armchair', (1080, 250, 140), (977, 94, 45)), ('f_plant', (1010, 190, 150), (1105, 50, 75)),
         ('f_office_wainscot', (900, 860, 160), (1060, 640, 60)), ('f_office_north', (900, 760, 150), (892, 566, 70)),
         ('f_sconce', (453, 470, 180), (453, 392, 195)), ('f_runner', (720, 470, 160), (240, 470, 0)),
         ('f_chairs', (652, 380, 150), (652, 250, 60)), ('f_slippers', (1100, 400, 130), (1170, 362, 0)),
         ('f_kitchen_switch', (330, 300, 150), (474, 364, 114)),
         ('f_bath_basin', (640, 790, 160), (784, 792, 115)), ('f_bath_toilet', (650, 720, 160), (555, 590, 60)),
         ('f_bath_tub', (650, 760, 165), (510, 925, 105)), ('f_bath_linen', (660, 760, 160), (745, 900, 90)),
         ('f_bath_sw', (700, 860, 170), (486, 949, 200)), ('f_bath_roll', (620, 650, 120), (488, 613, 72)),
         ('f_bath_door', (640, 860, 165), (680, 566, 120)), ('f_br_window', (300, 700, 160), (385, 955, 160)),
         ('f_br_shelf', (330, 860, 175), (474, 902, 185)), ('f_of_window', (1040, 760, 160), (1040, 955, 150)),
         ('f_of_lamp', (1000, 780, 165), (1015, 905, 85)), ('f_of_plant', (900, 693, 175), (800, 693, 190)),
         ('f_ki_window', (330, 250, 160), (215, 0, 160)),
         ('f_puddle_graze_e', (330, 140, 20), (205, 88, 0)), ('f_puddle_graze_w', (85, 160, 20), (205, 88, 0)),
         ('f_hall_058_wide', (515, 400, 150), (515, 554, 150)), ('f_chair_side', (760, 141, 105), (650, 141, 70)),
         ('f_plant_contact', (1105, 120, 60), (1105, 50, 52)), ('f_geranium_wall', (840, 640, 205), (800, 690, 185)),
         ('f_portal_kitchen', (330, 290, 160), (474, 295, 120)), ('f_portal_living', (660, 300, 160), (486, 295, 120)),
         ('f_junction_hall', (600, 480, 170), (486, 386, 220)), ('f_portal_switch', (400, 330, 130), (474, 366, 114)),
         ('f_side_table', (900, 300, 110), (848, 358, 35)), ('f_toilet', (555, 700, 140), (555, 600, 50)),
         ('f_toilet_bowl', (555, 660, 175), (555, 595, 27)),
         ('f_nightstand', (190, 840, 110), (122, 905, 40)), ('f_corner_hall_close', (520, 430, 60), (486, 386, 8)),
         ('f_corner_crown_close', (530, 430, 230), (486, 386, 268)),
         ('f_corner_out_hall', (540, 440, 45), (487, 387, 6)), ('f_corner_out_living', (540, 330, 45), (487, 387, 6)),
         ('f_faucet_front', (215, 160, 150), (215, 50, 118)), ('f_faucet_side', (300, 90, 135), (215, 45, 115))]
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
