#!/usr/bin/env python3
"""
Synthesize placeholder sound effects (python3 + numpy + stdlib wave only; no downloads, fully deterministic).

    python3 Tools/Audio/generate_sfx.py            # writes every sound
    python3 Tools/Audio/generate_sfx.py --only Footstep

Then import into Unreal (editor must be running):

    python3 Tools/run_in_editor.py Tools/Editor/import_sfx.py

Output: "Art Source/Audio/SFX/SFX_<Name>[_<n>].wav" (44.1 kHz, 16-bit, mono) plus manifest.json. The game
(Audio/FixHimSfxSubsystem) plays "SFX_<Name>" and picks randomly among the numbered variants. Tones are soft and
bubbly to suit the pink renovation-chic UI; swap any file for a real recording of the same name to replace it.
"""
import argparse
import json
import os
import wave
import zlib

import numpy as np

SR = 44100
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "Art Source/Audio/SFX")


# ---------------------------------------------------------------------------
# Building blocks. Every helper returns a float array at SR; t() is time in seconds.

def t(dur):
    return np.arange(int(dur * SR)) / SR


def env(n, attack=0.005, release=0.05, curve=1.0):
    """Linear attack, power-curve release over the whole buffer (never starts/ends on a hard edge)."""
    a = max(1, int(attack * SR))
    r = max(1, int(release * SR))
    e = np.ones(n)
    e[:a] = np.linspace(0, 1, a, endpoint=False) if a < n else np.linspace(0, 1, n)
    e[-r:] = np.minimum(e[-r:], np.linspace(1, 0, r) ** curve) if r < n else np.linspace(1, 0, n) ** curve
    return e


def decay(dur, rate):
    """Exponential decay with a tiny attack, ~-60 dB at `rate` e-folds."""
    x = t(dur)
    return np.exp(-x * rate) * np.minimum(1, x / 0.003)


def tone(freq, dur, harmonics=(1.0,), rate=8.0, vibrato=0.0):
    """Soft bell/pluck: sum of harmonics with exponential decay."""
    x = t(dur)
    f = freq * (1 + vibrato * np.sin(2 * np.pi * 5.5 * x))
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = sum(a * np.sin((i + 1) * ph) for i, a in enumerate(harmonics))
    return y * decay(dur, rate)


def bell(freq, dur, rate=7.0):
    """Inharmonic partials for a glassy ding."""
    x = t(dur)
    y = np.sin(2 * np.pi * freq * x) + 0.4 * np.sin(2 * np.pi * freq * 2.76 * x) * np.exp(-x * rate * 0.8) \
        + 0.2 * np.sin(2 * np.pi * freq * 5.4 * x) * np.exp(-x * rate * 1.6)
    return y * decay(dur, rate)


def sweep(f0, f1, dur, shape="exp", wave_="sine", rate=0.0):
    x = t(dur)
    u = x / dur
    f = f0 * (f1 / f0) ** u if shape == "exp" else f0 + (f1 - f0) * u
    ph = 2 * np.pi * np.cumsum(f) / SR
    if wave_ == "square":
        y = np.tanh(3 * np.sin(ph))
    elif wave_ == "saw":
        y = 2 * ((ph / (2 * np.pi)) % 1) - 1
    else:
        y = np.sin(ph)
    return y * (decay(dur, rate) if rate else 1.0)


def noise(dur, rng):
    return rng.standard_normal(int(dur * SR))


def lowpass(y, cutoff):
    """One-pole low-pass (cutoff may be an array for sweeps)."""
    cutoff = np.broadcast_to(cutoff, y.shape)
    a = 1 - np.exp(-2 * np.pi * cutoff / SR)
    out = np.empty_like(y)
    s = 0.0
    for i in range(len(y)):
        s += a[i] * (y[i] - s)
        out[i] = s
    return out


def highpass(y, cutoff):
    return y - lowpass(y, cutoff)


