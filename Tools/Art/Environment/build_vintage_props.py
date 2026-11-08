"""Create reusable 1950s apartment assets. Run with Blender --background --python.
Coordinates are metres, Z up, origin on floor, front faces -X. FBX imports at 1cm UE scale.
Materials are named slots; UE can replace them with painterly project materials.
"""
import bpy, math, os
from mathutils import Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
OUT = os.path.join(ROOT, 'Art Source', 'Environment Models')
os.makedirs(OUT, exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def mat(name, color, rough=.75, metal=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal
    return m
cream=mat('Enamel_Cream',(.75,.68,.53)); mint=mat('Paint_Sage',(.32,.43,.32)); dark=mat('Iron',(.10,.09,.075),.55,.4)
chrome=mat('Aged_Metal',(.38,.37,.31),.4,.65); rust=mat('Rust',(.35,.15,.065)); fabric=mat('Upholstery',(.29,.34,.23)); fabric_dark=mat('Upholstery_Shadow',(.20,.24,.16)); wood=mat('Wood',(.25,.115,.055)); porcelain=mat('Porcelain',(.8,.72,.63),.35); black=mat('Burner',(.07,.06,.05),.6,.4)

def box(name, loc, dims, material, bevel=.02):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o=bpy.context.object; o.name=name
    o.dimensions=dims; bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod=o.modifiers.new('Soft worn edges','BEVEL'); mod.width=bevel; mod.segments=3
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
        bpy.context.view_layer.objects.active=o
        for mod in list(o.modifiers): bpy.ops.object.modifier_apply(modifier=mod.name)
    o.data.materials.append(material); return o

def cylinder(name, loc, radius, depth, material, rotation=(0,0,0), vertices=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc, rotation=rotation); o=bpy.context.object; o.name=name; o.data.materials.append(material)
    bevel=o.modifiers.new('Edge softness','BEVEL'); bevel.width=min(.006,radius*.2); bevel.segments=2
    o.modifiers.new('Weighted normals','WEIGHTED_NORMAL'); bpy.context.view_layer.objects.active=o
    for mod in list(o.modifiers): bpy.ops.object.modifier_apply(modifier=mod.name)
    return o

def bar(name, start, end, radius, material):
    a,b=Vector(start),Vector(end); d=b-a
    o=cylinder(name,(a+b)*.5,radius,d.length,material); o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); return o

def export(name):
    objs=list(bpy.context.scene.objects)
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active=objs[0]
    bpy.ops.object.join(); o=bpy.context.object; o.name=name
    # Preserve floor origin irrespective of geometry centre.
    bpy.context.scene.cursor.location=(0,0,0); bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    bpy.ops.export_scene.fbx(filepath=os.path.join(OUT,name+'.fbx'), use_selection=True, apply_unit_scale=True, bake_space_transform=False, object_types={'MESH'}, add_leaf_bones=False, path_mode='AUTO')
    print('ASSET',name,'DIMENSIONS',tuple(round(x,3) for x in o.dimensions),'MATERIALS',[x.name for x in o.data.materials])
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,name+'.blend'))
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

# Rounded icebox cabinet. Door intentionally excluded: game has animated door.
# Hollow cabinet with a readable cavity behind the separately animated door.
box('Back',(.28,0,.91),(.08,.88,1.82),cream,.03)
for y in [-.40,.40]: box('Side',(-.01,y,.91),(.58,.08,1.82),cream,.035)
for z in [.05,1.77]: box('Top or bottom',(-.01,0,z),(.58,.76,.10),cream,.03)
for z in [.50,.95,1.37]: box('Interior shelf',(-.01,0,z),(.56,.75,.025),porcelain,.008)
box('Toe grille',(-.325,0,.09),(.025,.67,.10),dark,.008)
for y in [-.26,-.17,-.08,.01,.10,.19,.28]: box('Grille rib',(-.342,y,.09),(.01,.012,.075),chrome,.003)
export('SM_VintageFridgeBody')

# Range with oven face, top, backsplash, rings and knobs. The front faces -X.
box('Range body',(0,0,.43),(.63,.78,.86),cream,.045)
box('Enamel cooktop',(0,0,.87),(.65,.8,.05),cream,.018)
box('Backguard',(.265,0,1.0),(.12,.78,.27),cream,.045)
box('Oven door',(-.325,0,.38),(.04,.65,.48),cream,.022)
box('Oven window',(-.349,0,.39),(.012,.43,.21),dark,.025)
bar('Oven handle',(-.37,-.25,.62),(-.37,.25,.62),.014,chrome)
for y in [-.28,-.095,.095,.28]: cylinder('Control knob',(-.338,y,.76),.028,.027,chrome,(0,math.pi/2,0))
for x in [-.14,.14]:
    for y in [-.21,.21]:
        cylinder('Burner plate',(x,y,.903),.09,.013,black)
        bpy.ops.mesh.primitive_torus_add(major_segments=32,minor_segments=8,location=(x,y,.915),major_radius=.067,minor_radius=.006); bpy.context.object.data.materials.append(chrome)
export('SM_VintageRange')

# Rounded three-seater, approx 2.4m wide, upholstery creases expressed as panels.
box('Wood plinth',(0,0,.15),(.82,2.34,.18),wood,.025)
for x in [-.29,.29]:
    for y in [-1.03,1.03]: box('Foot',(x,y,.065),(.08,.08,.13),wood,.012)
box('Seat deck',(0,0,.30),(.87,2.4,.25),fabric_dark,.09)
box('Back',(.33,0,.71),(.25,2.37,.85),fabric_dark,.10)
for y in [-.76,0,.76]:
    box('Seat cushion',(-.075,y,.48),(.65,.72,.18),fabric,.075)
    box('Back cushion',(.17,y,.78),(.23,.72,.60),fabric,.075)
for y in [-1.10,1.10]: box('Rolled arm',(-.01,y,.57),(.95,.25,.60),fabric,.12)
export('SM_VintageSofa')

# Clawfoot tub: connected outer shell, broad lip, sloping inner well and bottom.
def rounded_rect(hx,hy,r,z):
    pts=[]
    for cx,cy,start in [(hx-r,hy-r,0),(-hx+r,hy-r,90),(-hx+r,-hy+r,180),(hx-r,-hy+r,270)]:
        for n in range(7):
            a=math.radians(start+n*15); pts.append((cx+r*math.cos(a),cy+r*math.sin(a),z))
    return pts
