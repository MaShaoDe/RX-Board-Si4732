"""Einfacher Gitter-Router (A*, 2 Lagen) fuer das RX-Board. Masse laeuft ueber Kupferflaechen (Zonen)."""
import heapq, math
import numpy as np
from rxmodel import *

RES = 0.1
NX, NY = int(round(W / RES)) + 1, int(round(H / RES)) + 1
CLR = 0.2          # Abstand Kupfer zu Kupfer
EDGE = 0.45        # Abstand Kupfer zur Platinenkante
VIA_D, VIA_DRILL = 0.6, 0.3
VIA_PITCH = 1.0   # Mittenabstand Via zu Via (Bohrung zu Bohrung mindestens 0.5 mm)
HOLE_R = 1.35 + 0.6
WIDTH = {"3V3": 0.4}
DEF_W = 0.25

def cell(v): return int(round(v / RES))

class Item:
    def __init__(self, kind, net, layers, **kw):
        self.kind, self.net, self.layers = kind, net, layers; self.__dict__.update(kw)

def pad_items():
    items = []
    for ref, kind, val, fpk, x, y, nets, desc in PARTS:
        for (num, typ, shape, px, py, w, h, drill, _rr) in FP[fpk][1]():
            net = nets.get(num)
            ax, ay = x + px, y + py
            if typ == "npth":
                items.append(Item("hole", None, [0, 1], x=ax, y=ay, r=HOLE_R, ref=ref, pad=num))
            elif shape == "circle" and typ == "thru":
                items.append(Item("disk", net, [0, 1], x=ax, y=ay, r=w / 2, ref=ref, pad=num))
            elif shape == "circle":
                items.append(Item("disk", net, [0], x=ax, y=ay, r=w / 2, ref=ref, pad=num))
            else:
                lay = [0, 1] if typ == "thru" else [0]
                items.append(Item("rect", net, lay, x0=ax - w / 2, y0=ay - h / 2, x1=ax + w / 2, y1=ay + h / 2,
                                  x=ax, y=ay, ref=ref, pad=num))
    return items

def paint_rect(m, x0, y0, x1, y1):
    ix0, ix1 = max(0, int(math.floor(x0 / RES))), min(NX - 1, int(math.ceil(x1 / RES)))
    iy0, iy1 = max(0, int(math.floor(y0 / RES))), min(NY - 1, int(math.ceil(y1 / RES)))
    m[iy0:iy1 + 1, ix0:ix1 + 1] = True

def paint_disk(m, cx, cy, r):
    ix0, ix1 = max(0, int(math.floor((cx - r) / RES))), min(NX - 1, int(math.ceil((cx + r) / RES)))
    iy0, iy1 = max(0, int(math.floor((cy - r) / RES))), min(NY - 1, int(math.ceil((cy + r) / RES)))
    if ix1 < ix0 or iy1 < iy0: return
    xs = (np.arange(ix0, ix1 + 1) * RES)[None, :]
    ys = (np.arange(iy0, iy1 + 1) * RES)[:, None]
    m[iy0:iy1 + 1, ix0:ix1 + 1] |= ((xs - cx) ** 2 + (ys - cy) ** 2) <= r * r + 1e-9

def paint_item(masks, it, infl):
    for l in it.layers:
        m = masks[l]
        if it.kind == "rect":
            paint_rect(m, it.x0 - infl, it.y0 - infl, it.x1 + infl, it.y1 + infl)
        elif it.kind in ("disk", "hole"):
            paint_disk(m, it.x, it.y, it.r + infl)
        elif it.kind == "seg":
            n = max(1, int(math.hypot(it.x2 - it.x1, it.y2 - it.y1) / 0.05))
            for k in range(n + 1):
                t = k / n
                paint_disk(m, it.x1 + (it.x2 - it.x1) * t, it.y1 + (it.y2 - it.y1) * t, it.w / 2 + infl)

