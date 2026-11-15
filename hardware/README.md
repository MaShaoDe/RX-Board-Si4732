# hardware

Rev A des RX-Boards (UKW, MW, LW). Stand 2026-11-15: **Entwurf, in KiCad noch nicht geöffnet und nicht geprüft.**

## Inhalt

| Pfad | Inhalt |
|---|---|
| `kicad/RX-Board-Si4732.kicad_pro` | KiCad-Projekt (Format KiCad 8, öffnet in KiCad 9) |
| `kicad/RX-Board-Si4732.kicad_sch` | Schaltplan. Verbindungen laufen über gleichnamige Netzbezeichner, nicht über gezeichnete Leitungen |
| `kicad/RX-Board-Si4732.kicad_pcb` | Platine 44 x 30 mm, 2 Lagen, bestückt und verlegt, Masseflächen vorne und hinten |
| `bom/RX-Board_RevA_BOM.csv` | Stückliste. Die Spalte "LCSC Part #" ist bis auf den Chip noch leer |
| `preview/layout-vorschau.png` | Grobe Vorschau des Layouts (kein KiCad-Bild) |
| `tools/` | Python-Skripte, die diese Dateien erzeugen (siehe unten) |

## Erste Schritte in KiCad

1. Projekt öffnen. Wenn KiCad nach Symbol- oder Footprint-Bibliotheken fragt, "Aktuelle Einstellungen behalten" wählen. Die Symbole sind im Schaltplan eingebettet.
2. Schaltplan: ERC ausführen. Zu erwarten sind Warnungen zu Power-Pins ohne Treiber (alle Pins sind als passiv gesetzt) und "Pin nicht auf Raster".
3. Platine: Zonen füllen (Taste B), dann DRC ausführen. Zu prüfen: Abstände, Silkscreen über Pads, Textgrössen, Beschriftung auf der Rückseite (gespiegelt).
4. Footprints mit "Aktualisieren aus Schaltplan" gegen die Standardbibliothek abgleichen.
5. Layout durchsehen. Das Verlegen hat ein Skript gemacht (Gitter-Router). Kritisch sind die Antennenpfade (FM, AM), der Quarz und die Lage der Teile zum Ferritstab.
6. Gerber, Bohrdateien und Bestückungsdatei (Position) in KiCad exportieren, im JLCPCB-Viewer Drehung der Bauteile prüfen.

## Erzeugen

```
cd hardware/tools
python3 rxwrite.py      # schreibt kicad/ und bom/
python3 rxcheck.py      # Abstands- und Verbindungsprüfung
python3 rxsyntax.py ../kicad/RX-Board-Si4732.kicad_pcb ../kicad/RX-Board-Si4732.kicad_sch
```

Benötigt Python 3 und numpy. `rxmodel.py` enthält Bauteile, Netze und Platzierung. Änderungen dort ergeben nach `rxwrite.py` neue Dateien. Manuelle Änderungen in KiCad werden dabei überschrieben.

## Offen

* LCSC-Nummern der Bauteile ergänzen und die Verfügbarkeit beim Hersteller prüfen.
* Quarz: Bauform 3215, Lastkapazität 12.5 pF, Toleranz laut AN383 ±50 ppm. Passenden Typ in der JLCPCB-Bibliothek wählen.
* FM-Spule 56 nH ist ein Startwert aus AN383 und wird im Labortest geprüft (Mikroe nutzt 270 nH).
* Footprint der Stiftleiste, Kodierung und mechanische Lage zur Hauptplatine festlegen.
