import bpy, math, random, os
from mathutils import Vector
from pathlib import Path

BASE=Path(__file__).resolve().parent.parent
random.seed(413)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for block in bpy.data.materials: bpy.data.materials.remove(block)

def mat(name, color, rough=.8, tex=None):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=rough
    if tex:
        image=m.node_tree.nodes.new('ShaderNodeTexImage'); image.image=bpy.data.images.load(str(BASE/'textures'/tex),check_existing=True); image.image.filepath='//../textures/'+tex
        m.node_tree.links.new(image.outputs['Color'],bs.inputs['Base Color'])
    return m
clay=mat('Painted weathered terracotta',(0.55,.26,.14),.87,'terracotta.png')
leafmat=mat('Variegated pothos painted leaf',(0.25,.38,.09),.72,'pothos-leaf.png')
stemmat=mat('Olive green stems',(.24,.31,.065),.9)
soilmat=mat('Dark potting soil',(.075,.042,.024),1)
cream=mat('Worn cream slip decoration',(.68,.54,.36),.92)

def lathe(name, profile, material, n=64):
    verts=[]; faces=[]
    for radius,z in profile:
        for j in range(n):
            a=2*math.pi*j/n; verts.append((radius*math.cos(a),radius*math.sin(a),z))
    for i in range(len(profile)-1):
        for j in range(n):
            a=i*n+j;b=i*n+(j+1)%n;c=(i+1)*n+(j+1)%n;d=(i+1)*n+j; faces.append((a,b,c,d))
    mesh=bpy.data.meshes.new(name); mesh.from_pydata(verts,[],faces); mesh.update(); obj=bpy.data.objects.new(name,mesh); bpy.context.collection.objects.link(obj); obj.data.materials.append(material)
    uv=mesh.uv_layers.new(name='UVMap')
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            vi=mesh.loops[li].vertex_index; j=vi%n; i=vi//n; u=j/n
            if j==0 and any(mesh.loops[l].vertex_index%n==n-1 for l in poly.loop_indices): u=1
            uv.data[li].uv=(u,profile[i][1]/.22)
        poly.use_smooth=True
    return obj
pot=lathe('Pot body and lip',[(.065,.005),(.071,.008),(.090,.171),(.098,.176),(.099,.188),(.096,.195),(.083,.195),(.081,.184)],clay)
lathe('Soil',[(.001,.176),(.081,.176)],soilmat)

def curve(name,points,radius,material):
    cv=bpy.data.curves.new(name,'CURVE'); cv.dimensions='3D'; cv.resolution_u=2; cv.bevel_depth=radius; cv.bevel_resolution=2
    if name.startswith(('Canopy stem','Low stem','Trailing vine')):
        sp=cv.splines.new('BEZIER'); sp.bezier_points.add(len(points)-1)
        for point,co in zip(sp.bezier_points,points):
            point.co=co; point.handle_left_type='AUTO'; point.handle_right_type='AUTO'
        sp.resolution_u=4
    else:
        sp=cv.splines.new('POLY'); sp.points.add(len(points)-1)
        for point,co in zip(sp.points,points): point.co=(*co,1)
    ob=bpy.data.objects.new(name,cv); bpy.context.collection.objects.link(ob); ob.data.materials.append(material); return ob
# Pale narrow hand-painted slip line around the shoulder; intentionally modest.
pts=[]
for i in range(257):
    a=2*math.pi*i/256; z=.137+.0035*math.cos(9*a); radius=.0871
    pts.append((radius*math.cos(a),radius*math.sin(a),z))
curve('Cream slip line',pts,.00065,cream)

