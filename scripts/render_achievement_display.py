"""Render scientific achievement narratives with consolidated public references."""
from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import posixpath
import re

ROOT = Path(__file__).resolve().parents[1]
CONTENT = 'content/achievement-display.v1.json'
DOCUMENT = 'docs/ACHIEVEMENT_DISPLAY_zh-CN.md'
BASELINE_COMMIT = '9a881e8724e16dd7bc17b12547c063dca4d4a401'
MAIN_ROUTES = {
    'A01': 'topics/early-fluoroketones/index.html',
    'A02': 'topics/fluoromonomers/index.html',
    'A03': 'pftb/index.html',
    'A04': 'topics/f53/index.html',
    'A05': 'topics/refrigerants/index.html',
    'A06': 'topics/chen-reagent/index.html',
    'A07': 'topics/single-electron-transfer/index.html',
    'A08': 'topics/fluoroporphyrins/index.html',
    'A09': 'people/index.html',
}
DEEP_ROUTES = {**MAIN_ROUTES, 'A06': 'topics/perfluorosulfonates/index.html',
               'A08': 'topics/deoxyfluorination/index.html'}
ROUTES = ('index.html', 'achievements/index.html', *MAIN_ROUTES.values(),
          'topics/perfluorosulfonates/index.html', 'topics/deoxyfluorination/index.html')


def identity(value: bytes) -> tuple[str, int]:
    return hashlib.sha256(value).hexdigest(), len(value)


def load_source(root: Path) -> dict:
    data = json.loads((root / CONTENT).read_bytes())
    fixed = {'schema_version': '1.0', 'baseline_commit': BASELINE_COMMIT,
             'scientific_review_status': 'review_required', 'release_eligible': False,
             'M0_status': 'paused', 'Nemotron_training_status': 'paused',
             'new_quantum_calls': 0, 'new_model_API_calls': 0, 'new_model_training_runs': 0}
    if any(data.get(k) != v or type(data.get(k)) is not type(v) for k, v in fixed.items()):
        raise ValueError('Reader editing cannot change the scientific or execution boundary')
    if list(data['pages']) != list(ROUTES) or [r['id'] for r in data['journeys']] != list(MAIN_ROUTES):
        raise ValueError('Achievement display requires the thirteen fixed pages and nine ordered lines')
    labels = json.loads((root / 'content/achievement-labels.v1.json').read_bytes())['labels']
    for row in data['journeys']:
        ident = row['id']
        if (row['name'] != labels[ident] or row['main_route'] != MAIN_ROUTES[ident]
                or row['deep_route'] != DEEP_ROUTES[ident]
                or row['representative_anchor'] != ident.lower() + '-representative-study'
                or row['deep_anchor'] != ident.lower() + '-deep-reading'
                or row['story_anchor'] != ident.lower() + '-representative-study-story'):
            raise ValueError('A reader entry lost its canonical line or destination')
        if not row['relationship'] or not row['deep_label']:
            raise ValueError('A cross-topic reading needs an explicit relationship')
    for route, page in data['pages'].items():
        if not isinstance(page['edits'], list) or not page['edits']:
            raise ValueError('Every reviewed page requires a bounded reversible edit')
        for version in ('before', 'after'):
            if (not re.fullmatch('[0-9a-f]{64}', page[version + '_sha256'])
                    or type(page[version + '_bytes']) is not int or page[version + '_bytes'] <= 0):
                raise ValueError('Incomplete page identity: ' + route)
        end = 0
        for edit in page['edits']:
            if (set(edit) != {'offset', 'old', 'new'} or type(edit['offset']) is not int
                    or edit['offset'] < end or not isinstance(edit['old'], str)
                    or not isinstance(edit['new'], str) or edit['old'] == edit['new']):
                raise ValueError('Invalid or overlapping exact editorial edit')
            end = edit['offset'] + len(edit['old'].encode('utf-8'))
    if re.search(r'private-sources|current-item-register|file://|[CD]:[\\/]',
                 json.dumps(data, ensure_ascii=False), re.I):
        raise ValueError('Private originals and tracking lists cannot enter the reading layer')
    return data


def transform(page: dict, value: bytes, *, reverse: bool = False) -> bytes:
    source, target = ('after', 'before') if reverse else ('before', 'after')
    if identity(value) != (page[source + '_sha256'], page[source + '_bytes']):
        raise ValueError('Page bytes differ from the reviewed ' + source + ' version')
    parts, cursor, delta = [], 0, 0
    for edit in page['edits']:
        old, new = edit['old'].encode('utf-8'), edit['new'].encode('utf-8')
        position = edit['offset'] + (delta if reverse else 0)
        before, after = (new, old) if reverse else (old, new)
        if position < cursor or value[position:position + len(before)] != before:
            raise ValueError('Exact reader edit differs at its reviewed offset')
        parts.extend((value[cursor:position], after))
        cursor = position + len(before)
        delta += len(new) - len(old)
    result = b''.join((*parts, value[cursor:]))
    if identity(result) != (page[target + '_sha256'], page[target + '_bytes']):
        raise ValueError('Reconstructed reader page has a different identity')
    return result


def restore_previous_html(root: Path, route: str, current_bytes: bytes) -> bytes:
    data = load_source(root)
    if route not in ROUTES:
        raise ValueError('Unapproved reader page')
    return transform(data['pages'][route], current_bytes, reverse=True)