def bandpass(y, lo, hi):
    return lowpass(highpass(y, lo), hi)


def mix(*parts, length=None):
    """Sum arrays, each given as (array, start_seconds, gain) or just an array."""
    items = [(p, 0.0, 1.0) if isinstance(p, np.ndarray) else p for p in parts]
    n = length or max(int(s * SR) + len(a) for a, s, _ in items)
    out = np.zeros(n)
    for a, s, g in items:
        i = int(s * SR)
        seg = a[: max(0, n - i)]
        out[i:i + len(seg)] += seg * g
    return out


def finish(y, peak=0.6, fade_in=0.002, fade_out=0.01):
    """Remove DC, fade the edges (no clicks), normalise to `peak`."""
    y = y - np.mean(y)
    n = len(y)
    fi, fo = max(1, int(fade_in * SR)), max(1, int(fade_out * SR))
    y[:fi] *= np.linspace(0, 1, fi)
    y[-fo:] *= np.linspace(1, 0, fo)
    m = np.max(np.abs(y))
    return y / m * peak if m > 0 else y


def note(semis, base=523.25):
    return base * 2 ** (semis / 12)


# ---------------------------------------------------------------------------
# Sound definitions. Each takes (rng, variant) and returns (samples, peak). `variants` > 1 produces numbered files.

def j(rng, amount=0.03):
    """Small deterministic multiplier around 1 for pitch/timing variation."""
    return 1 + rng.uniform(-amount, amount)


def ui_hover(rng, v):
    return tone(note(7) * j(rng), 0.07, (1, 0.2), rate=40), 0.25


def ui_click(rng, v):
    return mix(tone(note(0) * j(rng), 0.12, (1, 0.3), rate=30), (tone(note(7), 0.1, (1,), rate=34), 0.025, 0.7)), 0.45


def ui_back(rng, v):
    return mix(tone(note(2), 0.1, (1, 0.3), rate=30), (tone(note(-5), 0.12, (1, 0.3), rate=30), 0.045, 0.9)), 0.42


def modal_open(rng, v):
    whoosh = highpass(lowpass(noise(0.22, rng), np.linspace(500, 3500, int(0.22 * SR))), 300) * env(int(0.22 * SR), 0.08, 0.12)
    pop = tone(note(4), 0.18, (1, 0.25), rate=22)
    return mix((whoosh, 0, 0.35), (pop, 0.12, 1.0), (tone(note(11), 0.2, (1,), rate=24), 0.15, 0.4)), 0.5


def modal_close(rng, v):
    n = int(0.16 * SR)
    whoosh = lowpass(noise(0.16, rng), np.linspace(3000, 400, n)) * env(n, 0.02, 0.1)
    return mix((whoosh, 0, 0.3), (tone(note(-3), 0.14, (1, 0.2), rate=26), 0, 1.0)), 0.4


def slider_tick(rng, v):
    return tone(note(12 + v * 2) * j(rng, 0.01), 0.04, (1,), rate=70), 0.22


def toggle_on(rng, v):
    return mix(tone(note(0), 0.08, (1, 0.3), rate=36), (tone(note(7), 0.12, (1, 0.2), rate=26), 0.05, 1.0)), 0.4


def toggle_off(rng, v):
    return mix(tone(note(7), 0.08, (1, 0.3), rate=36), (tone(note(0), 0.12, (1, 0.2), rate=26), 0.05, 1.0)), 0.36


def toast(rng, v):
    return mix(bell(note(12), 0.5, 6), (bell(note(19), 0.6, 6), 0.09, 0.7)), 0.4


def choice_select(rng, v):
    return mix(tone(note(4), 0.1, (1, 0.3), rate=28), (tone(note(9), 0.16, (1, 0.2), rate=22), 0.06, 0.9), (bell(note(16), 0.3, 12), 0.06, 0.3)), 0.42


