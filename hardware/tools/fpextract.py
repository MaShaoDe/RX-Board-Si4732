"""Liest die echten Footprints (KiCad-Standardbibliothek) aus einer von KiCad gespeicherten .kicad_pcb und
schreibt sie als fplib.json. Aufruf: python3 fpextract.py <datei.kicad_pcb>"""
import re, sys, json, os
def parse(txt):
    toks = re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()"]+', txt)
    st = [[]]
    for t in toks:
        if t == "(": st.append([])
        elif t == ")": x = st.pop(); st[-1].append(x)
        else: st[-1].append(t)
    return st[0][0]
def kids(n, name): return [c for c in n if isinstance(c, list) and c and c[0] == name]
def one(n, name):
    k = kids(n, name); return k[0] if k else None
def q(s): return s.strip('"')
def fl(x): return [float(v) for v in x]
def main(path, out):
    root = parse(open(path, encoding="utf-8").read())
    lib = {}
    for fp in kids(root, "footprint"):
        name = q(fp[1])
        if name in lib: continue
        d = {"descr": q(one(fp, "descr")[1]) if one(fp, "descr") else "", "tags": q(one(fp, "tags")[1]) if one(fp, "tags") else "",
             "attr": [t for t in (one(fp, "attr") or ["attr"])[1:]], "pads": [], "gfx": [], "model": None}
        m = one(fp, "model")
        if m: d["model"] = q(m[1])
        for p in kids(fp, "pad"):
            sz = fl(one(p, "size")[1:3]); at = one(p, "at")
            dr = one(p, "drill")
            rr = one(p, "roundrect_rratio")
            d["pads"].append({"num": q(p[1]), "type": p[2], "shape": p[3], "at": fl(at[1:3]), "size": sz,
                              "drill": float(dr[1]) if dr else 0.0, "layers": [q(x) for x in one(p, "layers")[1:]],
                              "rr": float(rr[1]) if rr else None})
        for g in fp:
            if not (isinstance(g, list) and g and g[0] in ("fp_line", "fp_rect", "fp_circle", "fp_poly", "fp_text")): continue
            k = g[0]; e = {"kind": k, "layer": q(one(g, "layer")[1])}
            st = one(g, "stroke")
            if st: e["width"] = float(one(st, "width")[1]); e["stype"] = one(st, "type")[1]
            fi = one(g, "fill")
            if fi: e["fill"] = fi[1]
            if k in ("fp_line", "fp_rect"): e["start"] = fl(one(g, "start")[1:3]); e["end"] = fl(one(g, "end")[1:3])
            elif k == "fp_circle": e["center"] = fl(one(g, "center")[1:3]); e["end"] = fl(one(g, "end")[1:3])
            elif k == "fp_poly": e["pts"] = [fl(x[1:3]) for x in one(g, "pts")[1:]]
            elif k == "fp_text":
                e["ttype"] = g[1]; e["text"] = q(g[2]); a = one(g, "at"); e["at"] = fl(a[1:3])
                f = one(one(g, "effects"), "font"); e["size"] = fl(one(f, "size")[1:3]); e["thickness"] = float(one(f, "thickness")[1])
            d["gfx"].append(e)
        lib[name] = d
    json.dump(lib, open(out, "w"), indent=1)
    print(len(lib), "Footprints ->", out)
if __name__ == "__main__":
    main(sys.argv[1], os.path.join(os.path.dirname(os.path.abspath(__file__)), "fplib.json"))
