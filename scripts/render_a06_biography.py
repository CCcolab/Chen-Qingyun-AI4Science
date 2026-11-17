"""Present A06 history across its two existing topics; retain original evidence."""
from __future__ import annotations
import argparse
from html import escape
import json
from pathlib import Path
import re

from public_line_labels import project_html, project_markdown

CONTENT = 'content/a06-biography-narrative.v1.json'
DOCUMENT = 'docs/A06_ACADEMIC_ACHIEVEMENTS_zh-CN.md'
ROUTES = ('topics/perfluorosulfonates/index.html', 'topics/chen-reagent/index.html')
BEGIN = '<!-- A06_BIOGRAPHY_HISTORY:BEGIN -->'
END = '<!-- A06_BIOGRAPHY_HISTORY:END -->'
CONTEXT_BEGIN = '<!-- HERITAGE_CONTEXT_BEGIN -->'
CONTEXT_END = '<!-- HERITAGE_CONTEXT_END -->'
FEATURE_EDITS = (
    ('已核见原出版社题录与作者摘要；原全文及条件转录仍待补。', '此处按原出版社题录与作者摘要介绍试剂功能与反应对象。'),
    ('原论文全文、原始实验记录和具体条件仍待逐项核校；命名使用不等于全部机理已经证明。', '命名证据、具体反应方法与机理研究各按来源介绍，不从命名推定统一机理。'),
)


def load(root: Path) -> dict:
    d=json.loads((root/CONTENT).read_bytes())
    if (d.get('schema_version'), d.get('achievement_line'), d.get('scientific_review_status'),
            d.get('release_eligible'), d.get('m0_status')) != ('1.0','A06','review_required',False,'paused'):
        raise ValueError('A06 requires historical attribution and separate platform review')
    if tuple(p['route'] for p in d['pages']) != ROUTES:
        raise ValueError('A06 may use only its two existing topic routes')
    for p in d['pages']:
        ids=[s['id'] for s in p['sources']]
        if len(set(ids))!=len(ids) or any(not set(c['source_ids'])<=set(ids) for c in p['cards']):
            raise ValueError('A06 source identity must be unique and complete')
        if any(len(row)!=3 for row in p['roles']+p['scope_rows']):
            raise ValueError('A06 needs complete role and scope tables')
        if 'method_rows' in p and any(len(row)!=5 for row in p['method_rows']):
            raise ValueError('A06 historical methods require distinct roles')
    if re.search(r'private-sources|原始证据待核清单|现阶段待查事项统计|file://|(?<![A-Za-z])[A-Za-z]:[\\/]',json.dumps(d,ensure_ascii=False)):
        raise ValueError('Private A06 tracking cannot enter historical pages')
    return d


def element(text: str, tag: str, ident: str) -> str:
    pattern=r'<'+tag+r'\b[^>]*\bid="'+re.escape(ident)+r'"[^>]*>'
    matches=list(re.finditer(pattern,text,re.S))
    if len(matches)!=1:
        raise ValueError('Expected one preserved A06 element: '+ident)
    start=matches[0].start();depth=0
    for token in re.finditer(r'</?'+tag+r'\b[^>]*>',text[start:],re.S):
        depth+=-1 if token.group().startswith('</') else 1
        if depth==0:return text[start:start+token.end()]
    raise ValueError('Unclosed preserved A06 element: '+ident)


def feature(text: str) -> str:
    value=element(text,'section','chen-reagent-contribution')
    for old,new in FEATURE_EDITS:
        if value.count(old)+value.count(new)!=1:
            raise ValueError('A06 naming evidence differs from its two fixed text edits')
        value=value.replace(old,new)
    return value


def table(caption,columns,rows,ident):
    return ('<div class="a06-table" role="region" tabindex="0" aria-labelledby="'+ident+'"><table><caption id="'+ident+'">'+escape(caption)+'</caption><thead><tr>'
            +''.join('<th scope="col">'+escape(v)+'</th>' for v in columns)+'</tr></thead><tbody>'
            +''.join('<tr><th scope="row">'+escape(row[0])+'</th>'+''.join('<td>'+escape(v)+'</td>' for v in row[1:])+'</tr>' for row in rows)+'</tbody></table></div>')


