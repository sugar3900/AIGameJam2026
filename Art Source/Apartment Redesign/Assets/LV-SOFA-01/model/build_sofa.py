import bpy, math, os
from mathutils import Vector
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
bpy.context.scene.render.engine='CYCLES'; bpy.context.scene.cycles.samples=32

def material(name,col,tex=None):
 m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*col,1);bs.inputs['Roughness'].default_value=.88
 if tex:
  node=m.node_tree.nodes.new('ShaderNodeTexImage');node.image=bpy.data.images.load(str(tex),check_existing=True);m.node_tree.links.new(node.outputs['Color'],bs.inputs['Base Color'])
 return m
floral=material('Floral upholstery',(.33,.31,.18),ROOT/'textures'/'sofa-floral.png');piping=material('Subdued olive brown piping',(.19,.16,.09));wood=material('Warm aged wood',(.24,.11,.046));rose=material('Rose pillow',(.55,.25,.19),ROOT/'textures'/'pillow-rose.png');teal=material('Muted teal pillow',(.25,.30,.27));cream=material('Crochet throw',(.75,.66,.49),ROOT/'textures'/'throw-knit.png')
def box(name,loc,dims,mat,bevel=.03):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  b=o.modifiers.new('Soft upholstery','BEVEL');b.width=min(bevel,min(dims)*.45);b.segments=5
  bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=b.name)
 for p in o.data.polygons:p.use_smooth=True
 n=o.modifiers.new('Weighted normals','WEIGHTED_NORMAL');n.keep_sharp=True;bpy.ops.object.modifier_apply(modifier=n.name)
 # Preserve consistent floral scale across top/front/side faces.
 if mat == floral:
  uv=o.data.uv_layers.active or o.data.uv_layers.new(name='UVMap')
  for face in o.data.polygons:
   n=face.normal; axis=max(range(3),key=lambda k:abs(n[k]))
   for li in face.loop_indices:
    v=o.data.vertices[o.data.loops[li].vertex_index].co
    a,b=((v.y,v.z) if axis==0 else ((v.x,v.z) if axis==1 else (v.x,v.y)))
    uv.data[li].uv=(a/0.72+.5,b/0.72+.5)
 o.data.materials.append(mat);return o

def sphere(name,loc,scale,mat):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for p in o.data.polygons:p.use_smooth=True
 o.data.materials.append(mat);return o

def soft_pillow(name,loc,dims,mat):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=24,location=loc);o=bpy.context.object;o.name=name
 def power(v): return math.copysign(abs(v)**.55,v)
 for v in o.data.vertices:
  v.co.x=power(v.co.x)*dims[0]*.5
  v.co.y=power(v.co.y)*dims[1]*.5
  v.co.z=power(v.co.z)*dims[2]*.5
 o.data.update()
 for face in o.data.polygons:face.use_smooth=True
 if mat == floral:
  uv=o.data.uv_layers.active
  for face in o.data.polygons:
   n=face.normal; axis=max(range(3),key=lambda k:abs(n[k]))
   for li in face.loop_indices:
    v=o.data.vertices[o.data.loops[li].vertex_index].co
    a,b=((v.y,v.z) if axis==0 else ((v.x,v.z) if axis==1 else (v.x,v.y)))
    uv.data[li].uv=(a/.72+.5,b/.72+.5)
 o.data.materials.append(mat);return o

def tube(name,points,r,mat):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.resolution_u=12;c.bevel_depth=r;c.bevel_resolution=3;s=c.splines.new('POLY');s.points.add(len(points)-1)
 for p,co in zip(s.points,points):p.co=(*co,1)
 o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o);o.data.materials.append(mat);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False);return o
# low platform, skirt and rounded upholstered back
box('Sofa deck',(0,0,.23),(1.92,.78,.25),floral,.07)
box('Front apron',(0,-.405,.22),(1.67,.05,.21),floral,.018)
tube('Apron upper piping',[(-.79,-.432,.305),(.79,-.432,.305)],.004,piping)
tube('Apron lower piping',[(-.79,-.432,.13),(.79,-.432,.13)],.004,piping)
box('Back frame',(0,.325,.60),(1.69,.12,.52),floral,.05)
for x in [-.555,0,.555]:
 soft_pillow('Back cushion',(x,.205,.69),(.515,.26,.60),floral)
 soft_pillow('Seat cushion',(x,-.055,.40),(.52,.57,.17),floral)
 # narrow sewn seams on upper cushion leading edge
