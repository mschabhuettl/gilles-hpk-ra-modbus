# Changelog

> 🇩🇪 **Deutsch** · [🇬🇧 English](CHANGELOG.en.md)

Alle nennenswerten Erkenntnisse während des Reverse Engineerings der Gilles-Touch-Modbus-Map.

## [0.7.0] — 2026-09-25 — Weitere Phasen und Statuscodes

REG42-Code `10` und REG46-Code `43` erstmals als beobachtete Codes dokumentiert, beide ohne behauptete physische Bedeutung. Ein weiterer Abschaltpfad enthält `7→9→10→0`; eine sehr kurze unaufgezeichnete Zwischenphase ist durch Polling nicht ausgeschlossen. Code 43 kann bis in den Standby bestehen bleiben und ist nicht mit dem späteren Wegfall des Kessel-Solls gleichzusetzen.

Phase 10 in Phasentext, Brennzyklus-Binärsensor, Zyklusdauer heute/7 Tage, Abdeckung und Diagnoseprotokoll ergänzt. Status 43 bleibt neutral, Status 61 wird als vorläufige Meldungszuordnung markiert. Die indirekte Türanzeige bleibt bei Code 43 unbekannt. Bestehende IDs, Rohskalierungen und Abfrageintervalle bleiben erhalten.

Die O₂-Sollwert-Hypothese für REG56 und der Zündungsbezug von REG72 werden durch einen weiteren Verlauf gestützt. REG76 kann auch im Standby pulsen. Wärmeverschiebungen während REG78-Aktivintervallen stützen Pumpe/Freigabe als Hypothese; die physische Zuordnung bleibt offen. Keine neue Register-Vertrauensstufe vergeben.

Statistikgrenzen präzisiert: erfasste Codes sind nicht dasselbe wie lückenlose Kommunikation, Stichproben-Zeitspanne ist kein Kommunikationsnachweis, und ein über Mitternacht laufender Zyklus ist kein zusätzlicher Tagesstart. Der Fehler der rollierenden 24-h-Startstatistik bleibt offen. Dashboard-Hinweise aktualisiert; konkrete Betriebsverläufe bleiben privat.

Validierung: Repository-Konfigurationsprüfung und Python-Kompilierung bestanden; Phasen- und Statusvorlagen einschließlich unbekannter/nicht verfügbarer Eingaben im HA-Renderer geprüft. Live-Konfigurationsprüfung und Template-Neuladen erfolgreich; Helfer, Beobachtungsautomation und Dashboard zurückgelesen. Keine Änderung an Modbus-Abfragen oder Kesselsteuerung.

## [0.6.1] — 2026-09-24 — Touch-Diagnoseseiten abgeglichen

Zehn bereits zugeordnete Parameter erneut mit Touch und HA verglichen; ihre Skalierungen passen. Die neu identifizierte Ist/Soll-Seite liefert die konkrete Vergleichsanzeige für REG56 (O₂-Soll) und REG68 („aktuelle Einschubmenge“). Übereinstimmende Nullwerte im Standby reichen nicht zur Verifikation; die Vertrauensverteilung bleibt unverändert.

REG64-Dokumentation korrigiert: Ein Nullwert bedeutet nicht automatisch einen ausgeschalteten Betriebsmodus. Kontaktanzeigen, Funktionsfreigaben und tatsächliche Motorzustände werden getrennt; vorhandene Reinigungsparameter bestätigen keinen Reinigungslauf. Rücksetzbereich des Touch-Zündungszählers und Modbus-Adressen der zusätzlich sichtbaren Größen bleiben offen.

Nur anonymisierte Dokumentation ergänzt; keine neuen privaten Parameterwerte, Messstände, Laufzeiten, Bilder oder Betriebszeitpunkte veröffentlicht. HA-Laufzeitkonfiguration und Zähler unverändert.

## [0.6.0] — 2026-09-24 — Anonymisierte Register-Erkenntnisse und Statistikhinweise

Anonymisierte Erkenntnisse und offene Prüfungen in [REGISTER_FINDINGS](docs/REGISTER_FINDINGS.md) ergänzt. Private Messreihen, Betriebszeitpunkte und Screenshots sind nicht Teil der Veröffentlichung.

REG56 passt zu einem aus Abgastemperatur und O₂-Parametern interpolierten Sollwert; bleibt bis zum Touch-Abgleich stark vermutet. REG68 ist nichtmonoton und kein fortlaufender Zähler. REG72 zeigt Zündungsbezug. REG76 kann aktiv sein. Längere Aktivintervalle von REG78 widersprechen seiner bisherigen gesicherten Aschemotor-Zuordnung. REG46=61 ist ein Kandidat für „Puffertemperatur erreicht“, kein allgemeiner Indikator für Betriebsmodus 3. HA-Registerskalierungen und Entity-IDs bleiben erhalten; der Logger kennzeichnet ungesicherte Werte und zeigt REG56 ohne vorweggenommene Prozentumrechnung.

