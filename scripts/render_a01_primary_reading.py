"""Present original A01 contributions separately from platform interpretation."""
from __future__ import annotations

import hashlib
from html import escape
import json
from pathlib import Path
import re

CONTENT = 'content/a01-primary-reading.v1.json'
DOCUMENT = 'docs/A01_PRIMARY_READING_zh-CN.md'
TOPIC = 'site/topics/early-fluoroketones/index.html'
ANCHOR = 'a01-primary-records'
SOURCE_IDS = {'A01-HIST-BIO', 'A01-HIST-SIOC', 'A01-HIST-P1960', 'CQ-H02'}


def load(root: Path) -> dict:
    data = json.loads((root / CONTENT).read_bytes())
    if (data.get('schema_version') != '1.0' or data.get('achievement_line') != 'A01'
            or data.get('scientific_review_status') != 'review_required'
            or data.get('release_eligible') is not False or data.get('m0_status') != 'paused'):
        raise ValueError('A01 source reading must preserve its scope and review status')
    for key in ('title', 'intro', 'records_title', 'records_note', 'authorship_title', 'source_note', 'platform_note'):
        if not isinstance(data.get(key), str) or not data[key].strip():
            raise ValueError('Missing A01 primary-reading prose: '+key)
    for item in data['contributions']:
        if not set(item['source_ids']) <= SOURCE_IDS:
            raise ValueError('Unknown historical source in A01 contribution')
    for source in data['sources']:
        if source['id'] not in SOURCE_IDS or not source['url'].startswith('https://'):
            raise ValueError('A01 original evidence requires known public source links')
    table = data['comparison']
    if len(table['columns']) != 3 or any(len(row) != 3 for row in table['rows']+data['authorship']):
        raise ValueError('A01 original evidence requires complete three-column tables')
    if re.search(r'private-sources|current-item-register|现阶段待查事项统计|原始证据待核清单|file://|(?<![A-Za-z])[A-Za-z]:[\\/]',
                 json.dumps(data, ensure_ascii=False)):
        raise ValueError('Private A01 records must remain local')
    return data


def table_html(caption: str, columns: list[str], rows: list[list[str]], ident: str) -> str:
    return ('<div class="a01-primary-table" role="region" tabindex="0" aria-labelledby="'+ident+'">'
            '<table><caption id="'+ident+'">'+escape(caption)+'</caption><thead><tr>'
            +''.join('<th scope="col">'+escape(s)+'</th>' for s in columns)+'</tr></thead><tbody>'
            +''.join('<tr><th scope="row">'+escape(row[0])+'</th>'
                      +''.join('<td>'+escape(cell)+'</td>' for cell in row[1:])+'</tr>' for row in rows)
            +'</tbody></table></div>')


