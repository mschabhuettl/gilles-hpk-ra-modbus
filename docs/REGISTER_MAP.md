# Gilles Touch Modbus Register-Map

> 🇩🇪 **Deutsch** · [🇬🇧 English](REGISTER_MAP.en.md)

**Letzte Aktualisierung:** 2026-05-20 (v0.3.0 — Brennzyklus beobachtet)
**Steuerungs-Firmware:** LASAL II v5.36.4 (10.01.2024)
**Vertrauensgrade:** ✓✓ = empirisch verifiziert · ✓ = stark vermutet via Werte-Match · ? = unbekannt

## Stand

- **29 von 40 Registern** sicher identifiziert (✓✓)
- **4 weitere** stark vermutet (✓)
- **3 Register** wahrscheinlich permanent inaktiv in dieser Anlagenkonfiguration
- **4 Register** noch komplett unklar (REG[56, 68, 72] + REG[46]-Detailcodes)

## Verbindungsparameter

| Einstellung | Wert |
|---|---|
| Protokoll | Modbus TCP |
| Port | 502 |
| Slave-ID | 1 |
| Function Code | nur 03 (Read Holding Registers) |
| Anzahl Register | 80 (= 40 × int32) |
| Datentyp | int32, High Word zuerst (big-endian) |
| Adress-Basis | 0-indiziert |

**Wichtig:** Alle Werte sind 32-bit Integers, gespeichert über zwei 16-bit Register. Um den logischen Wert N zu lesen, lese die Register an Adresse N×2 und N×2+1 und kombiniere als `(reg[N*2] << 16) | reg[N*2+1]`.

**Bus-Eigenheit:** Die Sigmatek-Modbus-Implementierung schließt die TCP-Verbindung nach jeder Modbus-Exception. Immer eine frische Verbindung nach Fehler aufbauen und `retries=1` setzen (nicht 3, der pymodbus-Default).

## ⚠️ Wichtige Korrektur (v0.3.0)

**REG[62] ist NICHT die Brennraumtür**, sondern **SaugzugIst** (Saugzug-Drehzahl Ist in %). Der Beobachtungsfehler in v0.1.0/v0.2.0 entstand, weil beim Öffnen der Brennraumtür der Saugzug automatisch auf 100% fährt (Sicherheits-Rauchabzug). Beim Brennzyklus zeigte REG[62] dann eindeutig die Werte 71%, 76%, 80% — passend zur Touch-Anzeige des Saugzugs.

Die Brennraumtür selbst ist **nicht direkt** in der Modbus-Map exportiert, sondern nur indirekt über REG[46]=35 erkennbar.

## Register-Tabelle

