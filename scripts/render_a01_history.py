"""Render source-linked A01 history separately from frozen model records."""
from __future__ import annotations

import argparse
import hashlib
from html import escape
import json
from pathlib import Path
from public_line_labels import project_html
import re

ROOT = Path(__file__).resolve().parents[1]
CONTENT = 'content/a01-historical-achievements.v2.json'
TOPIC = 'topics/early-fluoroketones/index.html'
MARKERS = {'index.html': 'A01_HISTORY_HOME',
           'achievements/index.html': 'A01_HISTORY_SUMMARY', TOPIC: 'A01_HISTORY_TOPIC'}


def text(value) -> str:
    return escape(str(value), quote=True)


def source_anchor(value: str) -> str:
    if not re.fullmatch(r'[A-Za-z0-9_-]+', value):
        raise ValueError('Unsafe historical source ID')
    return 'a01-hist-source-'+value.lower()


def refs(rows: list[dict], prefix='') -> str:
    return ' '.join('<a href="'+prefix+'#'+source_anchor(r['source_id'])+'">'+
                    text(r['source_id'])+' · '+text(r['locator'])+'</a>' for r in rows)


def bullet(items: list[str]) -> str:
    return '<ul>'+''.join('<li>'+text(item)+'</li>' for item in items)+'</ul>'


def history_summary(data: dict, name: str) -> str:
    prefix = '' if name == 'index.html' else '../'
    topic = prefix+TOPIC
    return ('<article class="case" id="line-a01"><div class="case-side">A01 · 1950年代后期—1960年代初</div>'
            '<div class="case-main"><h3>'+text(data['title'])+'</h3>'
            '<p><b>研究问题：</b>六氟丙酮有哪些反应特性，怎样制得六氟双酚A，又怎样鉴定新衍生物？</p>'
            '<p>陈庆云与克鲁扬茨、甘巴里扬等合作者开展六氟丙酮的系列反应研究。1960年《Fluorinated ketones》第一报的英译本全文记载了多类反应，并给出六氟双酚A及另一二酚的制备与鉴定数据。相关衍生物论文还展示了以化学转化交叉判断结构的研究方法。</p>'
            '<p><a href="'+topic+'#a01-original-achievements">原始学术成果与证据 →</a> · '
            '<a href="'+topic+'#a01-first-report">1960年第一报原文与证据 →</a> · '
            '<a href="'+topic+'#record-inventor-certificate">发明人证书与合作故事 →</a> · '
            '<a href="'+topic+'#a01-research-overview">平台AI辅助整理与研究 →</a></p>'
            '<details><summary>出处与阅读范围</summary><p>已取得并核读第一报英译本647–653页全部影印页；俄文原刊与专业核译仍待核。传记、两篇Doklady原刊和117491号文书分别登记。'
            '<a href="'+topic+'#a01-historical-sources">查看来源、作者与核读范围</a>。历史实验成果依原作者归属；平台新增释读待专业核校，M0继续暂停。</p></details></div></article>')


