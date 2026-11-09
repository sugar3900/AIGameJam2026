import bpy,numpy as np
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'textures'
def load(n):
 im=bpy.data.images.load(str(p/n),check_existing=False); a=np.array(im.pixels[:],dtype=np.float32).reshape(im.size[1],im.size[0],4)[:,:,:3]; return a
pict=load('ENV-SKY-01_painterly_2k.png'); hdr=load('ENV-SKY-01_painterly_2k_LDR-derived.hdr')
expected=np.where(pict<=.04045,pict/12.92,((pict+.055)/1.055)**2.4)
print('mean_abs HDR-vs-sRGB-decoded',float(np.abs(hdr-expected).mean()),'max',float(np.abs(hdr-expected).max()),'PNG-sample',pict[512,1024].tolist(),'HDR-sample',hdr[512,1024].tolist())
print('mean_abs HDR-vs-Blender-PNG-linear',float(np.abs(hdr-pict).mean()),'max',float(np.abs(hdr-pict).max()))
