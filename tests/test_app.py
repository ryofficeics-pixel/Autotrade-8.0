import json
from pathlib import Path
import tempfile
import unittest

from autotrade8.app import SAMPLE, build_report, load_events, parse_event


class AppTests(unittest.TestCase):
    def test_sample_is_explicitly_synthetic_and_fail_closed(self):
        events, source = load_events(None)
        report = build_report(events, source, max_age_ns=1_000_000_000,
                              max_clock_skew_ns=500_000_000)
        self.assertIn("SYNTHETIC", report["source"])
        self.assertEqual([x["reason"] for x in report["events"]],
                         ["DATA_OK", "DATA_OK", "DATA_SEQUENCE_GAP"])
        self.assertFalse(report["entry_allowed"])
        self.assertFalse(report["trading_enabled"])
        json.dumps(report)

    def test_input_rejects_unknown_fields_and_malformed_line(self):
        with self.assertRaisesRegex(ValueError, "unknown"):
            parse_event({**SAMPLE[0], "live": True})
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "fixture.ndjson"
            path.write_text(json.dumps(SAMPLE[0]) + "\nnot-json\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "line 2"):
                load_events(path)

    def test_out_of_order_arrival_blocks(self):
        events = [parse_event(SAMPLE[0]), parse_event({**SAMPLE[1],
                  "receive_monotonic_ns": SAMPLE[0]["receive_monotonic_ns"] - 1})]
        report = build_report(events, "fixture", max_age_ns=1_000_000_000,
                              max_clock_skew_ns=500_000_000)
        self.assertFalse(report["entry_allowed"])
        self.assertEqual(report["events"][-1]["reason"], "DATA_MONOTONIC_ROLLBACK")


if __name__ == "__main__":
    unittest.main()
