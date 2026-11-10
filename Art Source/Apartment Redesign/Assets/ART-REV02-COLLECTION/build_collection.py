"""Seventeen unique framed artworks. Blender 5.x; two CPU threads.
Owns only ART-REV02-* and FIX006 inventory/README. Original assets remain untouched.
All source pivots: bottom-center/back plane, front -Y, metres, Z up.
"""
import bpy,math,json,shutil,hashlib,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent;ASSETS=ROOT.parent
REPO=ASSETS.parents[2]
INV=REPO/'docs/03 Art & Audio/Apartment Design/layout-revision-02/feedback/FIX-006/wall-art-inventory.json'
catalog=json.loads((ROOT/'catalog.json').read_text());inventory=json.loads(INV.read_text())
SOURCE_WOOD=ASSETS/'HA-ART-02/textures/walnut_painterly.png'
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
selected=set(args) if args else {x['id'] for x in catalog}
profiles={
 'cove':[(0,.35),(.10,.86),(.22,.95),(.37,.60),(.55,.45),(.75,.48),(.91,.73),(1,.75)],
 'steps':[(0,.48),(.10,.95),(.32,.95),(.32,.72),(.66,.72),(.66,.52),(1,.52)],
 'bevel':[(0,.38),(.12,.70),(.85,.70),(1,.53)],
 'scoop':[(0,.55),(.08,.96),(.20,1),(.32,.81),(.47,.59),(.67,.43),(.82,.47),(1,.72)],
 'double_step':[(0,.55),(.08,.92),(.27,.92),(.27,.65),(.47,.65),(.47,.85),(.65,.85),(.65,.55),(1,.55)],
 'ogee':[(0,.40),(.07,.65),(.17,.92),(.28,1),(.39,.91),(.51,.66),(.63,.43),(.73,.45),(.84,.64),(.93,.82),(1,.82)],
 'round':[(0,.42),(.1,.64),(.25,.86),(.5,1),(.75,.86),(.9,.64),(1,.48)],
 'scotia':[(0,.78),(.12,.92),(.28,.66),(.50,.38),(.70,.43),(.88,.72),(1,.76)],
 'beaded':[(0,.4),(.15,.64),(.35,.88),(.60,.88),(.82,.68),(1,.56)],
 'flat':[(0,.4),(.08,.70),(.88,.70),(1,.52)],
 'convex':[(0,.45),(.15,.75),(.38,.98),(.6,.93),(.85,.67),(1,.45)],
 'oval':[(0,.4),(.16,.8),(.35,1),(.54,.93),(.77,.62),(1,.68)],
 'slope':[(0,.82),(.12,.96),(.87,.46),(1,.48)],
 'twin_round':[(0,.45),(.12,.82),(.25,.98),(.38,.82),(.5,.50),(.62,.82),(.75,.98),(.88,.82),(1,.48)],
 'fluted':[(0,.55),(.10,.8),(.22,.45),(.34,.8),(.46,.45),(.58,.8),(.70,.45),(.82,.8),(1,.52)],
 'small_bead':[(0,.4),(.17,.77),(.35,.9),(.55,.77),(.73,.5),(1,.5)],
 'farmhouse':[(0,.55),(.2,.85),(.8,.85),(1,.55)]}
def material(name,color,rough=.65,metal=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;return m
def mesh(name,v,f,mat):
 me=bpy.data.meshes.new(name);me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);me.materials.append(mat);return o
def activate(o):
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
def smart(o):
 activate(o);bpy.ops.object.transform_apply(location=False,rotation=True,scale=True);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT')
def box(name,loc,size,mat,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=size;activate(o);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat)
 if bevel:
  m=o.modifiers.new('Soft worn edge','BEVEL');m.width=bevel;m.segments=2;bpy.ops.object.modifier_apply(modifier=m.name)
 smart(o);return o
