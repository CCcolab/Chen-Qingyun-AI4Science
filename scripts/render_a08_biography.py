"""Render the biography-led A08 historical topics and their public document."""
from __future__ import annotations

import argparse
from html import escape
import json
from pathlib import Path
import re

from public_line_labels import project_html, project_markdown

CONTENT = 'content/a08-biography-narrative.v1.json'
DOCUMENT = 'docs/A08_ACADEMIC_ACHIEVEMENTS_zh-CN.md'
ROUTES = (
    'topics/fluorinated-small-rings/index.html',
    'topics/fluoroporphyrins/index.html',
    'topics/deoxyfluorination/index.html',
    'topics/sulfonyl-fluoride/index.html',
)
BEGIN = '<!-- A08_BIOGRAPHY_HISTORY:BEGIN -->'
END = '<!-- A08_BIOGRAPHY_HISTORY:END -->'


def load(root: Path) -> dict:
    data = json.loads((root / CONTENT).read_bytes())
    if (data.get('schema_version'), data.get('achievement_line'),
            data.get('scientific_review_status'), data.get('release_eligible'),
            data.get('m0_status')) != ('1.0', 'A08', 'review_required', False, 'paused'):
        raise ValueError('A08 history and platform research scopes must remain separate')
    if tuple(page['route'] for page in data['pages']) != ROUTES:
        raise ValueError('A08 requires its four existing historical topic routes')
    for page in data['pages']:
        ids = [source['id'] for source in page['sources']]
        anchors = [source['anchor'] for source in page['sources']]
        cards = [card['id'] for card in page['cards']]
        if (len(ids) != len(set(ids)) or len(anchors) != len(set(anchors))
                or len(cards + anchors) != len(set(cards + anchors))
                or 'HERITAGE-S01' not in ids):
            raise ValueError('A08 source identities and topic anchors must be unique')
        if any(not set(card['source_ids']) <= set(ids) for card in page['cards']):
            raise ValueError('A08 historical contribution is missing its source')
        if any(len(row) != 3 for row in page['roles'] + page['authorship_rows'] + page['scope_rows']):
            raise ValueError('Incomplete A08 historical table')
    if re.search(r'private-sources|原始证据待核清单|现阶段待查事项统计|file://|(?<![A-Za-z])[A-Za-z]:[\\/]',
                 json.dumps(data, ensure_ascii=False)):
        raise ValueError('Private A08 worklists cannot enter public history')
    return data


def table(caption: str, columns: list[str], rows: list[list[str]], ident: str) -> str:
    return ('<div class="a08-table" role="region" tabindex="0" aria-labelledby="' + ident
            + '"><table><caption id="' + ident + '">' + escape(caption)
            + '</caption><thead><tr>'
            + ''.join('<th scope="col">' + escape(cell) + '</th>' for cell in columns)
            + '</tr></thead><tbody>'
            + ''.join('<tr><th scope="row">' + escape(row[0]) + '</th>'
                      + ''.join('<td>' + escape(cell) + '</td>' for cell in row[1:]) + '</tr>' for row in rows)
            + '</tbody></table></div>')


def render_block(root: Path, route: str) -> str:
    data = load(root)
    page = next(p for p in data['pages'] if p['route'] == route)
    sources = {s['id']: s for s in page['sources']}
    css = ('.a08-meaning{border-left:3px solid #aa7545;padding:10px 16px;background:#f7f4eb}'
           '.a08-locator{font-size:.86rem;color:var(--muted)}'
           '.a08-nav{display:flex;flex-wrap:wrap;gap:8px 18px}'
           '.a08-table{overflow-x:auto;max-width:100%;margin:20px 0;border:1px solid var(--line)}'
           '.a08-table table{border-collapse:collapse;min-width:640px;width:100%;font-size:.92rem}'
           '.a08-table caption{text-align:left;padding:14px;background:#edf3ee;color:var(--accent);font-weight:700}'
           '.a08-table th,.a08-table td{border-top:1px solid var(--line);padding:12px;text-align:left;vertical-align:top}'
           '.a08-table:focus-visible{outline:3px solid #aa7545}#refs{overflow-wrap:anywhere}')
    links = [('../fluorinated-small-rings/index.html', '含氟小环'),
             ('../fluoroporphyrins/index.html', '卟啉与大环'),
             ('../deoxyfluorination/index.html', '脱氧氟化'),
             ('../sulfonyl-fluoride/index.html', '氟磺酰化与表面活性分子'),
             ('#a08-cooperation', '合作与传承'), ('#refs', '参考资料')]
    out = [BEGIN, '<style id="a08-biography-css">' + css + '</style>']
    for index, card in enumerate(page['cards']):
        topic = (' data-topic-slug="' + route.split('/')[1]
                 + '" data-topic-type="dossier"') if index == 0 else ''
        out += ['<article id="' + card['id'] + '"' + topic
                + '><span class="status">历史成果与合作</span><h2>' + escape(card['title']) + '</h2>']
        if index == 0:
            out += ['<p>' + escape(page['intro']) + '</p><nav class="a08-nav" aria-label="A08专题导航">'
                    + ''.join('<a href="' + url + '">' + label + '</a>' for url, label in links) + '</nav>']
        out += ['<p>' + escape(p) + '</p>' for p in card['paragraphs']]
        out += ['<p class="a08-meaning"><b>学术与应用意义：</b>' + escape(card['meaning'])
                + '</p><p class="a08-locator">' + escape(card['locator']) + ' · '
                + ' · '.join('<a href="#' + sources[ident]['anchor'] + '">' + escape(ident) + '</a>'
                             for ident in card['source_ids']) + '</p></article>']
    out += ['<article id="a08-cooperation"><h2>合作与学术传承</h2>',
            table('传记所记角色与具体合作', ['人物或团队', '贡献与角色', '出处'], page['roles'], 'a08-cooperation-caption'),
            '<section id="a08-authorship"><h3>具体论文的署名</h3>',
            table('按论文分别保留研究归属', ['研究', '原文署名', '发表定位'], page['authorship_rows'], 'a08-authorship-caption'),
            '<p>传记明确记载的指导与合作角色按原叙述介绍；论文署名用于说明共同成果，不据署名分派各项实验或计算的执行者。</p></section></article>',
            '<article id="a08-ai-collation"><h2>平台的AI辅助资料整理</h2><p>'
            + escape(data['platform_text']) + '</p><p><a href="../../research/index.html#ai-a08">'
            + 'A08（交叉研究与晚年拓展）的AI研究资料 →</a></p></article>',
            '<article id="refs"><h2>参考资料</h2><ul>']
    for source in page['sources']:
        title = ('<a href="' + escape(source['url'], quote=True) + '">' + escape(source['title']) + '</a>') if source['url'] else escape(source['title'])
        out += ['<li id="' + source['anchor'] + '"><b>' + escape(source['id']) + '</b> · '
                + title + '；' + escape(source['locator']) + '</li>']
    out += ['</ul><details><summary>研究对象与解释范围</summary>',
            table('各项结果对应的化学对象', ['对象', '资料所述内容', '解释范围'], page['scope_rows'], 'a08-scope-caption'),
            '</details><p><a href="../../achievements/index.html#line-a08">A08（交叉研究与晚年拓展）成果线</a>'
            + ' · <a href="../index.html">返回专题索引 ↑</a></p></article>', END]
    return project_html('\n'.join(out), route)


