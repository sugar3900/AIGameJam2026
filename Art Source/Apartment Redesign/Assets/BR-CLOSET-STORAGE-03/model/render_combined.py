"""Refresh the read-only FIX-001 context and render a true inside-closet view."""
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'model/BR-CLOSET-STORAGE-03.blend'))
bpy.context.preferences.filepaths.save_version=0
for ob in list(bpy.data.objects):
 if ob.name.startswith(('BR_Mold02_Back','BR_Mold02_Return')):bpy.data.objects.remove(ob,do_unlink=True)
with bpy.data.libraries.load(str(ROOT.parent/'BR-MOLD-02/model/BR-MOLD-02.blend'),link=False) as (src,dst):
 dst.objects=[n for n in src.objects if n in ('BR_Mold02_Back','BR_Mold02_Return')]
for ob in dst.objects:
 if ob:bpy.context.collection.objects.link(ob)
collection=bpy.data.collections.get('BR-CLOSET-STORAGE-03_SOURCE') or bpy.data.collections.new('BR-CLOSET-STORAGE-03_SOURCE')
if collection.name not in bpy.context.scene.collection.children:bpy.context.scene.collection.children.link(collection)
for ob in list(bpy.data.objects):
 if ob.name.startswith(('West ','East ')) and any(m and m.name.startswith('CS03_') for m in ob.data.materials):
  if ob.name not in collection.objects:collection.objects.link(ob)
  for other in list(ob.users_collection):
   if other!=collection:other.objects.unlink(ob)
sc=bpy.context.scene
sc.render.engine='CYCLES';sc.cycles.samples=40
sc.render.resolution_x=1200;sc.render.resolution_y=1100;sc.render.resolution_percentage=100
cam=sc.camera
cam.location=(.18,-.62,1.77);target=Vector((-.76,-.33,1.70))
cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=54
sc.render.filepath=str(ROOT/'previews/hook-closeup.png')
bpy.ops.render.render(write_still=True)
cam.location=(0,-.69,1.59);target=Vector((0,.63,1.88))
cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=16
sc.render.filepath=str(ROOT/'previews/closet-inside-combined.png')
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'model/BR-CLOSET-STORAGE-03.blend'))
print('Combined interior preview complete; exports unchanged.')
