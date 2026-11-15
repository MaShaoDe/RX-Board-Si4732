# JLCPCB: Teile aussuchen (Rev A)

Stand 2026-11-15. Für jedes Teil die Anforderung, den Suchbegriff im JLCPCB-Teilekatalog (jlcpcb.com/parts) und die LCSC-Nummer eintragen. Bevorzugt "Basic Part" (keine Rüstgebühr). Nach der Wahl die Nummer in `RX-Board_RevA_BOM.csv` in die Spalte "LCSC Part #" setzen und Lagerbestand sowie Preis prüfen.

| Designator | Wert | Bauform | Anforderung | Suchbegriff | LCSC |
|---|---|---|---|---|---|
| C1 | 100 nF | 0805 | X7R, mindestens 16 V | `100nF 0805 X7R` | C49678 (Yageo, 50 V, bestätigt) |
| C4 | 1 µF | 0805 | X7R, mindestens 10 V | `1uF 0805 X7R` | C49326705 (16 V) |
| C2, C3 | 22 pF | 0805 | C0G/NP0, 5 % oder besser, mindestens 50 V | `22pF 0805 C0G` | C1804 (50 V) |
| C7 | 1 nF | 0805 | C0G/NP0, 10 % oder besser (Antennenpfad) | `1nF 0805 C0G` | |
| C5, C6, C8 | 470 nF | 0805 | X7R, mindestens 16 V | `470nF 0805 X7R` | C106846 (25 V) |
| R1, R2, R3 | 4.7 kΩ | 0805 | 1 % | `4.7k 0805 1%` | C17673 |
| R4, R5, R6 | 20 kΩ | 0805 | 1 % | `20k 0805 1%` | C2912590 |
| R7 | 0 Ω | 0805 | Brücke | `0R 0805` | C17477 |
| L1 | 56 nH | 0805 | HF-Spule, Güte mindestens 15 bei 100 MHz, kleiner Gleichstromwiderstand | `56nH 0805 inductor RF` | C373725 (Chilisin CS0805-56NJ-S, Q 60 bei 200 MHz, SRF 1.55 GHz, 340 mΩ, ±5 %). Alternative: C964072 (Q 15, billiger) |
| D1, D2 | BAV99 | SOT-23 | Doppeldiode, Pin 1 Anode, Pin 2 Kathode, Pin 3 gemeinsam | `BAV99 SOT-23` | C68983 |
| X1 | 32.768 kHz | 3.2 x 1.5 mm | 2 Pads, Lastkapazität 12.5 pF, Toleranz ±20 ppm (AN383 verlangt höchstens ±50 ppm) | `32.768kHz 3215 12.5pF` | C32346 (12.5 pF, ±20 ppm) |
| U1 | Si4732-A10-GS | SOIC-16 | Chip, Band-und-Rolle (GSR) ist in Ordnung | `SI4732-A10-GSR` | C2155558 (Lager und Preis prüfen) |

Nicht über JLCPCB: Stiftleisten J1 (1x9), J2 und J3 (je 1x2), Raster 2.54 mm. Die Kinder löten sie von Hand.

## Hinweise

* **L1:** AN383 nennt eine 0603-Spule (Murata LQW18AN56nJ00D). Unsere Pads sind 0805. Wenn nur 0603 in Frage kommt, in KiCad den Footprint `L_0603_1608Metric` setzen und neu verlegen lassen. Sag mir Bescheid.
* **Quarz:** Mit 22 pF Lastkondensatoren und einer Leiterbahn-Streukapazität von einigen pF liegt die wirksame Last bei rund 13 bis 16 pF. Das passt für einen Quarz mit 12.5 pF. Läuft der Quarz zu tief, 18 pF testen.
* **D1, D2:** AN383 empfiehlt für den Antennenschutz eine Diode mit höchstens 1 pF. BAV99 hat etwa 1.5 pF. Das ist der Wert aus dem Mikroe-Schaltplan. Im Labortest die UKW-Empfindlichkeit prüfen.
* **Extended Parts:** Der Chip ist ein "Extended Part" und kostet eine Rüstgebühr pro Sorte.
* Die Drehung der Bauteile in der JLCPCB-Vorschau prüfen (SOIC-16, SOT-23, Quarz).
