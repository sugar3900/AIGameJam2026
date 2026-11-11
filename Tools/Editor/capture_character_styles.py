"""Capture scene-lit styles in actual PIE encounter rooms (UI hidden for review).
Start a disposable PIE session, skip the podcast, then run this script. It changes
only that PIE world. Preserve/restore save files around a disposable new game.
Lead Paint uses an explicitly staged office placement; no gameplay exists yet.
Results: Saved/CharacterStyles/Rooms/*.png and result.txt. Stop PIE afterwards.
"""
def main():
    import math
    import os
    import time
    import unreal

    U = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    world = U.get_game_world()
    assert world, 'Start PIE first'
    pc = unreal.GameplayStatics.get_player_controller(world, 0)
    out = os.path.abspath(os.path.join(unreal.Paths.project_saved_dir(), 'CharacterStyles', 'Rooms'))
    os.makedirs(out, exist_ok=True)
    root = '/Game/ICanFixHim'
    folders = {'tyler': 'PinkTile', 'malcolm': 'BlackMold', 'lukey': 'LeakyPipes',
               'wyatt': 'FaultyWiring', 'leadpaint': 'LeadPaint'}
    names = list(folders)
    styles = ['original', 'illustrated', 'matte']
    masters = {s: unreal.load_asset(root+'/Materials/M_Hunk'+{'original':'','illustrated':'_Illustrated','matte':'_Cel'}[s]) for s in styles}
    hunks = {str(a.hunk_id): a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.FixHimHunk)}
    maladies = {str(a.hunk_id): a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.FixHimMalady)}
    assert pc and unreal.GameplayStatics.get_player_pawn(world, 0), 'PIE player is not ready'
    assert set(names[:-1]) <= hunks.keys() and set(names[:-1]) <= maladies.keys(), 'Expected all four encounter actors'
    assert all(masters.values()), 'Build all three character styles first'
    assert hunks['tyler'].mesh.get_editor_property('skeletal_mesh_asset').get_name() == 'SK_PinkTile', 'Restart PIE before repeating a capture'
    for folder in folders.values():
        for asset in (f'MI_{folder}', f'A_{folder}_Idle'):
            assert unreal.load_asset(f'{root}/Characters/{folder}/{asset}'), 'Missing review asset: ' + asset
    assert 'CharacterStyleCapture' not in map(str, hunks['tyler'].tags), 'Restart PIE before repeating a capture'
    hunks['tyler'].set_editor_property('tags', list(hunks['tyler'].tags) + ['CharacterStyleCapture'])
    # Open the actual bedroom closet doors so Malcolm's encounter sightline is clear.
    for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.FixHimInteractable):
        if a.get_actor_label().startswith('Wardrobe_Door_'):
            a.set_editor_property('auto_close_on_walk_away',False)
            a.set_on(True,True)
    for widget in unreal.WidgetLibrary.get_all_widgets_of_class(world, unreal.UserWidget, False):
        widget.set_visibility(unreal.SlateVisibility.COLLAPSED)
    unreal.GameplayStatics.get_player_pawn(world,0).set_actor_hidden_in_game(True)
    queue = [(n,s) for n in names for s in styles]
    for n,s in queue:
        path = os.path.join(out,n+'_'+s+'.png')
        if os.path.exists(path): os.remove(path)
    state = {'i': 0, 'phase': 'setup', 'since': time.monotonic(), 'mids': []}

    def finish(message):
        unreal.unregister_slate_post_tick_callback(state['handle'])
        with open(os.path.join(out,'result.txt'),'w') as f: f.write(message)
        unreal.log('[Character room review] '+message)

    def tick(delta):
        try:
            elapsed = time.monotonic()-state['since']
            if state['phase'] == 'setup':
                if state['i'] == len(queue):
                    assert all(os.path.isfile(os.path.join(out,n+'_'+s+'.png')) for n,s in queue)
                    finish('PASS: 12 actual-room captures + 3 staged Lead Paint office previews')
                    return
                name, style = queue[state['i']]
                for h in hunks.values(): h.set_actor_hidden_in_game(True)
                h = hunks['tyler' if name == 'leadpaint' else name]
                malady = maladies['tyler' if name == 'leadpaint' else name]
                camera = malady.dialogue_camera
                if name == 'leadpaint':
                    h.mesh.set_skeletal_mesh_asset(unreal.load_asset(root+'/Characters/LeadPaint/SK_LeadPaint'))
                    h.set_actor_location(unreal.Vector(1030,850,93), False, True)
                    h.set_actor_rotation(unreal.Rotator(pitch=0,yaw=-90,roll=0),False)
                    h.set_actor_scale3d(unreal.Vector(1,1,1))
                    camera.set_world_location(unreal.Vector(1030,650,163),False,False)
                    camera.set_world_rotation(unreal.Rotator(pitch=-7,yaw=90,roll=0),False,False)
                    camera.set_field_of_view(65)
                elif name == 'malcolm':
                    # Match FrameCamera after the closet doors have opened. Its
                    # BeginPlay sweep ran while they were closed and pushed it in.
                    head = h.get_actor_location()+unreal.Vector(0,0,62)
                    talk = malady.get_editor_property('talk_spot').get_world_location()
                    dx,dy = head.x-talk.x,head.y-talk.y
                    length = max(math.hypot(dx,dy),0.001)
                    eye = unreal.Vector(talk.x-dx/length*50,talk.y-dy/length*50,
                                        h.get_actor_location().z-92+160)
                    aim = head-unreal.Vector(0,0,30)
                    d = aim-eye
                    camera.set_world_location(eye,False,False)
                    camera.set_world_rotation(unreal.Rotator(pitch=math.degrees(math.atan2(d.z,math.hypot(d.x,d.y))),yaw=math.degrees(math.atan2(d.y,d.x)),roll=0),False,False)
                elif name == 'wyatt':
                    d = camera.get_world_location()-h.get_actor_location()
                    h.set_actor_rotation(unreal.Rotator(pitch=0,yaw=math.degrees(math.atan2(d.y,d.x)),roll=0),False)
                if style == 'original':
                    folder = folders[name]
                    h.mesh.set_animation_mode(unreal.AnimationMode.ANIMATION_BLUEPRINT)
                    h.mesh.set_animation_mode(unreal.AnimationMode.ANIMATION_SINGLE_NODE)
                    h.mesh.play_animation(unreal.load_asset(f'{root}/Characters/{folder}/A_{folder}_Idle'),True)
                    h.mesh.set_position(0.5,False)
                h.mesh.set_editor_property('pause_anims', style != 'original')
                h.set_actor_hidden_in_game(False)
                source = unreal.load_asset(f'{root}/Characters/{folders[name]}/MI_{folders[name]}')
                state['mids'] = []
                for i in range(h.mesh.get_num_materials()):
                    mid = unreal.MaterialLibrary.create_dynamic_material_instance(h, masters[style])
                    # Inherited defaults belong to the selected master, not the active style.
                    mid.copy_parameter_overrides(source)
                    if style != 'original':
                        expected = 0.22 if style == 'illustrated' else 0.0
                        assert abs(mid.get_scalar_parameter_value('StyleNormalStrength')-expected)<0.001, 'Style defaults were overwritten during capture'
                    mid.set_scalar_parameter_value('Dissolve',1)
                    h.mesh.set_material(i,mid)
                    state['mids'].append(mid)
                pc.set_view_target_with_blend(malady,0)
                state['phase']='settle'
                state['since']=time.monotonic()
            elif state['phase']=='settle' and elapsed > (2.5 if queue[state['i']][1] == 'original' else 1.2):
                name,style=queue[state['i']]
                hunks['tyler' if name == 'leadpaint' else name].mesh.set_editor_property('pause_anims',True)
                path=os.path.join(out,name+'_'+style+'.png')
                unreal.SystemLibrary.execute_console_command(world, 'HighResShot 1200x800 filename="'+path+'"')
                state['phase']='capture'
                state['since']=time.monotonic()
            elif state['phase']=='capture' and elapsed>0.8:
                name,style=queue[state['i']]
                if not os.path.isfile(os.path.join(out,name+'_'+style+'.png')):
                    assert elapsed<60,'Screenshot timeout'
                    return
                state['i']+=1
                state['phase']='setup'
        except Exception as exc:
            finish('FAIL: '+repr(exc))

    with open(os.path.join(out,'result.txt'),'w') as f: f.write('RUNNING')
    state['handle']=unreal.register_slate_post_tick_callback(tick)


main()
