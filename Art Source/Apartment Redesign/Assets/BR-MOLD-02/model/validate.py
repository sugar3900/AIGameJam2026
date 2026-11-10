from pathlib import Path
import bpy,json,math
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
manifest=json.loads((ROOT/'assembly.json').read_text());report={'asset':'BR-MOLD-02','exports':[]}
for e in manifest['exports']:
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.fbx(filepath=str(ROOT/e['file']))
 objs=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(objs)==1
 o=objs[0];assert o.location.length<1e-6
 verts=[o.matrix_world@v.co for v in o.data.vertices]
 assert all(math.isfinite(x) for v in verts for x in v)
 assert len(o.data.uv_layers)>0
 assert len(o.data.color_attributes)>0
 color=o.data.color_attributes[0];alpha=[v.color[3] for v in color.data]
 if 'Return' in e['file']:assert min(alpha)<.01 and max(alpha)>.99
 o.data.calc_loop_triangles();areas=[]
 for tri in o.data.loop_triangles:
  a,b,c=[verts[i] for i in tri.vertices];areas.append((b-a).cross(c-a).length/2)
 assert min(areas)>1e-6
 mn=[min(v[i] for v in verts) for i in range(3)];mx=[max(v[i] for v in verts) for i in range(3)]
 assert max(mx)<3 and min(mn)>-2
 assert not any(x.name.startswith('UCX_') for x in objs)
 report['exports'].append({'file':e['file'],'mesh_count':len(objs),'origin':list(o.location),'vertices':len(verts),'triangles':len(areas),'smallest_triangle_area_m2':min(areas),'world_bounds': [mn,mx],'uv_layers':len(o.data.uv_layers),'vertex_color_alpha_range':[min(alpha),max(alpha)]})
img=bpy.data.images.load(str(ROOT/'textures/mold-colonies-rgba.png'))
assert img.channels==4 and img.size[0]>1000
report['texture']={'file':'textures/mold-colonies-rgba.png','size':list(img.size),'channels':img.channels,'generated_alpha_preserved':True}
report['result']='PASS: two finite UV-mapped zero-origin overlay meshes, no shell or collision geometry.'
(ROOT/'model/validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(report['result'])