def topic_history(data: dict) -> str:
    evaluation = data['historical_evaluation']
    source_id = evaluation['source_id']
    out = ['<style id="a01-history-css">#a01-historical-sources{overflow-wrap:anywhere}#a01-historical-sources li{margin-bottom:1.2em}#record-inventor-certificate dd{margin-inline-start:18px;overflow-wrap:anywhere}</style>',
           '<article id="topic-early-fluoroketones" data-topic-slug="early-fluoroketones" data-topic-type="topic">',
           '<span class="status">A01 · 原始学术成果</span><h2 id="a01-original-achievements">从六氟丙酮反应到六氟双酚A</h2>',
           '<p>'+text(data['scope'])+'</p>',
           '<p>'+text(evaluation['statement'])+' <a href="#'+source_anchor(source_id)+'">机构出处</a>。'+text(evaluation['limitation'])+'</p>',
           '<p>这里介绍陈先生与合作者在当时完成的实验化学研究。原文观察、原作者解释与平台提出的后续问题分别标注。</p>',
           '<nav aria-label="A01内容导航"><a href="#a01-first-report">第一报原文与证据</a> · <a href="#a01-historical-sources">原始来源</a> · <a href="#record-inventor-certificate">证书档案</a> · <a href="#a01-history-cooperation">合作与研究训练</a> · <a href="#a01-historical-gaps">待核原件</a> · <a href="#a01-research-overview">平台AI工作</a></nav>']
    for card in data['achievement_cards']:
        if not re.fullmatch(r'[A-Za-z0-9_-]+', card['id']):
            raise ValueError('Unsafe achievement card ID')
        out += ['<section id="'+text(card['id'])+'" style="border-top:1px solid var(--line);margin-top:26px;padding-top:12px">',
                '<h3>'+text(card['title'])+'</h3>', '<p><b>当时的问题：</b>'+text(card['question'])+'</p>',
                '<p><b>原始记录：</b></p>'+bullet(card['observations'])]
        if card.get('author_interpretation'):
            out += ['<p><b>原作者解释：</b>'+text(card['author_interpretation'])+'</p>']
        out += ['<p><b>学术意义：</b>'+text(card['significance'])+'</p>',
                '<p class="evidence">'+refs(card['source_refs'])+'</p>',
                '<details><summary>适用范围与待核事项</summary>'+bullet(card['limits'])+'</details></section>']
    out += ['</article>', first_report(data), '<article id="record-inventor-certificate"><span class="status">A01 · 文书档案</span>',
            '<h2>第117491号：说明书与证书书影</h2><p>'+text(data['certificate']['statement'])+'</p><dl>']
    for field in data['certificate']['fields']:
        out += ['<dt><b>'+text(field['label'])+'</b></dt><dd>'+text(field['value'] or '尚未取得')+'（'+text(field['status'])+'）</dd>']
    out += ['</dl><p>'+text(data['certificate']['boundary'])+'</p><p class="evidence">'+refs(data['certificate']['source_refs'])+'</p></article>',
            '<article id="a01-history-cooperation"><span class="status">A01 · 合作与研究训练</span><h2>共同研究与尊重贡献</h2>']
    for story in data['cooperation']:
        out += ['<section id="'+text(story['id'])+'"><h3>'+text(story['title'])+'</h3><p>'+text(story['narrative'])+'</p>',
                '<p class="evidence">'+refs(story['source_refs'])+'。'+text(story['boundary'])+'</p></section>']
    followup = data.get('followup_use')
    if followup:
        out += ['<h3>'+text(followup['title'])+'</h3><p>'+text(followup['observation'])+'</p>',
                '<p class="evidence">'+refs(followup['source_refs'])+'。'+text(followup['boundary'])+'</p>']
    out += ['</article><article id="a01-historical-gaps"><h2>尚待核实的原件与问题</h2>']
    for gap in data['gaps']:
        out += ['<h3>'+text(gap['question'])+'</h3><p>'+text(gap['needed_evidence'])+'</p>']
    out += ['</article><article id="a01-historical-sources"><h2>原始来源、作者与核读范围</h2><p>以下为本专题的独立证据索引；保留全平台既有来源编号与资料。</p><ul>']
    for source in data['sources']:
        title = text(source['title'])
        if source.get('url'):
            title = '<a href="'+text(source['url'])+'" target="_blank" rel="noopener noreferrer">'+title+'</a>'
        authors = '；署名：'+text('、'.join(source['authors'])) if source.get('authors') else ''
        access = (' <a href="'+text(source['access_url'])+'" target="_blank" rel="noopener noreferrer">阅读馆藏原文 ↗</a>') if source.get('access_url') else ''
        out += ['<li id="'+source_anchor(source['id'])+'"><b>'+text(source['id'])+'｜'+title+'</b>'+authors+'。'+
                text(source['locator'])+'；'+text(source['material_type'])+'。<br>已核读：'+text(source['read_scope'])+'。'+text(source['note'])+access+'</li>']
    # Retain historical citation anchors used by the original topic and outside links.
    out += ['</ul><details id="refs"><summary>相关后续论文与机构资料</summary><ul>',
            '<li id="ref-cq-r01">CQ-R01｜1960年134卷1367–1370页原刊，见上方独立索引。</li>',
            '<li id="ref-cq-r02">CQ-R02｜<a href="https://link.springer.com/article/10.1007/BF00904766" target="_blank" rel="noopener noreferrer">Some reactions of hexafluoroacetone（1962），11:633–640</a>：既有摘要与书目记录；与1960年第一报分开登记。</li>',
            '<li id="ref-cq-r03">CQ-R03｜<a href="https://onlinelibrary.wiley.com/doi/abs/10.1002/anie.196609471" target="_blank" rel="noopener noreferrer">Gambaryan等，1966年共同综述，5:947–956</a>：既有作者、摘要与参考文献记录；共同综述不计为独立团队评价。</li>',
            '<li id="ref-cq-r28">CQ-R28｜<a href="https://www.sioc.ac.cn/dncqy/" target="_blank" rel="noopener noreferrer">上海有机所生平资料</a>：历史学术评价。</li>',
            '</ul></details><p><a href="../../achievements/index.html#line-a01">回到成果线 A01</a> · <a class="top" href="../index.html">返回专题索引 ↑</a></p></article>']
    work = data['platform_work']
    out += ['<article id="a01-research-overview"><span class="status">平台AI辅助整理与研究 · 待科学审阅</span>',
            '<h2>后人整理了什么，还要回答什么</h2><p>'+text(work['summary'])+'</p>',
            '<h3>已完成的资料工作</h3>'+bullet(work['completed']),
            '<h3>继续研究的具体问题</h3>'+bullet(work['next_questions']),
            '<p>既有双酚AF计量重建、衍生物物性复核及噁唑酮M0诊断分别留档；它们不替代上述历史成果。M0继续暂停，未开展新的量化计算或模型API调用。</p>',
            '<details><summary>当前不能作出的结论</summary>'+bullet(work['not_claimed'])+'</details>',
            '<p>平台新增释读与分析保持 <code>review_required</code>、<code>release_eligible=false</code>；历史已发表成果依其原作者和证据呈现。<a href="https://github.com/CCcolab/Chen-Qingyun-AI4Science/blob/main/docs/A01_FIRST_REPORT_zh-CN.md">阅读第一报学术成果与证据档案</a>。</p></article>']
    payload = json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2).replace('</', '<\\/')
    out += ['<script type="application/json" id="a01-historical-achievements">'+payload+'</script>']
    return '\n'.join(out)


