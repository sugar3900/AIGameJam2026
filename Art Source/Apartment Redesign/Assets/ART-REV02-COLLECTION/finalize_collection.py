"""Bake portable frame base color, validate all FBXs and create review contact sheet.
Run after build_collection.py. Native Blender bakes leave generated artwork PNGs untouched.
"""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent;ASSETS=ROOT.parent;REPO=ASSETS.parents[2]
INV=REPO/'docs/03 Art & Audio/Apartment Design/layout-revision-02/feedback/FIX-006/wall-art-inventory.json'
catalog=json.loads((ROOT/'catalog.json').read_text());inventory=json.loads(INV.read_text());entries=[]
def activate(o):
 bpy.ops.object.select_all(action='DESELECT');o.hide_set(False);o.select_set(True);bpy.context.view_layer.objects.active=o
for item in catalog:
 ident='ART-REV02-'+item['id'];dest=ASSETS/ident;entry=json.loads((dest/'manifest.json').read_text())
 if entry['frame_material'].get('base_color_map') and (dest/'textures/T_Frame_BaseColor.png').exists():
  entries.append(entry);print('FRAME_BAKE_REUSED',ident,flush=True);continue
 bpy.ops.wm.open_mainfile(filepath=str(dest/'models'/f'{ident}.blend'))
 sc=bpy.context.scene;sc.render.threads_mode='FIXED';sc.render.threads=2;sc.cycles.samples=1
 original=bpy.data.materials.get(ident+'_Frame') or bpy.data.materials[ident+'_Aged_Gilt'];copy=original.copy();copy.name='BAKE_FRAME_ONLY';nodes=copy.node_tree.nodes;links=copy.node_tree.links;p=nodes.get('Principled BSDF')
 out=nodes.get('Material Output');em=nodes.new('ShaderNodeEmission')
 if p.inputs['Base Color'].links:links.new(p.inputs['Base Color'].links[0].from_socket,em.inputs[0])
 else:em.inputs[0].default_value=p.inputs['Base Color'].default_value
 links.new(em.outputs[0],out.inputs['Surface'])
 image=bpy.data.images.new('T_Frame_BaseColor',width=512,height=512);image.colorspace_settings.name='sRGB';target=nodes.new('ShaderNodeTexImage');target.image=image;nodes.active=target
 bpy.ops.mesh.primitive_plane_add(size=2);plane=bpy.context.object;plane.name='BAKE_PLANE';plane.data.materials.append(copy);activate(plane);bpy.ops.object.bake(type='EMIT')
 image.filepath_raw=str(dest/'textures/T_Frame_BaseColor.png');image.file_format='PNG';image.save();image.pack();bpy.data.objects.remove(plane,do_unlink=True)
 nodes=original.node_tree.nodes;links=original.node_tree.links;p=nodes.get('Principled BSDF');tex=nodes.new('ShaderNodeTexImage');tex.image=image;links.new(tex.outputs['Color'],p.inputs['Base Color'])
 entry['frame_material']['base_color_map']='textures/T_Frame_BaseColor.png';entry['frame_material']['shader']='Use baked sRGB base color directly; wood roughness0.64. Gilt/separate accents use manifest/README constants.'
 entry['frame_material']['baked_material']=original.name
 obj=bpy.data.objects[ident.replace('-','_')];hull=bpy.data.objects['UCX_'+obj.name+'_00'];activate(obj);hull.hide_set(False);hull.select_set(True)
 bpy.ops.export_scene.fbx(filepath=str(dest/'models'/f'{ident}.fbx'),use_selection=True,object_types={'MESH'},add_leaf_bones=False,path_mode='AUTO',apply_unit_scale=True,axis_forward='-Y',axis_up='Z')
 hull.hide_set(True);bpy.data.materials.remove(copy);sc.cycles.samples=16;bpy.ops.wm.save_as_mainfile(filepath=str(dest/'models'/f'{ident}.blend'))
 (dest/'manifest.json').write_text(json.dumps(entry,indent=2)+'\n');entries.append(entry)
 print('FRAME_BAKE_COMPLETE',ident,flush=True)
