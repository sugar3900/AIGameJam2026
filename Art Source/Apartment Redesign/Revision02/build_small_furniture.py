"""Source-style wall table and stool, dimensions in metres. No edits to original assets."""
import bpy,math,json,shutil
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parents[1]/'Assets'

def build(aid,w,d,h):
 root=BASE/aid
 for sub in ('model','previews','textures'):(root/sub).mkdir(parents=True,exist_ok=True)
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.context.scene.unit_settings.system='METRIC';bpy.context.preferences.filepaths.save_version=0
 mats=[]
 for name,file in [('PaintedWalnut','table-wood-v2.png'),('PaintedSage','table-sage-v1.png')]:
  path=root/'textures'/file;shutil.copy2(BASE/'KI-TABLE-01/textures'/file,path)
  m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.82
  t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(path),check_existing=True);t.image.pack();m.node_tree.links.new(t.outputs['Color'],bs.inputs['Base Color']);mats.append(m)
 pieces=[];hulls=[]
 def box(name,loc,dim,mat,bev=.004):
  bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
  if bev:
   mod=o.modifiers.new('Eased joinery','BEVEL');mod.width=bev;mod.segments=3;bpy.ops.object.modifier_apply(modifier=mod.name)
  o.data.materials.append(mat);pieces.append(o);return o
 def hull(loc,dim):
  bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.hide_render=True;hulls.append(o);return o
 # Rounded rectangle top with a routed lower bead, preserves profile dimensions.
 box('Lower rim',(0,0,h-.033),(w-.018,d-.018,.022),mats[0],.008)
 box('Walnut top',(0,0,h-.016),(w,d,.032),mats[0],.010)
 hull((0,0,h-.022),(w,d,.044))
 is_table=aid=='KI-WALL-TABLE-02'
 inset=.07 if is_table else .045
 ax=w/2-inset;ay=d/2-inset;apronh=.08 if is_table else .055
 for y in (-ay,ay):box('Long sage apron',(0,y,h-.044-apronh/2),(2*ax+.025,.025,apronh),mats[1]);hull((0,y,h-.044-apronh/2),(2*ax+.025,.025,apronh))
 for x in (-ax,ax):box('End sage apron',(x,0,h-.044-apronh/2),(.025,2*ay,apronh),mats[1]);hull((x,0,h-.044-apronh/2),(.025,2*ay,apronh))
 for sx in (-1,1):
  for sy in (-1,1):
   foot=Vector((sx*(ax+.015),sy*(ay+.015),.0006));top=Vector((sx*ax,sy*ay,h-.045));v=top-foot
   bpy.ops.mesh.primitive_cone_add(vertices=16,radius1=.019 if is_table else .015,radius2=.029 if is_table else .024,depth=v.length,location=(top+foot)/2)
   o=bpy.context.object;o.name='Tapered timber leg';o.rotation_euler=v.to_track_quat('Z','Y').to_euler();bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
   for vert in o.data.vertices:
    if vert.co.z<.01:vert.co.z=0
   o.data.materials.append(mats[0]);pieces.append(o)
   co=hull((top+foot)/2,(.06 if is_table else .048,.06 if is_table else .048,v.length));co.rotation_euler=v.to_track_quat('Z','Y').to_euler()
   # Turned collar keeps familiar vintage detail without deforming source proportions.
   bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,location=(sx*ax,sy*ay,h-.12));o=bpy.context.object;o.scale=(.032,.032,.017) if is_table else (.026,.026,.013);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mats[0]);pieces.append(o)
 if not is_table:
  for y in (-ay,ay):box('Low stretcher',(0,y,.16),(2*ax,.017,.027),mats[1],.003)
  for x in (-ax,ax):box('Low stretcher',(x,0,.20),(.017,2*ay,.027),mats[1],.003)
 for o in pieces:
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.015);bpy.ops.object.mode_set(mode='OBJECT')
 bpy.ops.object.select_all(action='DESELECT')
 for o in pieces:o.select_set(True)
 bpy.context.view_layer.objects.active=pieces[0];bpy.ops.object.join();asset=bpy.context.object;asset.name=aid.replace('-','_');bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
 for i,o in enumerate(hulls):o.name=f'UCX_{asset.name}_{i:02}';o.select_set(True)
 bpy.ops.export_scene.fbx(filepath=str(root/'model'/f'{asset.name}.fbx'),use_selection=True,object_types={'MESH'},add_leaf_bones=False,axis_forward='-Y',axis_up='Z',apply_unit_scale=True)
 for o in hulls:o.hide_set(True)
 sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=24;sc.render.resolution_x=900;sc.render.resolution_y=800;sc.render.resolution_percentage=100;sc.render.film_transparent=True;sc.world.color=(.22,.2,.17)
 bpy.ops.object.camera_add(location=(1.5,-2,1.4));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,h*.55))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=max(w,h)*1.8;sc.camera=cam
 for loc,energy in [((1,-3,4),250),((-2,-1,2),140),((0,3,3),180)]:
  bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=energy;o.data.size=3;o.rotation_euler=(Vector((0,0,h*.5))-o.location).to_track_quat('-Z','Y').to_euler()
 sc.render.image_settings.file_format='PNG';sc.render.filepath=str(root/'previews/perspective.png');bpy.ops.render.render(write_still=True)
 bpy.ops.wm.save_as_mainfile(filepath=str(root/'model'/f'{aid}.blend'))
 (root/'assembly.json').write_text(json.dumps({'asset':aid,'dimensions_m':[w,d,h],'origin':'floor centre','source_front':'-Y','source_up':'+Z','fbx_axes':{'forward':'-Y','up':'Z'},'parts':[{'file':f'model/{asset.name}.fbx','offset_m':[0,0,0]}],'collision':'Per-member UCX, open underside retained','new_geometry':True,'texture_source':'KI-TABLE-01'},indent=2)+'\n')
 (root/'README.md').write_text(f'''# {aid} — fitted {'kitchen wall table' if is_table else 'tucked stool'}

New source-style geometry reusing the approved vintage dining table painted walnut and sage textures. Dimensions {w:.2f} × {d:.2f} × {h:.2f} m; floor-centred origin, front −Y, up Z, FBX −Y forward/Z up. Unit scale 1. Hardware/joinery profiles are physical dimensions, not a squashed dining-table mesh. See assembly.json. Separate convex UCX members preserve the open underside; no animation.

Build: Blender headless --python ../../Revision02/build_small_furniture.py (script builds both items). Model, packed textures and perspective preview included. Pending parent visual and FBX round-trip review; engine fit remains integration work. Table planning centre (2.45,3.455), stool (2.45,3.50); table faces north. Stool is intentionally tucked beneath the apron, not intersecting legs. Pull the stool north for use.
''')
for args in [('KI-WALL-TABLE-02',.90,.45,.74),('KI-STOOL-02',.30,.30,.45)]:build(*args)