def topic_click(rng, v):
    """Hypertext word: a glassy pluck with a little upward glide."""
    return mix(sweep(note(5), note(12), 0.09, rate=18), (bell(note(17) * j(rng), 0.25, 12), 0.04, 0.6)), 0.4


def dialogue_advance(rng, v):
    return tone(note(2 + (v % 3)) * j(rng, 0.01), 0.09, (1, 0.15), rate=32), 0.26


def type_tick(rng, v):
    return tone(note(14 + v) * j(rng, 0.01), 0.025, (1,), rate=90), 0.07


def menu_start(rng, v):
    chord = [mix((tone(note(s), 0.9, (1, 0.25), rate=4.5), i * 0.07, 1.0)) for i, s in enumerate((0, 4, 7, 12, 16))]
    return mix(*chord, (bell(note(24), 0.9, 5), 0.3, 0.4)), 0.5


def pause_on(rng, v):
    return mix(sweep(note(7), note(-5), 0.22, rate=8), (tone(note(-5), 0.18, (1, 0.3), rate=14), 0.05, 0.6)), 0.4


def pause_off(rng, v):
    return mix(sweep(note(-5), note(7), 0.2, rate=9), (tone(note(7), 0.18, (1, 0.3), rate=16), 0.06, 0.6)), 0.4


def map_open(rng, v):
    """Paper unfolding: filtered noise rustle with a soft chime."""
    n = int(0.35 * SR)
    r = bandpass(noise(0.35, rng) * (0.5 + 0.5 * np.sin(2 * np.pi * 24 * t(0.35)) ** 2), 1500, 5500) * env(n, 0.05, 0.15)
    return mix((r, 0, 0.7), (bell(note(12), 0.4, 8), 0.2, 0.5)), 0.4


def map_close(rng, v):
    n = int(0.25 * SR)
    r = bandpass(noise(0.25, rng), 1200, 4500) * env(n, 0.03, 0.12)
    return mix((r, 0, 0.6), (bell(note(5), 0.3, 10), 0.08, 0.4)), 0.36


def debug_open(rng, v):
    return mix(tone(note(-5), 0.06, (1, 0.5), rate=40), (tone(note(0), 0.06, (1, 0.5), rate=40), 0.06, 1.0), (tone(note(5), 0.08, (1, 0.5), rate=36), 0.12, 1.0)), 0.3


# --- World -----------------------------------------------------------------

def hover(rng, v):
    return mix(tone(note(14), 0.12, (1, 0.1), rate=24), (tone(note(21), 0.12, (1,), rate=28), 0.025, 0.5)), 0.22


def interact(rng, v):
    click = highpass(noise(0.05, rng), 1500) * decay(0.05, 80)
    return mix((click, 0, 0.4), (tone(note(-5) * j(rng), 0.12, (1, 0.4), rate=30), 0, 1.0)), 0.45


def knock(rng, v):
    """Knuckles on a wooden door."""
    def one(f):
        n = int(0.12 * SR)
        body = lowpass(noise(0.12, rng), 600) * decay(0.12, 45)
        return mix((body, 0, 1.0), (tone(f, 0.12, (1, 0.5), rate=45), 0, 0.7))
    return mix(one(150 * j(rng)), (one(140 * j(rng)), 0.19, 0.9), (one(145 * j(rng)), 0.38, 0.85)), 0.6


def door_latch(rng, v):
    def tk(f, dur=0.04):
        return highpass(noise(dur, rng), 1200) * decay(dur, 90) + 0.8 * tone(f, dur, (1, 0.3), rate=80)
    return mix(tk(1800), (tk(900, 0.07), 0.07, 1.2)), 0.5


def bed_rustle(rng, v):
    n = int(0.9 * SR)
    x = t(0.9)
    mod = 0.35 + 0.65 * np.abs(np.sin(2 * np.pi * 3.2 * x + 1.0)) * np.abs(np.sin(2 * np.pi * 1.3 * x))
    y = bandpass(noise(0.9, rng), 700, 4000) * mod * env(n, 0.1, 0.25)
    thump = tone(70, 0.2, (1, 0.5), rate=18)
    return mix((y, 0, 0.8), (thump, 0.02, 0.5)), 0.5


