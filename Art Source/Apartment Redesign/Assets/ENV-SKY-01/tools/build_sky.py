"""Technical bake of a generated LDR sky into 2:1, wrap-safe PNG + linear RGBE.
Run Blender background --python build_sky.py. No recovered HDR is claimed.
"""
import bpy
import numpy as np
from pathlib import Path
from math import pi

base = Path(__file__).resolve().parents[1]
src = bpy.data.images.load(str(base/'concepts/sky-candidate-b.png'), check_existing=False)
sw, sh = src.size
rgba = np.array(src.pixels[:], dtype=np.float32).reshape(sh, sw, 4)
# Blender pixel arrays are bottom-up. Output is 2048x1024, bicubic not invented detail.
w, h = 2048, 1024
# Source image's painted disc centre manually located at x=.5, top y=.313;
# remap latitude only to put it at 38 degrees while preserving equator and poles.
y_out = np.linspace(0, 1, h)  # bottom -> top
# Map output fraction in bottom-up coordinates to source fraction.
out_knots = np.array([0., .5, .5 + 38/180, 1.])
in_knots = np.array([0., .5, 1-.313, 1.])
y_src = np.interp(y_out, out_knots, in_knots)*(sh-1)
x_src = np.linspace(0, sw-1, w)
x0 = np.floor(x_src).astype(int); x1=np.minimum(x0+1,sw-1); ax=(x_src-x0)[None,:,None]
y0 = np.floor(y_src).astype(int); y1=np.minimum(y0+1,sh-1); ay=(y_src-y0)[:,None,None]
lo=rgba[y0[:,None],x0[None,:],:]*(1-ax)+rgba[y0[:,None],x1[None,:],:]*ax
hi=rgba[y1[:,None],x0[None,:],:]*(1-ax)+rgba[y1[:,None],x1[None,:],:]*ax
out=(lo*(1-ay)+hi*ay).astype(np.float32)
# Blend a 6% overlap of the original panorama ends, then remap that
# stitched circular sequence to output width. Both strips traverse left-to-right;
# unlike mirrored crossfading, it does not reflect a tree across the seam.
n=int(w*.06)
t=np.linspace(0,1,n,dtype=np.float32); t=t*t*(3-2*t)
cross=out[:,w-n:,:]*(1-t[None,:,None])+out[:,:n,:]*t[None,:,None]
m=n//2
stitched=np.concatenate((cross[:,m:,:],out[:,n:w-n,:],cross[:,:m,:]),axis=1)
q=np.linspace(0,stitched.shape[1]-1,w); q0=np.floor(q).astype(int); q1=np.minimum(q0+1,stitched.shape[1]-1); f=(q-q0)[None,:,None]
out=(stitched[:,q0,:]*(1-f)+stitched[:,q1,:]*f).astype(np.float32)
# Fade only the extreme 2.5% around each pole toward the row average; spherical
# projection collapses each of these rows to a point.
n_pole=int(h*.025)
for j in range(n_pole):
 t=j/(n_pole-1); t=t*t*(3-2*t)
 for row in (j,h-1-j):
  avg=out[row,:,:3].mean(axis=0)
  out[row,:,:3]=t*out[row,:,:3]+(1-t)*avg
out[:,:,3]=1.
# Enforce equality again to eliminate last-bit floating error after pole blend.
edge=(out[:,0,:]+out[:,-1,:])*.5
out[:,0,:]=edge; out[:,-1,:]=edge

def save(name, data, fmt, colorspace):
 image=bpy.data.images.new(name=name, width=w, height=h, alpha=False, float_buffer=True)
 image.colorspace_settings.name=colorspace
 image.pixels.foreach_set(np.ascontiguousarray(data,dtype=np.float32).ravel())
 image.file_format=fmt; image.filepath_raw=str(base/'textures'/name)
 image.save(); bpy.data.images.remove(image)

# Convert to the HDR save path; saved RGBE and PNG are compared after reload.
# The generated source itself is 8-bit LDR, so no radiance is recovered.
rgb=out[:,:,:3].copy()
linear=np.where(rgb<=.04045, rgb/12.92, ((rgb+.055)/1.055)**2.4)
lin=np.concatenate((linear,np.ones((h,w,1),dtype=np.float32)),axis=2)
save('ENV-SKY-01_painterly_2k.png',out,'PNG','sRGB')
save('ENV-SKY-01_painterly_2k_LDR-derived.hdr',lin,'HDR','Non-Color')
print('source',sw,sh,'output',w,h,'seam_max',np.abs(out[:,0,:3]-out[:,-1,:3]).max(),'zenith_spread',out[-1,:,:3].std(axis=0).max(),'nadir_spread',out[0,:,:3].std(axis=0).max(),'source_disc_top_v=.313 output_disc_top_v=',.5-38/180)
