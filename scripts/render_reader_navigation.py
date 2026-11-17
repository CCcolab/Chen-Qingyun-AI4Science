"""Render the compact historical achievement guide on the two reading pages."""
from __future__ import annotations

import argparse
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path('content/reader-navigation.v1.json')
DOCUMENT = Path('docs/READER_NAVIGATION_zh-CN.md')
BEGIN = '<!-- READER_NAVIGATION:BEGIN -->'
END = '<!-- READER_NAVIGATION:END -->'
PAGES = {'home': 'site/index.html', 'achievements': 'site/achievements/index.html'}


class Tags(HTMLParser):
    def __init__(self, value: str):
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.links: list[str] = []
        self.feed(value)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get('id'):
            self.ids.append(values['id'])
        if tag == 'a' and values.get('href'):
            self.links.append(values['href'])


def load(root: Path) -> dict:
    data = json.loads((root / SOURCE).read_bytes())
    guide = json.loads((root / 'content/nine-line-reading.v1.json').read_bytes())
    studies = json.loads((root / 'content/representative-studies.v1.json').read_bytes())
    labels = json.loads((root / 'content/achievement-labels.v1.json').read_bytes())['labels']
    if [row['id'] for row in data['lines']] != list(labels):
        raise ValueError('Reader guide must contain A01–A09 once in canonical order')
    if data['scientific_review_status'] != 'review_required' or data['release_eligible'] is not False:
        raise ValueError('Reader guide must retain scientific review boundaries')
    if data['m0_status'] != 'paused' or data['model_training_status'] != 'not_started':
        raise ValueError('Reader guide cannot resume scientific computation or training')
    for row, original, study in zip(data['lines'], guide['lines'], studies['studies']):
        if row['name'] != labels[row['id']]:
            raise ValueError('Noncanonical achievement name: ' + row['id'])
        for key in ('question', 'contribution', 'cooperation', 'source_note', 'source_ids'):
            if row[key] != original[key]:
                raise ValueError('Reader content differs from its cited historical guide: ' + row['id'] + '/' + key)
        if (row['route'], row['anchor'], row['study_title']) != (study['route'], study['anchor'], study['title']):
            raise ValueError('Reader destination differs from its representative study: ' + row['id'])
        for fragment in row.get('appendices', {}).values():
            if re.search(r'<(?:script|style)\b', fragment, re.I):
                raise ValueError('Legacy reading appendices cannot contain executable payloads')
    return data


def render_navigation(root: Path, page: str) -> str:
    if page not in PAGES:
        raise ValueError('Unknown reader page')
    data = load(root)
    prefix = '' if page == 'home' else '../'
    compatibility = '<span id="details"></span>' if page == 'home' else '<span id="heritage-inventory"></span>'
    out = [BEGIN, '<section class="shell-section" id="achievement-detail"><div class="wrap">' + compatibility,
           '<div class="section-head"><div><div class="kicker">SCIENTIFIC ACHIEVEMENTS AND CONTINUITY</div>'
           '<h2>八条科研成果线与一条学术传承线</h2></div><p>' + html.escape(data['intro']) + '</p></div>']
    for row in data['lines']:
        label = row['id'] + '（' + row['name'] + '）'
        compat = '' if page == 'home' else '<span id="heritage-line-' + row['id'].lower() + '"></span>'
        out += ['<article class="case" id="line-' + row['id'].lower() + '">'
                '<div class="case-side">' + html.escape(row['period']) + '</div><div class="case-main">' + compat,
                '<h3>' + html.escape(label) + '</h3>']
        if page == 'achievements':
            out.append('<p><b>科学问题：</b>' + html.escape(row['question']) + '</p>')
        out.append('<p><b>具体贡献：</b>' + html.escape(row['contribution']) + '</p>')
        if page == 'achievements':
            out += ['<p><b>合作与传承：</b>' + html.escape(row['cooperation']) + '</p>',
                    '<p class="meta">出处：' + html.escape(row['source_note']) + '</p>']
        out.append('<p><a class="text-link" href="' + html.escape(prefix + row['route'] + '#' + row['anchor'], quote=True)
                + '" aria-label="' + html.escape(label + '：' + row['study_title'], quote=True)
                + '">代表成果详读：' + html.escape(row['study_title']) + ' →</a></p>')
        appendix = row.get('appendices', {}).get(page, '')
        if appendix:
            out.append(appendix)
        out.append('</div></article>')
    out += ['</div></section>', END]
    return '\n'.join(out)


