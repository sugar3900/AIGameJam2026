#!/usr/bin/env python3
"""
Compose and synthesize the game's background music (python3 + numpy + stdlib wave only; deterministic, no downloads).

    python3 Tools/Audio/generate_bgm.py                 # writes every track
    python3 Tools/Audio/generate_bgm.py --only Tyler    # one track (name or BGM_ name)

Then import into Unreal:

    UnrealEditor-Cmd ICanFixHim.uproject -ExecutePythonScript=<abs>/Tools/Editor/import_bgm.py -unattended -nullrhi

Output: "Art Source/Audio/BGM/BGM_<Name>.wav" (44.1 kHz, 16-bit stereo, peak about -3 dBFS) plus manifest.json with
key/tempo/length/peak/RMS/seam metrics. The game plays them by name through Audio/FixHimMusicSubsystem.

How it works
  * Each track is a 32-bar form (four 8-bar blocks, e.g. A A' B A'') with a hand-picked key, tempo, swing and chord
    progression per block. Bass, comp, pad, countermelody, melody, arps and percussion are generated from the chords
    by small seeded rules (chord tones on strong beats, stepwise motion, chromatic approach notes as "spice").
  * Every layer has a gain per 8-bar block, so tracks breathe and build instead of looping one texture.
  * The whole mix is rendered CIRCULARLY: notes that ring past the last bar are overlap-added into the first bar, and
    filters/reverb are FFT based (circular), so the loop point is seamless by construction.
"""
import argparse
import json
import os
import wave

import numpy as np

SR = 44100
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "Art Source/Audio/BGM")
PEAK_DB = -3.0
BARS = 32
LOW_TRIM = 0.6


# ---------------------------------------------------------------------------
# Theory

NOTE_PC = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
QUAL = {
    "": [0, 4, 7], "m": [0, 3, 7], "6": [0, 4, 7, 9], "m6": [0, 3, 7, 9], "7": [0, 4, 7, 10], "m7": [0, 3, 7, 10],
    "maj7": [0, 4, 7, 11], "mmaj7": [0, 3, 7, 11], "dim7": [0, 3, 6, 9], "m7b5": [0, 3, 6, 10], "7b9": [0, 4, 7, 10, 13],
    "sus4": [0, 5, 7], "7sus": [0, 5, 7, 10], "add9": [0, 4, 7, 14], "9": [0, 4, 7, 10, 14], "m9": [0, 3, 7, 10, 14],
}


def parse_chord(s):
    root = NOTE_PC[s[0]]
    i = 1
    if i < len(s) and s[i] in "#b":
        root += 1 if s[i] == "#" else -1
        i += 1
    return root % 12, s[i:]


def scale_pcs(tonic, intervals):
    return {(tonic + i) % 12 for i in intervals}


MAJOR = [0, 2, 4, 5, 7, 9, 11]
MINOR = [0, 2, 3, 5, 7, 8, 10]
HARM_MINOR = [0, 2, 3, 5, 7, 8, 11]


def mtof(m):
    return 440.0 * 2.0 ** ((np.asarray(m, dtype=float) - 69.0) / 12.0)


# ---------------------------------------------------------------------------
# DSP basics (everything works on float64 arrays at SR)

def _t(n):
    return np.arange(n) / SR


def fft_filter(x, lo=None, hi=None, order=2):
    """Zero-phase Butterworth-magnitude band filter via FFT (circular). lo = highpass corner, hi = lowpass corner."""
    n = x.shape[-1]
    X = np.fft.rfft(x, axis=-1)
    f = np.fft.rfftfreq(n, 1.0 / SR)
    H = np.ones_like(f)
    if hi:
        H = H / np.sqrt(1.0 + (f / hi) ** (2 * order))
    if lo:
        H = H / np.sqrt(1.0 + (lo / np.maximum(f, 1e-3)) ** (2 * order))
    return np.fft.irfft(X * H, n, axis=-1)


def lfo(n, cycles, phase=0.0):
    """0..1 sine with a whole number of cycles per loop (so it is seamless)."""
    return 0.5 + 0.5 * np.sin(2 * np.pi * cycles * np.arange(n) / n + phase)


def edges(a, n_in=24, n_out=96):
    n = a.shape[-1]
    if n > n_in:
        a[..., :n_in] *= np.linspace(0, 1, n_in)
    if n > n_out:
        a[..., -n_out:] *= np.linspace(1, 0, n_out)
    return a


def tonal(fn):
    """Cache rendered notes: identical (pitch, length, velocity) notes are synthesized once."""
    cache = {}

    def wrapped(f, dur, vel, i=0):
        key = (round(float(f), 2), round(dur, 3), round(vel, 2))
        if key not in cache:
            cache[key] = fn(float(f), dur, vel)
        return cache[key]
    return wrapped


def note_off(t, dur, rel):
    """Multiplier that damps the sound after the note ends."""
    return np.where(t > dur, np.exp(-(t - dur) * (6.0 / max(rel, 1e-3))), 1.0)


# ---------------------------------------------------------------------------
# Instruments. Each factory returns inst(freq, dur_seconds, velocity, event_index) -> mono (n,) or stereo (2, n).

def pluck(rate=7.0, bright=0.8, nh=9, rel=0.1, click=0.06, tilt=1.0, octave=0.0):
    """Additive plucked string: harmonics decay faster the higher they are (Karplus-Strong flavour)."""
    @tonal
    def fn(f, dur, vel):
        n = max(int(min(dur + rel, 7.0 / rate) * SR), int(0.06 * SR))
        t = _t(n)
        y = np.zeros(n)
        for k in range(1, nh + 1):
            if f * k > 14000:
                break
            y += (1.0 / k ** tilt) * np.sin(2 * np.pi * f * k * t) * np.exp(-t * rate * (1 + bright * (k - 1)))
        if octave:
            y += octave * np.sin(2 * np.pi * f * 2 * t) * np.exp(-t * rate * 2.2)
        y *= np.minimum(1, t / 0.002)
        if click:
            y += click * np.sin(2 * np.pi * min(f * 4, 5000) * t) * np.exp(-t * 480)
        return edges(y * note_off(t, dur, rel) * vel)
    return fn


def bell(ratios, amps, rates, trem=0.0, trem_hz=5.0, rel=0.4, detune_cents=0.0, cap=3.0):
    """Inharmonic/struck partials: celesta, music box, vibraphone (with tremolo), marimba."""
    @tonal
    def fn(f, dur, vel):
        f = f * 2 ** (detune_cents / 1200.0)
        n = max(int(min(dur + rel, min(6.0 / min(rates), cap)) * SR), int(0.08 * SR))
        t = _t(n)
        y = np.zeros(n)
        for j, (r, a, k) in enumerate(zip(ratios, amps, rates)):
            if f * r > 15000:
                continue
            y += a * (vel ** (0.6 * j)) * np.sin(2 * np.pi * f * r * t) * np.exp(-k * t)
        if trem:
            y *= 1.0 - trem * 0.5 + trem * 0.5 * np.sin(2 * np.pi * trem_hz * t)
        y *= np.minimum(1, t / 0.0015)
        return edges(y * note_off(t, dur, rel) * vel)
    return fn


def celesta(**kw):
    return bell([1, 2.001, 4.0, 5.95], [1, .55, .25, .12], [2.2, 4.0, 7.0, 11.0], rel=0.35, **kw)


def music_box(**kw):
    return bell([1, 2.0, 3.01, 6.0], [1, .45, .2, .1], [2.8, 5.0, 9.0, 16.0], rel=0.25, **kw)


def vibes(trem=0.3, **kw):
    return bell([1, 3.99, 9.9], [1, .35, .08], [1.3, 3.2, 6.0], trem=trem, rel=0.5, cap=3.5, **kw)


def marimba(**kw):
    return bell([1, 3.98, 9.7], [1, .3, .1], [5.0, 22.0, 40.0], rel=0.12, cap=1.6, **kw)


def eerie_bell(**kw):
    return bell([1, 2.76, 5.4, 8.93], [1, .5, .25, .12], [1.4, 3.0, 6.0, 10.0], rel=0.8, cap=4.0, **kw)


def ep(arate=3.0, index=1.4, irate=5.0, tine=0.25, rel=0.15):
    """Muted electric piano (two-operator FM with a short tine)."""
    @tonal
    def fn(f, dur, vel):
        n = max(int(min(dur + rel, 6.0 / arate) * SR), int(0.08 * SR))
        t = _t(n)
        ph = 2 * np.pi * f * t
        idx = index * vel * np.exp(-irate * t)
        y = np.sin(ph + idx * np.sin(ph)) * np.exp(-arate * t)
        if f * 5 < 14000:
            y += tine * vel * np.sin(2 * np.pi * f * 5 * t) * np.exp(-t * 18)
        y *= np.minimum(1, t / 0.002)
        return edges(y * note_off(t, dur, rel) * vel)
    return fn


