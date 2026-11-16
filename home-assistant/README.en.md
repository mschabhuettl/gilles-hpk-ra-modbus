# Install and update Home Assistant

> [🇩🇪 Deutsch](README.md) · 🇬🇧 **English**

These files cover the Gilles packages and operating diagnostics updated on **Home Assistant 2026.11.1**. The original packages were validated with Home Assistant 2026.9.1. The boiler host is replaced by `192.0.2.1`; internal config-entry and automation IDs are omitted from portable definitions.

## Components

| File | Purpose |
|---|---|
| `modbus.yaml` | HA package: 40 raw sensors and seven state templates with availability checks |
| `gilles_derived.yaml` | HA package: timestamps of the last directly observed start and REG78 rising edge |
| `helpers.json` | Native helpers and one SQL sensor for the HA UI or Home Assistant MCP |
| `automations.yaml` | Four native counter/diagnostic automations to create or update individually |
| `entity_ids.json` | Entity IDs used by the examples and their YAML `unique_id` mapping |
| `dashboard.yaml` | Overview, burner, operating statistics, investigation and parameter views |

The helper JSON is **not an HA YAML package** or a `.storage` export. Installing the packages alone does not create every dashboard sensor.

## Installation

1. Copy the two package files to `packages/modbus.yaml` and `packages/gilles_derived.yaml` under the HA configuration directory. Replace the example host in `modbus.yaml`.
2. If packages are not enabled yet, merge this into the existing `homeassistant:` block:

   ```yaml
   homeassistant:
     packages: !include_dir_named packages
   ```

   Do not duplicate the `homeassistant:` block. With `!include_dir_named`, the filename becomes the package name: use an **underscore**, not `gilles-derived.yaml`.
3. Check and load the configuration. An existing integration can use the appropriate reloads (`modbus.reload`, `template.reload`); a new installation should follow HA's required setup steps.
4. Compare entity IDs with `entity_ids.json`. HA initially derives IDs from names and preserves them after renaming. A historical installation may use `sensor.gilles_rucklauftemperatur` or `_vermutet` suffixes that a new installation will not generate. On a new installation, align the IDs with the reference or update every consumer. Preserve identities and history on existing installations.
5. Create helpers from `helpers.json` **in list order** using Settings → Devices & services → Helpers. `parameters.helper_type` selects the type, `name` its name and `config` its fields. For templates, `next_step_id` selects sensor or binary sensor, while `additional_options.availability` is the availability template. Map `max_age`/`duration` to the relevant hours/days fields. Counter fields `initial`, `step`, `restore` and `icon` sit directly under `parameters`.

   With Home Assistant MCP, read its current best practices and pass each `parameters` object to the named `tool`; when omitted, use `ha_config_set_helper(action="create", ...)`. The SQL sensor uses `ha_set_integration` with `domain: sql`, or the SQL integration in the HA UI. `key`, `entity_id` and `tool` are reference metadata, not creation arguments. Resolve and update existing helpers instead of creating duplicates. Set the `Starts` or `Vorgänge` units on initial creation.
6. Create the four automations individually in the HA automation editor using `automations.yaml`. Preserve the identity when updating an existing automation. Do **not** replace the installation's entire `automations.yaml` file. The automations update HA counters and diagnostic helpers or write activity-log entries; they never write boiler registers.
7. Create a dashboard or update the existing Gilles dashboard using `dashboard.yaml` in the raw configuration editor. Adjust the displayed installation date when deploying on another system. The reference dashboard uses URL path `dashboard-gilles`.

## Migration from the previous example

The reference installation rejected the complete old `gilles-derived.yaml` package because its name was invalid. It is replaced by `gilles_derived.yaml` plus native helpers and automations. Remove the old file from the package directory. If another installation already ran it under a valid package name, inspect and migrate existing helpers/counters first to avoid duplicate entities.

All 40 raw sensors retain their addresses, data types, scales and `unique_id`. REG42 now polls every two seconds to stay below the measured TCP idle limit of approximately three seconds. The hub waits 200 ms between requests. HA 2026.9.1 sets PyModbus retries internally to three; the previous YAML `retries: 1` line did not change that value. See [operational validation](../docs/HA_VALIDATION.en.md) for evidence.

## Reading the dashboard

- Data loss appears as unavailable. Missing readings do not imply standby, a normal system state or a closed door.
- Start counters and helpers historically named ash counters require directly observed `0` to `1` transitions. Reconnection does not count as an event; events entirely inside a data gap may be missed. The ash counters count REG78 rising edges; a one-to-one relationship with physical ash discharge operations has not been confirmed.
- Counters start at installation. Initial daily, weekly and monthly periods are incomplete. Timestamps remain unknown until the first event. Newly created utility meters may also remain unknown until their first source update; do not generate artificial starts to initialize them.
- Burner-cycle time includes pre-purge and cooldown, so it is not proof of a flame. Historical durations and extrema use existing recorder data; phase-data coverage exposes missing time.
- Pellet consumption and efficiency require additional data and calibration and are not estimated here. Door detection remains indirect; uncertain register mappings/scales retain their labels.