def cabinet_open(rng, v):
    creak = lowpass(sweep(190, 250, 0.4, "lin", "saw") * (0.6 + 0.4 * np.sin(2 * np.pi * 38 * t(0.4))), 900) * env(int(0.4 * SR), 0.05, 0.1)
    return mix((creak, 0, 0.5), (tone(110, 0.14, (1, 0.5), rate=25), 0.38, 0.8)), 0.45


def cabinet_close(rng, v):
    body = lowpass(noise(0.14, rng), 700) * decay(0.14, 38)
    return mix((body, 0, 1.0), (tone(95, 0.16, (1, 0.5), rate=28), 0, 1.0), (tone(240, 0.05, (1,), rate=60), 0.01, 0.3)), 0.6


def door_creak(rng, v):
    x = t(0.9)
    f = 160 + 90 * np.sin(2 * np.pi * 1.1 * x) * np.sin(np.pi * x / 0.9) + 30 * np.sin(2 * np.pi * 9 * x)
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = lowpass(2 * ((ph / (2 * np.pi)) % 1) - 1, 1100) * env(len(x), 0.12, 0.3, 2.0)
    return y, 0.35


def switch_on(rng, v):
    return mix(highpass(noise(0.015, rng), 2500) * decay(0.015, 200), (tone(note(-3), 0.05, (1, 0.5), rate=70), 0, 0.6), (tone(note(9), 0.12, (1, 0.2), rate=24), 0.02, 0.6)), 0.45


def switch_off(rng, v):
    return mix(highpass(noise(0.015, rng), 2500) * decay(0.015, 200), (tone(note(-3), 0.05, (1, 0.5), rate=70), 0, 0.6), (tone(note(2), 0.12, (1, 0.2), rate=24), 0.02, 0.6)), 0.4


def tap_drip(rng, v):
    f0 = 1200 * j(rng, 0.12)
    return mix(sweep(f0, f0 * 1.9, 0.08, rate=45), (sweep(f0 * 2, f0 * 3.6, 0.05, rate=60), 0, 0.25)), 0.4


def water_splash(rng, v):
    n = int(0.5 * SR)
    x = t(0.5)
    y = bandpass(noise(0.5, rng), 600, 6000) * np.exp(-x * 5) * (0.7 + 0.3 * np.sin(2 * np.pi * 17 * x))
    bubbles = [(sweep(f, f * 1.8, 0.06, rate=50), st, 0.35) for f, st in ((800, 0.03), (1100, 0.09), (650, 0.16), (1300, 0.22))]
    return mix((y, 0, 0.8), *bubbles), 0.5


def pipe_clank(rng, v):
    x = t(1.1)
    y = sum(np.sin(2 * np.pi * f * x * j(rng, 0.01)) * np.exp(-x * r) * a
            for f, r, a in ((310, 5, 1), (472, 6, 0.7), (873, 8, 0.5), (1342, 11, 0.35)))
    return mix((y, 0, 1.0), (highpass(noise(0.03, rng), 1500) * decay(0.03, 120), 0, 0.6)), 0.55


def spark(rng, v):
    x = t(0.3)
    crackle = (rng.random(len(x)) > 0.985) * rng.standard_normal(len(x))
    crackle = highpass(crackle, 800) * np.exp(-x * 14)
    return mix((crackle * 4, 0, 1.0), (sweep(2400, 600, 0.12, rate=18), 0, 0.3)), 0.45


