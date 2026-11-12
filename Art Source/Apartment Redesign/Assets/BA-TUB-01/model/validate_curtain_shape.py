import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from io_scene_fbx import parse_fbx
D=Path(__file__).resolve().parents[1];M=D/'model'
bpy.ops.wm.open_mainfile(filepath=str(M/'BA-TUB-01.blend'))
o=bpy.data.objects['Curtain_panel_sliding'];report={'blend_shape_keys':list(o.data.shape_keys.key_blocks.keys()),'materials':[m.name for m in o.data.materials],'units':{'system':bpy.context.scene.unit_settings.system,'scale_length':bpy.context.scene.unit_settings.scale_length}}
assert report['blend_shape_keys']==['Basis','Closed','Closed_Mid']
tub=bpy.data.objects['BA_Tub03_Body'];tubvs=[tub.matrix_world@v.co for v in tub.data.vertices];tubfaces=[tuple(p.vertices) for p in tub.data.polygons];bvh=BVHTree.FromPolygons(tubvs,tubfaces)
keys=o.data.shape_keys.key_blocks
uncorrected=[b.co.lerp(c.co,.5) for b,c in zip(keys['Basis'].data,keys['Closed'].data)]
report['uncorrected_halfway_row_arc_cm']={label:round(100*sum((uncorrected[j*65+i+1]-uncorrected[j*65+i]).length for i in range(64)),3) for label,j in [('top',0),('mid',16),('hem',32)]}
report['drape']={'knee_center_world_z_cm':65,'knee_transition_world_z_cm':[58,72],'open_cloth_center_outward_shift_cm':5.5,'open_cloth_tilt_degrees':round(math.degrees(math.atan(.055/1.48)),3),'open_ring_to_lower_center_angle_degrees':round(math.degrees(math.atan(.09/(2.17-.65))),3),'closed_tilt_degrees':0}
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(M/'BA_Curtain_Animated.fbx'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];arms=[o for o in bpy.context.scene.objects if o.type=='ARMATURE'];assert len(meshes)==len(arms)==1
o=meshes[0];report['fbx_shape_keys']=list(o.data.shape_keys.key_blocks.keys());report['bones']=[b.name for b in arms[0].data.bones];assert report['fbx_shape_keys']==['Basis','Closed','Closed_Mid'];assert report['bones']==['CurtainRoot'];assert any(m.type=='ARMATURE' for m in o.modifiers)
root,_=parse_fbx.parse(str(M/'BA_Curtain_Animated.fbx'))
def walk(e):
 yield e
 for c in e.elems:yield from walk(c)
report['fbx_blend_shape_channels']=sum(1 for e in walk(root) if b'BlendShapeChannel' in e.props)
assert report['fbx_blend_shape_channels']==2
report['world_bounds_cm']={};report['row_arc_cm']={};report['minimum_tub_clearance_cm']={};report['fabric_width_cm']=210;report['open_fold_depth_cm']={}
for w in [i/20 for i in range(21)]:
 o.data.shape_keys.key_blocks['Closed'].value=w;o.data.shape_keys.key_blocks['Closed_Mid'].value=4*w*(1-w);bpy.context.view_layer.update();ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());vs=[ev.matrix_world@v.co for v in ev.data.vertices]
 world=[(580-100*v.x,907+100*v.y,100*v.z) for v in vs]
 report['world_bounds_cm'][str(w)]={axis:[round(min(v[i] for v in world),3),round(max(v[i] for v in world),3)] for i,axis in enumerate('xyz')}
 if w in [0,.5,1]:
  arcs={}
  for label,row in [('top',0),('mid',16),('z60',(2.13-.60)/1.905*32),('hem',32)]:
   j=int(row);f=row-j
   pts=[vs[j*65+i].lerp(vs[min(32,j+1)*65+i],f) for i in range(65)]
   arcs[label]=round(100*sum((b-a).length for a,b in zip(pts,pts[1:])),3)
  report['row_arc_cm'][str(w)]=arcs
  upper_arcs=[100*sum((vs[j*65+i+1]-vs[j*65+i]).length for i in range(64)) for j in range(33)]
  assert all(abs(a-210)<.01 for a in upper_arcs)
  report.setdefault('all_row_range_cm',{})[str(w)]=[round(min(upper_arcs),3),round(max(upper_arcs),3)]
  if w==0:
   for label,j in [('top',0),('hem',32)]:
    ys=[v.y for v in vs[j*65+4:j*65+65]];report['open_fold_depth_cm'][label]=round(100*(max(ys)-min(ys)),3)
 row_arcs=[100*sum((vs[j*65+i+1]-vs[j*65+i]).length for i in range(64)) for j in range(33)]
 report.setdefault('animation_row_range_cm',{})[str(w)]=[round(min(row_arcs),3),round(max(row_arcs),3)]
 assert all(abs(a-210)<6.3 for a in row_arcs),(w,min(row_arcs),max(row_arcs))
 # Sample triangle interiors, both cloth surfaces; +Y ray from room side finds actual tub front.
 clearance=float('inf');samples=0
 for layer in [0,2145]:
  for j in range(25,32):
   for i in range(64):
    q=layer+j*65+i
    for ids in [(q,q+1,q+66),(q,q+66,q+65)]:
     a,b,c=(vs[n] for n in ids)
     for k in range(9):
      for l in range(9-k):
       p=a+(b-a)*(k/8)+(c-a)*(l/8)
       if p.z>.60:continue
       hit,normal,idx,dist=bvh.ray_cast(Vector((p.x,-2,p.z)),Vector((0,1,0)),4)
       if hit is not None:
        clearance=min(clearance,100*(hit.y-p.y));samples+=1
 report['minimum_tub_clearance_cm'][str(w)]={'minimum':round(clearance,3),'triangle_samples':samples}
 assert clearance>=1,(w,clearance)
 # Every ring has invariant shape; its entire motion is translation on the straight rail.
 for k in range(7):
  ring=vs[4290+k*128:4290+(k+1)*128]
  assert abs(sum(v.y for v in ring)/128+.35)<1e-5
  assert abs(sum(v.z for v in ring)/128-2.17)<1e-5
  start=4290+k*128;basis_ring=[o.matrix_world@v.co for v in o.data.shape_keys.key_blocks['Basis'].data[start:start+128]]
  delta=ring[0]-basis_ring[0]
  assert all((v-b-delta).length<1e-5 for v,b in zip(ring,basis_ring))
report['ring_checks']='All 21 sampled poses: seven rigid tori, centre Y=-0.35m, Z=2.17m; linear translation only.'
report['corrective']='Closed=a; Closed_Mid=4*a*(1-a). Relative residual key, not absolute halfway pose.'
report['clearance_method']='Actual BA_Tub03_Body triangle BVH front surface at matching X/Z, both cloth layers, triangle barycentric subdivision 8, Z <= 60cm; rays outside tub silhouette excluded.'
report['mapping']='world_cm = (580 - 100*BlenderX, 907 + 100*BlenderY, 100*BlenderZ); includes FBX axis conversion and assembly yaw 180'

(D/'curtain-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
