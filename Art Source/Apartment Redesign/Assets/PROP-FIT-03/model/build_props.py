"""Reproducible source-only follow-up: rail-seated bedroom hangers, supported pan suspension, woven throw."""
from pathlib import Path
import bpy, math, json, sys
from mathutils import Vector, Matrix
R=Path(__file__).resolve().parents[1]; A=R.parent
bpy.context.preferences.filepaths.save_version=0
report={}
def select(obs):
 bpy.ops.object.select_all(action='DESELECT')
 for o in obs:o.select_set(True)
 bpy.context.view_layer.objects.active=obs[0]
def export(name,obs):
 select(obs);bpy.ops.export_scene.fbx(filepath=str(R/'model'/f'{name}.fbx'),use_selection=True,object_types={'MESH'},add_leaf_bones=False,axis_forward='-Y',axis_up='Z',apply_unit_scale=True,bake_anim=False,path_mode='COPY',embed_textures=True)
def tube(name,pts,r,mat):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=r;c.bevel_resolution=3;c.use_fill_caps=True;s=c.splines.new('POLY');s.points.add(len(pts)-1)
 for p,co in zip(s.points,pts):p.co=(*co,1)
 o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o);select([o]);bpy.ops.object.convert(target='MESH');o=bpy.context.object;o.data.materials.append(mat)
 for p in o.data.polygons:p.use_smooth=True
 return o
def uv(obs):
 for o in obs:
  if not o.data.uv_layers:
   select([o]);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.015);bpy.ops.object.mode_set(mode='OBJECT')
def preview(name,target,scale):
 sc=bpy.context.scene
 for o in list(sc.objects):
  if o.type in {'LIGHT','CAMERA'}:bpy.data.objects.remove(o,do_unlink=True)
 for loc,power in [((1,-3,3),250),((-2,-1,2),160)]:
  bpy.ops.object.light_add(type='AREA',location=Vector(target)+Vector(loc));o=bpy.context.object;o.data.energy=power;o.data.size=2;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
 bpy.ops.object.camera_add(location=Vector(target)+Vector((1,-3,1)));o=bpy.context.object;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.type='ORTHO';o.data.ortho_scale=scale;sc.camera=o
 sc.world.color=(.18,.18,.18);sc.render.engine='CYCLES';sc.cycles.samples=16;sc.render.resolution_x=1000;sc.render.resolution_y=800;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.film_transparent=True;sc.render.filepath=str(R/'previews'/f'{name}.png');bpy.ops.render.render(write_still=True)
