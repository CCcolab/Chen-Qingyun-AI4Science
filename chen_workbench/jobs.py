"""Offline, single-worker queue for explicitly allowlisted research runners.

This is a local wall-clock controller, not a quantum-computing queue or an OS
memory sandbox. Jobs cannot supply shell commands or promote scientific review.
"""

from __future__ import annotations

from contextlib import contextmanager
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time
from uuid import UUID, uuid4

from chen_research.input_contract import validate_inputs
from chen_research.review_gate import verify_run
from chen_research.run_record import active_code_paths, assert_safe_path

from .common import (CATALOG_PATH, ROOT, WorkbenchError, now, read_json, safe_output,
                     sha256, workspace_path, write_new)
from .catalog import get_task, task_status


RUNNER = "pftb1966_replay_v2"
TASK_ID = "PF1966-UV-T1"
STATES = {"queued", "running", "completed", "failed", "cancelled", "timed_out"}
TERMINAL = {"completed", "failed", "cancelled", "timed_out"}
_TRANSITIONS = {None: {"queued"}, "queued": {"running", "cancelled", "failed"},
                "running": TERMINAL}


def _uuid(value: str) -> str:
    try:
        if type(value) is not str or str(UUID(value)) != value:
            raise ValueError
    except (ValueError, AttributeError, TypeError) as exc:
        raise WorkbenchError("任务运行编号必须为规范 UUID") from exc
    return value


def _bounded_integer(value, label: str, maximum: int) -> int:
    if type(value) is not int or not 1 <= value <= maximum:
        raise WorkbenchError(f"{label} 必须为 1–{maximum} 的整数")
    return value


def _sha_value(value) -> bool:
    return type(value) is str and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def _code_bindings() -> dict:
    paths = active_code_paths(ROOT)
    package = assert_safe_path(ROOT / "chen_workbench", directory=True)
    for path in sorted(package.glob("*.py")):
        paths.append(assert_safe_path(path, directory=False))
    return {path.relative_to(ROOT).as_posix(): sha256(path) for path in paths}


def _input_bindings() -> dict:
    return {relative: sha256(assert_safe_path(ROOT / relative, directory=False)) for relative in
            ("data/pftb1966_table1.csv", "protocols/pftb1966_uv.json", "data/sources.json")}


def _qualified_task(task_id: str) -> dict:
    task = get_task(task_id)
    status = task_status(task)
    if (task_id != TASK_ID or task.get("runner") != RUNNER
            or status.get("execution_status") != "runnable"):
        reasons = "; ".join(str(item) for item in status.get("blockers", []))
        raise WorkbenchError("任务未具备受控运行资格" + (f"：{reasons}" if reasons else ""))
    validate_inputs(ROOT / "data/pftb1966_table1.csv", ROOT / "protocols/pftb1966_uv.json",
                    ROOT / "data/sources.json")
    return task


def _job_dir(workspace: Path, job_id: str) -> Path:
    return assert_safe_path(workspace / "jobs" / _uuid(job_id), directory=True)


def _job(path: Path) -> dict:
    job = read_json(assert_safe_path(path / "job.json", directory=False))
    expected = {"schema_version", "job_id", "task_id", "runner", "created_at_utc",
                "timeout_seconds", "catalog_sha256", "input_sha256", "code_sha256",
                "scientific_review_status", "model_api_called"}
    if type(job) is not dict or set(job) != expected:
        raise WorkbenchError("运行登记字段不完整或包含未知字段")
    if (job["schema_version"] != "1.0" or _uuid(job["job_id"]) != path.name
            or job["task_id"] != TASK_ID or job["runner"] != RUNNER
            or job["scientific_review_status"] != "review_required"
            or job["model_api_called"] is not False
            or type(job["created_at_utc"]) is not str or not job["created_at_utc"]
            or not _sha_value(job["catalog_sha256"])):
        raise WorkbenchError("运行登记身份或状态不符合固定队列合同")
    _bounded_integer(job["timeout_seconds"], "超时秒数", 300)
    for field in ("input_sha256", "code_sha256"):
        if (type(job[field]) is not dict or not job[field]
                or any(type(key) is not str or not _sha_value(value) for key, value in job[field].items())):
            raise WorkbenchError("运行登记的输入／代码指纹无效")
    return job


