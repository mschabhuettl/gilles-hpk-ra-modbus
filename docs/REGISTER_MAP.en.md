# Gilles Touch Modbus Register Map

> [🇩🇪 Deutsch (primary)](REGISTER_MAP.md) · 🇬🇧 **English**

**Status:** Extended passive analysis; historical Touch identifications retained with explicit uncertainty
**Controller firmware:** LASAL II v5.36.4 (10.01.2024)
**Confidence levels:** ✓✓ = empirically verified · ✓ = strongly indicated by value match · ? = unknown

## Status

| Confidence | Count | Meaning |
|---|---:|---|
| ✓✓ | 25 | Historically identified; REG58/62 scaling still needs verification |
| ✓ | 9 | Strong hypothesis, now including REG56 as a calculated O₂ target |
| ? — nonzero observed | 4 | REG68, REG72, REG76, REG78 |
| ? — only zero observed | 2 | REG70, REG74; purpose remains unknown |
| **Total** | **40** | |

The [anonymized register findings](REGISTER_FINDINGS.en.md) supersede the former claims that REG56 only pulses, REG68 is a counter, REG76 is inactive, and REG78 is a verified ash motor. A confidence mark describes the functional identification, not automatic confirmation of every scale or firmware variant.

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

**Bus quirks:** Connection closure was observed after Modbus exceptions. The reference installation also closes TCP after about three seconds without a request (measured twice). The standalone logger reconnects for each reading and sets `retries=1` on its client. HA 2026.9.1 sets retries internally; YAML `retries: 1` does not override them. HA now reads REG42 every two seconds. [Measurements and configuration](HA_VALIDATION.en.md).

## ⚠️ Important correction (v0.3.0)

**REG[62] is NOT the combustion chamber door**, it's **SaugzugIst** (induced-draft fan actual %). The misidentification in v0.1.0/v0.2.0 happened because opening the combustion chamber door automatically forces the induced draft to 100% (safety smoke extraction). During the observed burner cycle REG[62] clearly tracked Saugzug values like 71%, 76%, 80% — matching the Touch display.

The combustion chamber door itself is **not directly** exported via Modbus — it is only indirectly visible via REG[46]=35.

**Scaling review:** REG58/62 retain their historical primary-air/induced-draft identifications. The HA scale ×0.1 does not clearly agree with the historical Touch matches and observed relationships to parameter limits. A factor-of-ten display error is possible but unproven. Raw scale ×1 remains a candidate. The existing HA scales remain unchanged pending a simultaneous raw/HA/Touch comparison; the historical percentage values below are not fresh scaling evidence.

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
| 46 | `StatusBitmap` | int32 | enum/bitfield? | — | ✓ | 0/35/61 observed; 35 historically matched an open door. 61 matches the Touch banner “Puffertemperatur erreicht” (buffer temperature reached); provisional state association, not an exactly synchronized confirmation. Bitfield structure unproven. |
| **48** | **`KesselTemp_Ist`**   | int32 | ×0.1 | °C | ✓✓ | Boiler temperature (live) |
| **50** | **`AbgasTemp_Ist`** | int32 | ×0.1 | °C | ✓✓ | Flue gas temperature (live). |
| **52** | **`RuecklaufTemp_Ist`**| int32 | ×0.1 | °C | ✓✓ | Return temperature (live) |
| **54** | **`O2_Ist`**           | int32 | ×0.1 | %  | ✓✓ | Residual oxygen (live; 21% at start, ~12% during burn) |
| 56 | `?O2Soll_Live` | int32 | ×0.1? | %? | ✓ | Closely matches an exhaust-temperature-based O₂ target during regulation. The Touch actual/target page is identified; matching zero values establish neither identity nor scale. Nonzero comparison remains open. |
| **58** | **`PrimaerIst`** | int32 | ×0.1 HA; ? actual | %? | ✓✓ | Historical primary-air match. Functional identification retained, scale uncertain. |
| **60** | **`SekundaerIst`**     | int32 | ×0.1 | %  | ✓✓ | **Secondary air actual (live)** — stays 0 in this installation (Touch shows 0% throughout) |
| **62** | **`SaugzugIst`** | int32 | ×0.1 HA; ? actual | %? | ✓✓ | Historical induced-draft match. Functional identification retained, scale uncertain. |
| **64** | **`KesselSoll_Live`**  | int32 | ×0.1 | °C | ✓✓ | Active boiler target; can be zero in standby while Puffer/Boiler mode remains selected. |
| **66** | **`AbgasSoll_Live`** | int32 | ×0.1 | °C | ✓✓ | Active flue target; changes within phase 7. Not a fixed binary value. |
| 68 | `?REG68` | int32 | ? | ? | ? | Increases and decreases. Specific candidate: Touch “aktuelle Einschubmenge” (current feed amount). Nonzero comparison and scale remain open; not a monotonic consumption/runtime counter. |
| 70 | `?`                        | int32 | ?    | ?  | ? | Always 0 in all observations |
| 72 | `?BinaryFlag` | int32 | bool | — | ? | Active during ignition/startup; candidate ignition-related output. Exact actuator unknown. |
| 74 | `?`                        | int32 | ?    | ?  | ? | Always 0 in all observations |
| 76 | `?BinaryFlag` | int32 | bool | — | ? | Recurring high intervals observed. Purpose, periodicity and physical pulse width unknown. |
| **78** | **`?BinaryFlag`** | int32 | bool | — | ? | Former ash-discharge identification withdrawn because of a long high interval. Pump/release is a candidate; legacy HA IDs retained. |

## Enum: `BrennPhase` (REG[42])

Historical phase assignment; the full sequence was confirmed in a further passive observation. Code 7 also covers modulation, so it is not proof of full load:

