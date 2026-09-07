# Gilles HPK-RA Modbus TCP — Reverse-engineered Register Map

> [🇩🇪 Deutsch (primary)](README.md) · 🇬🇧 **English**

A community effort to document the Modbus TCP interface of the **Gilles Touch** controller used in Gilles biomass boilers (HPK-RA series), and to integrate them into Home Assistant.

> **Status:** 26 of 40 registers empirically verified (✓✓), 8 strongly suspected (✓), 3 with values but unclear semantics (?), 3 observed as zero with unconfirmed purpose. Total: 40.

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
- **Ash discharge active** yes/no
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
