# Gilles Touch Modbus Register Map

> [🇩🇪 Deutsch (primary)](REGISTER_MAP.md) · 🇬🇧 **English**

**Last updated:** 2026-05-20 (v0.3.0 — burner cycle observed)
**Controller firmware:** LASAL II v5.36.4 (10.01.2024)
**Confidence levels:** ✓✓ = empirically verified · ✓ = strongly indicated by value match · ? = unknown

## Status

- **29 of 40 registers** firmly identified (✓✓)
- **4 more** strongly suspected (✓)
- **3 registers** likely permanently inactive in this installation
- **4 registers** still entirely unclear (REG[56, 68, 72] + REG[46] sub-codes)

## Connection details

| Setting | Value |
|---|---|
| Protocol | Modbus TCP |
| Port | 502 |
| Slave ID | 1 |
| Function code | 03 (Read Holding Registers) only |
| Register count | 80 (= 40 × int32) |
| Data type | int32, high word first (big-endian) |
| Address base | 0-indexed |

**Important:** All values are 32-bit integers stored across two 16-bit registers. To read value at logical position N, read holding registers at addresses N×2 and N×2+1, then combine as `(reg[N*2] << 16) | reg[N*2+1]`.

**Bus quirk:** The Sigmatek Modbus implementation closes the TCP connection after each Modbus exception. Always reconnect fresh on error and use `retries=1` (not 3, which is the pymodbus default).

## ⚠️ Important correction (v0.3.0)

**REG[62] is NOT the combustion chamber door**, it's **SaugzugIst** (induced-draft fan actual %). The misidentification in v0.1.0/v0.2.0 happened because opening the combustion chamber door automatically forces the induced draft to 100% (safety smoke extraction). During the observed burner cycle REG[62] clearly tracked Saugzug values like 71%, 76%, 80% — matching the Touch display.

The combustion chamber door itself is **not directly** exported via Modbus — it is only indirectly visible via REG[46]=35.

## Register table

