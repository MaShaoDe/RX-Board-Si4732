"""Schreibt KiCad-8/9-Dateien (Schaltplan, Platine, Projekt) und die Stueckliste fuer das RX-Board Rev A."""
import uuid, os, json, csv, math
from rxroute import *
from rxmodel import _LIB
from rxcheck import check

NS = uuid.UUID("6f1c2a4e-0b9d-4c55-9a3e-5a2d7a1e4b10")
def U(s): return str(uuid.uuid5(NS, s))
ROOT = U("root-sheet")
OUT = os.path.join(os.path.dirname(__file__), "..", "kicad")
NAME = "RX-Board-Si4732"
COPY = "Copyright 2026 FerienBSD aka Marcel Sauder"
NETIDX = {n: i + 1 for i, n in enumerate(NETS)}
def f(v): return ("%.4f" % v).rstrip("0").rstrip(".")
def esc(s): return s.replace('"', "'")

# ---------------------------------------------------------------- PCB
def silk_candidates():
    return []

def text_bbox(x, y, t, size, just):
    w = 0.95 * size * len(t); h = size * 1.2
    if just == "left": return (x, y - h / 2, x + w, y + h / 2)
    if just == "right": return (x - w, y - h / 2, x, y + h / 2)
    return (x - w / 2, y - h / 2, x + w / 2, y + h / 2)

