"""Replay published Table 1 peak positions; no spectral fitting or quantum chemistry.

The two positive shifts have different definitions:
    delta_lambda_nm = lambda_H - lambda_B           (the paper's definition)
    blue_shift_cm_inverse = 10**7/lambda_B - 10**7/lambda_H
H is the C6H14 entry in the original table; B is EtOH or Et2O, not benzene.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path


class ReproducibilityError(ValueError):
    """Inputs do not qualify for this narrowly defined reproduction."""


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
    values = {}
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if set(reader.fieldnames or []) != COLUMNS:
            raise ReproducibilityError("CSV 字段或单位不符合本任务合同")
        for row in reader:
            compound, solvent = row["compound_id"], row["solvent"]
            if compound not in COMPOUNDS:
                raise ReproducibilityError("原表没有该分子的直接测量，不能补作实测")
            if row["formula"] != COMPOUNDS[compound]:
                raise ReproducibilityError("化学实体与分子式不匹配")
            if solvent not in (BASELINE, *DONORS, "CCl4"):
                raise ReproducibilityError("溶剂须保持原表记号；B 不代表苯")
            if (row["source_id"], row["pdf_page"], row["printed_page"], row["table_number"]) != ("PF01", "4", "21", "1"):
                raise ReproducibilityError("来源与定位不匹配")
            try:
                value = float(row["lambda_max_nm"])
            except (ValueError, TypeError) as exc:
                raise ReproducibilityError("波长须为有效的 nm 数值") from exc
            if not math.isfinite(value) or not 200 <= value <= 400:
                raise ReproducibilityError("数值不在本表 UV 波长的任务范围内")
            key = (compound, solvent)
            if key in values:
                raise ReproducibilityError("同一分子和溶剂存在重复记录")
            values[key] = value
    required = {(c, s) for c in COMPOUNDS for s in (BASELINE, *DONORS)}
    if not required <= values.keys():
        raise ReproducibilityError("缺少配对波长，不能计算完整三分子比较")
    if set(values) - required not in (set(), {("tC4F9I", "CCl4")}):
        raise ReproducibilityError("额外记录不属于原表已转录的观测")
    return values


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


def replay(csv_path: Path, protocol_path: Path) -> dict:
    values = load_observations(csv_path)
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    if protocol.get("task_id") != "PF1966-UV-T1" or protocol.get("baseline_solvent") != BASELINE:
        raise ReproducibilityError("协议不属于已定义的原表重放任务")
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
        "schema_version": "1.0", "task_id": "PF1966-UV-T1", "source_id": "PF01",
        "result_type": "published_table_numerical_replay",
        "numerical_status": "nominal_three_iodide_order_reproduced" if all(
            c["matches_three_iodide_order"] for c in comparisons) else "nominal_order_discrepancy",
        "scientific_review_status": "review_required",
        "source_pdf_sha256": protocol["source_pdf_sha256"],
        "data_sha256": digest(csv_path), "protocol_sha256": digest(protocol_path),
        "code_sha256": digest(Path(__file__)), "observations_count": len(values),
        "used_observations_count": 9, "excluded_from_comparison": ([{
            "compound_id": "tC4F9I", "solvent": "CCl4", "reason": "不属于本合同的 C6H14—给体溶剂配对"}]
            if ("tC4F9I", "CCl4") in values else []),
        "source_location": "1966, 32(1), printed p.21, Table 1; PDF p.4",
        "transcription_review": "AI 逐格对照原扫描页；尚无独立化学专家复核签认",
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
            "phase1_status": "仅形成可审阅数值重放，不等于模型服务、WSL 验收或网站已接入"},
    }


def write_outputs(result: dict, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    text = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    (output_dir / "pftb1966-uv-replay.json").write_text(text, encoding="utf-8")
    export = {"task_id": result["task_id"], "result_type": result["result_type"],
              "publication_status": "review_required", "source_ids": ["PF01"],
              "numeric_summary": result["measurements_and_derived_shifts"],
              "boundaries": result["boundaries"],
              "data_sha256": result["data_sha256"], "code_sha256": result["code_sha256"]}
    (output_dir / "website-candidate.json").write_text(
        json.dumps(export, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
