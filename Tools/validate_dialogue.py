#!/usr/bin/env python3
"""
Lint the dialogue JSON in Content/ICanFixHim/Data/Dialogue (same rules the game applies at load,
plus reachability). Run before committing dialogue changes:

    python3 Tools/validate_dialogue.py
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.path.join(ROOT, "Content", "ICanFixHim", "Data", "Dialogue")
ENDINGS = {"romance_success", "romance_failure", "friend_success", "friend_failure"}
STATS = {"romance", "friendship", "friction"}
COND_TOKEN = re.compile(r"\s*(\|\||&&|==|!=|>=|<=|[<>()!+-]|\d+|[A-Za-z_][A-Za-z0-9_.]*)")


def check_condition(expr):
    pos, s = 0, expr or ""
    while pos < len(s):
        m = COND_TOKEN.match(s, pos)
        if not m:
            if s[pos:].strip() == "":
                return None
            return f"bad token at {pos}: {s[pos:]!r}"
        pos = m.end()
    return None


def topics_in(text):
    out = []
    for inner in re.findall(r"\[([^\]]+)\]", text):
        out.append((inner.split("|", 1)[1] if "|" in inner else inner).strip().lower())
    return out


def validate(path, hunk_ids):
    errs, warns = [], []
    d = json.load(open(path))
    hid = d.get("id", "?")
    nodes = d.get("nodes", {})

    def ref(where, target):
        if target and target not in nodes:
            errs.append(f"{where} -> missing node '{target}'")

    def effects(where, do):
        for k in (do or {}):
            scope, _, name = k.rpartition(".")
            if scope == "flag":
                continue
            if name not in STATS:
                errs.append(f"{where}: unknown effect '{k}'")
            if scope and scope not in hunk_ids:
                errs.append(f"{where}: unknown hunk '{scope}' in effect '{k}'")

    for e in d.get("entries", []):
        ref("entry", e.get("node"))
        if (m := check_condition(e.get("if"))):
            errs.append(f"entry condition {m}")
    for nid, n in nodes.items():
        lines = n.get("lines", [])
        if not lines:
            errs.append(f"{nid}: no lines")
        if not n.get("choices") and not n.get("goto") and not n.get("end") and not n.get("ending"):
            errs.append(f"{nid}: dead end")
        ref(f"{nid}.goto", n.get("goto"))
        effects(nid, n.get("do"))
        if n.get("ending") and n["ending"] != "auto" and n["ending"] not in d.get("endings", {}):
            errs.append(f"{nid}: ending '{n['ending']}' has no card")
        topics = {k.lower(): v for k, v in n.get("topics", {}).items()}
        for line in lines:
            for t in topics_in(line):
                if t not in topics:
                    errs.append(f"{nid}: [{t}] has no topic entry")
        for t, v in topics.items():
            ref(f"{nid} topic {t}", v if isinstance(v, str) else v.get("goto"))
            if isinstance(v, dict):
                effects(f"{nid} topic {t}", v.get("do"))
        for c in n.get("choices", []):
            ref(f"{nid} choice", c.get("goto"))
            effects(f"{nid} choice", c.get("do"))
            if (m := check_condition(c.get("if"))):
                errs.append(f"{nid} choice condition {m}")
        if n.get("choices") and all(c.get("if") for c in n["choices"]):
            warns.append(f"{nid}: every choice is conditional (player could get stuck)")

    # Reachability from entries.
    seen, stack = set(), [e["node"] for e in d.get("entries", []) if e.get("node") in nodes]
    while stack:
        nid = stack.pop()
        if nid in seen:
            continue
        seen.add(nid)
        n = nodes[nid]
        nxt = [n.get("goto")] + [c.get("goto") for c in n.get("choices", [])]
        nxt += [v if isinstance(v, str) else v.get("goto") for v in n.get("topics", {}).values()]
        stack += [x for x in nxt if x in nodes]
    for nid in nodes:
        if nid not in seen:
            warns.append(f"{nid}: unreachable")
    missing = ENDINGS - set(d.get("endings", {}))
    if missing:
        warns.append(f"missing ending cards: {sorted(missing)}")
    return hid, errs, warns, len(nodes), sum(len(" ".join(n.get("lines", [])).split()) for n in nodes.values())


def main():
    files = sorted(glob.glob(os.path.join(DIR, "*.json")))
    hunk_ids = {json.load(open(f)).get("id") for f in files}
    bad = 0
    for f in files:
        hid, errs, warns, n, words = validate(f, hunk_ids)
        print(f"{hid:10s} {n:3d} nodes  {words:5d} words  {len(errs)} errors  {len(warns)} warnings")
        for e in errs:
            print("   ERROR", e)
        for w in warns:
            print("   warn ", w)
        bad += len(errs)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