def render_block(root: Path,route: str) -> str:
    d=load(root);p=next(v for v in d['pages'] if v['route']==route)
    css='.a06-meaning{border-left:3px solid #aa7545;padding:10px 16px;background:#f7f4eb}.a06-locator{font-size:.86rem;color:var(--muted)}.a06-nav{display:flex;flex-wrap:wrap;gap:8px 18px}.a06-table{overflow-x:auto;max-width:100%;margin:20px 0;border:1px solid var(--line)}.a06-table table{border-collapse:collapse;min-width:640px;width:100%;font-size:.92rem}.a06-table caption{text-align:left;padding:14px;background:#edf3ee;color:var(--accent);font-weight:700}.a06-table th,.a06-table td{border-top:1px solid var(--line);padding:12px;text-align:left;vertical-align:top}.a06-table:focus-visible{outline:3px solid #aa7545}#refs{overflow-wrap:anywhere}.a06-legacy{margin:22px 0}.a06-legacy summary{cursor:pointer;font-weight:600;padding:16px;border:1px solid var(--line)}'
    out=[BEGIN,'<style id="heritage-context-style">'+css+'</style>']
    for i,c in enumerate(p['cards']):
        topic=' data-topic-slug="'+('perfluorosulfonates' if route==ROUTES[0] else 'chen-reagent')+'" data-topic-type="topic"' if i==0 else ''
        out+=['<article id="'+c['id']+'"'+topic+'><span class="status">历史成果与合作</span><h2>'+escape(c['title'])+'</h2>']
        if i==0:
            out+=['<p>'+escape(p['intro'])+'</p><nav class="a06-nav" aria-label="A06成果专题"><a href="../perfluorosulfonates/index.html">磺酸酯与二氟卡宾</a><a href="../chen-reagent/index.html">陈试剂与三氟甲基化</a><a href="#heritage-context">合作分工</a><a href="../../research/index.html#ai-a06">AI资料整理</a><a href="#refs">参考资料</a></nav>']
        out+=['<p>'+escape(v)+'</p>' for v in c['paragraphs']]
        refs=' · '.join('<a href="#'+next(s['anchor'] for s in p['sources'] if s['id']==ident)+'">'+escape(ident)+'</a>' for ident in c['source_ids'])
        out+=['<p class="a06-meaning"><b>学术意义：</b>'+escape(c['meaning'])+'</p><p class="a06-locator">'+escape(c['locator'])+' · '+refs+'</p></article>']
    out+=['<article id="heritage-context"><h2>合作与学术接续</h2>',table('按传记及原文分别介绍合作角色',['人物或团队','具体工作与角色','出处'],p['roles'],'a06-cooperation-caption')]
    if p.get('method_rows'):
        out+=['<section id="a06-historical-methods"><h3>两项方法、两组提交与核查记录</h3>',table('2003与2010方法分别保存',['方法','具体用途','Submitted by','Checked by','卷页'],p['method_rows'],'a06-methods-caption'),'<p>这里的核查者为原刊历史方法的具名核查者。甲酯与硅酯、提交与核查角色各自分列。</p></section>']
    out+=['</article>','<article id="a06-ai-collation"><h2>平台的AI辅助资料整理</h2><p>'+escape(d['platform_text'])+'</p><p><a href="../../research/index.html#ai-a06">A06（磺酸酯、二氟卡宾与三氟甲基化）的AI研究资料 →</a></p></article>',
          '<article id="refs"><h2>参考资料</h2><ul>']
    later={'CQ-R13','CQ-R14','CQ-R21','CQ-R22','CQ-R23','CQ-R24'}
    def source_row(s):
        title='<a href="'+escape(s['url'],quote=True)+'">'+escape(s['title'])+'</a>' if s['url'] else escape(s['title'])
        return '<li id="'+s['anchor']+'"><b>'+escape(s['id'])+'</b> · '+title+'；'+escape(s['locator'])+'</li>'
    out+=[source_row(s) for s in p['sources'] if s['id'] not in later]
    out+=['</ul>']
    if any(s['id'] in later for s in p['sources']):
        out+=['<details><summary>保留的后续研究索引</summary><p>后续方法、评论及理论计算按其原作者归属；索引不构成本平台新增研究成果。</p><ul>']+[source_row(s) for s in p['sources'] if s['id'] in later]+['</ul></details>']
    out+=['<details><summary>研究对象与解释范围</summary>',table('保留各项研究的对象和范围',['对象','历史记录','解释范围'],p['scope_rows'],'a06-scope-caption'),'</details><p><a href="../../achievements/index.html#line-a06">A06（磺酸酯、二氟卡宾与三氟甲基化）成果线</a> · <a href="../index.html">返回专题索引 ↑</a></p></article>',END]
    return project_html('\n'.join(out),route)


