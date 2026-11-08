import bpy, math, os
from mathutils import Vector
from pathlib import Path
P=Path(__file__).resolve().parent.parent
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
def material(name, color, metal=0, rough=.6, texture=None):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough
 if texture and (P/'textures'/texture).exists():
  t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(P/'textures'/texture),check_existing=True); m.node_tree.links.new(t.outputs['Color'],bs.inputs['Base Color'])
 return m
wood=material('Painted_Walnut',(.33,.13,.04),texture='walnut-painted-v2.png'); dark=material('Shadowed_Wood',(.19,.075,.025)); brass=material('Aged_Brass',(.54,.31,.09),.55,.42); mirror=material('Mirror',(.44,.48,.44),.65,.18); interior=material('Drawer_Interior',(.38,.20,.10))
groups={}
def register(o,group,mat):
 o.data.materials.append(mat);groups.setdefault(group,[]).append(o);return o
def cube(name,loc,dims,group,mat, bevel=.006):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  mod=o.modifiers.new('soft edges','BEVEL');mod.width=min(bevel,min(dims)*.22);mod.segments=3; bpy.ops.object.modifier_apply(modifier=mod.name)
 return register(o,group,mat)
def sphere(name,loc,scale,group,mat):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);bpy.ops.object.shade_smooth();return register(o,group,mat)
def cyl(name,loc,radius,depth,group,mat,rotation=(0,0,0)):
 bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=radius,depth=depth,location=loc,rotation=rotation);o=bpy.context.object;o.name=name;bpy.ops.object.shade_smooth();return register(o,group,mat)
# Carcass: floor to top .91m, footprint 1.15 x .40m; front faces -Y.
cube('top',(0,0,.905),(1.15,.40,.04),'body',wood,.012)
cube('lower rail',(0,0,.17),(1.08,.36,.045),'body',wood)
cube('back',(0,.175,.53),(1.03,.025,.70),'body',dark)
for x in [-.535,.535]: cube('side panel',(x,0,.535),(.055,.36,.70),'body',wood)
for z in [.20,.42,.64,.86]: cube('face rail',(0,-.149,z),(1.02,.032,.012),'body',wood,.003)
for x in [-.50,.50]:
 for y in [-.145,.145]:
  cyl('turned foot',(x,y,.09),.025,.18,'body',wood)
  sphere('foot collar',(x,y,.155),(.038,.038,.025),'body',wood)
  sphere('foot toe',(x,y,.025),(.030,.030,.025),'body',wood)
# Complete drawer boxes remain independent, with closed position at shared origin.
for i,z in enumerate([.30,.52,.74],1):
 g='drawer%d'%i
 cube('drawer front',(0,-.190,z),(.99,.027,.212),g,wood,.004)
 cube('drawer bottom',(0,-.01,z-.08),(.94,.31,.012),g,interior,.002)
 for x in [-.46,.46]: cube('drawer side',(x,-.01,z-.008),(.018,.31,.15),g,interior,.002)
 cube('drawer rear',(0,.145,z-.008),(.92,.018,.15),g,interior,.002)
 for x in [-.28,.28]:
  # domed brass cup back and lip, visible from front
  sphere('brass cup pull',(x,-.214,z+.005),(.057,.012,.025),g,brass)
  cube('pull lip',(x,-.226,z-.007),(.105,.009,.006),g,brass,.002)
  for dx in [-.044,.044]: sphere('pull screw',(x+dx,-.229,z+.002),(.004,.003,.004),g,dark)
# Pulls remain inside the 0.40 m footprint; shifting the drawer assemblies
# inward avoids extending the interaction hardware into the circulation path.
for key in ('drawer1','drawer2','drawer3'):
 for obj in groups[key]: obj.location.y += .03
