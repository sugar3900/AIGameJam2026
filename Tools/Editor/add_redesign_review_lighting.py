"""Add temporary warm lighting and a start to the redesign review map."""
import unreal
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
if not levels.load_level('/Game/ICanFixHim/Maps/L_Apartment_Redesign_Blockout'):
    raise RuntimeError('Cannot load blockout')
for a in actors.get_all_level_actors():
    if a.get_actor_label().startswith('ReviewLight_') or a.get_actor_label() == 'Review_PlayerStart':
        actors.destroy_actor(a)
for name, x, y, intensity, radius in [
    ('Living',275,190,2400,450), ('Kitchen',875,190,2600,480),
    ('HallWest',300,470,1200,370), ('HallEast',900,470,1200,370),
    ('Bedroom',265,755,2000,400), ('Bathroom',635,755,1700,350),
    ('Office',995,755,1800,350), ('Closet',90,630,400,160)]:
    a = actors.spawn_actor_from_class(unreal.PointLight, unreal.Vector(x,y,215))
    a.set_actor_label('ReviewLight_'+name)
    a.set_folder_path('Redesign/Temporary Lighting')
    c = a.get_component_by_class(unreal.PointLightComponent)
    c.set_editor_property('intensity_units', unreal.LightUnits.LUMENS)
    c.set_editor_property('intensity', intensity * 0.7)
    c.set_editor_property('light_color', unreal.Color(255, 232, 202, 255))
    c.set_editor_property('attenuation_radius', radius)
    c.set_editor_property('source_radius', 8.0)
a = actors.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(920,470,100))
a.set_actor_label('Review_PlayerStart')
a.set_folder_path('Redesign/Temporary')
if not levels.save_current_level():
    raise RuntimeError('Could not save blockout')
