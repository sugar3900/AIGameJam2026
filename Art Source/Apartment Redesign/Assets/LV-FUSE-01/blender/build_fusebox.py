"""Build LV-FUSE-01 in metres, front -Y; Y=0 wall plane, Z=0 lower box edge."""
import bpy, math, random, os
from mathutils import Vector
P=os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
for d in ('textures','exports','previews'): os.makedirs(os.path.join(P,d),exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
random.seed(1927)
# Painterly albedo: restrained layered mottling and directional dry-brush streaks.
def paint_image(name,base,accent):
    n=512; rng=random.Random(name); pix=[0.0]*(n*n*4)
    strokes=[]
    for i in range(420):
        strokes.append((rng.uniform(0,n),rng.uniform(0,n),rng.uniform(6,34),rng.uniform(1,4),rng.uniform(-.065,.075)))
    # broad crosshatched pigment bands, no geometry displacement
    for y in range(n):
        for x in range(n):
            v=.028*math.sin(x*.034+y*.017)+.018*math.sin(x*.11-y*.04)+rng.uniform(-.012,.012)
            for sx,sy,rx,ry,sv in strokes:
                if abs(x-sx)<rx and abs(y-sy-(x-sx)*.12)<ry: v+=sv
            i=(y*n+x)*4
            for j in range(3): pix[i+j]=max(0,min(1,base[j]+v+accent[j]*.025*math.sin(x*.014+y*.02)))
            pix[i+3]=1
    im=bpy.data.images.new(name,width=n,height=n); im.pixels.foreach_set(pix); im.filepath_raw=os.path.join(P,'textures',name+'.png'); im.file_format='PNG'; im.save(); return im
metal_img=bpy.data.images.load(os.path.join(P,'textures','T_Fusebox_GrayGreen_Painterly_v2.png'), check_existing=True)
ceramic_img=bpy.data.images.load(os.path.join(P,'textures','T_Fusebox_Ceramic_Painterly_v2.png'), check_existing=True)
bronze_img=paint_image('T_Fusebox_AgedBrass',(.52,.36,.16),(.3,.2,.05))
def mat(name,color,img=None,metallic=0,rough=.83):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metallic
    if img:
        tex=m.node_tree.nodes.new('ShaderNodeTexImage'); tex.image=img; m.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color'])
    return m
olive=mat('Painted_Olive_Metal',(.36,.32,.25),metal_img,.15); dark=mat('Interior_Dark_Brown',(.105,.078,.055),None,.1); doorinner=mat('Bakelite_Dark_Brown',(.12,.075,.045),None,.06); brass=mat('Patinated_Brass',(.52,.36,.16),bronze_img,.55,.45); ceramic=mat('Ivory_Ceramic',(.75,.70,.60),ceramic_img,0,.4); red=mat('Wire_Brick_Red',(.42,.105,.065)); blue=mat('Wire_Navy',(.09,.11,.12)); cream=mat('Wire_Cloth',(.56,.48,.34)); copper=mat('Exposed_Copper',(.65,.27,.09),None,.6); burn=mat('Scorch',(.12,.07,.045)); wear=mat('Edge_Wear_Ochre',(.35,.235,.12),None,.18,.8); gasket=mat('Inset_Gasket',(.075,.07,.055))
def box(name,loc,dims,material,bevel=.006):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object;o.name=name;o.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        mod=o.modifiers.new('Rounded edges','BEVEL');mod.width=min(bevel,min(dims)*.45);mod.segments=3; bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
    o.data.materials.append(material);return o
def cyl(name,loc,radius,depth,material,axis='Y',vertices=32):
    rot=(math.pi/2,0,0) if axis=='Y' else ((0,math.pi/2,0) if axis=='X' else (0,0,0))
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=loc,rotation=rot);o=bpy.context.object;o.name=name;o.data.materials.append(material); bevel=o.modifiers.new('Turned lip','BEVEL');bevel.width=min(radius*.14,.002);bevel.segments=2;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=bevel.name);return o
def tube(name,points,radius,material):
    cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=16;cu.bevel_depth=radius;cu.bevel_resolution=4;s=cu.splines.new('BEZIER');s.bezier_points.add(len(points)-1)
    for p,co in zip(s.bezier_points,points):p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
    o=bpy.data.objects.new(name,cu);bpy.context.collection.objects.link(o);o.data.materials.append(material);bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH');return o
def wear_patch(x,y,z,w,h):
    # Irregular, flat wear marks on the metal lip; no raised paint geometry.
    rng=random.Random(f"{x}-{z}")
    pts=[]
    for i in range(9):
        a=2*math.pi*i/9; k=rng.uniform(.5,1.0)
        pts.append((x+math.cos(a)*w*.5*k,y,z+math.sin(a)*h*.5*k))
    mesh=bpy.data.meshes.new('Wear patch mesh');mesh.from_pydata(pts,[],[list(range(9))]);mesh.update()
    o=bpy.data.objects.new('Localized edge wear',mesh);bpy.context.collection.objects.link(o);o.data.materials.append(wear)
