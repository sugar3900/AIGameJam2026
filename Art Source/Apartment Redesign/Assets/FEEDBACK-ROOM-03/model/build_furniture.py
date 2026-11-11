from pathlib import Path
import bpy,math,json,random
from mathutils import Vector
P=Path(__file__).resolve().parent.parent;A=P.parent
bpy.context.preferences.filepaths.save_version=0
report={}
def export(parts,name,axes=False):
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0]
 bpy.ops.export_scene.fbx(filepath=str(P/'model'/f'{name}.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,add_leaf_bones=False,axis_forward='-Y' if axes else '-Z',axis_up='Z' if axes else 'Y')
 report[name]={'objects':len(parts),'bounds':[[min((o.matrix_world@v.co)[i] for o in parts for v in o.data.vertices) for i in range(3)],[max((o.matrix_world@v.co)[i] for o in parts for v in o.data.vertices) for i in range(3)]],'axes':['-Y','Z'] if axes else ['-Z','Y']}
def render(name,target,loc,scale):
 sc=bpy.context.scene
 for o in list(sc.objects):
  if o.type in {'CAMERA','LIGHT'}:bpy.data.objects.remove(o,do_unlink=True)
 bpy.ops.object.camera_add(location=loc);cam=bpy.context.object;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=scale;sc.camera=cam
 for xyz,power in [(loc,300),((-2,2,4),200)]:
  bpy.ops.object.light_add(type='AREA',location=xyz);o=bpy.context.object;o.data.energy=power;o.data.size=3;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
 sc.render.engine='CYCLES';sc.cycles.samples=12;sc.render.threads_mode='FIXED';sc.render.threads=2;sc.render.resolution_x=720;sc.render.resolution_y=640;sc.render.resolution_percentage=100;sc.render.film_transparent=True;sc.render.image_settings.file_format='PNG';sc.render.filepath=str(P/'previews'/f'{name}.png');bpy.ops.render.render(write_still=True)
def box(n,loc,dims,mat,b=.003):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=n;o.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if b:
  mod=o.modifiers.new('Eased corners','BEVEL');mod.width=min(b,min(dims)*.24);mod.segments=3;bpy.ops.object.modifier_apply(modifier=mod.name)
 o.data.materials.append(mat)
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT');return o

def pillow(n,center,width,depth,height,mat,rot=(0,0,0)):
 # Sewn rectangular envelope, shallow compressed edges and broad gently inflated faces.
 nx,ny=24,20;vs=[];fs=[]
 for side in [-1,1]:
  for j in range(ny+1):
   v=j/ny;y=(v-.5)*depth
   for i in range(nx+1):
    u=i/nx;x=(u-.5)*width
    # Corners draw inward along the seam; broad top avoids ellipsoid/lump shape.
    x*=1-.055*(abs(2*v-1)**8);y1=y*(1-.055*abs(2*u-1)**8)
    loft=(math.sin(math.pi*u)*math.sin(math.pi*v))**.48
    wrinkle=.0035*math.sin(u*41+v*17)*math.exp(-min(u,1-u,v,1-v)*14)
    z=side*(.007+height*.5*loft)+wrinkle
    vs.append((x,y1,z))
 N=(nx+1)*(ny+1)
 for k,side in enumerate([-1,1]):
  for j in range(ny):
   for i in range(nx):
    a=k*N+j*(nx+1)+i;f=(a,a+1,a+nx+2,a+nx+1);fs.append(tuple(reversed(f)) if side<0 else f)
 perimeter=list(range(nx+1))+[j*(nx+1)+nx for j in range(1,ny+1)]+[ny*(nx+1)+i for i in range(nx-1,-1,-1)]+[j*(nx+1) for j in range(ny-1,0,-1)]
 for a,b in zip(perimeter,perimeter[1:]+perimeter[:1]):fs.append((a,b,b+N,a+N))
 me=bpy.data.meshes.new(n);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(n,me);bpy.context.collection.objects.link(o);o.location=center;o.rotation_euler=rot;me.materials.append(mat);uv=me.uv_layers.new()
 for f in me.polygons:
  f.use_smooth=True
  for li in f.loop_indices:
   co=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(co.x/width+.5,co.y/depth+.5)
 cu=bpy.data.curves.new(n+' sewn welt','CURVE');cu.dimensions='3D';cu.bevel_depth=.0015;cu.bevel_resolution=2;sp=cu.splines.new('POLY');sp.points.add(len(perimeter)-1);sp.use_cyclic_u=True
 for p,idx in zip(sp.points,perimeter):p.co=(*vs[idx][:2],0,1)
 seam=bpy.data.objects.new(n+' sewn welt',cu);bpy.context.collection.objects.link(seam);seam.location=center;seam.rotation_euler=rot;cu.materials.append(mat);bpy.ops.object.select_all(action='DESELECT');seam.select_set(True);bpy.context.view_layer.objects.active=seam;bpy.ops.object.convert(target='MESH');return [o,bpy.context.object]
# Bed: preserve stable frame/bedding origin and source axis convention.
bpy.ops.wm.open_mainfile(filepath=str(A/'BR-BED-01/model/BR-BED-01.blend'))
for o in list(bpy.context.scene.objects):
 if o.name.startswith(('Soft pillow','Pillow seam')):bpy.data.objects.remove(o,do_unlink=True)
ivory=bpy.data.materials['Ivory_Cotton'];wood=bpy.data.materials['Painted_Walnut']
for x in [-.34,.34]:pillow('Sewn bed pillow',(x,.60,.696),.60,.45,.125,ivory,(.12,0,x*.08))
# Raised frame outlining recessed arched fields, with grain along actual boards.
for y,top,base in [(.9,1.07,.31),(-.9,.70,.20)]:
 for x in [-.59,.59]:box('Panel frame stile',(x,y-.04,(top+base-.06)/2),(.055,.025,top-base-.06),wood)
 box('Panel lower rail',(0,y-.04,base+.055),(1.2,.025,.06),wood)
 for x in [-.20,.20]:box('Panel dividing muntin',(x,y-.041,(top+base-.06)/2),(.022,.018,top-base-.06),wood,.002)
parts=[o for o in bpy.context.scene.objects if o.type=='MESH'];soft=('Mattress','Sewn bed pillow','Floral patchwork quilt','Dusty rose throw','Throw fringe')
export([o for o in parts if not o.name.startswith(soft)],'BR_Bed03_Frame');export([o for o in parts if o.name.startswith(soft)],'BR_Bed03_Bedding');render('bed-sewn-pillows',(0,0,.55),(3,-4,2.5),2.7);bpy.ops.wm.save_as_mainfile(filepath=str(P/'model/Bed03.blend'))
# Daybed keeps exact original frame, mattress becomes compressed/tufted with sewn corners.
bpy.ops.wm.open_mainfile(filepath=str(A/'OF-DAYBED-01/model/OF_DAYBED_Source.blend'))
for o in list(bpy.context.scene.objects):
 if o.name.startswith(('Sage cushion','Rose cushion','Mattress')):bpy.data.objects.remove(o,do_unlink=True)
linen=bpy.data.materials['Ivory linen'];sage=bpy.data.materials['Sage cloth'];rose=bpy.data.materials['Rose knit']
pillow('Soft daybed mattress',(0,0,.408),1.68,.64,.175,linen)
pillow('Sage sewn cushion',(.61,.065,.56),.33,.37,.11,sage,(0,-.29,.08));pillow('Rose sewn cushion',(.41,-.14,.55),.27,.25,.095,rose,(.08,-.09,-.17))
# Support retained quilt and stitched hem on the new mattress, keeping outboard hanging fabric.
from mathutils.bvhtree import BVHTree
def surface_tree(ob):return BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[list(p.vertices) for p in ob.data.polygons],all_triangles=False)
bpy.context.view_layer.update();mattress=bpy.data.objects['Soft daybed mattress'];support=surface_tree(mattress)
cloths=[ob for ob in bpy.context.scene.objects if ob.type=='MESH' and ob.name.startswith(('Floral quilt drape','Quilt stitched hem'))]
for ob in cloths:
 inv=ob.matrix_world.inverted()
 for vert in ob.data.vertices:
  world=ob.matrix_world@vert.co
  hit=support.ray_cast(Vector((world.x,world.y,2)),Vector((0,0,-1)),3)[0]
  if hit is not None and world.z<hit.z+.012:world.z=hit.z+.012;vert.co=inv@world
 ob.data.update()
bpy.context.view_layer.update()
contacts={ob.name:len(surface_tree(ob).overlap(support)) for ob in cloths}
assert not any(contacts.values()),('daybed quilt/mattress intersections',contacts)
(P/'daybed-contact-validation.json').write_text(json.dumps({'mattress_cloth_intersections':contacts,'supported_vertex_clearance_m':.012,'hanging_section':'preserved outside mattress XY footprint'},indent=2))
parts=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith(('Soft daybed mattress','Sage sewn cushion','Rose sewn cushion','Floral quilt drape','Quilt stitched hem'))];export(parts,'OF_Daybed03_Bedding',True);render('daybed-sewn',(0,0,.4),(3,-4,2.5),2.6);bpy.ops.wm.save_as_mainfile(filepath=str(P/'model/Daybed03.blend'))
# Books and plant: original shelf locations preserved; separate covers and page blocks avoid opaque cover hiding pages.
bpy.ops.wm.open_mainfile(filepath=str(A/'LV-BOOK-01/model/LV-BOOK-01.blend'))
for o in list(bpy.context.scene.objects):
 if o.type=='MESH' and (o.name.startswith(('book ','page ','spine ','lying ','leaf','plant stem','trailing '))):bpy.data.objects.remove(o,do_unlink=True)
