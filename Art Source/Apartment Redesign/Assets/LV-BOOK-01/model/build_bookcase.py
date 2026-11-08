"""LV-BOOK-01: Blender 5.x, metres, Z up, front -Y, common floor origin."""
import bpy, math, os, random
from mathutils import Vector
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
random.seed(27)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
def material(name,color,tex=None):
 m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=.8
 if tex:
  img=bpy.data.images.load(os.path.join(ROOT,'textures',tex),check_existing=True)
  node=m.node_tree.nodes.new('ShaderNodeTexImage'); node.image=img; m.node_tree.links.new(node.outputs['Color'],bs.inputs['Base Color'])
 return m
wood=material('Bookcase_Walnut',(.3,.12,.045),'walnut-painted.png'); dark=material('Bookcase_ShadowWood',(.19,.075,.03)); brass=material('Hardware_AgedBrass',(.47,.29,.11)); pages=material('Book_Pages',(.72,.63,.44)); ceramic=material('Ceramic_Pot',(.70,.58,.38)); ornament=material('Pot_Botanical',(.42,.24,.12)); soil=material('Pot_Soil',(.12,.075,.04)); leaf=material('Plant_Leaf',(.28,.38,.12)); leaf2=material('Plant_Leaf_Light',(.4,.46,.18))
cloth=[material('Book_Moss',(.1,.18,.08),'book-moss.png'),material('Book_Rust',(.32,.06,.035),'book-russet.png'),material('Book_Ochre',(.38,.21,.06)),material('Book_Teal',(.07,.18,.15)),material('Book_Brown',(.17,.065,.035))]
groups={'case':[],'books':[],'plant':[],'tin':[]}
def box(name,loc,dim,mat,g='case',bevel=.004):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=dim; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  mod=o.modifiers.new('soft edges','BEVEL');mod.width=min(bevel,min(dim)*.23);mod.segments=3
  bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 o.data.materials.append(mat);groups[g].append(o);return o
def cylinder(name,loc,r,depth,mat,g='case',verts=24):
 bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=depth,location=loc);o=bpy.context.object;o.name=name;o.data.materials.append(mat);groups[g].append(o);return o
# Shell; dimensions 1.25 x .40m. Vertical face frames conceal open edges.
box('back',(0,.177,1.01),(1.17,.022,1.90),wood)
for x in [-.575,.575]:
 box('side', (x,0,1.01),(.035,.38,1.9),wood)
 box('front stile',(x,-.19,1.01),(.045,.028,1.9),wood)
for z in [.10,.53,1.00,1.47,1.96]:
 box('shelf' if z<1.9 else 'top',(0,-.002,z),(1.16,.375,.035),wood)
 box('shelf front lip',(0,-.195,z-.01),(1.13,.022,.035),wood)
# Distinct crown and period plinth, modest edge bevel, dimensional silhouette.
box('crown lower',(0,0,1.975),(1.20,.39,.05),wood)
box('crown stepped',(0,-.002,2.015),(1.23,.40,.035),wood)
box('crown cap',(0,-.002,2.043),(1.25,.40,.025),wood)
box('plinth front',(0,-.174,.045),(1.22,.04,.09),wood)
for x in [-.57,.57]:box('plinth return',(x,0,.045),(.06,.37,.09),wood)
# Exposed shelf pin holes, thin dark inset studs arranged as detail.
for x in [-.548,.548]:
 for z in [.67,.73,.79,1.14,1.20,1.26,1.61,1.67,1.73]:
  o=cylinder('shelf pin', (x,-.12,z),.006,.003,dark);o.rotation_euler[1]=math.pi/2
# Individual volumes: colored cloth cover and inset pages with separate objects.
def book(x,z,w,h,color,angle=0):
 y=-.12; depth=.20; cover=box('book cover',(x,y,z+h/2),(w,depth,h),color,'books',.003);cover.rotation_euler[1]=angle
 inset=box('book pages',(x,y+.008,z+h/2),(max(.012,w-.008),depth-.018,h-.01),pages,'books',.001);inset.rotation_euler[1]=angle
 top=box('page top',(x,y+.012,z+h-.004),(max(.01,w-.009),depth-.025,.003),pages,'books',.0003);top.rotation_euler[1]=angle
 # decorative horizontal spine rules
 for dz in [.08,h-.08]:
  if dz>0:
   band=box('spine gilt',(x,-.223,z+dz),(w*.84,.004,.003),brass,'books',.0005);band.rotation_euler[1]=angle
for shelf, start, count in [(1.49,.14,6),(1.02,.17,7),(.55,-.43,6)]:
 x=start
 for i in range(count):
  w=.035+random.random()*.025;h=.23+random.random()*.13
  angle=([-.09,-.05,0,.02,.06][i%5] if i in (0,1,count-1) else 0)
  book(x+w/2,shelf+.029,w,h,cloth[(i+int(shelf*10))%len(cloth)],angle);x+=w+.008
