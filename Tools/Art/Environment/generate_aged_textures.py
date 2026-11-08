"""Generate stylized renovation textures without physical impasto.

Run generate_brush_texture.py first, then:
    /Applications/Blender.app/Contents/MacOS/Blender -b --python Tools/Art/Environment/generate_aged_textures.py
The brush mask is a separate shader layer: these maps express actual materials
and localized defects. RGBA overlays have transparent borders for plane/decal use.
"""
from pathlib import Path
import struct
import zlib
import numpy as np
import bpy

N = 512
R = np.random.default_rng(1957)
Y, X = np.mgrid[0:N, 0:N].astype(np.float32)
root = Path(__file__).resolve().parents[3] / 'Art Source/Environment Textures'
root.mkdir(parents=True, exist_ok=True)
# Blend the visual stroke pattern into color maps, not alpha overlays. It is
# a color treatment only, leaving geometric and material normals untouched.
brush_image = bpy.data.images.load(str(root / 'T_BrushValues.png'), check_existing=False)
brush_image.colorspace_settings.name = 'Non-Color'
brush_values = np.asarray(brush_image.pixels[:], dtype=np.float32).reshape(N, N, 4)[:,:,0]

def write(name, data):
    if data.shape[2] == 3:
        data = data * (1.0 + (brush_values[:,:,None] - .5)*.5)
    data = np.asarray(np.clip(data * 255, 0, 255), dtype=np.uint8)
    h, w, channels = data.shape
    raw = b''.join(b'\x00' + data[y].tobytes() for y in range(h))
    def chunk(t, d):
        return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t+d) & 0xffffffff)
    png = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6 if channels == 4 else 2, 0, 0, 0))
    (root / name).write_bytes(png + chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b''))
    print('WROTE', name)

def periodic_field(seed, octaves=7):
    # Wrapped smooth value noise: irregular paint/wear rather than repetitive
    # diagonal sine bands. Bilinear cells wrap cleanly at each edge.
    rng = np.random.default_rng(seed)
    a = np.zeros((N,N), dtype=np.float32)
    weight_sum = 0.0
    for cells in (2, 4, 8, 16, 32):
        grid = rng.uniform(-1,1,(cells,cells))
        fx = X / N * cells; fy = Y / N * cells
        ix = np.floor(fx).astype(int); iy = np.floor(fy).astype(int)
        tx = fx-ix; ty = fy-iy
        tx = tx*tx*(3-2*tx); ty = ty*ty*(3-2*ty)
        x1=(ix+1)%cells; y1=(iy+1)%cells
        low=grid[iy,ix]*(1-tx)+grid[iy,x1]*tx
        high=grid[y1,ix]*(1-tx)+grid[y1,x1]*tx
        weight = 1.0 / (cells**.45)
        a += (low*(1-ty)+high*ty)*weight
        weight_sum += weight
    return a / weight_sum

def rgb(base, variation):
    return np.clip(np.array(base)[None,None,:] + variation[:,:,None] * np.array([1., .86, .7]), 0, 1)