# Retain the original shelf and rail mesh construction and authored UCX, excluding old hangers.
code=(A/'ARC-CLOSET-STORAGE-02/model/build_storage.py').read_text()
start=code.index('# Hanger planes');end=code.index('# Smart UVs')
code=code[:start]+code[end:code.index('# Studio renders')]
code=code.replace('R=Path(__file__).resolve().parents[1]',f'R=Path({str(R)!r})').replace("R/'textures'/tex",f"Path({str(A/'ARC-CLOSET-STORAGE-02/textures')!r})/tex")
code=code.replace("'asset':'ARC-CLOSET-STORAGE-02'","'asset':'PROP-FIT-03 storage'").replace('static shelf/rail/hangers','static shelf/rail; hangers exported separately')
code=code.replace('ARC_ClosetStorage02','ARC_ClosetStorage03').replace("R/'assembly.json'","R/'storage-assembly.json'")
exec(compile(code,'storage-source','exec'),{'__file__':__file__})
# Export is already written. Use identical bedroom shoulder/hook vocabulary, rail datum at origin.
for o in list(bpy.data.objects):bpy.data.objects.remove(o,do_unlink=True)
wood=bpy.data.materials.new('CS03_HangerWood');wood.use_nodes=True
p=wood.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.31,.16,.065,1);p.inputs['Roughness'].default_value=.72
t=wood.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(A/'BR-CLOSET-STORAGE-03/textures/hanger-wood.png'));t.image.pack();wood.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
metal=bpy.data.materials.new('CS03_AgedSteel');metal.use_nodes=True;p=metal.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.3,.25,.18,1);p.inputs['Metallic'].default_value=.75;p.inputs['Roughness'].default_value=.38
pts=[(.022*math.cos(math.radians(a)),0,-.0065+.022*math.sin(math.radians(a))) for a in range(-35,226,5)]+[(-.012,0,-.037),(-.004,0,-.052),(0,0,-.068),(0,0,-.114)]
obs=[tube('HA_Hanger03_Hook',pts,.0035,metal)]
shape=[(-.205,-.237),(-.201,-.222),(-.095,-.159),(-.025,-.120),(0,-.113),(.025,-.120),(.095,-.159),(.201,-.222),(.205,-.237)]
obs += [tube('HA_Hanger03_Shoulders',[(x,0,z) for x,z in shape],.009,wood),tube('HA_Hanger03_Bar',[(-.205,0,-.237),(.205,0,-.237)],.007,wood),tube('HA_Hanger03_Ferrule',[(0,0,-.121),(0,0,-.106)],.006,metal)]
uv(obs)
# Rotate hanger plane to YZ to sit perpendicular to entry rail X. Contact datum remains (0,0,0).
for o in obs:o.rotation_euler.z=math.pi/2
export('HA_Hanger03',obs);bpy.ops.wm.save_as_mainfile(filepath=str(R/'model/HA_Hanger03.blend'));preview('hanger',(0,0,-.10),.55)
report['entry_hangers']={'storage':'ARC_ClosetStorage03.fbx','hanger':'HA_Hanger03.fbx','rail_datum_offsets':[[-.30,-.27,1.85],[0,-.27,1.85],[.30,-.27,1.85]],'hook_inner_apex':.012,'rail_radius':.012,'plane':'YZ; matches bedroom shoulder/hook construction; no old baked hangers'}
# Pan pair: transform original real-hole handle to face viewer, handle upward; hole centres coincide with hook bottom.
bpy.ops.wm.open_mainfile(filepath=str(A/'KI-PAN-01/model/KI-PAN-01.blend'))
metal=bpy.data.materials.new('PanHook_AgedSteel');metal.use_nodes=True
p=metal.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.19,.15,.10,1);p.inputs['Metallic'].default_value=.8;p.inputs['Roughness'].default_value=.4
parts=[o for o in bpy.context.scene.objects if o.type=='MESH']
for o in list(bpy.context.scene.objects):
 if o not in parts:bpy.data.objects.remove(o,do_unlink=True)
# Pan body bottoms face wall; original top (+Z) becomes front(-Y); handle+X becomes+Z.
rot=Matrix(((0,-1,0),(0,0,-1),(1,0,0)))
for o in parts:o.hide_render=True
allp=[]
for idx,(x,k) in enumerate([(-.18,.78),(.18,1.0)]):
 hole=Vector((x,-.070,-.060));offset=hole-rot@Vector((.331,0,.053))*k
 for original in parts:
  o=original.copy();o.data=original.data.copy();bpy.context.collection.objects.link(o);o.hide_render=False;o.name=f'Pan{idx+1}_{original.name}'
  for v in o.data.vertices:v.co=rot@(original.matrix_world@v.co)*k+offset
  o.matrix_world=Matrix.Identity(4);allp.append(o)
 # Hook top loop wraps rail y=-.045 z0; lower wire crosses handle hole along Y.
 points=[(x,-.045+.010*math.cos(a),-.0017+.010*math.sin(a)) for a in [math.radians(20+i*300/40) for i in range(41)]]
 points += [(x,-.045,-.030),(x,-.045,-.060),(x,-.095,-.060),(x,-.105,-.050),(x,-.105,-.040)]
 allp.append(tube(f'Engaged_S_hook_{idx+1}',points,.0023,metal))
for o in parts:bpy.data.objects.remove(o,do_unlink=True)
uv(allp);export('KI_PanPair03',allp);bpy.ops.wm.save_as_mainfile(filepath=str(R/'model/KI_PanPair03.blend'));preview('pan-pair',(0,-.07,-.22),.95)
report['pans']={'file':'KI_PanPair03.fbx','origin':'existing rail wall-centre at bar height; same actor yaw as rail','replace':'both existing pan body/handle pairs; keep rail BODY only, remove old hooks','diameters':[.2028,.26],'hole_radius':[.00468,.006],'wire_radius':.0023,'hole_centres':[[-.18,-.070,-.060],[.18,-.070,-.060]]}
(R/'assembly.json').write_text(json.dumps(report,indent=2)+'\n')
print('PROP-FIT-03 ready')