def _events(path: Path, job: dict) -> list[dict]:
    directory = assert_safe_path(path / "events", directory=True)
    files = sorted(directory.iterdir())
    result = []
    previous_sha = None
    previous_state = None
    expected_job_sha = sha256(path / "job.json")
    for sequence, file in enumerate(files):
        if not re.fullmatch(rf"{sequence:06d}-(queued|running|completed|failed|cancelled|timed_out)\.json", file.name):
            raise WorkbenchError("运行事件序列存在缺口或未知文件")
        event = read_json(assert_safe_path(file, directory=False))
        expected = {"schema_version", "event_number", "event_id", "job_id", "job_sha256",
                    "recorded_at_utc", "previous_event_sha256", "state", "details"}
        if (type(event) is not dict or set(event) != expected
                or event["schema_version"] != "1.0" or type(event["event_number"]) is not int
                or event["event_number"] != sequence or event["job_id"] != job["job_id"]
                or event["job_sha256"] != expected_job_sha
                or event["previous_event_sha256"] != previous_sha
                or type(event["state"]) is not str
                or event["state"] not in _TRANSITIONS.get(previous_state, set())
                or file.name != f"{sequence:06d}-{event['state']}.json"
                or type(event["recorded_at_utc"]) is not str
                or type(event["details"]) is not dict):
            raise WorkbenchError("运行事件链或状态转移不一致")
        _uuid(event["event_id"])
        result.append(event)
        previous_sha = sha256(file)
        previous_state = event["state"]
    return result


def _append_event(path: Path, job: dict, state: str, details: dict) -> dict:
    events = _events(path, job)
    previous = events[-1]["state"] if events else None
    if state not in _TRANSITIONS.get(previous, set()):
        raise WorkbenchError("禁止覆盖已完成事件或执行无效状态转移")
    sequence = len(events)
    previous_file = (path / "events" / f"{sequence - 1:06d}-{previous}.json") if events else None
    event = {"schema_version": "1.0", "event_number": sequence, "event_id": str(uuid4()),
             "job_id": job["job_id"], "job_sha256": sha256(path / "job.json"),
             "recorded_at_utc": now(), "previous_event_sha256": sha256(previous_file) if previous_file else None,
             "state": state, "details": details}
    write_new(path / "events" / f"{sequence:06d}-{state}.json", event)
    return event


def enqueue(workspace: Path, task_id: str, timeout_seconds: int = 120) -> dict:
    """Create a uniquely identified immutable job only after input qualification."""
    workspace = workspace_path(workspace)
    _bounded_integer(timeout_seconds, "超时秒数", 300)
    task = _qualified_task(task_id)
    if timeout_seconds > task["timeout_seconds"]:
        raise WorkbenchError("超时秒数超过任务已登记的硬预算")
    job_id = str(uuid4())
    job = {"schema_version": "1.0", "job_id": job_id, "task_id": task_id, "runner": RUNNER,
           "created_at_utc": now(), "timeout_seconds": timeout_seconds,
           "catalog_sha256": sha256(CATALOG_PATH), "input_sha256": _input_bindings(),
           "code_sha256": _code_bindings(), "scientific_review_status": "review_required",
           "model_api_called": False}
    # Publish only a fully registered job. A worker must never see an enqueue's
    # partially written job directory during concurrent producer activity.
    directory = safe_output(workspace / "jobs-pending" / job_id)
    directory.mkdir(parents=True, exist_ok=False)
    (directory / "events").mkdir()
    write_new(directory / "job.json", job)
    _append_event(directory, job, "queued", {"qualification": "fixed_runner_and_input_contract_checked"})
    destination = safe_output(workspace / "jobs" / job_id)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise WorkbenchError("运行编号已存在，保留待登记目录供检查")
    directory.rename(destination)
    return {**job, "state": "queued"}


