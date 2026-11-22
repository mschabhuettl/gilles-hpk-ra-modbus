# Home Assistant einrichten und aktualisieren

> 🇩🇪 **Deutsch** · [🇬🇧 English](README.en.md)

Diese Dateien bilden die Gilles-Pakete und die auf **Home Assistant 2026.11.1** aktualisierte Betriebsdiagnose ab. Die ursprünglichen Pakete wurden mit Home Assistant 2026.9.1 geprüft. Der Kesselhost wurde durch `192.0.2.1` ersetzt; interne Konfigurationseintrags- und Automations-IDs wurden aus den portablen Definitionen entfernt.

## Bestandteile

| Datei | Verwendung |
|---|---|
| `modbus.yaml` | HA-Paket: 40 Rohsensoren und sieben Zustandsvorlagen mit Verfügbarkeitsprüfung |
| `gilles_derived.yaml` | HA-Paket: Zeitstempel des letzten direkt beobachteten Starts und der letzten REG78-Einschaltflanke |
| `helpers.json` | Native Helfer und ein SQL-Sensor für HA-Oberfläche bzw. Home Assistant MCP |
| `automations.yaml` | Vier native Zähl-/Diagnoseautomationen; einzeln in der Automationsverwaltung anlegen oder aktualisieren |
| `entity_ids.json` | Verwendete Entity-IDs und Zuordnung zu den YAML-`unique_id` |
| `dashboard.yaml` | Dashboard mit Übersicht, Brenner, Betriebsstatistik, Detektivarbeit und Parametern |

Die JSON-Helferdefinition ist **kein HA-YAML-Paket** und kein `.storage`-Export. Pakete allein erzeugen deshalb noch nicht alle Dashboard-Sensoren.

## Installation

1. Die beiden Paketdateien nach `packages/modbus.yaml` und `packages/gilles_derived.yaml` im HA-Konfigurationsverzeichnis kopieren. Den Beispielhost in `modbus.yaml` ersetzen.
2. Falls noch nicht vorhanden, Pakete in den bestehenden `homeassistant:`-Block einbinden:

   ```yaml
   homeassistant:
     packages: !include_dir_named packages
   ```

   Keine zweite `homeassistant:`-Definition anlegen. Bei `!include_dir_named` ist der Dateiname der Paketname: **Unterstrich verwenden**, nicht `gilles-derived.yaml`.
3. Konfiguration prüfen und laden. Bei einer bestehenden Integration reichen die betreffenden Reloads (`modbus.reload`, `template.reload`); für eine erstmalige Einrichtung nur die von HA benötigten Schritte ausführen.
4. Die Entity-IDs mit `entity_ids.json` vergleichen. HA leitet IDs beim ersten Anlegen aus dem Namen ab und behält sie nach späteren Namensänderungen. Beispielsweise kann eine bestehende Anlage `sensor.gilles_rucklauftemperatur` verwenden, während eine Neuinstallation einen anderen Umlaut-/ASCII-Namen erzeugt. Auch Suffixe wie `_vermutet` können aus der Historie stammen. Auf einer Neuinstallation die IDs an die Referenz anpassen oder alle Verweise entsprechend ersetzen. Auf bestehenden Anlagen IDs und Historien erhalten.
5. Die Helfer aus `helpers.json` **in Listenreihenfolge** anlegen. In HA: Einstellungen → Geräte & Dienste → Helfer. `parameters.helper_type` bestimmt den Helfertyp, `name` den Namen und `config` die Fachfelder. Beim Template-Helfer wählt `next_step_id` Sensor oder Binärsensor; `additional_options.availability` gehört zur Verfügbarkeitsvorlage. Zeitfenster wie `max_age` bzw. `duration` in die entsprechenden Stunden-/Tagesfelder übertragen. Beim Counter stehen `initial`, `step`, `restore` und `icon` direkt unter `parameters`.

   Mit Home Assistant MCP werden die jeweiligen `parameters` nach Lesen der aktuellen Best Practices an das in `tool` angegebene Werkzeug übergeben; ohne `tool` gilt `ha_config_set_helper(action="create", ...)`. Der SQL-Sensor verwendet `ha_set_integration` mit `domain: sql` und wird in der HA-Oberfläche über die SQL-Integration angelegt. `key`, `entity_id` und `tool` sind Referenzmetadaten, keine Create-Argumente. Bei bestehenden Helfern zuerst den vorhandenen Eintrag auflösen und aktualisieren; nicht erneut anlegen. Einheiten `Starts` bzw. `Vorgänge` bereits beim Erstellen setzen.
