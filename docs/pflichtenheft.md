# RX-Board Si4732: Pflichtenheft Rev B (Stand 2026-11-19, Entwurf)

Ablage im Repo `RX-Board-Si4732`: `docs/pflichtenheft.md`. Gemeinsame Anforderungen des Geräts stehen in der Projektdefinition des Funkfüürli (Nummern F, G, H, T, L, O). Hier steht nur, was das Funkmodul selbst können muss. Die bestehende Beschreibung bleibt in `docs/rx-board.md` (Rev A, Pinbelegung des Chips, Beschaltung).

## 1. Zweck und Abgrenzung

* Das RX-Board ist die steckbare Empfänger-Baugruppe des **Funkfüürli**: Antennensignal rein, Ton links und rechts raus, Steuerung per I2C (Projektdefinition T1).
* Es ist **kein SDR** und kein Modul für den Wellenjäger. Der Si4732 liefert keine I/Q-Daten. Der Wellenjäger bekommt ein eigenes Funkmodul.
* Der Stecker J1 ist aber so ausgelegt, dass ein späteres Wellenjäger-Modul auf dieselbe Hauptplatine passt (Projektdefinition T8). Dafür sind Reservepins vorhanden, auf dem RX-Board bleiben sie unbeschaltet.
* Rev A (bestellt, in Fertigung) ist ein Testboard: UKW, MW, LW. Rev B ist die Version für den Kurs.

## 2. Anforderungen

Priorität: **M** = muss, **S** = soll, **K** = kann.

| Nr | Anforderung | Prio | Bemerkung |
|---|---|---|---|
| R1 | Empfang UKW 87.5 bis 108 MHz, MW 520 bis 1710 kHz, KW 2.3 bis 26.1 MHz | M | Chip: FM 64 bis 108 MHz, SW 2.3 bis 26.1 MHz, LW 153 bis 279 kHz (Kurzdatenblatt). LW bleibt in der Firmware ausgeblendet |
| R2 | KW-Empfang mit brauchbarer Qualität | M | Eingang offen, siehe Abschnitt 3 |
| R3 | RDS (Sendername) | K | Chip kann es, Firmware entscheidet |
| R4 | Antenneneingänge: Teleskop (UKW, evtl. KW), Ferritstab (MW, LW), KW-Antenne | M | Buchsen nach Abschnitt 3 |
| R5 | ESD-Schutz an jeder von aussen erreichbaren Antennenbuchse, Diode höchstens 1 pF | M | Beispiel CM1213-01ST (AN383) |
| R6 | Versorgung nur 3.3 V aus dem LDO der Hauptplatine, nie direkt vom Akku | M | Chip 2.7 bis 3.6 V. Entkopplung 100 nF und 1 µF am VDD |
| R7 | Ton analog links und rechts, Koppelkondensator 470 nF, 20 kΩ gegen GND | M | wie Rev A |
| R8 | I2C-Adresse fest 0x11 (SENB an GND) | M | Pull-ups 4.7 kΩ auf dem Board |
| R9 | Stecker J1 steckbar, Kodierung gegen falsches Aufstecken, Pin 1 markiert | M | Belegung Abschnitt 4 |
| R10 | Reservepins für I2S im J1, unbeschaltet | M | Nur Vorbereitung für den Wellenjäger, keine Wellenjäger-Bauteile |
| R11 | Kein Schaltregler auf dem Board | M | Störarm (G3, T7) |
| R12 | Alles SMD vollständig bestückt vom Hersteller, Kinder löten nur Stiftleisten | M | H2, H3 |
| R13 | Passive Teile 0805, grosszügige Abstände, Chip SOIC-16 | M | Qualität vor Grösse |
| R14 | Alle Teile in der Bibliothek des Herstellers lieferbar | M | LCSC-Nummern in der BOM, Verfügbarkeit vor der Bestellung prüfen |
| R15 | 2 Befestigungslöcher M2.5, das Board wird vom Gehäuse gehalten, nicht von der Stiftleiste | M | T10 (Falltest) |
| R16 | Beschriftete Testpunkte: 3V3, GND, SDA, SCL, AUDIO_L, AUDIO_R, RST | M | Rev B zusätzlich Testpunkt für das Antennensignal am Chip (FMI, AMI) |
| R17 | Siebdruck: Bauteilnamen, Pinnamen, Antennenanschlüsse, Version, Jahr, Seriennummernfeld, Copyright, Repo-Link, Lizenz | M | Kein Rufzeichen. Mindestgrösse beim Hersteller prüfen |
| R18 | Platine 1.6 mm FR4, 2 Lagen, ENIG, Lötstopplack matt dunkel | S | wie Rev A |
| R19 | Grösse so klein wie sinnvoll, Ziel höchstens ca. 50 x 30 mm | S | Rev A: 44 x 30 mm |
| R20 | Lizenz Hardware CERN-OHL-P-2.0, Doku CC-BY-4.0 | M | L1 |

