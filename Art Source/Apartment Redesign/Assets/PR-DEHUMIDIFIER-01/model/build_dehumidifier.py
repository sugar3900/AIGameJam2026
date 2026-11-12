"""Selected concept B floor dehumidifier. Blender 5.x, --threads 2.

Metres, Z up, front -Y, floor-centred assembly origin. No gameplay changes.
"""
import bpy, bmesh, math, json, fcntl, sys
from pathlib import Path
from mathutils import Vector, Matrix

LOCK = open('/tmp/apartment_blender.lock', 'w')
fcntl.flock(LOCK, fcntl.LOCK_EX)
ROOT = Path(__file__).resolve().parents[1]
MODEL, TEX, PRE = (ROOT / x for x in ('model', 'textures', 'previews'))
for p in (MODEL, TEX, PRE):
    p.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1
scene.render.engine = 'CYCLES'
scene.cycles.samples = 32
scene.cycles.use_denoising = True
scene.render.resolution_x = 1100
scene.render.resolution_y = 1100
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.film_transparent = True
scene.render.image_settings.color_mode = 'RGBA'
scene.view_settings.view_transform = 'AgX'
scene.world.color = (.25, .25, .25)
bpy.context.preferences.filepaths.save_version = 0

materials = []
contracts = []
def material(name, color, rough=.5, metallic=0, maps=False, transmission=0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    m.use_backface_culling = True
    nodes, links = m.node_tree.nodes, m.node_tree.links
    p = nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Roughness'].default_value = rough
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Transmission Weight'].default_value = transmission
    p.inputs['IOR'].default_value = 1.46 if transmission else 1.5
    if maps:
        files = ['enamel-albedo.png', 'enamel-brush.png'] if maps == 'enamel' else ['aged-metal.png']
        textures = []
        for f in files:
            t = nodes.new('ShaderNodeTexImage')
            t.image = bpy.data.images.load(str(TEX/f), check_existing=True)
            textures.append(t)
        output = textures[0].outputs['Color']
        if len(textures) == 2:
            mix = nodes.new('ShaderNodeMixRGB'); mix.blend_type = 'MIX'
            mix.inputs[0].default_value = .52
            links.new(output, mix.inputs[1]); links.new(textures[1].outputs['Color'], mix.inputs[2])
            output = mix.outputs[0]
        tint = nodes.new('ShaderNodeMixRGB'); tint.blend_type = 'MULTIPLY'
        tint.inputs[0].default_value = 1; tint.inputs[2].default_value = (*color, 1)
        links.new(output, tint.inputs[1]); links.new(tint.outputs[0], p.inputs['Base Color'])
    materials.append(m)
    contracts.append(dict(slot=name, tint=color, roughness=rough, metallic=metallic,
                          texture=maps or None, transmission=transmission))
    return m

ivory = material('DH_Ivory_Painted', (1.06, 1.04, 1.00), .40, maps='enamel')
blue = material('DH_BlueGray_Painted', (.26, .38, .49), .56, maps='enamel')
metal = material('DH_Aged_Hardware', (.46, .43, .34), .49, .7, 'metal')
rubber = material('DH_Rubber', (.035, .029, .024), .82)
dark = material('DH_Filter_Shadow', (.045, .040, .030), .91)
ink = material('DH_Control_Print', (.83, .79, .64), .62)
glass = material('DH_Tank_Window', (.38, .52, .48), .18, transmission=.6)
water = material('DH_Collected_Water', (.32, .45, .43), .12, transmission=.75)
amber = material('DH_Amber_Lens', (.60, .18, .025), .24)
bakelite = material('DH_Plug_Bakelite', (.22, .15, .09), .58, maps='metal')

body, tank, bail, cord, plug = [], [], [], [], []
def active(o):
    bpy.ops.object.select_all(action='DESELECT')
    o.select_set(True); bpy.context.view_layer.objects.active = o

def box(name, loc, dims, mat=None, bevel=.004, group=body, segments=3):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o=bpy.context.object; o.name=name; o.dimensions=dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        # Thin panels need an extruded rounded outline. A full 3D bevel at
        # half their thickness collapses edges and creates zero-area faces.
        if bevel > min(dims)*.45:
            axis=min(range(3),key=lambda i:dims[i])
            a,b=[i for i in range(3) if i!=axis]
            hw,hh=dims[a]/2,dims[b]/2
            r=min(bevel,min(hw,hh)*.90)
            profile=[]
            for cx,cy,start in [(hw-r,hh-r,0),(-hw+r,hh-r,90),(-hw+r,-hh+r,180),(hw-r,-hh+r,270)]:
                for k in range(segments+1):
                    angle=math.radians(start+90*k/segments)
                    profile.append((cx+r*math.cos(angle),cy+r*math.sin(angle)))
            n=len(profile); vs=[]
            for w in [-dims[axis]/2,dims[axis]/2]:
                for u,v in profile:
                    co=[0,0,0];co[axis]=w;co[a]=u;co[b]=v;vs.append(co)
            faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
            faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
            me=bpy.data.meshes.new(name+' rounded profile');me.from_pydata(vs,[],faces);me.update()
            old=o.data;o.data=me;bpy.data.meshes.remove(old)
            bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
        else:
            m=o.modifiers.new('Soft manufactured edge', 'BEVEL'); m.width=bevel; m.segments=segments
            bpy.ops.object.modifier_apply(modifier=m.name)
    if mat: o.data.materials.append(mat)
    if group is not None: group.append(o)
    return o

def subtract(o, cutter):
    active(o); m=o.modifiers.new('Authored opening', 'BOOLEAN')
    m.operation='DIFFERENCE'; m.solver='EXACT'; m.object=cutter
    bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.data.objects.remove(cutter, do_unlink=True)

def cylinder(name, loc, radius, depth, mat, axis='Z', group=body, vertices=32):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    o=bpy.context.object; o.name=name
    if axis=='Y': o.rotation_euler.x=math.pi/2
    elif axis=='X': o.rotation_euler.y=math.pi/2
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    m=o.modifiers.new('Rounded edges', 'BEVEL'); m.width=min(.0014,depth*.15,radius*.25); m.segments=2
    bpy.ops.object.modifier_apply(modifier=m.name)
    o.data.materials.append(mat); group.append(o)
    return o

def wire(name, points, radius, mat, group=body):
    c=bpy.data.curves.new(name, 'CURVE'); c.dimensions='3D'; c.resolution_u=8
    c.bevel_depth=radius; c.bevel_resolution=2; c.use_fill_caps=True
    s=c.splines.new('POLY'); s.points.add(len(points)-1)
    for p, co in zip(s.points,points): p.co=(*co,1)
    o=bpy.data.objects.new(name,c); bpy.context.collection.objects.link(o)
    active(o); bpy.ops.object.convert(target='MESH')
    o.data.materials.append(mat); group.append(o)
    return o

# Broader workhorse shell, vertical intake and a sloped cream control brow.
shell=box('Continuous cream casing', (0,0,.2825), (.390,.310,.455), ivory, .035, segments=7)
for v in shell.data.vertices:
    z=v.co.z+shell.location.z
    if v.co.y < -.095:
        v.co.y += .5*max(0,z-.405)
shell.data.update()
subtract(shell,box('Tank bay cut',(0,-.060,.166),(.342,.270,.193),bevel=.019,group=None,segments=5))
subtract(shell,box('Front grille cut',(0,-.155,.343),(.329,.086,.140),bevel=.018,group=None,segments=5))
subtract(shell,box('Rear grille cut',(0,.155,.351),(.285,.070,.160),bevel=.014,group=None))
subtract(shell,box('Top exhaust cut',(0,.024,.505),(.307,.136,.050),bevel=.019,group=None,segments=5))
box('Front intake filter',(0,-.111,.343),(.319,.004,.130),dark,.014)
for i in range(15):
    box('Cream vertical intake vane %02d'%i,(-.149+i*.0213,-.139,.343),(.005,.012,.144),ivory,.002)
box('Exhaust shadow',(0,.024,.481),(.299,.128,.004),dark,.014)
for i in range(6):
    box('Top exhaust vane %02d'%i,(0,-.027+i*.0204,.503),(.296,.006,.014),metal,.002)
box('Rear washable filter',(0,.123,.351),(.276,.004,.150),dark,.010)
for i in range(7):
    box('Rear horizontal filter slat %02d'%i,(0,.150,.288+i*.021),(.274,.010,.006),ivory,.002)
for x in [-.132,.132]:
    box('Rear filter end',(x,.153,.351),(.006,.008,.151),ivory,.0015)

# Broad blue-gray side panels, visible as a separate painted metal casing.
for side in [-1,1]:
    box('Blue gray side panel',(side*.195, .010,.267),(.007,.244,.350),blue,.027,segments=6)
    for y in [-.082,.103]:
        for z in [.114,.414]:
            cylinder('Side panel fastener',(side*.199,y,z),.0032,.002,metal,'X',vertices=16)

# Folding bail, parked 30 degrees back around the transverse hinge axis.
BAIL_PIVOT=Vector((0,.075,.428))
handle=box('Folding carry bail',(0,.075,.483),(.430,.020,.122),ivory,.014,bail,5)
subtract(handle,box('Bail open underside',(0,.075,.459),(.400,.070,.128),bevel=.013,group=None,segments=5))
box('Bail underside grip',(0,.075,.530),(.250,.022,.008),blue,.003,bail)
fold=Matrix.Translation(BAIL_PIVOT)@Matrix.Rotation(math.radians(-30),4,'X')@Matrix.Translation(-BAIL_PIVOT)
for o in bail:o.matrix_world=fold@o.matrix_world
for side in [-1,1]:
    cylinder('Bail hinge mount',(side*.201,.075,.428),.019,.007,ivory,'X')
    cylinder('Bail hinge axle',(side*.211,.075,.428),.010,.004,metal,'X')

# Controls on the cream sloping shoulder, with a larger workhorse dial.
brow_pivot=Vector((0,-.155,.455))
slope=Matrix.Translation(brow_pivot+Vector((0,.025,0)))@Matrix.Rotation(math.atan(-.5),4,'X')@Matrix.Translation(-brow_pivot)
pocket=box('Flat control panel seat',(0,-.140,.455),(.334,.035,.088),bevel=.010,group=None,segments=5)
pocket.matrix_world=slope@pocket.matrix_world
subtract(shell,pocket)
panel=box('Flat angled cream control panel',(0,-.137,.455),(.332,.036,.086),ivory,.010,segments=5)
panel.matrix_world=slope@panel.matrix_world
active(shell);join= shell.modifiers.new('Integral flat control brow','BOOLEAN');join.operation='UNION';join.solver='EXACT';join.object=panel
bpy.ops.object.modifier_apply(modifier=join.name);body.remove(panel);bpy.data.objects.remove(panel,do_unlink=True)
control_start=len(body)
cylinder('Dial seating ring',(-.044,-.160,.455),.031,.006,metal,'Y')
cylinder('Humidity dial',(-.044,-.169,.455),.027,.016,ivory,'Y',vertices=48)
for i in range(24):
    a=2*math.pi*i/24
    cylinder('Dial grip knurl %02d'%i,(-.044+.026*math.cos(a),-.168,.455+.026*math.sin(a)),.0014,.011,ivory,'Y',vertices=8)
pointer=box('Dial index',(-.039,-.178,.465),(.002,.0014,.015),metal,.0005)
pointer.rotation_euler.y=math.radians(25)
for i in range(9):
    a=math.radians(22+17*i)
    x=-.044+.039*math.cos(a); z=.455+.039*math.sin(a)
    tick=box('Printed humidity tick %02d'%i,(x,-.157,z),(.0018,.0008,.006 if i%2==0 else .0036),metal,.0003)
    tick.rotation_euler.y=math.pi/2-a
box('Tank lamp bezel',(.102,-.160,.457),(.037,.006,.028),metal,.007)
box('Amber full tank lens',(.102,-.164,.457),(.030,.003,.021),amber,.005)
wire('Tank pictogram',[(.089,-.157,.434),(.091,-.157,.427),(.110,-.157,.427),(.113,-.157,.434)],.0007,metal)
# An explicit power switch on the left, distinct from the humidity knob.
switch=box('Power rocker',(-.126,-.160,.455),(.015,.007,.025),rubber,.003)
box('Power rocker mark',(-.126,-.164,.461),(.0012,.0008,.007),ink,.0004)
for o in body[control_start:]:o.matrix_world=slope@o.matrix_world
# The control mounts now seat on a real flat panel instead of a curved shoulder.
for o in body[control_start:]:
    o.location += Vector((0,.894427,-.447214))*.00225

# Removable open-top bucket. The sight glass opens into the hollow container.
bucket=box('Collection bucket',(0,-.045,.166),(.336,.234,.187),ivory,.018,tank,5)
subtract(bucket,box('Bucket interior',(0,-.043,.194),(.311,.209,.165),bevel=.012,group=None,segments=4))
subtract(bucket,box('Bucket finger recess',(-.035,-.165,.242),(.128,.044,.025),bevel=.010,group=None,segments=4))
subtract(bucket,box('Sight glass aperture',(.105,-.162,.156),(.019,.042,.113),bevel=.008,group=None,segments=4))
box('Sight glass bezel',(.105,-.161,.156),(.025,.005,.119),blue,.011,tank,5)
# Bezel is a ring, not a solid panel covering the window.
bezel=tank[-1]
subtract(bezel,box('Bezel aperture',(.105,-.161,.156),(.018,.025,.112),bevel=.008,group=None,segments=4))
box('Water level window',(.105,-.159,.156),(.017,.002,.111),glass,.007,tank,5)
box('Collected water',(0,-.043,.134),(.305,.203,.038),water,.0006,tank)
box('Tank grip shadow',(-.035,-.145,.240),(.104,.003,.013),blue,.004,tank)
for z in [.121,.153,.185]:
    box('Water level graduation',(.121,-.165,z),(.007,.001,.001),blue,.0003,tank)

# Four swivel casters and axle caps. Their rubber bottoms sit on the floor.
for x in [-.145,.145]:
    for y in [-.103,.103]:
        cylinder('Caster swivel stem',(x,y,.051),.009,.019,metal)
        box('Caster fork',(x,y,.032),(.031,.025,.035),metal,.005)
        cylinder('Rubber caster',(x,y,.019),.019,.023,rubber,'X')
        cylinder('Caster outer hub',(x+(.0125 if x>0 else -.0125),y,.019),.008,.003,metal,'X')
        cylinder('Hub axle',(x+(.0143 if x>0 else -.0143),y,.019),.0024,.002,metal,'X',vertices=16)

# Rear service details and a stowed power cable with molded plug.
box('Rear service cover',(0,.155,.173),(.270,.008,.129),ivory,.012)
for x in [-.100,.100]:
    for z in [.123,.222]:
        cylinder('Service fastener',(x,.161,z),.003,.002,metal,'Y',vertices=16)
        box('Fastener slot',(x,.1625,z),(.0038,.0005,.0007),dark,.00015)
for x in [-.075,.075]:
    box('Cable keeper',(x,.172,.142),(.012,.032,.022),blue,.003)
points=[]
for k in range(3*64+1):
    a=2*math.pi*k/64
    points.append((.078*math.cos(a),.182+k/(3*64)*.021,.143+.027*math.sin(a)))
wire('Stowed power cord',points,.003,rubber,cord)
wire('Cord to strain relief',[(.078,.182,.143),(.089,.172,.110),(-.080,.162,.094)],.003,rubber,cord)
wire('Cord to stored plug',[(.078,.203,.143),(.102,.207,.151),(.100,.190,.159)],.003,rubber,cord)
cylinder('Cable strain relief',(-.080,.162,.094),.006,.011,rubber,'Y')
# Separate grounded plug, authored at its seating face: +Y is insertion.
plug_body=box('Tapered bakelite plug body',(0,-.017,0),(.028,.028,.028),bakelite,.004,plug,5)
for v in plug_body.data.vertices:
    taper=.70+.30*(v.co.y+.014)/.028
    v.co.x*=taper;v.co.z*=taper
box('Plug face collar',(0,-.002,0),(.031,.004,.032),bakelite,.005,plug,5)
for x in [-.0085,.0085]:
    blade=box('Plug blade',(x,.0075,.005),(.0016,.015,.006),metal,.00035,plug)
    hole=cylinder('Blade punched hole',(x,.010,.005),.0009,.006,metal,'X',group=[],vertices=16)
    subtract(blade,hole)
cylinder('Plug ground pin',(0,.008,-.0075),.0020,.016,metal,'Y',plug,24)
cylinder('Plug flexible neck',(0,-.035,0),.0045,.016,bakelite,'Y',plug)
for y in [-.031,-.036,-.041]:
    cylinder('Plug strain relief rib',(0,y,0),.0056,.002,bakelite,'Y',plug,24)
for y,z in [(-.009,.014),(-.015,.0128),(-.021,.0116)]:
    box('Molded top grip ridge',(0,y,z),(.014,.0016,.0012),bakelite,.0005,plug)
box('Rear identification plate',(-.023,.161,.196),(.083,.0015,.025),blue,.002)
for z in [.191,.196,.201]:
    box('Identification rule',(-.023,.162,z),(.064,.0006,.0007),ink,.0001)

# Prepare explicit UV0, outward component normals, and baked edge normals.
for o in body+tank+bail+cord+plug:
    active(o)
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    bm=bmesh.new(); bm.from_mesh(o.data)
    # Curve conversion duplicates the cap rim; weld it before checking solids.
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7)
    if o==shell:
        # Remove a sub-20-micron boolean sliver where the inset meets the brow.
        bmesh.ops.dissolve_degenerate(bm,dist=.00002,edges=list(bm.edges))
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces)); bm.to_mesh(o.data); bm.free()
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.02)
    bpy.ops.object.mode_set(mode='OBJECT')
    for p in o.data.polygons: p.use_smooth=True
    wn=o.modifiers.new('Baked weighted normals','WEIGHTED_NORMAL'); wn.keep_sharp=True; wn.weight=40
    bpy.ops.object.modifier_apply(modifier=wn.name)
    bpy.context.scene.cursor.location=(0,0,0); bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

