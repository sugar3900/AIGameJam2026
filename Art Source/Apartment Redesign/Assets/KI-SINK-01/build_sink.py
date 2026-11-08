import bpy, math, os, random
from mathutils import Vector
import numpy as np
ROOT=os.path.dirname(os.path.abspath(__file__))
for n in ('models','textures','previews'): os.makedirs(os.path.join(ROOT,n),exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
random.seed(23)
# Subtle colored strokes baked into UV image maps. These are surface colour, not thick geometry.
def painted(name,base):
 files={'Sink_SagePaint':'Sink_SageTint-v2.png','Sink_AgedEnamel':'Sink_EnamelPainterly-v3.png','Sink_ToeWood':'Sink_ToeTint-v2.png'}
 img=bpy.data.images.load(os.path.join(ROOT,'textures',files[name]),check_existing=True); img.pack()
 mat=bpy.data.materials.new(name); mat.diffuse_color=(*base,1); mat.use_nodes=True
 nodes=mat.node_tree.nodes; p=nodes.get('Principled BSDF'); t=nodes.new('ShaderNodeTexImage'); t.image=img; 
 mat.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
 p.inputs['Roughness'].default_value=.76
 return mat
sage=painted('Sink_SagePaint',(.36,.43,.25)); ivory=painted('Sink_AgedEnamel',(.78,.72,.59)); dark=painted('Sink_ToeWood',(.18,.13,.09))
def material(name,c,metal=0,rough=.5):
 m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough; return m
metal=material('Aged_Chrome',(.37,.33,.27),.75,.32); water=material('Leak_Water',(.33,.55,.58),.15,.22); puddle=material('Puddle',(.31,.45,.45),.12,.3)
parts={}
def add(o,group,mat):
 o.data.materials.append(mat); parts.setdefault(group,[]).append(o); return o
def box(n,loc,size,mat,group,bevel=.008):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=n; o.dimensions=size; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  m=o.modifiers.new('soft edges','BEVEL');m.width=bevel;m.segments=3;o.modifiers.new('weighted normals','WEIGHTED_NORMAL');bpy.context.view_layer.objects.active=o
  for m in list(o.modifiers): bpy.ops.object.modifier_apply(modifier=m.name)
 return add(o,group,mat)
def cyl(n,loc,r,depth,mat,group,rot=(0,0,0),verts=24):
 bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=depth,location=loc,rotation=rot);return add(bpy.context.object,group,mat)
def bar(n,a,b,r,mat,group):
 a,b=Vector(a),Vector(b);d=b-a;o=cyl(n,(a+b)/2,r,d.length,mat,group);o.rotation_euler=d.to_track_quat('Z','Y').to_euler();return o
def pipe(n,points,r,mat,group):
 cu=bpy.data.curves.new(n,'CURVE');cu.dimensions='3D';cu.resolution_u=20;cu.bevel_depth=r;cu.bevel_resolution=3;sp=cu.splines.new('BEZIER');sp.bezier_points.add(len(points)-1)
 for p,co in zip(sp.bezier_points,points): p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
 ob=bpy.data.objects.new(n,cu);bpy.context.collection.objects.link(ob);bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.convert(target='MESH');ob.select_set(False);return add(ob,group,mat)
