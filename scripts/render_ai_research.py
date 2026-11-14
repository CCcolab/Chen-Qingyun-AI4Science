"""Render the eight-line AI research guide from its separate source registry.

Default: inspect source labels, static rendering, review status and local links.
--write: generate the second-level page and document, then replace only the two
authorized home-page marker blocks. No source fetching or scientific execution.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
CONTENT = 'content/ai-research-section.v1.json'
PAGE = 'site/research/index.html'
DOCUMENT = 'docs/AI_RESEARCH_zh-CN.md'
HOME = 'site/index.html'
REPOSITORY = 'https://github.com/CCcolab/Chen-Qingyun-AI4Science/blob/main/'
LINE_IDS = tuple('A'+str(n).zfill(2) for n in range(1, 9))
MARKERS = ('AI_RESEARCH_HOME', 'AI_RESEARCH_FUTURE')

# The typography, paper, green header and card treatment follow the existing
# source-archive topic pages. Styles are static and do not read or copy payloads.
PAGE_CSS = """:root{color-scheme:light;--ink:#172b29;--muted:#506660;--accent:#176e62;--paper:#f6f5ef;--line:#d6e0d9;--serif:Georgia,'Songti SC','STSong',serif}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--paper);color:var(--ink);font-family:system-ui,-apple-system,'Microsoft YaHei',sans-serif;line-height:1.8}a{color:#155d55;text-underline-offset:.18em;overflow-wrap:anywhere}a:focus-visible{outline:3px solid #c97932;outline-offset:3px}.wrap{max-width:1120px;margin:auto;padding:0 28px}header{background:#173b37;color:#f2f4eb;padding:42px 0}header a{color:#c9e7d8}header h1{text-wrap:balance;font-family:var(--serif);font-size:clamp(2rem,5vw,3.3rem);line-height:1.22;margin:.3em 0}header p{max-width:800px;margin:.5em 0}.eyebrow{text-transform:uppercase;letter-spacing:.14em;font-size:.76rem;color:#bcd7c9}.skip{position:absolute;left:-9999px;top:0;background:#fff;z-index:10;padding:12px}.skip:focus{left:12px}.index{padding:28px 0 22px}.index h2{font:700 1.5rem/1.4 var(--serif)}.index ol{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px 28px;padding-left:24px}.index a{font-weight:600}.intro-note{border-left:3px solid #aa7545;padding:8px 20px;color:var(--muted);max-width:88ch}.research-line{background:#fffefa;border:1px solid var(--line);border-radius:12px;margin:22px 0;padding:clamp(22px,4vw,48px);scroll-margin-top:20px;min-width:0}.research-line h2{font-family:var(--serif);font-size:clamp(1.5rem,3vw,2.1rem);line-height:1.4;margin:.15em 0 .6em}.research-line h3{font-size:1rem;color:var(--accent);margin:1.5em 0 .3em}.research-line p{max-width:82ch;margin:.55em 0}.research-line ul{padding-left:1.2em}.status{display:inline-block;background:#e4f0e9;color:#155448;font-size:.82rem;padding:.22em .8em;border-radius:30px;font-weight:700}.record-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin-top:12px}.record{background:#f3f5ef;border:1px solid var(--line);padding:18px;min-width:0}.record h4{font-size:1rem;line-height:1.6;margin:0 0 8px}.record p{font-size:.93rem}.links{display:flex;flex-wrap:wrap;gap:8px 18px;font-size:.92rem}.prior-work{border-top:1px solid var(--line);margin-top:18px;padding-top:12px}.prior-work h4{font-size:1rem;margin:8px 0}.prior-work .citation{font-size:.9rem;color:var(--muted)}.evidence{border-top:1px solid var(--line);margin-top:22px;padding-top:4px;color:var(--muted)}.top{font-size:.9rem}footer{padding:30px 0 45px;color:var(--muted);font-size:.9rem}@media(max-width:640px){.wrap{padding:0 18px}header{padding:30px 0}.index ol,.record-grid{grid-template-columns:1fr}.research-line{border-radius:8px}}@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}"""
HOME_CSS = """#research .ai-line-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}#research .ai-line-card{padding:22px 24px;background:var(--white);border:1px solid var(--line);min-width:0}#research .ai-line-card h3{font-size:21px;line-height:1.5;margin:0 0 10px}#research .ai-line-card p{font-size:14px;color:var(--soft);margin:0 0 12px}#research .ai-line-card a{font-size:14px;color:var(--teal);font-weight:650}#research .ai-reading-note{font-size:14px;color:var(--soft);margin:22px 0 0}@media(max-width:640px){#research .ai-line-grid{grid-template-columns:1fr}}"""


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def label(line: dict) -> str:
    return line['id']+'（'+line['name']+'）'


def anchor(line: dict) -> str:
    return 'ai-'+line['id'].lower()


def nonempty(value, where: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError('Expected nonempty text: '+where)
    return value


def all_link_records(data: dict):
    for line in data['lines']:
        yield from line['source_links']
        for record in line['records']:
            yield from record['links']
        for work in line.get('prior_work', []):
            yield from work['links']


def load_content(root: Path = ROOT) -> dict:
    data = json.loads((root/CONTENT).read_text('utf-8'))
    canonical = json.loads((root/'content/achievement-labels.v1.json').read_text('utf-8'))['labels']
    for field in ('title', 'date', 'intro', 'scope_note', 'review_note', 'future_note'):
        nonempty(data.get(field), field)
    if data.get('schema_version') != '1.0':
        raise ValueError('Unsupported AI research source schema')
    if (data.get('scientific_review_status') != 'review_required'
            or data.get('release_eligible') is not False
            or data.get('m0_status') != 'paused'):
        raise ValueError('AI research must retain pending review, release_eligible=false and M0 paused')
    if not isinstance(data.get('lines'), list) or tuple(row.get('id') for row in data['lines']) != LINE_IDS:
        raise ValueError('Expected exactly eight ordered scientific lines A01 through A08')
    heritage = data.get('heritage', {})
    if heritage.get('id') != 'A09' or heritage.get('name') != canonical['A09']:
        raise ValueError('Academic heritage must remain separate with its canonical name')
    for line in data['lines']:
        ident = line['id']
        if line.get('name') != canonical[ident]:
            raise ValueError('Noncanonical scientific-line name: '+ident)
        for field in ('home_summary', 'question', 'ai_role', 'next_step', 'future_question'):
            nonempty(line.get(field), ident+'.'+field)
        if re.search(r'\d', line['home_summary']):
            raise ValueError('Home summaries must describe AI roles without numerical progress: '+ident)
        if not isinstance(line.get('boundaries'), list) or not line['boundaries']:
            raise ValueError('Missing scientific boundaries: '+ident)
        for boundary in line['boundaries']:
            nonempty(boundary, ident+'.boundary')
        if not line.get('records') or not line.get('source_links'):
            raise ValueError('Every line needs existing records and historical-source entry points: '+ident)
        for record in line['records']:
            for field in ('title', 'summary'):
                nonempty(record.get(field), ident+'.record.'+field)
            if not record.get('links'):
                raise ValueError('Existing records need concrete record links: '+ident)
        for work in line.get('prior_work', []):
            for field in ('source_id', 'title', 'authors', 'citation', 'scope'):
                nonempty(work.get(field), ident+'.prior_work.'+field)
            if not work.get('links'):
                raise ValueError('Prior work needs its original citation link')
    first = data['lines'][0]
    if not all(word in first['records'][0]['summary'] for word in ('647–653', '七页', '俄文原刊')):
        raise ValueError('Current seven-page English first-report reading scope is missing')
    titles = ' '.join(record['title'] for record in first['records'])
    if not all(word in titles for word in ('计量', '物性', 'M0保持暂停')):
        raise ValueError('Three distinct existing A01 research branches must be visible')
    prior = data['lines'][5].get('prior_work', [])
    if {work['source_id'] for work in prior} != {'CQ-R21', 'CQ-R25'}:
        raise ValueError('A06 must preserve the two attributed prior-research citations')
    for item in all_link_records(data):
        for field in ('title', 'url', 'kind'):
            nonempty(item.get(field), 'link.'+field)
        url = item['url']
        if any(character.isspace() or ord(character) < 32 for character in url):
            raise ValueError('Invalid whitespace/control character in URL')
        parsed = urlsplit(url)
        if item['kind'] == 'repo':
            if not url.startswith(REPOSITORY):
                raise ValueError('Repository records require the full configured GitHub URL')
        elif item['kind'] == 'site':
            if parsed.scheme or parsed.netloc or not url.startswith('../'):
                raise ValueError('Research-page historical links must use parent-relative site paths')
        elif item['kind'] == 'external':
            if parsed.scheme != 'https' or not parsed.netloc:
                raise ValueError('External citations require HTTPS')
        else:
            raise ValueError('Unknown link kind: '+item['kind'])
    return data


def links_html(links: list[dict]) -> str:
    return '<p class="links">'+''.join(
        '<a href="'+esc(item['url'])+'">'+esc(item['title'])+' →</a>' for item in links)+'</p>'


def render_home(data: dict) -> str:
    cards = []
    for line in data['lines']:
        cards.append('<article class="ai-line-card"><h3>'+esc(label(line))+'</h3><p>'
            +esc(line['home_summary'])+'</p><a href="research/index.html#'+anchor(line)
            +'">研究资料与问题 →</a></article>')
    heritage = data['heritage']
    return ('<!-- AI_RESEARCH_HOME:BEGIN -->\n'
        '<section class="shell-section band" id="research"><style>'+HOME_CSS+'</style><div class="wrap">'
        '<div class="section-head"><div><div class="kicker">AI FOR ARCHIVES AND INQUIRY</div><h2>'
        +esc(data['title'])+'</h2></div><p>从原始文献、化学对象与具体数据出发，说明AI方法怎样服务于八条科研成果线。</p></div>'
        '<div class="ai-line-grid">'+''.join(cards)+'</div>'
        '<p class="ai-reading-note">已开展的资料核读、数值重放与模型探索按实际记录列示；可用方法与拟议问题分别说明。具体结果、适用范围和待核证据见各线研究页，未来工作先查新并论证方法，再决定是否开展。</p>'
        '<p class="ai-reading-note">'+esc(label(heritage))+'作为独立的学术传承线，另见'
        '<a href="#line-a09">人物与传承</a>。</p>'
        '<p class="ai-reading-note"><a href="research/index.html">进入AI辅助研究资料页 →</a></p></div></section>\n'
        '<!-- AI_RESEARCH_HOME:END -->')


def render_future(data: dict) -> str:
    return ('<!-- AI_RESEARCH_FUTURE:BEGIN -->\n'
        '<section class="shell-section" id="d05"><div class="wrap"><div class="section-head"><div>'
        '<div class="kicker">QUESTIONS AND EXISTING WORK</div><h2>从已有研究提出后续问题</h2></div>'
        '<p>先梳理已有专业研究，再核对原始材料与可检验的问题；候选设想须经过查新和方法论证。</p></div>'
        '<p>陈试剂的既有机理研究与近期回顾均保留原作者和核查层级，具体对照与待核事项见'
        '<a href="research/index.html#ai-a06">'+esc(label(data['lines'][5]))+'研究资料</a>。</p>'
        '</div></section>\n<!-- AI_RESEARCH_FUTURE:END -->')


def render_page(data: dict) -> str:
    sections = []
    for line in data['lines']:
        records = ''.join('<div class="record"><h4>'+esc(row['title'])+'</h4><p>'
            +esc(row['summary'])+'</p>'+links_html(row['links'])+'</div>' for row in line['records'])
        prior = ''
        if line.get('prior_work'):
            prior = '<div class="prior-work"><h4>已有专业研究：保留原作者归属</h4>'
            for work in line['prior_work']:
                prior += ('<div><h4>'+esc(work['source_id']+' · '+work['title'])+'</h4><p>'
                    +esc(work['authors'])+'</p><p class="citation">'+esc(work['citation'])
                    +'</p><p>'+esc(work['scope'])+'</p>'+links_html(work['links'])+'</div>')
            prior += '</div>'
        sections.append('<section class="research-line" id="'+anchor(line)+'" aria-labelledby="'
            +anchor(line)+'-title"><span class="status">研究资料与问题</span><h2 id="'
            +anchor(line)+'-title">'+esc(label(line))+'</h2>'
            '<h3>科学问题</h3><p>'+esc(line['question'])+'</p>'
            '<h3>AI怎样辅助</h3><p>'+esc(line['ai_role'])+'</p>'
            '<h3>已有资料与结果</h3><div class="record-grid">'+records+'</div>'+prior
            +'<h3>待核事项与边界</h3><ul>'+''.join('<li>'+esc(row)+'</li>' for row in line['boundaries'])
            +'</ul><p><b>下一步先补的证据：</b>'+esc(line['next_step'])+'</p>'
            '<p><b>候选后续问题：</b>'+esc(line['future_question'])+'</p>'
            '<div class="evidence"><h3>史料与成果入口</h3>'+links_html(line['source_links'])
            +'<p class="top"><a href="#research-index">返回八条成果线目录 ↑</a></p></div></section>')
    heritage = data['heritage']
    index = ''.join('<li><a href="#'+anchor(line)+'">'+esc(label(line))+'</a></li>' for line in data['lines'])
    return ('<!DOCTYPE html>\n<html lang="zh-CN"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<meta name="description" content="沿八条科研成果线了解AI辅助原文整理、数据核对与后续问题研究的作用、现有记录和科学边界。">'
        '<title>'+esc(data['title'])+'｜陈庆云院士学术成就与传承</title><style>'+PAGE_CSS+'</style>'
        '</head><body><a class="skip" href="#main">跳至研究资料正文</a><header><div class="wrap">'
        '<div class="eyebrow">有机氟化学研究与传承 / AI FOR ARCHIVES AND INQUIRY</div>'
        '<h1>'+esc(data['title'])+'</h1><p>'+esc(data['intro'])+'</p>'
        '<nav aria-label="研究资料导航"><a href="../index.html#research">返回首页</a> · '
        '<a href="../topics/index.html">历史专题目录</a> · <a href="../achievements/index.html#heritage-inventory">成果与传承资料</a>'
        '</nav></div></header><main class="wrap" id="main" data-review-status="review_required" '
        'data-release-eligible="false" data-m0-status="paused"><nav class="index" id="research-index" aria-label="八条科研成果线">'
        '<h2>沿八条科研成果线阅读</h2><ol>'+index+'</ol></nav><div class="intro-note">'
        '<p>'+esc(data['scope_note'])+'</p><p>'+esc(data['review_note'])+'</p>'
        '<p>现代噁唑酮模型M0保持暂停，既有阶段记录保留。'+esc(data['future_note'])+'</p>'
        '<p><a href="'+esc(heritage['url'])+'">'+esc(label(heritage))+'</a>：'+esc(heritage['note'])
        +'</p></div>'+''.join(sections)+'</main><footer><div class="wrap">'
        '<p>历史工作归陈庆云院士及原作者、合作者；后续研究与平台整理分别说明来源。资料状态截至'
        +esc(data['date'])+'。</p><p><a href="../index.html">返回平台首页</a> · '
        '<a href="'+REPOSITORY+DOCUMENT+'">研究资料说明</a></p></div></footer></body></html>\n')


def markdown_links(links: list[dict], *, source_context: bool = False) -> str:
    # Markdown lives in docs/, so site links use the deployed Pages URL.
    items = []
    for item in links:
        url = item['url']
        if item['kind'] == 'site':
            url = 'https://cccolab.github.io/Chen-Qingyun-AI4Science/'+url[3:]
        items.append('['+item['title']+']('+url+')')
    return ' · '.join(items)


def render_document(data: dict) -> str:
    rows = ['# '+data['title'], '', '资料状态日期：'+data['date']+'。', '', data['intro'], '',
        '[打开八条科研成果线研究资料页](https://cccolab.github.io/Chen-Qingyun-AI4Science/research/index.html)', '',
        data['scope_note'], '', data['review_note'], '',
        '平台新增整理与分析：`scientific_review_status=review_required`；`release_eligible=false`；`m0_status=paused`。既有M0阶段档案保留，不自动续算。', '',
        data['future_note'], '', label(data['heritage'])+'作为独立学术传承线，另见[人物与传承](https://cccolab.github.io/Chen-Qingyun-AI4Science/index.html#line-a09)。', '']
    for line in data['lines']:
        rows += ['## '+label(line), '', '**科学问题：**'+line['question'], '', '**AI怎样辅助：**'+line['ai_role'], '', '### 已有资料与结果', '']
        for record in line['records']:
            rows += ['**'+record['title']+'。**'+record['summary'], '', markdown_links(record['links']), '']
        for work in line.get('prior_work', []):
            rows += ['**'+work['source_id']+' · '+work['title']+'。**'+work['authors']+'，'+work['citation'], '', work['scope'], '', markdown_links(work['links']), '']
        rows += ['### 待核事项与边界', '']+['- '+row for row in line['boundaries']]
        rows += ['', '**下一步先补的证据：**'+line['next_step'], '', '**候选后续问题：**'+line['future_question'], '', '### 史料与成果入口', '', markdown_links(line['source_links']), '']
    rows += ['## 维护与静态一致性检查', '',
        '内容源为仓库中的`content/ai-research-section.v1.json`，网页不嵌入源JSON。`scripts/render_ai_research.py`生成二级研究资料页、本说明及首页两个指定区块，保留各线原始史料入口。', '',
        '运行`python -B scripts/render_ai_research.py`检查八条成果线、规范名称、静态生成一致性、审阅状态和可解析链接；`--write`仅更新约定的展示文件与首页标记区块。检查不联网、不运行化学计算，也不代替科学审阅。', '']
    return '\n'.join(rows)


def marker_block(source: str, marker: str) -> str:
    begin, end = '<!-- '+marker+':BEGIN -->', '<!-- '+marker+':END -->'
    if source.count(begin) != 1 or source.count(end) != 1:
        raise ValueError('Expected exactly one home marker pair: '+marker)
    left, right = source.index(begin), source.index(end)
    if right <= left:
        raise ValueError('Reversed home marker pair: '+marker)
    return source[left:right+len(end)]


def replace_home(source: str, data: dict) -> str:
    for marker, rendered in zip(MARKERS, (render_home(data), render_future(data))):
        source = source.replace(marker_block(source, marker), rendered, 1)
    return source


class PageLinks(HTMLParser):
    def __init__(self, source: str):
        super().__init__(convert_charrefs=True)
        self.ids = Counter()
        self.links = []
        self.json_payloads = 0
        self.feed(source)
        self.close()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('id'):
            self.ids[attrs['id']] += 1
        if tag == 'a' and attrs.get('href'):
            self.links.append(attrs['href'])
        if tag == 'script' and attrs.get('type') == 'application/json':
            self.json_payloads += 1


def check_link(root: Path, page: str, url: str, generated: dict[str, str]) -> str:
    parsed = urlsplit(url)
    if parsed.scheme or parsed.netloc:
        if parsed.scheme != 'https' or not parsed.netloc:
            raise ValueError('Unsafe URL in '+page+': '+url)
        if url.startswith(REPOSITORY):
            relative = unquote(urlsplit(url[len(REPOSITORY):]).path)
            target = (root/relative).resolve()
            if not target.is_relative_to(root.resolve()) or (not target.is_file() and relative not in generated):
                raise ValueError('Repository record does not resolve locally: '+url)
            return 'repository_record_resolved_locally'
        return 'external_citation_not_fetched'
    if parsed.query:
        raise ValueError('Unexpected local query string: '+url)
    target = (root/page).parent/unquote(parsed.path) if parsed.path else root/page
    target = target.resolve()
    site = (root/'site').resolve()
    if not target.is_relative_to(site):
        raise ValueError('Site link leaves site directory: '+url)
    if target.is_dir():
        target /= 'index.html'
    relative = target.relative_to(root.resolve()).as_posix()
    if relative in generated:
        source = generated[relative]
    elif target.is_file():
        source = target.read_text('utf-8')
    else:
        raise ValueError('Missing site link target in '+page+': '+url)
    if parsed.fragment and PageLinks(source).ids[unquote(parsed.fragment)] != 1:
        raise ValueError('Missing or duplicate linked anchor in '+page+': '+url)
    return 'site_target_and_anchor_resolved'


def inspect_ai_research(root: Path = ROOT) -> dict:
    """Inspect publication consistency and links without fetching or computing."""
    root = Path(root)
    report = {'status': 'failed', 'content_path': CONTENT, 'errors': [],
        'scientific_review_status': 'review_required', 'release_eligible': False,
        'm0_status': 'paused', 'line_records': 0, 'page_checks': [], 'link_checks': [],
        'fact_review_performed': False, 'source_URLs_fetched': False,
        'new_quantum_calls': 0, 'model_API_calls': 0, 'network_calls': 0,
        'files_written': 0, 'source_JSON_embedded': False}
    try:
        content_bytes = (root/CONTENT).read_bytes()
        data = load_content(root)
        report.update(line_records=len(data['lines']), line_ids=[row['id'] for row in data['lines']],
            canonical_labels=True, A09_heritage_separate=True,
            content_sha256=hashlib.sha256(content_bytes).hexdigest())
        expected = {PAGE: render_page(data), DOCUMENT: render_document(data)}
        home = (root/HOME).read_bytes().decode('utf-8')
        expected[HOME] = replace_home(home, data)
        for path, rendered in expected.items():
            actual = (root/path).read_bytes() if (root/path).is_file() else None
            equal = actual == rendered.encode('utf-8')
            report['page_checks'].append({'path': path, 'equal': equal})
            if not equal:
                report['errors'].append('Saved display differs from AI research source: '+path)
        parsed = PageLinks(expected[PAGE])
        if parsed.json_payloads:
            raise ValueError('Research guide must not embed its source JSON')
        if any(count != 1 for count in parsed.ids.values()):
            raise ValueError('Duplicate identities in research page')
        if any(parsed.ids[anchor(line)] != 1 for line in data['lines']):
            raise ValueError('Missing or duplicated research-line section')
        for attribute in ('data-review-status="review_required"', 'data-release-eligible="false"', 'data-m0-status="paused"'):
            if attribute not in expected[PAGE]:
                raise ValueError('Research page lost its review or paused-state marker')
        target_pages = {PAGE: expected[PAGE], HOME: expected[HOME]}
        blocks = {PAGE: expected[PAGE], HOME: render_home(data)+render_future(data)}
        for page, source in blocks.items():
            for url in dict.fromkeys(PageLinks(source).links):
                state = check_link(root, page, url, target_pages)
                report['link_checks'].append({'page': page, 'url': url, 'status': state})
        if (root/CONTENT).read_bytes() != content_bytes:
            raise ValueError('Source registry changed during read-only inspection')
        report['source_references_resolved'] = True
    except (OSError, ValueError, KeyError, TypeError) as error:
        report['errors'].append(str(error))
    report['status'] = 'passed' if not report['errors'] else 'failed'
    return report


def write(root: Path = ROOT) -> dict:
    """Generate only the page, document and two authorized home marker blocks."""
    root = Path(root)
    data = load_content(root)
    source_home = (root/HOME).read_bytes().decode('utf-8')
    planned = {PAGE: render_page(data), DOCUMENT: render_document(data),
        HOME: replace_home(source_home, data)}
    # Resolve every generated website link before changing any display file.
    for page in (PAGE, HOME):
        source = planned[page] if page == PAGE else render_home(data)+render_future(data)
        for url in dict.fromkeys(PageLinks(source).links):
            check_link(root, page, url, planned)
    changed = []
    for relative, source in planned.items():
        path = root/relative
        payload = source.encode('utf-8')
        if not path.is_file() or path.read_bytes() != payload:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)
            changed.append(relative)
    report = inspect_ai_research(root)
    report.update(files_written=len(changed), written_paths=changed)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Generate page/document and replace the two authorized home marker blocks')
    args = parser.parse_args()
    try:
        report = write(ROOT) if args.write else inspect_ai_research(ROOT)
    except (OSError, ValueError, KeyError, TypeError) as error:
        report = {'status': 'failed', 'errors': [str(error)], 'network_calls': 0, 'new_quantum_calls': 0, 'model_API_calls': 0}
    print(json.dumps({'mode': 'write' if args.write else 'check', **report}, ensure_ascii=False))
    return 0 if report['status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
