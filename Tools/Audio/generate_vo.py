#!/usr/bin/env python3
"""
Generate placeholder voice-over for the dialogue scripts with the free, local
Kokoro neural TTS model (Apache-2.0, https://github.com/hexgrad/kokoro).

    uv run --python 3.11 --with kokoro-onnx --with soundfile Tools/Audio/generate_vo.py
    uv run ... Tools/Audio/generate_vo.py --force          # regenerate everything
    uv run ... Tools/Audio/generate_vo.py --only v3_dinner # just lines whose key contains this

Then import into Unreal (editor must be running):

    python3 Tools/run_in_editor.py Tools/Editor/import_vo.py

Output: "Art Source/Audio/VO/<script>/VO_<script>_<node>_<line>.wav", where <line>
is the 0-based index into the node's "lines" array. The game looks up
/Game/ICanFixHim/Audio/VO/<script>/VO_<script>_<node>_<line> when it shows that line,
so editing a line's text just needs this script re-run (unchanged lines are skipped
via manifest.json). The player is never voiced. Narration (*...*) is never voiced.

These are stand-ins until we record the final cast in ElevenLabs; see
docs/03 Art & Audio/Voice Casting.md.
"""
import argparse
import hashlib
import json
import os
import re
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DIALOGUE = os.path.join(ROOT, "Content/ICanFixHim/Data/Dialogue")
OUT = os.path.join(ROOT, "Art Source/Audio/VO")
MODELS = os.path.join(ROOT, "Saved/VOModels")  # gitignored; ~350 MB, downloaded on first run
MODEL_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/"
MODEL_FILES = ("kokoro-v1.0.onnx", "voices-v1.0.bin")

# Who gets a voice, and which Kokoro voice stands in for them. A voice is a weighted
# blend of Kokoro's built-in speakers. Bump "rev" to force a character's lines to regenerate.
VOICES = {
    "lukey": {
        # All-American, big friendly jock: warm, grinning, energetic.
        "blend": {"am_fenrir": 0.5, "am_michael": 0.3, "am_puck": 0.2},
        "speed": 1.05,
        "lang": "en-us",
        "rev": 1,
    },
}


def speaker_of(raw, speakers):
    """Mirror of ParseLine in FixHimDialogueSubsystem.cpp. Returns (speaker key, text)."""
    text = raw.strip()
    if text.lower().startswith("you:"):
        return "player", text[4:].strip()
    for name in speakers:
        if text.lower().startswith(name.lower() + ":"):
            return name.lower(), text[len(name) + 1:].strip()
    if len(text) > 1 and text.startswith("*") and text.endswith("*"):
        return "narration", text
    return "hunk", text


def speakable(text, hunk_name):
    """Turn a script line into something TTS can read. Returns None if nothing is left to say."""
    t = re.sub(r"\*[^*]*\*", " ", text)                       # inline stage directions
    t = re.sub(r"\[([^\]|]+)\|[^\]]*\]", r"\1", t)            # [shown|topic]
    t = re.sub(r"\[([^\]]+)\]", r"\1", t)                     # [topic]
    t = t.replace("{name}", hunk_name)
    # The player picks their name, so the recording skips it. "{player}, did you..." -> "Did you..."
    t = re.sub(r"^\s*\{player\}\s*[,.!?]*\s*", "", t)
    t = re.sub(r"\s*,?\s*\{player\}", "", t)
    # ALL-CAPS emphasis reads as an acronym in the phonemizer; say it as a word.
    t = re.sub(r"\b([A-Z][A-Z']+)\b", lambda m: m.group(1) if m.group(1).startswith("I'") else m.group(1).lower(), t)
    t = t.replace("—", ", ").replace("–", ", ")
    t = re.sub(r"\s+", " ", t).strip()
    t = re.sub(r"^[,\s]+", "", t)
    if not re.search(r"[A-Za-z]", t):
        return None
    return t[0].upper() + t[1:]


