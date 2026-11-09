import bpy, numpy as np
from pathlib import Path
base=Path(__file__).resolve().parents[1]
for p in sorted((base/'textures').glob('*')):
 im=bpy.data.images.load(str(p),check_existing=False); w,h=im.size; a=np.array(im.pixels[:],dtype=np.float32).reshape(h,w,4)[:,:,:3]
 edge=np.abs(a[:,0]-a[:,-1]); y0,y1=int(h*.68),int(h*.75); x0,x1=int(w*.47),int(w*.53)
 sub=a[y0:y1,x0:x1]; l=sub@np.array([.2126,.7152,.0722]); mask=l>np.percentile(l,99.8); yy,xx=np.nonzero(mask); x=(x0+xx.mean())/(w-1); y=(y0+yy.mean())/(h-1)
 print(p.name, 'size',w,h,'seam_max',float(edge.max()),'seam_mean',float(edge.mean()),'zenith_std',float(a[-1].std(axis=0).max()),'nadir_std',float(a[0].std(axis=0).max()),'sun_peak_uv_bottom',round(float(x),5),round(float(y),5),'approx_elevation_deg',round(float((y-.5)*180),2),'channel_max',float(a.max()),'colorspace',im.colorspace_settings.name)
 bpy.data.images.remove(im)