rings=[rounded_rect(.32,.72,.20,.14),rounded_rect(.38,.80,.20,.48),rounded_rect(.42,.84,.20,.53),rounded_rect(.32,.74,.19,.53),rounded_rect(.24,.65,.17,.20)]
verts=[v for ring in rings for v in ring]; n=len(rings[0]); faces=[]
for j in range(len(rings)-1):
    for i in range(n): faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
faces.append(tuple(range((len(rings)-1)*n,len(rings)*n)))
mesh=bpy.data.meshes.new('Tub shell'); mesh.from_pydata(verts,[],faces); mesh.update()
o=bpy.data.objects.new('Tub shell',mesh); bpy.context.collection.objects.link(o); o.data.materials.append(porcelain)
for poly in mesh.polygons: poly.use_smooth=True

for x in [-.25,.25]:
    for y in [-.64,.64]:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,location=(x,y,.08)); o=bpy.context.object; o.name='Clawfoot'; o.scale=(.09,.09,.08); o.data.materials.append(chrome)
export('SM_ClawfootTub')

# Four-poster-inspired bed with headboard at +Y; leave blanket surface unobstructed
# for the game's animated/clickable bed actor.
box('Bed frame',(0,0,.22),(1.74,2.08,.22),wood,.035)
box('Mattress',(0,0,.43),(1.64,1.98,.22),porcelain,.075)
box('Headboard',(0,.98,.78),(1.74,.10,1.23),wood,.045)
box('Headboard inset',(0,.915,.86),(1.46,.025,.67),fabric_dark,.08)
for x in [-.80,.80]:
    box('Headboard post',(x,.97,.80),(.11,.14,1.48),wood,.045)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,location=(x,.97,1.57)); o=bpy.context.object; o.scale=(.07,.07,.07); o.data.materials.append(wood)
for x in [-.78,.78]:
    for y in [-.91,.91]: box('Bed foot',(x,y,.08),(.10,.10,.16),wood,.02)
# Pillows are supplied by the separate interactive quilt asset.
export('SM_VintageBed')

# Drawer faces and knobs are deliberately large enough to read in a game view.
# Open-front dresser carcass: middle drawer is supplied by interactive actor.
box('Back',(.23,0,.43),(.05,1.48,.86),wood,.01)
for y in [-.71,.71]: box('Side',(0,y,.43),(.51,.06,.86),wood,.01)
for z in [.06,.42,.70,.85]: box('Shelf',(0,0,z),(.51,1.42,.04),wood,.01)
box('Top',(0,0,.90),(.58,1.54,.08),wood,.025)
for z in [.22,.78]:
    box('Drawer front',(-.263,0,z),(.035,1.35,.19),wood,.012)
    for y in [-.40,.40]:
        cylinder('Brass knob',(-.288,y,z),.022,.03,chrome,(0,math.pi/2,0))
for y in [-.63,.63]:
    for x in [-.19,.19]: box('Foot',(x,y,.035),(.08,.10,.07),wood,.012)
export('SM_VintageDresser')

# Empty open-front case; existing interactive door covers the opening.
box('Back',(.285,0,1.0),(.05,1.08,1.96),wood,.015)
for y in [-.51,.51]: box('Side',(0,y,1.0),(.62,.06,1.96),wood,.018)
for z in [.08,1.91]: box('Shelf',(0,0,z),(.62,1.02,.08),wood,.018)
bar('Hanging rail',(.08,-.45,1.65),(.08,.45,1.65),.015,chrome)
box('Crown',(0,0,2.0),(.72,1.20,.10),wood,.025)
box('Plinth',(0,0,.07),(.70,1.16,.14),wood,.025)
export('SM_VintageWardrobe')

# Toilet faces -X; lid is intentionally omitted to keep game's lid interactable.
box('Tank',(.20,0,.70),(.20,.43,.43),porcelain,.055)
box('Tank cap',(.20,0,.93),(.25,.47,.06),porcelain,.025)
box('Pedestal',(-.04,0,.15),(.40,.34,.30),porcelain,.08)
# Use broad oval bowl and visibly dark water inset, so silhouette reads from above.
bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,location=(-.04,0,.30)); o=bpy.context.object; o.name='Bowl'; o.scale=(.30,.23,.11); o.data.materials.append(porcelain)
bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=12,location=(-.07,0,.405)); o=bpy.context.object; o.name='Bowl inset'; o.scale=(.18,.14,.012); o.data.materials.append(cream)
cylinder('Flush',(.20,-.18,.91),.018,.025,chrome)
export('SM_VintageToiletBody')

# Pedestal sink has integral basin and rear taps, sits flush to wall behind +X.
cylinder('Pedestal',(0,0,.36),.10,.72,porcelain,vertices=32)
box('Foot',(0,0,.045),(.31,.30,.09),porcelain,.045)
box('Sink body',(0,0,.77),(.44,.58,.18),porcelain,.075)
box('Backsplash',(.17,0,.88),(.10,.58,.16),porcelain,.035)
# A shallow dark inset gives a legible bowl opening without the flat primitive look.
box('Basin inset',(-.02,0,.868),(.26,.37,.012),cream,.055)
bar('Faucet upright',(.14,0,.92),(.14,0,1.04),.012,chrome)
bar('Faucet spout',(.14,0,1.04),(.02,0,1.04),.012,chrome)
for y in [-.18,.18]: cylinder('Tap',(.12,y,.97),.025,.05,chrome)
export('SM_PedestalSink')

# Kitchen sink base: front -X, centred on sink; open middle reveals drain.
# Counter top deliberately absent above basin, permitting the malady actor there.
for y in [-.79,.79]:
    box('Cabinet base',(0,y,.43),(.62,.48,.86),mint,.018)
    box('Door face',(-.32,y,.40),(.035,.42,.61),mint,.012)
    box('Raised panel',(-.342,y,.40),(.012,.33,.48),fabric_dark,.012)
    box('Panel inset',(-.353,y,.40),(.012,.27,.40),mint,.010)
    cylinder('Cabinet knob',(-.37,y+(.12 if y<0 else -.12),.57),.019,.025,chrome,(0,math.pi/2,0))
    box('Drawer face',(-.324,y,.75),(.035,.42,.13),mint,.012)
    bar('Drawer pull',(-.355,y-.085,.75),(-.355,y+.085,.75),.009,chrome)
    box('Counter slab',(0,y,.89),(.68,.50,.06),porcelain,.02)
