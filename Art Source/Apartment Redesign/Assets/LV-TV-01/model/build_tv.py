"""Build LV-TV-01. Blender 5.x: blender -b --python build_tv.py.
Units metres; X width, Y depth, -Y front, Z up. Export body at floor origin,
left/right doors at their hinges, and separate on/off curved glass screens.
"""
import bpy, math, os, mathutils
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'model'; OUT.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for m in list(bpy.data.materials): bpy.data.materials.remove(m)

def mat(name,col,rough=.65,metal=0,emission=None,tex=None):
 m=bpy.data.materials.new(name); m.diffuse_color=(*col,1); m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 if emission: p.inputs['Emission Color'].default_value=(*emission[0],1);p.inputs['Emission Strength'].default_value=emission[1]
 if tex:
  image=bpy.data.images.load(str(tex),check_existing=True); image.pack(); node=m.node_tree.nodes.new('ShaderNodeTexImage');node.image=image; mix=m.node_tree.nodes.new('ShaderNodeMixRGB'); mix.blend_type='MULTIPLY'; mix.inputs[0].default_value=1; mix.inputs[2].default_value=(.25,.23,.14,1); m.node_tree.links.new(node.outputs['Color'],mix.inputs[1]); m.node_tree.links.new(mix.outputs['Color'],p.inputs['Base Color'])
 return m
wood=mat('Walnut_Painted',(.35,.14,.045),.78,tex=ROOT/'textures'/'walnut-painted.png')
darkwood=mat('Walnut_Shadow',(.19,.075,.035)); edge=mat('Warm_Wood_Trim',(.18,.085,.03)); brass=mat('Aged_Brass',(.56,.35,.10),.38,.6); back=mat('Back_Panel',(.14,.065,.035)); dark=mat('Vent_Dark',(.045,.033,.025)); trim=mat('Ivory_Bezel',(.37,.24,.12)); rubber=mat('CRT_Gasket',(.09,.075,.055)); off=mat('Screen_Off',(.008,.012,.009),.13,metal=.08); on=mat('Screen_On',(.18,.065,.012),.2,emission=((1,.22,.012),.48))
# CRT phosphor has a warm center and darker edges; recreating this node setup
# in Unreal is required since FBX transfers geometry/material names, not nodes.
tree=on.node_tree; principled=tree.nodes.get('Principled BSDF')
coords=tree.nodes.new('ShaderNodeTexCoord');distance=tree.nodes.new('ShaderNodeVectorMath');distance.operation='DISTANCE';distance.inputs[1].default_value=(.5,.5,0)
ramp=tree.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.05;ramp.color_ramp.elements[0].color=(1.0,.50,.10,1);ramp.color_ramp.elements[1].position=.65;ramp.color_ramp.elements[1].color=(.12,.025,.002,1)
tree.links.new(coords.outputs['UV'],distance.inputs[0]);tree.links.new(distance.outputs['Value'],ramp.inputs[0]);tree.links.new(ramp.outputs['Color'],principled.inputs['Emission Color']);principled.inputs['Emission Strength'].default_value=1.1
COL={k:[] for k in ['body','left','right','screen_off','screen_on']}
def register(o,key,material):
 o.data.materials.append(material);COL[key].append(o);return o

def box(n,loc,dim,material,key='body',bev=.008):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=n;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bev:
  mod=o.modifiers.new('Soft edges','BEVEL');mod.width=min(bev,min(dim)*.20);mod.segments=3;bpy.ops.object.modifier_apply(modifier=mod.name)
  mod=o.modifiers.new('Weighted normals','WEIGHTED_NORMAL');bpy.ops.object.modifier_apply(modifier=mod.name)
 return register(o,key,material)

def cylinder(n,loc,r,depth,material,key='body',axis='Y',verts=32):
 rot=(math.pi/2,0,0) if axis=='Y' else (0,0,0)
 bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=depth,location=loc,rotation=rot);o=bpy.context.object;o.name=n
 return register(o,key,material)

def rod(n,a,b,r,material,key='body'):
 a=mathutils.Vector(a);b=mathutils.Vector(b);d=b-a
 bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=r,depth=d.length,location=(a+b)/2);o=bpy.context.object;o.name=n;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();return register(o,key,material)

