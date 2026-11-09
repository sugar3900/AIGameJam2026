"""Fitted widths: 425, 775 and 450 mm. No global nonuniform furniture scaling."""
import bpy, math, json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
VARIANTS=[('0425',.425),('0775',.775),('0450',.450)]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.context.scene.unit_settings.system='METRIC'
bpy.context.preferences.filepaths.save_version=0
M={}
def tex(name,file):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;p=n.get('Principled BSDF');t=n.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(ROOT/'textures'/file),check_existing=True);t.image.pack()
 if name=='Cabinet_Sage':
  hsv=n.new('ShaderNodeHueSaturation');hsv.inputs['Value'].default_value=.75;m.node_tree.links.new(t.outputs['Color'],hsv.inputs['Color']);m.node_tree.links.new(hsv.outputs['Color'],p.inputs['Base Color'])
 else:m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
 p.inputs['Roughness'].default_value=.78;return m
for k,f in [('Cabinet_Sage','sage-D.png'),('Counter_Ivory','ivory-enamel.png'),('Interior_Wood','interior-wood.png'),('Toe_Dark','toe-dark.png')]:M[k]=tex(k,f)
def mat(name,col,metal=0,rough=.7):
 m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m
sage=M['Cabinet_Sage'];ivory=M['Counter_Ivory'];wood=M['Interior_Wood'];dark=M['Toe_Dark'];brass=mat('Aged_Brass',(.48,.29,.09),.7,.33);wear=mat('Muted_Edge_Wear',(.38,.29,.13),0,.8)
allparts=[];manifest={'units':'metres','up':'Z','front':'-Y','countertop_top':.91,'overall_depth':.65,'upstand':'none: separate backsplash and sill','variants':[]}
for code,module_w in VARIANTS:
 filler_w=.040 if code in ('0775','0450') else 0
 shift=-.020 if code=='0775' else .020 if code=='0450' else 0
 w=module_w-filler_w
 parts={};hulls={};prefix='KI_CAB_'+code
 def reg(o,g,m):o.data.materials.append(m);parts.setdefault(g,[]).append(o);return o
 def box(name,loc,dim,m,g='body',bev=.004,collision=True,offset=True):
  loc=(loc[0]+(shift if offset else 0),loc[1],loc[2])
  bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
  if collision:hulls.setdefault(g,[]).append((loc,dim))
  if bev:
   mod=o.modifiers.new('Soft edges','BEVEL');mod.width=min(bev,min(dim)*.22);mod.segments=3;bpy.ops.object.modifier_apply(modifier=mod.name)
   mod=o.modifiers.new('Weighted normals','WEIGHTED_NORMAL');bpy.ops.object.modifier_apply(modifier=mod.name)
  return reg(o,g,m)
 def cyl(name,loc,r,h,m,g,rot=(0,0,0)):
  loc=(loc[0]+shift,loc[1],loc[2])
  bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=r,depth=h,location=loc,rotation=rot);o=bpy.context.object;o.name=name;return reg(o,g,m)
 def curve(name,pts,r,m,g):
  pts=[(p[0]+shift,p[1],p[2]) for p in pts]
  cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=16;cu.bevel_depth=r;cu.bevel_resolution=3;sp=cu.splines.new('BEZIER');sp.bezier_points.add(len(pts)-1)
  for q,co in zip(sp.bezier_points,pts):q.co=co;q.handle_left_type='AUTO';q.handle_right_type='AUTO'
  ob=bpy.data.objects.new(name,cu);bpy.context.collection.objects.link(ob);bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.convert(target='MESH');return reg(ob,g,m)
 # Fixed-thickness stiles and shelves; shallow carcass puts pull extents within 650 mm.
 for side in (-1,1):box('Carcass side',(side*(w/2-.023),.04,.455),(.036,.55,.77),sage)
 box('Back',(0,.30,.455),(w-.08,.03,.77),wood)
 for z,t in [(.165,.035),(.41,.025),(.67,.025)]:box('Shelf',(0,.025,z),(w-.08,.52,t),wood)
 box('Toe kick',(0,.015,.055),(w-.016,.56,.11),dark,bev=.006)
 box('Enamel worktop',(0,0,.885),(module_w,.65,.05),ivory,bev=.009,offset=False)
 if filler_w:
  filler_x=(1 if code=='0775' else -1)*(module_w/2-filler_w/2)
  box('Recessed sage range filler',(filler_x,.04,.455),(filler_w,.46,.77),sage,bev=.003,offset=False)
 for side in (-1,1):box('Front stile',(side*(w/2-.033),-.226,.48),(.028,.025,.75),sage)
 box('Divider rail',(0,-.226,.662),(w-.10,.025,.020),sage,bev=.002)
 dw=w-.10
 paired=code=='0775'
 if paired:
  box('Centre stile',(0,-.226,.48),(.020,.025,.75),sage)
  box('Drawer divider',(0,.01,.77),(.020,.49,.18),wood)
 leaf_width=(dw-.006)/2 if paired else dw
 centers=[-(leaf_width+.006)/2,(leaf_width+.006)/2] if paired else [0]
 pivots={'body':(0,0,0)}
 for j,cx in enumerate(centers):
  sign=1 if paired and j==1 else -1
  g=('door_R' if j==1 else 'door_L') if paired else 'door'
  hinge=(shift+sign*(w/2-.042),-.2705,0);pivots[g]=hinge
  box('Door panel',(cx,-.2575,.393),(leaf_width,.035,.515),sage,g,.007)
  for x in (-leaf_width/2+.051,leaf_width/2-.051):box('Door stile',(cx+x,-.2805,.393),(.028,.014,.442),sage,g,.002,False)
  for z in (.180,.606):box('Door rail',(cx,-.2765,z),(leaf_width-.12,.014,.028),sage,g,.002,False)
  hx=cx-sign*(leaf_width/2-.075)
  curve('Door handle',[(hx,-.2845,.48),(hx-sign*.005,-.3025,.46),(hx-sign*.005,-.3025,.36),(hx,-.2845,.34)],.008,brass,g)
  for z in (.24,.53):
   cyl('Hinge barrel',(hinge[0]-shift,-.2705,z),.011,.065,brass,g)
   box('Hinge leaf',(hinge[0]-shift-sign*.013,-.2745,z),(.025,.01,.047),brass,g,.002,False)
  for xx,z,ww in [(-.35*leaf_width,.174,.035),(.16*leaf_width,.174,.03),(-.28*leaf_width,.613,.025),(.30*leaf_width,.613,.022)]:box('Fine edge rub',(cx+xx,-.2885,z),(ww,.0008,.0025),wear,g,0,False)
  # Each hollow drawer has five convex wall/bottom hulls, no enclosing box.
  g=('drawer_R' if j==1 else 'drawer_L') if paired else 'drawer';pivots[g]=(0,0,0)
  box('Drawer front',(cx,-.2575,.765),(leaf_width,.035,.18),sage,g,.006)
  iw=(w-.16-.026)/2 if paired else w-.16
  box('Drawer bottom',(cx,-.0025,.708),(iw,.475,.022),wood,g)
  for x in (-(iw/2-.01),iw/2-.01):box('Drawer side',(cx+x,-.0025,.768),(.02,.475,.12),wood,g,.003)
  box('Drawer back',(cx,.225,.768),(iw-.04,.02,.12),wood,g,.003)
  curve('Drawer pull',[(cx-.105,-.2825,.775),(cx-.085,-.2955,.76),(cx+.085,-.2955,.76),(cx+.105,-.2825,.775)],.008,brass,g)
  for x in (-.105,.105):cyl('Pull mount',(cx+x,-.2765,.775),.017,.008,brass,g,(math.pi/2,0,0))
 joined={};record={'code':code,'width':module_w,'module_width':module_w,'carcass_width':w,'carcass_offset_x':shift,'filler_width':filler_w,'filler_side':('east' if code=='0775' else 'west' if code=='0450' else None),'filler_front_y':(-.19 if filler_w else None),'parts':{}}
 for g,obs in parts.items():
  for ob in obs:
   bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.015);bpy.ops.object.mode_set(mode='OBJECT')
  bpy.ops.object.select_all(action='DESELECT')
  for ob in obs:ob.select_set(True)
  bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();ob=bpy.context.object;ob.name=prefix+'_'+g
  bpy.context.scene.cursor.location=pivots[g];bpy.ops.object.origin_set(type='ORIGIN_CURSOR');joined[g]=ob
  cs=[]
  for i,(loc,dim) in enumerate(hulls[g]):
   bpy.ops.mesh.primitive_cube_add(size=1,location=loc);c=bpy.context.object;c.name='UCX_'+ob.name+'_%02d'%i;c.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);bpy.context.scene.cursor.location=pivots[g];bpy.ops.object.origin_set(type='ORIGIN_CURSOR');cs.append(c)
  bpy.ops.object.select_all(action='DESELECT');ob.select_set(True)
  for c in cs:c.select_set(True)
  bpy.context.view_layer.objects.active=ob
  bpy.ops.export_scene.fbx(filepath=str(ROOT/'model'/(ob.name+'.fbx')),use_selection=True,object_types={'MESH'},add_leaf_bones=False,apply_unit_scale=True,path_mode='AUTO',axis_forward='-Z',axis_up='Y')
  pts=[ob.matrix_world@Vector(v) for v in ob.bound_box];mins=[min(v[k] for v in pts) for k in range(3)];maxs=[max(v[k] for v in pts) for k in range(3)]
  record['parts'][g]={'file':ob.name+'.fbx','object':ob.name,'pivot':pivots[g],'closed_min':mins,'closed_max':maxs,'ucx_hulls':len(cs)}
  for c in cs:bpy.data.objects.remove(c,do_unlink=True)
 
 if paired:
  for g,identity in [('door_L','Sink_Door_L'),('door_R','Sink_Door_R'),('drawer_L','Sink_Drawer_L'),('drawer_R','Sink_Drawer_R')]:record['parts'][g]['gameplay_identity']=identity
 manifest['variants'].append(record);allparts.append((code,joined))