def build_pcb(r):
    L = []; a = L.append
    a('(kicad_pcb (version 20240108) (generator "pcbnew") (generator_version "8.0")')
    a(' (general (thickness 1.6) (legacy_teardrops no))')
    a(' (paper "A4")')
    a(' (title_block (title "RX-Board Si4732") (date "2026-11-15") (rev "A") (company "FerienBSD aka Marcel Sauder") (comment 1 "CERN-OHL-P-2.0"))')
    a(' (layers (0 "F.Cu" signal) (31 "B.Cu" signal) (32 "B.Adhes" user "B.Adhesive") (33 "F.Adhes" user "F.Adhesive") (34 "B.Paste" user) (35 "F.Paste" user) (36 "B.SilkS" user "B.Silkscreen") (37 "F.SilkS" user "F.Silkscreen") (38 "B.Mask" user) (39 "F.Mask" user) (40 "Dwgs.User" user "User.Drawings") (41 "Cmts.User" user "User.Comments") (42 "Eco1.User" user "User.Eco1") (43 "Eco2.User" user "User.Eco2") (44 "Edge.Cuts" user) (45 "Margin" user) (46 "B.CrtYd" user "B.Courtyard") (47 "F.CrtYd" user "F.Courtyard") (48 "B.Fab" user "B.Fabrication") (49 "F.Fab" user "F.Fabrication"))')
    a(' (setup (pad_to_mask_clearance 0.05) (allow_soldermask_bridges_in_footprints no) (pcbplotparams (layerselection 0x00010fc_ffffffff) (plot_on_all_layers_selection 0x0000000_00000000) (disableapertmacros no) (usegerberextensions no) (usegerberattributes yes) (usegerberadvancedattributes yes) (creategerberjobfile yes) (dashed_line_dash_ratio 12.0) (dashed_line_gap_ratio 3.0) (svgprecision 4) (plotframeref no) (viasonmask no) (mode 1) (useauxorigin no) (hpglpennumber 1) (hpglpenspeed 20) (hpglpendiameter 15.0) (pdf_front_fp_property_popups yes) (pdf_back_fp_property_popups yes) (dxfpolygonmode yes) (dxfimperialunits yes) (dxfusepcbnewfont yes) (psnegative no) (psa4output no) (plotreference yes) (plotvalue yes) (plotfptext yes) (plotinvisibletext no) (sketchpadsonfab no) (subtractmaskfromsilk no) (outputformat 1) (mirror no) (drillshape 0) (scaleselection 1) (outputdirectory "gerber/")))')
    a(' (net 0 "")')
    for n in NETS: a(' (net %d "%s")' % (NETIDX[n], n))
    # Beschriftungs-Platzierung: Referenz neben dem Bauteil ohne Ueberdeckung von Pads und Silkscreen
    pads_box = []
    for p in r.pads:
        if p.kind == "rect": pads_box.append((p.x0 - 0.15, p.y0 - 0.15, p.x1 + 0.15, p.y1 + 0.15))
        else: pads_box.append((p.x - p.r - 0.15, p.y - p.r - 0.15, p.x + p.r + 0.15, p.y + p.r + 0.15))
    for ref, kind, val, fpk, x, y, nets, d in PARTS:
        for (a0, b0, a1, b1) in silk_boxes(fpk): pads_box.append((x + a0, y + b0, x + a1, y + b1))
    used = []
    FRONT = [("RX-Board Si4732", 6.0, 2.0), ("Rev A 2026", 6.0, 3.6), ("SN:_____", 6.0, 5.2)]
    for t, x, y in FRONT: used.append(text_bbox(x, y, t, 1.0, "left"))
    for i, t in enumerate(["L", "R", "GND", "3V3", "SDA", "SCL", "RST", "INT", "GND"]): used.append(text_bbox(38.6, J1Y0 + 2.54 * i, t, 1.0, "right"))
    used.append(text_bbox(4.6, 14.2, "FM", 1.0, "left")); used.append(text_bbox(4.6, 20.8, "AM", 1.0, "left"))
    def free(bb):
        if bb[0] < 0.6 or bb[1] < 0.6 or bb[2] > W - 0.6 or bb[3] > H - 0.6: return False
        for q in pads_box + used:
            if not (bb[2] < q[0] or bb[0] > q[2] or bb[3] < q[1] or bb[1] > q[3]): return False
        return True
    ref_pos = {}
    for ref, kind, val, fpk, x, y, nets, d in PARTS:
        if kind == "hole": continue
        cy_ = courtyard(fpk)
        bx = [s for s in cy_ if s[0] == "rect"]
        if bx: ex = max(max(abs(s[1]), abs(s[3])) for s in bx); eyu = -min(s[2] for s in bx); eyd = max(s[4] for s in bx); exl = -min(s[1] for s in bx); exr = max(s[3] for s in bx)
        else: ex = exl = exr = max(s[3] for s in cy_); eyu = eyd = ex
        size = 1.0; tw = 0.95 * size * len(ref)
        cands = [(0, -(eyu + 0.7)), (0, eyd + 0.7), (-(exl + tw / 2 + 0.2), 0), (exr + tw / 2 + 0.2, 0),
                 (0, -(eyu + 1.8)), (0, eyd + 1.8), (-(exl + tw / 2 + 0.2), -1.4), (exr + tw / 2 + 0.2, 1.4),
                 (-(exl + tw / 2 + 0.2), 1.4), (exr + tw / 2 + 0.2, -1.4)]
        chosen = None
        for dx, dy in cands:
            bb = text_bbox(x + dx, y + dy, ref, size, "center")
            if free(bb): chosen = (dx, dy, bb); break
        if chosen is None:
            r.log.append(f"Hinweis: kein freier Platz fuer {ref}"); chosen = (cands[0][0], cands[0][1], text_bbox(x + cands[0][0], y + cands[0][1], ref, size, "center"))
        used.append(chosen[2]); ref_pos[ref] = (chosen[0], chosen[1])
    LIBN = {}
    for ref, kind, val, fpk, x, y, nets, d in PARTS:
        name, padfn, attr = FP[fpk]
        lib = _LIB[name]
        sym_uuid = U("sym-" + ref)
        a(' (footprint "%s" (layer "F.Cu") (uuid "%s") (at %s %s)' % (name, U("fp-" + ref), f(x), f(y)))
        a('  (descr "%s")' % esc(lib["descr"]))
        if lib["tags"]: a('  (tags "%s")' % esc(lib["tags"]))
        if kind != "hole":
            rx, ry = ref_pos[ref]
            a('  (property "Reference" "%s" (at %s %s 0) (layer "F.SilkS") (uuid "%s") (effects (font (size 1 1) (thickness 0.15))))' % (ref, f(rx), f(ry), U("ref-" + ref)))
        else:
            a('  (property "Reference" "%s" (at 0 -3 0) (layer "F.Fab") (hide yes) (uuid "%s") (effects (font (size 1 1) (thickness 0.15))))' % (ref, U("ref-" + ref)))
        a('  (property "Value" "%s" (at 0 2 0) (layer "F.Fab") (hide yes) (uuid "%s") (effects (font (size 1 1) (thickness 0.15))))' % (esc(val), U("val-" + ref)))
        a('  (property "Footprint" "%s" (at 0 0 0) (layer "F.Fab") (hide yes) (uuid "%s") (effects (font (size 1.27 1.27))))' % (name, U("fpp-" + ref)))
        a('  (path "/%s/%s")' % (ROOT, sym_uuid))
        a('  (attr %s)' % attr)
        for gi, g in enumerate(lib["gfx"]):
            gu = U("g-%s-%d" % (ref, gi)); k = g["kind"]
            stroke = '(stroke (width %s) (type %s))' % (f(g.get("width", 0.12)), g.get("stype", "solid"))
            fill = "solid" if g.get("fill") == "yes" else "none"
            if k == "fp_line": a('  (fp_line (start %s %s) (end %s %s) %s (layer "%s") (uuid "%s"))' % (f(g["start"][0]), f(g["start"][1]), f(g["end"][0]), f(g["end"][1]), stroke, g["layer"], gu))
            elif k == "fp_rect": a('  (fp_rect (start %s %s) (end %s %s) %s (fill %s) (layer "%s") (uuid "%s"))' % (f(g["start"][0]), f(g["start"][1]), f(g["end"][0]), f(g["end"][1]), stroke, fill, g["layer"], gu))
            elif k == "fp_circle": a('  (fp_circle (center %s %s) (end %s %s) %s (fill %s) (layer "%s") (uuid "%s"))' % (f(g["center"][0]), f(g["center"][1]), f(g["end"][0]), f(g["end"][1]), stroke, fill, g["layer"], gu))
            elif k == "fp_poly": a('  (fp_poly (pts %s) %s (fill %s) (layer "%s") (uuid "%s"))' % (" ".join("(xy %s %s)" % (f(p[0]), f(p[1])) for p in g["pts"]), stroke, fill, g["layer"], gu))
            elif k == "fp_text": a('  (fp_text %s "%s" (at %s %s 0) (layer "%s") (uuid "%s") (effects (font (size %s %s) (thickness %s))))' % (g["ttype"], g["text"], f(g["at"][0]), f(g["at"][1]), g["layer"], gu, f(g["size"][0]), f(g["size"][1]), f(g["thickness"])))
        for (num, typ, shape, px, py, w, h, drill, rr) in padfn():
            net = nets.get(num)
            nt = (' (net %d "%s")' % (NETIDX[net], net)) if net else ""
            pu = U("pad-%s-%s" % (ref, num))
            pl = [p for p in lib["pads"] if p["num"] == num][0]
            lay = " ".join('"%s"' % x for x in pl["layers"])
            if typ == "smd":
                extra = (" (roundrect_rratio %s)" % f(rr)) if rr is not None else ""
                a('  (pad "%s" smd %s (at %s %s) (size %s %s) (layers %s)%s%s (uuid "%s"))' % (num, shape, f(px), f(py), f(w), f(h), lay, extra, nt, pu))
            elif typ == "thru":
                a('  (pad "%s" thru_hole %s (at %s %s) (size %s %s) (drill %s) (layers %s)%s (uuid "%s"))' % (num, shape, f(px), f(py), f(w), f(h), f(drill), lay, nt, pu))
            else:
                a('  (pad "%s" np_thru_hole circle (at %s %s) (size %s %s) (drill %s) (layers %s) (uuid "%s"))' % (num, f(px), f(py), f(w), f(h), f(drill), lay, pu))
        if lib["model"]:
            a('  (model "%s" (offset (xyz 0 0 0)) (scale (xyz 1 1 1)) (rotate (xyz 0 0 0)))' % lib["model"])
        a(' )')
    # Leiterbahnen und Vias
    k = 0
    for it in r.items:
        k += 1
        if it.kind == "seg":
            a(' (segment (start %s %s) (end %s %s) (width %s) (layer "%s") (net %d) (uuid "%s"))' %
              (f(it.x1), f(it.y1), f(it.x2), f(it.y2), f(it.w), "F.Cu" if it.layers[0] == 0 else "B.Cu", NETIDX[it.net], U("seg%d" % k)))
        elif getattr(it, "via", False):
            a(' (via (at %s %s) (size %s) (drill %s) (layers "F.Cu" "B.Cu") (net %d) (uuid "%s"))' % (f(it.x), f(it.y), f(VIA_D), f(VIA_DRILL), NETIDX[it.net], U("via%d" % k)))
    # Kontur
    a(' (gr_rect (start 0 0) (end %s %s) (stroke (width 0.1) (type default)) (fill none) (layer "Edge.Cuts") (uuid "%s"))' % (f(W), f(H), U("edge")))
    # Beschriftung vorne
    front = [(t, x, y, 1.0) for t, x, y in FRONT]
    for t, x, y, s in front:
        a(' (gr_text "%s" (at %s %s) (layer "F.SilkS") (uuid "%s") (effects (font (size %s %s) (thickness 0.15)) (justify left)))' % (t, f(x), f(y), U("ft" + t), f(s), f(s)))
    labels = [("L", 3), ("R", 3), ("GND", 3), ("3V3", 3), ("SDA", 3), ("SCL", 3), ("RST", 3), ("INT", 3), ("GND", 3)]
    for i, (t, _) in enumerate(labels):
        y = J1Y0 + 2.54 * i
        a(' (gr_text "%s" (at 38.6 %s) (layer "F.SilkS") (uuid "%s") (effects (font (size 1 1) (thickness 0.15)) (justify right)))' % (t, f(y), U("jl%d" % i)))
    a(' (gr_text "FM" (at 4.6 14.2) (layer "F.SilkS") (uuid "%s") (effects (font (size 1 1) (thickness 0.15)) (justify left)))' % U("fm"))
    a(' (gr_text "AM" (at 4.6 20.8) (layer "F.SilkS") (uuid "%s") (effects (font (size 1 1) (thickness 0.15)) (justify left)))' % U("am"))
    # Beschriftung hinten (gespiegelt)
    # gespiegelter Text wachsen nach links vom Ankerpunkt: Anker rechts setzen
    back = [("RX-Board Si4732 Rev A", 36.0, 8.0), ("Copyright 2026", 36.0, 9.6), ("FerienBSD aka Marcel Sauder", 36.0, 11.2),
            ("github.com/MaShaoDe/", 36.0, 12.8), ("RX-Board-Si4732", 36.0, 14.4), ("CERN-OHL-P-2.0", 36.0, 16.0), ("SN:_____", 36.0, 17.6)]
    for i, (t, x, y) in enumerate(back):
        a(' (gr_text "%s" (at %s %s) (layer "B.SilkS") (uuid "%s") (effects (font (size 1 1) (thickness 0.15)) (justify left mirror)))' % (t, f(x), f(y), U("bt%d" % i)))
    # Masse-Zonen
    for layer in ("F.Cu", "B.Cu"):
        a(' (zone (net %d) (net_name "GND") (layer "%s") (uuid "%s") (hatch edge 0.5) (connect_pads (clearance 0.3)) (min_thickness 0.25) (filled_areas_thickness no) (fill (thermal_gap 0.3) (thermal_bridge_width 0.4)) (polygon (pts (xy 0.3 0.3) (xy %s 0.3) (xy %s %s) (xy 0.3 %s))))' %
          (NETIDX["GND"], layer, U("zone" + layer), f(W - 0.3), f(W - 0.3), f(H - 0.3), f(H - 0.3)))
    a(')')
    return "\n".join(L) + "\n"

