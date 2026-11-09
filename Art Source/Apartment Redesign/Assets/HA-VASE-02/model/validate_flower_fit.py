import bpy
from pathlib import Path
from mathutils.bvhtree import BVHTree
D=Path(__file__).resolve().parent.parent
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(D/'model/HA_VASE_02.fbx'))
vase=[o for o in bpy.context.scene.objects if o.type=='MESH'][0]
vase_tree=BVHTree.FromObject(vase,bpy.context.evaluated_depsgraph_get())
before=set(bpy.context.scene.objects)
bpy.ops.import_scene.fbx(filepath=str(D.parent/'HA-FLOWERS-01/model/HA_FLOWERS_01.fbx'))
flowers=[o for o in bpy.context.scene.objects if o not in before and o.type=='MESH']
assert flowers
for o in flowers:o.location.z+=.27
bpy.context.view_layer.update()
for o in flowers:
 # FromPolygons applies full object transform into the common scene space.
 mesh=o.data
 vertices=[o.matrix_world@v.co for v in mesh.vertices]
 polygons=[list(p.vertices) for p in mesh.polygons]
 tree=BVHTree.FromPolygons(vertices,polygons)
 overlaps=vase_tree.overlap(tree)
 assert not overlaps, f'{o.name}: {len(overlaps)} intersects vase'
print('PASS flower groups:',len(flowers),'mouth datum z=0.270m; no triangle intersections with vase')
