"""Conditional reconstruction of the 117491 organic-mass/yield ledger.

No preparation procedure, model API, quantum calculation or experiment is run.
"""
from __future__ import annotations

from decimal import Decimal, getcontext
import hashlib
import itertools
import json
from pathlib import Path

getcontext().prec = 32
ROOT = Path(__file__).resolve().parent
SOURCE_SHA = "f7482b83780bd86523763f2e0e6b1b980a90ad1141ffc6e91811242f6a630469"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("Duplicate JSON field")
            result[key] = value
        return result
    def constant(value):
        raise ValueError("Nonfinite JSON constant")
    return json.loads(path.read_text("utf-8"), object_pairs_hook=pairs, parse_constant=constant)


def number(value):
    return float(round(value, 12))


def calculate():
    observations = read(ROOT / "observations.json")
    protocol = read(ROOT / "protocol.json")
    for document in (observations, protocol):
        if (document["task_id"] != "A01-AF-YIELD-T1"
                or document["scientific_review_status"] != "review_required"
                or document["source_image_sha256"] != SOURCE_SHA):
            raise ValueError("Fixed source identity or review status differs")
    masses = {key: Decimal(value) for key, value in observations["reported_organic_masses_g"].items()}
    if masses != {"phenol": Decimal("12.2"), "hexafluoroacetone": Decimal("11.2"), "product": Decimal("21.7")}:
        raise ValueError("Fixed printed masses differ")
    if observations["reported_yield_percent"] != "98" or observations["source_has_drawn_structure"] is not False:
        raise ValueError("Printed yield or structure provenance differs")
    weights = {atom: Decimal(value) for atom, value in protocol["atomic_weights_g_per_mol_of_atoms"].items()}
    formulas = protocol["formulae"]
    stoichiometry = protocol["stoichiometry"]
    atoms = set(weights)
    counts = {}
    for side, sign in (("reactants", -1), ("products", 1)):
        for species, coefficient in stoichiometry[side].items():
            if type(coefficient) is not int or coefficient <= 0:
                raise ValueError("Stoichiometric coefficients must be positive integers")
            for atom, count in formulas[species].items():
                if atom not in atoms or type(count) is not int or count <= 0:
                    raise ValueError("Invalid name-derived formula")
                counts[atom] = counts.get(atom, 0) + sign * coefficient * count
    if any(counts.values()):
        raise ValueError("Net equation is not atom-balanced")
    molar = {species: sum(weights[atom] * count for atom, count in formula.items())
             for species, formula in formulas.items()}
    reactants = stoichiometry["reactants"]
    def ledger(values):
        extent = {species: values[species] / molar[species] / coefficient
                  for species, coefficient in reactants.items()}
        limiting = min(extent, key=extent.get)
        theoretical = extent[limiting] * molar["product"] * stoichiometry["products"]["product"]
        return limiting, theoretical, values["product"] / theoretical * 100
    limiting, theoretical, nominal = ledger(masses)
    half = Decimal(protocol["display_rounding_diagnostic"]["mass_half_width_g"])
    percent_half = Decimal(protocol["display_rounding_diagnostic"]["reported_percent_half_width_percentage_points"])
    if half != Decimal("0.05") or percent_half != Decimal("0.5"):
        raise ValueError("Fixed display-rounding assumptions differ")
    endpoints = []
    limiting_set = set()
    for signs in itertools.product((-1, 1), repeat=3):
        values = {species: value + sign * half for (species, value), sign in zip(masses.items(), signs)}
        limiting_at_corner, _, apparent = ledger(values)
        limiting_set.add(limiting_at_corner)
        endpoints.append(apparent)
    lower, upper = min(endpoints), max(endpoints)
    reported = Decimal(observations["reported_yield_percent"])
    report_bounds = (reported - percent_half, reported + percent_half)
    alternative = {}
    for species, coefficient in reactants.items():
        basis_theoretical = masses[species] / molar[species] / coefficient * molar["product"]
        alternative[species] = {"theoretical_product_g_if_basis": number(basis_theoretical),
                                "mass_based_apparent_yield_percent": number(masses["product"] / basis_theoretical * 100),
                                "is_limiting_reagent_in_nominal_ledger": species == limiting}
    return {
        "schema_version": "1.0", "task_id": observations["task_id"],
        "result_type": protocol["result_type"], "scientific_review_status": "review_required",
        "source_image_sha256": SOURCE_SHA, "source_image_reverified_by_this_program": False,
        "observations_sha256": sha(ROOT / "observations.json"), "protocol_sha256": sha(ROOT / "protocol.json"),
        "code_sha256": sha(Path(__file__)),
        "formula_status": observations["formula_status"], "source_has_drawn_structure": False,
        "net_equation": "C3F6O + 2 C6H6O -> C15H10F6O2 + H2O",
        "net_equation_is_mechanism": False, "atom_balance_residual": counts,
        "molar_masses_g_per_mol": {key: number(value) for key, value in molar.items()},
        "reported_organic_masses_g": {key: number(value) for key, value in masses.items()},
        "reported_yield_percent": number(reported), "nominal_limiting_reagent": limiting,
        "nominal_theoretical_product_g": number(theoretical),
        "nominal_mass_based_apparent_yield_percent": number(nominal),
        "residual_to_reported_yield_percentage_points": number(nominal - reported),
        "reagent_basis_diagnostics": alternative,
        "display_rounding_diagnostic": {
            "mass_half_width_g": number(half), "reported_percent_half_width_percentage_points": number(percent_half),
            "apparent_yield_percent_bounds": [number(lower), number(upper)],
            "reported_percent_display_bounds": [number(value) for value in report_bounds],
            "overlap": max(lower, report_bounds[0]) <= min(upper, report_bounds[1]),
            "limiting_reagents_over_all_corners": sorted(limiting_set),
            "interpretation": "Display rounding only; not experimental uncertainty or confidence bounds"
        },
        "interpretation": "Conditional organic-mass ledger does not reproduce the printed 98 percent under stated assumptions; true yield and its original basis remain unresolved.",
        "unresolved": ["Product and reagent purity or assay", "Original theoretical-yield basis", "Historical mass and atomic-weight conventions", "Any unprinted correction or reporting convention"],
        "boundaries": {"corrected_true_yield": "not_claimed", "error_or_misconduct": "not_inferred", "chemical_identity_validation": "not_performed", "mechanism_validation": "not_performed", "quantum_calculation": "not_performed", "experimental_validation": "not_performed", "polymer_properties": "not_inferred"}
    }


if __name__ == "__main__":
    result = calculate()
    raw = (json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")
    target = ROOT / "result.json"
    if target.exists():
        if target.read_bytes() != raw:
            raise SystemExit("Existing scientific result differs; preserve it and create a versioned study")
    else:
        with target.open("xb") as stream:
            stream.write(raw)
    print(json.dumps({key: result[key] for key in ("task_id", "nominal_limiting_reagent", "nominal_theoretical_product_g", "nominal_mass_based_apparent_yield_percent", "reported_yield_percent", "residual_to_reported_yield_percentage_points", "display_rounding_diagnostic", "scientific_review_status")}, ensure_ascii=False, indent=2))
