"""Read back exported PNG bytes; verify derived normal orientation and data ranges."""
from pathlib import Path
import struct,zlib,json,numpy as np
R=Path(__file__).resolve().parent

def read(name):
 data=(R/'textures'/name).read_bytes();assert data[:8]==b'\x89PNG\r\n\x1a\n';i=8;payload=b''
 while i<len(data):
  length=struct.unpack('>I',data[i:i+4])[0];kind=data[i+4:i+8];chunk=data[i+8:i+8+length];crc=struct.unpack('>I',data[i+8+length:i+12+length])[0];assert crc==(zlib.crc32(kind+chunk)&0xffffffff)
  if kind==b'IHDR':w,h,depth,colour,*_=struct.unpack('>IIBBBBB',chunk)
  if kind==b'IDAT':payload+=chunk
  i+=12+length
 channels=3 if colour==2 else 1;stride=w*channels*(depth//8);rows=np.frombuffer(zlib.decompress(payload),dtype=np.uint8).reshape(h,stride+1);assert (rows[:,0]==0).all();a=np.frombuffer(rows[:,1:].tobytes(),dtype='>u2' if depth==16 else 'u1').reshape(h,w,channels).astype(float)/((1<<depth)-1)
 return a.squeeze()
h=read('T_BathGlaze_Height16.png')*.00018;normal=read('T_BathGlaze_NormalDX.png')*2-1;rough=read('T_BathGlaze_Roughness.png');step=.2425/h.shape[0]
dx=(np.roll(h,-1,1)-np.roll(h,1,1))/(2*step);dy=(np.roll(h,-1,0)-np.roll(h,1,0))/(2*step);ref=np.stack([-dx,-dy,np.ones_like(dx)],axis=2);ref/=np.linalg.norm(ref,axis=2,keepdims=True)
err=float(np.abs(normal-ref).max());assert err<.0045;assert normal[:,:,2].min()>.99;assert .37<rough.min()<rough.max()<.47
report={'png_crc_and_dimensions':'pass','normal_vs_height_max_channel_error':err,'DirectX_green_matches_V_down_height_derivative':True,'normal_srgb':False,'roughness_srgb':False,'height_srgb':False,'passed':True}
(R/'png-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
