"""Evidence-bound scientific review. A name or an approved string is not a signature.

The repository policy is the trust anchor and starts disabled with no reviewers.
Verification uses public keys only; no signing keys are created or stored here.
"""

from __future__ import annotations

import base64
import csv
from datetime import datetime, timezone, timedelta
import hashlib
import html
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import struct
import tempfile
from uuid import UUID, uuid4

from .input_contract import ReproducibilityError, assert_exact, read_strict_json
from .run_record import (ROOT, MANIFEST_NAME, active_code_paths, assert_safe_path,
                         publication_payload, json_bytes)
from .uv_replay import replay, write_outputs


POLICY_PATH = ROOT / "reviews/review-policy.json"
NAMESPACE = "chen-qingyun-scientific-review-v1"
CHECKS = ["source_transcription", "original_attribution", "units_and_arithmetic",
          "sensitivity_and_uncertainty", "claim_boundaries", "publication_text"]


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _object(path: Path) -> tuple[dict, bytes]:
    path = assert_safe_path(path, directory=False)
    if path.stat().st_size > 2_000_000:
        raise ReproducibilityError("Review evidence exceeds its size limit")
    raw = path.read_bytes()
    value = read_strict_json(raw, path.name)
    if type(value) is not dict:
        raise ReproducibilityError("Evidence must be a JSON object")
    return value, raw


def _keys(value, expected: set[str], label: str) -> None:
    if type(value) is not dict or set(value) != expected:
        raise ReproducibilityError(f"{label}: missing or unknown fields")


def _time(value) -> datetime:
    if type(value) is not str:
        raise ReproducibilityError("A timezone-aware review time is required")
    try:
        stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ReproducibilityError("Invalid timestamp") from exc
    if stamp.tzinfo is None or stamp.utcoffset() != timedelta(0):
        raise ReproducibilityError("Timestamps must identify UTC explicitly")
    return stamp


def _string(value, label: str, *, empty: bool = False) -> None:
    if type(value) is not str or (not empty and not value.strip()) or "\x00" in value:
        raise ReproducibilityError(f"{label}: invalid text")


def _argv(value, label: str) -> None:
    if type(value) is not list or not value or any(type(item) is not str or "\x00" in item for item in value):
        raise ReproducibilityError(f"{label}: an actual argument list is required")


def _environment_record(environment: dict, started: datetime, finished: datetime) -> None:
    required = {"schema_version", "recorded_at_utc", "python_version", "python_executable",
                "operating_system", "kernel", "platform", "machine", "wsl_kernel_detected",
                "wsl2_kernel_detected", "git", "tests_run", "tests_status", "scientific_review_status",
                "original_scan_reverified_by_this_run", "independent_transcription_signoff",
                "model_api_called", "quantum_calculation", "experiment"}
    if "os_release" in environment:
        required.add("os_release")
    _keys(environment, required, "environment")
    for field in ("python_version", "python_executable", "operating_system", "kernel", "platform", "machine"):
        _string(environment[field], f"environment.{field}")
    stamp = _time(environment["recorded_at_utc"])
    if not started <= stamp <= finished:
        raise ReproducibilityError("Environment time does not belong to this run")
    assert_exact({"schema_version": "1.0", "tests_run": 0, "tests_status": "not_run_by_runner",
                  "scientific_review_status": "review_required", "original_scan_reverified_by_this_run": False,
                  "independent_transcription_signoff": "pending", "model_api_called": False,
                  "quantum_calculation": "not_performed", "experiment": "not_performed"},
                 {key: environment[key] for key in ("schema_version", "tests_run", "tests_status",
                  "scientific_review_status", "original_scan_reverified_by_this_run",
                  "independent_transcription_signoff", "model_api_called", "quantum_calculation", "experiment")},
                 "environment.scientific_claims")
    kernel = environment["kernel"].lower()
    assert_exact({"wsl_kernel_detected": "microsoft" in kernel, "wsl2_kernel_detected": "wsl2" in kernel},
                 {key: environment[key] for key in ("wsl_kernel_detected", "wsl2_kernel_detected")}, "environment.wsl")
    git = environment["git"]
    _keys(git, {"available", "commit", "branch", "dirty"}, "environment.git")
    if type(git["available"]) is not bool:
        raise ReproducibilityError("Invalid Git availability")
    if git["available"]:
        if (type(git["commit"]) is not str or not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", git["commit"])
                or type(git["dirty"]) is not bool):
            raise ReproducibilityError("Invalid Git commit or worktree state")
        _string(git["branch"], "environment.git.branch", empty=True)
    else:
        assert_exact({"available": False, "commit": None, "branch": None, "dirty": None}, git, "environment.git")
    if "os_release" in environment:
        if (environment["operating_system"] != "Linux" or type(environment["os_release"]) is not dict
                or not environment["os_release"]
                or any(type(k) is not str or type(v) is not str for k, v in environment["os_release"].items())):
            raise ReproducibilityError("Invalid Linux release record")