6. Die vier Automationen aus `automations.yaml` einzeln in der HA-Automationsverwaltung anlegen. Beim Bearbeiten vorhandener Automationen deren Identität beibehalten. Die Datei ersetzt **nicht** die gesamte bestehende `automations.yaml`. Die Automationen schreiben ausschließlich HA-Zähler, Diagnose-Helfer und das Aktivitätenprotokoll; keine Kesselregister.
7. Ein Dashboard erstellen bzw. das bestehende Gilles-Dashboard im Rohkonfigurationseditor mit `dashboard.yaml` aktualisieren. Das dort genannte Einrichtungsdatum gehört zur Referenzanlage; bei einer neuen Installation anpassen. Die Referenz verwendet den URL-Pfad `dashboard-gilles`.

## Migration vom bisherigen Beispiel

Die alte Datei `gilles-derived.yaml` wurde wegen des ungültigen Paketnamens in der Referenzanlage vollständig verworfen. Sie wird durch `gilles_derived.yaml` plus native Helfer und Automationen ersetzt. Die alte Datei aus dem Paketverzeichnis entfernen. Falls sie auf einer anderen Anlage bereits unter einem gültigen Paketnamen aktiv war, die bestehenden Helfer und Zähler zuerst erfassen und migrieren; ein zusätzlicher Satz würde doppelte Entitäten erzeugen.

Die bisherigen 40 Rohsensoren behalten Adresse, Datentyp, Skalierung und `unique_id`. REG42 wird jetzt alle zwei Sekunden gelesen, um die gemessene TCP-Leerlaufgrenze von ungefähr drei Sekunden einzuhalten. Der Hub wartet 200 ms zwischen Anfragen. HA 2026.9.1 setzt PyModbus-Wiederholungen intern auf drei; die frühere YAML-Zeile `retries: 1` hatte darauf keinen Einfluss. Details und Messbeleg: [Betriebsprüfung](../docs/HA_VALIDATION.md).

## Bedeutung der Anzeigen

- Datenverluste werden als nicht verfügbar angezeigt. Fehlende Rohwerte bedeuten nicht Standby, Normalbetrieb oder geschlossene Tür.
- Startzähler und die historisch als Aschezähler benannten Helfer zählen direkt beobachtete Wechsel von `0` auf `1`; Wiederverbindungen zählen nicht als Ereignis. Ein Ereignis innerhalb einer Messlücke kann fehlen. Die Aschezähler zählen REG78-Einschaltflanken; dass jede Flanke genau einer Ascheaustragung entspricht, ist nicht bestätigt.
- Zähler beginnen mit ihrer Einrichtung. Erste Tages-, Wochen- und Monatsperioden sind unvollständig. Zeitstempel bleiben bis zum ersten Ereignis unbekannt. Neue Utility-Meter-Helfer können bis zur ersten Quellenmeldung ebenfalls unbekannt sein; keine künstlichen Starts zum Initialisieren erzeugen.
- Brennzyklus-Zeit umfasst Vorlüften und Nachlauf. Sie ist kein Flammennachweis. Historische Zeiten und Extremwerte verwenden vorhandene Recorder-Daten; die Phasendatenabdeckung macht fehlende Zeit sichtbar.
- Pelletverbrauch und Wirkungsgrad werden ohne zusätzliche Messdaten und Kalibrierung nicht geschätzt. Türerkennung bleibt indirekt. Register mit unklarer Zuordnung oder Skalierung bleiben entsprechend gekennzeichnet.

## Abgleich und Prüfung

Bei jeder weiteren Änderung an Gilles werden Live-Konfiguration, Helfer, Automationen, Dashboard und Dokumentation im selben Arbeitsschritt abgeglichen und auf GitHub aktualisiert; siehe [AGENTS.md](../AGENTS.md).

