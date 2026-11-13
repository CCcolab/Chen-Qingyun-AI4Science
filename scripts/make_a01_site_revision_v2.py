"""Bind the new A01 progress page to its immutable v1 predecessor and S3.

No original baseline, historical public data or historical revision is rewritten.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

from a01_publication_contract import (ALLOWED_CHANGES, ARCHIVE_SHA256,
    BASELINE_SHA256, COMMIT, CURRENT_PATH, PROGRESS_V2_PATH, REVISION_PATH,
    REVISION_V1_SHA256, REVISION_V2_PATH, TOPIC_PATH, digest,
    effective_website_entries, project_file, read_json)

ROOT = Path(__file__).resolve().parents[1]


def save_new(path, value):
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence-commit', required=True, help='Complete S3 evidence commit SHA')
    args = parser.parse_args()
    if not COMMIT.fullmatch(args.evidence_commit):
        parser.error('--evidence-commit requires a full lowercase 40-character SHA')
    if (ROOT/REVISION_V2_PATH).exists() or (ROOT/CURRENT_PATH).exists():
        parser.error('An existing current edition is immutable; a later task must create another explicit edition')
    baseline = read_json(project_file(ROOT, 'provenance/website-baseline.json'))
    previous, _ = effective_website_entries(ROOT, baseline, verify_current=False,
                                           revision_chain=[REVISION_PATH])
    progress_file = project_file(ROOT, PROGRESS_V2_PATH)
    progress = read_json(progress_file)
    if (progress.get('schema_version') != '2.0'
            or progress.get('evidence_archive_commit') != args.evidence_commit):
        raise ValueError('Public progress v2 must already identify its fixed S3 evidence commit')
    changes = []
    for name, old in previous.items():
        current = project_file(ROOT, 'site/'+name)
        actual, size = digest(current), current.stat().st_size
        if actual == old['sha256'] and size == old['bytes']:
            continue
        if name not in ALLOWED_CHANGES:
            raise ValueError('Change outside the three authorized A01 HTML paths: '+name)
        # This edition needs only the existing topic progress block.
        if name != TOPIC_PATH:
            raise ValueError('This five-point diagnosis edition authorizes a topic-only update: '+name)
        changes.append({'path': name, 'old_sha256': old['sha256'], 'old_bytes': old['bytes'],
            'new_sha256': actual, 'new_bytes': size,
            'source_evidence_commit': args.evidence_commit,
            'reason': 'Actual same-M0 CF3 center-gradient and four-displacement SCF-precision diagnosis; complete curvature, barriers and mechanism remain unqualified'})
    if {item['path'] for item in changes} != {TOPIC_PATH}:
        raise ValueError('The existing A01 topic must have exactly one explicit new page revision')
    revision = {'schema_version': '2.0', 'revision_id': 'A01-PROGRESS-20261113-v2',
        'created_at_utc': datetime.now(timezone.utc).isoformat(),
        'publication_kind': 'a01_research_progress',
        'scientific_review_status': 'review_required', 'release_eligible': False,
        'authorization': 'User task dated 2026-11-13: same-M0 CF3 center gradient and C6-y/C10-y precision diagnosis, then archive and publish actual results',
        'original_baseline_sha256': BASELINE_SHA256,
        'original_archive_sha256': ARCHIVE_SHA256,
        'previous_revision': {'path': REVISION_PATH, 'sha256': REVISION_V1_SHA256},
        'evidence_commit_s3': args.evidence_commit,
        'public_progress': {'path': PROGRESS_V2_PATH, 'sha256': digest(progress_file)},
        'changes': changes,
        'protected': 'Original YouMind baseline/ZIP, immutable v1 progress and revision, PFtB, two original JSON files, 51 source identities, and every effective page outside the explicitly listed topic',
        'publish_allowlist': 'Unchanged 15 original HTML routes, two original JSON files and empty .nojekyll; research JSON remains repository-only',
        'boundary': 'Public research progress is not scientific approval, complete-curvature qualification, a DFT barrier or mechanism confirmation.'}
    registry = {'schema_version': '1.0', 'registry_kind': 'a01_public_progress_current',
        'scientific_review_status': 'review_required', 'release_eligible': False,
        'public_progress': PROGRESS_V2_PATH, 'current_revision': REVISION_V2_PATH,
        'revision_chain': [REVISION_PATH, REVISION_V2_PATH],
        'history_policy': 'Original v1 public data and revision retain their exact bytes; apply each historical declaration before checking only the final current HTML'}
    save_new(ROOT/REVISION_V2_PATH, revision)
    save_new(ROOT/CURRENT_PATH, registry)
    _, report = effective_website_entries(ROOT, baseline)
    print(json.dumps({'status': 'passed', **report}, ensure_ascii=False))


if __name__ == '__main__':
    main()