| Code | Phase | Touch display | Typical state |
|------|-------|---------------|---------------|
| 0 | Standby / no burner | — | all blowers 0 |
| 1 | Vorlüften (pre-purge) | "Vorlüften 173" | Saugzug 80%, others 0 |
| 3 | Zündung (ignition) | "Zündung 589" | Primär 70%, Saugzug 80-100%, O₂ rises to 21% |
| 5 | Late ignition / transition | (between 3 and 6) | Saugzug 100%, O₂ still ~21% |
| 6 | Anbrennphase (initial combustion) | "Anbrennphase 34" | Saugzug 80%, exhaust rises rapidly |
| 7 | Heizen regeln (regulating heat) | "Heizen regeln" | Primär 63%, Saugzug 71%, O₂ 12-14%, exhaust 100+°C, REG[66] jumps to 240°C |
| 8 | Ausbrennen (burn-out) | "Ausbrennen" | Primary + Saugzug still on, exhaust falling |
| 9 | Auskühlphase (cooldown) | (after burner off) | only blower run-on |

Codes 2 and 4 have not been observed yet — likely additional sub-phases.

## Enum: `BoilerStatus` (REG[44])

The Touch's dropdown shows 7 modes (Steuerung Aus, Handbetrieb, Zeitbetrieb, Puffer/Boiler, Puffer/Boiler Gluterhaltung, Automatik, Notbetrieb). Of these, 3 are verified:

| Code | Mode | Touch display | KesselSoll_Live (REG[64]) |
|------|------|---------------|---------------------------|
| 1 | Handbetrieb (Manual) | "Handbetrieb" | Day 75°C / Night 70°C |
| 3 | Puffer/Boiler | "Puffer/Boiler" | State-dependent: an active charging target or zero with the burner off. Mode alone does not determine REG64. |
| 5 | Automatik | "Automatik" | Day 75°C / Night 70°C |
| ? | Steuerung Aus (controller off) | not yet observed | — |
| ? | Zeitbetrieb (time mode) | not yet observed | — |
| ? | Puffer/Boiler Gluterhaltung | not yet observed | — |
| ? | Notbetrieb (emergency) | not yet observed | — |

## Active boiler target (REG[64])

A numeric target, not a mode enum. The following nonzero values are historical examples; operating mode, time profile and current demand must be considered separately:

| Value | Meaning |
|-------|---------|
| 70.0°C | Night profile active (= REG[34] sKesselSollNacht) |
| 75.0°C | Day profile active (= REG[18] sKesselSollTag) |
| 80.0°C | Buffer charge setpoint (in BoilerStatus=3) |
| 0.0°C | Also observed with Puffer/Boiler still selected and the burner off; not evidence that the operating mode is disabled. |

## Verified test events

In chronological order of observations:

| Action | Modbus reaction |
|--------|-----------------|
| Switch to Puffer/Boiler mode | REG[44]: 1→3 · REG[46]: 0→61 · REG[64]: 75→0°C |
| Automatic Day→Night transition (setback period begins) | REG[64]: 75.0°C → 70.0°C |
| Historical REG78 pulse | About 30s high; a subsequently observed long high interval challenges the former ash interpretation. Duration match alone did not establish actuator identity. |
| Switch Handbetrieb → Puffer/Boiler before burner cycle | REG[44]: 1→3, REG[64]: 70→80°C |
| Burner starts (pre-purge) | REG[42]: 0→1, REG[62]: 0→80% (Saugzug) |
| Ignition starts | REG[42]: 1→3, REG[54]: 1→21% (O2 rises with fresh air) |
| Combustion chamber door opened during ignition | REG[46]: 0→35, REG[62]: 80→100 (Saugzug to max) |
| Initial combustion phase | REG[42]: 5→6, REG[58]: 0→70 (Primary air) |
| Regulating heat | REG[42]: 6→7, REG[50]: ~30→105°C, REG[66]: 90→240°C, REG[68]: 0→500 |
| Burner stop initiated | REG[44]: 3→1, REG[42]: 7→8 (burn-out) |
| Cooldown phase | REG[42]: 8→9 |

## Not identified in the tested map

Earlier targeted Touch tests produced no attributable Modbus changes for these values. This documents unsuccessful identification, not proof that no encoding can exist:

- Heating circuit setpoints (flow / room temperature) — Touch shows HK1 28°C, HK4 27°C
- DHW mode and temperature — Touch shows DHW 56°C
- Buffer tank temperatures top/bottom — Touch shows 48/39°C
- Bunker temperature
- Operating hours, ignition count
- Combustion chamber door direct signal (only indirectly via REG[46]=35)
- Config flags (External release ignore, Pulsed ignition feed, E-mail enabled, …)
- HZS expansion modules (all 48 configured as "not defined")

## Open questions

| Register | Next evidence needed |
|---|---|
| REG56 | Compare “Restsauerstoff – Soll” on the actual/target page simultaneously during natural regulation with nonzero values. |
| REG58/62 | Compare raw integers, HA values and Touch percentages simultaneously before changing the scale. |
| REG68 | Compare “aktuelle Einschubmenge” on the same actual/target page at nonzero values and during modulation. Scale remains open; no consumption calculation. |
| REG72 | Compare ignition and dosing outputs during a natural startup; distinguish pulsed ignition feed from ignition heating. |
| REG76 | Identify the actual output and function enable; cleaning time parameters and thermal contacts do not establish a cleaning cycle. |
| REG78 | Compare pump/release/ash indicators during a natural transition. Count raw rising edges only, not confirmed ash cycles. |
| REG42/44/46 | Missing phase/mode codes and status-code structure remain unresolved; test REG46=61 across changes of the Touch banner. |

REG70 and REG74 remained zero in the retrieved history. They are not proven to be permanently inactive or reserved for unused modules.
