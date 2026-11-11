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
import shutil
import subprocess
import sys
import tarfile
import tempfile
import zipfile

from accept_phase1 import RESULT_NAMES, compare_result, save_json


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_SHA256 = "623127d317b3a4ecc51052e43816286a3dd04eb95f41fc8bf7c3bb8d76bc2d4f"
ARCHIVE_ROOT = "Chen_Qingyun_AI_Research_20261111"


def stage_node(archive_path: Path, shasums_path: Path, staging: Path, output: Path) -> Path:
    """Verify the supplied official release checksum and extract only bin/node.

    No tar pathname or symlink is used for a filesystem write. npm, documentation
    and archive links are unnecessary for these syntax checks and are not extracted.
    """
    release = re.fullmatch(r"node-v(24\.\d+\.\d+)-linux-(x64|arm64)\.tar\.xz", archive_path.name)
    if not release:
        raise ValueError("--node-archive must be an official Node 24 Linux x64/arm64 tar.xz filename")
    version = release.group(1)
    evidence = output / "node-runtime"
    evidence.mkdir()
    manifest_bytes = shasums_path.read_bytes()
    (evidence / "SHASUMS256.txt").write_bytes(manifest_bytes)
    matches = []
    for line in manifest_bytes.decode("utf-8").splitlines():
        matched = re.fullmatch(r"([0-9a-fA-F]{64})\s+\*?(.+)", line.strip())
        if matched and matched.group(2) == archive_path.name:
            matches.append(matched.group(1).lower())
    provenance = {"archive_filename": archive_path.name,
                  "expected_official_archive_url": f"https://nodejs.org/dist/v{version}/{archive_path.name}",
                  "expected_official_shasums_url": f"https://nodejs.org/dist/v{version}/SHASUMS256.txt",
                  "archive_bytes": archive_path.stat().st_size,
                  "archive_sha256": hashlib.sha256(archive_path.read_bytes()).hexdigest(),
                  "shasums_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
                  "manifest_matches": matches, "checksum_verified": False,
                  "verification": "SHA-256 against caller-supplied release SHASUMS; signature not verified",
                  "extraction_scope": "regular-file bin/node only; no archive symlinks or hardlinks extracted",
                  "system_install_modified": False}
    retrieval = archive_path.parent / "retrieval.json"
    if retrieval.is_file():
        retrieval_bytes = retrieval.read_bytes()
        json.loads(retrieval_bytes.decode("utf-8"))
        (evidence / "retrieval.json").write_bytes(retrieval_bytes)
        provenance["caller_retrieval_record_sha256"] = hashlib.sha256(retrieval_bytes).hexdigest()
        provenance["caller_retrieval_record"] = "retrieval.json"
    save_json(evidence / "provenance.json", provenance)
    if len(matches) != 1 or provenance["archive_sha256"] != matches[0]:
        raise ValueError("Node archive SHA-256 does not match exactly one SHASUMS entry")
    provenance["checksum_verified"] = True
    save_json(evidence / "provenance.json", provenance)
    release_root = archive_path.name.removesuffix(".tar.xz")
    binary_name = f"{release_root}/bin/node"
    executable = staging / "node-runtime" / release_root / "bin/node"
    with tarfile.open(archive_path, mode="r:xz") as archive:
        binaries = []
        for member in archive.getmembers():
            path = PurePosixPath(member.name)
            if (not member.name or path.is_absolute() or ".." in path.parts
                    or "\\" in member.name or path.parts[0] != release_root):
                raise ValueError("Unsafe Node archive pathname")
            if member.name == binary_name:
                binaries.append(member)
        if len(binaries) != 1 or not binaries[0].isfile():
            raise ValueError("Node archive must contain one regular-file bin/node")
        executable.parent.mkdir(parents=True)
        source = archive.extractfile(binaries[0])
        if source is None:
            raise ValueError("Cannot read the Node executable from its archive")
        with source, executable.open("xb") as target:
            shutil.copyfileobj(source, target)
        executable.chmod(0o755)
    provenance["node_binary_sha256"] = hashlib.sha256(executable.read_bytes()).hexdigest()
    provenance["linux_temporary_executable"] = str(executable)
    save_json(evidence / "provenance.json", provenance)
    return executable


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, default=ROOT.parent / f"{ARCHIVE_ROOT}.zip")
    parser.add_argument("--output", type=Path, required=True, help="New evidence directory")
    parser.add_argument("--node-archive", type=Path, help="Official Node 24 Linux tar.xz (optional)")
    parser.add_argument("--node-shasums", type=Path, help="Its official release SHASUMS256.txt")
    args = parser.parse_args()
    if bool(args.node_archive) != bool(args.node_shasums):
        parser.error("--node-archive and --node-shasums must be supplied together")
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
               "website_modified": False, "original_scan_reverified_by_this_run": False,
               "independent_transcription_signoff": "pending"}
    child_env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8"}

    def run(label, command, cwd=ROOT):
        process = subprocess.run(command, cwd=cwd, capture_output=True, encoding="utf-8",
                                 errors="replace", check=False,
                                 env=child_env)
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
        status_command = ["git", "status", "--porcelain", "--", "."]
        try:
            relative_output = output.relative_to(ROOT)
        except ValueError:
            pass
        else:
            status_command.append(f":(exclude){relative_output.as_posix()}/**")
        source_status = run("source-status", status_command).stdout.strip()
        summary["source_worktree_dirty"] = bool(source_status)
        if source_status:
            raise ValueError("Commit all source changes before formal WSL acceptance")
        with tempfile.TemporaryDirectory(prefix="chen-phase1-wsl2-") as temporary:
            staging = Path(temporary)
            fs = run("linux-filesystem", ["stat", "-f", "-c", "%T", str(staging)]).stdout.strip()
            if fs in {"9p", "drvfs"}:
                raise ValueError("Staging must use the Linux filesystem")
            summary["linux_staging_filesystem"] = fs
            summary["linux_staging_directory"] = str(staging)
            staged_node = (stage_node(args.node_archive.resolve(), args.node_shasums.resolve(), staging, output)
                           if args.node_archive else None)
            if staged_node:
                child_env["PATH"] = str(staged_node.parent) + os.pathsep + child_env.get("PATH", "")
                summary["node_runtime_source"] = "verified_archive_in_linux_temporary_directory"
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
            summary["original_result_comparison_scope"] = "original_zip_v1_cli_vs_original_zip_results_only"
            integrated = staging / "integration"
            run("clone-committed-integration", ["git", "clone", "--no-hardlinks", "--single-branch",
                                                "--branch", summary["source_branch"], str(ROOT), str(integrated)])
            cloned_commit = run("cloned-commit", ["git", "rev-parse", "HEAD"], integrated).stdout.strip()
            if cloned_commit != summary["source_commit"]:
                raise ValueError("Source branch changed during staging; rerun against a fixed commit")
            run("integrated-acceptance", [sys.executable, "scripts/accept_phase1.py", "--skip-tests", "--output",
                                           str(output / "integration")], integrated)
            integrated_summary = json.loads((output / "integration/summary.json").read_text(encoding="utf-8"))
            summary["integrated_tests_run"] = integrated_summary["tests_run"]
            summary["integrated_tests_status"] = integrated_summary["tests_status"]
            summary["integrated_test_execution_policy"] = integrated_summary["test_execution_policy"]
            summary["integrated_result_bytes_equal"] = integrated_summary["all_result_bytes_equal"]
            summary["integrated_result_fields_equal"] = integrated_summary["all_result_fields_equal"]
            summary["integrated_result_comparison_scope"] = integrated_summary["result_comparison_scope"]
            summary["integrated_legacy_result_bytes_equal"] = integrated_summary["legacy_result_bytes_equal"]
            summary["integrated_legacy_result_fields_equal"] = integrated_summary["legacy_result_fields_equal"]
            for key in ("current_numerical_agreement", "current_run_integrity_passed",
                        "current_result_schema_version", "current_candidate_schema_version",
                        "current_result_sha256", "current_candidate_sha256",
                        "current_publication_payload_sha256", "current_run_id",
                        "current_run_manifest", "current_run_manifest_sha256"):
                summary[f"integrated_{key}"] = integrated_summary[key]
            summary["integrated_source_worktree_dirty"] = integrated_summary["source_worktree_dirty"]
            summary["upstream_files_verified"] = integrated_summary["upstream_files_verified"]
            if (integrated / "chen_workbench").is_dir():
                run("offline-workbench-acceptance", [sys.executable, "scripts/accept_workbench.py", "--output",
                                                     str(output / "workbench")], integrated)
                workbench = json.loads((output / "workbench/summary.json").read_text(encoding="utf-8"))
                for key in ("status", "task_count", "achievement_line_count", "runnable_task_count",
                            "blocked_task_count", "completed_jobs", "cancelled_jobs", "run_ids",
                            "tests_run", "tests_status", "model_api_called"):
                    summary[f"workbench_{key}"] = workbench[key]
            if (integrated / "site").is_dir():
                node = str(staged_node) if staged_node else shutil.which("node", path=child_env.get("PATH"))
                if not node:
                    raise ValueError("Website acceptance requires Node 24; provide both Node archive options or an environment Node 24")
                node_version = run("linux-node-version", [node, "--version"], integrated).stdout.strip()
                summary["linux_node_version"] = node_version
                if not re.fullmatch(r"v24\.\d+\.\d+", node_version):
                    raise ValueError(f"Website acceptance requires Node 24; found {node_version}")
                runtime = json.loads(run("linux-node-runtime", [node, "-p",
                    "JSON.stringify({platform:process.platform,arch:process.arch,version:process.version,execPath:process.execPath})"],
                    integrated).stdout)
                if runtime["platform"] != "linux" or runtime["version"] != node_version:
                    raise ValueError("Website acceptance requires a native Linux Node 24 process")
                summary["linux_node_runtime"] = runtime
                summary.setdefault("node_runtime_source", "existing_environment_node24")
                if not staged_node:
                    node_evidence = output / "node-runtime"
                    node_evidence.mkdir()
                    save_json(node_evidence / "provenance.json", {
                        "runtime_source": "existing_environment_node24", "executable": node,
                        "version": node_version, "linux_runtime": runtime,
                        "node_binary_sha256": hashlib.sha256(Path(runtime["execPath"]).read_bytes()).hexdigest(),
                        "release_archive_checksum_verified": False, "system_install_modified": False})
                run("website-static-check", [sys.executable, "scripts/check_site.py", "--require-node", "--output",
                                              str(output / "site-check.json")], integrated)
                run("website-build", [sys.executable, "scripts/build_site.py", "--require-node", "--output",
                                       str(output / "site-dist")], integrated)
                site_check = json.loads((output / "site-check.json").read_text(encoding="utf-8"))
                summary["website_static_status"] = site_check["status"]
                summary["website_source_members_verified"] = site_check["member_count"]
                summary["website_public_source_count"] = site_check["public_source_count"]
                summary["website_javascript_checks"] = len(site_check["javascript_checks"])
                summary["website_publish_member_count"] = sum(path.is_file() for path in (output / "site-dist").rglob("*"))
            summary["status"] = "passed"
    except (OSError, ValueError, KeyError, zipfile.BadZipFile, tarfile.TarError) as exc:
        summary["errors"].append(str(exc))
    finally:
        summary["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
        save_json(output / "summary.json", summary)
    print(json.dumps({key: value for key, value in summary.items() if key != "commands"}, ensure_ascii=False))
    return 0 if summary["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