| Addr | Name | Type | Scale | Unit | Confidence | Notes |
|------|------|------|-------|------|------------|-------|
| 0  | `sProzFoerderSchnecke`     | int32 | ×0.1 | %  | ✓✓ | Conveyor screw % (Touch: 40%) |
| 2  | `sPrimaerMax`              | int32 | ×0.1 | %  | ✓✓ | Primary air max (Touch: 70%) |
| 4  | `sPrimaerMin`              | int32 | ×0.1 | %  | ✓✓ | Primary air min (Touch: 35%) |
| 6  | `sSekundaerMax`            | int32 | ×0.1 | %  | ✓ | Secondary air max |
| 8  | `sSekundaerMin`            | int32 | ×0.1 | %  | ✓ | Secondary air min |
| 10 | `sSaugzugMax`              | int32 | ×0.1 | %  | ✓✓ | Induced draft max |
| 12 | `sSaugzugMin`              | int32 | ×0.1 | %  | ✓ | Induced draft min |
| 14 | `sO2Max`                   | int32 | ×0.1 | %  | ✓✓ | O₂ max setpoint |
| 16 | `sO2Min`                   | int32 | ×0.1 | %  | ✓✓ | O₂ min setpoint |
| 18 | `sKesselSollTag`           | int32 | ×0.1 | °C | ✓✓ | Boiler setpoint day (Touch: 75°C) |
| 20 | `sAschenaustrDauer`        | int32 | ×0.1 | s  | ✓✓ | Ash discharge duration (Touch: 30 sec) |
| 22 | `sAschenaustrPause`        | int32 | ×1   | min| ✓✓ | Ash discharge pause (Touch: 15 min) |
| 24 | `sStartSekundaer`          | int32 | ×0.1 | %  | ✓ | Secondary start value |
| 26 | `sZuendEinschub`           | int32 | ×0.1 | s  | ✓✓ | Ignition feeder duration (Touch: 75 sec) |
| 28 | `sTempDiffStart`           | int32 | ×0.1 | °C | ✓✓ | Temp diff start (Touch: 5°C) |
| 30 | `sTempDiffStop`            | int32 | ×0.1 | °C | ✓✓ | Temp diff stop (Touch: 3°C) |
| 32 | `sTempDiffTeillast`        | int32 | ×0.1 | °C | ✓ | Temp diff partial load |
| 34 | `sKesselSollNacht`         | int32 | ×0.1 | °C | ✓✓ | Boiler setpoint night (Touch: 70°C) |
| 36 | `sAbgasTempSollMin`        | int32 | ×0.1 | °C | ✓✓ | Flue gas setpoint min (Touch: 90°C) |
| 38 | `sAbgasTempMax`            | int32 | ×0.1 | °C | ✓ | Flue gas max (240°C) |
| 40 | `sAbgasTempMaxLimit`       | int32 | ×0.1 | °C | ✓ | Flue gas hard limit (270°C) |
| **42** | **`BrennPhase`**       | int32 | enum | —  | ✓✓ | **Burner cycle phase** (see enum below) |
| **44** | **`BoilerStatus`**     | int32 | enum | —  | ✓✓ | Boiler operating mode (see enum below) |
| 46 | `StatusBitmap`             | int32 | bitfield | — | ✓ | Plant status: 0=normal, 35=door open, 61=Puffer/Boiler-mode |
| **48** | **`KesselTemp_Ist`**   | int32 | ×0.1 | °C | ✓✓ | Boiler temperature (live) |
| **50** | **`AbgasTemp_Ist`**    | int32 | ×0.1 | °C | ✓✓ | Flue gas temperature (live; up to 110°C observed during burn) |
| **52** | **`RuecklaufTemp_Ist`**| int32 | ×0.1 | °C | ✓✓ | Return temperature (live) |
| **54** | **`O2_Ist`**           | int32 | ×0.1 | %  | ✓✓ | Residual oxygen (live; 21% at start, ~12% during burn) |
| 56 | `?REG56`                   | int32 | ×0.1 | %? | ? | Brief 10.3% spike at Heizen→Ausbrennen transition (30 sec) — function unclear |
| **58** | **`PrimaerIst`**       | int32 | ×0.1 | %  | ✓✓ | **Primary air actual (live)** — correlates exactly with Touch (63/67/70%) |
| **60** | **`SekundaerIst`**     | int32 | ×0.1 | %  | ✓✓ | **Secondary air actual (live)** — stays 0 in this installation (Touch shows 0% throughout) |
| **62** | **`SaugzugIst`**       | int32 | ×0.1 | %  | ✓✓ | **Induced draft actual (live)** — varies 71/72/76/80/100% by phase |
| **64** | **`KesselSoll_Live`**  | int32 | ×0.1 | °C | ✓✓ | Currently active setpoint (70/75/80°C depending on mode & time of day) |
| **66** | **`AbgasSoll_Live`**   | int32 | ×0.1 | °C | ✓✓ | Currently active flue gas setpoint (90°C standby / 240°C during burn) |
| 68 | `?Counter`                 | int32 | ?    | ?  | ? | Rises during heating phase from 500 to 600 in irregular steps — possibly pellet or burn-time counter |
| 70 | `?`                        | int32 | ?    | ?  | ? | Always 0 in all observations |
| 72 | `?BinaryFlag`              | int32 | bool | —  | ? | Binary 0/1, toggles multiple times during burner cycle — possibly Zellenrad (rotary feeder) status |
| 74 | `?`                        | int32 | ?    | ?  | ? | Always 0 in all observations |
| 76 | `?`                        | int32 | ?    | ?  | ? | Always 0 in all observations |
| **78** | **`AscheaustragungAktiv`** | int32 | bool | — | ✓✓ | **Ash discharge running** (1=active, 0=pause) — 30-sec spike matches exactly `sAschenaustrDauer` |

## Enum: `BrennPhase` (REG[42])

Derived from a fully observed burner cycle:

| Code | Phase | Touch display | Typical state |
|------|-------|---------------|---------------|
| 0 | Standby / no burner | — | all blowers 0 |
| 1 | Vorlüften (pre-purge) | "Vorlüften 173" | Saugzug 80%, others 0 |
| 3 | Zündung (ignition) | "Zündung 589" | Primär 70%, Saugzug 80-100%, O₂ rises to 21% |
| 5 | Late ignition / transition | (between 3 and 6) | Saugzug 100%, O₂ still ~21% |
| 6 | Anbrennphase (initial combustion) | "Anbrennphase 34" | Saugzug 80%, exhaust rises rapidly |
| 7 | Heizen regeln (full load) | "Heizen regeln" | Primär 63%, Saugzug 71%, O₂ 12-14%, exhaust 100+°C, REG[66] jumps to 240°C |
| 8 | Ausbrennen (burn-out) | "Ausbrennen" | Primary + Saugzug still on, exhaust falling |
| 9 | Auskühlphase (cooldown) | (after burner off) | only blower run-on |

