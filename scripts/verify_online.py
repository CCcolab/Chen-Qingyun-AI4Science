"""Verify public GitHub Pages bytes and identities without credentials or models."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urlsplit
from urllib.request import Request, urlopen

from a01_publication_contract import (PROGRESS_PATH, PROGRESS_V2_PATH, CURRENT_PATH,
    TOPIC_PATH, AI_RESEARCH_ROUTE, AI_RESEARCH_CONTENT, AI_RESEARCH_DOCUMENT, AI_RESEARCH_RENDERER,
    PRESENTATION_V12_PATH, current_progress_path, effective_website_entries, publication_members, read_json)


ROOT = Path(__file__).resolve().parents[1]
MAX_RESPONSE_BYTES = 2_000_000


def fetch(url: str) -> tuple[dict, bytes]:
    record = {"requested_url": url, "final_url": None, "status": None}
    body = b""
    try:
        request = Request(url, headers={"User-Agent": "Chen-Qingyun-Pages-Acceptance/1.0",
                                        "Cache-Control": "no-cache"})
        try:
            response = urlopen(request, timeout=30)
        except HTTPError as error:
            response = error
        with response:
            record["final_url"] = response.url
            record["status"] = response.code
            record["content_type"] = response.headers.get("Content-Type")
            body = response.read(MAX_RESPONSE_BYTES + 1)
        if len(body) > MAX_RESPONSE_BYTES:
            raise ValueError("Response exceeds the verification size limit")
        record["actual_bytes"] = len(body)
        record["actual_sha256"] = hashlib.sha256(body).hexdigest()
    except (OSError, URLError, ValueError) as error:
        record["error"] = str(error)
    return record, body


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", required=True, help="Actual HTTPS Pages site root")
    parser.add_argument("--output", type=Path, required=True, help="New JSON evidence file")
    parser.add_argument("--commit", help="Optional deployed revision, also used as a cache-busting query")
    args = parser.parse_args()
    parsed = urlsplit(args.base_url)
    if (parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password
            or parsed.query or parsed.fragment):
        parser.error("--base-url must be an HTTPS site root without credentials, query or fragment")
    if args.output.exists():
        parser.error("--output must be a new evidence file")
    base_url = args.base_url.rstrip("/") + "/"
    report = {"started_at_utc": datetime.now(timezone.utc).isoformat(), "base_url": base_url,
              "declared_deployed_commit": args.commit, "status": "failed", "errors": [],
              "published_file_checks": [], "exclusion_checks": [],
              "scope": "Public HTTPS responses, byte identity, source IDs and publication exclusions",
              "browser_interactions_tested": False, "model_api_called": False,
              "credentials_used": False}

    def url_for(path: str) -> str:
        url = base_url + quote(path, safe="/")
        return url + "?" + urlencode({"verification_commit": args.commit}) if args.commit else url

    try:
        baseline = json.loads((ROOT / "provenance/website-baseline.json").read_text(encoding="utf-8"))
        effective, revision = effective_website_entries(ROOT, baseline)
        report["website_revision"] = revision
        if revision["present"]:
            from check_a01_progress import inspect_progress
            consistency = inspect_progress(ROOT)
            report["local_a01_progress_consistency"] = consistency
            if consistency["status"] != "passed":
                raise ValueError("Local A01 progress and revision are not consistent: " + "; ".join(consistency["errors"]))
        members = publication_members(ROOT, effective)
        report["publication_allowlist"] = {"html_count": sum(row["path"].endswith(".html") for row in members),
            "json_count": 2, "member_count_with_marker": len(members)+1,
            "paths": [row["path"] for row in members]}
        json_bodies = {}
        html_bodies = {}
        expected_home = None
        for entry in members:
            name = entry["path"]
            path = PurePosixPath(name)
            if path.is_absolute() or ".." in path.parts or "\\" in name or ":" in name:
                raise ValueError(f"Unsafe baseline path: {name}")
            local = ROOT / "site" / name
            local_bytes = local.read_bytes()
            if (local.is_symlink() or len(local_bytes) != entry["bytes"]
                    or hashlib.sha256(local_bytes).hexdigest() != entry["sha256"]):
                raise ValueError(f"Local site bytes differ from the preserved baseline or explicit A01 revision: {name}")
            if name == "index.html":
                expected_home = entry
            check, body = fetch(url_for(name))
            check.update(path=name, expected_status=200, expected_bytes=entry["bytes"],
                         expected_sha256=entry["sha256"])
            check["equal"] = (check["status"] == 200 and "error" not in check
                              and check.get("actual_bytes") == entry["bytes"]
                              and check.get("actual_sha256") == entry["sha256"])
            report["published_file_checks"].append(check)
            if not check["equal"]:
                report["errors"].append(f"Published response differs from the approved site: {name}")
            if name.endswith(".json") and check["equal"]:
                json_bodies[name] = json.loads(body)
            if name.endswith(".html") and check["status"] == 200 and "error" not in check:
                html_bodies[name] = body

        if revision["present"]:
            from check_site import Page
            progress = read_json(ROOT / current_progress_path(ROOT))
            online_topic = Page(TOPIC_PATH)
            online_topic.feed(html_bodies.get(TOPIC_PATH, b"").decode("utf-8"))
            online_topic.close()
            records = [json.loads(script["text"]) for script in online_topic.scripts
                       if script["attributes"].get("id") == "a01-public-progress"]
            equal = len(records) == 1 and records[0] == progress
            observed = records[0] if len(records) == 1 else None
            actual_execution = observed.get("execution", {}) if isinstance(observed, dict) else {}
            report["online_a01_progress"] = {"equal_to_public_record": equal,
                "task_id": actual_execution.get("task_id"), "run_id": actual_execution.get("run_id"),
                "stage_outcome": actual_execution.get("status"),
                "finished_at_utc": actual_execution.get("finished_at_utc"),
                "scientific_review_status": observed.get("scientific_review_status") if observed else None,
                "release_eligible": observed.get("release_eligible") if observed else None,
                "evidence_archive_commit": observed.get("evidence_archive_commit") if observed else None,
                "unavailable_reason": None if observed else "Online page lacks a unique parseable A01 progress record",
                "expected_task_id": progress["execution"]["task_id"],
                "expected_run_id": progress["execution"]["run_id"]}
            if not equal:
                report["errors"].append("The matched online topic lacks the exact current A01 task/run, outcome or scientific boundaries")
            report["fixed_a01_evidence_checks"] = []
            for evidence in progress["evidence"]:
                raw_url = ("https://raw.githubusercontent.com/CCcolab/Chen-Qingyun-AI4Science/"
                           + progress["evidence_archive_commit"] + "/" + quote(evidence["path"], safe="/"))
                check, _ = fetch(raw_url)
                check.update(id=evidence["id"], fixed_url=evidence["fixed_url"],
                             expected_sha256=evidence["sha256"], expected_bytes=evidence["size_bytes"])
                check["equal"] = (check["status"] == 200 and "error" not in check
                                  and check.get("actual_sha256") == evidence["sha256"]
                                  and check.get("actual_bytes") == evidence["size_bytes"])
                report["fixed_a01_evidence_checks"].append(check)
                if not check["equal"]:
                    report["errors"].append("Fixed S1 A01 evidence is unavailable or differs: " + evidence["path"])

        if expected_home is None:
            raise ValueError("The baseline lacks index.html")
        alias, _ = fetch(url_for(""))
        alias.update(expected_status=200, expected_bytes=expected_home["bytes"],
                     expected_sha256=expected_home["sha256"])
        alias["equal"] = (alias["status"] == 200 and "error" not in alias
                          and alias.get("actual_bytes") == expected_home["bytes"]
                          and alias.get("actual_sha256") == expected_home["sha256"])
        report["homepage_directory_alias"] = alias
        if not alias["equal"]:
            report["errors"].append("The site directory URL does not serve the approved homepage")
        if AI_RESEARCH_ROUTE in effective:
            expected_research = effective[AI_RESEARCH_ROUTE]
            alias, _ = fetch(url_for("research/"))
            alias.update(expected_status=200, expected_bytes=expected_research["bytes"],
                         expected_sha256=expected_research["sha256"])
            alias["equal"] = (alias["status"] == 200 and "error" not in alias
                              and alias.get("actual_bytes") == expected_research["bytes"]
                              and alias.get("actual_sha256") == expected_research["sha256"])
            report["ai_research_directory_alias"] = alias
            if not alias["equal"]:
                report["errors"].append("The research directory URL does not serve the approved second-level page")

        public = json_bodies.get("data/public-sources.json")
        achievements = json_bodies.get("data/achievement-lines.json")
        if public is not None and achievements is not None:
            source_ids = [item["id"] for item in public["sources"]]
            line_ids = [item["id"] for item in achievements["lines"]]
            identities = {"public_source_count": len(source_ids), "public_source_ids": source_ids,
                          "achievement_line_ids": line_ids,
                          "sources_valid": len(source_ids) == len(set(source_ids)) == 51
                          and all(source_ids),
                          "lines_valid": len(line_ids) == 9 and set(line_ids) == {
                              f"A{index:02d}" for index in range(1, 10)}}
            report["public_identities"] = identities
            if not identities["sources_valid"] or not identities["lines_valid"]:
                report["errors"].append("Public JSON source or achievement identities differ")
        else:
            report["errors"].append("Public JSON identity checks could not run against matched responses")

        # These repository-only materials must not be part of the Pages artifact.
        excluded = ["results/website-candidate.json", "validation/",
                    "upstream/chen-qingyun-a2-citations-candidate.zip", PROGRESS_PATH,
                    PROGRESS_V2_PATH, CURRENT_PATH]
        if (ROOT/PRESENTATION_V12_PATH).is_file():
            excluded.extend((AI_RESEARCH_CONTENT, AI_RESEARCH_DOCUMENT, AI_RESEARCH_RENDERER, PRESENTATION_V12_PATH))
        for name in excluded:
            check, _ = fetch(url_for(name))
            check.update(path=name, expected_status=404)
            check["absent"] = check["status"] == 404 and "error" not in check
            report["exclusion_checks"].append(check)
            if not check["absent"]:
                report["errors"].append(f"Repository-only path did not return HTTP 404: {name}")
        report["status"] = "passed" if not report["errors"] else "failed"
    except (OSError, ValueError, KeyError, TypeError) as error:
        report["errors"].append(str(error))
    report["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")
    print(json.dumps({"status": report["status"], "published_files_checked": len(report["published_file_checks"]),
                      "exclusion_paths_checked": len(report["exclusion_checks"]),
                      "output": str(args.output), "errors": report["errors"]}, ensure_ascii=False))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
