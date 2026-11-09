"""Actual exported neighbours, source geometry coordinates; plan=(X,-Y,Z)."""
import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];ASSETS=ROOT.parent
m=json.loads((ROOT/'model/manifest.json').read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.context.scene.unit_settings.system='METRIC'
def imp(path):
 prior=set(bpy.context.scene.objects);bpy.ops.import_scene.fbx(filepath=str(path))
 obs=list(set(bpy.context.scene.objects)-prior)
 for o in list(obs):
  if o.name.startswith('UCX_'):bpy.data.objects.remove(o,do_unlink=True);obs.remove(o)
 return [o for o in obs if o.type=='MESH']
def bounds(obs):
 pts=[o.matrix_world@v.co for o in obs for v in o.data.vertices]
 return [min(v[k] for v in pts) for k in range(3)],[max(v[k] for v in pts) for k in range(3)]
def tree(o):return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons],epsilon=1e-8)
cabinets={};positions={'0425':(1.4125,.475),'0775':(3.0625,.475),'0450':(4.425,.475)}
for v in m['variants']:
 parts={}
 for g,p in v['parts'].items():
  obs=imp(ROOT/'model'/p['file']);assert len(obs)==1;ob=obs[0]
  ob.location+=Vector((positions[v['code']][0],-positions[v['code']][1],0));parts[g]=ob
 cabinets[v['code']]=parts
# Range: snap measured body back to approved north y=.15 and width centre x3.825.
rangebody=imp(ASSETS/'KI-RANGE-01/model/KI_RANGE_Body.fbx')[0]
lo,hi=bounds([rangebody]);range_offset=Vector((3.825-(lo[0]+hi[0])/2,-.15-hi[1],0))
rangebody.location+=range_offset
rangedoor=imp(ASSETS/'KI-RANGE-01/model/KI_RANGE_Door.fbx')[0];rangedoor.location+=range_offset
# Sink and fridge are actual FBXs, anchored at their approved centres/back planes.
sink=imp(ASSETS/'KI-SINK-NARROW-01/models/KI_SINK_NARROW_body.fbx')[0]
lo,hi=bounds([sink]);sink.location+=Vector((2.15-(lo[0]+hi[0])/2,-.15-hi[1],0))
fridge=imp(ASSETS/'KI-FRIDGE-01/models/KI_FRIDGE_BODY.fbx')[0]
lo,hi=bounds([fridge]);fridge_offset=Vector((.735-(lo[0]+hi[0])/2,-.15-hi[1],0));fridge.location+=fridge_offset
fridgedoor=imp(ASSETS/'KI-FRIDGE-01/models/KI_FRIDGE_DOOR.fbx')[0];fridgedoor.location+=fridge_offset
bpy.context.view_layer.update();rangelo,rangehi=bounds([rangebody]);fulllo,fullhi=bounds([rangebody,rangedoor])
assert abs(rangelo[0]-3.45)<1e-5 and abs(rangehi[0]-4.20)<1e-5
assert abs(-rangehi[1]-.15)<1e-5
rest={o:o.matrix_world.copy() for parts in cabinets.values() for o in parts.values()};rest[rangedoor]=rangedoor.matrix_world.copy()
def reset():
 for o,mat in rest.items():o.matrix_world=mat
 bpy.context.view_layer.update()
def pose(deg=None,slide=None):
 reset()
 for parts in cabinets.values():
  for g,o in parts.items():
   if deg is not None and g.startswith('door'):o.rotation_euler.z=math.radians(deg if g=='door_R' else -deg)
   if slide is not None and g.startswith('drawer'):o.location.y-=slide
 bpy.context.view_layer.update()
