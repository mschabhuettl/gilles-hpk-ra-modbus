# Install and update Home Assistant

> [🇩🇪 Deutsch](README.md) · 🇬🇧 **English**

These files reproduce the behavior validated on the reference installation on 7 September 2026 with **Home Assistant 2026.9.1**. The boiler host is replaced by `192.0.2.1`; internal config-entry and automation IDs are omitted from portable definitions.

## Components

| File | Purpose |
|---|---|
| `modbus.yaml` | HA package: 40 raw sensors and seven state templates with availability checks |
| `gilles_derived.yaml` | HA package: timestamps of the last directly observed start and ash discharge |
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
- Start and ash counters require directly observed `0` to `1` transitions. Reconnection does not count as an event; events entirely inside a data gap may be missed.
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

The rolling 24-hour buffer of observed counter changes provides an advisory start-frequency indicator. Default thresholds are more than 10 observed starts, startup longer than 20 minutes, and less than 2 °C boiler temperature rise after 30 minutes in phases 6 or 7. These are editable review thresholds, not manufacturer fault limits. Missing observations are never invented.

The diagnostic cycle is invalidated on restart, standby or missing phase data. Startup includes pre-purge and both ignition phases; burnout does not trigger the temperature-rise advisory. The two additional automations update HA helpers and write activity-log snapshots only. A synchronized Touch reading is still required to validate unclear register meanings or scaling.

The reference installation removed the orphaned REG20, 42, 46, 50, 52, 58, 60, 62, 64, 66, 68, 72, 78 and `gilles_brennraumtur_raw` entries after checking all consumers. Active renamed sensors and Recorder history were preserved. Check each installation's own references before cleanup.