for x in [-.91,.91]:
 box('Upholstered arm side',(x,0,.43),(.18,.76,.56),floral,.07)
 # rolled bolster along depth
 sphere('Rolled arm bolster',(x,-.02,.65),(.15,.40,.15),floral)
 sphere('Rolled arm front',(x,-.386,.65),(.145,.055,.145),floral)
 tube('Arm face piping',[(x+.115*math.cos(a),-.438,.65+.115*math.sin(a)) for a in [2*math.pi*k/48 for k in range(49)]],.003,piping)
for x in [-.79,.79]:
 for y in [-.29,.29]:
  sphere('Turned wooden foot',(x,y,.065),(.085,.085,.065),wood)
  sphere('Foot collar',(x,y,.12),(.065,.065,.025),wood)
# separate soft throw pillows
p=soft_pillow('Pillow teal',(-.55,.04,.68),(.35,.16,.36),teal);p.rotation_euler[1]=-.16;p.rotation_euler[2]=-.15;p.rotation_euler[0]=-.16
p=soft_pillow('Pillow rose',(-.30,-.02,.67),(.32,.16,.33),rose);p.rotation_euler[1]=.10;p.rotation_euler[2]=.15;p.rotation_euler[0]=-.12
# throw over right arm: surface grid with folds, independent object
verts=[];faces=[];nx,ny=17,25
for j in range(ny):
 v=j/(ny-1); y=-.34+v*.68
 for i in range(nx):
  u=i/(nx-1); x=.64+u*.47
  z=.815+.018*math.sin(v*math.pi*8+.7)+.010*math.sin(u*math.pi*4+v*3)
  if u>.80:z-=((u-.80)/.20)*.28
  verts.append((x,y,z))
for j in range(ny-1):
 for i in range(nx-1):
  a=j*nx+i;faces.append((a,a+1,a+1+nx,a+nx))
mesh=bpy.data.meshes.new('Throw weave');mesh.from_pydata(verts,[],faces);mesh.update();ob=bpy.data.objects.new('Cream throw',mesh);bpy.context.collection.objects.link(ob);ob.data.materials.append(cream)
uv=mesh.uv_layers.new(name='UVMap')
for poly in mesh.polygons:
 for li in poly.loop_indices:
  co=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=((co.x-.64)/.47,(co.y+.34)/.68)
for p in mesh.polygons:p.use_smooth=True
sol=ob.modifiers.new('cloth thickness','SOLIDIFY');sol.thickness=.007;bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.modifier_apply(modifier=sol.name);ob.select_set(False)
# tassels at front edge
for i in range(14):
 x=.66+i*.031; z=.81+.010*math.sin(i); tube('Throw tassel',[(x,-.342,z),(x+.004*math.sin(i),-.356,z-.06-.012*(i%3))],.002,cream)
# Tighten the width to the 2 m plan target, preserving floor origin.
for obj in list(bpy.context.scene.objects):
 if obj.type=='MESH':
  obj.location.x *= .94
  obj.scale.x *= .94
# meshes floor-centred; export assembly
bpy.ops.object.select_all(action='SELECT');
for o in bpy.context.selected_objects:
 if o.type=='MESH':
  for poly in o.data.polygons:
   if poly.area<1e-12: raise RuntimeError('degenerate '+o.name)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'model'/'LV-SOFA-01.blend'))
bpy.ops.export_scene.fbx(filepath=str(ROOT/'model'/'LV-SOFA-01.fbx'),use_selection=True,object_types={'MESH'},add_leaf_bones=False,apply_unit_scale=True)
# lighting and camera for review
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.object.camera_add(location=(3.1,-4.5,2.3));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.5))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.85;bpy.context.scene.camera=cam
for loc,power,size in [((0,-3,4),450,4),((-3,-1,2.7),220,3),((2,2,3),280,3)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,.5))-o.location).to_track_quat('-Z','Y').to_euler()
world=bpy.context.scene.world;world.color=(.3,.27,.23)
scene=bpy.context.scene;scene.render.resolution_x=1200;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=True;scene.render.filepath=str(ROOT/'previews'/'sofa-three-quarter.png');bpy.ops.render.render(write_still=True)
