import bpy, math, os
from mathutils import Vector
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
bpy.context.scene.unit_settings.system='METRIC'

def paint_material():
 m=bpy.data.materials.new('AgedIvoryPaint');m.use_nodes=True
 n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF')
 t=n.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(ROOT/'textures/paint-selected.png'),check_existing=True)
 mix=n.new('ShaderNodeMixRGB');mix.blend_type='MIX';mix.inputs[0].default_value=.36;mix.inputs[2].default_value=(.82,.76,.65,1)
 l.new(t.outputs['Color'],mix.inputs[1]);l.new(mix.outputs[0],p.inputs['Base Color']);p.inputs['Roughness'].default_value=.84
 return m
paint=paint_material()
def plain(name,color,rough=.9):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough
 return m
wall=plain('PreviewWarmPlaster',(.51,.38,.31));floor=plain('PreviewWood',(.22,.105,.055))

def molding(name, profile, miter=None):
 # profile is counter-clockwise (depth,height) cross-section; extruded along x, with square ends.
 n=len(profile);verts=[(((-y if miter == "start" else 0) if x == 0 else (1+y if miter == "end" else 1)),y,z) for x in (0,1) for y,z in profile]
 faces=[tuple(reversed(range(n))),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
 obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj)
 import bmesh
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bmesh.ops.triangulate(bm,faces=bm.faces[:]);bm.to_mesh(mesh);bm.free();mesh.update()
 uv=mesh.uv_layers.new(name='UVMap')
 for poly in mesh.polygons:
  for li in poly.loop_indices:
   v=mesh.vertices[mesh.loops[li].vertex_index].co
   uv.data[li].uv=(v.x, (v.z+v.y)*2.5)
 mesh.materials.append(paint)
 return obj
# Wall face y=0, trim projects into room toward negative y. Heights in metres.
base=molding('Baseboard_1m',[(0,0),(-.023,0),(-.023,.105),(-.030,.105),(-.030,.116),(-.025,.124),(-.015,.130),(0,.130)])
crown=molding('Crown_1m',[(0,0),(-.023,0),(-.028,.012),(-.030,.020),(-.028,.030),(-.021,.043),(-.014,.057),(-.018,.075),(-.035,.085),(-.035,.100),(0,.100)])
# Casing runs along X; profile height is nominal casing width; install rotated vertically when needed.
casing=molding('Casing_1m',[(0,0),(-.020,0),(-.026,.008),(-.026,.016),(-.018,.022),(-.018,.058),(-.026,.064),(-.026,.072),(-.020,.080),(0,.080)])
def profile_of(obj):
 n=len(obj.data.vertices)//2
 return [(obj.data.vertices[i].co.y,obj.data.vertices[i].co.z) for i in range(n)]
base_prof=profile_of(base);crown_prof=profile_of(crown)
base_end=molding('Baseboard_Inside_End',base_prof,'end');base_start=molding('Baseboard_Inside_Start',base_prof,'start')
crown_end=molding('Crown_Inside_End',crown_prof,'end');crown_start=molding('Crown_Inside_Start',crown_prof,'start')
for o in (base,crown,casing,base_end,base_start,crown_end,crown_start):
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
 bpy.ops.export_scene.fbx(filepath=str(ROOT/'model'/f'{o.name}.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,axis_forward='-Y',axis_up='Z',add_leaf_bones=False,path_mode='AUTO')
# Studio assembly shows the matching miter faces, not overlapping square ends.
base.hide_render=True;crown.hide_render=True
base_end.location=(-.65,0,0);crown_end.location=(-.65,0,2.65)
base_start.location=(.35,0,0);base_start.rotation_euler[2]=-math.pi/2
crown_start.location=(.35,0,2.65);crown_start.rotation_euler[2]=-math.pi/2
casing.location=(-.5,-.007,.25);casing.rotation_euler[1]=-math.pi/2
def box(name,loc,scale,mat):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat)
box('PreviewWallA',(-.35,.045,1.375),(1.4,.09,2.75),wall);box('PreviewWallB',(.395,-.5,1.375),(.09,1.0,2.75),wall);box('PreviewFloor',(-.15,-.15,-.025),(1.55,1.5,.05),floor)
def aim(obj,p):obj.rotation_euler=(Vector(p)-obj.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(-3,-4,2.7));cam=bpy.context.object;aim(cam,(0,0,1.35));cam.data.type='ORTHO';cam.data.ortho_scale=3.65;bpy.context.scene.camera=cam
for loc,power,size in [((-3,-4,5),750,4),((2,-3,3),400,3)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;aim(o,(0,0,1.2))
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.render.resolution_x=1100;scene.render.resolution_y=1100;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=True
scene.world.color=(.22,.22,.22)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'model'/'ARC-TRIM-01.blend'))
scene.render.filepath=str(ROOT/'previews'/'trim-junction.png');bpy.ops.render.render(write_still=True)
cam.location=(-.65,-1.0,3.05);aim(cam,(.35,0,2.70));cam.data.ortho_scale=.55
scene.render.filepath=str(ROOT/'previews'/'crown-inside-close.png');bpy.ops.render.render(write_still=True)
cam.location=(-.65,-1.0,.55);aim(cam,(.35,0,.07));cam.data.ortho_scale=.55
scene.render.filepath=str(ROOT/'previews'/'baseboard-inside-close.png');bpy.ops.render.render(write_still=True)

