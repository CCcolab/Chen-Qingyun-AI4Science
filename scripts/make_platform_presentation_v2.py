"""Bind the historical biography, nine-line inventory and sourced stories.

This bounded successor keeps v1 and scientific records immutable. Its three
historical document snapshots must match the already fixed v1 SHA256 promises.
The root operator exports those exact bytes from the preceding 4a42dff commit;
checks remain portable to shallow CI without Git, network or quantum entries.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

from a01_publication_contract import (ALLOWED_CHANGES, ARCHIVE_SHA256,
    BASELINE_SHA256, CURRENT_PATH, CURRENT_SHA256, PRESENTATION_PATH,
    PRESENTATION_V1_SHA256, PRESENTATION_V2_ID, PRESENTATION_V2_PATH,
    PRESENTATION_V2_PREVIOUS_COMMIT, PROGRESS_V2_PATH, PROGRESS_V2_SHA256,
    REVISION_PATH, REVISION_V2_PATH, REVISION_V2_SHA256, TOPIC_PATH,
    apply_presentation_v1, digest, effective_website_entries,
    heritage_content_binding, presentation_protected_bindings,
    presentation_v1_snapshot_bindings, presentation_v2_document_bindings,
    project_file, read_json)

ROOT = Path(__file__).resolve().parents[1]


def prepare_presentation(root: Path) -> dict:
    """Check saved files and return a declaration without writing anything."""
    if (root/PRESENTATION_V2_PATH).exists():
        raise FileExistsError('An existing content presentation v2 is immutable; refuse overwrite')
    bindings = [('scientific_revision', REVISION_V2_PATH, REVISION_V2_SHA256),
                ('public_progress', PROGRESS_V2_PATH, PROGRESS_V2_SHA256),
                ('current_registry', CURRENT_PATH, CURRENT_SHA256)]
    for _, name, expected in bindings:
        if digest(project_file(root, name)) != expected:
            raise ValueError('Frozen scientific predecessor changed: '+name)
    snapshots = presentation_v1_snapshot_bindings(root)
    baseline = read_json(project_file(root, 'provenance/website-baseline.json'))
    scientific_entries, report = effective_website_entries(root, baseline,
        verify_current=False, revision_chain=[REVISION_PATH, REVISION_V2_PATH],
        include_presentation=False)
    if report.get('public_progress_path') != PROGRESS_V2_PATH:
        raise ValueError('The scientific predecessor must remain the same A01 v2 edition')
    previous, v1 = apply_presentation_v1(root, scientific_entries,
        chain=[REVISION_PATH, REVISION_V2_PATH], use_document_snapshots=True)
    if v1 is None or v1['sha256'] != PRESENTATION_V1_SHA256:
        raise ValueError('Historical content requires the exact frozen presentation v1 predecessor')
    from check_site import check_member_set
    _, _, member_errors = check_member_set(root/'site', set(previous))
    if member_errors:
        raise ValueError('Heritage content changes the original site member set: '+'; '.join(member_errors))
    protected = presentation_protected_bindings(root, previous)
    documents = presentation_v2_document_bindings(root)
    content = heritage_content_binding(root)
    from check_a01_progress import inspect_progress
    scientific = inspect_progress(root, require_page=False, progress_path=PROGRESS_V2_PATH)
    if scientific['status'] != 'passed':
        raise ValueError('Existing A01 scientific evidence check failed: '+'; '.join(scientific['errors']))
    from render_a01_progress import BEGIN, END, render_block
    topic = project_file(root, 'site/'+TOPIC_PATH).read_text('utf-8')
    if topic.count(BEGIN) != 1 or topic.count(END) != 1:
        raise ValueError('Preserved A01 technical content requires one complete progress block')
    if topic[topic.index(BEGIN):topic.index(END)+len(END)] != render_block(read_json(root/PROGRESS_V2_PATH), PROGRESS_V2_SHA256):
        raise ValueError('Historical content must retain the complete A01 technical block bytes')
    reasons = {
        'index.html': 'Add separately sourced historical biography and academic-transmission stories, with explicit evidence gaps and an independent supporting AI pilot',
        'achievements/index.html': 'Add a sourced inventory of the nine stable historical lines without changing original source-register records or scientific qualifications',
        TOPIC_PATH: 'Add source-bound historical context outside the unchanged A01 scientific progress block',
    }
    changes = []
    for name, old in previous.items():
        path = project_file(root, 'site/'+name)
        value, size = digest(path), path.stat().st_size
        if value == old['sha256'] and size == old['bytes']:
            continue
        if name not in ALLOWED_CHANGES:
            raise ValueError('Heritage content change outside the three existing authorized HTML paths: '+name)
        changes.append({'path': name, 'old_sha256': old['sha256'], 'old_bytes': old['bytes'],
                        'new_sha256': value, 'new_bytes': size, 'reason': reasons[name]})
    if not changes:
        raise ValueError('No completed historical-content HTML changes to declare')
    return {'schema_version': '2.0', 'presentation_id': PRESENTATION_V2_ID,
        'created_at_utc': datetime.now(timezone.utc).isoformat(),
        'publication_kind': 'platform_historical_content',
        'scientific_review_status': 'review_required', 'release_eligible': False,
        'scientific_data_unchanged': True,
        'authorization': 'User historical-heritage construction task dated 2026-11-14: add source-bound biography, the nine-line inventory and sourced stories; perform no scientific computation',
        'original_baseline_sha256': BASELINE_SHA256,
        'original_archive_sha256': ARCHIVE_SHA256,
        'previous_presentation_commit': PRESENTATION_V2_PREVIOUS_COMMIT,
        'previous_presentation': {'path': PRESENTATION_PATH, 'sha256': PRESENTATION_V1_SHA256},
        **{field: {'path': name, 'sha256': expected} for field, name, expected in bindings},
        'historical_editorial_documents': snapshots,
        'historical_snapshot_origin': 'Exact bytes exported by the root operator from the fixed preceding commit; verified here against the immutable v1 SHA256/byte promises, never refreshed from current editable documents',
        'editorial_documents': documents, 'historical_content': content,
        'protected': protected, 'changes': changes,
        'ai_research': {'role': 'separate_supporting_pilot', 'new_quantum_calls': 0,
                        'new_model_API_calls': 0, 'scientific_data_unchanged': True},
        'boundary': 'Biography, the nine-line inventory and stories are historical materials with separately reviewed sources and evidence gaps. They do not establish AI reproduction, experimental verification, scientific priority or new computational results.',
        'publish_allowlist': 'The original 15 HTML routes and two original JSON files only, plus the empty .nojekyll marker. Supplemental HERITAGE-S sources remain in repository content and existing static HTML, not the original 51-source JSON or a new Pages JSON route.'}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-only', action='store_true', help='Check completed inputs without writing the v2 declaration')
    args = parser.parse_args()
    value = prepare_presentation(ROOT)
    if args.check_only:
        print(json.dumps({'status': 'passed', 'declaration_created': False,
            'presentation_id': PRESENTATION_V2_ID, 'changed_paths': [item['path'] for item in value['changes']],
            'supplemental_source_ids': value['historical_content']['supplemental_source_ids'],
            'scientific_progress_path': PROGRESS_V2_PATH, 'new_quantum_calls': 0}, ensure_ascii=False))
        return 0
    target = ROOT/PRESENTATION_V2_PATH
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
