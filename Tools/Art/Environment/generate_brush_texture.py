"""Make a seamless, neutral-centered colored brush mask for Unreal.

Runs with the standard Python 3 library. Marks alter color only, with no
physical bump or paint buildup. Created with layered broken broad strokes,
then smaller strokes, rather than directional noise or plaster damage.
"""
import math
import random
import struct
import zlib
from pathlib import Path

SIZE = 512
random.seed(1957)
pixels = [[128.0, 128.0, 128.0] for _ in range(SIZE * SIZE)]
for count, length, width, opacity in ((180, 70, 20, 14), (350, 37, 10, 11), (500, 15, 4, 8)):
    for _ in range(count):
        cx, cy = random.randrange(SIZE), random.randrange(SIZE)
        rx = random.uniform(length*.5, length)
        ry = random.uniform(width*.5, width)
        angle = random.uniform(-math.pi, math.pi)
        co, si = math.cos(angle), math.sin(angle)
        # Each mark has an independent warm/cool pigment shift, not just a
        # single monochrome cloud. Balanced around neutral when averaged.
        hue = random.choice(((1.0, .45, -.5), (-.45, .05, 1.0),
                             (.9, .75, .45), (-.75, -.55, -.30),
                             (.12, .7, .30), (-.35, -.65, -.75)))
        value = [x * random.uniform(opacity*.65, opacity) for x in hue]
        phase = random.uniform(0, math.tau)
        extent = int(rx + ry + 2)
        for dy in range(-extent, extent + 1):
            for dx in range(-extent, extent + 1):
                u = (dx*co + dy*si)/rx
                v = (-dx*si + dy*co)/ry
                # A broken, asymmetric edge gives each swash an authored shape.
                edge = .83 + .12*math.sin(u*11+phase) + .06*math.sin(u*23-phase)
                if abs(u)<1 and abs(v)<edge:
                    end = min(1.0, (1.0-abs(u))*6.0)
                    softness = min(1.0, (edge-abs(v))*6.0)
                    idx = ((cy+dy)%SIZE)*SIZE + ((cx+dx)%SIZE)
                    for channel in range(3):
                        pixels[idx][channel] += value[channel]*end*softness
rows = bytearray()
for y in range(SIZE):
    rows.append(0)
    for x in range(SIZE):
        rows.extend(max(55, min(200, round(v))) for v in pixels[y*SIZE+x])
def chunk(kind, data):
    return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',SIZE,SIZE,8,2,0,0,0))
png+=chunk(b'IDAT',zlib.compress(bytes(rows),9))+chunk(b'IEND',b'')
output=Path(__file__).resolve().parents[3]/'Art Source/Environment Textures/T_BrushValues.png'
output.parent.mkdir(parents=True,exist_ok=True)
output.write_bytes(png)
print(output)