class Page(HTMLParser):
    def __init__(self, value: bytes):
        super().__init__()
        self.ids, self.links, self.journey_navs = [], [], 0
        self.feed(value.decode('utf-8'))

    def handle_starttag(self, tag: str, attrs: list):
        data = dict(attrs)
        if data.get('id'):
            self.ids.append(data['id'])
        if tag == 'a' and data.get('name'):
            self.ids.append(data['name'])
        if tag == 'a' and data.get('href'):
            self.links.append(data['href'])
        classes = set(data.get('class', '').split())
        if (tag == 'nav' and 'cq-journey-nav' in classes
                and not classes.intersection({'cq-study-nav', 'cq-deep-nav'})):
            self.journey_navs += 1


def link(current: str, target: str, anchor: str = '') -> str:
    path = '' if current == target else posixpath.relpath(target, posixpath.dirname(current))
    return path + ('#' + anchor if anchor else '')


def render_document(root: Path) -> str:
    data = load_source(root)
    out = ['# 陈庆云院士学术成就与传承：成果阅读', '',
           '首页介绍生平与代表性贡献，成果汇总页连接八条科研成果线与一条学术传承线。专题展开科学问题、研究过程、关键结果与合作育人故事，让读者可以直接理解成果及其科学意义。', '',
           '| 成果与传承线 | 专题 |', '| --- | --- |']
    base = 'https://cccolab.github.io/Chen-Qingyun-AI4Science/'
    for row in data['journeys']:
        out.append('| ' + row['id'] + '（' + row['name'] + '） | [' + row['representative_title']
                   + '](' + base + row['main_route'] + '#' + row['representative_anchor'] + ') |')
    out += ['', '完整书目集中在各页末尾的参考资料，原文入口供进一步阅读。核查过程和内部资料管理不作为正文主线。', '',
            '历史成果归原作者与实际参与者；平台新增图解和释读属于AI辅助整理，保持review_required、release_eligible=false。文献核校不称为实验复现或机理验证。M0与Nemotron训练继续暂停。', '']
    return '\n'.join(out)


def inspect_achievement_display(root: Path) -> dict:
    errors, checked = [], []
    try:
        data = load_source(root)
        parsed = {}
        for route, page in data['pages'].items():
            value = (root / 'site' / route).read_bytes()
            before = transform(page, value, reverse=True)
            if transform(page, before) != value:
                errors.append('Reader page is not exactly reproducible: ' + route)
            old, current = Page(before), Page(value)
            parsed[route] = current
            if len(current.ids) != len(set(current.ids)) or not set(old.ids).issubset(current.ids):
                errors.append('Original reader anchors lost or duplicated: ' + route)
            if route not in ('index.html', 'achievements/index.html') and current.journey_navs != 1:
                errors.append('Expected one consistent topic navigation: ' + route)
            references = re.findall(r'<section\b[^>]*class="[^"]*cq-display-references[^"]*"[^>]*>', value.decode('utf-8'))
            if len(references) != 1:
                errors.append('Expected one consolidated references section: ' + route)
            if 'cq-achievement-display-style' not in current.ids:
                errors.append('Missing scoped reading styles: ' + route)
            checked.append({'route': route, 'exact_reverse': True, 'exact_render': True})
        for row in data['journeys']:
            ident = row['id']
            for page in ('index.html', 'achievements/index.html'):
                for target, anchor in [(row['main_route'], row['representative_anchor']),
                                       (row['deep_route'], row['deep_anchor']),
                                       (row['main_route'], row['story_anchor'])]:
                    if link(page, target, anchor) not in parsed[page].links:
                        errors.append('Missing direct overview reading entry: ' + page + '/' + ident)
            for route in dict.fromkeys((row['main_route'], row['deep_route'])):
                for target, anchor in [(row['main_route'], row['representative_anchor']),
                                       (row['deep_route'], row['deep_anchor']),
                                       (row['main_route'], row['story_anchor'])]:
                    if link(route, target, anchor) not in parsed[route].links:
                        errors.append('Topic navigation lost an intended reading: ' + route + '/' + anchor)
        from check_navigation import inspect_navigation
        from public_line_labels import inspect_line_labels
        errors.extend('Navigation: ' + e for e in inspect_navigation(root)['errors'])
        errors.extend(inspect_line_labels(root)['errors'])
        if (root / DOCUMENT).read_bytes() != render_document(root).encode('utf-8'):
            errors.append('Reader document differs from its reviewed source')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append(str(exc))
    return {'status': 'failed' if errors else 'passed', 'errors': errors,
            'achievement_lines': 9, 'pages': checked,
            'scientific_review_status': 'review_required', 'release_eligible': False,
            'M0_resumed': False, 'Nemotron_training_started': False}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    if args.write:
        data = load_source(root)
        for route, page in data['pages'].items():
            path = root / 'site' / route
            value = path.read_bytes()
            if identity(value) == (page['before_sha256'], page['before_bytes']):
                path.write_bytes(transform(page, value))
            elif identity(value) != (page['after_sha256'], page['after_bytes']):
                raise ValueError('Refusing to overwrite unreviewed page edits: ' + route)
        (root / DOCUMENT).write_bytes(render_document(root).encode('utf-8'))
    result = inspect_achievement_display(root)
    if args.output:
        args.output.write_bytes((json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
    print(json.dumps(result, ensure_ascii=False))
    return bool(result['errors'])


if __name__ == '__main__':
    raise SystemExit(main())