def _file(run_dir: Path, entry: dict, expected_path: str) -> Path:
    _keys(entry, {"path", "sha256", "bytes"}, "file binding")
    path = PurePosixPath(entry["path"]) if type(entry["path"]) is str else None
    if (path is None or path.is_absolute() or ".." in path.parts or "\\" in entry["path"]
            or ":" in entry["path"] or entry["path"] != expected_path
            or type(entry["bytes"]) is not int or entry["bytes"] < 0
            or type(entry["sha256"]) is not str or not re.fullmatch(r"[0-9a-f]{64}", entry["sha256"])):
        raise ReproducibilityError("Invalid evidence file identity")
    target = assert_safe_path(run_dir / expected_path, directory=False)
    raw = target.read_bytes()
    if len(raw) != entry["bytes"] or _sha(raw) != entry["sha256"]:
        raise ReproducibilityError(f"Bound evidence changed: {expected_path}; review is invalid")
    return target


def verify_run(manifest_path: Path) -> dict:
    """Recompute identities and scientific payloads, never trust manifest hashes alone."""
    manifest_path = assert_safe_path(manifest_path, directory=False)
    if manifest_path.name != MANIFEST_NAME:
        raise ReproducibilityError("An actual run-manifest.json is required")
    run_dir = manifest_path.parent
    manifest, raw = _object(manifest_path)
    _keys(manifest, {"schema_version", "record_type", "run_id", "task_id", "result_type",
                     "scientific_review_status", "started_at_utc", "finished_at_utc", "execution",
                     "inputs", "code", "artifacts", "tests", "source_scan_verification"}, "run manifest")
    if (manifest["schema_version"] != "1.0" or manifest["record_type"] != "fixed_task_run"
            or manifest["task_id"] != "PF1966-UV-T1"
            or manifest["result_type"] != "published_table_numerical_replay"
            or manifest["scientific_review_status"] != "review_required"):
        raise ReproducibilityError("Unknown run identity or promoted scientific state")
    try:
        if str(UUID(manifest["run_id"])) != manifest["run_id"]:
            raise ValueError("noncanonical UUID")
    except (ValueError, TypeError, AttributeError) as exc:
        raise ReproducibilityError("Invalid run ID") from exc
    started, finished = _time(manifest["started_at_utc"]), _time(manifest["finished_at_utc"])
    if started > finished:
        raise ReproducibilityError("Run times are reversed")
    execution = manifest["execution"]
    _keys(execution, {"kind", "invocation", "process_argv", "exit_code", "exit_code_scope", "status"}, "execution")
    if (type(execution["kind"]) is not str or execution["kind"] not in {"cli", "python_api"} or type(execution["exit_code"]) is not int
            or execution["exit_code"] != 0 or execution["status"] != "completed"
            or execution["exit_code_scope"] != "completed_runner_call"):
        raise ReproducibilityError("The run did not complete successfully")
    _argv(execution["process_argv"], "execution.process_argv")
    if execution["kind"] == "cli":
        assert_exact({"kind": "cli", "argv": execution["process_argv"]}, execution["invocation"], "execution.invocation")
    else:
        assert_exact({"kind": "python_api", "call": "chen_research.run_record.create_run"},
                     execution["invocation"], "execution.invocation")
    assert_exact({"tests_run": 0, "tests_status": "not_run_by_runner"}, manifest["tests"], "run.tests")
    _keys(manifest["inputs"], {"data", "protocol", "sources"}, "inputs")
    inputs = {key: _file(run_dir, manifest["inputs"][key], path) for key, path in (
        ("data", "inputs/pftb1966_table1.csv"), ("protocol", "inputs/pftb1966_uv.json"),
        ("sources", "inputs/sources.json"))}
    expected_code = {path.relative_to(ROOT).as_posix(): path for path in active_code_paths()}
    code = manifest["code"]
    if type(code) is not list or len(code) != len(expected_code):
        raise ReproducibilityError("Runtime code inventory changed; a new run and review are required")
    seen = set()
    for item in code:
        _keys(item, {"source_path", "path", "sha256", "bytes"}, "code binding")
        relative = item["source_path"]
        if type(relative) is not str or relative not in expected_code or relative in seen:
            raise ReproducibilityError("Unknown, missing or duplicate runtime module")
        seen.add(relative)
        snapshot = _file(run_dir, {k: item[k] for k in ("path", "sha256", "bytes")}, "code/" + relative)
        if snapshot.read_bytes() != expected_code[relative].read_bytes():
            raise ReproducibilityError(f"Current code changed: {relative}; previous approval cannot be reused")
    _keys(manifest["artifacts"], {"environment", "complete_result", "candidate_result", "publication_payload"}, "artifacts")
    artifacts = {key: _file(run_dir, manifest["artifacts"][key], path) for key, path in (
        ("environment", "environment.json"), ("complete_result", "pftb1966-uv-replay.json"),
        ("candidate_result", "website-candidate.json"), ("publication_payload", "publication-payload.json"))}
    result = replay(inputs["data"], inputs["protocol"], inputs["sources"])
    actual_result, _ = _object(artifacts["complete_result"])
    assert_exact(result, actual_result, "complete_result")
    with tempfile.TemporaryDirectory(prefix="chen-gate-replay-") as temporary:
        directory = Path(temporary)
        write_outputs(result, directory)
        expected_candidate, _ = _object(directory / "website-candidate.json")
        actual_candidate, _ = _object(artifacts["candidate_result"])
        assert_exact(expected_candidate, actual_candidate, "candidate_result")
    protocol, _ = _object(inputs["protocol"])
    sources, _ = _object(inputs["sources"])
    with inputs["data"].open(encoding="utf-8", newline="") as handle:
        observations = list(csv.DictReader(handle))
    for row in observations:
        row["lambda_max_nm"] = float(row["lambda_max_nm"])
        for field in ("pdf_page", "printed_page", "table_number"):
            row[field] = int(row[field])
    payload, _ = _object(artifacts["publication_payload"])
    assert_exact(publication_payload(result, observations, sources["sources"][0], protocol,
                                     manifest["run_id"]), payload, "publication_payload")
    assert_exact({"status": "not_reverified_by_this_run", "source_pdf_sha256": result["source_pdf_sha256"],
                  "independent_transcription_signoff": "pending"},
                 manifest["source_scan_verification"], "source_scan_verification")
    environment, _ = _object(artifacts["environment"])
    _environment_record(environment, started, finished)
    return {"manifest": manifest, "manifest_sha256": _sha(raw), "run_dir": run_dir,
            "result": result, "candidate": actual_candidate, "payload": payload,
            "protocol": protocol, "environment": environment}


