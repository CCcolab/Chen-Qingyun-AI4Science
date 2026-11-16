"""Render the biography-led A04 history without local acquisition worklists."""
from __future__ import annotations
import argparse
from html import escape
import json
from pathlib import Path
import re

from public_line_labels import project_html, project_markdown

CONTENT = 'content/a04-biography-narrative.v1.json'
DOCUMENT = 'docs/A04_ACADEMIC_ACHIEVEMENTS_zh-CN.md'
PAGE = 'site/topics/f53/index.html'
ROUTE = 'topics/f53/index.html'
BEGIN = '<!-- A04_BIOGRAPHY_HISTORY:BEGIN -->'
END = '<!-- A04_BIOGRAPHY_HISTORY:END -->'
SOURCE_IDS = {'HERITAGE-S01', 'CQ-H03', 'CQ-H04', 'CQ-H05', 'CQ-H15', 'CQ-R04', 'S1', 'CQ-R12'}


def load(root: Path) -> dict:
    d = json.loads((root/CONTENT).read_bytes())
    if (d.get('schema_version'), d.get('achievement_line'), d.get('scientific_review_status'),
            d.get('release_eligible'), d.get('m0_status')) != ('1.0', 'A04', 'review_required', False, 'paused'):
        raise ValueError('A04 historical and platform scopes must remain separate')
    if [c['id'] for c in d['cards']] != ['topic-f53', 'record-industrial-application', 'a04-research-continuity']:
        raise ValueError('A04 requires development, application and scientific continuity')
    if {s['id'] for s in d['sources']} != SOURCE_IDS:
        raise ValueError('Unexpected A04 source identity')
    if any(not set(c['source_ids']) <= SOURCE_IDS for c in d['cards']):
        raise ValueError('Missing A04 attribution')
    if any(len(row) != 3 for row in d['roles']+d['timeline']+d['clip_rows']):
        raise ValueError('Incomplete A04 historical table')
    if re.search(r'private-sources|原始证据待核清单|现阶段待查事项统计|file://|(?<![A-Za-z])[A-Za-z]:[\\/]', json.dumps(d, ensure_ascii=False)):
        raise ValueError('Private A04 worklists cannot enter public history')
    return d


def refs(d: dict, ids: list[str]) -> str:
    return ' · '.join('<a href="#'+next(s['anchor'] for s in d['sources'] if s['id'] == ident)+'">'+escape(ident)+'</a>' for ident in ids)


def table(caption: str, columns: list[str], rows: list[list[str]], ident: str) -> str:
    return ('<div class="a04-table" role="region" tabindex="0" aria-labelledby="'+ident+'"><table><caption id="'+ident+'">'+escape(caption)+'</caption><thead><tr>'
            +''.join('<th scope="col">'+escape(s)+'</th>' for s in columns)+'</tr></thead><tbody>'
            +''.join('<tr><th scope="row">'+escape(row[0])+'</th>'+''.join('<td>'+escape(s)+'</td>' for s in row[1:])+'</tr>' for row in rows)
            +'</tbody></table></div>')


def render_block(root: Path) -> str:
    d = load(root)
    css = '.a04-meaning{border-left:3px solid #aa7545;padding:10px 16px;background:#f7f4eb}.a04-locator{font-size:.86rem;color:var(--muted)}.a04-nav{display:flex;flex-wrap:wrap;gap:8px 18px}.a04-table{overflow-x:auto;max-width:100%;margin:20px 0;border:1px solid var(--line)}.a04-table table{border-collapse:collapse;min-width:640px;width:100%;font-size:.92rem}.a04-table caption{text-align:left;padding:14px;background:#edf3ee;color:var(--accent);font-weight:700}.a04-table th,.a04-table td{border-top:1px solid var(--line);padding:12px;text-align:left;vertical-align:top}.a04-table:focus-visible{outline:3px solid #aa7545}#refs{overflow-wrap:anywhere}'
    out = [BEGIN, '<style id="a04-biography-css">'+css+'</style>']
    for c in d['cards']:
        out += ['<article id="'+c['id']+'"'+(' data-topic-slug="f53" data-topic-type="topic"' if c['id']=='topic-f53' else '')+'><span class="status">历史成果与合作</span><h2>'+escape(c['title'])+'</h2>']
        if c['id'] == 'topic-f53':
            out += ['<p>'+escape(d['intro'])+'</p><nav class="a04-nav" aria-label="A04专题导航"><a href="#record-industrial-application">工业应用</a><a href="#a04-cooperation">合作分工</a><a href="#a04-research-continuity">基础研究</a><a href="#a04-ai-collation">AI资料整理</a><a href="#refs">参考资料</a></nav>']
        out += ['<p>'+escape(s)+'</p>' for s in c['paragraphs']]
        out += ['<p class="a04-meaning"><b>学术与应用意义：</b>'+escape(c['meaning'])+'</p><p class="a04-locator">'+escape(c['locator'])+' · '+refs(d,c['source_ids'])+'</p>']
        if c['id'] == 'record-industrial-application':
            out += [table('从研制到应用的历史记录', ['时间', '工作与记录', '出处'], d['timeline'], 'a04-timeline-caption'),
                    '<section id="a04-1982-report"><h3>'+escape(d['clip_title'])+'</h3><p>'+escape(d['clip_intro'])+'</p>',
                    table('1982年剪报所载数字：按原报口径展示', ['指标', '原报道记载', '解释范围'], d['clip_rows'], 'a04-clip-caption'),
                    '<p>'+escape(d['clip_scope'])+'</p><p class="a04-locator">'+refs(d,['CQ-H03'])+'</p></section>']
        out += ['</article>']
    out += ['<article id="a04-cooperation"><h2>合作分工：研究组、工程人员与工厂</h2><p>'+escape(d['cooperation_intro'])+'</p>',
            table('按传记、署名与致谢分别介绍角色', ['人物或单位', '具体贡献与角色', '出处'], d['roles'], 'a04-cooperation-caption'),
            '<p>'+escape(d['award_text'])+'</p></article>',
            '<article id="a04-ai-collation"><h2>平台的AI辅助资料整理</h2><p>'+escape(d['platform_text'])+'</p><p><a href="../../research/index.html#ai-a04">A04（F-53铬雾抑制剂）的AI研究资料 →</a></p></article>',
            '<article id="refs"><h2>参考资料</h2><ul>']
    for s in d['sources']:
        title = '<a href="'+escape(s['url'], quote=True)+'">'+escape(s['title'])+'</a>' if s['url'] else escape(s['title'])
        out += ['<li id="'+s['anchor']+'"><b>'+escape(s['id'])+'</b> · '+title+'；'+escape(s['locator'])+'</li>']
    out += ['</ul><details><summary>产品名称与化学对象的范围</summary>',
            table('保留原来源所指对象', ['来源', '所指化合物', '使用范围'], d['identity_rows'], 'a04-identity-caption'),
            '<p>'+escape(d['identity_scope'])+'</p></details><p><a href="../../achievements/index.html#line-a04">A04（F-53铬雾抑制剂）成果线</a> · <a href="../index.html">返回专题索引 ↑</a></p></article>', END]
    return project_html('\n'.join(out), ROUTE)


