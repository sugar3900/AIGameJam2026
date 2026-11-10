from pathlib import Path
import bpy, math, json, sys
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT.parent/'BR-CLOSET-02/model/BR-CLOSET-02.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
bpy.context.preferences.filepaths.save_version=0
sc=bpy.context.scene
sc.render.resolution_x=1200;sc.render.resolution_y=1000;sc.render.resolution_percentage=100
sc.cycles.samples=32
# Existing closet is preview-only; original mold hidden. Export only new two-plane overlay.
old=[o for o in sc.objects if o.name.startswith('Mold decal')]
for o in old:o.hide_render=True
mat=bpy.data.materials.new('Mold02_Neutral_Charcoal');mat.use_nodes=True
n=mat.node_tree.nodes;l=mat.node_tree.links;p=n.get('Principled BSDF')
p.inputs['Base Color'].default_value=(.022,.021,.020,1)
p.inputs['Roughness'].default_value=1;p.inputs['Metallic'].default_value=0;p.inputs['Specular IOR Level'].default_value=0
tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(ROOT/'textures/mold-colonies-rgba.png'));tex.image.colorspace_settings.name='Non-Color';tex.image.pack();tex.extension='EXTEND'
bw=n.new('ShaderNodeRGBToBW');l.new(tex.outputs['Color'],bw.inputs[0])
# Texture's pale charcoal wash must remain transparent. Dark pigment alone carries coverage.
remap=n.new('ShaderNodeMapRange');remap.clamp=True
remap.inputs['From Min'].default_value=.18;remap.inputs['From Max'].default_value=.56
remap.inputs['To Min'].default_value=1;remap.inputs['To Max'].default_value=0
l.new(bw.outputs[0],remap.inputs['Value'])
power=n.new('ShaderNodeMath');power.operation='POWER';power.inputs[1].default_value=1.35;l.new(remap.outputs['Result'],power.inputs[0])
mult=n.new('ShaderNodeMath');mult.operation='MULTIPLY';l.new(tex.outputs['Alpha'],mult.inputs[0]);l.new(power.outputs[0],mult.inputs[1]);l.new(mult.outputs[0],p.inputs['Alpha'])
edge=n.new('ShaderNodeVertexColor');edge.layer_name='MoldEdge'
fade=n.new('ShaderNodeMath');fade.operation='MULTIPLY';l.new(mult.outputs[0],fade.inputs[0]);l.new(edge.outputs['Alpha'],fade.inputs[1]);l.new(fade.outputs[0],p.inputs['Alpha'])
new=[]
def plane(name,verts,uv,faces=None,alphas=None):
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces or [(0,1,2,3)]);mesh.update()
 o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);o.data.materials.append(mat)
 layer=mesh.uv_layers.new(name='UVMap')
 for loop in mesh.loops:layer.data[loop.index].uv=uv[loop.vertex_index]
 color=mesh.color_attributes.new(name='MoldEdge',type='FLOAT_COLOR',domain='CORNER')
 for loop in mesh.loops:color.data[loop.index].color=(1,1,1,(alphas or [1]*len(verts))[loop.vertex_index])
 new.append(o);return o
plane('BR_Mold02_Back',[(-.55,.837,1.12),(1.037,.837,1.12),(1.037,.837,2.64),(-.55,.837,2.64)],[(0,0),(.96,0),(.96,.96),(0,.96)])
plane('BR_Mold02_Return',[(1.037,.837,1.12),(1.037,.30,1.12),(1.037,.20,1.12),(1.037,.837,2.64),(1.037,.30,2.64),(1.037,.20,2.64)],[(.96,0),(.6818,0),(.63,0),(.96,.96),(.6818,.96),(.63,.96)],faces=[(0,1,4,3),(1,2,5,4)],alphas=[1,1,0,1,1,0])
# Open the inherited preview leaves only; use each mesh's source-world position to choose its half.
for ob in list(sc.objects):
 if ob.type!='MESH' or ob in old+new:continue
 # The saved source groups don't retain a collection: use depth and width geometry to identify leaf members.
 vs=[ob.matrix_world@Vector(v) for v in ob.bound_box]
 if not vs:continue
 mn=[min(v[i] for v in vs) for i in range(3)];mx=[max(v[i] for v in vs) for i in range(3)]
 if mn[1]<-.92 and mx[1]<-.90 and mn[0]>-.52 and mx[0]<.52 and mx[2]<=2.112:
  side=-1 if (mn[0]+mx[0])/2<0 else 1;pv=Vector((side*.5,-.978,0));angle=95*side
  ob.matrix_world=Matrix.Translation(pv)@Matrix.Rotation(math.radians(angle),4,'Z')@Matrix.Translation(-pv)@ob.matrix_world