# Read actual exported files, not scene assumptions.
checks=[]
for entry in entries:
 x,y,w,d=entry['planned_rect'];front=entry['front']
 centers={'north':(x+w/2,y+d),'south':(x+w/2,y),'east':(x,y+d/2),'west':(x+w,y+d/2)}
 px,py=centers[front];entry['engine_placement']={'wall_datum_center_plan_m':[px,py,entry['bottom_z']],'ue_local_yaw_degrees':{'north':180,'south':0,'east':-90,'west':90}[front],'scale':[1,1,1],'note':'Source bottom/rear pivot. FBX import conversion keeps X/flips Y; confirm with installed frame front.'}
 (ASSETS/entry['asset']/'manifest.json').write_text(json.dumps(entry,indent=2)+'\n')
 ident=entry['asset'];dest=ASSETS/ident;bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(dest/entry['fbx']))
 visual=[o for o in bpy.data.objects if o.type=='MESH' and not o.name.startswith('UCX_')];ucx=[o for o in bpy.data.objects if o.name.startswith('UCX_')]
 assert len(visual)==1 and len(ucx)==1,(ident,len(visual),len(ucx))
 o=visual[0];v=[o.matrix_world@x.co for x in o.data.vertices];lo=[min(x[k] for x in v) for k in range(3)];hi=[max(x[k] for x in v) for k in range(3)]
 assert max(abs(a-b) for a,b in zip(lo+hi,entry['bounds_m']['min']+entry['bounds_m']['max']))<1e-5,(ident,lo,hi)
 assert o.location.length<1e-5 and o.data.uv_layers
 assert all(math.isfinite(c) for vtx in v for c in vtx)
 assert hashlib.sha256((dest/entry['art_texture']).read_bytes()).hexdigest()==entry['art_sha256'],'Artwork PNG mutated'
 checks.append({'asset':ident,'roundtrip':'PASS','visual_meshes':1,'ucx':1,'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'origin_m':list(o.location),'bounds_m':[lo,hi],'uv_loops':len(o.data.uv_layers.active.data),'artwork_unchanged':True})
assert len({e['art_sha256'] for e in entries})==17,'Repeated artwork image'
(ROOT/'validation.json').write_text(json.dumps({'items':checks,'unique_artwork_sha256_count':17,'original_artwork_pngs_preserved':True},indent=2)+'\n')
(ROOT/'build-manifest.json').write_text(json.dumps(entries,indent=2)+'\n')
for entry in entries:
 rec=next(x for x in inventory['items'] if x['instance']==entry['instance']);rec['source_art']=entry
 dest=ASSETS/entry['asset'];w,d,h=entry['dimensions_m']
 (dest/'README.md').write_text(f"# {entry['asset']} — {entry['title']}\n\nUnique replacement for `{entry['instance']}`. Frame: **{entry['frame']}**.\n\n- Outer dimensions {w:.3f} m wide × {h:.3f} m tall × {d:.3f} m deep. Origin bottom-center at rear wall plane, source front −Y, Z up. The established import keeps X and flips Y. Place using the unchanged instance wall orientation, frame center and bottom height in `manifest.json`; do not use old source dimensions.\n- Original generated artwork is `textures/T_Artwork.png`, unmodified. Its mesh UV center-crops with equal horizontal/vertical pixel scale; no stretching. The exact crop is recorded in the manifest.\n- Frame wood/paint uses `textures/T_Frame_BaseColor.png` (sRGB), roughness 0.64. `T_Frame_Grain.png` is the existing painterly walnut source used for the native Blender material bake, kept for reproducibility. Gilt accents: linear base `(0.38,0.26,0.095)`, metallic0.64, roughness0.48. Ivory mount `(0.72,0.67,0.55)`, roughness0.90. Backboard `(0.12,0.085,0.055)`, roughness0.90. Artwork is opaque and rough0.86; no reflective glass hides the image. Reconnect the material maps in Unreal.\n- One visual FBX mesh and one UCX box. Import legacy FBX with UCX enabled. This is static wall dressing with no interaction identity or RepairDamage tag. No collision is necessary if wall collision already covers it, but the simple box is included.\n- `models/{entry['asset']}.blend` packs textures and includes a disabled preview wall, camera and light, excluded from FBX. `previews/framed.png` is the neutral studio review.\n- Reproduce through `../ART-REV02-COLLECTION/build_collection.py -- {entry['asset'][-3:]}`, then run the collection finalizer. Source validation reimports the FBX and verifies UVs, bounds, origin, UCX and artwork SHA. Engine installation/lighting and in-room screenshots remain pending.\n")
inventory['status']='17 unique source artworks and fitted frames complete and roundtrip validated; engine integration/review pending'
INV.write_text(json.dumps(inventory,indent=2)+'\n')
# Contact sheet is a native scene of already-rendered previews, with labels.
bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene
def emission(name,color=None,img=None):
 m=bpy.data.materials.new(name);m.use_nodes=True;nd=m.node_tree.nodes;nd.clear();out=nd.new('ShaderNodeOutputMaterial');em=nd.new('ShaderNodeEmission')
 if img:
  t=nd.new('ShaderNodeTexImage');t.image=img;m.node_tree.links.new(t.outputs['Color'],em.inputs[0])
 else:em.inputs[0].default_value=(*color,1)
 m.node_tree.links.new(em.outputs[0],out.inputs[0]);return m
ink=emission('Ink',(.065,.055,.045))
def text(label,x,z,size):
 cu=bpy.data.curves.new('Label','FONT');cu.body=label;cu.align_x='CENTER';cu.size=size;o=bpy.data.objects.new(label,cu);bpy.context.collection.objects.link(o);o.location=(x,-.02,z);o.rotation_euler=(math.pi/2,0,0);o.data.materials.append(ink)
for i,entry in enumerate(entries):
 x=(i%4-1.5)*1.20;z=6.5-(i//4)*1.45;im=bpy.data.images.load(str(ASSETS/entry['asset']/'previews/framed.png'));mat=emission(entry['asset'],img=im)
 me=bpy.data.meshes.new('Image');me.from_pydata([(x-.55,0,z-.55),(x+.55,0,z-.55),(x+.55,0,z+.55),(x-.55,0,z+.55)],[],[(0,1,2,3)]);me.update();o=bpy.data.objects.new(entry['asset'],me);bpy.context.collection.objects.link(o);me.materials.append(mat);uv=me.uv_layers.new()
 for li,co in enumerate([(0,0),(1,0),(1,1),(0,1)]):uv.data[li].uv=co
 text(entry['asset'],x,z-.66,.075);text(entry['title'],x,z-.76,.045)
text('REV02 / A COLLECTED APARTMENT',0,7.28,.15)
text('17 unique paintings and frame treatments  •  source review',0,7.10,.065)
bpy.ops.object.camera_add(location=(0,-10,3.65));cam=bpy.context.object;cam.rotation_euler=(math.pi/2,0,0);cam.data.type='ORTHO';cam.data.ortho_scale=7.85;sc.camera=cam
sc.world=bpy.data.worlds.new('Paper');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.78,.75,.69,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=1
sc.render.engine='CYCLES';sc.cycles.samples=8;sc.render.threads_mode='FIXED';sc.render.threads=2;sc.render.resolution_x=1600;sc.render.resolution_y=2400;sc.render.resolution_percentage=100;sc.view_settings.view_transform='Standard';sc.render.image_settings.file_format='PNG';sc.render.filepath=str(ROOT/'previews/contact-sheet.png');bpy.ops.render.render(write_still=True)
print('COLLECTION_FINALIZED_17',flush=True)
import runpy
runpy.run_path(str(ROOT/'export_material_handoff.py'),run_name='__main__')