box('Toe kick',(.02,0,.06),(.58,2.06,.12),wood,.01)
box('Sink surround',(.03,0,.82),(.62,1.12,.19),porcelain,.045)
box('Basin surface',(-.005,0,.924),(.48,.86,.015),cream,.065)
box('Basin inset',(-.01,0,.934),(.36,.66,.012),chrome,.065)
# Visible exposed drain and supply pipes under apron.
bar('Drain drop',(0,0,.75),(0,0,.45),.032,chrome)
bar('Trap cross',(0,0,.45),(.12,0,.45),.032,chrome)
bar('Trap rise',(.12,0,.45),(.12,0,.61),.032,chrome)
for y in [-.19,.19]:
    bar('Supply',(.23,y,.12),(.23,y,.70),.014,chrome)
    cylinder('Valve',(.23,y,.57),.028,.025,rust,(0,math.pi/2,0))
bar('Faucet stem',(.24,0,.94),(.24,0,1.10),.016,chrome)
bar('Faucet spout',(.24,0,1.10),(.08,0,1.10),.016,chrome)
for y in [-.20,.20]: cylinder('Faucet tap',(.24,y,.98),.027,.04,chrome)
export('SM_KitchenSinkCabinet')

# Retrofit front has centre origin, facing -X; mount on animated actor if possible.
box('Door', (0,0,.91),(.075,.86,1.80),cream,.045)
# horizontal split, enamel accent strip and generous chrome handle
box('Freezer seam',(-.041,0,1.29),(.012,.78,.016),dark,.003)
bar('Upper handle',(-.085,.28,1.38),(-.085,.28,1.62),.013,chrome)
bar('Lower handle',(-.085,.28,.85),(-.085,.28,1.17),.013,chrome)
for z in [.85,1.17,1.38,1.62]: bar('Handle mount',(-.045,.28,z),(-.085,.28,z),.013,chrome)
export('SM_RetroFridgeDoor')

# Enamel kettle with a readable lid, spout and raised carrying handle.
bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,location=(0,0,.12)); o=bpy.context.object; o.name='Kettle body'; o.scale=(.15,.15,.12); o.data.materials.append(cream)
cylinder('Lid',(0,0,.24),.075,.022,chrome); cylinder('Lid knob',(0,0,.26),.025,.025,wood)
bar('Spout',(-.11,0,.16),(-.24,0,.23),.04,cream)
bar('Handle left',(.00,-.11,.18),(.00,-.12,.32),.012,dark)
bar('Handle top',(0,-.12,.32),(0,.12,.32),.012,dark)
bar('Handle right',(0,.12,.32),(0,.11,.18),.012,dark)
export('SM_EnamelKettle')

# Open repair bucket with visible rim and wire bail.
cylinder('Bucket body',(0,0,.13),.14,.26,chrome,vertices=32)
cylinder('Bucket interior',(0,0,.266),.125,.008,dark,vertices=32)
bpy.ops.mesh.primitive_torus_add(major_segments=32,minor_segments=8,location=(0,0,.27),major_radius=.137,minor_radius=.009); bpy.context.object.data.materials.append(chrome)
bar('Handle left',(0,-.14,.21),(0,-.14,.36),.005,dark)
bar('Handle grip',(0,-.14,.36),(0,.14,.36),.008,wood)
bar('Handle right',(0,.14,.36),(0,.14,.21),.005,dark)
export('SM_RepairBucket')

# Framed worn picture: a modest atmospheric wall prop.
box('Frame',(0,0,.35),(.045,.54,.70),wood,.025)
box('Mat',(-.028,0,.35),(.015,.43,.58),cream,.012)
box('Picture',(-.038,0,.35),(.01,.35,.50),fabric_dark,.008)
export('SM_FramedPicture')

# A pair of gathered curtains on a brass rail, front -X, back +X, bottom at zero.
# Pleats are sculpted vertex geometry, with painted fabric material slots.
def curtain(name,y0,y1):
    verts=[]; faces=[]; cols=32; rows=12
    for j in range(rows+1):
        z=.06+2.10*j/rows
        for i in range(cols+1):
            t=i/cols; y=y0+(y1-y0)*t
            x=.035*math.sin(t*math.pi*12)+.012*math.sin(t*math.pi*24)+.008*math.sin(z*2+t*3)
            verts.append((x,y,z+.012*math.cos(t*math.pi*12)))
    for j in range(rows):
        for i in range(cols):
            a=j*(cols+1)+i; faces.append((a,a+1,a+cols+2,a+cols+1))
    m=bpy.data.meshes.new(name); m.from_pydata(verts,[],faces);m.update()
    ob=bpy.data.objects.new(name,m);bpy.context.collection.objects.link(ob);ob.data.materials.append(fabric)
    for p in m.polygons:p.use_smooth=True
curtain('Left drape',-1.04,-.48); curtain('Right drape',.48,1.04)
bar('Curtain rail',(0,-1.14,2.22),(0,1.14,2.22),.018,chrome)
for y in [-1.19,1.19]:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,location=(0,y,2.22)); o=bpy.context.object;o.scale=(.045,.045,.045);o.data.materials.append(chrome)
for y in [-.76,.76]:
    box('Tieback',(-.03,y,1.02),(.08,.54,.045),wood,.015)
export('SM_GatheredCurtains')

# Classic fringed floor lamp. Geometry stays readable at gameplay distance.
cylinder('Floor base',(0,0,.025),.19,.05,wood,vertices=32)
cylinder('Pole',(0,0,.74),.022,1.43,chrome)
# Turned shade, two rings with capped top and bottom.
def tapered_shell(name,z0,z1,r0,r1,material,steps=32):
    verts=[]
    for z,r in [(z0,r0),(z1,r1)]:
        verts.extend([(r*math.cos(i*2*math.pi/steps),r*math.sin(i*2*math.pi/steps),z) for i in range(steps)])
    faces=[(i,(i+1)%steps,(i+1)%steps+steps,i+steps) for i in range(steps)]
    faces.append(tuple(range(steps,steps*2)))
    m=bpy.data.meshes.new(name);m.from_pydata(verts,[],faces);m.update();o=bpy.data.objects.new(name,m);bpy.context.collection.objects.link(o);o.data.materials.append(material)
    for p in m.polygons:p.use_smooth=True
    return o
tapered_shell('Fabric shade',1.35,1.66,.29,.16,cream)
for i in range(16):
    a=i*math.pi*2/16; x,y=.284*math.cos(a),.284*math.sin(a)
    bar('Tassel',(x,y,1.36),(x,y,1.29),.006,wood)
export('SM_VintageFloorLamp')

