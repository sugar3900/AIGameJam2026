"""Generate a clean-alpha water stain for placement over the sink backsplash.

Run in headless Blender: blender -b --python Tools/Art/Environment/generate_sink_stain.py
This produces an isolated RGBA overlay with constant RGB even where alpha is
zero; the stain is color-only, not a raised surface. Place once on a wall plane.
"""
from pathlib import Path
import math
import struct
import zlib
import numpy as np

N = 512
Y, X = np.mgrid[0:N, 0:N].astype(np.float32)
x = (X - 256) / 200
y = (Y - 215) / 135
# A broad broken water tide; distort the ellipse rather than applying an
# obvious repeating noise texture. Thin, weak rings imply dried residue.
noise = (.065*np.sin(x*5.9 + y*3.7) + .045*np.sin(x*11.1-y*7.4)
         + .025*np.sin(x*18.3+y*12.9))
r = np.sqrt(x*x + y*y) + noise
outer = np.clip((1.0-r)*4.5, 0, 1)
inner = np.clip((r-.54)*5.0, 0, 1)
base = outer * .075
ring = outer * inner * (.085 + .055 * np.sin(r*29 + x*1.7)**2)
alpha = base + ring
# Faint, tapered downward runs beneath a leak. Top of PNG is Y=0, so drips
# extend toward larger Y. They blend into the existing wall rather than
# representing a flat paper patch.
for cx, start, length, width, amount in ((206,265,122,7,.075), (271,275,145,5,.09), (320,260,108,9,.06), (368,245,96,4,.06)):
    t=(Y-start)/length
    line=np.exp(-((X-cx-4*np.sin(t*2))/width)**2)
    taper=np.clip(t*7,0,1)*np.clip((1-t)*4,0,1)
    alpha=np.maximum(alpha,line*taper*amount)
# Smooth finite falloff creates a fully transparent boundary on all four edges.
border=np.clip(np.minimum.reduce([X,Y,N-1-X,N-1-Y])/30,0,1)
alpha=np.clip(alpha*border,0,.25)
rgba=np.empty((N,N,4),dtype=np.uint8)
rgba[:,:,:3]=[91,61,34]  # shared RGB even in fully transparent pixels
rgba[:,:,3]=np.rint(alpha*255).astype(np.uint8)
rows=b''.join(b'\x00'+rgba[y].tobytes() for y in range(N))
def chunk(t,d):
    return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',N,N,8,6,0,0,0))
png+=chunk(b'IDAT',zlib.compress(rows,9))+chunk(b'IEND',b'')
out=Path(__file__).resolve().parents[3]/'Art Source/Environment Textures/T_SinkStain_Overlay.png'
out.write_bytes(png)
print('Saved',out,'alpha max',rgba[:,:,3].max(),'boundary max',max(rgba[0,:,3].max(),rgba[-1,:,3].max(),rgba[:,0,3].max(),rgba[:,-1,3].max()))
