"""RX-Board Si4732 Rev A: Bauteile, Netze und Platzierung (eine Quelle fuer Schaltplan, Platine, BOM)."""
W, H = 44.0, 30.0           # Platinengroesse in mm
CX, CY = 21.0, 15.0         # Mitte des Si4732

# Footprints: echte KiCad-Bibliothek (fplib.json, erzeugt mit fpextract.py aus einer von KiCad gespeicherten Platine)
import json, os
_LIB = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "fplib.json"), encoding="utf-8"))
def _pads(name):
    out = []
    for p in _LIB[name]["pads"]:
        typ = {"smd": "smd", "thru_hole": "thru", "np_thru_hole": "npth"}[p["type"]]
        out.append((p["num"], typ, p["shape"], p["at"][0], p["at"][1], p["size"][0], p["size"][1], p["drill"], p["rr"]))
    return out
def _fp(name): return (name, lambda: _pads(name), " ".join(_LIB[name]["attr"]))
FP = {
    "soic":  _fp("Package_SO:SOIC-16_3.9x9.9mm_P1.27mm"),
    "r":     _fp("Resistor_SMD:R_0805_2012Metric"),
    "c":     _fp("Capacitor_SMD:C_0805_2012Metric"),
    "l":     _fp("Inductor_SMD:L_0805_2012Metric"),
    "sot23": _fp("Package_TO_SOT_SMD:SOT-23"),
    "xtal":  _fp("Crystal:Crystal_SMD_3215-2Pin_3.2x1.5mm"),
    "h9":    _fp("Connector_PinHeader_2.54mm:PinHeader_1x09_P2.54mm_Vertical"),
    "h2":    _fp("Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical"),
    "tp":    _fp("TestPoint:TestPoint_Pad_D1.5mm"),
    "hole":  _fp("MountingHole:MountingHole_2.7mm_M2.5"),
}
# Abstandsflaechen (Courtyard) als Rechtecke bzw. Kreise relativ zum Ursprung
_HAND = {
    "Package_TO_SOT_SMD:SOT-23": [("rect", -1.93, -1.5, -0.9, -0.39), ("rect", -1.93, 0.39, -0.9, 1.5), ("rect", -0.9, -1.7, 0.9, 1.7), ("rect", 0.9, -0.55, 1.93, 0.55)],
    "Package_SO:SOIC-16_3.9x9.9mm_P1.27mm": [("rect", -2.2, -5.2, 2.2, 5.2), ("rect", -3.7, -5.0, -2.2, 5.0), ("rect", 2.2, -5.0, 3.7, 5.0)],
}
def courtyard(fpk):
    name = FP[fpk][0]
    if name in _HAND: return _HAND[name]
    out = []; pts = []
    for g in _LIB[name]["gfx"]:
        if g["layer"] != "F.CrtYd": continue
        if g["kind"] == "fp_rect":
            (x0, y0), (x1, y1) = g["start"], g["end"]; out.append(("rect", min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)))
        elif g["kind"] == "fp_circle":
            out.append(("circle", g["center"][0], g["center"][1], abs(g["end"][0] - g["center"][0])))
        elif g["kind"] == "fp_line": pts += [g["start"], g["end"]]
    if pts and not out:
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]; out.append(("rect", min(xs), min(ys), max(xs), max(ys)))
    return out
def silk_boxes(fpk):
    """Umhuellende Rechtecke der Silkscreen-Elemente des Footprints (relativ)."""
    out = []
    for g in _LIB[FP[fpk][0]]["gfx"]:
        if g["layer"] != "F.SilkS" or g["kind"] == "fp_text": continue
        w = g.get("width", 0.12) / 2 + 0.05
        if g["kind"] in ("fp_line", "fp_rect"):
            (x0, y0), (x1, y1) = g["start"], g["end"]; out.append((min(x0, x1) - w, min(y0, y1) - w, max(x0, x1) + w, max(y0, y1) + w))
        elif g["kind"] == "fp_circle":
            r = abs(g["end"][0] - g["center"][0]) + w; cx, cy = g["center"]; out.append((cx - r, cy - r, cx + r, cy + r))
        elif g["kind"] == "fp_poly":
            xs = [p[0] for p in g["pts"]]; ys = [p[1] for p in g["pts"]]; out.append((min(xs) - w, min(ys) - w, max(xs) + w, max(ys) + w))
    return out

