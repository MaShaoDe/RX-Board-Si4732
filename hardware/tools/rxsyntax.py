"""Einfache Syntaxpruefung der erzeugten KiCad-Dateien (Klammern, Strings, UUIDs, Netznamen)."""
import re, sys
def parse(txt):
    toks = re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()"]+', txt)
    stack = [[]]; 
    for t in toks:
        if t == "(": stack.append([])
        elif t == ")":
            if len(stack) < 2: raise SystemExit("zu viele ')'")
            x = stack.pop(); stack[-1].append(x)
        else: stack[-1].append(t)
    if len(stack) != 1: raise SystemExit("Klammern nicht geschlossen: %d offen" % (len(stack) - 1))
    return stack[0][0]
def walk(n, name, out):
    if isinstance(n, list):
        if n and n[0] == name: out.append(n)
        for c in n: walk(c, name, out)
    return out
for fn in sys.argv[1:]:
    txt = open(fn, encoding="utf-8").read()
    tree = parse(txt)
    uu = re.findall(r'\(uuid "([0-9a-f-]{36})"\)', txt)
    dup = {u for u in uu if uu.count(u) > 1}
    print(fn.split("/")[-1], "OK, Wurzel:", tree[0], "| UUIDs:", len(uu), "doppelt:", len(dup))
    if fn.endswith("kicad_pcb"):
        nets = {n[1] for n in walk(tree, "net", []) if len(n) == 3}
        names = {n[2].strip('"') for n in walk(tree, "net", []) if len(n) == 3}
        used = {n[1] for n in walk(tree, "net", []) if len(n) == 2}
        print("  Netze:", len(names), "| Footprints:", len(walk(tree, "footprint", [])), "| Segmente:", len(walk(tree, "segment", [])), "| Vias:", len(walk(tree, "via", [])), "| Zonen:", len(walk(tree, "zone", [])))
        print("  verwendete Netz-IDs ohne Eintrag:", sorted(u for u in used if u not in nets))
    if fn.endswith("kicad_sch"):
        syms = walk(tree, "symbol", []); inst = [s for s in syms if len(s) > 1 and isinstance(s[1], list) and s[1][0] == "lib_id"]
        print("  Symbole:", len(inst), "| Labels:", len(walk(tree, "label", [])), "| NoConnect:", len(walk(tree, "no_connect", [])))