# Boards run vertically; dark board edges and staggered end joints repeat at edges.
col = (X // 64).astype(int)
local = X % 64
wood = periodic_field(9) * .2 + .023*np.sin(X*.25 + 1.3*np.sin(Y*.019)) + .014*np.sin(X*.68 + Y*.012)
wood += np.take(np.array([-.03,.01,.035,-.015,.018,-.025,.025,-.01]), col)
seam = np.minimum(local, 64-local)
wood -= .10*np.exp(-seam*1.15)
for i in range(8):
    offset = (i%2)*128
    joint = np.minimum((Y-offset)%256, (offset-Y)%256)
    wood -= (col==i)*.07*np.exp(-joint*1.2)
write('T_Floorboards.png', rgb([.48,.31,.20], wood))

# Muted sage enamel with a few broad rubs exposing underlying warm wood.
field = periodic_field(18, 12)
woodpaint = rgb([.52,.60,.46], periodic_field(20)*.16)
worn = np.clip((field - .13)*3.0, 0, .45)
woodbase = rgb([.42,.28,.17], periodic_field(28)*.16)
woodpaint = woodpaint*(1-worn[:,:,None]) + woodbase*worn[:,:,None]
# A few restrained fine scratches, concentrated in one portion.
for _ in range(45):
    cx,cy = R.uniform(0,N,2); length=R.uniform(5,36)
    dx=(X-cx+N/2)%N-N/2; dy=(Y-cy+N/2)%N-N/2
    scratch=np.clip(1-np.abs(dy)/.8,0,1)*np.clip(1-np.abs(dx)/length,0,1)*.23
    woodpaint *= 1-scratch[:,:,None]
write('T_AgedSagePaint.png', woodpaint)

# Repeatable mid-century pink ceramic tile and soft grout, no cracks baked in.
tile_x = X % 128; tile_y=Y % 128
distance = np.minimum.reduce([tile_x, 128-tile_x, tile_y, 128-tile_y])
grout = np.clip((2.3-distance)/1.7, 0, 1)
index = (X//128 + 4*(Y//128)).astype(int)
tints = np.array([-.025,.012,.0,.025,.018,-.015,.03,-.02,.01,-.025,.015,.002,-.005,.02,-.015,.01])
tilevar=np.take(tints,index) + periodic_field(12)*.09 + .014*np.sin((X+Y)*.08)
tile=rgb([.75,.39,.46],tilevar)
tile=tile*(1-grout[:,:,None])+np.array([.72,.65,.57])[None,None,:]*grout[:,:,None]
write('T_PinkTile.png',tile)

# Warm, scuffed checker linoleum. Four squares per 120 cm texture tile gives
# 30 cm checks when the Unreal material uses a 120 cm world projection.
tx = X % 128; ty = Y % 128
parity = ((X//128 + Y//128) % 2).astype(bool)
d = np.minimum.reduce([tx,128-tx,ty,128-ty])
seams=np.clip((1.3-d)/1.2,0,1)
cream=np.array([.77,.70,.57]); terracotta=np.array([.55,.34,.27])
checker=np.where(parity[:,:,None],cream,terracotta)
checker=checker*(1-seams[:,:,None])+np.array([.36,.32,.27])[None,None,:]*seams[:,:,None]
checker=np.clip(checker+periodic_field(93)[:,:,None]*.085,0,1)
write('T_KitchenChecker.png',checker)

# Localized wall damp ring, with transparent edge. Warm umber varies in opacity.
u=(X-256)/185; v=(Y-245)/185
r=np.sqrt((u*(1+.08*np.sin(v*8)))**2 + (v*(1+.1*np.sin(u*7)))**2)
noise=periodic_field(32, 14)
edge=r+noise*.55
alpha=np.clip((.92-edge)*4,0,1)*np.clip((edge-.28)*5,0,1)*.30
alpha *= np.clip(.68 + noise*2, .25,1)
rgba=np.empty((N,N,4)); rgba[:,:,:3]=np.array([.31,.20,.10]); rgba[:,:,3]=alpha
write('T_WaterStain_Overlay.png',rgba)

# Localized linoleum wear, intended to sit just above the existing floor.
# Constant RGB at all alpha values prevents colored edge fringes. It is never
# tiled; place the plane near the leak and tag it so a repair can hide it.
u=(X-256)/225; v=(Y-250)/175
falloff=np.clip(1-(u*u+v*v),0,1)**1.6
stainfield=np.clip((periodic_field(53)*1.9+.25),0,1)
wear=falloff*stainfield*.28
for i in range(36):
    cx,cy=R.uniform(100,412),R.uniform(110,390)
    ang=R.uniform(-.6,.6); length=R.uniform(12,75); width=R.uniform(.35,1.2)
    dx=X-cx; dy=Y-cy
    uu=dx*np.cos(ang)+dy*np.sin(ang); vv=-dx*np.sin(ang)+dy*np.cos(ang)
    mark=np.clip((width+0.8-np.abs(vv))/0.8,0,1)*np.clip(1-np.abs(uu)/length,0,1)
    wear=np.maximum(wear,mark*falloff*R.uniform(.12,.35))
rgba=np.empty((N,N,4)); rgba[:,:,:3]=np.array([.24,.18,.12]); rgba[:,:,3]=wear
write('T_LinoleumWear_Overlay.png',rgba)

# Fine irregular fracture network intended to overlay the tile, not a bump map.
crack=np.zeros((N,N), dtype=np.float32)
def line(x1,y1,x2,y2,thick,opacity):
    global crack
    vx=x2-x1; vy=y2-y1
    t=np.clip(((X-x1)*vx+(Y-y1)*vy)/(vx*vx+vy*vy),0,1)
    dist=np.sqrt((X-(x1+t*vx))**2+(Y-(y1+t*vy))**2)
    crack=np.maximum(crack,np.clip(thick+.75-dist,0,1)*opacity)
pts=[(225,75),(232,130),(215,175),(240,226),(227,275),(258,325),(247,390),(262,432)]
for a,b in zip(pts,pts[1:]): line(*a,*b,1.0,.8)
for pts2 in [[(240,226),(284,208),(315,177),(364,166)],[(227,275),(190,292),(160,329),(119,337)],[(258,325),(298,341),(323,380)],[(232,130),(200,112),(178,84)],[(215,175),(177,193),(154,230)]]:
    for a,b in zip(pts2,pts2[1:]): line(*a,*b,.65,.65)
rgba=np.empty((N,N,4)); rgba[:,:,:3]=np.array([.22,.11,.12]); rgba[:,:,3]=crack
write('T_TileCrack_Overlay.png',rgba)