# A curved heart silhouette with a center ridge. Each leaf is geometry, not alpha cards.
def heart_leaf(name,attach,direction,width,length,roll=0):
    d=Vector(direction).normalized(); up=Vector((0,0,1)); side=d.cross(up)
    if side.length<.08: side=d.cross(Vector((0,1,0)))
    side.normalize(); normal=side.cross(d).normalized()
    # roll about the leaf axis for varied-facing foliage
    side2=side*math.cos(roll)+normal*math.sin(roll); normal2=normal*math.cos(roll)-side*math.sin(roll)
    # Rounded heart outline, interpolated between control points; no sharp mathematical cusp.
    controls=[(0,0),(-.23,-.04),(-.43,.02),(-.5,.16),(-.48,.32),(-.39,.52),(-.24,.76),(-.11,.91),(0,.95),(.11,.91),(.24,.76),(.39,.52),(.48,.32),(.5,.16),(.43,.02),(.23,-.04)]
    coords=[]
    for i in range(len(controls)):
        p0=controls[(i-1)%len(controls)]; p1=controls[i]; p2=controls[(i+1)%len(controls)]; p3=controls[(i+2)%len(controls)]
        for j in range(3):
            t=j/3
            coords.append(tuple(.5*((2*p1[k])+(-p0[k]+p2[k])*t+(2*p0[k]-5*p1[k]+4*p2[k]-p3[k])*t*t+(-p0[k]+3*p1[k]-3*p2[k]+p3[k])*t*t*t) for k in range(2)))
    # Two inset rings yield a modest center ridge and cupped edges.
    center=(0,.43); count=len(coords); verts=[]; mapping=[]
    def add(x,y,bulge):
        verts.append(Vector(attach)+side2*(x*width)+d*(y*length)+normal2*bulge)
        mapping.append((x+.5,1-max(0,min(1,y))))
    add(*center,.008)
    for ratio in (.52,1):
        for x,y in coords:
            xx=center[0]+(x-center[0])*ratio; yy=center[1]+(y-center[1])*ratio
            add(xx,yy,.008*(1-ratio*ratio))
    faces=[]
    for i in range(count):
        j=(i+1)%count; faces.append((0,1+i,1+j)); faces.append((1+i,1+count+i,1+count+j,1+j))
    mesh=bpy.data.meshes.new(name); mesh.from_pydata(verts,[],faces); mesh.update(); ob=bpy.data.objects.new(name,mesh); bpy.context.collection.objects.link(ob); ob.data.materials.append(leafmat)
    layer=mesh.uv_layers.new(name='UVMap'); random_u=random.random()*.32; random_v=random.random()*.32
    for poly in mesh.polygons:
        poly.use_smooth=True
        for li in poly.loop_indices:
            vi=mesh.loops[li].vertex_index; u,v=mapping[vi]; layer.data[li].uv=(u*.65+random_u,v*.65+random_v)
    return ob
# Layered radial shoots: short individual curved stems and a heart-shaped leaf at each end.
for i in range(40):
    a=i*2.399963 + random.uniform(-.15,.15)
    radius=random.uniform(.025,.095); z=random.uniform(.22,.35)
    start=Vector((random.uniform(-.04,.04),random.uniform(-.04,.04),.175))
    end=Vector((radius*math.cos(a),radius*math.sin(a),z))
    middle=(start+end)*.5+Vector((0,0,.022))
    curve('Canopy stem %02d'%i,[start,middle,end],.0014,stemmat)
    direction=Vector((math.cos(a)*random.uniform(.45,.8),math.sin(a)*random.uniform(.45,.8),random.uniform(-.20,.60)))
    heart_leaf('Canopy leaf %02d'%i,end,direction,random.uniform(.055,.085),random.uniform(.070,.105),random.uniform(-.8,.8))
# A few low leaves bridge the pot rim and the airy upper canopy.
for i in range(13):
    a=i*2.399963+random.uniform(-.15,.15); radius=random.uniform(.045,.08); z=random.uniform(.20,.24)
    start=Vector((.018*math.cos(a),.018*math.sin(a),.176)); end=Vector((radius*math.cos(a),radius*math.sin(a),z))
    curve('Low stem %02d'%i,[start,(start+end)*.5+Vector((0,0,.01)),end],.0014,stemmat)
    direction=Vector((math.cos(a),math.sin(a),random.uniform(-.45,.05)))
    heart_leaf('Low leaf %02d'%i,end,direction,random.uniform(.052,.073),random.uniform(.060,.085),random.uniform(-.75,.75))
