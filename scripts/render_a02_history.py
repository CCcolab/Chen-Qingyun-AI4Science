"""Present sourced A02 historical work, with AI reading kept distinct."""
from __future__ import annotations

import argparse
from html import escape
import hashlib
import json
from pathlib import Path
import re

from public_line_labels import project_html, project_markdown
from render_ai_research import PageLinks, check_link

ROOT = Path(__file__).resolve().parents[1]
CONTENT = 'content/a02-academic-achievements.v1.json'
DOCUMENT = 'docs/A02_ACADEMIC_ACHIEVEMENTS_zh-CN.md'
ROUTE = 'topics/fluoromonomers/index.html'
PAGE = 'site/'+ROUTE
BEGIN = '<!-- A02_ACADEMIC_HISTORY:BEGIN -->'
END = '<!-- A02_ACADEMIC_HISTORY:END -->'
REPO = 'https://github.com/CCcolab/Chen-Qingyun-AI4Science/blob/main/'


def esc(value):
    return escape(str(value), quote=True)


def load(root: Path) -> dict:
    data = json.loads((root/CONTENT).read_bytes())
    if (data.get('achievement_line') != 'A02'
            or data.get('scientific_review_status') != 'review_required'
            or data.get('release_eligible') is not False or data.get('m0_status') != 'paused'
            or data.get('new_quantum_calls') != 0 or data.get('new_experiments') != 0):
        raise ValueError('A02 presentation must preserve source scope and paused research')
    if len(data['history_cards']) != 3 or len(data['cooperation']) != 2:
        raise ValueError('A02 requires three distinct historical objects and two cooperation records')
    sources = {s['id']: s for s in data['sources']}
    if len(sources) != len(data['sources']):
        raise ValueError('Duplicate A02 source identity')
    for row in data['history_cards']+data['cooperation']+[data['paper']]:
        if not row['source_refs'] or any(s not in sources for s in row['source_refs']):
            raise ValueError('Missing A02 source attribution')
    paper = data['paper']
    if (not re.fullmatch(r'[a-f0-9]{64}', paper['pdf_sha256'])
            or paper['authors'] != ['陈庆云','马振中','蒋锡夔','张元发','贾世茂']
            or paper['pages'] != '175–184' or not paper['observations']):
        raise ValueError('A02 paper must identify the acquired primary document and its authors')
    return data


def refs(ids: list[str], data: dict) -> str:
    return ' · '.join('<a href="#'+esc(next(s['anchor'] for s in data['sources'] if s['id']==ident))+'">'+esc(ident)+'</a>' for ident in ids)


def listing(rows):
    return '<ul>'+''.join('<li>'+esc(row)+'</li>' for row in rows)+'</ul>'