def render_document(root: Path) -> str:
    d = load(root)
    out = ['# '+d['title'], '', d['intro'], '']
    def md_table(columns, rows):
        return ['| '+' | '.join(columns)+' |','| '+' | '.join('---' for _ in columns)+' |']+['| '+' | '.join(v.replace('|','\\|') for v in row)+' |' for row in rows]+['']
    for c in d['cards']:
        out += ['## '+c['title'],'']
        for p in c['paragraphs']:out += [p,'']
        out += ['**学术与应用意义：**'+c['meaning'],'',c['locator']+' · '+'、'.join(c['source_ids']),'']
        if c['id']=='record-industrial-application':
            out += md_table(['时间','工作与记录','出处'],d['timeline'])
            out += ['### '+d['clip_title'],'',d['clip_intro'],'']+md_table(['指标','原报道记载','解释范围'],d['clip_rows'])+[d['clip_scope'],'']
    out += ['## 合作分工：研究组、工程人员与工厂','',d['cooperation_intro'],'']+md_table(['人物或单位','具体贡献与角色','出处'],d['roles'])
    out += [d['award_text'],'','## 平台的AI辅助资料整理','',d['platform_text'],'','[A04（F-53铬雾抑制剂）专题](../site/topics/f53/index.html) · [AI研究资料](../site/research/index.html#ai-a04)','','## 参考资料','']
    for s in d['sources']:
        title='['+s['title']+']('+s['url']+')' if s['url'] else s['title']
        out += ['- **'+s['id']+'** · '+title+'；'+s['locator']]
    out += ['','## 产品名称与化学对象的范围','']+md_table(['来源','所指化合物','使用范围'],d['identity_rows'])+[d['identity_scope'],'']
    return project_markdown('\n'.join(out))


def inspect_biography(root: Path) -> dict:
    errors=[]
    try:
        s=(root/PAGE).read_bytes().decode('utf-8');expected=render_block(root)
        if s.count(BEGIN)!=1 or s.count(END)!=1 or expected not in s:
            errors.append('A04 history HTML differs from its source')
        if (root/DOCUMENT).read_bytes()!=render_document(root).encode('utf-8'):
            errors.append('A04 history document differs from its source')
    except (ValueError,KeyError,OSError) as e:errors.append(str(e))
    return {'status':'failed' if errors else 'passed','errors':errors}


def write(root: Path) -> None:
    path=root/PAGE;s=path.read_bytes().decode('utf-8')
    a='<main class="wrap">';b='</main>'
    if s.count(a)!=1 or s.count(b)!=1:raise ValueError('A04 requires one bounded main region')
    start=s.index(a)+len(a);end=s.index(b,start)
    path.write_bytes((s[:start]+render_block(root)+s[end:]).encode('utf-8'))
    (root/DOCUMENT).write_bytes(render_document(root).encode('utf-8'))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');args=p.parse_args();root=Path(__file__).resolve().parents[1]
    if args.write:write(root)
    result=inspect_biography(root);print(json.dumps(result,ensure_ascii=False,indent=2));raise SystemExit(bool(result['errors']))