# Tall mismatched bookshelf; integrated large books, framed fronts remain readable.
box('Back panel',(0,0,.96),(.035,1.05,1.88),wood,.008)
for y in [-.50,.50]: box('Side',(0,y,.98),(.32,.045,1.96),wood,.015)
for z in [.06,.48,.91,1.34,1.91]: box('Shelf',(0,0,z),(.34,1.05,.055),wood,.012)
for shelf in range(4):
    for i in range(6):
        y=-.40+i*.15; h=.23+.025*((i+shelf)%4)
        book=box('Old book',(-.055,y,.09+shelf*.43+h/2),(.20,.10,h),[cream,fabric_dark,mint,rust][(i+shelf)%4],.006)
        if i==5: book.rotation_euler[0]=.08
export('SM_OldBookshelf')

# Cast-iron sectional radiator, mounting side +X, front -X.
for i in range(11):
    y=-.50+i*.10
    box('Radiator fin',(0,y,.39),(.15,.075,.72),chrome,.034)
    box('Fin inset',(-.080,y,.40),(.018,.040,.48),dark,.012)
for z in [.10,.65]: bar('Radiator header',(0,-.58,z),(0,.58,z),.045,chrome)
for y in [-.48,.48]: box('Radiator foot',(0,y,.035),(.22,.09,.07),chrome,.02)
bar('Valve stem',(0,.58,.63),(0,.69,.63),.025,chrome)
cylinder('Valve wheel',(0,.69,.68),.055,.02,wood)
export('SM_OldRadiator')

# Worn woven rug: large soft color shapes, with low relief border and tassels.
box('Rug field',(0,0,.012),(1.90,2.80,.024),fabric_dark,.02)
for y in [-1.31,1.31]: box('Long woven border',(0,y,.026),(1.76,.09,.006),rust,.004)
for x in [-.87,.87]: box('Short woven border',(x,0,.026),(.09,2.54,.006),rust,.004)
box('Central field',(0,0,.027),(1.45,2.10,.006),fabric,.008)
# Simple diamond is geometry, not a painted-on stripe of wear.
for angle in [-1,1]:
    for y in [-.45,.45]:
        o=box('Diamond motif',(0,y,.032),(.06,1.10,.006),cream,.004);o.rotation_euler[2]=angle*.72
for x in [-.8+i*.1 for i in range(17)]:
    for y in [-1.42,1.42]: box('Fringe',(x,y,.009),(.018,.09,.008),cream,.003)
export('SM_WovenRug')

# Bathroom towel rail and draped towel. Mounted back +X, front -X, origin bottom.
bar('Rail',(.02,-.32,.65),(.02,.32,.65),.012,chrome)
for y in [-.34,.34]:
    bar('Wall mount',(.02,y,.65),(.10,y,.65),.018,chrome)
    cylinder('Rosette',(.10,y,.65),.04,.015,chrome,(0,math.pi/2,0))
box('Towel fold',(-.015,0,.42),(.07,.48,.45),cream,.025)
box('Towel trim',(-.057,0,.23),(.01,.45,.03),mint,.003)
export('SM_TowelRail')

# A framed, aged wall mirror with a shelf and functional silhouette.
box('Mirror frame',(0,0,.52),(.08,.62,1.04),wood,.045)
box('Reflective glass',(-.045,0,.53),(.012,.49,.87),chrome,.045)
box('Little shelf',(-.10,0,.06),(.20,.72,.06),wood,.015)
export('SM_BathMirror')

# Faded chipped pink wall tile feature: preserve a separate interactive malady actor
# and locate this thin visible panel just behind/in front of it with trace collision off.
pink=mat('Pink_Tile',(.67,.31,.35),.48)
grout=mat('Grout',(.63,.54,.45))
crack=mat('Tile_Crack',(.16,.095,.075))
box('Grout bed',(0,0,.90),(.025,2.20,1.80),grout,.002)
for row in range(8):
    for col in range(10):
        y=-.99+col*.22;z=.113+row*.225
        box('Pink tile',(-.017,y,z),(.012,.205,.21),pink,.006)
# Long break across several tiles, represented by hairline strips over their face.
pts=[(-.026,-.42,1.52),(-.026,-.37,1.33),(-.026,-.45,1.19),(-.026,-.32,1.03),(-.026,-.35,.84),(-.026,-.19,.68)]
for i in range(len(pts)-1): bar('Crack',pts[i],pts[i+1],.004,crack)
bar('Crack branch',pts[2],(-.026,-.60,1.06),.003,crack)
export('SM_CrackedPinkTilePanel')

# Bedside lamp; leave its local switch area unobstructed for game interaction.
cylinder('Foot',(0,0,.022),.12,.044,wood,vertices=32)
cylinder('Stem',(0,0,.19),.025,.34,chrome)
bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,location=(0,0,.18)); o=bpy.context.object;o.name='Ceramic base';o.scale=(.085,.085,.13);o.data.materials.append(pink)
tapered_shell('Shade',.31,.57,.17,.095,cream)
export('SM_BedsideLamp')

# Basket with rolled spare towels: broad weave bands instead of microdetail.
cylinder('Basket',(0,0,.22),.23,.42,wood,vertices=24)
for z in [.07,.17,.27,.37]:
    bpy.ops.mesh.primitive_torus_add(major_segments=32,minor_segments=8,location=(0,0,z),major_radius=.229,minor_radius=.008);bpy.context.object.data.materials.append(cream)
for x,y in [(-.09,-.03),(.08,.03)]:
    cylinder('Rolled towel',(x,y,.44),.09,.12,cream,(math.pi/2,0,0))
export('SM_TowelBasket')

# Bedroom damp stain silhouette; thin visual applique, no collision, for placement
# around (not over) the existing mold malady's trace target.
mildew=mat('Mildew',(.12,.18,.13)); mildew_light=mat('Damp',(.29,.32,.22))
# Overlapping, hand-shaped flat silhouettes with narrow drips. All points are
# in Y/Z, and successive layers sit less than a millimetre apart.
def stain_patch(name, coords, depth, material):
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata([(depth,y,z) for y,z in coords],[],[tuple(range(len(coords)))])
    mesh.update();obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);obj.data.materials.append(material)
