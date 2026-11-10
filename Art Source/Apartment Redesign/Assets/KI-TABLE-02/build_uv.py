"""FIX035: apron UV relayout only; preserve every geometry face and all other UVs."""
from pathlib import Path
import bpy,json,shutil,collections
from mathutils import Vector
R=Path(__file__).resolve().parent;OLD=R.parent/'KI-TABLE-01';bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(OLD/'model/KI_TABLE_01.fbx'));o=next(o for o in bpy.context.scene.objects if o.type=='MESH' and not o.name.startswith('UCX_'));bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
slot=next(i for i,m in enumerate(o.data.materials) if m.name=='Table_Sage_Painted');uv=o.data.uv_layers.active.data

def record(obj,exclude_uv_slot=None):
 result=[];u=obj.data.uv_layers.active.data
 for p in obj.data.polygons:
  corners=[]
  for li in p.loop_indices:
   v=obj.matrix_world@obj.data.vertices[obj.data.loops[li].vertex_index].co;corner=tuple(float(x) for x in v)
   if p.material_index!=exclude_uv_slot:corner+=tuple(float(x) for x in u[li].uv)
   corners.append(corner)
  result.append((p.material_index,tuple(sorted(corners))))
 return collections.Counter(result)
before=record(o,slot)
# Find connected apron boards, welding FBX split-normal vertices only by exact positions.
parents={};vkey={}
def root(k):
 parents.setdefault(k,k)
 if parents[k]!=k:parents[k]=root(parents[k])
 return parents[k]
for p in o.data.polygons:
 if p.material_index!=slot:continue
 keys=[tuple(round(x,6) for x in o.data.vertices[i].co) for i in p.vertices]
 for k in keys:parents[root(k)]=root(keys[0])
groups={}
for p in o.data.polygons:
 if p.material_index==slot:
  key=root(tuple(round(x,6) for x in o.data.vertices[p.vertices[0]].co));groups.setdefault(key,[]).append(p)
assert len(groups)==4,len(groups)
reports=[]
for polys in groups.values():
 verts=[o.data.vertices[i].co for p in polys for i in p.vertices];span=[max(v[i] for v in verts)-min(v[i] for v in verts) for i in range(3)];axis=0 if span[0]>span[1] else 1
 for p in polys:
  for li in p.loop_indices:
   v=o.data.vertices[o.data.loops[li].vertex_index].co;uv[li].uv=((v[axis]+1.5)/3.0,(v.z-.60)/1.7+.45)
 reports.append({'length_axis':'XY'[axis],'length_m':span[axis],'length_m_per_U':3.0,'height_m_per_V':1.7,'faces':len(polys)})
assert record(o,slot)==before
# Source preview uses the same wood image on the apron; engine preserves its installed wood material.
tex=R/'textures/table-wood-v2.png';shutil.copyfile(OLD/'textures/table-wood-v2.png',tex)
for m in o.data.materials:
 if not m.use_nodes:continue
 for n in m.node_tree.nodes:
  if n.type=='TEX_IMAGE':n.image=bpy.data.images.load(str(tex),check_existing=True);n.image.pack()
o.name='KI_TABLE_02';bpy.ops.export_scene.fbx(filepath=str(R/'models/KI_TABLE_02.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',add_leaf_bones=False,path_mode='RELATIVE')
# Read the actual exported FBX in a clean scene and compare geometry plus every non-apron UV.
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(R/'models/KI_TABLE_02.fbx'));o=next(o for o in bpy.context.scene.objects if o.type=='MESH');after=record(o,slot)
remaining=list(after.elements());max_error=0.0
for material,corners in before.elements():
 match=None
 for index,(m,other) in enumerate(remaining):
  if material!=m or len(corners)!=len(other):continue
  # Every face corner must match position and any protected UV within tolerance.
  err=max(min(max(abs(a-b) for a,b in zip(c,d)) for d in other) for c in corners)
  if err<1e-6:match=index;max_error=max(max_error,err);break
 assert match is not None,('Unmatched face',material,corners)
 remaining.pop(match)
assert not remaining
# Reimported materials lose image paths in some FBX versions; repair for source preview only.
for m in o.data.materials:
 if not m.use_nodes:continue
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.8
 for n in m.node_tree.nodes:
  if n.type=='TEX_IMAGE':n.image=bpy.data.images.load(str(tex),check_existing=True)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=16;s.render.threads_mode='FIXED';s.render.threads=1;s.render.resolution_x=1000;s.render.resolution_y=800;s.render.resolution_percentage=100;s.world=bpy.data.worlds.new('Neutral studio');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.18,.18,.18,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.5
bpy.ops.object.light_add(type='AREA',location=(1,-3,3));l=bpy.context.object;l.data.energy=180;l.data.size=3;l.rotation_euler=(Vector((0,0,.5))-l.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(1.8,-2.6,1.05));c=bpy.context.object;c.data.type='ORTHO';c.data.ortho_scale=1.85;c.rotation_euler=(Vector((0,0,.43))-c.location).to_track_quat('-Z','Y').to_euler();s.camera=c;s.render.image_settings.file_format='PNG';s.render.filepath=str(R/'previews/apron-continuous.png');bpy.ops.render.render(write_still=True)
(R/'validation.json').write_text(json.dumps({'passed':True,'geometry_faces_unchanged':True,'non_apron_uvs_unchanged':True,'fresh_fbx_roundtrip_unchanged':True,'maximum_position_or_protected_uv_error':max_error,'tolerance':1e-6,'boards':reports,'limits':'Engine must retain installed collision and materials; use identity UV on apron slot, no former UV swap/scale.'},indent=2)+'\n')
print('TABLE UV RELEASE VALIDATED')