## Synchronization and validation

Further Gilles changes must update live configuration, helper definitions, automations, dashboard and documentation on GitHub in the same work session. See [AGENTS.md](../AGENTS.md).

```bash
python3 -m pip install -r scripts/requirements-dev.txt
python3 scripts/validate_config.py
```

Back up the affected HA files and UI configurations before deployment. Check configuration and entity references, reload the relevant integrations and inspect real readings afterwards. A structurally valid dashboard is not a visual check; the initial validation had no screenshot feature available.

## Operating diagnostics (0.9.0)

The rolling start count uses directly recorded `0→1` transitions within the last 24 hours. Gaps and unrecorded events are not backfilled. Editable review thresholds remain more than 10 observed starts/24 h and startup longer than 20 minutes. They are not manufacturer fault limits.

On a valid observed start, the diagnosis still records the original boiler temperature. It also initializes `input_number.gilles_kesseltemperatur_diagnoseminimum` with that value and lowers it when valid lower readings arrive during the observed cycle. This does not overwrite the initial reading. Warm-start recovery is now measured from the recorded low point instead of requiring the boiler to exceed its warm initial temperature again.

The temperature advisory requires a directly observed start, numeric inputs, all raw readings available, current phase `6` or `7`, and more than 30 minutes since the start. **Both** temperature conditions must also hold: the rise from the diagnostic minimum is below the configured minimum rise, and the smoothed temperature trend is insufficient. Activation requires a trend below `minimum rise / 30 minutes`; an active advisory clears at or above `minimum rise / 20 minutes`. This hysteresis avoids switching around a single boundary. All activation conditions must hold continuously for five minutes (`delay_on`). When the criteria no longer hold, the advisory clears without an additional off delay.

The native derivative helper `sensor.gilles_kesseltemperatur_trend_10min` uses boiler temperature, a ten-minute smoothing window, minutes as its time unit, and recalculation at least once per minute (`max_sub_interval`). An unchanged reading therefore lets the trend decay instead of retaining an old positive slope indefinitely. The window smooths available changes; it does not prove uninterrupted communication. The diagnosis is not evidence of flame, a heat-output measurement or general stall monitoring after the required rise has been reached.

Standby, an HA restart, or a missing or nonnumeric value among all 40 raw sensors invalidates the ongoing startup diagnosis. Data recovery does not reactivate it; only the next directly observed `0→1` transition establishes a new baseline. Burnout does not trigger the temperature-rise advisory. After editing during an active cycle, invalidate the diagnosis rather than inventing an earlier start or minimum.

For migration, create the new minimum helper before updating the diagnostic automation and warning template. Existing initial-temperature, timestamp and counter helpers retain their identities and history. The diagnostic minimum is initialized at the next valid start; its provisional numeric value is meaningless without an active diagnostic baseline.

The quality tile is labeled “40 Messwerte numerisch vorhanden” (40 numeric readings present). It checks numeric values, not the age of an acknowledged Modbus response. Unchanged states and their HA timestamps are not reliable evidence of communication continuity. Register observations log the last asynchronously polled values; synchronized Touch comparisons remain necessary to verify unknown registers.

The warning sensors and dashboard do not send notifications themselves. An existing central notification automation must be enabled separately and its delivery route checked. This package does not enable unrelated notification automations.

## Statistics limits and unresolved registers

The four statistics helpers for boiler minimum, boiler maximum, flue-gas maximum and O₂ minimum now retain up to **10,000 instead of 4,000 samples**, with `max_age: 24 h` unchanged. Frequent changes can cause the sample limit to evict older values before the time window expires. The “24 h” label therefore does not guarantee a full 24 hours. Update only the existing helpers' `sampling_size` option, preserving entity IDs and history. Check `age_coverage_ratio` and `buffer_usage_ratio` again after reloading. More buffer capacity cannot replace missing source readings.

**O₂ minimum from the heating phase only:** The new source `sensor.gilles_o2_heizbetrieb` accepts a valid raw O₂ value only in phase `7` and after its state update falls after entry into that phase (`last_updated >= phase.last_changed`). This avoids immediately copying a held startup-phase value; a timestamp still does not independently prove measurement freshness. With valid inputs outside phase `7`, the template returns `none`, producing `unknown`, not a substitute zero or a held last numeric value. Invalid phase/O₂ inputs make it `unavailable`.

`sensor.gilles_o2_heizbetrieb_24h_min` evaluates only numeric source readings. It ignores `unknown`, retaining genuine heating samples during standby until `max_age: 24 h` expires. `keep_last_sample: false` prevents an expired sample from being retained indefinitely. Actual source unavailability also makes the statistic `unavailable`. Before the first qualifying heating phase, or after all samples expire, no minimum can be evaluated. The dashboard marks this state instead of inventing a number.

