"""Source-located historical diagrams and examples, without scientific execution."""
from __future__ import annotations

import argparse
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import posixpath
import re
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
CONTENT='content/nine-line-deep-reading.v1.json'
DOCUMENT='docs/NINE_LINE_DEEP_READING_zh-CN.md'
MAIN_ROUTES={
    'A01':'topics/early-fluoroketones/index.html','A02':'topics/fluoromonomers/index.html',
    'A03':'pftb/index.html','A04':'topics/f53/index.html','A05':'topics/refrigerants/index.html',
    'A06':'topics/chen-reagent/index.html','A07':'topics/single-electron-transfer/index.html',
    'A08':'topics/fluoroporphyrins/index.html','A09':'people/index.html',
}
TARGET_ROUTES={**MAIN_ROUTES,'A06':'topics/perfluorosulfonates/index.html',
               'A08':'topics/deoxyfluorination/index.html'}
ROUTES=tuple(dict.fromkeys((*MAIN_ROUTES.values(),*TARGET_ROUTES.values())))
IDENTITIES={'original_observation':'原文观察与结果','author_interpretation':'原作者的解释','platform_reading':'读图说明'}
ENTRY_CSS='.cq-deep-entry{box-sizing:border-box;max-width:1120px;margin:20px auto;padding:12px 18px;background:#eef7f7;border-left:4px solid #177c80;line-height:1.8}.cq-deep-entry a{color:#086878;text-decoration:underline}@media(max-width:620px){.cq-deep-entry{margin:14px 10px}}'
CSS='''.cq-deep{box-sizing:border-box;max-width:1120px;margin:28px auto;padding:clamp(20px,4vw,40px);border:1px solid #c7d9df;border-top:4px solid #177c80;border-radius:14px;background:#fff;color:#172b3a;line-height:1.85;overflow-wrap:anywhere}.cq-deep h2{font-size:clamp(1.4rem,3vw,1.9rem);line-height:1.5;margin:.4em 0 1em}.cq-deep h3{font-size:1.15rem;margin:1.6em 0 .6em}.cq-deep h4{margin:.5em 0}.cq-deep p{max-width:78ch}.cq-deep-label{font-size:.9rem;color:#25636d}.cq-deep-identity,.cq-deep-cite{font-size:.86rem;color:#496471}.cq-deep-cite{margin-top:.25em}.cq-deep a{color:#087080;text-decoration:underline;text-underline-offset:.15em}.cq-deep-flow,.cq-deep-molecules{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,230px),1fr));gap:16px;margin:1.2em 0;padding:0;list-style:none}.cq-deep-flow>li,.cq-deep-molecule{border:1px solid #cfdee3;border-radius:10px;padding:16px;background:#f5fafb;min-width:0}.cq-deep-step{display:block;color:#177c80;font-size:.82rem;font-weight:700}.cq-deep-flow>li p,.cq-deep-molecule p{margin:.6em 0}.cq-deep svg{display:block;max-width:100%;width:100%;height:auto;background:#fff}.cq-deep figure{margin:1.4em 0}.cq-deep figcaption{font-weight:600;margin:.8em 0}.cq-deep-note,.cq-deep-scope{font-size:.9rem;color:#3c5360;background:#f5f8fa;border-left:3px solid #c0d1d9;padding:12px 16px}.cq-deep-table{overflow-x:auto;margin:1.4em 0}.cq-deep table{width:100%;min-width:540px;border-collapse:collapse;font-size:.92rem}.cq-deep th,.cq-deep td{border:1px solid #cfdbe1;padding:10px 12px;text-align:left;vertical-align:top}.cq-deep thead{background:#edf5f7}.cq-deep caption{text-align:left;font-weight:600;margin-bottom:10px}.cq-deep-nav{display:flex;flex-wrap:wrap;gap:12px 24px;margin-top:24px}.cq-deep-sources{font-size:.9rem;padding-left:1.4em}.cq-deep-entry{box-sizing:border-box;max-width:1120px;margin:20px auto;padding:12px 18px;background:#eef7f7;border-left:4px solid #177c80;line-height:1.8}.cq-deep-entry a{color:#086878;text-decoration:underline}@media(max-width:620px){.cq-deep{margin:18px 10px;padding:20px 16px}.cq-deep-flow,.cq-deep-molecules{grid-template-columns:1fr}.cq-deep-entry{margin:14px 10px}.cq-deep h2{font-size:1.35rem}}'''


