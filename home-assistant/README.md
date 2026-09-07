# Home Assistant einrichten und aktualisieren

> 🇩🇪 **Deutsch** · [🇬🇧 English](README.en.md)

Diese Dateien entsprechen funktional dem am 7. September 2026 geprüften Stand der Referenzanlage mit **Home Assistant 2026.9.1**. Der Kesselhost wurde durch `192.0.2.1` ersetzt; interne Konfigurationseintrags- und Automations-IDs wurden aus den portablen Definitionen entfernt.

## Bestandteile

| Datei | Verwendung |
|---|---|
| `modbus.yaml` | HA-Paket: 40 Rohsensoren und sieben Zustandsvorlagen mit Verfügbarkeitsprüfung |
| `gilles_derived.yaml` | HA-Paket: Zeitstempel des letzten direkt beobachteten Starts und der letzten Ascheaustragung |
| `helpers.json` | 35 native Helfer: Definitionen für die HA-Oberfläche bzw. Home Assistant MCP |
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

   Mit Home Assistant MCP können die jeweiligen `parameters` nach Lesen der aktuellen Best Practices als Argumente an `ha_config_set_helper(action="create", ...)` übergeben werden. `key` und `entity_id` sind Referenzmetadaten, keine Create-Argumente. Bei bestehenden Helfern zuerst den vorhandenen Eintrag auflösen und aktualisieren; nicht erneut anlegen. Einheiten `Starts` bzw. `Vorgänge` bereits beim Erstellen setzen.
6. Die vier Automationen aus `automations.yaml` einzeln in der HA-Automationsverwaltung anlegen. Beim Bearbeiten vorhandener Automationen deren Identität beibehalten. Die Datei ersetzt **nicht** die gesamte bestehende `automations.yaml`. Die Automationen schreiben ausschließlich HA-Zähler, Diagnose-Helfer und das Aktivitätenprotokoll; keine Kesselregister.
7. Ein Dashboard erstellen bzw. das bestehende Gilles-Dashboard im Rohkonfigurationseditor mit `dashboard.yaml` aktualisieren. Das dort genannte Einrichtungsdatum gehört zur Referenzanlage; bei einer neuen Installation anpassen. Die Referenz verwendet den URL-Pfad `dashboard-gilles`.

## Migration vom bisherigen Beispiel

Die alte Datei `gilles-derived.yaml` wurde wegen des ungültigen Paketnamens in der Referenzanlage vollständig verworfen. Sie wird durch `gilles_derived.yaml` plus native Helfer und Automationen ersetzt. Die alte Datei aus dem Paketverzeichnis entfernen. Falls sie auf einer anderen Anlage bereits unter einem gültigen Paketnamen aktiv war, die bestehenden Helfer und Zähler zuerst erfassen und migrieren; ein zusätzlicher Satz würde doppelte Entitäten erzeugen.

Die bisherigen 40 Rohsensoren behalten Adresse, Datentyp, Skalierung und `unique_id`. REG42 wird jetzt alle zwei Sekunden gelesen, um die gemessene TCP-Leerlaufgrenze von ungefähr drei Sekunden einzuhalten. Der Hub wartet 200 ms zwischen Anfragen. HA 2026.9.1 setzt PyModbus-Wiederholungen intern auf drei; die frühere YAML-Zeile `retries: 1` hatte darauf keinen Einfluss. Details und Messbeleg: [Betriebsprüfung](../docs/HA_VALIDATION.md).

## Bedeutung der Anzeigen

- Datenverluste werden als nicht verfügbar angezeigt. Fehlende Rohwerte bedeuten nicht Standby, Normalbetrieb oder geschlossene Tür.
- Start- und Aschezähler zählen direkt beobachtete Wechsel von `0` auf `1`; Wiederverbindungen zählen nicht als Ereignis. Ein Ereignis innerhalb einer Messlücke kann fehlen.
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

## Ergänzte Betriebsdiagnose (0.5.0)

- Die letzten 24 Stunden beobachteter Zähleränderungen dienen als Hinweis auf häufige Starts. Messlücken und Ereignisse außerhalb der Beobachtung werden nicht ergänzt.
- Voreinstellungen: mehr als 10 beobachtete Starts/24 h, Startphase über 20 Minuten, weniger als 2 °C Anstieg nach 30 Minuten im Anbrenn-/Heizbetrieb. Dies sind einstellbare Prüfschwellen, keine vom Hersteller bestätigten Fehlergrenzen.
- Standby und Datenlücken verwerfen den für eine laufende Startdiagnose gespeicherten Beginn. Ausbrennen wird nicht als fehlender Temperaturanstieg bewertet.
- Die Registerbeobachtung speichert Werte mit Zeitpunkt im Aktivitätenprotokoll. Eine zeitgleiche Touch-Anzeige ist weiterhin erforderlich, um unklare Register oder Skalierungen zu bestätigen.
- In der Referenz wurden 14 verwaiste Einträge entfernt: REG20, 42, 46, 50, 52, 58, 60, 62, 64, 66, 68, 72, 78 sowie `gilles_brennraumtur_raw`. Die aktiven, umbenannten Rohsensoren und ihre Messhistorien bleiben erhalten. Andere Installationen müssen ihre Verweise vor einer vergleichbaren Bereinigung selbst prüfen.
