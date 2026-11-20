"""Verify the bounded page revisions following the story navigation release."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory

import story_navigation_publication as navigation
import home_achievement_links_publication as home
import study_details_publication as studies
import research_line_overviews_publication as overviews
from stories_rebalance_publication import PUBLICATION_PATHS, _file, _identity, _reconstruct, _sha


MANIFEST = 'provenance/platform-presentation.v50.json'
MANIFEST_SHA256 = '1d392c6af7f1ff6d2d226570fc363502559ff934d1ac14133515635a04e53f3f'
PRESENTATION_ID = 'PLATFORM-STORY-SOURCES-20261119-v50'
PREDECESSOR = '8a99ea44f5deb956041e9ff5720d29bfd10c4d94'
STORY = 'people/stories/index.html'
CHANGED_FILES = {'site/'+STORY, 'scripts/a01_publication_contract.py', 'scripts/check_site.py'}
_projections = {}


def _manifest(root, path=MANIFEST, digest=MANIFEST_SHA256, html_paths=(STORY,), files=CHANGED_FILES):
    raw = _file(root, path).read_bytes()
    if _sha(raw) != digest:
        raise ValueError('Page revision manifest differs from the reviewed changes: '+path)
    data = json.loads(raw)
    if data['changed_html_paths'] != list(html_paths) or {row['path'] for row in data['reversible_text_files']} != files:
        raise ValueError('Page revision exceeds the reviewed paths: '+path)
    return data


def _v49_files(root):
    preceding = navigation._manifest(root)
    return {**navigation.PREVIOUS_FILES, **_revised_files(preceding),
            navigation.MANIFEST: (navigation.MANIFEST_SHA256, 74962),
            'scripts/story_navigation_publication.py':
                ('3ba857bf5b4e5fca4ee685595dfa4231e87042bbfea0d378dd886e07337b4010', 6334)}


def _revised_files(data):
    return {row['path']: (row['new_sha256'], row['new_bytes']) for row in data['reversible_text_files']}


def _project(root, data, identities):
    """Restore the complete predecessor tree and verify cached files on every use."""
    root = root.resolve()
    edited = {row['path']: row for row in data['reversible_text_files']}
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


def _previous(root):
    revisions = ((home, home.V50_ADDITIONS), (studies, studies.V51_ADDITIONS),
                 (overviews, overviews.V52_ADDITIONS))
    latest = next((revision for revision, _ in reversed(revisions) if (root/revision.MANIFEST).is_file()), None)
    if latest is None and not (root/MANIFEST).is_file():
        return root, None
    identities = _v49_files(root)
    data = _manifest(root)
    path, digest = MANIFEST, MANIFEST_SHA256
    if latest is not None:
        for revision, additions in revisions:
            identities.update(_revised_files(data))
            identities.update(additions)
            path, digest = revision.MANIFEST, revision.MANIFEST_SHA256
            data = _manifest(root, path, digest, revision.HTML_PATHS, revision.CHANGED_FILES)
            if revision is latest:
                break
    return _project(root, data, identities), (path, digest, data)


def projection_root(root: Path) -> Path:
    previous, layer = _previous(root)
    if layer is None:
        raise ValueError('No page revision to project')
    return previous


def _layers(root):
    """Unwind the active revisions, returning the v49 view and oldest-first manifests."""
    layers = []
    while True:
        root, layer = _previous(root)
        if layer is None:
            return root, layers[::-1]
        layers.append(layer)


def historical_root(root: Path) -> Path:
    previous, _ = _layers(root)
    return navigation.historical_root(previous)


def _updated(entries, data):
    revised = dict(entries)
    for route in data['changed_html_paths']:
        row = next(row for row in data['reversible_text_files'] if row['path'] == 'site/'+route)
        old = entries[route]
        if (old['sha256'], old['bytes']) != (row['old_sha256'], row['old_bytes']):
            raise ValueError('Page entry differs from the preceding publication: '+route)
        revised[route] = {**old, 'sha256': row['new_sha256'], 'bytes': row['new_bytes'],
                          'presentation_id': data['presentation_id']}
    return revised


def apply(root, baseline, callback, *, verify_current=True, revision_chain=None, include_presentation=True):
    previous, layers = _layers(root)
    entries, report = navigation._entries(previous, baseline, callback, {
        'verify_current': verify_current, 'revision_chain': revision_chain,
        'include_presentation': include_presentation})
    if not include_presentation:
        return entries, report
    for path, digest, data in layers:
        entries = _updated(entries, data)
        report = _append_report(report, path, digest, data)
    return entries, report


def _append_report(report, path, digest, data):
    summary = {key: data[key] for key in ('presentation_id', 'publication_kind',
        'previous_presentation_commit', 'scientific_review_status', 'release_eligible',
        'scientific_data_unchanged', 'historical_achievement_independent_of_AI_review',
        'M0_resumed', 'Nemotron_training_resumed')}
    changed = data['changed_html_paths']
    summary.update(path=path, sha256=digest, changed_paths=changed, added_paths=[])
    history = report['presentation']['presentation_chain']
    return {**report, 'changed_paths': sorted(set(report['changed_paths']) | set(changed)),
            'presentation': {**summary, 'presentation_chain': [*history, summary]}}


def publication_members(root, entries, prior_entries, prior_members):
    previous, layers = _layers(root)
    baseline = json.loads(_file(previous, 'provenance/website-baseline.json').read_bytes())
    old, _ = navigation._entries(previous, baseline, prior_entries, {
        'verify_current': True, 'revision_chain': None, 'include_presentation': True})
    revised = old
    for _, _, data in layers:
        revised = _updated(revised, data)
    if entries != revised:
        raise ValueError('Page revision entries differ in identity, role or membership')
    members = prior_members(previous, old)
    if (len(members) != len(PUBLICATION_PATHS) or {row['path'] for row in members} != set(PUBLICATION_PATHS)
            or any(row != old[row['path']] for row in members)):
        raise ValueError('Story source update must preserve the preceding publication allowlist')
    return [deepcopy(entries[row['path']]) for row in members]
