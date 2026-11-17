"""Render A07 historical contributions and cooperation from the biography."""
from __future__ import annotations
import argparse
from html import escape
import json
from pathlib import Path
import re

from public_line_labels import project_html, project_markdown

CONTENT = 'content/a07-biography-narrative.v1.json'
DOCUMENT = 'docs/A07_ACADEMIC_ACHIEVEMENTS_zh-CN.md'
PAGE = 'site/topics/single-electron-transfer/index.html'
ROUTE = 'topics/single-electron-transfer/index.html'
BEGIN = '<!-- A07_BIOGRAPHY_HISTORY:BEGIN -->'
END = '<!-- A07_BIOGRAPHY_HISTORY:END -->'
CONTEXT_BEGIN = '<!-- HERITAGE_CONTEXT_BEGIN -->'
CONTEXT_END = '<!-- HERITAGE_CONTEXT_END -->'
SOURCE_IDS = {'HERITAGE-S01', 'A07-ACTA1984-906', 'A07-ACTA1986-265', 'CQ-R04', 'CQ-R06', 'HERITAGE-S07', 'HERITAGE-S06'}


def load(root: Path) -> dict:
    d = json.loads((root/CONTENT).read_bytes())
    if (d.get('schema_version'), d.get('achievement_line'), d.get('scientific_review_status'),
            d.get('release_eligible'), d.get('m0_status')) != ('1.0', 'A07', 'review_required', False, 'paused'):
        raise ValueError('A07 historical and platform scopes must remain separate')
    if [c['id'] for c in d['cards']] != ['topic-single-electron-transfer', 'a07-solvent-discovery',
                                       'a07-set-synthesis', 'record-ccl-activation']:
        raise ValueError('A07 requires historical methods, discovery, specific synthesis and C-Cl studies')
    if {s['id'] for s in d['sources']} != SOURCE_IDS or len(d['sources']) != len(SOURCE_IDS):
        raise ValueError('Unexpected A07 source identity')
    if any(not set(c['source_ids']) <= SOURCE_IDS for c in d['cards']):
        raise ValueError('Missing A07 attribution')
    if any(len(row) != 3 for row in d['roles']+d['timeline']+d['authorship_rows']+d['scope_rows']):
        raise ValueError('Incomplete A07 historical table')
    if re.search(r'private-sources|原始证据待核清单|现阶段待查事项统计|file://|(?<![A-Za-z])[A-Za-z]:[\\/]', json.dumps(d, ensure_ascii=False)):
        raise ValueError('Private A07 worklists cannot enter public history')
    return d


def refs(d: dict, ids: list[str]) -> str:
    return ' · '.join('<a href="#'+next(s['anchor'] for s in d['sources'] if s['id'] == ident)+'">'+escape(ident)+'</a>' for ident in ids)


def table(caption: str, columns: list[str], rows: list[list[str]], ident: str) -> str:
    return ('<div class="a07-table" role="region" tabindex="0" aria-labelledby="'+ident+'"><table><caption id="'+ident+'">'+escape(caption)+'</caption><thead><tr>'
            +''.join('<th scope="col">'+escape(s)+'</th>' for s in columns)+'</tr></thead><tbody>'
            +''.join('<tr><th scope="row">'+escape(row[0])+'</th>'+''.join('<td>'+escape(s)+'</td>' for s in row[1:])+'</tr>' for row in rows)
            +'</tbody></table></div>')