def render_block(data: dict) -> str:
    cards = data['history_cards']
    out = [BEGIN, '<style id="a02-academic-css">header h1{text-wrap:balance}#a02-paper-table{overflow-x:auto;max-width:100%}#a02-paper-table table{border-collapse:collapse;min-width:650px;width:100%;font-size:.9rem}#a02-paper-table th,#a02-paper-table td{border:1px solid var(--line);padding:12px;text-align:left;vertical-align:top}#a02-paper-table th{background:#edf3ee}.a02-meaning{border-left:3px solid #aa7545;padding:8px 16px;background:#f7f4eb}.a02-locator{font-size:.88rem;color:var(--muted)}#a02-primary-sources{overflow-wrap:anywhere}</style>',
           '<article id="topic-fluoromonomers" data-topic-slug="fluoromonomers" data-topic-type="dossier"><span class="status">A02 · 原始学术成果与合作</span><h2>'+esc(data['title'])+'</h2><p>'+esc(data['intro'])+'</p>',
           '<nav aria-label="A02专题导航"><a href="#a02-monomers">单体与分离</a> · <a href="#a02-materials">氟橡胶与团队</a> · <a href="#record-fluorinated-oils">氟油</a> · <a href="#a02-vdf-1980">1980年原刊</a> · <a href="#a02-cooperation">合作故事</a> · <a href="#refs">来源与待核事项</a></nav>']
    for card in cards[:2]:
        out += ['<section id="'+esc(card['id'])+'"><h3>'+esc(card['title'])+'</h3><p>'+esc(card['text'])+'</p><p class="a02-meaning"><b>学术意义：</b>'+esc(card['meaning'])+'</p><p class="a02-locator">'+esc(card['locator'])+' · '+refs(card['source_refs'], data)+'</p></section>']
    out += ['<p><a href="../../research/index.html#ai-a02">AI辅助资料整理与研究 →</a> · <a href="'+REPO+DOCUMENT+'">完整学术贡献与证据说明 →</a></p></article>']
    card = cards[2]
    out += ['<article id="record-fluorinated-oils"><span class="status">A02 · 氟油研究</span><h2>'+esc(card['title'])+'</h2><p>'+esc(card['text'])+'</p><p class="a02-meaning"><b>学术意义：</b>'+esc(card['meaning'])+'</p><p class="a02-locator">'+esc(card['locator'])+' · '+refs(card['source_refs'],data)+'</p>'+listing(card['limits'])+'</article>']
    paper = data['paper']
    out += ['<article id="a02-vdf-1980"><span class="status">原始论文 · AI辅助核读</span><h2>'+esc(paper['title'])+'</h2><p><b>原作者：</b>'+esc('、'.join(paper['authors']))+'；'+esc(paper['citation'])+'。</p><p>'+esc(paper['question'])+'</p><p><b>核读范围：</b>'+esc(paper['reading_scope'])+'</p>',
            '<p id="a02-table-caption"><b>原文观察、鉴定依据及其范围</b>（宽表可横向滑动）</p><div id="a02-paper-table" role="region" tabindex="0" aria-labelledby="a02-table-caption"><table><thead><tr><th scope="col">研究对象／比较</th><th scope="col">原文结果与证据</th><th scope="col">原刊定位</th></tr></thead><tbody>']
    for observation in paper['observations']:
        out += ['<tr><th scope="row">'+esc(observation['object'])+'</th><td>'+esc(observation['finding'])+'</td><td>'+esc(observation['locator'])+'</td></tr>']
    out += ['</tbody></table></div><p class="a02-meaning"><b>科学意义：</b>'+esc(paper['meaning'])+'</p>'+listing(paper['limits']),
            '<p><a href="'+esc(paper['url'])+'">官方论文入口 →</a> · <a href="'+esc(paper['pdf_url'])+'">期刊原文PDF →</a></p><p class="a02-locator">'+refs(paper['source_refs'],data)+'</p></article>',
            '<article id="a02-cooperation"><span class="status">合作与研究接续</span><h2>共同攻关怎样支持学术成果</h2>']
    for story in data['cooperation']:
        out += ['<h3>'+esc(story['title'])+'</h3><p>'+esc(story['text'])+'</p><p class="a02-locator">'+esc(story['locator'])+' · '+refs(story['source_refs'],data)+'</p>']
    out += ['</article><article id="refs"><span class="status">来源与证据范围</span><h2 id="a02-primary-sources">原始来源及资料性质</h2><ul>']
    for source in data['sources']:
        title = '<a href="'+esc(source['url'])+'">'+esc(source['title'])+'</a>' if source['url'] else esc(source['title'])
        out += ['<li id="'+esc(source['anchor'])+'"><b>'+esc(source['id'])+'</b> · '+title+'；'+esc(source['kind'])+'。'+esc(source['locator'])+'</li>']
    out += ['</ul><h3>待核事项</h3>'+listing(data['pending']), '<h3>AI辅助工作的范围</h3><p>'+esc(data['ai_scope'])+'</p><p><a href="../../research/index.html#ai-a02">已完成的资料整理与未来问题 →</a></p><p><a href="../index.html">返回专题索引 ↑</a></p></article>',END]
    return project_html('\n'.join(out), ROUTE)


