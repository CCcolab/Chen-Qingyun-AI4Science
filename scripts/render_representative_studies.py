"""Static, source-located historical cases; no inference or scientific execution."""
from __future__ import annotations

import argparse
from html import escape
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
CONTENT='content/representative-studies.v1.json'
DOCUMENT='docs/REPRESENTATIVE_STUDIES_zh-CN.md'
ROUTES=('topics/early-fluoroketones/index.html','topics/fluoromonomers/index.html','pftb/index.html',
        'topics/f53/index.html','topics/refrigerants/index.html','topics/chen-reagent/index.html',
        'topics/single-electron-transfer/index.html','topics/fluoroporphyrins/index.html','people/index.html')
BASE='https://cccolab.github.io/Chen-Qingyun-AI4Science/'
CSS='''.cq-study{box-sizing:border-box;max-width:1120px;margin:28px auto;padding:clamp(22px,4vw,42px);border:1px solid #c8d8cd;border-top:4px solid #176e62;border-radius:10px;background:#fffefa;color:#182f2b;line-height:1.85;scroll-margin-top:24px}.cq-study *{box-sizing:border-box}.cq-study h2{font-size:clamp(25px,3.5vw,36px);line-height:1.45;margin:.3em 0 .7em}.cq-study h3{font-size:1.25rem;line-height:1.5;margin:1.6em 0 .7em;color:#155d55}.cq-study h4{font-size:1rem;line-height:1.6;margin:.8em 0 .3em}.cq-study p{max-width:84ch;margin:.65em 0}.cq-study a{color:#155d55;text-underline-offset:.2em}.cq-study a:focus-visible,.cq-study [tabindex]:focus-visible{outline:3px solid #aa7545;outline-offset:3px}.cq-study-label{font-size:.85rem;color:#155d55;font-weight:700}.cq-study-locator{font-size:.83rem;color:#51685e;overflow-wrap:anywhere}.cq-study-process{padding-left:1.5em}.cq-study-process>li{padding-left:.3em;margin:1.1em 0}.cq-study-table{overflow-x:auto;width:100%;margin:18px 0;border:1px solid #d6e0d9}.cq-study-table table{border-collapse:collapse;min-width:580px;width:100%;font-size:.91rem}.cq-study-table caption{text-align:left;font-weight:700;padding:12px;background:#edf3ee}.cq-study-table th,.cq-study-table td{padding:12px;border-top:1px solid #d6e0d9;text-align:left;vertical-align:top;overflow-wrap:anywhere}.cq-study-story{margin:24px 0;padding:18px 22px;background:#edf3ee;border-left:3px solid #aa7545}.cq-study-story h3{margin-top:0}.cq-study-meaning{padding:12px 18px;border-left:3px solid #176e62;background:#f5f3e9}.cq-study-references{padding-left:1.4em;font-size:.86rem;overflow-wrap:anywhere}.cq-study-references>li{margin:.9em 0;scroll-margin-top:24px}.cq-study-scope{font-size:.87rem;color:#51685e}.cq-study-nav{display:flex;flex-wrap:wrap;gap:10px 20px;border-top:1px solid #d6e0d9;padding-top:16px;margin-top:24px}@media(max-width:620px){.cq-study{margin:20px 0;padding:20px 16px;border-radius:6px}.cq-study-story{padding:14px 16px}.cq-study h2{font-size:25px}}'''


