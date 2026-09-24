# Install and update Home Assistant

> [🇩🇪 Deutsch](README.md) · 🇬🇧 **English**

These files reproduce the behavior validated on the reference installation on 7 September 2026 with **Home Assistant 2026.9.1**. The boiler host is replaced by `192.0.2.1`; internal config-entry and automation IDs are omitted from portable definitions.

## Components

| File | Purpose |
|---|---|
| `modbus.yaml` | HA package: 40 raw sensors and seven state templates with availability checks |
| `gilles_derived.yaml` | HA package: timestamps of the last directly observed start and REG78 rising edge |
| `helpers.json` | 35 native helper definitions for the HA UI or Home Assistant MCP |
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

   With Home Assistant MCP, read its current best practices and pass each helper's `parameters` to `ha_config_set_helper(action="create", ...)`. `key` and `entity_id` are reference metadata, not creation arguments. Resolve and update existing helpers instead of creating duplicates. Set the `Starts` or `Vorgänge` units on initial creation.
6. Create the four automations individually in the HA automation editor using `automations.yaml`. Preserve the identity when updating an existing automation. Do **not** replace the installation's entire `automations.yaml` file. The counter automations only increment HA counters.
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

## Added operating diagnostics (0.5.0)

The existing rolling 24-hour start indicator is unreliable with sparse counter changes; see the guidance below. An inactive warning therefore does not establish a low start count. Default thresholds are more than 10 observed starts, startup longer than 20 minutes, and less than 2 °C boiler temperature rise after 30 minutes in phases 6 or 7. These are editable review thresholds, not manufacturer fault limits. Missing observations are never invented.

The diagnostic cycle is invalidated on restart, standby or missing phase data. Startup includes pre-purge and both ignition phases; burnout does not trigger the temperature-rise advisory. The two additional automations update HA helpers and write activity-log snapshots only. A synchronized Touch reading is still required to validate unclear register meanings or scaling.

The reference installation removed the orphaned REG20, 42, 46, 50, 52, 58, 60, 62, 64, 66, 68, 72, 78 and `gilles_brennraumtur_raw` entries after checking all consumers. Active renamed sensors and Recorder history were preserved. Check each installation's own references before cleanup.

## Statistics limits and unresolved registers

The four statistics helpers for boiler minimum, boiler maximum, flue-gas maximum and O₂ minimum now retain up to **10,000 instead of 4,000 samples**, with `max_age: 24 h` unchanged. Frequent changes can cause the sample limit to evict older values before the time window expires. The “24 h” label therefore does not guarantee a full 24 hours. Update only the existing helpers' `sampling_size` option, preserving entity IDs and history. Check `age_coverage_ratio` and `buffer_usage_ratio` again after reloading. More buffer capacity cannot replace missing source readings.

**Known rolling start-counter defect:** `sensor.gilles_brennstarts_24h` can miss sparse starts. `sum_differences_nonnegative` computes differences only between retained samples. After more than 24 hours without a change, the preceding counter value may be missing as a baseline; `keep_last_sample: true` retains only the newest sample. Increasing capacity does not fix this defect. Treat this helper and its frequent-start warning as unreliable until a separately validated event-counting design replaces the calculation. Daily, weekly and monthly counters remain separate and are neither reset nor artificially backfilled. Simply substituting `history_stats` on phase `1` would change window-boundary and reconnection semantics, so it is not an equivalent repair.

**REG78 remains a hypothesis:** Extended active intervals contradict its previous interpretation as the ash screw's immediate running state. Existing IDs containing `asche…` remain for compatibility. Their values and timestamps represent observed REG78 edges, not verified physical ash discharge operations. Further anonymized findings and pending Touch comparisons are documented in [REGISTER_FINDINGS](../docs/REGISTER_FINDINGS.en.md).

The buffer and difference semantics are documented in the [official Statistics documentation](https://www.home-assistant.io/integrations/statistics/); the different state-counting rather than transition-counting semantics are described in [History Stats](https://www.home-assistant.io/integrations/history_stats/).

## Touch comparison: targets, inputs and counters

The Touch actual/target page separately displays “Restsauerstoff – Ist/Soll” (oxygen actual/target), “aktuelle Einschubmenge” (current feed amount), boiler/flue targets and the blowers. It is the relevant comparison page for REG56 and the more specific REG68 feed candidate. Matching zero values in standby establish neither register identity nor scale. Current percentage conversions remain unchanged pending a nonzero comparison; no newly verified target or consumption sensor is introduced.

REG64 can be zero while Puffer/Boiler mode remains selected. Use REG44 for operating mode; do not infer “controller off” from a missing active boiler target. Thermal/motor-protection indications on the X-contact pages do not indicate motor operation; color alone does not establish contact polarity. Cleaning time parameters alone do not prove that cleaning is enabled.

The Touch “Laufzeiten” (runtimes) and “Anzahl Zündungen” (ignition count) have no established common counting or reset scope with the HA helpers. Do not overwrite or initialize HA counters from a screenshot. The known rolling 24-hour start-counter defect remains unresolved. Further limitations and the focused comparison procedure are in [REGISTER_FINDINGS](../docs/REGISTER_FINDINGS.en.md).
