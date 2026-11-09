import bpy, math, os
from mathutils import Vector
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for mat in bpy.data.materials: bpy.data.materials.remove(mat)

def material(name, color, metallic=0, roughness=.7, tex=None):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    n=m.node_tree.nodes; p=n.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Metallic'].default_value=metallic; p.inputs['Roughness'].default_value=roughness
    if tex:
        t=n.new('ShaderNodeTexImage'); t.image=bpy.data.images.load(str(ROOT/'textures'/tex), check_existing=True); m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
    return m
cream=material('Aged ivory painted cast iron',(.7,.59,.43),.10,.75,'enamel-selected.png')
brass=material('Tarnished brass',(.30,.205,.10),.55,.58,'brass-patina.png')
dark=material('Recessed dark bronze',(.13,.085,.04),.4,.75)

def finish(o,name,mat):
    o.name=name; o.data.materials.append(mat)
    if o.type=='MESH':
        bpy.context.view_layer.objects.active=o; o.select_set(True)
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.uv.smart_project(island_margin=.02); bpy.ops.object.mode_set(mode='OBJECT'); o.select_set(False)
        for p in o.data.polygons: p.use_smooth=True
    return o

def box(name,loc,dim,mat,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.dimensions=dim; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        m=o.modifiers.new('Rounded cast edges','BEVEL'); m.width=bevel; m.segments=4
        bpy.context.view_layer.objects.active=o; bpy.ops.object.modifier_apply(modifier=m.name)
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return finish(o,name,mat)
def cyl(name,loc,r,depth,mat,axis='Z',verts=32):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=depth,location=loc); o=bpy.context.object
    if axis=='X': o.rotation_euler[1]=math.pi/2
    if axis=='Y': o.rotation_euler[0]=math.pi/2
    m=o.modifiers.new('Soft cast rim','BEVEL'); m.width=min(.003,r*.16); m.segments=2; bpy.context.view_layer.objects.active=o; bpy.ops.object.modifier_apply(modifier=m.name)
    return finish(o,name,mat)
def torus(name,loc,major,minor,mat,rot=(0,0,0)):
    bpy.ops.mesh.primitive_torus_add(major_segments=32,minor_segments=10,location=loc,major_radius=major,minor_radius=minor,rotation=rot);return finish(bpy.context.object,name,mat)
# Six separated cast sections, rounded, with end flanges and fine raised cast seams.
for i in range(6):
    x=-.1875+i*.075
    box('Fin_%02d'%(i+1),(x,0,.32),(.061,.172,.49),cream,.029)
    # Raised, soft central fillet gives each rounded fin its visible front-to-back profile.
    for side in (-1,1):
        box('Fin_%02d_face_ridge_%s'%(i+1,side),(x,side*.086,.32),(.024,.008,.40),cream,.003)
for z in (.125,.515):
    cyl('Cross manifold', (0,0,z),.028,.425,cream,'X')
    for x in (-.218,.218): cyl('End cap bolt', (x,0,z),.027,.014,cream,'X',6)
def foot(x,y):
    verts=[]
    for z,wide,deep in ((.012,.034,.039),(.095,.022,.025)):
        verts.extend([(x-wide,y-deep,z),(x+wide,y-deep,z),(x+wide,y+deep,z),(x-wide,y+deep,z)])
    mesh=bpy.data.meshes.new('Tapered foot mesh');mesh.from_pydata(verts,[],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);mesh.update()
    o=bpy.data.objects.new('Tapered cast foot',mesh);bpy.context.collection.objects.link(o);bpy.context.view_layer.objects.active=o;o.select_set(True)
    m=o.modifiers.new('Rounded casting','BEVEL');m.width=.006;m.segments=3;bpy.ops.object.modifier_apply(modifier=m.name);o.select_set(False);finish(o,'Tapered cast foot',cream)
    box('Foot pad',(x,y,.008),(.070,.08,.016),cream,.005)
for x in (-.1875,.1875):
    for y in (-.055,.055): foot(x,y)
# External pipework and valve, with separate wheel object suitable for a future animation.
cyl('Vertical supply pipe',(-.292,0,.325),.013,.49,brass)
for z in (.095,.55): cyl('Pipe coupling',(-.292,0,z),.020,.026,brass,verts=8)
cyl('Supply elbow',(-.292,0,.095),.021,.036,brass)
cyl('Lower pipe connection',(-.257,0,.095),.018,.070,brass,'X')
cyl('Valve body',(-.257,0,.126),.023,.045,brass)
cyl('Valve spindle',(-.257,0,.165),.007,.037,dark)
torus('Valve handwheel rim',(-.257,0,.187),.026,.0045,brass)
cyl('Valve handwheel hub',(-.257,0,.187),.007,.009,brass)
for a in range(6):
    ang=a*math.pi/3; x=-.257+math.cos(ang)*.013; y=math.sin(ang)*.013
    o=box('Valve wheel spoke %s'%a,(x,y,.187),(.025,.004,.004),brass,.001); o.rotation_euler[2]=ang
# Wall attachment standoffs for the supply pipe.
for z in (.18,.48):
    cyl('Wall bracket',(-.292,.08,z),.009,.15,brass,'Y')
    cyl('Wall mounting flange',(-.292,.155,z),.025,.008,brass,'Y')
# Origin remains floor-level and centered on core. Export mesh only.
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
for o in meshes: o.select_set(True)
bpy.context.view_layer.objects.active=meshes[0]
bpy.ops.export_scene.fbx(filepath=str(ROOT/'model'/'LV_Radiator.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,axis_forward='-Y',axis_up='Z',add_leaf_bones=False,path_mode='AUTO')
for o in meshes:o.select_set(False)
# Studio preview, no extra scene meshes included in FBX.
scene=bpy.context.scene; scene.render.engine='CYCLES'; scene.cycles.samples=32
scene.render.resolution_x=1024;scene.render.resolution_y=1024;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=True
scene.world.color=(.24,.24,.24)
def point(o,target):o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
def area(name,loc,power,size):
    bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.shape='DISK';o.data.size=size;point(o,(0,0,.3))
area('Warm key',(-1,-2,2),180,3);area('Cool fill',(2,-.3,1.2),90,2);area('Rim',(.2,1,1.5),110,2)
bpy.ops.object.camera_add(location=(-1.4,-2.1,1.15));cam=bpy.context.object;point(cam,(0,0,.29));cam.data.type='ORTHO';cam.data.ortho_scale=1.08;scene.camera=cam
scene.view_settings.view_transform='AgX'
scene.render.filepath=str(ROOT/'previews'/'radiator-perspective.png')
for im in bpy.data.images:
    if im.source == 'FILE' and im.filepath: im.filepath='//../textures/'+Path(bpy.path.abspath(im.filepath)).name
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'model'/'LV-RADIATOR-01.blend'))
bpy.ops.render.render(write_still=True)