def list_jobs(workspace: Path) -> list[dict]:
    workspace = workspace_path(workspace)
    jobs = workspace / "jobs"
    if not jobs.exists():
        return []
    assert_safe_path(jobs, directory=True)
    records = []
    for path in jobs.iterdir():
        _uuid(path.name)
        assert_safe_path(path, directory=True)
        job = _job(path)
        events = _events(path, job)
        if not events:
            raise WorkbenchError("存在未完成登记的运行目录；请保留并人工检查")
        cancellation_requested = _cancellation_requested(path, job)
        records.append({**job, "state": events[-1]["state"], "latest_event": events[-1],
                        "cancellation_requested": cancellation_requested})
    return sorted(records, key=lambda item: (item["created_at_utc"], item["job_id"]))


def _cancellation_requested(path: Path, job: dict) -> bool:
    marker = path / "cancel-request.json"
    if not marker.exists():
        # assert_safe_path still rejects a dangling symlink at this pathname.
        assert_safe_path(marker, must_exist=False, directory=False)
        return False
    value = read_json(assert_safe_path(marker, directory=False))
    if (type(value) is not dict or set(value) != {"schema_version", "job_id", "requested_at_utc", "reason"}
            or value["schema_version"] != "1.0" or value["job_id"] != job["job_id"]
            or type(value["requested_at_utc"]) is not str or value["reason"] != "user_requested"):
        raise WorkbenchError("取消请求格式或运行编号不符")
    return True


def request_cancel(workspace: Path, job_id: str) -> dict:
    workspace = workspace_path(workspace)
    directory = _job_dir(workspace, job_id)
    job = _job(directory)
    events = _events(directory, job)
    if not events or events[-1]["state"] in TERMINAL:
        raise WorkbenchError("运行已结束或尚未完成登记，不能新增取消请求")
    if not _cancellation_requested(directory, job):
        write_new(directory / "cancel-request.json", {"schema_version": "1.0", "job_id": job_id,
                  "requested_at_utc": now(), "reason": "user_requested"})
    return {"job_id": job_id, "state": events[-1]["state"], "cancellation_requested": True,
            "note": "取消由 worker 处理；本响应不代表进程已经停止"}


@contextmanager
def _worker_lock(workspace: Path):
    marker = safe_output(workspace / "locks" / "worker.lock")
    token = str(uuid4())
    record = {"schema_version": "1.0", "token": token, "pid": os.getpid(), "started_at_utc": now()}
    try:
        write_new(marker, record)
    except (FileExistsError, WorkbenchError) as exc:
        if marker.exists():
            raise WorkbenchError("已有 worker 锁；不会自动移除其他 worker 或异常退出留下的锁") from exc
        raise
    clean_exit = False
    try:
        yield
        clean_exit = True
    finally:
        # Never remove a lock replaced by another process or by an operator.
        # An unhandled crash retains this lock for operator inspection.
        if clean_exit and marker.exists():
            current = read_json(assert_safe_path(marker, directory=False))
            if current != record:
                raise WorkbenchError("worker 锁已变化，已保留供人工检查")
            marker.unlink()


def _command(directory: Path) -> list[str]:
    return [sys.executable, "-B", "-m", "chen_research", "--output", str(directory / "run")]


def _stop_process(process: subprocess.Popen) -> None:
    if process.poll() is not None:
        return
    if os.name == "nt":
        # This fixed command addresses only the already-started child PID/tree.
        try:
            subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"], check=False,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
        except (OSError, subprocess.SubprocessError):
            # Direct-child fallback still reaps the actual fixed runner process.
            if process.poll() is None:
                process.kill()
        if process.poll() is None:
            process.kill()
    else:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            return
        try:
            process.wait(timeout=2)
            return
        except subprocess.TimeoutExpired:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                return
    process.wait(timeout=10)


def _preflight(job: dict) -> None:
    task = _qualified_task(job["task_id"])
    if job["timeout_seconds"] > task["timeout_seconds"]:
        raise WorkbenchError("运行超时秒数超过任务已登记的硬预算")
    if job["catalog_sha256"] != sha256(CATALOG_PATH):
        raise WorkbenchError("任务登记在入队后变化，必须重新入队")
    if job["input_sha256"] != _input_bindings() or job["code_sha256"] != _code_bindings():
        raise WorkbenchError("输入或代码在入队后变化，必须重新入队")