# Packed textures make preview independent of the original kit once saved.
for image in bpy.data.images:
 if image.source=='FILE' and image.has_data:image.pack()
cam=sc.camera;cam.location=(-.18,-1.72,1.73);target=Vector((.20,.73,1.95));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=24
sc.render.filepath=str(ROOT/'previews/corner-mold.png');bpy.ops.render.render(write_still=True)
for o in new:o.hide_render=True
sc.render.filepath=str(ROOT/'previews/corner-repaired.png')
if '--refresh' not in sys.argv:bpy.ops.render.render(write_still=True)
for o in old:o.hide_render=False
sc.render.filepath=str(ROOT/'previews/previous-central-mold.png')
if '--refresh' not in sys.argv:bpy.ops.render.render(write_still=True)
for o in old:o.hide_render=True
for o in new:o.hide_render=False
cam.location=(0,-4.4,1.65);cam.rotation_euler=(Vector((.18,.30,1.85))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=44
sc.render.filepath=str(ROOT/'previews/doorway-mold.png');bpy.ops.render.render(write_still=True)
cam.location=(-.24,-.35,1.80);cam.rotation_euler=(Vector((.43,.75,2.10))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=20
sc.render.filepath=str(ROOT/'previews/inside-closeup.png');bpy.ops.render.render(write_still=True)
exports=[]
for o in new:
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
 path=ROOT/'model'/f'{o.name}.fbx'
 bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,object_types={'MESH'},add_leaf_bones=False,apply_unit_scale=True,axis_forward='-Y',axis_up='Z',path_mode='RELATIVE')
 exports.append({'file':str(path.relative_to(ROOT)),'mesh':o.name,'origin':[0,0,0],'vertices':len(o.data.vertices),'triangles':2 if 'Back' in o.name else 4,'collision':'none; decoration only','source_bounds':[[min(v.co[i] for v in o.data.vertices) for i in range(3)],[max(v.co[i] for v in o.data.vertices) for i in range(3)]]})
manifest={'id':'BR-MOLD-02','fix':'FIX-001','plan_origin_m':[1.1,4.7,0],'source_up':'+Z','source_front':'-Y','fbx_forward':'-Y','fbx_up':'Z','mapping':'plan=(1.10+sourceX,4.70-sourceY,sourceZ)','exports':exports,'material':{'texture':'textures/mold-colonies-rgba.png','texture_srgb':False,'base_color_linear':[.022,.021,.020],'roughness':1,'metallic':0,'specular':0,'alpha_formula':'VertexColor.A * texture.A * pow(saturate((0.56-dot(texture.RGB,(0.2126,0.7152,0.0722)))/0.38),1.35)','recommended_unreal':'Masked + DitherTemporalAA for graded pigment coverage; opacity mask clip0.1, two-sided; do not reuse green Tint','mask_note':'Original generated alpha preserved. Material also suppresses pale RGB wash.'},'suggested_inspect_world_m':[1.82,3.89,2.16],'runtime':'Retain existing Malcolm hunk identity/spawn/talk/camera world transforms. Attach both overlays to existing malady with RepairDamage + AuthoredMoldDamage tags; hide both after repair. Move inspect body to raised patch and verify real click reachability.'}
(ROOT/'assembly.json').write_text(json.dumps(manifest,indent=2)+'\n')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'model/BR-MOLD-02.blend'))
print('BR-MOLD-02 BUILT')
