import bpy, math, os
from mathutils import Vector
P=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def mat(name,col,metal=0,rough=.55):
 m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*col,1);bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough;return m
ivory=mat('Enamel_painted_ivory',(.72,.57,.43),0,.35);chrome=mat('Aged_chrome',(.36,.27,.18),.72,.28);drain=mat('Drain_dark',(.12,.09,.065),.5,.45)
# UV-painted enamel albedo: exported as a separate texture for Unreal.
enamel_tex=ivory.node_tree.nodes.new('ShaderNodeTexImage');enamel_tex.image=bpy.data.images.load(os.path.join(P,'textures','enamel-albedo.png'))
brush_tex=ivory.node_tree.nodes.new('ShaderNodeTexImage');brush_tex.image=bpy.data.images.load(os.path.join(P,'textures','enamel-brush-v2.png'))
mix=ivory.node_tree.nodes.new('ShaderNodeMixRGB');mix.blend_type='MIX';mix.inputs[0].default_value=.60
ivory.node_tree.links.new(enamel_tex.outputs['Color'],mix.inputs[1]);ivory.node_tree.links.new(brush_tex.outputs['Color'],mix.inputs[2]);ivory.node_tree.links.new(mix.outputs[0],ivory.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
fabric=mat('Floral_cotton',(.87,.69,.55),0,.9)
texture=os.path.join(P,'textures','floral-albedo.png')
if os.path.exists(texture):
 tex=fabric.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(texture);fabric.node_tree.links.new(tex.outputs['Color'],fabric.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])

def mesh(name,verts,faces,material,uv=None):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);me.materials.append(material)
 for f in me.polygons:f.use_smooth=True
 if uv:
  layer=me.uv_layers.new(name='UVMap')
  for p in me.polygons:
   for i in p.loop_indices:layer.data[i].uv=uv[me.loops[i].vertex_index]
 return ob

def cube(name,loc,dim,material,bevel=.015):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(material)
 if bevel:
  mod=o.modifiers.new('Rounded edges','BEVEL');mod.width=bevel;mod.segments=3;bpy.ops.object.modifier_apply(modifier=mod.name)
 for p in o.data.polygons:p.use_smooth=True
 return o

def cyl(name,a,b,r,material,vertices=24):
 a,b=Vector(a),Vector(b);d=b-a;bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=d.length,location=(a+b)/2);o=bpy.context.object;o.name=name;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();o.data.materials.append(material)
 for f in o.data.polygons:f.use_smooth=True
 return o

def sphere(name,loc,scale,material):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(material)
 for f in o.data.polygons:f.use_smooth=True
 return o

def curve(name,points,r,material):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.resolution_u=16;c.bevel_depth=r;c.bevel_resolution=4;sp=c.splines.new('BEZIER');sp.bezier_points.add(len(points)-1)
 for p,co in zip(sp.bezier_points,points):p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
 o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o);o.data.materials.append(material);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False);return o
# Outer skin and inner basin share a continuous manifold surface. Rounded-rectangle rings.
N=96; verts=[];faces=[];uv=[]
def ring(rx,ry,z):
 for i in range(N):
  a=2*math.pi*i/N;cs=math.cos(a);sn=math.sin(a);exp=.65
  verts.append((rx*math.copysign(abs(cs)**exp,cs),ry*math.copysign(abs(sn)**exp,sn),z));uv.append((i/N,z/.62))
for spec in [(.65,.22,.12),(.75,.28,.17),(.82,.33,.48),(.835,.34,.55),(.83,.335,.57),(.76,.265,.57),(.755,.26,.54),(.70,.215,.22),(.61,.17,.18)]:ring(*spec)
for j in range(8):
 for i in range(N):a=j*N+i;b=j*N+(i+1)%N;faces.append((a,b,b+N,a+N))
faces.append(tuple(reversed(range(N))));faces.append(tuple(range(8*N,9*N)))
body=mesh('Tub_shell_hollow',verts,faces,ivory,uv)
# Soft rim catch-light, no displacement.
pts=[]
for i in range(N+1):
 a=2*math.pi*i/N;c,s=math.cos(a),math.sin(a);pts.append((.795*math.copysign(abs(c)**.65,c),.302*math.copysign(abs(s)**.65,s),.565))
