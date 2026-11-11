import csv
import json
import tempfile
import unittest
from pathlib import Path

from chen_research.uv_replay import ReproducibilityError, load_observations, replay


ROOT = Path(__file__).resolve().parents[1]


class ScientificBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.data = Path(self.tmp.name) / "data.csv"
        self.protocol = Path(self.tmp.name) / "protocol.json"
        self.data.write_bytes((ROOT / "data/pftb1966_table1.csv").read_bytes())
        self.protocol.write_bytes((ROOT / "protocols/pftb1966_uv.json").read_bytes())

    def tearDown(self):
        self.tmp.cleanup()

    def modify(self, fn):
        with self.data.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fields, rows = reader.fieldnames, list(reader)
        fn(rows)
        with self.data.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    def test_original_table_arithmetic_and_independent_energy_conversion(self):
        r = replay(self.data, self.protocol)
        expected = {
            ("nC3F7I", "EtOH"): (20, 2962.962963),
            ("iC3F7I", "EtOH"): (24, 3503.649635),
            ("tC4F9I", "EtOH"): (27.5, 3665.493709),
            ("nC3F7I", "Et2O"): (14, 2025.462963),
            ("iC3F7I", "Et2O"): (17, 2414.155472),
            ("tC4F9I", "Et2O"): (24, 3156.565657),
        }
        for row in r["measurements_and_derived_shifts"]:
            nm, cm = expected[row["compound_id"], row["donor_solvent"]]
            self.assertEqual(row["delta_lambda_nm"], nm)
            self.assertAlmostEqual(row["blue_shift_cm_inverse"], cm, places=5)
        self.assertTrue(all(c["matches_three_iodide_order"] for c in r["comparisons"]))
        self.assertEqual(r["boundaries"]["universal_four_group_order"], "not_tested")

    def test_fourth_iodide_cannot_be_invented_as_measured(self):
        self.modify(lambda rows: rows.append({**rows[0], "measurement_id": "fake", "compound_id": "CF3I"}))
        with self.assertRaises(ReproducibilityError):
            load_observations(self.data)

    def test_missing_pair_does_not_get_imputed(self):
        self.modify(lambda rows: rows.pop(1))
        with self.assertRaises(ReproducibilityError):
            replay(self.data, self.protocol)

    def test_duplicate_observation_rejected(self):
        self.modify(lambda rows: rows.append(rows[0]))
        with self.assertRaises(ReproducibilityError):
            load_observations(self.data)

    def test_b_not_silently_interpreted_as_benzene(self):
        self.modify(lambda rows: rows[1].update(solvent="benzene"))
        with self.assertRaises(ReproducibilityError):
            load_observations(self.data)

    def test_nonfinite_value_rejected(self):
        self.modify(lambda rows: rows[0].update(lambda_max_nm="nan"))
        with self.assertRaises(ReproducibilityError):
            load_observations(self.data)

    def test_transcription_that_misses_original_shift_rejected(self):
        self.modify(lambda rows: rows[0].update(lambda_max_nm="271.0"))
        with self.assertRaises(ReproducibilityError):
            replay(self.data, self.protocol)

    def test_rounding_cannot_be_promoted_to_experimental_uncertainty(self):
        protocol = json.loads(self.protocol.read_text())
        protocol["experimental_uncertainty_nm"] = 0.05
        self.protocol.write_text(json.dumps(protocol))
        with self.assertRaises(ReproducibilityError):
            replay(self.data, self.protocol)

    def test_wavelength_units_cannot_be_renamed_without_conversion(self):
        self.data.write_text(self.data.read_text().replace("lambda_max_nm", "lambda_max_angstrom"))
        with self.assertRaises(ReproducibilityError):
            load_observations(self.data)


if __name__ == "__main__":
    unittest.main()
