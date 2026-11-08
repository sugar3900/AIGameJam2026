"""
Regenerates every dialogue portrait into "Art Source/Portraits/T_Portrait_<Name>.png" (512x512), the source files that
Tools/Editor/import_portraits.py imports as /Game/ICanFixHim/UI/Portraits/T_Portrait_<Name>.

    python3 Tools/Art/Portraits/render_portraits.py [--only Lukey Malcolm ...] [--preview-dir <dir>]

Requires Python 3.9+ with: Pillow, numpy, opencv-python-headless  (pip install pillow numpy opencv-python-headless)

Each hunk is wired to his texture by look.portrait in his dialogue JSON (Content/ICanFixHim/Data/Dialogue/<id>.json);
the player's is PlayerPortraitTexture in Config/DefaultGame.ini.

Framing: a square crop about 1.09x the hair-top-to-chin height, from just above the hair to the top of the neck, face
centred. Backdrops are deep versions of each hunk's look.glow colour, and the halo is the glow colour itself.
"""
import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
CHAR_ART = os.path.join(ROOT, "Art Source", "Character Art")
OUT_DIR = os.path.join(ROOT, "Art Source", "Portraits")

# name: (art folder, crop CX,TOP,SIZE in source px, backdrop, halo, halo strength, extra tuning flags)
HUNKS = {
    # Leaks: deep water teal against his copper curls.
    "Lukey": ("Leaky Pipes", "552,-4,216", "#164B5A", "#4FA8FF", 0.55, []),
    # Black mold, brooding poet: deep moss. The green halo is what separates his black hair from the dark backdrop;
    # the extra flags stop his dark hair / pale face blotching and clear the white showing between loose strands.
    "Malcolm": ("Black Mold", "500,-6,180", "#233D2B", "#6BCF7F", 0.60,
                ["--seed-borders", "--close", "5", "--white-thresh", "0.78", "--fill-pockets", "40",
                 "--flatten", "0.9", "--dark-calm", "0.8", "--dark-only", "--material-ref", "3"]),
    # Pink tile: his glow is pink too, so a hot-pink halo on the game's Plum.
    "Tyler": ("Pink Tile", "555,1,196", "#3B1434", "#FF2E88", 0.55, []),
    # Faulty wiring, flickering lights at night: midnight indigo, yellow spark halo. Wider crop for his big hair.
    "Wyatt": ("Faulty Wiring", "550,-6,210", "#29235E", "#FFD54A", 0.50, []),
    # Lead paint (no dialogue file yet): warm chocolate behind his pale cream look, soft peach halo.
    "LeadPaint": ("Lead Paint", "560,6,204", "#3E2418", "#FFB38A", 0.50, ["--seed-borders", "--material-ref", "4"]),
}
# The heroine: deep rose, keeping the pink identity of the old blush silhouette.
PLAYER = ("#7A2350", "#FF5CA8", "128,10,190")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", nargs="*", help="names to render (default: all hunks + Player)")
    ap.add_argument("--preview-dir", help="also write 210px in-frame previews here")
    a = ap.parse_args()
    names = a.only or list(HUNKS) + ["Player"]
    os.makedirs(OUT_DIR, exist_ok=True)
    for name in names:
        out = os.path.join(OUT_DIR, f"T_Portrait_{name}.png")
        preview = ["--preview", os.path.join(a.preview_dir, f"{name}_in_frame_210.png")] if a.preview_dir else []
        if name == "Player":
            bg, glow, crop = PLAYER
            cmd = [sys.executable, os.path.join(HERE, "player_portrait.py"), out, "--bg", bg, "--glow", glow, "--crop", crop]
        else:
            folder, crop, bg, glow, strength, extra = HUNKS[name]
            src = os.path.join(CHAR_ART, folder, f"{folder}-front.png")
            cmd = [sys.executable, os.path.join(HERE, "toon_portrait.py"), src, out, "--crop", crop, "--bg", bg,
                   "--glow", glow, "--glow-strength", str(strength)] + extra
        subprocess.run(cmd + preview, check=True)


if __name__ == "__main__":
    main()
