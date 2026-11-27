# Gilles HPK-RA Modbus TCP — Reverse-engineered Register-Map

> 🇩🇪 **Deutsch** (Primärsprache) · [🇬🇧 English](README.en.md)

Community-Projekt zur Dokumentation der Modbus-TCP-Schnittstelle der **Gilles Touch** Steuerung in Gilles-Biomasse-Heizungen (HPK-RA-Serie) — inklusive Home-Assistant-Integration.

> **Registerstatus:** 25 von 40 Registern historisch verifiziert (✓✓), 9 stark vermutet (✓), 4 mit unklarer Semantik (?), 2 bisher 0. REG56 ist ein starker O₂-Sollwert-Kandidat; die bisher sichere Asche-Zuordnung von REG78 wurde zurückgenommen. Die Skalierung von REG58/60/62 bleibt offen.

## Inoffizielle Schnittstellenspezifikation

Die [Spezifikation 0.1.0](docs/spec/README.md) beschreibt das lesende Modbus-TCP-Profil, alle 40 bekannten logischen Werte, Zustandszuordnungen und offene Skalen. Sie bündelt den Befundstand 0.9.1; diese Ausgabe bestätigt keine neue Registerbedeutung und enthält keine neuen Messungen. Die Dokumentversion wird getrennt von der Projektversion geführt.

[PDF Deutsch](docs/spec/gilles-modbus-spec-v0.1.0-de.pdf) · [PDF English](docs/spec/gilles-modbus-spec-v0.1.0-en.pdf) · [LaTeX-Quellen als ZIP](docs/spec/gilles-modbus-spec-v0.1.0-sources.zip). Beide Sprachfassungen verwenden dieselbe `registers.json`; synthetische Telegramme und Decodervektoren lassen sich offline prüfen. Eigenständige Community-Dokumentation, keine Herstellerfreigabe.

## Anonymisierte Register-Erkenntnisse

[Erkenntnisse und offene Prüfungen](docs/REGISTER_FINDINGS.md): O₂-Sollwert-Hypothese für REG56, nichtmonotones REG68, aktive REG76-Pulse und Widerspruch zur Aschemotor-Deutung von REG78. REG46=61 ist ein Kandidat für die Meldung „Puffertemperatur erreicht“. Die rollierende 24-h-Startzählung verwendet jetzt direkt aufgezeichnete Übergänge `0→1` im Recorder. Die Startdiagnose vergleicht den Wiederanstieg mit dem tiefsten beobachteten Kesselwert seit dem Start; Trendhysterese und Einschaltverzögerung unterdrücken kurze Schwankungen. Eine eigene O₂-Statistik berücksichtigt nur die Heizphase. Die breitere passive Auswertung stützt REG56 weiterhin als O₂-Sollwert-Kandidaten, ohne seine Vertrauensstufe anzuheben. Private Betriebsverläufe und Screenshots werden nicht veröffentlicht.

Die [Nachprüfung natürlicher Brennzyklen](docs/HA_VALIDATION.md) bestätigt die laufende Minimum-Basis, die aufgezeichnete Startzählung und das phasenbezogene O₂-Minimum einschließlich des Ablaufs alter Tiefstwerte. Niedrige O₂-Werte wurden auch innerhalb der Heizphase aufgezeichnet; der Zahlenwert allein kennzeichnet daher keinen Standbyzustand. Die tatsächliche Auslösung der Warnverzögerung bleibt mangels passendem Alarmfall ungeprüft.

## Hintergrund