def render_block(root: Path) -> str:
    d = load(root)
    css = '.a07-meaning{border-left:3px solid #aa7545;padding:10px 16px;background:#f7f4eb}.a07-locator{font-size:.86rem;color:var(--muted)}.a07-nav{display:flex;flex-wrap:wrap;gap:8px 18px}.a07-table{overflow-x:auto;max-width:100%;margin:20px 0;border:1px solid var(--line)}.a07-table table{border-collapse:collapse;min-width:640px;width:100%;font-size:.92rem}.a07-table caption{text-align:left;padding:14px;background:#edf3ee;color:var(--accent);font-weight:700}.a07-table th,.a07-table td{border-top:1px solid var(--line);padding:12px;text-align:left;vertical-align:top}.a07-table:focus-visible{outline:3px solid #aa7545}#refs{overflow-wrap:anywhere}'
    out = [BEGIN, '<style id="heritage-context-style">'+css+'</style>']
    for c in d['cards']:
        out += ['<article id="'+c['id']+'"'+(' data-topic-slug="single-electron-transfer" data-topic-type="topic"' if c['id']=='topic-single-electron-transfer' else '')+'><span class="status">历史成果与合作</span><h2>'+escape(c['title'])+'</h2>']
        if c['id'] == 'topic-single-electron-transfer':
            out += ['<p>'+escape(d['intro'])+'</p><nav class="a07-nav" aria-label="A07专题导航"><a href="#record-ccl-activation">C–Cl活化</a><a href="#a07-solvent-discovery">换溶剂的发现</a><a href="#heritage-context">合作分工</a><a href="#a07-ai-collation">AI资料整理</a><a href="#refs">参考资料</a></nav>']
        out += ['<p>'+escape(s)+'</p>' for s in c['paragraphs']]
        out += ['<p class="a07-meaning"><b>学术与应用意义：</b>'+escape(c['meaning'])+'</p><p class="a07-locator">'+escape(c['locator'])+' · '+refs(d,c['source_ids'])+'</p></article>']
    out += ['<article id="a07-chronology"><h2>从溶剂效应到方法拓展</h2>',
            table('传记与原刊中的研究历程', ['时间', '工作与记录', '出处'], d['timeline'], 'a07-chronology-caption'),
            '<p>'+escape(d['timeline_scope'])+'</p></article>',
            '<article id="heritage-context"><h2>合作分工：研究思路与方法发展</h2><p>'+escape(d['cooperation_intro'])+'</p>',
            table('按传记明确记载介绍合作角色', ['人物或单位', '具体贡献与角色', '出处'], d['roles'], 'a07-cooperation-caption'),
            '<section id="a07-authorship"><h3>原论文与技术文书中的署名</h3>',
            table('保留各份原文的贡献归属', ['文书', '原文署名', '介绍范围'], d['authorship_rows'], 'a07-authorship-caption'),
            '<p>'+escape(d['authorship_scope'])+'</p><p class="a07-locator">'+refs(d,['CQ-R06','HERITAGE-S07','HERITAGE-S06'])+'</p></section></article>',
            '<article id="a07-ai-collation"><h2>平台的AI辅助资料整理</h2><p>'+escape(d['platform_text'])+'</p><p><a href="../../research/index.html#ai-a07">A07（单电子转移与C–Cl活化）的AI研究资料 →</a></p></article>',
            '<article id="refs"><h2>参考资料</h2><ul>']
    for s in d['sources']:
        title = '<a href="'+escape(s['url'], quote=True)+'">'+escape(s['title'])+'</a>' if s['url'] else escape(s['title'])
        out += ['<li id="'+s['anchor']+'"><b>'+escape(s['id'])+'</b> · '+title+'；'+escape(s['locator'])+'</li>']
    out += ['</ul><details><summary>研究对象与解释范围</summary>',
            table('按各环节原有口径介绍', ['对象或数量', '所指内容', '适用范围'], d['scope_rows'], 'a07-scope-caption'),
            '</details><p><a href="../../achievements/index.html#line-a07">A07（单电子转移与C–Cl活化）成果线</a> · <a href="../index.html">返回专题索引 ↑</a></p></article>', END]
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
    out += ['## 从溶剂效应到方法拓展','']+md_table(['时间','工作与记录','出处'],d['timeline'])+[d['timeline_scope'],'']
    out += ['## 合作分工：研究思路与方法发展','',d['cooperation_intro'],'']+md_table(['人物或单位','具体贡献与角色','出处'],d['roles'])
    out += ['### 原论文与技术文书中的署名','']+md_table(['文书','原文署名','介绍范围'],d['authorship_rows'])+[d['authorship_scope'],'']
    out += ['## 平台的AI辅助资料整理','',d['platform_text'],'','[A07（单电子转移与C–Cl活化）专题](../site/topics/single-electron-transfer/index.html) · [AI研究资料](../site/research/index.html#ai-a07)','','## 参考资料','']
    for s in d['sources']:
        title='['+s['title']+']('+s['url']+')' if s['url'] else s['title']
        out += ['- **'+s['id']+'** · '+title+'；'+s['locator']]
    out += ['','## 研究对象与解释范围','']+md_table(['对象或数量','所指内容','适用范围'],d['scope_rows'])
    return project_markdown('\n'.join(out))


def inspect_biography(root: Path) -> dict:
    errors=[]
    try:
        s=(root/PAGE).read_bytes().decode('utf-8');expected=render_block(root)
        context = CONTEXT_BEGIN+'\n'+expected+'\n'+CONTEXT_END
        if (s.count(BEGIN)!=1 or s.count(END)!=1 or s.count(CONTEXT_BEGIN)!=1
                or s.count(CONTEXT_END)!=1 or context not in s):
            errors.append('A07 history HTML differs from its source')
        if (root/DOCUMENT).read_bytes()!=render_document(root).encode('utf-8'):
            errors.append('A07 history document differs from its source')
    except (ValueError,KeyError,OSError) as e:errors.append(str(e))
    return {'status':'failed' if errors else 'passed','errors':errors}


def write(root: Path) -> None:
    path=root/PAGE;s=path.read_bytes().decode('utf-8')
    a='<main class="wrap">';b='</main>'
    if s.count(a)!=1 or s.count(b)!=1:raise ValueError('A07 requires one bounded main region')
    start=s.index(a)+len(a);end=s.index(b,start)
    context = CONTEXT_BEGIN+'\n'+render_block(root)+'\n'+CONTEXT_END
    path.write_bytes((s[:start]+context+s[end:]).encode('utf-8'))
    (root/DOCUMENT).write_bytes(render_document(root).encode('utf-8'))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');args=p.parse_args();root=Path(__file__).resolve().parents[1]
    if args.write:write(root)
    result=inspect_biography(root);print(json.dumps(result,ensure_ascii=False,indent=2));raise SystemExit(bool(result['errors']))
