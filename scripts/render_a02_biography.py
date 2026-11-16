"""Render A02 around the biography's academic narrative, without local worklists."""
from __future__ import annotations

import hashlib
from html import escape
import json
from pathlib import Path
import re

from public_line_labels import project_html, project_markdown
from render_ai_research import PageLinks, check_link

CONTENT = 'content/a02-biography-narrative.v1.json'
HISTORICAL_SOURCE = 'content/a02-academic-achievements.v1.json'
DOCUMENT = 'docs/A02_ACADEMIC_ACHIEVEMENTS_zh-CN.md'
PAGE = 'site/topics/fluoromonomers/index.html'
ROUTE = 'topics/fluoromonomers/index.html'
BEGIN = '<!-- A02_ACADEMIC_HISTORY:BEGIN -->'
END = '<!-- A02_ACADEMIC_HISTORY:END -->'
SOURCE_IDS = {'HERITAGE-S01', 'CQ-R28', 'HERITAGE-S04', 'A02-P1980'}
LEGACY_IDS = ('a02-academic-css', 'topic-fluoromonomers', 'a02-monomers', 'a02-materials',
    'record-fluorinated-oils', 'a02-team-records', 'a02-team-hfp', 'a02-team-hfp-table-1',
    'a02-team-hfp-table-2', 'a02-team-rubber', 'a02-team-rubber-table-1', 'a02-team-oil',
    'a02-team-oil-table-1', 'a02-vdf-1980', 'a02-table-caption', 'a02-paper-table',
    'a02-cooperation', 'a02-source-trace', 'a02-trace-interview', 'a02-trace-interview-table-1',
    'a02-trace-book2009', 'a02-trace-book2009-table-1', 'a02-context-background',
    'a02-technical-records', 'a02-technical-hfp', 'a02-technical-hfp-table-1',
    'a02-technical-rubber', 'a02-technical-rubber-table-1', 'a02-technical-oil',
    'a02-technical-oil-table-1', 'a02-technical-oil-table-2', 'refs', 'a02-primary-sources',
    'a02-source-book', 'ref-r28', 'ref-s1', 'a02-source-cas', 'a02-source-paper',
    'a02-source-hfp1963', 'a02-source-fj23', 'a02-source-fj23-old', 'a02-source-fl1986',
    'a02-source-mmcs2025', 'a02-source-ic-history', 'a02-source-jiang-recollection',
    'a02-source-catalog', 'a02-source-gale', 'a02-source-mmcs-project', 'a02-source-mmcs-search',
    'a02-source-mmcs-video', 'a02-source-las-yearbook', 'a02-source-ihns-database',
    'a02-source-easl-catalog', 'a02-source-nlc2009', 'a02-source-report2019', 'a02-source-nlc2009-extent')


def load(root: Path) -> dict:
    data = json.loads((root / CONTENT).read_bytes())
    if (data.get('schema_version') != '1.0' or data.get('achievement_line') != 'A02'
            or data.get('scientific_review_status') != 'review_required'
            or data.get('release_eligible') is not False or data.get('m0_status') != 'paused'):
        raise ValueError('A02 biography presentation must preserve its review and research scope')
    if [r['id'] for r in data['cards']] != ['a02-monomers', 'a02-materials', 'record-fluorinated-oils']:
        raise ValueError('A02 requires three distinct historical objects')
    if {s['id'] for s in data['sources']} != SOURCE_IDS:
        raise ValueError('A02 must retain its bounded source attribution')
    for card in data['cards']:
        if not set(card['source_ids']) <= SOURCE_IDS or not card['paragraphs']:
            raise ValueError('Missing historical attribution in A02 narrative')
    if any(len(row) != 3 for row in data['roles']):
        raise ValueError('Incomplete cooperation table')
    raw = json.dumps(data, ensure_ascii=False)
    if re.search(r'private-sources|current-item-register|原始证据待核清单|现阶段待查事项统计|file://|(?<![A-Za-z])[A-Za-z]:[\\/]', raw):
        raise ValueError('Private A02 records cannot enter public narrative')
    # Reuse only the previously published, immutable paper identity and observations.
    data['paper'] = json.loads((root / HISTORICAL_SOURCE).read_bytes())['paper']
    return data