def combined(name, parts):
    copies=[]
    for o in parts:
        c=o.copy(); c.data=o.data.copy(); bpy.context.collection.objects.link(c); copies.append(c)
    active(copies[0])
    for c in copies:c.select_set(True)
    bpy.ops.object.join(); o=bpy.context.object; o.name=name
    return o

# Separate plug export retains the insertion-face pivot, not the floor pivot.
plug_export=combined('DH_Plug01',plug);active(plug_export)
bpy.ops.export_scene.fbx(filepath=str(MODEL/'DH_Plug01.fbx'),use_selection=True,
    object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,add_leaf_bones=False)
bpy.data.objects.remove(plug_export,do_unlink=True)
STORED_PLUG=Matrix.Translation((.100,.190,.116))@Matrix.Rotation(-math.pi/2,4,'X')
for o in plug:
    o.matrix_world=STORED_PLUG@o.matrix_world
    active(o);bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
# Simple body collision; running/movement integration can author its own profile.
ucx=box('UCX_DH_Dehumidifier01_00',(0,0,.2825),(.390,.310,.455),bevel=0,group=None)
ucx.display_type='WIRE'; ucx.hide_render=True
fixed=combined('DH_Dehumidifier01',body+tank+bail+cord+plug)
active(fixed); ucx.select_set(True)
bpy.ops.export_scene.fbx(filepath=str(MODEL/'DH_Dehumidifier01.fbx'),use_selection=True,
    object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,add_leaf_bones=False)