def zap(rng, v):
    x = t(0.45)
    buzz = np.tanh(2 * np.sin(2 * np.pi * np.cumsum(120 + 900 * np.exp(-x * 14)) / SR)) * np.exp(-x * 6)
    crackle = highpass((rng.random(len(x)) > 0.97) * rng.standard_normal(len(x)), 1000) * np.exp(-x * 8)
    return lowpass(buzz, 3500) * 0.7 + crackle * 3, 0.5


def toilet_flush(rng, v):
    x = t(1.9)
    swirl = bandpass(noise(1.9, rng), 300, 3200) * (np.minimum(1, x / 0.2)) * np.exp(-np.maximum(0, x - 0.6) * 1.6)
    return mix((swirl, 0, 0.9), (sweep(220, 100, 0.5, rate=3), 1.3, 0.3)), 0.5


def sizzle(rng, v):
    x = t(1.2)
    crackle = (rng.random(len(x)) > 0.995) * rng.standard_normal(len(x))
    y = highpass(noise(1.2, rng), 4000) * 0.25 + highpass(crackle, 1500) * 1.5
    return y * env(len(x), 0.08, 0.35), 0.4


def hum(rng, v):
    x = t(1.4)
    y = np.sin(2 * np.pi * 100 * x) + 0.5 * np.sin(2 * np.pi * 200 * x) + 0.12 * np.sin(2 * np.pi * 300 * x)
    return y * (1 + 0.1 * np.sin(2 * np.pi * 6 * x)) * env(len(x), 0.2, 0.4), 0.3


def fix_complete(rng, v):
    arp = [bell(note(s), 0.9, 4.5) for s in (0, 4, 7, 12, 16, 19)]
    parts = [(a, i * 0.075, 1.0 - 0.1 * i) for i, a in enumerate(arp)]
    sparkle = (highpass(noise(0.8, rng), 6000) * decay(0.8, 5) * (rng.random(int(0.8 * SR)) > 0.6), 0.2, 0.12)
    return mix(*parts, sparkle), 0.55


def repair_fail(rng, v):
    return mix(tone(note(-12), 0.22, (1, 0.5, 0.3), rate=12), (tone(note(-17), 0.35, (1, 0.5, 0.3), rate=9), 0.14, 1.0)), 0.5


def error_buzz(rng, v):
    x = t(0.25)
    y = np.tanh(2 * np.sin(2 * np.pi * 130 * x)) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 28 * x)))
    return lowpass(y, 1500) * env(len(x), 0.01, 0.06), 0.4


def footstep(rng, v):
    """Soft slipper on wood: low thud + a little filtered scuff."""
    f = (95 + 8 * v) * j(rng, 0.06)
    thud = tone(f, 0.12, (1, 0.4), rate=34)
    scuff = bandpass(noise(0.1, rng), 500, 2200) * decay(0.1, 45)
    return mix((thud, 0, 1.0), (scuff, 0.005, 0.45)), 0.3


def day_end(rng, v):
    notes = [(note(s), i * 0.28) for i, s in enumerate((7, 4, 0, -5))]
    return mix(*[(bell(f, 1.6, 3.2), s, 1.0) for f, s in notes], (tone(note(-12), 2.2, (1, 0.3), rate=2.4), 0.5, 0.35)), 0.5


def day_start(rng, v):
    notes = [(note(s), i * 0.16) for i, s in enumerate((0, 4, 7, 12, 16))]
    return mix(*[(bell(f, 1.3, 4.2), s, 1.0) for f, s in notes], (highpass(noise(1.0, rng), 7000) * decay(1.0, 4) * 0.2, 0.3, 1.0)), 0.5


# --- Characters ------------------------------------------------------------

def hunk_pop(rng, v):
    """Magical poof: airy burst, upward whistle, and a glitter tail."""
    n = int(0.6 * SR)
    poof = lowpass(noise(0.6, rng), np.linspace(5000, 600, n)) * decay(0.6, 8)
    zip_ = sweep(400, 1800, 0.14, rate=10)
    pop = tone(note(-12), 0.1, (1, 0.5), rate=30)
    glit = [(bell(note(s), 0.4, 9), 0.1 + i * 0.05, 0.5) for i, s in enumerate((12, 16, 19, 24))]
    return mix((poof, 0, 0.7), (zip_, 0, 0.35), (pop, 0.12, 0.8), *glit), 0.55


