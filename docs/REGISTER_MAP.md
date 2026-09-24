# Gilles Touch Modbus Register-Map

> 🇩🇪 **Deutsch** · [🇬🇧 English](REGISTER_MAP.en.md)

**Stand:** Erweiterte passive Auswertung; historische Touch-Zuordnungen mit ausdrücklich offener Unsicherheit
**Steuerungs-Firmware:** LASAL II v5.36.4 (10.01.2024)
**Vertrauensgrade:** ✓✓ = empirisch verifiziert · ✓ = stark vermutet via Werte-Match · ? = unbekannt

## Stand

| Vertrauen | Anzahl | Bedeutung |
|---|---:|---|
| ✓✓ | 25 | Historisch identifiziert; Skalierung von REG58/62 weiterhin zu prüfen |
| ✓ | 9 | Starke Hypothese, jetzt einschließlich REG56 als berechneter O₂-Sollwert |
| ? — Wert ungleich null beobachtet | 4 | REG68, REG72, REG76, REG78 |
| ? — bisher nur null beobachtet | 2 | REG70, REG74; Funktion weiterhin offen |
| **Summe** | **40** | |

Die [anonymisierte Zusammenfassung der Registerbefunde](REGISTER_FINDINGS.md) ersetzt die früheren Aussagen, REG56 zeige nur einen Impuls, REG68 sei ein Zähler, REG76 sei inaktiv und REG78 sei ein verifizierter Aschemotor. Das Vertrauenszeichen beschreibt die Funktionszuordnung, keine pauschale Bestätigung jeder Skalierung oder Firmwarevariante.

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

**Bus-Eigenheiten:** Nach Modbus-Exceptions wurde ein Verbindungsende beobachtet. Zusätzlich schließt die Referenzanlage TCP nach etwa drei Sekunden ohne Anfrage (zweimal gemessen). Der Python-Logger verbindet pro Abfrage neu und setzt `retries=1` direkt am Client. HA 2026.9.1 setzt Wiederholungen dagegen intern; die YAML-Zeile `retries: 1` wirkt dort nicht. REG42 wird in HA alle zwei Sekunden gelesen. [Messung und Konfiguration](HA_VALIDATION.md).

## ⚠️ Wichtige Korrektur (v0.3.0)

**REG[62] ist NICHT die Brennraumtür**, sondern **SaugzugIst** (Saugzug-Drehzahl Ist in %). Der Beobachtungsfehler in v0.1.0/v0.2.0 entstand, weil beim Öffnen der Brennraumtür der Saugzug automatisch auf 100% fährt (Sicherheits-Rauchabzug). Beim Brennzyklus zeigte REG[62] dann eindeutig die Werte 71%, 76%, 80% — passend zur Touch-Anzeige des Saugzugs.

Die Brennraumtür selbst ist **nicht direkt** in der Modbus-Map exportiert, sondern nur indirekt über REG[46]=35 erkennbar.