def first_report(data: dict) -> str:
    report = data['first_report']
    bibliography = report['bibliography']
    out = ['<article id="a01-first-report"><span class="status">A01 · 原论文核读</span>',
           '<h2>'+text(report['title'])+'</h2><p>'+text(report['read_scope'])+'</p>',
           '<p><a href="'+text(report['archive_url'])+'" target="_blank" rel="noopener noreferrer">阅读馆藏英译本 ↗</a> · '
           '<a href="https://github.com/CCcolab/Chen-Qingyun-AI4Science/blob/main/docs/A01_FIRST_REPORT_zh-CN.md">阅读学术释读与待核事项 ↗</a></p>',
           '<dl><dt><b>原页署名</b></dt><dd>'+text('、'.join(bibliography['authors']))+'</dd>',
           '<dt><b>机构</b></dt><dd>'+text(bibliography['affiliation'])+'</dd>',
           '<dt><b>版本与时间</b></dt><dd>英译页码 '+text(bibliography['english_pages'])+'；译者注明俄文原刊 '+text(bibliography['russian_pages_as_translator_note'])+'；收稿 '+text(bibliography['received'])+'，刊期 '+text(bibliography['issue_date'])+'。</dd></dl>',
           '<h3>从原始观察理解学术贡献</h3>']
    for entry in report['contributions']:
        out += ['<section class="a01-original-contribution"><h3>'+text(entry['title'])+'</h3>',
                '<p><b>原文观察：</b>'+text(entry['observation'])+'</p>',
                '<p><b>作者解释与研究意义：</b>'+text(entry['interpretation'])+'</p>',
                '<p class="evidence">原文 '+text(entry['locator'])+'。'+text(entry['boundary'])+'</p></section>']
    out += ['<h3>双酚制备、对照与用途：逐项登记</h3>']
    for entry in report['selected_data']:
        out += ['<section class="a01-selected-evidence"><h3>'+text(entry['object'])+'</h3><p>'+text(entry['value'])+'</p>',
                '<p class="evidence">原文 '+text(entry['locator'])+'。'+text(entry['boundary'])+'</p></section>']
    out += ['<p>'+text(report['source_note'])+'</p><p>'+text(report['boundary'])+'</p></article>']
    return '\n'.join(out)


