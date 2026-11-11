"""Repair thin painted edge UVs; all front crops and geometry remain unchanged."""
from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
R=Path(__file__).resolve().parent
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.open_mainfile(filepath=str(R/'models/Pantry03.blend'))
result={}
for side in ['L','R']:
 name='KI_Pantry03_'+('LeftDoor' if side=='L' else 'RightDoor')
 obj=bpy.data.objects[name];pv=obj.location.copy();uv=obj.data.uv_layers.active
 paint=next(i for i,m in enumerate(obj.data.materials) if m.name=='Joinery_Sage')
 u0,u1=(.08,.28) if side=='L' else (.64,.84)
 count=0
 for f in obj.data.polygons:
  if f.material_index!=paint:continue
  nx,ny,nz=map(abs,f.normal)
  if ny>=max(nx,nz):continue
  for li in f.loop_indices:
   v=obj.data.vertices[obj.data.loops[li].vertex_index].co+pv
   xn=(v.x+.462)/.460 if side=='L' else (v.x-.002)/.460
   zn=(v.z-.195)/1.650
   if nx>max(ny,nz):
    u=u0+.02+.10*(v.y+.36)/.10;vt=.05+.90*zn if side=='L' else .95-.90*zn
   else:u=u0+(u1-u0)*xn;vt=.35+.10*(v.y+.36)/.10
   uv.data[li].uv=(u,vt)
  count+=1
 obj.data.calc_loop_triangles()
 for t in obj.data.loop_triangles:
  if obj.data.polygons[t.polygon_index].material_index!=paint:continue
  a,b,c=[uv.data[i].uv for i in t.loops]
  assert abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))>1e-12,(side,t.index)
 hull=bpy.data.objects['UCX_'+name+'_00'];hl=hull.location.copy()
 obj.location=(0,0,0);hull.location=(0,0,0)
 bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);hull.select_set(True);bpy.context.view_layer.objects.active=obj
 bpy.ops.export_scene.fbx(filepath=str(R/'models'/(name+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,add_leaf_bones=False,axis_forward='-Z',axis_up='Y',path_mode='RELATIVE')
 obj.location=pv;hull.location=hl
 result[side]={'edge_faces_fixed':count,'collapsed_painted_uv_triangles':0,'geometry_front_uvs_unchanged':True}
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/Pantry03.blend'))
(R/'edge-uv-validation.json').write_text(json.dumps(result,indent=2)+'\n')
(R/'file-manifest.json').write_text(json.dumps({str(f.relative_to(R)):hashlib.sha256(f.read_bytes()).hexdigest() for d in ['models','textures'] for f in sorted((R/d).iterdir()) if f.suffix in ['.fbx','.png']},indent=2)+'\n')
print('PANTRY EDGE UV PASS',result)
