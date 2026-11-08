import bpy,math
from pathlib import Path
asset_model_path=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(asset_model_path/'ARC_Floor_Wood_2m.fbx'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']; assert len(meshes)==2
bad=degen=missing=verts=tris=0; bounds=[]; board=None; base=None
for o in meshes:
    missing+=not bool(o.data.uv_layers); verts+=len(o.data.vertices);o.data.calc_loop_triangles();tris+=len(o.data.loop_triangles)
    if 'floorboards' in o.name.lower(): board=o
    if 'subfloor' in o.name.lower(): base=o
    for v in o.data.vertices:
        co=o.matrix_world@v.co;bounds.append(co);bad+=not all(math.isfinite(x) for x in co)
    for p in o.data.polygons: degen+=p.area<1e-12
    for layer in o.data.uv_layers:
        for entry in layer.data: bad+=not all(math.isfinite(x) for x in entry.uv)
assert board is not None and base is not None
left=[];right=[];uv=board.data.uv_layers.active.data
for p in board.data.polygons:
    for li in p.loop_indices:
        co=board.matrix_world@board.data.vertices[board.data.loops[li].vertex_index].co
        item=(round(co.y,5),round(co.z,5),round(uv[li].uv.x,5),round(uv[li].uv.y,5),p.material_index)
        if abs(co.x+1)<1e-5:left.append(item)
        if abs(co.x-1)<1e-5:right.append(item)
assert sorted(left)==sorted(right), f'x-edge geometry/material/UV mismatch: {left} vs {right}'
# Y seams lie between distinct board rows. Check equal, intentional half-gaps
# on both module edges and continuous subfloor edge vertices rather than requiring
# unrelated boards to share their material or joint locations.
board_y=[(board.matrix_world@v.co).y for v in board.data.vertices]
assert abs(min(board_y)+.9985)<1e-5 and abs(max(board_y)-.9985)<1e-5
bottom=[];top=[]
for v in base.data.vertices:
    co=base.matrix_world@v.co; item=(round(co.x,5),round(co.z,5))
    if abs(co.y+1)<1e-5: bottom.append(item)
    if abs(co.y-1)<1e-5: top.append(item)
assert sorted(bottom)==sorted(top) and len(bottom)==4
print('VALIDATION y edges matching subfloor, board half-gap 0.0015m on both sides')
mn=[min(v[i] for v in bounds) for i in range(3)];mx=[max(v[i] for v in bounds) for i in range(3)]
print('VALIDATION meshes',len(meshes),'vertices',verts,'triangles',tris,'missing_uv',missing,'nonfinite',bad,'degenerate',degen)
print('VALIDATION bounds',mn,mx,'dimensions',[mx[i]-mn[i] for i in range(3)])
print('VALIDATION x module edge board endpoints match:',len(left),'per edge, material and UV included')
assert not (missing or bad or degen)

# The optional independent layer is a UV-mapped single plane with actual image alpha.
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(asset_model_path/'ARC_Floor_Wear_Optional.fbx'))
wear=[o for o in bpy.context.scene.objects if o.type=='MESH']; assert len(wear)==1 and wear[0].data.uv_layers
assert all(poly.area>1e-12 for poly in wear[0].data.polygons)
img=bpy.data.images.load(str(asset_model_path.parent/'textures'/'wear-candidate-b.png'),check_existing=True)
assert img.channels==4
alpha=img.pixels[3::4]; assert min(alpha)<.001 and max(alpha)>.01
print('VALIDATION optional wear UV plane and alpha range',min(alpha),max(alpha))
