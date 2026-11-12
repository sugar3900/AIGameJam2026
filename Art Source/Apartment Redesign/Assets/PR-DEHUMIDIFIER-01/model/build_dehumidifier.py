"""Concept A floor dehumidifier. Run with Blender 5.x, --threads 2.

Metres, Z up, front -Y, floor-centred assembly origin. No gameplay changes.
"""
import bpy, bmesh, math, json, fcntl
from pathlib import Path
from mathutils import Vector

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
scene.cycles.samples = 48
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
sage = material('DH_Sage_Painted', (.37, .47, .32), .52, maps='enamel')
metal = material('DH_Aged_Hardware', (.46, .43, .34), .49, .7, 'metal')
rubber = material('DH_Rubber', (.035, .029, .024), .82)
dark = material('DH_Filter_Shadow', (.045, .040, .030), .91)
ink = material('DH_Control_Print', (.83, .79, .64), .62)
glass = material('DH_Tank_Window', (.38, .52, .48), .18, transmission=.6)
water = material('DH_Collected_Water', (.32, .45, .43), .12, transmission=.75)
amber = material('DH_Amber_Lens', (.60, .18, .025), .24)

body, tank = [], []
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

# A continuous rounded shell, with true recesses for both grilles and tank.
shell=box('Continuous ivory casing', (0,0,.290), (.340,.290,.470), ivory, .039, segments=7)
subtract(shell,box('Tank bay cut',(0,-.060,.163),(.288,.260,.187),bevel=.019,group=None,segments=5))
subtract(shell,box('Front grille cut',(0,-.145,.352),(.278,.086,.138),bevel=.020,group=None,segments=5))
subtract(shell,box('Rear grille cut',(0,.145,.351),(.248,.070,.160),bevel=.014,group=None))
subtract(shell,box('Top exhaust cut',(0,.043,.516),(.185,.103,.050),bevel=.017,group=None))
box('Front intake filter',(0,-.101,.352),(.267,.004,.127),dark,.015)
for i in range(6):
    o=box('Sage intake louver %02d'%i,(0,-.131,.300+i*.0207),(.264,.029,.007),sage,.003)
    o.rotation_euler.x=math.radians(-12)
box('Exhaust shadow',(0,.043,.492),(.179,.097,.004),dark,.012)
for i in range(5):
    box('Top exhaust vane %02d'%i,(0,.005+i*.018,.513),(.174,.005,.013),sage,.002)
box('Rear washable filter',(0,.113,.351),(.239,.004,.150),dark,.010)
for i in range(12):
    box('Rear filter slat %02d'%i,(-.109+i*.0198,.140,.351),(.006,.010,.143),ivory,.002)
for z in [.311,.391]:
    box('Rear filter crossbar',(0,.143,z),(.237,.008,.005),ivory,.0015)

# Lift handle: a solid arch with a real rounded hand opening.
handle=box('Carry handle',(0,-.005,.548),(.216,.036,.065),ivory,.015,segments=5)
subtract(handle,box('Handle aperture',(0,-.005,.540),(.157,.080,.034),bevel=.013,group=None,segments=5))
box('Handle underside grip',(0,-.005,.562),(.128,.037,.007),sage,.003)

# Control panel, rotary knob, scale ticks and full-tank lamp.
panel=box('Sage control inset',(0,-.143,.466),(.267,.011,.067),sage,.025,segments=6)
cylinder('Dial seating ring',(-.028,-.153,.467),.029,.006,metal,'Y')
cylinder('Humidity dial',(-.028,-.162,.467),.025,.016,ivory,'Y',vertices=48)
for i in range(24):
    a=2*math.pi*i/24
    cylinder('Dial grip knurl %02d'%i,(-.028+.024*math.cos(a),-.161,.467+.024*math.sin(a)),.0014,.011,ivory,'Y',vertices=8)
pointer=box('Dial index',(-.023,-.171,.477),(.002,.0014,.015),metal,.0005)
pointer.rotation_euler.y=math.radians(25)
for i in range(9):
    a=math.radians(22+17*i)
    x=-.028+.037*math.cos(a); z=.467+.037*math.sin(a)
    tick=box('Printed humidity tick %02d'%i,(x,-.150,z),(.0018,.0008,.006 if i%2==0 else .0036),ink,.0003)
    tick.rotation_euler.y=math.pi/2-a
cylinder('Tank lamp bezel',(.090,-.152,.472),.009,.004,metal,'Y')
cylinder('Amber full tank lens',(.090,-.155,.472),.0067,.003,amber,'Y')
wire('Tank pictogram',[(.078,-.150,.450),(.081,-.150,.440),(.101,-.150,.440),(.104,-.150,.450)],.0007,ink)
wire('Tank pictogram water',[(.082,-.150,.445),(.088,-.150,.446),(.094,-.150,.4445),(.100,-.150,.445)],.0006,ink)
# An explicit power switch on the left, distinct from the humidity knob.
switch=box('Power rocker',(-.100,-.153,.465),(.015,.007,.025),rubber,.003)
box('Power rocker mark',(-.100,-.157,.471),(.0012,.0008,.007),ink,.0004)