cloth=[bpy.data.materials[n] for n in ['Book_Moss','Book_Rust','Book_Ochre','Book_Teal','Book_Brown']];pages=bpy.data.materials['Book_Pages'];brass=bpy.data.materials['Hardware_AgedBrass'];new=[];random.seed(27)
for shelf,start,count in [(1.49,.14,6),(1.02,.17,7),(.55,-.43,6)]:
 x=start
 for i in range(count):
  w=.035+random.random()*.025;h=.23+random.random()*.13;cx=x+w/2;mat=cloth[(i+int(shelf*10))%len(cloth)];z=shelf+.029
  # U-shaped book casing with open fore edge at rear; readable pages at top/bottom and fore edge.
  new += [box('Book03 pages',(cx,-.111,z+h/2),(w-.009,.182,h-.010),pages,.001)]
  for sx in [-1,1]:new.append(box('Book03 cover',(cx+sx*(w/2-.002),-.12,z+h/2),(.004,.20,h),mat,.001))
  new.append(box('Book03 rounded spine',(cx,-.218,z+h/2),(w,.010,h),mat,.004))
  for dz in [.045,h-.045]:new.append(box('Book03 gilt band',(cx,-.224,z+dz),(w*.83,.001,.002),brass,.0002))
  for k in range(6):new.append(box('Book03 page edge',(cx,-.111,z+.007+k*(h-.014)/5),(w-.010,.181,.0006),pages,.0001))
  x+=w+.008
