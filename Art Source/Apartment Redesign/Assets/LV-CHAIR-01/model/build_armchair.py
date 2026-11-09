import bpy, math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent.parent
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32

def material(name,color,tex=None):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=.88
 if tex:
  im=m.node_tree.nodes.new('ShaderNodeTexImage');im.image=bpy.data.images.load(str(tex),check_existing=True);m.node_tree.links.new(im.outputs['Color'],bs.inputs['Base Color'])
 if name=='Terracotta painted floral':
  mult=m.node_tree.nodes.new('ShaderNodeMixRGB');mult.blend_type='MULTIPLY';mult.inputs[0].default_value=1;mult.inputs[2].default_value=(.72,.66,.56,1)
  m.node_tree.links.new(im.outputs['Color'],mult.inputs[1]);m.node_tree.links.new(mult.outputs['Color'],bs.inputs['Base Color'])
 return m
fabric=material('Terracotta painted floral',(.48,.16,.08),ROOT/'textures/floral-candidate-a.png');wood=material('Aged dark walnut',(.20,.08,.035));seam=material('Subdued piping',(.29,.11,.05));lace=material('Ivory lace',(.83,.76,.61),ROOT/'textures/lace-knit.png')

def uv_planar(o,scale=.72):
 uv=o.data.uv_layers.active or o.data.uv_layers.new(name='UVMap')
 for f in o.data.polygons:
  n=f.normal;axis=max(range(3),key=lambda k:abs(n[k]))
  for li in f.loop_indices:
   v=o.data.vertices[o.data.loops[li].vertex_index].co
   a,b=((v.y,v.z) if axis==0 else ((v.x,v.z) if axis==1 else (v.x,v.y)))
   uv.data[li].uv=(a/scale+.5,b/scale+.5)
def rounded(name,loc,dims,mat,bevel=.04):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 b=o.modifiers.new('Soft upholstery edge','BEVEL');b.width=min(bevel,min(dims)*.43);b.segments=5;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=b.name)
 for f in o.data.polygons:f.use_smooth=True
 n=o.modifiers.new('Weighted normals','WEIGHTED_NORMAL');n.keep_sharp=True;bpy.ops.object.modifier_apply(modifier=n.name)
 if mat==fabric:uv_planar(o)
 o.data.materials.append(mat);return o

def pillow(name,loc,dims,mat):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=24,location=loc);o=bpy.context.object;o.name=name
 def power(v):return math.copysign(abs(v)**.50,v)
 for v in o.data.vertices:
  v.co.x=power(v.co.x)*dims[0]*.5;v.co.y=power(v.co.y)*dims[1]*.5;v.co.z=power(v.co.z)*dims[2]*.5
 o.data.update()
 for p in o.data.polygons:p.use_smooth=True
 uv_planar(o);o.data.materials.append(mat);return o

def tube(name,pts,r,mat):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.resolution_u=12;c.bevel_depth=r;c.bevel_resolution=3;s=c.splines.new('POLY');s.points.add(len(pts)-1)
 for p,co in zip(s.points,pts):p.co=(*co,1)
 o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o);o.data.materials.append(mat);bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH');o.select_set(False);return o
# front is -Y, bottom Z=0.  Overall ~0.75 x 0.70 x 0.93 m.
rounded('Upholstered lower body',(0,0,.235),(.69,.63,.29),fabric,.055)
rounded('Front apron',(0,-.313,.205),(.56,.018,.18),fabric,.007)
# Back leans very slightly back, independent cushion gives visual layering
back=rounded('High upholstered back',(0,.255,.625),(.61,.15,.62),fabric,.07);back.rotation_euler.x=-.06
backpad=pillow('Soft back cushion',(0,.166,.66),(.53,.18,.55),fabric);backpad.rotation_euler.x=-.06
pillow('Seat cushion',(0,-.045,.408),(.52,.49,.15),fabric)
for x in [-.295,.295]:
 rounded('Side arm body',(x,-.005,.385),(.15,.63,.48),fabric,.055)
 p=pillow('Rounded rolled arm',(x,-.015,.60),(.18,.64,.17),fabric)
 # A subtle seam around the upholstered front roll, sitting close to its surface.
 # The face is part of the roll itself, so avoid broad floating piping.
 rollface=pillow('Upholstered arm roll end',(x,-.322,.60),(.16,.032,.145),fabric)
 pts=[(x+.073*math.cos(a),-.343,.60+.064*math.sin(a)) for a in [2*math.pi*i/48 for i in range(49)]]
 tube('Roll end seam',pts,.0007,seam)
