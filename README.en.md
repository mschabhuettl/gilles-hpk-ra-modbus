# Gilles HPK-RA Modbus TCP — Reverse-engineered Register Map

> [🇩🇪 Deutsch (primary)](README.md) · 🇬🇧 **English**

A community effort to document the Modbus TCP interface of the **Gilles Touch** controller used in Gilles biomass boilers (HPK-RA series), and to integrate them into Home Assistant.

> **Register status:** 25 of 40 registers historically verified (✓✓), 9 strongly suspected (✓), 4 with unresolved semantics (?), 2 still observed only at zero. REG56 is a strong O₂ target candidate; the previously verified ash interpretation of REG78 has been withdrawn. REG58/60/62 scaling remains unresolved.

## Unofficial interface specification

[Specification 0.1.0](docs/spec/README.en.md) describes the read-only Modbus TCP profile, all 40 known logical values, state mappings and unresolved scales. It consolidates the 0.9.1 evidence baseline; this edition confirms no new register meanings and includes no new measurements. The document version is maintained separately from the project version.

[English PDF](docs/spec/gilles-modbus-spec-v0.1.0-en.pdf) · [German PDF](docs/spec/gilles-modbus-spec-v0.1.0-de.pdf) · [LaTeX source ZIP](docs/spec/gilles-modbus-spec-v0.1.0-sources.zip). Both languages use the same `registers.json`; synthetic messages and decoder vectors can be checked offline. Independent community documentation, without manufacturer approval.

## Anonymized register findings

[Findings and open checks](docs/REGISTER_FINDINGS.en.md): O₂ target hypothesis for REG56, nonmonotonic REG68, active REG76 pulses and evidence contradicting the ash-motor interpretation of REG78. REG46=61 is a candidate for the “buffer temperature reached” message. The rolling 24-hour start count now uses directly recorded `0→1` transitions in Recorder. Startup diagnostics compare recovery with the lowest boiler reading observed since the start; trend hysteresis and an activation delay suppress brief fluctuations. A separate O₂ statistic includes only the heating phase. Broader passive analysis continues to support REG56 as an O₂-target candidate without upgrading its confidence level. Private operating histories and screenshots are not published.

The [follow-up of natural burner cycles](docs/HA_VALIDATION.en.md) confirms the running minimum baseline, recorded start counting and phase-filtered O₂ minimum, including expiry of older low samples. Low O₂ values were also recorded within the heating phase, so the number alone does not identify standby. Actual execution of the warning delay remains untested because no qualifying alarm case occurred.

## Background

The Gilles HPK-RA pellet boilers are equipped with the **Gilles Touch** controller, built on a Sigmatek HZS panel running LASAL II. Modbus TCP support is advertised in the product brochure ("Modbus und/oder BAC-Net kompatibel") and runs on port 502.

Although Hargassner acquired Gilles in 2020, the existing HPK-RA controllers are **not** compatible with the Hargassner Modbus map (which uses register addresses ≥40287). The Gilles Touch exposes a much smaller custom map starting at address 0.

No matching manufacturer register map was available during the investigation. This repository documents reverse engineering against a real installation.

## What's in this repo

| Path | Contents |
|---|---|
| `docs/REGISTER_MAP.en.md` | Register table and confidence levels |
| `docs/METHODOLOGY.en.md` | Reverse-engineering methods |
| `docs/CONTROLLER_INFO.en.md` | Controller background |
| `docs/HA_VALIDATION.en.md` | HA cleanup, TCP idle-limit measurements and open checks |
| `home-assistant/` | Packages, native helpers, automations, entity mapping and dashboard |
| `scripts/` | Logger, snapshot and configuration consistency check |
| `reference/` | Parameter sample and sanitized validation evidence |

German is the primary language — see `*.md` files. English translations are alongside as `*.en.md`.

## What you can do with it

With the HA integration you can monitor:

- **Boiler temperature** (actual & setpoint, with automatic day/night switching)
- **Flue gas temperature** and **return temperature** (live)
- **Residual oxygen (O₂)** and the mapped combustion parameters
- **Burner cycle phase** as plain text: Vorlüften, Zündung, Anbrennen, Heizen regeln, Ausbrennen, Auskühlen
- **Air/induced-draft values** (REG58/60/62 scales still need comparison with the Touch)
- **Indirect combustion chamber door indication** (REG46=35 historically observed with the door open; unknown codes do not establish a door position)
- **REG78 signal and rising edges** (previously labelled ash discharge; physical function remains unresolved)
- **Operating mode**: Handbetrieb, Puffer/Boiler, Automatik (others not yet observed)

## Quick start

1. **Find your boiler's IP** — at the Touch panel: Allgemeines → Ethernet
2. **Verify Modbus is reachable:**
   ```bash
   nc -zv <your-boiler-ip> 502
   ```
3. **Take a snapshot:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   python3 -m pip install -r scripts/requirements.txt
   python3 scripts/gilles_snapshot.py <your-boiler-ip>
   ```
4. **Compare to** [docs/REGISTER_MAP.en.md](docs/REGISTER_MAP.en.md) — your values should look similar to ours
5. **Install/update Home Assistant:** follow [home-assistant/README.en.md](home-assistant/README.en.md). It covers both packages, native helpers and one SQL sensor, four counter/diagnostic automations and the dashboard, including entity IDs and migration.

## Current HA status and development workflow

The 7 September 2026 cleanup adds explicit availability, observed operating statistics and corrected dashboard references. A TCP idle close after about three seconds was measured on the reference controller; two-second REG42 polling is the targeted mitigation, not a general stability guarantee. See [measurements and limitations](docs/HA_VALIDATION.en.md).

Whenever the Gilles integration changes, its configuration, German/English documentation and changelog are updated and committed to this repository in the same work session. The standing workflow is recorded in [AGENTS.md](AGENTS.md).

## Tested with

- Home Assistant 2026.11.1 (current operating diagnostics); original packages validated with 2026.9.1
- Gilles HPK-RA pellet boiler
- Gilles Touch with LASAL II v5.36.4 (Jan 2024)
- Software config: Heizkreis 1, Warmwasser 2, Puffer 3, O2 sensor present

If you have a Gilles boiler and want to verify or extend this map, please open an issue or PR.

## Quantities not yet mapped

The following quantities lack reliable mappings in the tested map. This does not prove that they are inaccessible in principle or absent from every possible encoding:

- Heating circuit (Heizkreis) setpoints and modes
- Domestic hot water (Warmwasser) modes and temperature
- Buffer tank (Puffer) temperatures (top/bottom)
- Heating circuit flow temperatures
- Bunker temperature
- Operating hours / pellet consumption / ignition counter
- Combustion chamber door direct signal (REG46=35 is only a historically observed indirect indication)
- Configuration flags

Further mappings require a simultaneous comparison with the Touch display. This project has not established whether the manufacturer offers an additional register map or an activation option. See [open checks](docs/REGISTER_FINDINGS.en.md).

## License

MIT — see [LICENSE](LICENSE).

## Disclaimer

This project is not affiliated with Gilles or Hargassner. Reverse engineering was done **read-only** (no Modbus writes) against a privately owned boiler. No warranty — use at your own risk. Write access has not been investigated and is outside the documented read profile.