Live-Dashboard und portables Beispiel kennzeichnen offene Bedeutungen und die unzuverlässige 24-h-Startstatistik. Vier Extremwert-Helfer erhalten 10.000 statt 4.000 Stichproben; der Fehler bei seltenen Startzähleränderungen bleibt bis zu einer gesondert validierten Ereigniszählung offen. Bestehendes Diagnoseprotokoll um Modus, REG46, Kessel-Soll, Rücklauf und REG78 erweitert. Die Ascheautomation zählt unverändert beobachtete REG78-Flanken; ihre Beschreibung wurde präzisiert.

HA-Änderungen gespeichert und zurückgelesen; Konfigurationsprüfung ohne neue Konfigurationsfehler im abgefragten Systemlog. Offline-Konsistenzprüfung, Python-Kompilierung und isolierte Prüfung der Logger-Ausgabe ohne Modbus-Verbindung erfolgreich. Keine Kesselregister geschrieben, kein Brennlauf ausgelöst und keine Zähler zurückgesetzt. Die Pflicht zur anonymisierten Veröffentlichung ist in `AGENTS.md` festgehalten.

## [0.5.0] — 2026-09-07 — Betriebsdiagnose und Bereinigung

- 14 verwaiste Registereinträge nach vollständiger Suche in aktiven Helfern, Automationen, Dashboards, YAML und AppDaemon entfernt. Recorder-Historien wurden nicht gelöscht.
- Native Helfer von 23 auf 35 und Automationen von zwei auf vier erweitert. Hinweise für häufige beobachtete Starts, lange Startphase, fehlenden Kesseltemperaturanstieg und unplausible Temperaturen ergänzt; Schwellen sind in HA einstellbar.
- Startdiagnose nur nach direkt beobachtetem Übergang 0→1; Neustart, Standby oder Datenlücke verwerfen die laufende Diagnose. Startphase umfasst Vorlüften und beide Zündphasen. Temperaturvergleich gilt erst nach 30 Minuten in Phase 6 oder 7.
- Registerstände während regulärer Brennläufe werden alle fünf Minuten und bei Phasenwechseln im Aktivitätenprotokoll festgehalten. Ein erneuter synchronisierter Touch-Abgleich ist weiterhin offen; kein Brennlauf wurde ausgelöst und keine Registersemantik geändert.
- Zähler-Statistikeinheiten `Starts` und `Vorgänge` ohne Konflikt geprüft. TCP-Maßnahmen aus 0.4.0 beibehalten; kein neuer Langzeitnachweis behauptet.
- Live-Konfiguration geprüft; Offline-Konsistenzprüfung: 40 Rohsensoren, 49 YAML-Entitäten, 35 Helfer, vier Automationen, 78 Dashboard-Verweise. Neue Brenndiagnosen konnten wegen Standby noch nicht im Brennbetrieb geprüft werden.

## [0.4.0] — 2026-09-07 — Home Assistant abgeglichen

- TCP-Leerlaufgrenze an der Referenzanlage zweimal gemessen: 3,010 bzw. 3,060 Sekunden. REG42 wird in HA nun alle zwei Sekunden gelesen; 200 ms Abstand zwischen einzelnen Anfragen. Die kurze Nachprüfung war lückenlos, ein Langzeitnachweis steht aus.
- Wirkungsloses HA-YAML `retries: 1` entfernt; die Abgrenzung zum eigenständigen Python-Client dokumentiert.
- Sieben Zustandsvorlagen mit Verfügbarkeitsprüfung: Messausfälle werden nicht mehr als Standby/Normal/geschlossene Tür dargestellt.
- Ungültiges Paket `gilles-derived.yaml` durch `gilles_derived.yaml` ersetzt. Native Helfer (23), Zählautomationen (2) und vorhandene Entity-IDs als portable Definitionen ergänzt.
- Dashboard mit 69 aufgelösten Entity-Verweisen abgeglichen; Betriebsstatistiken, Datenabdeckung und beobachtete Starts/Ascheaustragungen ergänzt. Nicht belegte Pelletverbrauchs-, Wirkungsgrad- und Modulationsschätzungen entfernt.
- Bestehende Rohsensor-IDs und Skalierungen erhalten. REG62-Skalierung bleibt bis zum erneuten synchronisierten Touch-Vergleich offen; keine neue Registersemantik behauptet.
- Installations-/Migrationsanleitung und Messbeleg auf Deutsch/Englisch ergänzt. Repository-Abgleich bei jeder Gilles-Änderung als Arbeitsregel in `AGENTS.md` festgehalten.
- Mindestversion für die von den Skripten verwendete `device_id=`-API auf `pymodbus>=3.10.0,<4` korrigiert; lokale Konsistenzprüfung der HA-Beispiele ergänzt.

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