For migration, create the new template source, then the new statistic, and switch the dashboard to it. The unfiltered raw sensor and `sensor.gilles_o2_24h_min` remain unchanged. The new metric builds its history from installation onward; existing history is not retrospectively cleaned. Parameter labels “O₂ Min/Max” refer to targets at minimum/maximum **output**, not numerical oxygen limits; see [manufacturer context and register findings](../docs/REGISTER_FINDINGS.en.md).

**Rolling start count through SQL:** `sensor.gilles_brennstarts_24h` now counts HA Recorder rows whose state is `1` and whose predecessor, joined through `old_state_id` for the same entity, is `0`. The window is `now() - 24 h < last_updated_ts <= now()`. A phase `1` already active before the window does not count again. Transitions from `unavailable` or `unknown` to `1` are also excluded. The old `sum_differences_nonnegative` statistics helper undercounted sparse starts when its preceding counter sample aged out; that helper is no longer created.

The SQL integration reads the default Recorder database; the portable definition contains no database credentials. When `db_url` is omitted, it uses the configured Recorder connection, including an external backend. Configure a separate connection locally only when intentionally querying a different database. Recorder must include the phase sensor and retain at least the selected window plus predecessor rows. Exclusions, Recorder outages or purged history can still undercount. The query counts recorded transitions, not unobserved physical starts. The displayed value follows the SQL integration's update interval.

During migration, preserve consumers and the identity of `sensor.gilles_brennstarts_24h`. Clearly distinguish the previous statistics helper and verify the SQL sensor before removing the old definition after a dependency check. Do not purge Recorder history. Do not reset daily, weekly, monthly or lifetime counters or retrospectively overwrite them from the SQL count.

**REG78 remains a hypothesis:** Extended active intervals contradict its previous interpretation as the ash screw's immediate running state. Existing IDs containing `asche…` remain for compatibility. Their values and timestamps represent observed REG78 edges, not verified physical ash discharge operations. Further anonymized findings and pending Touch comparisons are documented in [REGISTER_FINDINGS](../docs/REGISTER_FINDINGS.en.md).

The [SQL integration](https://www.home-assistant.io/integrations/sql/) runs the new start query. The previous approach's buffer and difference semantics are documented in [Statistics](https://www.home-assistant.io/integrations/statistics/); [History Stats](https://www.home-assistant.io/integrations/history_stats/) counts state intervals with different boundary semantics.

## Touch comparison: targets, inputs and counters

The Touch actual/target page separately displays “Restsauerstoff – Ist/Soll” (oxygen actual/target), “aktuelle Einschubmenge” (current feed amount), boiler/flue targets and the blowers. It is the relevant comparison page for REG56 and the more specific REG68 feed candidate. Matching zero values in standby establish neither register identity nor scale. Current percentage conversions remain unchanged pending a nonzero comparison; no newly verified target or consumption sensor is introduced.

REG64 can be zero while Puffer/Boiler mode remains selected. Use REG44 for operating mode; do not infer “controller off” from a missing active boiler target. Thermal/motor-protection indications on the X-contact pages do not indicate motor operation; color alone does not establish contact polarity. Cleaning time parameters alone do not prove that cleaning is enabled.

The Touch “Laufzeiten” (runtimes) and “Anzahl Zündungen” (ignition count) have no established common counting or reset scope with the HA helpers. Do not overwrite or initialize HA counters from a screenshot. The SQL start count retains only the Recorder scope described above. Further limitations and the focused comparison procedure are in [REGISTER_FINDINGS](../docs/REGISTER_FINDINGS.en.md).

## Additional observed codes and data coverage

Phase `10` has been observed as a numeric state between `9` and `0`; its physical function is unresolved. The phase label states this explicitly. The cycle binary sensor, today/7-day cycle duration, observed-phase coverage and diagnostic log now include `10`. This establishes neither combustion nor a known actuator. Future unknown codes remain unavailable on the binary sensor, independently of the numeric raw phase. Existing History Stats helpers retain their IDs and recalculate from recorded raw history; old binary-sensor state history is not rewritten.

The coverage statistic counts the code values observed so far. New numeric codes can therefore look like a coverage gap even when data is being transmitted. Inspect actual `unavailable` intervals separately; rounding to one decimal place can show 100% despite short outages. Similarly, extrema statistics' `age_coverage_ratio` describes the sample time span, not uninterrupted communication. A constant source value can limit that span without filling the buffer.

Status `43` is displayed neutrally as unresolved. It has also been observed in standby and is not identified as a fault or a definite door state. The indirect door indicator remains unavailable for this code. Status `61` is only provisionally associated with “buffer temperature reached” and is labeled accordingly.

A cycle crossing midnight does not create a new start on the next day: the daily counter assigns an observed start to its start date, while cycle duration is split at the day boundary. The rolling SQL count independently uses a sliding time window; no starts are backfilled and no counters are reset.

