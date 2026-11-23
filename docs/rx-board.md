# RX-Board: Empfänger-Baugruppe (Stand 2026-11-19, Rev A gefertigt, Tests offen)

Dieses Dokument ist die Quelle. Die Kopie im Hauptprojekt verweist hierher.

Das RX-Board ist die Empfänger-Baugruppe des Funkfüürli. Es steckt auf der Hauptplatine und enthält den Empfängerchip Si4732 mit seiner Beschaltung. Die Kinder löten nur die Stiftleisten, das Board kommt bestückt aus der Fertigung.

Einordnung im Gerät: [blockschaltbild.md](https://github.com/MaShaoDe/Funkfuerli/blob/main/docs/blockschaltbild.md). Pins der Hauptplatine: [pinplan.md](https://github.com/MaShaoDe/Funkfuerli/blob/main/docs/pinplan.md).

## 1. Aufgabe

Das RX-Board nimmt das Antennensignal auf, wählt einen Sender (Abstimmung), demoduliert ihn (UKW, MW, KW) und gibt das Tonsignal links und rechts aus. Der Si4732 macht Tuner, Demodulator und Stereodecoder in einem Chip. Er ist kein SDR und liefert keine Rohdaten (siehe [konzept.md](https://github.com/MaShaoDe/Funkfuerli/blob/main/docs/konzept.md)).

```
Antenne  ->  RX-Board  ->  Ton (L, R)  ->  Verstärker / Klinke
                ^
        Steuerung (ESP32) über I2C
```

## 2. Entscheid

* Eigenes Board statt fertigem Mikroe AM/FM 2 Click (2026-11-15). Der Click passt nicht zu unserem Pinplan und hat keinen KW-Zweig.
* Kinder löten kein SMD. Das RX-Board wird komplett bestückt bestellt (PCBA bei JLCPCB), die Kinder löten nur Stiftleisten.
* Der Chip, der Quarz und die Kondensatoren müssen deshalb in der Fertigungsbibliothek des Herstellers lieferbar sein. Das wird beim Entwurf je Bauteil geprüft.
* Vorlage für die Beschaltung: offene Schaltpläne der PU2CLR-Bibliothek (MIT) und das Datenblatt des Si4732-A10. Nichts von Sunnygold (CC BY-NC-SA) und nichts von den Umbaumodulen für UV-K5/K6.

## 3. Schnittstelle zur Hauptplatine

Die Belegung der Stiftleiste wird nach dem Pinplan der Hauptplatine festgelegt (Abschnitt 7). Geplant sind diese Signale:

| Signal | Richtung | Bemerkung |
|---|---|---|
| 3.3 V | Eingang | Versorgung, Chip arbeitet laut Datenblatt mit 2.7 bis 3.6 V. Aus dem LDO, nie direkt vom Akku |
| GND | | Masse, mehrere Pins |
| SDA, SCL | Ein/Aus | I2C zur Steuerung (Pinplan: GPIO 8 und 9) |
| RST | Eingang | Reset (Pinplan: GPIO 7) |
| Audio L, Audio R | Ausgang | Analoges Tonsignal, weiter an Verstärker und Klinke |
| Antenne FM (und KW) | Eingang | Teleskopantenne oder BNC |
| Antenne AM/LW | Eingang | Ferritstab |
| Interrupt (optional) | Ausgang | Nur wenn die Firmware ihn braucht |

Welche Antenne an welchen Eingang gehört: FM kommt vom Teleskop an FMI. Für Kurzwelle (SW) beschreibt AN383 die Beschaltung über AMI, aber nur für Si4734/35. Beim Si4732 ist offen, ob KW über FMI oder AMI läuft (Rev-A-Tests P4 und P5 im Pflichtenheft). Der Ferritstab sitzt an AMI für MW und LW. Details in Abschnitt 4c.

## 4. Anforderungen

Qualität und Haltbarkeit haben Vorrang vor Grösse. Wenn eine enge Bestückung nicht sicher ist, wird grosszügiger gebaut.

**Grundlagen** (aus [anforderungen.md](https://github.com/MaShaoDe/Funkfuerli/blob/main/docs/anforderungen.md)): wenig Strom, gute Empfangsqualität, einfache Handhabung, robust, günstig.

**Mechanik und Robustheit**
* Passive Bauteile in Grösse 0805, keine kleineren. Grosszügige Abstände zwischen den Teilen, mehr als das Minimum des Herstellers. Der Chip im SOIC-16-Gehäuse bleibt, das ist gross genug.
* Stiftleisten im Raster 2.54 mm, steckbar und tauschbar.
* 2 Befestigungslöcher. Das Board wird im Gehäuse gehalten, die Stiftleiste trägt nur die Elektrik (Konzept Abschnitt 11, Falltest aus 1 m).
* Kleiner als der Mikroe-Click (57.15 x 25.4 mm), genaue Masse nach dem Layout.

**Schutz vor Fehlern**
* Pin 1 deutlich markiert, die Stiftleiste so gelegt, dass das Board nur in einer Richtung passt (Kodierung).
* Der Chip arbeitet laut Datenblatt mit 2.7 bis 3.6 V. Die Versorgung kommt nur aus dem LDO, nie direkt vom Akku oder aus 5 V. Absolute Maximalwerte im Datenblatt nachsehen.
* Schutz der Antenneneingänge gegen statische Aufladung (SMD, auf dem Board).

**Platine und Lack**
* 1.6 mm FR4, 2 Lagen, Oberfläche ENIG (flach, korrosionsfest, gut für feine Lötpads).
* Lötstopplack matt, dunkel. Weisser Siebdruck darauf. Zusätzlicher Schutzlack ist optional und kommt erst nach dem Test, weil er Antenneneingänge und Quarz leicht verstimmen kann. Stiftleisten und Pads bleiben frei.

**Beschriftung** (alles auf dem Board beschriftet)
* Bauteilnamen (R1, C1, U1, X1) und Pin-Namen an den Stiftleisten.
* Antennenanschlüsse (FM/SW, AM/LW), "RX", Version (Rev A) und Jahr, Feld für die Seriennummer.
* Beschriftete Testpunkte für 3.3 V, GND, SDA, SCL, Audio links und rechts, Reset.
* `Copyright 2026 FerienBSD aka Marcel Sauder`, Link `github.com/MaShaoDe/Funkfuerli` und `CERN-OHL-P-2.0`.
* Kein Rufzeichen auf dem Board, nur Copyright (Entscheid 2026-11-15).
* Mindestgrösse von Schrift und Linien beim Hersteller vor der Bestellung prüfen.

**Elektrik und Störungen**
* Kein Schaltregler auf dem Board, Versorgung nur über Kondensatoren (Entkopplung).
* Kurze Leitungen zu den Antenneneingängen, durchgehende Massefläche, Quarz nahe am Chip, Abstand zu ESP32, Display und Verstärker.

**Qualitätssicherung**
* Jedes Board wird vor dem Kurs geprüft: Ein kleines Testprogramm liest den Chip aus und stimmt einen Sender ab.
* Mehr Boards bestellen, als der Kurs braucht (Mindestmenge meist 5), als Reserve.
* Zwei Revisionen einplanen: Rev A zum Testen, Rev B mit den Korrekturen für den Kurs.
* DRC in KiCad und die Herstellerprüfung der Bestückungsdaten (Drehung der Bauteile) vor der Bestellung.

## 4a. Si4732-A10-GS: geprüfte Pinbelegung (SOIC-16)

Quellen: Datenblatt-Kurzfassung Silicon Labs (2013) und Skyworks (2021), beide gleich. Gegengelesen mit dem Mikroe-Schaltplan "AM/FM 2 Click v100". Die frühere Tabelle aus der PU2CLR-Vorlage (Gedächtnis) war falsch und ist ersetzt.

| Pin | Name | Funktion | Auf dem RX-Board |
|---|---|---|---|
| 1 | LOUT/DFS | Audio links | Ausgang, 470 nF Koppelkondensator |
| 2 | GPO3/DCLK | General Purpose Out 3 / Takt | Quarz (OSC-OUT), 22 pF nach GND |
| 3 | GPO2/INTB | General Purpose Out 2 / Interrupt | offen lassen oder optional zur Stiftleiste (muss beim Reset low sein) |
| 4 | GPO1 | General Purpose Out 1 | unbeschaltet (interner Pull-up, muss beim Reset high sein) |
| 5 | NC | nicht belegt | unbeschaltet |
| 6 | FMI | FM Antenneneingang | Teleskop, ESD-Schutz |
| 7 | RFGND | HF-Masse | an GND |
| 8 | AMI | AM und LW Antenneneingang (SW offen, siehe oben) | Ferritstab, ESD-Schutz |
| 9 | RST | Reset, aktiv low | Pull-up 4.7 kΩ, von ESP32 |
| 10 | SENB | Adresswahl I2C | fest verdrahtet (siehe unten) |
| 11 | SCLK | I2C Takt | Pull-up 4.7 kΩ |
| 12 | SDIO | I2C Daten | Pull-up 4.7 kΩ |
| 13 | RCLK | Referenztakt | Quarz (OSC-IN), 22 pF nach GND |
| 14 | VDD | 2.7 bis 3.6 V | 3.3 V, 100 nF und 1 µF |
| 15 | GND | Masse | GND |
| 16 | ROUT/DOUT | Audio rechts | Ausgang, 470 nF Koppelkondensator |

Gehäuse: Rastermass 1.27 mm, Körper 3.90 x 9.90 mm (JEDEC MS-012). Temperaturbereich –20 bis 85 °C.

## 4b. Beschaltung (Werte aus dem Mikroe-Schaltplan, Startwerte)

Das Layout wird nach Schaltplan und Datenblatt gezeichnet. Die Werte unten sind Startwerte und werden im Labortest geprüft.

* Quarz 32.768 kHz zwischen Pin 2 und Pin 13, je 22 pF nach GND.
* I2C und Reset: Pull-ups 4.7 kΩ nach 3.3 V.
* Versorgung: 100 nF und 1 µF direkt an Pin 14.
* Adresse (AN332, Abschnitt 6.1): SENB = GND ergibt 7-Bit-Adresse 0x11 (Schreiben 0x22), SENB = 3.3 V ergibt 0x63 (Schreiben 0xC6). Wir legen SENB fest auf GND (Adresse 0x11). Beim Mikroe-Click ist es per Jumper wählbar.
* Audio: je 470 nF in Reihe pro Kanal, dazu 20 kΩ Widerstände.
* FM-Pfad (Rev A, laut Stückliste): 1 nF in Reihe, Spule 56 nH, Schutzdioden BAV99. Mikroe nutzt 270 nH.
* AM-Pfad: 470 nF in Reihe, Ferritstab an Pin 8, Dioden BAV99 als Schutz.
* Der Kopfhörerverstärker (LM4910) des Mikroe-Clicks entfällt. Das Tonsignal geht auf die Stiftleiste. Der Chip liefert nur Line-Pegel (Datenblatt Si473x-B20: 80 mV eff, Last mindestens 10 kΩ). Der Kopfhörerverstärker sitzt im Basisboard (Repo Funkbasis-ESP32). Am Ausgang liegen 470 nF in Reihe und 20 kΩ nach GND pro Kanal.
* Bus-Modus (AN332, Abschnitt 6): Der Chip wählt den Modus beim Reset über GPO1 und GPO2. Intern ziehen 1 MΩ Widerstände GPO1 hoch und GPO2 tief, das ergibt I2C (2-Wire). Darum bleiben GPO1 und GPO2 auf dem Board unbeschaltet.
* Start (AN332): Quarzbetrieb braucht beim Befehl POWER_UP XOSCEN = 1 und OPMODE = 0x05 (analoger Ausgang). Danach mindestens 500 ms warten, bis der erste Abstimmbefehl kommt. Zum Chip-Test gibt POWER_UP mit FUNC = 15 die Teilenummer zurück.
* Die genaue Verschaltung (welcher Wert in welcher Leitung) wird aus dem Schaltplan gezeichnet, nicht aus dieser Liste. Der Ferritstab (180 bis 450 µH) steht in 4c, der Wert wird gemessen.

## 4c. Antennen (Quelle: AN383, Skyworks 2025)

**FM, Teleskop an FMI**
* Kopplung 1 nF (C0G) in Reihe zu FMI, Anpassspule 56 nH (Güte mindestens 15 bei 100 MHz, kleiner Gleichstromwiderstand), ESD-Diode mit höchstens 1 pF (Beispiel CM1213-01ST).
* Der Mikroe-Click nutzt 270 nH an seiner SMA-Buchse. Wir starten mit den Werten aus AN383 (56 nH) und prüfen im Labortest.
* Chip möglichst nah an der Antennenbuchse, Spule und Buchse zusammen und weit weg von Störquellen und I/O-Leitungen, ESD-Diode direkt an der Buchse.

**MW und LW, Ferritstab an AMI**
* Ferritstab mit 180 bis 450 µH, Kopplung 0.47 µF (X7R) in Reihe zu AMI. ESD-Diode nur nötig, wenn ein freies Pad nach aussen führt.
* Empfohlene Stäbe laut AN383: SL8X50MW70T (8 x 50 mm, Tischradio), SL4X30MW100T (4 x 30 mm, Portable). Hersteller Jiaxin (firstantenna.com).
* Gesamtkapazität am AMI klein halten: etwa 29 pF bei 300 µH (der Chip selbst hat 8 pF). Kurze Leitungen, kleine Pads.
* Unter dem Ferritstab keine Massefläche und keine Leitung, Abstand etwa 6 mm (1/4 Zoll) oder die Breite des Stabs. Weit weg von Taktleitungen, ESP32 und Display. Aussen am Gerät oder an einem Kabel sitzt der Stab weniger im Störfeld.

**KW (SW), Eingang offen (erst Rev B)**
* Für die Kurzwelle beschreibt AN383 (nur Si4734/35) den Weg über AMI, beim Si4732 ist er ungeprüft. Der Weg über AMI braucht eine Tiefpass-Spule 4.7 µH (Güte mindestens 20 bei 25 MHz), 33 pF als Sperrkreis für AM, und der Ferritstab dient als Spule gegen Masse. Alternativ eine feste Spule 220 µH, wenn kein AM gebraucht wird.
* Umschalter (SPDT) zwischen KW-Teleskop und AM-Ferritstab, oder zwei getrennte Buchsen. Entscheid 2026-11-15: Die KW-Beschaltung kommt erst in Rev B.
* Zwei ESD-Dioden (je höchstens 1 pF) an den Antennenbuchsen, weil die Teleskopantenne aussen liegt.

**Layout allgemein**
* Der Abblockkondensator sitzt direkt am VDD-Pin (AN383 nennt 22 nF, wir bleiben bei 100 nF und 1 µF), mit kurzer, breiter Masseleitung zum GND-Pin.
* RFGND lokal von GND trennen und an der Masseebene anbinden (Datenblatt Si473x).
* Quarz so nah wie möglich an den Pins 2 und 13. Die RCLK-Leitung weit weg von SDIO führen.
* Kein Schaltregler, keine Taktleitungen im Bereich 520 bis 1720 kHz in der Nähe der AM-Antenne.

## 4d. Revisionen

| Rev | Inhalt |
|---|---|
| A | UKW (FMI), MW und LW (AMI mit Ferritstab). Kein KW-Zweig. Zum Testen von Chip, Quarz, I2C, Audio, Antennen. KiCad-Entwurf liegt in `hardware/kicad/` (siehe `hardware/README.md`). |
| B | Korrekturen aus Rev A. Dazu KW, Eingang nach Tests P4 und P5 (Variante AMI: Tiefpass-Spule 4.7 µH, 33 pF, Umschalter). Version für den Kurs. |

## 4e. Stiftleiste J1 zur Hauptplatine (Rev A)

1x9, Raster 2.54 mm, an der rechten Kante. Pin 1 ist quadratisch und oben.

| Pin | Signal | Bemerkung |
|---|---|---|
| 1 | AUDIO_L | Tonsignal links, nach 470 nF, 20 kΩ gegen GND |
| 2 | AUDIO_R | Tonsignal rechts |
| 3 | GND | |
| 4 | 3V3 | Versorgung aus dem LDO der Hauptplatine |
| 5 | SDA | I2C Daten, Pull-up 4.7 kΩ auf dem Board |
| 6 | SCL | I2C Takt, Pull-up 4.7 kΩ auf dem Board |
| 7 | RST | Reset, Pull-up 4.7 kΩ auf dem Board |
| 8 | INT | GPO2/INTB, optional |
| 9 | GND | |

Der Pinplan der Hauptplatine muss dieser Reihenfolge folgen (Buchsenleiste 1x9).

## 4f. Antennenanschlüsse J2 und J3 (Rev A)

Beide Stiftleisten 1x2, Raster 2.54 mm, Pin 1 quadratisch.

| Anschluss | Pin | Signal | Bemerkung |
|---|---|---|---|
| J2 (FM_ANT) | 1 | FM_ANT | Antenne für UKW, über das FM-Anpassnetz (1 nF, 56 nH) zum Chip-Eingang FMI (Pin 6). Für den KW-Versuch P4 |
| J2 (FM_ANT) | 2 | GND | Masse |
| J3 (AM_ANT) | 1 | AM_ANT | Ferritstab für MW und LW, über 470 nF zum Chip-Eingang AMI (Pin 8), BAV99 als Schutz. Für den KW-Versuch P5 |
| J3 (AM_ANT) | 2 | RFGND | Antennenmasse, Chip-Pin 7. Nur über R7 (0 Ω) mit GND verbunden (Schaltplan) |

## 4g. Testpunkte (Rev A)

SMD-Pads mit 1.5 mm Durchmesser, beschriftet.

| Nr. | Signal | Bemerkung |
|---|---|---|
| TP1 | 3V3 | Versorgung |
| TP2 | GND | Masse, Bezug für Messungen |
| TP3 | SDA | I2C Daten, im Ruhezustand etwa 3.3 V |
| TP4 | SCL | I2C Takt, im Ruhezustand etwa 3.3 V |
| TP5 | AUDIO_L (Aufdruck L) | Ton links, wie J1 Pin 1 |
| TP6 | AUDIO_R (Aufdruck R) | Ton rechts, wie J1 Pin 2 |
| TP7 | RST | Reset, im Ruhezustand etwa 3.3 V |

Befestigung: 2 Löcher mit 2.7 mm für M2.5 (MH1, MH2). Platine 44 x 30 mm. Quelle der Netznamen und Pins: `hardware/kicad/RX-Board-Si4732.kicad_pcb` und `.kicad_sch`.

## 5. Bestückung

* Chip: Si4732-A10-GS im 16-poligen SOIC-Gehäuse.
* Quarz: 32.768 kHz (bestätigt durch den Mikroe-Schaltplan).
* Entkopplung und Lastkondensatoren: Werte aus Abschnitt 4b.
* Alles SMD, bestückt vom Hersteller. Von Hand gelötet werden nur die Stiftleisten.
* Mindestmenge: Platinen meist 5 Stück, bei der Bestückung vor der Bestellung im Angebot prüfen.

## 6. Test

* Vergleich: Empfang UKW, MW und LW. KW nur als Versuch (Tests P4 und P5, Rev A hat keinen KW-Zweig).
* Stromaufnahme im Betrieb messen.
* Störtest nach Konzept Abschnitt 8.
* Zuerst auf dem Breadboard mit Kabeln (Stufe 1 in [prototyp.md](https://github.com/MaShaoDe/Funkfuerli/blob/main/docs/prototyp.md)).

## 7. Offene Punkte

1. Vollständiges Datenblatt des Si4732-A10: Es gibt öffentlich nur das 3-seitige Data Short. AN332 (Programming Guide) liegt vor und liefert Adresse, Bus-Modus und Start. Es fehlen weiter Applikationsschaltung mit Werten, Maximalwerte und Layout-Hinweise. Pinbelegung ist geprüft (Abschnitt 4a), die Werte in 4b sind Startwerte aus dem Mikroe-Schaltplan.
2. Erledigt: Mikroe-Schaltplan gegengelesen (Abschnitt 4a und 4b).
3. Erledigt: Ferritstab (180 bis 450 µH, 0.47 µF) nach AN383, siehe 4c. Entscheid 2026-11-15: Rev A ohne Kurzwelle (UKW, MW, LW), KW in Rev B. Offen für Rev B: KW-Eingang FMI oder AMI (Tests P4, P5), Umschalter oder zwei Buchsen, Teleskop für FM und KW gemeinsam oder getrennt.
4. Schutz der Antenneneingänge gegen statische Aufladung (SMD, auf dem Board).
5. Verfügbarkeit von Chip, Quarz und Kondensatoren beim Hersteller, Angebot einholen.
6. Lizenzdatei der PU2CLR-Bibliothek einsehen, Autor in der Doku nennen.
7. Eigenes Repo für das RX-Board: `RX-Board-Si4732` (dieses Repo, angelegt 2026-11-15).

## 8. Erklärt für Laien

**Das Ohr des Radios.**

Stell dir den Himmel voller Radiowellen vor, wie ein Meer voller Wellen. Alle Sender funken gleichzeitig, durcheinander. Die Antenne ist wie ein Netz: Sie fängt alles auf einmal. Aber ein Netz voller Wellen gibt noch keinen Ton.

Dafür gibt es das RX-Board. Es ist der Sortierer. Du drehst am Knopf, und das RX-Board pickt genau den einen Sender heraus, den du willst. Alle anderen lässt es draussen. Dann übersetzt es die Welle in Töne, die der Lautsprecher abspielen kann.

Im Herzen des Boards sitzt ein kleiner Chip, kleiner als ein Fingernagel. Er rechnet sehr schnell und macht dabei alles, was früher ein ganzer Schrank voller Bauteile gebraucht hat. Weil er so winzig ist, bestücken wir ihn nicht von Hand. Das macht eine Maschine. Du lötest nur die Stifte an, mit denen das Board in das Radio gesteckt wird.

Das RX-Board ist also: das Ohr, das alles hört, und der Kopf, der den richtigen Sender findet.

*Copyright FerienBSD aka Marcel Sauder. Doku unter CC-BY-4.0.*