def load(root:Path)->dict:
    data=json.loads((root/CONTENT).read_bytes())
    labels=json.loads((root/'content/achievement-labels.v1.json').read_bytes())['labels']
    if (data.get('schema_version'),data.get('scientific_review_status'),data.get('release_eligible'),
        data.get('m0_status'),data.get('nemotron_training_status'))!=('1.0','review_required',False,'paused','paused'):
        raise ValueError('Historical case/AI boundaries changed')
    if [r['id'] for r in data['studies']]!=list(labels) or tuple(r['route'] for r in data['studies'])!=ROUTES:
        raise ValueError('Exactly nine canonical cases and existing routes are required')
    for row in data['studies']:
        if row['line_name']!=labels[row['id']] or row['anchor']!=row['id'].lower()+'-representative-study':
            raise ValueError('A case lost its canonical identity')
        if len(row['process'])<2 or len(row['results'])<2 or len(row['cooperation'])<2:
            raise ValueError('An expanded case needs process, result and collaboration details')
        ids=[s['id'] for s in row['sources']]
        if not ids or len(ids)!=len(set(ids)):
            raise ValueError('Duplicate or missing case sources')
        for part in [*row['process'],*row['results'],*row['cooperation'],row['story'],*([row['result_table']] if row.get('result_table') else [])]:
            if not part.get('locator') or not part.get('source_ids') or not set(part['source_ids'])<=set(ids):
                raise ValueError('Each process/result/story needs its own resolved citation and locator')
        for source in row['sources']:
            for key in ['url','supporting_url','supporting_download_url']:
                if source.get(key) and not source[key].startswith('https://'):
                    raise ValueError('Only explicit public HTTPS source links are allowed')
        if row.get('result_table'):
            t=row['result_table']
            if any(len(r)!=len(t['columns']) for r in t['rows']):raise ValueError('Incomplete result table')
    if re.search(r'private-sources|file://|[CD]:[\\/]|原始证据待核清单|现阶段待查事项统计',json.dumps(data,ensure_ascii=False)):
        raise ValueError('Private originals or tracking records cannot enter public cases')
    return data


def find(root:Path,route:str)->dict|None:
    return next((r for r in load(root)['studies'] if r['route']==route),None)


def markers(row:dict)->tuple[str,str]:
    return ('<!-- REPRESENTATIVE_STUDY_'+row['id']+':BEGIN -->','<!-- REPRESENTATIVE_STUDY_'+row['id']+':END -->')


def anchor(row:dict,source_id:str)->str:
    return row['id'].lower()+'-study-source-'+re.sub('[^a-z0-9]+','-',source_id.lower())


def citation(row:dict,part:dict)->str:
    numbers={s['id']:i for i,s in enumerate(row['sources'],1)}
    return ('<p class="cq-study-locator">出处：'+escape(part['locator'])+' '
        +' '.join('<a href="#'+anchor(row,sid)+'">['+str(numbers[sid])+']</a>' for sid in part['source_ids'])+'</p>')


def paragraphs(value:str)->str:
    return ''.join('<p>'+escape(p)+'</p>' for p in value.split('\n\n') if p.strip())


def table(row:dict,record:dict,kind:str)->str:
    caption=row['anchor']+'-'+kind+'-caption'
    return ('<div class="cq-study-table" role="region" tabindex="0" aria-labelledby="'+caption+'"><table><caption id="'+caption+'">'
        +escape(record['caption'])+'</caption><thead><tr>'+''.join('<th scope="col">'+escape(c)+'</th>' for c in record['columns'])
        +'</tr></thead><tbody>'+''.join('<tr><th scope="row">'+escape(cells[0])+'</th>'
        +''.join('<td>'+escape(c)+'</td>' for c in cells[1:])+'</tr>' for cells in record['rows'])+'</tbody></table></div>')


