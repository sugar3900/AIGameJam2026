import bpy, numpy as np
from pathlib import Path
base=Path(__file__).resolve().parents[1]
for path in sorted((base/'concepts').glob('*.png')):
 im=bpy.data.images.load(str(path), check_existing=False); w,h=im.size; rgba=np.array(im.pixels[:],dtype=np.float32).reshape(h,w,4); a=rgba[...,:3]; diff=np.abs(a[:,0]-a[:,-1]); l=a@np.array([.2126,.7152,.0722]); y,x=np.unravel_index(np.argmax(l),l.shape)
 print(path.name, f'{w}x{h}',f'seam_mean={diff.mean():.6f}',f'seam_max={diff.max():.6f}',f'zenith_spread={a[-1].std(axis=0).mean():.6f}',f'nadir_spread={a[0].std(axis=0).mean():.6f}',f'brightest_uv_bottom=({x/(w-1):.4f},{y/(h-1):.4f})',f'elevation={(y/(h-1)-.5)*180:.2f}')
 bpy.data.images.remove(im)
