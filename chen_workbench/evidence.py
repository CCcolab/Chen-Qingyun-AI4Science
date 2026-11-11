"""Local text excerpts with location and byte identity; never a professional signoff."""
from __future__ import annotations

import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from uuid import UUID, uuid4

from chen_research.run_record import assert_safe_path
from .catalog import get_task, load_catalog
from .common import WorkbenchError, now, read_json, write_new, workspace_path, safe_output

KINDS = {"metadata", "publisher_abstract", "primary_excerpt", "archival_excerpt", "transcribed_table"}
MAX_EXCERPT_BYTES = 65_536
KEYS = {"evidence_id", "source_id", "kind", "locator", "sha256", "text_path",
        "source_verification", "scientific_review_status", "recorded_at_utc"}


def register_evidence(workspace: Path, source_id: str, kind: str, locator: str, text_path: Path) -> dict:
    workspace = workspace_path(workspace)
    known = {source for task in load_catalog()["tasks"] for source in task["source_ids"]}
    if type(source_id) is not str or source_id not in known or type(kind) is not str or kind not in KINDS:
        raise WorkbenchError("Unknown source or evidence kind")
    if type(locator) is not str or not locator.strip() or len(locator) > 1000:
        raise WorkbenchError("A specific page, table, figure or archival location is required")
    text_path = assert_safe_path(text_path, directory=False)
    if text_path.stat().st_size > MAX_EXCERPT_BYTES:
        raise WorkbenchError("Excerpt must be at most 64 KiB; register separate located excerpts")
    raw, _ = _excerpt_bytes(text_path)
    identity = str(uuid4())
    directory = safe_output(workspace / "evidence" / identity)
    directory.mkdir()
    target = directory / "excerpt.txt"
    with target.open("xb") as handle:
        handle.write(raw)
    record = {"evidence_id": identity, "source_id": source_id, "kind": kind, "locator": locator,
              "sha256": hashlib.sha256(raw).hexdigest(), "text_path": f"evidence/{identity}/excerpt.txt",
              "source_verification": "user_supplied_unverified", "scientific_review_status": "review_required",
              "recorded_at_utc": now()}
    write_new(directory / "record.json", record)
    return record


def read_evidence(workspace: Path, evidence_id: str) -> dict:
    workspace = workspace_path(workspace)
    try:
        if str(UUID(evidence_id)) != evidence_id:
            raise ValueError("noncanonical UUID")
    except (ValueError, TypeError, AttributeError) as exc:
        raise WorkbenchError("Invalid evidence identifier") from exc
    record = read_json(workspace / "evidence" / evidence_id / "record.json")
    expected_path = f"evidence/{evidence_id}/excerpt.txt"
    known = {source for task in load_catalog()["tasks"] for source in task["source_ids"]}
    if (set(record) != KEYS or record["evidence_id"] != evidence_id or record["text_path"] != expected_path
            or type(record["kind"]) is not str or record["kind"] not in KINDS
            or type(record["source_id"]) is not str or record["source_id"] not in known
            or record["source_verification"] != "user_supplied_unverified"
            or record["scientific_review_status"] != "review_required"
            or type(record["locator"]) is not str or not record["locator"].strip()
            or len(record["locator"]) > 1000
            or type(record["sha256"]) is not str or len(record["sha256"]) != 64
            or any(character not in "0123456789abcdef" for character in record["sha256"])):
        raise WorkbenchError("Invalid or promoted evidence record")
    try:
        if type(record["recorded_at_utc"]) is not str:
            raise ValueError("timestamp type")
        stamp = datetime.fromisoformat(record["recorded_at_utc"])
        if stamp.utcoffset() != timedelta(0):
            raise ValueError("UTC required")
    except ValueError as exc:
        raise WorkbenchError("Invalid evidence timestamp") from exc
    target = assert_safe_path(workspace / expected_path, directory=False)
    raw, text = _excerpt_bytes(target)
    if hashlib.sha256(raw).hexdigest() != record["sha256"]:
        raise WorkbenchError("Evidence bytes changed after registration")
    return {**record, "text": text}


def evidence_for_task(workspace: Path, task_id: str) -> list[dict]:
    workspace = workspace_path(workspace)
    task = get_task(task_id)
    result = []
    for directory in sorted((workspace / "evidence").iterdir()):
        if not directory.is_dir():
            raise WorkbenchError("Unexpected file in evidence store")
        record = read_evidence(workspace, directory.name)
        if record["source_id"] in task["source_ids"]:
            result.append(record)
    return result


def _excerpt_bytes(path: Path) -> tuple[bytes, str]:
    """Hash and decode the same bounded snapshot, never a second mutable read."""
    with path.open("rb") as handle:
        raw = handle.read(MAX_EXCERPT_BYTES + 1)
    if len(raw) > MAX_EXCERPT_BYTES:
        raise WorkbenchError("Excerpt must be at most 64 KiB")
    try:
        text = raw.decode("utf-8")
    except UnicodeError as exc:
        raise WorkbenchError("Evidence must be UTF-8 text") from exc
    if not text.strip() or "\x00" in text:
        raise WorkbenchError("Empty or binary evidence is not accepted")
    return raw, text