def plane_uv(o):
 if o.type != 'MESH': return
 if not o.data.uv_layers:o.data.uv_layers.new(name='UVMap')
 # Object/world-space planar mapping, with oriented projection per face.
 uv=o.data.uv_layers.active.data
 for poly in o.data.polygons:
  n=poly.normal; ax=max(range(3),key=lambda i:abs(n[i]))
  for li in poly.loop_indices:
   v=o.data.vertices[o.data.loops[li].vertex_index].co
   if ax==0: u,vv=v.y,v.z
   elif ax==1: u,vv=v.x,v.z
   else: u,vv=v.x,v.y
   uv[li].uv=(u*1.3+0.5,vv*1.3+0.5)

# Credible cabinet: thin sides, back, bottom, shelf, full top; open front.
box('Stand top',(0,0,.62),(1.10,.46,.055),wood,bev=.018)
box('Stand left side',(-.517,0,.40),(.05,.41,.40),wood)
box('Stand right side',(.517,0,.40),(.05,.41,.40),wood)
box('Stand back',(0,.195,.40),(1.00,.025,.40),back)
box('Stand floor',(0,0,.207),(1.00,.40,.035),wood)
box('Interior shelf',(0,0,.395),(1.0,.39,.025),wood)
box('Lower moulding',(0,-.002,.182),(1.08,.44,.04),edge)
for x in [-.45,.45]:
 for y in [-.15,.15]:
  rod('Splayed tapered leg',(x*1.16,y*1.13,.025),(x,y,.19),.024,wood)
  cylinder('Brass foot',(x*1.16,y*1.13,.028),.027,.05,brass,axis='Z',verts=20)
# side fluted slats on doors and separate left/right pivot pieces
for x,key in [(-.245,'left'),(.245,'right')]:
 box(key+' cabinet door',(x,-.218,.398),(.475,.030,.37),wood,key,bev=.008)
 for i in range(7):
  sx=x+(-.19+i*.017 if x<0 else .09+i*.017)
  box(key+' vertical groove',(sx,-.235,.398),(.005,.005,.32),darkwood,key,bev=0)
 hx=x+(.195 if x<0 else -.195)
 rod(key+' brass handle',(hx,-.252,.35),(hx,-.252,.45),.009,brass,key)
 for z in (.35,.45):cylinder('Handle mount',(hx,-.24,z),.014,.012,brass,key)
# TV case is a solid rounded shell with layered dark screen surround in front.
box('CRT wooden housing',(0,.005,.965),(.90,.36,.59),wood,bev=.065)
# Back plate and vent slits (visible from rear)
box('Back cover',(0,.190,.96),(.78,.008,.47),back,bev=.003)
for rowz in (.84,1.08):
 for i in range(12):
  box('Rear vent',(-.32+i*.027,.196,rowz),(.008,.004,.10),dark,bev=0)
# Rounded-rectangle face layers: superellipse contour and subtly convex glass.
def squircle(name, cx, y, cz, rx, rz, depth, material, key='body'):
    n=64; rings=8; verts=[(cx,y-depth,cz)]; faces=[]
    for r in range(1,rings+1):
        t=r/rings
        for i in range(n):
            a=2*math.pi*i/n; co=math.cos(a); si=math.sin(a)
            x=rx*math.copysign(abs(co)**.5,co)*t; z=rz*math.copysign(abs(si)**.5,si)*t
            verts.append((cx+x,y-depth*(1-t*t),cz+z))
    for i in range(n): faces.append((0,1+i,1+(i+1)%n))
    for ring in range(1,rings):
        a=1+(ring-1)*n;b=1+ring*n
        for i in range(n): j=(i+1)%n;faces.append((a+i,b+i,b+j,a+j))
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
    ob=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(ob)
    for poly in mesh.polygons:poly.use_smooth=True
    return register(ob,key,material)