def render_document(root: Path) -> str:
    data = load(root)
    out = ['# ' + data['title'], '',
           '从首页认识陈庆云院士的生平、开拓性成果和治学精神；首页九条简明导览介绍具体贡献，成果汇总页展开科学问题与合作线索，下一层专题详读研究过程和关键结果。', '',
           '《氟缘笃志：陈庆云传》贯穿研究道路与合作育人故事，具体页码和原文出处随专题保留。具名回忆、原论文和机构报道按各自资料性质使用。', '',
           '| 成果与传承线 | 代表成果详读 |', '| --- | --- |']
    for row in data['lines']:
        out.append('| ' + row['id'] + '（' + row['name'] + '） | [' + row['study_title']
                   + '](https://cccolab.github.io/Chen-Qingyun-AI4Science/' + row['route'] + '#' + row['anchor'] + ') |')
    out += ['', '每个专题的代表成果详读先讲历史研究，延伸阅读保留原文、图表及后续作者的不同贡献。合作与育人故事保留姓名、传记页码和回忆性质；科学论断按原作的对象和条件理解。', '',
            'AI辅助资料整理与研究独立呈现。多语核译、数据重放及计算探索属于平台新增工作，不能改称陈先生当年的计算，也不能将文献核校称为实验复现或机理验证。', '',
            '首页末尾的“参考资料与延伸阅读”收拢详细来源、来源检索和旧选读路径。原有编号与链接仍可定位到相应内容。', '']
    return '\n'.join(out)


def inspect_reader_navigation(root: Path) -> dict:
    errors: list[str] = []
    try:
        data = load(root)
        for page, path in PAGES.items():
            value = (root / path).read_bytes().decode('utf-8')
            if value.count(BEGIN) != 1 or value.count(END) != 1 or render_navigation(root, page) not in value:
                errors.append('Reader navigation differs from its source: ' + path)
            parsed = Tags(value)
            if len(parsed.ids) != len(set(parsed.ids)):
                errors.append('Duplicate page identifiers: ' + path)
            prefix = '' if page == 'home' else '../'
            for row in data['lines']:
                if prefix + row['route'] + '#' + row['anchor'] not in parsed.links:
                    errors.append('Missing representative-study entry: ' + path + '/' + row['id'])
                if 'line-' + row['id'].lower() not in parsed.ids:
                    errors.append('Missing line anchor: ' + path + '/' + row['id'])
        for row in data['lines']:
            path = root / 'site' / row['route']
            value = path.read_bytes().decode('utf-8')
            label = row['id'] + '（' + row['name'] + '）'
            headings = re.findall(r'<h1\b[^>]*>(.*?)</h1>', value, re.S)
            titles = re.findall(r'<title>(.*?)</title>', value, re.S)
            if len(headings) != 1 or not html.unescape(re.sub('<[^>]*>', '', headings[0])).startswith(label):
                errors.append('Noncanonical topic heading: ' + row['route'])
            if len(titles) != 1 or not html.unescape(titles[0]).startswith(label):
                errors.append('Noncanonical topic title: ' + row['route'])
            parsed = Tags(value)
            if parsed.ids.count(row['anchor']) != 1 or len(parsed.ids) != len(set(parsed.ids)):
                errors.append('Topic anchor identity problem: ' + row['route'])
        if (root / DOCUMENT).read_bytes() != render_document(root).encode('utf-8'):
            errors.append('Reader document differs from its source rendering')
        from render_representative_studies import inspect_studies
        study_report = inspect_studies(root)
        errors += study_report['errors']
    except (OSError, ValueError, KeyError, TypeError) as error:
        errors.append(str(error))
    return {'status': 'failed' if errors else 'passed', 'errors': errors, 'lines': 9,
            'scientific_review_status': 'review_required', 'release_eligible': False,
            'M0_resumed': False, 'Nemotron_training_started': False}


def main() -> int:
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument('--write', action='store_true')
    args = argument_parser.parse_args()
    if args.write:
        for page, path in PAGES.items():
            target = ROOT / path
            value = target.read_bytes().decode('utf-8')
            if value.count(BEGIN) != 1 or value.count(END) != 1:
                raise ValueError('Reader markers are missing or ambiguous: ' + path)
            value = re.sub(re.escape(BEGIN) + '.*?' + re.escape(END),
                           lambda _: render_navigation(ROOT, page), value, flags=re.S)
            target.write_bytes(value.encode('utf-8'))
        (ROOT / DOCUMENT).write_bytes(render_document(ROOT).encode('utf-8'))
    report = inspect_reader_navigation(ROOT)
    print(json.dumps(report, ensure_ascii=False))
    return report['status'] != 'passed'


if __name__ == '__main__':
    raise SystemExit(main())
