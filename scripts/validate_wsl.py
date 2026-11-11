"""Validate the original ZIP and a committed integration in WSL's Linux filesystem.

Run with Ubuntu python3, from the mounted source repository. Outputs are evidence,
never modifications to the original package or a website publication.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import subprocess
import sys
import tempfile
import zipfile

from accept_phase1 import RESULT_NAMES, compare_result, save_json


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_SHA256 = "623127d317b3a4ecc51052e43816286a3dd04eb95f41fc8bf7c3bb8d76bc2d4f"
ARCHIVE_ROOT = "Chen_Qingyun_AI_Research_20261111"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, default=ROOT.parent / f"{ARCHIVE_ROOT}.zip")
    parser.add_argument("--output", type=Path, required=True, help="New evidence directory")
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        parser.error("Use a new evidence directory; previous records are never overwritten")
    output.mkdir(parents=True)
    (output / "logs").mkdir()
    summary = {"status": "failed", "started_at_utc": datetime.now(timezone.utc).isoformat(),
               "commands": [], "errors": [], "scientific_review_status": "review_required",
               "result_type": "published_table_numerical_replay", "model_api_called": False,
               "quantum_calculation": "not_performed", "experiment": "not_performed",
               "future_hypotheses": "not_tested", "GitHub_Actions_executed": False,
               "website_modified": False}

    def run(label, command, cwd=ROOT):
        process = subprocess.run(command, cwd=cwd, capture_output=True, encoding="utf-8",
                                 errors="replace", check=False,
                                 env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1",
                                      "PYTHONIOENCODING": "utf-8"})
        for stream in ("stdout", "stderr"):
            (output / "logs" / f"{label}.{stream}.txt").write_text(
                getattr(process, stream), encoding="utf-8", newline="\n")
        summary["commands"].append({"label": label, "command": command, "cwd": str(cwd),
                                    "exit_code": process.returncode,
                                    "stdout": f"logs/{label}.stdout.txt",
                                    "stderr": f"logs/{label}.stderr.txt"})
        if process.returncode:
            raise ValueError(f"{label} failed with exit {process.returncode}")
        return process

    try:
        if platform.system() != "Linux" or "wsl2" not in platform.release().lower():
            raise ValueError("This formal acceptance requires a WSL 2 Linux kernel")
        if sys.version_info < (3, 10):
            raise ValueError("Python 3.10+ is required")
        actual_hash = hashlib.sha256(args.archive.read_bytes()).hexdigest()
        summary["archive_sha256"] = actual_hash
        if actual_hash != ARCHIVE_SHA256:
            raise ValueError("ZIP does not match the user-supplied delivery")
        summary["source_commit"] = run("source-commit", ["git", "rev-parse", "HEAD"]).stdout.strip()
        summary["source_branch"] = run("source-branch", ["git", "branch", "--show-current"]).stdout.strip()
        with tempfile.TemporaryDirectory(prefix="chen-phase1-wsl2-") as temporary:
            staging = Path(temporary)
            fs = run("linux-filesystem", ["stat", "-f", "-c", "%T", str(staging)]).stdout.strip()
            if fs in {"9p", "drvfs"}:
                raise ValueError("Staging must use the Linux filesystem")
            summary["linux_staging_filesystem"] = fs
            summary["linux_staging_directory"] = str(staging)
            with zipfile.ZipFile(args.archive) as archive:
                members = archive.infolist()
                names = [member.filename for member in members]
                if len(names) != 20 or len(set(names)) != 20:
                    raise ValueError("Expected exactly 20 unique archive members")
                for member in members:
                    path = PurePosixPath(member.filename)
                    if (path.is_absolute() or ".." in path.parts or "\\" in member.filename
                            or path.parts[0] != ARCHIVE_ROOT
                            or ((member.external_attr >> 16) & 0o170000) == 0o120000):
                        raise ValueError("Unsafe archive member")
                archive.extractall(staging)
            original = staging / ARCHIVE_ROOT
            run("original-integrity", [sys.executable, "scripts/verify_delivery.py"], original)
            original_tests = run("original-tests", [sys.executable, "-m", "unittest", "discover",
                                                    "-s", "tests", "-v"], original)
            count = re.search(r"Ran (\d+) tests?", original_tests.stderr)
            summary["original_tests_run"] = int(count.group(1)) if count else None
            replay = output / "original-replay"
            run("original-replay", [sys.executable, "-m", "chen_research", "--output", str(replay)], original)
            comparisons = [compare_result(original / "results" / name, replay / name)
                           for name in RESULT_NAMES]
            save_json(output / "original-result-comparison.json", comparisons)
            if not all(item["byte_equal"] and item["all_fields_equal"] for item in comparisons):
                raise ValueError("The original ZIP replay differs from its delivered results")
            summary["original_result_bytes_equal"] = True
            summary["original_result_fields_equal"] = True
            integrated = staging / "integration"
            run("clone-committed-integration", ["git", "clone", "--no-hardlinks", "--single-branch",
                                                "--branch", summary["source_branch"], str(ROOT), str(integrated)])
            cloned_commit = run("cloned-commit", ["git", "rev-parse", "HEAD"], integrated).stdout.strip()
            if cloned_commit != summary["source_commit"]:
                raise ValueError("Source branch changed during staging; rerun against a fixed commit")
            run("integrated-acceptance", [sys.executable, "scripts/accept_phase1.py", "--output",
                                           str(output / "integration")], integrated)
            integrated_summary = json.loads((output / "integration/summary.json").read_text(encoding="utf-8"))
            summary["integrated_tests_run"] = integrated_summary["tests_run"]
            summary["integrated_result_bytes_equal"] = integrated_summary["all_result_bytes_equal"]
            summary["integrated_result_fields_equal"] = integrated_summary["all_result_fields_equal"]
            summary["integrated_source_worktree_dirty"] = integrated_summary["source_worktree_dirty"]
            summary["upstream_files_verified"] = integrated_summary["upstream_files_verified"]
            summary["status"] = "passed"
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as exc:
        summary["errors"].append(str(exc))
    finally:
        summary["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
        save_json(output / "summary.json", summary)
    print(json.dumps({key: value for key, value in summary.items() if key != "commands"}, ensure_ascii=False))
    return 0 if summary["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
