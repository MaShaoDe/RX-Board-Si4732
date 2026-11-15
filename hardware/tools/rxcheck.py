"""Unabhaengige Pruefung des Routers: Abstaende, Randabstand, Verbindungen."""
import math
from rxroute import *

def pt_rect(px, py, it):
    dx = max(it.x0 - px, 0, px - it.x1); dy = max(it.y0 - py, 0, py - it.y1); return math.hypot(dx, dy)
def seg_pts(it, step=0.02):
    n = max(1, int(math.hypot(it.x2 - it.x1, it.y2 - it.y1) / step))
    return [(it.x1 + (it.x2 - it.x1) * k / n, it.y1 + (it.y2 - it.y1) * k / n) for k in range(n + 1)]
def seg_seg(a, b):
    # Mindestabstand zweier Strecken
    def pd(p, q1, q2):
        vx, vy = q2[0] - q1[0], q2[1] - q1[1]; L = vx * vx + vy * vy
        t = 0 if L == 0 else max(0, min(1, ((p[0] - q1[0]) * vx + (p[1] - q1[1]) * vy) / L))
        return math.hypot(p[0] - q1[0] - t * vx, p[1] - q1[1] - t * vy)
    A1, A2, B1, B2 = (a.x1, a.y1), (a.x2, a.y2), (b.x1, b.y1), (b.x2, b.y2)
    def inter(p1, p2, p3, p4):
        def o(p, q, r): return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
        return o(p1, p2, p3) * o(p1, p2, p4) < 0 and o(p3, p4, p1) * o(p3, p4, p2) < 0
    if inter(A1, A2, B1, B2): return 0.0
    return min(pd(A1, B1, B2), pd(A2, B1, B2), pd(B1, A1, A2), pd(B2, A1, A2))

def dist(a, b):
    """Abstand der Kupferrandlinien (kann negativ sein = Ueberlappung)."""
    ka, kb = a.kind, b.kind
    if ka == "rect" and kb == "rect":
        dx = max(a.x0 - b.x1, b.x0 - a.x1, 0); dy = max(a.y0 - b.y1, b.y0 - a.y1, 0); return math.hypot(dx, dy)
    if ka in ("disk", "hole") and kb in ("disk", "hole"):
        return math.hypot(a.x - b.x, a.y - b.y) - a.r - b.r
    if ka == "seg" and kb == "seg":
        return seg_seg(a, b) - a.w / 2 - b.w / 2
    for p, q in ((a, b), (b, a)):
        if p.kind == "rect" and q.kind in ("disk", "hole"): return pt_rect(q.x, q.y, p) - q.r
        if p.kind == "rect" and q.kind == "seg": return min(pt_rect(x, y, p) for x, y in seg_pts(q)) - q.w / 2
        if p.kind in ("disk", "hole") and q.kind == "seg":
            return min(math.hypot(x - p.x, y - p.y) for x, y in seg_pts(q)) - p.r - q.w / 2
    raise ValueError((ka, kb))

def courtyard_errors():
    shapes = []
    for ref, kind, val, fpk, x, y, nets, d in PARTS:
        for s in courtyard(fpk):
            if s[0] == "rect": shapes.append((ref, "rect", x + s[1], y + s[2], x + s[3], y + s[4]))
            else: shapes.append((ref, "circle", x + s[1], y + s[2], s[3], 0))
    errs = []; seen = set()
    for i in range(len(shapes)):
        for j in range(i + 1, len(shapes)):
            a, b = shapes[i], shapes[j]
            if a[0] == b[0]: continue
            hit = False
            if a[1] == "rect" and b[1] == "rect":
                hit = min(a[4], b[4]) - max(a[2], b[2]) > 1e-6 and min(a[5], b[5]) - max(a[3], b[3]) > 1e-6
            elif a[1] == "circle" and b[1] == "circle":
                hit = math.hypot(a[2] - b[2], a[3] - b[3]) < a[4] + b[4] - 1e-6
            else:
                ci, re_ = (a, b) if a[1] == "circle" else (b, a)
                dx = max(re_[2] - ci[2], 0, ci[2] - re_[4]); dy = max(re_[3] - ci[3], 0, ci[3] - re_[5])
                hit = math.hypot(dx, dy) < ci[4] - 1e-6
            if hit and (a[0], b[0]) not in seen:
                seen.add((a[0], b[0])); errs.append(f"Abstandsflaechen ueberlappen: {a[0]} und {b[0]}")
    return errs

