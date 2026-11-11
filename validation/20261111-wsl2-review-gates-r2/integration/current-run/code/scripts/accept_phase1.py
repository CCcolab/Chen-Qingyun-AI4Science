"""Offline acceptance of the immutable upstream replay and additive integration.

Local full acceptance checks all 19 SHA256SUMS members and the original verifier.
Published-source acceptance excludes the local test member and never claims that
the original complete package or local test suite was verified in GitHub CI.
No source, historical result, publication status, or scientific signoff is changed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parents[1]
UPSTREAM_MANIFEST_SHA256 = "60275b777259e44d7277ffae4f15f71f5f628b1ef5e57286119d8e2b348a507a"
RESULT_NAMES = ("pftb1966-uv-replay.json", "website-candidate.json")
SEALED_ENGINE_MEMBERS = frozenset({
    "chen_research/__init__.py", "chen_research/__main__.py", "chen_research/uv_replay.py",
})
SEALED_ROOT = "upstream/pftb1966-v1"
NUMERICAL_FIELDS = (
    "task_id", "source_id", "result_type", "numerical_status", "scientific_review_status",
    "observations_count", "used_observations_count", "excluded_from_comparison",
    "source_location", "experimental_uncertainty_nm", "display_rounding_assumption",
    "measurements_and_derived_shifts", "comparisons",
)


def upstream_member(name: str) -> Path:
    """Resolve the original manifest identity without treating v2 as v1 code."""
    return ROOT / SEALED_ROOT / name if name in SEALED_ENGINE_MEMBERS else ROOT / name


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
                    encoding="utf-8", newline="\n")


def check_upstream(*, include_tests: bool = True) -> dict:
    manifest = ROOT / "SHA256SUMS"
    actual_manifest_hash = sha256(manifest)
    if actual_manifest_hash != UPSTREAM_MANIFEST_SHA256:
        raise ValueError("The original SHA256SUMS manifest changed")
    checks = []
    seen = set()
    excluded = []
    for line in manifest.read_text(encoding="utf-8").splitlines():
        expected, name = line.split("  ", 1)
        path = PurePosixPath(name)
        if (not re.fullmatch(r"[0-9a-f]{64}", expected) or path.is_absolute()
                or ".." in path.parts or "\\" in name or name in seen):
            raise ValueError(f"Invalid upstream manifest member: {name}")
        seen.add(name)
        if not include_tests and name == "tests/test_uv_replay.py":
            excluded.append({"path": name, "physical_path": name,
                             "reason": "Local-only test source is not distributed"})
            continue
        member = upstream_member(name)
        if member.is_symlink() or not member.is_file():
            raise ValueError(f"Missing or symlinked upstream member: {name}")
        actual = sha256(member)
        checks.append({"path": name, "physical_path": member.relative_to(ROOT).as_posix(),
                       "expected_sha256": expected,
                       "actual_sha256": actual, "equal": actual == expected})
    expected_count = 19 if include_tests else 18
    if len(seen) != 19 or len(checks) != expected_count or not all(check["equal"] for check in checks):
        raise ValueError("One or more retained upstream files changed")
    return {"manifest_sha256": actual_manifest_hash, "files_checked": len(checks),
            "manifest_member_count": len(seen), "excluded_by_distribution_policy": excluded,
            "all_equal": True, "scope": "original_v1_delivery_members_with_sealed_engine",
            "files": checks}


def compare_values(expected, actual, path: str = "$") -> list[dict]:
    """Record every container and leaf check, including exact JSON value types."""
    if type(expected) is not type(actual):
        return [{"path": path, "equal": False, "expected": expected, "actual": actual,
                 "reason": "type_mismatch"}]
    if isinstance(expected, dict):
        checks = [{"path": path, "equal": expected.keys() == actual.keys(),
                   "expected_keys": sorted(expected), "actual_keys": sorted(actual)}]
        for key in sorted(expected.keys() & actual.keys()):
            checks.extend(compare_values(expected[key], actual[key], f"{path}.{key}"))
        return checks
    if isinstance(expected, list):
        checks = [{"path": path, "equal": len(expected) == len(actual),
                   "expected_length": len(expected), "actual_length": len(actual)}]
        for index, (left, right) in enumerate(zip(expected, actual)):
            checks.extend(compare_values(left, right, f"{path}[{index}]"))
        return checks
    return [{"path": path, "equal": expected == actual, "expected": expected, "actual": actual}]


def compare_result(reference: Path, generated: Path) -> dict:
    checks = compare_values(json.loads(reference.read_text(encoding="utf-8")),
                            json.loads(generated.read_text(encoding="utf-8")))
    return {"reference": str(reference), "generated": str(generated),
            "reference_sha256": sha256(reference), "generated_sha256": sha256(generated),
            "byte_equal": reference.read_bytes() == generated.read_bytes(),
            "all_fields_equal": all(check["equal"] for check in checks),
            "field_checks": checks}


def numerical_projection(result: dict, *, candidate: bool = False) -> dict:
    """Compare science, while v2 provenance and the engineering status evolve."""
    fields = (("task_id", "result_type", "publication_status", "source_ids", "numeric_summary")
              if candidate else NUMERICAL_FIELDS)
    projection = {key: result[key] for key in fields}
    projection["boundaries"] = {key: value for key, value in result["boundaries"].items()
                                if key != "phase1_status"}
    return projection


def compare_numerical_result(reference: Path, generated: Path, *, candidate: bool) -> dict:
    checks = compare_values(numerical_projection(load_json(reference), candidate=candidate),
                            numerical_projection(load_json(generated), candidate=candidate))
    return {"reference": str(reference), "generated": str(generated),
            "scope": "v1_v2_scientific_numerical_projection_only",
            "full_file_byte_equality_required": False,
            "full_file_field_equality_required": False,
            "excluded_from_projection": ["schema_version", "input_contract_version",
                "provenance_metadata_and_fingerprints", "transcription_review", "boundaries.phase1_status"],
            "all_projected_fields_equal": all(check["equal"] for check in checks),
            "field_checks": checks}


def load_json(path: Path):
    def unique_object(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError(f"Duplicate JSON key in {path.name}: {key}")
            result[key] = value
        return result

    def nonfinite(value):
        raise ValueError(f"Non-finite JSON value in {path.name}: {value}")

    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object,
                      parse_constant=nonfinite)


def check_current_run(run_dir: Path) -> dict:
    """Check v2 identities and links; this does not grant scientific approval."""
    manifest_path = run_dir / "run-manifest.json"
    manifest = load_json(manifest_path)
    complete = load_json(run_dir / RESULT_NAMES[0])
    candidate = load_json(run_dir / RESULT_NAMES[1])
    payload = load_json(run_dir / "publication-payload.json")
    checks = []

    def equal(expected, actual, path):
        checks.extend(compare_values(expected, actual, path))

    def check_binding(item, expected_path: str) -> Path:
        if not isinstance(item, dict) or set(item) != {"path", "sha256", "bytes"}:
            raise ValueError("Run manifest contains an invalid file binding")
        path = PurePosixPath(item["path"])
        if (path.as_posix() != expected_path or path.is_absolute() or ".." in path.parts
                or "\\" in item["path"]):
            raise ValueError(f"Unexpected run-bound path: {item['path']}")
        physical = run_dir / path
        if (not physical.is_file() or any(component.is_symlink()
                for component in [physical, *physical.parents] if component != run_dir.parent)):
            raise ValueError(f"Missing or symlinked run-bound file: {item['path']}")
        equal(sha256(physical), item["sha256"], f"binding.{expected_path}.sha256")
        equal(physical.stat().st_size, item["bytes"], f"binding.{expected_path}.bytes")
        return physical

    equal("1.0", manifest["schema_version"], "manifest.schema_version")
    equal("fixed_task_run", manifest["record_type"], "manifest.record_type")
    equal("PF1966-UV-T1", manifest["task_id"], "manifest.task_id")
    equal("review_required", manifest["scientific_review_status"], "manifest.scientific_review_status")
    equal("completed", manifest["execution"]["status"], "manifest.execution.status")
    equal(0, manifest["execution"]["exit_code"], "manifest.execution.exit_code")
    equal("cli", manifest["execution"]["kind"], "manifest.execution.kind")
    equal(manifest["execution"]["process_argv"], manifest["execution"]["invocation"]["argv"],
          "manifest.execution.argv")
    recorded_arguments = manifest["execution"]["process_argv"][1:]
    equal(2, len(recorded_arguments), "manifest.execution.argument_count")
    equal("--output", recorded_arguments[0], "manifest.execution.output_option")
    equal(str(run_dir.resolve()), str((ROOT / recorded_arguments[1]).resolve()),
          "manifest.execution.output_argument")
    equal({"tests_run": 0, "tests_status": "not_run_by_runner"}, manifest["tests"], "manifest.tests")
    inputs = {"data": ("inputs/pftb1966_table1.csv", "data/pftb1966_table1.csv"),
              "protocol": ("inputs/pftb1966_uv.json", "protocols/pftb1966_uv.json"),
              "sources": ("inputs/sources.json", "data/sources.json")}
    equal(set(inputs), set(manifest["inputs"]), "manifest.input_keys")
    for key, (relative, original) in inputs.items():
        snapshot = check_binding(manifest["inputs"][key], relative)
        equal(sha256(ROOT / original), sha256(snapshot), f"inputs.{key}.active_sha256")
    expected_code = {path.relative_to(ROOT).as_posix(): path
                     for path in (ROOT / "chen_research").glob("*.py")}
    expected_code["scripts/accept_phase1.py"] = Path(__file__).resolve()
    bound_code = set()
    for item in manifest["code"]:
        source_path = item["source_path"]
        if source_path not in expected_code or source_path in bound_code:
            raise ValueError("Duplicate or unexpected run-bound source module")
        bound_code.add(source_path)
        snapshot = check_binding({key: item[key] for key in ("path", "sha256", "bytes")},
                                 f"code/{source_path}")
        equal(sha256(expected_code[source_path]), sha256(snapshot), f"code.{source_path}.active_sha256")
    equal(set(expected_code), bound_code, "manifest.code_paths")
    artifacts = {"environment": "environment.json", "complete_result": RESULT_NAMES[0],
                 "candidate_result": RESULT_NAMES[1], "publication_payload": "publication-payload.json"}
    equal(set(artifacts), set(manifest["artifacts"]), "manifest.artifact_keys")
    for key, relative in artifacts.items():
        check_binding(manifest["artifacts"][key], relative)
    protocol = load_json(ROOT / "protocols/pftb1966_uv.json")
    registry = load_json(ROOT / "data/sources.json")
    expected_hashes = {"data_sha256": sha256(ROOT / "data/pftb1966_table1.csv"),
                       "protocol_sha256": sha256(ROOT / "protocols/pftb1966_uv.json"),
                       "source_registry_sha256": sha256(ROOT / "data/sources.json"),
                       "code_sha256": sha256(ROOT / "chen_research/uv_replay.py"),
                       "validator_code_sha256": sha256(ROOT / "chen_research/input_contract.py"),
                       "source_pdf_sha256": protocol["source_pdf_sha256"]}
    for key, value in expected_hashes.items():
        equal(value, complete[key], f"complete.{key}")
    for key in ("original_authors", "publication_year", "source_url", "location"):
        equal(protocol[key], complete[key], f"complete.{key}")
    equal("2.0", complete["schema_version"], "complete.schema_version")
    equal("PF1966-UV-T1.fixed.v2", complete["input_contract_version"], "complete.input_contract_version")
    equal("review_required", complete["scientific_review_status"], "complete.scientific_review_status")
    common = ("schema_version", "input_contract_version", "task_id", "result_type",
              "original_authors", "publication_year", "source_url", "location", "source_pdf_sha256",
              "protocol_sha256", "source_registry_sha256", "validator_code_sha256", "observation_ids",
              "measurement_id_pairs", "comparisons", "experimental_uncertainty_nm",
              "display_rounding_assumption", "transcription_review", "boundaries", "data_sha256", "code_sha256")
    expected_candidate = {key: complete[key] for key in common}
    expected_candidate.update(publication_status="review_required", source_ids=[complete["source_id"]],
                              numeric_summary=complete["measurements_and_derived_shifts"])
    equal(expected_candidate, candidate, "candidate_complete_relationship")
    equal(manifest["run_id"], payload["run_id"], "payload.run_id")
    equal(f"PF1966-UV-T1:{manifest['run_id']}", payload["record_id"], "payload.record_id")
    equal("review_required", payload["publication_status"], "payload.publication_status")
    equal(expected_hashes, payload["provenance"], "payload.provenance")
    source = next(item for item in registry["sources"] if item["source_id"] == complete["source_id"])
    equal({**source, "location": protocol["location"]}, payload["source"], "payload.source")
    for key in ("comparisons", "experimental_uncertainty_nm", "display_rounding_assumption",
                "excluded_from_comparison", "measurement_id_pairs", "boundaries"):
        equal(complete[key], payload[key], f"payload.{key}")
    equal(complete["measurements_and_derived_shifts"], payload["numeric_summary"], "payload.numeric_summary")
    equal({"status": "review_required", "original_scan_reverified_by_this_run": False,
           "independent_transcription_signoff": "pending"}, payload["scientific_review"], "payload.scientific_review")
    equal({"status": "not_reverified_by_this_run", "source_pdf_sha256": complete["source_pdf_sha256"],
           "independent_transcription_signoff": "pending"}, manifest["source_scan_verification"],
          "manifest.source_scan_verification")
    environment = load_json(run_dir / "environment.json")
    equal(False, environment["original_scan_reverified_by_this_run"], "environment.original_scan_reverified")
    equal("pending", environment["independent_transcription_signoff"], "environment.transcription_signoff")
    equal("review_required", environment["scientific_review_status"], "environment.scientific_review_status")
    # JSON-safe sorted lists retain the exact type check without serializing sets.
    for item in checks:
        for field in ("expected", "actual"):
            if isinstance(item.get(field), set):
                item[field] = sorted(item[field])
    return {"scope": "v2_run_manifest_artifact_input_code_and_candidate_relationships",
            "all_equal": all(check["equal"] for check in checks), "field_checks": checks,
            "run_id": manifest["run_id"], "run_manifest": str(manifest_path),
            "run_manifest_sha256": sha256(manifest_path),
            "result_schema_version": complete["schema_version"],
            "candidate_schema_version": candidate["schema_version"],
            "complete_result_sha256": sha256(run_dir / RESULT_NAMES[0]),
            "candidate_result_sha256": sha256(run_dir / RESULT_NAMES[1]),
            "publication_payload_sha256": sha256(run_dir / "publication-payload.json")}


def source_inventory(output: Path) -> list[dict]:
    inventory = []
    for path in sorted(ROOT.rglob("*")):
        relative = path.relative_to(ROOT)
        if (set(relative.parts) & {".git", "scratch", "__pycache__", ".venv"}
                or path == output or output in path.parents or not path.is_file()
                or path.suffix in {".pyc", ".pyo"}):
            continue
        if path.is_symlink():
            raise ValueError(f"Source inventory contains a symlink: {relative}")
        inventory.append({"path": relative.as_posix(), "sha256": sha256(path)})
    return inventory


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("scratch/phase1-acceptance"),
                        help="New or empty evidence directory; never overwrites a previous run")
    parser.add_argument("--skip-tests", action="store_true",
                        help="Published-source checks only; the local test suite is not distributed")
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        parser.error("--output must be a new or empty directory")
    output.mkdir(parents=True, exist_ok=True)
    (output / "logs").mkdir()
    summary = {"started_at_utc": datetime.now(timezone.utc).isoformat(),
               "task_id": "PF1966-UV-T1", "result_type": "published_table_numerical_replay",
               "scientific_review_status": "review_required", "commands": [],
               "quantum_calculation": "not_performed", "experiment": "not_performed",
               "future_hypotheses": "not_tested", "model_api_called": False,
               "website_modified": False, "original_scan_reverified_by_this_run": False,
               "independent_transcription_signoff": "pending", "status": "failed", "errors": [],
               "result_comparison_scope": {
                   "all_result_bytes_equal": "sealed_v1_cli_vs_historical_results_only",
                   "all_result_fields_equal": "sealed_v1_cli_vs_historical_results_only",
                   "current_numerical_agreement": "v2_vs_v1_explicit_scientific_projection_only",
                   "current_full_file_equality_with_v1": "not_required_schema_and_provenance_changed"}}
    summary["test_execution_policy"] = "local_only_not_run" if args.skip_tests else "run_local_tests"
    summary["tests_run"] = 0 if args.skip_tests else None
    summary["tests_status"] = "not_run_by_distribution_policy" if args.skip_tests else "pending"
    environment = {"python_version": platform.python_version(), "python_executable": sys.executable,
                   "operating_system": platform.system(), "kernel": platform.release(),
                   "machine": platform.machine(), "platform": platform.platform(),
                   "working_directory": str(ROOT),
                   "wsl2_kernel_detected": "wsl2" in platform.release().lower(),
                   "third_party_python_dependencies": []}
    if hasattr(platform, "freedesktop_os_release") and platform.system() == "Linux":
        environment["os_release"] = platform.freedesktop_os_release()
    save_json(output / "environment.json", environment)

    def run(label: str, command: list[str], cwd: Path = ROOT) -> dict:
        started = datetime.now(timezone.utc).isoformat()
        child_env = os.environ.copy()
        child_env["PYTHONDONTWRITEBYTECODE"] = "1"
        child_env["PYTHONIOENCODING"] = "utf-8"
        process = subprocess.run(command, cwd=cwd, env=child_env, capture_output=True,
                                 text=True, encoding="utf-8", errors="replace", check=False)
        stdout_name, stderr_name = f"logs/{label}.stdout.txt", f"logs/{label}.stderr.txt"
        (output / stdout_name).write_text(process.stdout, encoding="utf-8", newline="\n")
        (output / stderr_name).write_text(process.stderr, encoding="utf-8", newline="\n")
        record = {"label": label, "command": command, "cwd": str(cwd),
                  "started_at_utc": started, "finished_at_utc": datetime.now(timezone.utc).isoformat(),
                  "exit_code": process.returncode, "stdout": stdout_name, "stderr": stderr_name}
        summary["commands"].append(record)
        return {**record, "stdout_text": process.stdout, "stderr_text": process.stderr}

    try:
        integrity = check_upstream(include_tests=not args.skip_tests)
        save_json(output / "upstream-integrity.json", integrity)
        summary["upstream_files_verified"] = integrity["files_checked"]
        save_json(output / "source-inventory.json", source_inventory(output))
        try:
            git = run("git-revision", ["git", "rev-parse", "HEAD"])
            summary["source_commit"] = git["stdout_text"].strip() if git["exit_code"] == 0 else None
            git_status = run("git-status", ["git", "status", "--porcelain"])
            summary["source_worktree_dirty"] = (bool(git_status["stdout_text"].strip())
                                                  if git_status["exit_code"] == 0 else None)
        except OSError:
            summary["source_commit"] = None
            summary["source_worktree_dirty"] = None
        # Run v1 from its own package namespace, never from active v2 modules.
        with tempfile.TemporaryDirectory(prefix="chen-upstream-") as temporary:
            snapshot = Path(temporary)
            for member in ["SHA256SUMS", *[item["path"] for item in integrity["files"]]]:
                destination = snapshot / member
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(upstream_member(member), destination)
            if args.skip_tests:
                summary["original_delivery_verifier"] = "not_run_original_test_member_not_distributed"
            else:
                # The strict original verifier applies to exactly its 19-member snapshot.
                verified = run("original-delivery-verifier",
                               [sys.executable, "scripts/verify_delivery.py"], snapshot)
                if verified["exit_code"] != 0:
                    raise ValueError("The unchanged original delivery verifier failed")
                summary["original_delivery_verifier"] = "passed"
            legacy_generated = output / "legacy-replay"
            replayed = run("sealed-v1-numerical-replay",
                           [sys.executable, "-m", "chen_research", "--output", str(legacy_generated)], snapshot)
            if replayed["exit_code"] != 0:
                raise ValueError("The sealed v1 PF1966-UV-T1 replay failed")
        comparisons = [compare_result(ROOT / "results" / name, legacy_generated / name)
                       for name in RESULT_NAMES]
        save_json(output / "legacy-result-comparison.json", {
            "scope": "sealed_v1_cli_vs_historical_results_only", "results": comparisons})
        summary["result_files_compared"] = len(comparisons)
        summary["all_result_bytes_equal"] = all(item["byte_equal"] for item in comparisons)
        summary["all_result_fields_equal"] = all(item["all_fields_equal"] for item in comparisons)
        summary["legacy_result_bytes_equal"] = summary["all_result_bytes_equal"]
        summary["legacy_result_fields_equal"] = summary["all_result_fields_equal"]
        if not summary["all_result_bytes_equal"] or not summary["all_result_fields_equal"]:
            raise ValueError("Sealed v1 replay differs from historical results; see legacy-result-comparison.json")
        if not args.skip_tests:
            if not (ROOT / "tests").is_dir():
                raise ValueError("Local tests are unavailable; use --skip-tests for published-source verification")
            tested = run("all-tests", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"])
            counts = re.search(r"Ran (\d+) tests?", tested["stderr_text"])
            summary["tests_run"] = int(counts.group(1)) if counts else None
            if tested["exit_code"] != 0 or not summary["tests_run"]:
                summary["tests_status"] = "failed"
                raise ValueError("The complete local test suite failed or was empty")
            summary["tests_status"] = "passed"
        generated = output / "current-run"
        replayed = run("current-v2-numerical-replay",
                       [sys.executable, "-m", "chen_research", "--output", str(generated)])
        if replayed["exit_code"] != 0:
            raise ValueError("Current v2 PF1966-UV-T1 run failed")
        numerical = [compare_numerical_result(ROOT / "results" / name, generated / name,
                                             candidate=name == "website-candidate.json")
                     for name in RESULT_NAMES]
        save_json(output / "current-numerical-comparison.json", numerical)
        summary["current_numerical_agreement"] = all(item["all_projected_fields_equal"] for item in numerical)
        if not summary["current_numerical_agreement"]:
            raise ValueError("Current v2 science projection differs from v1; see current-numerical-comparison.json")
        current_integrity = check_current_run(generated)
        save_json(output / "current-run-integrity.json", current_integrity)
        summary.update(current_run_integrity_passed=current_integrity["all_equal"],
                       current_result_schema_version=current_integrity["result_schema_version"],
                       current_candidate_schema_version=current_integrity["candidate_schema_version"],
                       current_result_sha256=current_integrity["complete_result_sha256"],
                       current_candidate_sha256=current_integrity["candidate_result_sha256"],
                       current_publication_payload_sha256=current_integrity["publication_payload_sha256"],
                       current_run_id=current_integrity["run_id"],
                       current_run_manifest=current_integrity["run_manifest"],
                       current_run_manifest_sha256=current_integrity["run_manifest_sha256"])
        if not current_integrity["all_equal"]:
            raise ValueError("Current v2 run identities disagree; see current-run-integrity.json")
        summary["status"] = "passed"
    except (OSError, ValueError, KeyError, TypeError) as exc:
        summary["errors"].append(str(exc))
    finally:
        summary["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
        save_json(output / "summary.json", summary)
    print(json.dumps({"status": summary["status"], "tests_run": summary.get("tests_run"),
                      "tests_status": summary.get("tests_status"),
                      "all_result_bytes_equal": summary.get("all_result_bytes_equal"),
                      "all_result_fields_equal": summary.get("all_result_fields_equal"),
                      "result_comparison_scope": summary["result_comparison_scope"],
                      "current_numerical_agreement": summary.get("current_numerical_agreement"),
                      "current_run_integrity_passed": summary.get("current_run_integrity_passed"),
                      "current_result_schema_version": summary.get("current_result_schema_version"),
                      "current_run_manifest": summary.get("current_run_manifest"),
                      "evidence_directory": str(output), "errors": summary["errors"]},
                     ensure_ascii=False))
    return 0 if summary["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