def refs(data: dict, ids: list[str]) -> str:
    return ' · '.join('<a href="#'+next(s['anchor'] for s in data['sources'] if s['id'] == ident)+'">'
                      +escape(ident)+'</a>' for ident in ids)


def table(caption: str, columns: list[str], rows: list[list[str]], ident: str) -> str:
    return ('<div class="a02-table" role="region" tabindex="0" aria-labelledby="'+ident+'"><table>'
            '<caption id="'+ident+'">'+escape(caption)+'</caption><thead><tr>'
            +''.join('<th scope="col">'+escape(s)+'</th>' for s in columns)+'</tr></thead><tbody>'
            +''.join('<tr><th scope="row">'+escape(row[0])+'</th>'
                     +''.join('<td>'+escape(s)+'</td>' for s in row[1:])+'</tr>' for row in rows)
            +'</tbody></table></div>')


def render_block(root: Path) -> str:
    data = load(root)
    live = {'a02-academic-css', 'topic-fluoromonomers', 'a02-monomers', 'a02-materials',
            'record-fluorinated-oils', 'a02-team-records', 'a02-cooperation', 'a02-vdf-1980',
            'a02-paper-table', 'a02-table-caption', 'refs', 'a02-primary-sources'}
    live.update(s['anchor'] for s in data['sources'])
    emitted = set(live)

    def aliases(names):
        result = []
        for ident in names:
            if ident not in emitted:
                if ident not in LEGACY_IDS:
                    raise ValueError('Unknown A02 citation alias')
                result.append('<span id="'+ident+'" aria-hidden="true"></span>')
                emitted.add(ident)
        return ''.join(result)

    css = ('#topic-fluoromonomers p{max-width:82ch}.a02-meaning{border-left:3px solid #aa7545;padding:8px 16px;background:#f7f4eb}'
           '.a02-locator{font-size:.88rem;color:var(--muted)}.a02-table{overflow-x:auto;max-width:100%;margin:20px 0;border:1px solid var(--line)}'
           '.a02-table table{border-collapse:collapse;min-width:650px;width:100%;font-size:.9rem}.a02-table caption{text-align:left;padding:14px;background:#edf3ee;color:var(--accent);font-weight:700}'
           '.a02-table th,.a02-table td{border-top:1px solid var(--line);padding:12px;text-align:left;vertical-align:top;overflow-wrap:anywhere}.a02-table thead{background:#f5f5ef}'
           '.a02-table:focus-visible{outline:3px solid #aa7545}#refs{overflow-wrap:anywhere}.a02-nav{display:flex;flex-wrap:wrap;gap:8px 18px}')
    out = [BEGIN, '<style id="a02-academic-css">'+css+'</style>',
           '<article id="topic-fluoromonomers" data-topic-slug="fluoromonomers" data-topic-type="dossier">'
           '<span class="status">A02 · 学术成果与合作</span><h2>'+escape(data['title'])+'</h2><p>'+escape(data['intro'])+'</p>',
           '<nav class="a02-nav" aria-label="A02专题导航"><a href="#a02-monomers">单体与分离</a>'
           '<a href="#a02-materials">氟橡胶</a><a href="#record-fluorinated-oils">氟油</a>'
           '<a href="#a02-team-records">合作分工</a><a href="#a02-vdf-1980">后续调聚研究</a><a href="#refs">参考资料</a></nav>']
    for card in data['cards'][:2]:
        prefix = 'a02-team-hfp' if card['id'] == 'a02-monomers' else 'a02-team-rubber'
        out += [aliases(i for i in LEGACY_IDS if i.startswith(prefix)), '<section id="'+card['id']+'"><h3>'+escape(card['title'])+'</h3>']
        out += ['<p>'+escape(s)+'</p>' for s in card['paragraphs']]
        out += ['<p class="a02-meaning"><b>学术意义：</b>'+escape(card['meaning'])+'</p>'
                '<p class="a02-locator">'+escape(card['locator'])+' · '+refs(data, card['source_ids'])+'</p></section>']
    out += ['</article>']
    card = data['cards'][2]
    out += ['<article id="record-fluorinated-oils">'+aliases(i for i in LEGACY_IDS if i.startswith('a02-team-oil'))
            +'<span class="status">A02 · 氟油研究</span><h2>'+escape(card['title'])+'</h2>']
    out += ['<p>'+escape(s)+'</p>' for s in card['paragraphs']]
    out += ['<p class="a02-meaning"><b>学术意义：</b>'+escape(card['meaning'])+'</p>'
            '<p class="a02-locator">'+escape(card['locator'])+' · '+refs(data, card['source_ids'])+'</p></article>',
            '<article id="a02-team-records"><h2>'+escape(data['cooperation_title'])+'</h2><p>'+escape(data['cooperation_intro'])+'</p>',
            table(data['cooperation_title'], ['人物与团队', '具体工作', '出处'], data['roles'], 'a02-collaboration-caption'),
            '<section id="a02-cooperation"><h3>'+escape(data['migration_title'])+'</h3><p>'+escape(data['migration_text'])+'</p>'
            '<p class="a02-locator">'+escape(data['migration_locator'])+' · '+refs(data,['HERITAGE-S01','HERITAGE-S04'])+'</p></section></article>']
    paper = data['paper']
    out += ['<article id="a02-vdf-1980"><span class="status">原作者的后续研究</span><h2>'+escape(data['paper_title'])+'</h2>'
            '<p>'+escape(data['paper_intro'])+'</p><p><b>原论文：</b>'+escape(paper['title']+'；'+paper['citation'])+'</p>',
            '<details><summary>原刊观察与转化</summary><div id="a02-paper-table">'
            +table('原文观察与转化', ['研究对象', '原文结果与证据', '原刊定位'],
                   [[o['object'], o['finding'], o['locator']] for o in paper['observations']], 'a02-table-caption')+'</div></details>',
            '<p>'+escape(data['paper_scope'])+'</p><p>'+refs(data,['A02-P1980'])+'</p></article>',
            '<article id="a02-ai-materials">'+aliases(i for i in LEGACY_IDS if i.startswith(('a02-source-trace','a02-trace-')))
            +'<h2>'+escape(data['platform_title'])+'</h2><p>'+escape(data['platform_text'])+'</p>'
            '<p><a href="../../research/index.html#ai-a02">A02（含氟单体、氟橡胶与氟油）的AI资料整理 →</a></p></article>',
            '<article id="refs"><h2 id="a02-primary-sources">参考资料</h2><ul>']
    for source in data['sources']:
        title = '<a href="'+escape(source['url'], quote=True)+'">'+escape(source['title'])+'</a>' if source['url'] else escape(source['title'])
        out += ['<li id="'+source['anchor']+'"><b>'+escape(source['id'])+'</b> · '+title+'；'+escape(source['locator'])+'</li>']
    out += ['</ul>', aliases(i for i in LEGACY_IDS if i not in emitted),
            '<p><a href="../../achievements/index.html#line-a02">A02（含氟单体、氟橡胶与氟油）成果线</a> · '
            '<a href="../index.html">返回专题索引 ↑</a></p></article>', END]
    return project_html('\n'.join(out), ROUTE)