```bash
python3 -m pip install -r scripts/requirements-dev.txt
python3 scripts/validate_config.py
```

Vor Live-Änderungen die betroffenen HA-Dateien und UI-Konfigurationen sichern. Nach einem Update Konfiguration und Entity-Verweise prüfen, gezielt neu laden und echte Messwerte kontrollieren. Ein syntaktisch gültiges Dashboard ersetzt keine Sichtprüfung; die initiale Prüfung hatte keine Screenshot-Funktion verfügbar.

## Betriebsdiagnose (0.9.0)

Die rollierende Startzählung erfasst direkt aufgezeichnete `0→1`-Übergänge innerhalb der letzten 24 Stunden. Messlücken und Ereignisse außerhalb der Aufzeichnung werden nicht ergänzt. Die einstellbaren Prüfschwellen bleiben mehr als 10 beobachtete Starts/24 h und eine Startphase über 20 Minuten. Es sind keine vom Hersteller bestätigten Fehlergrenzen.

Bei einem gültig beobachteten Start speichert die Diagnose weiterhin die ursprüngliche Kesseltemperatur. Zusätzlich wird `input_number.gilles_kesseltemperatur_diagnoseminimum` mit diesem Wert initialisiert und im beobachteten Zyklus bei niedrigeren gültigen Messwerten nach unten geführt. Der Startwert wird dadurch nicht überschrieben. Bei Warmstarts zählt nun der Wiederanstieg vom erfassten Tiefpunkt, statt erneut die warme Ausgangstemperatur übersteigen zu müssen.

Die Temperaturwarnung benötigt einen direkt beobachteten Start, numerische Eingangswerte, vollständige Rohdaten, eine aktuelle Phase `6` oder `7` und mehr als 30 Minuten seit dem Start. Zusätzlich müssen **beide** Temperaturbedingungen gelten: Der Anstieg gegenüber dem Diagnoseminimum liegt unter dem konfigurierten Mindestanstieg, und der geglättete Temperaturtrend ist zu klein. Zum Einschalten muss der Trend unter `Mindestanstieg / 30 Minuten` liegen; eine bereits aktive Warnung wird bei einem Trend ab `Mindestanstieg / 20 Minuten` aufgehoben. Diese Hysterese vermeidet Umschalten direkt an einer einzelnen Grenze. Alle Einschaltbedingungen müssen fünf Minuten durchgehend gelten (`delay_on`). Sobald die Kriterien nicht mehr gelten, schaltet die Warnung ohne zusätzliche Ausschaltverzögerung aus.

Der native Ableitungshelfer `sensor.gilles_kesseltemperatur_trend_10min` nutzt die Kesseltemperatur, ein Glättungsfenster von zehn Minuten, die Zeiteinheit Minuten und eine Neuberechnung spätestens nach einer Minute (`max_sub_interval`). So fällt ein unveränderter Wert im Trend ab, statt einen alten positiven Anstieg unbegrenzt zu halten. Das Fenster glättet verfügbare Änderungen; es belegt keine lückenlose Kommunikation. Die Diagnose ist kein Flammennachweis, keine Wärmeleistungsmessung und keine allgemeine Stillstandsüberwachung nach bereits erreichtem Mindestanstieg.

Standby, HA-Neustart sowie ein fehlender oder nichtnumerischer Wert aus den 40 Rohsensoren verwerfen die laufende Startdiagnose. Eine Datenrückkehr reaktiviert sie nicht; erst der nächste direkt beobachtete `0→1`-Übergang schafft eine neue Basis. Ausbrennen wird nicht als fehlender Temperaturanstieg bewertet. Nach einer Änderung während eines laufenden Zyklus die Diagnosebasis invalidieren, statt nachträglich einen Start oder ein Minimum zu erfinden.

Bei der Migration zuerst den neuen Minimum-Helfer anlegen, danach Diagnoseautomation und Warnvorlage aktualisieren. Bestehende Starttemperatur-, Zeit- und Zählerhelfer behalten ihre Identität und Historie. Das Diagnoseminimum wird beim nächsten gültigen Start initialisiert; sein vorläufiger Zahlenwert ist ohne aktive Diagnosebasis bedeutungslos.

