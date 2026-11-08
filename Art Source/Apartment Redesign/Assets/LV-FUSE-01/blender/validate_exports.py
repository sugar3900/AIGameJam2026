"""Run blender -b --python validate_exports.py; fails on invalid FBX geometry."""
import bpy, os, math
P=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'exports'))
for fn in sorted(x for x in os.listdir(P) if x.endswith('.fbx')):
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.fbx(filepath=os.path.join(P, fn))
    meshes=[o for o in bpy.context.selected_objects if o.type=='MESH']
    if len(meshes)!=1: raise RuntimeError(fn+' must contain exactly one mesh')
    o=meshes[0]; d=o.data
    bad=sum(not all(math.isfinite(c) for c in v.co) for v in d.vertices)
    deg=sum(p.area < 1e-12 for p in d.polygons)
    uv=sum(not all(math.isfinite(c) for c in l.uv) for layer in d.uv_layers for l in layer.data)
    if bad or deg or uv or not d.uv_layers: raise RuntimeError(f'{fn}: bad vertices={bad}, zero faces={deg}, bad UVs={uv}')
    print('PASS',fn,'verts',len(d.vertices),'faces',len(d.polygons),'dims_m',tuple(round(v,4) for v in o.dimensions),'origin',tuple(round(v,4) for v in o.location))