def load_policy() -> tuple[dict, str]:
    policy, raw = _object(POLICY_PATH)
    _keys(policy, {"schema_version", "policy_id", "release_enabled", "signature_namespace",
                   "minimum_reviewers", "required_checks", "authorized_reviewers"}, "policy")
    if (policy["schema_version"] != "1.0" or policy["policy_id"] != "PF1966-UV-T1.scientific-review.v1"
            or type(policy["release_enabled"]) is not bool or type(policy["minimum_reviewers"]) is not int
            or policy["minimum_reviewers"] != 1 or policy["signature_namespace"] != NAMESPACE
            or policy["required_checks"] != CHECKS or type(policy["authorized_reviewers"]) is not list):
        raise ReproducibilityError("Unknown or incomplete scientific review policy")
    ids = set()
    for reviewer in policy["authorized_reviewers"]:
        _keys(reviewer, {"reviewer_id", "full_name", "affiliation", "public_key", "qualified_checks",
                         "identity_verified_by_maintainer", "revoked"}, "authorized reviewer")
        identity = reviewer["reviewer_id"]
        if (type(identity) is not str or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.@-]{0,79}", identity)
                or identity in ids or reviewer["qualified_checks"] != CHECKS
                or reviewer["identity_verified_by_maintainer"] is not True
                or type(reviewer["revoked"]) is not bool
                or any(type(reviewer[x]) is not str or not reviewer[x].strip() for x in ("full_name", "affiliation"))):
            raise ReproducibilityError("A maintainer-verified, qualified reviewer identity is required")
        ids.add(identity)
        key = reviewer["public_key"]
        if type(key) is not str or not re.fullmatch(r"ssh-ed25519 [A-Za-z0-9+/=]+", key):
            raise ReproducibilityError("Only a registered Ed25519 public verification key is accepted")
        try:
            decoded = base64.b64decode(key.split()[1], validate=True)
            expected_prefix = struct.pack(">I", 11) + b"ssh-ed25519" + struct.pack(">I", 32)
            if len(decoded) != len(expected_prefix) + 32 or not decoded.startswith(expected_prefix):
                raise ValueError("Invalid Ed25519 wire format")
        except (ValueError, struct.error) as exc:
            raise ReproducibilityError("Invalid reviewer public key") from exc
    return policy, _sha(raw)