def render_heritage_context(root: Path) -> str:
    load(root)
    return ('<style id="heritage-context-style">#heritage-context{margin:28px 0;padding:24px;border-top:1px solid var(--line)}'
            '#heritage-context nav{display:flex;flex-wrap:wrap;gap:10px 22px}</style>'
            '<section id="heritage-context"><h2>成果与学术传承</h2><nav aria-label="A02成果与传承">'
            '<a href="#a02-team-records">本专题的合作分工</a>'
            '<a href="../../achievements/index.html#heritage-story-st09">相关合作与育人故事</a>'
            '<a href="../../achievements/index.html#heritage-line-a02">A02（含氟单体、氟橡胶与氟油）成果资料</a>'
            '</nav></section>')


def md_table(columns, rows):
    return ['| '+' | '.join(columns)+' |', '| '+' | '.join('---' for _ in columns)+' |']+[
        '| '+' | '.join(s.replace('|','\\|') for s in row)+' |' for row in rows]


def render_document(data: dict) -> str:
    out = ['# A02（含氟单体、氟橡胶与氟油）', '', data['title'], '', data['intro'], '']
    for card in data['cards']:
        out += ['## '+card['title'], '']
        for paragraph in card['paragraphs']:
            out += [paragraph, '']
        out += ['**学术意义：**'+card['meaning'], '', '出处：'+card['locator']+'；'+'、'.join(card['source_ids'])+'。', '']
    out += ['## '+data['cooperation_title'], '', data['cooperation_intro'], '']
    out += md_table(['人物与团队','具体工作','出处'],data['roles'])+['']
    out += ['### '+data['migration_title'], '', data['migration_text'], '', '出处：'+data['migration_locator']+'。', '']
    p = data['paper']
    out += ['## '+data['paper_title'], '', data['paper_intro'], '', '**原论文：**'+p['title']+'；'+p['citation']+'。', '']
    out += md_table(['研究对象','原文结果与证据','原刊定位'],[[o['object'],o['finding'],o['locator']] for o in p['observations']])+['',data['paper_scope'],'']
    out += ['## '+data['platform_title'], '', data['platform_text'], '',
            '[A02（含氟单体、氟橡胶与氟油）AI资料整理](https://cccolab.github.io/Chen-Qingyun-AI4Science/research/index.html#ai-a02)', '', '## 参考资料', '']
    for source in data['sources']:
        title = '['+source['title']+']('+source['url']+')' if source['url'] else source['title']
        out += ['- **'+source['id']+'** · '+title+'；'+source['locator']+'。']
    return project_markdown('\n'.join(out)+'\n')


