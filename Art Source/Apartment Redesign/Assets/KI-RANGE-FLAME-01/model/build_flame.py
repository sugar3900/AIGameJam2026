import bpy, math, os
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent.parent
R=P.parent/'KI-RANGE-01'/'model'/'KI_RANGE_Body.fbx'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)

def material(name, color, power, alpha):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,alpha);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.72
 a=m.node_tree.nodes.new('ShaderNodeVertexColor');a.layer_name='FlameTint'
 m.node_tree.links.new(a.outputs['Color'],p.inputs['Base Color']);m.node_tree.links.new(a.outputs['Color'],p.inputs['Emission Color'])
 p.inputs['Emission Strength'].default_value=power
 mul=m.node_tree.nodes.new('ShaderNodeMath');mul.operation='MULTIPLY';mul.inputs[1].default_value=alpha
 m.node_tree.links.new(a.outputs['Alpha'],mul.inputs[0]);m.node_tree.links.new(mul.outputs[0],p.inputs['Alpha'])
 return m
outer=material('Flame_Outer_Blue',(0.035,.18,.52),.8,.38)
inner=material('Flame_Inner_Cyan',(.10,.40,.70),1.0,.54)
# Twelve flame jets fit the KI-RANGE-01 port ring; short jets remain under grate spokes.
def jets(name,material,scale,height,zbase,offset,is_inner):
 verts=[]; faces=[]; levels=[]
 nside=12
 def vertex(p,zf): verts.append(p);levels.append(zf);return len(verts)-1
 for j in range(12):
  jh=height*(.34 if j%3==0 else 1.0)*(1+.045*math.sin(j*2.13))
  a=math.tau*j/12; px=.046*math.cos(a);py=.046*math.sin(a); tangent=Vector((-math.sin(a),math.cos(a),0)); radial=Vector((math.cos(a),math.sin(a),0))
  bend=offset*(1 if j%2 else -1)
  base=vertex((px,py,zbase),0)
  rings=[]
  for zf,rf in [(0.04,.62),(.14,.90),(.27,1),(.40,.96),(.54,.83),(.68,.64),(.79,.45),(.89,.26),(.96,.10)]:
   ring=[]
   for k in range(nside):
    t=math.tau*k/nside
    q=Vector((px,py,zbase+jh*zf))+tangent*(scale*rf*math.cos(t))+radial*(scale*rf*math.sin(t))+tangent*(bend*zf*zf)+radial*(.0008*math.sin(zf*math.pi))
    ring.append(vertex(q,zf))
   rings.append(ring)
  tip=vertex((px+tangent.x*bend,py+tangent.y*bend,zbase+jh),1)
  for k in range(nside): faces.append((base,rings[0][(k+1)%nside],rings[0][k]))
  for aa,bb in zip(rings,rings[1:]):
   for k in range(nside): faces.append((aa[k],aa[(k+1)%nside],bb[(k+1)%nside],bb[k]))
  for k in range(nside):faces.append((rings[-1][k],rings[-1][(k+1)%nside],tip))
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();uv=mesh.uv_layers.new(name='UVMap')
 col=mesh.color_attributes.new(name='FlameTint',type='FLOAT_COLOR',domain='POINT')
 for idx,zf in enumerate(levels):
  alpha=max(.025,math.sin(math.pi*zf)**.60)
  if is_inner: c=(.055+.055*(1-zf),.24+.16*(1-zf),.53+.17*(1-zf))
  else: c=(.025+.045*(1-zf),.16+.18*(1-zf),.47+.20*(1-zf))
  col.data[idx].color=(*c,alpha)
 for p in mesh.polygons:
  p.use_smooth=True
  for li in p.loop_indices:
   v=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=(v.x*5+.5,v.y*5+.5)
 obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);obj.data.materials.append(material);return obj
objects=[jets('Painterly_Blue',outer,.0048,.029,0,.0038,False)]
# Export at local burner origin and without range or preview lights.
bpy.ops.object.select_all(action='DESELECT')
for o in objects:o.select_set(True)
bpy.context.view_layer.objects.active=objects[0]
bpy.ops.export_scene.fbx(filepath=str(P/'model'/'KI_Range_Flame.fbx'),use_selection=True,object_types={'MESH'},add_leaf_bones=False,axis_forward='-Y',axis_up='Z',apply_unit_scale=True)
# Range is for presentation only, never included in export.
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.import_scene.fbx(filepath=str(R))
body=[o for o in bpy.context.selected_objects if o.type=='MESH']
for o in body:o.name='PREVIEW_ONLY_Range'
for m in bpy.data.materials:
 if m.use_nodes:
  for n in m.node_tree.nodes:
   if n.type=='TEX_IMAGE' and 'range-enamel' in getattr(n.image,'filepath',''):
    n.image=bpy.data.images.load(str(P.parent/'KI-RANGE-01'/'textures'/'range-enamel-v2.png'),check_existing=True)
# Source scene shows front-left burner; all four original port centers are ±.18, ±.15.
for o in objects:o.location=(-.18,-.15,.931)
bpy.ops.object.light_add(type='AREA',location=(1.4,-1.8,2.8));key=bpy.context.object;key.data.energy=175;key.data.shape='DISK';key.data.size=3.0
bpy.ops.object.light_add(type='POINT',location=(-.18,-.15,1.0));light=bpy.context.object;light.data.energy=1.5;light.data.color=(.18,.46,1.0);light.data.shadow_soft_size=.08
bpy.ops.object.camera_add(location=(1.3,-1.7,1.65));cam=bpy.context.object;cam.rotation_euler=(Vector((-.08,-.05,.76))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=1.18
s=bpy.context.scene;s.camera=cam;s.render.engine='CYCLES';s.cycles.samples=24;s.render.resolution_x=900;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.film_transparent=True;s.world.color=(.12,.10,.08);s.view_settings.view_transform='AgX'
s.render.image_settings.file_format='PNG';s.render.filepath=str(P/'previews'/'burner-on.png');bpy.ops.render.render(write_still=True)
cam.location=(.20,-.63,1.38);cam.rotation_euler=(Vector((-.18,-.15,.94))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.24
s.render.filepath=str(P/'previews'/'burner-detail-on.png');bpy.ops.render.render(write_still=True)
for o in objects:o.hide_render=True
light.data.energy=0;s.render.filepath=str(P/'previews'/'burner-detail-off.png');bpy.ops.render.render(write_still=True)
cam.location=(1.3,-1.7,1.65);cam.rotation_euler=(Vector((-.08,-.05,.76))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.18
s.render.filepath=str(P/'previews'/'burner-off.png');bpy.ops.render.render(write_still=True)
for o in objects:o.hide_render=False
light.data.energy=1.5
bpy.ops.wm.save_as_mainfile(filepath=str(P/'model'/'KI-RANGE-FLAME-01.blend'))