def hunk_leave(rng, v):
    n = int(0.45 * SR)
    poof = lowpass(noise(0.45, rng), np.linspace(2500, 300, n)) * decay(0.45, 9)
    return mix((poof, 0, 0.7), (sweep(1500, 350, 0.2, rate=9), 0, 0.4), (bell(note(7), 0.3, 12), 0.12, 0.3)), 0.4


def react_happy(rng, v):
    return mix(*[(bell(note(s), 0.7, 5.5), i * 0.09, 1.0) for i, s in enumerate((0, 4, 7, 12))],
               (highpass(noise(0.6, rng), 6500) * decay(0.6, 6) * (rng.random(int(0.6 * SR)) > 0.7), 0.15, 0.12)), 0.5


def react_hearts(rng, v):
    return mix(*[(bell(note(s), 0.6, 6), i * 0.11, 1.0 - 0.15 * i) for i, s in enumerate((7, 12, 16, 19, 24))],
               (sweep(500, 2000, 0.3, rate=8), 0, 0.15)), 0.45


def react_angry(rng, v):
    x = t(0.4)
    buzz = lowpass(np.tanh(3 * np.sin(2 * np.pi * 72 * x)) * (1 + 0.5 * np.sin(2 * np.pi * 22 * x)), 700) * env(len(x), 0.005, 0.18)
    thud = tone(55, 0.3, (1, 0.5), rate=12)
    return mix((buzz, 0, 0.8), (thud, 0, 1.0)), 0.55


def react_sad(rng, v):
    return mix(*[(tone(note(s, 440), 0.7, (1, 0.3), rate=5, vibrato=0.004), i * 0.22, 1.0) for i, s in enumerate((3, 0, -4))]), 0.4


def react_surprise(rng, v):
    return mix(tone(note(12), 0.12, (1, 0.5), rate=22), (tone(note(18), 0.2, (1, 0.5), rate=14), 0.07, 1.0), (sweep(300, 1400, 0.1, rate=10), 0, 0.3)), 0.5


def ending_romance(rng, v):
    chords = [((0, 4, 7), 0.0), ((5, 9, 12), 0.45), ((7, 11, 14), 0.9), ((12, 16, 19, 24), 1.4)]
    parts = [(bell(note(s - 12), 1.7 if st > 1 else 1.0, 3.0), st + k * 0.03, 1.0) for notes, st in chords for k, s in enumerate(notes)]
    sparkle = [(bell(note(s + 12), 0.8, 5), 1.5 + i * 0.1, 0.35) for i, s in enumerate((0, 4, 7, 12, 16))]
    return mix(*parts, *sparkle), 0.55


def ending_friend(rng, v):
    return mix(*[(bell(note(s - 5), 1.2, 3.8), i * 0.22, 1.0) for i, s in enumerate((0, 4, 7, 9, 12))],
               (tone(note(-5), 1.4, (1, 0.3), rate=3), 0.7, 0.3)), 0.5


def ending_fail(rng, v):
    return mix(*[(tone(note(s, 330), 1.1, (1, 0.5, 0.3), rate=3.2, vibrato=0.006), i * 0.3, 1.0) for i, s in enumerate((0, -3, -7, -12))]), 0.45


def fade_out(rng, v):
    n = int(1.0 * SR)
    return mix((lowpass(noise(1.0, rng), np.linspace(3500, 250, n)) * env(n, 0.3, 0.5), 0, 0.6),
               (sweep(400, 120, 1.0, rate=1.5), 0, 0.5)), 0.4