def _run_one(workspace: Path, summary: dict) -> dict:
    directory = _job_dir(workspace, summary["job_id"])
    job = _job(directory)
    if _cancellation_requested(directory, job):
        return _append_event(directory, job, "cancelled", {"process_started": False, "exit_code": None})
    try:
        _preflight(job)
    except Exception as exc:
        return _append_event(directory, job, "failed", {"process_started": False, "exit_code": None,
                             "error_type": type(exc).__name__, "error": str(exc)})
    command = _command(directory)
    _append_event(directory, job, "running", {"command": command, "cwd": str(ROOT),
                                            "timeout_seconds": job["timeout_seconds"]})
    process = None
    finished_state = "failed"
    details = {"process_started": False, "exit_code": None, "stdout": "stdout.txt", "stderr": "stderr.txt"}
    try:
        with (directory / "stdout.txt").open("xb") as stdout, (directory / "stderr.txt").open("xb") as stderr:
            environment = {**os.environ, "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1",
                           "PYTHONIOENCODING": "utf-8"}
            options = ({"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW} if os.name == "nt"
                       else {"start_new_session": True})
            process = subprocess.Popen(command, cwd=ROOT, env=environment, stdout=stdout, stderr=stderr, **options)
            details["process_started"] = True
            started = time.monotonic()
            finished_state = None
            while process.poll() is None:
                if _cancellation_requested(directory, job):
                    finished_state = "cancelled"
                    _stop_process(process)
                    break
                if time.monotonic() - started >= job["timeout_seconds"]:
                    finished_state = "timed_out"
                    _stop_process(process)
                    break
                time.sleep(0.05)
            details["exit_code"] = process.wait()
        details["stdout_sha256"] = sha256(directory / "stdout.txt")
        details["stderr_sha256"] = sha256(directory / "stderr.txt")
        if finished_state is None:
            if details["exit_code"] != 0:
                finished_state = "failed"
            else:
                _preflight(job)
                manifest_path = directory / "run" / "run-manifest.json"
                verified = verify_run(manifest_path)
                finished_state = "completed"
                details.update(run_manifest="run/run-manifest.json", run_manifest_sha256=sha256(manifest_path),
                               run_id=verified["manifest"]["run_id"], scientific_review_status="review_required")
    except BaseException as exc:
        if process is not None and process.poll() is None:
            _stop_process(process)
        if not isinstance(exc, Exception):
            _append_event(directory, job, "cancelled", {"process_started": process is not None,
                          "exit_code": process.returncode if process is not None else None,
                          "reason": "worker_interrupted", "error_type": type(exc).__name__})
            raise
        details.update(error_type=type(exc).__name__, error=str(exc),
                       exit_code=process.returncode if process is not None else None)
        finished_state = "failed"
    for stream in ("stdout", "stderr"):
        stream_path = directory / f"{stream}.txt"
        if stream_path.exists():
            details[f"{stream}_sha256"] = sha256(stream_path)
    return _append_event(directory, job, finished_state, details)


def run_worker(workspace: Path, max_jobs: int = 1) -> dict:
    """Run queued jobs serially under one exclusive local worker lock."""
    workspace = workspace_path(workspace)
    _bounded_integer(max_jobs, "每次处理任务数", 100)
    processed = []
    with _worker_lock(workspace):
        queued = [item for item in list_jobs(workspace) if item["state"] == "queued"]
        for job in queued[:max_jobs]:
            event = _run_one(workspace, job)
            processed.append({"job_id": job["job_id"], "task_id": job["task_id"],
                              "state": event["state"], "details": event["details"]})
    return {"schema_version": "1.0", "worker_mode": "offline_single_worker", "processed": processed,
            "processed_count": len(processed), "scientific_review_status": "review_required",
            "model_api_called": False, "resource_controls": {"wall_clock_limit": True, "memory_isolation": False}}
