"""Build a separate A+ apartment shell for layout review, without replacing gameplay.

Run with this checkout open in Unreal: python3 Tools/run_in_editor.py
Tools/Editor/build_redesign_blockout.py. Recreates L_Apartment_Redesign_Blockout.
Coordinates and placeholder footprints are read from the design wiki JSON.
"""
import json
import os
import unreal

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
PLAN = os.path.join(ROOT, 'docs/03 Art & Audio/Apartment Design/A-plus-candidate.json')
MAP = '/Game/ICanFixHim/Maps/L_Apartment_Redesign_Blockout'
with open(PLAN) as f:
    plan = json.load(f)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
levels.new_level(MAP)
cube = unreal.load_asset('/Engine/BasicShapes/Cube')

def box(name, center, size, folder):
    a = actors.spawn_actor_from_object(cube, unreal.Vector(*center))
    a.set_actor_label(name)
    a.set_actor_scale3d(unreal.Vector(*(v / 100.0 for v in size)))
    a.set_folder_path(folder)
    return a

def wall(name, axis, fixed, start, end, openings=()):
    # Partition into full-height piers and sill/header sections; no collision
    # is left behind a window or doorway.
    points = sorted(set([start, end] + [v for o in openings for v in o[:2]]))
    for i, (a, b) in enumerate(zip(points, points[1:])):
        opening = next((o for o in openings if a >= o[0] - .001 and b <= o[1] + .001), None)
        spans = [(0, 275)] if opening is None else [(0, opening[2]), (opening[3], 275)]
        for j, (z0, z1) in enumerate(spans):
            if z1 <= z0: continue
            center = ((a+b)/2, fixed, (z0+z1)/2) if axis == 'x' else (fixed, (a+b)/2, (z0+z1)/2)
            size = (b-a, 12, z1-z0) if axis == 'x' else (12, b-a, z1-z0)
            box('%s_%d_%d' % (name, i, j), center, size, 'Redesign/Shell')

def openings(axis, fixed):
    result = []
    for d in plan['swing_doors'] + plan['windows']:
        if d['axis'] != ('h' if axis == 'x' else 'v'): continue
        if abs(100 * d['y' if axis == 'x' else 'x'] - fixed) > .01: continue
        start = 100*d['x' if axis == 'x' else 'y']
        result.append((start, start+100*d['width'], 100*d.get('sill_height', 0), 100*d.get('head_height', 2.1)))
    if axis == 'x' and abs(fixed - 380) < .01:
        result.append ( (1090, 1180, 0, 210) )  # hall-facing coat closet
    return result

for room in plan['rooms']:
    x,y,w,d = [v*100 for v in room['rect']]
    box('Floor_'+room['id'], (x+w/2,y+d/2,-6), (w,d,12), 'Redesign/Floors')
# Single shared partitions avoid overlapping walls.
for name,axis,fixed,start,end in [
    ('North','x',0,0,1200),('South','x',955,0,1200),
    ('West','y',0,0,955),('East','y',1200,0,955),
    ('HallNorth','x',380,0,1200),('HallSouth','x',560,0,1200),
    ('LivingKitchen','y',550,0,380),('BedroomBath','y',480,560,955),
    ('BathOffice','y',790,560,955)]:
    wall(name,axis,fixed,start,end,openings(axis,fixed))
# Closet fronts and sides. Existing exterior and room walls form their backs.
wall('BedroomClosetFront','x',705,0,180,[(45,135,0,210)])
wall('BedroomClosetSide','y',180,560,705)
wall('OfficeClosetFront','x',680,1075,1200,[(1093,1183,0,210)])
wall('OfficeClosetSide','y',1075,560,680)
wall('CoatClosetBack','x',300,1070,1200)
wall('CoatClosetSide','y',1070,300,380)
# Footprint-only stand-ins are deliberately labeled and grouped for replacement.
heights = {'Sofa':85,'TV cabinet':65,'Bookcase':180,'Armchair':85,'Coffee table':45,
           'Fusebox':60,'Fridge':180,'Range':90,'Counter':90,'Sink / leak':90,'Pantry':190,
           'Dining table':75,'Dining chair':90,'Bed':60,'Nightstand':55,'Dresser':100,
           'Tub / crack':60,'Basin':85,'WC':75,'Linen':180,'Daybed':65,'Desk':75,'Chair':90}
for i, obj in enumerate(plan['objects']):
    x,y,w,d = [v*100 for v in obj['rect']]
    h = heights.get(obj['name'], 60)
    z = 150 if obj['name'] == 'Fusebox' else h/2
    box('Placeholder_%02d_%s' % (i,obj['name'].replace('/','_')), (x+w/2,y+d/2,z), (w,d,h), 'Redesign/Placeholders/'+obj['room'])
levels.save_current_level()
unreal.log('[Redesign] Saved layout blockout to '+MAP)
