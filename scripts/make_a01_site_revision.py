"""Create the one explicit A01 website revision after the S1 archive commit."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re

from a01_publication_contract import (ALLOWED_CHANGES, ARCHIVE_SHA256, BASELINE_SHA256,
    COMMIT, PROGRESS_PATH, REVISION_PATH, TOPIC_PATH, digest, effective_website_entries,
    project_file, read_json)

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence-commit', required=True)
    args = parser.parse_args()
    if not COMMIT.fullmatch(args.evidence_commit):
        parser.error('--evidence-commit requires a full lowercase 40-character SHA')
    output = ROOT/REVISION_PATH
    if output.exists():
        parser.error('An existing page revision is immutable; create a reviewed new edition instead')
    baseline_path = project_file(ROOT, 'provenance/website-baseline.json')
    if digest(baseline_path) != BASELINE_SHA256:
        raise ValueError('Original website baseline bytes changed')
    baseline = read_json(baseline_path)
    progress_path = project_file(ROOT, PROGRESS_PATH)
    progress = read_json(progress_path)
    if progress.get('evidence_archive_commit') != args.evidence_commit:
        raise ValueError('Public data must already point to the selected S1 evidence commit')
    reasons = {
        TOPIC_PATH: 'Authorized A01 historical-source clarification, separate research branches and evidence-bound pending-review progress block',
        'index.html': 'Authorized A01 display-title, topic-entry and homepage research-status clarification; original source payloads and other achievement content retained',
        'achievements/index.html': 'Authorized A01 display-title clarification; stable achievement identity and other lines retained',
    }
    changes = []
    for entry in baseline['files']:
        name = entry['path']; current = project_file(ROOT, 'site/'+name)
        actual, size = digest(current), current.stat().st_size
        if actual == entry['sha256'] and size == entry['bytes']:
            continue
        if name not in ALLOWED_CHANGES:
            raise ValueError('Change outside A01 HTML authorization: '+name)
        changes.append({'path': name, 'old_sha256': entry['sha256'], 'old_bytes': entry['bytes'],
            'new_sha256': actual, 'new_bytes': size, 'source_evidence_commit': args.evidence_commit,
            'reason': reasons[name]})
    if TOPIC_PATH not in {row['path'] for row in changes}:
        raise ValueError('The existing A01 topic page has not changed')
    revision = {'schema_version': '1.0', 'revision_id': 'A01-PROGRESS-20261113-v1',
        'created_at_utc': datetime.now(timezone.utc).isoformat(),
        'publication_kind': 'a01_research_progress', 'scientific_review_status': 'review_required',
        'release_eligible': False,
        'authorization': 'User task dated 2026-11-13: publish the actual single-center SCF stage and A01 progress without scientific-release promotion',
        'original_baseline_sha256': BASELINE_SHA256, 'original_archive_sha256': ARCHIVE_SHA256,
        'evidence_commit_s1': args.evidence_commit,
        'public_progress': {'path': PROGRESS_PATH, 'sha256': digest(progress_path)},
        'changes': changes,
        'protected': 'Original baseline and export archive; PFtB; the two original JSON files and 51 source identities; every baseline member outside these explicit changes',
        'publish_allowlist': 'Unchanged 15 original HTML routes, two original JSON files and empty .nojekyll; A01 progress is static HTML, not a new published JSON route',
        'boundary': 'Public progress is not PF1966 reviewed-result export or scientific approval. No original evidence baseline is refreshed.'}
    with output.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(revision, stream, ensure_ascii=False, indent=2, allow_nan=False); stream.write('\n')
    _, report = effective_website_entries(ROOT, baseline)
    print(json.dumps({'status': 'passed', 'revision': str(output), **report}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