**Skalierungsprüfung:** Die historischen Funktionszuordnungen von REG58/62 zu Primärluft/Saugzug bleiben bestehen. Die HA-Skalierung ×0,1 passt nicht eindeutig zu den historischen Touch-Zuordnungen und den beobachteten Beziehungen zu den Parametergrenzen. Ein Faktor-10-Anzeigefehler ist möglich, aber nicht bewiesen. Rohwert-Skala ×1 bleibt ein Kandidat. Die HA-Skalierung wird erst nach gleichzeitigem Rohwert-/HA-/Touch-Vergleich geändert; die historischen Prozentangaben unten sind kein neuer Skalierungsnachweis.

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
| 46 | `StatusBitmap` | int32 | enum/bitfield? | — | ✓ | 0/35/61 beobachtet; 35 historisch bei offener Tür. 61 passt zur Touch-Meldung „Puffertemperatur erreicht“; vorläufige Zustandszuordnung, kein exakt synchroner Nachweis. Bitfeldstruktur nicht belegt. |
| **48** | **`KesselTemp_Ist`**   | int32 | ×0.1 | °C | ✓✓ | Kesseltemperatur (live) |
| **50** | **`AbgasTemp_Ist`** | int32 | ×0.1 | °C | ✓✓ | Abgastemperatur (live). |
| **52** | **`RuecklaufTemp_Ist`**| int32 | ×0.1 | °C | ✓✓ | Rücklauftemperatur (live) |
| **54** | **`O2_Ist`**           | int32 | ×0.1 | %  | ✓✓ | Restsauerstoff (live; 21% bei Brennerstart, ~12% im Vollbetrieb) |
| 56 | `?O2Soll_Live` | int32 | ×0.1? | %? | ✓ | Passt im Regelbetrieb eng zu einem abgastemperaturabhängigen O₂-Soll. Parametrisierte Formel und Grenzen in den Registerbefunden; keine Touch-Bestätigung. |
| **58** | **`PrimaerIst`** | int32 | ×0.1 HA; ? real | %? | ✓✓ | Historischer Primärluft-Match. Funktionszuordnung bleibt, Skala offen. |
| **60** | **`SekundaerIst`**     | int32 | ×0.1 | %  | ✓✓ | **Sekundärluft Ist (live)** — bleibt 0 in dieser Anlage (Touch zeigt durchgehend 0%) |
| **62** | **`SaugzugIst`** | int32 | ×0.1 HA; ? real | %? | ✓✓ | Historischer Saugzug-Match. Funktionszuordnung bleibt, Skala offen. |
| **64** | **`KesselSoll_Live`**  | int32 | ×0.1 | °C | ✓✓ | Aktiv wirksamer Sollwert (70/75/80°C je nach Modus & Tageszeit) |
| **66** | **`AbgasSoll_Live`** | int32 | ×0.1 | °C | ✓✓ | Aktiver Abgas-Sollwert; verändert sich auch innerhalb Phase 7. Kein fester Zweizustandswert. |
| 68 | `?REG68` | int32 | ? | ? | ? | Steigt und fällt mit wiederholten Nullintervallen. Stell-/Modulationsgröße als Kandidat; kein monotoner Verbrauchs-/Laufzeitzähler. |
| 70 | `?`                        | int32 | ?    | ?  | ? | In allen Beobachtungen 0 |
| 72 | `?BinaerFlag` | int32 | bool | — | ? | Während Zündung/Anbrennen aktiv; Kandidat für zündungsbezogenen Ausgang. Konkreter Aktor unbekannt. |
| 74 | `?`                        | int32 | ?    | ?  | ? | In allen Beobachtungen 0 |
| 76 | `?BinaerFlag` | int32 | bool | — | ? | Wiederkehrende High-Intervalle beobachtet. Funktion, Periodizität und physische Impulsdauer offen. |
| **78** | **`?BinaerFlag`** | int32 | bool | — | ? | Frühere Asche-Zuordnung wegen eines langen High-Intervalls zurückgenommen. Pumpe/Freigabe als Kandidat; historische HA-IDs bleiben erhalten. |

## Enum: `BrennPhase` (REG[42])

Historische Phasenzuordnung; die vollständige Folge wurde in einer weiteren passiven Beobachtung bestätigt. Code 7 umfasst auch Modulation und belegt daher keine Volllast:

