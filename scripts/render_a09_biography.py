"""Render A09 academic heritage from its biography-led historical narrative."""
from __future__ import annotations

import argparse
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import re

from public_line_labels import project_html, project_markdown

CONTENT = 'content/a09-biography-narrative.v1.json'
DOCUMENT = 'docs/A09_ACADEMIC_HERITAGE_zh-CN.md'
ROUTE = 'people/index.html'
BEGIN = '<!-- A09_BIOGRAPHY_HISTORY:BEGIN -->'
END = '<!-- A09_BIOGRAPHY_HISTORY:END -->'
CARD_IDS = ('a09-discipline', 'a09-independent', 'a09-writing', 'a09-team',
            'a09-exchange', 'a09-service', 'a09-continuity')
SOURCE_IDS = {'HERITAGE-S01', 'HERITAGE-S08', 'HERITAGE-S09', 'HERITAGE-S10', 'CQ-H06'}
CSS = '''
:root{color-scheme:light;--ink:#172b29;--muted:#506660;--accent:#176e62;--paper:#f6f5ef;--line:#d6e0d9}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--paper);color:var(--ink);font-family:system-ui,-apple-system,"Microsoft YaHei",sans-serif;line-height:1.85}
a{color:#155d55;text-underline-offset:.18em}a:focus-visible{outline:3px solid #c97932;outline-offset:3px}.wrap{max-width:1120px;margin:auto;padding:0 28px}
header{background:#173b37;color:#f2f4eb;padding:42px 0}header a{color:#c9e7d8}h1{font-size:clamp(2rem,5vw,3.2rem);line-height:1.3;margin:.4em 0}header p{max-width:80ch}.eyebrow{letter-spacing:.12em;font-size:.8rem;color:#bcd7c9}
article{background:#fff;border:1px solid var(--line);border-radius:12px;margin:24px 0;padding:clamp(22px,4vw,46px);scroll-margin-top:20px}h2{font-size:clamp(1.5rem,3vw,2rem);line-height:1.4;margin:.15em 0 .7em}h3{font-size:1.1rem;color:var(--accent)}p{max-width:82ch;margin:.65em 0}
.status{display:inline-block;background:#e4f0e9;color:#155448;font-size:.82rem;padding:.22em .8em;border-radius:30px;font-weight:700}.index{padding:26px 0 0}.index ol{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:8px 30px;padding-left:24px}
.meaning{border-left:3px solid #aa7545;padding:10px 16px;background:#f7f4eb}.locator{font-size:.86rem;color:var(--muted)}.table-scroll{overflow-x:auto;margin:20px 0;border:1px solid var(--line)}table{border-collapse:collapse;min-width:650px;width:100%;font-size:.92rem}caption{text-align:left;padding:14px;background:#edf3ee;color:var(--accent);font-weight:700}th,td{border-top:1px solid var(--line);padding:12px;text-align:left;vertical-align:top}
.skip{position:absolute;left:12px;top:-80px;background:#fff;padding:8px}.skip:focus{top:8px}#refs{overflow-wrap:anywhere}footer{padding:25px 0 40px;color:var(--muted);font-size:.9rem}
@media(max-width:600px){.wrap{padding:0 18px}header{padding:28px 0}article{border-radius:8px}.index ol{grid-template-columns:1fr}}@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
'''.strip()


def load(root: Path) -> dict:
    data = json.loads((root / CONTENT).read_bytes())
    if (data.get('schema_version'), data.get('achievement_line'), data.get('scientific_review_status'),
            data.get('release_eligible'), data.get('m0_status')) != ('1.0', 'A09', 'review_required', False, 'paused'):
        raise ValueError('A09 historical heritage must remain distinct from scientific research')
    if tuple(card['id'] for card in data['cards']) != CARD_IDS:
        raise ValueError('Unexpected A09 historical story identities')
    ids = [source['id'] for source in data['sources']]
    if len(ids) != len(SOURCE_IDS) or set(ids) != SOURCE_IDS:
        raise ValueError('A09 requires its exact attributed source set')
    if any(not set(card['source_ids']) <= SOURCE_IDS for card in data['cards']):
        raise ValueError('An A09 contribution is missing its source')
    if any(len(row) != 3 for row in data['roles'] + data['timeline']):
        raise ValueError('Incomplete A09 historical table')
    if re.search(r'private-sources|原始证据待核清单|现阶段待查事项统计|file://|(?<![A-Za-z])[A-Za-z]:[\\/]', json.dumps(data, ensure_ascii=False)):
        raise ValueError('Private A09 records cannot enter public history')
    return data