J1X, J1Y0 = 40.5, 4.84
# (ref, kind, value, fp-key, x, y, {pad: net}, Beschreibung)
PARTS = [
 ("U1", "ic", "Si4732-A10-GS", "soic", CX, CY,
   {"1": "LOUT", "2": "OSC_OUT", "3": "INT", "6": "FMI", "7": "RFGND", "8": "AMI", "9": "RST", "10": "SENB",
    "11": "SCL", "12": "SDA", "13": "RCLK", "14": "3V3", "15": "GND", "16": "ROUT"}, "AM/FM/SW/LW/RDS Empfaenger"),
 ("X1", "xtal", "32.768kHz", "xtal", 21.0, 5.2, {"1": "RCLK", "2": "OSC_OUT"}, "Quarz 32.768 kHz, 3.2x1.5 mm, CL 12.5 pF"),
 ("C2", "c", "22p", "c", 15.5, 6.0, {"1": "OSC_OUT", "2": "GND"}, "C0G 22 pF"),
 ("C3", "c", "22p", "c", 26.5, 6.0, {"1": "RCLK", "2": "GND"}, "C0G 22 pF"),
 ("C1", "c", "100n", "c", 27.4, 13.1, {"1": "3V3", "2": "GND"}, "X7R 100 nF"),
 ("C4", "c", "1u", "c", 27.4, 10.9, {"1": "3V3", "2": "GND"}, "X7R 1 uF"),
 ("R1", "r", "4.7k", "r", 31.5, 15.6, {"1": "3V3", "2": "SDA"}, "Pull-up SDA"),
 ("R2", "r", "4.7k", "r", 31.5, 17.6, {"1": "3V3", "2": "SCL"}, "Pull-up SCL"),
 ("R3", "r", "4.7k", "r", 31.5, 19.6, {"1": "3V3", "2": "RST"}, "Pull-up RST"),
 ("R4", "r", "20k", "r", 27.4, 18.4, {"1": "SENB", "2": "GND"}, "SENB nach GND: Adresse 0x11"),
 ("C5", "c", "470n", "c", 14.0, 9.6, {"1": "LOUT", "2": "AUDIO_L"}, "X7R 470 nF Koppelkondensator links"),
 ("C6", "c", "470n", "c", 27.4, 8.6, {"1": "ROUT", "2": "AUDIO_R"}, "X7R 470 nF Koppelkondensator rechts"),
 ("R5", "r", "20k", "r", 31.5, 8.6, {"1": "AUDIO_L", "2": "GND"}, "Ableitwiderstand links"),
 ("R6", "r", "20k", "r", 33.6, 11.4, {"1": "AUDIO_R", "2": "GND"}, "Ableitwiderstand rechts"),
 ("L1", "l", "56n", "l", 11.6, 16.9, {"1": "FM_ANT", "2": "FM_MID"}, "FM Anpassspule 56 nH, Q>=15 bei 100 MHz"),
 ("C7", "c", "1n", "c", 15.2, 16.9, {"1": "FM_MID", "2": "FMI"}, "C0G 1 nF"),
 ("D1", "d", "BAV99", "sot23", 7.4, 17.0, {"1": "GND", "2": "3V3", "3": "FM_ANT"}, "ESD-Schutz FM"),
 ("R7", "r", "0R", "r", 9.6, 26.2, {"1": "RFGND", "2": "GND"}, "RFGND-Verbindung zu GND"),
 ("C8", "c", "470n", "c", 15.2, 21.0, {"1": "AM_ANT", "2": "AMI"}, "X7R 470 nF Koppelkondensator AM"),
 ("D2", "d", "BAV99", "sot23", 7.4, 23.0, {"1": "GND", "2": "3V3", "3": "AM_ANT"}, "ESD-Schutz AM"),
 ("J2", "conn", "FM_ANT", "h2", 3.0, 15.5, {"1": "FM_ANT", "2": "GND"}, "Teleskopantenne FM"),
 ("J3", "conn", "AM_ANT", "h2", 3.0, 22.0, {"1": "AM_ANT", "2": "RFGND"}, "Ferritstab AM/LW"),
 ("J1", "conn", "RX_BUS", "h9", J1X, J1Y0,
   {"1": "AUDIO_L", "2": "AUDIO_R", "3": "GND", "4": "3V3", "5": "SDA", "6": "SCL", "7": "RST", "8": "INT", "9": "GND"},
   "Stiftleiste zur Hauptplatine"),
 ("TP1", "tp", "3V3", "tp", 26.0, 27.0, {"1": "3V3"}, "Testpunkt 3V3"),
 ("TP2", "tp", "GND", "tp", 23.0, 27.0, {"1": "GND"}, "Testpunkt GND"),
 ("TP3", "tp", "SDA", "tp", 20.0, 27.0, {"1": "SDA"}, "Testpunkt SDA"),
 ("TP4", "tp", "SCL", "tp", 17.0, 27.0, {"1": "SCL"}, "Testpunkt SCL"),
 ("TP5", "tp", "L", "tp", 33.5, 22.5, {"1": "AUDIO_L"}, "Testpunkt Audio links"),
 ("TP6", "tp", "R", "tp", 36.0, 6.0, {"1": "AUDIO_R"}, "Testpunkt Audio rechts"),
 ("TP7", "tp", "RST", "tp", 14.0, 27.0, {"1": "RST"}, "Testpunkt Reset"),
 ("MH1", "hole", "M2.5", "hole", 3.2, 3.2, {}, "Befestigung"),
 ("MH2", "hole", "M2.5", "hole", 35.0, 27.0, {}, "Befestigung"),
]
NETS = sorted({n for p in PARTS for n in p[6].values()})
