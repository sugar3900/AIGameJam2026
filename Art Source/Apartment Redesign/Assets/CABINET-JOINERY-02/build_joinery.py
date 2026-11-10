"""FIX033/034/036. Preserve fitted carcasses; rebuild true frame/panel doors and hardware.
All exports functional-pivot local at identity. See assembly.json for original assembly offsets.
"""
from pathlib import Path
import bpy,bmesh,math,json,sys,shutil
import numpy as np
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parent;A=R.parent
for d in ('models','textures','previews'):(R/d).mkdir(exist_ok=True)
RENDER='--skip-render' not in sys.argv
BASE=json.loads((A/'KI-CABINET-02/model/manifest.json').read_text())
REPORT=[]

def active(o):
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o

def material(n,c,rough=.75,metal=0,image=None):
 m=bpy.data.materials.new(n);m.use_nodes=True;m.diffuse_color=(*c,1);p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 if image:
  t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=image;m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
 return m

def bake(name,paths,weights,tint=None,constant=None):
 out=None;shape=None
 for path,w in zip(paths,weights):
  im=bpy.data.images.load(str(path),check_existing=True);rgb=np.array(im.pixels[:],dtype=np.float32).reshape(-1,4)[:,:3];shape=im.size[:];linear=np.where(rgb<=.04045,rgb/12.92,((rgb+.055)/1.055)**2.4);out=linear*w if out is None else out+linear*w
 if tint is not None:out*=tint
 if constant is not None:out+=np.array(constant)
 out=np.clip(out,0,1);out=np.where(out<=.0031308,out*12.92,1.055*out**(1/2.4)-.055);pix=np.ones((len(out),4),np.float32);pix[:,:3]=out
 im=bpy.data.images.new(name,width=shape[0],height=shape[1]);im.pixels.foreach_set(pix.ravel());im.filepath_raw=str(R/'textures'/(name+'.png'));im.file_format='PNG';im.save();im.pack();return im

def box(n,loc,dim,m,parts,bev=.0015):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=n;o.dimensions=dim;active(o);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bev:
  b=o.modifiers.new('Joinery edge','BEVEL');b.width=min(bev,min(dim)*.2);b.segments=3;bpy.ops.object.modifier_apply(modifier=b.name)
  b=o.modifiers.new('Weighted normals','WEIGHTED_NORMAL');bpy.ops.object.modifier_apply(modifier=b.name)
 o.data.materials.append(m);parts.append(o);uv(o);return o

def uv(o):
 if not o.data.uv_layers:o.data.uv_layers.new(name='UVMap')
 for p in o.data.polygons:
  ax=max(range(3),key=lambda i:abs(p.normal[i]))
  for li in p.loop_indices:
   v=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co
   o.data.uv_layers.active.data[li].uv=((v.y*1.7+.5,v.z*1.7) if ax==0 else (v.x*1.7+.5,v.z*1.7) if ax==1 else (v.x*1.7+.5,v.y*1.7+.5))

def cylinder(n,loc,r,d,m,parts,axis='Y'):
 bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=r,depth=d,location=loc,rotation=(math.pi/2,0,0) if axis=='Y' else (0,0,0));o=bpy.context.object;o.name=n;active(o);bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
 b=o.modifiers.new('Turned edge','BEVEL');b.width=min(.0008,r*.1);b.segments=2;bpy.ops.object.modifier_apply(modifier=b.name);o.data.materials.append(m);parts.append(o);uv(o);return o

def knob(cx,front,z,brass,ivory,parts):
 # Turned metal rose, narrow neck, flattened ceramic mushroom and rolled collar.
 cylinder('Knob backplate',(cx,front-.002,z),.011,.004,brass,parts)
 cylinder('Knob neck',(cx,front-.009,z),.0045,.014,brass,parts)
 cylinder('Knob collar',(cx,front-.015,z),.0085,.003,brass,parts)
 bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,radius=1,location=(cx,front-.023,z));o=bpy.context.object;o.name='Turned ceramic grip';o.scale=(.0145,.009,.0145);active(o);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for p in o.data.polygons:p.use_smooth=True
 o.data.materials.append(ivory);parts.append(o);uv(o)