def rendered_blocks(root: Path) -> tuple[dict, dict]:
    data = json.loads((root/CONTENT).read_text('utf-8-sig'))
    if (data.get('achievement_line') != 'A01' or data.get('scientific_review_status') != 'review_required'
            or data.get('release_eligible') is not False or data['platform_work'].get('m0_status') != 'paused'
            or len(data.get('achievement_cards', [])) != 5
            or data.get('schema_version') != '2.0'
            or data.get('first_report', {}).get('pages') != list(range(647, 654))
            or data['first_report'].get('russian_original_obtained') is not False):
        raise ValueError('Unsupported A01 historical content or review scope')
    identifiers = [row['id'] for row in data['sources']]
    if len(set(identifiers)) != len(identifiers):
        raise ValueError('Duplicate historical source IDs')
    for row in data['achievement_cards']+data['cooperation']+[data['certificate']]+([data['followup_use']] if data.get('followup_use') else []):
        if not row['source_refs'] or any(ref['source_id'] not in identifiers for ref in row['source_refs']):
            raise ValueError('Missing historical source binding')
    blocks = {}
    for name, marker in MARKERS.items():
        body = topic_history(data) if name == TOPIC else history_summary(data, name)
        blocks[name] = '<!-- '+marker+':BEGIN -->\n'+project_html(body, name)+'\n<!-- '+marker+':END -->'
    return data, blocks


def inspect_a01_history(root: Path) -> dict:
    data, blocks = rendered_blocks(root)
    for name, expected in blocks.items():
        raw = (root/'site'/name).read_text('utf-8')
        marker = MARKERS[name]
        pattern = r'<!-- '+marker+r':BEGIN -->.*?<!-- '+marker+r':END -->'
        matches = re.findall(pattern, raw, re.S)
        if matches != [expected]:
            raise ValueError('A01 historical presentation differs from source: '+name)
    return {'status': 'passed', 'source_sha256': hashlib.sha256((root/CONTENT).read_bytes()).hexdigest(),
            'cards': len(data['achievement_cards']), 'sources': len(data['sources']), 'pages': len(blocks),
            'first_report_pages': data['first_report']['pages'], 'russian_original_obtained': False,
            'scientific_review_status': 'review_required', 'release_eligible': False, 'M0_resumed': False}


def write(root: Path) -> None:
    _, blocks = rendered_blocks(root)
    for name, expected in blocks.items():
        path = root/'site'/name
        raw = path.read_text('utf-8')
        marker = MARKERS[name]
        pattern = r'<!-- '+marker+r':BEGIN -->.*?<!-- '+marker+r':END -->'
        if re.search(pattern, raw, re.S):
            raw, count = re.subn(pattern, lambda _: expected, raw, flags=re.S)
            if count != 1:
                raise ValueError('Duplicate historical presentation marker')
        elif name == TOPIC:
            start = raw.index('<article id="topic-early-fluoroketones"')
            end = raw.index('<details id="a01-technical-record"', start)
            raw = raw[:start]+expected+'\n'+raw[end:]
        else:
            pattern = r'<article class="case" id="line-a01">.*?</article>'
            raw, count = re.subn(pattern, lambda _: expected, raw, flags=re.S)
            if count != 1:
                raise ValueError('Missing or duplicate A01 line')
        path.write_bytes(raw.encode('utf-8'))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    if args.write:
        write(ROOT)
    print(json.dumps(inspect_a01_history(ROOT), ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