Die Qualitätsanzeige heißt „40 Messwerte numerisch vorhanden“. Sie prüft numerische Werte, nicht das Alter einer bestätigten Modbus-Antwort. Unveränderte Zustände und ihre HA-Zeitstempel sind kein zuverlässiger Kommunikationsnachweis. Die Registerbeobachtung hält die zuletzt asynchron abgefragten Werte im Aktivitätenprotokoll fest; zur Bestätigung unbekannter Register bleibt ein zeitgleicher Touch-Abgleich erforderlich.

Die Warnsensoren und das Dashboard versenden selbst keine Benachrichtigungen. Eine vorhandene zentrale Meldeautomation muss separat eingeschaltet und ihr Zustellweg geprüft sein. Dieses Paket aktiviert keine fremde Meldeautomation.

Die Nachprüfung natürlicher Brennzyklen bestätigt die laufende Diagnoseminimum-Basis und die aufgezeichnete Startzählung. Ein Betrieb ohne Temperaturwarnung prüft jedoch nicht automatisch die tatsächliche Ausführung ihrer Einschaltverzögerung oder Hysterese. Die beobachteten Fälle und verbleibenden Grenzen stehen im [Prüfbericht](../docs/HA_VALIDATION.md).

## Statistikgrenzen und ungesicherte Register

Die vier Statistikhelfer für Kesselminimum, Kesselmaximum, Abgasmaximum und O₂-Minimum speichern jetzt bis zu **10.000 statt 4.000 Stichproben** bei unverändertem `max_age: 24 h`. Bei häufigen Änderungen kann die Stichprobengrenze ältere Werte vor Ablauf des Zeitfensters verdrängen. Die Beschriftung „24 h“ garantiert daher keine vollständigen 24 Stunden. Bei bestehenden Installationen nur die Option `sampling_size` des jeweiligen Helfers aktualisieren; Entity-ID und Historie erhalten. Nach dem Neuladen `age_coverage_ratio` und `buffer_usage_ratio` erneut prüfen. Ein größerer Puffer ersetzt keine fehlenden Quelldaten.

**O₂-Minimum nur aus der Heizphase:** Die neue Quelle `sensor.gilles_o2_heizbetrieb` übernimmt einen gültigen O₂-Rohwert ausschließlich bei Phase `7` und erst, wenn dessen Zustandsaktualisierung nach Eintritt in diese Phase liegt (`last_updated >= phase.last_changed`). Das verhindert die unmittelbare Übernahme eines gehaltenen Startphasenwerts; ein Zeitstempel ist weiterhin kein unabhängiger Messfrischenachweis. Bei gültigen Eingangsdaten außerhalb Phase `7` liefert die Vorlage `none` und damit `unknown`, keinen Ersatzwert null oder einen gehaltenen letzten Zahlenwert. Bei ungültigen Phasen-/O₂-Daten wird sie `unavailable`.

`sensor.gilles_o2_heizbetrieb_24h_min` wertet nur numerische Quellenwerte aus. `unknown` wird ignoriert, sodass im Standby echte Heizwerte bis zum Ablauf von `max_age: 24 h` im Puffer bleiben. `keep_last_sample: false` verhindert das unbegrenzte Festhalten einer abgelaufenen Stichprobe. Tatsächliche Quellen-Nichtverfügbarkeit wird auch von der Statistik als `unavailable` weitergegeben. Vor der ersten passenden Heizphase oder nach Ablauf aller Stichproben gibt es kein auswertbares Minimum. Das Dashboard kennzeichnet diesen Zustand, statt eine Zahl zu erfinden.

Bei der Migration zuerst die neue Templatequelle, danach die neue Statistik anlegen und das Dashboard auf sie umstellen. Der ungefilterte Rohsensor sowie `sensor.gilles_o2_24h_min` bleiben unverändert erhalten. Die neue Kennzahl wird ab ihrer Einrichtung aufgebaut; keine rückwirkende Bereinigung alter Historie. „O₂ Min/Max“ bei den Parametern bezeichnet Sollwerte bei minimaler/maximaler **Leistung**, keine numerischen Sauerstoffgrenzen; siehe [Herstellerbezug und Registerbefunde](../docs/REGISTER_FINDINGS.md).