# Layer runs counter-clockwise in world-facing view: normal towards -X.
stain_patch('Diffuse irregular damp', [(-.77,.81),(-.69,.90),(-.73,1.01),(-.64,1.07),(-.67,1.20),(-.53,1.25),(-.42,1.22),(-.31,1.32),(-.20,1.26),(-.09,1.33),(.04,1.27),(.16,1.31),(.27,1.22),(.40,1.25),(.48,1.13),(.62,1.12),(.66,.98),(.60,.89),(.67,.78),(.57,.72),(.53,.61),(.44,.65),(.39,.48),(.32,.60),(.22,.53),(.14,.64),(.05,.53),(-.04,.62),(-.13,.48),(-.22,.55),(-.29,.37),(-.35,.56),(-.45,.51),(-.50,.66),(-.60,.61),(-.63,.74)],0,mildew_light)
stain_patch('Deep connected mildew',[(-.63,.88),(-.58,.98),(-.60,1.09),(-.49,1.16),(-.40,1.12),(-.31,1.24),(-.19,1.18),(-.10,1.25),(.03,1.18),(.15,1.23),(.23,1.13),(.35,1.16),(.39,1.03),(.53,1.01),(.49,.90),(.55,.82),(.44,.77),(.37,.84),(.32,.68),(.23,.77),(.13,.68),(.04,.78),(-.05,.66),(-.14,.77),(-.23,.65),(-.32,.72),(-.40,.64),(-.47,.78),(-.57,.75)],-.001,mildew)
stain_patch('Uneven damp fringe left',[(-.65,.79),(-.59,.81),(-.54,.67),(-.49,.62),(-.50,.47),(-.46,.40),(-.48,.22),(-.53,.39),(-.57,.46),(-.58,.61)],-.002,mildew_light)
stain_patch('Damp long streak',[(-.26,.70),(-.18,.73),(-.17,.53),(-.12,.40),(-.14,.12),(-.19,.05),(-.20,.34),(-.25,.43)],-.002,mildew_light)
stain_patch('Damp narrow streak',[(.23,.73),(.28,.77),(.29,.60),(.34,.49),(.31,.32),(.27,.46),(.24,.49)],-.002,mildew_light)
stain_patch('Dark jagged vein',[(-.49,1.02),(-.36,1.12),(-.22,1.06),(-.12,1.17),(.00,1.09),(.11,1.15),(.19,1.02),(.35,1.06),(.25,.94),(.13,.99),(.03,.90),(-.11,.98),(-.23,.89),(-.36,.98)],-.003,mildew)
export('SM_DampStain')

# Single hinged wardrobe door; centered horizontally with origin at floor.
# Front faces -X. Offset it from the gameplay pivot to place its hinge.
box('Door slab',(0,0,.98),(.05,1.06,1.96),wood,.02)
for y in [-.265,.265]:
    box('Raised panel',(-.031,y,1.02),(.015,.43,1.62),fabric_dark,.018)
    box('Inner panel',(-.041,y,1.02),(.012,.35,1.50),wood,.015)
# Handle at local -Y, opposite hinge after 180 degree relative rotation.
cylinder('Door knob',(-.066,-.43,1.02),.029,.038,chrome,(0,math.pi/2,0))
export('SM_WardrobeDoor')

# Drawer centred at origin, front -X; carcass adds depth during slide animation.
box('Drawer case',(0,0,0),(.26,1.24,.19),wood,.012)
box('Drawer face',(-.14,0,0),(.035,1.30,.24),wood,.012)
box('Face inset',(-.162,0,0),(.012,1.12,.16),fabric_dark,.009)
for y in [-.38,.38]:
    cylinder('Drawer knob',(-.182,y,0),.026,.03,chrome,(0,math.pi/2,0))
export('SM_DresserDrawer')

# Tartan cushions: geometric woven stripes across outward-facing face, not surface damage.
plaid_red=mat('Plaid_Rose',(.43,.18,.17)); plaid_gold=mat('Plaid_Gold',(.76,.53,.25)); plaid_cream=mat('Plaid_Cream',(.79,.70,.55))
box('Cushion', (0,0,.23),(.18,.46,.46),plaid_red,.08)
for y in [-.13,0,.13]: box('Vertical weave',(-.093,y,.23),(.009,.025,.35),plaid_gold,.004)
for z in [.12,.23,.34]: box('Horizontal weave',(-.098,0,z),(.009,.35,.023),plaid_cream,.004)
export('SM_PlaidCushion')

# Soft folded throw with uneven layered cloth and blanket stitch details.
box('Folded throw',(0,0,.07),(.62,.44,.14),plaid_cream,.06)
box('Top fold',(-.02,0,.145),(.54,.42,.045),plaid_red,.025)
for y in [-.14,-.07,0,.07,.14]: box('Woven band',(-.02,y,.169),(.49,.018,.005),plaid_gold,.003)
for i in range(7):
    y=-.18+i*.06;bar('Tassel',(-.31,y,.085),(-.36,y,.055),.004,plaid_cream)
export('SM_FoldedThrow')

# Several old hardcover books, uneven stacked covers and visible paper blocks.
for idx,(x,y,z,angle) in enumerate([(0,0,.025,.04),(.02,-.02,.077,-.08),(-.015,.015,.128,.12)]):
    cover=[wood,plaid_red,fabric_dark][idx]
    for part,loc,dims,material in [('Pages',(x,y,z),(.30,.21,.037),plaid_cream),('Lower cover',(x,y,z-.023),(.32,.23,.01),cover),('Upper cover',(x,y,z+.023),(.32,.23,.01),cover)]:
        o=box(part,loc,dims,material,.004);o.rotation_euler[2]=angle
export('SM_StackedBooks')

# A small repair caddy, brushes and screwdriver tell a renovation story.
box('Caddy floor',(0,0,.045),(.42,.28,.07),wood,.012)
for y in [-.13,.13]: box('Caddy side',(0,y,.14),(.42,.025,.20),wood,.012)
for x in [-.20,.20]: box('Caddy end',(x,0,.14),(.025,.26,.20),wood,.012)
for x in [-.15,.15]: bar('Caddy uprights',(x,0,.20),(x,0,.35),.014,wood)
bar('Caddy handle',(-.15,0,.35),(.15,0,.35),.014,wood)
bar('Screwdriver shaft',(-.06,-.06,.14),(-.06,-.06,.29),.008,chrome)
bar('Screwdriver grip',(-.06,-.06,.29),(-.06,-.06,.36),.018,plaid_red)
box('Paintbrush handle',(.06,.04,.23),(.035,.025,.23),wood,.008)
box('Paintbrush ferrule',(.06,.04,.36),(.045,.035,.05),chrome,.005)
box('Paintbrush bristles',(.06,.04,.41),(.05,.04,.07),plaid_cream,.008)
export('SM_RepairCaddy')

