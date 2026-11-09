import bpy, numpy as np, math
from pathlib import Path
A=Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(A/'model/KI_Wall_Stain.fbx'))
meshes=[x for x in bpy.context.scene.objects if x.type=='MESH'];assert len(meshes)==1
ob=meshes[0];assert ob.data.uv_layers; assert len(ob.data.polygons)==1
verts=np.array([tuple(v.co) for v in ob.data.vertices]); uv=np.array([tuple(x.uv) for x in ob.data.uv_layers.active.data]);assert np.isfinite(verts).all() and np.isfinite(uv).all()
assert all(p.area>1e-9 for p in ob.data.polygons)
dims=tuple(round(v,4) for v in ob.dimensions)
assert abs(sorted(dims)[1]-.47)<1e-3 and abs(sorted(dims)[2]-.70)<1e-3, dims
im=bpy.data.images.load(str(A/'textures/stain-candidate-b.png'));w,h=im.size;a=np.array(im.pixels[:]).reshape(h,w,4)[:,:,3]
edge=np.concatenate([a[0],a[-1],a[:,0],a[:,-1]]); assert edge.max()<.02, edge.max()
effective=np.clip((edge-.008)*1.25,0,1);assert effective.max()==0
print('PASS single mesh, UVs finite, nonzero area, dimensions',dims,'raw_edge_alpha_max',float(edge.max()),'effective_edge_alpha_max',float(effective.max()),'alpha_range',float(a.min()),float(a.max()))
