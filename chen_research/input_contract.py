"""Strict input identity for the single sealed PF1966-UV-T1 table replay.

These checks validate the delivered transcription and provenance registration.
They do not inspect the original PDF or provide a professional transcription signoff.
The contract deliberately accepts no new compounds, observations or protocols.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import math
from pathlib import Path


class ReproducibilityError(ValueError):
    """Inputs do not qualify for this fixed and evidence-bound replay."""


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_VERSION = "PF1966-UV-T1.fixed.v2"
DATA_SHA256 = "92af88d5c1307d0a01b418354d2620a0d9eb8a8c68766adedd8be0feec2ff29a"
PROTOCOL_SHA256 = "3439dbf5d535663672afd034c888fce4aacc3c4314657199f40b90252568735c"
SOURCE_REGISTRY_SHA256 = "5d898ddda4013b0361d4a33cb3cca964374fabe1f63c1b528218ac867adda0cc"
SOURCE_PDF_SHA256 = "b97a7b641968561a1387d82c9b01fb8b2973c2a47e2e36c07ce85db2831302be"
MAX_INPUT_BYTES = 65_536

EXPECTED_COLUMNS = (
    "measurement_id", "compound_id", "formula", "solvent", "lambda_max_nm",
    "source_id", "pdf_page", "printed_page", "table_number",
)
_OBSERVATIONS = (
    ("UV01", "nC3F7I", "C3F7I", "C6H14", "270.0"),
    ("UV02", "nC3F7I", "C3F7I", "EtOH", "250.0"),
    ("UV03", "nC3F7I", "C3F7I", "Et2O", "256.0"),
    ("UV04", "iC3F7I", "C3F7I", "C6H14", "274.0"),
    ("UV05", "iC3F7I", "C3F7I", "EtOH", "250.0"),
    ("UV06", "iC3F7I", "C3F7I", "Et2O", "257.0"),
    ("UV07", "tC4F9I", "C4F9I", "C6H14", "288.0"),
    ("UV08", "tC4F9I", "C4F9I", "CCl4", "288.0"),
    ("UV09", "tC4F9I", "C4F9I", "EtOH", "260.5"),
    ("UV10", "tC4F9I", "C4F9I", "Et2O", "264.0"),
)
_PAIRS = {
    ("nC3F7I", "EtOH"): ("UV01", "UV02"),
    ("iC3F7I", "EtOH"): ("UV04", "UV05"),
    ("tC4F9I", "EtOH"): ("UV07", "UV09"),
    ("nC3F7I", "Et2O"): ("UV01", "UV03"),
    ("iC3F7I", "Et2O"): ("UV04", "UV06"),
    ("tC4F9I", "Et2O"): ("UV07", "UV10"),
}

_EXPECTED_PROTOCOL = {
    "task_id": "PF1966-UV-T1", "source_id": "PF01",
    "source_url": "https://sioc-journal.cn/Jwk_hxxb/CN/Y1966/V32/I1/18",
    "original_authors": ["陈庆云", "蒋锡夔", "陈秉启", "梁梦兰"],
    "publication_year": 1966, "web_platform_date_is_publication_year": False,
    "source_pdf_sha256": SOURCE_PDF_SHA256,
    "inspected_scan_page_sha256": "7db29ab674d3625139a32954268dd878945bfb6cfe327464d801ead7cc4ce5c5",
    "location": {"pdf_page": 4, "printed_page": 21, "table": 1},
    "original_wavelength_unit": "毫微米（millimicron），数值等于 nm",
    "baseline_solvent": "C6H14",
    "baseline_identity_note": "CSV 保留原表分子式记号；没有在本合同中将其进一步指定为某种异构体",
    "donor_solvents": ["EtOH", "Et2O"],
    "delta_lambda_definition": "lambda_H_nm - lambda_B_nm",
    "blue_shift_definition": "10000000 * (1/lambda_B_nm - 1/lambda_H_nm), in cm^-1",
    "display_rounding_half_width_nm": 0.05, "experimental_uncertainty_nm": None,
    "reported_delta_lambda_nm": {
        "EtOH": {"nC3F7I": 20.0, "iC3F7I": 24.0, "tC4F9I": 27.5},
        "Et2O": {"nC3F7I": 14.0, "iC3F7I": 17.0, "tC4F9I": 24.0},
    },
    "claim_scope": "原表三个完整碘代物的溶剂位移数值关系；不是四种孤立基团的普适吸电子顺序",
    "not_directly_measured_here": ["CF3CF2I", "CF3I"],
    "original_pdf_distributed": False,
    "transcription_status": "AI visual cross-check against cached original scan; independent expert review pending",
}
_EXPECTED_SOURCES = {
    "review_date": "2026-11-11",
    "sources": [{
        "source_id": "PF01", "authors": ["陈庆云", "蒋锡夔", "陈秉启", "梁梦兰"],
        "title": "全氟和多氟型有机化合物的化学特性——全氟叔丁基碘以及全氟烷基的诱导效应顺序",
        "year": 1966, "venue": "化学学报 32(1), 18–25",
        "url": "https://sioc-journal.cn/Jwk_hxxb/CN/Y1966/V32/I1/18",
        "inspected_location": "印刷 p.21，表1；PDF 第4页",
        "transcribed_field": "lambda_max（毫微米，数值同 nm）；没有把相邻 ε 列作为波长",
        "cached_pdf_sha256": SOURCE_PDF_SHA256, "material_included": False,
        "boundary": "原表数值可重放；不重现实验，不证明亲卤机理、游离阴离子或四基团普适排序",
    }],
    "private_materials_note": "传记深读用于研究选题边界，书稿全文及图片不随包分发。原来源编号未改写。",
}


def assert_exact(expected, actual, path: str = "$") -> None:
    """Reject missing/unknown fields and Python's bool-equals-int equivalence."""
    if type(expected) is not type(actual):
        raise ReproducibilityError(f"{path} 类型不符合固定合同")
    if isinstance(expected, dict):
        if expected.keys() != actual.keys():
            raise ReproducibilityError(f"{path} 字段缺失或含未登记字段")
        for key in expected:
            assert_exact(expected[key], actual[key], f"{path}.{key}")
    elif isinstance(expected, list):
        if len(expected) != len(actual):
            raise ReproducibilityError(f"{path} 集合长度不符合固定合同")
        for index, (left, right) in enumerate(zip(expected, actual)):
            assert_exact(left, right, f"{path}[{index}]")
    elif isinstance(actual, float) and not math.isfinite(actual):
        raise ReproducibilityError(f"{path} 不能是 NaN 或无穷值")
    elif expected != actual:
        raise ReproducibilityError(f"{path} 与封存任务合同不符")


