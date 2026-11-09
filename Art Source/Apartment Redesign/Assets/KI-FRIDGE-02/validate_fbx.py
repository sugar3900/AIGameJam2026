import bpy,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
meta=json.loads((ROOT/'models/manifest.json').read_text())
results=[]
for key in ('BODY','DOOR'):
 for o in list(bpy.data.objects):bpy.data.objects.remove(o,do_unlink=True)
 bpy.ops.import_scene.fbx(filepath=str(ROOT/'models'/f"{meta[key]['mesh']}.fbx"))
 render=[o for o in bpy.context.scene.objects if o.type=='MESH' and not o.name.startswith('UCX_')]
 hulls=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith('UCX_')]
 assert len(render)==1
 o=render[0];mesh=o.data;mesh.calc_loop_triangles()
 assert o.matrix_world.determinant()>0
 assert all(v>0 for v in o.scale)
 assert mesh.uv_layers
 assert all(math.isfinite(c) for v in mesh.vertices for c in v.co)
 assert all(math.isfinite(c) for p in mesh.polygons for c in p.normal)
 assert all(math.isfinite(c) for layer in mesh.uv_layers for uv in layer.data for c in uv.uv)
 assert all(t.area>=1e-10 for t in mesh.loop_triangles)
 pts=[o.matrix_world@v.co for v in mesh.vertices]
 lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
 assert max(abs(a-b) for a,b in zip(lo+hi,meta[key]['closed_bounds_min']+meta[key]['closed_bounds_max']))<1e-5
 assert (o.location-Vector(meta[key]['origin_m'])).length<1e-5
 assert len(hulls)==meta[key]['collision_hulls']
 for h in hulls:
  assert h.name.startswith('UCX_'+meta[key]['mesh']+'_')
  assert h.matrix_world.determinant()>0 and all(v>0 for v in h.scale)
  assert len(h.data.vertices)==8 and len(h.data.polygons)==6
  assert (h.location-o.location).length<1e-5
 results.append({'part':key,'vertices':len(mesh.vertices),'triangles':len(mesh.loop_triangles),'UV_layers':len(mesh.uv_layers),'collision_hulls':len(hulls),'origin_m':list(o.location),'determinant':o.matrix_world.determinant(),'scale':list(o.scale),'bounds_min':lo,'bounds_max':hi})
out={'status':'PASS','checks':['finite geometry/UV/normals','nonzero triangle areas','positive render and collision transforms','mirrored bounds','body and door hinge origins','named convex box UCX and shared pivot'],'parts':results,'limitations':'Source and Blender reimport validation only; Unreal hinge sign and material/collision import still require integration test.'}
(ROOT/'models/validation.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
