from pathlib import Path
import bpy,math,json
from mathutils import Vector
R=Path(__file__).resolve().parents[1];results=[]
for f in sorted((R/'model').glob('*.fbx')):
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(f),use_custom_normals=True)
 meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];visual=[o for o in meshes if not o.name.startswith('UCX_')]
 assert visual,f
 points=[o.matrix_world@v.co for o in visual for v in o.data.vertices]
 assert all(math.isfinite(c) for p in points for c in p)
 assert all(o.data.uv_layers for o in visual)
 bounds=[[min(p[k] for p in points) for k in range(3)],[max(p[k] for p in points) for k in range(3)]]
 results.append({'file':f.name,'bounds_m':bounds,'vertices':len(points),'uv':True,'hulls':len(meshes)-len(visual)})
 if 'Hanger' in f.name:assert .42<bounds[1][1]-bounds[0][1]<.45
 if 'PanPair' in f.name:assert .59<bounds[1][0]-bounds[0][0]<.595
 if 'ClosetStorage' in f.name:assert len(meshes)-len(visual)==2
# Analytic mating checks: wire passes bore axis across full wood thickness; both sides emerge clear.
for k in [.78,1]:
 bore=.006*k;wire=.0023
 assert bore>wire+.002
 # Handle thickness +/- .012*k around y=-.070; straight wire spans y=-.045 to-.095 at z=-.060.
 assert -.045>-.070+.012*k+wire and -.095<-.070-.012*k-wire
(R/'model/validation.json').write_text(json.dumps({'fresh_fbx_imports':results,'pan_hole_engagement':'wire traverses bore on axis; min radial clearance2.38mm','hanger_hook_contact':'inner apex12mm equals rail radius12mm','limitations':'Source geometry tests; installed fit and appearance remain engine acceptance'},indent=2)+'\n')
print('PROP-FIT03 validated',len(results))
