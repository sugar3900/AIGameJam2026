import bpy, math, os
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parent.parent
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for data in bpy.data.materials: bpy.data.materials.remove(data)
def mat(name, path, tint, rough=.8, metal=0):
 m=bpy.data.materials.new(name); m.diffuse_color=(*tint,1); m.use_nodes=True
 n=m.node_tree.nodes; l=m.node_tree.links; bs=n.get('Principled BSDF'); bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metal
 tex=n.new('ShaderNodeTexImage'); tex.image=bpy.data.images.load(str(R/'textures'/path),check_existing=True); tex.extension='REPEAT'
 mult=n.new('ShaderNodeMixRGB'); mult.blend_type='MULTIPLY'; mult.inputs[0].default_value=1; mult.inputs[2].default_value=(*tint,1)
 l.new(tex.outputs['Color'],mult.inputs[1]); l.new(mult.outputs[0],bs.inputs['Base Color']); return m
brass=mat('Aged Brass','aged-brass.png',(.8,.75,.56),.45,.68)
ivory=mat('Ivory Terry','terry.png',(.94,.91,.84),.93); rose=mat('Rose Terry','terry.png',(.71,.42,.40),.93)
ivorystripe=mat('Ivory Border','terry.png',(.88,.83,.74),.94); rosestripe=mat('Rose Border','terry.png',(.61,.32,.30),.94)
def cyl(name, radius, depth, loc, rot=(0,0,0)):
 bpy.ops.mesh.primitive_cylinder_add(vertices=16 if name=='Mount screw' else 32, radius=radius, depth=depth, location=loc, rotation=rot); o=bpy.context.object;o.name=name;o.data.materials.append(brass);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);bpy.ops.object.shade_smooth(); bev=o.modifiers.new('Rounded edges','BEVEL');bev.width=min(.001,depth*.2,radius*.2);bev.segments=2; return o
rail=[]
rail.append(cyl('Bar',.012,1.04,(0,-.11,0),(0,math.pi/2,0)))
for x in (-.525,.525):
 rail.append(cyl('Wall mounting plate',.040,.012,(x,-.006,0),(math.pi/2,0,0)))
 rail.append(cyl('Collar',.024,.018,(x,-.021,0),(math.pi/2,0,0)))
 rail.append(cyl('Bracket',.011,.085,(x,-.068,0),(math.pi/2,0,0)))
 rail.append(cyl('Rail finial',.020,.024,(x,-.11,0),(0,math.pi/2,0)))
 for ang in (math.pi/2, math.pi*7/6, math.pi*11/6):
  rail.append(cyl('Mount screw',.003,.002,(x+.028*math.cos(ang),-.013,.028*math.sin(ang)),(math.pi/2,0,0)))
def towel(name,center,width,length,phase,material,stripe):
 nx,ns=32,48; verts=[]; faces=[]
 for j in range(ns+1):
  s=-1+2*j/ns
  for i in range(nx+1):
   u=i/nx; x=center+(u-.5)*width + .004*math.sin(2*math.pi*u+phase)*abs(s)
   z=.020 - length*(max(0,abs(s)-.045)/.955)**.96 * (1 if s<0 else .82)
   z+=.006*math.sin(2*math.pi*(u*1.2)+phase)*abs(s)**2
   y=-.110+.019*math.tanh(s*25) + .019*math.sin(2*math.pi*(u*3.3)+phase+.12*math.sin(s*4))*min(1,abs(s)*8)
   
   if abs(z)<.020:
    clearance=math.sqrt(max(0,.020**2-z*z))+.002
    y=min(y,-.110-clearance) if s<0 else max(y,-.110+clearance)
   verts.append((x,y,z))
 for j in range(ns):
  for i in range(nx):
   a=j*(nx+1)+i; faces.append((a,a+1,a+nx+2,a+nx+1))
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update(); ob=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(ob)
 uv=mesh.uv_layers.new(name='UVMap')
 for p in mesh.polygons:
  j=p.index//nx
  p.material_index=1 if (j in (2,5,ns-6,ns-3)) else 0
  p.use_smooth=True
  for li in p.loop_indices:
   vi=mesh.loops[li].vertex_index; u=(vi%(nx+1))/nx; v=(vi//(nx+1))/ns; uv.data[li].uv=(u*2,v*4)
 ob.data.materials.append(material);ob.data.materials.append(stripe)
 sol=ob.modifiers.new('Hem thickness','SOLIDIFY');sol.thickness=.0025;sol.offset=0
 return ob
cloth1=towel('Ivory towel',-.222,.43,.68,.2,ivory,rosestripe)
cloth2=towel('Rose towel',.220,.43,.72,1.1,rose,ivorystripe)
# Camera-only scene extras
wallmat=bpy.data.materials.new('Preview wall');wallmat.diffuse_color=(.54,.40,.38,1)
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,.045,-.3));wall=bpy.context.object;wall.name='Preview wall';wall.dimensions=(2,.07,1.8);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);wall.data.materials.append(wallmat)
def export(name,objects):
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0]
 bpy.ops.export_scene.fbx(filepath=str(R/'model'/name),use_selection=True,object_types={'MESH'},apply_unit_scale=True,axis_forward='-Y',axis_up='Z',bake_space_transform=False,mesh_smooth_type='FACE',add_leaf_bones=False)
export('BA_Towel_Rail.fbx',rail); export('BA_Towel_Ivory.fbx',[cloth1]); export('BA_Towel_Rose.fbx',[cloth2])
# camera and lights
bpy.ops.object.camera_add(location=(2.7,-4.5,1.25));cam=bpy.context.object;cam.rotation_euler=(Vector((0,-.1,-.33))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=1.75;bpy.context.scene.camera=cam
for loc,power,size in [((1,-3,3),450,4),((-2,-2,1),250,3)]:
 bpy.ops.object.light_add(type='AREA',location=loc); l=bpy.context.object;l.data.energy=power;l.data.shape='DISK';l.data.size=size;l.rotation_euler=(Vector((0,0,-.3))-l.location).to_track_quat('-Z','Y').to_euler()
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=32;sc.render.resolution_x=1100;sc.render.resolution_y=1100;sc.render.resolution_percentage=100;sc.world.color=(.20,.20,.20);sc.view_settings.view_transform='AgX';sc.render.image_settings.file_format='PNG';sc.render.filepath=str(R/'previews'/'towel-rail-perspective.png')
bpy.ops.wm.save_as_mainfile(filepath=str(R/'model'/'BA-TOWEL-RAIL-01.blend')); bpy.ops.file.make_paths_relative(); bpy.ops.wm.save_as_mainfile(filepath=str(R/'model'/'BA-TOWEL-RAIL-01.blend')); bpy.ops.render.render(write_still=True)