# stack lying flat on middle shelf
for i,c in enumerate([cloth[0],cloth[2],cloth[1]]):
 box('lying book',(-.26,-.105,1.045+.025*i),(.26,.18,.022),c,'books',.002)
 box('lying page block',(-.26,-.199,1.045+.025*i),(.23,.006,.014),pages,'books',.001)
# Decorative pottery plant, separate set to allow layout reuse.
bpy.ops.mesh.primitive_cone_add(vertices=32,radius1=.07,radius2=.095,depth=.16,location=(-.33,-.08,1.57));o=bpy.context.object;o.name='tapered ceramic pot';o.data.materials.append(ceramic);groups['plant'].append(o)
cylinder('pot lip',(-.33,-.08,1.65),.107,.025,ceramic,'plant',32)
cylinder('soil',(-.33,-.08,1.667),.09,.007,soil,'plant',32)
for x in [-.38,-.34,-.30,-.26]:
 bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=6,location=(x,-.173,1.58));o=bpy.context.object;o.name='pot botanical accent';o.scale=(.016,.002,.018);o.data.materials.append(ornament);groups['plant'].append(o)
for i in range(13):
 a=i*2.4; r=.06+(i%4)*.035; h=1.75+(i%4)*.035
 pos=Vector((-.33+r*math.cos(a),-.08+r*math.sin(a),h)); base=Vector((-.33,-.08,1.67));d=pos-base
 bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=.0025,depth=d.length,location=(pos+base)/2);o=bpy.context.object;o.name='plant stem';o.rotation_euler=d.to_track_quat('Z','Y').to_euler();o.data.materials.append(leaf);groups['plant'].append(o)
 bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,location=pos);o=bpy.context.object;o.name='leaf';o.scale=(.065,.034,.014);o.rotation_euler=(0,.35,a);o.data.materials.append(leaf2 if i%3==0 else leaf);groups['plant'].append(o)
# Trailing vine: connected descending stems and pairs of pointed leaves.
prev=Vector((-.34,-.15,1.70))
for i in range(6):
 pos=Vector((-.37-.025*math.sin(i),-.20-.014*i,1.64-.048*i));d=pos-prev
 bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=.0025,depth=d.length,location=(pos+prev)/2);o=bpy.context.object;o.name='trailing vine';o.rotation_euler=d.to_track_quat('Z','Y').to_euler();o.data.materials.append(leaf);groups['plant'].append(o)
 for side in [-1,1]:
  bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,location=(pos.x+side*.045,pos.y,pos.z));o=bpy.context.object;o.name='trailing leaf';o.scale=(.055,.025,.012);o.rotation_euler=(.2,side*.35,side*.7);o.data.materials.append(leaf2 if i%2 else leaf);groups['plant'].append(o)
 prev=pos
# little decorative lidded tin
box('tin body',(.29,-.09,.64),(.20,.14,.14),ceramic,'tin',.006);box('tin lid',(.29,-.09,.718),(.21,.15,.018),brass,'tin',.003);cylinder('tin knob',(.29,-.09,.733),.014,.016,brass,'tin')
# Join each category into independent export mesh; same floor-based pivot.
def export_group(group):
 bpy.ops.object.select_all(action='DESELECT')
 for o in groups[group]: o.select_set(True)
 bpy.context.view_layer.objects.active=groups[group][0]
 if group=='case':
  bpy.ops.object.join(); o=bpy.context.object; o.name='LV_BOOK_CASE'; bpy.context.scene.cursor.location=(0,0,0); bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
 bpy.ops.export_scene.fbx(filepath=os.path.join(ROOT,'model','LV_BOOK_'+group.upper()+'.fbx'),use_selection=True,object_types={'MESH'},add_leaf_bones=False,apply_unit_scale=True)
for group in groups: export_group(group)
# Camera, neutral warm studio preview.
world=bpy.context.scene.world or bpy.data.worlds.new('World');bpy.context.scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.20,.17,.13,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.5
bpy.ops.object.light_add(type='AREA',location=(2,-4,5));key=bpy.context.object;key.data.energy=600;key.data.color=(1,.76,.52);key.data.shape='DISK';key.data.size=5
bpy.ops.object.light_add(type='AREA',location=(-3,-2,3));bpy.context.object.data.energy=220;bpy.context.object.data.color=(1,.88,.68);bpy.context.object.data.size=4
bpy.ops.object.camera_add(location=(3,-5,2.8));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,1.05))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.75;bpy.context.scene.camera=cam
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=32;sc.render.resolution_x=1200;sc.render.resolution_y=1200;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.film_transparent=True
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'model','LV-BOOK-01.blend'));sc.render.filepath=os.path.join(ROOT,'previews','bookcase-three-quarter.png');bpy.ops.render.render(write_still=True)
