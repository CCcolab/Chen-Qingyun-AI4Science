"""Stage the preserved static website; publish no research data, logs or handoff documents."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil

from check_site import BASELINE, SITE, inspect_site


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("scratch/site-dist"),
                        help="New or empty publish directory")
    parser.add_argument("--require-node", action="store_true", help="Require inline JavaScript syntax validation")
    args = parser.parse_args()
    output = args.output.resolve()
    if output == SITE.resolve() or SITE.resolve() in output.parents:
        parser.error("The publish directory must be outside the immutable site source")
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        parser.error("--output must be a new or empty directory")
    checked = inspect_site(require_node=args.require_node)
    if checked["status"] != "passed":
        print(json.dumps({"status": "failed", "errors": checked["errors"], "warnings": checked["warnings"]},
                         ensure_ascii=False))
        return 1
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    members = [entry for entry in baseline["files"] if Path(entry["path"]).suffix in {".html", ".json"}]
    if len(members) != 17 or sum(entry["path"].endswith(".html") for entry in members) != 15:
        raise ValueError("The publish allowlist must contain exactly 15 HTML and two JSON files")
    output.mkdir(parents=True, exist_ok=True)
    copied = []
    for entry in members:
        target = output / entry["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(SITE / entry["path"], target)
        actual_hash = hashlib.sha256(target.read_bytes()).hexdigest()
        if actual_hash != entry["sha256"]:
            raise ValueError(f"Copied website bytes differ: {entry['path']}")
        copied.append(entry["path"])
    (output / ".nojekyll").write_bytes(b"")
    published = {path.relative_to(output).as_posix() for path in output.rglob("*") if path.is_file()}
    if published != set(copied) | {".nojekyll"}:
        raise ValueError("The publish directory contains unexpected members")
    print(json.dumps({"status": "passed", "output": str(output), "html_count": 15,
                      "json_count": 2, "published_member_count": len(published),
                      "all_source_bytes_preserved": True,
                      "published_files": sorted(published), "scientific_review_status": "review_required",
                      "website_deployed": False, "warnings": checked["warnings"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