def intro_card(rng, v):
    n = int(0.5 * SR)
    swoosh = bandpass(noise(0.5, rng), 500, 5000) * env(n, 0.3, 0.2)
    return mix((swoosh, 0, 0.5), (bell(note(7), 0.9, 4.5), 0.3, 1.0), (bell(note(14), 0.9, 4.5), 0.34, 0.5)), 0.5


# name, function, variants, max_seconds (sanity)
SOUNDS = [
    ("ButtonHover", ui_hover, 1), ("ButtonClick", ui_click, 1), ("ButtonBack", ui_back, 1),
    ("ModalOpen", modal_open, 1), ("ModalClose", modal_close, 1),
    ("SliderTick", slider_tick, 3), ("ToggleOn", toggle_on, 1), ("ToggleOff", toggle_off, 1),
    ("Toast", toast, 1), ("ChoiceSelect", choice_select, 1), ("TopicClick", topic_click, 2),
    ("DialogueAdvance", dialogue_advance, 3), ("TypeTick", type_tick, 4), ("MenuStart", menu_start, 1),
    ("PauseOn", pause_on, 1), ("PauseOff", pause_off, 1), ("MapOpen", map_open, 1), ("MapClose", map_close, 1),
    ("DebugOpen", debug_open, 1),
    ("Hover", hover, 1), ("Interact", interact, 2), ("DoorKnock", knock, 2), ("DoorLatch", door_latch, 2),
    ("BedRustle", bed_rustle, 2), ("CabinetOpen", cabinet_open, 1), ("CabinetClose", cabinet_close, 1),
    ("DoorCreak", door_creak, 1), ("SwitchOn", switch_on, 1), ("SwitchOff", switch_off, 1),
    ("TapDrip", tap_drip, 3), ("WaterSplash", water_splash, 2), ("PipeClank", pipe_clank, 2),
    ("Spark", spark, 2), ("Zap", zap, 2), ("ToiletFlush", toilet_flush, 1), ("Sizzle", sizzle, 1), ("Hum", hum, 1),
    ("FixComplete", fix_complete, 1), ("RepairFail", repair_fail, 1), ("ErrorBuzz", error_buzz, 1),
    ("Footstep", footstep, 4), ("DayEnd", day_end, 1), ("DayStart", day_start, 1),
    ("HunkPop", hunk_pop, 1), ("HunkLeave", hunk_leave, 1),
    ("ReactHappy", react_happy, 1), ("ReactHearts", react_hearts, 1), ("ReactAngry", react_angry, 1),
    ("ReactSad", react_sad, 1), ("ReactSurprise", react_surprise, 1),
    ("EndingRomance", ending_romance, 1), ("EndingFriend", ending_friend, 1), ("EndingFail", ending_fail, 1),
    ("FadeOut", fade_out, 1), ("IntroCard", intro_card, 1),
]


def write_wav(path, y):
    pcm = (np.clip(y, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="only sounds whose name contains this")
    args = ap.parse_args()

    os.makedirs(OUT, exist_ok=True)
    manifest = []
    for name, fn, variants in SOUNDS:
        for v in range(variants):
            fname = f"SFX_{name}_{v + 1}" if variants > 1 else f"SFX_{name}"
            manifest.append(fname + ".wav")
            if args.only and args.only.lower() not in name.lower():
                continue
            # crc32 (not hash()) so output is identical across runs and machines.
            rng = np.random.default_rng(zlib.crc32(fname.encode()))
            y, peak = fn(rng, v)
            y = finish(np.asarray(y, dtype=float), peak)
            assert len(y) / SR <= 3.2, f"{fname} is too long ({len(y) / SR:.2f}s)"
            write_wav(os.path.join(OUT, fname + ".wav"), y)
            print(f"{fname}.wav  {len(y) / SR:.2f}s")
    with open(os.path.join(OUT, "manifest.json"), "w") as f:
        json.dump(sorted(manifest), f, indent=2)
        f.write("\n")


if __name__ == "__main__":
    main()