def _binding(context: dict, policy_sha256: str) -> dict:
    manifest = context["manifest"]
    return {"run_manifest_sha256": context["manifest_sha256"], "policy_sha256": policy_sha256,
            "inputs_sha256": {k: v["sha256"] for k, v in manifest["inputs"].items()},
            "code_sha256": {v["source_path"]: v["sha256"] for v in manifest["code"]},
            "complete_result_sha256": manifest["artifacts"]["complete_result"]["sha256"],
            "candidate_result_sha256": manifest["artifacts"]["candidate_result"]["sha256"],
            "environment_sha256": manifest["artifacts"]["environment"]["sha256"],
            "publication_payload_sha256": manifest["artifacts"]["publication_payload"]["sha256"]}


def _exclusive(path: Path, raw: bytes) -> None:
    path = assert_safe_path(path, must_exist=False, directory=False)
    for name in (".git", "site", "data", "protocols", "chen_research", "upstream", "results"):
        protected = ROOT / name
        if path == protected or protected in path.parents:
            raise ReproducibilityError("Review output must not replace sources, historical results or site files")
    if path.exists():
        raise ReproducibilityError("Existing review evidence is never overwritten")
    path.parent.mkdir(parents=True, exist_ok=True)
    assert_safe_path(path.parent, directory=True)
    with path.open("xb") as handle:
        handle.write(raw)


