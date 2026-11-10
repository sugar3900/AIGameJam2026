"""
The heroine's "You:" dialogue portrait in the same toon style as the hunks (toon_portrait.py): the anonymous bust
silhouette from Tools/Art/player_silhouette.svg (bob with flicks, top bun, bow, neck, shoulders), redrawn at 1024 with
plum light / mid / shadow bands, a hair shine, a 3-tone hot-pink bow, ink outline, pink/gold rim, halo and backdrop.

    python3 Tools/Art/Portraits/player_portrait.py <out.png> [--bg "#7A2350"] [--glow "#FF5CA8"] [--crop 128,10,190]
        [--preview <framed_210.png>]

The crop is in SVG units (viewBox 0..256). It is wider than the hunks' head-only framing on purpose: a faceless head
alone reads as a bell, the neck and shoulders make it read as a person.

Requires Python 3.9+ with: Pillow, numpy, opencv-python-headless  (pip install pillow numpy opencv-python-headless)
If you change the silhouette in player_silhouette.svg, update the shape strings below to match.
"""
import argparse
import os
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from toon_portrait import GOLD, HOTPINK, INK, PINK, PLUM, W, backdrop, rim_masks, save_outputs, smoothstep  # noqa: E402

# Shapes copied from Tools/Art/player_silhouette.svg.
SHOULDERS = "M40 256 C42 212 70 188 106 178 C118 183 138 183 150 178 C186 188 214 212 216 256 Z"
NECK = "M116 140 L140 140 L144 180 C134 186 122 186 112 180 Z"
HAIR = ("M76 106 C74 68 98 50 128 50 C158 50 182 68 180 106 C181 126 184 140 192 150 C181 155 170 152 163 145 "
        "C157 152 148 154 141 151 L115 151 C108 154 99 152 93 145 C86 152 75 155 64 150 C72 140 75 126 76 106 Z")
