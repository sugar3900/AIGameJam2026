"""
Cel-shaded dialogue portrait of a hunk, made from his front turnaround art ("Art Source/Character Art/<Folder>/<Folder>-front.png").

Look: soft 3-tone toon shading (light / mid / purple-tinted shadow), ink lines, a pink rim light from the upper-left and a gold
one from the right, a halo in the hunk's glow colour and a radial backdrop in his own colour. Normally run through
render_portraits.py, which holds the per-hunk crop and colours.

    python3 Tools/Art/Portraits/toon_portrait.py <front.png> <out.png> --crop CX,TOP,SIZE --bg "#164B5A" --glow "#4FA8FF"
        [--preview <framed_210.png>] [per-character tuning flags, see --help]

Requires Python 3.9+ with: Pillow, numpy, opencv-python-headless  (pip install pillow numpy opencv-python-headless)

How it works: the square source crop (about 1.09x the hair-top-to-chin height) is Lanczos-upscaled to a 1024 working size
first, so the ink and rim are drawn at full resolution, then the result is downsampled to 512.
  * mask: flood-fill the white turnaround background from the borders
  * base colour: an edge-preserving flatten of the art (hair / skin / beard stay separate without colour-cluster seams)
  * bands: medium-scale shading compared with its broad surroundings -> 3 levels, small islands merged, edges feathered
  * blue irises and specular pops (eye whites, teeth, tape) are restored from the source
  * ink: XDoG lines on the flattened art + an outline on the silhouette
"""
import argparse
import os

import cv2
import numpy as np
from PIL import Image, ImageDraw

W, OUT_SIZE = 1024, 512


def hexc(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], np.float32) / 255.0


PINK, HOTPINK, PLUM, GOLD = map(hexc, ("#FF5CA8", "#FF2E88", "#3B1434", "#FFC857"))
INK = np.array([0.16, 0.05, 0.14], np.float32)

# Shading constants.
BASE_SIGMA_S, BASE_SIGMA_R, DETAIL_SIGMA, REF_SIGMA = 60, 0.12, 7.0, 40.0
T_LO, T_HI, ISLAND = 0.88, 1.10, 1800
MID_TINT, SH_TINT = np.array([0.86, 0.78, 0.86]), np.array([0.58, 0.45, 0.66])


def lum(c):
    return c[..., 0] * 0.299 + c[..., 1] * 0.587 + c[..., 2] * 0.114


def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def kmeans_colors(c, k, m):
    pts = cv2.cvtColor(c[m].reshape(1, -1, 3).astype(np.float32), cv2.COLOR_RGB2LAB)[0]
    rng = np.random.default_rng(3)
    sel = pts[rng.choice(len(pts), min(60000, len(pts)), replace=False)]
    cv2.setRNGSeed(7)
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.5)
    _, _, centers = cv2.kmeans(sel, k, None, crit, 4, cv2.KMEANS_PP_CENTERS)
    full = cv2.cvtColor(c.reshape(1, -1, 3).astype(np.float32), cv2.COLOR_RGB2LAB)[0]
    idx = ((full[:, None, :] - centers[None]) ** 2).sum(-1).argmin(1).reshape(c.shape[:2])
    return idx, cv2.cvtColor(centers[None].astype(np.float32), cv2.COLOR_LAB2RGB)[0]


def mode_filter(idx, k, r):
    votes = np.stack([cv2.boxFilter((idx == i).astype(np.float32), -1, (2 * r + 1, 2 * r + 1)) for i in range(k)])
    return votes.argmax(0)


def rim_masks(fg):
    """Pink (upper-left) and gold (right) rim bands just inside the silhouette, plus the inside distance field."""
    fgb = fg > 0.5
    dist = cv2.distanceTransform(fgb.astype(np.uint8), cv2.DIST_L2, 5)
    band = smoothstep(26, 20, dist).astype(np.float32)        # ~10px at 512
    sm = cv2.GaussianBlur(fg, (0, 0), 14)
    gx = cv2.GaussianBlur(cv2.Sobel(sm, cv2.CV_32F, 1, 0, ksize=5), (0, 0), 16)
    gy = cv2.GaussianBlur(cv2.Sobel(sm, cv2.CV_32F, 0, 1, ksize=5), (0, 0), 16)
    nrm = np.sqrt(gx ** 2 + gy ** 2) + 1e-6
    nx, ny = -gx / nrm, -gy / nrm                              # outward normal
    left = smoothstep(0.10, 0.30, -nx * 0.85 - ny * 0.5) * band
    right = smoothstep(0.20, 0.40, nx * 0.95 - ny * 0.3) * band
    return dist, left, right


