import bpy, math
from mathutils import Vector
from pathlib import Path
P=Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
bpy.context.scene.unit_settings.system='METRIC'
def mat(name,col,metal=0,rough=.6,tex=None):
 m=bpy.data.materials.new(name); m.diffuse_color=(*col,1); m.use_nodes=True; n=m.node_tree.nodes.get('Principled BSDF'); n.inputs['Base Color'].default_value=(*col,1); n.inputs['Metallic'].default_value=metal; n.inputs['Roughness'].default_value=rough
 if tex:
  t=m.node_tree.nodes.new('ShaderNodeTexImage'); t.image=bpy.data.images.load(str(tex),check_existing=True); m.node_tree.links.new(t.outputs['Color'],n.inputs['Base Color'])
 return m
rose=mat('Rose ceramic',(.59,.17,.12),rough=.4); floral=mat('Rose painted flower',(.49,.20,.18),rough=.4,tex=P/'textures/rose-floral.png'); brass=mat('Aged brass',(.37,.245,.095),metal=.68,rough=.46); ivory=mat('Stopper ivory',(.79,.70,.56),rough=.32); dark=mat('Neck interior',(.17,.085,.075),rough=.75)
def cube(name,loc,dim,material,bevel):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=dim; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(material)
 if bevel:
  b=o.modifiers.new('Soft corners','BEVEL'); b.width=bevel; b.segments=4; b.affect='EDGES'; bpy.context.view_layer.objects.active=o; bpy.ops.object.modifier_apply(modifier=b.name)
 for p in o.data.polygons: p.use_smooth=True
 o.modifiers.new('Weighted normals','WEIGHTED_NORMAL'); return o
# The painted motif is applied directly to the forward face of the rounded body.
body=cube('Bottle', (0,0,.039),(.060,.040,.078),rose,.008); body.data.materials.append(floral)
uv=body.data.uv_layers.active or body.data.uv_layers.new(name='UVMap')
for face in body.data.polygons:
 face.material_index=1
 for li in face.loop_indices:
  co=body.data.vertices[body.data.loops[li].vertex_index].co
  if face.normal.y < -.88:
   uv.data[li].uv=(co.x/.060+.5,co.z/.078+.5)
  elif abs(face.normal.z) > .7:
   uv.data[li].uv=(.05+.20*(co.x/.060+.5),.05+.20*(co.y/.040+.5))
  else:
   uv.data[li].uv=(.05+.20*(co.y/.040+.5),.05+.20*(co.z/.078+.5))
# Actual annular hollow neck with internal vertical wall, circular opening at top.
def annulus(name,ro,ri,z0,z1,material):
 n=48; verts=[]
 for z,r in [(z0,ro),(z1,ro),(z1,ri),(z0,ri)]:
  verts += [(r*math.cos(2*math.pi*i/n),r*math.sin(2*math.pi*i/n),z) for i in range(n)]
 faces=[]
 for k in range(3):
  for i in range(n): j=(i+1)%n; faces.append((k*n+i,k*n+j,(k+1)*n+j,(k+1)*n+i))
 me=bpy.data.meshes.new(name); me.from_pydata(verts,[],faces); me.update(); ob=bpy.data.objects.new(name,me); bpy.context.collection.objects.link(ob); ob.data.materials.append(material)
 bpy.ops.object.select_all(action='DESELECT'); bpy.context.view_layer.objects.active=ob; ob.select_set(True); bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.uv.smart_project(island_margin=.02); bpy.ops.object.mode_set(mode='OBJECT'); ob.select_set(False)
 for p in me.polygons:p.use_smooth=True
 return ob
neck=annulus('Hollow neck',.010,.006,.075,.093,rose)
collar=annulus('Brass collar',.0108,.0099,.087,.090,brass)
bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=.006,depth=.001,location=(0,0,.079)); inside=bpy.context.object;inside.name='Dark interior bottom';inside.data.materials.append(dark)
# separate stopper: flange plus low faceted jewel and insertion peg
bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=.0055,depth=.008,location=(0,0,.090)); peg=bpy.context.object;peg.name='Stopper peg';peg.data.materials.append(ivory)
bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=6,location=(0,0,.106)); jewel=bpy.context.object;jewel.name='Faceted stopper';jewel.scale=(.013,.013,.012);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);jewel.data.materials.append(ivory)
# make self-contained exports using per-object selection and origins
bpy.ops.object.select_all(action='DESELECT')
for o in [body,neck,collar,inside]:o.select_set(True)
bpy.context.view_layer.objects.active=body
bpy.ops.export_scene.fbx(filepath=str(P/'model/BR_Perfume_Body.fbx'),use_selection=True,apply_unit_scale=True,axis_forward='-Y',axis_up='Z',add_leaf_bones=False)
bpy.ops.object.select_all(action='DESELECT')
for o in [peg,jewel]:o.select_set(True)
bpy.context.view_layer.objects.active=peg
bpy.ops.object.join(); stopper=bpy.context.object;stopper.name='Stopper'
bpy.context.scene.cursor.location=(0,0,.094);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
bpy.ops.export_scene.fbx(filepath=str(P/'model/BR_Perfume_Stopper.fbx'),use_selection=True,apply_unit_scale=True,axis_forward='-Y',axis_up='Z',add_leaf_bones=False)
# studio camera
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.object.camera_add(location=(.19,-.30,.18)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,0,.055))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO';cam.data.ortho_scale=.19;bpy.context.scene.camera=cam
for loc,power,size in [((-.3,-.4,.5),2,.32),((.3,-.2,.35),1,.25),((0,.3,.4),1.2,.2)]:
 bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,.05))-o.location).to_track_quat('-Z','Y').to_euler()
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.render.resolution_x=900;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.film_transparent=True
scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG';scene.render.filepath=str(P/'previews/perfume-closed.png');bpy.ops.wm.save_as_mainfile(filepath=str(P/'model/BR-PERFUME-01.blend'));bpy.ops.render.render(write_still=True)
stopper.location.z+=.035;scene.render.filepath=str(P/'previews/perfume-open.png');bpy.ops.render.render(write_still=True)