def ring(name,w,h,off,width,y,mat,oval=False):
 return mould(name,w,h,off,width,[(0,y),(1,y)],mat,oval=oval,absolute=True)
def mould(name,w,h,off,width,profile,mat,oval=False,absolute=False,depth=.035):
 loops=[]
 for t,d in profile:
  inset=off+t*width;ww=w/2-inset;hh=h/2-inset;yy=d if absolute else -depth*d/max(p[1] for p in profile)
  if oval:loops.append([(ww*math.cos(i*math.tau/96),yy,h/2+hh*math.sin(i*math.tau/96)) for i in range(96)])
  else:loops.append([(-ww,yy,inset),(ww,yy,inset),(ww,yy,h-inset),(-ww,yy,h-inset)])
 n=len(loops[0]);v=[x for l in loops for x in l];f=[]
 for j in range(len(loops)-1):
  for i in range(n):f.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
 # Close thin molding backs into a solid rail; ring remains hollow.
 outer=[(x,0,z) for x,_,z in loops[0]];inner=[(x,0,z) for x,_,z in loops[-1]];a=len(v);v+=outer+inner
 for i in range(n):
  k=(i+1)%n;f += [(i,a+i,a+k,k),((len(loops)-1)*n+i,(len(loops)-1)*n+k,a+n+k,a+n+i),(a+i,a+n+i,a+n+k,a+k)]
 o=mesh(name,v,f,mat);smart(o);return o
def surface(name,w,h,inset,y,mat,img,oval=False):
 aw=w-2*inset;ah=h-2*inset
 if oval:
  v=[(0,y,h/2)]+[(aw/2*math.cos(i*math.tau/96),y,h/2+ah/2*math.sin(i*math.tau/96)) for i in range(96)];f=[(0,1+i,1+(i+1)%96) for i in range(96)]
 else:v=[(-aw/2,y,inset),(aw/2,y,inset),(aw/2,y,h-inset),(-aw/2,y,h-inset)];f=[(0,1,2,3)]
 o=mesh(name,v,f,mat);uv=o.data.uv_layers.new(name='UVMap');aspect=img.size[0]/img.size[1];target=aw/ah;us=min(1,target/aspect);vs=min(1,aspect/target)
 for p in o.data.polygons:
  for li in p.loop_indices:
   co=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(.5+co.x/aw*us,.5+(co.z-h/2)/ah*vs)
 return o,{'u_span':us,'v_span':vs,'source_aspect':aspect,'aperture_aspect':target,'mode':'center crop; uniform pixel scale; no stretch'}