| Code | Phase | Touch-Anzeige | Typische Werte zum Zeitpunkt |
|------|-------|---------------|------------------------------|
| 0 | Standby / kein Brenner | — | alle Drehzahlen 0 |
| 1 | Vorlüften | „Vorlüften 173" | Saugzug 80%, sonst 0 |
| 3 | Zündung | „Zündung 589" | Primär 70%, Saugzug 80-100%, O₂ steigt auf 21% |
| 5 | Spät-Zündung / Übergang | (zwischen 3 und 6) | Saugzug 100%, O₂ noch ~21% |
| 6 | Anbrennphase | „Anbrennphase 34" | Saugzug 80%, Abgas steigt schnell |
| 7 | Heizen regeln (Regelbetrieb) | „Heizen regeln" | Primär 63%, Saugzug 71%, O₂ 12-14%, Abgas 100+°C, REG[66] springt auf 240°C |
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
| Historischer REG78-Impuls | Etwa 30s high; die frühere Asche-Deutung wird durch ein später beobachtetes langes High-Intervall infrage gestellt. Gleiche Dauer allein belegt keinen Aktor. |
| Wechsel Handbetrieb → Puffer/Boiler vor Brennzyklus | REG[44]: 1→3, REG[64]: 70→80°C |
| Brenner startet (Vorlüften) | REG[42]: 0→1, REG[62]: 0→80% (Saugzug) |
| Zündung beginnt | REG[42]: 1→3, REG[54]: 1→21% (O2 ↑ wegen Frischluft) |
| Brennraumtür wird geöffnet während Zündung | REG[46]: 0→35, REG[62]: 80→100 (Saugzug-Notlauf) |
| Anbrennphase | REG[42]: 5→6, REG[58]: 0→70 (Primärluft) |
| Heizen regeln (Regelbetrieb) | REG[42]: 6→7, REG[50]: ~30→105°C, REG[66]: 90→240°C, REG[68]: 0→500 |
| Brenner-Stopp eingeleitet | REG[44]: 3→1, REG[42]: 7→8 (Ausbrennen) |
| Auskühlphase | REG[42]: 8→9 |

## In der getesteten Map nicht identifiziert

Frühere gezielte Touch-Tests ergaben für diese Werte keine zuordenbare Modbus-Änderung. Das dokumentiert eine fehlende Identifikation, keinen Beweis, dass keinerlei Codierung existieren kann:

- Heizkreis-Sollwerte (Vorlauf/Raum) — Touch zeigt HK1 28°C, HK4 27°C
- Warmwasser-Modus und -Temperatur — Touch zeigt WW 56°C
- Pufferspeicher-Temperaturen oben/unten — Touch zeigt 48/39°C
- Bunkertemperatur
- Betriebsstunden, Anzahl Zündungen
- Brennraumtür-Direktsignal (nur indirekt über REG[46]=35)
- Konfig-Flags (Externe Freigabe, Zündeinschub getaktet, E-Mail vorhanden, …)
- HZS-Erweiterungsmodule (alle 48 als „not defined" konfiguriert)

## Offene Fragen

| Register | Nächster benötigter Beleg |
|---|---|
| REG56 | Kandidatenwert gleichzeitig mit O₂-Soll am Touch und den Parameter-Endpunkten vergleichen. |
| REG58/62 | Rohinteger, HA-Wert und Touch-Prozent gleichzeitig ablesen, bevor die Skala geändert wird. |
| REG68 | Touch-Anzeigen für Stellgröße/Leistung/Einschub bei natürlichem Nullintervall und Modulation abgleichen. Keine Verbrauchsberechnung daraus. |
| REG72 | Zündungsausgang am Touch während eines natürlichen Starts abgleichen. |
| REG76 | Ausgang identifizieren; gespeicherte High-Dauer belegt keinen gleich langen Motorlauf. |
| REG78 | Pumpen-/Freigabe-/Asche-Anzeigen bei natürlichem Übergang vergleichen. Nur rohe steigende Flanken zählen, keine bestätigten Aschezyklen. |
| REG42/44/46 | Fehlende Phasen-/Moduscodes und Struktur der Statuscodes bleiben offen; REG46=61 bei wechselnder Touch-Meldung prüfen. |

REG70 und REG74 blieben in der abgefragten Historie null. Das belegt weder dauerhafte Inaktivität noch eine Reservierung für ungenutzte Erweiterungen.
