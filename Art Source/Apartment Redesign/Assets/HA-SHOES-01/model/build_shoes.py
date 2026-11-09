"""HA-SHOES-01: tray and four independently exported shoes; metres, Z up."""
import bpy, math, bmesh
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent.parent; M=P/'model'; T=P/'textures'; O=P/'previews'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)

def flat(name,color,rough=.75,metal=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*color,1);b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=metal;return m

def image_mat(name,offset,scale):
 m=flat(name,(.4,.3,.2),.83);n=m.node_tree.nodes;l=m.node_tree.links
 img=n.new('ShaderNodeTexImage');img.image=bpy.data.images.load(str(T/'leather-canvas-sheet.png'),check_existing=True);img.image.pack();v=n.new('ShaderNodeUVMap');mult=n.new('ShaderNodeVectorMath');mult.operation='MULTIPLY';mult.inputs[1].default_value=scale;add=n.new('ShaderNodeVectorMath');add.operation='ADD';add.inputs[1].default_value=offset;l.new(v.outputs['UV'],mult.inputs[0]);l.new(mult.outputs['Vector'],add.inputs[0]);l.new(add.outputs['Vector'],img.inputs['Vector']);l.new(img.outputs['Color'],n.get('Principled BSDF').inputs['Base Color']);return m
leather=image_mat('Chestnut leather – sheet left',(.02,.03,0),(.47,.94,1));canvas=image_mat('Sage canvas – sheet right',(.51,.03,0),(.47,.94,1))
metal=flat('Aged warm metal tray',(.19,.13,.08),.68,.62);rim=flat('Warm rubbed rim',(.39,.27,.14),.65,.52)
sole=flat('Worn dark sole',(.12,.085,.055),.9);rubber=flat('Cream rubber sole',(.62,.56,.43),.95)
lining=flat('Warm dark lining',(.12,.075,.045),.95);thread=flat('Laces and stitches',(.23,.13,.07),.9);lightthread=flat('Canvas stitching',(.38,.40,.29),.94)

def uv(o):
 if o.type=='MESH' and not o.data.uv_layers: o.data.uv_layers.new(name='UVMap')
 return o

def box(name,loc,dim,mat,bevel=.0015):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  mod=o.modifiers.new('soft edges','BEVEL');mod.width=bevel;mod.segments=2;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 o.data.materials.append(mat);return uv(o)

def sphere(name,loc,scale,mat):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat);bpy.ops.object.shade_smooth();return uv(o)

def tube(name,pts,r,mat):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.resolution_u=12;c.bevel_depth=r;c.bevel_resolution=2;s=c.splines.new('BEZIER');s.bezier_points.add(len(pts)-1)
 for b,p in zip(s.bezier_points,pts): b.co=p;b.handle_left_type='AUTO';b.handle_right_type='AUTO'
 o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o);o.data.materials.append(mat);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False);uv(o)
 # Planar mapping for converted tubing, enough for solid-color materials.
 return o

def join(name,parts,origin):
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();o=bpy.context.object;o.name=name;bpy.context.scene.cursor.location=origin;bpy.ops.object.origin_set(type='ORIGIN_CURSOR');return o

def export(o,name):
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.export_scene.fbx(filepath=str(M/(name+'.fbx')),use_selection=True,object_types={'MESH'},add_leaf_bones=False,apply_unit_scale=True)

# Shallow physically open tray. Handles stay inside outer 0.38 × 0.25 footprint.
parts=[box('Tray floor',(0,0,.004),(.372,.242,.008),metal,.003)]
for y in (-.121,.121):parts.append(box('Long raised rim',(0,y,.014),(.378,.006,.022),metal,.002))
for x in (-.186,.186):parts.append(box('End raised rim',(x,0,.014),(.006,.242,.022),metal,.002))
for y in (-.121,.121):parts.append(box('Long rim highlight',(0,y,.025),(.371,.002,.002),rim,.0005))
for x in (-.186,.186):parts.append(box('End rim highlight',(x,0,.025),(.002,.236,.002),rim,.0005))
for x in (-.184,.184):parts.append(tube('Inset tray handle',[(x,-.025,.022),(x,-.025,.043),(x,0,.051),(x,.025,.043),(x,.025,.022)],.0015,rim))
tray=join('HA_ShoeTray',parts,(0,0,0));export(tray,'HA_ShoeTray')

