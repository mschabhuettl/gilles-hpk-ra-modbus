# Gilles HPK-RA Modbus TCP — Reverse-engineered Register-Map

> 🇩🇪 **Deutsch** (Primärsprache) · [🇬🇧 English](README.en.md)

Community-Projekt zur Dokumentation der Modbus-TCP-Schnittstelle der **Gilles Touch** Steuerung in Gilles-Biomasse-Heizungen (HPK-RA-Serie) — inklusive Home-Assistant-Integration.

> **Stand:** 26 von 40 Registern empirisch verifiziert (✓✓), 8 stark vermutet (✓), 3 mit Werten aber unklarer Semantik (?), 3 wahrscheinlich permanent inaktiv. Summe: 40.

## Hintergrund

Die Gilles HPK-RA Pelletkessel sind mit der **Gilles Touch** Steuerung ausgestattet, die auf einem Sigmatek HZS-Touchpanel mit LASAL II läuft. Modbus TCP ist im Produktprospekt angekündigt („Modbus und/oder BAC-Net kompatibel") und lauscht auf Port 502.

Obwohl Hargassner Gilles 2020 übernommen hat, sind die existierenden HPK-RA-Steuerungen **nicht** kompatibel mit der Hargassner-Modbus-Map (Adressen ≥40287, andere Datentypen). Die Gilles Touch exportiert eine eigene, kleinere Map ab Adresse 0.

**Es gibt keine öffentliche Dokumentation dieser Map.** Dieses Repository ist das Ergebnis von Reverse Engineering an einer realen Installation.

## Was steckt drin

```
.
├── docs/
│   ├── REGISTER_MAP.md      — die eigentliche Register-Tabelle (Herzstück)
│   ├── METHODOLOGY.md       — wie wir reverse engineered haben
│   └── CONTROLLER_INFO.md   — Hintergrund Sigmatek / LASAL II
├── scripts/
│   ├── gilles_logger.py     — langläufiger Change-Detection-Logger mit CSV-Output
│   ├── gilles_snapshot.py   — einmaliger Register-Dump
│   └── requirements.txt
├── home-assistant/
│   ├── modbus.yaml          — HA-Modbus-Integration für alle 40 Register
│   └── dashboard.yaml       — Lovelace-Dashboard
└── reference/
    └── parameter-export-sample.txt — Beispiel LASAL-Parameter-Export
```

Englische Übersetzungen aller Dokumente sind als `*.en.md` parallel verfügbar.

## Was du damit kannst

Mit der HA-Integration auf einen Blick sichtbar:

- **Kesseltemperatur** (Ist & Soll, mit automatischem Tag/Nacht-Wechsel)
- **Abgastemperatur** und **Rücklauftemperatur** (Live)
- **Restsauerstoff (O₂)** und alle Verbrennungs-Parameter
- **Brennzyklus-Phase** als Klartext: Vorlüften, Zündung, Anbrennen, Heizen regeln, Ausbrennen, Auskühlen
- **Drehzahlen Primär/Saugzug** (Sekundär bleibt 0 in dieser Anlagenkonfiguration)
- **Brennraumtür-Zustand** (über StatusBitmap erkannt)
- **Ascheaustragung** läuft gerade ja/nein
- **Betriebsmodus**: Handbetrieb, Puffer/Boiler, Automatik (weitere noch nicht beobachtet)

## Schnellstart

1. **Boiler-IP herausfinden** — am Touch unter Allgemeines → Ethernet
2. **Modbus-Erreichbarkeit prüfen:**
   ```bash
   nc -zv <deine-boiler-ip> 502
   ```
3. **Snapshot ziehen:**
   ```bash
   pip install pymodbus
   python3 scripts/gilles_snapshot.py <deine-boiler-ip>
   ```
4. **Werte mit** [docs/REGISTER_MAP.md](docs/REGISTER_MAP.md) **vergleichen**
5. **HA-Konfiguration einbauen:** Inhalt von `home-assistant/modbus.yaml` in `configuration.yaml` integrieren, IP anpassen, HA neu starten

## Getestet mit

- Gilles HPK-RA Pelletkessel
- Gilles Touch mit LASAL II v5.36.4 (Januar 2024)
- Anlagenkonfiguration: Heizkreis 1, Warmwasser 2, Puffer 3, O2-Sonde vorhanden

Falls du eine andere Gilles-Heizung hast und die Map verifizieren oder ergänzen willst — gerne ein Issue oder einen PR.

## Was NICHT in der Modbus-Map ist

Durch gezielte Tests bestätigt — die folgenden Daten sind **nicht** über Modbus zugänglich:

- Heizkreis-Sollwerte und -Modi (Vorlauf, Raumtemperatur)
- Warmwasser-Modus und -Temperatur (Boiler)
- Pufferspeicher-Temperaturen oben/unten
- Heizkreis-Vorlauftemperaturen
- Bunkertemperatur
- Betriebsstunden / Pelletverbrauch / Anzahl Zündungen
- Brennraumtür-Direktsignal (nur indirekt über StatusBitmap REG[46]=35)
- Konfigurations-Flags

Wenn du diese Werte brauchst: entweder über den Hargassner-Servicepartner eine erweiterte Modbus-Map freischalten lassen, oder über VNC-Screen-Scraping vom Touch.

## Lizenz

MIT — siehe [LICENSE](LICENSE).

## Haftungsausschluss

Dieses Projekt ist nicht mit Gilles oder Hargassner verbunden. Das Reverse Engineering erfolgte ausschließlich **lesend** (keine Modbus-Schreibvorgänge) an einem privat betriebenen Kessel. Keine Garantie für Korrektheit oder Vollständigkeit — Verwendung auf eigene Verantwortung. Das Ändern von Steuerungsparametern via Modbus kann die Verbrennung und Sicherheit beeinflussen; nur Register beschreiben, deren Funktion vollständig verstanden ist.