def refs(data: dict, ids: list[str]) -> str:
    sources = {s['id']: s for s in data['sources']}
    return ' · '.join('<a href="#' + sources[ident]['anchor'] + '">' + escape(ident) + '</a>' for ident in ids)


def table(caption: str, columns: list[str], rows: list[list[str]], ident: str) -> str:
    return ('<div class="table-scroll" role="region" tabindex="0" aria-labelledby="' + ident
            + '"><table><caption id="' + ident + '">' + escape(caption) + '</caption><thead><tr>'
            + ''.join('<th scope="col">' + escape(cell) + '</th>' for cell in columns) + '</tr></thead><tbody>'
            + ''.join('<tr><th scope="row">' + escape(row[0]) + '</th>'
                      + ''.join('<td>' + escape(cell) + '</td>' for cell in row[1:]) + '</tr>' for row in rows)
            + '</tbody></table></div>')


def render_page(root: Path) -> str:
    data = load(root)
    out = ['<!DOCTYPE html>', '<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">',
           '<meta name="description" content="以陈庆云传记与机构资料介绍学科建设、具体培养方法、合作与学术传承。"><title>'
           + escape(data['title']) + '｜陈庆云院士学术成就</title><style>' + CSS + '</style></head><body>',
           '<a class="skip" href="#main">跳至人物与传承正文</a><header><div class="wrap"><div class="eyebrow">有机氟化学研究与传承</div><h1>'
           + escape(data['title']) + '</h1><p>' + escape(data['intro']) + '</p><nav aria-label="平台导航">'
           + '<a href="../index.html#line-a09">首页传承线</a> · <a href="../achievements/index.html#heritage-line-a09">成果与传承资料</a> · <a href="../topics/index.html#topic-line-a09">专题目录</a></nav></div></header>',
           '<main class="wrap" id="main">', BEGIN,
           '<nav class="index" aria-label="学科建设与人才培养专题目录"><ol>'
           + ''.join('<li><a href="#' + card['id'] + '">' + escape(card['title']) + '</a></li>' for card in data['cards'])
           + '<li><a href="#a09-people">人物与合作角色</a></li><li><a href="#a09-ai-collation">AI辅助资料整理</a></li><li><a href="#refs">参考资料</a></li></ol></nav>']
    for card in data['cards']:
        out += ['<article id="' + card['id'] + '"><span class="status">历史经历与学术传承</span><h2>' + escape(card['title']) + '</h2>']
        out += ['<p>' + escape(p) + '</p>' for p in card['paragraphs']]
        out += ['<p class="meaning"><b>学术传承的具体作用：</b>' + escape(card['meaning']) + '</p>',
                '<p class="locator">出处：' + escape(card['locator']) + ' · ' + refs(data, card['source_ids']) + '</p>',
                '<p class="locator">资料性质：' + escape(card['source_kind']) + '</p>']
        if card['links']:
            out += ['<p>' + ' · '.join('<a href="' + escape(link['url'], quote=True) + '">' + escape(link['title']) + ' →</a>' for link in card['links']) + '</p>']
        out += ['</article>']
    out += ['<article id="a09-people"><h2>人物与合作角色</h2>',
            table('让具体参与者和回忆者可被看见', ['人物或群体', '所述角色与贡献', '出处'], data['roles'], 'a09-people-caption'),
            '<p>导师、学生、同仁、合作者与报告人按明确记述分别介绍；合著、合影或同场活动不自动证明师承，也不用于分派个人实验任务。</p></article>',
            '<article id="a09-timeline"><h2>学科服务与交流节点</h2>',
            table('按传记年表与机构历史报道列示', ['时间', '工作或事件', '出处'], data['timeline'], 'a09-timeline-caption'),
            '<p class="locator">以上是历史节点；任职、机构沿革和各阶段的统计口径分别保留。</p></article>',
            '<article id="a09-academic-archive"><h2>' + escape(data['archive']['title']) + '</h2><details><summary>论著目录与1987年收录数分别意味着什么</summary>']
    out += ['<p>' + escape(p) + '</p>' for p in data['archive']['paragraphs']]
    out += ['<p class="locator">' + escape(data['archive']['locator']) + ' · ' + refs(data, data['archive']['source_ids']) + '</p></details></article>',
            '<article id="a09-ai-collation" data-review-status="review_required" data-release-eligible="false" data-m0-status="paused"><span class="status">平台新增资料整理</span><h2>'
            + escape(data['ai']['title']) + '</h2><p>' + escape(data['ai']['intro']) + '</p><h3>本轮已完成</h3><ul>']
    out += ['<li>' + escape(p) + '</li>' for p in data['ai']['completed']]
    out += ['</ul><h3>整理的适用范围</h3><p>' + escape(data['ai']['scope']) + '</p><h3>未来设想</h3><p>' + escape(data['ai']['future'])
            + '</p><p class="locator">' + escape(data['ai']['state']) + '</p><p><a href="../research/index.html">八条科研成果线的AI研究资料 →</a></p></article>',
            '<article id="refs"><h2>参考资料</h2><ul>']
    for source in data['sources']:
        title = ('<a href="' + escape(source['url'], quote=True) + '">' + escape(source['title']) + '</a>') if source['url'] else escape(source['title'])
        out += ['<li id="' + source['anchor'] + '"><b>' + escape(source['id']) + '</b> · ' + title + '；' + escape(source['locator']) + '</li>']
    out += ['</ul><p><a href="../index.html#line-a09">返回A09（学科建设与人才培养）首页入口 ↑</a></p></article>', END, '</main>',
            '<footer class="wrap">历史成就与共同成果归陈庆云及实际参与者。平台保存出处、资料性质与学术传承脉络。</footer></body></html>']
    from render_representative_studies import inject_study
    return inject_study(root, ROUTE, project_html('\n'.join(out), ROUTE))


