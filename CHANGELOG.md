# Changelog

> 🇩🇪 **Deutsch** · [🇬🇧 English](CHANGELOG.en.md)

Alle nennenswerten Erkenntnisse während des Reverse Engineerings der Gilles-Touch-Modbus-Map.

## [0.3.0] — 2026-05-20 — Brennzyklus beobachtet

Vollständiger Brennzyklus (Vorlüften → Zündung → Anbrennphase → Heizen regeln → Ausbrennen → Auskühlphase) wurde mit synchronisierten Touch-Screenshots und Modbus-Logging beobachtet. Damit konnte fast die gesamte Map bestimmt werden.

### Neu verifiziert (✓✓)

- **REG[42]** `BrennPhase` — Brennzyklus-Phase als Enum mit Codes 0/1/3/5/6/7/8/9 (vorher: „immer 0")
- **REG[58]** `PrimaerIst` — Primärluft Ist live (vorher: vermutet REG[56], war falsch)
- **REG[60]** `SekundaerIst` — Sekundärluft Ist live (vorher: vermutet, jetzt bestätigt — in dieser Anlage immer 0%)
- **REG[62]** `SaugzugIst` — **WICHTIGE KORREKTUR**: Saugzug Ist, NICHT Brennraumtür (siehe unten)
- **REG[66]** `AbgasSoll_Live` — aktiver Abgas-Sollwert: 90°C standby / 240°C Brennbetrieb
- **REG[78]** `AscheaustragungAktiv` — Ascheaustragung läuft (1=aktiv, 0=Pause), 30-Sek-Spike entspricht exakt `sAschenaustrDauer`

### Erweitert

- **REG[44]** BoilerStatus: neuer Code **5 = Automatik** identifiziert. Touch-Dropdown zeigt 7 mögliche Modi (siehe REGISTER_MAP); 3 davon jetzt verifiziert.
- **REG[64]** KesselSoll_Live: dritter Wert **80°C** in BoilerStatus=3 (Puffer-Lade-Sollwert). Bisher bekannt: 70°C Nacht / 75°C Tag / 0°C deaktiviert / **neu**: 80°C Puffer.

### Korrektur (Breaking Change in der Map-Semantik)

**REG[62] ist NICHT die Brennraumtür.** Die Beobachtung in v0.2.0 („Tür auf → REG[62]=100") war Zufall: beim Öffnen der Brennraumtür fährt der Saugzug automatisch auf 100% (Sicherheits-Rauchabzug). Während des Brennzyklus zeigte REG[62] eindeutig die Saugzug-Werte (71%, 76%, 80%, 100%) — passend zur Touch-Anzeige.

Die Brennraumtür selbst ist **nicht direkt** in der Modbus-Map exportiert, sondern nur indirekt über REG[46]=35 erkennbar.

**Konsequenzen für bestehende HA-Integrationen:**
- Sensor `sensor.gilles_brennraumtur_raw` wurde umbenannt zu `sensor.gilles_saugzug_ist`
- Binary sensor `binary_sensor.gilles_brennraumtur` basiert jetzt auf REG[46]=35 statt REG[62]>0
- Bisheriger Sensor für Saugzug-Ist (REG[60]) ist jetzt korrekt als `sensor.gilles_sekundaer_ist`

### Teilweise verstanden

- **REG[56]** — Kurzer 30-Sekunden-Spike auf 103 (= 10,3%?) beim Übergang Heizen→Ausbrennen. Funktion unklar.
- **REG[68]** — Steigt während Heizphase von 500 auf 600 in unregelmäßigen Schritten. Vermutlich ein Pellet- oder Brennzeit-Zähler.
- **REG[72]** — Binäres Flag (0/1), toggelt mehrfach pro Brennzyklus. Vermutlich Zellenrad-Status (am Touch als farbiges Quadrat sichtbar).

### Werkzeug-Updates

- Logger v3.1: aktualisierte Labels mit Brennphasen-Enum, Klartext für REG[44]-Codes (Handbetrieb/Puffer-Boiler/Automatik), korrigierte Register-Zuordnungen
- HA modbus.yaml: alle 5 betroffenen Sensoren umbenannt + neue Template-Sensoren für Brennphase-Klartext

## [0.2.0] — 2026-05-20 — Erweiterte Identifikation

### Neu verifizierte Register

- **REG[20]** `sAschenaustrDauer` (Ascheaustragung Dauer, 30 Sek)
- **REG[50]** `AbgasTemp_Ist` — Abgastemperatur live (Korrektur)
- **REG[52]** `RuecklaufTemp_Ist` — Rücklauftemperatur live (Korrektur)

### REG[64] zusätzlich verifiziert

Beobachtet wurde ein automatischer Wechsel von 75,0°C → 70,0°C exakt am Übergangspunkt vom Tag- in den Nacht-Sollwert — passt zur am Touch konfigurierten Absenkbetrieb-Periode.

### Negativ verifiziert

Folgendes wurde durch direkte Tests als **nicht in der Map** bestätigt:
- Heizkreis-Sollwerte, Warmwasser-Modi, Pufferspeicher-Temperaturen
- Boolean-Konfigurationsflags
- HZS-Erweiterungsmodule (alle 48 als „not defined" konfiguriert)

### Neue Werkzeuge

- `gilles_logger.py` v3 mit Klartext-Anzeige, Rauschfilterung, CSV-Ausgabe

### Bilinguale Dokumentation

- Alle Dokumente in Deutsch (primär) und Englisch (`*.en.md`) parallel verfügbar

## [0.1.0] — 2026-05-19 — Initiale Map

### Bestätigte Register

22 Register inklusive sProzFoerderSchnecke, sPrimaerMax/Min, sSaugzugMax, sO2Max/Min, sKesselSollTag/Nacht, sAschenaustrPause, sZuendEinschub, sTempDiffStart/Stop, sAbgasTempSollMin und Live-Messwerte für Kesseltemperatur und O₂.

### Stark vermutet

REG[6], [8], [12], [24], [32] über Werte-Match.

### Initiale Werkzeuge

- pymodbus-basierter Logger und Snapshot
- HA-Modbus-Integration mit 40 Sensoren
- HA-Lovelace-Dashboard mit Detektivansicht