# Front faces -Y. Assembly overall width 2.35m; centre sink width 1.05m.
for side,x in [('L',-.845),('R',.845)]:
 for ix in [-.31,.31]: box(side+' cabinet side',(x+ix,.025,.46),(.04,.59,.80),sage,'body',.006)
 box(side+' cabinet back',(x,.30,.46),(.58,.035,.80),sage,'body',.004)
 box(side+' cabinet shelf',(x,.025,.19),(.58,.55,.035),sage,'body',.004)
 box(side+' cabinet divider',(x,.025,.65),(.58,.55,.035),sage,'body',.004)
 box(side+' cabinet toe',(x,-.03,.06),(.66,.62,.12),dark,'body',.006)
 box(side+' worktop',(x,-.005,.885),(.68,.65,.05),ivory,'body',.012)
 # drawer and door geometry separate for actual animation; fronts stand proud.
 box(side+' drawer face',(x,-.282,.775),(.57,.035,.17),sage,side+'_drawer',.008)
 box(side+' drawer bottom',(x,.0,.70),(.51,.52,.025),dark,side+'_drawer',.003)
 for dx in [-.245,.245]: box(side+' drawer side',(x+dx,0,.76),(.025,.52,.12),sage,side+'_drawer',.003)
 box(side+' drawer back',(x,.25,.76),(.50,.025,.12),sage,side+'_drawer',.003)
 box(side+' raised door',(x,-.282,.405),(.57,.035,.54),sage,side+'_door',.008)
 # inset stile outlines on door, separate mesh joined into moving piece
 for sx in [-.225,.225]: box(side+' stile',(x+sx,-.307,.405),(.022,.015,.45),sage,side+'_door',.003)
 for z in [.19,.62]: box(side+' rail',(x,-.307,z),(.46,.015,.022),sage,side+'_door',.003)
 pipe(side+' drawer handle',[(x-.08,-.312,.775),(x-.065,-.337,.77),(x+.065,-.337,.77),(x+.08,-.312,.775)],.009,metal,side+'_drawer')
 hx=x+(.20 if side=='L' else -.20)
 pipe(side+' door pull',[(hx,-.313,.45),(hx,-.338,.43),(hx,-.338,.34),(hx,-.313,.32)],.008,metal,side+'_door')
# apron-front ceramic sink with deep open basin. Rim ring meshes taper to bottom.
def basin():
 # Rounded rectangular loops give a truly curved apron, rim and sloped interior.
 def loop(hx,hy,r,z):
  coords=[]
  for cx,cy,a0 in [(hx-r,hy-r,0),(-hx+r,hy-r,90),(-hx+r,-hy+r,180),(hx-r,-hy+r,270)]:
   for k in range(5):
    a=math.radians(a0+k*90/4); coords.append((cx+r*math.cos(a),cy+r*math.sin(a)-.015,z))
  return coords
 loops=[loop(.525,.325,.075,.90),loop(.455,.255,.085,.90),loop(.390,.185,.085,.68),loop(.525,.325,.075,.64)]
 n=len(loops[0]); verts=[v for ring in loops for v in ring]; faces=[]
 for a,b in [(0,1),(1,2),(0,3)]:
  for i in range(n): faces.append((a*n+i,a*n+(i+1)%n,b*n+(i+1)%n,b*n+i))
 faces.extend([tuple(2*n+i for i in range(n)),tuple(reversed([3*n+i for i in range(n)]))])
 mesh=bpy.data.meshes.new('Sink bowl');mesh.from_pydata(verts,[],faces);mesh.update()
 import bmesh
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
 o=bpy.data.objects.new('Deep open rounded apron basin',mesh);bpy.context.collection.objects.link(o);add(o,'body',ivory)
 # A small bevel gives porcelain its soft lip while preserving the hollow.
 bpy.context.view_layer.objects.active=o;o.select_set(True);m=o.modifiers.new('soft porcelain lip','BEVEL');m.width=.006;m.segments=3; bpy.ops.object.modifier_apply(modifier=m.name);o.select_set(False)

basin()
box('Raised enamel backsplash',(0,.272,1.01),(1.05,.075,.25),ivory,'body',.025)
# Painted panel behind open knee space, recessed enough to leave exposed drain visible.
box('Recessed aged back panel',(0,.298,.38),(1.02,.025,.72),sage,'body',.004)
# drain, exposed chromed waste and P trap
cyl('Drain in bowl',(0,0,.685),.045,.012,metal,'body')
pipe('Exposed P trap',[(0,0,.68),(0,0,.44),(0,0,.30),(-.10,0,.27),(-.19,0,.31),(-.19,.13,.35),(-.19,.24,.35)],.026,metal,'body')
for z in [.42,.57]: cyl('Drain collar',(0,0,z),.033,.028,metal,'body')
# taps and high swan neck, split knobs for optional rotation
pipe('Arched faucet',[(0,.24,1.04),(0,.24,1.22),(0,.15,1.32),(0,.02,1.30),(0,-.04,1.23)],.016,metal,'body')
bar('Tap manifold',(-.22,.24,1.04),(.22,.24,1.04),.021,metal,'body')
for side,x in [('L',-.25),('R',.25)]:
 cyl(side+' tap base',(x,.24,1.04),.038,.04,metal,'body',(math.pi/2,0,0))
 cyl(side+' valve stem',(x,.20,1.075),.022,.055,metal,side+'_tap')
 cyl(side+' porcelain tap center',(x,.20,1.11),.014,.009,ivory,side+'_tap')
 cyl(side+' valve collar',(x,.24,1.04),.048,.012,metal,'body',(math.pi/2,0,0))
 bar(side+' tap handle horizontal',(x-.05,.21,1.105),(x+.05,.21,1.105),.009,metal,side+'_tap')
 bar(side+' tap handle vertical',(x,.21,1.065),(x,.21,1.145),.009,metal,side+'_tap')