def turned_foot(x,y):
 # Lathed walnut foot: narrow ankle, bell-shaped shoulder and rounded toe.
 profile=[(0,.000),(0.022,.000),(.030,.006),(.034,.018),(.032,.028),(.027,.037),(.026,.071),(.034,.082),(.041,.087),(.041,.100),(.031,.108),(0,.108)]
 n=32; vs=[]; fs=[]
 for radius,z in profile:
  for i in range(n):
   a=2*math.pi*i/n; vs.append((x+radius*math.cos(a),y+radius*math.sin(a),z))
 for j in range(len(profile)-1):
  for i in range(n):
   a=j*n+i;b=j*n+(i+1)%n;c=(j+1)*n+(i+1)%n;d=(j+1)*n+i
   if profile[j][0]==0:fs.append((a,c,d))
   elif profile[j+1][0]==0:fs.append((a,b,c))
   else:fs.append((a,b,c,d))
 mesh=bpy.data.meshes.new('Turned walnut foot');mesh.from_pydata(vs,[],fs);mesh.update();o=bpy.data.objects.new('Turned walnut foot',mesh);bpy.context.collection.objects.link(o)
 for f in mesh.polygons:f.use_smooth=True
 uv_planar(o);o.data.materials.append(wood)
for x in [-.28,.28]:
 for y in [-.245,.245]: turned_foot(x,y)
# Draped lace panel follows the crown; scalloped lower edge and painted crochet material.
verts=[];faces=[];nx=49;ny=31
for j in range(ny):
 v=j/(ny-1)
 for i in range(nx):
  u=i/(nx-1); x=(u-.5)*.38
  # hangs on the front of the rounded back, with a soft scalloped edge
  z=.91-v*(.19*math.sqrt(max(0.001,1-(2*u-1)**2))+.009*math.cos(u*math.pi*12))
  y=.068 - .012*math.sin(v*math.pi) + .004*math.cos(u*math.pi*4)
  verts.append((x,y,z))
for j in range(ny-1):
 for i in range(nx-1):
  a=j*nx+i
  # Openwork holes are geometry rather than alpha, eliminating masked halos.
  # Leave borders and thin connecting threads intact.
  hole = 3 <= j < ny-4 and 3 <= i < nx-4 and (i%6 in (2,3)) and (j%6 in (2,3))
  if not hole: faces.append((a,a+1,a+1+nx,a+nx))
mesh=bpy.data.meshes.new('Crochet drape');mesh.from_pydata(verts,[],faces);mesh.update();ob=bpy.data.objects.new('Lace antimacassar',mesh);bpy.context.collection.objects.link(ob);ob.data.materials.append(lace)
uv=mesh.uv_layers.new(name='UVMap')
for poly in mesh.polygons:
 for li in poly.loop_indices:
  co=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=((co.x+.19)/.38,(.91-co.z)/.21)
for p in mesh.polygons:p.use_smooth=True
bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
mod=ob.modifiers.new('cloth thickness','SOLIDIFY');mod.thickness=.002;bpy.ops.object.modifier_apply(modifier=mod.name)
# Fit the 0.75 m design envelope while preserving the floor origin.
for obj in list(scene.objects):
 if obj.type=='MESH': obj.location.x *= .973; obj.scale.x *= .973
# End the mesh work before adding lights or cameras: no light/camera in exports.
bpy.ops.object.select_all(action='SELECT')
for o in bpy.context.selected_objects:
 if o.type=='MESH':
  for f in o.data.polygons:
   if f.area<1e-12:raise RuntimeError('Degenerate '+o.name)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'model/LV-CHAIR-01.blend'))
bpy.ops.export_scene.fbx(filepath=str(ROOT/'model/LV-CHAIR-01.fbx'),use_selection=True,object_types={'MESH'},add_leaf_bones=False,apply_unit_scale=True)
bpy.ops.object.select_all(action='DESELECT');bpy.ops.object.camera_add(location=(2.2,-3.2,1.75));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.48))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=1.47;scene.camera=cam
for loc,power,size in [((0,-3,3.6),350,3),((-2,-1,2.6),160,2.5),((2,2,3),200,2.5)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,.5))-o.location).to_track_quat('-Z','Y').to_euler()
scene.world.color=(.32,.27,.22);scene.render.resolution_x=1100;scene.render.resolution_y=1100;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=True;scene.render.filepath=str(ROOT/'previews/armchair-three-quarter.png');bpy.ops.render.render(write_still=True)
