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

## Operating-diagnostics follow-up

On 2026-09-07, reference validation passed with 35 native helpers, four automations and 78 dashboard references. `homeassistant.check_config` succeeded. Both counter statistics units were consistent. Fourteen verified orphan entries were removed without purging Recorder. The new startup diagnostics have not yet encountered a real firing cycle during the observed standby period.


## Operating-diagnostic validation for 0.8.0

The updated diagnostics were deployed on Home Assistant 2026.10.2. The new native derivative helper is loaded. Saved templates for numeric raw-data quality and the temperature advisory, the diagnostic automation and the dashboard were read back and compared with the intended definitions. All 79 dashboard references resolve; unavailable startup duration in standby is intentional. The affected Gilles config entries are loaded, the quality indicator is active and the diagnostic automation is enabled. The configuration check completed successfully.

The existing central notification automation was not enabled. Warning sensors may appear in the dashboard; this validation does not claim successful push delivery. A notification route requires a separate check. No burner cycle was initiated and no boiler register was written.

The offline consistency check passes with 40 raw sensors, 49 YAML entities, 36 UI definitions, four automations, 79 dashboard references and five views. Ten automated tests cover the combination of start baseline, total rise and trend, numeric raw readings, diagnostic invalidation and SQL event boundaries. Eleven scenarios also passed in HA's template renderer. Python compilation and `git diff --check` passed. Scenario fixtures use synthetic values, not published operating histories.

```bash
python3 scripts/validate_config.py
python3 scripts/test_start_diagnostics.py
python3 -m py_compile scripts/test_start_diagnostics.py
```

A retrospective calculation from a private warm-start trace suppresses the new advisory using both stepwise carry-forward and linear interpolation of recorded readings. Recorder state-change history omits unchanged sensor reports, so this checks two approximations rather than replaying the HA derivative helper exactly. The trace and its operating timestamps remain private.

The log comparison found no newly added Gilles errors since deployment. Existing older template messages and the known warning about the targeted two-second polling interval do not establish a new failure. This acceptance check covers configuration and diagnostic behavior; it does not replace longer observation of natural firing cycles. Dashboard validation used configuration and entity checks, not a newly rendered screenshot.
