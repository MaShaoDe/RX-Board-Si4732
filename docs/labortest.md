# Labortest-Plan RX-Board Rev A

Ziel: Chip, Quarz, FM und MW/LW der ersten Platinen prüfen und die Startwerte (L1, BAV99, Quarzlast) bewerten. Quellen: AN332 (Befehle), AN383 (Antennen). Alle Befehlswerte vor dem ersten Einsatz gegen AN332 prüfen.

## 1. Material

* RX-Board Rev A mit eingelöteter Stiftleiste J1 (1x9)
* Mikrocontroller mit 3.3 V Logik (Pico, ESP32, Arduino 3.3 V). 5 V Logik nur mit Pegelwandler, der Chip verträgt maximal 3.6 V.
* Stromversorgung 3.3 V mit Strombegrenzung (50 mA)
* Multimeter, Oszilloskop (optional), Kopfhörer oder Aktivlautsprecher
* FM: Draht 75 cm oder Teleskopantenne an J2. AM: Ferritstab 180 bis 450 µH an J3.

## 2. Anschluss J1

| Pin | Signal | Anschluss |
|---|---|---|
| 1 | AUDIO_L | Verstärker oder Kopfhörer links |
| 2 | AUDIO_R | Verstärker oder Kopfhörer rechts |
| 3 | GND | GND |
| 4 | 3V3 | 3.3 V |
| 5 | SDA | I2C Daten |
| 6 | SCL | I2C Takt |
| 7 | RST | Ausgang des Mikrocontrollers (Reset, aktiv Low) |
| 8 | INT | im ersten Test offen lassen |
| 9 | GND | GND |

Auf dem Board: Pull-ups 4.7 kΩ für SDA, SCL und RST nach 3V3. SENB liegt über 20 kΩ auf GND, damit ist die I2C-Adresse 0x11.

Messpunkte: TP1 3V3, TP2 GND, TP3 SDA, TP4 SCL, TP5 AUDIO_L, TP6 AUDIO_R, TP7 RST.

## 3. Teststufen

**Stufe 0, ohne Spannung**
* Sichtprüfung: Pin 1 von U1 (Dreieck im Siebdruck), D1, D2, Lötstellen der Stiftleiste.
* Widerstand zwischen 3V3 und GND messen. Kein Kurzschluss.

**Stufe 1, Spannung**
* 3.3 V anlegen, Strombegrenzung 50 mA. Strom vor dem ersten Befehl klein (Richtwert unter 10 mA). Bei hohem Strom sofort trennen und auf Kurzschluss und Lötbrücken prüfen.
* TP3, TP4, TP7 zeigen etwa 3.3 V.

**Stufe 2, I2C-Scan**
* RST kurz auf Low, dann High. Scan über SDA und SCL. Erwartet: Adresse 0x11.
* Keine Antwort: Reset-Folge, Verdrahtung, Pull-ups (TP3, TP4 bei 3.3 V) und Lötstellen von U1 prüfen.

**Stufe 3, Chip-Test**
* POWER_UP (Befehl 0x01) mit FUNC = 15 (Query Library ID, OPMODE laut AN332). Die Antwort enthält Teilenummer und Firmware. Si4732-A10 hat dieselbe Firmware wie Si4735-D60.
* Prüfen, dass das Fehlerbit im Status nicht gesetzt ist.

**Stufe 4, Quarzstart und FM**
* POWER_UP FM-Empfang: XOSCEN = 1, FUNC = 0, OPMODE = 0x05 (analoger Ausgang). Danach mindestens 500 ms warten.
* Lautstärke setzen (Property RX_VOLUME), FM_TUNE_FREQ auf einen starken Sender (Einheit 10 kHz, 101.30 MHz = 10130). FM_TUNE_STATUS lesen: RSSI und SNR notieren.
* Ton an TP5 und TP6 messen oder am Kopfhörer hören.
* Läuft der Quarz nicht (keine Antwort nach POWER_UP), RCLK mit hochohmigem Tastkopf prüfen. Ein 10 MΩ Tastkopf belastet den Quarz weniger als ein 1 MΩ Tastkopf.

**Stufe 5, MW und LW**
* POWER_UP AM-Empfang: XOSCEN = 1, FUNC = 1, OPMODE = 0x05. AM_TUNE_FREQ in kHz (Mittelwelle 531 bis 1602 kHz).
* In der Schweiz sind kaum noch Mittelwellensender aktiv. Test abends mit ausländischen Sendern oder mit einem Signalgenerator und Schleifenantenne.
* Ferritstab weit weg von der Platine halten, Abstand zu Digitalleitungen.

## 4. Abgleich (Startwerte prüfen)

Messen bei gleichem Sender und gleicher Antennenlage, jeweils RSSI und SNR notieren.

| Versuch | Änderung | RSSI | SNR | Bemerkung |
|---|---|---|---|---|
| A | Aufbau wie bestückt (L1 56 nH) | | | |
| B | L1 gegen 270 nH tauschen (Wert des Mikroe-Clicks) | | | |
| C | D1 entfernen (BAV99 hat etwa 1.5 pF, AN383 nennt höchstens 1 pF) | | | |
| D | C2 und C3 von 22 pF auf 18 pF, falls Quarz zu tief läuft | | | |

Ziel: Die beste Kombination als Wert für Rev B festhalten.

## 5. Fehlersuche

| Symptom | Prüfen |
|---|---|
| Strom zu hoch | Lötbrücken an U1, Kurzschluss an C1 oder C4, Pin 1 von U1 verdreht |
| Keine I2C-Antwort | Reset-Folge, SDA und SCL vertauscht, Pegel 3.3 V, Lötstellen |
| Antwort, aber kein Ton | Lautstärke, Stummschaltung, Property RX_VOLUME, Koppelkondensatoren C5 und C6 |
| Kein Sender | Antenne an J2, FM_TUNE_STATUS Valid-Bit, Quarz läuft, 500 ms Wartezeit eingehalten |
| Rauschen | Netzteil, GND-Verbindung, USB-Störungen, Abstand zu digitalen Leitungen |

## 6. Ergebnisse

Messwerte und Beobachtungen hier ergänzen und in die Rev-B-Liste (docs/rx-board.md, offene Punkte) übernehmen.
