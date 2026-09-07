# Home Assistant operational validation, 7 September 2026

> [🇩🇪 Deutsch](HA_VALIDATION.md) · 🇬🇧 **English**

The Gilles configuration was compared with the reference installation running Home Assistant 2026.9.1. This extends the earlier register work; it does not establish new meanings for unknown registers.

## Reproducible TCP idle limit

An additional TCP connection performed only FC03 reads of REG42. Following a valid response, it passively waited for the peer to close the connection.

| Experiment | Observation |
|---|---|
| One request, then no further traffic | Valid response in 54.3 ms; connection closed after 3.010 s idle |
| Three requests spaced 2 s apart over the same connection | All answered; response times 76.9 / 29.5 / 11.9 ms |
| No further requests afterwards | Connection closed after 3.060 s idle |

The control experiment shows that total connection lifetime can exceed three seconds when more reads occur. This idle limit explains disconnects between the previous requests, some of which were ten seconds apart. It was measured on this installation and is not guaranteed for every firmware version.

HA now reads REG42 every two seconds, preserving the other 39 polling intervals. A 200 ms inter-request wait separates individual requests; this wait alone had not eliminated the gaps. A separate FC03 block read also successfully retrieved all 80 registers as 40 int32 values.

HA logs a generic warning for polling below five seconds. The targeted exception for one sensor stays within the measured idle limit; the warning was not suppressed. Observation began at 07:46:57 Europe/Vienna. Throughout the archived interval ending 07:52:02, all 40 values remained available and the phase code stayed at 0 without a gap. The final session check through 07:53:44 likewise showed no further gap. **This is a short functional check, not long-term evidence.**

Evidence without hosts or credentials: [ha-validation-2026-09-07.json](../reference/ha-validation-2026-09-07.json).

## HA configuration and dashboard

- The package named `gilles-derived` was rejected because of its hyphen. Its replacement is `gilles_derived.yaml`.
- Seven existing templates now check input availability. A failed read no longer becomes standby, normal state or a closed door.
- 23 native helpers and two counter automations were created. Native state transitions update the two timestamps; no artificial starting events are generated.
- All 69 dashboard entity references existed after cleanup, accounting for 16 historical naming differences. Screenshot verification was unavailable because the rendering feature was disabled.
- All 40 raw sensors retain their identities and register scales. Counters, data coverage and observed operating times replace unsupported consumption/efficiency displays.
- HA configuration validation passed and the affected integrations were reloaded. The new counter statistics units were aligned to `Starts`/`Vorgänge` and validated as consistent.

## Retry settings

The standalone logger creates a fresh connection per reading and passes `retries=1` directly to PyModbus. HA 2026.9.1 internally uses `retries=3`; an extra YAML `retries: 1` key does not override it. `delay` is a startup delay, not the inter-request wait. See the [HA 2026.9.1 implementation](https://github.com/home-assistant/core/blob/2026.9.1/homeassistant/components/modbus/__init__.py) and [Modbus configuration](https://www.home-assistant.io/integrations/modbus/).

The scripts use `device_id=`, which replaced `slave=` in [PyModbus 3.10](https://pymodbus.readthedocs.io/en/latest/source/api_changes.html#api-changes-3-10-0). Their minimum dependency was raised accordingly.

## Open questions

The boiler was in cold standby during this validation. A natural combustion cycle and a longer stability assessment remain outstanding. REG62 scaling especially needs another synchronized Touch comparison: the earlier description and the HA scale were not consistent with one door observation. The existing scale remains until that comparison. REG56, REG68 and REG72 retain unknown semantics; earlier hypotheses are not promoted to confirmed measurements.
