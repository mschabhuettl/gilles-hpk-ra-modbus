#!/usr/bin/env python3
"""Check cross-file consistency of the public Home Assistant examples offline."""

import json
from pathlib import Path
import re
import sys

import yaml

ROOT = Path(__file__).resolve().parent.parent
HA = ROOT / 'home-assistant'
ENTITY = re.compile(r'\b(?:sensor|binary_sensor|counter|automation|input_boolean|input_number|input_datetime|timer)\.[a-z0-9_]+\b')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def refs(value):
    if isinstance(value, dict):
        return set().union(*(refs(child) for key, child in value.items() if key not in {'action', 'service'}))
    if isinstance(value, list):
        return set().union(*(refs(child) for child in value))
    return set(ENTITY.findall(value)) if isinstance(value, str) else set()


def template_entities(config):
    for group in config.get('template', []):
        for kind in ('sensor', 'binary_sensor'):
            yield from group.get(kind, [])


def dictionaries(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from dictionaries(child)
    elif isinstance(value, list):
        for child in value:
            yield from dictionaries(child)


def main():
    modbus = yaml.safe_load((HA / 'modbus.yaml').read_text())
    derived = yaml.safe_load((HA / 'gilles_derived.yaml').read_text())
    dashboard = yaml.safe_load((HA / 'dashboard.yaml').read_text())
    automations = yaml.safe_load((HA / 'automations.yaml').read_text())
    helpers = json.loads((HA / 'helpers.json').read_text())['helpers']
    mapping = json.loads((HA / 'entity_ids.json').read_text())

    require(not (HA / 'gilles-derived.yaml').exists(), 'Obsolete invalid package filename remains')
    for filename in ('modbus.yaml', 'gilles_derived.yaml'):
        require(re.fullmatch(r'[a-z0-9_]+', Path(filename).stem), f'Invalid package name: {filename}')

    require(len(modbus['modbus']) == 1, 'Expected one documented Gilles hub')
    hub = modbus['modbus'][0]
    require(hub['host'] == '192.0.2.1', 'Public example must use the documentation host')
    require(not set(hub) & {'switches', 'climates', 'fans', 'covers', 'lights'}, 'Examples must remain read-only')
    sensors = hub['sensors']
    require(sorted(s['address'] for s in sensors) == list(range(0, 80, 2)), 'Incomplete/duplicate register map')
    require(all(s['data_type'] == 'int32' and s['input_type'] == 'holding' and s['slave'] == 1 for s in sensors), 'Unexpected Modbus decoding or request type')
    require(all('availability' in s for s in template_entities(modbus)), 'State template lacks availability handling')

    yaml_entities = sensors + list(template_entities(modbus)) + list(template_entities(derived))
    unique_ids = [s['unique_id'] for s in yaml_entities]
    require(len(unique_ids) == len(set(unique_ids)), 'Duplicate YAML unique_id')
    require(set(unique_ids) == set(mapping['yaml_entities']), 'YAML identity map is incomplete or stale')
    helper_keys = [h['key'] for h in helpers]
    require(len(helper_keys) == len(set(helper_keys)), 'Duplicate helper key')
    require({h['key']: h['entity_id'] for h in helpers} == mapping['helpers'], 'Helper identity map is stale')
    require({a['alias'] for a in automations} == set(mapping['automations']), 'Automation identity map is stale')

    ids = list(mapping['yaml_entities'].values()) + list(mapping['helpers'].values()) + list(mapping['automations'].values())
    require(len(ids) == len(set(ids)), 'Duplicate entity_id across definitions')
    known = set(ids)
    for name, value in [('modbus', modbus), ('derived', derived), ('dashboard', dashboard), ('automations', automations), ('helpers', helpers)]:
        require(not refs(value) - known, f'{name}: undefined entities: {sorted(refs(value) - known)}')

    available = set(mapping['yaml_entities'].values())
    for helper in helpers:
        dependencies = refs(helper['parameters'])
        require(not dependencies - available, f"{helper['key']}: helper dependency created too late: {sorted(dependencies - available)}")
        available.add(helper['entity_id'])

    for item in dictionaries(automations):
        action = item.get('action', item.get('service', ''))
        require(not isinstance(action, str) or not action.startswith('modbus.write'), 'Automation writes boiler registers')

    paths = [view['path'] for view in dashboard['views']]
    require(len(paths) == len(set(paths)), 'Duplicate dashboard view path')
    for file in ROOT.rglob('*.md'):
        for target in re.findall(r'\[[^\]]*\]\(([^)\s]+)\)', file.read_text()):
            if '://' in target or target.startswith(('#', 'mailto:')):
                continue
            local = target.split('#', 1)[0]
            require((file.parent / local).exists(), f'{file.relative_to(ROOT)}: broken link: {target}')

    print(json.dumps({'status': 'passed', 'raw_sensors': len(sensors), 'yaml_entities': len(yaml_entities), 'helpers': len(helpers), 'automations': len(automations), 'dashboard_references': len(refs(dashboard)), 'views': len(paths)}, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (KeyError, ValueError, OSError) as error:
        print(f'Validation failed: {error}', file=sys.stderr)
        sys.exit(1)