# ---------------------------------------------------------------- Schaltplan
TXT = '(effects (font (size 1.27 1.27)))'
HID = '(effects (font (size 1.27 1.27)) (hide yes))'
def props(ref, val, fp, extra=""):
    return ('(property "Reference" "%s" (at 0 -2.54 0) %s)(property "Value" "%s" (at 0 2.54 0) %s)'
            '(property "Footprint" "%s" (at 0 0 0) %s)(property "Datasheet" "~" (at 0 0 0) %s)') % (ref, TXT, val, TXT, fp, HID, HID)

def libdefs():
    def pin(t, x, y, ang, name, num, ln=1.27):
        return '(pin %s line (at %s %s %d) (length %s) (name "%s" %s) (number "%s" %s))' % (t, f(x), f(y), ang, f(ln), name, TXT, num, TXT)
    S = ['(symbol "RXBoard:R" (pin_numbers hide) (pin_names (offset 0)) (exclude_from_sim no) (in_bom yes) (on_board yes) ' + props("R", "R", "") +
         '(symbol "R_0_1" (rectangle (start -1.016 -2.54) (end 1.016 2.54) (stroke (width 0.254) (type default)) (fill (type none))))' +
         '(symbol "R_1_1" ' + pin("passive", 0, 3.81, 270, "~", "1") + pin("passive", 0, -3.81, 90, "~", "2") + '))']
    S.append('(symbol "RXBoard:C" (pin_numbers hide) (pin_names (offset 0.254)) (exclude_from_sim no) (in_bom yes) (on_board yes) ' + props("C", "C", "") +
         '(symbol "C_0_1" (polyline (pts (xy -2.032 -0.762) (xy 2.032 -0.762)) (stroke (width 0.508) (type default)) (fill (type none))) (polyline (pts (xy -2.032 0.762) (xy 2.032 0.762)) (stroke (width 0.508) (type default)) (fill (type none))))' +
         '(symbol "C_1_1" ' + pin("passive", 0, 3.81, 270, "~", "1", 3.048) + pin("passive", 0, -3.81, 90, "~", "2", 3.048) + '))')
    S.append('(symbol "RXBoard:L" (pin_numbers hide) (pin_names (offset 0)) (exclude_from_sim no) (in_bom yes) (on_board yes) ' + props("L", "L", "") +
         '(symbol "L_0_1" (rectangle (start -1.016 -2.54) (end 1.016 2.54) (stroke (width 0.254) (type default)) (fill (type background))))' +
         '(symbol "L_1_1" ' + pin("passive", 0, 3.81, 270, "~", "1") + pin("passive", 0, -3.81, 90, "~", "2") + '))')
    S.append('(symbol "RXBoard:Crystal" (pin_numbers hide) (pin_names (offset 1.016) hide) (exclude_from_sim no) (in_bom yes) (on_board yes) ' + props("X", "Crystal", "") +
         '(symbol "Crystal_0_1" (rectangle (start -1.016 -2.54) (end 1.016 2.54) (stroke (width 0.254) (type default)) (fill (type none))) (polyline (pts (xy -2.032 -1.778) (xy -2.032 1.778)) (stroke (width 0.508) (type default)) (fill (type none))) (polyline (pts (xy 2.032 -1.778) (xy 2.032 1.778)) (stroke (width 0.508) (type default)) (fill (type none))))' +
         '(symbol "Crystal_1_1" ' + pin("passive", 0, 3.81, 270, "1", "1") + pin("passive", 0, -3.81, 90, "2", "2") + '))')
    S.append('(symbol "RXBoard:BAV99" (pin_names (offset 0)) (exclude_from_sim no) (in_bom yes) (on_board yes) ' + props("D", "BAV99", "") +
         '(symbol "BAV99_0_1" (rectangle (start -5.08 5.08) (end 5.08 -5.08) (stroke (width 0.254) (type default)) (fill (type background))))' +
         '(symbol "BAV99_1_1" ' + pin("passive", -7.62, 2.54, 0, "A1", "1", 2.54) + pin("passive", -7.62, -2.54, 0, "K2", "2", 2.54) + pin("passive", 7.62, 0, 180, "K1/A2", "3", 2.54) + '))')
    S.append('(symbol "RXBoard:Conn_01x02" (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes) ' + props("J", "Conn_01x02", "") +
         '(symbol "Conn_01x02_0_1" (rectangle (start -2.54 3.81) (end 2.54 -3.81) (stroke (width 0.254) (type default)) (fill (type background))))' +
         '(symbol "Conn_01x02_1_1" ' + pin("passive", -5.08, 1.27, 0, "Pin_1", "1", 2.54) + pin("passive", -5.08, -1.27, 0, "Pin_2", "2", 2.54) + '))')
    pins9 = "".join(pin("passive", -5.08, 10.16 - 2.54 * i, 0, "Pin_%d" % (i + 1), str(i + 1), 2.54) for i in range(9))
    S.append('(symbol "RXBoard:Conn_01x09" (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes) ' + props("J", "Conn_01x09", "") +
         '(symbol "Conn_01x09_0_1" (rectangle (start -2.54 11.43) (end 2.54 -11.43) (stroke (width 0.254) (type default)) (fill (type background))))' +
         '(symbol "Conn_01x09_1_1" ' + pins9 + '))')
    S.append('(symbol "RXBoard:TestPoint" (pin_numbers hide) (pin_names (offset 0.762) hide) (exclude_from_sim no) (in_bom yes) (on_board yes) ' + props("TP", "TestPoint", "") +
         '(symbol "TestPoint_0_1" (circle (center 0 1.27) (radius 0.762) (stroke (width 0) (type default)) (fill (type none))))' +
         '(symbol "TestPoint_1_1" ' + pin("passive", 0, 0, 90, "1", "1", 0.508) + '))')
    S.append('(symbol "RXBoard:MountingHole" (pin_names (offset 1.016)) (exclude_from_sim yes) (in_bom no) (on_board yes) ' + props("H", "MountingHole", "") +
         '(symbol "MountingHole_0_1" (circle (center 0 0) (radius 1.27) (stroke (width 0.254) (type default)) (fill (type none)))))')
    # Si4732: Pins links 1..8, rechts 9..16 (unten nach oben)
    names = {1: "LOUT/DFS", 2: "GPO3/DCLK", 3: "GPO2/INTB", 4: "GPO1", 5: "NC", 6: "FMI", 7: "RFGND", 8: "AMI", 9: "RST", 10: "SENB",
             11: "SCLK", 12: "SDIO", 13: "RCLK", 14: "VDD", 15: "GND", 16: "ROUT/DOUT"}
    ps = ""
    for i in range(1, 9): ps += pin("passive", -15.24, 8.89 - 2.54 * (i - 1), 0, names[i], str(i), 3.81)
    for j in range(9, 17): ps += pin("passive", 15.24, -8.89 + 2.54 * (j - 9), 180, names[j], str(j), 3.81)
    S.append('(symbol "RXBoard:Si4732-A10-GS" (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes) ' + props("U", "Si4732-A10-GS", "") +
         '(symbol "Si4732-A10-GS_0_1" (rectangle (start -11.43 11.43) (end 11.43 -11.43) (stroke (width 0.254) (type default)) (fill (type background))))' +
         '(symbol "Si4732-A10-GS_1_1" ' + ps + '))')
    return "\n".join(S)

