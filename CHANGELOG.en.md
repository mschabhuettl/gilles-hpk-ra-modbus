# Changelog

> [🇩🇪 Deutsch (primary)](CHANGELOG.md) · 🇬🇧 **English**

All notable findings during the reverse engineering of the Gilles Touch Modbus map.

## [0.3.0] — 2026-05-20 — Burner cycle observed

A complete burner cycle (pre-purge → ignition → initial combustion → full load heating → burn-out → cooldown) was observed with synchronized Touch screenshots and Modbus logging. This revealed almost the entire map.

### Newly verified (✓✓)

- **REG[42]** `BrennPhase` — burner cycle phase as enum with codes 0/1/3/5/6/7/8/9 (previously: "always 0")
- **REG[58]** `PrimaerIst` — primary air actual live (previously: suspected REG[56], which was wrong)
- **REG[60]** `SekundaerIst` — secondary air actual live (previously suspected, now confirmed — always 0% in this installation)
- **REG[62]** `SaugzugIst` — **IMPORTANT CORRECTION**: induced draft actual, NOT combustion chamber door (see below)
- **REG[66]** `AbgasSoll_Live` — active flue gas setpoint: 90°C standby / 240°C during burn
- **REG[78]** `AscheaustragungAktiv` — ash discharge running (1=active, 0=pause), 30-second spike matches exactly `sAschenaustrDauer`

### Extended

- **REG[44]** BoilerStatus: new code **5 = Automatik** identified. Touch dropdown shows 7 possible modes; 3 of them now verified.
- **REG[64]** KesselSoll_Live: third value **80°C** in BoilerStatus=3 (buffer charge setpoint). Previously known: 70°C night / 75°C day / 0°C disabled / **new**: 80°C buffer.

### Correction (breaking change in map semantics)

**REG[62] is NOT the combustion chamber door.** The observation in v0.2.0 ("door open → REG[62]=100") was coincidental: opening the combustion door automatically forces the induced draft to 100% (safety smoke extraction). During the burner cycle REG[62] clearly tracked Saugzug values (71%, 76%, 80%, 100%) matching the Touch display.

The combustion chamber door itself is **not directly** exported via Modbus — only indirectly visible through REG[46]=35.

**Impact on existing HA integrations:**
- Sensor `sensor.gilles_brennraumtur_raw` was renamed to `sensor.gilles_saugzug_ist`
- Binary sensor `binary_sensor.gilles_brennraumtur` now derives from REG[46]=35 instead of REG[62]>0
- Previous Saugzug-Ist sensor (REG[60]) is now correctly `sensor.gilles_sekundaer_ist`

### Partially understood

- **REG[56]** — Brief 30-second spike to 103 (= 10.3%?) at Heizen→Ausbrennen transition. Function unclear.
- **REG[68]** — Rises during heating phase from 500 to 600 in irregular steps. Possibly pellet feed or burn-time counter.
- **REG[72]** — Binary flag (0/1), toggles several times per burner cycle. Likely Zellenrad (rotary feeder) status visible on Touch as colored square.

### Tool updates

- Logger v3.1: updated labels with BrennPhase enum, plain-text for REG[44] codes (Handbetrieb/Puffer-Boiler/Automatik), corrected register assignments
- HA modbus.yaml: all 5 affected sensors renamed + new template sensors for BrennPhase plain text

## [0.2.0] — 2026-05-20 — Extended identification

### Newly verified registers

- **REG[20]** `sAschenaustrDauer` (Ash discharge duration, 30 sec)
- **REG[50]** `AbgasTemp_Ist` — flue gas temperature live (correction)
- **REG[52]** `RuecklaufTemp_Ist` — return temperature live (correction)

### REG[64] additional verification

Observed automatic transition from 75.0°C → 70.0°C exactly at the transition point from day to night setpoint — matching the setback period configured at the Touch.

### Negatively verified

The following were confirmed **not in the map** through targeted tests:
- Heating circuit setpoints, DHW modes, buffer tank temperatures
- Boolean configuration flags
- HZS expansion modules (all 48 configured as "not defined")

### New tooling

- `gilles_logger.py` v3 with plain-text display, noise filtering, CSV output

### Bilingual documentation

- All documents available in German (primary) and English (`*.en.md`)

## [0.1.0] — 2026-05-19 — Initial map

### Confirmed registers

22 registers including sProzFoerderSchnecke, sPrimaerMax/Min, sSaugzugMax, sO2Max/Min, sKesselSollTag/Nacht, sAschenaustrPause, sZuendEinschub, sTempDiffStart/Stop, sAbgasTempSollMin, plus live measurements for boiler temperature and O₂.

### Strongly suspected

REG[6], [8], [12], [24], [32] via value match.

### Initial tooling

- pymodbus-based logger and snapshot
- HA Modbus integration with 40 sensors
- HA Lovelace dashboard with detective view
