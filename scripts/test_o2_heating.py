#!/usr/bin/env python3
"""Render the shipped phase-filtered O2 helper with synthetic state timestamps.

This checks the source predicate and statistics configuration. It does not
simulate Home Assistant's recorder, statistics buffer, or asynchronous polling.
"""

from datetime import timedelta
import json
from types import SimpleNamespace
import unittest

from test_start_diagnostics import FakeHA, HA, NOW, PHASE


O2 = "sensor.gilles_o2_ist"
FILTERED = "sensor.gilles_o2_heizbetrieb"
STATISTICS = "sensor.gilles_o2_heizbetrieb_24h_min"


class StateAccessor:
    """Supply both states('id') and the two state objects used for timestamps."""

    def __init__(self, ha, phase_changed, source_updated):
        self.ha = ha
        self.sensor = SimpleNamespace(
            gilles_brenn_phase_code=SimpleNamespace(
                state=ha.state(PHASE), last_changed=phase_changed,
            ),
            gilles_o2_ist=SimpleNamespace(
                state=ha.state(O2), last_updated=source_updated,
            ),
        )

    def __call__(self, entity):
        return self.ha.state(entity)


class HeatingO2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        entries = json.loads((HA / "helpers.json").read_text())["helpers"]
        cls.helpers = {entry["entity_id"]: entry for entry in entries}
        cls.source = cls.helpers[FILTERED]["parameters"]["config"]
        cls.statistics = cls.helpers[STATISTICS]["parameters"]["config"]

    def evaluate(self, phase="7", value="9.5", source_age=0):
        ha = FakeHA({PHASE: phase, O2: value})
        ha.env.globals["states"] = StateAccessor(
            ha, phase_changed=NOW, source_updated=NOW - timedelta(seconds=source_age),
        )
        available = ha.render(self.source["additional_options"]["availability"])
        return "unavailable" if not available else ha.render(self.source["state"])

    def test_valid_heating_samples_include_boundary_values(self):
        for value in ("0", "1", "9.5", "21"):
            with self.subTest(value=value):
                self.assertEqual(self.evaluate(value=value), float(value))

    def test_other_known_phases_produce_no_numeric_sample(self):
        # `none` becomes unknown in HA. It is deliberately not unavailable,
        # so the statistics helper can retain its previous in-window samples.
        for phase in ("0", "1", "3", "5", "6", "8", "9", "10"):
            with self.subTest(phase=phase):
                self.assertIsNone(self.evaluate(phase=phase))

    def test_invalid_phase_or_value_marks_source_unavailable(self):
        for phase in ("unknown", "unavailable", "invalid", "99"):
            self.assertEqual(self.evaluate(phase=phase), "unavailable")
        for value in ("unknown", "unavailable", "bad", "nan", "inf", "-inf", "-0.1", "21.1"):
            with self.subTest(value=value):
                self.assertEqual(self.evaluate(value=value), "unavailable")

    def test_previous_phase_sample_is_not_reused_at_heating_entry(self):
        self.assertIsNone(self.evaluate(source_age=1))
        self.assertEqual(self.evaluate(source_age=0), 9.5)
        self.assertEqual(self.evaluate(source_age=-1), 9.5)

    def test_statistics_uses_filtered_source_without_extending_expired_samples(self):
        self.assertEqual(self.statistics["entity_id"], FILTERED)
        self.assertEqual(self.statistics["state_characteristic"], "value_min")
        self.assertEqual(self.statistics["max_age"], {"hours": 24})
        self.assertFalse(self.statistics["keep_last_sample"])
        self.assertEqual(self.statistics["sampling_size"], 10000)
        self.assertEqual(self.source["state_class"], "measurement")
        self.assertIn("sensor.gilles_o2_24h_min", self.helpers)


if __name__ == "__main__":
    unittest.main(verbosity=2)