def render_overview(root: Path, route: str) -> str:
    data = load(root)
    url = 'people/index.html' if route == 'index.html' else '../people/index.html'
    archive = data['archive']
    result = ('<article class="case" id="line-a09"><div class="case-side">独立研究与学术共同体</div><div class="case-main">'
              + '<h3>A09（学科建设与人才培养）</h3><p>' + escape(data['overview']) + '</p><p><a href="' + url
              + '">学科建设、育人故事与合作传承 →</a></p><p><a href="' + url + '#a09-independent">自主选题与论证训练</a> · <a href="'
              + url + '#a09-team">团队带教与人才接续</a> · <a href="' + url + '#a09-service">期刊与国际学术服务</a></p>'
              + '<details><summary>学术档案的阅读口径</summary><section class="supporting-record" id="record-publication-index"><h4>'
              + escape(archive['title']) + '</h4>' + ''.join('<p>' + escape(p) + '</p>' for p in archive['paragraphs'])
              + '<p><a href="' + url + '#a09-academic-archive">出处与统计范围 →</a></p></section></details></div></article>')
    return project_html(result, route)


def render_inventory_summary(root: Path) -> str:
    data = load(root)
    study = ('<p><a href="../people/index.html#a09-representative-study">代表成果详读：自主选题、写作与共同带教 →</a></p>'
             if (root/'content/representative-studies.v1.json').is_file() else '')
    return project_html('<article class="heritage-card" id="heritage-line-a09"><p class="heritage-meta">A09（学科建设与人才培养）</p>'
        + '<h3>独立研究、团队接续与学术服务</h3><p>' + escape(data['inventory_intro']) + '</p><ul><li>自主选题、论文修改与完整谱图讨论。</li>'
        + '<li>高年级带新生、人才梯队衔接及长期同行合作。</li><li>研究生教育、期刊编辑、国际命名与会议服务。</li></ul>'
        + '<p class="heritage-locator">传记78–79、87–105、111、117–122页；机构2009、2019年报道及生平图集，各段出处见专题。</p>'
        + '<p><a href="../people/index.html">A09（学科建设与人才培养）人物与传承专题 →</a> · <a href="../people/index.html#refs">参考资料</a></p>'+study+'</article>', 'achievements/index.html')


def render_inventory_markdown_summary(root: Path) -> list[str]:
    data = load(root)
    rows = ['### A09（学科建设与人才培养）', '', data['inventory_intro'], '',
            '自主选题、论文修改和谱图讨论，高年级带新生与人才接续，以及期刊、会议和国际交流，分别在独立专题保留人物、事件与出处。', '',
            '依据：《氟缘笃志：陈庆云传》78–79、87–105、111、117–122页；机构2009、2019年报道与生平图集。', '',
            '[A09（学科建设与人才培养）人物与传承专题](https://cccolab.github.io/Chen-Qingyun-AI4Science/people/index.html) · [AI辅助资料整理](https://cccolab.github.io/Chen-Qingyun-AI4Science/people/index.html#a09-ai-collation)', '']
    if (root/'content/representative-studies.v1.json').is_file():
        rows += ['[代表成果详读：自主选题、写作与共同带教](https://cccolab.github.io/Chen-Qingyun-AI4Science/people/index.html#a09-representative-study)', '']
    return rows