def render_primary_history(root: Path) -> str:
    if not (root / CONTENT).exists():
        return ''
    data = load(root)
    styles = ('#a01-primary-records .a01-primary-table{max-width:100%;overflow-x:auto;margin:20px 0;border:1px solid var(--line)}'
              '#a01-primary-records table{width:100%;min-width:620px;border-collapse:collapse;font-size:.9rem}'
              '#a01-primary-records caption{text-align:left;background:#edf2ec;padding:14px;color:var(--accent);font-weight:700}'
              '#a01-primary-records th,#a01-primary-records td{text-align:left;vertical-align:top;padding:12px;border-top:1px solid var(--line);overflow-wrap:anywhere}'
              '#a01-primary-records thead{background:#f5f5ef}#a01-primary-records .a01-primary-table:focus-visible{outline:3px solid #aa7545}'
              '#a01-primary-records .a01-platform-note{border-top:1px solid var(--line);padding-top:16px;color:var(--muted);font-size:.9rem}')
    out = ['<style id="a01-primary-reading-css">'+styles+'</style>',
           '<article id="'+ANCHOR+'"><span class="status">A01 · 原作者的实验记录与共同贡献</span>',
           '<h2>'+escape(data['records_title'])+'</h2>', '<p>'+escape(data['intro'])+'</p>',
           table_html(data['records_title'], data['comparison']['columns'], data['comparison']['rows'], 'a01-primary-comparison'),
           '<p>'+escape(data['records_note'])+'</p>', '<ul>'+''.join('<li>'+escape(s)+'</li>' for s in data['data_notes'])+'</ul>',
           '<h3>'+escape(data['authorship_title'])+'</h3>',
           table_html(data['authorship_title'], ['材料', '署名与贡献归属', '出处'], data['authorship'], 'a01-primary-authorship'),
           '<p>'+escape(data['source_note'])+'</p>', '<details><summary>原文及资料出处</summary><ul>']
    out += ['<li><a href="'+escape(s['url'], quote=True)+'">'+escape(s['id']+' · '+s['title'])+'</a>：'+escape(s['locator'])+'</li>'
            for s in data['sources']]
    out += ['</ul></details><aside class="a01-platform-note"><h3>平台整理说明</h3><p>'+escape(data['platform_note'])+'</p>'
            '<p><a href="https://github.com/CCcolab/Chen-Qingyun-AI4Science/blob/main/'+DOCUMENT+'">原文证据与学术贡献说明</a> · '
            '<a href="../../research/index.html#ai-a01">A01（全氟酮化学：六氟丙酮与双酚AF）的AI辅助资料</a></p></aside></article>']
    return '\n'.join(out)


def table_markdown(columns: list[str], rows: list[list[str]]) -> list[str]:
    return ['| '+' | '.join(columns)+' |', '| '+' | '.join('---' for _ in columns)+' |']+[
        '| '+' | '.join(s.replace('|', '\\|') for s in row)+' |' for row in rows]


def render_document(data: dict) -> str:
    out = ['# A01（全氟酮化学：六氟丙酮与双酚AF）｜'+data['title'], '', data['intro'], '']
    for item in data['contributions']:
        out += ['## '+item['title'], '', item['text'], '',
                '出处：'+ '、'.join(item['source_ids'])+'；['+item['locator']+']('+item['url']+')。', '']
    out += ['## '+data['records_title'], '', data['records_note'], '']
    out += table_markdown(data['comparison']['columns'], data['comparison']['rows'])+['']
    out += [s+'\n' for s in data['data_notes']]
    out += ['## '+data['authorship_title'], '']
    out += table_markdown(['材料', '署名与贡献归属', '出处'], data['authorship'])+['']
    out += ['## 原文及资料出处', '', data['source_note'], '']
    out += ['- **'+s['id']+'** · ['+s['title']+']('+s['url']+')：'+s['locator']+'。' for s in data['sources']]
    out += ['', '## 平台整理的性质', '', data['platform_note'], '',
            '[A01历史成果专题](https://cccolab.github.io/Chen-Qingyun-AI4Science/topics/early-fluoroketones/index.html#'+ANCHOR+') · '
            '[平台AI研究资料](https://cccolab.github.io/Chen-Qingyun-AI4Science/research/index.html#ai-a01)', '']
    return '\n'.join(out)


def inspect_primary_reading(root: Path) -> dict:
    try:
        data = load(root)
        if (root / DOCUMENT).read_text('utf-8') != render_document(data):
            raise ValueError('A01 primary-reading document differs from its source')
        return {'status': 'passed', 'errors': [], 'scientific_review_status': 'review_required',
                'release_eligible': False, 'm0_status': 'paused',
                'source_sha256': hashlib.sha256((root / CONTENT).read_bytes()).hexdigest()}
    except (OSError, ValueError, KeyError, TypeError) as error:
        return {'status': 'failed', 'errors': [str(error)]}


def write(root: Path) -> None:
    data = load(root)
    (root / DOCUMENT).write_bytes(render_document(data).encode('utf-8'))