def check(r):
    errs = courtyard_errors(); items = r.items; n = len(items); minc = 9
    for i in range(n):
        for j in range(i + 1, n):
            a, b = items[i], items[j]
            if not set(a.layers) & set(b.layers): continue
            if a.net is not None and a.net == b.net: continue
            if a.kind == "hole" and b.kind == "hole": continue
            need = 0.0 if "hole" in (a.kind, b.kind) else 0.15
            d = dist(a, b)
            minc = min(minc, d) if not "hole" in (a.kind, b.kind) else minc
            if d < need - 1e-6:
                errs.append(f"Abstand {d:.3f} < {need}: {a.ref}.{a.pad}/{a.kind}:{a.net} - {b.ref}.{b.pad}/{b.kind}:{b.net}")
    vias = [it for it in items if getattr(it, "via", False)]
    for i in range(len(vias)):
        for j in range(i + 1, len(vias)):
            d = math.hypot(vias[i].x - vias[j].x, vias[i].y - vias[j].y) - VIA_DRILL
            if d < 0.5 - 1e-6: errs.append(f"Bohrung zu Bohrung {d:.2f} mm: Vias bei ({vias[i].x:.1f},{vias[i].y:.1f}) und ({vias[j].x:.1f},{vias[j].y:.1f})")
    # Kante
    for it in items:
        if it.kind == "hole": continue
        if it.kind == "rect": xs, ys = (it.x0, it.x1), (it.y0, it.y1)
        elif it.kind == "disk": xs, ys = (it.x - it.r, it.x + it.r), (it.y - it.r, it.y + it.r)
        else: xs, ys = (min(it.x1, it.x2) - it.w / 2, max(it.x1, it.x2) + it.w / 2), (min(it.y1, it.y2) - it.w / 2, max(it.y1, it.y2) + it.w / 2)
        e = min(xs[0], ys[0], W - xs[1], H - ys[1])
        if e < 0.3 - 1e-6: errs.append(f"Kantenabstand {e:.2f}: {it.ref}.{it.pad}")
    # Verbindungen
    parent = list(range(n))
    def f(x):
        while parent[x] != x: parent[x] = parent[parent[x]]; x = parent[x]
        return x
    def inside(px, py, it):
        if it.kind == "rect": return it.x0 - 1e-6 <= px <= it.x1 + 1e-6 and it.y0 - 1e-6 <= py <= it.y1 + 1e-6
        return math.hypot(px - it.x, py - it.y) <= it.r + 1e-6
    def pt_seg(px, py, s):
        vx, vy = s.x2 - s.x1, s.y2 - s.y1; Lq = vx * vx + vy * vy
        t = 0 if Lq == 0 else max(0, min(1, ((px - s.x1) * vx + (py - s.y1) * vy) / Lq))
        return math.hypot(px - s.x1 - t * vx, py - s.y1 - t * vy)
    for i in range(n):
        for j in range(i + 1, n):
            a, b = items[i], items[j]
            if a.net is None or a.net != b.net or not set(a.layers) & set(b.layers): continue
            ok = False
            # KiCad verbindet, wenn der Endpunkt einer Bahn im Pad / Via liegt oder auf einer anderen Bahn
            for p, q in ((a, b), (b, a)):
                if p.kind == "seg":
                    ends = ((p.x1, p.y1), (p.x2, p.y2))
                    if q.kind in ("rect", "disk"): ok = ok or any(inside(ex, ey, q) for ex, ey in ends)
                    elif q.kind == "seg": ok = ok or any(pt_seg(ex, ey, q) <= q.w / 2 + 1e-6 for ex, ey in ends)
            if a.kind != "seg" and b.kind != "seg" and dist(a, b) <= 0.001: ok = True
            if ok: parent[f(i)] = f(j)
    for net in NETS:
        its = [i for i, it in enumerate(items) if it.net == net]
        pads = [i for i in its if items[i].kind != "seg" and not getattr(items[i], "via", False)]
        comps = {}
        for i in pads: comps.setdefault(f(i), []).append(items[i].ref + "." + items[i].pad)
        if net == "GND":
            for root, ps in comps.items():
                grp = [items[i] for i in its if f(i) == root]
                tht = any(len(g.layers) == 2 for g in grp)
                if not tht: errs.append(f"GND-Pad ohne Via/THT: {ps}")
        elif len(comps) > 1:
            errs.append(f"Netz {net} getrennt: {list(comps.values())}")
    return errs, minc

if __name__ == "__main__":
    r = run(); errs, minc = check(r)
    print("\n".join(r.log)); print("\n".join(errs[:40]) or "keine Fehler"); print("kleinster Abstand Kupfer-Kupfer: %.3f mm" % minc)