def _check_refs(part:dict, known:set[str])->None:
    refs=part.get('source_refs')
    if (not isinstance(refs,list) or not refs
            or any(not isinstance(x,dict) or x.get('id') not in known
                   or not isinstance(x.get('locator'),str) or not x['locator'].strip() for x in refs)):
        raise ValueError('Each historical example/diagram needs resolved sources and exact locators')


def checked_svg(value:str)->str:
    value=re.sub(r'^\s*<\?xml[^>]*\?>','',value).strip()
    if re.search(r'<!DOCTYPE|<!ENTITY',value,re.I):raise ValueError('SVG entity declarations are forbidden')
    node=ET.fromstring(value)
    if node.tag.split('}')[-1]!='svg':raise ValueError('A molecule depiction must be SVG')
    for child in node.iter():
        if child.tag.split('}')[-1].lower() in {'script','style','link','object','embed','audio','video','foreignobject','image','iframe','animate','set','use'}:
            raise ValueError('Only static, self-contained molecule depictions are allowed')
        for key,val in child.attrib.items():
            local=key.split('}')[-1].lower()
            if (local.startswith('on') or (local in {'href','src'} and not val.startswith('#'))
                    or re.search(r'javascript:|url\(\s*["\x27]?(?!#)[a-z/]',val,re.I)):
                raise ValueError('SVG contains an executable or external resource')
    return value


def load(root:Path)->dict:
    data=json.loads((root/CONTENT).read_bytes())
    labels=json.loads((root/'content/achievement-labels.v1.json').read_bytes())['labels']
    if (data.get('schema_version'),data.get('scientific_review_status'),data.get('release_eligible'),
            data.get('M0_status'),data.get('Nemotron_training_status'))!=('1.0','review_required',False,'paused','paused'):
        raise ValueError('Deep reading cannot change scientific or computation boundaries')
    if [r['id'] for r in data['items']]!=list(MAIN_ROUTES):raise ValueError('Exactly nine ordered achievement lines are required')
    for row in data['items']:
        ident=row['id']
        if (row['line_name']!=labels[ident] or row['route']!=TARGET_ROUTES[ident]
                or row['main_route']!=MAIN_ROUTES[ident] or row['anchor']!=ident.lower()+'-deep-reading'):
            raise ValueError('Deep reading lost a canonical achievement identity or route')
        if not all(isinstance(row.get(k),str) and row[k].strip() for k in ('title','question','meaning')):
            raise ValueError('Incomplete historical reading')
        sources=row['sources'];known={s['id'] for s in sources}
        if not sources or len(known)!=len(sources):raise ValueError('Duplicate or missing deep-reading source')
        for source in sources:
            if not all(isinstance(source.get(k),str) and source[k].strip() for k in ('id','title','kind','locator')):
                raise ValueError('A source requires its identity, title and scope')
            if source.get('url') and not source['url'].startswith('https://'):
                raise ValueError('Only public HTTPS reference links may be published')
        if not isinstance(row['sections'],list) or len(row['sections'])<2:raise ValueError('An example needs a research narrative')
        for part in row['sections']:
            if part.get('identity') not in IDENTITIES or not part.get('heading') or not part.get('text'):
                raise ValueError('Observation, original explanation and reading aid must remain distinct')
            _check_refs(part,known)
        _check_refs(row['cooperation'],known)
        diagram=row['diagram']
        if not diagram.get('caption') or diagram.get('kind') not in ('steps','molecules'):
            raise ValueError('Missing source-bound reading diagram')
        for step in diagram.get('steps',[]):
            if not step.get('label') or not step.get('text'):raise ValueError('Incomplete reading step')
            _check_refs(step,known)
        for mol in diagram.get('molecules',[]):
            if not all(mol.get(k) for k in ('label','formula','smiles','inline_svg')):raise ValueError('Incomplete molecule depiction')
            checked_svg(mol['inline_svg']);_check_refs(mol,known)
        if diagram['kind']=='steps' and len(diagram.get('steps',[]))<2:raise ValueError('A reading path needs at least two steps')
        if diagram['kind']=='molecules' and not diagram.get('molecules'):raise ValueError('Missing depicted molecules')
        if row.get('table'):
            t=row['table'];_check_refs(t,known)
            if not t.get('caption') or not t.get('columns') or not t.get('rows') or any(len(r)!=len(t['columns']) for r in t['rows']):
                raise ValueError('Incomplete historical result table')
        if not row.get('boundaries'):raise ValueError('Each example must state its scientific scope')
        for link in row.get('related_readings',[]):
            path=link.get('path','');fragment=link.get('anchor','')
            if (not path or path.startswith('/') or '..' in path.split('/') or '\\' in path
                    or not (root/'site'/path).is_file() or not link.get('label') or not fragment):
                raise ValueError('Unknown related historical reading')
            if not re.search(r'\bid\s*=\s*["\x27]'+re.escape(fragment)+r'["\x27]',(root/'site'/path).read_text('utf-8')):
                raise ValueError('Related historical reading has no target anchor')
    if re.search(r'private-sources|current-item-register|现阶段待查事项统计|file://|[CD]:[\\/]',json.dumps(data,ensure_ascii=False),re.I):
        raise ValueError('Private originals or internal evidence lists cannot enter public reading content')
    return data