def render_block(root:Path,row:dict)->str:
    begin,end=markers(row)
    titles={'question':'科学问题','process':'研究过程','results':'关键结果','meaning':'学术意义',**row.get('section_titles',{})}
    up='../' if row['route'].startswith(('pftb/','people/')) else '../../'
    full=row['id']+'（'+row['line_name']+'）'
    out=[begin,'<style id="'+row['anchor']+'-style">'+CSS+'</style>',
         '<section class="cq-study" id="'+row['anchor']+'" aria-labelledby="'+row['anchor']+'-title">',
         '<p class="cq-study-label">'+escape(full)+' · 代表性成果详读</p><h2 id="'+row['anchor']+'-title">'+escape(row['title'])+'</h2>',
         '<h3>'+titles['question']+'</h3>'+paragraphs(row['question']),'<h3>'+titles['process']+'</h3><ol class="cq-study-process">']
    for part in row['process']:
        out+=['<li><h4>'+escape(part['title'])+'</h4>'+paragraphs(part['text'])+citation(row,part)+'</li>']
    out+=['</ol><h3>'+titles['results']+'</h3>']
    for part in row['results']:
        out+=['<h4>'+escape(part['title'])+'</h4>'+paragraphs(part['text'])+citation(row,part)]
    if row.get('result_table'):
        t=row['result_table'];out += [table(row,t,'results'),citation(row,t)]
        out += ['<p class="cq-study-locator">'+escape(n)+'</p>' for n in t.get('notes',[])]
    out+=['<h3>合作分工</h3>']
    for person in row['cooperation']:
        out+=['<h4>'+escape(person['person'])+'</h4>'+paragraphs(person['role'])+citation(row,person)]
    story=row['story']
    out+=['<aside class="cq-study-story" aria-labelledby="'+row['anchor']+'-story"><h3 id="'+row['anchor']+'-story">'
          +escape(row['story_heading']+'：'+story['title'])+'</h3>'+paragraphs(story['text'])+citation(row,story)
          +'<p class="cq-study-locator">资料性质：'+escape(story['identity'])+'</p></aside>',
          '<div class="cq-study-meaning"><h3>'+titles['meaning']+'</h3>'+paragraphs(row['meaning'])+'</div>',
          '<h3>阅读范围</h3><div class="cq-study-scope">'+''.join(paragraphs(x) for x in row['boundaries'])+'</div>',
          '<h3>参考资料与原文出处</h3><ol class="cq-study-references">']
    for source in row['sources']:
        title=escape(source['title'])
        if source.get('url'):title='<a href="'+escape(source['url'],quote=True)+'">'+title+'</a>'
        entry='<li id="'+anchor(row,source['id'])+'"><b>'+title+'</b>；'+escape(source['kind'])+'。'+escape(source['locator'])
        if source.get('supporting_url'):
            entry+=' <a href="'+escape(source['supporting_url'],quote=True)+'">原作者支持信息（SI）</a>；'+escape(source.get('supporting_locator',''))
        out+=[entry+'</li>']
    ai=up+'people/index.html#a09-ai-collation' if row['id']=='A09' else up+'research/index.html#ai-'+row['id'].lower()
    out+=['</ol><p class="cq-study-scope">历史成果与合作归原作者和实际参与者。本节依据所列史料展开学术叙述；平台AI辅助整理另列。</p>',
          '<nav class="cq-study-nav" aria-label="代表成果阅读导航"><a href="'+up+'achievements/index.html#heritage-inventory">九条成果线导读</a>'
          +'<a href="'+ai+'">AI辅助资料整理</a><a href="#refs">本专题原有参考资料</a></nav></section>',end]
    # PFtB uses #sources; the other existing topics expose #refs.
    value='\n'.join(out)
    if row['id']=='A03':value=value.replace('href="#refs"','href="#sources"')
    return value


def inject_study(root:Path,route:str,value:str)->str:
    if not (root/CONTENT).is_file():return value
    row=find(root,route)
    if row is None:return value
    begin,end=markers(row)
    if begin in value or end in value:raise ValueError('A representative study must be inserted exactly once')
    block=render_block(root,row)
    main=re.search(r'<main\b[^>]*>',value)
    if main is None:raise ValueError('A topic must have a main element')
    if row['id']=='A03':
        hero=re.search(r'<header class="hero"[^>]*>.*?</header>',value[main.end():],re.S)
        if hero is None:raise ValueError('PFtB original hero must remain intact')
        pos=main.end()+hero.end()
    else:pos=main.end()
    return value[:pos]+block+value[pos:]