# Removable open-top bucket. The sight glass opens into the hollow container.
bucket=box('Collection bucket',(0,-.043,.163),(.282,.224,.181),ivory,.018,tank,5)
subtract(bucket,box('Bucket interior',(0,-.041,.191),(.257,.199,.159),bevel=.012,group=None,segments=4))
subtract(bucket,box('Bucket finger recess',(0,-.158,.240),(.111,.044,.025),bevel=.010,group=None,segments=4))
subtract(bucket,box('Sight glass aperture',(.057,-.155,.154),(.019,.042,.109),bevel=.008,group=None,segments=4))
box('Sight glass bezel',(.057,-.154,.154),(.025,.005,.115),sage,.011,tank,5)
# Bezel is a ring, not a solid panel covering the window.
bezel=tank[-1]
subtract(bezel,box('Bezel aperture',(.057,-.154,.154),(.018,.025,.108),bevel=.008,group=None,segments=4))
box('Water level window',(.057,-.152,.154),(.017,.002,.107),glass,.007,tank,5)
box('Collected water',(0,-.041,.133),(.251,.193,.038),water,.0006,tank)
box('Tank grip shadow',(0,-.138,.238),(.087,.003,.013),sage,.004,tank)
for z in [.121,.153,.185]:
    box('Water level graduation',(.073,-.158,z),(.007,.001,.001),sage,.0003,tank)

# Four swivel casters and axle caps. Their rubber bottoms sit on the floor.
for x in [-.125,.125]:
    for y in [-.095,.095]:
        cylinder('Caster swivel stem',(x,y,.051),.009,.019,metal)
        box('Caster fork',(x,y,.032),(.031,.025,.035),metal,.005)
        cylinder('Rubber caster',(x,y,.019),.019,.023,rubber,'X')
        cylinder('Caster outer hub',(x+(.0125 if x>0 else -.0125),y,.019),.008,.003,metal,'X')
        cylinder('Hub axle',(x+(.0143 if x>0 else -.0143),y,.019),.0024,.002,metal,'X',vertices=16)

# Rear service details and a stowed power cable with molded plug.
box('Rear service cover',(0,.145,.173),(.230,.008,.129),ivory,.012)
for x in [-.100,.100]:
    for z in [.123,.222]:
        cylinder('Service fastener',(x,.151,z),.003,.002,metal,'Y',vertices=16)
        box('Fastener slot',(x,.1525,z),(.0038,.0005,.0007),dark,.00015)
for x in [-.075,.075]:
    box('Cable keeper',(x,.162,.142),(.012,.032,.022),sage,.003)
points=[]
for k in range(3*64+1):
    a=2*math.pi*k/64
    points.append((.078*math.cos(a),.172+k/(3*64)*.009,.143+.027*math.sin(a)))
wire('Stowed power cord',points,.003,rubber)
wire('Cord to strain relief',[(-.078,.172,.143),(-.085,.163,.111),(-.080,.152,.094)],.003,rubber)
cylinder('Cable strain relief',(-.080,.152,.094),.006,.011,rubber,'Y')
box('Molded plug',(.080,.183,.117),(.023,.015,.032),rubber,.004)
for x in [.074,.086]:
    box('Plug pin',(x,.183,.094),(.003,.006,.014),metal,.0006)
box('Rear identification plate',(-.023,.151,.196),(.083,.0015,.025),sage,.002)
for z in [.191,.196,.201]:
    box('Identification rule',(-.023,.152,z),(.064,.0006,.0007),ink,.0001)

# Prepare explicit UV0, outward component normals, and baked edge normals.
for o in body+tank:
    active(o)
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    bm=bmesh.new(); bm.from_mesh(o.data)
    # Curve conversion duplicates the cap rim; weld it before checking solids.
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7)
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

# Simple collision intentionally encloses the fixed appliance; no tiny grille/cord hulls.
ucx=box('UCX_DH_Dehumidifier01_00',(0,0,.290),(.340,.290,.470),bevel=0,group=None)
ucx.display_type='WIRE'; ucx.hide_render=True
fixed=combined('DH_Dehumidifier01',body+tank)
active(fixed); ucx.select_set(True)
bpy.ops.export_scene.fbx(filepath=str(MODEL/'DH_Dehumidifier01.fbx'),use_selection=True,
    object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,add_leaf_bones=False)
bpy.data.objects.remove(fixed,do_unlink=True)
ucx.hide_set(True)
# Optional split exports preserve the SAME assembly pivot for an authored tank pull.
for name, parts in [('DH_Dehumidifier01_Body',body),('DH_Dehumidifier01_Tank',tank)]:
    o=combined(name,parts); active(o)
    bpy.ops.export_scene.fbx(filepath=str(MODEL/(name+'.fbx')),use_selection=True,
        object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,add_leaf_bones=False)
    bpy.data.objects.remove(o,do_unlink=True)

for img in bpy.data.images:
    if img.source=='FILE': img.filepath='//../textures/'+Path(img.filepath).name
(ROOT/'materials.json').write_text(json.dumps(contracts,indent=2)+'\n')

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
camera((.80,-1.15,.77))
bpy.ops.wm.save_as_mainfile(filepath=str(MODEL/'PR-DEHUMIDIFIER-01.blend'))
for name,pos in [('front-three-quarter',(.80,-1.15,.77)),('rear-three-quarter',(-.80,1.15,.73))]:
    camera(pos); scene.render.filepath=str(PRE/(name+'.png')); bpy.ops.render.render(write_still=True)
for o in tank:o.location.y-=.245
camera((.8,-1.15,.83),target=(0,-.07,.28),scale=.80)
scene.render.filepath=str(PRE/'tank-removed.png'); bpy.ops.render.render(write_still=True)
print('DEHUMIDIFIER_BUILD_COMPLETE',len(body),len(tank))
