"""Explicit A01 progress-page exceptions to the preserved YouMind baseline.

This never grants scientific release or modifies the original baseline.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import re

BASELINE_SHA256 = '5e3e70988d76ac1d777ff85ee7c1945341e2141767fc77560c6cea39eabab329'
ARCHIVE_SHA256 = 'fa9740d7a244ab4d52885600a312487869d780a82517aa0d0a401215696c4d3e'
REVISION_PATH = 'provenance/a01-site-revision.v1.json'
PROGRESS_PATH = 'research/a01/public-progress.v1.json'
TOPIC_PATH = 'topics/early-fluoroketones/index.html'
ALLOWED_CHANGES = {TOPIC_PATH, 'index.html', 'achievements/index.html'}
SHA = re.compile(r'[0-9a-f]{64}')
COMMIT = re.compile(r'[0-9a-f]{40}')


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text('utf-8-sig'))


def project_file(root: Path, name: str) -> Path:
    relative = PurePosixPath(name)
    if (not name or relative.is_absolute() or '..' in relative.parts or '\\' in name
            or relative.as_posix() != name):
        raise ValueError('Unsafe project-relative evidence path: '+str(name))
    candidate = root/name
    if candidate.is_symlink() or not candidate.is_file() or not candidate.resolve().is_relative_to(root.resolve()):
        raise ValueError('Missing or nonregular evidence: '+name)
    return candidate


def effective_website_entries(root: Path, baseline: dict) -> tuple[dict, dict]:
    baseline_path = root/'provenance/website-baseline.json'
    if digest(baseline_path) != BASELINE_SHA256:
        raise ValueError('Original YouMind baseline bytes changed; a revision must not refresh it')
    if baseline.get('archive_sha256') != ARCHIVE_SHA256:
        raise ValueError('Unexpected original export archive identity')
    if digest(project_file(root, 'upstream/chen-qingyun-a2-citations-candidate.zip')) != ARCHIVE_SHA256:
        raise ValueError('Original YouMind export ZIP bytes changed')
    entries = {entry['path']: dict(entry) for entry in baseline['files']}
    revision_path = root/REVISION_PATH
    if not revision_path.exists():
        return entries, {'present': False, 'changed_paths': [], 'original_baseline_preserved': True}
    revision = read_json(project_file(root, REVISION_PATH))
    if revision.get('schema_version') != '1.0' or revision.get('revision_id') != 'A01-PROGRESS-20261113-v1':
        raise ValueError('Unsupported A01 page revision contract')
    if (revision.get('publication_kind') != 'a01_research_progress'
            or revision.get('scientific_review_status') != 'review_required'
            or revision.get('release_eligible') is not False):
        raise ValueError('A01 page revision is public progress only, pending scientific review')
    if revision.get('original_baseline_sha256') != BASELINE_SHA256 or revision.get('original_archive_sha256') != ARCHIVE_SHA256:
        raise ValueError('Revision does not bind the preserved original source identities')
    commit = revision.get('evidence_commit_s1')
    if not isinstance(commit, str) or not COMMIT.fullmatch(commit):
        raise ValueError('A01 page revision requires a fixed S1 evidence commit')
    public = revision.get('public_progress', {})
    if public.get('path') != PROGRESS_PATH or not isinstance(public.get('sha256'), str) or not SHA.fullmatch(public['sha256']):
        raise ValueError('A01 revision must bind its separate public progress data')
    if digest(project_file(root, PROGRESS_PATH)) != public['sha256']:
        raise ValueError('A01 progress bytes differ from page revision binding')
    progress = read_json(root/PROGRESS_PATH)
    if progress.get('evidence_archive_commit') != commit:
        raise ValueError('A01 page and progress record refer to different evidence commits')
    changes = revision.get('changes')
    if not isinstance(changes, list) or not 1 <= len(changes) <= len(ALLOWED_CHANGES):
        raise ValueError('Revision must explicitly enumerate one to three authorized HTML changes')
    seen = set()
    for item in changes:
        name = item.get('path')
        if name not in ALLOWED_CHANGES or name in seen:
            raise ValueError('Unauthorized or duplicate revised website path: '+str(name))
        seen.add(name)
        old = entries.get(name)
        if old is None or item.get('old_sha256') != old['sha256'] or item.get('old_bytes') != old['bytes']:
            raise ValueError('Revision old bytes must match original baseline: '+name)
        value, size = item.get('new_sha256'), item.get('new_bytes')
        if (not isinstance(value, str) or not SHA.fullmatch(value) or value == old['sha256']
                or not isinstance(size, int) or isinstance(size, bool) or size <= 0
                or not isinstance(item.get('reason'), str) or not item['reason'].strip()
                or item.get('source_evidence_commit') != commit):
            raise ValueError('Incomplete A01 page revision record: '+name)
        current = project_file(root, 'site/'+name)
        if digest(current) != value or current.stat().st_size != size:
            raise ValueError('Revised website bytes differ from explicitly authorized revision: '+name)
        entries[name] = {**old, 'sha256': value, 'bytes': size,
                         'original_sha256': old['sha256'], 'revision_id': revision['revision_id']}
    if TOPIC_PATH not in seen:
        raise ValueError('An A01 progress revision must update its existing topic page')
    return entries, {'present': True, 'path': REVISION_PATH, 'sha256': digest(revision_path),
        'revision_id': revision['revision_id'], 'changed_paths': sorted(seen),
        'original_baseline_preserved': True, 'original_baseline_sha256': BASELINE_SHA256,
        'public_progress_sha256': public['sha256'], 'evidence_commit_s1': commit,
        'publication_kind': 'a01_research_progress', 'scientific_review_status': 'review_required',
        'release_eligible': False}
