# Working on the Gilles integration

## Standing maintainer request

Matthias requested that this repository be kept up to date whenever we improve the Gilles integration in Home Assistant. Treat the repository update as part of each authorized Gilles change, including changes made through Home Assistant MCP.

- Read the current default-branch revision and the relevant live Gilles configuration before editing. Preserve unrelated work and existing entity identities/history.
- Update the relevant files under `home-assistant/`, register documentation, and both German and English changelogs in the same work session. New findings must state their evidence and remaining uncertainty.
- Include native helper definitions and automation changes; exporting only the YAML packages is incomplete. `home-assistant/README.md` explains the supported installation format.
- After appropriate validation, commit and push the completed changes. Routine synchronization is covered by the maintainer's request and does not need another confirmation. Use a normal fast-forward update; never force-push. If branch protection requires a pull request, use that workflow and report its status accurately.
- Finish with the GitHub commit or pull-request link and the actual validation result. Do not claim synchronization if the remote update failed.

This is a workflow requirement for integration work, not an unattended mirror of arbitrary Home Assistant edits. Do not add a polling job, publish unrelated HA configuration, or change heating controls to satisfy it.

## Source and deployment conventions

- German is primary; maintain the matching `.en.md` documentation for changed behavior.
- The deployed integration reads Modbus registers. Writing boiler registers or intentionally initiating a burner cycle requires an explicit task covering that action.
- Preserve `unique_id` and existing HA entity IDs. `home-assistant/entity_ids.json` records the reference mapping; update all consumers if an ID must change.
- `helpers.json` contains portable native helper creation parameters in dependency order. Do not commit config-entry IDs, auth data, `.storage`, live secrets, or full HA backups. Use the existing documentation address `192.0.2.1` for the boiler host.
- Keep observations separate from assumptions. The approximately three-second TCP idle close was measured on the reference installation; the two-second REG42 poll is a targeted mitigation. A short successful observation is not a long-term stability guarantee.

## Validation

Run `python3 scripts/validate_config.py` after changing HA examples. It checks entity references, helper dependencies, package names and read-only scope. Compile changed Python scripts and run focused checks for changed behavior. For a deployed HA change, also perform the relevant HA configuration check/reload and verify live states. Record any validation that could not be performed.