bpy.data.objects.remove(fixed,do_unlink=True)
ucx.hide_set(True)
# Optional split exports preserve the SAME assembly pivot for an authored tank pull.
for name, parts in [('DH_Dehumidifier01_Body',body+bail),('DH_Dehumidifier01_Tank',tank),('DH_Dehumidifier01_CordStowed',cord)]:
    o=combined(name,parts); active(o)
    bpy.ops.export_scene.fbx(filepath=str(MODEL/(name+'.fbx')),use_selection=True,
        object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,add_leaf_bones=False)
    bpy.data.objects.remove(o,do_unlink=True)

# Straight, subdivided X-axis cable for a runtime spline mesh. Not the stored coil.
vs=[];faces=[];rings=33;segments=12
for j in range(rings):
    for i in range(segments):
        a=2*math.pi*i/segments;vs.append((j/(rings-1),.003*math.cos(a),.003*math.sin(a)))
for j in range(rings-1):
    for i in range(segments):
        n=(i+1)%segments;faces.append((j*segments+i,j*segments+n,(j+1)*segments+n,(j+1)*segments+i))
faces += [tuple(reversed(range(segments))),tuple((rings-1)*segments+i for i in range(segments))]
me=bpy.data.meshes.new('Spline cable source');me.from_pydata(vs,[],faces);me.update()
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
cable=bpy.data.objects.new('DH_CableSegment01',me);bpy.context.collection.objects.link(cable);me.materials.append(rubber)
uv=me.uv_layers.new(name='UVMap')
for f in me.polygons:
    for li in f.loop_indices:
        co=me.vertices[me.loops[li].vertex_index].co
        uv.data[li].uv=(co.x,(math.atan2(co.z,co.y)/(2*math.pi))%1)
    f.use_smooth=len(f.vertices)==4
