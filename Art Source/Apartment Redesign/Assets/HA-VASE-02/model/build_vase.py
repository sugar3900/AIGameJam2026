import bpy, math
from pathlib import Path
from mathutils import Vector
D=Path(__file__).resolve().parent.parent
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
scene.unit_settings.system='METRIC'
# Closed ceramic wall profile: exterior foot -> body -> flared lip -> hollow interior -> inner bottom.
profile=[(.048,.002),(.058,.003),(.064,.008),(.068,.016),(.074,.030),(.084,.052),(.094,.080),(.104,.110),(.110,.140),(.108,.163),(.101,.182),(.088,.199),(.075,.210),(.070,.220),(.070,.231),(.076,.243),(.086,.254),(.091,.262),(.090,.267),(.086,.270),(.080,.269),(.075,.266),(.071,.260),(.067,.253),(.064,.244),(.063,.232),(.064,.220),(.069,.209),(.082,.194),(.093,.178),(.099,.157),(.100,.138),(.095,.114),(.085,.085),(.075,.062),(.060,.045),(.040,.032),(.020,.027)]
N=96
verts=[]
for r,z in profile:
 for i in range(N):
  theta=2*math.pi*(i/N)-1.5*math.pi
  verts.append((r*math.cos(theta),r*(.18/.22)*math.sin(theta),z))
faces=[]
for j in range(len(profile)-1):
 for i in range(N):
  k=(i+1)%N;faces.append((j*N+i,j*N+k,(j+1)*N+k,(j+1)*N+i))
# Cap hidden foot and inner bottom with ngons.
faces.append(tuple(reversed(tuple(range(N)))))
faces.append(tuple((len(profile)-1)*N+i for i in range(N)))
mesh=bpy.data.meshes.new('Vase_Ceramic');mesh.from_pydata(verts,[],faces);mesh.update()
obj=bpy.data.objects.new('HA_VASE_02',mesh);scene.collection.objects.link(obj)
uv=mesh.uv_layers.new(name='VaseUV')
for j in range(len(profile)-1):
 for i in range(N):
  poly=mesh.polygons[j*N+i]; u0=i/N;u1=(i+1)/N
  # Image top corresponds to high Z, image center is the belly artwork.
  v0=profile[j][1]/.27;v1=profile[j+1][1]/.27
  for li,coords in zip(poly.loop_indices,((u0,v0),(u1,v0),(u1,v1),(u0,v1))):uv.data[li].uv=coords
for poly in list(mesh.polygons)[-2:]:
 for li in poly.loop_indices:
  v=mesh.vertices[mesh.loops[li].vertex_index].co
  uv.data[li].uv=(.5+v.x/.30,.5+v.y/.30)
for poly in mesh.polygons:poly.use_smooth=poly.index < (len(profile)-1)*N
mat=bpy.data.materials.new('Painted_Sage_Ceramic');mat.use_nodes=True
nodes=mat.node_tree.nodes;bsdf=nodes.get('Principled BSDF');bsdf.inputs['Roughness'].default_value=.48
tex=nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(D/'textures/sage-botanical.png'));tex.image.pack();mat.node_tree.links.new(tex.outputs['Color'],bsdf.inputs['Base Color']);obj.data.materials.append(mat)
# Warm studio camera and lighting.
world=bpy.data.worlds.new('Studio');scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.17,.16,.15,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.55

def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
def light(name,loc,power,size):
 data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size;o=bpy.data.objects.new(name,data);scene.collection.objects.link(o);o.location=loc;aim(o,(0,0,.13))
light('Key',(.45,-.7,1),18,.9);light('Fill',(-.7,-.25,.55),8,.7);light('Rim',(.3,.5,.7),12,.65)
camdata=bpy.data.cameras.new('Camera');cam=bpy.data.objects.new('Camera',camdata);scene.collection.objects.link(cam);cam.location=(.47,-.82,.55);aim(cam,(0,0,.13));camdata.type='ORTHO';camdata.ortho_scale=.42;scene.camera=cam
scene.render.engine='CYCLES';scene.cycles.samples=40
scene.render.resolution_x=1024;scene.render.resolution_y=1024;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=True
scene.view_settings.view_transform='AgX'
bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
bpy.ops.wm.save_as_mainfile(filepath=str(D/'model/HA-VASE-02.blend'))
bpy.ops.export_scene.fbx(filepath=str(D/'model/HA_VASE_02.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,add_leaf_bones=False,path_mode='AUTO')
scene.render.filepath=str(D/'previews/vase-three-quarter.png');bpy.ops.render.render(write_still=True)
cam.location=(0,-1,.29);aim(cam,(0,0,.13));scene.render.filepath=str(D/'previews/vase-front.png');bpy.ops.render.render(write_still=True)

# Compare the actual five exported flower material groups at the mouth datum.
flower_src=D.parent/'HA-FLOWERS-01/model/HA-FLOWERS-01.blend'
with bpy.data.libraries.load(str(flower_src),link=False) as (src,dst):
 dst.objects=[n for n in src.objects if n.startswith('Flowers_')]
for o in dst.objects:
 if o:
  scene.collection.objects.link(o); o.location=(0,0,.270)
cam.location=(.48,-.85,.60);aim(cam,(0,0,.24));camdata.ortho_scale=.70
scene.render.filepath=str(D/'previews/vase-with-flowers.png');bpy.ops.render.render(write_still=True)