def inspect_biography(root: Path) -> dict:
    try:
        data = load(root)
        expected = render_block(root)
        actual = (root/PAGE).read_text('utf-8')
        blocks = re.findall(re.escape(BEGIN)+r'.*?'+re.escape(END),actual,re.S)
        if blocks != [expected] or (root/DOCUMENT).read_text('utf-8') != render_document(data):
            raise ValueError('A02 biography page/document differs from its source rendering')
        page = PageLinks(actual)
        if any(n != 1 for n in page.ids.values()) or page.json_payloads:
            raise ValueError('A02 biography cannot duplicate identities or embed original records')
        if any(page.ids[ident] != 1 for ident in LEGACY_IDS):
            raise ValueError('A02 biography lost a historical citation anchor')
        if re.search(r'待取得|原件缺口|馆藏|待核事项|待查清单|调阅|私有目录',expected):
            raise ValueError('Local tracking work must not appear in the public A02 narrative')
        context = '<!-- HERITAGE_CONTEXT_BEGIN -->\n'+project_html(render_heritage_context(root), ROUTE)+'\n<!-- HERITAGE_CONTEXT_END -->'
        if re.findall(r'<!-- HERITAGE_CONTEXT_BEGIN -->.*?<!-- HERITAGE_CONTEXT_END -->',actual,re.S) != [context]:
            raise ValueError('A02 inherited context must use its current academic navigation')
        for url in page.links:
            check_link(root,PAGE,url,{PAGE:actual})
        return {'status':'passed','errors':[],'scientific_review_status':'review_required','release_eligible':False,
                'M0_resumed':False,'new_quantum_calls':0,'source_sha256':hashlib.sha256((root/CONTENT).read_bytes()).hexdigest(),
                'three_historical_objects':True,'legacy_anchors_preserved':True,'public_tracking_worklists':False}
    except (OSError,ValueError,KeyError,TypeError) as error:
        return {'status':'failed','errors':[str(error)]}