export(new,'LV_Book03_Books')
# Thin pointed leaves follow connected curved petioles, no disc or solid ellipsoid foliage.
leafmat=bpy.data.materials['Plant_Leaf'];light=bpy.data.materials['Plant_Leaf_Light'];new=[]
for m,filename in [(leafmat,'pothos-leaf.png'),(light,'pothos-leaf.png'),(bpy.data.materials['Ceramic_Pot'],'terracotta.png')]:
 m.use_nodes=True;t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(A/'LV-PLANT-02/textures'/filename),check_existing=True);m.node_tree.links.new(t.outputs['Color'],m.node_tree.nodes['Principled BSDF'].inputs['Base Color']);t.image.pack()

def tube(name,pts,r,mat):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=2;sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
 for p,co in zip(sp.points,pts):p.co=(*co,1)
 o=bpy.data.objects.new(name,cu);bpy.context.collection.objects.link(o);cu.materials.append(mat);bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH');return bpy.context.object
for i in range(19):
 a=i*2.399;length=.095+(i%4)*.019;r=.04+(i%4)*.028;z=1.72+(i%5)*.027;start=Vector((-.33,-.08,1.667));tip=Vector((-.33+r*math.cos(a),-.08+r*math.sin(a),z));mid=(start+tip)*.5+Vector((0,0,.025));new.append(tube('Plant03 branching petiole',[start,mid,tip],.0014,leafmat));vs=[];nx,ny=12,6
 for j in range(nx+1):
  t=j/nx;wide=.038*math.sin(math.pi*t)**.8
  for k in range(ny+1):
   v=(k/ny-.5)*2;xx=t*length;yy=v*wide;zz=.021*math.sin(t*math.pi)-.012*v*v*math.sin(math.pi*t)
   vs.append(tuple(tip+Vector((xx*math.cos(a)-yy*math.sin(a),xx*math.sin(a)+yy*math.cos(a),zz))))
 fs=[]
 for j in range(nx):
  for k in range(ny):
   q=j*(ny+1)+k;fs.append((q,q+1,q+ny+2,q+ny+1))
 me=bpy.data.meshes.new('Plant03 leaf');me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new('Plant03 curved pointed leaf',me);bpy.context.collection.objects.link(o);me.materials.append(light if i%3==0 else leafmat);uv=me.uv_layers.new()
 for f in me.polygons:
  f.use_smooth=True
  for li in f.loop_indices:
   idx=me.loops[li].vertex_index;uv.data[li].uv=(idx//(ny+1)/nx,idx%(ny+1)/ny)
 new.append(o)
new +=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith(('tapered ceramic pot','pot lip','soil','pot botanical'))]
export(new,'LV_Book03_Plant');render('bookcase-books-and-foliage',(0,0,1.1),(3,-5,2.8),2.6);bpy.ops.wm.save_as_mainfile(filepath=str(P/'model/BooksPlant03.blend'))
(P/'furniture-validation.json').write_text(json.dumps(report,indent=2))
