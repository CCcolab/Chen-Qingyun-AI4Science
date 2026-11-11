"""Check the imported, byte-preserved website without changing scientific text.

This is a static migration check, not a browser/deployment or scientific review.
Only Python's standard library is required. Node syntax checking is optional.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path, PurePosixPath
import posixpath
import re
import shutil
import subprocess
import tempfile
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
BASELINE = ROOT / "provenance/website-baseline.json"
ARCHIVE_SHA256 = "fa9740d7a244ab4d52885600a312487869d780a82517aa0d0a401215696c4d3e"
PROTECTED_JSON = {
    "data/public-sources.json": "94f8b9f6d0849deb9f26f75947205cfc8c4eb0973045fe958f2121237d987062",
    "data/achievement-lines.json": "1c9ec28bf41a7d79214e84a1c07f3bea1e0d91630dd3a88c93c39ff68a9bccec",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_member_set(site: Path, expected: set[str]) -> tuple[set[str], dict, list[str]]:
    """Allow only the empty, regular Pages marker outside the baseline members."""
    actual = {path.relative_to(site).as_posix() for path in site.rglob("*")
              if path.is_file() or path.is_symlink()}
    marker = site / ".nojekyll"
    present = marker.exists() or marker.is_symlink()
    regular = marker.is_file() and not marker.is_symlink()
    size = marker.stat().st_size if regular else None
    accepted = present and regular and size == 0
    marker_report = {"path": ".nojekyll", "present": present, "accepted": accepted,
                     "bytes": size, "is_symlink": marker.is_symlink(),
                     "role": "GitHub Pages deployment marker; not an original ZIP member"}
    errors = []
    if present and not accepted:
        errors.append("The additional site/.nojekyll must be an empty regular file, not a symlink")
    allowed_extra = {".nojekyll"} if accepted else set()
    missing = expected - actual
    extra = actual - expected - allowed_extra
    if missing or extra:
        errors.append(f"Website member set changed; missing={sorted(missing)}, extra={sorted(extra)}")
    return actual, marker_report, errors


class Page(HTMLParser):
    def __init__(self, path: str):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.ids = []
        self.links = []
        self.data = {}
        self.scripts = []
        self._script = None

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if attributes.get("id"):
            self.ids.append(attributes["id"])
        if tag == "a" and attributes.get("name"):
            self.ids.append(attributes["name"])
        for attribute in ("href", "src"):
            if attributes.get(attribute) is not None:
                self.links.append({"attribute": attribute, "value": attributes[attribute],
                                   "line": self.getpos()[0]})
        for name, value in attrs:
            if name.startswith("data-") and value:
                self.data.setdefault(name, set()).add(value)
        if tag == "script":
            self._script = {"attributes": attributes, "line": self.getpos()[0], "text": ""}

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_data(self, data):
        if self._script is not None:
            self._script["text"] += data

    def handle_endtag(self, tag):
        if tag == "script" and self._script is not None:
            self.scripts.append(self._script)
            self._script = None


def inspect_site(*, require_node: bool = False) -> dict:
    report = {"checked_at_utc": datetime.now(timezone.utc).isoformat(), "status": "failed",
              "scope": "static byte integrity, identities, links and optional JavaScript syntax",
              "browser_navigation_tested": False, "deployed_site_tested": False,
              "scientific_review_status": "review_required", "website_modified": False,
              "errors": [], "warnings": [], "file_checks": [], "link_checks": [],
              "javascript_checks": [], "protected_json_checks": []}
    errors = report["errors"]
    try:
        baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
        if baseline["archive_sha256"] != ARCHIVE_SHA256:
            errors.append("Website baseline does not identify the approved source ZIP")
        if baseline.get("member_count") != 21 or baseline.get("html_count") != 15:
            errors.append("Website baseline must contain 21 members and 15 HTML files")
        if baseline["protected_json_sha256"] != PROTECTED_JSON:
            errors.append("Protected JSON fingerprints in the baseline changed")
        expected = {}
        for entry in baseline["files"]:
            name = entry["path"]
            path = PurePosixPath(name)
            if (not name or path.is_absolute() or ".." in path.parts or "\\" in name
                    or name in expected or not re.fullmatch(r"[0-9a-f]{64}", entry["sha256"])):
                raise ValueError(f"Unsafe or duplicate baseline path: {name}")
            expected[name] = entry
        if len(expected) != 21:
            errors.append("Expected exactly 21 unique baseline members")
        actual, deployment_marker, member_errors = check_member_set(SITE, set(expected))
        report["baseline_member_count"] = len(expected)
        report["deployment_marker"] = deployment_marker
        errors.extend(member_errors)
        for name, entry in expected.items():
            path = SITE / name
            present = path.is_file() and not path.is_symlink()
            actual_hash = digest(path) if present else None
            actual_size = path.stat().st_size if present else None
            equal = present and actual_hash == entry["sha256"] and actual_size == entry["bytes"]
            report["file_checks"].append({"path": name, "equal": equal,
                                          "expected_sha256": entry["sha256"], "actual_sha256": actual_hash,
                                          "expected_bytes": entry["bytes"], "actual_bytes": actual_size})
            if not equal:
                errors.append(f"Original website member changed or missing: {name}")
        for name, expected_hash in PROTECTED_JSON.items():
            actual_hash = digest(SITE / name)
            equal = actual_hash == expected_hash
            report["protected_json_checks"].append({"path": name, "equal": equal,
                                                    "expected_sha256": expected_hash, "actual_sha256": actual_hash})
            if not equal:
                errors.append(f"Protected source data changed: {name}")

        public = json.loads((SITE / "data/public-sources.json").read_text(encoding="utf-8"))
        achievements = json.loads((SITE / "data/achievement-lines.json").read_text(encoding="utf-8"))
        sources = [item["id"] for item in public["sources"]]
        source_ids = set(sources)
        if len(sources) != 51 or len(source_ids) != 51 or any(not value for value in sources):
            errors.append("The 51 public source IDs must remain nonempty and unique")
        lines = [item["id"] for item in achievements["lines"]]
        expected_lines = {f"A{index:02d}" for index in range(1, 10)}
        if len(lines) != 9 or set(lines) != expected_lines:
            errors.append("Achievement lines must retain the nine unique IDs A01 through A09")
        report["public_source_ids"] = sources
        report["public_source_count"] = len(sources)
        report["achievement_line_ids"] = lines

        pages = {}
        for name in sorted(expected):
            if name.endswith(".html") and (SITE / name).is_file():
                page = Page(name)
                page.feed((SITE / name).read_text(encoding="utf-8"))
                page.close()
                pages[name] = page
                duplicates = sorted(value for value, count in Counter(page.ids).items() if count > 1)
                if duplicates:
                    errors.append(f"Duplicate HTML anchor IDs in {name}: {duplicates}")
        report["html_count"] = len(pages)
        if len(pages) != 15:
            errors.append("Exactly 15 HTML pages must be preserved")
        home = pages["index.html"]
        absent_source_anchors = sorted(source for source in source_ids
                                       if f"source-{source.lower()}" not in home.ids)
        if absent_source_anchors:
            errors.append(f"Public source anchors missing from homepage: {absent_source_anchors}")

        pftb = pages["pftb/index.html"]
        data_scripts = [script for script in pftb.scripts
                        if script["attributes"].get("id") == "site-data"]
        if len(data_scripts) != 1:
            raise ValueError("PFtB must retain exactly one embedded site-data record")
        pftb_data = json.loads(data_scripts[0]["text"])
        chapters = {item["id"] for item in pftb_data["chapters"]}
        contexts = {item["id"] for item in pftb_data["reception_contexts"]}
        views = pftb.data.get("data-view", set())
        selected_contexts = pftb.data.get("data-ctx92", set())
        if (chapters != pftb.data.get("data-chapter", set())
                or chapters != pftb.data.get("data-chapter-panel", set())):
            errors.append("PFtB chapter identities differ between embedded data, controls and panels")
        if (not selected_contexts or not selected_contexts <= contexts
                or not selected_contexts <= pftb.data.get("data-ctx-card", set())):
            errors.append("PFtB reception-state controls do not identify valid contexts and cards")
        if views != {"all", "observation", "interpretation", "conditions", "boundary", "reception"}:
            errors.append("PFtB state views changed")
        pftb_source = (SITE / "pftb/index.html").read_text(encoding="utf-8")
        if not all(token in pftb_source for token in ("'#s/'", "function parseHash()", "hashchange", "popstate")):
            errors.append("PFtB #s state serialization and history handlers are missing")
        report["pftb_state_contract"] = {
            "chapters": sorted(chapters), "views": sorted(views),
            "reception_contexts": sorted(selected_contexts),
            "canonical_states": [f"#s/{chapter}/{view}/{context}" for chapter in sorted(chapters)
                                  for view in sorted(views) for context in sorted(selected_contexts)],
            "validation": "static identities and source handlers; browser state execution requires separate validation"}

        def check_link(source: str, value: str, attribute: str, line=None):
            item = {"source": source, "value": value, "attribute": attribute, "line": line}
            report["link_checks"].append(item)
            parsed = urlsplit(value)
            if parsed.scheme or parsed.netloc:
                item["status"] = "external_or_nonfile_scheme_not_fetched"
                return
            path = unquote(parsed.path)
            if path.startswith(("/", "\\")) or "\\" in path:
                item.update(status="failed", reason="absolute_or_backslash_local_path")
                errors.append(f"Subpath-unsafe local link in {source}: {value}")
                return
            target = posixpath.normpath(posixpath.join(posixpath.dirname(source), path)) if path else source
            if target == ".." or target.startswith("../"):
                item.update(status="failed", reason="escapes_site")
                errors.append(f"Link escapes the published site in {source}: {value}")
                return
            if path.endswith("/") or (SITE / target).is_dir():
                target = posixpath.join(target, "index.html")
            item["target"] = target
            if target not in actual or Path(target).suffix not in {".html", ".json"}:
                item.update(status="failed", reason="missing_or_unpublished_target")
                errors.append(f"Missing published target in {source}: {value} -> {target}")
                return
            fragment = unquote(parsed.fragment)
            if fragment.startswith("s/"):
                parts = fragment.split("/")
                valid = (target == "pftb/index.html" and len(parts) in {3, 4}
                         and parts[1] in chapters and parts[2] in views
                         and (len(parts) == 3 or parts[3] in selected_contexts))
                if not valid:
                    item.update(status="failed", reason="invalid_pftb_state_identity")
                    errors.append(f"Invalid PFtB state link in {source}: {value}")
                    return
                item["status"] = "valid_pftb_dynamic_state"
            elif fragment and (target not in pages or fragment not in pages[target].ids):
                item.update(status="failed", reason="missing_anchor")
                errors.append(f"Missing anchor in {source}: {value} -> {target}#{fragment}")
            else:
                item["status"] = "valid_static_local_link"

        for name, page in pages.items():
            for link in page.links:
                check_link(name, link["value"], link["attribute"], link["line"])
        # JSON routes are site-root-relative contracts, not URLs from /data/.
        def check_references(value, location="achievement-lines"):
            if isinstance(value, dict):
                for key, child in value.items():
                    if key in {"sources", "refs"} and isinstance(child, list):
                        unknown = sorted(set(child) - source_ids)
                        if unknown:
                            errors.append(f"Unknown public source IDs at {location}.{key}: {unknown}")
                    if key == "routes" and isinstance(child, list):
                        for route in child:
                            route_url = route["path"] + ("#" + route["anchor"] if route.get("anchor") else "")
                            check_link("index.html", route_url, f"JSON:{location}.routes")
                    check_references(child, f"{location}.{key}")
            elif isinstance(value, list):
                for index, child in enumerate(value):
                    check_references(child, f"{location}[{index}]")
        check_references(achievements)
        for state in report["pftb_state_contract"]["canonical_states"]:
            check_link("pftb/index.html", state, "dynamic_state_contract")

        node = shutil.which("node")
        report["node_executable"] = node
        if node:
            version = subprocess.run([node, "--version"], capture_output=True, text=True, check=False)
            report["node_version"] = version.stdout.strip()
        else:
            message = "Node is unavailable; inline JavaScript syntax was not checked"
            (errors if require_node else report["warnings"]).append(message)
        with tempfile.TemporaryDirectory(prefix="chen-site-js-") as temporary:
            for name, page in pages.items():
                for index, script in enumerate(page.scripts):
                    attributes = script["attributes"]
                    kind = attributes.get("type", "").lower()
                    if kind in {"application/json", "application/ld+json"}:
                        json.loads(script["text"])
                        continue
                    if attributes.get("src") or kind not in {"", "text/javascript", "application/javascript", "module"}:
                        continue
                    record = {"page": name, "script_index": index, "line": script["line"],
                              "sha256": hashlib.sha256(script["text"].encode("utf-8")).hexdigest()}
                    if node:
                        extracted = Path(temporary) / f"script-{len(report['javascript_checks'])}.{'mjs' if kind == 'module' else 'js'}"
                        extracted.write_text(script["text"], encoding="utf-8", newline="\n")
                        process = subprocess.run([node, "--check", str(extracted)], capture_output=True,
                                                 text=True, encoding="utf-8", errors="replace", check=False)
                        record.update(status="passed" if process.returncode == 0 else "failed",
                                      exit_code=process.returncode, stdout=process.stdout, stderr=process.stderr)
                        if process.returncode:
                            errors.append(f"Inline JavaScript syntax failure in {name} at line {script['line']}")
                    else:
                        record["status"] = "not_run_node_unavailable"
                    report["javascript_checks"].append(record)
        report["member_count"] = len(actual)
        report["status"] = "passed" if not errors else "failed"
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append(str(exc))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="New JSON evidence file")
    parser.add_argument("--require-node", action="store_true", help="Fail if Node syntax checking is unavailable")
    args = parser.parse_args()
    if args.output and args.output.exists():
        parser.error("--output must be a new evidence file")
    report = inspect_site(require_node=args.require_node)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                               encoding="utf-8", newline="\n")
    print(json.dumps({"status": report["status"], "member_count": report.get("member_count"),
                      "html_count": report.get("html_count"), "public_source_count": report.get("public_source_count"),
                      "achievement_line_ids": report.get("achievement_line_ids"),
                      "link_checks": len(report["link_checks"]),
                      "javascript_checks": len(report["javascript_checks"]),
                      "output": str(args.output) if args.output else None,
                      "errors": report["errors"], "warnings": report["warnings"]}, ensure_ascii=False))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