def render_document(root: Path) -> str:
    data = load(root)
    out = ['# ' + data['title'], '', data['intro'], '']
    for card in data['cards']:
        out += ['## ' + card['title'], '']
        for paragraph in card['paragraphs']:
            out += [paragraph, '']
        out += ['**学术传承的具体作用：**' + card['meaning'], '', '出处：' + card['locator'] + ' · ' + '、'.join(card['source_ids']), '', '资料性质：' + card['source_kind'], '']
    for title, columns, rows in [('人物与合作角色', ['人物或群体', '所述角色与贡献', '出处'], data['roles']),
                                 ('学科服务与交流节点', ['时间', '工作或事件', '出处'], data['timeline'])]:
        out += ['## ' + title, '', '| ' + ' | '.join(columns) + ' |', '| --- | --- | --- |']
        out += ['| ' + ' | '.join(cell.replace('|', '\\|') for cell in row) + ' |' for row in rows]
        out += ['']
    out += ['## ' + data['archive']['title'], '']
    for p in data['archive']['paragraphs']:
        out += [p, '']
    out += [data['archive']['locator'], '', '## ' + data['ai']['title'], '', data['ai']['intro'], '', '### 本轮已完成', '']
    out += ['- ' + p for p in data['ai']['completed']]
    out += ['', '### 整理的适用范围', '', data['ai']['scope'], '', '### 未来设想', '', data['ai']['future'], '', data['ai']['state'], '', '## 参考资料', '']
    for source in data['sources']:
        title = '[' + source['title'] + '](' + source['url'] + ')' if source['url'] else source['title']
        out += ['- **' + source['id'] + '** · ' + title + '；' + source['locator']]
    out += ['', '[人物与传承专题](../site/people/index.html)', '']
    return project_markdown('\n'.join(out))


def topic_navigation() -> str:
    return project_html('<section class="topic-line" id="topic-line-a09"><h2><a href="../index.html#line-a09">A09（学科建设与人才培养）</a></h2>'
        + '<ul><li><a href="../people/index.html">学科建设、育人故事与学术传承</a></li>'
        + '<li><a href="../people/index.html#a09-people">人物与合作角色</a></li><li><a href="../people/index.html#a09-ai-collation">AI辅助资料整理</a></li>'
        + '<li><a href="../achievements/index.html#heritage-line-a09">成果与传承汇总</a></li></ul></section>', 'topics/index.html')


def inspect_biography(root: Path) -> dict:
    errors = []
    try:
        for name, expected in [('site/' + ROUTE, render_page(root)), (DOCUMENT, render_document(root))]:
            if (root / name).read_bytes() != expected.encode('utf-8'):
                errors.append('A09 display differs from its historical source: ' + name)
        for route in ['index.html', 'achievements/index.html']:
            source = (root / 'site' / route).read_text('utf-8')
            if render_overview(root, route) not in source:
                errors.append('A09 overview differs from source: ' + route)
        if render_inventory_summary(root) not in (root / 'site/achievements/index.html').read_text('utf-8'):
            errors.append('A09 inventory summary differs from source')
        if topic_navigation() not in (root / 'site/topics/index.html').read_text('utf-8'):
            errors.append('A09 topic navigation differs from source')
    except (KeyError, ValueError, OSError) as error:
        errors.append(str(error))
    return {'status': 'failed' if errors else 'passed', 'errors': errors}


def write(root: Path) -> None:
    for route in ['index.html', 'achievements/index.html']:
        path = root / 'site' / route
        text = path.read_bytes().decode('utf-8')
        text, count = re.subn(r'<article class="case" id="line-a09">.*?</article>', lambda _: render_overview(root, route), text, flags=re.S)
        if count != 1:
            raise ValueError('A09 requires its one existing overview per route')
        if route.startswith('achievements/'):
            text, count = re.subn(r'<article class="heritage-card" id="heritage-line-a09">.*?</article>', lambda _: render_inventory_summary(root), text, flags=re.S)
            if count != 1:
                raise ValueError('A09 requires its existing historical inventory card')
        path.write_bytes(text.encode('utf-8'))
    path = root / 'site/topics/index.html'
    text, count = re.subn(r'<section class="topic-line" id="topic-line-a09">.*?</section>', lambda _: topic_navigation(), path.read_bytes().decode('utf-8'), flags=re.S)
    if count != 1:
        raise ValueError('A09 requires its existing topic-navigation section')
    path.write_bytes(text.encode('utf-8'))
    (root / 'site/people').mkdir(exist_ok=True)
    (root / 'site' / ROUTE).write_bytes(render_page(root).encode('utf-8'))
    (root / DOCUMENT).write_bytes(render_document(root).encode('utf-8'))
    from render_heritage import load_content, render_inventory_markdown, DOCUMENT as HERITAGE_DOCUMENT
    heritage, sources = load_content(root)
    (root / HERITAGE_DOCUMENT).write_bytes(render_inventory_markdown(heritage, sources, root).encode('utf-8'))


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