| Adr. | Name | Typ | Skala | Einheit | Vertrauen | Notizen |
|------|------|-----|-------|---------|-----------|---------|
| 0  | `sProzFoerderSchnecke`     | int32 | ×0.1 | %  | ✓✓ | Förderschneckenleistung (Touch: 40%) |
| 2  | `sPrimaerMax`              | int32 | ×0.1 | %  | ✓✓ | Maximale Primärluft (Touch: 70%) |
| 4  | `sPrimaerMin`              | int32 | ×0.1 | %  | ✓✓ | Minimale Primärluft (Touch: 35%) |
| 6  | `sSekundaerMax`            | int32 | ×0.1 | %  | ✓ | Maximale Sekundärluft |
| 8  | `sSekundaerMin`            | int32 | ×0.1 | %  | ✓ | Minimale Sekundärluft |
| 10 | `sSaugzugMax`              | int32 | ×0.1 | %  | ✓✓ | Maximaler Saugzug |
| 12 | `sSaugzugMin`              | int32 | ×0.1 | %  | ✓ | Minimaler Saugzug |
| 14 | `sO2Max`                   | int32 | ×0.1 | %  | ✓✓ | O₂-Soll-Maximum |
| 16 | `sO2Min`                   | int32 | ×0.1 | %  | ✓✓ | O₂-Soll-Minimum |
| 18 | `sKesselSollTag`           | int32 | ×0.1 | °C | ✓✓ | Kessel-Solltemperatur Tag (Touch: 75°C) |
| 20 | `sAschenaustrDauer`        | int32 | ×0.1 | s  | ✓✓ | Ascheaustragung Dauer (Touch: 30 Sek) |
| 22 | `sAschenaustrPause`        | int32 | ×1   | min| ✓✓ | Ascheaustragung Pause (Touch: 15 Min) |
| 24 | `sStartSekundaer`          | int32 | ×0.1 | %  | ✓ | Sekundär-Startwert |
| 26 | `sZuendEinschub`           | int32 | ×0.1 | s  | ✓✓ | Zündeinschubdauer (Touch: 75 Sek) |
| 28 | `sTempDiffStart`           | int32 | ×0.1 | °C | ✓✓ | Temperaturdifferenz Start (Touch: 5°C) |
| 30 | `sTempDiffStop`            | int32 | ×0.1 | °C | ✓✓ | Temperaturdifferenz Stop (Touch: 3°C) |
| 32 | `sTempDiffTeillast`        | int32 | ×0.1 | °C | ✓ | Temperaturdifferenz Teillast |
| 34 | `sKesselSollNacht`         | int32 | ×0.1 | °C | ✓✓ | Kessel-Solltemperatur Nacht (Touch: 70°C) |
| 36 | `sAbgasTempSollMin`        | int32 | ×0.1 | °C | ✓✓ | Abgastemp-Sollwert Min (Touch: 90°C) |
| 38 | `sAbgasTempMax`            | int32 | ×0.1 | °C | ✓ | Abgastemp-Maximum (240°C) |
| 40 | `sAbgasTempMaxLimit`       | int32 | ×0.1 | °C | ✓ | Abgastemp-Sicherheitslimit (270°C) |
| **42** | **`BrennPhase`**       | int32 | enum | —  | ✓✓ | **Brennzyklus-Phase** (siehe Enum unten) |
| **44** | **`BoilerStatus`**     | int32 | enum | —  | ✓✓ | Kessel-Betriebsmodus (siehe Enum unten) |
| 46 | `StatusBitmap`             | int32 | bitfield | — | ✓ | Anlagen-Zustand: 0=normal, 35=Brennraumtür offen, 61=Puffer/Boiler-Modus |
| **48** | **`KesselTemp_Ist`**   | int32 | ×0.1 | °C | ✓✓ | Kesseltemperatur (live) |
| **50** | **`AbgasTemp_Ist`**    | int32 | ×0.1 | °C | ✓✓ | Abgastemperatur (live; bis 110°C beim Brennen beobachtet) |
| **52** | **`RuecklaufTemp_Ist`**| int32 | ×0.1 | °C | ✓✓ | Rücklauftemperatur (live) |
| **54** | **`O2_Ist`**           | int32 | ×0.1 | %  | ✓✓ | Restsauerstoff (live; 21% bei Brennerstart, ~12% im Vollbetrieb) |
| 56 | `?REG56`                   | int32 | ×0.1 | %? | ? | Sehr kurzer Spike auf 10,3% beim Übergang Heizen→Ausbrennen (30 Sek lang) — Funktion unklar |
| **58** | **`PrimaerIst`**       | int32 | ×0.1 | %  | ✓✓ | **Primärluft Ist (live)** — korreliert exakt mit Touch (63/67/70%) |
| **60** | **`SekundaerIst`**     | int32 | ×0.1 | %  | ✓✓ | **Sekundärluft Ist (live)** — bleibt 0 in dieser Anlage (Touch zeigt durchgehend 0%) |
| **62** | **`SaugzugIst`**       | int32 | ×0.1 | %  | ✓✓ | **Saugzug Ist (live)** — wechselt zwischen 71/72/76/80/100% je nach Phase |
| **64** | **`KesselSoll_Live`**  | int32 | ×0.1 | °C | ✓✓ | Aktiv wirksamer Sollwert (70/75/80°C je nach Modus & Tageszeit) |
| **66** | **`AbgasSoll_Live`**   | int32 | ×0.1 | °C | ✓✓ | Aktiv wirksamer Abgas-Sollwert (90°C Standby / 240°C Brennbetrieb) |
| 68 | `?Zaehler`                 | int32 | ?    | ?  | ? | Steigt während Heizphase von 500 auf 600 in unregelmäßigen Schritten — vermutlich Pellet- oder Brennzeit-Zähler |
| 70 | `?`                        | int32 | ?    | ?  | ? | In allen Beobachtungen 0 |
| 72 | `?BinarFlag`               | int32 | bool | —  | ? | Binär 0/1, wechselt während Brennzyklus — vermutlich Zellenrad-Status |
| 74 | `?`                        | int32 | ?    | ?  | ? | In allen Beobachtungen 0 |
| 76 | `?`                        | int32 | ?    | ?  | ? | In allen Beobachtungen 0 |
| **78** | **`AscheaustragungAktiv`** | int32 | bool | — | ✓✓ | **Ascheaustragung läuft** (1=aktiv, 0=Pause) — 30-Sek-Spike entspricht exakt `sAschenaustrDauer` |

