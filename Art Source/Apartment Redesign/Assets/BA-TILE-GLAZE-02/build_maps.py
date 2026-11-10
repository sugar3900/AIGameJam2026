"""Deterministic periodic technical surface maps; no painted colour or baked grout.
Run with Blender's bundled Python (numpy), no editor required.
"""
from pathlib import Path
import numpy as np,json,zlib,struct
R=Path(__file__).resolve().parent;N=1024;PERIOD=.097/.40
rng=np.random.default_rng(3802)
y,x=np.mgrid[0:N,0:N]/N
# PNG rows follow V-down. DirectX tangent normal uses matching +V-down green.
def field(bands):
 h=np.zeros((N,N));dx=h.copy();dy=h.copy();modes=[]
 for lo,hi,count,amplitude in bands:
  for _ in range(count):
   kx,ky=rng.integers(-hi,hi+1,2)
   while not lo<=np.hypot(kx,ky)<=hi:kx,ky=rng.integers(-hi,hi+1,2)
   phase=rng.uniform(0,2*np.pi);a=amplitude/np.sqrt(count/2);theta=2*np.pi*(kx*x+ky*y)+phase
   h+=a*np.sin(theta);dx+=a*np.cos(theta)*2*np.pi*kx/PERIOD;dy+=a*np.cos(theta)*2*np.pi*ky/PERIOD
   modes.append([int(kx),int(ky),float(phase),float(a)])
 return h,dx,dy,modes
h,dx,dy,modes=field([(2,6,16,.000025),(9,22,24,.000012),(35,80,32,.000002)])
# Physical amplitude limit: gentle glaze, not hammered stone.
scale=.00018/np.ptp(h);h*=scale;dx*=scale;dy*=scale
normal=np.stack([-dx,-dy,np.ones_like(dx)],axis=2);normal/=np.linalg.norm(normal,axis=2,keepdims=True)
low,_,_,_=field([(2,9,20,1)])
rough=np.clip(.42+.032*np.tanh(low)+.015*np.tanh(h/(np.std(h)+1e-9)),.36,.48)
height=(h-h.min())/np.ptp(h)
def png(path,a,depth=8):
 a=np.asarray(a);colour=2 if a.ndim==3 else 0;arr=(np.clip(a,0,1)*((1<<depth)-1)+.5).astype('>u2' if depth==16 else 'u1')
 def chunk(kind,data):return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
 raw=b''.join(b'\0'+row.tobytes() for row in arr)
 path.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',N,N,depth,colour,0,0,0))+chunk(b'IDAT',zlib.compress(raw,9))+chunk(b'IEND',b''))
png(R/'textures/T_BathGlaze_NormalDX.png',normal*.5+.5)
png(R/'textures/T_BathGlaze_Roughness.png',rough)
png(R/'textures/T_BathGlaze_Height16.png',height,16)
# Edge samples differ by one texel, as expected; analytically the Fourier period closes exactly.
seam=[]
for axis in (0,1):
 edge=np.abs(np.take(h,0,axis)-np.take(h,-1,axis));interior=np.abs(np.diff(h,axis=axis));seam.append({'axis':axis,'seam_step_max_m':float(edge.max()),'interior_step_max_m':float(interior.max())})
report={'resolution':[N,N],'uv_repeat_metres':PERIOD,'height_peak_to_peak_m':float(np.ptp(h)),'height_rms_m':float(np.std(h)),'roughness_range':[float(rough.min()),float(rough.max())],'normal_max_tilt_degrees':float(np.degrees(np.arccos(normal[:,:,2].min()))),'periodic_integer_fourier_modes':True,'seam_checks':seam,'finite':bool(np.isfinite(normal).all()),'normal_length_max_error':float(np.abs(np.linalg.norm(normal,axis=2)-1).max()),'passed':bool(np.isfinite(normal).all() and all(q['seam_step_max_m']<=q['interior_step_max_m']*1.05 for q in seam))}
(R/'map-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));assert report['passed']