## 3. KW-Eingang (offene Frage)

Die Quellen widersprechen sich, welcher Chip-Eingang bei KW verwendet wird:
* Blockbild des Si4732-A10 (Kurzdatenblatt): FMI = "FM / SW ANT", AMI = "AM / LW ANT".
* AN383 Abschnitt 10 (nennt Si4734/35, nicht Si4732): KW-Antenne über L1 4.7 µH auf **AMI**.
* Pinbeschreibung der Si473x-Familie: FMI "FM/WB/SW", AMI "AM/SW/LW".

Entscheid erst nach dem Rev-A-Test (Abschnitt 5).

| | Variante A: KW an FMI | Variante B: KW an AMI (nach AN383) |
|---|---|---|
| Idee | Teleskop oder Draht an den FM-Eingang, Anpassung für UKW und KW zusammen | Teleskop über L1 und Umschalter an AMI, Ferritstab für MW |
| Neue Teile | evtl. nur andere Werte im FM-Pfad | L1 4.7 µH (Güte mindestens 20 bei 25 MHz), C3 33 pF C0G 5 %, SPDT-Umschalter mit kleiner Kapazität, zweite ESD-Diode |
| Umschaltung MW und KW | nicht nötig, getrennte Eingänge | nötig: Umschalter, gesteuert per Jumper oder per Chip-Ausgang GPO1 |
| Antenne | gemeinsames Teleskop für UKW und KW | gemeinsames Teleskop möglich (C1 18 pF und L2 180 nH nach AN383) |
| Risiko | UKW-Qualität leidet, wenn die Anpassung für KW verändert wird | Wert von L1 passt zu Teleskop bis ca. 56 cm (12 pF), eine lange Drahtantenne verstimmt das Filter |
| Aufwand Rev B | klein | mittel |

Offen bei beiden:
* **Lange Drahtantenne an BNC (5 bis 10 m):** Kapazität deutlich über der Teleskopantenne, Filter verstimmt. Dämpfung oder getrennter Anschluss prüfen.
* **Umschaltung per GPO1:** Ob der Chip den Ausgang per Befehl schaltet und wie er sich beim Reset verhält (GPO1 muss beim Reset high sein, Busmodus), steht im Programming Guide AN332. Das Dokument liegt im Projekt nicht vor.
* **FM-Anpassung:** Rev A 1 nF und 56 nH, AN383 Abschnitt 10: 18 pF und 180 nH, Mikroe: 270 nH. Im Test vergleichen.

## 4. Stecker J1 (Rev B, Vorschlag)

Bestehende Pins 1 bis 9 bleiben wie bei Rev A, damit Rev A und Rev B auf derselben Hauptplatine und demselben Breadboard laufen. Pins 10 bis 13 sind neu und auf dem RX-Board unbeschaltet.

