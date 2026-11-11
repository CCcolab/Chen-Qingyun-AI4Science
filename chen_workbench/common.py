"""Shared offline workspace primitives. Scientific source files are read-only."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
from uuid import UUID, uuid4

from chen_research.input_contract import read_strict_json
from chen_research.run_record import assert_safe_path

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "research/tasks.v1.json"
DEFAULT_WORKSPACE = ROOT / "scratch/workbench"


class WorkbenchError(ValueError):
    """A request does not qualify for the offline research workflow."""


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    path = assert_safe_path(path, directory=False)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> dict:
    path = assert_safe_path(path, directory=False)
    if path.stat().st_size > 2_000_000:
        raise WorkbenchError("JSON exceeds the 2 MB limit")
    with path.open("rb") as handle:
        raw = handle.read(2_000_001)
    if len(raw) > 2_000_000:
        raise WorkbenchError("JSON exceeds the 2 MB limit")
    value = read_strict_json(raw, path.name)
    if type(value) is not dict:
        raise WorkbenchError("Expected a JSON object")
    remaining = [value]
    while remaining:
        item = remaining.pop()
        if type(item) is float and not math.isfinite(item):
            raise WorkbenchError("Non-finite numbers are not allowed in workflow JSON")
        if type(item) is dict:
            remaining.extend(item.values())
        elif type(item) is list:
            remaining.extend(item)
    return value


def safe_output(path: Path) -> Path:
    path = assert_safe_path(path, must_exist=False)
    if path == ROOT or path in ROOT.parents:
        raise WorkbenchError("The source repository or its ancestors cannot be used as a workspace")
    if ROOT in path.parents and (ROOT / "scratch") not in path.parents:
        raise WorkbenchError("Workspaces inside this repository must be under ignored scratch/")
    return path


def write_new(path: Path, value: dict) -> Path:
    path = safe_output(path)
    if type(value) is not dict:
        raise WorkbenchError("New workflow records must be JSON objects")
    if path.exists():
        raise WorkbenchError(f"Existing evidence is not overwritten: {path.name}")
    raw = (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    assert_safe_path(path.parent, directory=True)
    with path.open("xb") as handle:
        handle.write(raw)
    return path


def init_workspace(path: Path = DEFAULT_WORKSPACE) -> Path:
    path = safe_output(path)
    if path.exists():
        if (path / "workspace.json").is_file():
            return workspace_path(path)
        if not path.is_dir() or any(path.iterdir()):
            raise WorkbenchError("Use a new or empty workspace directory")
    path.mkdir(parents=True, exist_ok=True)
    for name in ("evidence", "requests", "proposals", "jobs", "locks", "reports"):
        (path / name).mkdir()
    write_new(path / "workspace.json", {
        "schema_version": "1.0", "workspace_id": str(uuid4()), "created_at_utc": now(),
        "mode": "offline", "model_api_called": False,
        "scientific_review_status": "review_required",
    })
    return path


def workspace_path(path: Path = DEFAULT_WORKSPACE) -> Path:
    path = safe_output(path)
    marker = read_json(path / "workspace.json")
    if (set(marker) != {"schema_version", "workspace_id", "created_at_utc", "mode",
                        "model_api_called", "scientific_review_status"}
            or marker["schema_version"] != "1.0" or marker["mode"] != "offline"
            or marker["model_api_called"] is not False
            or marker["scientific_review_status"] != "review_required"):
        raise WorkbenchError("Invalid offline workspace marker")
    try:
        if str(UUID(marker["workspace_id"])) != marker["workspace_id"]:
            raise ValueError("noncanonical UUID")
        stamp = datetime.fromisoformat(marker["created_at_utc"])
        if stamp.utcoffset() != timezone.utc.utcoffset(stamp):
            raise ValueError("UTC required")
    except (ValueError, TypeError, AttributeError) as exc:
        raise WorkbenchError("Invalid workspace identity or timestamp") from exc
    for name in ("evidence", "requests", "proposals", "jobs", "locks", "reports"):
        assert_safe_path(path / name, directory=True)
    return path