**Niedrige Heizwerte bleiben sichtbar:** Auch nach Eintritt in Phase `7` wurden neue niedrige O₂-Werte zusammen mit einem dynamischen Temperaturverlauf aufgezeichnet. Der Zahlenwert allein kennzeichnet keinen Standby- oder Sonden-Aus-Zustand. Solange die vorhandenen Eingangsprüfungen erfüllt sind, bleiben diese Werte im Heizphasen-Minimum enthalten. Es gibt keine zusätzliche Untergrenze, die solche Beobachtungen versteckt. Der Filter prüft numerische Eingänge und Phasenzugehörigkeit; er bestätigt keine physische Messgültigkeit. Die Nachprüfung zeigt außerdem das erwartete Beibehalten im Standby und den Ablauf alter Tiefstwerte. Ein vollständig leerer Puffer nach einer ausreichend langen Heizpause wurde dabei nicht beobachtet.

**Rollierende Startzählung über SQL:** `sensor.gilles_brennstarts_24h` zählt jetzt Zeilen im HA-Recorder, deren Zustand `1` und deren über `old_state_id` verbundener Vorgänger derselben Entität `0` ist. Das Zeitfenster lautet `now() - 24 h < last_updated_ts <= now()`. Ein Zustand `1`, der schon vor Fensterbeginn besteht, zählt nicht erneut. Übergänge von `unavailable` oder `unknown` zu `1` zählen ebenfalls nicht. Der alte Statistikhelfer mit `sum_differences_nonnegative` unterschätzte seltene Starts, wenn der vorangehende Zählerstand aus seinem Puffer fiel; dieser Helfer wird nicht mehr angelegt.

Die SQL-Integration liest die Standard-Recorder-Datenbank; der portable Eintrag enthält keine Datenbank-Zugangsdaten. Ohne `db_url` verwendet sie die konfigurierte Recorder-Verbindung, auch bei einem externen Backend. Nur für eine bewusst andere Datenbank ist lokal eine eigene Verbindung anzugeben. Die Datenbank muss den Phasensensor aufzeichnen und mindestens das gewählte Zeitfenster samt Vorgängerzeilen aufbewahren. Ausschlüsse, Recorder-Ausfälle oder gelöschte Historie können weiterhin unterzählen. Die Abfrage bildet aufgezeichnete Übergänge ab, keine unbeobachteten physischen Starts. Der angezeigte Wert folgt dem Aktualisierungsintervall der SQL-Integration.

Bei der Migration vorhandene Verweise und die Identität von `sensor.gilles_brennstarts_24h` erhalten. Den bisherigen Statistikhelfer zunächst eindeutig kennzeichnen und den SQL-Sensor prüfen, bevor die alte Definition nach Abhängigkeitsprüfung entfernt wird. Keine Recorder-Historie löschen. Tages-, Wochen-, Monats- und Gesamtzähler weder zurücksetzen noch aus der SQL-Zahl rückwirkend überschreiben.

**REG78 bleibt eine Hypothese:** Längere Aktivintervalle widersprechen der bisherigen Deutung als unmittelbarer Laufzustand der Ascheschnecke. Bestehende IDs mit `asche…` bleiben aus Kompatibilitätsgründen erhalten. Ihre Werte und Zeitstempel stehen für beobachtete REG78-Flanken, nicht für nachgewiesene mechanische Austragungsvorgänge. Weitere anonymisierte Erkenntnisse und offene Touch-Abgleiche stehen in [REGISTER_FINDINGS](../docs/REGISTER_FINDINGS.md).