def screw(x,z,y=-.135):
    o=cyl('Brass screw',(x,y,z),.008,.004,brass); box('Screw slot',(x,y-.003,z),(.009,.001,.0015),dark,.0003)
def join_objects(name,objects,origin):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:o.select_set(True)
    bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();o=bpy.context.object;o.name=name
    bpy.context.scene.cursor.location=origin;bpy.ops.object.origin_set(type='ORIGIN_CURSOR');return o
def collect(): return set(bpy.context.scene.objects)
def export(o,name):
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
    bpy.ops.export_scene.fbx(filepath=os.path.join(P,'exports',name+'.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,add_leaf_bones=False,path_mode='COPY',embed_textures=False)
# 0.45 wide x .58 high x .12 deep shell; open front towards -Y.
before=collect();box('Back panel',(0,-.015,.29),(.45,.03,.58),olive,.012)
box('Dark cavity',(0,-.033,.29),(.398,.007,.525),dark,.008)
for x in (-.216,.216):box('Side return',(x,-.071,.29),(.018,.115,.56),olive,.006)
for z in (.009,.571):box('End return',(0,-.071,z),(.438,.115,.018),olive,.006)
# Inset lip and gasket frame strengthen the recessed silhouette.
for x in (-.199,.199): box('Dark lip gasket',(x,-.126,.29),(.005,.004,.52),gasket,.001)
for z in (.03,.55): box('Dark lip gasket',(0,-.126,z),(.402,.004,.005),gasket,.001)
for x in (-.19,.19):
 for z in (.035,.545):screw(x,z,-.132)
# Small flat ochre abrasions punctuate the outside lip, rather than a uniform rust coat.
for x,z,w,h in [(-.214,.07,.006,.038),(-.214,.32,.004,.022),(-.214,.49,.006,.018),(.214,.11,.005,.035),(.214,.46,.006,.023),(-.15,.562,.025,.004),(.09,.562,.035,.004),(-.09,.018,.032,.004),(.14,.018,.018,.004)]:
 wear_patch(x,-.133,z,w,h)
# Twin brown mounting plates, four ceramic fuse assemblies
for z in (.37,.245):
 box('Bakelite fuse rail',(0,-.068,z),(.27,.028,.094),doorinner,.01)
 for x in (-.07,.07):
  cyl('Porcelain fuse base',(x,-.091,z),.039,.023,ceramic);cyl('Porcelain fuse collar',(x,-.106,z),.028,.012,ceramic);cyl('Brass fuse cap',(x,-.114,z),.016,.009,brass);cyl('Fuse glass inset',(x,-.120,z),.009,.004,dark)
 for x in (-.116,.116):screw(x,z,-.085)
 # Four ceramic fuse carriers are anchored to independent brass terminals.
 for x in (-.07,.07):
  cyl('Terminal top',(x,-.072,z+.056),.009,.018,brass,'Z')
  cyl('Terminal bottom',(x,-.072,z-.056),.009,.018,brass,'Z')
# Exterior cable continuation and interior red / dark / repaired wire.
for x,ma in ((-.055,red),(0,blue),(.055,cream)):
 tube('Upper cloth lead',[(x,-.05,.58),(x,-.05,.64),(x+.015,-.05,.70)],.010,ma)
 tube('Lower cloth lead',[(x,-.05,0),(x,-.05,-.07),(x+.01,-.05,-.12)],.010,ma)
for z in (.61,-.04):
 box('Cable clamp',(0,-.068,z),(.145,.018,.027),brass,.004)
 for x in (-.06,.06):screw(x,z,-.079)
tube('Red internal wire',[(-.055,-.052,.57),(-.09,-.061,.48),(-.17,-.06,.44),(-.16,-.06,.17),(-.055,-.055,.02)],.009,red)
tube('Dark internal wire',[(0,-.052,.57),(0,-.06,.46),(.03,-.06,.40),(.03,-.06,.18),(0,-.052,.02)],.009,blue)
# Branch leads route from the bus cables into terminal tops and bottoms.
tube('Red feed upper',[(-.16,-.06,.44),(-.12,-.07,.445),(-.07,-.072,.435)],.006,red)
tube('Blue feed upper',[(.03,-.06,.44),(.07,-.072,.435)],.006,blue)
tube('Red bridge',[(-.16,-.06,.30),(-.12,-.07,.30),(-.07,-.072,.31)],.006,red)
tube('Blue bridge',[(.03,-.06,.30),(.07,-.072,.31)],.006,blue)
tube('Red lower return',[(-.15,-.06,.18),(-.11,-.07,.19),(-.07,-.072,.18)],.006,red)
tube('Blue lower return',[(.03,-.06,.18),(.07,-.072,.18)],.006,blue)
# Upper and lower hinge barrels belong to fixed shell.
for z in (.14,.44):cyl('Fixed hinge barrel',(-.229,-.13,z),.010,.07,brass,'Z')
shell=join_objects('LV_FUSE_01_Shell',list(collect()-before),(0,0,0))
# Sliding/rotating door group origin exactly at left hinge axis.
before=collect();box('Door slab',(0,-.147,.29),(.45,.025,.58),olive,.012)
box('Recessed inner panel',(0,-.163,.29),(.385,.009,.51),olive,.008)
for x in (-.175,.175):
 for z in (.065,.515):screw(x,z,-.17)
# Edge scuffs on the door stay flush with its surface.
for x,z,w,h in [(-.219,.11,.003,.032),(-.219,.39,.003,.025),(.219,.20,.003,.025),(.219,.49,.003,.018),(-.11,.576,.035,.003),(.12,.004,.024,.003)]:
 wear_patch(x,-.1605,z,w,h)
box('Latch plate',(.173,-.172,.29),(.038,.012,.088),brass,.009);cyl('Latch button',(.173,-.184,.29),.012,.012,brass);box('Latch lever',(.150,-.191,.29),(.071,.01,.014),brass,.004)
for z in (.14,.44):
 cyl('Door hinge knuckle',(-.229,-.14,z),.009,.038,brass,'Z')
 for dz in (-.025,.025): cyl('Hinge end cap',(-.229,-.14,z+dz),.010,.004,dark,'Z')
door=join_objects('LV_FUSE_01_Door',list(collect()-before),(-.229,-.14,0))
# Repair swap: clean continuous cream wire versus damaged ends and frayed copper.
before=collect();tube('Clean cream insulated wire',[(.055,-.052,.57),(.085,-.057,.46),(.15,-.058,.40),(.155,-.06,.16),(.055,-.052,.02)],.009,cream);clean=join_objects('LV_FUSE_01_Wire_Repaired',list(collect()-before),(0,0,0))
before=collect();tube('Broken insulated upper',[(.055,-.052,.57),(.085,-.057,.46),(.15,-.058,.40),(.155,-.06,.20)],.009,cream);tube('Broken insulated lower',[(.055,-.052,.02),(.095,-.058,.07),(.13,-.06,.12)],.009,cream)
for i in range(5):tube('Frayed copper strand',[(.154,-.064,.20),(.153+i*.006,-.070,.17-i*.003),(.145+i*.009,-.07,.155)],.0014,copper)
damaged=join_objects('LV_FUSE_01_Wire_Damaged',list(collect()-before),(0,0,0))
# Explicit auto UV for exported texture fidelity.
for o in (shell,door,clean,damaged):
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.transform_apply(location=False,rotation=True,scale=True);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.025);bpy.ops.object.mode_set(mode='OBJECT')
 # Planar projection retains legible brush scale across the large front surfaces;
 # smaller parts reuse the same albedos and materials without raised relief.
 uv=o.data.uv_layers.active.data
 for poly in o.data.polygons:
  n=poly.normal; axis=max(range(3),key=lambda i:abs(n[i]))
  for li in poly.loop_indices:
   p=o.data.vertices[o.data.loops[li].vertex_index].co+o.location
   if axis==1: uv[li].uv=((p.x+.23)/.46,p.z/.58)
   elif axis==0: uv[li].uv=((p.y+.16)/.16,p.z/.58)
   else: uv[li].uv=((p.x+.23)/.46,(p.y+.16)/.16)
 export(o,o.name)
# Scene lighting and orthographic presentation; show the clean counterpart only when repaired.
clean.hide_render=True
bpy.ops.object.camera_add(location=(1.1,-2.6,1.15));cam=bpy.context.object;cam.name='PresentationCamera';cam.rotation_euler=(Vector((0,-.06,.29))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=1.12;bpy.context.scene.camera=cam
bpy.ops.object.light_add(type='AREA',location=(-1,-1.8,2));bpy.context.object.data.energy=150;bpy.context.object.data.color=(1.0,.78,.57);bpy.context.object.data.shape='DISK';bpy.context.object.data.size=3
bpy.ops.object.light_add(type='AREA',location=(1,-.8,1.2));bpy.context.object.data.energy=65;bpy.context.object.data.color=(.74,.84,1.0);bpy.context.object.data.size=2
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.world.color=(.24,.20,.16);scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False; scene.world.use_nodes=True; scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.31,.245,.17,1); scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.45
scene.render.filepath=os.path.join(P,'previews','fusebox-closed.png');bpy.ops.render.render(write_still=True)
door.rotation_euler.z=math.radians(-105)
scene.render.filepath=os.path.join(P,'previews','fusebox-open-damaged.png');bpy.ops.render.render(write_still=True)
damaged.hide_render=True;clean.hide_render=False;scene.render.filepath=os.path.join(P,'previews','fusebox-open-repaired.png');bpy.ops.render.render(write_still=True)
door.rotation_euler.z=0;damaged.hide_render=False;clean.hide_render=True
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(P,'blender','LV-FUSE-01.blend'))
print('FINISHED',P)
