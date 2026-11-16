# Home-Assistant-Betriebsprüfung, 7. September 2026

> 🇩🇪 **Deutsch** · [🇬🇧 English](HA_VALIDATION.en.md)

Die Gilles-Konfiguration wurde mit Home Assistant 2026.9.1 an der Referenzanlage abgeglichen. Diese Prüfung ergänzt die frühere Registeridentifikation; sie beweist keine neuen Bedeutungen der bisher unbekannten Register.

## Reproduzierbare TCP-Leerlaufgrenze

Eine zusätzliche TCP-Verbindung führte ausschließlich FC03-Lesezugriffe auf REG42 aus. Nach einer gültigen Antwort wurde passiv auf das Schließen durch die Gegenstelle gewartet.

| Versuch | Beobachtung |
|---|---|
| Eine Anfrage, danach keine weitere | Gültige Antwort nach 54,3 ms; Verbindung nach 3,010 s Leerlauf geschlossen |
| Drei Anfragen im Abstand von 2 s über dieselbe Verbindung | Alle beantwortet; Antwortzeiten 76,9 / 29,5 / 11,9 ms |
| Danach keine weiteren Anfragen | Verbindung nach 3,060 s Leerlauf geschlossen |

Der Kontrollversuch zeigt, dass die Verbindung länger als drei Sekunden insgesamt bestehen kann, sofern weitere Lesezugriffe erfolgen. Die Leerlaufgrenze erklärt die Verbindungsabbrüche zwischen den bisher teilweise zehn Sekunden auseinanderliegenden Abfragen. Sie wurde an dieser Installation gemessen und ist keine zugesicherte Eigenschaft aller Firmware-Versionen.

Die aktive HA-Konfiguration liest REG42 nun alle zwei Sekunden; die anderen 39 Intervalle bleiben erhalten. 200 ms Abstand zwischen Anfragen vermeiden unmittelbar aufeinanderfolgende Abfragen. Dieser Abstand allein hatte die Aussetzer nicht beseitigt. Ein separater FC03-Block-Read konnte außerdem alle 80 Register als 40 int32-Werte erfolgreich lesen.

HA warnt allgemein bei Intervallen unter fünf Sekunden. Die gezielte Ausnahme für einen Sensor hält hier die gemessene Leerlaufgrenze ein. Die Warnung wurde nicht unterdrückt. Der Beginn der Nachbeobachtung war 07:46:57 Uhr Europe/Vienna. Im gespeicherten Prüfintervall bis 07:52:02 Uhr waren alle 40 Werte verfügbar und der Phasencode blieb ohne Ausfall auf 0. Die abschließende Sitzungskontrolle bis 07:53:44 Uhr zeigte ebenfalls keine weitere Messlücke. **Das ist eine kurze Funktionsprüfung, kein Langzeitnachweis.**

Messdaten ohne Host-/Zugangsdaten: [ha-validation-2026-09-07.json](../reference/ha-validation-2026-09-07.json).

## HA-Konfiguration und Dashboard

- Das Paket `gilles-derived` wurde wegen des Bindestrichs im Paketnamen verworfen. Die neue Datei heißt `gilles_derived.yaml`.
- Sieben vorhandene Vorlagen prüfen jetzt ihre Eingangsdaten. Ein Ausfall wird nicht mehr als Standby, Normal oder geschlossene Tür interpretiert.
- 23 native Helfer und zwei Zählautomationen wurden angelegt. Die beiden Zeitstempel werden durch native Zustandswechsel aktualisiert; es gibt keine künstlichen Startwerte.
- Nach der Bereinigung existierten alle 69 im Dashboard referenzierten Entitäten. 16 historische Namensabweichungen wurden berücksichtigt. Ein Bild des Dashboards konnte mangels aktivierter Screenshot-Funktion nicht geprüft werden.
- Die 40 Rohsensoren behalten IDs und Registerskalierung. Zähler, Datenabdeckung und echte Betriebszeiten ersetzen nicht belegte Verbrauchs-/Wirkungsgradanzeigen.
- HA-Konfigurationsprüfung erfolgreich; betroffene Integrationen gezielt neu geladen. Statistik-Einheiten der neuen Zähler wurden auf `Starts` bzw. `Vorgänge` abgestimmt und anschließend konsistent validiert.