# Mirror, separate asset; frame has a rounded arch approximated by smooth curves.
# Arch-top glass follows the outer frame rather than a rectangular panel.
verts=[(-.274,.104,1.005),(.274,.104,1.005),(.274,.104,1.53)]
verts += [(x,.104,1.53+.078*math.sqrt(max(0,1-(x/.274)**2))) for x in [.274-i*.548/24 for i in range(1,25)]]
me=bpy.data.meshes.new('mirror arch glass');me.from_pydata(verts,[],[list(range(len(verts)))]);me.update();o=bpy.data.objects.new('mirror arched glass',me);bpy.context.collection.objects.link(o);register(o,'mirror',mirror)
for x in [-.30,.30]:
 cyl('mirror post',(x,.115,1.26),.014,.65,'mirror',wood)
 sphere('post finial',(x,.115,1.59),(.027,.027,.027),'mirror',wood)
for z in [1.0]: cube('mirror horizontal rim',(0,.09,z),(.59,.025,.035),'mirror',wood,.008)
for x in [-.285,.285]:
 cube('mirror side rim',(x,.09,1.265),(.03,.025,.53),'mirror',wood,.008)
 sphere('arch corner junction',(x,.09,1.527),(.016,.015,.016),'mirror',wood)
 sphere('lower frame junction',(x,.09,1.0),(.017,.015,.017),'mirror',wood)
# Arc crown (frame rests on top edge, smooth curvature) 
pts=[]
for i in range(17):
 x=-.28+i*.035; z=1.53+.085*math.sqrt(max(0,1-(x/.28)**2));pts.append((x,.09,z))
curve=bpy.data.curves.new('arched mirror crown','CURVE');curve.dimensions='3D';curve.bevel_depth=.014;curve.bevel_resolution=3;sp=curve.splines.new('POLY');sp.points.add(len(pts)-1)
for q,co in zip(sp.points,pts): q.co=(*co,1)
o=bpy.data.objects.new('arched mirror crown',curve);bpy.context.collection.objects.link(o);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o.select_set(False);register(o,'mirror',wood)
# Set consistent UVs using cube projection where missing.
for o in [x for arr in groups.values() for x in arr]:
 if o.type=='MESH':
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
  bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT')
  if o.name.startswith('drawer front'):
   # Orient horizontal wood grain along the long face of every drawer.
   uv=o.data.uv_layers.active.data
   for poly in o.data.polygons:
    if abs(poly.normal.y) > .7:
     for li in poly.loop_indices:
      co=o.data.vertices[o.data.loops[li].vertex_index].co
      uv[li].uv=(co.x/1.05+.5,co.z/.80+.20+(o.location.z-.30)*.85)
# Join each assembly, preserve origin at floor and export separately.
for key,objs in groups.items():
 bpy.ops.object.select_all(action='DESELECT')
 for o in objs:o.select_set(True)
 bpy.context.view_layer.objects.active=objs[0];bpy.ops.object.join();o=bpy.context.object;o.name='BR_Dresser_'+key
 bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
 bpy.ops.export_scene.fbx(filepath=str(P/'model'/('BR_Dresser_'+key+'.fbx')),use_selection=True,object_types={'MESH'},add_leaf_bones=False)
# Camera, warm studio presentation.
world=bpy.context.scene.world;world.color=(.25,.20,.16)
bpy.ops.object.light_add(type='AREA',location=(1,-3,4));bpy.context.object.data.energy=500;bpy.context.object.data.size=4;bpy.context.object.data.color=(1.0,.84,.72)
bpy.ops.object.camera_add(location=(2.7,-4,2.45));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.85))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.15;bpy.context.scene.camera=cam
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=32;sc.render.resolution_x=1200;sc.render.resolution_y=1200;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.film_transparent=True
sc.render.filepath=str(P/'previews'/'dresser-closed.png');bpy.ops.render.render(write_still=True)
bpy.data.objects['BR_Dresser_drawer2'].location.y=-.22
sc.render.filepath=str(P/'previews'/'dresser-open.png');bpy.ops.render.render(write_still=True)
bpy.data.objects['BR_Dresser_drawer2'].location.y=0
bpy.ops.wm.save_as_mainfile(filepath=str(P/'model'/'BR-DRESSER-01.blend'))