squircle('Face surround',-.08,-.189,.965,.335,.245,.002,trim)
squircle('Gasket',-.08,-.198,.965,.301,.212,.001,rubber)
squircle('Screen off',-.08,-.205,.965,.277,.188,.052,off,'screen_off')
squircle('Screen on',-.08,-.205,.965,.277,.188,.052,on,'screen_on')
for z in (1.09,.965):
 cylinder('Knob housing',(.335,-.199,z),.045,.022,brass)
 cylinder('Knob center',(.335,-.215,z),.032,.014,edge)
 box('Knob indicator',(.335,-.226,z),(.005,.004,.045),brass,bev=0)
 # Readable period dial ticks and small inlaid pointer.
 box('Knob pointer',(.335,-.230,z+.012),(.003,.003,.017),dark,bev=0)
 for i in range(12):
  a=2*math.pi*i/12; tick=box('Dial tick',(.335+.051*math.sin(a),-.204,z+.051*math.cos(a)),(.003,.003,.009),brass,bev=0);tick.rotation_euler.y=a

for i in range(6):box('Front speaker grille',(.27+i*.021,-.193,.82),(.007,.006,.105),dark,bev=0)
# UV every part before joining.
for group in COL.values():
 for o in group:plane_uv(o)
# Normalize the two screen UVs for radial phosphor color.
for key in ('screen_off','screen_on'):
 for ob in COL[key]:
  for p in ob.data.polygons:
   for li in p.loop_indices:
    v=ob.data.vertices[ob.data.loops[li].vertex_index].co
    ob.data.uv_layers.active.data[li].uv=((v.x+.357)/.554,(v.z-.777)/.376)

# rendering and reusable export
scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.samples=32
scene.render.resolution_x=1100;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=True
scene.world.color=(.24,.21,.18)
def aim(o,point):o.rotation_euler=(mathutils.Vector(point)-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(2.5,-3.8,2.15));camera=bpy.context.object;camera.data.type='ORTHO';camera.data.ortho_scale=1.95;aim(camera,(0,0,.66));scene.camera=camera
for loc,power,size in [((1.5,-2.5,3.5),180,3.0),((-2,-1,2.6),110,2.5),((0,2,2.8),80,2.5)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;aim(o,(0,0,.65))
for state in ('off','on'):
 for o in COL['screen_on']:o.hide_render=(state!='on')
 for o in COL['screen_off']:o.hide_render=(state!='off')
 scene.render.filepath=str(ROOT/'previews'/('tv-'+state+'.png'));bpy.ops.render.render(write_still=True)
# Show that cabinet doors rotate around their respective outside hinge lines.
from mathutils import Matrix
for key,point,angle in [('left',(-.483,-.218,0),-math.pi/2),('right',(.483,-.218,0),math.pi/2)]:
    hinge=mathutils.Vector(point); M=Matrix.Translation(hinge) @ Matrix.Rotation(angle,4,'Z') @ Matrix.Translation(-hinge)
    for ob in COL[key]: ob.matrix_world=M @ ob.matrix_world
for o in COL['screen_on']:o.hide_render=True
for o in COL['screen_off']:o.hide_render=False
scene.render.filepath=str(ROOT/'previews'/'tv-doors-open.png');bpy.ops.render.render(write_still=True)
for key,point,angle in [('left',(-.483,-.218,0),math.pi/2),('right',(.483,-.218,0),-math.pi/2)]:
    hinge=mathutils.Vector(point); M=Matrix.Translation(hinge) @ Matrix.Rotation(angle,4,'Z') @ Matrix.Translation(-hinge)
    for ob in COL[key]: ob.matrix_world=M @ ob.matrix_world
# Save packed Blender source before export, including separate meshes and materials.
for o in COL['screen_off']:o.hide_render=False
for o in COL['screen_on']:o.hide_render=True
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'LV-TV-01.blend'))
# Export each group preserving a shared origin or local hinge origin.
def export_group(key,origin):
 bpy.ops.object.select_all(action='DESELECT')
 for o in COL[key]:o.select_set(True)
 bpy.context.view_layer.objects.active=COL[key][0];bpy.ops.object.join();o=bpy.context.object;o.name='LV_TV_'+key
 bpy.context.scene.cursor.location=origin;bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
 bpy.ops.export_scene.fbx(filepath=str(OUT/(o.name+'.fbx')),use_selection=True,object_types={'MESH'},add_leaf_bones=False,apply_unit_scale=True)
 print('EXPORTED',key,len(o.data.vertices),tuple(round(x,4) for x in o.dimensions))
for key,origin in [('body',(0,0,0)),('left',(-.483,-.218,0)),('right',(.483,-.218,0)),('screen_off',(0,0,0)),('screen_on',(0,0,0))]:export_group(key,origin)