## Abgrenzung der Retry-Einstellung

Der eigenständige Python-Logger erzeugt pro Lesezyklus eine neue Verbindung und übergibt `retries=1` direkt an PyModbus. Die HA-Integration verwendet dagegen in Version 2026.9.1 intern `retries=3`; ein zusätzlicher YAML-Schlüssel `retries: 1` steuert das nicht. `delay` ist eine Startverzögerung, kein Ersatz für den Abstand zwischen Anfragen. Siehe [HA-Modbus-Quellcode 2026.9.1](https://github.com/home-assistant/core/blob/2026.9.1/homeassistant/components/modbus/__init__.py) und [Modbus-Konfiguration](https://www.home-assistant.io/integrations/modbus/).

Die Skripte verwenden `device_id=`, das seit [PyModbus 3.10](https://pymodbus.readthedocs.io/en/latest/source/api_changes.html#api-changes-3-10-0) den früheren Parameter `slave=` ersetzt. Die Mindestabhängigkeit wurde entsprechend angehoben.

## Offen

Die Anlage war bei dieser Prüfung im kalten Standby. Ein natürlicher Brennzyklus und eine längere Stabilitätsauswertung stehen aus. Insbesondere die Skalierung von REG62 muss erneut mit dem Touch abgeglichen werden: Die frühere Beschreibung und die HA-Skalierung passen bei einer Türbeobachtung nicht eindeutig zusammen. Bis zur synchronisierten Messung bleibt die vorhandene Skalierung erhalten. REG56, REG68 und REG72 behalten ihre unbekannte Semantik; frühere Vermutungen werden nicht zu bestätigten Messgrößen aufgewertet.

## Nachprüfung Betriebsdiagnose

Am 07.09.2026 wurden 35 native Helfer, vier Automationen und 78 Dashboard-Verweise konsistent geprüft. `homeassistant.check_config` war erfolgreich. Die beiden Zähler-Statistikeinheiten sind konfliktfrei. 14 geprüfte Waisen wurden ohne Recorder-Löschung entfernt. Die neue Startdiagnose war im aktuellen Standby noch keinem realen Brennlauf ausgesetzt.


## Nachprüfung der Betriebsdiagnose 0.8.0

Die aktualisierte Diagnose wurde mit Home Assistant 2026.10.2 eingerichtet. Der neue native Ableitungshelfer ist geladen. Die gespeicherten Vorlagen für numerische Rohdaten und Temperaturwarnung, die Diagnoseautomation und das Dashboard wurden zurückgelesen und mit den vorgesehenen Definitionen verglichen. Alle 79 Dashboard-Verweise sind auflösbar; die nicht verfügbare Startphasendauer im Standby ist beabsichtigt. Die betroffenen Gilles-Konfigurationseinträge sind geladen, die Qualitätsanzeige ist aktiv und die Diagnoseautomation eingeschaltet. Die Konfigurationsprüfung wurde erfolgreich ausgeführt.

Die vorhandene zentrale Meldeautomation wurde nicht aktiviert. Warnsensoren können im Dashboard erscheinen; diese Prüfung behauptet keine erfolgreiche Push-Zustellung. Eine Meldungsroute ist getrennt zu prüfen. Es wurde kein Brennzyklus ausgelöst und kein Kesselregister geschrieben.

Die Offline-Konsistenzprüfung besteht mit 40 Rohsensoren, 49 YAML-Entitäten, 36 UI-Definitionen, vier Automationen, 79 Dashboard-Verweisen und fünf Ansichten. Zehn automatisierte Tests prüfen die Kombination aus Startbasis, Gesamtanstieg und Trend, numerische Rohwerte, Rücksetzen der Diagnose und SQL-Ereignisgrenzen. Elf Szenarien wurden zusätzlich im HA-Vorlagenrenderer erfolgreich ausgewertet. Python-Kompilierung und `git diff --check` bestanden. Die Szenarien verwenden synthetische Werte, keine veröffentlichten Betriebsverläufe.

```bash
python3 scripts/validate_config.py
python3 scripts/test_start_diagnostics.py
python3 -m py_compile scripts/test_start_diagnostics.py
```

Eine retrospektive Nachrechnung eines privaten Warmstart-Verlaufs unterdrückt den neuen Hinweis sowohl bei stufenweiser Fortschreibung als auch bei linearer Interpolation der aufgezeichneten Werte. Die Recorder-Änderungshistorie enthält nicht jeden unveränderten Sensorreport; dies ist deshalb eine Prüfung mit zwei Näherungen und keine exakte Wiederholung des HA-Ableitungshelfers. Der Verlauf und seine Betriebszeitpunkte bleiben privat.

Der Protokollvergleich ergab keine neu hinzugekommenen Gilles-Fehler seit der Änderung. Vorhandene ältere Template-Meldungen und die bekannte Warnung zum gezielten Zwei-Sekunden-Abfrageintervall sind kein Nachweis eines neuen Fehlers. Die Abnahme prüft Konfiguration und Diagnoseverhalten; sie ersetzt keine längere Nachbeobachtung natürlicher Brennzyklen. Die Dashboard-Prüfung erfolgte anhand der Konfiguration und Entitäten, nicht anhand eines neu gerenderten Bildschirmbilds.

## Nachprüfung der Betriebsdiagnose 0.9.0

Die Änderungen wurden auf Home Assistant 2026.11.1 eingerichtet. Der neue Minimum-Helfer, die aktualisierte Diagnoseautomation und Warnvorlage sowie beide O₂-Helfer sind vorhanden; die drei betroffenen Konfigurationseinträge sind geladen. Die zurückgelesenen Vorlagen enthalten Diagnoseminimum, Trendhysterese, fünf Minuten Einschaltverzögerung und keine zusätzliche Ausschaltverzögerung. Die Automation behält ihre bisherige Identität und ist eingeschaltet. `homeassistant.check_config` wurde erfolgreich ausgeführt; die Änderungen der UI-Helfer und Automation sind ohne Core-Neustart geladen.

Das gespeicherte Dashboard stimmt mit der vorgesehenen Änderung überein. Alle 83 referenzierten Entitäten sind auflösbar. Bei der Prüfung gab es erwartungsgemäß noch keinen Heizmesswert in der neu angelegten O₂-Quelle und ihrem Minimum; ein Anfangswert wurde nicht erfunden. Die Startphasendauer bleibt außerhalb eines Starts nicht verfügbar. Die aktuelle Qualitätsanzeige ist aktiv und der Temperaturhinweis ausgeschaltet. Der abgefragte begrenzte Ausschnitt des Fehlerprotokolls enthielt keine Gilles-Treffer; dies ist keine vollständige Protokollprüfung. Ein Screenshot wurde angefordert, war wegen der deaktivierten Renderfunktion aber nicht verfügbar.

Die Offline-Konsistenzprüfung besteht mit 40 Rohsensoren, 49 YAML-Entitäten, 39 UI-Definitionen, vier Automationen, 83 Dashboard-Verweisen und fünf portablen Ansichten. 24 automatisierte Tests bestehen: 19 für Diagnose, Resetverhalten und Startzählung sowie fünf für O₂-Phasenfilter, ungültige Daten, Zustandszeitpunkte und Statistik-Konfiguration. Die Tests rendern die ausgelieferten Vorlagen mit synthetischen Daten. Python-Kompilierung und `git diff --check` sind erfolgreich.

```bash
python3 scripts/validate_config.py
python3 -m unittest discover -s scripts -p 'test_*.py'
python3 -m py_compile scripts/test_start_diagnostics.py scripts/test_o2_heating.py
```

Die neue Minimum-Basis wurde zusätzlich gegen private Warmstart-Verläufe nachgerechnet; die zuvor auftretenden Hinweise werden dabei unterdrückt. Diese Nachrechnung ersetzt keine exakte Wiederholung der asynchronen HA-Verarbeitung. Die Ausführung der Einschaltverzögerung, das Altern des Statistikpuffers und ein vollständiger natürlicher Brennzyklus nach der Änderung sind mit den Offline-Tests nicht bestätigt. Es wurden keine Rohsensorzustände für einen Live-Test überschrieben, keine Benachrichtigungen testweise versandt und kein Brennzyklus ausgelöst. Bestehende Rohwerte, ungefiltertes O₂-Minimum und Historien bleiben erhalten.
