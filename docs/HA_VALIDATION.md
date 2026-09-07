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
