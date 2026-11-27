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
  - Function Code 03 (Read Holding Registers) is the established read method. Historical attempts using FC01, FC02 and FC04 produced errors or no response; this is not a complete list of supported functions.
  - The known range contains 40 logical values in 80 16-bit registers starting at address 0. Historical attempts above this range produced no usable response.
  - Connections have been observed to close after Modbus exceptions. Clients must handle such closures and reconnect when needed.
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

1. `parameter.txt` — Plain-text export of named LASAL parameters with current values. Comparisons support several register mappings; completeness and a counterpart for every Modbus value have not been established. The order differs from the Modbus map.
2. `moduser.para` — Binary serialized parameter set. Not human-readable; appears to be Sigmatek's internal LASAL format.
3. `moduser.conf` — Tiny config file declaring which subsystems are configured (e.g., `Heizkreis_1`, `Warmwasser_2`, `Puffer_3`).

The `parameter.txt` from a sample installation is in [`reference/parameter-export-sample.txt`](../reference/parameter-export-sample.txt).

## Scope of the known map

The values mapped so far mainly cover:

- Combustion control parameters (lambda air ratios, O2 limits, flue gas limits)
- Boiler setpoints (day/night, hysteresis)
- Boiler-side live measurements (kessel temp, O2 actual)
- Operating mode and status codes; the REG46=35 door indication is indirect

Reliable Modbus mappings are missing for further heating-circuit, DHW, buffer and feed-system quantities. REG68 remains a candidate for current feed quantity with unresolved unit and scale. These gaps do not establish a manufacturer design decision or inaccessibility in principle. The [unofficial read profile](spec/README.en.md) records the known scope and its limits.

## Hargassner relationship

Hargassner acquired Gilles in September 2020. Despite the merger:

- **The Gilles Touch hardware is not replaced** on existing HPK-RA boilers
- **The Hargassner Modbus map is completely different** — addresses ≥40287, requires a separately purchased Modbus ID card, and uses float32 instead of int32
- Service is still provided by Hargassner technicians who know the Gilles system

So while integrations like [TheRealKillaruna/nano_pk](https://github.com/TheRealKillaruna/nano_pk) work for Hargassner Nano-PK / Touch Tronic systems, they are **not compatible** with Gilles HPK-RA. This is why the present repository exists.
