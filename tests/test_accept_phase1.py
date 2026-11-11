"""Ensure acceptance distinguishes exact provenance bytes from JSON semantics."""

import importlib.util
from pathlib import Path
import tempfile
import unittest


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "accept_phase1.py"
SPEC = importlib.util.spec_from_file_location("accept_phase1", MODULE_PATH)
ACCEPTANCE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ACCEPTANCE)


class AcceptanceComparisonTests(unittest.TestCase):
    def compare(self, original: bytes, generated: bytes) -> dict:
        with tempfile.TemporaryDirectory() as temporary:
            reference, candidate = Path(temporary) / "baseline.json", Path(temporary) / "candidate.json"
            reference.write_bytes(original)
            candidate.write_bytes(generated)
            return ACCEPTANCE.compare_result(reference, candidate)

    def test_reformatted_json_is_semantically_equal_but_not_byte_identical(self):
        result = self.compare(b'{"status":"review_required","value":20.0}\n',
                              b'{\n  "value": 20.0, "status": "review_required"\n}\n')
        self.assertFalse(result["byte_equal"])
        self.assertTrue(result["all_fields_equal"])

    def test_nested_scientific_status_change_reports_its_exact_field(self):
        result = self.compare(b'{"boundaries":{"quantum_calculation":"not_performed"}}',
                              b'{"boundaries":{"quantum_calculation":"performed"}}')
        self.assertFalse(result["all_fields_equal"])
        failures = [item["path"] for item in result["field_checks"] if not item["equal"]]
        self.assertEqual(failures, ["$.boundaries.quantum_calculation"])

    def test_boolean_is_not_accepted_as_numeric_one(self):
        result = self.compare(b'{"measurements":[1]}', b'{"measurements":[true]}')
        self.assertFalse(result["all_fields_equal"])


if __name__ == "__main__":
    unittest.main()