def create_review_request(manifest_path: Path, output: Path) -> dict:
    context = verify_run(manifest_path)
    _, policy_hash = load_policy()
    request = {"schema_version": "1.0", "record_type": "scientific_review",
               "review_id": str(uuid4()), "run_id": context["manifest"]["run_id"],
               "task_id": "PF1966-UV-T1", "binding": _binding(context, policy_hash),
               "reviewer": {"reviewer_id": None, "full_name": None, "affiliation": None},
               "decision": "pending", "reviewed_at_utc": None,
               "checks": {key: False for key in CHECKS},
               "source_evidence": {"source_pdf_sha256": context["protocol"]["source_pdf_sha256"],
                                   "scan_page_sha256": context["protocol"]["inspected_scan_page_sha256"],
                                   "transcription_status": "pending"},
               "attestation": {"method": "openssh-detached", "namespace": NAMESPACE, "status": "unsigned"},
               "comments": ""}
    _exclusive(output, json_bytes(request))
    return request


def verify_detached_signature(raw: bytes, signature: Path, reviewer: dict) -> None:
    signature = assert_safe_path(signature, directory=False)
    if signature.stat().st_size > 32_768:
        raise ReproducibilityError("Invalid signature size")
    _verify_signature_bytes(raw, signature.read_bytes(), reviewer)


def _verify_signature_bytes(raw: bytes, signature_raw: bytes, reviewer: dict) -> None:
    if not signature_raw or len(signature_raw) > 32_768:
        raise ReproducibilityError("Invalid signature size")
    if (type(reviewer.get("reviewer_id")) is not str
            or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.@-]{0,79}", reviewer["reviewer_id"])
            or type(reviewer.get("public_key")) is not str
            or not re.fullmatch(r"ssh-ed25519 [A-Za-z0-9+/=]+", reviewer["public_key"])):
        raise ReproducibilityError("Invalid signature verification identity")
    executable = shutil.which("ssh-keygen")
    if not executable:
        raise ReproducibilityError("OpenSSH ssh-keygen is required to verify a real detached signature")
    with tempfile.TemporaryDirectory(prefix="chen-review-key-") as temporary:
        allowed = Path(temporary) / "allowed_signers"
        allowed.write_text(f"{reviewer['reviewer_id']} {reviewer['public_key']}\n", encoding="utf-8", newline="\n")
        frozen_signature = Path(temporary) / "review.sig"
        frozen_signature.write_bytes(signature_raw)
        result = subprocess.run([executable, "-Y", "verify", "-f", str(allowed), "-I", reviewer["reviewer_id"],
                                 "-n", NAMESPACE, "-s", str(frozen_signature)], input=raw, capture_output=True,
                                timeout=30, check=False)
        if result.returncode != 0:
            raise ReproducibilityError("Scientific review signature did not verify against the registered identity")