# Pin-Offsets (Welt, y nach unten) je Symbol
def pin_offsets(sym):
    if sym == "C" or sym == "R" or sym == "L" or sym == "Crystal":
        return {"1": (0, -3.81, 90), "2": (0, 3.81, 270)}
    if sym == "BAV99": return {"1": (-7.62, -2.54, 180), "2": (-7.62, 2.54, 180), "3": (7.62, 0, 0)}
    if sym == "Conn_01x02": return {"1": (-5.08, -1.27, 180), "2": (-5.08, 1.27, 180)}
    if sym == "Conn_01x09": return {str(i + 1): (-5.08, -10.16 + 2.54 * i, 180) for i in range(9)}
    if sym == "TestPoint": return {"1": (0, 0, 90)}
    if sym == "MountingHole": return {}
    if sym == "Si4732-A10-GS":
        d = {}
        for i in range(1, 9): d[str(i)] = (-15.24, -8.89 + 2.54 * (i - 1), 180)
        for j in range(9, 17): d[str(j)] = (15.24, 8.89 - 2.54 * (j - 9), 0)
        return d

SYM = {"ic": "Si4732-A10-GS", "xtal": "Crystal", "c": "C", "r": "R", "l": "L", "d": "BAV99", "conn": None, "tp": "TestPoint", "hole": "MountingHole"}

