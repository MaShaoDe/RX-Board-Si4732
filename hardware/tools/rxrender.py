"""Grobe Vorschau der Platine (Vorderseite) als PNG. Kein KiCad-Bild."""
import re, os, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
from rxroute import *
from rxwrite import build_pcb

def main(path):
    r = run(); pcb = build_pcb(r)
    fig, ax = plt.subplots(figsize=(18, 12.5))
    ax.set_xlim(-1, W + 1); ax.set_ylim(H + 1, -1); ax.set_aspect("equal"); ax.set_facecolor("#0b2a14")
    ax.add_patch(Rectangle((0, 0), W, H, fill=False, ec="#e0e000", lw=2))
    col = {0: "#c83232", 1: "#3a63c8"}; S = 17 * 72 / (W + 2)
    for pas in (1, 0):
        for it in r.items:
            if pas not in it.layers or it.kind == "hole": continue
            a = 0.5 if pas == 1 else 0.9
            if it.kind == "seg": ax.plot([it.x1, it.x2], [it.y1, it.y2], color=col[pas], lw=it.w * S, alpha=a, solid_capstyle="round")
            elif it.kind == "rect": ax.add_patch(Rectangle((it.x0, it.y0), it.x1 - it.x0, it.y1 - it.y0, color=col[pas], alpha=a))
            else:
                v = getattr(it, "via", False)
                ax.add_patch(Circle((it.x, it.y), it.r, color="#dddddd" if v else col[pas], alpha=a))
                if v: ax.add_patch(Circle((it.x, it.y), VIA_DRILL / 2, color="#0b2a14"))
    for it in r.items:
        if it.kind == "hole": ax.add_patch(Circle((it.x, it.y), 1.35, color="black"))
    for m in re.finditer(r'\(footprint "[^"]+" \(layer "F.Cu"\) \(uuid "[^"]+"\) \(at ([\d.-]+) ([\d.-]+)\).*?\(property "Reference" "([^"]+)" \(at ([\d.-]+) ([\d.-]+) 0\) \(layer "F.SilkS"\)', pcb, re.S):
        x, y, ref, dx, dy = m.groups(); ax.text(float(x) + float(dx), float(y) + float(dy), ref, color="white", fontsize=9, ha="center", va="center")
    for m in re.finditer(r'\(gr_text "([^"]+)" \(at ([\d.-]+) ([\d.-]+)\) \(layer "F.SilkS"\).*?\(justify (\w+)\)', pcb, re.S):
        t, x, y, j = m.groups(); ax.text(float(x), float(y), t, color="white", fontsize=9, ha=j, va="center")
    plt.savefig(path, dpi=70, bbox_inches="tight", facecolor="#0b2a14")
if __name__ == "__main__":
    main(os.path.join(os.path.dirname(__file__), "..", "preview", "layout-vorschau.png"))
