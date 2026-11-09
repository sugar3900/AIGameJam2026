"""Read-only source FBX assembly check at approved transforms; writes only own report."""
import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
meshes={}
for path in sorted((ROOT/'model').glob('ARC_Window_Kitchen_*.fbx')):
 before=set(bpy.context.scene.objects);bpy.ops.import_scene.fbx(filepath=str(path))
 for o in set(bpy.context.scene.objects)-before:
  if o.type!='MESH' or o.name.startswith('UCX_'):continue
  o.location.z+=1.25;meshes[o.name]=o
before=set(bpy.context.scene.objects)
bpy.ops.import_scene.fbx(filepath=str(ROOT.parent/'KI-SINK-NARROW-01/models/KI_SINK_NARROW_body.fbx'))
sink=[o for o in set(bpy.context.scene.objects)-before if o.type=='MESH'][0]
# Both fronts -Y. Sink footprint y=.15..80 corresponds to local Y=-.80..-.15.
bpy.context.view_layer.update()
pts=[sink.matrix_world@v.co for v in sink.data.vertices];ymax=max(v.y for v in pts)
sink.location.y+=-.15-ymax
bpy.context.view_layer.update()
def bvh(o):
 return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons])
sinktree=bvh(sink);checks=[]
for rise in (0,.12,.24,.36,.48):
 for name,o in meshes.items():
  o.location.z=1.25+(rise if 'lower' in name else 0)
 bpy.context.view_layer.update()
 hits={name:len(sinktree.overlap(bvh(o))) for name,o in meshes.items()}
 assert not any(hits.values()),(rise,hits)
 checks.append({'lower_sash_rise_m':rise,'intersecting_triangle_pairs':hits})
pts=[sink.matrix_world@v.co for v in sink.data.vertices];high=[v for v in pts if v.z>=1.18]
out={'status':'PASS','sink_placement_y':sink.location.y,'sink_source_front':'-Y','sink_northmost_y':max(v.y for v in pts),'faucet_northmost_above_apron_y':max(v.y for v in high),'window_sill_front_y':-.17,'faucet_to_sill_depth_gap_m':-.17-max(v.y for v in high),'checks':checks,'limitations':'Mesh-surface intersection check only; excludes room shell, player, individual tap controls and engine collision inflation.'}
(ROOT/'model/sink-fit-validation.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