# Poly rim avoids spline overshoot.
c=bpy.data.curves.new('Rolled_rim_curve','CURVE');c.dimensions='3D';c.bevel_depth=.018;c.bevel_resolution=4;s=c.splines.new('POLY');s.points.add(N)
for p,co in zip(s.points,pts):p.co=(*co,1)
o=bpy.data.objects.new('Rolled_rim',c);bpy.context.collection.objects.link(o);c.materials.append(ivory);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False)
for x in [-.62,.62]:
 for y in [-.22,.22]:
  fv=[];ff=[]; seg=24
  for z,rx,ry,offset in [(.01,.068,.055,-.012),(.035,.075,.061,-.012),(.09,.061,.052,-.004),(.16,.052,.047,0)]:
   for i in range(seg):
    a=2*math.pi*i/seg;fv.append((x+rx*math.cos(a),y+offset+ry*math.sin(a),z))
  for k in range(3):
   for i in range(seg):
    a=k*seg+i;b=k*seg+(i+1)%seg;ff.append((a,b,b+seg,a+seg))
  ff.extend([tuple(reversed(range(seg))),tuple(range(3*seg,4*seg))]);mesh('Porcelain_foot',fv,ff,ivory)
  # Three tapered toes and a raised ankle collar evoke restrained vintage claw feet.
  for toe in [-1,0,1]:
   sphere('Claw_toe',(x+toe*.036,y-.055,.034),(.026,.050,.022),ivory)
  sphere('Foot_collar',(x,y,.145),(.067,.058,.025),ivory)
# Drain lies in basin bottom, overflow on the inside back wall.
cyl('Drain_rim',(-.50,0,.184),(-.50,0,.189),.042,chrome,32);cyl('Drain_insert',(-.50,0,.190),(-.50,0,.192),.028,drain,32)
cyl('Overflow_rim',(-.53,.227,.39),(-.53,.231,.39),.032,chrome,32)
tub_parts=list(bpy.context.scene.objects)
# A wall-adjacent fixture. Placed behind +Y edge; may be separated from tub in engine.
tap_groups=[]
for x in [-.59,-.41]:
 before=set(bpy.context.scene.objects)
 cyl('Tap_backplate',(x,.355,.96),(x,.39,.96),.035,chrome);cyl('Tap_stem',(x,.31,.96),(x,.37,.96),.014,chrome)
 sphere('Tap_boss',(x,.30,.96),(.028,.020,.028),chrome)
 for angle in range(4):
  a=angle*math.pi/2;cyl('Tap_cross_arm',(x,.29,.96),(x+.038*math.cos(a),.29,.96+.038*math.sin(a)),.008,chrome,12)
 tap_groups.append([o for o in bpy.context.scene.objects if o not in before and (o.name.startswith('Tap_boss') or o.name.startswith('Tap_cross_arm'))])
cyl('Mixer_manifold',(-.59,.37,.96),(-.41,.37,.96),.014,chrome)
curve('Mixer_downpipe',[(-.50,.37,.96),(-.50,.37,.88),(-.50,.37,.79)],.012,chrome)
curve('Tub_spout',[(-.50,.37,.79),(-.50,.28,.79),(-.50,.20,.77),(-.50,.18,.73)],.017,chrome)
curve('Shower_riser',[(-.50,.39,.97),(-.50,.39,1.9),(-.50,.37,2.05),(-.50,.27,2.13),(-.50,.15,2.09)],.013,chrome)
# Shower head shallow tapered bell.
bpy.ops.mesh.primitive_cone_add(vertices=32,radius1=.095,radius2=.035,depth=.075,location=(-.50,.15,2.05));o=bpy.context.object;o.name='Shower_head';o.data.materials.append(chrome)
for xx in [-.035,0,.035]:
 for yy in [-.035,0,.035]:cyl('Shower_nozzle',(-.50+xx,.15+yy,2.01),(-.50+xx,.15+yy,2.012),.004,drain,12)
# Shift plumbing toward the west end so the riser clears the south-wall window.
# Plan: tub centre x=5.80 m, bathroom window begins x=5.25 m.
for part in [o for o in bpy.context.scene.objects if o not in tub_parts]:
 part.location.x -= .25
# Join each tap handle around its real rotation centre, separate from the fixtures.
handles=[]
for index, parts in enumerate(tap_groups):
 bpy.ops.object.select_all(action='DESELECT')
 for ob in parts: ob.select_set(True)
 bpy.context.view_layer.objects.active=parts[0]; bpy.ops.object.join(); handle=bpy.context.object
 handle.name=('Tap_handle_left' if index == 0 else 'Tap_handle_right')
 bpy.context.scene.cursor.location=((-0.59 if index == 0 else -0.41)-.25,.29,.96)
 bpy.ops.object.origin_set(type='ORIGIN_CURSOR'); handles.append(handle)
