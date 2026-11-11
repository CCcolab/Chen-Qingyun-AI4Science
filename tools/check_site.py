#!/usr/bin/env python3
"""Validate migration integrity and local destinations without third-party packages."""
import argparse
from collections import Counter
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import platform
from threading import Thread
from urllib.parse import quote, unquote, urljoin, urlsplit
from urllib.request import ProxyHandler, build_opener

from serve_site import ROOT, create_server, normalize_prefix

SITE = ROOT / 'site'
PROTECTED = {
    'data/public-sources.json': '94f8b9f6d0849deb9f26f75947205cfc8c4eb0973045fe958f2121237d987062',
    'data/achievement-lines.json': '1c9ec28bf41a7d79214e84a1c07f3bea1e0d91630dd3a88c93c39ff68a9bccec',
}


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.references = []
        self.json_blocks = {}
        self.active_json = None
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('id'):
            self.ids.append(attrs['id'])
        for attr in ('href', 'src', 'poster'):
            if attrs.get(attr):
                self.references.append(attrs[attr])
        if tag == 'script' and attrs.get('type') == 'application/json' and attrs.get('id'):
            self.active_json = attrs['id']
            self.json_blocks[self.active_json] = ''

    def handle_data(self, data):
        if self.active_json:
            self.json_blocks[self.active_json] += data

    def handle_endtag(self, tag):
        if tag == 'script':
            self.active_json = None


def check(http=False, prefix='/Chen-Qingyun-AI4Science/'):
    errors = []
    manifest = json.loads((ROOT / 'audit/site-manifest.json').read_text())
    files = {p.relative_to(SITE).as_posix(): p for p in SITE.rglob('*') if p.is_file()}
    if set(files) != set(manifest['files']):
        errors.append('Site file list differs from immutable migration manifest')
    for name, digest in manifest['files'].items():
        if name not in files or sha256(files[name].read_bytes()).hexdigest() != digest:
            errors.append(f'Changed or missing baseline file: {name}')
    for name, digest in PROTECTED.items():
        if name not in files or sha256(files[name].read_bytes()).hexdigest() != digest:
            errors.append(f'Protected JSON differs from original A2 bytes: {name}')

    pages = {n: Page(p.read_text(encoding='utf-8')) for n, p in files.items() if p.suffix == '.html'}
    if len(pages) != manifest['expected_html_count']:
        errors.append(f'Expected 15 HTML pages, found {len(pages)}')
    sources = json.loads((SITE / 'data/public-sources.json').read_text())
    lines = json.loads((SITE / 'data/achievement-lines.json').read_text())
    if len(sources['sources']) != manifest['expected_sources'] or len(lines['lines']) != manifest['expected_achievement_lines']:
        errors.append('Expected 51 sources and 9 achievement lines')
    home = pages['index.html']
    if json.loads(home.json_blocks.get('citation-original-data', '{}')) != sources:
        errors.append('Homepage citation JSON differs from canonical source JSON')
    for source in sources['sources']:
        if home.ids.count('source-' + source['id'].lower()) != 1:
            errors.append(f'Missing or duplicate source card: {source["id"]}')

    local_count = 0
    http_targets = set(files)
    for name, page in pages.items():
        duplicates = [key for key, count in Counter(page.ids).items() if count > 1]
        if duplicates:
            errors.append(f'{name}: duplicate IDs {duplicates}')
        for ref in page.references:
            parts = urlsplit(ref)
            if parts.scheme or parts.netloc:
                continue
            local_count += 1
            if parts.path.startswith('/'):
                errors.append(f'{name}: root-relative link breaks project hosting: {ref}')
                continue
            destination = urlsplit(urljoin('https://migration.invalid/' + name, ref))
            target = unquote(destination.path).lstrip('/')
            if not target or target.endswith('/'):
                target += 'index.html'
            if target not in files:
                errors.append(f'{name}: missing target {ref} -> {target}')
                continue
            http_targets.add(target)
            fragment = unquote(destination.fragment)
            if fragment and target in pages and fragment not in pages[target].ids:
                if target == 'pftb/index.html' and fragment.startswith('s/'):
                    continue  # PFtB application state, not an HTML element ID.
                errors.append(f'{name}: missing anchor {ref} -> {target}#{fragment}')

    requests = 0
    if http and not errors:
        opener = build_opener(ProxyHandler({}))
        with create_server(prefix=prefix) as server:
            thread = Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                for mount in ('/', normalize_prefix(prefix)):
                    for target in sorted(http_targets):
                        url = f'http://127.0.0.1:{server.server_port}{mount}{quote(target)}'
                        with opener.open(url, timeout=10) as response:
                            requests += 1
                            if response.status != 200 or response.read() != files[target].read_bytes():
                                errors.append(f'HTTP bytes mismatch: {mount}{target}')
                    for target in sorted(pages):
                        route = target[:-len('index.html')]
                        with opener.open(f'http://127.0.0.1:{server.server_port}{mount}{route}', timeout=10) as response:
                            requests += 1
                            if response.read() != files[target].read_bytes():
                                errors.append(f'Directory index mismatch: {mount}{route}')
            finally:
                server.shutdown()
                thread.join(timeout=5)

    return {
        'status': 'pass' if not errors else 'fail',
        'environment': {'system': platform.system(), 'release': platform.release(), 'python': platform.python_version()},
        'scope': 'File integrity, JSON equality, static destinations and optional loopback HTTP; excludes browser interactions, clipboard and scientific validation.',
        'html_pages': len(pages), 'sources': len(sources['sources']), 'achievement_lines': len(lines['lines']),
        'local_references_checked': local_count, 'http_requests': requests,
        'mounts_checked': ['/', normalize_prefix(prefix)] if http and requests else [],
        'errors': errors,
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--http', action='store_true')
    parser.add_argument('--prefix', default='/Chen-Qingyun-AI4Science/')
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    result = check(args.http, args.prefix)
    serialized = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(serialized)
    print(serialized, end='')
    raise SystemExit(0 if result['status'] == 'pass' else 1)
