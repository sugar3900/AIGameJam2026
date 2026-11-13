"""Separate painterly outlet. Metres, Z up, wall datum Y=0, face -Y."""
import bpy, bmesh, math, json, fcntl
from pathlib import Path
from mathutils import Vector

LOCK=open('/tmp/apartment_blender.lock','w');fcntl.flock(LOCK,fcntl.LOCK_EX)
ROOT=Path(__file__).resolve().parents[1]
MODEL,TEX,PRE=(ROOT/x for x in ('model','textures','previews'))
for p in (MODEL,TEX,PRE):p.mkdir(parents=True,exist_ok=True)
DH=ROOT.parent/'PR-DEHUMIDIFIER-01'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.context.preferences.filepaths.save_version=0
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
parts=[]
def material(name,color,rough,metal=0,maps=None):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;m.use_backface_culling=True
    ns,ls=m.node_tree.nodes,m.node_tree.links;p=ns.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
    if maps:
        ts=[]
        for file in maps:
            t=ns.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(TEX/file),check_existing=True);ts.append(t)
        out=ts[0].outputs['Color']
        if len(ts)==2:
            mix=ns.new('ShaderNodeMixRGB');mix.inputs[0].default_value=.52
            ls.new(out,mix.inputs[1]);ls.new(ts[1].outputs['Color'],mix.inputs[2]);out=mix.outputs[0]
        tint=ns.new('ShaderNodeMixRGB');tint.blend_type='MULTIPLY';tint.inputs[0].default_value=1;tint.inputs[2].default_value=(*color,1)
        ls.new(out,tint.inputs[1]);ls.new(tint.outputs[0],p.inputs['Base Color'])
    return m
ivory=material('Outlet_Ivory_Painted',(1.06,1.04,1),.46,maps=['enamel-albedo.png','enamel-brush.png'])
socket=material('Outlet_Aged_Receptacle',(.76,.74,.67),.59,maps=['enamel-albedo.png','enamel-brush.png'])
metal=material('Outlet_Aged_Screw',(1.0,.91,.75),.45,.12,['enamel-albedo.png','enamel-brush.png'])
dark=material('Outlet_Socket_Shadow',(.023,.019,.014),.95)
rubber=material('DH_Rubber',(.035,.029,.024),.82)
def active(o):
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
def box(name,loc,dims,mat=None,r=.001,group=parts):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if r:
        m=o.modifiers.new('Soft edge','BEVEL');m.width=min(r,min(dims)*.44);m.segments=4
        bpy.ops.object.modifier_apply(modifier=m.name)
    if mat:o.data.materials.append(mat)
    if group is not None:group.append(o)
    return o
def cylinder(name,loc,r,depth,mat=None,group=parts):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=r,depth=depth,location=loc,rotation=(math.pi/2,0,0))
    o=bpy.context.object;o.name=name;bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    if mat:o.data.materials.append(mat)
    if group is not None:group.append(o)
    return o
def cut(o,c):
    active(o);m=o.modifiers.new('Socket recess','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=c
    bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(c,do_unlink=True)
def socket_face(z):
    hw,hh,clip=.019,.0175,.006
    outline=[(-hw+clip,-hh),(hw-clip,-hh),(hw,-hh+clip),(hw,hh-clip),
             (hw-clip,hh),(-hw+clip,hh),(-hw,hh-clip),(-hw,-hh+clip)]
    verts=[(x,y,h+z) for y in [-.0105,-.0145] for x,h in outline]
    faces=[tuple(reversed(range(8))),tuple(range(8,16))]
    faces += [(i,(i+1)%8,(i+1)%8+8,i+8) for i in range(8)]
    me=bpy.data.meshes.new('Octagonal socket face');me.from_pydata(verts,[],faces);me.update()
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    o=bpy.data.objects.new('Aged octagonal receptacle',me);bpy.context.collection.objects.link(o);me.materials.append(socket);parts.append(o)
    active(o);m=o.modifiers.new('Rounded octagonal corners','BEVEL');m.width=.0012;m.segments=4
    bpy.ops.object.modifier_apply(modifier=m.name)
    return o
def rounded_field(name,width,height,y0,y1,r,mat,z=0):
    outline=[]
    for cx,cz,a in [(width/2-r,height/2-r,0),(-width/2+r,height/2-r,90),(-width/2+r,-height/2+r,180),(width/2-r,-height/2+r,270)]:
        for i in range(9):
            t=math.radians(a+90*i/8);outline.append((cx+r*math.cos(t),z+cz+r*math.sin(t)))
    n=len(outline);vs=[(x,y,h) for y in [y0,y1] for x,h in outline]
    fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update()
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);me.materials.append(mat);parts.append(o);return o
plate=rounded_field('Rounded ivory outlet plate',.070,.115,0,-.0115,.009,ivory)
field=rounded_field('Raised inset plate field',.064,.109,-.0105,-.012,.007,ivory)
for z in [-.022,.022]:
    cap=socket_face(z)
    for part in [plate,field,cap]:
        for x in [-.0085,.0085]:
            cut(part,box('Blade opening',(x,-.006,z+.005),(.0030,.040,.0095),r=.0004,group=None))
        # D-shaped throat: straight bottom/sides and a semicircular upper arch.
        outline=[(-.003,-.0028),(.003,-.0028)]+[(.003*math.cos(math.pi*i/16),.003*math.sin(math.pi*i/16)) for i in range(17)]
        n=len(outline);vs=[(x,y,z-.0075+h) for y in [-.026,.014] for x,h in outline]
        fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
        me=bpy.data.meshes.new('D ground throat');me.from_pydata(vs,[],fs);me.update()
        bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
        ground=bpy.data.objects.new('Ground opening',me);bpy.context.collection.objects.link(ground)
        cut(part,ground)
    box('Socket deep shadow',(0,.005,z),(.035,.002,.033),dark,.0005)
bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,location=(0,-.0123,0))
screw=bpy.context.object;screw.name='Cream domed slotted fixing screw';screw.scale=(.0034,.0020,.0034)
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);screw.data.materials.append(metal);parts.append(screw)
slot=box('Screwdriver slot',(0,-.0141,0),(.00065,.002,.0052),r=.0001,group=None)
slot.rotation_euler.y=math.radians(38);cut(screw,slot)

for o in parts:
    active(o);bm=bmesh.new();bm.from_mesh(o.data)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT')
    for f in o.data.polygons:f.use_smooth=True
    m=o.modifiers.new('Baked normals','WEIGHTED_NORMAL');m.keep_sharp=True;bpy.ops.object.modifier_apply(modifier=m.name)
    scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
copies=[]
for o in parts:
    c=o.copy();c.data=o.data.copy();bpy.context.collection.objects.link(c);copies.append(c)
active(copies[0])
for c in copies:c.select_set(True)
bpy.ops.object.join();combined=bpy.context.object;combined.name='PR_Outlet01'
collision=box('UCX_PR_Outlet01_00',(0,-.00575,0),(.070,.0115,.115),r=0,group=None)
active(combined);collision.select_set(True)
bpy.ops.export_scene.fbx(filepath=str(MODEL/'PR_Outlet01.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,add_leaf_bones=False)
bpy.data.objects.remove(combined,do_unlink=True);collision.hide_render=True;collision.hide_set(True)
anchors={'units':'Blender metres; wall mounting datum Y=0; front -Y; Z up',
         'mount':[0,0,0], 'upper_socket':[0,-.0147,.022], 'lower_socket':[0,-.0147,-.022],
         'plug_mesh':'../PR-DEHUMIDIFIER-01/model/DH_Plug01.fbx','plug_rotation_deg':[0,0,0],
         'insertion_axis':[0,1,0],'cord_exit_relative_to_plug':[0,-.043,0],
         'blade_centers_x':[-.0085,.0085],'blade_center_z_offset':.005,
         'ground_center_z_offset':-.0075,'seating_clearance_m':.0002,
         'interaction_note':'Outlet stays on wall while appliance changes rooms. Occupancy/power and cable are runtime state.'}
(ROOT/'interaction-anchors.json').write_text(json.dumps(anchors,indent=2)+'\n')
for name,loc in [('Mount',anchors['mount']),('UpperSocket',anchors['upper_socket']),('LowerSocket',anchors['lower_socket'])]:
    o=bpy.data.objects.new('Outlet_Anchor_'+name,None);bpy.context.collection.objects.link(o);o.location=loc;o.empty_display_size=.01
for image in bpy.data.images:
    if image.source=='FILE':image.filepath='//../textures/'+Path(image.filepath).name
scene.render.engine='CYCLES';scene.cycles.samples=48
scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=True
scene.world.color=(.25,.25,.25);scene.view_settings.view_transform='AgX'
for loc,power,size in [((-.15,-.3,.3),2.7,.25),((.25,-.1,.1),1.2,.22),((0,.2,.3),2,.2)]:
    bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.size=size
    o.rotation_euler=(Vector((0,0,0))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(.15,-.30,.105));cam=bpy.context.object
cam.rotation_euler=(-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.165;scene.camera=cam
bpy.ops.wm.save_as_mainfile(filepath=str(MODEL/'PR-OUTLET-01.blend'))
scene.render.filepath=str(PRE/'outlet-unplugged.png');bpy.ops.render.render(write_still=True)
bpy.ops.import_scene.fbx(filepath=str(DH/'model'/'DH_Plug01.fbx'))
plug=bpy.context.selected_objects[0];plug.name='Preview_GroundedPlug';plug.location=anchors['lower_socket']
# Imported FBX supplies geometry; restore the authored PBR materials.
plug_metal=material('DH_Aged_Hardware',(.46,.43,.34),.49,.7,['aged-metal.png'])
plug_brown=material('DH_Plug_Bakelite',(.22,.15,.09),.58,0,['aged-metal.png'])
for slot in plug.material_slots:
    slot.material=plug_metal if 'Hardware' in slot.name else plug_brown if 'Bakelite' in slot.name else rubber
curve=bpy.data.curves.new('Preview flexible lead','CURVE');curve.dimensions='3D';curve.bevel_depth=.003;curve.bevel_resolution=3;curve.use_fill_caps=True
s=curve.splines.new('BEZIER');s.bezier_points.add(3)
for p,co in zip(s.bezier_points,[(0,-.0577,-.022),(0,-.072,-.032),(.004,-.075,-.066),(.014,-.080,-.090)]):
    p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
lead=bpy.data.objects.new('Preview cable only',curve);bpy.context.collection.objects.link(lead);lead.data.materials.append(rubber)
cam.data.ortho_scale=.205;cam.location=(.18,-.34,.095)
cam.rotation_euler=(Vector((0,-.02,-.012))-cam.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath=str(PRE/'outlet-plugged.png');bpy.ops.render.render(write_still=True)
for o in parts:o.hide_render=True
lead.hide_render=True;plug.location=(0,0,0)
cam.location=(.075,.11,.075);cam.rotation_euler=(Vector((0,-.01,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.085
scene.render.filepath=str(PRE/'plug-close.png');bpy.ops.render.render(write_still=True)
print('OUTLET_BUILD_COMPLETE')
