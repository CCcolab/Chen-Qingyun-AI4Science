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
    technical = data.get('technical_records', [])
    if [r['id'] for r in technical] != ['a02-technical-hfp','a02-technical-rubber','a02-technical-oil']:
        raise ValueError('A02 technical records must keep three independently attributed objects')
    team = data.get('team_records', [])
    if ([r['id'] for r in team] != ['a02-team-hfp','a02-team-rubber','a02-team-oil']
            or any(r.get('original_records_obtained') is not False for r in team)):
        raise ValueError('Team history must distinguish three objects with technical originals still pending')
    trace = data.get('source_trace', [])
    if ([r['id'] for r in trace] != ['a02-trace-interview','a02-trace-book2009']
            or any(r.get('original_obtained') is not False for r in trace)
            or trace[1].get('volume_confirmed') is not False):
        raise ValueError('Cited-source tracing must keep interview originals and book volume unresolved')
    for row in data['history_cards']+data['cooperation']+[data['paper']]+technical+team+trace:
        if not row['source_refs'] or any(s not in sources for s in row['source_refs']):
            raise ValueError('Missing A02 source attribution')
    for row in technical+team+trace:
        if row.get('original_pdf_obtained') and not re.fullmatch(r'[a-f0-9]{64}', row['pdf_sha256'] or ''):
            raise ValueError('Acquired technical original must have a document fingerprint')
        for table in row['tables']:
            if not table['columns'] or any(len(r)!=len(table['columns']) for r in table['rows']):
                raise ValueError('Technical property table has inconsistent columns')
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


def technical_html(data: dict, *, team=False) -> str:
    if team:
        out = ['<article id="a02-team-records"><span class="status">陈先生团队的研究贡献与合作</span><h2>单体制取、低温分离与材料接续</h2><p>依据传记与机构公开资料，呈现陈先生及合作者解决的具体问题。下列三项的同期技术原件仍未取得，已有叙述与待核原件分别标明；公开检索未取得原件，不表示档案不存在或历史成就不成立。</p>']
    else:
        out = ['<article id="a02-technical-records"><span class="status">技术与物性原始记录</span><h2>制取、材料与氟油：证据分别呈现</h2><p>以下资料按原作者与材料身份单列。他组同期方法、机构成果登记及相关材料实测各有用途；与陈先生团队历史工作的关联，须由原始档案逐项建立。</p>']
    for record in data['team_records' if team else 'technical_records']:
        out += ['<section id="'+esc(record['id'])+'"><h3>'+esc(record['title'])+'</h3><p class="a02-locator">'+esc(record['identity'])+'</p><p>'+esc(record['description'])+'</p>']
        for i, table in enumerate(record['tables']):
            caption=record['id']+'-table-'+str(i+1)
            out += ['<p id="'+caption+'"><b>'+esc(table['caption'])+'</b>（宽表可横向滑动）</p><div class="a02-technical-table" role="region" tabindex="0" aria-labelledby="'+caption+'"><table><thead><tr>'+''.join('<th scope="col">'+esc(v)+'</th>' for v in table['columns'])+'</tr></thead><tbody>']
            for row in table['rows']:
                out += ['<tr><th scope="row">'+esc(row[0])+'</th>'+''.join('<td>'+esc(v)+'</td>' for v in row[1:])+'</tr>']
            out += ['</tbody></table></div>'+listing(table['notes'])]
        out += ['<p><b>署名与合作：</b>'+esc(record['attribution'])+'</p><p class="a02-meaning"><b>学术意义与范围：</b>'+esc(record['meaning'])+'</p><h4>待核事项</h4>'+listing(record['pending']),'<p class="a02-locator">'+esc(record['reading_scope'])+' · '+refs(record['source_refs'],data)+'</p><p>'+' · '.join('<a href="'+esc(v['url'])+'">'+esc(v['title'])+'</a>' for v in record['links'])+'</p></section>']
    out += ['</article>']
    return '\n'.join(out)


def source_trace_html(data: dict) -> str:
    out = ['<article id="a02-source-trace"><span class="status">AI辅助资料整理 · 引据追踪</span><h2>本人访谈与所引书页：已核信息与原件缺口</h2><p>这一部分记录平台对传记引据的定位工作。原始访谈和目标书页尚未取得，以下目录信息不作为新增历史成果、工艺参数或材料性能证据。</p>']
    for record in data['source_trace']:
        out += ['<section id="'+esc(record['id'])+'"><h3>'+esc(record['title'])+'</h3><p class="a02-locator">'+esc(record['identity'])+'</p><p>'+esc(record['description'])+'</p>']
        for i, table in enumerate(record['tables']):
            caption=record['id']+'-table-'+str(i+1)
            out += ['<p id="'+caption+'"><b>'+esc(table['caption'])+'</b>（宽表可横向滑动）</p><div class="a02-technical-table" role="region" tabindex="0" aria-labelledby="'+caption+'"><table><thead><tr>'+''.join('<th scope="col">'+esc(v)+'</th>' for v in table['columns'])+'</tr></thead><tbody>']
            out += ['<tr><th scope="row">'+esc(row[0])+'</th>'+''.join('<td>'+esc(v)+'</td>' for v in row[1:])+'</tr>' for row in table['rows']]
            out += ['</tbody></table></div>'+listing(table['notes'])]
        out += ['<p class="a02-meaning"><b>证据范围：</b>'+esc(record['scope'])+'</p><h4>待取得的原件</h4>'+listing(record['pending']),'<p class="a02-locator">'+refs(record['source_refs'],data)+'</p><p>'+' · '.join('<a href="'+esc(v['url'])+'">'+esc(v['title'])+'</a>' for v in record['links'])+'</p></section>']
    return '\n'.join(out+['</article>'])