def ornament(name,loc,scale,mat):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,radius=1,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;o.data.materials.append(mat);smart(o);return o
def build(item,record):
 ident='ART-REV02-'+item['id'];dest=ASSETS/ident
 for d in ('models','previews','textures','concepts'):(dest/d).mkdir(parents=True,exist_ok=True)
 if not (dest/'textures/T_Artwork.png').exists():print('SKIP_MISSING',ident);return
 bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene
 w=max(record['rect'][2:]);h=record['h'];dep=.035
 if item['id']=='006':w=1.30;h=.90;dep=.055;record['rect']=[4.5,5.54-dep,w,dep];record['z']=1.12;record['h']=h
 oval=item['profile']=='oval';rail=min(w,h)*(.068 if item['id']!='006' else .075);matwidth=item['mat'];parts=[]
 wood=material(ident+'_Frame',item['wood'],.64,.12 if item['gilt'] else 0)
 texpath=dest/'textures/T_Frame_Grain.png';shutil.copy2(SOURCE_WOOD,texpath);im=bpy.data.images.load(str(texpath));im.pack();ns=wood.node_tree.nodes;links=wood.node_tree.links;t=ns.new('ShaderNodeTexImage');t.image=im;gray=ns.new('ShaderNodeRGBToBW');links.new(t.outputs['Color'],gray.inputs[0]);ramp=ns.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(*(c*.67 for c in item['wood']),1);ramp.color_ramp.elements[1].color=(*(min(1,c*1.3) for c in item['wood']),1);links.new(gray.outputs[0],ramp.inputs[0]);links.new(ramp.outputs[0],ns.get('Principled BSDF').inputs['Base Color'])
 gold=material(ident+'_Aged_Gilt',(.38,.26,.095),.48,.64);ivory=material(ident+'_Mount',(.72,.67,.55),.90);slip=material(ident+'_Inner_Slip',(.13,.19,.18) if item['id'] in ('005','010','016') else (.48,.37,.23),.70);back=material(ident+'_Backboard',(.12,.085,.055),.9)
 mainmat=gold if item['id'] in ('006','014') else wood
 parts.append(mould('Mitered '+item['profile']+' molding',w,h,0,rail,profiles[item['profile']],mainmat,oval,depth=dep))
 parts.append(ring('Inner contrasting slip',w,h,rail-.002,.005,-dep*.73,gold if item['gilt'] else slip,oval))
 if matwidth:
  parts.append(ring('Archival mount',w,h,rail,matwidth,-dep*.65,ivory,oval))
  if item['id'] in ('007','010','014','016'):
   parts.append(ring('Double mount colored bevel',w,h,rail+matwidth-.004,.004,-dep*.68,slip,oval))
 # Individually recognizable frame construction beyond recoloring.
 if item['id']=='006':parts.append(ring('Walnut outer edge',w,h,0,.010,-dep*.50,wood))
 if item['id'] in ('004','006'):
  for sx in (-1,1):
   for top in (False,True):
    x=sx*(w/2-rail*.5);z=h-rail*.5 if top else rail*.5
    if item['id']=='004':parts.append(ornament('Gilt rosette',(x,-dep*.90,z),(.007,.003,.007),gold))
    else:
     for j in (-1,0,1):
      o=ornament('Carved corner leaf',(x+sx*j*.009,-dep*.91,z+j*.009),(.006,.003,.012),gold);o.rotation_euler.y=sx*.65;parts.append(o)
 if item['id'] in ('009','016'):
  count=max(10,round(w/.018))
  for i in range(1,count):
   x=-w/2+rail*.5+(w-rail)*i/count
   for z in (rail*.5,h-rail*.5):parts.append(ornament('Frame beading',(x,-dep*.88,z),(.0028,.002,.0028),ivory))
 if item['id']=='017':
  for sx in (-1,1):
   for z in (rail*.5,h-rail*.5):parts.append(ornament('Corner brass pin',(sx*(w/2-rail*.5),-dep*.85,z),(.002,.001,.002),gold))
 if oval:
  bpy.ops.mesh.primitive_cylinder_add(vertices=96,radius=1,depth=.004,location=(0,-.002,h/2),rotation=(math.pi/2,0,0));board=bpy.context.object;board.scale=(w/2-.005,h/2-.005,1);board.data.materials.append(back);smart(board);parts.append(board)
 else:parts.append(box('Timber backboard',(0,-.003,h/2),(w-.006,.006,h-.006),back,.001))
 art=bpy.data.images.load(str(dest/'textures/T_Artwork.png'));art.pack();paint=material(ident+'_Artwork',(1,1,1),.86);t=paint.node_tree.nodes.new('ShaderNodeTexImage');t.image=art;paint.node_tree.links.new(t.outputs['Color'],paint.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
 panel,crop=surface('Unique artwork',w,h,rail+matwidth,-dep*.61,paint,art,oval);parts.append(panel)
 # Join while retaining materials and artwork UV; origin deliberately remains wall datum.
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();obj=bpy.context.object;obj.name=ident.replace('-','_');sc.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
 hull=box('UCX_'+obj.name+'_00',(0,-dep/2,h/2),(w,dep,h),back);hull.hide_render=True
 activate(obj);hull.select_set(True);bpy.ops.export_scene.fbx(filepath=str(dest/'models'/f'{ident}.fbx'),use_selection=True,object_types={'MESH'},add_leaf_bones=False,path_mode='AUTO',apply_unit_scale=True,axis_forward='-Y',axis_up='Z')
 verts=[obj.matrix_world@v.co for v in obj.data.vertices];lo=[min(v[k] for v in verts) for k in range(3)];hi=[max(v[k] for v in verts) for k in range(3)]
 assert max(abs(a-b) for a,b in zip(lo+hi,[-w/2,-dep,0,w/2,0,h]))<.003,(ident,lo,hi)
 entry={'asset':ident,'instance':record['instance'],'title':item['title'],'frame':item['frame'],'dimensions_m':[w,dep,h],'bounds_m':{'min':lo,'max':hi},'origin':'bottom-center rear wall plane; front -Y; Z up','planned_rect':record['rect'],'bottom_z':record['z'],'front':record['front'],'fbx':f'models/{ident}.fbx','art_texture':'textures/T_Artwork.png','art_sha256':hashlib.sha256((dest/'textures/T_Artwork.png').read_bytes()).hexdigest(),'crop':crop,'frame_material':{'wood_color_linear':item['wood'],'roughness':.64,'grain_map':'textures/T_Frame_Grain.png','shader':'RGBToBW(grain), ramp endpoints wood*0.67 and wood*1.3; legacy FBX needs material recreation'},'ucx':1,'status':'Source complete; Unreal installation/review pending'}
 (dest/'manifest.json').write_text(json.dumps(entry,indent=2)+'\n')
 (dest/'concepts/prompt.md').write_text('# '+item['title']+'\n\n'+item['subject']+'\n\nGenerated separately with built-in imagegen. Flat full-bleed painting, no frame or text. Center-cropped only through mesh UV to preserve proportions.\n') if item['id'] not in ('010','011','012','013','014','015','016') else None
 # Neutral reference wall and shallow angle establish distinct cross-sections.
 wallmat=material('PREVIEW chalk wall',(.40,.36,.29),.9);wall=box('PREVIEW_WALL',(0,.025,h/2),(3,.04,3),wallmat)
 bpy.ops.object.camera_add(location=(w*.20,-max(w,h)*2.8,h*.85));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,h/2))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=max(w,h)*1.20;sc.camera=cam
 bpy.ops.object.light_add(type='AREA',location=(-1,-2,3));light=bpy.context.object;light.data.energy=180;light.data.size=3;light.rotation_euler=(Vector((0,0,h/2))-light.location).to_track_quat('-Z','Y').to_euler()
 sc.world=bpy.data.worlds.new('Preview world');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.5,.5,.5,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.5
 sc.render.engine='CYCLES';sc.cycles.samples=16;sc.cycles.use_denoising=True;sc.render.threads_mode='FIXED';sc.render.threads=2;sc.render.resolution_x=640;sc.render.resolution_y=640;sc.render.resolution_percentage=100;sc.view_settings.view_transform='AgX';sc.render.image_settings.file_format='PNG';sc.render.filepath=str(dest/'previews/framed.png');bpy.ops.render.render(write_still=True)
 hull.hide_set(True);wall.hide_set(True);wall.hide_render=True;bpy.ops.wm.save_as_mainfile(filepath=str(dest/'models'/f'{ident}.blend'))
 record['source_art']=entry
 print('ART_COMPLETE',ident,flush=True)
 return entry
entries=[]
for item in catalog:
 if item['id'] in selected:
  rec=next(x for x in inventory['items'] if x['replacement_asset']=='ART-REV02-'+item['id']);e=build(item,rec)
  if e:entries.append(e)
inventory['status']='Unique source collection in progress; original instance IDs retained; engine integration pending'
INV.write_text(json.dumps(inventory,indent=2)+'\n')
(ROOT/'build-manifest.json').write_text(json.dumps(entries,indent=2)+'\n')
