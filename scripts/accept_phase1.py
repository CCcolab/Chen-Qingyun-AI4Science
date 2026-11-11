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
            excluded.append({"path": name, "reason": "Local-only test source is not distributed"})
            continue
        member = ROOT / name
        if member.is_symlink() or not member.is_file():
            raise ValueError(f"Missing or symlinked upstream member: {name}")
        actual = sha256(member)
        checks.append({"path": name, "expected_sha256": expected,
                       "actual_sha256": actual, "equal": actual == expected})
    expected_count = 19 if include_tests else 18
    if len(seen) != 19 or len(checks) != expected_count or not all(check["equal"] for check in checks):
        raise ValueError("One or more retained upstream files changed")
    return {"manifest_sha256": actual_manifest_hash, "files_checked": len(checks),
            "manifest_member_count": len(seen), "excluded_by_distribution_policy": excluded,
            "all_equal": True, "files": checks}


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
               "website_modified": False, "status": "failed", "errors": []}
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
        if args.skip_tests:
            summary["original_delivery_verifier"] = "not_run_original_test_member_not_distributed"
        else:
            # The strict original-package verifier applies only when local tests are available.
            with tempfile.TemporaryDirectory(prefix="chen-upstream-") as temporary:
                snapshot = Path(temporary)
                for member in ["SHA256SUMS", *[item["path"] for item in integrity["files"]]]:
                    destination = snapshot / member
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(ROOT / member, destination)
                verified = run("original-delivery-verifier",
                               [sys.executable, "scripts/verify_delivery.py"], snapshot)
                if verified["exit_code"] != 0:
                    raise ValueError("The unchanged original delivery verifier failed")
            summary["original_delivery_verifier"] = "passed"
            if not (ROOT / "tests").is_dir():
                raise ValueError("Local tests are unavailable; use --skip-tests for published-source verification")
            tested = run("all-tests", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"])
            counts = re.search(r"Ran (\d+) tests?", tested["stderr_text"])
            summary["tests_run"] = int(counts.group(1)) if counts else None
            if tested["exit_code"] != 0 or not summary["tests_run"]:
                summary["tests_status"] = "failed"
                raise ValueError("The complete local test suite failed or was empty")
            summary["tests_status"] = "passed"
        generated = output / "replay"
        replayed = run("numerical-replay", [sys.executable, "-m", "chen_research", "--output", str(generated)])
        if replayed["exit_code"] != 0:
            raise ValueError("PF1966-UV-T1 replay failed")
        comparisons = [compare_result(ROOT / "results" / name, generated / name) for name in RESULT_NAMES]
        save_json(output / "result-comparison.json", comparisons)
        summary["result_files_compared"] = len(comparisons)
        summary["all_result_bytes_equal"] = all(item["byte_equal"] for item in comparisons)
        summary["all_result_fields_equal"] = all(item["all_fields_equal"] for item in comparisons)
        if not summary["all_result_bytes_equal"] or not summary["all_result_fields_equal"]:
            raise ValueError("Replay differs from the delivered baseline; see result-comparison.json")
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
                      "evidence_directory": str(output), "errors": summary["errors"]},
                     ensure_ascii=False))
    return 0 if summary["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