def markers(ident:str,entry=False)->tuple[str,str]:
    name='DEEP_READING_'+('ENTRY_' if entry else '')+ident
    return '<!-- '+name+':BEGIN -->','<!-- '+name+':END -->'


def rel_link(source:str,target:str,anchor='')->str:
    if source==target:return '#'+anchor if anchor else posixpath.basename(target)
    return posixpath.relpath(target,posixpath.dirname(source))+('#'+anchor if anchor else '')


def source_anchor(row:dict,ident:str)->str:
    return row['anchor']+'-source-'+re.sub('[^a-z0-9]+','-',ident.lower())


def cite(row:dict,part:dict)->str:
    numbers={s['id']:i for i,s in enumerate(row['sources'],1)}
    return '<p class="cq-deep-cite">出处：'+'；'.join(escape(x['locator'])+' <a href="#'+source_anchor(row,x['id'])+'">['+str(numbers[x['id']])+']</a>' for x in part['source_refs'])+'</p>'


def paras(value:str)->str:
    return ''.join('<p>'+escape(p)+'</p>' for p in value.split('\n\n') if p.strip())


def render_entry(root:Path,row:dict,current_route:str)->str:
    a,b=markers(row['id'],True)
    value=a+'\n<style id="'+row['anchor']+'-entry-style">'+ENTRY_CSS+'</style><p class="cq-deep-entry"><a href="'+escape(rel_link(current_route,row['route'],row['anchor']),quote=True)+'">深入原文：'+escape(row['title'])+' →</a></p>\n'+b+'\n'
    from public_line_labels import project_html
    return project_html(value,current_route)


def molecule_svg(row:dict,mol:dict,index:int)->str:
    value=checked_svg(mol['inline_svg']);prefix=row['anchor']+'-molecule-'+str(index)
    ids=re.findall(r'\bid\s*=\s*["\x27]([^"\x27]+)["\x27]',value)
    for ident in sorted(set(ids),key=len,reverse=True):
        value=re.sub(r'(\bid\s*=\s*["\x27])'+re.escape(ident)+r'(["\x27])',lambda m:m[1]+prefix+'-'+ident+m[2],value)
        value=value.replace('url(#'+ident+')','url(#'+prefix+'-'+ident+')').replace('href="#'+ident+'"','href="#'+prefix+'-'+ident+'"')
    title_id=prefix+'-title'
    opening=re.search(r'<svg\b[^>]*>',value)
    if opening is None:raise ValueError('Missing root SVG element')
    clean=re.sub(r'\s+(?:role|aria-labelledby|aria-describedby|aria-label)\s*=\s*(["\x27]).*?\1','',opening.group(),flags=re.I|re.S)
    desc_ids=re.findall(r'<desc\b[^>]*\bid\s*=\s*["\x27]([^"\x27]+)["\x27]',value)
    role=' role="img" aria-labelledby="'+title_id+'"'
    if desc_ids:role+=' aria-describedby="'+escape(' '.join(desc_ids),quote=True)+'"'
    clean=re.sub(r'<svg\b',lambda _:'<svg'+role,clean,count=1)
    value=value[:opening.start()]+clean+value[opening.end():]
    position=value.index('>')+1
    result=value[:position]+'<title id="'+title_id+'">'+escape(mol['label']+'；'+mol['formula'])+'</title>'+value[position:]
    ET.fromstring(result)
    return result