# Rod spans tub, gathered curtain hangs to floor on right.
cyl('Curtain_rod',(-.93,-.35,2.18),(.93,-.35,2.18),.012,chrome)
for x in [-.93,.93]:sphere('Rod_finial',(x,-.35,2.18),(.029,.029,.029),chrome)
fixture_parts=[o for o in bpy.context.scene.objects if o not in tub_parts and o not in handles]
# Freestanding gathered cloth; UVs preserve image texture. Top x range at right end.
verts=[];uv=[];faces=[];NX=64;NZ=32
for j in range(NZ+1):
 v=j/NZ;z=2.14-v*1.89
 for i in range(NX+1):
  u=i/NX;x=.44+u*.48+(v**1.8)*(.026*math.sin(u*19)-.02); y=-.35+(.045+.014*v)*math.sin(u*math.pi*10)+.012*math.sin(v*7+u*16);x+=.012*math.sin(v*4+u*6);verts.append((x,y,z+.025*math.sin(u*31+.4)*v));uv.append((u*2,1-v))
for j in range(NZ):
 for i in range(NX):
  a=j*(NX+1)+i;faces.append((a,a+1,a+NX+2,a+NX+1))
curtain=mesh('Gathered_floral_curtain',verts,faces,fabric,uv);sol=curtain.modifiers.new('Fabric thickness','SOLIDIFY');sol.thickness=.002;bpy.context.view_layer.objects.active=curtain;bpy.ops.object.modifier_apply(modifier=sol.name)
for x in [.47,.54,.61,.68,.75,.82,.89]:
 bpy.ops.mesh.primitive_torus_add(major_segments=16,minor_segments=8,location=(x,-.35,2.17),major_radius=.024,minor_radius=.004,rotation=(0,math.pi/2,0));bpy.context.object.name='Curtain_ring';bpy.context.object.data.materials.append(chrome)
curtain_parts=[o for o in bpy.context.scene.objects if o not in tub_parts and o not in fixture_parts and o not in handles]
# Gathered curtain and rings slide as one rigid panel; pivot is at the rod's right end.
bpy.ops.object.select_all(action='DESELECT')
for ob in curtain_parts: ob.select_set(True)
bpy.context.view_layer.objects.active=curtain; bpy.ops.object.join(); curtain=bpy.context.object
curtain.name='Curtain_panel_sliding'; bpy.context.scene.cursor.location=(.92,-.35,2.18)
bpy.ops.object.origin_set(type='ORIGIN_CURSOR'); curtain_parts=[curtain]
# Give every mesh explicit UVs so painted materials survive export.
for ob in tub_parts + fixture_parts + curtain_parts + handles:
 if ob.type == 'MESH' and not ob.data.uv_layers:
  bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True); bpy.context.view_layer.objects.active=ob
  bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.uv.smart_project(island_margin=.02); bpy.ops.object.mode_set(mode='OBJECT')
# Three FBXs preserve independent component origins at apartment floor.
for name,group in [('BA_Tub',tub_parts),('BA_TubFixtures',fixture_parts),('BA_Curtain',curtain_parts),('BA_TapLeft',[handles[0]]),('BA_TapRight',[handles[1]])]:
 bpy.ops.object.select_all(action='DESELECT')
 for o in group:o.select_set(True)
 bpy.context.view_layer.objects.active=group[0]
 bpy.ops.export_scene.fbx(filepath=os.path.join(P,'model',name+'.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,add_leaf_bones=False,mesh_smooth_type='FACE')
# Studio setup retained in source, never exported.
world=bpy.context.scene.world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.32,.25,.20,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.55
bpy.ops.object.light_add(type='AREA',location=(-2,-3,4));bpy.context.object.data.energy=550;bpy.context.object.data.color=(1,.79,.60);bpy.context.object.data.shape='DISK';bpy.context.object.data.size=4
bpy.ops.object.camera_add(location=(3,-4,2.6));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,1.0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=3.2;bpy.context.scene.camera=cam
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.render.resolution_x=1200;scene.render.resolution_y=1200;scene.render.resolution_percentage=100;scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG';scene.render.filepath=os.path.join(P,'previews','three-quarter.png');scene.render.film_transparent=False
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(P,'model','BA-TUB-01.blend'));bpy.ops.render.render(write_still=True)