def _read(path: Path, label: str) -> bytes:
    try:
        path = Path(path)
        if path.is_symlink() or not path.is_file():
            raise ReproducibilityError(f"{label} 须为实际普通文件")
        if path.stat().st_size > MAX_INPUT_BYTES:
            raise ReproducibilityError(f"{label} 超过固定任务的输入大小上限")
        raw = path.read_bytes()
        if len(raw) > MAX_INPUT_BYTES:
            raise ReproducibilityError(f"{label} 超过固定任务的输入大小上限")
        return raw
    except (OSError, TypeError) as exc:
        raise ReproducibilityError(f"无法读取{label}") from exc


def _fingerprint(raw: bytes, expected: str, label: str) -> None:
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ReproducibilityError(f"{label} 字节 SHA-256 与封存输入不符")


def _pairs(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ReproducibilityError(f"JSON 重复字段：{key}")
        value[key] = item
    return value


def _invalid_constant(value):
    raise ReproducibilityError(f"JSON 非有限数值不合格：{value}")


def read_strict_json(raw: bytes, label: str):
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs,
                          parse_constant=_invalid_constant)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ReproducibilityError(f"{label} 不是合格的 UTF-8 JSON") from exc


def validate_protocol(path: Path) -> dict:
    raw = _read(path, "协议")
    protocol = read_strict_json(raw, "协议")
    assert_exact(_EXPECTED_PROTOCOL, protocol, "protocol")
    _fingerprint(raw, PROTOCOL_SHA256, "协议")
    return protocol


def validate_sources(path: Path) -> dict:
    raw = _read(path, "来源登记")
    sources = read_strict_json(raw, "来源登记")
    assert_exact(_EXPECTED_SOURCES, sources, "source_registry")
    _fingerprint(raw, SOURCE_REGISTRY_SHA256, "来源登记")
    return sources


def validate_observations(path: Path) -> dict[tuple[str, str], float]:
    raw = _read(path, "观测 CSV")
    try:
        rows = list(csv.reader(io.StringIO(raw.decode("utf-8"), newline=""), strict=True))
    except (UnicodeError, csv.Error) as exc:
        raise ReproducibilityError("观测 CSV 格式不合格") from exc
    if not rows or tuple(rows[0]) != EXPECTED_COLUMNS:
        raise ReproducibilityError("CSV 字段顺序、唯一性或单位不符合固定合同")
    if len(rows) != len(_OBSERVATIONS) + 1:
        raise ReproducibilityError("须保留全部十条原始观测，不补造、不删除")
    seen = set()
    values = {}
    for ordinal, (row, expected) in enumerate(zip(rows[1:], _OBSERVATIONS), start=1):
        if len(row) != len(EXPECTED_COLUMNS):
            raise ReproducibilityError(f"CSV 第 {ordinal} 条记录字段缺失或过多")
        observation_id = row[0]
        if not observation_id or observation_id in seen:
            raise ReproducibilityError("观测编号须非空且唯一")
        seen.add(observation_id)
        if tuple(row) != (*expected, "PF01", "4", "21", "1"):
            raise ReproducibilityError(f"观测 {observation_id} 的对象、编号、数值或来源定位不符")
        value = float(row[4])
        if not math.isfinite(value):
            raise ReproducibilityError("波长必须是有限 nm 数值")
        values[row[1], row[3]] = value
    _fingerprint(raw, DATA_SHA256, "观测 CSV")
    return values


def validate_inputs(csv_path: Path, protocol_path: Path, sources_path: Path | None = None) -> dict:
    """Verify complete semantics and exact bytes before performing arithmetic."""
    protocol = validate_protocol(protocol_path)
    sources = validate_sources(sources_path if sources_path is not None else ROOT / "data/sources.json")
    source = sources["sources"][0]
    for protocol_key, source_key in (("source_id", "source_id"), ("original_authors", "authors"),
                                     ("publication_year", "year"), ("source_url", "url"),
                                     ("source_pdf_sha256", "cached_pdf_sha256")):
        assert_exact(protocol[protocol_key], source[source_key], f"source_link.{protocol_key}")
    values = validate_observations(csv_path)
    return {"protocol": protocol, "sources": sources, "values": values,
            "observation_ids": [{"measurement_id": item[0], "compound_id": item[1], "solvent": item[3]}
                                for item in _OBSERVATIONS],
            "measurement_id_pairs": [{"compound_id": compound, "donor_solvent": donor,
                                      "baseline_measurement_id": ids[0], "donor_measurement_id": ids[1]}
                                     for (compound, donor), ids in _PAIRS.items()]}