# Pleated table lamp, with ceramic base distinct from floor lamp.
cylinder('Foot',(0,0,.018),.10,.036,chrome,vertices=32)
bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,location=(0,0,.14));o=bpy.context.object;o.scale=(.09,.09,.13);o.data.materials.append(plaid_red)
cylinder('Stem',(0,0,.27),.015,.12,chrome)
tapered_shell('Shade',.30,.52,.16,.09,plaid_cream)
for i in range(12):
    a=i*math.pi*2/12;bar('Shade seam',(.159*math.cos(a),.159*math.sin(a),.30),(.089*math.cos(a),.089*math.sin(a),.52),.002,plaid_gold)
export('SM_VintageTableLamp')

# Cosmetic damaged fusebox overlay. Origin centered; front -X. Place forward
# of interactive Body and disable collision so its original trace remains available.
wire_red=mat('Wire_Red',(.42,.12,.09)); wire_yellow=mat('Wire_Ochre',(.68,.46,.16)); wire_blue=mat('Wire_Blue',(.20,.31,.35))
box('Panel recessed back',(0,0,0),(.035,.59,.78),dark,.015)
for y in [-.30,.30]: box('Metal vertical surround',(-.026,y,0),(.06,.045,.83),chrome,.01)
for z in [-.39,.39]: box('Metal horizontal surround',(-.026,0,z),(.06,.63,.045),chrome,.01)
for z in [-.19,0,.19]:
    for y in [-.13,.13]:
        cylinder('Fuse socket',(-.052,y,z),.052,.025,wood,(0,math.pi/2,0))
        cylinder('Fuse glass',(-.070,y,z),.035,.014,cream,(0,math.pi/2,0))
for i,material in enumerate([wire_red,wire_yellow,wire_blue]):
    y=-.15+i*.13
    pts=[(-.065,y,-.28),(-.08,y+.03,-.34),(-.09,y-.04,-.43),(-.075,y+.05,-.54)]
    for a,b in zip(pts,pts[1:]): bar('Loose insulated wire',a,b,.008,material)
    bar('Exposed wire tip',pts[-1],(-.075,y+.075,-.565),.004,chrome)
# Door hinged open to one side, angled toward viewer.
o=box('Open panel door',(-.14,.49,.00),(.055,.36,.74),chrome,.015);o.rotation_euler[2]=-.35
box('Door latch',(-.23,.62,0),(.03,.04,.08),rust,.008)
export('SM_DamagedFuseboxOverlay')

# Broad localized plaster discoloration/paint-loss silhouettes are thin single-plane
# shapes: painterly value patches, not physical thick flakes. Front is -X.
plaster_base=mat('Exposed_Plaster',(.57,.47,.36)); plaster_light=mat('Old_Paint',(.75,.66,.52)); plaster_dark=mat('Damp_Edge',(.38,.32,.26))
def flat_patch(name,pts,x,material):
    m=bpy.data.meshes.new(name);m.from_pydata([(x,y,z) for y,z in pts],[],[tuple(range(len(pts)))]);m.update()
    o=bpy.data.objects.new(name,m);bpy.context.collection.objects.link(o);o.data.materials.append(material)
flat_patch('Large loss',[(-.67,-.46),(-.57,-.28),(-.62,-.11),(-.42,.05),(-.38,.24),(-.16,.31),(.02,.25),(.16,.37),(.36,.31),(.45,.12),(.64,.07),(.68,-.12),(.53,-.23),(.48,-.41),(.25,-.45),(.08,-.55),(-.09,-.47),(-.30,-.56),(-.46,-.47)],0,plaster_base)
flat_patch('Exposed ground',[(-.45,-.29),(-.48,-.12),(-.30,-.02),(-.23,.13),(-.04,.15),(.07,.08),(.27,.20),(.39,.08),(.42,-.11),(.29,-.23),(.11,-.21),(-.04,-.36),(-.22,-.28)],-.002,plaster_light)
flat_patch('Damp lower edge',[(-.51,-.34),(-.33,-.33),(-.23,-.40),(-.05,-.35),(.08,-.43),(.27,-.35),(.47,-.33),(.35,-.43),(.12,-.49),(-.10,-.49),(-.31,-.51)],-.004,plaster_dark)
export('SM_PlasterDamage')

# Soft patchwork quilt: centered at origin, nominal top z=0, edges drape down.
# Dimensions 164×140 cm before modest droop; styled as broad textiles not impasto.
quilt_rose=mat('Quilt_Rose',(.55,.29,.30)); quilt_sage=mat('Quilt_Sage',(.43,.47,.34)); quilt_cream=mat('Quilt_Ivory',(.76,.67,.53))
verts=[];faces=[];nx=20;ny=18
for j in range(ny+1):
    y=-.70+1.40*j/ny
    for i in range(nx+1):
        x=-.82+1.64*i/nx
        edge=max(0,(abs(x)-.69)/.13, (abs(y)-.57)/.13)
        z=.014*math.sin(x*9+y*2)+.012*math.sin(y*11-x*2)-.12*edge*edge
        verts.append((x,y,z))
for j in range(ny):
    for i in range(nx):
        a=j*(nx+1)+i;faces.append((a,a+1,a+nx+2,a+nx+1))
