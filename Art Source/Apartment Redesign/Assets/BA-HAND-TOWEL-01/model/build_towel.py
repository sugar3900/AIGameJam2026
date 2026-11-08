import bpy, math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent; R=P.parent
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
tex=bpy.data.images.load(str(R/'textures'/'terry.png'),check_existing=True)
def textile(name,tint):
 m=bpy.data.materials.new(name);m.use_nodes=True
 n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF');p.inputs['Roughness'].default_value=.93
 im=n.new('ShaderNodeTexImage');im.image=tex;im.extension='REPEAT'
 mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[2].default_value=(*tint,1)
 l.new(im.outputs['Color'],mix.inputs[1]);l.new(mix.outputs[0],p.inputs['Base Color']);return m
ivory=textile('Ivory Terry',(.94,.91,.84));rose=textile('Dusty Rose Hem',(.61,.32,.30))
# Datum exactly matches BA-HOOK-01 wall-plane backplate center. Top hangs from the tip.
nx,ny=32,48;v=[];faces=[]
for j in range(ny+1):
 t=j/ny
 for i in range(nx+1):
  u=i/nx; a=2*u-1
  width=.32*(.12+.88*math.sqrt(t))
  x=(u-.5)*width + .006*t*math.sin(2.2*t)
  z=-.050-.455*t-.018*abs(a)*(1-t)+.004*t**4*math.sin(2*math.pi*(u*2.5+.12))
  y=-.075-.016*(1-math.exp(-t*10))-.015*math.sin(2*math.pi*(u*3.2)+.25*math.sin(t*4))*(.18+.82*t)-.006*t*math.sin(2*math.pi*(u*1.1+.2))
  v.append((x,y,z))
for j in range(ny):
 for i in range(nx):
  a=j*(nx+1)+i;faces.append((a,a+nx+1,a+nx+2,a+1))
mesh=bpy.data.meshes.new('Gathered terry mesh');mesh.from_pydata(v,[],faces);mesh.update();ob=bpy.data.objects.new('BA_Hand_Towel',mesh);bpy.context.collection.objects.link(ob)
mesh.materials.append(ivory);mesh.materials.append(rose);uv=mesh.uv_layers.new(name='UVMap')
for p in mesh.polygons:
 j=p.index//nx;p.material_index=1 if j in (ny-8,ny-7,ny-4,ny-3) else 0;p.use_smooth=True
 for li in p.loop_indices:
  vi=mesh.loops[li].vertex_index;uv.data[li].uv=((vi%(nx+1))/nx*2,(vi//(nx+1))/ny*3)
solid=ob.modifiers.new('Cloth thickness','SOLIDIFY');solid.thickness=.0025;solid.offset=0
bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.modifier_apply(modifier=solid.name)
bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
bpy.ops.export_scene.fbx(filepath=str(P/'BA_Hand_Towel.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,axis_forward='-Z',axis_up='Y',add_leaf_bones=False,mesh_smooth_type='FACE')
# Only for review: actual hook and wall, never exported in towel FBX.
bpy.ops.object.select_all(action='DESELECT');bpy.ops.import_scene.fbx(filepath=str(R.parent/'BA-HOOK-01'/'model'/'BA_Hook_01.fbx'),axis_forward='-Z',axis_up='Y')
previewbrass=bpy.data.materials.new('Preview aged brass');previewbrass.use_nodes=True
pb=previewbrass.node_tree.nodes.get('Principled BSDF');pb.inputs['Base Color'].default_value=(.34,.25,.09,1);pb.inputs['Metallic'].default_value=.68;pb.inputs['Roughness'].default_value=.45
for o in bpy.context.selected_objects:
 o.name='Preview hook (not exported)'
 if o.type=='MESH':
  o.data.materials.clear();o.data.materials.append(previewbrass)
wallmat=bpy.data.materials.new('Preview wall');wallmat.use_nodes=True;wallmat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.56,.46,.43,1)
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,.02,-.25)); wall=bpy.context.object;wall.name='Preview wall (not exported)';wall.dimensions=(1,.04,1);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);wall.data.materials.append(wallmat)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.world.color=(.18,.18,.18);scene.view_settings.view_transform='AgX'
for loc,power,size in [((-.8,-1.5,1.2),55,2),((1,-1,.2),35,1.5)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,-.08,-.25))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(.55,-1.3,.25));cam=bpy.context.object;cam.rotation_euler=(Vector((0,-.06,-.27))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=.75;scene.camera=cam
bpy.ops.wm.save_as_mainfile(filepath=str(P/'BA-HAND-TOWEL-01.blend'));scene.render.filepath=str(R/'previews'/'towel-perspective.png');bpy.ops.render.render(write_still=True)
cam.location=(0,-1.4,-.26);cam.rotation_euler=(Vector((0,-.06,-.27))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.68;scene.render.filepath=str(R/'previews'/'towel-front.png');bpy.ops.render.render(write_still=True)
