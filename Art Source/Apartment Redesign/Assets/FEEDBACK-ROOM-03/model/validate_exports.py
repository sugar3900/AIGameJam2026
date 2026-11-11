from pathlib import Path
import bpy,json,math
P=Path(__file__).resolve().parent.parent;A=P.parent
reports=[]
for path in list((P/'model').glob('*.fbx'))+list((A/'ARC-DOOR-03/model').glob('*.fbx')):
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.fbx(filepath=str(path))
 meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];render=[o for o in meshes if not o.name.startswith('UCX_')];hulls=[o for o in meshes if o.name.startswith('UCX_')]
 assert render,path
 assert all(all(math.isfinite(c) for c in v.co) for o in meshes for v in o.data.vertices),path
 assert all(o.data.uv_layers for o in render),path
 bounds=[[min((o.matrix_world@v.co)[i] for o in render for v in o.data.vertices) for i in range(3)],[max((o.matrix_world@v.co)[i] for o in render for v in o.data.vertices) for i in range(3)]]
 if path.name.startswith('Baseboard_'):
  assert abs(bounds[0][1]+.014)<1e-5 and abs(bounds[1][2]-.13)<1e-5,path
 if path.name=='ARC_Door03_Frame.fbx':assert len(hulls)==3
 if path.name=='ARC_Door03_Leaf.fbx':assert len(hulls)==1
 reports.append({'file':str(path.relative_to(A)),'meshes':len(render),'hulls':len(hulls),'UV0':'pass','bounds':bounds})
(P/'roundtrip-validation.json').write_text(json.dumps(reports,indent=2))
print('PASS',len(reports),'FBX files')
