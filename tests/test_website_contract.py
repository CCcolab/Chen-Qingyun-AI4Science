"""Regression checks for the fixed, review-only PF1966 website export contract."""

import csv
import hashlib
import json
import math
import re
import tempfile
import unittest
from pathlib import Path

from chen_research.uv_replay import replay, write_outputs


ROOT = Path(__file__).resolve().parents[1]
AUTHORS = ["陈庆云", "蒋锡夔", "陈秉启", "梁梦兰"]
FORMULAS = {"nC3F7I": "C3F7I", "iC3F7I": "C3F7I", "tC4F9I": "C4F9I"}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


class WebsiteContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.output = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.output.cleanup)
        cls.generated_result = replay(
            ROOT / "data/pftb1966_table1.csv", ROOT / "protocols/pftb1966_uv.json"
        )
        write_outputs(cls.generated_result, Path(cls.output.name))
        cls.candidates = (
            read_json(ROOT / "results/website-candidate.json"),
            read_json(Path(cls.output.name) / "website-candidate.json"),
        )
        cls.full_results = (
            read_json(ROOT / "results/pftb1966-uv-replay.json"),
            cls.generated_result,
        )
        cls.protocol = read_json(ROOT / "protocols/pftb1966_uv.json")
        cls.sources = read_json(ROOT / "data/sources.json")["sources"]

    def test_candidate_cannot_promote_engineering_success_to_scientific_approval(self):
        for candidate, full in zip(self.candidates, self.full_results):
            with self.subTest(candidate=candidate["task_id"]):
                self.assertEqual(candidate["task_id"], "PF1966-UV-T1")
                self.assertEqual(candidate["result_type"], "published_table_numerical_replay")
                self.assertEqual(candidate["publication_status"], "review_required")
                self.assertEqual(full["scientific_review_status"], "review_required")
                self.assertEqual(candidate["task_id"], full["task_id"])

    def test_stable_source_reference_resolves_and_preserves_original_attribution(self):
        sources_by_id = {source["source_id"]: source for source in self.sources}
        self.assertEqual(len(sources_by_id), len(self.sources))
        for candidate in self.candidates:
            self.assertEqual(candidate["source_ids"], ["PF01"])
            source = sources_by_id[candidate["source_ids"][0]]
            self.assertEqual(source["authors"], AUTHORS)
            self.assertEqual(source["year"], 1966)
            self.assertEqual(source["url"], self.protocol["source_url"])
            self.assertEqual(source["cached_pdf_sha256"], self.protocol["source_pdf_sha256"])
        self.assertEqual(self.protocol["source_id"], "PF01")
        self.assertEqual(self.protocol["original_authors"], AUTHORS)
        self.assertEqual(self.protocol["location"], {"pdf_page": 4, "printed_page": 21, "table": 1})

    def test_rows_preserve_isomer_identity_and_exact_donor_coverage(self):
        expected_pairs = {(compound, donor) for compound in FORMULAS for donor in ("EtOH", "Et2O")}
        for candidate in self.candidates:
            rows = candidate["numeric_summary"]
            self.assertEqual(len(rows), 6)
            self.assertEqual({(row["compound_id"], row["donor_solvent"]) for row in rows}, expected_pairs)
            for row in rows:
                self.assertEqual(row["formula"], FORMULAS[row["compound_id"]])
                self.assertEqual(row["baseline_solvent"], "C6H14")
                for name in ("lambda_h_nm", "lambda_b_nm", "delta_lambda_nm", "blue_shift_cm_inverse"):
                    self.assertTrue(math.isfinite(row[name]))

    def test_original_measurement_ids_remain_unique_and_map_to_each_exported_pair(self):
        with (ROOT / "data/pftb1966_table1.csv").open(encoding="utf-8", newline="") as handle:
            observations = list(csv.DictReader(handle))
        by_id = {row["measurement_id"]: row for row in observations}
        self.assertEqual(len(by_id), len(observations))
        self.assertEqual(set(by_id), {f"UV{index:02d}" for index in range(1, 11)})
        mapping = {
            ("nC3F7I", "EtOH"): ("UV01", "UV02"),
            ("nC3F7I", "Et2O"): ("UV01", "UV03"),
            ("iC3F7I", "EtOH"): ("UV04", "UV05"),
            ("iC3F7I", "Et2O"): ("UV04", "UV06"),
            ("tC4F9I", "EtOH"): ("UV07", "UV09"),
            ("tC4F9I", "Et2O"): ("UV07", "UV10"),
        }
        for candidate in self.candidates:
            for row in candidate["numeric_summary"]:
                baseline_id, donor_id = mapping[row["compound_id"], row["donor_solvent"]]
                baseline, donor = by_id[baseline_id], by_id[donor_id]
                self.assertEqual(baseline["compound_id"], row["compound_id"])
                self.assertEqual(donor["compound_id"], row["compound_id"])
                self.assertEqual(baseline["solvent"], "C6H14")
                self.assertEqual(donor["solvent"], row["donor_solvent"])
                self.assertEqual(float(baseline["lambda_max_nm"]), row["lambda_h_nm"])
                self.assertEqual(float(donor["lambda_max_nm"]), row["lambda_b_nm"])
                self.assertEqual(baseline["source_id"], "PF01")
                self.assertEqual(donor["source_id"], "PF01")
        self.assertEqual((by_id["UV08"]["compound_id"], by_id["UV08"]["solvent"]), ("tC4F9I", "CCl4"))

    def test_all_scientific_boundaries_survive_export(self):
        required = {
            "new_experiment": "not_performed",
            "raw_spectrum_refitting": "not_performed",
            "quantum_calculation": "not_performed",
            "reaction_mechanism": "not_tested",
            "free_anion_detection": "not_tested",
            "universal_four_group_order": "not_tested",
            "novel_chemistry": "not_claimed",
            "unmeasured_iodides": ["C2F5I", "CF3I"],
        }
        for candidate, full in zip(self.candidates, self.full_results):
            self.assertEqual(candidate["boundaries"], full["boundaries"])
            for key, value in required.items():
                self.assertEqual(candidate["boundaries"][key], value)
            self.assertTrue(candidate["boundaries"]["entity_warning"])
            self.assertTrue(candidate["boundaries"]["phase1_status"])

    def test_rounding_intervals_retain_their_nonexperimental_context(self):
        for candidate, full in zip(self.candidates, self.full_results):
            self.assertIsNone(full["experimental_uncertainty_nm"])
            self.assertEqual(full["display_rounding_assumption"]["half_width_nm"], 0.05)
            self.assertIn("不是仪器精度、测量误差或置信区间", full["display_rounding_assumption"]["interpretation"])
            self.assertEqual(candidate["numeric_summary"], full["measurements_and_derived_shifts"])
            for row in candidate["numeric_summary"]:
                for metric in ("delta_lambda_nm", "blue_shift_cm_inverse"):
                    lo, hi = row["display_rounding_intervals"][metric]
                    self.assertLess(lo, row[metric])
                    self.assertLess(row[metric], hi)

    def test_candidate_fingerprints_match_actual_inputs_and_paired_result(self):
        actual = {
            "data_sha256": hashlib.sha256((ROOT / "data/pftb1966_table1.csv").read_bytes()).hexdigest(),
            "code_sha256": hashlib.sha256((ROOT / "chen_research/uv_replay.py").read_bytes()).hexdigest(),
        }
        for candidate, full in zip(self.candidates, self.full_results):
            for name, digest in actual.items():
                self.assertTrue(re.fullmatch(r"[0-9a-f]{64}", candidate[name]))
                self.assertEqual(candidate[name], digest)
                self.assertEqual(candidate[name], full[name])
            self.assertEqual(full["source_pdf_sha256"], self.protocol["source_pdf_sha256"])


if __name__ == "__main__":
    unittest.main()