def backdrop(fg, bg_hex, glow_hex, glow_strength):
    """Radial backdrop in the character's colour plus a halo in his glow colour around the silhouette."""
    bgc, glowc = hexc(bg_hex), hexc(glow_hex)
    yy, xx = np.mgrid[0:W, 0:W] / W
    r = np.clip(np.sqrt((xx - 0.5) ** 2 + (yy - 0.35) ** 2) / 0.75, 0, 1) ** 1.4
    bg = np.clip(bgc * 1.85, 0, 1) * (1 - r[..., None]) + bgc * 0.75 * r[..., None]
    glow = cv2.GaussianBlur(fg, (0, 0), 36)[..., None]
    return bg + glowc * glow * (1 - fg[..., None]) * glow_strength


def save_outputs(res, out_path, preview_path=None):
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    final = Image.fromarray((np.clip(res, 0, 1) * 255).astype(np.uint8)).resize((OUT_SIZE, OUT_SIZE), Image.LANCZOS)
    final.save(out_path)
    print(out_path)
    if preview_path:
        framed_preview(final).save(preview_path)
        print(preview_path)


def framed_preview(final):
    """The portrait as the dialogue widget shows it: 210x210 SizeBox, Plum rounded border (r20) with a 4px HotPink
    outline, 6px padding, on the Cream panel. Preview only - the game draws the frame itself."""
    S, SS = 210, 4
    big = Image.new("RGBA", (S * SS, S * SS), (0, 0, 0, 0))
    dr = ImageDraw.Draw(big)
    dr.rounded_rectangle([0, 0, S * SS - 1, S * SS - 1], 20 * SS, fill=tuple((HOTPINK * 255).astype(int)))
    dr.rounded_rectangle([4 * SS, 4 * SS, (S - 4) * SS - 1, (S - 4) * SS - 1], 16 * SS, fill=tuple((PLUM * 255).astype(int)))
    inner = S - 12
    tile = final.resize((inner * SS, inner * SS), Image.LANCZOS).convert("RGBA")
    m = Image.new("L", (inner * SS, inner * SS), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, inner * SS - 1, inner * SS - 1], 14 * SS, fill=255)
    big.paste(tile, (6 * SS, 6 * SS), m)
    framed = big.resize((S, S), Image.LANCZOS)
    panel = Image.new("RGBA", (S, S), (255, 247, 240, 255))
    panel.alpha_composite(framed)
    return panel.convert("RGB")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--crop", required=True, help="CX,TOP,SIZE: square crop in source pixels (TOP may be negative)")
    ap.add_argument("--bg", default="#3B1434", help="backdrop colour; centre lifted ~1.85x, edges 0.75x")
    ap.add_argument("--glow", default="#FF2E88", help="halo colour behind the silhouette")
    ap.add_argument("--glow-strength", type=float, default=0.55)
    ap.add_argument("--preview", default=None, help="also write a 210px in-frame preview here")
    # per-character tuning (defaults suit most art; Malcolm's dark hair needs the extras)
    ap.add_argument("--material-ref", type=int, default=0,
                    help="N>0: compare shading only within N material groups (stops dark hair / pale skin bleeding)")
    ap.add_argument("--fill-pockets", type=int, default=0,
                    help="treat near-white blobs >= this many px (at 1024) near the background as background")
    ap.add_argument("--flatten", type=float, default=0.0, help="0..1 pull materials toward one flat colour")
    ap.add_argument("--dark-only", action="store_true", help="--flatten applies only to dark materials")
    ap.add_argument("--dark-calm", type=float, default=0.0, help="0..1 reduce band contrast in dark materials")
    ap.add_argument("--close", type=int, default=13, help="mask closing kernel (smaller keeps gaps between hair strands)")
    ap.add_argument("--white-thresh", type=float, default=0.92, help="background whiteness threshold")
    ap.add_argument("--seed-borders", action="store_true", help="flood the background from every border pixel")
    ap.add_argument("--no-iris", action="store_true", help="skip the blue-iris restore")
    a = ap.parse_args()

    cx, top, size = map(int, a.crop.split(","))
    x0 = cx - size // 2

    # ---- crop (white padding outside the image), upscale first
    src = np.asarray(Image.open(a.src).convert("RGB"))
    pad = np.full((size, size, 3), 255, np.uint8)
    sy0, sy1 = max(0, top), min(src.shape[0], top + size)
    sx0, sx1 = max(0, x0), min(src.shape[1], x0 + size)
    pad[sy0 - top:sy1 - top, sx0 - x0:sx1 - x0] = src[sy0:sy1, sx0:sx1]
    img = np.asarray(Image.fromarray(pad).resize((W, W), Image.LANCZOS)).astype(np.float32) / 255.0
    img = np.clip(img + 0.6 * (img - cv2.GaussianBlur(img, (0, 0), 2.5)), 0, 1)   # firm up the soft upscale

    # ---- mask: flood the white background
    ff = ((img.min(2) > a.white_thresh) & (img.max(2) - img.min(2) < 0.07)).astype(np.uint8)
    flood = np.zeros((W + 2, W + 2), np.uint8)
    seeds = [(0, 0), (W - 1, 0), (W // 2, 0), (0, W // 2), (W - 1, W // 2), (0, W - 1), (W - 1, W - 1)]
    if a.seed_borders:
        seeds = [(x, y) for x in range(0, W, 4) for y in (0, W - 1)] + [(x, y) for y in range(0, W, 4) for x in (0, W - 1)]
    for seed in seeds:
        if ff[seed[1], seed[0]] == 1:
            cv2.floodFill(ff, flood, seed, 2)
    if a.fill_pockets:
        near = cv2.dilate((ff == 2).astype(np.uint8), np.ones((45, 45), np.uint8))
        nl, lab, st, _ = cv2.connectedComponentsWithStats((ff == 1).astype(np.uint8), connectivity=8)
        for j in range(1, nl):
            if st[j, cv2.CC_STAT_AREA] >= a.fill_pockets:
                comp = lab == j
                if (near[comp] > 0).any():
                    ff[comp] = 2
    fg = (ff != 2).astype(np.uint8)
    fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((7, 7), np.uint8))
    fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, np.ones((a.close, a.close), np.uint8))
    _, lab, stats, _ = cv2.connectedComponentsWithStats(fg)
    fg = (lab == 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])).astype(np.float32)
    fg = smoothstep(0.35, 0.65, cv2.GaussianBlur(fg, (0, 0), 1.5)).astype(np.float32)
    fgb = fg > 0.5
    M3 = fg[..., None]

    # ---- flattened art (for shading detail and ink)
    flat = cv2.bilateralFilter((img * 255).astype(np.uint8), 15, 35, 12)
    for _ in range(3):
        flat = cv2.bilateralFilter(flat, 15, 28, 12)
    flat_f = flat.astype(np.float32) / 255.0
    L = lum(flat_f)

    # ---- base colour + 3 bands
    base8 = cv2.edgePreservingFilter((img * 255).astype(np.uint8), flags=cv2.RECURS_FILTER,
                                     sigma_s=BASE_SIGMA_S, sigma_r=BASE_SIGMA_R)
    base8 = cv2.edgePreservingFilter(base8, flags=cv2.RECURS_FILTER, sigma_s=BASE_SIGMA_S, sigma_r=BASE_SIGMA_R)
    base = base8.astype(np.float32) / 255.0
    Lm = cv2.GaussianBlur(L, (0, 0), DETAIL_SIGMA)
    ref = cv2.GaussianBlur(L * fg, (0, 0), REF_SIGMA) / np.maximum(cv2.GaussianBlur(fg, (0, 0), REF_SIGMA), 1e-3)
    if a.material_ref:
        km = a.material_ref
        midx = mode_filter(kmeans_colors(base, km, fgb)[0], km, 6)
        ref = np.zeros_like(L)
        for k in range(km):
            mk = ((midx == k) & fgb).astype(np.float32)
            rk = cv2.GaussianBlur(L * mk, (0, 0), REF_SIGMA) / np.maximum(cv2.GaussianBlur(mk, (0, 0), REF_SIGMA), 1e-3)
            ref[midx == k] = rk[midx == k]
    ratio = Lm / np.maximum(ref, 0.04)
    level = (ratio > T_LO).astype(np.uint8) + (ratio > T_HI)
    level = cv2.medianBlur(level * 100, 21) // 100
    for v in range(3):
        nl, lab, st, _ = cv2.connectedComponentsWithStats(((level == v) & fgb).astype(np.uint8), connectivity=4)
        for j in range(1, nl):
            if st[j, cv2.CC_STAT_AREA] < ISLAND:
                isl = lab == j
                ring = cv2.dilate(isl.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool) & ~isl
                if ring.any():
                    level[isl] = np.bincount(level[ring], minlength=3).argmax()
    tint = np.stack([SH_TINT * 0.95, MID_TINT * 1.02, np.ones(3) * 1.12])[level].astype(np.float32)
    tint = cv2.GaussianBlur(tint, (0, 0), 2.6)
    if a.flatten or a.dark_calm:
        km = max(a.material_ref, 4)
        midx2 = mode_filter(kmeans_colors(base, km, fgb)[0], km, 6)
        flatc = np.zeros_like(base)
        for k in range(km):
            sel = (midx2 == k) & fgb
            if sel.any():
                flatc[midx2 == k] = np.median(base[sel], axis=0)
        flatc = cv2.GaussianBlur(flatc, (0, 0), 2.0)
        darkm = smoothstep(0.30, 0.15, cv2.GaussianBlur(lum(flatc), (0, 0), 3))[..., None]
        wf = a.flatten * (darkm if a.dark_only else 1.0)
        base = base * (1 - wf) + flatc * wf
        if a.dark_calm:
            tint = tint * (1 - darkm * a.dark_calm) + MID_TINT * 1.02 * darkm * a.dark_calm
    lifted = np.clip(base * 1.08 + 0.02, 0, 1)
    out = np.minimum(lifted * tint, lifted + (1 - lifted) * 0.45)   # pale skin never blows out to white

    # ---- details restored from the source
    spec = cv2.GaussianBlur(smoothstep(0.84, 0.94, lum(img)).astype(np.float32), (0, 0), 1.0)[..., None] * M3
    out = out * (1 - spec) + np.clip(img * 1.04, 0, 1) * spec
    if not a.no_iris:
        blue = ((img[..., 2] - img[..., 0]) > 0.10) & ((img[..., 2] - img[..., 1]) > -0.02) & fgb
        blue = cv2.morphologyEx(blue.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)).astype(np.float32)
        blue = cv2.GaussianBlur(blue, (0, 0), 1.2)[..., None]
        iris = cv2.GaussianBlur(img, (0, 0), 1.0)
        iris_q = np.where(lum(iris)[..., None] > 0.45, iris * 1.1, iris * 0.85)
        out = out * (1 - blue) + np.clip(iris_q, 0, 1) * blue

    # ---- rim light
    dist, left, right = rim_masks(fg)
    left = cv2.GaussianBlur(left.astype(np.float32), (0, 0), 1.2)[..., None]
    right = cv2.GaussianBlur(right.astype(np.float32), (0, 0), 1.2)[..., None]
    out = out * (1 - left * 0.9) + np.clip(PINK + 0.12, 0, 1) * left * 0.9
    out = out * (1 - right * 0.85) + GOLD * right * 0.85

    # ---- ink: XDoG on the flattened art + silhouette outline (~3.5px at 512)
    gray = lum(flat_f).astype(np.float32)
    d = cv2.GaussianBlur(gray, (0, 0), 1.8) - 0.982 * cv2.GaussianBlur(gray, (0, 0), 1.8 * 1.6)
    ink = (1 - np.clip(np.where(d >= 0, 1.0, 1.0 + np.tanh(40 * d)), 0, 1)) * fg
    nl, lab, stats, _ = cv2.connectedComponentsWithStats((ink > 0.5).astype(np.uint8), connectivity=8)
    keep = np.zeros(nl, bool)
    keep[1:] = stats[1:, cv2.CC_STAT_AREA] >= 160
    ink = ink * keep[lab] * 0.88
    ink = np.maximum(ink, cv2.GaussianBlur((dist < 7).astype(np.float32) * fgb, (0, 0), 1.0))
    ink = cv2.GaussianBlur(ink.astype(np.float32), (0, 0), 0.8)[..., None]
    out = out * (1 - ink) + INK * ink

    res = out * M3 + backdrop(fg, a.bg, a.glow, a.glow_strength) * (1 - M3)
    save_outputs(res, a.out, a.preview)


if __name__ == "__main__":
    main()
