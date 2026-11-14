"""Check nine-line navigation and archive hierarchy; no scientific review or network."""
from __future__ import annotations

import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import posixpath
import re
from urllib.parse import unquote, urlsplit

from a01_publication_contract import inspect_line_numbering
from public_line_labels import display_text

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = 'topics/index.html'
LINES = ['A'+str(n).zfill(2) for n in range(1, 10)]
LEGACY_ARCHIVES = {'case-pftb': 'A03', 'case-f53': 'A04',
    'case-refrigerant': 'A05', 'case-reagent': 'A06',
    'case-activation': 'A07', 'case-porphyrin': 'A08'}
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
        'link', 'meta', 'param', 'source', 'track', 'wbr'}


class Element:
    def __init__(self, tag, attrs=(), parent=None):
        self.tag, self.attrs, self.parent = tag, dict(attrs), parent
        self.children = []

    def text(self):
        return ''.join(x if isinstance(x, str) else x.text() for x in self.children).strip()

    def nodes(self):
        for child in self.children:
            if isinstance(child, Element):
                yield child
                yield from child.nodes()

    def ancestors(self):
        parent = self.parent
        while parent is not None:
            yield parent
            parent = parent.parent


class NavigationPage(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.root = self.current = Element('document')
        self.feed(source)
        self.close()

    def handle_starttag(self, tag, attrs):
        node = Element(tag, attrs, self.current)
        self.current.children.append(node)
        if tag not in VOID:
            self.current = node

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_data(self, value):
        self.current.children.append(value)

    def handle_endtag(self, tag):
        for node in [self.current, *self.current.ancestors()]:
            if node.tag == tag and node.parent is not None:
                self.current = node.parent
                break


def one(nodes, label):
    values = list(nodes)
    if len(values) != 1:
        raise ValueError(label+' must occur exactly once')
    return values[0]


def links(node):
    return [x for x in node.nodes() if x.tag == 'a' and x.attrs.get('href') is not None]


def destination(site, source, link):
    parsed = urlsplit(link.attrs['href'])
    if parsed.scheme or parsed.netloc:
        return None, None
    path = unquote(parsed.path)
    target = posixpath.normpath(posixpath.join(posixpath.dirname(source), path)) if path else source
    if (site/target).is_dir():
        target = posixpath.join(target, 'index.html')
    return target, unquote(parsed.fragment)


def inspect_navigation(root: Path = ROOT) -> dict:
    report = {'status': 'failed', 'scope': 'Nine-line ownership, directory links and supplemental archive hierarchy only',
              'errors': [], 'page_checks': [], 'network_calls': 0, 'new_quantum_calls': 0,
              'scientific_claims_reviewed': False, 'files_written': 0}
    site, pages = root/'site', {}

    def page(name):
        if name not in pages:
            pages[name] = NavigationPage((site/name).read_text('utf-8')).root
        return pages[name]

    def check(name, action):
        item = {'path': name, 'status': 'failed'}
        report['page_checks'].append(item)
        try:
            item.update(action(), status='passed')
        except (OSError, ValueError, KeyError, TypeError) as error:
            report['errors'].append(name+': '+str(error))

    try:
        registry = json.loads((site/'data/achievement-lines.json').read_text('utf-8'))['lines']
        if [line['id'] for line in registry] != LINES:
            raise ValueError('The source registry must retain A01 through A09 in order')
        owners = {route['path']: line['id'] for line in registry for route in line['routes']
                  if route['path'].startswith('topics/') and route['path'] != DIRECTORY}
        if len(owners) != 11:
            raise ValueError('The source registry must identify the eleven detailed topics')

        def directory_check():
            directory = page(DIRECTORY)
            groups = [n for n in directory.nodes() if n.attrs.get('id', '').startswith('topic-line-')]
            if [n.attrs['id'] for n in groups] != ['topic-line-'+n.lower() for n in LINES]:
                raise ValueError('The topic directory must contain nine ordered groups A01 through A09')
            for line, group in zip(registry, groups):
                number = line['id']
                heading = one((n for n in group.nodes() if n.tag == 'h2'), number+' directory heading')
                link = one(links(heading), number+' heading link')
                if not re.match(number+r'\b', link.text()) or destination(site, DIRECTORY, link) != ('index.html', 'line-'+number.lower()):
                    raise ValueError(number+' directory heading must link to its own homepage line')
                targets = {destination(site, DIRECTORY, a) for a in links(group)}
                for route in line['routes']:
                    if route['path'] in owners or route['path'] == 'pftb/index.html':
                        if not any(target[0] == route['path'] for target in targets):
                            raise ValueError(number+' directory omits its topic '+route['path'])
                if number == 'A09' and not targets & {('achievements/index.html', 'heritage-line-a09'),
                        ('achievements/index.html', 'record-publication-index'), ('index.html', 'record-publication-index')}:
                    raise ValueError('A09 requires a link to its actual heritage materials')
            return {'line_groups': LINES, 'PFtB_in_A03': True, 'A09_material_entry': True}

        check(DIRECTORY, directory_check)
        for name, owner in owners.items():
            def topic_check(name=name, owner=owner):
                anchors = links(page(name))
                belonging = one((a for a in anchors if '所属成果线' in a.text()), 'Topic ownership link')
                if belonging.text() != display_text('所属成果线 '+owner) or destination(site, name, belonging) != ('index.html', 'line-'+owner.lower()):
                    raise ValueError('Topic ownership must match source registry '+owner)
                indexes = [a for a in anchors if '专题索引' in a.text()]
                if len(indexes) < 2 or not any(a.text().startswith('返回专题索引') for a in indexes):
                    raise ValueError('Both topic index and return-to-index entries are required')
                if any(destination(site, name, a) != (DIRECTORY, '') for a in indexes):
                    raise ValueError('Every topic-index entry must lead to the real directory')
                return {'achievement_line': owner, 'directory_links_checked': len(indexes)}
            check(name, topic_check)

        for name in ('index.html', 'achievements/index.html'):
            def overview_check(name=name):
                result = inspect_line_numbering(site/name)
                overview = page(name)
                nav = one((n for n in overview.nodes() if n.tag == 'nav' and n.attrs.get('aria-label') == '按九条成果线查阅专题'), 'Nine-line directory navigation')
                anchors = links(nav)
                if [destination(site, name, a) for a in anchors] != [(DIRECTORY, 'topic-line-'+n.lower()) for n in LINES]:
                    raise ValueError('Directory navigation must link to the nine corresponding groups in order')
                if any(not re.match(number+r'\b', a.text()) for number, a in zip(LINES, anchors)):
                    raise ValueError('Directory entry labels must agree with their line destinations')
                if name == 'index.html':
                    for ident, owner in LEGACY_ARCHIVES.items():
                        archive = one((n for n in overview.nodes() if n.attrs.get('id') == ident), ident)
                        if archive.tag != 'details' or 'open' in archive.attrs or not any(n.attrs.get('id') == 'line-'+owner.lower() for n in archive.ancestors()):
                            raise ValueError(ident+' must be a collapsed supplemental archive within '+owner)
                        if any(re.fullmatch(r'0[1-6]', n.text()) for n in archive.nodes()
                               if {'num', 'case-side'} & set(n.attrs.get('class', '').split())):
                            raise ValueError(ident+' retains a competing bare 01–06 label')
                    result['legacy_archives_nested'] = len(LEGACY_ARCHIVES)
                return result
            check(name, overview_check)
    except (OSError, ValueError, KeyError, TypeError) as error:
        report['errors'].append(str(error))
    report['status'] = 'failed' if report['errors'] else 'passed'
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='New optional JSON evidence file')
    args = parser.parse_args()
    report = inspect_navigation()
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x', encoding='utf-8', newline='\n') as stream:
            json.dump(report, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
    print(json.dumps({'status': report['status'], 'pages_checked': len(report['page_checks']),
                      'errors': report['errors']}, ensure_ascii=False))
    return 0 if report['status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
