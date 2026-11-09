import bpy, math, bmesh
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent.parent
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def mat(name,tint):
 m=bpy.data.materials.new(name);m.diffuse_color=(*tint,1);m.use_nodes=True
 n=m.node_tree.nodes;p=n.get('Principled BSDF');p.inputs['Roughness'].default_value=.92
 img=n.new('ShaderNodeTexImage');img.image=bpy.data.images.load(str(ROOT/'textures'/'terry.png'),check_existing=True)
 mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.88;mix.inputs[2].default_value=(*tint,1)
 m.node_tree.links.new(img.outputs['Color'],mix.inputs[1]);m.node_tree.links.new(mix.outputs[0],p.inputs['Base Color']);return m
ivory=mat('Terry_Ivory',(1.0,.91,.80)); rose=mat('Terry_DustyRose',(.66,.25,.24))
parts=[]
def layer(name,dimensions,position):
 bpy.ops.mesh.primitive_cube_add(size=1, location=position);o=bpy.context.object;o.name=name;o.dimensions=dimensions
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 mod=o.modifiers.new('soft_rounded_fold','BEVEL');mod.width=.010;mod.segments=4
 bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 for p in o.data.polygons:p.use_smooth=True
 o.data.materials.append(ivory)
 if name=='Upper_fold':
  # Split the existing top face at stripe edges; assign its actual faces a
  # contrasting material. No coplanar overlay and no surface-height change.
  o.data.materials.append(rose)
  bm=bmesh.new();bm.from_mesh(o.data)
  for cut in (-.0565,-.0495,-.0415,-.0345):
   bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-7,plane_co=(0,cut-position[1],0),plane_no=(0,1,0),clear_inner=False,clear_outer=False)
  bm.normal_update()
  for face in bm.faces:
   center=face.calc_center_median(); y=center.y+position[1]
   if face.normal.z>.98 and ((-.0565<y<-.0495) or (-.0415<y<-.0345)):
    face.material_index=1
  bm.to_mesh(o.data);bm.free();o.data.update()
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.015);bpy.ops.object.mode_set(mode='OBJECT')
 parts.append(o);return o
layer('Lower_fold',(.296,.190,.026),(-.001,.003,.013))
layer('Middle_fold',(.298,.194,.026),(.001,.001,.039))
layer('Upper_fold',(.300,.198,.026),(0,-.001,.065))
# Join to one asset, preserving per-face UVs and two material slots.
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();towel=bpy.context.object;towel.name='BA_Folded_Towel'
bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
# Export before adding preview-only elements.
bpy.ops.export_scene.fbx(filepath=str(ROOT/'model'/'BA_Folded_Towel.fbx'),use_selection=True,axis_forward='-Y',axis_up='Z',apply_unit_scale=True,object_types={'MESH'},add_leaf_bones=False)
# Preview environment
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.mesh.primitive_plane_add(size=4,location=(0,0,-.0008));floor=bpy.context.object;floor.name='PreviewOnly_Floor'
m=bpy.data.materials.new('Preview');m.diffuse_color=(.32,.25,.21,1);m.use_nodes=True;m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.32,.25,.21,1);floor.data.materials.append(m)
def point(o,target):o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(.62,-.85,.62));cam=bpy.context.object;point(cam,(0,0,.04));cam.data.type='ORTHO';cam.data.ortho_scale=.52;bpy.context.scene.camera=cam
for loc,power,size in [((-.5,-.5,.9),30,1.3),((.6,.4,.75),15,1.0)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;point(o,(0,0,0))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=32;s.render.resolution_x=900;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.film_transparent=False
s.world.color=(.16,.16,.16);s.view_settings.view_transform='AgX';s.render.filepath=str(ROOT/'previews'/'towel-perspective.png')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'model'/'BA-FOLDED-TOWEL-01.blend'))
bpy.ops.render.render(write_still=True)