def _saw_stack(f, t, nharm, cut, tilt, phases, formant=None):
    y = np.zeros_like(t)
    for k in range(1, nharm + 1):
        fk = f * k
        if fk > 12000:
            break
        a = 1.0 / k ** tilt / np.sqrt(1.0 + (fk / cut) ** 4)
        if formant:
            a *= sum(g * np.exp(-0.5 * ((fk - F) / B) ** 2) for F, B, g in formant) + 0.02
        y += a * np.sin(2 * np.pi * fk * t + phases[k % len(phases)])
    return y


def pad(att=0.5, rel=0.9, cut=2400, detune=(-9, 0, 9), nharm=14, tilt=1.0, vib=0.0, formant=None, seed=5):
    """Detuned saw (or formant 'ooh') pad: stereo, slow attack."""
    ph = np.random.default_rng(seed).uniform(0, 2 * np.pi, (3, 32))

    @tonal
    def fn(f, dur, vel):
        n = int((dur + rel) * SR)
        t = _t(n)
        tt = t + vib * (1 - np.cos(2 * np.pi * 5.2 * t)) / (2 * np.pi * 5.2) if vib else t
        env = np.minimum(1, t / att) ** 1.5
        env = env * np.where(t > dur, np.maximum(0, 1 - (t - dur) / rel) ** 2, 1.0)
        out = np.zeros((2, n))
        for side, vs in ((0, (0, 1)), (1, (1, 2))):
            for v in vs:
                out[side] += _saw_stack(f * 2 ** (detune[v] / 1200.0), tt, nharm, cut, tilt, ph[v], formant)
        return edges(out * env * vel * 0.5)
    return fn


def ooh_pad(**kw):
    return pad(formant=[(330, 110, 1.0), (850, 170, 0.5), (2500, 300, 0.05)], cut=3000, nharm=24, tilt=0.8, vib=0.004, att=0.35, rel=0.7, **kw)


def upright(rate=4.0, h2=0.55, h3=0.22, click=0.12, rel=0.08):
    @tonal
    def fn(f, dur, vel):
        n = max(int(min(dur + rel, 3.0) * SR), int(0.1 * SR))
        t = _t(n)
        ph = 2 * np.pi * f * t
        y = np.sin(ph) * np.exp(-rate * t) + h2 * np.sin(2 * ph) * np.exp(-rate * 1.6 * t) + h3 * np.sin(3 * ph) * np.exp(-rate * 2.5 * t)
        y *= np.minimum(1, t / 0.004)
        y += click * np.sin(2 * np.pi * f * 5 * t) * np.exp(-t * 90)
        return edges(y * note_off(t, dur, rel) * vel)
    return fn


def sub_bass(glide=1.0, tau=0.06, drive=2.2, rel=0.14, decay=1.0):
    """Slinky sub: sine through soft saturation, sliding up into each note."""
    @tonal
    def fn(f, dur, vel):
        n = int((dur + rel) * SR)
        t = _t(n)
        fr = f * 2.0 ** (-glide * np.exp(-t / tau) / 12.0)
        ph = 2 * np.pi * np.cumsum(fr) / SR
        y = np.tanh(drive * np.sin(ph)) / np.tanh(drive) + 0.22 * np.sin(2 * ph) * np.exp(-t * 3)
        y *= np.minimum(1, t / 0.008) * np.exp(-t * decay)
        return edges(y * note_off(t, dur, rel) * vel)
    return fn


def pulse(pw=0.3, rate=9.0, nh=14, vib=0.0, rel=0.04, sustain=0.0):
    """Buzzy pulse-wave synth (arps and leads)."""
    @tonal
    def fn(f, dur, vel):
        n = max(int(min(dur + rel, 4.0) * SR), int(0.05 * SR))
        t = _t(n)
        tt = t + vib * (1 - np.cos(2 * np.pi * 5.8 * t)) / (2 * np.pi * 5.8) if vib else t
        y = np.zeros(n)
        for k in range(1, nh + 1):
            if f * k > 12000:
                break
            y += (np.sin(np.pi * k * pw) / k) * np.sin(2 * np.pi * f * k * tt + np.pi * k * pw)
        env = sustain + (1 - sustain) * np.exp(-rate * t)
        y *= env * np.minimum(1, t / 0.002)
        return edges(y * note_off(t, dur, rel) * vel)
    return fn


def drop(rate=26.0, tau=0.03):
    """Water drip 'bloop': a sine sliding up, with a quick decay."""
    @tonal
    def fn(f, dur, vel):
        n = int(0.45 * SR)
        t = _t(n)
        fr = f * (0.55 + 0.45 * (1 - np.exp(-t / tau)))
        ph = 2 * np.pi * np.cumsum(fr) / SR
        y = np.sin(ph) * np.exp(-rate * t) + 0.25 * np.sin(2 * ph) * np.exp(-rate * 1.5 * t)
        y *= np.minimum(1, t / 0.002)
        return edges(y * vel)
    return fn


def zap():
    def fn(f, dur, vel, i=0):
        rng = np.random.default_rng(100 + i)
        n = int(0.2 * SR)
        t = _t(n)
        fr = 5200 * np.exp(-t * (14 + (i % 3) * 5)) + 400
        y = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 16)
        y += 0.5 * fft_filter(rng.normal(size=n), lo=3500) * np.exp(-t * 35)
        return edges(y * vel * 0.8)
    return fn


# --- percussion (templates are built once with fixed seeds; events pick a variant by index) ---

def _drum(builder, variants=3):
    temps = [builder(np.random.default_rng(900 + v)) for v in range(variants)]

    def fn(f, dur, vel, i=0):
        return temps[i % variants] * vel
    return fn


def kick(punch=1.0):
    def build(rng):
        n = int(0.3 * SR)
        t = _t(n)
        fr = 46 + 90 * punch * np.exp(-t * 40)
        y = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 12) * np.minimum(1, t / 0.0015)
        y += 0.12 * fft_filter(rng.normal(size=n), lo=800, hi=4000) * np.exp(-t * 300)
        return edges(y, 8, 200)
    return _drum(build)


def snare():
    def build(rng):
        n = int(0.25 * SR)
        t = _t(n)
        y = fft_filter(rng.normal(size=n), lo=1200, hi=7500) * np.exp(-t * 22) * 0.6
        y += 0.45 * np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30)
        return edges(y, 8, 200)
    return _drum(build)


def brush():
    def build(rng):
        n = int(0.32 * SR)
        t = _t(n)
        y = fft_filter(rng.normal(size=n), lo=1500, hi=8000) * (1 - np.exp(-t / 0.025)) * np.exp(-t * 9) * 0.7
        return edges(y, 8, 300)
    return _drum(build)


def hat(open_=False):
    def build(rng):
        n = int((0.38 if open_ else 0.09) * SR)
        t = _t(n)
        y = fft_filter(rng.normal(size=n), lo=6500) * np.exp(-t * (11 if open_ else 65)) * 0.6
        return edges(y, 4, 100)
    return _drum(build)


def shaker():
    def build(rng):
        n = int(0.11 * SR)
        t = _t(n)
        y = fft_filter(rng.normal(size=n), lo=4000, hi=9500) * np.exp(-t * 38) * (1 - np.exp(-t / 0.006))
        return edges(y, 4, 100)
    return _drum(build)


def snap():
    def build(rng):
        n = int(0.13 * SR)
        t = _t(n)
        y = fft_filter(rng.normal(size=n), lo=1300, hi=5200) * np.exp(-t * 55) * 0.9
        y += 0.3 * np.sin(2 * np.pi * 1900 * t) * np.exp(-t * 90)
        return edges(y, 4, 100)
    return _drum(build)


def rim():
    def build(rng):
        n = int(0.07 * SR)
        t = _t(n)
        y = (np.sin(2 * np.pi * 1700 * t) + 0.5 * np.sin(2 * np.pi * 2650 * t)) * np.exp(-t * 110)
        y += 0.2 * fft_filter(rng.normal(size=n), lo=2000) * np.exp(-t * 200)
        return edges(y * 0.6, 4, 100)
    return _drum(build)