def pull(cx,front,z,vertical,brass,parts):
 def pos(u,y):return (cx,y,z+u) if vertical else (cx+u,y,z)
 for u in (-.048,.048):cylinder('Pull rose',pos(u,front-.0015),.0085,.003,brass,parts)
 pts=[pos(-.048,front-.002),pos(-.048,front-.012),pos(-.033,front-.027),pos(.033,front-.027),pos(.048,front-.012),pos(.048,front-.002)]
 cu=bpy.data.curves.new('96mm bow pull','CURVE');cu.dimensions='3D';cu.bevel_depth=.0045;cu.bevel_resolution=3;cu.resolution_u=12;cu.use_fill_caps=True;sp=cu.splines.new('BEZIER');sp.bezier_points.add(len(pts)-1)
 for p,co in zip(sp.bezier_points,pts):p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
 ob=bpy.data.objects.new('96mm bow pull',cu);bpy.context.collection.objects.link(ob);active(ob);bpy.ops.object.convert(target='MESH');ob.data.materials.append(brass)
 for p in ob.data.polygons:p.use_smooth=True
 parts.append(ob);uv(ob)

def hinge(axis,heights,side,brass,parts):
 x,y,_=axis
 for z in heights:
  cylinder('Hinge barrel on pivot',(x,y,z),.0055,.044,brass,parts,'Z')
  box('Hinge leaf',(x-side*.014,y-.009,z),(.025,.004,.034),brass,parts,.0007)

def framed(cx,cy,cz,w,h,rail,paint,parts,mid=None):
 #22mm rails/stiles,6mm panel at rear with14mm recess from front. Panel tongue overlaps3mm.
 for x in (cx-w/2+rail/2,cx+w/2-rail/2):box('Frame stile',(x,cy,cz),(rail,.022,h),paint,parts)
 for z in (cz-h/2+rail/2,cz+h/2-rail/2):box('Frame rail',(cx,cy,z),(w-2*rail,.022,rail),paint,parts)
 ranges=[(cz-h/2+rail,cz+h/2-rail)]
 if mid is not None:
  box('Centre rail',(cx,cy,mid),(w-2*rail,.022,rail),paint,parts);ranges=[(ranges[0][0],mid-rail/2),(mid+rail/2,ranges[0][1])]
 for lo,hi in ranges:box('Thin recessed panel',(cx,cy+.006,(lo+hi)/2),(w-2*rail+.006,.006,hi-lo+.006),paint,parts,.0007)

def load(path):
 before=set(bpy.context.scene.objects);bpy.ops.import_scene.fbx(filepath=str(path));objs=[o for o in set(bpy.context.scene.objects)-before if o.type=='MESH'];visual=next(o for o in objs if not o.name.startswith('UCX_'));hulls=[o for o in objs if o!=visual]
 for m in visual.data.materials:
  if not m or not m.use_nodes:continue
  for node in m.node_tree.nodes:
   if node.type=='TEX_IMAGE' and node.image:
    candidate=path.parent.parent/'textures'/Path(node.image.filepath).name
    if candidate.exists():node.image=bpy.data.images.load(str(candidate),check_existing=True)
 return visual,hulls

def strip_material(o,predicate):
 bm=bmesh.new();bm.from_mesh(o.data);bad=[f for f in bm.faces if predicate(o.data.materials[f.material_index].name)];bmesh.ops.delete(bm,geom=bad,context='FACES');bm.to_mesh(o.data);bm.free()

def swap(o,paint,inside,brass):
 for i,m in enumerate(o.data.materials):
  n=m.name.lower()
  if any(k in n for k in ('sage','ivory','painterly')) and 'counter' not in n:o.data.materials[i]=paint
  elif any(k in n for k in ('interior','timber')):o.data.materials[i]=inside
  elif 'brass' in n:o.data.materials[i]=brass

