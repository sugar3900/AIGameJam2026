"""Validate exported plaster surface by FBX round-trip in Blender."""
import bpy,math,os
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
p=os.path.join(os.path.dirname(os.path.abspath(__file__)),'ARC_Bedroom_UpperPlaster_2m.fbx');bpy.ops.import_scene.fbx(filepath=p)
objs=[o for o in bpy.context.selected_objects if o.type=='MESH'];assert len(objs)==1
ob=objs[0];me=ob.data;me.calc_loop_triangles();assert me.uv_layers.active and len(me.loop_triangles)>0
points=[ob.matrix_world@v.co for v in me.vertices];mins=[min(v[i] for v in points) for i in range(3)];maxs=[max(v[i] for v in points) for i in range(3)]
assert all(math.isfinite(c) for p in points for c in p)
for tri in me.loop_triangles:
 a,b,c=(points[i] for i in tri.vertices);assert (b-a).cross(c-a).length>1e-8
 u=[me.uv_layers.active.data[i].uv for i in tri.loops];assert all(math.isfinite(v) for t in u for v in t);assert abs((u[1].x-u[0].x)*(u[2].y-u[0].y)-(u[1].y-u[0].y)*(u[2].x-u[0].x))>1e-8
assert ((points[1]-points[0]).cross(points[2]-points[0])).normalized().y < -0.99, 'surface must face -Y'
assert abs((maxs[0]-mins[0])-2)<.001 and abs((maxs[2]-mins[2])-1.65)<.001 and abs(mins[2]-1.1)<.001
print('PASS bounds:',mins,maxs,'triangles:',len(me.loop_triangles),'uv:',len(me.uv_layers.active.data))
