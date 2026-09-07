# Methodik — Wie die Register identifiziert wurden

> 🇩🇪 **Deutsch** · [🇬🇧 English](METHODOLOGY.en.md)

Dieses Dokument beschreibt das Vorgehen beim Reverse Engineering der Gilles-Touch-Modbus-Map. Zweck: Reproduzierbarkeit für andere Gilles-Besitzer und Vorlage für ähnliche Projekte.

## Phase 1 — Erreichbarkeit prüfen

Erstmal überprüfen, ob Modbus TCP überhaupt läuft:

```bash
nmap -p 80,443,502,1502,1954,5900,8080 <boiler-ip>
```

Gefunden:
- 80/tcp — LASAL Remote View Java-Applet (veraltet, läuft in modernen Browsern nicht mehr)
- 502/tcp — Modbus TCP (nmap kennzeichnet es als „mbap")
- 1954/tcp — Sigmatek LASAL Service-Port
- 5900/tcp — VNC für Touch-Screen-Spiegelung

## Phase 2 — Map-Grenzen und Format

Eine simple Python-Schleife mit `pymodbus` versucht Lesen an verschiedenen Startadressen (0, 100, 1000, 30000, 40000). Nur Adresse 0 mit count ≥2 antwortet. Die erste Antwort verrät die Struktur:

```
HR[0]=0, HR[1]=400      ← kombiniert int32 = 400
HR[2]=0, HR[3]=700      ← kombiniert int32 = 700
...
```

Muster: jedes gerade 16-bit-Register ist 0, jedes ungerade hat Daten. Das ist das **klassische Sigmatek-Muster**: alle Werte sind 32-bit Big-Endian-Integers, gespeichert über zwei Register, das High-Word ist immer 0 weil die zugrundeliegenden Werte klein sind.

Die Map endet bei Adresse 78 (= 40 int32-Werte). Lesen ab Adresse 80 oder höher liefert keine Antwort, der Controller schließt die TCP-Verbindung.

## Phase 3 — Querverweis mit Parameter-Export

Die Gilles Touch kann alle Parameter via USB-Stick als `parameter.txt` exportieren. Diese Datei enthält jeden internen LASAL-Parameter mit seinem aktuellen Wert und Namen:

```
LSE_KesselPara_Temp1.sKesselSollTag,750,Temp3_0,...
LSE_KesselPara_Lambda1.sO2Max,85,Prozent_3_1,...
```

Durch Matchen von Werten aus dem Modbus-Dump gegen Werte im Parameter-Export konnten mehrere Register über ihren eindeutigen Wert identifiziert werden:

- REG[14] = 85 → `sO2Max` (eindeutiges 85 in der Parameter-Datei)
- REG[16] = 105 → `sO2Min` (eindeutiges 105)
- REG[38] = 2400 → `sAbgasTempMax` (eindeutiges 2400)

Bei mehrdeutigen Treffern (z.B. mehrere Parameter mit Wert 300) lieferten die Position in der Map und die Gruppierung (Min/Max-Paare nebeneinander) den Kontext.

## Phase 4 — Direktvergleich mit Touch-Anzeige

Screenshots der Touch-Anzeige zeitgleich mit einem Modbus-Snapshot, dann matchen:

- Touch zeigt „Kesseltemp 47°C" → REG[48] = 472 (47,2°C) ✓
- Touch zeigt „O2 Wert 1,0%" → REG[54] = 10 (1,0%) ✓
- Touch zeigt „Kesselsolltemperatur TAG 75°C" → REG[18] = 750 ✓

Das ergab hochsichere Verifikation der Live-Messwert-Register.

## Phase 5 — Live-Korrelation via Zustandsänderungen

Die mächtigste Technik: Jemand vor Ort am Touch führt diskrete Aktionen aus, während ein Logger alle Änderungen mit Zeitstempel aufzeichnet. Dann korrelieren.

Beispiel-Test-Session:

```
T+0  — Wechsel auf Handbetrieb (Baseline)
T+1  — Wechsel auf Puffer/Boiler-Modus
T+3  — Zurück auf Handbetrieb
T+7  — Brennraumtür auf
T+9  — Brennraumtür zu
```

Der Logger zeigte:

```
CHANGE: REG[44]: 1→3 | REG[46]: 0→61 | REG[64]: 75°C→0°C
CHANGE: REG[44]: 3→1 | REG[46]: 61→0 | REG[64]: 0°C→75°C
CHANGE: REG[46]: 0→35 | REG[62]: 0→100
CHANGE: REG[46]: 35→0 | REG[62]: 100→0
```

Diese Korrelationen identifizierten in einer Session **vier neue Register**:
- REG[44] = Kessel-Betriebsmodus (Enum)
- REG[46] = Status-Bitfeld
- REG[62] = (zunächst falsch interpretiert als Brennraumtür — siehe Phase 7)
- REG[64] = Aktiver Live-Sollwert

Dieselbe Session lieferte auch **negative Befunde**: Im Testfenster wurden mehrfach Heizkreis-1-Sollwert und Warmwasser-Modus geändert — **kein Modbus-Register reagierte**.

## Phase 6 — Passive Verifikation über Zeit

Den Logger durchlaufen lassen und schauen, was sich von alleine ändert.

Schlüssel-Beobachtung: **REG[64] wechselte automatisch von 75,0°C auf 70,0°C** — ohne dass jemand am Touch war. Vergleich mit den Touch-Einstellungen ergab: der Absenkbetrieb ist abends bis frühmorgens konfiguriert, und der Wechsel passierte exakt zum Übergangszeitpunkt.

Das verifizierte unabhängig zweimal:
- REG[18] = sKesselSollTag = 75°C
- REG[34] = sKesselSollNacht = 70°C
- REG[64] = aktiver Sollwert, automatisch je nach Tageszeit

## Phase 7 — Aktiver Brennzyklus: der große Wurf

Der Schritt, der die Map fast komplett enthüllte: einen vollständigen Brennzyklus mit aktiver Anlage durchlaufen lassen. Aktionen:

```
T+0   — Modus-Wechsel auf Puffer/Boiler  (löst Brenner-Anforderung aus)
T+8m  — Anlage durchläuft Phasen: Vorlüften → Zündung → Anbrennen → Heizen
T+11m — Modus zurück auf Handbetrieb     (Brenner-Stopp)
T+15m — Anlage durchläuft Auskühlphase
```

In diesen 15 Minuten **bewegten sich plötzlich Register, die vorher 24 Stunden lang 0 waren**:

- **REG[42]** zeigte eine klare Sequenz `0→1→3→5→6→7→8→9` — das ist der **Brennphasen-Zähler**. Touch-Anzeige bestätigte (Vorlüften, Zündung, Anbrennphase, Heizen regeln, Ausbrennen).
- **REG[58]** sprang von 0 auf 70, später auf 63 — Touch zeigte Primärluft 70% bzw. 63%. → **PrimärIst**.
- **REG[62]** zeigte 71/76/80/100% je nach Phase — Touch zeigte Saugzug 71/76/80/100%. → **SaugzugIst**.
- **REG[66]** sprang von 90 auf 240 als das Heizen begann — = REG[38] sAbgasTempMax. → **aktiver Abgas-Sollwert**.
- **REG[64]** nahm den neuen Wert 80°C an im Puffer/Boiler-Modus. → **Puffer-Lade-Sollwert**.
- **REG[44]** zeigte kurz Code 5 als die Anlage in Automatik wechselte. → **Automatik = 5**.
- **REG[78]** zeigte einen 30-Sekunden-Spike während einer nächtlichen Ruhephase. → **Ascheaustragung aktiv** (30 Sek = sAschenaustrDauer).

## Phase 8 — Korrektur falscher Annahmen

Die Brennzyklus-Daten zwangen zu einer **wichtigen Korrektur**:

In v0.2.0 war REG[62] als „Brennraumtür" identifiziert (basierend auf der Beobachtung: Tür auf → REG[62]=100). Im Brennzyklus zeigte REG[62] aber 71%, 76%, 80% — alles **Saugzug-Werte** vom Touch. Die ursprüngliche Beobachtung war **Zufall**: beim Öffnen der Brennraumtür fährt der Saugzug automatisch auf 100% (Sicherheits-Rauchabzug). REG[62]=100 bei offener Tür war also Korrelation, nicht Identität.

**Lehre**: Korrelation ist nicht Identität. Bei Zustandsänderungen mehrere abhängige Größen prüfen, sonst weist man einem Register die falsche Semantik zu. Im Zweifel: weitere Beobachtungen abwarten, in denen die beiden Größen unabhängig variieren.

Die Brennraumtür ist tatsächlich **gar nicht direkt** in der Modbus-Map exportiert — sie ist nur indirekt über REG[46]=35 erkennbar.

## Warum das funktioniert

Modbus hat kein Discovery-Protokoll. Ohne Dokumentation ist der einzige Weg, den Controller in bekannte Zustände zu bringen und zu beobachten, welche Register sich bewegen. Drei Quellen für „bekannte Zustände":

1. **Parameter-Export** (statische Konfiguration) — für Sollwerte und Konstanten
2. **Touch-Anzeige** (Live-Werte) — für aktuelle Messwerte
3. **Owner-gefahrene Test-Sequenzen** — für zustandsabhängige Werte

Jede Quelle deckt verschiedene Register ab; Kombination liefert volle Abdeckung.

Vor allem **Phase 5 (Live-Korrelation)** und **Phase 7 (Brennzyklus)** waren wertmäßig die produktivsten — pro 30-minütiger Test-Session ließen sich oft 4-7 Register identifizieren.

## Werkzeuge

- `pymodbus` (Python-Library) für Roh-Registerzugriff
- Ein Change-Detection-Logger (in `scripts/gilles_logger.py`) — pollt alle 40 Werte alle 10s, gibt Klartext-Ausgabe für Enums, filtert Temperatur-Rauschen, schreibt eine parallele CSV-Datei für spätere Analyse
- Ein One-Shot-Snapshot-Skript (`scripts/gilles_snapshot.py`) — Zustand zu einem bestimmten Moment einfangen
- Geduld und ein kooperativer Kesselbesitzer

## Was noch zu tun ist

Mit dem beobachteten Brennzyklus sind ~82% der Map verstanden. Was noch fehlt:

- **REG[56, 68, 72]** — aktivieren sich nur in bestimmten Phasen, Identifikation braucht weitere Beobachtung mit zeitlich präzisem Touch-Bezug
- **REG[44] BoilerStatus**: noch 4 von 7 Modi nicht beobachtet (Steuerung Aus, Zeitbetrieb, Gluterhaltung, Notbetrieb)
- **REG[42] BrennPhase**: Codes 2 und 4 fehlen
- **REG[46] StatusBitmap**: vollständiges Bitfeld-Schema

Die Register **REG[70, 74, 76]** werden voraussichtlich in dieser Installation für immer 0 bleiben — sie sind vermutlich für Subsysteme reserviert, die diese Anlage nicht hat.

## Phase 9 — Home Assistant und Verbindungslebensdauer (2026-09-07)

Der Abgleich von Repository, HA-Paketen, Entity-Registry und Dashboard deckte verworfene Pakete, historische Namensabweichungen und verdeckte Messausfälle auf. Zwei ausschließlich lesende TCP-Versuche zeigten eine Leerlaufgrenze von ungefähr drei Sekunden; ein Kontrollversuch mit Zwei-Sekunden-Abfragen hielt dieselbe Verbindung darüber hinaus offen. Die Bereinigung und ihre Grenzen sind in [HA_VALIDATION.md](HA_VALIDATION.md) dokumentiert. Sie ersetzt keine neue Brennzyklusbeobachtung und bestätigt keine weitere Registersemantik.
