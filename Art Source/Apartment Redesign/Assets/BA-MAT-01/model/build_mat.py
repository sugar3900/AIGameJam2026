import bpy, math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent.parent
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.unit_settings.system='METRIC'
scene.render.engine='CYCLES'; scene.cycles.samples=32
scene.render.resolution_x=1100;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=True
scene.world.color=(0.17,0.17,0.17)
scene.view_settings.view_transform='AgX'
mat=bpy.data.materials.new('Mat_Painterly_Woven_Cotton');mat.use_nodes=True
nodes=mat.node_tree.nodes; bs=nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.92
tex=nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(P/'textures/bath-mat-albedo.png'),check_existing=True)
mat.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
nx,ny=36,28
verts=[];faces=[]
for j in range(ny+1):
    v=j/ny; yy=2*v-1
    for i in range(nx+1):
        u=i/nx;xx=2*u-1
        x=.275*xx*math.sqrt(1-.10*abs(yy)**10)
        y=.2*yy*math.sqrt(1-.12*abs(xx)**10)
        # Restrained handmade boundary waviness, avoiding detached vertices.
        x+=.0011*math.sin(yy*math.pi*5)*abs(xx)**12
        y+=.0011*math.sin(xx*math.pi*6)*abs(yy)**12
        z=.0055+.0012*math.sin(3*math.pi*u)*math.sin(3*math.pi*v)
        verts.append((x,y,z))
for j in range(ny):
    for i in range(nx):
        a=j*(nx+1)+i;faces.append((a,a+1,a+nx+2,a+nx+1))
mesh=bpy.data.meshes.new('WovenMatMesh');mesh.from_pydata(verts,[],faces);mesh.update()
obj=bpy.data.objects.new('BA_Mat',mesh);bpy.context.collection.objects.link(obj);bpy.context.view_layer.objects.active=obj;obj.select_set(True)
uv=mesh.uv_layers.new(name='UVMap')
for poly in mesh.polygons:
    poly.use_smooth=True
    for li in poly.loop_indices:
        vi=mesh.loops[li].vertex_index;uv.data[li].uv=((vi%(nx+1))/nx,(vi//(nx+1))/ny)
obj.data.materials.append(mat)
sol=obj.modifiers.new('thin textile edge','SOLIDIFY');sol.thickness=.004;sol.offset=-1
bpy.ops.object.modifier_apply(modifier=sol.name)
bpy.ops.export_scene.fbx(filepath=str(P/'model/BA_Mat.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,axis_forward='-Z',axis_up='Y',add_leaf_bones=False,mesh_smooth_type='FACE')
# A preview-only floor is excluded from FBX.
bpy.ops.mesh.primitive_plane_add(size=3,location=(0,0,-.001));floor=bpy.context.object;floor.name='PREVIEW_ONLY_Floor'
fm=bpy.data.materials.new('PREVIEW_Floor');fm.diffuse_color=(.65,.54,.50,1);floor.data.materials.append(fm)
def point(obj, target):obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.light_add(type='AREA',location=(0,-1.6,2.7));light=bpy.context.object;light.data.energy=260;light.data.shape='DISK';light.data.size=2.3;point(light,(0,0,0))
bpy.ops.object.camera_add(location=(.82,-1.05,1.15));cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=.83;point(cam,(0,0,0));scene.camera=cam
scene.render.filepath=str(P/'previews/mat-perspective.png');bpy.ops.render.render(write_still=True)
cam.location=(0,0,2);point(cam,(0,0,0));cam.data.ortho_scale=.71
scene.render.filepath=str(P/'previews/mat-top.png');bpy.ops.render.render(write_still=True)
# Preserve a clean editable source with paths portable relative to this blend.
tex.image.filepath=bpy.path.relpath(str(P/'textures/bath-mat-albedo.png'),start=str(P/'model'))
bpy.ops.wm.save_as_mainfile(filepath=str(P/'model/BA-MAT-01.blend'))
