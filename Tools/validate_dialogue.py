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
# Node "fx" values and inline {fx:name} tags (played by UFixHimDialogueWidget).
FX = {"fade", "hearts"}
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

    def aside_warns(where, start):
        # Walk the aside chain (gotos, choices, one-way topic diverts; nested asides return here
        # by themselves, so don't follow them). It must be able to reach a "return" node.
        seen, stack, enders = set(), [start], []
        while stack:
            nid = stack.pop()
            if nid not in nodes or nid in seen:
                continue
            seen.add(nid)
            n = nodes[nid]
            if n.get("return") and not n.get("choices"):
                continue
            if n.get("end") or n.get("ending"):
                enders.append(nid)
            stack.append(n.get("goto"))
            stack += [c.get("goto") for c in n.get("choices", [])]
            stack += [v if isinstance(v, str) else v.get("goto") for v in n.get("topics", {}).values()
                      if isinstance(v, str) or not v.get("aside")]
        if not any(nodes[x].get("return") for x in seen):
            warns.append(f"{where}: aside chain from '{start}' never reaches a \"return\": true node")
        for x in enders:
            warns.append(f"{where}: aside chain reaches '{x}', which ends the conversation mid-aside")

    for e in d.get("entries", []):
        ref("entry", e.get("node"))
        if (m := check_condition(e.get("if"))):
            errs.append(f"entry condition {m}")
    # Hypertext dead ends (StoryWriter link nodes): reached only through non-aside [word] links,
    # no flow of their own. The game rewinds to the line the link was clicked on.
    strong = {e.get("node") for e in d.get("entries", [])}
    linked = set()
    for n in nodes.values():
        strong.add(n.get("goto"))
        strong.update(c.get("goto") for c in n.get("choices", []))
        linked.update(v if isinstance(v, str) else v.get("goto") for v in n.get("topics", {}).values()
                      if isinstance(v, str) or not v.get("aside"))
    hypertext = linked - strong

    for nid, n in nodes.items():
        lines = n.get("lines", [])
        if not lines:
            errs.append(f"{nid}: no lines")
        if not n.get("choices") and not n.get("goto") and not n.get("end") and not n.get("ending") and not n.get("return") \
                and nid not in hypertext:
            errs.append(f"{nid}: dead end")
        if n.get("return") and (n.get("choices") or n.get("goto") or n.get("end") or n.get("ending")):
            warns.append(f"{nid}: 'return' node also has choices/goto/end/ending (return wins once its lines run out, unless it has choices)")
        ref(f"{nid}.goto", n.get("goto"))
        effects(nid, n.get("do"))
        if n.get("ending") and n["ending"] != "auto" and n["ending"] not in d.get("endings", {}):
            errs.append(f"{nid}: ending '{n['ending']}' has no card")
        if n.get("fx") and n["fx"] not in FX:
            errs.append(f"{nid}: unknown fx '{n['fx']}' (known: {sorted(FX)})")
        for line in lines:
            for tag in re.findall(r"\{fx:([^}]*)\}", line):
                if tag.strip().lower() not in FX:
                    errs.append(f"{nid}: unknown inline fx '{{fx:{tag}}}' (known: {sorted(FX)})")
        topics = {k.lower(): v for k, v in n.get("topics", {}).items()}
        for line in lines:
            for t in topics_in(line):
                if t not in topics:
                    errs.append(f"{nid}: [{t}] has no topic entry")
        for t, v in topics.items():
            ref(f"{nid} topic {t}", v if isinstance(v, str) else v.get("goto"))
            if isinstance(v, dict):
                effects(f"{nid} topic {t}", v.get("do"))
                if "aside" in v and not isinstance(v["aside"], bool):
                    errs.append(f"{nid} topic {t}: 'aside' must be true/false")
                if v.get("aside"):
                    aside_warns(f"{nid} topic {t}", v.get("goto"))
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
    if missing and d.get("kind", "hunk") == "hunk":
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
