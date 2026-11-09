import bpy, math, random
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parent.parent
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
image=bpy.data.images.load(str(BASE/'textures'/'wood-candidate-c.png'), check_existing=True); image.filepath='//../textures/wood-candidate-c.png'

def woodmat(name,tint):
    m=bpy.data.materials.new(name); m.use_nodes=True; bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Roughness'].default_value=.88
    tex=m.node_tree.nodes.new('ShaderNodeTexImage'); tex.image=image; tex.extension='EXTEND'
    mix=m.node_tree.nodes.new('ShaderNodeMixRGB'); mix.blend_type='MULTIPLY'; mix.inputs[0].default_value=1; mix.inputs[2].default_value=(*tint,1)
    m.node_tree.links.new(tex.outputs['Color'],mix.inputs[1]); m.node_tree.links.new(mix.outputs['Color'],bs.inputs['Base Color']); return m
mats=[woodmat('Wood tone %d'%i,t) for i,t in enumerate([(1.03,1.0,.96),(.72,.75,.76),(.90,.84,.77),(.79,.83,.85),(.98,.88,.77),(.84,.86,.82)])]
dark=bpy.data.materials.new('Shadow between planks'); dark.diffuse_color=(.095,.047,.019,1); dark.use_nodes=True; dark.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=dark.diffuse_color; dark.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.93
verts=[]; faces=[]; faceuv=[]; material_ids=[]
def quad(xa,xb,ya,yb,uv,mat):
    i=len(verts); verts.extend([(xa,ya,0),(xb,ya,0),(xb,yb,0),(xa,yb,0)]); faces.append((i,i+1,i+2,i+3)); faceuv.append(uv); material_ids.append(mat)
def tri_u(x): return 1-abs(x)
# 16 rows, 0.125m wide. Joint offsets repeat exactly at the 2m module boundary.
for row in range(16):
    y0=-1+row*.125+.0015; y1=-1+(row+1)*.125-.0015
    offset=(row%4)*.25; board_breaks=[-1]+[offset+k for k in range(-3,4) if -1+1e-7<offset+k<1-1e-7]+[1]
    for a,b in zip(board_breaks[:-1],board_breaks[1:]):
        # Apply half-gap at a joint, including module boundaries where a joint falls.
        isjoint=lambda x: abs((x-offset)-round(x-offset))<1e-6
        left=a+(.0012 if isjoint(a) else 0); right=b-(.0012 if isjoint(b) else 0)
        board_index=math.floor(((a+b)*.5-offset)+1e-6)
        shade=((row*17+(board_index%2)*7)%6)
        points=[left]+([0] if left<0<right else [])+[right]
        # same two edge UVs in each row ensure exact material continuity across module edges.
        v0=.02+((row*3)%11)*.07; v1=v0+.20
        for x0,x1 in zip(points[:-1],points[1:]):
            quad(x0,x1,y0,y1,[(tri_u(x0),v0),(tri_u(x1),v0),(tri_u(x1),v1),(tri_u(x0),v1)],shade)
mesh=bpy.data.meshes.new('Floorboards module mesh'); mesh.from_pydata(verts,[],faces); mesh.update(); obj=bpy.data.objects.new('Wood floorboards 2m module',mesh); bpy.context.collection.objects.link(obj)
for m in mats: obj.data.materials.append(m)
uv=mesh.uv_layers.new(name='UVMap')
for i,p in enumerate(mesh.polygons):
    p.material_index=material_ids[i]
    for k,li in enumerate(p.loop_indices): uv.data[li].uv=faceuv[i][k]