m=bpy.data.meshes.new('Rumpled quilt');m.from_pydata(verts,[],faces);m.update();o=bpy.data.objects.new('Rumpled quilt',m);bpy.context.collection.objects.link(o)
m.materials.append(quilt_rose)
uv=m.uv_layers.new(name='UVMap')
for p in m.polygons:
    p.use_smooth=True
    p.material_index=0
    for loop_index in p.loop_indices:
        vertex_index=m.loops[loop_index].vertex_index
        uv.data[loop_index].uv=((vertex_index % (nx+1))/nx, (vertex_index // (nx+1))/ny)
# Accent pillows have their own UVs generated by the cube primitive.
for x,material in [(-.39,quilt_cream),(.39,quilt_cream)]:
    box('Pillow',(x,.47,.11),(.60,.30,.16),material,.075)
export('SM_RumpledQuilt')

# Small old wood nightstand; drawer fronts and handles remain visible from -X.
box('Case',(0,0,.27),(.43,.42,.50),wood,.02)
box('Top',(0,0,.54),(.47,.46,.055),wood,.02)
for x in [-.16,.16]:
    for y in [-.15,.15]: box('Foot',(x,y,.03),(.06,.06,.06),wood,.012)
for z in [.19,.36]:
    box('Drawer face',(-.225,0,z),(.025,.35,.14),wood,.009)
    box('Inset',(-.241,0,z),(.01,.28,.09),fabric_dark,.006)
    cylinder('Knob',(-.257,0,z),.023,.025,chrome,(0,math.pi/2,0))
export('SM_VintageNightstand')

# 1950s base cabinetry. Nominal cabinet body 60cm deep, 86cm high; handles
# protrude in front of the -X face. Countertop is separate in Unreal.
def base_cabinet(name,width):
    if width < .90:
        # Cavity across the upper cabinet for a separate animated drawer.
        box('Lower case',(.01,0,.29),(.58,width,.58),mint,.014)
        box('Drawer back',(.27,0,.71),(.06,width,.28),mint,.01)
        for sy in [-1,1]: box('Drawer side',(.01,sy*(width/2-.015),.71),(.58,.03,.28),mint,.01)
    else:
        box('Case',(.01,0,.43),(.58,width,.86),mint,.014)
    box('Recessed toe kick',(.015,0,.055),(.53,width-.03,.11),fabric_dark,.008)
    for sign in [-1,1]:
        y=sign*width*.25; doorw=width*.46
        box('Door',(-.292,y,.36),(.025,doorw,.55),mint,.012)
        box('Panel frame',(-.307,y,.36),(.008,doorw-.06,.44),fabric_dark,.008)
        box('Inset face',(-.313,y,.36),(.008,doorw-.11,.37),mint,.008)
        cylinder('Door knob',(-.328,y-sign*(doorw*.34),.54),.018,.022,chrome,(0,math.pi/2,0))
        if width >= .90:
            box('Drawer',(-.292,y,.73),(.025,doorw,.14),mint,.009)
            bar('Drawer handle',(-.32,y-.065,.73),(-.32,y+.065,.73),.008,chrome)
    export(name)
base_cabinet('SM_BaseCabinet96',.96)
base_cabinet('SM_BaseCabinet86',.86)

# Wall mounted cupboard. Origin bottom center; front -X.
box('Upper case',(0,0,.36),(.30,.94,.72),mint,.018)
box('Crown',(0,0,.73),(.33,.99,.06),wood,.01)
for sign in [-1,1]:
    y=sign*.235
    box('Upper door',(-.155,y,.36),(.025,.45,.65),mint,.012)
    box('Panel frame',(-.171,y,.36),(.008,.37,.55),fabric_dark,.009)
    box('Inset face',(-.178,y,.36),(.008,.30,.48),mint,.008)
    cylinder('Knob',(-.192,y-sign*.14,.27),.018,.025,chrome,(0,math.pi/2,0))
export('SM_UpperKitchenCabinet')

# A rail, hooks and two recognisable pans dress a kitchen wall. Front -X.
box('Wall backplate',(.065,0,.65),(.02,.92,.035),wood,.006)
bar('Rail',(0,-.46,.65),(0,.46,.65),.013,chrome)
for y in [-.45,.45]: bar('Wall bracket',(0,y,.65),(.07,y,.65),.018,chrome)
for y in [-.23,.20]:
    bar('Hook',(0,y,.65),(-.03,y,.55),.008,chrome)
    # disk normal towards -X with concentric contrasting inner pan face
    cylinder('Copper pan',(-.04,y,.35),.14,.05,rust,(0,math.pi/2,0),vertices=32)
    cylinder('Pan inner',(-.069,y,.35),.11,.008,chrome,(0,math.pi/2,0),vertices=32)
    bar('Pan handle',(-.04,y,.49),(-.04,y,.56),.015,wood)
bpy.context.view_layer.update()
export('SM_HangingPans')

# Center-origin moving drawer; front -X, nominal 35×80×24 cm.
box('Drawer case',(0,0,0),(.32,.75,.19),wood,.012)
box('Drawer front',(-.17,0,0),(.025,.80,.24),mint,.009)
box('Drawer face inset',(-.185,0,0),(.008,.70,.16),fabric_dark,.008)
box('Drawer center',(-.19,0,0),(.008,.64,.11),mint,.006)
bar('Drawer pull',(-.21,-.10,0),(-.21,.10,0),.009,chrome)
export('SM_KitchenDrawer')

# Midcentury coffee table, carved lip, lower shelf and four splayed legs.
box('Tabletop',(0,0,.40),(.75,1.40,.07),wood,.025)
box('Top inset',(0,0,.439),(.65,1.30,.008),cream,.01)
box('Lower shelf',(0,0,.15),(.58,1.19,.035),wood,.012)
for x in [-.29,.29]:
    for y in [-.60,.60]:
        bar('Tapered table leg',(x*1.10,y*1.06,0),(x,y,.38),.027,wood)
export('SM_VintageCoffeeTable')

# Low TV console cabinet with panelled drawers, suitable for a vintage screen.
box('Console case',(0,0,.27),(.48,1.72,.48),wood,.025)
box('Console top',(0,0,.53),(.52,1.80,.06),wood,.02)
for x in [-.16,.16]:
    for y in [-.70,.70]: bar('Console foot',(x,y,.02),(x,y,.11),.025,wood)
for y in [-.55,0,.55]:
    box('Door',(-.25,y,.28),(.025,.50,.34),wood,.012)
    box('Door inset',(-.266,y,.28),(.008,.40,.25),fabric_dark,.008)
    box('Inner face',(-.273,y,.28),(.008,.35,.20),wood,.006)
    cylinder('Knob',(-.29,y,.28),.018,.024,chrome,(0,math.pi/2,0))
export('SM_VintageTVStand')

# Hollow rectangular frame around existing interactive TV screen. Origin centered;
# front -X, aperture 128cm wide ×72cm high and no middle obstructing the click actor.
for y in [-.69,.69]:box('Side bezel',(0,y,0),(.12,.10,.84),wood,.022)
for z in [-.39,.39]:box('Top or bottom bezel',(0,0,z),(.12,1.30,.06),wood,.018)
for y in [-.45,0,.45]:cylinder('TV dial',(-.075,y,-.39),.022,.025,chrome,(0,math.pi/2,0))
export('SM_VintageTVFrame')

# Base and stem only, separate from existing toggleable shade actor.
cylinder('Foot',(0,0,.025),.18,.05,wood,vertices=32)
cylinder('Foot ring',(0,0,.055),.11,.018,chrome,vertices=32)
cylinder('Pole',(0,0,.76),.018,1.42,chrome,vertices=24)
export('SM_FloorLampBase')
# Interactive lamp shade centered on origin so actor keeps same transform.
tapered_shell('Shade',-.17,.17,.23,.14,cream)
for i in range(12):
    a=i*math.pi*2/12
    bar('Pleat seam',(.228*math.cos(a),.228*math.sin(a),-.17),(.14*math.cos(a),.14*math.sin(a),.17),.003,wood)
export('SM_FloorLampShade')

# Leafy houseplant with modeled pot, soil, branching stalks and broad leaves.
leaf=mat('Leaf_Green',(.18,.31,.16)); leaf_light=mat('Leaf_Light',(.32,.43,.22)); pot=mat('Pot_Terracotta',(.48,.25,.15))
tapered_shell('Terracotta pot',0,.42,.16,.22,pot)
cylinder('Soil',(0,0,.42),.20,.015,wood,vertices=32)
bpy.ops.mesh.primitive_torus_add(major_segments=32,minor_segments=8,location=(0,0,.41),major_radius=.21,minor_radius=.018);bpy.context.object.data.materials.append(pot)
for i in range(9):
    a=i*2*math.pi/9; r=.22+.04*(i%3);z=.67+.09*(i%4)
    tip=(r*math.cos(a),r*math.sin(a),z)
    bar('Stem',(0,0,.41),tip,.009,leaf)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,location=tip);o=bpy.context.object;o.name='Leaf'
    o.scale=(.08,.15,.035);o.rotation_euler=(.25*math.sin(a),.3*math.cos(a),a);o.data.materials.append(leaf_light if i%3==0 else leaf)
export('SM_LeafyPottedPlant')

# Small vintage kitchen table; bottom origin, top 74 cm from floor.
box('Tabletop',(0,0,.71),(.90,1.30,.06),wood,.02)
box('Table apron',(0,0,.64),(.78,1.18,.10),wood,.02)
for x in [-.35,.35]:
    for y in [-.54,.54]:
        box('Table leg',(x,y,.32),(.07,.07,.64),wood,.008)
export('SM_VintageDiningTable')

# Bentwood inspired chair. Back at +X, seat faces -X, bottom origin.
box('Seat',(0,0,.46),(.42,.42,.07),wood,.055)
box('Seat cushion',(-.015,0,.50),(.34,.34,.035),plaid_red,.05)
for x in [-.15,.15]:
    for y in [-.15,.15]:
        bar('Chair leg',(x*1.16,y*1.16,.01),(x,y,.44),.022,wood)
for y in [-.18,.18]: bar('Back upright',(.16,y,.42),(.16,y,.80),.022,wood)
# Smooth silhouette and vertical back slats.
box('Rounded top rail',(.16,0,.82),(.07,.42,.11),wood,.055)
for y in [-.10,0,.10]:bar('Back slat',(.16,y,.53),(.16,y,.79),.015,wood)
export('SM_VintageDiningChair')

# Fruit bowl with a recessed interior: ring shell and three bright fruit silhouettes.
fruit_red=mat('Fruit_Red',(.55,.16,.11)); fruit_gold=mat('Fruit_Gold',(.85,.58,.12)); fruit_green=mat('Fruit_Green',(.35,.45,.14))
# First neutral anchor gives consistent local orientation.
steps=32; rings=[(.04,.075),(.11,.015),(.17,.07),(.18,.12),(.155,.12),(.125,.07),(.045,.045)]
vertices=[]
for r,z in rings:vertices.extend([(r*math.cos(i*2*math.pi/steps),r*math.sin(i*2*math.pi/steps),z) for i in range(steps)])
faces=[]
for j in range(len(rings)-1):
    for i in range(steps):faces.append((j*steps+i,j*steps+(i+1)%steps,(j+1)*steps+(i+1)%steps,(j+1)*steps+i))
mesh=bpy.data.meshes.new('Bowl');mesh.from_pydata(vertices,[],faces);mesh.update();obj=bpy.data.objects.new('Bowl',mesh);bpy.context.collection.objects.link(obj);obj.data.materials.append(cream)
for poly in mesh.polygons:poly.use_smooth=True
for x,y,z,c in [(-.07,-.02,.14,fruit_red),(.04,-.05,.14,fruit_gold),(.01,.08,.14,fruit_green)]:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,location=(x,y,z));o=bpy.context.object;o.name='Fruit';o.scale=(.06,.06,.055);o.data.materials.append(c)
    cylinder('Stem',(x,y,z+.06),.004,.024,wood,vertices=10)
