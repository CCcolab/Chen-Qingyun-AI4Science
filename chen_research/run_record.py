"""Create a new evidence-bound run without replacing historical replay results."""

from __future__ import annotations

import csv
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import re
import stat
import subprocess
import sys
from uuid import uuid4

from .uv_replay import ReproducibilityError, replay, write_outputs
from .input_contract import MAX_INPUT_BYTES


ROOT = Path(__file__).resolve().parents[1]
RESULT_NAME = "pftb1966-uv-replay.json"
CANDIDATE_NAME = "website-candidate.json"
MANIFEST_NAME = "run-manifest.json"
PAYLOAD_NAME = "publication-payload.json"
FAILURE_ROOT = ROOT / "scratch" / "failures"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def json_bytes(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")


def assert_safe_path(path: Path, *, must_exist: bool = True, directory: bool | None = None) -> Path:
    """Reject lexical traversal and links/reparse points, including parent directories."""
    path = Path(path)
    if ".." in path.parts or "\x00" in str(path):
        raise ReproducibilityError("运行记录路径不得包含父目录跳转或空字符")
    path = path.absolute()
    if str(path).startswith(("\\\\", "//")):
        raise ReproducibilityError("运行记录不自动访问网络共享路径")
    for component in [*reversed(path.parents), path]:
        try:
            information = component.lstat()
        except FileNotFoundError:
            continue
        if (stat.S_ISLNK(information.st_mode)
                or getattr(information, "st_file_attributes", 0) & 0x400
                or getattr(component, "is_junction", lambda: False)()):
            raise ReproducibilityError("运行记录路径不得经过符号链接或重解析点")
    if must_exist and not path.exists():
        raise ReproducibilityError(f"运行记录所需文件不存在：{path.name}")
    if path.exists() and directory is not None:
        correct = path.is_dir() if directory else path.is_file()
        if not correct:
            raise ReproducibilityError("运行记录路径的文件／目录类型不符")
    return path


def active_code_paths(root: Path = ROOT) -> list[Path]:
    """The whole current Python package plus the acceptance entry point are bound."""
    root = assert_safe_path(root, directory=True)
    package = assert_safe_path(root / "chen_research", directory=True)
    paths = sorted(package.glob("*.py")) + [root / "scripts/accept_phase1.py"]
    if not paths:
        raise ReproducibilityError("没有可绑定的实际执行源码")
    for path in paths:
        assert_safe_path(path, directory=False)
    return paths


def binding(path: Path, run_dir: Path) -> dict:
    path = assert_safe_path(path, directory=False)
    data = path.read_bytes()
    return {"path": path.relative_to(run_dir).as_posix(),
            "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}


def _write_exclusive(path: Path, data: bytes) -> None:
    assert_safe_path(path, must_exist=False, directory=False)
    path.parent.mkdir(parents=True, exist_ok=True)
    assert_safe_path(path.parent, directory=True)
    with path.open("xb") as handle:
        handle.write(data)


def _audit_text(value: str, *, limit: int = 4096) -> str:
    """Keep path/diagnostic metadata without persisting credential-shaped values."""
    value = re.sub(r"(?i)(https?://)[^/\s@]+@", r"\1[redacted]@", value)
    value = re.sub(r"(?i)\b(?:sk-(?:proj-)?[A-Za-z0-9_-]{6,}|gh[pousr]_[A-Za-z0-9_]{6,})",
                   "[redacted]", value)
    value = re.sub(r"(?i)\b(?:bearer\s+\S+|(?:api[_-]?key|token|password|secret)\s*[:=]\s*[^;\s,]+)",
                   "[redacted]", value)
    return value if len(value) <= limit else value[:limit] + "[truncated]"


def failure_error(error: Exception) -> dict:
    """Bind the original diagnostic, but omit fragments supplied by input bodies."""
    original = str(error)
    safe = original
    if safe.startswith("JSON 重复字段："):
        safe = "JSON 重复字段：[输入字段名未保存]"
    match = re.fullmatch(r"观测 (.+) 的对象、编号、数值或来源定位不符", safe, flags=re.DOTALL)
    if match and match.group(1) not in {f"UV{number:02d}" for number in range(1, 11)}:
        safe = "观测 [输入编号未保存] 的对象、编号、数值或来源定位不符"
    safe = _audit_text(safe, limit=2048)
    return {"type": type(error).__name__, "message": safe,
            "message_redacted": safe != original,
            "original_message_sha256": hashlib.sha256(original.encode("utf-8", errors="replace")).hexdigest()}


def _failure_input(path: Path) -> dict:
    """Read at most the fixed input limit, never a link, device or network share."""
    recorded = {"path": _audit_text(str(path)), "sha256": None, "bytes": None,
                "hash_status": "unavailable"}
    try:
        physical = assert_safe_path(path, directory=False)
        recorded["absolute_path"] = _audit_text(str(physical))
        information = physical.stat()
        if not stat.S_ISREG(information.st_mode):
            recorded["hash_status"] = "omitted_not_regular_file"
            return recorded
        if information.st_size > MAX_INPUT_BYTES:
            recorded["hash_status"] = "omitted_size_exceeds_fixed_input_limit"
            return recorded
        flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
        with os.fdopen(os.open(physical, flags), "rb") as handle:
            opened = os.fstat(handle.fileno())
            if not stat.S_ISREG(opened.st_mode) or opened.st_size > MAX_INPUT_BYTES:
                recorded["hash_status"] = "omitted_not_safe_regular_input"
                return recorded
            data = handle.read(MAX_INPUT_BYTES + 1)
        if len(data) > MAX_INPUT_BYTES:
            recorded["hash_status"] = "omitted_size_exceeds_fixed_input_limit"
            return recorded
        assert_safe_path(physical, directory=False)
        final = physical.stat()
        if (final.st_dev, final.st_ino, final.st_size, final.st_mtime_ns) != (
                opened.st_dev, opened.st_ino, opened.st_size, opened.st_mtime_ns):
            recorded["hash_status"] = "omitted_input_changed_while_reading"
            return recorded
        recorded.update(sha256=hashlib.sha256(data).hexdigest(), bytes=len(data), hash_status="recorded")
    except (OSError, ReproducibilityError, TypeError, ValueError) as error:
        recorded["hash_unavailable_error_type"] = type(error).__name__
    return recorded


def write_failure_record(error: Exception, data_path: Path, protocol_path: Path,
                         sources_path: Path, requested_output: Path, *, started_at_utc: str) -> Path:
    """Audit a failed CLI attempt independently of its untrusted output path.

    No input body, environment variables, candidate result or success manifest is
    written. Failure to write this record must be reported by the CLI itself.
    """
    recorded = utc_now()
    identifier = str(uuid4())
    code = []
    code_status = "recorded"
    try:
        for path in active_code_paths(ROOT):
            raw = path.read_bytes()
            code.append({"source_path": path.relative_to(ROOT).as_posix(),
                         "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)})
    except (OSError, ReproducibilityError, TypeError, ValueError):
        code_status = "incomplete_unavailable_source"
    arguments = list(sys.argv)
    safe_arguments = [_audit_text(argument) for argument in arguments]
    record = {"schema_version": "1.0", "record_type": "failed_fixed_task_cli_attempt",
              "failure_id": identifier, "task_id": "PF1966-UV-T1", "status": "failed",
              "scientific_review_status": "review_required", "publication_status": "review_required",
              "started_at_utc": started_at_utc, "recorded_at_utc": recorded,
              "execution": {"kind": "cli", "argv": safe_arguments,
                            "argv_redacted": safe_arguments != arguments,
                            "original_argv_sha256": hashlib.sha256(json_bytes(arguments)).hexdigest(),
                            "working_directory": _audit_text(str(Path.cwd())),
                            "exit_code": 2, "status": "failed"},
              "requested_output": _audit_text(str(requested_output)),
              "inputs": {"data": _failure_input(data_path), "protocol": _failure_input(protocol_path),
                         "sources": _failure_input(sources_path)},
              "error": failure_error(error), "code_fingerprint_status": code_status, "code": code,
              "input_contents_recorded": False, "failure_record_contains_candidate_results": False,
              "original_scan_reverified_by_this_run": False,
              "independent_transcription_signoff": "pending"}
    root = assert_safe_path(FAILURE_ROOT, must_exist=False, directory=True)
    directory = root / f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{identifier}"
    assert_safe_path(directory, must_exist=False, directory=True)
    directory.mkdir(parents=True, exist_ok=False)
    target = directory / "failure.json"
    _write_exclusive(target, json_bytes(record))
    return target


def _git_state() -> dict:
    state = {"available": False, "commit": None, "branch": None, "dirty": None}
    try:
        def command(*args):
            return subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                                  text=True, encoding="utf-8", errors="replace", timeout=15,
                                  check=True).stdout.strip()
        state.update(available=True, commit=command("rev-parse", "HEAD"),
                     branch=command("branch", "--show-current"),
                     dirty=bool(command("status", "--porcelain")))
    except (OSError, subprocess.SubprocessError):
        state = {"available": False, "commit": None, "branch": None, "dirty": None}
    return state


def _environment() -> dict:
    release = platform.release()
    environment = {"schema_version": "1.0", "recorded_at_utc": utc_now(),
                   "python_version": platform.python_version(), "python_executable": sys.executable,
                   "operating_system": platform.system(), "kernel": release,
                   "platform": platform.platform(), "machine": platform.machine(),
                   "wsl_kernel_detected": "microsoft" in release.lower(),
                   "wsl2_kernel_detected": "wsl2" in release.lower(), "git": _git_state(),
                   "tests_run": 0, "tests_status": "not_run_by_runner",
                   "scientific_review_status": "review_required",
                   "original_scan_reverified_by_this_run": False,
                   "independent_transcription_signoff": "pending",
                   "model_api_called": False, "quantum_calculation": "not_performed",
                   "experiment": "not_performed"}
    if platform.system() == "Linux" and hasattr(platform, "freedesktop_os_release"):
        environment["os_release"] = platform.freedesktop_os_release()
    return environment


def _invocation(value) -> dict:
    if value is None:
        return {"kind": "python_api", "call": "chen_research.run_record.create_run"}
    if not isinstance(value, dict) or set(value) != {"kind", "argv"} or value["kind"] != "cli":
        raise ReproducibilityError("invocation 仅可省略为 API 调用，或记录当前真实 CLI argv")
    if (not isinstance(value["argv"], list) or any(type(item) is not str for item in value["argv"])
            or value["argv"] != list(sys.argv)):
        raise ReproducibilityError("CLI 调用记录必须与当前 sys.argv 一致")
    return {"kind": "cli", "argv": list(value["argv"])}


def publication_payload(result: dict, observations: list[dict], source: dict,
                        protocol: dict, run_id: str) -> dict:
    """The exact pending display content is hashed before any scientific review."""
    return {
        "schema_version": "1.0", "record_id": f"{result['task_id']}:{run_id}",
        "run_id": run_id, "task_id": result["task_id"], "result_type": result["result_type"],
        "publication_status": "review_required", "title": "PF1966-UV-T1 原表数值重放",
        "source": {**source, "location": protocol["location"]},
        "provenance": {key: result[key] for key in (
            "data_sha256", "protocol_sha256", "source_registry_sha256", "code_sha256",
            "validator_code_sha256", "source_pdf_sha256")},
        "observations": observations, "measurement_id_pairs": result["measurement_id_pairs"],
        "numeric_summary": result["measurements_and_derived_shifts"],
        "comparisons": result["comparisons"],
        "experimental_uncertainty_nm": result["experimental_uncertainty_nm"],
        "display_rounding_assumption": result["display_rounding_assumption"],
        "excluded_from_comparison": result["excluded_from_comparison"],
        "claim_scope": protocol["claim_scope"], "boundaries": result["boundaries"],
        "scientific_review": {"status": "review_required",
                              "original_scan_reverified_by_this_run": False,
                              "independent_transcription_signoff": "pending"},
    }


def create_run(data_path: Path, protocol_path: Path, sources_path: Path,
               output_dir: Path, invocation=None) -> Path:
    """Validate first, create a new evidence directory, then write its manifest last.

    No success manifest is produced if execution or writing fails. A partially
    written directory is retained for inspection and is never reused/overwritten.
    """
    started = utc_now()
    recorded_invocation = _invocation(invocation)
    paths = {"data": assert_safe_path(data_path, directory=False),
             "protocol": assert_safe_path(protocol_path, directory=False),
             "sources": assert_safe_path(sources_path, directory=False)}
    output = assert_safe_path(output_dir, must_exist=False, directory=True)
    if ".git" in output.parts:
        raise ReproducibilityError("运行产物不得写入 Git 元数据目录")
    for protected in ("site", "data", "protocols", "chen_research", "upstream", "results"):
        protected_root = ROOT / protected
        if output == protected_root or protected_root in output.parents:
            raise ReproducibilityError("运行产物不得写入原数据、历史结果或网站源码目录")
    if output.exists() and any(output.iterdir()):
        raise ReproducibilityError("运行输出目录必须新建或为空，不覆盖既有运行")

    input_bytes = {name: path.read_bytes() for name, path in paths.items()}
    code_paths = active_code_paths()
    code_bytes = {path.relative_to(ROOT).as_posix(): path.read_bytes() for path in code_paths}
    result = replay(paths["data"], paths["protocol"], paths["sources"])
    for relative, field in (("chen_research/uv_replay.py", "code_sha256"),
                            ("chen_research/input_contract.py", "validator_code_sha256")):
        if hashlib.sha256(code_bytes[relative]).hexdigest() != result[field]:
            raise ReproducibilityError("结果中的代码指纹与本次代码快照不一致")
    for name, field in (("data", "data_sha256"), ("protocol", "protocol_sha256"),
                        ("sources", "source_registry_sha256")):
        if (hashlib.sha256(input_bytes[name]).hexdigest() != result[field]
                or paths[name].read_bytes() != input_bytes[name]):
            raise ReproducibilityError("输入在核验期间变化，不能形成有效运行记录")
    for relative, data in code_bytes.items():
        if (ROOT / relative).read_bytes() != data:
            raise ReproducibilityError("执行源码在核验期间变化，不能形成有效运行记录")

    protocol = json.loads(input_bytes["protocol"].decode("utf-8"))
    sources = json.loads(input_bytes["sources"].decode("utf-8"))
    source = next(item for item in sources["sources"] if item["source_id"] == result["source_id"])
    observations = list(csv.DictReader(io.StringIO(input_bytes["data"].decode("utf-8"), newline="")))
    for row in observations:
        row["lambda_max_nm"] = float(row["lambda_max_nm"])
        for field in ("pdf_page", "printed_page", "table_number"):
            row[field] = int(row[field])
    run_id = str(uuid4())
    payload = publication_payload(result, observations, source, protocol, run_id)
    environment = _environment()
    # All core validation and payload preparation precede creation of the target.
    output.mkdir(parents=True, exist_ok=True)
    assert_safe_path(output, directory=True)
    if any(output.iterdir()):
        raise ReproducibilityError("输出目录在准备期间已被占用")
    input_names = {"data": "inputs/pftb1966_table1.csv",
                   "protocol": "inputs/pftb1966_uv.json", "sources": "inputs/sources.json"}
    for name, relative in input_names.items():
        _write_exclusive(output / relative, input_bytes[name])
    code = []
    for relative, data in code_bytes.items():
        target = output / "code" / relative
        _write_exclusive(target, data)
        code.append({"source_path": relative, **binding(target, output)})
    _write_exclusive(output / "environment.json", json_bytes(environment))
    write_outputs(result, output)
    _write_exclusive(output / PAYLOAD_NAME, json_bytes(payload))
    # Snapshots must still represent the inputs and code that were actually checked.
    for name, data in input_bytes.items():
        if assert_safe_path(paths[name], directory=False).read_bytes() != data:
            raise ReproducibilityError("输入在运行期间变化；未生成成功清单")
    for relative, data in code_bytes.items():
        if assert_safe_path(ROOT / relative, directory=False).read_bytes() != data:
            raise ReproducibilityError("源码在运行期间变化；未生成成功清单")
    if {path.relative_to(ROOT).as_posix() for path in active_code_paths()} != set(code_bytes):
        raise ReproducibilityError("运行期间新增／移除了代码模块；未生成成功清单")
    artifacts = {name: binding(output / filename, output) for name, filename in (
        ("environment", "environment.json"), ("complete_result", RESULT_NAME),
        ("candidate_result", CANDIDATE_NAME), ("publication_payload", PAYLOAD_NAME))}
    manifest = {"schema_version": "1.0", "record_type": "fixed_task_run", "run_id": run_id,
                "task_id": result["task_id"], "result_type": result["result_type"],
                "scientific_review_status": "review_required", "started_at_utc": started,
                "finished_at_utc": utc_now(),
                "execution": {"kind": recorded_invocation["kind"], "invocation": recorded_invocation,
                              "process_argv": list(sys.argv), "exit_code": 0,
                              "exit_code_scope": "completed_runner_call", "status": "completed"},
                "inputs": {name: binding(output / relative, output)
                           for name, relative in input_names.items()},
                "code": code, "artifacts": artifacts,
                "tests": {"tests_run": 0, "tests_status": "not_run_by_runner"},
                "source_scan_verification": {"status": "not_reverified_by_this_run",
                                             "source_pdf_sha256": result["source_pdf_sha256"],
                                             "independent_transcription_signoff": "pending"}}
    manifest_path = output / MANIFEST_NAME
    _write_exclusive(manifest_path, json_bytes(manifest))
    return manifest_path


def new_run_directory() -> Path:
    label = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return Path("scratch") / "runs" / f"{label}-{uuid4().hex}"