def render_block(root:Path,row:dict)->str:
    a,b=markers(row['id']);anchor=row['anchor'];full=row['id']+'（'+row['line_name']+'）'
    out=[a,'<style id="'+anchor+'-style">'+CSS+'</style>',
         '<section class="cq-deep" id="'+anchor+'" aria-labelledby="'+anchor+'-title">',
         '<p class="cq-deep-label">'+escape(full)+' · 深入原文</p>',
         '<h2 id="'+anchor+'-title">'+escape(row['title'])+'</h2>',paras(row['question'])]
    for part in row['sections']:
        out+=['<h3>'+escape(part['heading'])+'</h3><p class="cq-deep-identity">'+IDENTITIES[part['identity']]+'</p>',paras(part['text']),cite(row,part)]
    d=row['diagram'];out+=['<figure aria-labelledby="'+anchor+'-figure-caption"><figcaption id="'+anchor+'-figure-caption">'+escape(d['caption'])+'</figcaption>']
    if d.get('steps'):
        out+=['<ol class="cq-deep-flow">']
        for i,step in enumerate(d['steps'],1):
            out+=['<li><span class="cq-deep-step">'+str(i)+'</span><h4>'+escape(step['label'])+'</h4>'+paras(step['text'])+cite(row,step)+'</li>']
        out+=['</ol>']
    if d.get('molecules'):
        out+=['<div class="cq-deep-molecules">']
        for i,mol in enumerate(d['molecules'],1):
            out+=['<div class="cq-deep-molecule"><h4>'+escape(mol['label'])+'</h4>'+molecule_svg(row,mol,i)+'<p>'+escape(mol['formula'])+'</p>'+cite(row,mol)+'</div>']
        out+=['</div>']
    out+=['<p class="cq-deep-note">'+escape(n)+'</p>' for n in d.get('notes',[])]
    out+=['</figure>']
    if row.get('table'):
        t=row['table'];cap=anchor+'-table-caption'
        out+=['<div class="cq-deep-table" role="region" tabindex="0" aria-labelledby="'+cap+'"><table><caption id="'+cap+'">'+escape(t['caption'])+'</caption><thead><tr>'+''.join('<th scope="col">'+escape(str(c))+'</th>' for c in t['columns'])+'</tr></thead><tbody>']
        for cells in t['rows']:
            out+=['<tr><th scope="row">'+escape(str(cells[0]))+'</th>'+''.join('<td>'+escape(str(c))+'</td>' for c in cells[1:])+'</tr>']
        out+=['</tbody></table></div>',cite(row,t)]
    out+=['<h3>共同研究与学术接续</h3>',paras(row['cooperation']['text']),cite(row,row['cooperation']),'<h3>怎样理解这项工作</h3>',paras(row['meaning'])]
    out+=['<details class="cq-deep-scope"><summary>图解与论断的适用范围</summary>'+''.join(paras(x) for x in row['boundaries'])+'</details>','<h3>原文出处</h3><ol class="cq-deep-sources">']
    for s in row['sources']:
        title=escape(s['title'])
        if s.get('url'):title='<a href="'+escape(s['url'],quote=True)+'">'+title+'</a>'
        out+=['<li id="'+source_anchor(row,s['id'])+'">'+title+'；'+escape(s['kind'])+'。'+escape(s['locator'])+'</li>']
    out+=['</ol>']
    for link in row.get('related_readings',[]):
        out+=['<p>接着读：<a href="'+escape(rel_link(row['route'],link['path'],link['anchor']),quote=True)+'">'+escape(link['label'])+' →</a></p>']
    ai='people/index.html' if row['id']=='A09' else 'research/index.html'
    ai_anchor='a09-ai-collation' if row['id']=='A09' else 'ai-'+row['id'].lower()
    out+=['<p class="cq-deep-scope">历史研究及结果归原作者与实际参与者。本节新增图解、转录与释读为平台AI辅助整理，保持 <code>review_required</code>、<code>release_eligible=false</code>；未开展新实验或量化计算。</p>',
          '<nav class="cq-deep-nav" aria-label="深入阅读导航"><a href="'+escape(rel_link(row['route'],row['main_route'],row['id'].lower()+'-representative-study'),quote=True)+'">代表成果详读</a><a href="'+escape(rel_link(row['route'],'achievements/index.html','heritage-inventory'),quote=True)+'">九条成果线导读</a><a href="'+escape(rel_link(row['route'],ai,ai_anchor),quote=True)+'">AI辅助资料整理</a></nav></section>',b,'']
    from public_line_labels import project_html
    return project_html('\n'.join(out),row['route'])