## Enum: `BrennPhase` (REG[42])

Aus einem vollständig beobachteten Brennzyklus abgeleitet:

| Code | Phase | Touch-Anzeige | Typische Werte zum Zeitpunkt |
|------|-------|---------------|------------------------------|
| 0 | Standby / kein Brenner | — | alle Drehzahlen 0 |
| 1 | Vorlüften | „Vorlüften 173" | Saugzug 80%, sonst 0 |
| 3 | Zündung | „Zündung 589" | Primär 70%, Saugzug 80-100%, O₂ steigt auf 21% |
| 5 | Spät-Zündung / Übergang | (zwischen 3 und 6) | Saugzug 100%, O₂ noch ~21% |
| 6 | Anbrennphase | „Anbrennphase 34" | Saugzug 80%, Abgas steigt schnell |
| 7 | Heizen regeln (Volllast) | „Heizen regeln" | Primär 63%, Saugzug 71%, O₂ 12-14%, Abgas 100+°C, REG[66] springt auf 240°C |
| 8 | Ausbrennen | „Ausbrennen" | Primär+Saugzug noch laufend, Abgas fällt |
| 9 | Nachlauf / Auskühlphase | (nach Brenner aus) | nur noch Lüfter-Nachlauf |

Die Codes 2 und 4 wurden bisher nicht beobachtet — vermutlich weitere Sub-Phasen.

## Enum: `BoilerStatus` (REG[44])

Das Drop-Down am Touch zeigt 7 Modi (Steuerung Aus, Handbetrieb, Zeitbetrieb, Puffer/Boiler, Puffer/Boiler Gluterhaltung, Automatik, Notbetrieb). Davon sind 3 verifiziert:

| Code | Modus | Touch-Anzeige | KesselSoll_Live (REG[64]) |
|------|-------|---------------|---------------------------|
| 1 | Handbetrieb | „Handbetrieb" | Tag 75°C / Nacht 70°C |
| 3 | Puffer/Boiler | „Puffer/Boiler" | **80°C** (= Puffer-Lade-Sollwert) |
| 5 | Automatik | „Automatik" | Tag 75°C / Nacht 70°C |
| ? | Steuerung Aus | noch nicht beobachtet | — |
| ? | Zeitbetrieb | noch nicht beobachtet | — |
| ? | Puffer/Boiler Gluterhaltung | noch nicht beobachtet | — |
| ? | Notbetrieb | noch nicht beobachtet | — |

## Enum: `KesselSoll_Live` (REG[64])

Aktiv wirksamer Sollwert. Wechselt je nach Modus und Tageszeit:

| Wert | Bedeutung |
|------|-----------|
| 70,0°C | Nacht-Profil aktiv (= REG[34] sKesselSollNacht) |
| 75,0°C | Tag-Profil aktiv (= REG[18] sKesselSollTag) |
| 80,0°C | Puffer-Lade-Sollwert (in BoilerStatus=3) |
| 0,0°C | Modus deaktiviert |