def render_document(data: dict) -> str:
    out = ['# A02（含氟单体、氟橡胶与氟油）', '', data['title'], '', data['intro'], '']
    for card in data['history_cards']:
        out += ['## '+card['title'],'',card['text'],'','**学术意义：**'+card['meaning'],'','出处：'+card['locator']+'；'+'、'.join(card['source_refs'])+'。','']
        out += ['- '+s for s in card.get('limits',[])]+['']
    p = data['paper']
    out += ['## 1980年偏氟乙烯调聚原刊','',p['title'],'','原作者：'+'、'.join(p['authors'])+'；'+p['citation']+'。','',p['question'],'','核读范围：'+p['reading_scope'],'',
            '| 研究对象／比较 | 原文结果与证据 | 原刊定位 |','|---|---|---|']
    out += ['| '+o['object']+' | '+o['finding']+' | '+o['locator']+' |' for o in p['observations']]
    out += ['','**科学意义：**'+p['meaning'],'']+['- '+s for s in p['limits']]+['','[官方论文入口]('+p['url']+') · [原刊PDF]('+p['pdf_url']+')','','已取得PDF的SHA-256：`'+p['pdf_sha256']+'`。原文PDF留本机，网页不分发全文；AI核读不代替专业结构签认。','']
    out += ['## 合作与研究接续','']
    for s in data['cooperation']:
        out += ['### '+s['title'],'',s['text'],'','出处：'+s['locator']+'；'+'、'.join(s['source_refs'])+'。','']
    out += ['## 待核事项','']+['- '+s for s in data['pending']]+['','## AI辅助工作的范围','',data['ai_scope'],'','## 来源与原文定位','']
    for s in data['sources']:
        title = '['+s['title']+']('+s['url']+')' if s['url'] else s['title']
        out += ['- **'+s['id']+'**：'+title+'。'+s['kind']+'；'+s['locator']+'。']
    return project_markdown('\n'.join(out)+'\n')


def target_page(root: Path, data: dict) -> str:
    s = (root/PAGE).read_text('utf-8')
    block = render_block(data)
    if BEGIN in s:
        pattern = re.escape(BEGIN)+r'.*?'+re.escape(END)
        s, count = re.subn(pattern,lambda _:block,s,flags=re.S)
        if count != 1:
            raise ValueError('Duplicate A02 marker')
    else:
        start=s.index('<article id="topic-fluoromonomers"');end=s.index('<!-- HERITAGE_CONTEXT_BEGIN -->',start)
        s=s[:start]+block+'\n'+s[end:]
    s = s.replace('<title>专题｜六氟丙烯等含氟单体</title>','<title>专题｜含氟单体、氟橡胶与氟油</title>')
    s = s.replace('<h1>六氟丙烯等含氟单体</h1>','<h1>含氟单体、氟橡胶与氟油</h1>')
    s = s.replace('有机氟化学研究与传承 / 审阅预览','有机氟化学研究与传承 / 学术成果')
    return s


def inspect_a02_history(root: Path=ROOT) -> dict:
    report={'status':'failed','errors':[],'scientific_review_status':'review_required','release_eligible':False,'M0_resumed':False,'network_calls':0,'new_quantum_calls':0}
    try:
        data=load(root);expected=target_page(root,data)
        if (root/PAGE).read_bytes()!=expected.encode('utf-8') or (root/DOCUMENT).read_text('utf-8')!=render_document(data):
            raise ValueError('A02 page or document differs from its source-derived rendering')
        page=PageLinks(expected)
        if any(v!=1 for v in page.ids.values()) or page.json_payloads:
            raise ValueError('A02 cannot duplicate identities or add embedded source JSON')
        for ident in ['topic-fluoromonomers','record-fluorinated-oils','refs','ref-r28','ref-s1','a02-vdf-1980']:
            if page.ids[ident]!=1:raise ValueError('A02 lost a source or topic identity: '+ident)
        for url in page.links:check_link(root,PAGE,url,{PAGE:expected})
        report.update(status='passed',source_sha256=hashlib.sha256((root/CONTENT).read_bytes()).hexdigest(),history_cards=3,cooperation_stories=2,primary_observations=len(data['paper']['observations']),original_pdf_redistributed=False)
    except (OSError,ValueError,KeyError,TypeError) as error:report['errors'].append(str(error))
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--write',action='store_true');args=parser.parse_args()
    if args.write:
        d=load(ROOT);s=target_page(ROOT,d);(ROOT/PAGE).write_bytes(s.encode('utf-8'));(ROOT/DOCUMENT).write_text(render_document(d),'utf-8',newline='\n')
    report=inspect_a02_history(ROOT);print(json.dumps(report,ensure_ascii=False));return 0 if report['status']=='passed' else 1


if __name__=='__main__':raise SystemExit(main())
