import bpy, math
from mathutils import Vector
from pathlib import Path

P = Path(__file__).resolve().parent.parent
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for m in bpy.data.materials: bpy.data.materials.remove(m)
bpy.context.scene.render.engine='CYCLES'
bpy.context.scene.cycles.samples=48
bpy.context.scene.render.resolution_x=1200; bpy.context.scene.render.resolution_y=1000; bpy.context.scene.render.resolution_percentage=100
bpy.context.scene.render.image_settings.file_format='PNG'; bpy.context.scene.render.film_transparent=True
bpy.context.scene.view_settings.view_transform='AgX'

def mat(name,color,texture=None):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Roughness'].default_value=.92;b.inputs['Base Color'].default_value=(*color,1)
 if texture:
  n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=bpy.data.images.load(str(texture),check_existing=True);n.image.pack();m.node_tree.links.new(n.outputs['Color'],b.inputs['Base Color'])
 return m
ink=mat('Paper_painterly_written',(.85,.78,.65),P/'textures'/'paper-candidate-b.png')
postcard=mat('Postcard_painterly_sepia',(.83,.72,.57),P/'textures'/'paper-candidate-a.png')
plain=mat('Paper_clean_reverse',(.73,.67,.56))
deskmat=mat('Preview_desk',(.24,.14,.08))

# Each sheet is a curved thin mesh with modeled top and underside. UVs are
# normalized per sheet; the same generated color source is reused with distinct placement.
def sheet(name,w,h,cx,cy,z,angle,curve,phase,material):
 nx,ny=12,14; verts=[]; faces=[]
 for side in (0,1):
  for j in range(ny+1):
   v=j/ny
   for i in range(nx+1):
    u=i/nx; x=(u-.5)*w; y=(v-.5)*h
    edge=max(0.,abs(u-.5)*2-.72)*max(0.,abs(v-.5)*2-.72)
    wave=.00065*math.sin(u*math.pi*2+phase)*math.sin(v*math.pi)+curve*edge*edge
    # Rotate the paper within its tabletop XY plane.
    a=math.radians(angle); X=cx+x*math.cos(a)-y*math.sin(a); Y=cy+x*math.sin(a)+y*math.cos(a)
    verts.append((X,Y,z+wave-side*.00035))
 N=(nx+1)*(ny+1)
 for j in range(ny):
  for i in range(nx):
   k=j*(nx+1)+i;faces.append((k,k+1,k+nx+2,k+nx+1));faces.append((N+k+nx+1,N+k+nx+2,N+k+1,N+k))
 # Connect perimeter; preserve thin but finite thickness.
 boundary=[i for i in range(nx+1)]+[j*(nx+1)+nx for j in range(1,ny+1)]+[ny*(nx+1)+i for i in range(nx-1,-1,-1)]+[j*(nx+1) for j in range(ny-1,0,-1)]
 for k in range(len(boundary)):
  a=boundary[k];b=boundary[(k+1)%len(boundary)];faces.append((a,N+a,N+b,b))
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o)
 mesh.materials.append(material);mesh.materials.append(plain);uv=mesh.uv_layers.new(name='UVMap')
 for poly in mesh.polygons:
  poly.material_index=0 if poly.index<2*nx*ny and poly.index%2==0 else 1
  for corner,li in enumerate(poly.loop_indices):
   vi=mesh.loops[li].vertex_index%N;i=vi%(nx+1);j=vi//(nx+1)
   uv.data[li].uv=((0,0),(0,.01),(1,.01),(1,0))[corner] if poly.index>=2*nx*ny else (i/nx,j/ny)
 for p in mesh.polygons: p.use_smooth=True
 return o

papers=[
 sheet('Bottom_sheet',.205,.255,-.012,.002,.001, -7,.023,0.1,plain),
 sheet('Second_sheet',.195,.245,.012,-.002,.0021, 6,.020,1.5,plain),
 sheet('Written_page',.192,.250,-.004,.004,.0033,-2,.024,2.8,ink),
 sheet('Small_letter',.132,.160,.058,-.025,.0050,12,.020,1.0,ink),
 sheet('Postcard',.105,.070,.065,-.075,.0064,-9,.014,3.2,postcard),
]
# Save only asset geometry in master; preview environment is deliberately separate.
scene=bpy.context.scene
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
bpy.ops.object.select_all(action='DESELECT')
for o in papers:o.select_set(True)
bpy.context.view_layer.objects.active=papers[0]
bpy.ops.wm.save_as_mainfile(filepath=str(P/'model'/'OF-PAPERS-01.blend'))
bpy.ops.export_scene.fbx(filepath=str(P/'model'/'OF_PAPERS_01.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Y',axis_up='Z',apply_unit_scale=True,bake_anim=False,add_leaf_bones=False)
# Show a desk-colored support only in the studio image.
bpy.ops.mesh.primitive_plane_add(size=2,location=(0,0,-.0008));desk=bpy.context.object;desk.name='PREVIEW_ONLY_desk';desk.data.materials.append(deskmat)
world=bpy.data.worlds.new('Studio') if not bpy.data.worlds else bpy.data.worlds[0];scene.world=world;world.color=(.10,.10,.10)
def area(name,loc,power,size):
 data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size;o=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,0))-o.location).to_track_quat('-Z','Y').to_euler()
area('Key',(0.2,-0.5,1.4),14,1.3);area('Fill',(-.8,.5,1),7,1)
camdata=bpy.data.cameras.new('Camera');cam=bpy.data.objects.new('Camera',camdata);bpy.context.collection.objects.link(cam);scene.camera=cam
cam.location=(.58,-.78,.86);cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler();camdata.type='ORTHO';camdata.ortho_scale=.43
scene.render.filepath=str(P/'previews'/'papers-perspective.png');bpy.ops.render.render(write_still=True)
cam.location=(0,0,1.2);cam.rotation_euler=(0,0,0);cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler();camdata.ortho_scale=.39
scene.render.filepath=str(P/'previews'/'papers-top.png');bpy.ops.render.render(write_still=True)
