"""Publish the story navigation edits while replaying the existing website checks."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory

import stories_rebalance_publication as prior


MANIFEST = 'provenance/platform-presentation.v49.json'
MANIFEST_SHA256 = '259c3c34be56b532d74741b9f961cb3fad251cd183c4f011b8f0c7de84f9bf62'
PRESENTATION_ID = 'PLATFORM-STORY-NAVIGATION-20261119-v49'
PREDECESSOR = '6e4574238d1a433a8d090970147c64f83e68cc1b'

# v48 already records every v47 file and the exact bytes of its five revisions.
# Its new module and manifest complete the inventory for the v48 tree.
PREVIOUS_FILES = {
    **prior.PREDECESSOR_FILES, **prior.REVIEWED_FILES,
    prior.MANIFEST: ('70d34f9a83eabdfac4e990bdaa86cae51d28999996ee3988529ad96c788aa503', 177341),
    'scripts/stories_rebalance_publication.py': (
        'd34007008f2640d5e545cf22f63e101b1f9cd7ae76ad242af9db22ef1461d748', 193597),
}
_projections = {}
_entry_cache = {}


def _manifest(root):
    data = prior._file(root, MANIFEST).read_bytes()
    if prior._sha(data) != MANIFEST_SHA256:
        raise ValueError('Story navigation manifest differs from the reviewed changes')
    return json.loads(data)


def projection_root(root: Path) -> Path:
    """Reconstruct and verify the entire preceding tree, including on cache hits."""
    root = root.resolve()
    data = _manifest(root)
    edited = {row['path']: row for row in data['reversible_text_files']}
    actual = {p.relative_to(root/'site').as_posix() for p in (root/'site').rglob('*')
              if p.is_file() or p.is_symlink()}
    if actual != {name[5:] for name in PREVIOUS_FILES if name.startswith('site/')}:
        raise ValueError('Story navigation changed the website member set')
    cached = _projections.get(root)
    temp = cached or TemporaryDirectory(prefix='sn49-', dir=root.parent)
    target = Path(temp.name)
    for name, expected in PREVIOUS_FILES.items():
        value = prior._file(root, name).read_bytes()
        if name in edited:
            value = prior._reconstruct(value, edited[name], data['reverse_text_patch_pool'])
        if prior._identity(value) != expected:
            raise ValueError('Story navigation predecessor mismatch: '+name)
        if cached:
            if prior._file(target, name).read_bytes() != value:
                raise ValueError('Cached story navigation predecessor changed: '+name)
        else:
            destination = target/name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(value)
    _projections[root] = temp
    return target


def historical_root(root: Path) -> Path:
    predecessor = projection_root(root) if (root/MANIFEST).is_file() else root
    return prior.historical_root(predecessor)


def _entries(predecessor, baseline, callback, arguments):
    if baseline != json.loads(prior._file(predecessor, 'provenance/website-baseline.json').read_bytes()):
        raise ValueError('Original website baseline differs')
    key = predecessor, callback, json.dumps(arguments, sort_keys=True)
    if key not in _entry_cache:
        _entry_cache[key] = callback(predecessor, deepcopy(baseline), **deepcopy(arguments))
    return deepcopy(_entry_cache[key])


def _updated(entries, data):
    updated = deepcopy(entries)
    for row in data['reversible_text_files']:
        name = row['path']
        if name.startswith('site/'):
            route = name[5:]
            old = entries[route]
            if (old['sha256'], old['bytes']) != (row['old_sha256'], row['old_bytes']):
                raise ValueError('Story link update differs from the preceding website entry: '+route)
            updated[route] = {**old, 'sha256': row['new_sha256'], 'bytes': row['new_bytes'],
                              'presentation_id': PRESENTATION_ID}
    return updated


def apply(root: Path, baseline: dict, callback, *, verify_current=True,
          revision_chain=None, include_presentation=True):
    previous_root = projection_root(root)
    entries, report = _entries(previous_root, baseline, callback, {
        'verify_current': verify_current, 'revision_chain': revision_chain,
        'include_presentation': include_presentation})
    if not include_presentation:
        return entries, report
    data = _manifest(root)
    updated = _updated(entries, data)
    for route, entry in updated.items():
        if prior._identity(prior._file(root, 'site/'+route).read_bytes()) != (entry['sha256'], entry['bytes']):
            raise ValueError('Story navigation page or asset identity changed: '+route)
    summary = {key: data[key] for key in ('presentation_id', 'publication_kind',
        'previous_presentation_commit', 'scientific_review_status', 'release_eligible',
        'scientific_data_unchanged', 'historical_achievement_independent_of_AI_review',
        'M0_resumed', 'Nemotron_training_resumed')}
    summary.update(path=MANIFEST, sha256=MANIFEST_SHA256, changed_paths=data['changed_html_paths'],
                   added_paths=[])
    history = report['presentation']['presentation_chain']
    return updated, {**report, 'changed_paths': sorted(set(report['changed_paths']) | set(data['changed_html_paths'])),
                     'presentation': {**summary, 'presentation_chain': [*history, summary]}}


def publication_members(root: Path, entries: dict, prior_entries, prior_members):
    previous_root = projection_root(root)
    baseline = json.loads(prior._file(previous_root, 'provenance/website-baseline.json').read_bytes())
    previous, _ = _entries(previous_root, baseline, prior_entries, {
        'verify_current': True, 'revision_chain': None, 'include_presentation': True})
    if entries != _updated(previous, _manifest(root)):
        raise ValueError('Story navigation publication entries differ in identity, role or membership')
    members = prior_members(previous_root, previous)
    if ({row['path'] for row in members} != set(prior.PUBLICATION_PATHS)
            or len(members) != len(prior.PUBLICATION_PATHS)
            or any(row != previous[row['path']] for row in members)):
        raise ValueError('Story navigation must preserve the complete previous publication allowlist')
    return [deepcopy(entries[row['path']]) for row in members]
