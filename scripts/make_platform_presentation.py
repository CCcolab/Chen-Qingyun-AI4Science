"""Declare one editorial platform overlay after the immutable A01 v2 edition.

Run only after the three HTML pages and three current platform documents are
complete. No scientific record, source baseline, archive or old revision is
rewritten. This script performs saved-file checks only; it has no network,
model API, quantum backend or Git entry.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

from a01_publication_contract import (ALLOWED_CHANGES, ARCHIVE_SHA256,
    BASELINE_SHA256, CURRENT_PATH, CURRENT_SHA256, PRESENTATION_ID,
    PRESENTATION_PATH, PRESENTATION_PREVIOUS_COMMIT, PROGRESS_V2_PATH,
    PROGRESS_V2_SHA256, REVISION_PATH, REVISION_V2_PATH, REVISION_V2_SHA256,
    TOPIC_PATH, digest, effective_website_entries, presentation_document_bindings,
    presentation_protected_bindings, project_file, read_json)

ROOT = Path(__file__).resolve().parents[1]


def prepare_presentation(root: Path) -> dict:
    """Return a checked declaration; do not create or alter any file."""
    if (root/PRESENTATION_PATH).exists():
        raise FileExistsError('An existing presentation declaration is immutable; refuse overwrite')
    bindings = [('scientific_revision', REVISION_V2_PATH, REVISION_V2_SHA256),
                ('public_progress', PROGRESS_V2_PATH, PROGRESS_V2_SHA256),
                ('current_registry', CURRENT_PATH, CURRENT_SHA256)]
    for _, name, expected in bindings:
        if digest(project_file(root, name)) != expected:
            raise ValueError('Frozen scientific predecessor changed: '+name)
    baseline = read_json(project_file(root, 'provenance/website-baseline.json'))
    previous, report = effective_website_entries(root, baseline, verify_current=False,
        revision_chain=[REVISION_PATH, REVISION_V2_PATH], include_presentation=False)
    if report.get('public_progress_path') != PROGRESS_V2_PATH:
        raise ValueError('The scientific predecessor must remain the same A01 v2 edition')
    from check_site import check_member_set
    _, _, member_errors = check_member_set(root/'site', set(previous))
    if member_errors:
        raise ValueError('Presentation changes the original site member set: '+'; '.join(member_errors))
    protected = presentation_protected_bindings(root, previous)
    documents = presentation_document_bindings(root)
    from check_a01_progress import inspect_progress
    scientific = inspect_progress(root, require_page=False, progress_path=PROGRESS_V2_PATH)
    if scientific['status'] != 'passed':
        raise ValueError('Existing A01 scientific data check failed: '+'; '.join(scientific['errors']))
    from render_a01_progress import BEGIN, END, render_block
    page = project_file(root, 'site/'+TOPIC_PATH).read_text('utf-8')
    if page.count(BEGIN) != 1 or page.count(END) != 1:
        raise ValueError('The preserved scientific progress block requires exactly one marker pair')
    visible = page[page.index(BEGIN):page.index(END)+len(END)]
    if visible != render_block(read_json(root/PROGRESS_V2_PATH), PROGRESS_V2_SHA256):
        raise ValueError('Editorial changes must retain the complete scientific progress block bytes')
    reasons = {
        'index.html': 'Clarify the commemorative platform, documented contributions and transmission; present AI research as a bounded supporting pilot',
        'achievements/index.html': 'Retain stable historical achievement identities while clarifying contributions and academic transmission before the AI pilot',
        TOPIC_PATH: 'Clarify the historical perfluoroketone achievement and supporting AI pilot outside the unchanged evidence-bound scientific progress block',
    }
    changes = []
    for name, old in previous.items():
        path = project_file(root, 'site/'+name)
        value, size = digest(path), path.stat().st_size
        if value == old['sha256'] and size == old['bytes']:
            continue
        if name not in ALLOWED_CHANGES:
            raise ValueError('Editorial change outside the three authorized HTML paths: '+name)
        changes.append({'path': name, 'old_sha256': old['sha256'], 'old_bytes': old['bytes'],
                        'new_sha256': value, 'new_bytes': size, 'reason': reasons[name]})
    if {item['path'] for item in changes} != ALLOWED_CHANGES:
        raise ValueError('Complete all three authorized platform presentations before declaring the overlay')
    return {'schema_version': '1.0', 'presentation_id': PRESENTATION_ID,
        'created_at_utc': datetime.now(timezone.utc).isoformat(),
        'publication_kind': 'platform_editorial_presentation',
        'scientific_review_status': 'review_required', 'release_eligible': False,
        'scientific_data_unchanged': True,
        'authorization': 'User platform-positioning correction dated 2026-11-14: commemorate Chen Qingyun, present documented scientific contributions and academic transmission, and keep the AI pilot subordinate to those purposes',
        'original_baseline_sha256': BASELINE_SHA256,
        'original_archive_sha256': ARCHIVE_SHA256,
        'previous_presentation_commit': PRESENTATION_PREVIOUS_COMMIT,
        **{field: {'path': name, 'sha256': expected} for field, name, expected in bindings},
        'editorial_documents': documents, 'protected': protected, 'changes': changes,
        'boundary': 'An editorial overlay only: no new calculation, scientific release, reinterpretation of existing results or promotion of AI evidence; the original scientific v1/v2 records and current registry remain unchanged.',
        'publish_allowlist': 'Exactly the original 15 HTML routes, two original JSON files and the existing empty .nojekyll marker; no research-data route is added.'}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-only', action='store_true', help='Validate completed inputs without creating the presentation declaration')
    args = parser.parse_args()
    value = prepare_presentation(ROOT)
    if args.check_only:
        print(json.dumps({'status': 'passed', 'declaration_created': False,
            'presentation_id': PRESENTATION_ID, 'changed_paths': sorted(ALLOWED_CHANGES),
            'scientific_progress_path': PROGRESS_V2_PATH, 'new_quantum_calls': 0}, ensure_ascii=False))
        return 0
    target = ROOT/PRESENTATION_PATH
    with target.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')
    _, report = effective_website_entries(ROOT, read_json(ROOT/'provenance/website-baseline.json'))
    print(json.dumps({'status': 'passed', 'declaration_created': True,
        'presentation': report['presentation'], 'public_progress_path': report['public_progress_path'],
        'scientific_data_unchanged': True, 'new_quantum_calls': 0}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
