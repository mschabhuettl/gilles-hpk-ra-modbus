#!/usr/bin/env python3
"""Exercise the shipped diagnostics with synthetic states and an in-memory recorder.

Run with ``python3 scripts/test_start_diagnostics.py``. These tests render the
actual helper templates and interpret the small, supported native automation
subset. They do not import Home Assistant, contact a boiler, or reproduce HA's
event queue, recorder scheduling, derivative implementation, or delay timers.
"""

from datetime import datetime, timedelta, timezone
import json
import math
from pathlib import Path
import sqlite3
from types import SimpleNamespace
import unittest

from jinja2 import StrictUndefined
from jinja2.nativetypes import NativeEnvironment
import yaml


ROOT = Path(__file__).resolve().parent.parent
HA = ROOT / "home-assistant"
NOW = datetime(2000, 1, 2, 12, tzinfo=timezone.utc)
PHASE = "sensor.gilles_brenn_phase_code"
QUALITY = "binary_sensor.gilles_messdaten_verfuegbar"
OBSERVED = "input_boolean.gilles_brennstart_beobachtet"
TEMPERATURE = "sensor.gilles_kesseltemperatur"
BASELINE = "input_number.gilles_kesseltemperatur_bei_brennstart"
DIAGNOSTIC_MIN = "input_number.gilles_kesseltemperatur_diagnoseminimum"
MINIMUM = "input_number.gilles_temperaturanstieg_mindestwert"
START = "input_datetime.gilles_letzter_brennstart"
RATE = "sensor.gilles_kesseltemperatur_trend_10min"
WARNING = "binary_sensor.gilles_temperaturanstieg_fehlt"
START_COUNT = "sensor.gilles_brennstarts_24h"


def is_number(value):
    """HA's numeric test excludes NaN and infinities, unlike float conversion."""
    try:
        return math.isfinite(float(value))
    except (ValueError, TypeError, OverflowError):
        return False


def as_timestamp(value, default=None):
    if isinstance(value, datetime):
        return value.timestamp()
    if is_number(value):
        return float(value)
    try:
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.timestamp()
    except (TypeError, ValueError):
        return default


class FakeHA:
    """Only the state access and native actions used by these shipped examples."""

    def __init__(self, states=None, now=NOW):
        self.states = dict(states or {})
        self.now = now
        self.actions = []
        self.env = NativeEnvironment(undefined=StrictUndefined)
        self.env.globals.update(
            states=self.state,
            is_state=lambda entity, state: self.state(entity) == state,
            is_number=is_number,
            has_value=lambda entity: self.state(entity) not in ("unknown", "unavailable"),
            as_timestamp=as_timestamp,
            now=lambda: self.now,
        )
        self.env.filters["states"] = self.state
        self.env.tests["is_number"] = is_number
        self.env.tests["has_value"] = self.env.globals["has_value"]

    def state(self, entity):
        return self.states.get(entity, "unknown")

    def render(self, template, **context):
        return self.env.from_string(template).render(**context)

    def binary_state(self, config, previous_state="off"):
        """Evaluate the predicate, not HA's delayed publication of its result."""
        options = config.get("additional_options", config.get("advanced_options", {}))
        availability = config.get("availability", options.get("availability"))
        if availability and not self.render(availability):
            return "unavailable"
        previous = SimpleNamespace(state=previous_state)
        return "on" if self.render(config["state"], this=previous) else "off"

    def condition(self, condition, trigger_id):
        kind = condition["condition"]
        if kind == "trigger":
            expected = condition["id"]
            return trigger_id in expected if isinstance(expected, list) else trigger_id == expected
        if kind == "state":
            expected = condition["state"]
            actual = self.state(condition["entity_id"])
            return actual in expected if isinstance(expected, list) else actual == expected
        if kind == "template":
            return bool(self.render(condition["value_template"]))
        if kind == "numeric_state":
            actual = self.state(condition["entity_id"])
            if not is_number(actual):
                return False
            for comparison in ("above", "below"):
                if comparison not in condition:
                    continue
                bound = condition[comparison]
                if not is_number(bound):
                    bound = self.state(bound)
                if not is_number(bound):
                    return False
                if comparison == "above" and not float(actual) > float(bound):
                    return False
                if comparison == "below" and not float(actual) < float(bound):
                    return False
            return True
        raise AssertionError(f"Unsupported native condition: {kind}")

    def sequence(self, actions, trigger_id):
        for action in actions:
            if "choose" in action:
                selected = action.get("default", [])
                for choice in action["choose"]:
                    if all(self.condition(c, trigger_id) for c in choice["conditions"]):
                        selected = choice["sequence"]
                        break
                self.sequence(selected, trigger_id)
                continue
            service = action["action"]
            entity = action["target"]["entity_id"]
            self.actions.append(service)
            if service == "input_boolean.turn_on":
                self.states[entity] = "on"
            elif service == "input_boolean.turn_off":
                self.states[entity] = "off"
            elif service == "input_datetime.set_datetime":
                self.states[entity] = str(self.render(action["data"]["timestamp"]))
            elif service == "input_number.set_value":
                self.states[entity] = str(self.render(action["data"]["value"]))
            else:
                raise AssertionError(f"Unexpected action in diagnostic automation: {service}")

    def state_event(self, automation, entity, value):
        old = self.state(entity)
        self.states[entity] = value
        if old == value:
            return
        for trigger in automation["triggers"]:
            if trigger["trigger"] != "state" or trigger["entity_id"] != entity:
                continue
            if "from" in trigger and trigger["from"] != old:
                continue
            expected = trigger.get("to")
            if expected is not None and value not in (expected if isinstance(expected, list) else [expected]):
                continue
            self.sequence(automation["actions"], trigger["id"])

    def restart(self, automation):
        for trigger in automation["triggers"]:
            if trigger["trigger"] == "homeassistant" and trigger["event"] == "start":
                self.sequence(automation["actions"], trigger["id"])


class StartDiagnosticsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        helpers = json.loads((HA / "helpers.json").read_text())["helpers"]
        cls.helpers = {helper["entity_id"]: helper["parameters"] for helper in helpers}
        cls.warning = cls.helpers[WARNING]["config"]
        cls.quality = cls.helpers[QUALITY]["config"]
        cls.sql = cls.helpers[START_COUNT]["config"]["query"]
        cls.automation = next(
            item for item in yaml.safe_load((HA / "automations.yaml").read_text())
            if item["alias"] == "Gilles Brennstart Diagnosebasis"
        )
        mapping = json.loads((HA / "entity_ids.json").read_text())["yaml_entities"]
        modbus = yaml.safe_load((HA / "modbus.yaml").read_text())["modbus"][0]
        cls.raw_entities = [mapping[sensor["unique_id"]] for sensor in modbus["sensors"]]

    def fixture(self, **overrides):
        states = {
            PHASE: "7", QUALITY: "on", OBSERVED: "on", TEMPERATURE: "60",
            BASELINE: "60", DIAGNOSTIC_MIN: "60", MINIMUM: "2", RATE: "0",
            START: (NOW - timedelta(minutes=31)).isoformat(),
        }
        states.update(overrides)
        return FakeHA(states)

    def test_temperature_profiles(self):
        # Public examples are deliberately synthetic; expected results are explicit.
        cases = [
            ("warm restart recovering", "69", "70", "0.4", "off"),
            ("flat after start", "60", "60", "0", "on"),
            ("still cooling", "58", "60", "-0.3", "on"),
            ("slow but sufficient recent rise", "60.5", "60", "0.1", "off"),
            ("insufficient recent rise", "60.5", "60", "0.03", "on"),
            ("minimum exactly reached", "62", "60", "0", "off"),
            ("already heated then level", "65", "60", "0", "off"),
        ]
        for name, current, baseline, rate, expected in cases:
            with self.subTest(name=name):
                ha = self.fixture(**{TEMPERATURE: current, DIAGNOSTIC_MIN: baseline, RATE: rate})
                self.assertEqual(ha.binary_state(self.warning), expected)

    def test_warning_delay_is_configured_but_not_simulated(self):
        options = self.warning["additional_options"]
        self.assertEqual(options["delay_on"], {"minutes": 5})
        self.assertEqual(options["delay_off"], {"seconds": 0})
        # HA must verify timer execution and cancellation; FakeHA evaluates only
        # the underlying predicate and cannot prove a five-minute runtime wait.

    def test_trend_hysteresis_and_immediate_temperature_recovery(self):
        ha = self.fixture(**{TEMPERATURE: "60.5", RATE: "0.08"})
        self.assertEqual(ha.binary_state(self.warning, previous_state="off"), "off")
        self.assertEqual(ha.binary_state(self.warning, previous_state="on"), "on")
        for previous_state in ("unknown", "unavailable"):
            self.assertEqual(ha.binary_state(self.warning, previous_state=previous_state), "off")
        ha.states[RATE] = "0.1"
        self.assertEqual(ha.binary_state(self.warning, previous_state="on"), "off")
        ha.states[RATE] = "0.06"
        self.assertEqual(ha.binary_state(self.warning, previous_state="off"), "on")
        ha.states[TEMPERATURE] = "62"
        self.assertEqual(ha.binary_state(self.warning, previous_state="on"), "off")
        ha.states[TEMPERATURE] = "60"
        self.assertTrue(ha.render(self.warning["state"]))  # Safe with no `this` context.

    def test_configurable_minimum_affects_both_criteria(self):
        ha = self.fixture(**{TEMPERATURE: "60.5", MINIMUM: "6", RATE: "0.1"})
        self.assertEqual(ha.binary_state(self.warning), "on")
        ha.states[MINIMUM] = "2"
        self.assertEqual(ha.binary_state(self.warning), "off")

    def test_phase_and_elapsed_time_boundaries(self):
        for phase in ("0", "1", "3", "5", "8", "9", "10", "unknown", "unavailable"):
            with self.subTest(phase=phase):
                self.assertEqual(self.fixture(**{PHASE: phase}).binary_state(self.warning), "off")
        for phase in ("6", "7"):
            for seconds, expected in ((1799, "off"), (1800, "off"), (1801, "on")):
                with self.subTest(phase=phase, seconds=seconds):
                    ha = self.fixture(**{PHASE: phase, START: (NOW - timedelta(seconds=seconds)).isoformat()})
                    self.assertEqual(ha.binary_state(self.warning), expected)
        self.assertEqual(self.fixture(**{OBSERVED: "off"}).binary_state(self.warning), "off")
        self.assertEqual(self.fixture(**{START: (NOW + timedelta(minutes=1)).isoformat()}).binary_state(self.warning), "off")

    def test_invalid_inputs_are_not_reported_as_healthy_or_as_an_alarm(self):
        for entity in (TEMPERATURE, DIAGNOSTIC_MIN, MINIMUM, RATE):
            for value in ("unknown", "unavailable", "bad", "nan", "inf", "-inf"):
                with self.subTest(entity=entity, value=value):
                    self.assertEqual(self.fixture(**{entity: value}).binary_state(self.warning), "unavailable")
        for value in ("unknown", "unavailable", "not-a-date"):
            self.assertEqual(self.fixture(**{START: value}).binary_state(self.warning), "unavailable")
        self.assertEqual(self.fixture(**{QUALITY: "off"}).binary_state(self.warning), "unavailable")

    def test_each_raw_sensor_is_required_and_must_be_numeric(self):
        self.assertEqual(len(self.raw_entities), 40)
        states = dict.fromkeys(self.raw_entities, "0")
        ha = FakeHA(states)
        self.assertEqual(ha.binary_state(self.quality), "on")
        for entity in self.raw_entities:
            for value in ("unknown", "unavailable", "bad", "nan", "inf", "-inf"):
                with self.subTest(entity=entity, value=value):
                    ha.states[entity] = value
                    self.assertEqual(ha.binary_state(self.quality), "off")
            del ha.states[entity]
            self.assertEqual(ha.binary_state(self.quality), "off")
            ha.states[entity] = "0"
        self.assertEqual(ha.binary_state(self.quality), "on")

    def test_data_loss_latches_until_a_new_observed_start(self):
        for lost in ("off", "unknown", "unavailable"):
            with self.subTest(lost=lost):
                ha = self.fixture(**{PHASE: "0", OBSERVED: "off"})
                ha.state_event(self.automation, PHASE, "1")
                self.assertEqual(ha.state(OBSERVED), "on")
                self.assertEqual(float(ha.state(BASELINE)), 60)
                self.assertEqual(float(ha.state(DIAGNOSTIC_MIN)), 60)
                self.assertEqual(float(ha.state(START)), NOW.timestamp())
                ha.state_event(self.automation, PHASE, "7")
                ha.state_event(self.automation, QUALITY, lost)
                self.assertEqual(ha.state(OBSERVED), "off")
                ha.state_event(self.automation, QUALITY, "on")
                self.assertEqual(ha.state(OBSERVED), "off")
                ha.state_event(self.automation, PHASE, "0")
                ha.state_event(self.automation, PHASE, "1")
                self.assertEqual(ha.state(OBSERVED), "on")

    def test_phase_loss_restart_and_invalid_start_clear_observation(self):
        for phase in ("0", "unknown", "unavailable"):
            ha = self.fixture()
            ha.state_event(self.automation, PHASE, phase)
            self.assertEqual(ha.state(OBSERVED), "off")
        ha = self.fixture()
        ha.restart(self.automation)
        self.assertEqual(ha.state(OBSERVED), "off")
        ha = self.fixture(**{PHASE: "0", QUALITY: "off"})
        ha.state_event(self.automation, PHASE, "1")
        self.assertEqual(ha.state(OBSERVED), "off")
        ha = self.fixture(**{PHASE: "unavailable", OBSERVED: "off"})
        ha.state_event(self.automation, PHASE, "1")
        self.assertEqual(ha.state(OBSERVED), "off")

    def test_start_initializes_both_temperatures_before_arming(self):
        ha = self.fixture(**{PHASE: "0", OBSERVED: "off", TEMPERATURE: "70", DIAGNOSTIC_MIN: "45"})
        ha.state_event(self.automation, PHASE, "1")
        self.assertEqual(float(ha.state(BASELINE)), 70)
        self.assertEqual(float(ha.state(DIAGNOSTIC_MIN)), 70)
        self.assertEqual(ha.actions, [
            "input_datetime.set_datetime", "input_number.set_value",
            "input_number.set_value", "input_boolean.turn_on",
        ])

    def test_minimum_tracks_a_warm_start_dip_even_after_phase_seven(self):
        ha = self.fixture(**{PHASE: "0", OBSERVED: "off", TEMPERATURE: "70"})
        ha.state_event(self.automation, PHASE, "1")
        ha.state_event(self.automation, PHASE, "3")
        ha.state_event(self.automation, TEMPERATURE, "59")
        ha.state_event(self.automation, PHASE, "7")
        ha.state_event(self.automation, TEMPERATURE, "56")
        self.assertEqual(float(ha.state(DIAGNOSTIC_MIN)), 56)
        for value in ("56", "57", "59"):
            ha.state_event(self.automation, TEMPERATURE, value)
            self.assertEqual(ha.state(OBSERVED), "on")
            self.assertEqual(float(ha.state(DIAGNOSTIC_MIN)), 56)
            self.assertEqual(float(ha.state(BASELINE)), 70)
        ha.now += timedelta(minutes=31)
        self.assertEqual(ha.binary_state(self.warning), "off")

    def test_cooling_then_no_meaningful_rise_still_warns(self):
        for final_value in ("56", "57"):
            with self.subTest(final_value=final_value):
                ha = self.fixture(**{PHASE: "0", OBSERVED: "off", TEMPERATURE: "70"})
                ha.state_event(self.automation, PHASE, "1")
                ha.state_event(self.automation, PHASE, "7")
                ha.state_event(self.automation, TEMPERATURE, "56")
                ha.state_event(self.automation, TEMPERATURE, final_value)
                ha.now += timedelta(minutes=31)
                self.assertEqual(ha.binary_state(self.warning), "on")

    def test_ignored_temperature_updates_do_not_reset_or_rearm(self):
        ha = self.fixture()
        for value in ("60.5", "61", "60.1"):
            ha.state_event(self.automation, TEMPERATURE, value)
            self.assertEqual(ha.state(OBSERVED), "on")
            self.assertEqual(float(ha.state(DIAGNOSTIC_MIN)), 60)
        self.assertEqual(ha.actions, [])
        ha.states[OBSERVED] = "off"
        ha.state_event(self.automation, TEMPERATURE, "55")
        self.assertEqual(ha.state(OBSERVED), "off")
        self.assertEqual(float(ha.state(DIAGNOSTIC_MIN)), 60)
        self.assertEqual(ha.actions, [])

    def test_corrupt_temperature_or_minimum_invalidates_until_new_start(self):
        for entity in (TEMPERATURE, DIAGNOSTIC_MIN):
            for invalid in ("unknown", "unavailable", "bad", "nan", "inf", "-inf"):
                with self.subTest(entity=entity, invalid=invalid):
                    ha = self.fixture()
                    if entity == DIAGNOSTIC_MIN:
                        ha.states[DIAGNOSTIC_MIN] = invalid
                        ha.state_event(self.automation, TEMPERATURE, "59")
                    else:
                        ha.state_event(self.automation, TEMPERATURE, invalid)
                    self.assertEqual(ha.state(OBSERVED), "off")
                    ha.state_event(self.automation, TEMPERATURE, "58")
                    self.assertEqual(ha.state(OBSERVED), "off")
                    ha.state_event(self.automation, PHASE, "0")
                    ha.state_event(self.automation, PHASE, "1")
                    self.assertEqual(ha.state(OBSERVED), "on")
                    self.assertEqual(float(ha.state(BASELINE)), 58)
                    self.assertEqual(float(ha.state(DIAGNOSTIC_MIN)), 58)

    def test_invalid_temperature_at_start_does_not_arm_with_stale_quality(self):
        for invalid in ("unknown", "unavailable", "bad", "nan", "inf", "-inf"):
            with self.subTest(invalid=invalid):
                ha = self.fixture(**{PHASE: "0", TEMPERATURE: invalid, QUALITY: "on"})
                ha.state_event(self.automation, PHASE, "1")
                self.assertEqual(ha.state(OBSERVED), "off")
                self.assertEqual(ha.actions, ["input_boolean.turn_off"])

    def test_minimum_helper_restores_without_an_initial_override(self):
        helper = self.helpers[DIAGNOSTIC_MIN]
        self.assertEqual(helper["min_value"], -20)
        self.assertEqual(helper["max_value"], 150)
        self.assertEqual(helper["step"], 0.1)
        self.assertNotIn("initial", helper)

    def count_starts(self, transitions, now=NOW):
        with sqlite3.connect(":memory:") as database:
            database.executescript(
                "CREATE TABLE states_meta (metadata_id INTEGER, entity_id TEXT);"
                "CREATE TABLE states (state_id INTEGER PRIMARY KEY, metadata_id INTEGER, "
                "state TEXT, old_state_id INTEGER, last_updated_ts REAL);"
            )
            database.executemany("INSERT INTO states_meta VALUES (?, ?)", [(1, PHASE), (2, "sensor.unrelated")])
            for index, (old, new, timestamp, metadata, previous_metadata) in enumerate(transitions):
                previous_id = index * 2 + 1
                database.execute("INSERT INTO states VALUES (?, ?, ?, NULL, ?)",
                                 (previous_id, previous_metadata, old, timestamp - 1))
                database.execute("INSERT INTO states VALUES (?, ?, ?, ?, ?)",
                                 (previous_id + 1, metadata, new, previous_id, timestamp))
            result = database.execute(str(FakeHA(now=now).render(self.sql))).fetchone()
            return result[0]

    def test_sql_counts_only_direct_phase_starts(self):
        timestamp = NOW.timestamp() - 60
        transitions = [
            ("0", "1", timestamp, 1, 1),
            ("unavailable", "1", timestamp, 1, 1),
            ("unknown", "1", timestamp, 1, 1),
            ("1", "1", timestamp, 1, 1),
            ("7", "1", timestamp, 1, 1),
            ("0", "1", timestamp, 2, 2),
            ("0", "1", timestamp, 1, 2),
        ]
        self.assertEqual(self.count_starts(transitions), 1)

    def test_sql_rolling_window_boundaries(self):
        end = NOW.timestamp()
        transitions = [("0", "1", end + offset, 1, 1) for offset in (-86401, -86400, -86399, 0, 1)]
        self.assertEqual(self.count_starts(transitions), 2)
        self.assertEqual(self.count_starts([]), 0)

    def test_sql_midnight_does_not_create_an_additional_start(self):
        now = NOW.replace(hour=0, minute=1)
        before_midnight = now.timestamp() - 360
        after_midnight = now.timestamp() - 30
        self.assertEqual(self.count_starts([
            ("0", "1", before_midnight, 1, 1),
            ("1", "1", after_midnight, 1, 1),
        ], now=now), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