def border_mask(margin):
    m = np.zeros((NY, NX), bool)
    b = int(math.ceil(margin / RES))
    m[:b + 1, :] = True; m[-b - 1:, :] = True; m[:, :b + 1] = True; m[:, -b - 1:] = True
    return m

DIRS = [(1, 0, 10), (-1, 0, 10), (0, 1, 10), (0, -1, 10), (1, 1, 14), (-1, 1, 14), (1, -1, 14), (-1, -1, 14)]

class Router:
    def __init__(self):
        self.items = pad_items()
        self.pads = [i for i in self.items if i.kind != "hole"]
        self.log = []

    def masks_for(self, net, hw):
        tm = [np.zeros((NY, NX), bool), np.zeros((NY, NX), bool)]
        vm = [np.zeros((NY, NX), bool), np.zeros((NY, NX), bool)]
        for it in self.items:
            if it.net is not None and it.net == net: continue
            paint_item(tm, it, CLR + hw)
            paint_item(vm, it, CLR + VIA_D / 2)
        b1, b2 = border_mask(EDGE + hw), border_mask(EDGE + VIA_D / 2)
        for l in (0, 1): tm[l] |= b1; vm[l] |= b2
        via_bad = vm[0] | vm[1]
        for it in self.items:
            if getattr(it, "via", False): paint_disk(via_bad, it.x, it.y, VIA_PITCH)
        return tm, via_bad

    def route_net(self, net, bbox_margin=None):
        hw = WIDTH.get(net, DEF_W) / 2
        pads = [p for p in self.pads if p.net == net]
        if len(pads) < 2: return True
        tm, via_bad = self.masks_for(net, hw)
        def pad_cells(p):
            cs = set()
            if p.kind == "rect":
                for iy in range(cell(p.y0) - 1, cell(p.y1) + 2):
                    for ix in range(cell(p.x0) - 1, cell(p.x1) + 2):
                        if p.x0 + 0.03 <= ix * RES <= p.x1 - 0.03 and p.y0 + 0.03 <= iy * RES <= p.y1 - 0.03: cs.add((ix, iy))
            else:
                r = p.r
                for iy in range(cell(p.y - r), cell(p.y + r) + 1):
                    for ix in range(cell(p.x - r), cell(p.x + r) + 1):
                        if (ix * RES - p.x) ** 2 + (iy * RES - p.y) ** 2 <= (r - 0.03) ** 2: cs.add((ix, iy))
            return cs
        connected = [pads[0]]
        tree = {}   # (ix,iy,l) -> exact (x,y) or None
        def add_pad_tree(p):
            c = (cell(p.x), cell(p.y))
            for l in p.layers: tree[(c[0], c[1], l)] = (p.x, p.y)
        add_pad_tree(pads[0])
        rest = pads[1:]
        ok = True
        while rest:
            cx = sum(p.x for p in connected) / len(connected); cy = sum(p.y for p in connected) / len(connected)
            rest.sort(key=lambda p: (p.x - cx) ** 2 + (p.y - cy) ** 2)
            tgt = rest.pop(0)
            res = self.astar(tree, tgt, pad_cells(tgt), tm, via_bad, net, hw)
            if res is None:
                self.log.append(f"FEHLER: {net} {tgt.ref}.{tgt.pad} nicht routbar"); ok = False; continue
            self.commit(res, tree, net, hw, tgt)
            connected.append(tgt); add_pad_tree(tgt)
        return ok

    def astar(self, tree, tgt, tcells, tm, via_bad, net, hw, via_cost=70, bcu_pen=2, turn=12):
        tx, ty = cell(tgt.x), cell(tgt.y)
        tl = set(tgt.layers)
        def h(ix, iy):
            dx, dy = abs(ix - tx), abs(iy - ty)
            return 10 * (dx + dy) - 6 * min(dx, dy)
        g = {}; par = {}
        pq = []
        for (ix, iy, l) in tree:
            st = (ix, iy, l, 8); g[st] = 0; heapq.heappush(pq, (h(ix, iy), 0, st))
        while pq:
            f, gc, st = heapq.heappop(pq)
            if g.get(st, 1e18) < gc: continue
            ix, iy, l, d = st
            if (ix, iy) in tcells and l in tl:
                path = []; s = st
                while s in par: path.append(s); s = par[s]
                path.append(s); path.reverse(); return path
            for k, (dx, dy, c) in enumerate(DIRS):
                nx, ny = ix + dx, iy + dy
                if not (0 <= nx < NX and 0 <= ny < NY): continue
                if tm[l][ny, nx]:
                    # Pad des Zielnetzes darf betreten werden, wenn es nicht blockiert ist (Netz-eigen: nie blockiert)
                    continue
                if dx and dy and (tm[l][iy, nx] or tm[l][ny, ix]): continue
                nc = gc + c + (bcu_pen if l == 1 else 0) + (turn if (d != 8 and d != k) else 0)
                ns = (nx, ny, l, k)
                if nc < g.get(ns, 1e18):
                    g[ns] = nc; par[ns] = st; heapq.heappush(pq, (nc + h(nx, ny), nc, ns))
            # Via
            if not via_bad[iy, ix] and not tm[1 - l][iy, ix]:
                ns = (ix, iy, 1 - l, 8); nc = gc + via_cost
                if nc < g.get(ns, 1e18):
                    g[ns] = nc; par[ns] = st; heapq.heappush(pq, (nc + h(ix, iy), nc, ns))
        return None

    def commit(self, path, tree, net, hw, tgt):
        pts = [(s[0], s[1], s[2]) for s in path]
        # Segmente je Lage, Vias bei Lagenwechsel
        seg_start = 0
        def exact(c):
            return tree.get(c) or (c[0] * RES, c[1] * RES)
        poly = []  # (x,y,l)
        for i, c in enumerate(pts):
            x, y = c[0] * RES, c[1] * RES
            if i == 0 and c in tree and tree[c]: x, y = tree[c]
            poly.append((x, y, c[2]))
        if getattr(tgt, "pad", None) not in (None, "") or hasattr(tgt, "ref"):
            last = poly[-1]
            if abs(last[0] - tgt.x) > 1e-6 or abs(last[1] - tgt.y) > 1e-6: poly.append((tgt.x, tgt.y, last[2]))
        # in Lagenabschnitte teilen
        runs = []; cur = [poly[0]]
        for a, b in zip(poly, poly[1:]):
            if a[2] != b[2]:
                runs.append(cur); self.add_via(a[0], a[1], net); cur = [b]
            else: cur.append(b)
        runs.append(cur)
        for run in runs:
            # kollineare Punkte zusammenfassen
            out = [run[0]]
            for p in run[1:]:
                if len(out) >= 2:
                    a, b = out[-2], out[-1]
                    if abs((b[0] - a[0]) * (p[1] - b[1]) - (b[1] - a[1]) * (p[0] - b[0])) < 1e-6 and \
                       (b[0] - a[0]) * (p[0] - b[0]) + (b[1] - a[1]) * (p[1] - b[1]) > 0:
                        out[-1] = p; continue
                out.append(p)
            for a, b in zip(out, out[1:]):
                if math.hypot(b[0] - a[0], b[1] - a[1]) < 1e-6: continue
                self.items.append(Item("seg", net, [a[2]], x1=a[0], y1=a[1], x2=b[0], y2=b[1], w=hw * 2))
        for c in pts:
            tree[(c[0], c[1], c[2])] = None
        # Via-Zellen in beiden Lagen als Baumknoten
    def add_via(self, x, y, net):
        self.items.append(Item("disk", net, [0, 1], x=x, y=y, r=VIA_D / 2, via=True, ref="VIA", pad=""))

    def gnd_stubs(self, net="GND"):
        hw = DEF_W / 2
        nv = np.zeros((NY, NX), bool)
        for p in self.pads: paint_item([nv, nv], p, VIA_D / 2 + 0.15)
        for p in [p for p in self.pads if p.net == net and p.layers == [0]]:
            tm, via_bad = self.masks_for(net, hw)
            via_bad = via_bad | nv
            # Stub bis zu einer Via-Position
            tree = {(cell(p.x), cell(p.y), 0): (p.x, p.y)}
            res = self.astar_via(tree, p, tm, via_bad)
            if res is None:
                self.log.append(f"FEHLER: GND-Stub {p.ref}.{p.pad}"); continue
            path = res
            last = path[-1]
            class T: pass
            t = T(); t.x, t.y = last[0] * RES, last[1] * RES
            self.commit(path, tree, net, hw, t)
            self.add_via(last[0] * RES, last[1] * RES, net)
            # neue Kupferteile blockieren Masken nicht fuer GND selbst; weitere Netze werden spaeter nicht mehr geroutet

    def astar_via(self, tree, p, tm, via_bad, turn=12):
        g = {}; par = {}; pq = []
        for (ix, iy, l) in tree:
            st = (ix, iy, l, 8); g[st] = 0; heapq.heappush(pq, (0, 0, st))
        while pq:
            f, gc, st = heapq.heappop(pq)
            if g.get(st, 1e18) < gc: continue
            ix, iy, l, d = st
            if l == 0 and not via_bad[iy, ix] and not tm[1][iy, ix]:
                path = []; s = st
                while s in par: path.append(s); s = par[s]
                path.append(s); path.reverse(); return path
            for k, (dx, dy, c) in enumerate(DIRS):
                nx, ny = ix + dx, iy + dy
                if not (0 <= nx < NX and 0 <= ny < NY) or tm[0][ny, nx]: continue
                if dx and dy and (tm[0][iy, nx] or tm[0][ny, ix]): continue
                nc = gc + c + (turn if (d != 8 and d != k) else 0)
                ns = (nx, ny, 0, k)
                if nc < g.get(ns, 1e18):
                    g[ns] = nc; par[ns] = st; heapq.heappush(pq, (nc, nc, ns))
        return None

    def stitch(self, pitch=4.0):
        tm, via_bad = self.masks_for("GND", 0.0)
        nv = np.zeros((NY, NX), bool)
        for p in self.pads: paint_item([nv, nv], p, VIA_D / 2 + 0.15)
        via_bad = via_bad | nv
        n = 0
        y = 2.0
        while y < H - 1.5:
            x = 2.0
            while x < W - 1.5:
                ix, iy = cell(x), cell(y)
                # kleine Suche nach freiem Platz
                found = None
                for r in range(0, 12):
                    for dy in range(-r, r + 1):
                        for dx in range(-r, r + 1):
                            if max(abs(dx), abs(dy)) != r: continue
                            jx, jy = ix + dx, iy + dy
                            if 0 <= jx < NX and 0 <= jy < NY and not via_bad[jy, jx] and not tm[0][jy, jx] and not tm[1][jy, jx]:
                                found = (jx, jy); break
                        if found: break
                    if found: break
                if found:
                    vx, vy = found[0] * RES, found[1] * RES
                    self.add_via(vx, vy, "GND"); n += 1
                    paint_disk(via_bad, vx, vy, VIA_D + CLR + 0.2)
                x += pitch
            y += pitch
        return n

ORDER = ["OSC_OUT", "RCLK", "FM_ANT", "FM_MID", "FMI", "AM_ANT", "AMI", "RFGND", "SDA", "SCL", "RST", "SENB",
         "LOUT", "ROUT", "AUDIO_L", "AUDIO_R", "INT", "3V3"]

def run():
    r = Router()
    for n in ORDER:
        r.route_net(n)
    r.gnd_stubs()
    nst = r.stitch()
    r.log.append(f"Stitching-Vias: {nst}")
    return r

if __name__ == "__main__":
    r = run()
    print("\n".join(r.log) or "alle Netze geroutet")
    print(len([i for i in r.items if i.kind == 'seg']), "Segmente,", len([i for i in r.items if getattr(i, 'via', False)]), "Vias")