def validate_review(manifest_path: Path, review_path: Path, signature: Path,
                    source_pdf: Path, scan_page: Path) -> dict:
    context = verify_run(manifest_path)
    policy, policy_hash = load_policy()
    if not policy["release_enabled"] or not policy["authorized_reviewers"]:
        raise ReproducibilityError("Scientific release is disabled; no qualified named reviewer has been registered")
    review, raw = _object(review_path)
    _keys(review, {"schema_version", "record_type", "review_id", "run_id", "task_id", "binding", "reviewer",
                   "decision", "reviewed_at_utc", "checks", "source_evidence", "attestation", "comments"}, "review")
    if (review["schema_version"] != "1.0" or review["record_type"] != "scientific_review"
            or review["decision"] != "approved" or review["task_id"] != "PF1966-UV-T1"
            or review["run_id"] != context["manifest"]["run_id"]):
        raise ReproducibilityError("No approved review for this exact run")
    try:
        if str(UUID(review["review_id"])) != review["review_id"]:
            raise ValueError("noncanonical UUID")
    except (ValueError, TypeError, AttributeError) as exc:
        raise ReproducibilityError("Invalid review ID") from exc
    assert_exact(_binding(context, policy_hash), review["binding"], "review.binding")
    assert_exact({key: True for key in CHECKS}, review["checks"], "review.checks")
    assert_exact({"method": "openssh-detached", "namespace": NAMESPACE, "status": "signed"},
                 review["attestation"], "review.attestation")
    stamp = _time(review["reviewed_at_utc"])
    if stamp < _time(context["manifest"]["finished_at_utc"]) or stamp > datetime.now(timezone.utc) + timedelta(minutes=5):
        raise ReproducibilityError("Review timestamp does not correspond to this completed run")
    _keys(review["reviewer"], {"reviewer_id", "full_name", "affiliation"}, "reviewer")
    registered = next((r for r in policy["authorized_reviewers"]
                       if r["reviewer_id"] == review["reviewer"]["reviewer_id"] and not r["revoked"]), None)
    if registered is None:
        raise ReproducibilityError("Reviewer is unregistered or revoked")
    assert_exact({key: registered[key] for key in ("reviewer_id", "full_name", "affiliation")},
                 review["reviewer"], "reviewer.identity")
    expected = {"source_pdf_sha256": context["protocol"]["source_pdf_sha256"],
                "scan_page_sha256": context["protocol"]["inspected_scan_page_sha256"],
                "transcription_status": "professionally_checked"}
    assert_exact(expected, review["source_evidence"], "source_evidence")
    for path, key in ((source_pdf, "source_pdf_sha256"), (scan_page, "scan_page_sha256")):
        actual = assert_safe_path(path, directory=False).read_bytes()
        if _sha(actual) != expected[key]:
            raise ReproducibilityError("Original scan material is absent or differs from the reviewed identity")
    if type(review["comments"]) is not str or len(review["comments"]) > 8_000:
        raise ReproducibilityError("Invalid review comments")
    signature = assert_safe_path(signature, directory=False)
    signature_raw = signature.read_bytes()
    _verify_signature_bytes(raw, signature_raw, registered)
    return {**context, "review": review, "review_raw": raw, "signature_raw": signature_raw,
            "review_sha256": _sha(raw), "signature_sha256": _sha(signature_raw), "policy_sha256": policy_hash}


def _page(payload: dict, *, approved: bool, json_name: str) -> bytes:
    esc = lambda value: html.escape(str(value), quote=True)
    source = payload["source"]
    status = "科学签认记录已核验" if approved else "待专业转录核校与具名科学签认"
    rows = "".join("<tr>" + "".join(f"<td>{esc(row[key])}</td>" for key in (
        "compound_id", "donor_solvent", "lambda_h_nm", "lambda_b_nm", "delta_lambda_nm",
        "blue_shift_cm_inverse")) + "</tr>" for row in payload["numeric_summary"])
    content = f"""<!doctype html><html lang="zh-CN"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(payload['title'])}</title>
<style>body{{font:17px/1.7 system-ui;max-width:1050px;margin:3rem auto;padding:0 24px;color:#173b36}}
table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #ccd7d2;padding:.6rem}}pre{{white-space:pre-wrap;overflow-wrap:anywhere;background:#f2f5f1;padding:1rem}}small{{color:#456}}</style>
<h1>{esc(payload['title'])}</h1><p><strong>{esc(status)}</strong></p>
<p>本记录仅为原表数值重放。原作者：{esc('、'.join(source['authors']))}；{esc(source['year'])}，{esc(source['venue'])}。</p>
<p>来源编号 {esc(source['source_id'])}，印刷 p.21 表1，PDF第4页。<a href="{esc(source['url'])}">原论文入口</a></p>
<p>运行编号 {esc(payload['run_id'])}；与既有 PFtB 科学正文分别归档。</p>
<h2>原表观测与稳定编号</h2><pre>{esc(json.dumps(payload['observations'],ensure_ascii=False,indent=2))}</pre>
<h2>固定计算</h2><p>Δλ = λH − λB（nm）；蓝移 = 10⁷ × (1/λB − 1/λH)（cm⁻¹）。</p>
<table><thead><tr><th>碘代物</th><th>给体</th><th>λH nm</th><th>λB nm</th><th>Δλ nm</th><th>蓝移 cm⁻¹</th></tr></thead><tbody>{rows}</tbody></table>
<p>保留但未用于该固定溶剂比较的观测：</p><pre>{esc(json.dumps(payload['excluded_from_comparison'],ensure_ascii=False,indent=2))}</pre>
<h2>敏感性与不确定性</h2><p>{esc(payload['display_rounding_assumption']['interpretation'])}；原实验不确定度未提供。</p>
<pre>{esc(json.dumps(payload['numeric_summary'],ensure_ascii=False,indent=2))}</pre>
<pre>{esc(json.dumps(payload['comparisons'],ensure_ascii=False,indent=2))}</pre>
<h2>来源、结果与代码指纹</h2><pre>{esc(json.dumps(payload['provenance'],ensure_ascii=False,indent=2))}</pre>
<h2>本记录的科学签认状态</h2><pre>{esc(json.dumps(payload['scientific_review'],ensure_ascii=False,indent=2))}</pre>
<h2>论断范围与边界</h2><p>{esc(payload['claim_scope'])}</p><pre>{esc(json.dumps(payload['boundaries'],ensure_ascii=False,indent=2))}</pre>
<p><a href="{esc(json_name)}">下载本记录数据</a></p><small>工程验收、量化计算、实验验证与科学签认分别记录。候选历史保持 review_required。</small></html>"""
    return content.encode("utf-8")