export('SM_FruitBowl')

# Oval lid centred on origin for existing hinge actor; long axis local X,
# hinge side at -X, visible surface z≈0 and room-facing tip at +X.
bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,location=(0,0,0));o=bpy.context.object;o.name='Oval lid';o.scale=(.22,.19,.022);o.data.materials.append(porcelain)
box('Rear hinge',(-.205,0,-.005),(.04,.30,.035),chrome,.012)
export('SM_ToiletLid')

# Tub filler, actor-local +X projects toward room (actor yaw 180 in level).
# Origin at fixture mounting point, faucet extends 26cm toward +X.
box('Mount plate',(-.01,0,0),(.02,.08,.08),chrome,.012)
cylinder('Wall collar',(0,0,0),.045,.035,chrome,(0,math.pi/2,0))
bar('Spout',(.005,0,0),(.24,0,0),.025,chrome)
bar('Curved lip',(.24,0,0),(.26,0,-.035),.025,chrome)
for y in [-.13,.13]:
    bar('Tap stem',(0,y,0),(.06,y,0),.016,chrome)
    cylinder('Tap cross',(.07,y,0),.04,.025,chrome,(0,math.pi/2,0))
export('SM_TubFaucet')

# Molded apartment entry, origin centered at floor, door plane Y width 116cm,
# front -X; separate closed actor remains noninteractive.
box('Door slab',(0,0,1.09),(.07,1.16,2.18),wood,.025)
for y in [-.28,.28]:
    for z,h in [(.52,.69),(1.54,.78)]:
        box('Molding',(-.042,y,z),(.018,.47,h),fabric_dark,.012)
        box('Raised door panel',(-.053,y,z),(.012,.39,h-.08),wood,.01)
# knob on local +Y so yaw -90 places it near the historic X=230 side.
cylinder('Backplate',(-.07,.40,1.0),.06,.018,chrome,(0,math.pi/2,0))
bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,location=(-.10,.40,1.0));o=bpy.context.object;o.scale=(.035,.035,.035);o.data.materials.append(chrome)
export('SM_MoldedFrontDoor')