def render_document(root:Path)->str:
    data=load(root)
    out=['# '+data['title'],'',data['history_identity'],'',data['editorial_identity'],'']
    for row in data['studies']:
        titles={'question':'科学问题','process':'研究过程','results':'关键结果','meaning':'学术意义',**row.get('section_titles',{})}
        out+=['## '+row['id']+'（'+row['line_name']+'） · '+row['title'],'',
              '[阅读专题个案]('+BASE+row['route']+'#'+row['anchor']+')','', '### '+titles['question'],'',row['question'],'','### '+titles['process'],'']
        for key in ['process','results']:
            if key=='results':out+=['### '+titles['results'],'']
            for part in row[key]:out+=['**'+part['title']+'**','',part['text'],'','出处：'+part['locator']+'；'+'、'.join(part['source_ids'])+'。','']
        if row.get('result_table'):
            t=row['result_table'];out += ['**'+t['caption']+'**','','| '+' | '.join(t['columns'])+' |','| '+' | '.join('---' for _ in t['columns'])+' |']
            out += ['| '+' | '.join(c.replace('|','\\|') for c in cells)+' |' for cells in t['rows']]
            out += ['','出处：'+t['locator']+'；'+'、'.join(t['source_ids'])+'。','']+t.get('notes',[])+['']
        out+=['### 合作分工','']
        for person in row['cooperation']:out+=['- **'+person['person']+'**：'+person['role']+'（'+person['locator']+'；'+'、'.join(person['source_ids'])+'）']
        s=row['story'];out+=['','### '+row['story_heading']+'：'+s['title'],'',s['text'],'',
                            '出处：'+s['locator']+'；'+'、'.join(s['source_ids'])+'。资料性质：'+s['identity']+'。','',
                            '### '+titles['meaning'],'',row['meaning'],'','### 阅读范围','']+row['boundaries']+['','### 参考资料与原文出处','']
        for source in row['sources']:
            title=source['title']
            if source.get('url'):title='['+title+']('+source['url']+')'
            out+=['- **'+source['id']+'** · '+title+'；'+source['kind']+'；'+source['locator']]
            if source.get('supporting_url'):out+=['  [原作者支持信息（SI）]('+source['supporting_url']+')；'+source.get('supporting_locator','')]
        out+=['']
    return '\n'.join(out)


def inspect_studies(root:Path)->dict:
    errors=[]
    try:
        data=load(root)
        for row in data['studies']:
            value=(root/'site'/row['route']).read_text('utf-8');begin,end=markers(row)
            if value.count(begin)!=1 or value.count(end)!=1 or render_block(root,row) not in value:
                errors.append('Study differs from its source: '+row['id'])
        if (root/DOCUMENT).read_bytes()!=render_document(root).encode('utf-8'):
            errors.append('Study document differs from source rendering')
    except (OSError,ValueError,KeyError,TypeError) as error:errors.append(str(error))
    return {'status':'failed' if errors else 'passed','errors':errors,'cases':9,'scientific_review_status':'review_required',
            'release_eligible':False,'M0_resumed':False,'Nemotron_training_started':False}


def main()->int:
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
    if args.write:
        data=load(ROOT)
        for row in data['studies']:
            p=ROOT/'site'/row['route'];value=p.read_bytes().decode('utf-8');begin,end=markers(row)
            pat=re.escape(begin)+'.*?'+re.escape(end)
            if begin in value or end in value:
                if value.count(begin)!=1 or value.count(end)!=1:raise ValueError('Ambiguous case markers')
                value=re.sub(pat,lambda _:render_block(ROOT,row),value,flags=re.S)
            else:value=inject_study(ROOT,row['route'],value)
            p.write_bytes(value.encode('utf-8'))
        (ROOT/DOCUMENT).write_bytes(render_document(ROOT).encode('utf-8'))
    report=inspect_studies(ROOT);print(json.dumps(report,ensure_ascii=False));return report['status']!='passed'


if __name__=='__main__':raise SystemExit(main())
