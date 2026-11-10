"""FIX-020: thin fitted runner with a woven edge and loose short fringe.
Blender -b -t 2 --python-exit-code 1 --python this_file.py
"""
import bpy, math, random, json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent.parent
LENGTH=5.00
WIDTH=.80
random.seed(206)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
def mat(name,color,rough=.96):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough
 return m
cloth=mat('Runner02_Painterly',(1,1,1));n=cloth.node_tree.nodes.new('ShaderNodeTexImage');n.image=bpy.data.images.load(str(ROOT/'textures/runner-albedo.png'));n.image.pack();cloth.node_tree.links.new(n.outputs['Color'],cloth.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
binding=mat('Runner02_FadedRoseBinding',(.27,.14,.105));back=mat('Runner02_LinenBacking',(.29,.23,.16));fringe=mat('Runner02_FlaxFringe',(.55,.46,.31))
def mesh(name,verts,faces,material):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);me.materials.append(material);uv=me.uv_layers.new(name='UVMap')
 for p in me.polygons:
  p.use_smooth=True
  for li in p.loop_indices:
   x,y,z=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(.5+x/6,.5+y/.8)
 return o
nx,ny=160,22;v=[];f=[]
for j in range(ny+1):
 for i in range(nx+1):
  x=-LENGTH/2+LENGTH*i/nx;y=-WIDTH/2+WIDTH*j/ny
  # Low, irregular edge relief, not a periodic raised carpet slab.
  wave=.0007*math.sin(x*7.13+1.2)*math.sin(y*9.1)+.0005*math.sin(x*18.4+y*13.1)
  y+=.0014*math.sin(x*5.31+.8)*(abs(y)/.4)**7
  v.append((x,y,.005+wave))
for j in range(ny):
 for i in range(nx):
  a=j*(nx+1)+i;f.append((a,a+1,a+nx+2,a+nx+1))
top=mesh('Runner02 textile',v,f,cloth)
solid=top.modifiers.new('Flexible linen backing','SOLIDIFY');solid.thickness=.003;solid.offset=-1;top.data.materials.append(back);solid.material_offset=1;bpy.context.view_layer.objects.active=top;bpy.ops.object.modifier_apply(modifier=solid.name)
def cord(name,points,radius,material):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=radius;c.bevel_resolution=1;c.resolution_u=1;s=c.splines.new('POLY');s.points.add(len(points)-1)
 for p,co in zip(s.points,points):p.co=(*co,1)
 o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o);c.materials.append(material);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');o=bpy.context.object;o.select_set(False)
 if not o.data.uv_layers:o.data.uv_layers.new(name='UVMap')
 return o
for side in [-1,1]:
 cord('Soft bound long edge',[(x,side*(.398+.0013*math.sin(x*5.31+.8)),.0045+.0006*math.sin(x*7.1)) for x in [-LENGTH/2+LENGTH*i/180 for i in range(181)]],.0028,binding)
 cord('Woven end seam',[(side*(LENGTH/2-.002),-.397+.794*i/70,.0047) for i in range(71)],.0032,fringe)
 for k in range(104):
  y=-.39+.78*k/103;length=random.uniform(.048,.068);bend=random.uniform(-.009,.009)
  # Each short warp bundle lies on the floor with a slightly splayed tip.
  pts=[]
  for n in range(7):
   t=n/6;pts.append((side*(LENGTH/2-.002+length*t),y+bend*t*t,.002+.0022*(1-t)+.001*math.sin(t*math.pi)))
  cord('Loose flax end bundle',pts,random.uniform(.0009,.00135),fringe)
objs=[o for o in bpy.context.scene.objects if o.type=='MESH'];bpy.ops.object.select_all(action='DESELECT')
for o in objs:o.select_set(True)
bpy.context.view_layer.objects.active=top;bpy.ops.object.join();o=bpy.context.object;o.name='HA_RUNNER_02';bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
bpy.ops.export_scene.fbx(filepath=str(ROOT/'model/HA_RUNNER_02.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,add_leaf_bones=False)
coords=[o.matrix_world@p.co for p in o.data.vertices];bounds={'min':[min(p[i] for p in coords) for i in range(3)],'max':[max(p[i] for p in coords) for i in range(3)]}
(ROOT/'assembly.json').write_text(json.dumps({'asset':'HA-RUNNER-02','fix':'FIX-020','units':'metres','origin':'floor center','long_axis':'+X','up':'+Z','fbx_forward':'-Y','body_length':LENGTH,'body_width':WIDTH,'fringe_length_range':[.048,.068],'bounds':bounds,'collision':'none; underlying floor supplies collision','texture_uv':'Long axis samples original artwork at 6m scale, centered crop; width samples original .8m scale. No motif stretch.','placement':{'origin_plan_m':[5.234,4.70,.00118546],'yaw_degrees':0,'scale':[1,1,1],'expected_fringe_x_extent_m':[2.668,7.800],'cabinet_front_x_m':2.5275,'minimum_gap_m':.1405,'evidence':'Existing dressing pipeline places 6m runner at (4.80,4.70); Rev02 leaves it unchanged. New east fringe endpoint preserves7.80m. Verify actual bounds in engine before acceptance.'},'materials':[{'slot':i,'name':m.name,'base_color_linear':list(m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value)[:3],'roughness':.96,'base_color_texture':'textures/runner-albedo.png' if i==0 else None} for i,m in enumerate(o.data.materials)]},indent=2)+'\n')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'model/HA-RUNNER-02.blend'))
# Review only; floor and lighting never enter the export.
bpy.ops.mesh.primitive_plane_add(size=200);floor=bpy.context.object;floor.location.z=-.001;floor.data.materials.append(mat('PREVIEW floor',(.19,.12,.075)))
bpy.ops.object.light_add(type='AREA',location=(0,-2,5));bpy.context.object.data.energy=900;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=5
bpy.ops.object.camera_add(location=(3.7,-3.5,3.7));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=6.4;bpy.context.scene.camera=cam
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=24;s.render.resolution_x=1200;s.render.resolution_y=650;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.world.color=(.3,.3,.3);s.render.filepath=str(ROOT/'previews/runner-perspective.png');bpy.ops.render.render(write_still=True)
cam.location=(LENGTH/2+.2,-.45,.45);cam.rotation_euler=(Vector((LENGTH/2-.05,0,.002))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.95;s.render.resolution_x=1000;s.render.resolution_y=700;s.render.filepath=str(ROOT/'previews/fringe-closeup.png');bpy.ops.render.render(write_still=True)
