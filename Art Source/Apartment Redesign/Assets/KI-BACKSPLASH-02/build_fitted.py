"""Fitted square checker tiles, cropped boundaries and ceramic bullnose."""
import bpy,math,json,shutil
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent;A=R.parent
for d in ('models','textures','previews'):(R/d).mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
bpy.context.scene.unit_settings.system='METRIC'
ns={'__file__':str(A/'KI-BACKSPLASH-01/model/build_backsplash.py')}
exec((A/'KI-BACKSPLASH-01/model/build_backsplash.py').read_text().split('# X along wall')[0],ns)
block=ns['block'];ivory=ns['ivory'];sage=ns['sage'];grout=ns['grout'];cap=ns['capmat']
for m in (ivory,sage,cap):
 for n in m.node_tree.nodes:
  if n.type=='TEX_IMAGE':
   src=Path(n.image.filepath);dst=R/'textures'/src.name
   if src.resolve()!=dst.resolve():shutil.copyfile(src,dst)
   n.image.filepath=str(dst);n.image.pack()
# Existing counter enamel for gap fillers.
im=bpy.data.images.load(str(A/'KI-CABINET-02/textures/ivory-enamel.png'));im.pack()
ct=bpy.data.materials.new('Counter_Ivory');ct.use_nodes=True;p=ct.node_tree.nodes['Principled BSDF'];p.inputs['Roughness'].default_value=.48;t=ct.node_tree.nodes.new('ShaderNodeTexImage');t.image=im;ct.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color']);shutil.copyfile(A/'KI-CABINET-02/textures/ivory-enamel.png',R/'textures/ivory-enamel.png')
recs=[];review=[]
def mesh_profile(name,width,h,vertical=False):
 # Quarter-round face smoothly returns to the wall; underside is flat.
 profile=[(0,h-.018),(-.018,h-.018)]
 for i in range(1,13):
  a=math.pi/2*(1-i/12);profile.append((-.018*math.sin(a),h-.018+.018*math.cos(a)))
 profile.append((0,h-.018))
 verts=[]
 for x in (0,width):verts.extend([(x,y,z) for y,z in profile])
 n=len(profile);faces=[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);o.data.materials.append(cap)
 return o

def export(name,parts,origin,role):
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();o=bpy.context.object;o.name=name
 bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.012);bpy.ops.object.mode_set(mode='OBJECT')
 bpy.ops.export_scene.fbx(filepath=str(R/'models'/(name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',path_mode='RELATIVE',add_leaf_bones=False)
 vs=[v.co for v in o.data.vertices];recs.append({'file':name+'.fbx','role':role,'world_origin_cm':origin,'source_min':[min(v[i] for v in vs) for i in range(3)],'source_max':[max(v[i] for v in vs) for i in range(3)],'collision':'static decorative backsplash: no collision; fillers use simple boxes','source_front':'-Y; UE +Y','scale':[1,1,1]})
 o.location=(origin[0]/100,-origin[1]/100,origin[2]/100);review.append(o)

for label,start,end,bottom,top in [('A',112.1,162.5,91,117.5),('B',267.5,345,91,117.5),('Range',345,420,107,117.5),('C',420,474,91,117.5)]:
 w=(end-start)/100;h=(top-bottom)/100
 parts=[block('Grout substrate',(w/2,-.004,(h-.018)/2),(w,.008,h-.018),grout)]
 # Grid anchored globally, so checker cadence is continuous across separated runs.
 gx0=math.floor(start/10);gx1=math.ceil(end/10);gz0=math.floor(bottom/10);gz1=math.ceil((top-1.8)/10)
 for gx in range(gx0,gx1):
  for gz in range(gz0,gz1):
   x0=max(start,gx*10+.15);x1=min(end,(gx+1)*10-.15);z0=max(bottom,gz*10+.15);z1=min(top-1.8,(gz+1)*10-.15)
   if x1-x0<.1 or z1-z0<.1:continue
   parts.append(block('Cropped square checker',((x0+x1)/200-start/100,-.011,(z0+z1)/200-bottom/100),((x1-x0)/100,.014,(z1-z0)/100),ivory if (gx+gz)%2==0 else sage,.0008))
 parts.append(mesh_profile('Top ceramic bullnose',w,h))
 if label=='A':
  # Rotated quarter-round top profile becomes an exposed left end; joins top cleanly.
  o=mesh_profile('Fridge-side ceramic bullnose',h-.018,.018)
  for v in o.data.vertices:
   x,y,z=v.co;v.co=(.018-z,y,x)
  parts.append(o)
 export('KI_Backsplash02_'+label,parts,[start,6,bottom],'fitted backsplash')
for label,x0,x1,y0,y1 in [('Rear0425',112.1,162.5,6,15),('Rear0775',267.5,345,6,15),('Rear0450',420,474,6,15),('EastEnd',465,474,15,80),('FridgeExtension',112.1,120,15,80)]:
 w=(x1-x0)/100;d=(y1-y0)/100
 parts=[block('Ivory counter infill',(w/2,-d/2,.02),(w,d,.04),ct,.0015)]
 export('KI_CounterFiller02_'+label,parts,[x0,y0,87],'counter infill top91cm')
(R/'assembly.json').write_text(json.dumps({'units':'metres; native meshes at identity, place using world_origin_cm with no scale','parts':recs,'top_cm':117.5,'window_apron_bottom_cm':118,'apron_clearance_cm':.5,'tile_pitch_cm':10,'note':'Remove legacy backsplash modules and all end caps. No bottom bullnose. Top bullnose only plus exposed fridge-side end. Fillers top91cm, thickness4cm.'},indent=2)+'\n')
s=bpy.context.scene
if s.world is None:s.world=bpy.data.worlds.new('Studio')
s.render.engine='CYCLES';s.cycles.samples=12;s.render.threads_mode='FIXED';s.render.threads=1;s.render.resolution_x=1200;s.render.resolution_y=500;s.render.resolution_percentage=100;s.world.color=(.22,.22,.22);s.render.image_settings.file_format='PNG'
bpy.ops.object.camera_add(location=(3,-4,2.2));cam=bpy.context.object;cam.rotation_euler=(Vector((2.93,-.25,1.02))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=4.15;s.camera=cam
bpy.ops.object.light_add(type='AREA',location=(2,-3,4));l=bpy.context.object;l.data.energy=350;l.data.size=4
s.render.filepath=str(R/'previews/fitted-runs.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/KI-BACKSPLASH-02.blend'))
print('FITTED_BACKSPLASH_COMPLETE')
