"""Import the KI-FRIDGE-01 / KI-RANGE-01 doors (assembly space, same origin as their bodies) and
place them closed in the redesign map. Re-runnable: existing door actors (which may be hidden
gameplay body sources) are updated in place."""
import os, unreal
exec(open(os.path.join(os.path.dirname(__file__), 'import_redesign_kitchen_bodies.py')).read().split("if __name__ == '__main__':")[0])
assert L.load_level('/Game/ICanFixHim/Maps/L_Apartment_Redesign_Blockout')
for name, src, part, pos in [('Fridge', 'KI-FRIDGE-01/models', 'KI_FRIDGE_DOOR', (599.5, 47, 0)),
                             ('Range', 'KI-RANGE-01/model', 'KI_RANGE_Door', (687.5, 47, 0))]:
    m = import_mesh(src, part, '/Game/ICanFixHim/Environment/Redesign/KI_' + name, False)
    place('Art_KI_' + name + '_Door', m, pos, 'Redesign/Imported Art/Kitchen', collision=False)
    unreal.log('[Kitchen] door %s %s' % (name, m.get_bounds().box_extent))
assert L.save_current_level()
