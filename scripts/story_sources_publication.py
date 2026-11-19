"""Verify the revised story sources and replay the preceding publication contract."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory

import story_navigation_publication as navigation
from stories_rebalance_publication import PUBLICATION_PATHS, _file, _identity, _reconstruct, _sha


MANIFEST = 'provenance/platform-presentation.v50.json'
MANIFEST_SHA256 = '1d392c6af7f1ff6d2d226570fc363502559ff934d1ac14133515635a04e53f3f'
PRESENTATION_ID = 'PLATFORM-STORY-SOURCES-20261119-v50'
PREDECESSOR = '8a99ea44f5deb956041e9ff5720d29bfd10c4d94'
STORY = 'people/stories/index.html'
CHANGED_FILES = {'site/'+STORY, 'scripts/a01_publication_contract.py', 'scripts/check_site.py'}
_projections = {}


def _manifest(root):
    raw = _file(root, MANIFEST).read_bytes()
    if _sha(raw) != MANIFEST_SHA256:
        raise ValueError('Story source manifest differs from the reviewed changes')
    data = json.loads(raw)
    if data['changed_html_paths'] != [STORY] or {row['path'] for row in data['reversible_text_files']} != CHANGED_FILES:
        raise ValueError('Story source manifest exceeds the reviewed paths')
    return data


def projection_root(root: Path) -> Path:
    """Restore all v49 files from their reviewed identities, including on cache hits."""
    root = root.resolve()
    data = _manifest(root)
    edited = {row['path']: row for row in data['reversible_text_files']}
    preceding = navigation._manifest(root)
    identities = {**navigation.PREVIOUS_FILES,
                  **{row['path']: (row['new_sha256'], row['new_bytes'])
                     for row in preceding['reversible_text_files']},
                  navigation.MANIFEST: (navigation.MANIFEST_SHA256, 74962),
                  'scripts/story_navigation_publication.py':
                      ('3ba857bf5b4e5fca4ee685595dfa4231e87042bbfea0d378dd886e07337b4010', 6334)}
    site = root/'site'
    members = {p.relative_to(site).as_posix() for p in site.rglob('*') if p.is_file() or p.is_symlink()}
    if members != {name[5:] for name in identities if name.startswith('site/')}:
        raise ValueError('Story source update changed the website member set')
    cache = _projections.get(root)
    temporary = cache or TemporaryDirectory(prefix='ss50-', dir=root.parent)
    target = Path(temporary.name)
    for name, expected in identities.items():
        value = _file(root, name).read_bytes()
        if name in edited:
            value = _reconstruct(value, edited[name], data['reverse_text_patch_pool'])
        if _identity(value) != expected:
            raise ValueError('Story source predecessor mismatch: '+name)
        if cache:
            if _file(target, name).read_bytes() != value:
                raise ValueError('Cached story source predecessor changed: '+name)
        else:
            destination = target/name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(value)
    _projections[root] = temporary
    return target


def historical_root(root: Path) -> Path:
    predecessor = projection_root(root) if (root/MANIFEST).is_file() else root
    return navigation.historical_root(predecessor)


def _updated(entries, data):
    row = next(row for row in data['reversible_text_files'] if row['path'] == 'site/'+STORY)
    old = entries[STORY]
    if (old['sha256'], old['bytes']) != (row['old_sha256'], row['old_bytes']):
        raise ValueError('Story entry differs from the preceding publication')
    return {**entries, STORY: {**old, 'sha256': row['new_sha256'], 'bytes': row['new_bytes'],
                               'presentation_id': PRESENTATION_ID}}


def apply(root, baseline, callback, *, verify_current=True, revision_chain=None, include_presentation=True):
    previous = projection_root(root)
    entries, report = navigation._entries(previous, baseline, callback, {
        'verify_current': verify_current, 'revision_chain': revision_chain,
        'include_presentation': include_presentation})
    if not include_presentation:
        return entries, report
    data = _manifest(root)
    summary = {key: data[key] for key in ('presentation_id', 'publication_kind',
        'previous_presentation_commit', 'scientific_review_status', 'release_eligible',
        'scientific_data_unchanged', 'historical_achievement_independent_of_AI_review',
        'M0_resumed', 'Nemotron_training_resumed')}
    summary.update(path=MANIFEST, sha256=MANIFEST_SHA256, changed_paths=[STORY], added_paths=[])
    history = report['presentation']['presentation_chain']
    return _updated(entries, data), {**report, 'changed_paths': sorted(set(report['changed_paths']) | {STORY}),
                                     'presentation': {**summary, 'presentation_chain': [*history, summary]}}


def publication_members(root, entries, prior_entries, prior_members):
    previous = projection_root(root)
    baseline = json.loads(_file(previous, 'provenance/website-baseline.json').read_bytes())
    old, _ = navigation._entries(previous, baseline, prior_entries, {
        'verify_current': True, 'revision_chain': None, 'include_presentation': True})
    if entries != _updated(old, _manifest(root)):
        raise ValueError('Story source publication entries differ in identity, role or membership')
    members = prior_members(previous, old)
    if (len(members) != len(PUBLICATION_PATHS) or {row['path'] for row in members} != set(PUBLICATION_PATHS)
            or any(row != old[row['path']] for row in members)):
        raise ValueError('Story source update must preserve the preceding publication allowlist')
    return [deepcopy(entries[row['path']]) for row in members]