# Save each variant with native origins; exclude other variants in its source scene.
for code,joined in allparts:
 for co,js in allparts:
  for ob in js.values():ob.hide_render=co!=code;ob.hide_set(co!=code)
 bpy.context.scene['active_variant']=code
 bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'model'/('KI-CABINET-02-'+code+'.blend')))
# Presentation lineup. The saved individual files above retain all origin positions unchanged.
for x,(code,joined) in zip((-1.0,0,1.0),allparts):
 for ob in joined.values():ob.hide_render=False;ob.hide_set(False);ob.location.x+=x
sc=bpy.context.scene
bpy.ops.object.camera_add(location=(3.4,-5.6,3.0));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.48))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=3.65;sc.camera=cam
for name,loc,power,size in [('Key',(0,-3,4),450,5),('Fill',(-3,-1,2.5),180,4)]:
 bpy.ops.object.light_add(type='AREA',location=loc);ob=bpy.context.object;ob.name=name;ob.data.energy=power;ob.data.shape='DISK';ob.data.size=size;ob.rotation_euler=(Vector((0,0,.45))-ob.location).to_track_quat('-Z','Y').to_euler()
sc.world.color=(.22,.20,.17);sc.render.engine='CYCLES';sc.cycles.samples=32;sc.render.resolution_x=1500;sc.render.resolution_y=850;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.film_transparent=True
sc.render.filepath=str(ROOT/'previews'/'casework-closed.png');bpy.ops.render.render(write_still=True)
for _,js in allparts:
 for g,ob in js.items():
  if g.startswith('door'):ob.rotation_euler.z=math.radians(100 if g=='door_R' else -100)
  if g.startswith('drawer'):ob.location.y-=.30
sc.render.filepath=str(ROOT/'previews'/'casework-open.png');bpy.ops.render.render(write_still=True)
(ROOT/'model'/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('FITTED_CASEWORK_COMPLETE')
