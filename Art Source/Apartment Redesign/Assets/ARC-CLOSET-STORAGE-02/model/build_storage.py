from pathlib import Path
import bpy, math, json
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1
parts=[];collision=[]
def mat(name,col,metal=0,tex=None):
 m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=.8 if not metal else .45
 if tex:
  t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(R/'textures'/tex));t.image.pack();m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
 return m
ivory=mat('Aged_White_Wood',(.79,.75,.65),tex='closet-white-wood.png');wood=mat('Warm_Hanger_Wood',(.32,.20,.10));brass=mat('Aged_Brass',(.34,.23,.09),.65)
def reg(o,m):o.data.materials.append(m);parts.append(o);return o
def box(name,loc,dim,m,bevel=.003):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 mod=o.modifiers.new('Eased joinery','BEVEL');mod.width=min(bevel,min(dim)*.22);mod.segments=3;bpy.ops.object.modifier_apply(modifier=mod.name)
 return reg(o,m)
def cyl(name,loc,r,depth,m,rot=(0,0,0)):
 bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=r,depth=depth,location=loc,rotation=rot);o=bpy.context.object;o.name=name
 mod=o.modifiers.new('Soft metal edges','BEVEL');mod.width=.001;mod.segments=2;bpy.ops.object.modifier_apply(modifier=mod.name)
 for p in o.data.polygons:p.use_smooth=True
 return reg(o,m)
def bar(name,a,b,r,m):
 a,b=Vector(a),Vector(b);o=cyl(name,(a+b)/2,r,(b-a).length,m);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
box('Painted storage shelf',(0,-.15,1.9675),(.95,.30,.035),ivory)
collision.append(((0,-.15,1.9675),(.95,.30,.035)))
# Cleats and diagonal brackets terminate at the rear plane, without protruding into wall.
box('Rear cleat',(0,-.015,1.925),(.87,.03,.05),ivory,.002)
for x in (-.40,.40):
 box('Wall bracket back',(x,-.012,1.87),(.045,.024,.18),ivory,.002)
 bar('Shelf diagonal support',(x,-.03,1.79),(x,-.25,1.946),.009,brass)
 bar('Rail support',(x,-.262,1.95),(x,-.262,1.85),.008,brass)
 cyl('Bracket screw',(x,-.026,1.91),.008,.004,brass,(math.pi/2,0,0))
# Rail near front edge. Narrow convex box permits item/player traces without adding hangar collisions.
cyl('Brass clothes rail',(0,-.27,1.85),.012,.87,brass,(0,math.pi/2,0))
collision.append(((0,-.27,1.85),(.87,.024,.024)))
for x in (-.442,.442):cyl('Rail end button',(x,-.27,1.85),.017,.018,brass,(0,math.pi/2,0))
# Hanger planes run along closet depth; rail runs across width. Three empty wood hangers.
for idx,x in enumerate((-.30,0,.30)):
 # Bent hook arcs around the X-directed rail, open at bottom back.
 pts=[]
 for j in range(17):
  a=math.radians(-55+j*290/16);pts.append((x,-.27+.025*math.cos(a),1.845+.025*math.sin(a)))
 for a,b in zip(pts,pts[1:]):bar('Hanger hook',a,b,.0035,brass)
 bar('Hanger neck',(x,-.279,1.822),(x,-.27,1.755),.004,brass)
 for yy in (-.48,-.06):bar('Wood hanger shoulder',(x,-.27,1.755),(x,yy,1.59),.009,wood)
 bar('Wood hanger bottom',(x,-.48,1.59),(x,-.06,1.59),.008,wood)
# Smart UVs and single static visual mesh.
for ob in parts:
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.015);bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_all(action='DESELECT')
for ob in parts:ob.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();visual=bpy.context.object;visual.name='ARC_ClosetStorage02';sc.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
hulls=[]
for idx,(loc,dim) in enumerate(collision):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=f'UCX_ARC_ClosetStorage02_{idx:02d}';o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);hulls.append(o)
bpy.ops.object.select_all(action='DESELECT');visual.select_set(True)
for o in hulls:o.select_set(True)
bpy.context.view_layer.objects.active=visual
bpy.ops.export_scene.fbx(filepath=str(R/'model/ARC_ClosetStorage02.fbx'),use_selection=True,object_types={'MESH'},add_leaf_bones=False,axis_forward='-Y',axis_up='Z',apply_unit_scale=True,path_mode='RELATIVE')
for o in hulls:o.hide_render=True;o.hide_set(True)
(R/'assembly.json').write_text(json.dumps({'asset':'ARC-CLOSET-STORAGE-02','units':'metres','up':'+Z','front':'-Y','origin':'rear-edge center at floor level; rear plane local Y=0','exports':[{'file':'model/ARC_ClosetStorage02.fbx','mesh':'ARC_ClosetStorage02','assembly_offset':[0,0,0],'collision_hulls':2}],'shelf_bounds':{'min':[-.475,-.30,1.95],'max':[.475,0,1.985]},'rail_center':[0,-.27,1.85],'recommended_placements':[{'closet':'coat','plan_origin':[11.375,6.34,0],'front':'north','plan_mapping':'x=11.375+localX; y=6.34+localY; z=localZ'},{'closet':'guest','plan_origin':[11.375,6.46,0],'front':'south','plan_mapping':'x=11.375-localX; y=6.46-localY; z=localZ'}],'motion':'static shelf/rail/hangers; no door geometry'},indent=2)+'\n')
# Studio renders show the shelf assembly only, using a separate non-exported backdrop.
bpy.ops.object.camera_add(location=(2,-3,2.7));cam=bpy.context.object;cam.rotation_euler=(Vector((0,-.18,1.78))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=1.30;sc.camera=cam
for loc,power,size in [((1,-3,4),300,3),((-2,-1,3),150,2),((0,2,3),200,2)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.size=size;o.rotation_euler=(Vector((0,-.2,1.8))-o.location).to_track_quat('-Z','Y').to_euler()
sc.world.color=(.20,.18,.14);sc.render.engine='CYCLES';sc.cycles.samples=24;sc.render.resolution_x=1000;sc.render.resolution_y=800;sc.render.resolution_percentage=100;sc.render.film_transparent=True;sc.render.image_settings.file_format='PNG'
for name,loc in [('perspective',(2,-3,2.7)),('front',(0,-3,1.82)),('side',(3,-.20,1.82))]:
 cam.location=loc;cam.rotation_euler=(Vector((0,-.18,1.78))-cam.location).to_track_quat('-Z','Y').to_euler();sc.render.filepath=str(R/'previews'/f'{name}.png');bpy.ops.render.render(write_still=True)
cam.location=(2,-3,2.7);cam.rotation_euler=(Vector((0,-.18,1.78))-cam.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.wm.save_as_mainfile(filepath=str(R/'model/ARC-CLOSET-STORAGE-02.blend'))