def preview_run(manifest_path: Path, output_dir: Path) -> Path:
    context = verify_run(manifest_path)
    output_dir = assert_safe_path(output_dir, must_exist=False, directory=True)
    if output_dir.exists():
        raise ReproducibilityError("Use a new preview directory")
    _exclusive(output_dir / "candidate-record.json", json_bytes(context["payload"]))
    _exclusive(output_dir / "PF1966-UV-T1.html", _page(context["payload"], approved=False, json_name="candidate-record.json"))
    create_review_request(manifest_path, output_dir / "review-request.json")
    return output_dir / "PF1966-UV-T1.html"


def export_reviewed(manifest_path: Path, review_path: Path, signature: Path,
                    source_pdf: Path, scan_page: Path, output_dir: Path) -> Path:
    context = validate_review(manifest_path, review_path, signature, source_pdf, scan_page)
    output_dir = assert_safe_path(output_dir, must_exist=False, directory=True)
    if output_dir.exists():
        raise ReproducibilityError("Use a new reviewed export directory")
    record = json.loads(json.dumps(context["payload"], ensure_ascii=False))
    record["publication_status"] = "scientifically_reviewed"
    record["scientific_review"] = {"status": "signature_verified", "reviewer": context["review"]["reviewer"],
                                   "reviewed_at_utc": context["review"]["reviewed_at_utc"],
                                   "review_sha256": context["review_sha256"],
                                   "signature_sha256": context["signature_sha256"],
                                   "policy_sha256": context["policy_sha256"], "binding": context["review"]["binding"]}
    catalog = {"schema_version": "1.0", "publication_status": "scientifically_reviewed", "records": [record]}
    _exclusive(output_dir / "reviewed-results.json", json_bytes(catalog))
    _exclusive(output_dir / "PF1966-UV-T1.html", _page(record, approved=True, json_name="reviewed-results.json"))
    _exclusive(output_dir / "review-record.json", context["review_raw"])
    _exclusive(output_dir / "review-record.json.sig", context["signature_raw"])
    return output_dir / "reviewed-results.json"


def empty_catalog(output: Path) -> dict:
    policy, policy_hash = load_policy()
    catalog = {"schema_version": "1.0", "publication_status": "review_required", "records": [],
               "policy_sha256": policy_hash, "release_enabled": policy["release_enabled"],
               "reason": "No independently signed scientific approval has been supplied to this catalog"}
    _exclusive(output, json_bytes(catalog))
    return catalog