Die [SQL-Integration](https://www.home-assistant.io/integrations/sql/) führt die neue Startzählung aus. Die Puffer- und Differenzsemantik des früheren Ansatzes steht in der [Statistik-Dokumentation](https://www.home-assistant.io/integrations/statistics/); [History Stats](https://www.home-assistant.io/integrations/history_stats/) zählt Zustandsintervalle mit anderer Grenzsemantik.

## Touch-Abgleich: Sollwerte, Eingänge und Zähler

Die Touch-Ist/Soll-Seite zeigt getrennt „Restsauerstoff – Ist/Soll“, „aktuelle Einschubmenge“, Kessel-/Abgas-Soll und die Gebläse. Sie ist die passende Vergleichsseite für REG56 und den konkreteren REG68-Einschub-Kandidaten. Gleiche Nullwerte im Standby verifizieren weder eine Registerzuordnung noch einen Skalierungsfaktor. Aktuelle Prozentanzeigen bleiben bis zum Nichtnull-Abgleich unverändert; es wird kein neuer bestätigter Sollwert- oder Verbrauchssensor angelegt.

REG64 kann auch bei weiterhin ausgewähltem Puffer/Boiler-Modus null sein. Für den Betriebsmodus REG44 verwenden und nicht aus einem fehlenden aktiven Kessel-Sollwert „Steuerung aus“ ableiten. Thermo-/Motorschutzanzeigen auf den X-Kontaktseiten sind keine Motorlaufanzeigen; die Kontaktpolarität lässt sich nicht aus der Farbe bestimmen. Reinigungszeitparameter allein beweisen keine freigegebene Reinigungsfunktion.

Die Touch-Seite „Laufzeiten“ und „Anzahl Zündungen“ hat keinen belegten gemeinsamen Zähl- oder Rücksetzzeitraum mit den HA-Helfern. Vorhandene HA-Zähler daher weder anhand eines Screenshots überschreiben noch auf den Touch-Wert initialisieren. Die SQL-Startzählung hat weiterhin ausschließlich den oben beschriebenen Recorder-Bezug. Weitere Grenzen und der gezielte Vergleichsablauf stehen in [REGISTER_FINDINGS](../docs/REGISTER_FINDINGS.md).

## Weitere beobachtete Codes und Datenabdeckung

Phase `10` ist als numerischer Zustand zwischen `9` und `0` beobachtet worden; ihre physische Funktion ist ungeklärt. Die Phasenanzeige benennt das ausdrücklich. Brennzyklus-Binärsensor, Zyklusdauer heute/7 Tage, Abdeckung der beobachteten Phasencodes und Diagnoseprotokoll berücksichtigen nun auch `10`. Das bedeutet weder bestätigte Verbrennung noch einen bekannten Aktor. Unbekannte zukünftige Codes bleiben beim Binärsensor unverfügbar; die numerische Rohphase bleibt davon getrennt. Bestehende History-Stats-Helfer behalten ihre IDs und berechnen aus der vorhandenen Rohhistorie neu; alte Zustandsverläufe des Binärsensors werden nicht umgeschrieben.

Die Abdeckungsstatistik zählt die bisher beobachteten Codewerte. Neue numerische Codes können deshalb wie eine Abdeckungslücke wirken, obwohl Daten übertragen werden. Echte `unavailable`-Intervalle separat prüfen; die auf eine Dezimalstelle gerundete Anzeige kann trotz kurzer Ausfälle 100 % erreichen. Auch `age_coverage_ratio` der Extremwertstatistik beschreibt eine Stichproben-Zeitspanne und keinen Nachweis ununterbrochener Kommunikation. Ein konstanter Quellwert kann diese Zeitspanne begrenzen, ohne dass der Puffer voll ist.

Status `43` wird neutral als ungeklärt angezeigt. Er wurde auch im Standby beobachtet und ist weder als Störung noch als eindeutiger Türzustand identifiziert. Die indirekte Türanzeige bleibt bei diesem Code unverfügbar. Status `61` ist nur vorläufig mit „Puffertemperatur erreicht“ verbunden und wird entsprechend beschriftet.

Ein Brennzyklus über Mitternacht erzeugt keinen neuen Start am Folgetag: Der Tageszähler zählt den beobachteten Start am Starttag, die Zyklusdauer wird an der Tagesgrenze aufgeteilt. Die rollierende SQL-Zählung verwendet unabhängig davon ein gleitendes Zeitfenster; es werden keine Starts nachgetragen oder Zähler zurückgesetzt.

