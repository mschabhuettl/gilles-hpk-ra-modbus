# Methodology — How registers were identified

> [🇩🇪 Deutsch (primary)](METHODOLOGY.md) · 🇬🇧 **English**

This document explains the approach used to reverse-engineer the Gilles Touch Modbus map. The goal is twofold: to make the work reproducible for other Gilles owners and to provide a template for similar projects.

## Phase 1 — Connectivity discovery

Verified that Modbus TCP is actually running on the controller:

```bash
nmap -p 80,443,502,1502,1954,5900,8080 <boiler-ip>
```

Found:
- 80/tcp — LASAL Remote View Java applet (legacy)
- 502/tcp — Modbus TCP (nmap labels it "mbap")
- 1954/tcp — Sigmatek LASAL service port
- 5900/tcp — VNC for Touch screen mirroring

## Phase 2 — Map bounds & format

A naive Python loop with `pymodbus` tried reading at various start addresses (0, 100, 1000, 30000, 40000). Only address 0 with count ≥2 responded. The first response revealed the structure: every even-indexed 16-bit register is 0, every odd has data. **Classic Sigmatek pattern**: all values are 32-bit big-endian integers stored across two registers.

The map ends at address 78 (= 40 int32 values). Reading higher returns no response.

## Phase 3 — Cross-reference with parameter export

The Gilles Touch can export all parameters to USB stick as `parameter.txt`:

```
LSE_KesselPara_Temp1.sKesselSollTag,750,Temp3_0,...
LSE_KesselPara_Lambda1.sO2Max,85,Prozent_3_1,...
```

By matching unique values from the Modbus dump to values in the parameter export, several registers were identified — e.g., REG[14]=85 → `sO2Max` (unique 85 in parameter file).

## Phase 4 — Direct comparison with Touch display

Screenshots of the Touch display alongside a Modbus snapshot, then matched:
- Touch shows "Kesseltemp 47°C" → REG[48] = 472 (47.2°C) ✓
- Touch shows "O2 Wert 1.0%" → REG[54] = 10 (1.0%) ✓

## Phase 5 — Live correlation via state changes

The most powerful technique: have someone at the Touch perform discrete actions while a logger records all changes with timestamps. Then correlate.

Example test session:

```
T+0  — switch to Handbetrieb (baseline)
T+1  — switch to Puffer/Boiler mode
T+3  — switch back to Handbetrieb
T+7  — open combustion chamber door
T+9  — close door
```

The logger showed:

```
CHANGE: REG[44]: 1→3 | REG[46]: 0→61 | REG[64]: 75°C→0°C
CHANGE: REG[46]: 0→35 | REG[62]: 0→100
CHANGE: REG[46]: 35→0 | REG[62]: 100→0
```

These correlations gave us **four new register identifications** in one session, including REG[44], REG[46], REG[64], and (initially mislabeled) REG[62] — see Phase 7.

The same session also produced **negative findings**: heating circuit setpoint and DHW mode changes triggered **no Modbus reaction**.

## Phase 6 — Passive verification over time

Let the logger run and observe what changes on its own.

Key observation: **REG[64] automatically switched from 75.0°C to 70.0°C** — without anyone at the Touch. Comparison with Touch settings showed: the setback period is configured for evenings through early mornings, and the change occurred at the configured boundary.

This independently verified REG[18] (day), REG[34] (night), and REG[64] (active setpoint, auto-switching).

## Phase 7 — Active burner cycle: the big breakthrough

The step that revealed almost the entire map: run a full burner cycle with the boiler active.

```
T+0   — Switch to Puffer/Boiler  (triggers burner demand)
T+8m  — Boiler runs through phases: pre-purge → ignition → initial → heating
T+11m — Switch back to Handbetrieb  (burner stop)
T+15m — Boiler runs through cooldown
```

In these 15 minutes, **registers that had been 0 for 24 hours suddenly came alive**:

- **REG[42]** showed a clear sequence `0→1→3→5→6→7→8→9` — the **burner phase counter**. Touch display confirmed (Vorlüften, Zündung, Anbrennphase, Heizen regeln, Ausbrennen).
- **REG[58]** jumped from 0 to 70, then 63 — Touch showed Primary air 70% / 63%. → **PrimaerIst** (Primary air actual).
- **REG[62]** showed 71/76/80/100% by phase — Touch showed Saugzug 71/76/80/100%. → **SaugzugIst** (Induced draft actual).
- **REG[66]** jumped from 90 to 240 when heating started — equals REG[38] sAbgasTempMax. → **active flue gas setpoint**.
- **REG[64]** took new value 80°C in Puffer/Boiler mode. → **buffer charge setpoint**.
- **REG[44]** briefly showed code 5 when the boiler switched to Automatik. → **Automatik = 5**.
- **REG[78]** showed a 30-second spike during a nighttime idle period. → **Ash discharge active** (30s = sAschenaustrDauer).

## Phase 8 — Correcting wrong assumptions

The burner cycle data forced an **important correction**:

In v0.2.0 REG[62] was identified as "combustion chamber door" (based on the observation: door open → REG[62]=100). But during the burner cycle REG[62] showed 71%, 76%, 80% — all **Saugzug values** from the Touch. The original observation was **coincidental**: opening the combustion door automatically forces the induced draft to 100% (safety smoke extraction). REG[62]=100 with the door open was correlation, not identity.

**Lesson**: Correlation is not identity. When state changes, multiple dependent variables can move together, leading to false semantic assignment. When in doubt: wait for further observations where the two variables vary independently.

The combustion chamber door is in fact **not directly** exported via Modbus — only indirectly visible through REG[46]=35.

## Why this works

Modbus has no discovery protocol. Without documentation, the only way forward is to put the controller into known states and observe which registers move. Three sources of "known state":

1. **Parameter export** (static configuration) — for setpoints and constants
2. **Touch display** (live values) — for current measurements
3. **Owner-performed test sequences** — for state-dependent values

Each source covers different registers; combining them gives full coverage.

**Phase 5 (live correlation)** and **Phase 7 (burner cycle)** were the most productive — typically 4-7 register identifications per 30-minute session.

## Tools

- `pymodbus` (Python library) for raw register access
- A change-detection logger (`scripts/gilles_logger.py`) — polls all 40 values every 10s, plain-text output for enums, noise filtering for temperatures, parallel CSV output
- A one-shot snapshot script (`scripts/gilles_snapshot.py`)
- Patience and a cooperative boiler owner

## What's left to do

With the observed burner cycle, ~82% of the map is understood. Remaining:

- **REG[56, 68, 72]** — activate only during specific phases, identification needs further observation with timestamped Touch reference
- **REG[44] BoilerStatus**: 4 of 7 modes still unobserved (Steuerung Aus, Zeitbetrieb, Gluterhaltung, Notbetrieb)
- **REG[42] BrennPhase**: codes 2 and 4 missing
- **REG[46] StatusBitmap**: full bitfield schema

Registers **REG[70, 74, 76]** will likely stay 0 forever in this installation — reserved for subsystems not present (cascade master, mixers, district heating, additional HZS modules).
