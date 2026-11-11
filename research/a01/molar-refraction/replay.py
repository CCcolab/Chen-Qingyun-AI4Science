"""Reconstruct a physical-property relation from visually read 1960 observations.

This is neither a new experiment nor a quantum calculation. The source's printed
found MR and calculated MR remain separate from the present reconstruction.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PDF_SHA256 = "fc88042708adc563e5cc6910aa4e3e05c32f52e9055480f980fef50d9e278b87"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def formula_mass(formula, masses):
    parts = re.findall(r"([A-Z][a-z]?)([0-9]*)", formula)
    if "".join(a + n for a, n in parts) != formula or any(a not in masses for a, _ in parts):
        raise ValueError("Unknown or invalid molecular formula")
    return sum(masses[a] * (int(n) if n else 1) for a, n in parts)


def refractivity(n, mass, density):
    return (n * n - 1) / (n * n + 2) * mass / density


def run():
    protocol_path, csv_path = HERE / "protocol.json", HERE / "observations.csv"
    protocol = json.loads(protocol_path.read_text("utf-8"))
    if digest(csv_path) != protocol["observations_sha256"]:
        raise ValueError("Observation bytes changed; create a reviewed new data/protocol version")
    if protocol["source_pdf_sha256"] != PDF_SHA256:
        raise ValueError("Unexpected source PDF fingerprint")
    pdf = ROOT / protocol["source_pdf_local_path"]
    source_check = {"status": "not_reverified_in_this_execution", "registered_sha256": PDF_SHA256}
    if pdf.is_file():
        actual = digest(pdf)
        if actual != PDF_SHA256:
            raise ValueError("Local original PDF fingerprint does not match")
        source_check.update(status="local_file_sha256_verified", actual_sha256=actual, bytes=pdf.stat().st_size)
    with csv_path.open(encoding="utf-8", newline="") as stream:
        observations = list(csv.DictReader(stream))
    if [o["compound_id"] for o in observations] != ["I", "II", "III", "IV", "V"]:
        raise ValueError("Expected the five visually transcribed compounds in fixed order")
    rows = []
    u = protocol["display_rounding_diagnostic"]["n_and_density_half_width"]
    printed_u = protocol["display_rounding_diagnostic"]["printed_MR_half_width"]
    for o in observations:
        n, d = float(o["n_D"]), float(o["relative_density"])
        found, calculated = float(o["printed_found_MR_cm3_mol"]), float(o["printed_calculated_MR_cm3_mol"])
        if not all(math.isfinite(v) for v in (n, d, found, calculated)) or n <= 1 or d <= u:
            raise ValueError("Unqualified physical-property input")
        mixed = o["n_temperature_C"] != o["density_temperature_C"]
        row = {"compound_id": o["compound_id"], "formula_used": o["formula"],
               "printed_page": int(o["printed_page"]), "source_region": o["source_region"],
               "reported_n_D": n, "n_temperature_C": float(o["n_temperature_C"]),
               "reported_relative_density": d, "density_temperature_C": float(o["density_temperature_C"]),
               "reference_water_temperature_C": float(o["reference_water_temperature_C"]),
               "printed_found_MR_cm3_mol": found, "printed_calculated_MR_cm3_mol": calculated,
               "mixed_measurement_temperature": mixed,
               "interpretation_scope": "mixed_temperature_conditional_value" if mixed else "same_temperature_input_reconstruction",
               "temperature_correction": "not_applied", "note": o["note"], "mass_conventions": {}}
        for convention, masses in protocol["atomic_mass_conventions"].items():
            mass = formula_mass(o["formula"], masses)
            value = refractivity(n, mass, d)
            interval = [refractivity(n - u, mass, d + u), refractivity(n + u, mass, d - u)]
            ratio = found * d / mass
            needed_n = math.sqrt((1 + 2 * ratio) / (1 - ratio)) if 0 < ratio < 1 else None
            needed_d = (n * n - 1) / (n * n + 2) * mass / found
            row["mass_conventions"][convention] = {
                "molar_mass_g_mol": mass, "reconstructed_MR_cm3_mol": value,
                "reconstructed_minus_printed_found_cm3_mol": value - found,
                "relative_difference_percent": 100 * (value - found) / found,
                "display_rounding_only_interval_cm3_mol": interval,
                "printed_found_display_interval_cm3_mol": [found - printed_u, found + printed_u],
                "intervals_overlap": interval[0] <= found + printed_u and interval[1] >= found - printed_u,
                "counterfactual_density_at_reported_n_to_match_found": needed_d,
                "counterfactual_n_at_reported_density_to_match_found": needed_n,
                "counterfactual_scope": "conditional algebra only; no proposed correction of source data",
            }
        rows.append(row)
    return {"schema_version": "1.0", "task_id": "A01-MR-T1",
            "result_type": "published_property_consistency_reconstruction",
            "scientific_review_status": "review_required",
            "source_pdf_verification": source_check, "observations_sha256": digest(csv_path),
            "protocol_sha256": digest(protocol_path), "code_sha256": digest(Path(__file__)),
            "formula": protocol["relation"], "density_approximation": protocol["density_approximation"],
            "display_rounding_diagnostic": protocol["display_rounding_diagnostic"],
            "experimental_uncertainty": "not_reported_in_source",
            "printed_calculated_MR_scope": protocol["printed_calculated_MR_scope"],
            "rows": rows,
            "interpretation": {
                "primary_same_temperature_comparison": ["I", "V"],
                "I": "Integer-mass reconstruction overlaps the printed found value under display rounding.",
                "V": "Neither stated mass convention nor the stated display rounding reconciles the full residual.",
                "cause_of_residual": "unresolved; no ruling on printing, measurement, purity or undocumented convention",
                "IV": "Mixed-temperature conditional reconstruction only; no unprovided temperature correction.",
            },
            "boundaries": {"quantum_calculation": "not_performed", "new_experiment": "not_performed",
                           "conjugation_explanation": "not_validated", "source_data_repair": "not_performed",
                           "professional_transcription_signoff": "pending"}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HERE / "result.json")
    args = parser.parse_args()
    result = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")
    print(json.dumps({"task_id": result["task_id"], "result": str(args.output),
                      "scientific_review_status": "review_required", "source_pdf": result["source_pdf_verification"]["status"]}))


if __name__ == "__main__":
    main()