def open_upper(x,mat):
 o=sphere('Open upper',(x,-.004,.045),(.038,.105,.038),mat)
 cutter=sphere('Temporary cavity cutter',(x,.052,.081),(.026,.034,.030),lining)
 bpy.context.view_layer.objects.active=o
 mod=o.modifiers.new('Foot opening','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
 bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
 return o

# Each shoe is a separate mesh with its origin at its own sole centre.
positions=(-.135,-.045,.045,.135); shoes=[]
for index,x in enumerate(positions):
 is_oxford=index<2; color=leather if is_oxford else canvas;solemat=sole if is_oxford else rubber
 parts=[]
 parts.append(sphere('Sole',(x,0,.016),(.040,.111,.008),solemat))
 parts.append(box('Low heel',(x,.068,.013),(.048,.040,.010),solemat,.002))
 # Upper shoe silhouette: broad toe, lower vamp and heel, built as shaded UV surfaces.
 parts.append(open_upper(x,color))
 parts.append(sphere('Interior lining',(x,.053,.056),(.023,.030,.0015),lining))
 def sz(dx,yy):
  v=max(0,1-(dx/.038)**2-((yy+.004)/.105)**2)
  return .045+.038*math.sqrt(v)+.0014
 # A curved toe seam follows the upper, and a fine lip follows the opening.
 seam=[(x+dx,-.067,sz(dx,-.067)) for dx in (-.022,-.012,0,.012,.022)]
 parts.append(tube('Toe construction seam',seam,.00035,thread if is_oxford else lightthread))
 if is_oxford:
  # Laces follow the curved upper surface rather than floating or disappearing into it.
  for yy in (-.040,-.020,0):
   left=(x-.023,yy-.006,sz(-.023,yy-.006));mid=(x,yy,sz(0,yy)+.001);right=(x+.023,yy+.006,sz(.023,yy+.006))
   parts.append(tube('Crossing lace A',[left,mid,right],.0009,thread))
   left=(x+.023,yy-.006,sz(.023,yy-.006));right=(x-.023,yy+.006,sz(-.023,yy+.006))
   parts.append(tube('Crossing lace B',[left,mid,right],.0009,thread))
  # Small paired tied loops sit above the upper at the top of the lacing.
  cy=-.004;z=sz(0,cy)+.003
  for side in (-1,1):
   loop=[(x,cy,z),(x+side*.012,cy-.004,z+.002),(x+side*.017,cy+.004,z+.002),(x+side*.010,cy+.011,z+.002),(x,cy,z)]
   parts.append(tube('Tied lace loop',loop,.00085,thread))
   parts.append(tube('Loose lace end',[(x,cy,z),(x+side*.010,cy-.013,sz(side*.010,cy-.013)+.003),(x+side*.015,cy-.025,sz(side*.015,cy-.025)+.002)],.0007,thread))
 else:
  # Split vamp seams give the canvas slip-on readable assembled construction.
  for side in (-1,1):
   pts=[]
   for yy in (-.052,-.036,-.018,0,.016):
    dx=side*.026;pts.append((x+dx,yy,sz(dx,yy)))
   parts.append(tube('Canvas vamp side seam',pts,.00035,lightthread))
 o=join(('Oxford' if is_oxford else 'SlipOn')+str(index+1),parts,(x,0,.008))
 # Taper the heel slightly and offset the toe toward opposite sides for left/right shoes.
 # The deformation acts on every joined detail so sole, upper and stitches remain aligned.
 side=-1 if index%2==0 else 1
 for vert in o.data.vertices:
  yy=vert.co.y;toe=max(0,min(1,(-yy+.015)/.12));heel=max(0,min(1,(yy-.005)/.10))
  vert.co.x=vert.co.x*(1-.12*heel)+side*.0022*toe
 # The boolean cavity can create near-zero triangles. Remove them explicitly before export.
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.triangulate(bm,faces=list(bm.faces))
 tiny=[f for f in bm.faces if f.calc_area()<=1e-10]
 if tiny:bmesh.ops.delete(bm,geom=tiny,context='FACES')
 loose=[v for v in bm.verts if not v.link_faces]
 if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
 bm.to_mesh(o.data);bm.free();o.data.update()
 shoes.append(o);export(o,('HA_Oxford_' if is_oxford else 'HA_SlipOn_')+str(index%2+1))

scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.render.resolution_x=1200;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=True;scene.world.color=(.15,.13,.12)
for loc,energy,size in [((1,-2,2),150,3),((-1,1,1.4),75,2)]:
 bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.data.energy=energy;l.data.size=size
bpy.ops.object.camera_add(location=(.72,-1.0,.70));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.04))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.56;scene.camera=cam
scene.render.filepath=str(O/'tray-perspective.png');bpy.ops.render.render(write_still=True)
cam.location=(0,0,1.5);cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.48;scene.render.filepath=str(O/'tray-top.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(M/'HA-SHOES-01.blend'))
for o in [tray]+shoes:print('BOUNDS',o.name,tuple(round(v,5) for v in o.dimensions),'ORIGIN',tuple(round(v,5) for v in o.location))