active(cable)
bpy.ops.export_scene.fbx(filepath=str(MODEL/'DH_CableSegment01.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,add_leaf_bones=False)
bpy.data.objects.remove(cable,do_unlink=True)

for img in bpy.data.images:
    if img.source=='FILE': img.filepath='//../textures/'+Path(img.filepath).name
(ROOT/'materials.json').write_text(json.dumps(contracts,indent=2)+'\n')
anchors={
    'units':'Blender metres; front -Y, Z up',
    'selected_concept':'B — cream and blue-gray workhorse',
    'planned_movement':'Choose a destination room; gameplay is implemented in a separate thread',
    'placement':[0,0,0], 'carry':[0,.075,.520],
    'cord_exit':[-.080,.162,.094], 'bail_hinge':list(BAIL_PIVOT),
    'tank_pull_direction':[0,-1,0], 'tank_pull_distance':.245,
    'plug':{'mesh':'DH_Plug01.fbx','insertion_axis':[0,1,0],
            'seating_pivot':[0,0,0], 'cord_exit':[0,-.043,0],
            'stored_location':[.100,.190,.116], 'stored_rotation_x_deg':-90},
    'states':{
        'portable':'Body + Tank + CordStowed + plug at stored transform',
        'plugged':'Body + Tank, plug at outlet socket anchor; replace CordStowed with runtime cable',
        'moving':'Use carry/placement anchor; outlet remains in its room'},
    'runtime_cable':{'radius_m':.003,'endpoints':['cord_exit','plug.cord_exit'],
                     'mesh':'DH_CableSegment01.fbx','forward_axis':'X','source_length_m':1,
                     'collision':'none','note':'Use a spline/cable component; do not stretch the stowed coil mesh.'}}
(ROOT/'interaction-anchors.json').write_text(json.dumps(anchors,indent=2)+'\n')
for name,loc in [('Placement',(0,0,0)),('Carry',(0,.075,.520)),('CordExit',(-.080,.162,.094)),('BailHinge',BAIL_PIVOT)]:
    o=bpy.data.objects.new('DH_Anchor_'+name,None);bpy.context.collection.objects.link(o);o.location=loc;o.empty_display_size=.025

# Neutral studio, no apartment lighting baked into the surface textures.
def camera(pos,target=(0,0,.285),scale=.72):
    if not scene.camera:
        bpy.ops.object.camera_add(); scene.camera=bpy.context.object
    c=scene.camera; c.location=pos
    c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler()
    c.data.type='ORTHO'; c.data.ortho_scale=scale
for pos,power,size in [((-.6,-.8,1.1),38,.75),((.7,-.15,.7),16,.7),((.1,.7,.9),25,.55)]:
    bpy.ops.object.light_add(type='AREA',location=pos)
    o=bpy.context.object; o.data.energy=power; o.data.shape='DISK'; o.data.size=size
    o.rotation_euler=(Vector((0,0,.28))-o.location).to_track_quat('-Z','Y').to_euler()
camera((.80,-1.15,.77),scale=.75)
bpy.ops.wm.save_as_mainfile(filepath=str(MODEL/'PR-DEHUMIDIFIER-01.blend'))
if '--no-render' in sys.argv:
    print('DEHUMIDIFIER_GEOMETRY_COMPLETE');sys.exit(0)
for name,pos in [('front-three-quarter',(.80,-1.15,.77)),('rear-three-quarter',(-.80,1.15,.73))]:
    camera(pos,scale=.75); scene.render.filepath=str(PRE/(name+'.png')); bpy.ops.render.render(write_still=True)
for o in tank:o.location.y-=.245
camera((.8,-1.15,.83),target=(0,-.07,.28),scale=.80)
scene.render.filepath=str(PRE/'tank-removed.png'); bpy.ops.render.render(write_still=True)
for o in tank:o.location.y+=.245
raise_bail=Matrix.Translation(BAIL_PIVOT)@Matrix.Rotation(math.radians(30),4,'X')@Matrix.Translation(-BAIL_PIVOT)
for o in bail:o.matrix_world=raise_bail@o.matrix_world
camera((.80,-1.15,.77),scale=.75)
scene.render.filepath=str(PRE/'handle-raised.png');bpy.ops.render.render(write_still=True)
for name,pos in [('controls-side',(.75,-.18,.48)),('controls-low',(-.55,-.65,.27)),('controls-overhead',(.45,-.65,.82))]:
    camera(pos,target=(0,-.125,.451),scale=.34)
    scene.render.filepath=str(PRE/(name+'.png'));bpy.ops.render.render(write_still=True)
print('DEHUMIDIFIER_BUILD_COMPLETE',len(body),len(tank),len(bail),len(cord),len(plug))
