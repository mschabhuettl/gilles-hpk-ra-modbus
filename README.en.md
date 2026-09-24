# Gilles HPK-RA Modbus TCP — Reverse-engineered Register Map

> [🇩🇪 Deutsch (primary)](README.md) · 🇬🇧 **English**

A community effort to document the Modbus TCP interface of the **Gilles Touch** controller used in Gilles biomass boilers (HPK-RA series), and to integrate them into Home Assistant.

> **Register status:** 25 of 40 registers historically verified (✓✓), 9 strongly suspected (✓), 4 with unresolved semantics (?), 2 still observed only at zero. REG56 is a strong O₂ target candidate; the previously verified ash interpretation of REG78 has been withdrawn. REG58/60/62 scaling remains unresolved.

## Anonymized register findings

[Findings and open checks](docs/REGISTER_FINDINGS.en.md): O₂ target hypothesis for REG56, nonmonotonic REG68, active REG76 pulses and evidence contradicting the ash-motor interpretation of REG78. REG46=61 is a candidate for the “buffer temperature reached” message. The rolling 24-hour start statistic can undercount sparse starts and is marked unreliable on the dashboard. Private operating histories and screenshots are not published.

## Background

The Gilles HPK-RA pellet boilers are equipped with the **Gilles Touch** controller, built on a Sigmatek HZS panel running LASAL II. Modbus TCP support is advertised in the product brochure ("Modbus und/oder BAC-Net kompatibel") and runs on port 502.

Although Hargassner acquired Gilles in 2020, the existing HPK-RA controllers are **not** compatible with the Hargassner Modbus map (which uses register addresses ≥40287). The Gilles Touch exposes a much smaller custom map starting at address 0.

**No public documentation exists** for this map. This repository is the result of reverse engineering against a real installation.

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
- **Residual oxygen (O₂)** and all combustion parameters
- **Burner cycle phase** as plain text: Vorlüften, Zündung, Anbrennen, Heizen regeln, Ausbrennen, Auskühlen
- **Primary & induced-draft fan values** (check REG62 scaling against the Touch; secondary was 0 in previous observations)
- **Combustion chamber door state** (detected via StatusBitmap)
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
5. **Install/update Home Assistant:** follow [home-assistant/README.en.md](home-assistant/README.en.md). It covers both packages, 35 native helpers, four counter/diagnostic automations and the dashboard, including entity IDs and migration.

## Current HA status and development workflow

The 7 September 2026 cleanup adds explicit availability, observed operating statistics and corrected dashboard references. The reference controller closes idle TCP connections after about three seconds; a two-second REG42 read keeps the HA connection active. See [measurements and limitations](docs/HA_VALIDATION.en.md).

Whenever the Gilles integration changes, its configuration, German/English documentation and changelog are updated and committed to this repository in the same work session. The standing workflow is recorded in [AGENTS.md](AGENTS.md).

## Tested with

- Home Assistant 2026.9.1 (September 2026 configuration validation)
- Gilles HPK-RA pellet boiler
- Gilles Touch with LASAL II v5.36.4 (Jan 2024)
- Software config: Heizkreis 1, Warmwasser 2, Puffer 3, O2 sensor present

If you have a Gilles boiler and want to verify or extend this map, please open an issue or PR.

## What's NOT in this Modbus map

Confirmed by testing — the following data is **not** exposed via Modbus:

- Heating circuit (Heizkreis) setpoints and modes
- Domestic hot water (Warmwasser) modes and temperature
- Buffer tank (Puffer) temperatures (top/bottom)
- Heating circuit flow temperatures
- Bunker temperature
- Operating hours / pellet consumption / ignition counter
- Combustion chamber door direct signal (only indirectly via StatusBitmap REG[46]=35)
- Configuration flags

For these values you'd need a different integration path: either ask a Hargassner service technician to enable an extended Modbus map (paid), or do VNC screen scraping of the Touch.

## License

MIT — see [LICENSE](LICENSE).

## Disclaimer

This project is not affiliated with Gilles or Hargassner. Reverse engineering was done **read-only** (no Modbus writes) against a privately owned boiler. No warranty — use at your own risk. Modifying boiler parameters via Modbus can affect combustion and safety; only write to registers whose function you fully understand.
