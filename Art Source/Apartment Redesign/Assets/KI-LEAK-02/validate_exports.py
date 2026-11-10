"""Headless FBX round trip and mask validation. Writes only this package."""
import bpy,json,math,hashlib
import numpy as np
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
manifest=json.loads((ROOT/'validation.json').read_text());result={}
for name,expected in manifest['exports'].items():
 bpy.ops.wm.read_factory_settings(use_empty=True)
 bpy.ops.import_scene.fbx(filepath=str(ROOT/'models'/f'{name}.fbx'))
 visual=[o for o in bpy.data.objects if o.type=='MESH' and not o.name.startswith('UCX_')]
 hulls=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('UCX_')]
 assert len(visual)==1,(name,[o.name for o in visual])
 o=visual[0];v=[o.matrix_world@x.co for x in o.data.vertices]
 lo=[min(p[k] for p in v) for k in range(3)];hi=[max(p[k] for p in v) for k in range(3)]
 assert max(abs(a-b) for a,b in zip(lo+hi,expected['min']+expected['max']))<.00001,(name,lo,hi)
 assert o.data.uv_layers and len(o.data.uv_layers.active.data)==len(o.data.loops),name
 assert all(math.isfinite(c) for p in v for c in p)
 assert o.location.length<.00001,(name,list(o.location))
 if name.endswith('_bucket'):assert len(hulls)==13
 else:assert len(hulls)==0
 result[name]={'bounds_m':{'min':lo,'max':hi},'uv_loops':len(o.data.uv_layers.active.data),'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'ucx_hulls':len(hulls),'origin_m':list(o.location),'roundtrip':'PASS'}
bpy.ops.wm.read_factory_settings(use_empty=True)
im=bpy.data.images.load(str(ROOT/'textures/T_Leak_Puddle_Mask.png'))
a=np.empty(len(im.pixels),dtype=np.float32);im.pixels.foreach_get(a);a=a.reshape((im.size[1],im.size[0],4))
alpha=a[:,:,3];edge=np.concatenate([alpha[0],alpha[-1],alpha[:,0],alpha[:,-1]])
assert edge.max()==0,'Mask clipped at image boundary'
assert alpha.max()>.99 and alpha.min()==0
partial=int(np.count_nonzero((alpha>.01)&(alpha<.99)));assert partial>100,'No feathering'
result['mask']={'width':im.size[0],'height':im.size[1],'fully_transparent_border':True,'partial_alpha_pixels':partial,'alpha_min':float(alpha.min()),'alpha_max':float(alpha.max()),'physical_size_m':manifest['puddle_mask']['size_m']}
source=ROOT.parent/'KI-SINK-NARROW-01/models/KI_SINK_NARROW_assembly.blend'
assert hashlib.sha256(source.read_bytes()).hexdigest()==manifest['source_blend_sha256'],'Original asset changed'
result['original_source_unchanged']=True
(ROOT/'fbx-validation.json').write_text(json.dumps(result,indent=2)+'\n')
print('EXPORT_VALIDATION_PASS',json.dumps(result))