## Verifizierte Test-Events

In chronologischer Reihenfolge der Beobachtungen:

| Aktion | Modbus-Reaktion |
|--------|-----------------|
| Wechsel auf Puffer/Boiler-Modus | REG[44]: 1→3 · REG[46]: 0→61 · REG[64]: 75→0°C |
| Automatischer Tag→Nacht-Wechsel (Absenkbetrieb-Beginn) | REG[64]: 75,0°C → 70,0°C |
| Automatische Ascheaustragung | REG[78]: 0→1 (genau 30 Sek = sAschenaustrDauer), dann zurück auf 0 |
| Wechsel Handbetrieb → Puffer/Boiler vor Brennzyklus | REG[44]: 1→3, REG[64]: 70→80°C |
| Brenner startet (Vorlüften) | REG[42]: 0→1, REG[62]: 0→80% (Saugzug) |
| Zündung beginnt | REG[42]: 1→3, REG[54]: 1→21% (O2 ↑ wegen Frischluft) |
| Brennraumtür wird geöffnet während Zündung | REG[46]: 0→35, REG[62]: 80→100 (Saugzug-Notlauf) |
| Anbrennphase | REG[42]: 5→6, REG[58]: 0→70 (Primärluft) |
| Heizen regeln (Volllast) | REG[42]: 6→7, REG[50]: ~30→105°C, REG[66]: 90→240°C, REG[68]: 0→500 |
| Brenner-Stopp eingeleitet | REG[44]: 3→1, REG[42]: 7→8 (Ausbrennen) |
| Auskühlphase | REG[42]: 8→9 |

## Was definitiv NICHT in der Map ist

Durch gezielte Tests bestätigt — alle folgenden Änderungen am Touch lösten **keine** Modbus-Reaktion aus:

- Heizkreis-Sollwerte (Vorlauf/Raum) — Touch zeigt HK1 28°C, HK4 27°C
- Warmwasser-Modus und -Temperatur — Touch zeigt WW 56°C
- Pufferspeicher-Temperaturen oben/unten — Touch zeigt 48/39°C
- Bunkertemperatur
- Betriebsstunden, Anzahl Zündungen
- Brennraumtür-Direktsignal (nur indirekt über REG[46]=35)
- Konfig-Flags (Externe Freigabe, Zündeinschub getaktet, E-Mail vorhanden, …)
- HZS-Erweiterungsmodule (alle 48 als „not defined" konfiguriert)

## Offene Fragen

1. Was ist **REG[56]**? Nur ein 30-Sekunden-Spike auf 10,3% beim Übergang Phase 7→8 — eine kurz aktivierte Pumpe oder ein Aktor?
2. Was ist **REG[68]**? Steigt während Heizphase von 500 auf 600. Pellet-Eingabe-Zähler? Brennzeit-Counter?
3. Was ist **REG[72]**? Binäres Flag, mehrfach toggelnd pro Brennzyklus. Vermutlich Zellenrad-Status (am Touch als Quadrat angezeigt).
4. Vollständige `BrennPhase`-Codes (REG[42]) — Code 2 und 4 fehlen.
5. Vollständige `BoilerStatus`-Codes (REG[44]) — 4 von 7 Modi noch nicht beobachtet.
6. Vollständiges Bitfeld-Schema von REG[46] — weitere Codes für andere Anlagen-Zustände.

## Wahrscheinlich permanent inaktiv

Die folgenden Register zeigten in **keiner** Beobachtung jemals einen Wert ≠ 0 — auch nicht während des vollständigen Brennzyklus:

- **REG[70]**, **REG[74]**, **REG[76]**

Vermutlich für HZS-Erweiterungsmodule oder andere Subsysteme reserviert, die diese Installation nicht hat (Kaskadenmaster, Mischer, Fernwärme). Werden voraussichtlich nie aktiv werden — außer bei einer Erweiterung der Anlagenkonfiguration.