def render_document(root: Path) -> str:
    data = load(root)
    out = ['# ' + data['title'], '', '以《氟缘笃志：陈庆云传》中的研究经历与合作记述为主线，分别介绍具体化学对象、方法发展及晚年共同成果。', '']

    def md_table(columns, rows):
        return ['| ' + ' | '.join(columns) + ' |', '| ' + ' | '.join('---' for _ in columns) + ' |'] + [
            '| ' + ' | '.join(cell.replace('|', '\\|') for cell in row) + ' |' for row in rows] + ['']

    for page in data['pages']:
        out += ['## ' + page['title'], '', page['intro'], '', '[阅读专题](../site/' + page['route'] + ')', '']
        for card in page['cards']:
            out += ['### ' + card['title'], '']
            for paragraph in card['paragraphs']:
                out += [paragraph, '']
            out += ['**学术与应用意义：**' + card['meaning'], '', card['locator'] + ' · ' + '、'.join(card['source_ids']), '']
        out += ['### 合作与学术传承', ''] + md_table(['人物或团队', '贡献与角色', '出处'], page['roles'])
        out += ['### 具体论文的署名', ''] + md_table(['研究', '原文署名', '发表定位'], page['authorship_rows'])
        out += ['传记明确记载的指导与合作角色按原叙述介绍；论文署名用于说明共同成果，不据署名分派各项实验或计算的执行者。', '', '### 参考资料', '']
        for source in page['sources']:
            title = '[' + source['title'] + '](' + source['url'] + ')' if source['url'] else source['title']
            out += ['- **' + source['id'] + '** · ' + title + '；' + source['locator']]
        out += ['', '### 研究对象与解释范围', ''] + md_table(['对象', '资料所述内容', '解释范围'], page['scope_rows'])
    out += ['## 平台的AI辅助资料整理', '', data['platform_text'], '',
            '[A08（交叉研究与晚年拓展）的AI研究资料](../site/research/index.html#ai-a08)', '']
    return project_markdown('\n'.join(out))


def inspect_biography(root: Path) -> dict:
    errors = []
    try:
        for route in ROUTES:
            source = (root / 'site' / route).read_bytes().decode('utf-8')
            if source.count(BEGIN) != 1 or source.count(END) != 1 or render_block(root, route) not in source:
                errors.append('A08 topic differs from its historical source: ' + route)
        if (root / DOCUMENT).read_bytes() != render_document(root).encode('utf-8'):
            errors.append('A08 historical document differs from its source')
    except (ValueError, KeyError, OSError, StopIteration) as error:
        errors.append(str(error))
    return {'status': 'failed' if errors else 'passed', 'pages': len(ROUTES), 'errors': errors}


def write(root: Path) -> None:
    for route in ROUTES:
        path = root / 'site' / route
        source = path.read_bytes().decode('utf-8')
        start_marker, end_marker = '<main class="wrap">', '</main>'
        if source.count(start_marker) != 1 or source.count(end_marker) != 1:
            raise ValueError('A08 requires one bounded topic main region')
        start = source.index(start_marker) + len(start_marker)
        end = source.index(end_marker, start)
        path.write_bytes((source[:start] + render_block(root, route) + source[end:]).encode('utf-8'))
    (root / DOCUMENT).write_bytes(render_document(root).encode('utf-8'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    if args.write:
        write(root)
    result = inspect_biography(root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(bool(result['errors']))
