# Gilles Touch Controller — Technical Background

> [🇩🇪 Deutsch (primary)](CONTROLLER_INFO.md) · 🇬🇧 **English**

The Gilles Touch controller used in HPK-RA boilers is based on **industrial-grade Sigmatek hardware**, not on bespoke Gilles electronics. This page collects what we know about the hardware/software stack for reference.

## Hardware

- **Manufacturer:** Sigmatek (Lamprechtshausen, Austria)
- **Product family:** HZS-series boiler control panels — typically HZS 732 / 7321 (multi-touch) or HZS 771 / 772 / 774 (single-touch)
- **Touchscreen:** 7" color display
- **Connectivity:** Ethernet (100 Mbit), USB (for parameter export and firmware updates)

## Software

- **PLC runtime:** LASAL II (Sigmatek's IEC 61131-3 compliant runtime)
- **Visualization:** LSE (LASAL Screen Editor), runs on the same panel
- **Programming environment:** LASAL Engineering Tool (Sigmatek proprietary)
- **Remote access:**
  - VNC server on port 5900 (Touch mirroring)
  - HTTP server on port 80 (LASAL Remote View Java applet — legacy, doesn't work in modern browsers)
  - LASAL service port on 1954 (used by Sigmatek's own engineering tools)

## Modbus implementation specifics

- **Stack:** Sigmatek's built-in Modbus TCP server
- **Activation:** Appears to be active by default once the boiler is networked. We could not find a menu setting to toggle it.
- **Limitations observed:**
  - Only Function Code 03 (Read Holding Registers) is supported. Coils (FC01), Discrete Inputs (FC02), and Input Registers (FC04) all return errors or no response.
  - Map exposes exactly 40 logical values (80 16-bit registers) starting at address 0. Higher addresses return no response.
  - The TCP connection is closed after each Modbus exception. Clients must reconnect.
  - Minimum count for reads appears to be 2 registers (1-register reads return "Illegal Data Value" exception).
  - The reference installation closes TCP after about three idle seconds (measured 2026-09-07). HA therefore reads REG42 every two seconds.
  - The Python logger sets `retries=1` directly on its client and reconnects per reading. HA 2026.9.1 sets retries internally to three; YAML `retries: 1` does not override it. [Evidence and limitations](HA_VALIDATION.en.md).

## Firmware versions

Our test boiler runs:
- LASAL II Version: v5.36.4 (10.01.2024)
- LSE Version: v5.36.4 (10.01.2024)

Both values are visible at the Touch under **Allgemeines → Version**.

## Configuration export

A `Save to USB` function in **Allgemeines → Load/Save** writes three files to a connected USB stick:

1. `parameter.txt` — Plain-text export of all named LASAL parameters with current values. Extremely useful for reverse engineering: every Modbus value corresponds to one of these parameters (though the order in Modbus differs from the order in parameter.txt).
2. `moduser.para` — Binary serialized parameter set. Not human-readable; appears to be Sigmatek's internal LASAL format.
3. `moduser.conf` — Tiny config file declaring which subsystems are configured (e.g., `Heizkreis_1`, `Warmwasser_2`, `Puffer_3`).

The `parameter.txt` from a sample installation is in [`reference/parameter-export-sample.txt`](../reference/parameter-export-sample.txt).

## Why the map is so small

Gilles likely chose to expose only a curated subset of parameters via Modbus, focused on:

- Combustion control parameters (lambda air ratios, O2 limits, flue gas limits)
- Boiler setpoints (day/night, hysteresis)
- Boiler-side live measurements (kessel temp, O2 actual)
- Status flags (operating mode, door state)

Heating-circuit, DHW, buffer, and pellet-feed-system data are managed internally by the LASAL application but not surfaced on the Modbus interface. This is a deliberate design choice, not a limitation of the underlying platform — Sigmatek HZS could easily expose thousands of registers.

## Hargassner relationship

Hargassner acquired Gilles in September 2020. Despite the merger:

- **The Gilles Touch hardware is not replaced** on existing HPK-RA boilers
- **The Hargassner Modbus map is completely different** — addresses ≥40287, requires a separately purchased Modbus ID card, and uses float32 instead of int32
- Service is still provided by Hargassner technicians who know the Gilles system

So while integrations like [TheRealKillaruna/nano_pk](https://github.com/TheRealKillaruna/nano_pk) work for Hargassner Nano-PK / Touch Tronic systems, they are **not compatible** with Gilles HPK-RA. This is why the present repository exists.