def render_block(data: dict) -> str:
    cards = data['history_cards']
    out = [BEGIN, '<style id="a02-academic-css">header h1{text-wrap:balance}#a02-paper-table{overflow-x:auto;max-width:100%}#a02-paper-table table{border-collapse:collapse;min-width:650px;width:100%;font-size:.9rem}#a02-paper-table th,#a02-paper-table td{border:1px solid var(--line);padding:12px;text-align:left;vertical-align:top}#a02-paper-table th{background:#edf3ee}.a02-meaning{border-left:3px solid #aa7545;padding:8px 16px;background:#f7f4eb}.a02-locator{font-size:.88rem;color:var(--muted)}#a02-primary-sources{overflow-wrap:anywhere}</style>',
           '<article id="topic-fluoromonomers" data-topic-slug="fluoromonomers" data-topic-type="dossier"><span class="status">A02 · 原始学术成果与合作</span><h2>'+esc(data['title'])+'</h2><p>'+esc(data['intro'])+'</p>',
           '<nav aria-label="A02专题导航"><a href="#a02-monomers">单体与分离</a> · <a href="#a02-materials">氟橡胶与团队</a> · <a href="#record-fluorinated-oils">氟油</a> · <a href="#a02-team-records">团队贡献与原件追查</a> · <a href="#a02-vdf-1980">1980年原刊</a> · <a href="#a02-cooperation">合作故事</a> · <a href="#a02-technical-records">相关技术背景</a> · <a href="#refs">来源与待核事项</a></nav>']
    out.insert(2, '<style>.a02-technical-table{overflow-x:auto;max-width:100%}.a02-technical-table table{border-collapse:collapse;min-width:650px;width:100%;font-size:.9rem}.a02-technical-table th,.a02-technical-table td{border:1px solid var(--line);padding:12px;text-align:left;vertical-align:top}.a02-technical-table th{background:#edf3ee}#a02-technical-records section+section{margin-top:36px;border-top:1px solid var(--line);padding-top:24px}</style>')
    out.insert(3, '<style>#a02-team-records section+section{margin-top:36px;border-top:1px solid var(--line);padding-top:24px}#a02-context-background>summary{cursor:pointer;padding:20px;font-weight:700;color:var(--teal);border:1px solid var(--line)}#a02-context-background{margin:24px 0}</style>')
    for card in cards[:2]:
        out += ['<section id="'+esc(card['id'])+'"><h3>'+esc(card['title'])+'</h3><p>'+esc(card['text'])+'</p><p class="a02-meaning"><b>学术意义：</b>'+esc(card['meaning'])+'</p><p class="a02-locator">'+esc(card['locator'])+' · '+refs(card['source_refs'], data)+'</p></section>']
    out += ['<p><a href="../../research/index.html#ai-a02">AI辅助资料整理与研究 →</a> · <a href="'+REPO+DOCUMENT+'">完整学术贡献与证据说明 →</a></p></article>']
    card = cards[2]
    out += ['<article id="record-fluorinated-oils"><span class="status">A02 · 氟油研究</span><h2>'+esc(card['title'])+'</h2><p>'+esc(card['text'])+'</p><p class="a02-meaning"><b>学术意义：</b>'+esc(card['meaning'])+'</p><p class="a02-locator">'+esc(card['locator'])+' · '+refs(card['source_refs'],data)+'</p>'+listing(card['limits'])+'</article>']
    out += [technical_html(data, team=True)]
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
    out += ['</article>',source_trace_html(data),'<details id="a02-context-background"><summary>同期他组与相关材料背景（与陈团队成果分别归属）</summary>',technical_html(data),'</details><article id="refs"><span class="status">来源与证据范围</span><h2 id="a02-primary-sources">原始来源及资料性质</h2><ul>']
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
    out += ['## 陈先生团队：具体贡献与原件追查','','依据传记与机构资料细化研究对象和合作分工；同期技术原件仍待取得，不以其他团队数据填补。公开检索未取得不表示原件不存在或原成就不成立。','']
    for record in data['team_records']:
        out += ['### '+record['title'],'',record['identity'],'',record['description'],'']
        for table in record['tables']:
            out += ['**'+table['caption']+'**','','| '+' | '.join(table['columns'])+' |','|'+'|'.join('---' for _ in table['columns'])+'|']
            out += ['| '+' | '.join(row)+' |' for row in table['rows']]
            out += ['']+['- '+s for s in table['notes']]+['']
        out += ['**署名与合作：**'+record['attribution'],'','**学术意义与范围：**'+record['meaning'],'','待取得原件：','']+['- '+s for s in record['pending']]+['','已核读范围：'+record['reading_scope'],'','出处：'+'、'.join(record['source_refs'])+'。','']
        out += ['['+v['title']+']('+v['url']+')' for v in record['links']]+['']
    out += ['## 同期他组与相关材料背景','','以下不作陈团队同期原始成果证据；原作者、材料身份和原报数据保留。','']
    for record in data['technical_records']:
        out += ['### '+record['title'],'',record['identity'],'',record['description'],'']
        for table in record['tables']:
            out += ['**'+table['caption']+'**','','| '+' | '.join(table['columns'])+' |','|'+'|'.join('---' for _ in table['columns'])+'|']
            out += ['| '+' | '.join(row)+' |' for row in table['rows']]
            out += ['']+['- '+s for s in table['notes']]+['']
        out += ['**署名与合作：**'+record['attribution'],'','**学术意义与范围：**'+record['meaning'],'','待核事项：','']+['- '+s for s in record['pending']]+['','核读范围：'+record['reading_scope'],'','出处：'+'、'.join(record['source_refs'])+'。','']
        out += ['['+v['title']+']('+v['url']+')' for v in record['links']]+['']
        if record['original_pdf_obtained']:
            out += ['本机原刊PDF的SHA-256：`'+record['pdf_sha256']+'`；不分发原文扫描件。','']
    p = data['paper']
    out += ['## 1980年偏氟乙烯调聚原刊','',p['title'],'','原作者：'+'、'.join(p['authors'])+'；'+p['citation']+'。','',p['question'],'','核读范围：'+p['reading_scope'],'',
            '| 研究对象／比较 | 原文结果与证据 | 原刊定位 |','|---|---|---|']
    out += ['| '+o['object']+' | '+o['finding']+' | '+o['locator']+' |' for o in p['observations']]
    out += ['','**科学意义：**'+p['meaning'],'']+['- '+s for s in p['limits']]+['','[官方论文入口]('+p['url']+') · [原刊PDF]('+p['pdf_url']+')','','已取得PDF的SHA-256：`'+p['pdf_sha256']+'`。原文PDF留本机，网页不分发全文；AI核读不代替专业结构签认。','']
    out += ['## 合作与研究接续','']
    for s in data['cooperation']:
        out += ['### '+s['title'],'',s['text'],'','出处：'+s['locator']+'；'+'、'.join(s['source_refs'])+'。','']
    out += ['## AI辅助资料整理：本人访谈与所引书页','','以下是传记引据的定位工作；原始访谈和目标书页尚未取得，目录信息不作为新增历史成果、工艺或性能证据。','']
    for record in data['source_trace']:
        out += ['### '+record['title'],'',record['identity'],'',record['description'],'']
        for table in record['tables']:
            out += ['**'+table['caption']+'**','','| '+' | '.join(table['columns'])+' |','|'+'|'.join('---' for _ in table['columns'])+'|']
            out += ['| '+' | '.join(row)+' |' for row in table['rows']]
            out += ['']+['- '+s for s in table['notes']]+['']
        out += ['**证据范围：**'+record['scope'],'','待取得的原件：','']+['- '+s for s in record['pending']]+['','出处：'+'、'.join(record['source_refs'])+'。','']
        out += ['['+v['title']+']('+v['url']+')' for v in record['links']]+['']
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
        for ident in ['topic-fluoromonomers','record-fluorinated-oils','refs','ref-r28','ref-s1','a02-vdf-1980','a02-technical-records','a02-team-records','a02-context-background','a02-source-trace']+[r['id'] for r in data['technical_records']+data['team_records']+data['source_trace']]:
            if page.ids[ident]!=1:raise ValueError('A02 lost a source or topic identity: '+ident)
        for url in page.links:check_link(root,PAGE,url,{PAGE:expected})
        if expected.index('id="a02-team-records"') >= expected.index('id="a02-technical-records"'):
            raise ValueError('Attributed team work must precede contextual technical records')
        report.update(status='passed',source_sha256=hashlib.sha256((root/CONTENT).read_bytes()).hexdigest(),history_cards=3,cooperation_stories=2,team_records=len(data['team_records']),new_team_technical_originals=0,technical_records=len(data['technical_records']),technical_tables=sum(len(r['tables']) for r in data['technical_records']),primary_observations=len(data['paper']['observations']),source_trace_records=len(data['source_trace']),book_2009_volume_confirmed=False,interview_original_obtained=False,original_pdf_redistributed=False)
    except (OSError,ValueError,KeyError,TypeError) as error:report['errors'].append(str(error))
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--write',action='store_true');args=parser.parse_args()
    if args.write:
        d=load(ROOT);s=target_page(ROOT,d);(ROOT/PAGE).write_bytes(s.encode('utf-8'));(ROOT/DOCUMENT).write_text(render_document(d),'utf-8',newline='\n')
    report=inspect_a02_history(ROOT);print(json.dumps(report,ensure_ascii=False));return 0 if report['status']=='passed' else 1


if __name__=='__main__':raise SystemExit(main())