def _rows_for_route(root:Path,route:str)->list[dict]:
    return [r for r in load(root)['items'] if route in (r['route'],r['main_route'])]


def restore_previous_html(root:Path,route:str,current_bytes:bytes)->bytes:
    value=current_bytes.decode('utf-8')
    for row in _rows_for_route(root,route):
        entry=render_entry(root,row,route)
        if value.count(entry)!=1:raise ValueError('Missing or modified deeper-reading entry: '+route)
        value=value.replace(entry,'',1)
        if route==row['route']:
            block=render_block(root,row)
            if value.count(block)!=1:raise ValueError('Missing or modified deeper-reading block: '+route)
            value=value.replace(block,'',1)
    return value.encode('utf-8')


def inject(root:Path,row:dict,route:str,before:str)->str:
    if any(m in before for m in markers(row['id'],True)):raise ValueError('Deeper-reading entry already exists')
    entry=render_entry(root,row,route)
    study_begin='<!-- REPRESENTATIVE_STUDY_'+row['id']+':BEGIN -->'
    study_end='<!-- REPRESENTATIVE_STUDY_'+row['id']+':END -->'
    if study_begin in before:
        if before.count(study_begin)!=1 or before.count(study_end)!=1:raise ValueError('Ambiguous existing historical case')
        start=before.index(study_begin);end=before.index(study_end)+len(study_end)
        block=render_block(root,row) if route==row['route'] else ''
        return before[:start]+entry+before[start:end]+block+before[end:]
    main=re.search(r'<main\b[^>]*>',before)
    if main is None:raise ValueError('Target topic has no main element')
    block=render_block(root,row) if route==row['route'] else ''
    return before[:main.end()]+entry+block+before[main.end():]