BUN = (128, 44, 20)
BOW = ["M128 55 L106 44 C100 41 98 58 104 61 Z", "M128 55 L150 44 C156 41 158 58 152 61 Z"]
BOW_KNOT = (128, 55, 6)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out")
    ap.add_argument("--bg", default="#7A2350")
    ap.add_argument("--glow", default="#FF5CA8")
    ap.add_argument("--glow-strength", type=float, default=0.55)
    ap.add_argument("--crop", default="128,10,190", help="CX,TOP,SIZE in SVG units")
    ap.add_argument("--preview", default=None)
    a = ap.parse_args()

    cx, top, size = map(float, a.crop.split(","))
    x0, sc = cx - size / 2, W / size

    def tx(p):
        return ((p[0] - x0) * sc, (p[1] - top) * sc)

    def path_poly(d):
        """Minimal SVG path parser for the absolute M / L / C / Z commands used in the silhouette."""
        for c in "MLCZ":
            d = d.replace(c, f" {c} ")
        toks = d.replace(",", " ").split()
        pts, cur, i, cmd = [], None, 0, None
        while i < len(toks):
            if toks[i] in ("M", "L", "C", "Z"):
                cmd = toks[i]
                i += 1
                if cmd == "Z":
                    continue
            if cmd in ("M", "L"):
                cur = (float(toks[i]), float(toks[i + 1]))
                pts.append(cur)
                i += 2
            elif cmd == "C":
                c1, c2, e = [np.array((float(toks[i + k]), float(toks[i + k + 1]))) for k in (0, 2, 4)]
                p0 = np.array(cur)
                for t in np.linspace(0, 1, 40)[1:]:
                    u = 1 - t
                    pts.append(tuple(u ** 3 * p0 + 3 * u * u * t * c1 + 3 * u * t * t * c2 + t ** 3 * e))
                cur = tuple(e)
                i += 6
        return [tx(p) for p in pts]

    ss = 4  # supersampled rasterisation for smooth masks

    def raster(paths=(), circles=()):
        im = Image.new("L", (W * ss, W * ss), 0)
        d = ImageDraw.Draw(im)
        for p in paths:
            d.polygon([(x * ss, y * ss) for x, y in path_poly(p)], fill=255)
        for ccx, ccy, r in circles:
            (x, y), rr = tx((ccx, ccy)), r * sc
            d.ellipse([(x - rr) * ss, (y - rr) * ss, (x + rr) * ss, (y + rr) * ss], fill=255)
        return np.asarray(im.resize((W, W), Image.LANCZOS)).astype(np.float32) / 255.0

    body = raster([SHOULDERS, NECK, HAIR], [BUN])
    hair = raster([HAIR], [BUN])
    bow = raster(BOW, [BOW_KNOT])
    fg = np.maximum(body, bow)
    fgb = fg > 0.5
    M3 = fg[..., None]
    yy, xx = np.mgrid[0:W, 0:W].astype(np.float32)

    # ---- plum cel fill, keyed from the upper-left (no features: she stays anonymous)
    dist_in = cv2.distanceTransform(fgb.astype(np.uint8), cv2.DIST_L2, 5)
    sm = cv2.GaussianBlur(fg, (0, 0), 60)
    gx = cv2.Sobel(sm, cv2.CV_32F, 1, 0, ksize=5)
    gy = cv2.Sobel(sm, cv2.CV_32F, 0, 1, ksize=5)
    nrm = np.sqrt(gx ** 2 + gy ** 2) + 1e-6
    facing = (gx / nrm) * -0.75 + (-gy / nrm) * -0.65
    shade = np.clip(0.5 + 0.5 * facing * smoothstep(120, 0, dist_in), 0, 1)
    level = (shade > 0.42).astype(np.uint8) + (shade > 0.62)
    level = cv2.medianBlur(level * 100, 21) // 100
    tones = np.stack([PLUM * 0.78, PLUM * 1.15 + 0.02, PLUM * 1.6 + np.array([0.06, 0.02, 0.06])])
    fill = cv2.GaussianBlur(tones[level].astype(np.float32), (0, 0), 2.6)
    # anime hair shine: an arc across the crown
    ccx, ccy = tx((128, 108))
    hl = np.abs(np.hypot(xx - ccx, yy - ccy) - 46 * sc) < 3.2 * sc
    hl &= (yy < tx((0, 84))[1]) & (xx < tx((150, 0))[0])
    hl = cv2.GaussianBlur((hl & (hair > 0.5)).astype(np.float32), (0, 0), 2.0)[..., None]
    fill = fill * (1 - hl * 0.6) + np.clip(PLUM * 2.2 + 0.08, 0, 1) * hl * 0.6

    # ---- bow: 3-tone hot pink (shadow below the knot line, light in the middle of each loop)
    bdist = cv2.distanceTransform((bow > 0.5).astype(np.uint8), cv2.DIST_L2, 5)
    blevel = np.where(yy > tx((0, 57))[1], 0, 1) + (bdist > 10)
    btones = np.stack([HOTPINK * np.array([0.72, 0.55, 0.78]), HOTPINK, np.clip(PINK + 0.15, 0, 1)])
    bfill = cv2.GaussianBlur(btones[np.clip(blevel, 0, 2)].astype(np.float32), (0, 0), 2.6)
    bw = bow[..., None]
    out = fill * (1 - bw) + bfill * bw

    # ---- rim (same rules as the hunks, kept off the bow)
    dist, left, right = rim_masks(fg)
    left = cv2.GaussianBlur(left.astype(np.float32), (0, 0), 1.2)[..., None] * (1 - bw)
    right = cv2.GaussianBlur(right.astype(np.float32), (0, 0), 1.2)[..., None] * (1 - bw)
    out = out * (1 - left * 0.9) + np.clip(PINK + 0.12, 0, 1) * left * 0.9
    out = out * (1 - right * 0.85) + GOLD * right * 0.85

    # ---- ink: silhouette outline + bow outline + hair edge over the neck / shoulders
    def edge_of(m, w):
        mb = (m > 0.5).astype(np.uint8)
        return (mb - cv2.erode(mb, np.ones((w, w), np.uint8))).astype(np.float32)

    ink = cv2.GaussianBlur((dist < 7).astype(np.float32) * fgb, (0, 0), 1.0)
    ink = np.maximum(ink, cv2.GaussianBlur(edge_of(bow, 6), (0, 0), 0.9))
    ink = np.maximum(ink, cv2.GaussianBlur(edge_of(hair, 6), (0, 0), 0.9) * 0.9)
    ink = cv2.GaussianBlur(ink, (0, 0), 0.8)[..., None]
    out = out * (1 - ink) + INK * ink

    # ---- backdrop, halo, and three faint hearts (a nod to the original SVG)
    bg = backdrop(fg, a.bg, a.glow, a.glow_strength)
    hearts = Image.new("L", (W, W), 0)
    hd = ImageDraw.Draw(hearts)
    for hx, hy, s in [(0.13, 0.20, 22), (0.86, 0.30, 16), (0.84, 0.12, 11)]:
        px, py = hx * W, hy * W
        hd.ellipse([px - s, py - s * 0.8, px, py + s * 0.2], fill=255)
        hd.ellipse([px, py - s * 0.8, px + s, py + s * 0.2], fill=255)
        hd.polygon([(px - s * 0.98, py - 0.1 * s), (px + s * 0.98, py - 0.1 * s), (px, py + s * 1.05)], fill=255)
    hm = cv2.GaussianBlur(np.asarray(hearts).astype(np.float32) / 255, (0, 0), 1.2)[..., None] * 0.35
    bg = bg * (1 - hm) + np.clip(PINK + 0.2, 0, 1) * hm

    save_outputs(out * M3 + bg * (1 - M3), a.out, a.preview)


if __name__ == "__main__":
    main()