def clap():
    def build(rng):
        n = int(0.22 * SR)
        t = _t(n)
        noise = fft_filter(rng.normal(size=n), lo=1000, hi=4500)
        y = np.zeros(n)
        for d in (0, 0.009, 0.019):
            s = int(d * SR)
            y[s:] += noise[: n - s] * np.exp(-t[: n - s] * 120)
        y += 0.5 * noise * np.exp(-t * 24) * (t > 0.02)
        return edges(y * 0.5, 4, 200)
    return _drum(build)


def tick():
    """Clock tick / woodblock."""
    def build(rng):
        n = int(0.06 * SR)
        t = _t(n)
        y = (np.sin(2 * np.pi * 1250 * t) + 0.6 * np.sin(2 * np.pi * 1870 * t)) * np.exp(-t * 95)
        return edges(y * 0.6, 4, 100)
    return _drum(build)


# ---------------------------------------------------------------------------
# Composition helpers

class Ctx:
    def __init__(self, name, bpm, swing, seed, form, progs, scales):
        self.name, self.bpm, self.swing = name, bpm, swing
        self.spb = 60.0 / bpm
        self.N = int(round(BARS * 4 * self.spb * SR))
        self.rng = np.random.default_rng(seed)
        self.seed = seed
        self.form, self.scales = form, scales
        self.layers = []
        self.chords = []
        for b in range(BARS):
            names = progs[form[b // 8]][b % 8].split()
            for j, s in enumerate(names):
                r, q = parse_chord(s)
                ivs = QUAL[q]
                self.chords.append(dict(beat=b * 4 + j * 4.0 / len(names), dur=4.0 / len(names), root=r, q=q, ivs=ivs,
                                        pcs=[(r + i) % 12 for i in ivs], prog=form[b // 8], name=s))
        self.chord_beats = np.array([c["beat"] for c in self.chords])
        self.rev = dict(rt60=2.0, pre=18, damp=5500, level=0.3, seed=7)

    def chord_at(self, beat):
        i = int(np.searchsorted(self.chord_beats, (beat % (BARS * 4)) + 1e-6, side="right")) - 1
        return self.chords[max(i, 0)]

    def add(self, name, inst, events=None, raw=None, gain=1.0, pan=0.0, pan_jit=0.0, rev=0.2, blocks=(1, 1, 1, 1), hp=None,
            lp=None, hum=8.0, widen=0.0, sat=0.0, wob=None, gate=None, am=None):
        self.layers.append(dict(name=name, inst=inst, events=events or [], raw=raw, gain=gain, pan=pan, pan_jit=pan_jit, rev=rev,
                                blocks=blocks, hp=hp, lp=lp, hum=hum, widen=widen, sat=sat, wob=wob, gate=gate, am=am))


def voice(pcs, prev, lo, hi):
    """Pick the inversion/octave of a chord (ascending stack) closest to the previous voicing."""
    best, best_cost = None, 1e9
    n = len(pcs)
    for r in range(n):
        order = pcs[r:] + pcs[:r]
        for start in range(lo, lo + 12):
            if start % 12 != order[0]:
                continue
            stack, cur = [start], start
            for pc in order[1:]:
                cur += (pc - cur) % 12 or 12
                stack.append(cur)
            if stack[-1] > hi:
                continue
            if prev:
                cost = sum(abs(a - b) for a, b in zip(stack, prev)) + abs(len(stack) - len(prev)) * 3
            else:
                cost = abs(np.mean(stack) - (lo + hi) / 2)
            if cost < best_cost:
                best, best_cost = stack, cost
    return best or [lo + ((p - lo) % 12) for p in pcs]


def root_midi(pc, lo):
    return lo + (pc - lo) % 12


def gen_bass(ctx, patterns, lo=31, hi=47, vel=0.85):
    """patterns: list of per-bar patterns [(beat_in_bar, dur, degree)], degrees r 3 5 7 o(ctave) a(pproach next root)."""
    events = []
    for ci, c in enumerate(ctx.chords):
        nxt = ctx.chords[(ci + 1) % len(ctx.chords)]
        base = root_midi(c["root"], lo)
        nbase = root_midi(nxt["root"], lo)
        bar = int(c["beat"] // 4)
        pat = patterns[bar % len(patterns)]
        iv = c["ivs"]
        third, fifth = iv[1], iv[2]
        seventh = iv[3] if len(iv) > 3 and iv[3] < 12 else 10
        first = True
        for ob, od, deg in pat:
            beat = bar * 4 + ob
            if not (c["beat"] - 1e-6 <= beat < c["beat"] + c["dur"] - 1e-6):
                continue
            if first:
                deg = "r"
            first = False
            if deg == "r":
                m = base
            elif deg == "o":
                m = base + 12
            elif deg == "3":
                m = base + third
            elif deg == "5":
                m = base + fifth
            elif deg == "7":
                m = base + seventh
            else:  # approach
                m = nbase - 1 if (ctx.rng.random() < 0.5 or nbase <= base) else nbase + 1
                if nxt["root"] == c["root"]:
                    m = base + fifth
            while m > hi:
                m -= 12
            events.append((beat, od, m, vel * (1.0 if ob % 4 == 0 else 0.85)))
    return events


def gen_comp(ctx, patterns, lo, hi, vel, strum=0.02, drop_root=True):
    events, prev = [], None
    for c in ctx.chords:
        pcs = list(c["pcs"])
        if drop_root and len(pcs) >= 4:
            pcs = pcs[1:]
        v = voice(pcs, prev, lo, hi)
        prev = v
        bar = int(c["beat"] // 4)
        for ob, od in patterns[bar % len(patterns)]:
            beat = bar * 4 + ob
            if c["beat"] - 1e-6 <= beat < c["beat"] + c["dur"] - 1e-6:
                for j, m in enumerate(v):
                    events.append((beat + j * strum, od, m, vel * (1.0 if j == 0 else 0.88)))
    return events


def gen_pad(ctx, lo=50, hi=67, vel=0.7):
    events, prev = [], None
    for c in ctx.chords:
        v = voice(list(c["pcs"][:4]), prev, lo, hi)
        prev = v
        for m in v:
            events.append((c["beat"], c["dur"] + 0.1, m, vel))
    return events


def gen_counter(ctx, patterns, lo, hi, vel, avoid=(), seed=3):
    rng = np.random.default_rng(seed)
    avoid = np.array(sorted(avoid)) if len(avoid) else None
    events, prev = [], None
    for bar in range(BARS):
        for ob, od in patterns[bar % len(patterns)]:
            beat = bar * 4 + ob
            if avoid is not None and np.abs(avoid - beat).min() < 0.3:
                continue
            c = ctx.chord_at(beat)
            iv = c["ivs"]
            pcs = [(c["root"] + iv[1]) % 12, (c["root"] + iv[2]) % 12]
            pcs.append((c["root"] + (iv[3] if len(iv) > 3 else 12)) % 12)
            opts = sorted((m for m in range(lo, hi + 1) if m % 12 in pcs), key=lambda m: abs(m - (prev if prev else (lo + hi) / 2)))
            opts = [m for m in opts if m != prev] or opts
            m = opts[min(len(opts) - 1, int(rng.integers(0, 2)))]
            prev = m
            events.append((beat, od, m, vel))
    return events


def gen_arp(ctx, shape, step, lo, hi, vel, accent=1.0):
    events = []
    for c in ctx.chords:
        tones = sorted(m for m in range(lo, hi + 1) if m % 12 in c["pcs"])
        for s in range(int(round(c["dur"] / step))):
            m = tones[shape[s % len(shape)] % len(tones)]
            events.append((c["beat"] + s * step, step * 0.8, m, vel * (accent if s % 4 == 0 else 0.8)))
    return events


def gen_pattern(pats, vel=1.0, fill=None, levels={"x": 1.0, "o": 0.6, "g": 0.32}):
    """Per-bar 16-step strings; x = hit, o = soft, g = ghost, . = rest. `fill` replaces every 8th bar."""
    events = []
    for b in range(BARS):
        p = fill if (fill and b % 8 == 7) else pats[b % len(pats)]
        for s, ch in enumerate(p):
            if ch in levels:
                events.append((b * 4 + s * 0.25, 0.1, 0, levels[ch] * vel))
    return events


RHYTHMS = {  # two-bar (8 beat) onset/duration templates
    "sparse": [(0.5, 1), (2.5, 0.5), (3, 1.5), (5.5, 1), (7, 1)],
    "bounce": [(0, 0.5), (0.5, 0.5), (1.5, 1), (3, 0.5), (3.5, 0.5), (4, 1), (5.5, 0.5), (6, 2)],
    "dotted": [(0, 1.5), (1.5, 0.5), (2, 1), (3, 1), (4, 1.5), (5.5, 0.5), (6, 2)],
    "sync": [(0.5, 0.5), (1.5, 0.5), (2, 0.5), (3, 1), (4.5, 0.5), (5.5, 0.5), (6, 1), (7.5, 0.5)],
    "run": [(0, 0.5), (0.5, 0.5), (1, 0.5), (1.5, 0.5), (2, 1), (4, 0.5), (4.5, 0.5), (5, 0.5), (5.5, 0.5), (6, 2)],
    "long": [(0, 2), (2, 1), (3, 1), (4, 2), (6, 1.5), (7.5, 0.5)],
    "cheeky": [(0, 0.5), (0.75, 0.75), (2, 0.5), (2.5, 0.5), (3.5, 0.5), (4, 0.5), (4.75, 0.75), (6, 1), (7, 1)],
}
PHRASE_BIAS = [0.12, -0.15, 0.1, -0.2]


def gen_melody(ctx, plans, lo, hi, center, rest_p=0.0, spice_p=0.15, vel=0.8, seed=1, legato=0.92):
    """plans[block] = four (template, contour_seed, end) phrases; end is the landing chord tone 'R', '3' or '5'.
    The same contour seed in different phrases/blocks gives a recognisable repeated motif that is re-fitted to the
    harmony (strong beats snap to chord tones; weak passing notes stay in the scale)."""
    events, prev = [], None
    deltas = np.array([-3, -2, -1, 0, 1, 2, 3])
    w0 = np.array([0.04, 0.15, 0.28, 0.06, 0.28, 0.15, 0.04])
    for blk in range(4):
        scale = ctx.scales[ctx.form[blk]]
        cand = [m for m in range(lo, hi + 1) if m % 12 in scale]
        for ph in range(4):
            tpl, sid, end = plans[blk][ph]
            rng = np.random.default_rng(seed * 1000 + sid)
            start = blk * 32 + ph * 8
            cur = min(range(len(cand)), key=lambda j: abs(cand[j] - (prev if prev else center)))
            template = RHYTHMS[tpl]
            last_end = -9
            for k, (ob, od) in enumerate(template):
                beat = start + ob
                c = ctx.chord_at(beat)
                is_last = k == len(template) - 1
                u_step, u_rest, u_spice, u_vel = rng.random(), rng.random(), rng.random(), rng.random()
                if k > 0:
                    w = w0.copy()
                    w[deltas > 0] *= 1 + PHRASE_BIAS[ph]
                    w[deltas < 0] *= 1 - PHRASE_BIAS[ph]
                    pull = float(np.clip((cand[cur] - center) / 10.0, -0.8, 0.8))
                    w[deltas > 0] *= 1 - pull
                    w[deltas < 0] *= 1 + pull
                    w = np.clip(w, 1e-3, None)
                    w /= w.sum()
                    step = int(deltas[min(6, int(np.searchsorted(np.cumsum(w), u_step)))])
                    cur = int(np.clip(cur + step, 0, len(cand) - 1))
                pitch = cand[cur]
                strong = (ob % 2 == 0) or od >= 0.75
                if k == 0 or strong or is_last:
                    if is_last:
                        targets = {(c["root"] + c["ivs"][{"R": 0, "3": 1, "5": 2}[end]]) % 12}
                    else:
                        targets = set(c["pcs"])
                    near = [m for m in range(lo, hi + 1) if m % 12 in targets] or [pitch]
                    pitch = min(near, key=lambda m: abs(m - pitch))
                    cur = min(range(len(cand)), key=lambda j: abs(cand[j] - pitch))
                if 0 < k < len(template) - 1 and u_rest < rest_p:
                    continue
                v = vel * (1.0 if ob % 2 == 0 else 0.8) * (0.92 + 0.16 * u_vel)
                if strong and k > 0 and u_spice < spice_p and beat - 0.25 >= last_end:
                    events.append((beat - 0.25, 0.25, pitch - 1, v * 0.6))  # chromatic approach from below
                events.append((beat, od * (1.0 if is_last else legato), pitch, v))
                last_end = beat + od
                prev = pitch
    return events


def transpose(events, semis, vel=1.0):
    return [(b, d, m + semis, v * vel) for b, d, m, v in events]


# ---------------------------------------------------------------------------
# Rendering and mixing

def swing_beat(beat, sw):
    f = beat % 1.0
    if abs(f - 0.5) < 1e-6:
        return beat + sw / 6.0
    if abs(f - 0.75) < 1e-6:
        return beat + sw / 12.0
    return beat


def add_circ(buf, a, pos):
    n = a.shape[-1]
    N = buf.shape[-1]
    end = pos + n
    if end <= N:
        buf[..., pos:end] += a
    else:
        k = N - pos
        buf[..., pos:] += a[..., :k]
        buf[..., : end - N] += a[..., k:]


def render_layer(ctx, L, idx):
    N, spb = ctx.N, ctx.spb
    out = np.zeros((2, N))
    if L["raw"] is not None:
        r = L["raw"]
        th = (L["pan"] + 1) * np.pi / 4
        out += np.stack([r * np.cos(th), r * np.sin(th)]) if r.ndim == 1 else r
    rng = np.random.default_rng(ctx.seed * 31 + idx)
    for i, (beat, dur, m, vel) in enumerate(L["events"]):
        b = swing_beat(beat, ctx.swing)
        h = L["hum"] / 1000.0
        jit = float(np.clip(rng.normal(0, h), -2.5 * h, 2.5 * h))
        pos = int(round((b * spb + jit) * SR)) % N
        v = float(np.clip(vel * (1 + rng.normal(0, 0.05)), 0.03, 1.3))
        a = L["inst"](float(mtof(m)) if m else 0.0, dur * spb, v, i)
        if a.ndim == 1:
            pan = float(np.clip(L["pan"] + rng.uniform(-L["pan_jit"], L["pan_jit"]), -1, 1))
            th = (pan + 1) * np.pi / 4
            a = np.stack([a * np.cos(th), a * np.sin(th)])
        add_circ(out, a, pos)
    # stem processing
    if L["wob"]:
        lo_c, hi_c, cyc = L["wob"]
        m = lfo(N, cyc)
        out = fft_filter(out, hi=lo_c) * (1 - m) + fft_filter(out, hi=hi_c) * m
    if L["lp"] or L["hp"]:
        out = fft_filter(out, lo=L["hp"], hi=L["lp"])
    if L["gate"]:  # flicker: random dropouts (seeded), smooth edges
        drop_p, seg_ms = L["gate"]
        g = np.ones(N)
        pos = 0
        while pos < N:
            ln = int(rng.uniform(0.4, 1.6) * seg_ms / 1000.0 * SR)
            if rng.random() < drop_p:
                g[pos:pos + ln] = 0.15
            pos += ln
        k = int(0.003 * SR)
        ker = np.zeros(N)
        ker[:k] = 1.0 / k
        g = np.fft.irfft(np.fft.rfft(g) * np.fft.rfft(ker), N)
        out = out * g
    if L["am"]:
        depth, hz = L["am"]
        cyc = max(1, round(hz * N / SR))
        out = out * (1 - depth + depth * lfo(N, cyc))
    if L["widen"]:
        d = int(L["widen"] / 1000.0 * SR)
        mid = out.mean(0)
        out = np.stack([out[0] * 0.6 + np.roll(mid, d) * 0.4, out[1] * 0.6 + np.roll(mid, -d) * 0.4])
    if L["sat"]:
        out = np.tanh(out * L["sat"]) / L["sat"]
    # per-8-bar-block gain, smoothed over half a bar (circularly)
    bar = N // BARS
    g = np.repeat(np.array([L["blocks"][b // 8] for b in range(BARS)], dtype=float), bar)
    g = np.concatenate([g, np.full(N - len(g), g[-1])])
    k = max(1, bar // 2)
    ker = np.zeros(N)
    ker[:k] = 1.0 / k
    g = np.fft.irfft(np.fft.rfft(g) * np.fft.rfft(np.roll(ker, -k // 2)), N)
    return out * g


def make_ir(rev, N):
    rng = np.random.default_rng(rev["seed"])
    L = int(min(rev["rt60"] * 1.15 * SR, N // 2))
    pre = int(rev["pre"] / 1000.0 * SR)
    t = _t(L)
    ir = np.zeros((2, L + pre))
    for c in (0, 1):
        noise = rng.normal(size=L)
        dark = fft_filter(noise, hi=rev["damp"] * 0.45)
        bright = fft_filter(noise, hi=rev["damp"])
        w = np.exp(-t / 0.45)
        x = (bright * w + dark * (1 - w)) * np.exp(-6.91 * t / rev["rt60"])
        ir[c, pre:] = x
        for tap in rng.uniform(0.012, 0.075, 6):
            ir[c, pre + int(tap * SR)] += rng.choice([-1, 1]) * rng.uniform(0.15, 0.4) * np.abs(x[:2000]).max() * 6
        ir[c] /= np.sqrt((ir[c] ** 2).sum())
    return ir


def circ_conv(x, ir):
    N = x.shape[-1]
    return np.fft.irfft(np.fft.rfft(x, axis=-1) * np.fft.rfft(ir, N, axis=-1), N, axis=-1)


def mix(ctx):
    N = ctx.N
    dry = np.zeros((2, N))
    send = np.zeros((2, N))
    for idx, L in enumerate(ctx.layers):
        trim = LOW_TRIM if L["name"] in ("bass", "sub", "kick") else 1.0  # keep sub/low energy modest on small speakers
        st = render_layer(ctx, L, idx) * L["gain"] * trim
        dry += st
        send += st * L["rev"]
    wet = circ_conv(fft_filter(send, lo=180, hi=9000), make_ir(ctx.rev, N)) * ctx.rev["level"] * 3.0
    out = fft_filter(dry + wet, lo=28)
    out /= np.abs(out).max()
    out = np.tanh(out * 1.35) / np.tanh(1.35)  # soft limiter
    out *= 10 ** (PEAK_DB / 20) / np.abs(out).max()
    return out


# ---------------------------------------------------------------------------
# Tracks

def melody_onsets(ev):
    return [b for b, d, m, v in ev]


WALK_A = [(0, 0.95, "r"), (1, 0.95, "3"), (2, 0.95, "5"), (3, 0.95, "a")]
WALK_B = [(0, 0.95, "r"), (1, 0.95, "5"), (2, 0.95, "3"), (3, 0.95, "a")]


def track_mainmenu():
    major = scale_pcs(5, MAJOR)
    progs = {
        "A": ["F6", "Dm7", "Bbmaj7", "Bbm6", "F Am7", "D7", "Gm7 C7", "F6"],
        "B": ["Dm7", "Dm7", "Gm7", "C7", "Am7", "Abdim7 Gm7", "Bbmaj7 Bbm6", "C7sus C7"],
    }
    progs["B"] = [p.replace("C7sus", "C7sus") for p in progs["B"]]
    ctx = Ctx("MainMenu", 112, 0.25, 11, ["A", "A", "B", "A"], progs, {"A": major, "B": major})
    ctx.rev.update(rt60=2.2, level=0.3)
    plans = [
        [("bounce", 1, "3"), ("sync", 2, "5"), ("bounce", 1, "3"), ("dotted", 3, "R")],
        [("bounce", 1, "3"), ("sync", 4, "5"), ("bounce", 1, "3"), ("dotted", 5, "R")],
        [("long", 6, "3"), ("run", 7, "5"), ("long", 6, "3"), ("sync", 8, "3")],
        [("bounce", 1, "3"), ("sync", 9, "5"), ("bounce", 1, "3"), ("dotted", 3, "R")],
    ]
    mel = gen_melody(ctx, plans, 72, 89, 79, rest_p=0.08, spice_p=0.2, vel=0.8, seed=11)
    ctx.add("melody", celesta(), mel, gain=1.0, pan=0.12, pan_jit=0.05, rev=0.35, hp=300)
    ctx.add("melody8va", celesta(), transpose(mel, 12, 0.35), gain=0.4, pan=-0.25, rev=0.45, blocks=(0, 0, 1, 0.5), hp=400)
    ctx.add("bass", upright(), gen_bass(ctx, [WALK_A, WALK_B], vel=0.85), gain=0.85, rev=0.05, lp=700, hp=40, hum=6)
    ctx.add("ep", ep(arate=5.0, index=1.2, irate=7.0), gen_comp(ctx, [[(0.5, 0.45), (2.5, 0.45), (3.5, 0.35)], [(0.5, 0.45), (1.5, 0.35), (2.5, 0.45)]], 55, 71, 0.5),
            gain=0.5, pan=-0.2, rev=0.25, lp=3500, blocks=(0.7, 1, 1, 0.9))
    ctx.add("harpsi", pluck(rate=9, bright=0.5, nh=14, click=0.12, octave=0.3), gen_counter(ctx, [[(1.5, 0.5)], [(3.5, 0.5)], [(1.5, 0.5), (3.5, 0.5)], [(2.5, 0.5)]], 58, 74, 0.55, avoid=melody_onsets(mel)),
            gain=0.5, pan=0.45, rev=0.3, blocks=(0.3, 0.8, 1, 0.8))
    ctx.add("pad", pad(att=0.7, rel=1.0, cut=1800), gen_pad(ctx, 50, 66, 0.6), gain=0.22, rev=0.4, hp=150, widen=14, blocks=(0.6, 0.8, 1, 0.8))
    ctx.add("kick", kick(), gen_pattern(["x.......x.....g.", "x.....g.x......."], 0.55), gain=0.45, rev=0.02, blocks=(0.0, 0.8, 1, 0.9))
    ctx.add("brush", brush(), gen_pattern(["....x.......x...", "....x.....g.x..."], 0.6, fill="....x...x.x.xxxx"), gain=0.38, pan=0.1, rev=0.12)
    ctx.add("shaker", shaker(), gen_pattern(["o.g.o.g.o.g.o.g.", "o.g.o.g.o.g.ogg."], 0.5), gain=0.3, pan=-0.3, rev=0.1)
    return ctx


def track_explore():
    minor = scale_pcs(7, MINOR)
    progs = {
        "A": ["Gm7", "C7", "Bbmaj7", "Ebmaj7", "Gm7", "C9", "Ebmaj7", "D7"],
        "B": ["Cm7", "F7", "Bbmaj7", "Gm7", "Cm7", "Ebmaj7", "Am7b5", "D7"],
    }
    ctx = Ctx("Explore", 100, 0.2, 23, ["A", "A", "B", "A"], progs, {"A": minor, "B": minor})
    ctx.rev.update(rt60=2.4, level=0.32, damp=4800)
    plans = [
        [("sparse", 1, "3"), ("sync", 2, "5"), ("sparse", 1, "3"), ("long", 3, "R")],
        [("sparse", 1, "3"), ("long", 4, "5"), ("sparse", 1, "3"), ("sparse", 5, "R")],
        [("long", 6, "5"), ("sparse", 7, "3"), ("sync", 8, "5"), ("long", 9, "R")],
        [("sparse", 1, "3"), ("sync", 2, "5"), ("sparse", 10, "3"), ("long", 3, "R")],
    ]
    mel = gen_melody(ctx, plans, 70, 86, 77, rest_p=0.3, spice_p=0.22, vel=0.75, seed=23)
    ctx.add("marimba", marimba(), mel, gain=1.0, pan=0.1, pan_jit=0.08, rev=0.3, hp=250, blocks=(1, 0.75, 1, 0.55))
    ctx.add("musicbox", music_box(), gen_counter(ctx, [[(2.5, 0.5)], [(1.5, 0.5), (3.5, 0.5)], [(3.0, 0.5)], [(0.5, 0.5)]], 72, 89, 0.5, avoid=melody_onsets(mel), seed=5),
            gain=0.5, pan=-0.35, rev=0.45, blocks=(0.5, 1, 0.8, 1))
    ctx.add("bass", upright(rate=4.5), gen_bass(ctx, [[(0, 0.7, "r"), (1.5, 0.4, "5"), (2.5, 0.7, "r"), (3.5, 0.4, "a")],
                                                      [(0, 0.7, "r"), (2, 0.5, "5"), (2.5, 0.5, "3"), (3.5, 0.4, "a")]], vel=0.8), gain=0.55, rev=0.05, lp=650, hp=40)
    ctx.add("ep", ep(arate=6.0, index=1.0, irate=8.0, tine=0.15), gen_comp(ctx, [[(1.5, 0.5)], [(0.5, 0.4), (2.5, 0.4)], [(1.5, 0.5), (3.0, 0.4)], [(2.5, 0.5)]], 56, 71, 0.42),
            gain=0.5, pan=-0.2, rev=0.3, lp=3000, blocks=(0.8, 1, 0.8, 1))
    ctx.add("pad", pad(att=0.9, rel=1.2, cut=1500, detune=(-7, 0, 7)), gen_pad(ctx, 50, 65, 0.6), gain=0.2, rev=0.45, hp=150, widen=16, blocks=(0.7, 0.9, 1, 0.8))
    ctx.add("kick", kick(0.7), gen_pattern(["x.......g.o.....", "x.........g.x..."], 0.4), gain=0.4, rev=0.02, blocks=(0.8, 1, 1, 0.8))
    ctx.add("wood", rim(), gen_pattern(["....x.......x...", "....x....o..x..."], 0.4), gain=0.3, pan=0.35, rev=0.2, blocks=(0.6, 1, 0.8, 1))
    ctx.add("shaker", shaker(), gen_pattern(["o.g.o.g.o.g.o.g.", "o.g.o.g.o.g.o.gg"], 0.42), gain=0.28, pan=-0.3, rev=0.1)
    return ctx


def track_lukey():
    major = scale_pcs(10, MAJOR)
    progs = {
        "A": ["Bb6", "G7", "Cm7", "F7", "Bb6", "Gm7 C7", "Cm7 F7", "Bb6 G7"],
        "B": ["Cm7", "F7", "Bbmaj7", "G7", "Cm7", "F7", "Bb6 Gm7", "Cm7 F7"],
    }
    ctx = Ctx("Lukey", 118, 0.75, 37, ["A", "A", "B", "A"], progs, {"A": major, "B": major})
    ctx.rev.update(rt60=1.7, level=0.28, damp=6000)
    plans = [
        [("cheeky", 1, "3"), ("bounce", 2, "5"), ("cheeky", 1, "3"), ("dotted", 3, "R")],
        [("cheeky", 1, "3"), ("bounce", 4, "5"), ("cheeky", 1, "3"), ("sync", 5, "R")],
        [("run", 6, "5"), ("cheeky", 7, "3"), ("run", 6, "5"), ("sync", 8, "3")],
        [("cheeky", 1, "3"), ("bounce", 9, "5"), ("cheeky", 1, "3"), ("dotted", 3, "R")],
    ]
    mel = gen_melody(ctx, plans, 72, 89, 80, rest_p=0.06, spice_p=0.28, vel=0.85, seed=37)
    ctx.add("pizz", pluck(rate=9.5, bright=0.9, nh=10, click=0.1), mel, gain=1.0, pan=0.1, pan_jit=0.05, rev=0.3, hp=300)
    ctx.add("vibes", vibes(trem=0.2), transpose(mel, 0, 0.55), gain=0.4, pan=-0.3, rev=0.4, blocks=(0, 0.5, 1, 0.6), hp=300)
    ctx.add("bass", upright(rate=4.0), gen_bass(ctx, [WALK_A, WALK_B, [(0, 0.95, "r"), (1, 0.95, "5"), (2, 0.95, "o"), (3, 0.95, "a")]], vel=0.88), gain=0.9, rev=0.05, lp=700, hp=40, hum=7)
    ctx.add("ep", ep(arate=5.5, index=1.3, irate=7.0), gen_comp(ctx, [[(0.5, 0.4), (2.5, 0.4), (3.5, 0.3)], [(1.5, 0.4), (2.5, 0.4)]], 55, 71, 0.5),
            gain=0.5, pan=-0.2, rev=0.2, lp=3500, blocks=(0.8, 1, 1, 0.9))
    # drips: water-drop plucks on scale notes, with a faint echo, fixed random placement
    rng = np.random.default_rng(371)
    scale = sorted(m for m in range(84, 100) if m % 12 in major)
    drips = []
    for bar in range(BARS):
        for b in (0.5, 1.5, 2.5, 3.5):
            if rng.random() < 0.13:
                m = int(rng.choice(scale))
                beat = bar * 4 + b
                drips.append((beat, 0.5, m, 0.55))
                drips.append((beat + 0.75, 0.5, m, 0.22))
    ctx.add("drops", drop(), drips, gain=0.5, pan=0.0, pan_jit=0.8, rev=0.5, hp=500)
    ctx.add("pad", pad(att=0.6, rel=0.9, cut=2000), gen_pad(ctx, 50, 66, 0.6), gain=0.15, rev=0.4, hp=160, widen=12, blocks=(0.5, 0.8, 1, 0.8))
    ctx.add("kick", kick(), gen_pattern(["x.......x.......", "x.....g.x.o....."], 0.45), gain=0.4, rev=0.02)
    ctx.add("brush", brush(), gen_pattern(["....x.......x...", "....x.....g.x..."], 0.65, fill="....x.g.x.g.xgxx"), gain=0.4, pan=0.1, rev=0.12)
    ctx.add("ride", hat(), gen_pattern(["x...x.x.x...x.x.", "x...x.x.x...x.xg"], 0.5), gain=0.3, pan=0.3, rev=0.1)
    return ctx


def track_malcolm():
    hm = scale_pcs(2, HARM_MINOR)
    progs = {
        "A": ["Dm", "Dm", "Bbmaj7", "A7b9", "Dm", "Gm6", "Bbmaj7", "A7b9"],
        "B": ["Gm", "Gm", "Dm", "Dm", "Bbmaj7", "A7b9", "Dmmaj7", "A7b9"],
    }
    ctx = Ctx("Malcolm", 92, 0.15, 53, ["A", "A", "B", "A"], progs, {"A": hm, "B": hm})
    ctx.rev.update(rt60=3.2, level=0.34, damp=4200, pre=28)
    plans = [
        [("long", 1, "5"), ("sync", 2, "3"), ("long", 1, "5"), ("sparse", 3, "R")],
        [("long", 1, "5"), ("sync", 4, "3"), ("sparse", 5, "5"), ("long", 6, "R")],
        [("sync", 7, "5"), ("dotted", 8, "3"), ("sync", 7, "5"), ("long", 9, "R")],
        [("long", 1, "5"), ("sync", 2, "3"), ("long", 1, "5"), ("sparse", 3, "R")],
    ]
    mel = gen_melody(ctx, plans, 62, 81, 72, rest_p=0.18, spice_p=0.3, vel=0.8, seed=53)
    ctx.add("ep", ep(arate=2.4, index=1.4, irate=3.5, tine=0.1, rel=0.3), mel, gain=1.0, pan=0.15, rev=0.4, lp=3000, hp=200, blocks=(0, 0.75, 1, 0.65))
    ctx.add("bell", eerie_bell(), gen_counter(ctx, [[(2.5, 1.0)], [(1.5, 1.0)], [(3.0, 1.0)], [(0.5, 1.0)]], 76, 93, 0.5, avoid=melody_onsets(mel), seed=9),
            gain=0.5, pan=-0.35, rev=0.6, blocks=(0, 0.6, 1, 0.5))
    slink = [[(0, 1.75, "r"), (2, 0.5, "r"), (2.75, 0.5, "o"), (3.5, 0.5, "5")],
             [(0, 1.25, "r"), (1.5, 0.5, "r"), (2.5, 0.75, "5"), (3.5, 0.5, "a")]]
    ctx.add("sub", sub_bass(), gen_bass(ctx, slink, lo=28, hi=44, vel=0.9), gain=0.5, rev=0.05, lp=420, hp=30)
    ctx.add("pad", pad(att=1.4, rel=1.6, cut=1400, detune=(-13, 0, 13)), gen_pad(ctx, 53, 67, 0.8), gain=0.2, rev=0.5, hp=210, widen=22, wob=(700, 1800, 4))
    ctx.add("stab", ep(arate=7.0, index=0.9, irate=9.0, tine=0.05), gen_comp(ctx, [[(1.5, 0.35)], [(3.5, 0.35)], [(1.5, 0.35), (2.75, 0.3)], [(0.75, 0.3)]], 55, 69, 0.32),
            gain=0.4, pan=-0.2, rev=0.3, lp=2200, blocks=(0, 0.5, 1, 0.5))
    ctx.add("kick", kick(0.8), gen_pattern(["x.....x...x.....", "x.......x.g.o..."], 0.5), gain=0.45, rev=0.03, blocks=(0.6, 1, 1, 0.8))
    ctx.add("snap", snap(), gen_pattern(["....x.......x...", "....x.......x..g"], 0.55), gain=0.35, pan=0.25, rev=0.4, blocks=(0, 0.6, 1, 0.6))
    ctx.add("hat", hat(), gen_pattern(["......o.......o.", "..o...o...g...o."], 0.4), gain=0.22, pan=-0.2, rev=0.2, blocks=(0, 0.5, 1, 0.5))
    ctx.add("shaker", shaker(), gen_pattern(["g.o.g.o.g.o.g.o."], 0.35), gain=0.2, pan=0.3, rev=0.15, blocks=(0.4, 0.8, 1, 0.8))
    return ctx


def track_tyler():
    major = scale_pcs(8, MAJOR)
    progs = {
        "A": ["Ab", "Fm7", "Dbmaj7", "Eb7", "Ab", "Fm7", "Bbm7", "Eb7"],
        "A2": ["Ab", "Fm7", "Dbmaj7", "Dbm6", "Ab", "Fm7", "Bbm7", "Eb7"],
        "B": ["Dbmaj7", "Dbmaj7", "Ab", "Ab", "Bb7", "Bb7", "Bbm7", "Eb7"],
    }
    ctx = Ctx("Tyler", 96, 1.0, 71, ["A", "A2", "B", "A"], progs, {"A": major, "A2": major, "B": major})
    ctx.rev.update(rt60=2.6, level=0.34, damp=4500)
    plans = [
        [("dotted", 1, "3"), ("bounce", 2, "5"), ("dotted", 1, "3"), ("long", 3, "R")],
        [("dotted", 1, "3"), ("sync", 4, "5"), ("dotted", 1, "3"), ("long", 5, "R")],
        [("long", 6, "5"), ("dotted", 7, "3"), ("long", 6, "5"), ("sparse", 8, "3")],
        [("dotted", 1, "3"), ("bounce", 9, "5"), ("dotted", 1, "3"), ("long", 3, "R")],
    ]
    mel = gen_melody(ctx, plans, 72, 89, 79, rest_p=0.05, spice_p=0.18, vel=0.8, seed=71, legato=1.0)
    ctx.add("vibes", vibes(trem=0.35), mel, gain=1.0, pan=0.1, rev=0.35, hp=300)
    # uncanny: a second, slightly flat celesta shadowing the vibraphone a hair late
    ctx.add("ghost", celesta(detune_cents=-34), [(b + 0.03, d, m + 12, v * 0.5) for b, d, m, v in mel], gain=0.35, pan=-0.4, rev=0.5, blocks=(0.3, 0.7, 1, 0.6), hp=500, hum=14)
    ctx.add("ooh", ooh_pad(), gen_pad(ctx, 55, 70, 0.7), gain=0.3, rev=0.45, hp=200, widen=16, blocks=(0.4, 0.9, 1, 0.7))
    walk2 = [(0, 1.9, "r"), (2, 0.95, "5"), (3, 0.95, "a")]
    ctx.add("bass", upright(rate=3.6), gen_bass(ctx, [walk2, WALK_A], vel=0.85), gain=0.9, rev=0.05, lp=650, hp=40, hum=7)
    triplets = [[(b + o, 0.28) for b in range(4) for o in (0, 1 / 3.0, 2 / 3.0)]]
    ctx.add("piano", ep(arate=5.0, index=0.8, irate=8.0, tine=0.12), gen_comp(ctx, triplets, 55, 70, 0.34, strum=0.01),
            gain=0.5, pan=-0.2, rev=0.25, lp=3200, blocks=(0.8, 1, 1, 0.9))
    ctx.add("kick", kick(0.8), gen_pattern(["x.......x.......", "x.....g.x......."], 0.4), gain=0.35, rev=0.02)
    ctx.add("brush", brush(), gen_pattern(["....x.......x...", "....x...g...x..."], 0.6, fill="....x...x.g.xxgx"), gain=0.38, pan=0.1, rev=0.15)
    ctx.add("snap", snap(), gen_pattern(["....x.......x..."], 0.45), gain=0.3, pan=0.3, rev=0.3, blocks=(0, 1, 1, 0.8))
    ctx.add("ride", hat(), gen_pattern(["x...x.x.x...x.x."], 0.42), gain=0.26, pan=-0.3, rev=0.1)
    return ctx


def track_wyatt():
    minor = scale_pcs(9, MINOR) | {8}
    progs = {
        "A": ["Am", "F", "C", "G", "Am", "F", "Dm", "E7"],
        "B": ["F", "G", "Am", "C", "F", "G", "Dm", "E7b9"],
    }
    ctx = Ctx("Wyatt", 130, 0.1, 89, ["A", "A", "B", "A"], progs, {"A": minor, "B": minor})
    ctx.rev.update(rt60=1.5, level=0.24, damp=7000, pre=10)
    plans = [
        [("sync", 1, "3"), ("run", 2, "5"), ("sync", 1, "3"), ("dotted", 3, "R")],
        [("sync", 1, "3"), ("run", 4, "5"), ("sync", 1, "3"), ("long", 5, "R")],
        [("run", 6, "5"), ("sync", 7, "3"), ("run", 6, "5"), ("dotted", 8, "3")],
        [("sync", 1, "3"), ("run", 9, "5"), ("sync", 1, "3"), ("dotted", 3, "R")],
    ]
    mel = gen_melody(ctx, plans, 72, 88, 79, rest_p=0.1, spice_p=0.25, vel=0.75, seed=89, legato=0.8)
    ctx.add("lead", pulse(pw=0.25, rate=2.5, vib=0.006, sustain=0.35, rel=0.06), mel, gain=0.85, pan=0.1, rev=0.25, lp=5500, hp=300, gate=(0.1, 80), blocks=(0.7, 1, 1, 0.9))
    arp = gen_arp(ctx, [0, 2, 1, 3, 2, 4, 3, 1], 0.25, 57, 79, 0.55)
    ctx.add("arp", pulse(pw=0.4, rate=14.0, nh=10), arp, gain=0.55, pan=-0.35, pan_jit=0.1, rev=0.25, lp=6000, hp=250, gate=(0.14, 55), am=(0.18, 100), blocks=(0.8, 1, 1, 0.8))
    ctx.add("arp2", pulse(pw=0.15, rate=18.0, nh=8), [(b + 0.125, d, m + 12, v * 0.6) for b, d, m, v in arp[1::2]], gain=0.3, pan=0.5, rev=0.3,
            lp=7000, hp=500, gate=(0.18, 45), blocks=(0, 0.6, 1, 0.5))
    pump = [[(0, 0.45, "r"), (0.5, 0.45, "r"), (1, 0.45, "o"), (1.5, 0.45, "r"), (2, 0.45, "r"), (2.5, 0.45, "o"), (3, 0.45, "r"), (3.5, 0.45, "5")]]
    ctx.add("bass", pulse(pw=0.5, rate=7.0, nh=6, rel=0.05), gen_bass(ctx, pump, lo=33, hi=47, vel=0.75), gain=0.7, rev=0.03, lp=600, hp=40)
    ctx.add("pad", pad(att=0.3, rel=0.5, cut=2600, detune=(-20, 0, 20)), gen_pad(ctx, 52, 67, 0.5), gain=0.14, rev=0.3, hp=200, widen=10, am=(0.3, 6.0), blocks=(0.6, 0.8, 1, 0.8))
    ctx.add("kick", kick(1.1), gen_pattern(["x...x...x...x..."], 0.55), gain=0.5, rev=0.02, blocks=(0.8, 1, 1, 1))
    ctx.add("clap", clap(), gen_pattern(["....x.......x...", "....x.......x..g"], 0.5, fill="....x...x.x.xxxx"), gain=0.34, pan=0.1, rev=0.2)
    ctx.add("hat", hat(), gen_pattern(["x.x.x.x.x.x.x.xg"], 0.45), gain=0.26, pan=-0.2, rev=0.08)
    ctx.add("ohat", hat(True), gen_pattern(["..o...o...o...o."], 0.4), gain=0.2, pan=0.25, rev=0.1, blocks=(0, 1, 1, 0.8))
    # crackle (random clicks, bursty) and sparks (zap sweeps at fixed random places)
    rng = np.random.default_rng(891)
    crackle = np.zeros(ctx.N)
    pos = 0
    while True:
        pos += int(rng.exponential(0.11) * SR)
        if pos >= ctx.N - 600:
            break
        for j in range(int(rng.integers(1, 4))):
            p = pos + j * int(rng.uniform(0.002, 0.012) * SR)
            ln = int(rng.uniform(0.0006, 0.002) * SR)
            if p + ln < ctx.N:
                crackle[p:p + ln] += rng.normal(size=ln) * np.exp(-np.arange(ln) / (ln / 3.0)) * rng.uniform(0.15, 1.0)
    crackle = fft_filter(crackle, lo=2500)
    ctx.add("crackle", None, raw=crackle, gain=0.22, rev=0.1, blocks=(0.8, 1, 1, 1))
    sparks = [(float(b), 0.2, 0, 0.5) for b in sorted(rng.choice(np.arange(2, BARS * 4 - 1, 0.5), 18, replace=False))]
    ctx.add("sparks", zap(), sparks, gain=0.3, pan=0.0, pan_jit=0.8, rev=0.35, blocks=(0.6, 1, 1, 1))
    return ctx


def track_finale():
    major = scale_pcs(2, MAJOR) | {8}
    progs = {
        "T": ["Bm", "Bm7", "Gmaj7", "F#7", "Bm", "Gmaj7", "Em7", "F#7"],
        "T2": ["Bm", "Gmaj7", "Em7", "F#7", "Bm", "", "Em", "F#7b9"],
        "W": ["D", "A", "Bm7", "Gmaj7", "D", "A", "Gmaj7 Em7", "A7"],
        "W2": ["D", "A", "Bm7", "Gmaj7", "D", "A", "Gmaj7 A7", "D Bm7"],
    }
    progs["T2"][5] = "G"
    ctx = Ctx("Finale", 100, 0.1, 97, ["T", "T2", "W", "W2"], progs, {k: major for k in progs})
    ctx.rev.update(rt60=2.8, level=0.36, damp=5000, pre=22)
    plans = [
        [("long", 1, "3"), ("sparse", 2, "5"), ("long", 1, "3"), ("sparse", 3, "5")],
        [("sparse", 4, "3"), ("sync", 5, "5"), ("dotted", 4, "3"), ("sync", 6, "5")],
        [("bounce", 7, "3"), ("dotted", 8, "5"), ("bounce", 7, "3"), ("run", 9, "3")],
        [("bounce", 7, "3"), ("dotted", 10, "5"), ("dotted", 8, "3"), ("long", 11, "R")],
    ]
    mel = gen_melody(ctx, plans, 71, 90, 79, rest_p=0.08, spice_p=0.2, vel=0.8, seed=97)
    ctx.add("celesta", celesta(), mel, gain=1.0, pan=0.1, rev=0.4, hp=300, blocks=(0.8, 1, 1, 0.9))
    ctx.add("vibes", vibes(trem=0.3), transpose(mel, 0, 0.6), gain=0.45, pan=-0.3, rev=0.4, blocks=(0, 0, 0.8, 0.7), hp=300)
    ctx.add("strings", pad(att=0.9, rel=1.2, cut=3000, detune=(-12, 0, 12), nharm=18), gen_pad(ctx, 50, 69, 0.8), gain=0.3, rev=0.5, hp=150, widen=20, blocks=(0.6, 0.85, 1, 0.9))
    ctx.add("ooh", ooh_pad(), gen_pad(ctx, 57, 72, 0.6), gain=0.22, rev=0.5, hp=250, widen=14, blocks=(0, 0, 0.9, 1))
    ctx.add("bass", upright(rate=3.6), gen_bass(ctx, [[(0, 1.9, "r"), (2, 1.9, "5")], WALK_A, WALK_B, [(0, 0.95, "r"), (1, 0.95, "5"), (2, 0.95, "3"), (3, 0.95, "a")]], vel=0.85),
            gain=0.85, rev=0.05, lp=650, hp=40, blocks=(0.55, 1, 1, 0.9))
    ctx.add("ep", ep(arate=4.0, index=1.0, irate=6.0, tine=0.15), gen_comp(ctx, [[(0, 1.5), (2.5, 0.5)], [(0, 1.0), (1.5, 0.5), (2.5, 1.0)]], 55, 70, 0.4),
            gain=0.5, pan=-0.2, rev=0.3, lp=3200, blocks=(0, 0.7, 1, 0.8))
    ctx.add("harpsi", pluck(rate=9, bright=0.5, nh=14, click=0.12, octave=0.3), gen_counter(ctx, [[(1.5, 0.5)], [(3.5, 0.5)], [(2.5, 0.5), (3.5, 0.5)], [(0.5, 0.5)]], 58, 74, 0.45, avoid=melody_onsets(mel), seed=13),
            gain=0.45, pan=0.45, rev=0.35, blocks=(0.4, 0.8, 0.5, 0.3))
    ctx.add("tick", tick(), gen_pattern(["x...x...x...x..."], 0.45), gain=0.35, pan=0.3, rev=0.25, blocks=(1, 0.8, 0.3, 0))
    ctx.add("kick", kick(0.8), gen_pattern(["x.......x.......", "x.....g.x.o....."], 0.45), gain=0.4, rev=0.03, blocks=(0, 0.5, 1, 0.8))
    ctx.add("brush", brush(), gen_pattern(["....x.......x...", "....x...g...x..."], 0.6, fill="....x...x.g.xxgx"), gain=0.36, pan=0.1, rev=0.15, blocks=(0, 0.6, 1, 0.8))
    ctx.add("shaker", shaker(), gen_pattern(["o.g.o.g.o.g.o.g."], 0.4), gain=0.24, pan=-0.3, rev=0.1, blocks=(0, 0.4, 0.9, 0.7))
    return ctx


TRACKS = {
    "MainMenu": track_mainmenu, "Explore": track_explore, "Lukey": track_lukey, "Malcolm": track_malcolm,
    "Tyler": track_tyler, "Wyatt": track_wyatt, "Finale": track_finale,
}
KEYS = {"MainMenu": "F major", "Explore": "G minor/dorian", "Lukey": "Bb major", "Malcolm": "D harmonic minor",
        "Tyler": "Ab major", "Wyatt": "A minor", "Finale": "B minor to D major"}


# ---------------------------------------------------------------------------
# Output and checks

def write_wav(path, stereo):
    pcm = np.clip(np.round(stereo.T * 32767.0), -32768, 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def db(x):
    return 20 * np.log10(max(float(x), 1e-9))


def analyse(out):
    N = out.shape[1]
    mono = out.mean(0)
    d = np.abs(np.diff(np.concatenate([mono, mono[:1]])))  # last diff is the wrap-around step
    seam = d[-1]
    local = np.percentile(d[:-1], 99.9)  # a seam step below the file's own 99.9th-percentile step is inaudible
    win = int(0.1 * SR)
    spec = np.abs(np.fft.rfft(mono)) ** 2
    f = np.fft.rfftfreq(N, 1 / SR)
    bands = [("sub<80", 0, 80), ("low80-250", 80, 250), ("lomid250-500", 250, 500), ("mid.5-2k", 500, 2000), ("hi2-6k", 2000, 6000), ("air>6k", 6000, 22050)]
    tot = spec.sum()
    bd = {k: round(float(10 * np.log10(spec[(f >= a) & (f < b)].sum() / tot + 1e-12)), 1) for k, a, b in bands}
    blocks = [round(float(db(np.sqrt(np.mean(mono[int(i * N / 4):int((i + 1) * N / 4)] ** 2)))), 1) for i in range(4)]
    return dict(
        duration=round(N / SR, 2), peak_db=round(db(np.abs(out).max()), 2), rms_db=round(db(np.sqrt(np.mean(out ** 2))), 2),
        seam_step=round(float(seam), 6), seam_ratio=round(float(seam / local), 3),
        seam_level_db=round(db(np.sqrt(np.mean(mono[-win:] ** 2))) - db(np.sqrt(np.mean(mono[:win] ** 2))), 2),
        bands_db=bd, quarter_rms_db=blocks,
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="track name(s), comma separated, e.g. Tyler or BGM_Tyler")
    args = ap.parse_args()
    wanted = {n.replace("BGM_", "") for n in args.only.split(",")} if args.only else None
    os.makedirs(OUT, exist_ok=True)
    manifest_path = os.path.join(OUT, "manifest.json")
    manifest = {}
    if os.path.exists(manifest_path):
        with open(manifest_path, encoding="utf-8") as fh:
            manifest = json.load(fh)
    for name, builder in TRACKS.items():
        if wanted and name not in wanted:
            continue
        ctx = builder()
        out = mix(ctx)
        fn = f"BGM_{name}.wav"
        write_wav(os.path.join(OUT, fn), out)
        info = analyse(out)
        info.update(key=KEYS[name], bpm=ctx.bpm, bars=BARS, swing=ctx.swing, layers=[L["name"] for L in ctx.layers])
        manifest[fn] = info
        print(f"{fn}: {info['duration']}s {KEYS[name]} {ctx.bpm}bpm peak {info['peak_db']} dB rms {info['rms_db']} dB "
              f"seam step {info['seam_step']} ({info['seam_ratio']}x the p99.9 sample step) level jump {info['seam_level_db']} dB")
        print("   bands", info["bands_db"], "quarters", info["quarter_rms_db"], flush=True)
    manifest = {k: manifest[k] for k in sorted(manifest)}
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)


if __name__ == "__main__":
    main()
