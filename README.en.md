# Gilles HPK-RA Modbus TCP — Reverse-engineered Register Map

> [🇩🇪 Deutsch (primary)](README.md) · 🇬🇧 **English**

A community effort to document the Modbus TCP interface of the **Gilles Touch** controller used in Gilles biomass boilers (HPK-RA series), and to integrate them into Home Assistant.

> **Status:** 26 of 40 registers empirically verified (✓✓), 8 strongly suspected (✓), 3 with values but unclear semantics (?), 3 likely permanently inactive. Total: 40.

## Background

The Gilles HPK-RA pellet boilers are equipped with the **Gilles Touch** controller, built on a Sigmatek HZS panel running LASAL II. Modbus TCP support is advertised in the product brochure ("Modbus und/oder BAC-Net kompatibel") and runs on port 502.

Although Hargassner acquired Gilles in 2020, the existing HPK-RA controllers are **not** compatible with the Hargassner Modbus map (which uses register addresses ≥40287). The Gilles Touch exposes a much smaller custom map starting at address 0.

**No public documentation exists** for this map. This repository is the result of reverse engineering against a real installation.

## What's in this repo

```
.
├── docs/
│   ├── REGISTER_MAP.md      — the actual register table (the heart of this repo)
│   ├── METHODOLOGY.md       — how registers were identified
│   └── CONTROLLER_INFO.md   — background on Sigmatek/LASAL II
├── scripts/
│   ├── gilles_logger.py     — long-running change-detection logger with CSV output
│   ├── gilles_snapshot.py   — one-shot register dump
│   └── requirements.txt
├── home-assistant/
│   ├── modbus.yaml          — HA Modbus integration for all 40 registers
│   └── dashboard.yaml       — Lovelace dashboard
└── reference/
    └── parameter-export-sample.txt — sample LASAL parameter export
```

German is the primary language — see `*.md` files. English translations are alongside as `*.en.md`.

## What you can do with it

With the HA integration you can monitor:

- **Boiler temperature** (actual & setpoint, with automatic day/night switching)
- **Flue gas temperature** and **return temperature** (live)
- **Residual oxygen (O₂)** and all combustion parameters
- **Burner cycle phase** as plain text: Vorlüften, Zündung, Anbrennen, Heizen regeln, Ausbrennen, Auskühlen
- **Primary & induced-draft fan speeds** (secondary stays 0 in this installation)
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
   pip install pymodbus
   python3 scripts/gilles_snapshot.py <your-boiler-ip>
   ```
4. **Compare to** [docs/REGISTER_MAP.en.md](docs/REGISTER_MAP.en.md) — your values should look similar to ours
5. **Drop the HA config** into your `configuration.yaml`, adjust the host IP, restart HA

## Tested with

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
