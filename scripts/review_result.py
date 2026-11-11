"""Prepare review evidence or export a separately signed, scientifically reviewed record."""
import argparse
import json
from pathlib import Path
import sys
import subprocess

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from chen_research.input_contract import ReproducibilityError
from chen_research.review_gate import (create_review_request, empty_catalog, export_reviewed,
                                       load_policy, preview_run, verify_run)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("verify-run", "request", "preview", "export-reviewed"):
        command = sub.add_parser(name)
        command.add_argument("--run", type=Path, required=True, help="Exact run-manifest.json")
        if name != "verify-run":
            command.add_argument("--output", type=Path, required=True)
        if name == "export-reviewed":
            for flag in ("review", "signature", "source-pdf", "scan-page"):
                command.add_argument("--" + flag, type=Path, required=True)
    catalog = sub.add_parser("empty-catalog")
    catalog.add_argument("--output", type=Path, required=True)
    sub.add_parser("policy-status")
    args = parser.parse_args()
    try:
        if args.command == "verify-run":
            result = verify_run(args.run)
            print(json.dumps({"status": "verified", "run_id": result["manifest"]["run_id"],
                              "manifest_sha256": result["manifest_sha256"],
                              "scientific_review_status": "review_required"}))
        elif args.command == "request":
            create_review_request(args.run, args.output)
        elif args.command == "preview":
            print(preview_run(args.run, args.output))
        elif args.command == "empty-catalog":
            print(json.dumps(empty_catalog(args.output), ensure_ascii=False))
        elif args.command == "policy-status":
            policy, digest = load_policy()
            print(json.dumps({"release_enabled": policy["release_enabled"],
                              "authorized_reviewers": len(policy["authorized_reviewers"]),
                              "policy_sha256": digest, "scientific_review_status": "review_required"}))
        else:
            print(export_reviewed(args.run, args.review, args.signature, args.source_pdf,
                                  args.scan_page, args.output))
    except (ReproducibilityError, OSError, KeyError, TypeError, ValueError, subprocess.SubprocessError) as exc:
        parser.exit(2, f"未通过运行／科学签认门禁：{exc}\n")


if __name__ == "__main__":
    main()
