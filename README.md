# RX-Board Si4732

Steckbare Empfänger-Baugruppe für das [Funkfüürli](https://github.com/MaShaoDe/Funkfuerli), das Notfallradio zum Selberbauen für Kinder und Schüler.

Das RX-Board trägt den Empfängerchip Si4732-A10 (UKW, MW, KW, LW, RDS) mit Quarz und Beschaltung. Es wird komplett bestückt bestellt. Die Kinder löten nur die Stiftleisten.

**Stand:** Entwurf, Rev A in Arbeit. Noch keine Fertigungsdaten.

* Beschreibung, Pinbelegung und Anforderungen: [docs/rx-board.md](docs/rx-board.md)
* Englische Kurzfassung: [README.en.md](README.en.md)
* Lizenzen: [LICENSE.md](LICENSE.md)

## Ordner

| Ordner | Inhalt |
|---|---|
| `docs/` | Beschreibung, Anforderungen, Prüfanleitung |
| `hardware/` | KiCad 9 Projekt, Gerber, Bestückungsdaten (folgt) |
| `LICENSES/` | Lizenztexte |

## Plan

1. Schaltplan Rev A nach geprüfter Pinbelegung (siehe docs).
2. Layout mit grosszügigen Abständen, 0805, Beschriftung, Testpunkten.
3. Fertigungsdaten für JLCPCB (Gerber, Stückliste, Bestückungsliste).
4. Test: Testprogramm liest Chip aus und stimmt einen Sender ab.

Copyright 2026 FerienBSD aka Marcel Sauder. Hardware CERN-OHL-P-2.0, Doku CC-BY-4.0.