def render_document(root:Path)->str:
    data=load(root);out=['# 九条成果线：深入原文与图解','',
        '以下沿已公开的历史成果，选读原作者实例、鉴定依据与合作记录；新增图解和释读单列为平台AI辅助整理。','']
    for row in data['items']:
        out+=['## '+row['id']+'（'+row['line_name']+'）：'+row['title'],'',row['question'],'']
        for part in row['sections']:
            out+=['### '+part['heading'],'',IDENTITIES[part['identity']]+'：'+part['text'],'',
                  '出处：'+'；'.join(x['id']+'，'+x['locator'] for x in part['source_refs'])+'。','']
        d=row['diagram'];out+=['### '+d['caption'],'']
        for i,step in enumerate(d.get('steps',[]),1):out+=[str(i)+'. '+step['label']+'：'+step['text']]
        for mol in d.get('molecules',[]):out+=['- '+mol['label']+'：'+mol['formula']+'；结构图见专题。']
        out+=['',*d.get('notes',[]),'']
        if row.get('table'):
            t=row['table'];out+=[t['caption'],'','| '+' | '.join(map(str,t['columns']))+' |','| '+' | '.join('---' for _ in t['columns'])+' |']
            out+=['| '+' | '.join(str(c).replace('|','／') for c in cells)+' |' for cells in t['rows']];out+=['']
        out+=['### 合作与学术意义','',row['cooperation']['text'],'',row['meaning'],'','阅读范围：','']
        out+=['- '+x for x in row['boundaries']]
        out+=['','原文出处：','']
        for s in row['sources']:
            title='['+s['title']+']('+s['url']+')' if s.get('url') else s['title']
            out+=['- '+s['id']+'：'+title+'；'+s['locator']]
        for link in row.get('related_readings',[]):
            out+=['','[接着读：'+link['label']+'](https://cccolab.github.io/Chen-Qingyun-AI4Science/'+link['path']+'#'+link['anchor']+')']
        out+=['','[进入本专题深入阅读](https://cccolab.github.io/Chen-Qingyun-AI4Science/'+row['route']+'#'+row['anchor']+')','']
    out+=['平台新增图解与释读保持review_required、release_eligible=false。M0与Nemotron训练暂停，本轮无新实验、量化计算或模型训练。','']
    from public_line_labels import project_markdown
    return project_markdown('\n'.join(out))


class _Ids(HTMLParser):
    def __init__(self,value):super().__init__();self.ids=[];self.links=[];self.feed(value)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if a.get('id'):self.ids.append(a['id'])
        if tag=='a' and a.get('href'):self.links.append(a['href'])


def inspect_deep_reading(root:Path)->dict:
    errors=[]
    try:
        data=load(root)
        for row in data['items']:
            for route in dict.fromkeys((row['route'],row['main_route'])):
                text=(root/'site'/route).read_bytes().decode('utf-8')
                if text.count(render_entry(root,row,route))!=1:errors.append('Deeper-reading entry differs from source: '+route)
                if route==row['route'] and text.count(render_block(root,row))!=1:errors.append('Deeper-reading body differs from source: '+route)
                parsed=_Ids(text)
                if len(parsed.ids)!=len(set(parsed.ids)):errors.append('Duplicate page IDs: '+route)
            target=_Ids((root/'site'/row['route']).read_bytes().decode('utf-8'))
            if target.ids.count(row['anchor'])!=1:errors.append('Missing unique deeper-reading anchor: '+row['id'])
        if (root/DOCUMENT).read_bytes()!=render_document(root).encode('utf-8'):errors.append('Deeper-reading document differs from source')
        from render_representative_studies import inspect_studies
        errors+=inspect_studies(root)['errors']
    except (OSError,ValueError,KeyError,TypeError,ET.ParseError) as exc:errors.append(str(exc))
    return {'status':'failed' if errors else 'passed','errors':errors,'achievement_lines':9,
        'scientific_review_status':'review_required','release_eligible':False,'M0_resumed':False,'Nemotron_training_started':False}


def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args()
    if args.write:
        for row in load(ROOT)['items']:
            for route in dict.fromkeys((row['route'],row['main_route'])):
                path=ROOT/'site'/route;text=path.read_bytes().decode('utf-8')
                for entry in (True,False):
                    if not entry and route!=row['route']:continue
                    a,b=markers(row['id'],entry)
                    if a in text:
                        if text.count(a)!=1 or text.count(b)!=1:raise ValueError('Ambiguous deeper-reading markers')
                        expected=render_entry(ROOT,row,route) if entry else render_block(ROOT,row)
                        pattern=re.escape(a)+'.*?'+re.escape(b)+'\n'
                        text,count=re.subn(pattern,lambda _:expected,text,flags=re.S)
                        if count!=1:raise ValueError('Cannot replace deeper-reading region exactly')
                if markers(row['id'],True)[0] not in text:text=inject(ROOT,row,route,text)
                path.write_bytes(text.encode('utf-8'))
        (ROOT/DOCUMENT).write_bytes(render_document(ROOT).encode('utf-8'))
    report=inspect_deep_reading(ROOT);print(json.dumps(report,ensure_ascii=False));return report['status']!='passed'


if __name__=='__main__':raise SystemExit(main())