| Pin | Signal | Bemerkung |
|---|---|---|
| 1 | AUDIO_L | |
| 2 | AUDIO_R | |
| 3 | GND | |
| 4 | 3V3 | aus dem LDO |
| 5 | SDA | |
| 6 | SCL | |
| 7 | RST | |
| 8 | INT | GPO2/INTB, optional |
| 9 | GND | |
| 10 | I2S_BCLK | Reserve (Wellenjäger), hier unbeschaltet |
| 11 | I2S_WS | Reserve |
| 12 | I2S_DIN | Reserve |
| 13 | I2S_DOUT | Reserve |

Die endgültige Belegung der Reservepins richtet sich nach dem Pinplan der Hauptplatine. Die freien GPIOs des ESP32-S3 (N16R8) müssen dafür reichen, das prüft das Pflichtenheft der Hauptplatine. Eine Verlängerung auf 1x13 gegenüber Rev A ändert die Hauptplatinen-Buchsenleiste von 1x9 auf 1x13.

## 5. Rev A: Tests, die Rev B festlegen

Rev A kommt bald an. Diese Tests entscheiden die offenen Punkte von Rev B.

| Nr | Test | Entscheidet über |
|---|---|---|
| P1 | Chip auslesen (POWER_UP mit Teilenummer), I2C-Adresse 0x11, Quarz läuft | Grundfunktion |
| P2 | UKW abstimmen mit Teleskop an J2, Empfangsqualität | FM-Anpassung (56 nH) |
| P3 | MW und LW abstimmen mit Ferritstab an J3 | Ferritstab, AM-Pfad |
| P4 | **KW über J2 (FMI):** Teleskop und 5 m Draht, abends auf 49 m, 31 m, 25 m, 19 m | Variante A |
| P5 | **KW über J3 (AMI):** externe Schaltung nach AN383 (L1 4.7 µH zur Antenne, C3 33 pF in Reihe mit 220 µH oder Ferritstab nach RFGND) | Variante B |
| P6 | Audiopegel an J1, Klirren, Brummen | R7 |
| P7 | Stromaufnahme (UKW, MW, KW) | G1, T5 |
| P8 | Störtest: leerer MW-Kanal, ESP32, Display und Verstärker einzeln zuschalten | G3, T7 |
| P9 | Falltest des gesteckten Boards (nach Breadboard-Stufe) | R15, T10 |

Vorschlag Entscheidungsregel: Die Variante, mit der an einem Abend in mindestens 2 KW-Bändern mindestens 3 Rundfunksender verständlich zu hören sind, bei unveränderter UKW- und MW-Qualität. Bei Gleichstand gewinnt A (weniger Teile). Die Regel ist ein Vorschlag, bitte bestätigen.

## 6. Offene Punkte

| Nr | Punkt | Stand |
|---|---|---|
| Q1 | KW-Eingang FMI oder AMI (Abschnitt 3) | Entscheid nach Rev-A-Test |
| Q2 | GPO1 per Befehl schaltbar, Verhalten beim Reset (AN332 beschaffen) | offen |
| Q3 | FM-Anpassung: 56 nH, 180 nH oder 270 nH | Rev-A-Test P2 |
| Q4 | Belegung der Reservepins I2S in J1 mit dem Pinplan abstimmen | offen, vor Layout der Hauptplatine |
| Q5 | Lange Drahtantenne an BNC: Dämpfung oder getrennter Anschluss | Rev-A-Test P4 und P5 |
| Q6 | Lieferbarkeit beim Hersteller: L1 4.7 µH, Umschalter, ESD-Dioden | vor Bestellung |
| Q7 | Boardgrösse und Lage der Antennenanschlüsse (Rev B) | nach Q1 |
| Q8 | Vollständiges Si4732-A10-Datenblatt fehlt (nur Kurzfassung) | offen |
| Q9 | STATUS.md und rx-board.md des RX-Boards nachführen: Rev A in Fertigung, Aussage "KW über AMI, nicht über FMI" als offen markieren | in PR 10, nach Merge erledigt |

*Copyright FerienBSD aka Marcel Sauder. Doku unter CC-BY-4.0.*