def build_sch():
    L = []; a = L.append
    a('(kicad_sch (version 20231120) (generator "eeschema") (generator_version "8.0") (uuid "%s") (paper "A3")' % ROOT)
    a(' (title_block (title "RX-Board Si4732 (Rev A)") (date "2026-11-15") (rev "A") (company "FerienBSD aka Marcel Sauder") (comment 1 "%s") (comment 2 "CERN-OHL-P-2.0") (comment 3 "Netzlisten-Stil: Verbindungen ueber gleichnamige Netzbezeichner"))' % COPY)
    a(' (lib_symbols')
    a(libdefs())
    a(' )')
    # Platzierung
    pos = {}
    pos["U1"] = (254.0, 101.6)
    grid_x = [38.1 + 33.02 * k for k in range(8)]
    passives = [p for p in PARTS if p[1] in ("r", "c", "l", "xtal")]
    others = [p for p in PARTS if p[1] in ("d", "conn", "tp", "hole")]
    for i, p in enumerate(passives): pos[p[0]] = (grid_x[i % 4] + 0, 60.96 + 30.48 * (i // 4))
    for i, p in enumerate(others):
        row, col = divmod(i, 6)
        pos[p[0]] = (38.1 + 40.64 * col, 180.34 + 33.02 * row)
    # Passive auf linke Haelfte (4 Spalten), IC rechts
    labels = []; nocon = []
    for ref, kind, val, fpk, x, y, nets, d in PARTS:
        sym = SYM[kind] if kind != "conn" else ("Conn_01x09" if fpk == "h9" else "Conn_01x02")
        px, py = pos[ref]
        fp = FP[fpk][0]
        a(' (symbol (lib_id "RXBoard:%s") (at %s %s 0) (unit 1) (exclude_from_sim no) (in_bom %s) (on_board yes) (dnp no) (uuid "%s")' %
          (sym, f(px), f(py), "no" if kind == "hole" else "yes", U("sym-" + ref)))
        a('  (property "Reference" "%s" (at %s %s 0) %s)' % (ref, f(px + (17.78 if kind == "ic" else 3.81)), f(py - 2.54), TXT.replace("))", ") (justify left))") if False else '(effects (font (size 1.27 1.27)) (justify left))'))
        a('  (property "Value" "%s" (at %s %s 0) %s)' % (esc(val), f(px + (17.78 if kind == "ic" else 3.81)), f(py + 2.54), '(effects (font (size 1.27 1.27)) (justify left))'))
        a('  (property "Footprint" "%s" (at %s %s 0) %s)' % (fp, f(px), f(py), HID))
        a('  (property "Datasheet" "~" (at %s %s 0) %s)' % (f(px), f(py), HID))
        a('  (property "Beschreibung" "%s" (at %s %s 0) %s)' % (esc(d), f(px), f(py), HID))
        offs = pin_offsets(sym)
        for num in offs: a('  (pin "%s" (uuid "%s"))' % (num, U("pin-%s-%s" % (ref, num))))
        a('  (instances (project "%s" (path "/%s" (reference "%s") (unit 1))))' % (NAME, ROOT, ref))
        a(' )')
        for num, (ox, oy, ang) in offs.items():
            net = nets.get(num)
            wx, wy = px + ox, py + oy
            if net: labels.append((net, wx, wy, ang))
            elif ref == "U1": nocon.append((wx, wy))
    k = 0
    for net, x, y, ang in labels:
        k += 1
        just = "right bottom" if ang == 180 else "left bottom"
        a(' (label "%s" (at %s %s %d) (fields_autoplaced yes) (effects (font (size 1.27 1.27)) (justify %s)) (uuid "%s"))' % (net, f(x), f(y), ang, just, U("lbl%d" % k)))
    for i, (x, y) in enumerate(nocon):
        a(' (no_connect (at %s %s) (uuid "%s"))' % (f(x), f(y), U("nc%d" % i)))
    # Hinweistexte
    notes = ["RX-Board Si4732, Rev A (UKW, MW, LW). Kurzwelle folgt in Rev B.",
             "Pinbelegung Si4732-A10-GS geprueft (Datenblatt-Kurzfassung, Mikroe-Schaltplan). Werte: AN383, AN332, Mikroe AM/FM 2 Click.",
             "SENB nach GND ueber R4: I2C-Adresse 0x11. GPO1 und GPO2 bleiben beim Reset unbeschaltet: Bus-Modus I2C.",
             "Quarz 32.768 kHz zwischen GPO3/DCLK (Pin 2) und RCLK (Pin 13). Start: POWER_UP mit XOSCEN=1, OPMODE=0x05, dann 500 ms warten.",
             "RFGND nur ueber R7 mit GND verbunden. Ferritstab an J3 (180 bis 450 uH). Teleskopantenne FM an J2.",
             COPY + ", CERN-OHL-P-2.0"]
    for i, t in enumerate(notes):
        a(' (text "%s" (exclude_from_sim no) (at 25.4 %s 0) (effects (font (size 1.905 1.905)) (justify left bottom)) (uuid "%s"))' % (esc(t), f(20.32 + 6.35 * i), U("note%d" % i)))
    a(' (sheet_instances (path "/" (page "1")))')
    a(')')
    return "\n".join(L) + "\n"

def build_pro():
    return json.dumps({
        "board": {"design_settings": {"rules": {"min_clearance": 0.2, "min_track_width": 0.2, "min_via_diameter": 0.6,
                  "min_through_hole_diameter": 0.3, "min_copper_edge_clearance": 0.3, "min_hole_to_hole": 0.5},
                  "defaults": {"copper_line_width": 0.25, "board_outline_line_width": 0.1, "silk_line_width": 0.15,
                               "silk_text_size_h": 1.0, "silk_text_size_v": 1.0, "silk_text_thickness": 0.15}}},
        "meta": {"filename": NAME + ".kicad_pro", "version": 1},
        "net_settings": {"classes": [{"name": "Default", "clearance": 0.2, "track_width": 0.25, "via_diameter": 0.6, "via_drill": 0.3}],
                         "meta": {"version": 3}},
        "sheets": [[ROOT, "Root"]],
        "text_variables": {}}, indent=2) + "\n"

def build_bom():
    groups = {}
    for ref, kind, val, fpk, x, y, nets, d in PARTS:
        if kind in ("hole", "tp"): continue
        key = (val, FP[fpk][0])
        groups.setdefault(key, []).append(ref)
    rows = []
    lcsc = {"Si4732-A10-GS": "C2155558", "100n": "C49678", "1u": "C49326705", "470n": "C106846", "4.7k": "C17673", "20k": "C2912590", "BAV99": "C68983", "32.768kHz": "C32346", "22p": "C1804", "0R": "C17477", "56n": "C373725", "1n": "C62774"}
    desc = {"100n": "Kondensator X7R 100 nF", "22p": "Kondensator C0G 22 pF", "1u": "Kondensator X7R 1 uF", "470n": "Kondensator X7R 470 nF",
            "1n": "Kondensator C0G 1 nF", "56n": "Induktivitaet 56 nH, Q>=60 bei 200 MHz", "4.7k": "Widerstand 4.7 kOhm", "20k": "Widerstand 20 kOhm",
            "0R": "Widerstand 0 Ohm", "BAV99": "Doppeldiode BAV99 (ESD-Schutz)", "Si4732-A10-GS": "AM/FM/SW/LW/RDS Empfaenger",
            "32.768kHz": "Quarz 32.768 kHz, 3.2x1.5 mm, CL 12.5 pF", "RX_BUS": "Stiftleiste 1x9, 2.54 mm", "FM_ANT": "Stiftleiste 1x2, 2.54 mm", "AM_ANT": "Stiftleiste 1x2, 2.54 mm"}
    for (val, fp), refs in sorted(groups.items(), key=lambda kv: kv[1][0]):
        asm = "nein, Kinder loeten" if refs[0].startswith("J") else "ja"
        rows.append([val, ",".join(refs), fp.split(":")[-1], lcsc.get(val, ""), desc.get(val, ""), asm])
    return rows

def main():
    r = run(); errs, minc = check(r)
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, NAME + ".kicad_pcb"), "w", encoding="utf-8").write(build_pcb(r))
    open(os.path.join(OUT, NAME + ".kicad_sch"), "w", encoding="utf-8").write(build_sch())
    open(os.path.join(OUT, NAME + ".kicad_pro"), "w", encoding="utf-8").write(build_pro())
    bomdir = os.path.join(OUT, "..", "bom"); os.makedirs(bomdir, exist_ok=True)
    with open(os.path.join(bomdir, "RX-Board_RevA_BOM.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #", "Beschreibung", "Bestueckung"]); w.writerows(build_bom())
    with open(os.path.join(bomdir, "RX-Board_RevA_BOM_JLCPCB.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
        for row in build_bom():
            if row[5] == "ja": w.writerow([row[0], row[1], row[2], row[3]])
    print("\n".join(r.log)); print("Pruefung:", errs or "keine Fehler", "| kleinster Abstand %.3f mm" % minc)
    return r

if __name__ == "__main__":
    main()