checks=[]
if '--preview-only' not in sys.argv:
 checks=[]
 for oven_deg in (0,82):
  for code,parts in cabinets.items():
   for g,moving in parts.items():
    if not(g.startswith('door') or g.startswith('drawer')):continue
    values=range(101) if g.startswith('door') else [j*.005 for j in range(61)]
    for value in values:
     reset();rangedoor.rotation_euler.x=math.radians(oven_deg)
     if g.startswith('door'):moving.rotation_euler.z=math.radians(value if g=='door_R' else -value)
     else:moving.location.y-=value
     bpy.context.view_layer.update();t=tree(moving)
     obstacles=[('range body',rangebody),('range oven door',rangedoor),('sink',sink),('fridge body',fridge),('fridge door',fridgedoor)]
     obstacles +=[(oc+'/'+og,o) for oc,ps in cabinets.items() for og,o in ps.items() if o!=moving]
     for label,o in obstacles:
      assert not t.overlap(tree(o)),(code,g,value,'oven',oven_deg,'overlap',label)
    checks.append({'variant':code,'part':g,'oven_angle':oven_deg,'samples':len(values),'range':([0,100] if g.startswith('door') else [0,.30]),'passed':True})
 # Simultaneous leaves + drawers also clear range and one another at 101 source poses.
 for deg in range(101):
  pose(deg,.30);moving=[(c+'/'+g,o) for c,ps in cabinets.items() for g,o in ps.items() if g.startswith(('door','drawer'))]
  ts=[(n,tree(o)) for n,o in moving]
  for i,(n,t) in enumerate(ts):
   for name,o in [('range body',rangebody),('oven door',rangedoor),('sink',sink),('fridge',fridge),('fridge door',fridgedoor)]:assert not t.overlap(tree(o)),(deg,n,name,'combined sweep')
   for n2,t2 in ts[i+1:]:assert not t.overlap(t2),(deg,n,n2,'combined sweep')
 result={'status':'passed','coordinate_map':'BVH tests use right-handed Blender source common coordinates (X,-planY,Z); isometric reflection yields UE floor-plan coordinates (X,planY,Z). No neighbour mesh scaled.','range_source_files':['KI-RANGE-01/model/KI_RANGE_Body.fbx','KI-RANGE-01/model/KI_RANGE_Door.fbx'],'range_offset_source_m':list(range_offset),'range_body_plan_bounds':[[rangelo[0],-rangehi[1],rangelo[2]],[rangehi[0],-rangelo[1],rangehi[2]]],'range_closed_assembly_plan_bounds':[[fulllo[0],-fullhi[1],fulllo[2]],[fullhi[0],-fulllo[1],fullhi[2]]],'casework_origin_plan_m':positions,'tests':checks,'simultaneous_open_samples':101,'neighbours':['actual range body/controls','actual range oven door closed and82 degrees','actual narrow sink body','actual fridge body and door','all three actual cabinet render assemblies'],'limitation':'Discrete triangle-intersection samples at1 degree for doors and5mm for drawers, not a continuous physics proof; validate engine hulls and easing.'}
 (ROOT/'model/range-fit-validation.json').write_text(json.dumps(result,indent=2)+'\n')
# Recreate authored shader values with explicit source image paths. FBX texture links
# can be unresolved even though the original packed blend renders correctly.
cache={}
def preview_material(source,kind):
 base=source.name.split('.')[0];key=(kind,base)
 if key in cache:return cache[key]
 mat=bpy.data.materials.new('Fit_'+kind+'_'+base);mat.use_nodes=True;n=mat.node_tree.nodes;p=n.get('Principled BSDF');p.inputs['Roughness'].default_value=.78
 files={'Cabinet_Sage':'sage-D.png','Counter_Ivory':'ivory-enamel.png','Interior_Wood':'interior-wood.png','Toe_Dark':'toe-dark.png'}
 file=(ROOT/'textures'/files[base]) if kind=='cabinet' and base in files else (ASSETS/'KI-RANGE-01/textures/range-enamel-v2.png') if base=='Enamel_Painted' else None
 if file:
  t=n.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(file),check_existing=False)
  if base=='Cabinet_Sage':
   hsv=n.new('ShaderNodeHueSaturation');hsv.inputs['Value'].default_value=.75;mat.node_tree.links.new(t.outputs['Color'],hsv.inputs['Color']);mat.node_tree.links.new(hsv.outputs['Color'],p.inputs['Base Color'])
  else:mat.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
 else:
  settings={'Aged_Brass':((.48,.29,.09),.7,.33),'Muted_Edge_Wear':((.38,.29,.13),0,.8),'Oven_Dark':((.082,.065,.052),0,.5),'Burner_Cast_Iron':((.075,.067,.06),.25,.8),'Aged_Steel':((.44,.40,.32),.7,.37),'Oven_Window':((.16,.115,.072),0,.32),'Gasket':((.13,.115,.09),0,.8)}
  assert base in settings,('unmapped preview material',base)
  color,metal,rough=settings[base];p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 cache[key]=mat;return mat
for o in [o for ps in cabinets.values() for o in ps.values()]:
 for i,mat in enumerate(o.data.materials):o.data.materials[i]=preview_material(mat,'cabinet')
for o in (rangebody,rangedoor):
 for i,mat in enumerate(o.data.materials):o.data.materials[i]=preview_material(mat,'range')
# Keep fit preview to the critical range and adjacent two cabinets; other neighbours tested above.
for o in list(cabinets['0425'].values())+[sink,fridge,fridgedoor]:o.hide_render=True
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=32;sc.render.resolution_x=1500;sc.render.resolution_y=1050;sc.render.resolution_percentage=100;sc.render.film_transparent=True;sc.render.image_settings.file_format='PNG';sc.world.color=(.22,.20,.17)
target=Vector((3.65,-.6,.55));bpy.ops.object.camera_add(location=(5.3,-3.5,2.2));cam=bpy.context.object;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.65;sc.camera=cam
for loc,energy in [((3,-3,4),500),((1,-1,2),200),((4,2,3),150)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=energy;o.data.size=4;o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler()
pose(0,0);sc.render.filepath=str(ROOT/'previews/range-fit-closed.png');bpy.ops.render.render(write_still=True)
pose(100,.30);sc.render.filepath=str(ROOT/'previews/range-fit-open.png');bpy.ops.render.render(write_still=True)
print('RANGE_FIT_PREVIEWS_COMPLETE' if '--preview-only' in sys.argv else 'RANGE_FIT_PASSED: 16 independent sweep configurations; 101 combined poses')
