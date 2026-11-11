"""Exercise the distributed offline workflow with real jobs; runs zero unit tests.

The generated proposal is a labelled contract fixture, not model output or a
scientific approval. User excerpts and production pages are never imported here.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import platform
import subprocess
import sys
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from chen_workbench.common import (WorkbenchError, init_workspace, now, read_json,
                                   safe_output, sha256, write_new)
from chen_workbench.catalog import load_catalog, task_status
from chen_workbench.evidence import register_evidence
from chen_workbench.ai_exchange import export_request, import_proposal
from chen_workbench.jobs import enqueue, list_jobs, request_cancel, run_worker
from chen_workbench.report import create_report


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="A new directory under scratch/")
    args = parser.parse_args()
    output = safe_output(args.output)
    if output.exists():
        parser.error("Use a new output directory; acceptance evidence is never overwritten")
    output.mkdir(parents=True)
    summary = {"schema_version": "1.0", "status": "failed", "started_at_utc": now(),
               "tests_run": 0, "tests_status": "not_run_by_distribution_policy",
               "model_api_called": False, "scientific_review_status": "review_required",
               "quantum_calculation": "not_performed", "experiment": "not_performed",
               "proposal_origin": "labelled_contract_fixture_not_model_output", "errors": [],
               "environment": {"python": platform.python_version(), "system": platform.system(),
                               "kernel": platform.release(),
                               "wsl2_kernel_detected": "wsl2" in platform.release().lower()}}
    try:
        revision = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, capture_output=True, check=True)
        summary["source_commit"] = revision.stdout.strip()
        source_state = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, text=True,
                                      capture_output=True, check=True)
        summary["source_worktree_dirty"] = bool(source_state.stdout.strip())
        summary["workbench_code_sha256"] = {path.relative_to(ROOT).as_posix(): sha256(path)
                                             for path in sorted((ROOT / "chen_workbench").glob("*.py"))}
        catalog = load_catalog()
        statuses = [task_status(task) for task in catalog["tasks"]]
        summary.update(task_count=len(statuses), achievement_line_count=len({t["achievement_line"] for t in catalog["tasks"]}),
                       runnable_task_count=sum(s["execution_status"] == "runnable" for s in statuses),
                       blocked_task_count=sum(s["execution_status"] == "blocked" for s in statuses))
        require(summary["task_count"] == 12 and summary["achievement_line_count"] == 9
                and summary["runnable_task_count"] == 1, "Unexpected catalog coverage or execution eligibility")
        workspace = init_workspace(output / "workspace")
        evidence = register_evidence(workspace, "PF01", "transcribed_table",
                                     "封存CSV转录；印刷p.21表1／PDF第4页；本轮未重新核原扫描",
                                     ROOT / "data/pftb1966_table1.csv")
        request = export_request(workspace, "PF1966-UV-T1")
        proposal = read_json(request.parent / "response-template.json")
        proposal["provenance"] = {"tool": "offline_contract_fixture", "model": "not_invoked",
                                   "mode": "external_assistance", "executed_by_platform": False}
        quote = (ROOT / "data/pftb1966_table1.csv").read_text("utf-8").splitlines()[1]
        proposal["claims"] = [{"claim_id": "C001", "kind": "observation",
                               "text": "封存转录中存在这条观测登记；这不是本轮原扫描核校。",
                               "citations": [{"evidence_id": evidence["evidence_id"], "quote": quote,
                                              "locator": evidence["locator"]}]}]
        proposal_path = write_new(output / "proposal-fixture.json", proposal)
        imported = import_proposal(workspace, proposal_path)
        summary["proposal_import"] = imported
        false_proposal = json.loads(json.dumps(proposal))
        false_proposal["claims"][0]["citations"][0]["quote"] = "UNSUPPORTED_QUOTATION_" + str(uuid4())
        false_path = write_new(output / "rejected-proposal-fixture.json", false_proposal)
        try:
            import_proposal(workspace, false_path)
        except WorkbenchError:
            summary["unsupported_citation_rejected"] = True
        else:
            raise ValueError("Unsupported citation was accepted")
        try:
            enqueue(workspace, "PF-03")
        except WorkbenchError:
            summary["blocked_calculation_rejected"] = True
        else:
            raise ValueError("Unapproved computation was enqueued")
        first = enqueue(workspace, "PF1966-UV-T1")
        second = enqueue(workspace, "PF1966-UV-T1")
        cancelled = enqueue(workspace, "PF1966-UV-T1")
        request_cancel(workspace, cancelled["job_id"])
        worker = run_worker(workspace, max_jobs=3)
        write_new(output / "worker-result.json", worker)
        jobs = {job["job_id"]: job for job in list_jobs(workspace)}
        require(jobs[first["job_id"]]["state"] == jobs[second["job_id"]]["state"] == "completed",
                "Two independent real replays did not complete")
        require(jobs[cancelled["job_id"]]["state"] == "cancelled", "Cancellation was not recorded")
        summary["completed_jobs"] = 2
        summary["cancelled_jobs"] = 1
        summary["run_ids"] = [entry["details"]["run_id"] for entry in worker["processed"] if entry["state"] == "completed"]
        require(len(set(summary["run_ids"])) == 2, "Repeated runs reused their identity")
        summary["report"] = str(create_report(workspace))
        summary["status"] = "passed"
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        summary["errors"].append(str(exc))
    finally:
        summary["finished_at_utc"] = now()
        write_new(output / "summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