def collect():
    """Every voiced line in every script: [(script, node, index, voice, text)]."""
    lines = []
    for fn in sorted(os.listdir(DIALOGUE)):
        if not fn.endswith(".json"):
            continue
        with open(os.path.join(DIALOGUE, fn), encoding="utf-8") as f:
            d = json.load(f)
        script, kind = d["id"], d.get("kind", "hunk")
        speakers = d.get("speakers", [])
        for node_id, node in d.get("nodes", {}).items():
            raw_lines = node.get("lines", [])
            if isinstance(raw_lines, str):
                raw_lines = [raw_lines]
            for i, raw in enumerate(raw_lines):
                who, text = speaker_of(raw, speakers)
                voice = script if (who == "hunk" and kind == "hunk") else who
                if voice not in VOICES:
                    continue
                say = speakable(text, d.get("name", script))
                if say:
                    lines.append((script, node_id, i, voice, say))
    return lines


def ensure_models():
    os.makedirs(MODELS, exist_ok=True)
    for name in MODEL_FILES:
        path = os.path.join(MODELS, name)
        if not os.path.exists(path):
            print(f"downloading {name}...")
            urllib.request.urlretrieve(MODEL_URL + name, path + ".part")
            os.replace(path + ".part", path)
    return [os.path.join(MODELS, n) for n in MODEL_FILES]


def master(audio, sr):
    """Trim silence, level to a consistent loudness, short fades."""
    import numpy as np
    a = np.asarray(audio, dtype=np.float32)
    loud = np.where(np.abs(a) > 0.01)[0]
    if len(loud):
        a = a[max(0, loud[0] - int(0.03 * sr)): loud[-1] + int(0.12 * sr)]
    rms = float(np.sqrt(np.mean(a ** 2))) or 1e-6
    a = a * (0.12 / rms)
    peak = float(np.max(np.abs(a))) or 1.0
    if peak > 0.95:
        a = np.tanh(a / peak * 1.2) / np.tanh(1.2) * 0.95   # gentle limiter
    fade = int(0.01 * sr)
    a[:fade] *= np.linspace(0, 1, fade)
    a[-fade:] *= np.linspace(1, 0, fade)
    return a


def write_manifest(path, manifest):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(dict(sorted(manifest.items())), f, indent=1, ensure_ascii=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--only", default="")
    ap.add_argument("--dry-run", action="store_true", help="print what would be spoken")
    args = ap.parse_args()

    lines = collect()
    if args.dry_run:
        for script, node, i, voice, say in lines:
            print(f"{script}/{node}/{i} [{voice}] {say}")
        print(len(lines), "lines")
        return

    import numpy as np
    import soundfile as sf
    from kokoro_onnx import Kokoro

    kokoro = Kokoro(*ensure_models())
    manifest_path = os.path.join(OUT, "manifest.json")
    manifest = {}
    if os.path.exists(manifest_path):
        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)

    styles = {}
    keep = set()
    made = 0
    for script, node, i, voice, say in lines:
        cfg = VOICES[voice]
        key = f"VO_{script}_{node}_{i}"
        rel = f"{script}/{key}.wav"
        keep.add(rel)
        digest = hashlib.sha1(json.dumps([say, cfg], sort_keys=True).encode()).hexdigest()[:12]
        path = os.path.join(OUT, rel)
        if args.only and args.only not in key:
            continue
        if not args.force and manifest.get(rel, {}).get("hash") == digest and os.path.exists(path):
            continue
        if voice not in styles:
            styles[voice] = sum(w * kokoro.get_voice_style(n) for n, w in cfg["blend"].items())
        audio, sr = kokoro.create(say, voice=styles[voice], speed=cfg["speed"], lang=cfg["lang"])
        os.makedirs(os.path.dirname(path), exist_ok=True)
        sf.write(path, master(audio, sr), sr, subtype="PCM_16")
        manifest[rel] = {"hash": digest, "voice": voice, "text": say}
        made += 1
        if made % 10 == 0:
            write_manifest(manifest_path, manifest)  # survive interruptions
        print(f"[{made}] {key}: {say}")

    # Lines that were deleted or stopped being voiced.
    if not args.only:
        for rel in list(manifest):
            if rel not in keep:
                p = os.path.join(OUT, rel)
                if os.path.exists(p):
                    os.remove(p)
                del manifest[rel]
                print("removed", rel)

    write_manifest(manifest_path, manifest)
    print(f"done: {made} generated, {len(keep)} voiced lines total")


if __name__ == "__main__":
    sys.exit(main())
