"""RX-Board Si4732 Rev A: Bauteile, Netze und Platzierung (eine Quelle fuer Schaltplan, Platine, BOM)."""
W, H = 44.0, 30.0           # Platinengroesse in mm
CX, CY = 21.0, 15.0         # Mitte des Si4732

# Footprint-Geometrie nach KiCad-Standardbibliothek (Pads relativ zum Ursprung)
def fp_soic16():
    pads = []
    for i in range(1, 9):
        pads.append((str(i), "smd", "roundrect", -2.475, -4.445 + 1.27 * (i - 1), 1.975, 0.6, 0))
    for j in range(9, 17):
        pads.append((str(j), "smd", "roundrect", 2.475, 4.445 - 1.27 * (j - 9), 1.975, 0.6, 0))
    return pads
def fp_r0805():  return [("1", "smd", "roundrect", -0.9125, 0, 1.025, 1.4, 0), ("2", "smd", "roundrect", 0.9125, 0, 1.025, 1.4, 0)]
def fp_c0805():  return [("1", "smd", "roundrect", -0.95, 0, 1.0, 1.45, 0), ("2", "smd", "roundrect", 0.95, 0, 1.0, 1.45, 0)]
def fp_sot23():  return [("1", "smd", "roundrect", -0.9375, -0.95, 1.475, 0.6, 0), ("2", "smd", "roundrect", -0.9375, 0.95, 1.475, 0.6, 0), ("3", "smd", "roundrect", 0.9375, 0, 1.475, 0.6, 0)]
def fp_xtal():   return [("1", "smd", "roundrect", -1.25, 0, 1.0, 1.8, 0), ("2", "smd", "roundrect", 1.25, 0, 1.0, 1.8, 0)]
def fp_hdr(n):
    return [(str(i + 1), "thru", "rect" if i == 0 else "circle", 0, 2.54 * i, 1.7, 1.7, 1.0) for i in range(n)]
def fp_tp():     return [("1", "smd", "circle", 0, 0, 1.5, 1.5, 0)]
def fp_hole():   return [("", "npth", "circle", 0, 0, 2.7, 2.7, 2.7)]

FP = {
    "soic":  ("Package_SO:SOIC-16_3.9x9.9mm_P1.27mm", fp_soic16, "smd"),
    "r":     ("Resistor_SMD:R_0805_2012Metric", fp_r0805, "smd"),
    "c":     ("Capacitor_SMD:C_0805_2012Metric", fp_c0805, "smd"),
    "l":     ("Inductor_SMD:L_0805_2012Metric", fp_c0805, "smd"),
    "sot23": ("Package_TO_SOT_SMD:SOT-23", fp_sot23, "smd"),
    "xtal":  ("Crystal:Crystal_SMD_3215-2Pin_3.2x1.5mm", fp_xtal, "smd"),
    "h9":    ("Connector_PinHeader_2.54mm:PinHeader_1x09_P2.54mm_Vertical", lambda: fp_hdr(9), "through_hole"),
    "h2":    ("Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical", lambda: fp_hdr(2), "through_hole"),
    "tp":    ("TestPoint:TestPoint_Pad_D1.5mm", fp_tp, "smd"),
    "hole":  ("MountingHole:MountingHole_2.7mm_M2.5", fp_hole, "exclude_from_pos_files"),
}

J1X, J1Y0 = 40.5, 4.84
# (ref, kind, value, fp-key, x, y, {pad: net}, Beschreibung)
PARTS = [
 ("U1", "ic", "Si4732-A10-GS", "soic", CX, CY,
   {"1": "LOUT", "2": "OSC_OUT", "3": "INT", "6": "FMI", "7": "RFGND", "8": "AMI", "9": "RST", "10": "SENB",
    "11": "SCL", "12": "SDA", "13": "RCLK", "14": "3V3", "15": "GND", "16": "ROUT"}, "AM/FM/SW/LW/RDS Empfaenger"),
 ("X1", "xtal", "32.768kHz", "xtal", 21.0, 5.2, {"1": "OSC_OUT", "2": "RCLK"}, "Quarz 32.768 kHz, 3.2x1.5 mm, CL 12.5 pF"),
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
 ("L1", "l", "56n", "l", 11.0, 16.9, {"1": "FM_ANT", "2": "FM_MID"}, "FM Anpassspule 56 nH, Q>=15 bei 100 MHz"),
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
 ("TP5", "tp", "L", "tp", 33.0, 23.5, {"1": "AUDIO_L"}, "Testpunkt Audio links"),
 ("TP6", "tp", "R", "tp", 36.0, 6.0, {"1": "AUDIO_R"}, "Testpunkt Audio rechts"),
 ("TP7", "tp", "RST", "tp", 14.0, 27.0, {"1": "RST"}, "Testpunkt Reset"),
 ("MH1", "hole", "M2.5", "hole", 3.2, 3.2, {}, "Befestigung"),
 ("MH2", "hole", "M2.5", "hole", 35.0, 27.0, {}, "Befestigung"),
]
NETS = sorted({n for p in PARTS for n in p[6].values()})
