"""Present A03 historical achievements separately from platform collation."""
from __future__ import annotations

import argparse
from html import escape
import json
from pathlib import Path
import re

CONTENT = 'content/a03-biography-narrative.v1.json'
DOCUMENT = 'docs/A03_ACADEMIC_ACHIEVEMENTS_zh-CN.md'
PAGE = 'site/pftb/index.html'
BEGIN = '<!-- A03_BIOGRAPHY_HISTORY:BEGIN -->'
END = '<!-- A03_BIOGRAPHY_HISTORY:END -->'
ANCHOR = '<!-- ============ 原始贡献 ============ -->'


def load(root: Path) -> dict:
    data = json.loads((root / CONTENT).read_bytes())
    if (data.get('schema_version'), data.get('achievement_line'), data.get('scientific_review_status'),
            data.get('release_eligible'), data.get('m0_status')) != ('1.0', 'A03', 'review_required', False, 'paused'):
        raise ValueError('A03 scope or review identity changed')
    if len(data['cards']) != 3 or len(data['roles']) != 4:
        raise ValueError('Incomplete A03 historical presentation')
    ids = {s['id'] for s in data['sources']}
    if ids != {'HERITAGE-S01', 'PF01', 'HERITAGE-S04'}:
        raise ValueError('Unexpected A03 source scope')
    if any(not set(c['source_ids']) <= ids for c in data['cards']):
        raise ValueError('Unknown A03 citation')
    if re.search(r'private-sources|原始证据待核清单|现阶段待查事项统计|file://|(?<![A-Za-z])[A-Za-z]:[\\/]', json.dumps(data, ensure_ascii=False)):
        raise ValueError('Private local records cannot be published')
    return data


def render_block(root: Path) -> str:
    d = load(root)
    out = [BEGIN, '<style id="a03-biography-style">.a03-biography-card{margin:24px 0;padding:20px;border:1px solid var(--line);border-radius:8px}.a03-biography-meaning{border-left:3px solid #aa7545;padding-left:14px}.a03-biography-locator{font-size:.85rem;color:var(--muted)}.a03-biography-table{overflow-x:auto}.a03-biography-table table{border-collapse:collapse;min-width:620px;width:100%}.a03-biography-table th,.a03-biography-table td{padding:12px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line)}#a03-biography-history a{overflow-wrap:anywhere}</style>',
           '<section id="a03-biography-history"><div class="wrap"><div class="sec-head"><h2>'+escape(d['title'])+'</h2><p>历史成果与合作</p></div><p>'+escape(d['intro'])+'</p>']
    for i, c in enumerate(d['cards'], 1):
        refs = ' · '.join('<a href="#a03-biography-ref-'+escape(s, quote=True)+'">'+escape(s)+'</a>' for s in c['source_ids'])
        out += ['<article class="a03-biography-card" id="a03-biography-contribution-'+str(i)+'"><h3>'+escape(c['title'])+'</h3><p>'+escape(c['text'])+'</p><p class="a03-biography-meaning"><b>学术意义：</b>'+escape(c['meaning'])+'</p><p class="a03-biography-locator">'+escape(c['locator'])+' · '+refs+'</p></article>']
    out += ['<h3>共同研究：科学问题、实验与培养</h3><p>'+escape(d['cooperation_intro'])+'</p><div class="a03-biography-table" role="region" tabindex="0" aria-label="A03合作分工"><table><caption>传记与原论文所记合作</caption><thead><tr><th scope="col">人物</th><th scope="col">具体工作</th><th scope="col">出处</th></tr></thead><tbody>']
    for row in d['roles']:
        out += ['<tr><th scope="row">'+escape(row[0])+'</th>'+''.join('<td>'+escape(v)+'</td>' for v in row[1:])+'</tr>']
    out += ['</tbody></table></div><h3>平台的AI辅助整理</h3><p>'+escape(d['platform_text'])+'</p><p><a href="../research/index.html#ai-a03">A03 全氟叔丁基化学：AI整理与原表数值重放 →</a></p><details><summary>本段参考资料</summary><ul>']
    for s in d['sources']:
        title = '<a href="'+escape(s['url'], quote=True)+'">'+escape(s['title'])+'</a>' if s['url'] else escape(s['title'])
        out += ['<li id="a03-biography-ref-'+s['id']+'"><b>'+s['id']+'</b> · '+title+'；'+escape(s['locator'])+'</li>']
    out += ['</ul></details></div></section>', END]
    return '\n'.join(out)


def render_document(root: Path) -> str:
    d = load(root)
    rows = ['# '+d['title'], '', d['intro'], '']
    for c in d['cards']:
        rows += ['## '+c['title'], '', c['text'], '', '**学术意义：**'+c['meaning'], '', c['locator']+' · '+'、'.join(c['source_ids']), '']
    rows += ['## 共同研究：科学问题、实验与培养', '', d['cooperation_intro'], '', '| 人物 | 具体工作 | 出处 |', '| --- | --- | --- |']
    rows += ['| '+' | '.join(row)+' |' for row in d['roles']]
    rows += ['', '## 平台的AI辅助整理', '', d['platform_text'], '', '[A03 全氟叔丁基化学专题](../site/pftb/index.html) · [AI整理与原表数值重放](../site/research/index.html#ai-a03)', '', '## 参考资料', '']
    for s in d['sources']:
        title = '['+s['title']+']('+s['url']+')' if s['url'] else s['title']
        rows += ['- **'+s['id']+'** · '+title+'；'+s['locator']]
    return '\n'.join(rows)+'\n'


def inspect_biography(root: Path) -> dict:
    errors = []
    try:
        block = render_block(root)
        html = (root / PAGE).read_bytes().decode('utf-8')
        if html.count(BEGIN) != 1 or html.count(END) != 1 or block not in html:
            errors.append('A03 biography HTML differs from its source')
        if (root / DOCUMENT).read_bytes() != render_document(root).encode('utf-8'):
            errors.append('A03 biography document differs from its source')
    except (ValueError, KeyError, OSError) as exc:
        errors.append(str(exc))
    return {'status': 'failed' if errors else 'passed', 'errors': errors}


def write(root: Path) -> None:
    path = root / PAGE
    html = path.read_bytes().decode('utf-8')
    block = render_block(root)
    if BEGIN in html:
        html = re.sub(re.escape(BEGIN)+r'.*?'+re.escape(END), lambda _: block, html, flags=re.S)
    else:
        if html.count(ANCHOR) != 1:
            raise ValueError('Missing original PFtB insertion anchor')
        html = html.replace(ANCHOR, block+'\n\n'+ANCHOR, 1)
    path.write_bytes(html.encode('utf-8'))
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