Die Gilles HPK-RA Pelletkessel sind mit der **Gilles Touch** Steuerung ausgestattet, die auf einem Sigmatek HZS-Touchpanel mit LASAL II läuft. Modbus TCP ist im Produktprospekt angekündigt („Modbus und/oder BAC-Net kompatibel") und lauscht auf Port 502.

Obwohl Hargassner Gilles 2020 übernommen hat, sind die existierenden HPK-RA-Steuerungen **nicht** kompatibel mit der Hargassner-Modbus-Map (Adressen ≥40287, andere Datentypen). Die Gilles Touch exportiert eine eigene, kleinere Map ab Adresse 0.

Während der Untersuchung lag keine passende Hersteller-Registermap vor. Dieses Repository dokumentiert das Reverse Engineering an einer realen Installation.

## Was steckt drin

| Pfad | Inhalt |
|---|---|
| `docs/REGISTER_MAP.md` | Registertabelle und Vertrauensgrade |
| `docs/METHODOLOGY.md` | Vorgehen beim Reverse Engineering |
| `docs/CONTROLLER_INFO.md` | Hintergrund der Steuerung |
| `docs/HA_VALIDATION.md` | HA-Bereinigung, TCP-Leerlaufmessung und offene Prüfungen |
| `home-assistant/` | Pakete, native Helfer, Automationen, Entity-Zuordnung und Dashboard |
| `scripts/` | Logger, Snapshot und Konfigurationsprüfung |
| `reference/` | Parameterbeispiel und bereinigte Prüfbelege |

Englische Übersetzungen aller Dokumente sind als `*.en.md` parallel verfügbar.

## Was du damit kannst

Mit der HA-Integration auf einen Blick sichtbar:

- **Kesseltemperatur** (Ist & Soll, mit automatischem Tag/Nacht-Wechsel)
- **Abgastemperatur** und **Rücklauftemperatur** (Live)
- **Restsauerstoff (O₂)** und die zugeordneten Verbrennungsparameter
- **Brennzyklus-Phase** als Klartext: Vorlüften, Zündung, Anbrennen, Heizen regeln, Ausbrennen, Auskühlen
- **Luft-/Saugzug-Werte** (Skalierungen von REG58/60/62 noch am Touch abgleichen)
- **Indirekter Brennraumtür-Hinweis** (REG46=35 historisch bei offener Tür beobachtet; unbekannte Codes ergeben keine sichere Türposition)
- **REG78-Signal und Einschaltflanken** (bisher als Ascheaustragung bezeichnet; Funktion wieder offen)
- **Betriebsmodus**: Handbetrieb, Puffer/Boiler, Automatik (weitere noch nicht beobachtet)

## Schnellstart

1. **Boiler-IP herausfinden** — am Touch unter Allgemeines → Ethernet
2. **Modbus-Erreichbarkeit prüfen:**
   ```bash
   nc -zv <deine-boiler-ip> 502
   ```
3. **Snapshot ziehen:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   python3 -m pip install -r scripts/requirements.txt
   python3 scripts/gilles_snapshot.py <deine-boiler-ip>
   ```
4. **Werte mit** [docs/REGISTER_MAP.md](docs/REGISTER_MAP.md) **vergleichen**
5. **Home Assistant einrichten/aktualisieren:** [home-assistant/README.md](home-assistant/README.md) erklärt beide Pakete, native Helfer und einen SQL-Sensor, vier Zähl-/Diagnoseautomationen und das Dashboard einschließlich Entity-IDs und Migration.

## Aktueller HA-Stand und Entwicklungsablauf

Die Bereinigung vom 7. September 2026 ergänzt Verfügbarkeitsprüfungen, erfasste Betriebsstatistiken und korrigierte Dashboard-Verweise. An der Referenzsteuerung wurde ein TCP-Leerlaufende nach ungefähr drei Sekunden gemessen; REG42-Abfragen alle zwei Sekunden sind die gezielte Gegenmaßnahme, keine allgemeine Stabilitätsgarantie. Siehe [Messung und Grenzen](docs/HA_VALIDATION.md).

Bei weiteren Gilles-Änderungen werden Konfiguration, deutsche/englische Dokumentation und Changelog im selben Arbeitsschritt aktualisiert und auf GitHub veröffentlicht. Der dauerhafte Arbeitsablauf steht in [AGENTS.md](AGENTS.md).

## Getestet mit

- Home Assistant 2026.11.1 (aktuelle Betriebsdiagnose); ursprüngliche Pakete mit 2026.9.1 geprüft
- Gilles HPK-RA Pelletkessel
- Gilles Touch mit LASAL II v5.36.4 (Januar 2024)
- Anlagenkonfiguration: Heizkreis 1, Warmwasser 2, Puffer 3, O2-Sonde vorhanden

Falls du eine andere Gilles-Heizung hast und die Map verifizieren oder ergänzen willst — gerne ein Issue oder einen PR.

## Noch nicht zugeordnete Größen

Für die folgenden Größen fehlt in der getesteten Map eine belastbare Zuordnung. Das beweist nicht, dass sie grundsätzlich unzugänglich oder nirgends codiert sind:

- Heizkreis-Sollwerte und -Modi (Vorlauf, Raumtemperatur)
- Warmwasser-Modus und -Temperatur (Boiler)
- Pufferspeicher-Temperaturen oben/unten
- Heizkreis-Vorlauftemperaturen
- Bunkertemperatur
- Betriebsstunden / Pelletverbrauch / Anzahl Zündungen
- Brennraumtür-Direktsignal (REG46=35 ist lediglich ein historisch beobachteter indirekter Hinweis)
- Konfigurations-Flags

Weitere Zuordnungen benötigen einen zeitgleichen Vergleich mit der Touch-Anzeige. Ob der Hersteller eine zusätzliche Registermap oder Freischaltung anbietet, ist durch dieses Projekt nicht belegt. Siehe [offene Prüfungen](docs/REGISTER_FINDINGS.md).

## Lizenz

MIT — siehe [LICENSE](LICENSE).

## Haftungsausschluss

Dieses Projekt ist nicht mit Gilles oder Hargassner verbunden. Das Reverse Engineering erfolgte ausschließlich **lesend** (keine Modbus-Schreibvorgänge) an einem privat betriebenen Kessel. Keine Garantie für Korrektheit oder Vollständigkeit — Verwendung auf eigene Verantwortung. Schreibzugriffe sind nicht untersucht und gehören nicht zum dokumentierten Leseprofil.