# Trailing stems sweep down over the rim. Leaves grow at several staggered nodes.
for vine in range(7):
    a=2*math.pi*vine/7+random.uniform(-.22,.22)
    points=[]
    for j in range(9):
        t=j/8; r=.065+.08*math.sin(t*math.pi*.5); z=.184-.155*t+.025*math.sin(t*math.pi)
        points.append(Vector((r*math.cos(a+.15*t),r*math.sin(a+.15*t),z)))
    curve('Trailing vine %02d'%vine,points,.0018,stemmat)
    for k in (2,4,6,8):
        p=points[k]; tangent=Vector((math.cos(a)*.40,math.sin(a)*.40,-.85))
        tangent+=Vector((-math.sin(a),math.cos(a),0))*random.uniform(-.5,.5)
        heart_leaf('Trailing leaf %02d-%02d'%(vine,k),p,tangent,random.uniform(.045,.070),random.uniform(.050,.075),random.uniform(-1,1))
# Convert all production curves to meshes with UVs for FBX.
for ob in list(bpy.context.scene.objects):
    if ob.type=='CURVE':
        bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True); bpy.context.view_layer.objects.active=ob; bpy.ops.object.convert(target='MESH')
production=[o for o in bpy.context.scene.objects if o.type=='MESH']
for ob in production:
    if not ob.data.uv_layers:
        bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True); bpy.context.view_layer.objects.active=ob
        bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.uv.smart_project(); bpy.ops.object.mode_set(mode='OBJECT')

# Join static submeshes by material to keep the imported asset manageable.
for material in (clay,leafmat,stemmat,soilmat,cream):
    group=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.data.materials and o.data.materials[0]==material]
    if len(group)>1:
        bpy.ops.object.select_all(action='DESELECT')
        for o in group: o.select_set(True)
        bpy.context.view_layer.objects.active=group[0]; bpy.ops.object.join()
production=[o for o in bpy.context.scene.objects if o.type=='MESH']
# Export just the prop; no scene lights or camera.
bpy.ops.object.select_all(action='DESELECT')
for ob in production: ob.select_set(True)
bpy.context.view_layer.objects.active=pot
bpy.ops.export_scene.fbx(filepath=str(BASE/'model'/'LV_Plant.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,add_leaf_bones=False,mesh_smooth_type='FACE',path_mode='AUTO')
# Studio preview
world=bpy.context.scene.world; world.color=(.15,.15,.15)
def area(name,loc,energy,size):
    data=bpy.data.lights.new(name,'AREA'); data.energy=energy; data.shape='DISK'; data.size=size; ob=bpy.data.objects.new(name,data); bpy.context.collection.objects.link(ob); ob.location=loc; ob.rotation_euler=(Vector((0,0,.15))-ob.location).to_track_quat('-Z','Y').to_euler()
area('Key',(-1,-2,2.5),85,2); area('Fill',(1.5,-1,1.2),45,1.5); area('Rim',(0,1.6,2),55,1)
camdata=bpy.data.cameras.new('Camera'); cam=bpy.data.objects.new('Camera',camdata); bpy.context.collection.objects.link(cam); cam.location=(.72,-1.15,.75); target=Vector((0,0,.17)); cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler(); camdata.type='ORTHO'; camdata.ortho_scale=.65; bpy.context.scene.camera=cam
scene=bpy.context.scene; scene.render.engine='CYCLES'; scene.cycles.samples=32; scene.render.resolution_x=1000; scene.render.resolution_y=1000; scene.render.resolution_percentage=100; scene.render.film_transparent=True
scene.view_settings.view_transform='AgX'; scene.render.image_settings.file_format='PNG'; scene.render.filepath=str(BASE/'previews'/'plant-three-quarter.png')
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'model'/'LV-PLANT-01.blend'))
bpy.ops.render.render(write_still=True)
