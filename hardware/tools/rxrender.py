import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
from rxroute import *
def render(r, path, texts=()):
    fig, ax = plt.subplots(figsize=(17, 11.6))
    ax.add_patch(Rectangle((0, 0), W, H, fill=False, ec="#c8c800", lw=2))
    ax.set_xlim(-1, W + 1); ax.set_ylim(H + 1, -1); ax.set_aspect("equal")
    ax.set_facecolor("#102010")
    col = {0: "#d03030", 1: "#3060d0"}
    for pas in (1, 0):
        for it in r.items:
            if pas not in it.layers: continue
            c = col[pas]; a = 0.55 if pas == 1 else 0.85
            if it.kind == "seg":
                ax.plot([it.x1, it.x2], [it.y1, it.y2], color=c, lw=it.w * 31, alpha=a, solid_capstyle="round")
            elif it.kind == "rect":
                ax.add_patch(Rectangle((it.x0, it.y0), it.x1 - it.x0, it.y1 - it.y0, color=c, alpha=a))
            elif it.kind == "disk":
                ax.add_patch(Circle((it.x, it.y), it.r, color=c if not getattr(it, "via", False) else "#e0e0e0", alpha=a))
                if getattr(it, "via", False): ax.add_patch(Circle((it.x, it.y), VIA_DRILL / 2, color="black"))
            elif it.kind == "hole":
                ax.add_patch(Circle((it.x, it.y), 1.35, color="black"))
    for ref, kind, val, fpk, x, y, nets, d in PARTS:
        if kind in ("hole",): continue
        ax.text(x, y - 1.6 if fpk not in ("soic",) else y - 6.2, ref, color="white", fontsize=7, ha="center")
    for (x, y, t, s) in texts:
        ax.text(x, y, t, color="#f0f0f0", fontsize=s * 5, ha="left", va="center")
    plt.savefig(path, dpi=80, bbox_inches="tight", facecolor="#102010"); plt.close()
if __name__ == "__main__":
    r = run(); render(r, "/tmp/rx_layout.png"); print(r.log)