def render_heritage_context(root: Path,route: str) -> str:
    return render_block(root,route)


def render_document(root: Path) -> str:
    d=load(root);out=['# '+d['title'],'']
    def md_table(columns,rows):
        return ['| '+' | '.join(columns)+' |','| '+' | '.join('---' for _ in columns)+' |']+['| '+' | '.join(v.replace('|','\\|') for v in row)+' |' for row in rows]+['']
    for p in d['pages']:
        out+=['## '+p['title'],'',p['intro'],'']
        for c in p['cards']:
            out+=['### '+c['title'],'']
            for v in c['paragraphs']:out+=[v,'']
            out+=['**学术意义：**'+c['meaning'],'',c['locator']+' · '+'、'.join(c['source_ids']),'']
        out+=['### 合作与学术接续','']+md_table(['人物或团队','具体工作与角色','出处'],p['roles'])
        if p.get('method_rows'):out+=md_table(['方法','具体用途','Submitted by','Checked by','卷页'],p['method_rows'])
        out+=['### 参考资料','']
        for s in p['sources']:
            title='['+s['title']+']('+s['url']+')' if s['url'] else s['title']
            out+=['- **'+s['id']+'** · '+title+'；'+s['locator']]
        out+=['','### 研究对象与解释范围','']+md_table(['对象','历史记录','解释范围'],p['scope_rows'])
    out+=['## 平台的AI辅助资料整理','',d['platform_text'],'','[A06（磺酸酯、二氟卡宾与三氟甲基化）AI研究资料](../site/research/index.html#ai-a06)','']
    return project_markdown('\n'.join(out))


def inspect_biography(root: Path) -> dict:
    errors=[]
    try:
        for route in ROUTES:
            s=(root/'site'/route).read_text('utf-8');expected=CONTEXT_BEGIN+'\n'+render_block(root,route)+'\n'+CONTEXT_END
            if any(s.count(x)!=1 for x in (BEGIN,END,CONTEXT_BEGIN,CONTEXT_END)) or expected not in s:
                errors.append('A06 topic differs from source: '+route)
            if route==ROUTES[1]:
                if feature(s)!=element(s,'section','chen-reagent-contribution'):errors.append('A06 feature text edits missing')
                element(s,'article','record-reagent-identity')
        if (root/DOCUMENT).read_bytes()!=render_document(root).encode('utf-8'):errors.append('A06 document differs from source')
    except (ValueError,KeyError,OSError) as e:errors.append(str(e))
    return {'status':'failed' if errors else 'passed','errors':errors}


def write(root: Path) -> None:
    for route in ROUTES:
        path=root/'site'/route;s=path.read_bytes().decode('utf-8');a='<main class="wrap">';b='</main>'
        if s.count(a)!=1 or s.count(b)!=1:raise ValueError('A06 needs one bounded main region')
        start=s.index(a)+len(a);end=s.index(b,start)
        prefix=feature(s)+'\n' if route==ROUTES[1] else ''
        suffix='\n<details class="a06-legacy"><summary>既有试剂身份与方法记录</summary>'+element(s,'article','record-reagent-identity')+'</details>' if route==ROUTES[1] else ''
        body=prefix+CONTEXT_BEGIN+'\n'+render_block(root,route)+'\n'+CONTEXT_END+suffix
        path.write_bytes((s[:start]+body+s[end:]).encode('utf-8'))
    (root/DOCUMENT).write_bytes(render_document(root).encode('utf-8'))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--write',action='store_true');args=parser.parse_args();root=Path(__file__).resolve().parents[1]
    if args.write:write(root)
    report=inspect_biography(root);print(json.dumps(report,ensure_ascii=False,indent=2));raise SystemExit(bool(report['errors']))