Codes 2 and 4 have not been observed yet — likely additional sub-phases.

## Enum: `BoilerStatus` (REG[44])

The Touch's dropdown shows 7 modes (Steuerung Aus, Handbetrieb, Zeitbetrieb, Puffer/Boiler, Puffer/Boiler Gluterhaltung, Automatik, Notbetrieb). Of these, 3 are verified:

| Code | Mode | Touch display | KesselSoll_Live (REG[64]) |
|------|------|---------------|---------------------------|
| 1 | Handbetrieb (Manual) | "Handbetrieb" | Day 75°C / Night 70°C |
| 3 | Puffer/Boiler | "Puffer/Boiler" | **80°C** (= buffer charge setpoint) |
| 5 | Automatik | "Automatik" | Day 75°C / Night 70°C |
| ? | Steuerung Aus (controller off) | not yet observed | — |
| ? | Zeitbetrieb (time mode) | not yet observed | — |
| ? | Puffer/Boiler Gluterhaltung | not yet observed | — |
| ? | Notbetrieb (emergency) | not yet observed | — |

## Enum: `KesselSoll_Live` (REG[64])

Active setpoint. Switches by mode and time of day:

| Value | Meaning |
|-------|---------|
| 70.0°C | Night profile active (= REG[34] sKesselSollNacht) |
| 75.0°C | Day profile active (= REG[18] sKesselSollTag) |
| 80.0°C | Buffer charge setpoint (in BoilerStatus=3) |
| 0.0°C | Mode disabled |

## Verified test events

In chronological order of observations:

| Action | Modbus reaction |
|--------|-----------------|
| Switch to Puffer/Boiler mode | REG[44]: 1→3 · REG[46]: 0→61 · REG[64]: 75→0°C |
| Automatic Day→Night transition (setback period begins) | REG[64]: 75.0°C → 70.0°C |
| Automatic ash discharge cycle | REG[78]: 0→1 (exactly 30 sec = sAschenaustrDauer), then back to 0 |
| Switch Handbetrieb → Puffer/Boiler before burner cycle | REG[44]: 1→3, REG[64]: 70→80°C |
| Burner starts (pre-purge) | REG[42]: 0→1, REG[62]: 0→80% (Saugzug) |
| Ignition starts | REG[42]: 1→3, REG[54]: 1→21% (O2 rises with fresh air) |
| Combustion chamber door opened during ignition | REG[46]: 0→35, REG[62]: 80→100 (Saugzug to max) |
| Initial combustion phase | REG[42]: 5→6, REG[58]: 0→70 (Primary air) |
| Full load heating | REG[42]: 6→7, REG[50]: ~30→105°C, REG[66]: 90→240°C, REG[68]: 0→500 |
| Burner stop initiated | REG[44]: 3→1, REG[42]: 7→8 (burn-out) |
| Cooldown phase | REG[42]: 8→9 |

## Definitely NOT in the map

Confirmed by targeted tests — none of the following actions on the Touch produced any Modbus changes:

- Heating circuit setpoints (flow / room temperature) — Touch shows HK1 28°C, HK4 27°C
- DHW mode and temperature — Touch shows DHW 56°C
- Buffer tank temperatures top/bottom — Touch shows 48/39°C
- Bunker temperature
- Operating hours, ignition count
- Combustion chamber door direct signal (only indirectly via REG[46]=35)
- Config flags (External release ignore, Pulsed ignition feed, E-mail enabled, …)
- HZS expansion modules (all 48 configured as "not defined")

## Open questions

1. What is **REG[56]**? Only a 30-second spike to 10.3% at the Phase 7→8 transition — a briefly activated pump or actuator?
2. What is **REG[68]**? Rises from 500 to 600 during heating phase. Pellet feed counter? Burn-time counter?
3. What is **REG[72]**? Binary flag, toggling several times per burner cycle. Likely Zellenrad (rotary feeder) status visible on Touch as colored square.
4. Complete `BrennPhase` codes (REG[42]) — codes 2 and 4 missing.
5. Complete `BoilerStatus` codes (REG[44]) — 4 of 7 modes not yet observed.
6. Complete bitfield schema of REG[46] — likely more codes for other plant states.

## Likely permanently inactive

The following registers never showed any value ≠ 0 — including during the full burner cycle:

- **REG[70]**, **REG[74]**, **REG[76]**

Likely reserved for HZS expansion modules or subsystems this installation doesn't have (cascade master, mixers, district heating). Won't become active unless the installation is extended.