# Galvanized bucket below drain; open tapered shell, solid bottom and separate wire handle.
def bucket():
 n=32; verts=[]
 for z,r in [(.035,.115),(.27,.15),(.27,.14),(.045,.105)]:
  verts += [(r*math.cos(i*2*math.pi/n)-.12,r*math.sin(i*2*math.pi/n)-.055,z) for i in range(n)]
 faces=[]
 for ring in range(3):
  for i in range(n): faces.append((ring*n+i,ring*n+(i+1)%n,(ring+1)*n+(i+1)%n,(ring+1)*n+i))
 faces.append(tuple(reversed([3*n+i for i in range(n)])))
 mesh=bpy.data.meshes.new('Bucket shell');mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new('Galvanized bucket',mesh);bpy.context.collection.objects.link(o);add(o,'body',metal)
 pipe('Bucket wire handle',[(-.265,-.055,.22),(-.23,-.055,.32),(-.12,-.055,.36),(-.01,-.055,.32),(.025,-.055,.22)],.004,metal,'body')
bucket()
# Damage overlay, separately exported and hidden upon repair
for i in range(5):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,location=(-.12,-.025,.40-i*.026));o=bpy.context.object;o.scale=(.012,.012,.025);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);add(o,'damage',water)
bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=8,location=(-.12,-.06,.012));o=bpy.context.object;o.scale=(.23,.16,.009);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);add(o,'damage',puddle)
# Smart UV each object for portable FBX texture coordinates.
for group,objs in parts.items():
 for o in objs:
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
  bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
  bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.018);bpy.ops.object.mode_set(mode='OBJECT')
# Export each separately with defined pivot. Body and damage origin at assembly floor centre.
pivots={'body':(0,0,0),'damage':(0,0,0),'L_door':(-1.13,-.30,.405),'R_door':(1.13,-.30,.405),'L_drawer':(-.845,-.30,.775),'R_drawer':(.845,-.30,.775),'L_tap':(-.25,.21,1.075),'R_tap':(.25,.21,1.075)}
for name,objs in parts.items():
 bpy.ops.object.select_all(action='DESELECT')
 for o in objs:o.select_set(True)
 bpy.context.view_layer.objects.active=objs[0];bpy.ops.object.join();o=bpy.context.object;o.name='KI_SINK_'+name
 bpy.context.scene.cursor.location=pivots[name];bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
 bpy.ops.export_scene.fbx(filepath=os.path.join(ROOT,'models',o.name+'.fbx'),use_selection=True,object_types={'MESH'},add_leaf_bones=False,path_mode='AUTO',apply_unit_scale=True)
# Camera / render with neutral lighting.
bpy.ops.object.select_all(action='DESELECT');bpy.ops.object.camera_add(location=(3.3,-5.3,3.0));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.65))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=3.35;bpy.context.scene.camera=cam
for loc,power,size in [((1,-3,5),800,4),((-3,-1,3),450,3)]:
 bpy.ops.object.light_add(type='AREA',location=loc);a=bpy.context.object;a.data.energy=power;a.data.shape='DISK';a.data.size=size;a.data.color=(1.0,.82,.65) if loc[0]>0 else (1.0,.91,.78);a.rotation_euler=(Vector((0,0,.6))-a.location).to_track_quat('-Z','Y').to_euler()
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=32;sc.world.color=(.24,.24,.24);sc.render.resolution_x=1400;sc.render.resolution_y=1050;sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX';sc.render.image_settings.file_format='PNG';sc.render.filepath=os.path.join(ROOT,'previews','leaking-three-quarter.png');bpy.ops.render.render(write_still=True)
parts['damage'][0].hide_render=True
sc.render.filepath=os.path.join(ROOT,'previews','repaired-three-quarter.png');bpy.ops.render.render(write_still=True)
parts['damage'][0].hide_render=False
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'models','KI_SINK_assembly.blend'))
