"""Describe exact exported material slot order without changing source models."""
import bpy,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent;ASSETS=ROOT.parent
manifest=ROOT/'build-manifest.json';entries=json.loads(manifest.read_text())
for entry in entries:
 dest=ASSETS/entry['asset'];bpy.ops.wm.open_mainfile(filepath=str(dest/'models'/(entry['asset']+'.blend')))
 obj=bpy.data.objects[entry['asset'].replace('-','_')];mats=[]
 for i,m in enumerate(obj.data.materials):
  p=m.node_tree.nodes.get('Principled BSDF');d={'slot':i,'name':m.name,'base_color_linear':[round(float(v),7) for v in p.inputs['Base Color'].default_value[:3]],'roughness':round(p.inputs['Roughness'].default_value,7),'metallic':round(p.inputs['Metallic'].default_value,7),'opacity':1,'two_sided':False}
  if p.inputs['Base Color'].links:
   node=p.inputs['Base Color'].links[0].from_node
   if node.type=='TEX_IMAGE':d['base_color_texture']='textures/'+Path(node.image.filepath).name;d['texture_srgb']=True
  mats.append(d)
 entry['materials']=mats;(dest/'manifest.json').write_text(json.dumps(entry,indent=2)+'\n')
manifest.write_text(json.dumps(entries,indent=2)+'\n')
invpath=ASSETS.parents[2]/'docs/03 Art & Audio/Apartment Design/layout-revision-02/feedback/FIX-006/wall-art-inventory.json';inv=json.loads(invpath.read_text())
for e in entries:next(x for x in inv['items'] if x['instance']==e['instance'])['source_art']=e
invpath.write_text(json.dumps(inv,indent=2)+'\n')
print('MATERIAL_HANDOFF_COMPLETE_17',flush=True)
