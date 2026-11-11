"""Replay published Table 1 peak positions; no spectral fitting or quantum chemistry.

The two positive shifts have different definitions:
    delta_lambda_nm = lambda_H - lambda_B           (the paper's definition)
    blue_shift_cm_inverse = 10**7/lambda_B - 10**7/lambda_H
H is the C6H14 entry in the original table; B is EtOH or Et2O, not benzene.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

from .input_contract import (
    CONTRACT_VERSION, DATA_SHA256, PROTOCOL_SHA256, SOURCE_REGISTRY_SHA256,
    ReproducibilityError, assert_exact, validate_inputs, validate_observations, validate_sources,
)


COMPOUNDS = {"nC3F7I": "C3F7I", "iC3F7I": "C3F7I", "tC4F9I": "C4F9I"}
BASELINE = "C6H14"
DONORS = ("EtOH", "Et2O")
EXPECTED_ORDER = ["tC4F9I", "iC3F7I", "nC3F7I"]
COLUMNS = {
    "measurement_id", "compound_id", "formula", "solvent", "lambda_max_nm",
    "source_id", "pdf_page", "printed_page", "table_number",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_observations(path: Path) -> dict[tuple[str, str], float]:
    validate_sources(Path(__file__).resolve().parents[1] / "data/sources.json")
    return validate_observations(path)


def shifts(lambda_h: float, lambda_b: float) -> dict[str, float]:
    return {"delta_lambda_nm": lambda_h - lambda_b,
            "blue_shift_cm_inverse": 1e7 * (1 / lambda_b - 1 / lambda_h)}


def interval(lambda_h: float, lambda_b: float, half_width_nm: float, metric: str) -> tuple[float, float]:
    """Independent bounded wavelength perturbations, NOT experimental error bars."""
    u = half_width_nm
    if not math.isfinite(u) or u < 0 or u >= min(lambda_h, lambda_b):
        raise ReproducibilityError("波长扰动半宽无效")
    if metric == "delta_lambda_nm":
        return lambda_h - lambda_b - 2 * u, lambda_h - lambda_b + 2 * u
    if metric == "blue_shift_cm_inverse":
        return (1e7 * (1 / (lambda_b + u) - 1 / (lambda_h - u)),
                1e7 * (1 / (lambda_b - u) - 1 / (lambda_h + u)))
    raise ReproducibilityError("未知指标")


def overlap_half_width(high: tuple[float, float], low: tuple[float, float], metric: str) -> float:
    """Smallest common half-width at which adjacent worst-case intervals touch."""
    def separation(u: float) -> float:
        return interval(*high, u, metric)[0] - interval(*low, u, metric)[1]
    if separation(0) <= 0:
        return 0.0
    left, right = 0.0, min(*high, *low) / 2
    if separation(right) > 0:
        raise ReproducibilityError("本任务区间内未找到可比较的敏感性阈值")
    for _ in range(80):
        mid = (left + right) / 2
        if separation(mid) > 0:
            left = mid
        else:
            right = mid
    return (left + right) / 2


def replay(csv_path: Path, protocol_path: Path, sources_path: Path | None = None) -> dict:
    validated = validate_inputs(csv_path, protocol_path, sources_path)
    values, protocol = validated["values"], validated["protocol"]
    u = protocol["display_rounding_half_width_nm"]
    if u != 0.05 or protocol["experimental_uncertainty_nm"] is not None:
        raise ReproducibilityError("不得把展示舍入假设改写成原实验误差")
    rows, comparisons = [], []
    for donor in DONORS:
        raw = {}
        for compound in COMPOUNDS:
            h, b = values[compound, BASELINE], values[compound, donor]
            metrics = shifts(h, b)
            target = protocol["reported_delta_lambda_nm"][donor][compound]
            if not math.isclose(metrics["delta_lambda_nm"], target, rel_tol=0, abs_tol=1e-10):
                raise ReproducibilityError("转录数据的算术结果与原表所列位移不符")
            raw[compound] = metrics
            bounds = {m: [round(x, 6) for x in interval(h, b, u, m)] for m in metrics}
            rows.append({"compound_id": compound, "formula": COMPOUNDS[compound],
                         "baseline_solvent": BASELINE, "donor_solvent": donor,
                         "lambda_h_nm": h, "lambda_b_nm": b,
                         **{m: round(v, 6) for m, v in metrics.items()},
                         "display_rounding_intervals": bounds})
        for metric in ("delta_lambda_nm", "blue_shift_cm_inverse"):
            order = sorted(COMPOUNDS, key=lambda c: raw[c][metric], reverse=True)
            adjacent = []
            for high, low in zip(order, order[1:]):
                high_pair = values[high, BASELINE], values[high, donor]
                low_pair = values[low, BASELINE], values[low, donor]
                gap = interval(*high_pair, u, metric)[0] - interval(*low_pair, u, metric)[1]
                adjacent.append({"higher": high, "lower": low,
                                 "nominal_gap": round(raw[high][metric] - raw[low][metric], 6),
                                 "separated_under_display_rounding_assumption": gap > 0,
                                 "first_overlap_common_wavelength_half_width_nm": round(
                                     overlap_half_width(high_pair, low_pair, metric), 6)})
            comparisons.append({"donor_solvent": donor, "metric": metric,
                                "nominal_order": order, "matches_three_iodide_order": order == EXPECTED_ORDER,
                                "adjacent_comparisons": adjacent})
    return {
        "schema_version": "2.0", "input_contract_version": CONTRACT_VERSION,
        "task_id": "PF1966-UV-T1", "source_id": "PF01",
        "result_type": "published_table_numerical_replay",
        "numerical_status": "nominal_three_iodide_order_reproduced" if all(
            c["matches_three_iodide_order"] for c in comparisons) else "nominal_order_discrepancy",
        "scientific_review_status": "review_required",
        "original_authors": protocol["original_authors"],
        "publication_year": protocol["publication_year"], "source_url": protocol["source_url"],
        "location": protocol["location"],
        "source_pdf_sha256": protocol["source_pdf_sha256"],
        "data_sha256": DATA_SHA256, "protocol_sha256": PROTOCOL_SHA256,
        "source_registry_sha256": SOURCE_REGISTRY_SHA256,
        "validator_code_sha256": digest(Path(__file__).with_name("input_contract.py")),
        "code_sha256": digest(Path(__file__)), "observations_count": len(values),
        "observation_ids": validated["observation_ids"],
        "measurement_id_pairs": validated["measurement_id_pairs"],
        "used_observations_count": 9, "excluded_from_comparison": ([{
            "compound_id": "tC4F9I", "solvent": "CCl4", "reason": "不属于本合同的 C6H14—给体溶剂配对"}]
            if ("tC4F9I", "CCl4") in values else []),
        "source_location": "1966, 32(1), printed p.21, Table 1; PDF p.4",
        "transcription_review": "继承封存包转录；本轮未重新核验原扫描，独立专业签认待补",
        "experimental_uncertainty_nm": None,
        "display_rounding_assumption": {"half_width_nm": u, "interpretation":
            "按一位小数的通常舍入作独立有界扰动诊断，不是仪器精度、测量误差或置信区间"},
        "measurements_and_derived_shifts": rows, "comparisons": comparisons,
        "boundaries": {
            "new_experiment": "not_performed", "raw_spectrum_refitting": "not_performed",
            "quantum_calculation": "not_performed", "reaction_mechanism": "not_tested",
            "free_anion_detection": "not_tested", "universal_four_group_order": "not_tested",
            "novel_chemistry": "not_claimed",
            "unmeasured_iodides": ["C2F5I", "CF3I"],
            "entity_warning": "原表第三个测量对象为 n-C3F7I，不能替换为 C2F5I；B 是给体溶剂不是苯",
            "phase1_status": "原表数值重放候选；独立专业签认及审定发布待完成，工程环境另见绑定运行记录"},
    }


def write_outputs(result: dict, output_dir: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    expected = replay(root / "data/pftb1966_table1.csv", root / "protocols/pftb1966_uv.json",
                      root / "data/sources.json")
    assert_exact(expected, result, "result")
    output_dir = Path(output_dir)
    targets = [output_dir / name for name in ("pftb1966-uv-replay.json", "website-candidate.json")]
    if any(path.exists() or path.is_symlink() for path in targets):
        raise ReproducibilityError("输出已存在；请使用新的运行目录，不覆盖封存结果或候选历史")
    text = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    export = {"schema_version": result["schema_version"],
              "input_contract_version": result["input_contract_version"],
              "task_id": result["task_id"], "result_type": result["result_type"],
              "publication_status": "review_required", "source_ids": ["PF01"],
              "original_authors": result["original_authors"], "publication_year": result["publication_year"],
              "source_url": result["source_url"], "location": result["location"],
              "source_pdf_sha256": result["source_pdf_sha256"],
              "protocol_sha256": result["protocol_sha256"],
              "source_registry_sha256": result["source_registry_sha256"],
              "validator_code_sha256": result["validator_code_sha256"],
              "observation_ids": result["observation_ids"],
              "measurement_id_pairs": result["measurement_id_pairs"],
              "numeric_summary": result["measurements_and_derived_shifts"],
              "comparisons": result["comparisons"],
              "experimental_uncertainty_nm": result["experimental_uncertainty_nm"],
              "display_rounding_assumption": result["display_rounding_assumption"],
              "transcription_review": result["transcription_review"],
              "boundaries": result["boundaries"],
              "data_sha256": result["data_sha256"], "code_sha256": result["code_sha256"]}
    candidate_text = json.dumps(export, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    output_dir.mkdir(parents=True, exist_ok=True)
    for path, content in zip(targets, (text, candidate_text)):
        with path.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
