#!/usr/bin/env python3
"""
Rebuild the recorded sound effects in "Art Source/Audio/SFX" from their original downloads, using the edit recipes in
"Art Source/Audio/SFX/recorded.json". Needs numpy, scipy and soundfile (pip install soundfile; it decodes .wav/.ogg/.mp3).

    python3 Tools/Audio/process_recorded_sfx.py --src-root <dir with the downloads>            # every recorded file
    python3 Tools/Audio/process_recorded_sfx.py --src-root <dir> --only Fridge                  # names containing "Fridge"
    python3 Tools/Audio/process_recorded_sfx.py --src-root <dir> --check                        # only report missing sources

This script never downloads or runs anything. Fetch the originals yourself from the URLs in recorded.json ("sources":
page / file_url, or archive + member for Kenney zips) and lay them out under --src-root at each source's "local" path,
e.g. <src-root>/bigsoundbank/0036/sound.wav, <src-root>/freesound/541762/preview.mp3,
<src-root>/kenney-rpg-audio/x/Audio/doorOpen_1.ogg.

Recipe ("files" -> "SFX_<Cue>[_N].wav" -> "edit"):
    layers   list of {src, start, end, at=0, gain_db=0, pitch=0 (semitones, resample), pitch_end (glide to this many
             semitones by the end of the layer), fade_in=0.002, fade_out=0.01, highpass, lowpass (Hz)}; each layer is
             cut from its source (seconds), processed and mixed at `at` seconds.
    highpass Hz on the mix (default 40; also removes DC)          lowpass   Hz on the mix (optional)
    onset_db start the file where the mix first rises above this level relative to its peak (default -36)
    tail_db  end the file where it last stays above this level (default -54)     max_len  hard cap in seconds
    fade_out seconds of fade at the end (default 0.03)            peak      final peak level (0..1)
Output: 44.1 kHz, 16-bit, mono WAV.
"""
import argparse
import json
import os
import sys
import wave

import numpy as np

SR = 44100
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SFX_DIR = os.path.join(ROOT, "Art Source/Audio/SFX")
RECORDED = os.path.join(SFX_DIR, "recorded.json")


def load(path):
    import soundfile as sf
    from scipy.signal import resample_poly

    y, sr = sf.read(path, always_2d=True, dtype="float64")
    y = y.mean(axis=1)
    if sr != SR:
        g = np.gcd(int(sr), SR)
        y = resample_poly(y, SR // g, int(sr) // g)
    return y


def filt(y, kind, hz):
    from scipy.signal import butter, sosfilt

    if not hz or len(y) < 16:
        return y
    return sosfilt(butter(2, hz, kind, fs=SR, output="sos"), y)


def repitch(y, semis, semis_end=None):
    """Resample to shift pitch (and length). With semis_end, the shift glides linearly across the clip."""
    if not semis and semis_end is None:
        return y
    s0 = semis or 0.0
    s1 = s0 if semis_end is None else semis_end
    n = len(y)
    # The read position advances by 2^(semis/12) per output sample; semis glides across the output.
    out_len = int(n / np.mean(2 ** (np.linspace(s0, s1, 64) / 12))) + 2
    rates = 2 ** (np.linspace(s0, s1, out_len) / 12)
    pos = np.concatenate([[0.0], np.cumsum(rates)[:-1]])
    pos = pos[pos < n - 1]
    return np.interp(pos, np.arange(n), y)


def fades(y, fi, fo):
    y = y.copy()
    a, b = min(len(y), int(fi * SR)), min(len(y), int(fo * SR))
    if a > 1:
        y[:a] *= np.linspace(0, 1, a)
    if b > 1:
        y[-b:] *= np.linspace(1, 0, b) ** 1.5
    return y


def render(edit, sources, src_root, cache):
    parts = []
    for L in edit["layers"]:
        src = sources[L["src"]]
        path = os.path.join(src_root, src["local"])
        if path not in cache:
            cache[path] = load(path)
        y = cache[path]
        seg = y[int(L.get("start", 0) * SR): int(L["end"] * SR) if "end" in L else None]
        seg = filt(seg, "highpass", L.get("highpass"))
        seg = filt(seg, "lowpass", L.get("lowpass"))
        seg = repitch(seg, L.get("pitch", 0), L.get("pitch_end"))
        seg = fades(seg, L.get("fade_in", 0.002), L.get("fade_out", 0.01)) * 10 ** (L.get("gain_db", 0) / 20)
        parts.append((int(L.get("at", 0) * SR), seg))
    n = max(i + len(s) for i, s in parts)
    mix = np.zeros(n)
    for i, s in parts:
        mix[i:i + len(s)] += s

    mix = filt(mix - mix.mean(), "highpass", edit.get("highpass", 40))
    mix = filt(mix, "lowpass", edit.get("lowpass"))
    env = np.abs(mix)
    pk = env.max()
    # Onset: first sample above onset_db; keep 1 ms of pre-roll so the transient isn't chopped.
    above = np.nonzero(env > pk * 10 ** (edit.get("onset_db", -36) / 20))[0]
    start = max(0, above[0] - int(0.001 * SR))
    # Tail: last 10 ms block whose RMS is above tail_db.
    hop = int(0.01 * SR)
    m = len(mix) // hop
    rms = np.sqrt(np.mean(mix[:m * hop].reshape(m, hop) ** 2, axis=1) + 1e-20)
    loud = np.nonzero(rms > rms.max() * 10 ** (edit.get("tail_db", -54) / 20))[0]
    end = min(len(mix), (loud[-1] + 2) * hop)
    mix = mix[start:end]
    if "max_len" in edit:
        mix = mix[: int(edit["max_len"] * SR)]
    mix = fades(mix - mix.mean(), 0.0015, edit.get("fade_out", 0.03))
    return mix / np.max(np.abs(mix)) * edit["peak"]


def write_wav(path, y):
    pcm = (np.clip(y, -1, 1) * 32767).round().astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src-root", required=True, help="directory holding the downloaded originals at their 'local' paths")
    ap.add_argument("--only", help="only files whose name contains this")
    ap.add_argument("--check", action="store_true", help="list missing source files and exit")
    args = ap.parse_args()

    with open(RECORDED, encoding="utf-8") as f:
        data = json.load(f)
    sources, files = data["sources"], data["files"]
    missing = sorted({os.path.join(args.src_root, sources[L["src"]]["local"])
                      for name, e in files.items() for L in e["edit"]["layers"]
                      if not os.path.exists(os.path.join(args.src_root, sources[L["src"]]["local"]))})
    if missing:
        print("missing sources:\n  " + "\n  ".join(missing))
        if args.check or not args.only:
            sys.exit(1)
    if args.check:
        print(f"all {len(sources)} sources present")
        return

    cache = {}
    for name, entry in sorted(files.items()):
        if args.only and args.only.lower() not in name.lower():
            continue
        y = render(entry["edit"], sources, args.src_root, cache)
        write_wav(os.path.join(SFX_DIR, name), y)
        print(f"{name:28s} {len(y) / SR:5.2f}s  peak {np.max(np.abs(y)):.2f}")


if __name__ == "__main__":
    main()