def export(name,parts,pivot,hulls,kit):
 active(parts[0])
 for o in parts:o.select_set(True)
 bpy.ops.object.join();o=bpy.context.object;o.name=name;active(o);bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
 # All vertices now assembly-space. Shift to the functional pivot; identity object transform.
 pv=Vector(pivot)
 for v in o.data.vertices:v.co-=pv
 for i,h in enumerate(hulls):
  active(h);bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
  for v in h.data.vertices:v.co-=pv
  h.name='UCX_'+name+'_%02d'%i
 for m in o.data.materials:
  if not m or not m.use_nodes:continue
  for n in m.node_tree.nodes:
   if n.type=='TEX_IMAGE' and n.image:
    im=n.image;src=Path(bpy.path.abspath(im.filepath));dst=R/'textures'/src.name
    if src.exists() and src.resolve()!=dst.resolve():shutil.copyfile(src,dst)
    if dst.exists():im.filepath=str(dst);im.pack()
 active(o)
 for h in hulls:h.select_set(True)
 bpy.ops.export_scene.fbx(filepath=str(R/'models'/(name+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,add_leaf_bones=False,axis_forward='-Z',axis_up='Y',path_mode='RELATIVE')
 for h in hulls:bpy.data.objects.remove(h,do_unlink=True)
 xyz=[v.co+pv for v in o.data.vertices];rec={'file':name+'.fbx','kit':kit,'pivot_source_m':list(pivot),'export':'pivot-local vertices / identity object','assembly_min':[min(p[i] for p in xyz) for i in range(3)],'assembly_max':[max(p[i] for p in xyz) for i in range(3)],'slots':[m.name for m in o.data.materials],'ucx':len(hulls),'triangles':sum(len(p.vertices)-2 for p in o.data.polygons)};REPORT.append(rec)
 if 'Door' in name or '_door' in name:
  sign=-1 if ('RightDoor' in name or '_door_R' in name) else 1
  rec.update(engine_swing_sign=sign,source_swing_sign=-sign,max_angle_deg=(60 if 'LowerDoor' in name else 90) if kit=='Linen' else 100)
 # Restore assembled pose for review/save.
 o.location=pv;return o

def hull(loc,dim):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.dimensions=dim;active(o);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return o

def preview(kit,objs,scale,focus):
 s=bpy.context.scene;s.world=bpy.data.worlds.new('Neutral studio');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.18,.18,.18,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.50
 s.render.engine='CYCLES';s.cycles.samples=16;s.render.resolution_x=1000;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX';s.render.image_settings.file_format='PNG'
 bpy.ops.object.camera_add(location=(2,-3.7,focus+1.25));cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=scale;cam.rotation_euler=(Vector((0,0,focus))-cam.location).to_track_quat('-Z','Y').to_euler();s.camera=cam
 for pos,power,size in [((1,-3,4),200,3),((-2,-1,2),130,2)]:
  bpy.ops.object.light_add(type='AREA',location=pos);o=bpy.context.object;o.data.energy=power;o.data.size=size;o.rotation_euler=(Vector((0,0,focus))-o.location).to_track_quat('-Z','Y').to_euler()
 s.render.filepath=str(R/'previews'/(kit+'-closed.png'))
 if RENDER:bpy.ops.render.render(write_still=True)
 for o,angle in objs:
  if angle is None:o.location.y-=.30
  else:o.rotation_euler.z=math.radians(angle)
 cam.data.ortho_scale=scale*1.18;s.render.filepath=str(R/'previews'/(kit+'-open.png'))
 if RENDER:bpy.ops.render.render(write_still=True)
 for o,angle in objs:
  if angle is None:o.location.y+=.30
  else:o.rotation_euler.z=0
 bpy.ops.wm.save_as_mainfile(filepath=str(R/'models'/(kit+'.blend')))

for kit in ('Base0425','Base0775','Base0450','Upper','Pantry','Linen'):
 bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1;s.render.threads_mode='FIXED';s.render.threads=1;bpy.context.preferences.filepaths.save_version=0
 brass=material('Joinery_AgedBrass',(.32,.22,.085),.42,.65);ceramic=material('Joinery_KnobIvory',(.63,.59,.48),.32)
 if kit.startswith('Base'):
  im=bake('T_Joinery_Sage',[A/'KI-CABINET-02/textures/sage-D.png'],[1],tint=.75);paint=material('Joinery_Sage',(.30,.36,.20),.78,image=im)
 else:
  if kit=='Linen':im=bake('T_Joinery_Ivory',[A/'BA-LINEN-01/textures/ivory-paint-C.png'],[.44],constant=np.array([.94,.91,.82])*.56);paint=material('Joinery_Ivory',(.75,.70,.58),.72,image=im)
  else:im=bake('T_Joinery_Sage',[A/'KI-CABINET-02/textures/sage-D.png'],[1],tint=.75);paint=material('Joinery_Sage',(.30,.36,.20),.78,image=im)
 imi=bake('T_Joinery_Interior',[A/'KI-PANTRY-01/textures/interior-wood.png'],[.52],constant=np.array([.36,.26,.18])*.48);inside=paint if kit=='Linen' else material('Joinery_Interior',(.36,.26,.18),.80,image=imi)
 moving=[]
 if kit.startswith('Base'):
  code=kit[4:];v=next(v for v in BASE['variants'] if v['code']==code);w=v['carcass_width'];shift=v['carcass_offset_x'];paired=code=='0775';dw=(w-.106)/2 if paired else w-.10;lw=(w-.038)/2 if paired else w-.032;centres=[-(lw+.006)/2,(lw+.006)/2] if paired else [0]
  body,hs=load(A/'KI-CABINET-02/model'/v['parts']['body']['file']);strip_material(body,lambda n:'wear' in n.lower());swap(body,paint,inside,brass);export('KI_Cab03_'+code+'_Body',[body],(0,0,0),hs,kit)
  for j,cx in enumerate(centres):
   side=1 if paired and j else -1;key=('door_R' if j else 'door_L') if paired else 'door';pv=(shift+side*(w/2-.010),-.253,0);parts=[]
   framed(cx+shift,-.264,.393,lw,.515,.040,paint,parts);pull(cx+shift-side*(lw/2-.020),-.275,.440,True,brass,parts);hinge(pv,(.24,.53),side,brass,parts)
   o=export('KI_Cab03_'+code+'_'+key,parts,pv,[hull((cx+shift,-.264,.393),(lw,.022,.515))],kit);moving.append((o,100 if side==1 else -100))
   key=('drawer_R' if j else 'drawer_L') if paired else 'drawer';o,hs=load(A/'KI-CABINET-02/model'/v['parts'][key]['file']);strip_material(o,lambda n:any(k in n.lower() for k in ('brass','wear')));swap(o,paint,inside,brass);parts=[o];pull(shift+(side*(dw+.006)/2 if paired else 0),-.275,.765,False,brass,parts);o=export('KI_Cab03_'+code+'_'+key,parts,(0,0,0),hs,kit);moving.append((o,None))
  preview(kit,moving,1.20 if paired else 1.05,.45)
 else:
  old={'Upper':'KI-UPPER-01','Pantry':'KI-PANTRY-01','Linen':'BA-LINEN-01'}[kit];prefix={'Upper':'KI_Upper','Pantry':'KI_Pantry','Linen':'BA_Linen'}[kit];newprefix=prefix+'02'
  body,hs=load(A/old/'model'/(prefix+'_Body.fbx'));strip_material(body,lambda n:any(t in n.lower() for t in ('wear','worn','ochre')));swap(body,paint,inside,brass);export(newprefix+'_Body',[body],(0,0,0),hs,kit)
  if kit=='Upper':specs=[('LeftDoor',-.235,-.178,.265,.462,.470,-1,(-.472,-.167,.265),.085,None),('RightDoor',.235,-.178,.265,.462,.470,1,(.472,-.167,.265),.085,None)];heights=(.13,.40);scale=1.40;focus=.27
  elif kit=='Pantry':specs=[('LeftDoor',-.235,-.329,1.02,.454,1.65,-1,(-.470,-.318,1.02),1.02,.99),('RightDoor',.235,-.329,1.02,.454,1.65,1,(.470,-.318,1.02),1.02,.99)];heights=(.42,1.02,1.61);scale=2.45;focus=.98
  else:specs=[('LowerDoor',0,-.316,.565,.545,.68,-1,(-.278,-.305,.565),.565,None),('UpperDoor',0,-.316,1.295,.545,.68,-1,(-.278,-.305,1.295),1.295,None)];scale=2.10;focus=.88
  for key,cx,cy,cz,w,h,side,pv,kz,mid in specs:
   parts=[];rail=.040;framed(cx,cy,cz,w,h,rail,paint,parts,mid);knob(cx-side*(w/2-rail/2),cy-.011,kz,brass,ceramic,parts);hinge(pv,(cz-.22,cz+.22) if kit=='Linen' else heights,side,brass,parts)
   o=export(newprefix+'_'+key,parts,pv,[hull((cx,cy,cz),(w,.022,h))],kit);angle=(60 if key=='LowerDoor' else 90) if kit=='Linen' else 100;moving.append((o,angle if side==1 else -angle))
  preview(kit,moving,scale,focus)
(R/'assembly.json').write_text(json.dumps({'units':'metres; source -Y front; X stays X, Y flips in Unreal','export':'all meshes pivot-local identity. Place at transformed pivot_source_m relative to current assembly origin, no double translation','frame_thickness_m':.022,'panel_thickness_m':.006,'panel_front_recess_m':.014,'pull_mount_centres_m':.096,'parts':REPORT},indent=2)+'\n')
print('JOINERY BUILD COMPLETE',len(REPORT))

# Preserve explicit integration metadata on rebuild.
a=json.loads((R/'assembly.json').read_text());a.update(json.loads((R/'material-contract.json').read_text()))
for rec in a['parts']:
 f=rec['file'];k=rec['kit']
 if k.startswith('Base'):
  c=k[4:];part=f.split(c+'_')[1].removesuffix('.fbx');rec['replaces']='KI-CABINET-02/model/KI_CAB_'+c+'_'+part.lower()+'.fbx'
 else:
  old={'Upper':('KI-UPPER-01','KI_Upper'),'Pantry':('KI-PANTRY-01','KI_Pantry'),'Linen':('BA-LINEN-01','BA_Linen')}[k];rec['replaces']=old[0]+'/model/'+f.replace(old[1]+'02',old[1])
(R/'assembly.json').write_text(json.dumps(a,indent=2)+'\n')