# Continuous narrow subfloor fills joints; this also gives a simple collision surface.
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,-.016)); base=bpy.context.object; base.name='Continuous subfloor'; base.dimensions=(2,2,.026); bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); base.data.materials.append(dark)
production=[obj,base]; bpy.ops.object.select_all(action='DESELECT')
for o in production:o.select_set(True)
bpy.context.view_layer.objects.active=obj
bpy.ops.export_scene.fbx(filepath=str(BASE/'model'/'ARC_Floor_Wood_2m.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,add_leaf_bones=False,mesh_smooth_type='FACE',path_mode='AUTO')
# The editable source shows one module; duplicate only for repeat test render.
scene=bpy.context.scene; world=scene.world; world.color=(.16,.16,.16)
for x,y in [(2,0),(0,2),(2,2)]:
    for orig in production:
        dup=orig.copy(); dup.data=orig.data; bpy.context.collection.objects.link(dup); dup.location.x+=x; dup.location.y+=y; dup.name='PREVIEW repeat '+orig.name
# Optional wear is a separate asset, not built into the 2 m repeated tile.
wear_image=bpy.data.images.load(str(BASE/'textures'/'wear-candidate-b.png'),check_existing=True); wear_image.filepath='//../textures/wear-candidate-b.png'
wear=bpy.data.materials.new('Optional painterly worn finish'); wear.use_nodes=True; wear.surface_render_method='DITHERED'
wbs=wear.node_tree.nodes.get('Principled BSDF'); wbs.inputs['Roughness'].default_value=.95
wt=wear.node_tree.nodes.new('ShaderNodeTexImage'); wt.image=wear_image; wt.extension='CLIP'
opacity=wear.node_tree.nodes.new('ShaderNodeMath'); opacity.operation='MULTIPLY'; opacity.inputs[1].default_value=.22
wear.node_tree.links.new(wt.outputs['Color'],wbs.inputs['Base Color']); wear.node_tree.links.new(wt.outputs['Alpha'],opacity.inputs[0]); wear.node_tree.links.new(opacity.outputs[0],wbs.inputs['Alpha'])
bpy.ops.mesh.primitive_plane_add(size=1,location=(0,0,0)); decal=bpy.context.object; decal.name='Optional wear layer 0.9m'; decal.dimensions=(.9,.6,0); bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); decal.data.materials.append(wear)
bpy.ops.object.select_all(action='DESELECT'); decal.select_set(True); bpy.context.view_layer.objects.active=decal
bpy.ops.export_scene.fbx(filepath=str(BASE/'model'/'ARC_Floor_Wear_Optional.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,add_leaf_bones=False,path_mode='AUTO')
# These instances intentionally do not follow the two-metre tile cadence.
decal.location=(.2,-.35,.001)
for x,y,scale,rotation in [(1.55,1.35,1.2,.23),(2.55,.18,.7,-.11),(2.3,2.6,.8,.1)]:
    du=decal.copy(); du.data=decal.data; bpy.context.collection.objects.link(du); du.name='PREVIEW wear varied'; du.location=(x,y,.001); du.scale=(scale,scale,scale); du.rotation_euler.z=rotation
ld=bpy.data.lights.new('Large soft light','AREA'); ld.energy=450; ld.shape='DISK'; ld.size=7
lo=bpy.data.objects.new('Large soft light',ld); bpy.context.collection.objects.link(lo); lo.location=(0,-1,6); lo.rotation_euler=(Vector((1,1,0))-lo.location).to_track_quat('-Z','Y').to_euler()
camdata=bpy.data.cameras.new('Camera'); cam=bpy.data.objects.new('Camera',camdata); bpy.context.collection.objects.link(cam); cam.location=(1,1,10); cam.rotation_euler=(Vector((1,1,0))-cam.location).to_track_quat('-Z','Y').to_euler(); camdata.type='ORTHO'; camdata.ortho_scale=4.26; scene.camera=cam
scene.render.engine='CYCLES'; scene.cycles.samples=24; scene.render.resolution_x=1200; scene.render.resolution_y=1200; scene.render.resolution_percentage=100; scene.render.film_transparent=True; scene.render.image_settings.file_format='PNG'; scene.view_settings.view_transform='AgX'; scene.render.filepath=str(BASE/'previews'/'floor-repeat-top.png')
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'model'/'ARC-FLOOR-WOOD-01.blend'))
bpy.ops.render.render(write_still=True)
cam.location=(5,-6,8); cam.rotation_euler=(Vector((1,1,0))-cam.location).to_track_quat('-Z','Y').to_euler(); camdata.ortho_scale=5.4; scene.render.filepath=str(BASE/'previews'/'floor-repeat-perspective.png'); bpy.ops.render.render(write_still=True)
