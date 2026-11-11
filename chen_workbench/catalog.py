"""Versioned research tasks, distinct from sealed phase-one protocols."""
from __future__ import annotations

import re

from chen_research.input_contract import assert_exact, validate_inputs
from .common import ROOT, CATALOG_PATH, WorkbenchError, read_json, sha256

KINDS = {"published_table_numerical_replay", "evidence_reconstruction",
         "computational_reproduction", "model_validation", "future_hypothesis",
         "historical_evidence", "scholarly_legacy"}
TASK_KEYS = {"task_id", "achievement_line", "title", "work_type", "question",
             "source_ids", "runner", "timeout_seconds", "blockers", "ai_role",
             "acceptance", "claim_boundary", "scientific_review_status"}


def _sources() -> dict:
    sources = {}
    for relative, field, registry in (
            ("site/data/public-sources.json", "sources", "website_metadata"),
            ("literature/related_work.json", "works", "related_work_registration")):
        records = read_json(ROOT / relative).get(field)
        if type(records) is not list:
            raise WorkbenchError("Invalid source registry")
        for item in records:
            if (type(item) is not dict or type(item.get("id")) is not str
                    or not item["id"].strip() or item["id"] in sources):
                raise WorkbenchError("Invalid or duplicate source identifier")
            sources[item["id"]] = {**item, "registry": registry,
                                    "workflow_verification": "metadata_registration_only"}
    return sources


def load_catalog() -> dict:
    catalog = read_json(CATALOG_PATH)
    if (set(catalog) != {"schema_version", "catalog_id", "catalog_version", "baselines", "tasks"}
            or catalog["schema_version"] != "1.0"
            or catalog["catalog_id"] != "Chen-Qingyun.research"
            or type(catalog["catalog_version"]) is not str or not catalog["catalog_version"].strip()
            or type(catalog["tasks"]) is not list or not catalog["tasks"]):
        raise WorkbenchError("Invalid research catalog")
    expected_paths = {"site/data/achievement-lines.json", "site/data/public-sources.json",
                      "protocols/research_queue.json", "literature/related_work.json"}
    if type(catalog["baselines"]) is not dict or set(catalog["baselines"]) != expected_paths:
        raise WorkbenchError("The catalog must bind its source registries")
    for relative, digest in catalog["baselines"].items():
        if type(digest) is not str or sha256(ROOT / relative) != digest:
            raise WorkbenchError(f"Catalog source baseline changed: {relative}")
    sources = _sources()
    ids, lines = set(), set()
    for task in catalog["tasks"]:
        if type(task) is not dict or set(task) != TASK_KEYS:
            raise WorkbenchError("Missing or unknown task fields")
        identity = task["task_id"]
        if (type(identity) is not str or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", identity)
                or identity in ids or type(task["achievement_line"]) is not str
                or task["achievement_line"] not in {f"A{i:02d}" for i in range(1, 10)}
                or type(task["work_type"]) is not str or task["work_type"] not in KINDS
                or task["scientific_review_status"] != "review_required"):
            raise WorkbenchError("Invalid task identity, type or scientific status")
        ids.add(identity)
        lines.add(task["achievement_line"])
        for key in ("title", "question", "ai_role", "claim_boundary"):
            if type(task[key]) is not str or not task[key].strip():
                raise WorkbenchError(f"Invalid task text: {key}")
        for key in ("source_ids", "blockers", "acceptance"):
            values = task[key]
            if (type(values) is not list or any(type(item) is not str or not item.strip() for item in values)
                    or len(values) != len(set(values))):
                raise WorkbenchError(f"Invalid task list: {key}")
        if (not task["source_ids"] or not task["acceptance"]
                or any(source not in sources for source in task["source_ids"])):
            raise WorkbenchError("Task references unknown sources")
        if (type(task["timeout_seconds"]) is not int or not 1 <= task["timeout_seconds"] <= 300):
            raise WorkbenchError("Task timeout must be an integer in 1..300 seconds")
        if task["runner"] is not None and not (
                identity == "PF1966-UV-T1" and task["runner"] == "pftb1966_replay_v2"
                and task["work_type"] == "published_table_numerical_replay"
                and task["achievement_line"] == "A03" and task["source_ids"] == ["PF01"]
                and not task["blockers"]):
            raise WorkbenchError("No approved execution adapter for this task")
    if lines != {f"A{i:02d}" for i in range(1, 10)}:
        raise WorkbenchError("Catalog must cover all nine achievement/legacy lines")
    return catalog


def get_task(task_id: str) -> dict:
    if type(task_id) is not str:
        raise WorkbenchError("A registered task identifier is required")
    for task in load_catalog()["tasks"]:
        if task["task_id"] == task_id:
            return task
    raise WorkbenchError(f"Unknown task: {task_id}")


def sources_for(task: dict) -> list[dict]:
    task = _registered_task(task)
    sources = _sources()
    return [sources[identity] for identity in task["source_ids"]]


def task_status(task: dict) -> dict:
    task = _registered_task(task)
    blockers = list(task["blockers"])
    allowed = (task["task_id"] == "PF1966-UV-T1" and task["runner"] == "pftb1966_replay_v2"
               and task["work_type"] == "published_table_numerical_replay"
               and task["achievement_line"] == "A03" and task["source_ids"] == ["PF01"])
    if not allowed:
        blockers.append("没有获准的执行适配器；仅可开展资料与协议工作")
    else:
        try:
            validate_inputs(ROOT / "data/pftb1966_table1.csv", ROOT / "protocols/pftb1966_uv.json",
                            ROOT / "data/sources.json")
        except (OSError, ValueError) as exc:
            blockers.append(f"固定输入合同未通过：{exc}")
    return {"execution_status": "blocked" if blockers else "runnable", "blockers": blockers,
            "scientific_review_status": "review_required"}


def _registered_task(task: dict) -> dict:
    if type(task) is not dict or type(task.get("task_id")) is not str:
        raise WorkbenchError("A complete registered task is required")
    registered = get_task(task["task_id"])
    try:
        assert_exact(registered, task, "task")
    except ValueError as exc:
        raise WorkbenchError("Task differs from the registered catalog; no qualification granted") from exc
    return registered
