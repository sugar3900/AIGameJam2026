import bpy, math, random
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent.parent
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.render.engine='CYCLES'; scene.cycles.samples=24
scene.view_settings.view_transform='AgX'
# A 20-column by 20-row flat-top hex lattice: an even column count ensures stagger continuity.
r=.03; W=30*r; H=20*math.sqrt(3)*r; gap=.001

def mat(name,color,texture=None,blend=0):
 m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
 n=m.node_tree.nodes; l=m.node_tree.links; bs=n.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=.79
 if texture:
  im=n.new('ShaderNodeTexImage'); im.image=bpy.data.images.load(str(texture),check_existing=True)
  mix=n.new('ShaderNodeMixRGB'); mix.blend_type='MIX'; mix.inputs[0].default_value=blend; mix.inputs[2].default_value=(*color,1)
  l.new(im.outputs['Color'],mix.inputs[1]); l.new(mix.outputs['Color'],bs.inputs['Base Color'])
 return m
tex=P/'textures'/'ivory-glaze.png'
ivory=mat('Ivory ceramic',(.79,.66,.57),tex,.3)
rose=mat('Dusty rose ceramic',(.56,.28,.27),tex,.80)
grout=mat('Warm cream grout',(.60,.51,.44))
# Clip polygons to exact module rectangle. Interpolated UVs preserve shared partial tiles.
def clip(poly,axis,bound,greater):
 out=[]
 for i,a in enumerate(poly):
  b=poly[(i+1)%len(poly)]; av=a[axis]; bv=b[axis]
  inside=(av>=bound-1e-9) if greater else (av<=bound+1e-9)
  nxt=(bv>=bound-1e-9) if greater else (bv<=bound+1e-9)
  if inside: out.append(a)
  if inside != nxt:
   t=(bound-av)/(bv-av); out.append(tuple(a[k]+t*(b[k]-a[k]) for k in range(4)))
 return out
verts=[]; faces=[]; uvs=[]; mids=[]
flowers={(6,5),(4,5),(5,6),(5,4),(6,4),(4,6)}
for col in range(-2,23):
 for row in range(-2,23):
  cx=1.5*r*col; cy=math.sqrt(3)*r*(row+.5*(col%2)); axial=(col%10,(row-(col-(col&1))//2)%10)
  isrose=axial in flowers
  # Sample many deterministic unmarked neighborhoods of the generated glaze.
  rng=random.Random((col%20)*100+(row%20)); u0=.10+.68*rng.random(); v0=.10+.68*rng.random(); span=.10
  poly=[]
  for k in range(6):
   ang=math.pi*k/3; dx=(r-gap)*math.cos(ang); dy=(r-gap)*math.sin(ang)
   poly.append((cx+dx,cy+dy,u0+span*(dx/(2*r)+.5),v0+span*(dy/(2*r)+.5)))
  for axis,bound,g in [(0,0,True),(0,W,False),(1,0,True),(1,H,False)]:
   if poly: poly=clip(poly,axis,bound,g)
  # Remove coincident and collinear clip vertices before triangulation.
  dedup=[]
  for point in poly:
   if not dedup or math.dist(point[:2],dedup[-1][:2])>1e-7: dedup.append(point)
  if len(dedup)>1 and math.dist(dedup[0][:2],dedup[-1][:2])<1e-7: dedup.pop()
  poly=dedup
  changed=True
  while changed and len(poly)>=3:
   changed=False
   for i in range(len(poly)):
    a,b,c=poly[i-1],poly[i],poly[(i+1)%len(poly)]
    if abs((b[0]-a[0])*(c[1]-b[1])-(b[1]-a[1])*(c[0]-b[0]))<1e-9:
     poly.pop(i);changed=True;break
  if len(poly)<3: continue
  start=len(verts); verts.extend([(a,b,.002) for a,b,u,v in poly]); faces.append(tuple(range(start,start+len(poly)))); uvs.append([(u,v) for a,b,u,v in poly]); mids.append(int(isrose))
mesh=bpy.data.meshes.new('Mosaic'); mesh.from_pydata(verts,[],faces); mesh.update()
obj=bpy.data.objects.new('Mosaic tops',mesh); bpy.context.collection.objects.link(obj)
mesh.materials.append(ivory); mesh.materials.append(rose); layer=mesh.uv_layers.new(name='UVMap')
for poly,uv,mi in zip(mesh.polygons,uvs,mids):
 poly.material_index=mi
 for li,coord in zip(poly.loop_indices,uv): layer.data[li].uv=coord
bpy.ops.mesh.primitive_cube_add(size=1,location=(W/2,H/2,-.0125)); back=bpy.context.object; back.name='Grout substrate'; back.dimensions=(W,H,.025); bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); back.data.materials.append(grout)
def export(path,objects):
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0]
 bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,apply_unit_scale=True,object_types={'MESH'},add_leaf_bones=False,path_mode='AUTO')
export(P/'model'/'BA_FLOOR_MODULE.fbx',[obj,back])
# Room-scale optional translucent wear: independent surface mesh, not repeated with mosaic.
weartex=P/'textures'/'wear-overlay.png'
bpy.ops.mesh.primitive_plane_add(size=2,location=(W,H,.0035)); wear=bpy.context.object; wear.name='Optional wear 1.8 x 2.08m'; wear.scale=(W,H,1); bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
wm=bpy.data.materials.new('Optional wear translucent'); wm.use_nodes=True
nodes=wm.node_tree.nodes; links=wm.node_tree.links; bs=nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(.30,.18,.12,1);bs.inputs['Roughness'].default_value=.9
im=nodes.new('ShaderNodeTexImage'); im.image=bpy.data.images.load(str(weartex),check_existing=True)
mult=nodes.new('ShaderNodeMath');mult.operation='MULTIPLY';mult.inputs[1].default_value=.35;links.new(im.outputs['Alpha'],mult.inputs[0]);links.new(mult.outputs[0],bs.inputs['Alpha'])
wear.data.materials.append(wm); export(P/'model'/'BA_FLOOR_WEAR.fbx',[wear])
# Duplicate modules into a 1.8 x 2.08m repeat preview (4 modules).
for x,y in [(1,0),(0,1),(1,1)]:
 for src in (obj,back):
  cp=src.copy();cp.data=src.data; bpy.context.collection.objects.link(cp);cp.location.x+=x*W;cp.location.y+=y*H
# Camera and render
world=scene.world or bpy.data.worlds.new('World');scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.21,.19,.18,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.45
bpy.ops.object.light_add(type='AREA',location=(0,-1,4)); light=bpy.context.object;light.data.energy=500;light.data.shape='DISK';light.data.size=5
bpy.ops.object.camera_add(location=(3.2,-3.4,4.5));cam=bpy.context.object;cam.rotation_euler=(Vector((W,H,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=3.8;scene.camera=cam
scene.render.resolution_x=1200;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
wear.hide_render=True;scene.render.filepath=str(P/'previews'/'mosaic-repeat.png');bpy.ops.render.render(write_still=True)
wear.hide_render=False;scene.render.filepath=str(P/'previews'/'mosaic-worn.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'model'/'BA-FLOOR-01.blend'))
print('MODULE',W,H,'faces',len(faces))
