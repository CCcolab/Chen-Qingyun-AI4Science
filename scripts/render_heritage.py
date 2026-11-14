"""Render the bounded 2026-11-14 historical-heritage content and inventory.

Default: check existing marker blocks and the generated inventory document.
--write: replace only the five existing marker blocks and that document.
No marker insertion, scientific-data change, network, model API or QM backend.
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
from urllib.parse import quote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
CONTENT = 'content/heritage-20261114.v1.json'
DOCUMENT = 'docs/HERITAGE_INVENTORY_20261114_zh-CN.md'
PAGE_MARKERS = {
    'index.html': ('HERITAGE_LIFE', 'HERITAGE_STORIES', 'HERITAGE_SOURCES'),
    'achievements/index.html': ('HERITAGE_INVENTORY', 'HERITAGE_STORIES_ALL'),
}
LINE_IDS = {'A'+str(index).zfill(2) for index in range(1, 10)}
SOURCE_ID = re.compile(r'HERITAGE-S[0-9]{2,}')


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def text(value, location: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError('Expected nonempty text: '+location)
    return value


def text_list(value, location: str, *, nonempty=False) -> list:
    if not isinstance(value, list) or (nonempty and not value):
        raise ValueError('Expected text list: '+location)
    for index, item in enumerate(value):
        text(item, location+'['+str(index)+']')
    return value


def safe_url(value, location: str) -> str | None:
    if value is None:
        return None
    text(value, location)
    if any(character.isspace() or ord(character) < 32 for character in value):
        raise ValueError('Whitespace/control characters in source URL: '+location)
    parsed = urlsplit(value)
    if (parsed.scheme != 'https' or not parsed.hostname or parsed.username
            or parsed.password or '<' in value or '>' in value):
        raise ValueError('Only HTTPS or null source URLs are accepted: '+location)
    return value


def _records(value, location: str, *, nonempty=False) -> list:
    if (not isinstance(value, list) or (nonempty and not value)
            or not all(isinstance(item, dict) for item in value)):
        raise ValueError('Expected object list: '+location)
    return value


def _unique_ids(rows: list, location: str, key='id') -> None:
    identifiers = [text(row.get(key), location+'.'+key) for row in rows]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError('Duplicate identities: '+location)
    if any(any(character.isspace() for character in value) for value in identifiers):
        raise ValueError('Whitespace in logical identity: '+location)


def source_title(source: dict) -> str:
    return next((str(source[key]) for key in ('title', 'formal_title', 'display_title')
                 if source.get(key)), str(source['id']))


def validate_content(data: dict, legacy_sources: dict | list) -> dict:
    """Return a resolved source index; validate shape and refs, not truth claims."""
    if not isinstance(data, dict) or data.get('schema_version') != '1.0' or data.get('date') != '2026-11-14':
        raise ValueError('Expected the fixed historical content schema/date')
    legacy = legacy_sources.get('sources') if isinstance(legacy_sources, dict) else legacy_sources
    _records(legacy, 'legacy sources', nonempty=True)
    _unique_ids(legacy, 'legacy sources')
    if len(legacy) != 51:
        raise ValueError('The unchanged original source register must contain 51 identities')
    index = {row['id']: row for row in legacy}
    for row in legacy:
        safe_url(row.get('url'), 'legacy source '+row['id'])
    book = data.get('book')
    if not isinstance(book, dict):
        raise ValueError('Missing book metadata')
    for key in ('title', 'file_name', 'edition_note'):
        text(book.get(key), 'book.'+key)
    if isinstance(book.get('authors'), list):
        text_list(book['authors'], 'book.authors', nonempty=True)
    else:
        text(book.get('authors'), 'book.authors')
    if not isinstance(book.get('sha256'), str) or not re.fullmatch(r'[0-9a-f]{64}', book['sha256']):
        raise ValueError('Book identity requires a lowercase SHA256')
    for key in ('page_count', 'printed_page_to_pdf_offset'):
        value = book.get(key)
        if not isinstance(value, int) or isinstance(value, bool) or value < (1 if key == 'page_count' else 0):
            raise ValueError('Invalid book page metadata: '+key)
    text_list(book.get('reading_scope'), 'book.reading_scope', nonempty=True)
    sources = _records(data.get('sources'), 'sources', nonempty=True)
    _unique_ids(sources, 'sources')
    legacy_ids = set(index)
    for row in sources:
        identifier = row['id']
        if not SOURCE_ID.fullmatch(identifier) or identifier in index:
            raise ValueError('New sources require a separate unique HERITAGE-S namespace')
        for key in ('title', 'kind', 'locator', 'note'):
            text(row.get(key), identifier+'.'+key)
        safe_url(row.get('url'), identifier+'.url')
        refs = text_list(row.get('legacy_source_ids'), identifier+'.legacy_source_ids')
        if not set(refs) <= legacy_ids:
            raise ValueError('Unknown original source identity in '+identifier)
        index[identifier] = row

    def refs(row: dict, location: str, *, nonempty=False):
        values = text_list(row.get('source_refs'), location+'.source_refs', nonempty=nonempty)
        missing = set(values)-set(index)
        if missing:
            raise ValueError('Unresolved source references at '+location+': '+', '.join(sorted(missing)))
        text(row.get('locator'), location+'.locator')

    biography = _records(data.get('biography'), 'biography', nonempty=True)
    _unique_ids(biography, 'biography')
    for row in biography:
        for key in ('period', 'title', 'text'):
            text(row.get(key), 'biography '+row['id']+'.'+key)
        refs(row, 'biography '+row['id'], nonempty=True)
    stories = _records(data.get('stories'), 'stories', nonempty=True)
    _unique_ids(stories, 'stories')
    for row in stories:
        for key in ('title', 'theme', 'text', 'source_identity', 'remaining_gap'):
            text(row.get(key), 'story '+row['id']+'.'+key)
        text_list(row.get('people'), 'story '+row['id']+'.people', nonempty=True)
        if not set(text_list(row.get('line_ids'), 'story '+row['id']+'.line_ids')) <= LINE_IDS:
            raise ValueError('Unknown stable line identity in story '+row['id'])
        if not isinstance(row.get('featured'), bool):
            raise ValueError('Story featured flag must be explicit boolean')
        refs(row, 'story '+row['id'], nonempty=True)
    lines = _records(data.get('lines'), 'lines', nonempty=True)
    _unique_ids(lines, 'lines', 'line_id')
    if len(lines) != 9 or {row['line_id'] for row in lines} != LINE_IDS:
        raise ValueError('The inventory must contain exactly the nine stable A01-to-A09 lines')
    for row in lines:
        for key in ('title', 'contribution', 'next_document', 'ai_status'):
            text(row.get(key), row['line_id']+'.'+key)
        for number, item in enumerate(_records(row.get('materials'), row['line_id']+'.materials', nonempty=True)):
            text(item.get('text'), row['line_id']+'.materials.text')
            text(item.get('status'), row['line_id']+'.materials.status')
            refs(item, row['line_id']+'.materials['+str(number)+']')
        text_list(row.get('gaps'), row['line_id']+'.gaps', nonempty=True)
    gaps = _records(data.get('source_gaps'), 'source_gaps')
    _unique_ids(gaps, 'source_gaps')
    for row in gaps:
        for key in ('title', 'detail', 'current_treatment'):
            text(row.get(key), 'source gap '+row['id']+'.'+key)
        refs(row, 'source gap '+row['id'])
    scope = data.get('scope')
    if not isinstance(scope, dict):
        raise ValueError('Missing historical/AI scope statements')
    for key in ('history_identity', 'AI_identity', 'm0_status'):
        text(scope.get(key), 'scope.'+key)
    return index


def load_content(root: Path = ROOT) -> tuple[dict, dict]:
    data = json.loads((root/CONTENT).read_bytes())
    legacy = json.loads((root/'site/data/public-sources.json').read_bytes())
    return data, validate_content(data, legacy)


def source_anchor(identifier: str) -> str:
    if SOURCE_ID.fullmatch(identifier):
        return 'heritage-source-'+identifier.removeprefix('HERITAGE-').lower()
    return 'source-'+identifier.lower()


def render_references(refs: list, sources: dict, *, prefix='') -> str:
    links = [f'<a href="{esc(prefix+"#"+quote(source_anchor(value), safe="-"))}" title="{esc(source_title(sources[value]))}">[{esc(value)}]</a>'
             for value in refs]
    return '<span class="heritage-refs">'+' '.join(links)+'</span>' if links else ''


def _style(identifier: str) -> str:
    return '<style id="'+identifier+'">\n'+'''/* Existing-page historical cards; no viewport-width layout. */
.heritage-section{max-width:100%;min-width:0;margin:2rem auto;overflow-wrap:anywhere}
.heritage-section>h2{font-size:clamp(28px,3.4vw,40px);margin:.3em 0 .6em}
.heritage-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1rem;max-width:100%;min-width:0}
.heritage-card{min-width:0;max-width:100%;padding:1.1rem;border:1px solid #d9e2df;border-radius:14px;background:var(--card,#fff);overflow-wrap:anywhere}
.heritage-card h3,.heritage-card h4{margin:.15rem 0 .65rem;line-height:1.45}
.heritage-card p{margin:.5rem 0;line-height:1.8}
.heritage-card ul{padding-left:1.3rem;margin:.55rem 0}
.heritage-card li{margin:.4rem 0;line-height:1.7}
.heritage-meta,.heritage-locator{font-size:.9em;color:#526560;line-height:1.75}
.heritage-refs{font-size:.85em;white-space:normal;overflow-wrap:anywhere}
.heritage-refs a{display:inline-block;margin-right:.25em}
.heritage-tag{display:inline-block;border:1px solid #c4d6ce;border-radius:6px;padding:.08rem .4rem;margin:.1rem .25rem .1rem 0;font-size:.8em;color:#34574b}
.heritage-section details{margin:.8rem 0;min-width:0;max-width:100%}
.heritage-section summary{cursor:pointer;font-weight:600;line-height:1.7}
.heritage-boundary{border-left:3px solid #6e8d7d;padding:.65rem .9rem;background:#f4f7f5;line-height:1.8}
@media(max-width:720px){.heritage-grid{grid-template-columns:minmax(0,1fr)}.heritage-card{padding:.9rem}}
'''+'\n</style>'


def _locator(row: dict, sources: dict, *, prefix='') -> str:
    return '<p class="heritage-locator">出处定位：'+esc(row['locator'])+' '+render_references(row['source_refs'], sources, prefix=prefix)+'</p>'


def _boundary(data: dict) -> str:
    return '<div class="heritage-boundary"><p>'+esc(data['scope']['history_identity'])+'</p><p>'+esc(data['scope']['AI_identity'])+'</p></div>'


def render_life(data: dict, sources: dict) -> str:
    cards = []
    for row in data['biography']:
        cards.append('<article class="heritage-card"><p class="heritage-meta">'+esc(row['period'])+'</p><h3>'+esc(row['title'])+'</h3><p>'+esc(row['text'])+'</p>'+_locator(row, sources)+'</article>')
    return _style('heritage-home-style')+'\n<section id="biography" class="heritage-section" aria-label="生平与学术历程"><h2>生平与学术历程</h2><p>'+esc(data['scope']['history_identity'])+'</p><div class="heritage-grid">'+''.join(cards)+'</div></section>'


def _story_card(row: dict, sources: dict, *, prefix='') -> str:
    people = '、'.join(row['people'])
    tags = ''.join('<span class="heritage-tag">'+esc(value)+'</span>' for value in row['line_ids'])
    return ('<article class="heritage-card" id="heritage-story-'+esc(row['id'].lower())+'"><p class="heritage-meta">'+esc(row['theme'])+'</p><h3>'+esc(row['title'])+'</h3><p class="heritage-meta">人物：'+esc(people)+'</p><p>'+esc(row['text'])+'</p>'+tags+'<p class="heritage-meta">资料性质：'+esc(row['source_identity'])+'</p>'+_locator(row, sources, prefix=prefix)+'<details><summary>仍待补齐的材料</summary><p>'+esc(row['remaining_gap'])+'</p></details></article>')


def render_featured_stories(data: dict, sources: dict) -> str:
    cards = ''.join(_story_card(row, sources) for row in data['stories'] if row['featured'])
    if not cards:
        cards = '<p>尚无达到本次编辑选择条件的故事。</p>'
    return '<section id="heritage-stories" class="wrap heritage-section"><h2>人物与合作的故事</h2><p>故事分别标示传记叙述、口述回忆或转引的资料性质，保留参与者与待补原件。</p><div class="heritage-grid">'+cards+'</div><p><a href="achievements/index.html#heritage-stories-all">查看全部故事与出处</a></p></section>'


def render_sources(data: dict, sources: dict) -> str:
    rows = []
    for row in data['sources']:
        title = esc(row['title'])
        if row['url'] is not None:
            title = '<a href="'+esc(safe_url(row['url'], row['id']))+'" rel="noopener noreferrer">'+title+'</a>'
        rows.append('<article class="heritage-card" id="'+esc(source_anchor(row['id']))+'"><h3>'+esc(row['id'])+' · '+title+'</h3><p class="heritage-meta">'+esc(row['kind'])+'</p><p>定位：'+esc(row['locator'])+'</p><p>'+esc(row['note'])+'</p>'+('<p>关联原登记：'+render_references(row['legacy_source_ids'], sources)+'</p>' if row['legacy_source_ids'] else '')+'</article>')
    gaps = []
    for row in data['source_gaps']:
        gaps.append('<article class="heritage-card"><h4>'+esc(row['title'])+'</h4><p>'+esc(row['detail'])+'</p><p>当前处理：'+esc(row['current_treatment'])+'</p>'+_locator(row, sources)+'</article>')
    book = data['book']
    authors = '、'.join(book['authors']) if isinstance(book['authors'], list) else book['authors']
    reading = '<ul>'+''.join('<li>'+esc(value)+'</li>' for value in book['reading_scope'])+'</ul>'
    payload = json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False).replace('&', '\\u0026').replace('<', '\\u003c').replace('>', '\\u003e')
    return ('<section id="heritage-sources" class="wrap heritage-section"><h2>本次资料来源与证据缺口</h2><p>补充资料使用独立 HERITAGE-S 编号；原有51条来源登记及编号保持原样。</p><details><summary>本次阅读范围与书本身份</summary><p>'+esc(authors)+'：《'+esc(book['title'])+'》。'+esc(book['edition_note'])+'</p><p class="heritage-meta">本机文件身份：'+esc(book['file_name'])+'；SHA256 '+esc(book['sha256'])+'；PDF共'+esc(book['page_count'])+'页。正文页码映射的偏移量为'+esc(book['printed_page_to_pdf_offset'])+'页。</p>'+reading+'</details><div class="heritage-grid">'+''.join(rows)+'</div><details><summary>具体缺口及当前处理</summary><div class="heritage-grid">'+''.join(gaps)+'</div></details><details><summary>历史资料与新增AI工作的关系</summary>'+_boundary(data)+'<p>'+esc(data['scope']['m0_status'])+'</p></details><script id="heritage-content" type="application/json">\n'+payload+'\n</script></section>')


def render_inventory(data: dict, sources: dict) -> str:
    cards = []
    for row in sorted(data['lines'], key=lambda value: value['line_id']):
        materials = []
        for item in row['materials']:
            materials.append('<li><span class="heritage-tag">'+esc(item['status'])+'</span>'+esc(item['text'])+_locator(item, sources, prefix='../index.html')+'</li>')
        gaps = ''.join('<li>'+esc(value)+'</li>' for value in row['gaps'])
        cards.append('<article class="heritage-card" id="heritage-line-'+row['line_id'].lower()+'"><p class="heritage-meta">'+row['line_id']+'</p><h3>'+esc(row['title'])+'</h3><p>'+esc(row['contribution'])+'</p><details><summary>现有材料及来源定位</summary><ul>'+''.join(materials)+'</ul></details><h4>明确缺口</h4><ul>'+gaps+'</ul><p><strong>优先补齐资料：</strong>'+esc(row['next_document'])+'</p><p class="heritage-meta">AI工作状态：'+esc(row['ai_status'])+'</p></article>')
    return _style('heritage-achievements-style')+'\n<section id="heritage-inventory" class="wrap heritage-section"><h2>九条成果与传承线：资料盘点</h2>'+_boundary(data)+'<div class="heritage-grid">'+''.join(cards)+'</div></section>'


def render_all_stories(data: dict, sources: dict) -> str:
    return '<section id="heritage-stories-all" class="wrap heritage-section"><h2>全部人物与合作故事</h2><p>以下为历史资料整理，各则均保留资料性质、页码或定位与尚缺原件。</p><div class="heritage-grid">'+''.join(_story_card(row, sources, prefix='../index.html') for row in data['stories'])+'</div></section>'


def _md(value) -> str:
    result = str(value).replace('\\', '\\\\').replace('<', '&lt;').replace('>', '&gt;')
    return re.sub(r'([`*\[\]])', r'\\\1', result).replace('\r\n', '\n').replace('\n', ' ')


def _md_refs(refs: list, sources: dict) -> str:
    return '；'.join(_md(value)+'（'+_md(source_title(sources[value]))+'）' for value in refs) if refs else '暂无可回链来源'


def render_inventory_markdown(data: dict, sources: dict) -> str:
    book = data['book']
    authors = '、'.join(book['authors']) if isinstance(book['authors'], list) else book['authors']
    rows = ['# 陈庆云院士纪念与传承资料盘点', '', '资料日期：'+_md(data['date'])+'。本文件由历史资料数据生成，不执行计算。', '',
        '## 资料身份与阅读范围', '', _md(authors)+'：《'+_md(book['title'])+'》。'+_md(book['edition_note']), '',
        '本机文件：'+_md(book['file_name'])+'；SHA256 `'+book['sha256']+'`；PDF '+str(book['page_count'])+'页，正文页码映射偏移量 '+str(book['printed_page_to_pdf_offset'])+'。', '']
    rows += ['- '+_md(value) for value in book['reading_scope']]
    rows += ['', '## 生平与学术历程', '']
    for row in data['biography']:
        rows += ['### '+_md(row['period'])+' · '+_md(row['title']), '', _md(row['text']), '',
            '出处：'+_md_refs(row['source_refs'], sources)+'；定位：'+_md(row['locator'])+'。', '']
    rows += ['## 九条成果与传承线', '']
    for row in sorted(data['lines'], key=lambda value: value['line_id']):
        rows += ['### '+row['line_id']+' · '+_md(row['title']), '', _md(row['contribution']), '', '现有材料：', '']
        for item in row['materials']:
            rows += ['- **'+_md(item['status'])+'**：'+_md(item['text'])+'；出处：'+_md_refs(item['source_refs'], sources)+'；定位：'+_md(item['locator'])+'。']
        rows += ['', '明确缺口：', '']+['- '+_md(value) for value in row['gaps']]
        rows += ['', '优先补齐资料：'+_md(row['next_document']), '', 'AI工作状态：'+_md(row['ai_status']), '']
    rows += ['## 人物与合作故事', '']
    for row in data['stories']:
        rows += ['### '+_md(row['title']), '', '主题：'+_md(row['theme'])+'；关联：'+_md('、'.join(row['line_ids']))+'；人物：'+_md('、'.join(row['people']))+'。', '',
            _md(row['text']), '', '资料性质：'+_md(row['source_identity']), '',
            '出处：'+_md_refs(row['source_refs'], sources)+'；定位：'+_md(row['locator'])+'。', '', '仍待补齐：'+_md(row['remaining_gap']), '']
    rows += ['## 补充来源登记', '']
    for row in data['sources']:
        rows += ['### '+row['id']+' · '+_md(row['title']), '', '资料类型：'+_md(row['kind'])+'；定位：'+_md(row['locator'])+'。', '', _md(row['note']), '']
        if row['url']:
            rows += ['来源链接：['+_md(row['title'])+'](<'+safe_url(row['url'], row['id'])+'>)', '']
        if row['legacy_source_ids']:
            rows += ['关联原有来源：'+_md_refs(row['legacy_source_ids'], sources), '']
    rows += ['## 具体证据缺口与当前处理', '']
    for row in data['source_gaps']:
        rows += ['### '+_md(row['title']), '', _md(row['detail']), '', '当前处理：'+_md(row['current_treatment']), '',
            '出处：'+_md_refs(row['source_refs'], sources)+'；定位：'+_md(row['locator'])+'。', '']
    rows += ['## 历史资料与新增AI工作分开登记', '', _md(data['scope']['history_identity']), '',
        _md(data['scope']['AI_identity']), '', _md(data['scope']['m0_status']), '',
        '原有51条来源JSON、稳定编号、PFtB正文与科研记录不由本生成器修改。新增资料不是新实验、原刊独立复验或新增量化结果。', '']
    return '\n'.join(rows)


def marker_block(name: str, body: str) -> str:
    return '<!-- '+name+'_BEGIN -->\n'+body+'\n<!-- '+name+'_END -->'


def render_blocks(data: dict, sources: dict) -> dict:
    return {
        'index.html': {
            'HERITAGE_LIFE': marker_block('HERITAGE_LIFE', render_life(data, sources)),
            'HERITAGE_STORIES': marker_block('HERITAGE_STORIES', render_featured_stories(data, sources)),
            'HERITAGE_SOURCES': marker_block('HERITAGE_SOURCES', render_sources(data, sources)),
        },
        'achievements/index.html': {
            'HERITAGE_INVENTORY': marker_block('HERITAGE_INVENTORY', render_inventory(data, sources)),
            'HERITAGE_STORIES_ALL': marker_block('HERITAGE_STORIES_ALL', render_all_stories(data, sources)),
        },
    }


def replace_marker_blocks(original: str, blocks: dict) -> str:
    """Replace existing, unique, nonoverlapping markers; never insert one."""
    spans = []
    for name, value in blocks.items():
        begin, end = '<!-- '+name+'_BEGIN -->', '<!-- '+name+'_END -->'
        if original.count(begin) != 1 or original.count(end) != 1:
            raise ValueError('Expected exactly one existing marker pair: '+name)
        left, right = original.index(begin), original.index(end)
        if right <= left:
            raise ValueError('Reversed heritage marker pair: '+name)
        spans.append((left, right+len(end), value, name))
    ordered = sorted(spans)
    if any(ordered[index][1] > ordered[index+1][0] for index in range(len(ordered)-1)):
        raise ValueError('Heritage marker blocks cannot overlap or nest')
    result = original
    for left, right, value, _ in reversed(ordered):
        result = result[:left]+value+result[right:]
    return result


class _Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids, self.scripts, self.current = [], [], None

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if values.get('id'):
            self.ids.append(values['id'])
        if tag == 'script' and values.get('id') == 'heritage-content':
            self.current = []

    def handle_data(self, data):
        if self.current is not None:
            self.current.append(data)

    def handle_endtag(self, tag):
        if tag == 'script' and self.current is not None:
            self.scripts.append(''.join(self.current)); self.current = None


def check_rendered_page(name: str, value: str, data: dict) -> None:
    parser = _Page(); parser.feed(value); parser.close()
    counts = Counter(parser.ids)
    owned = [identifier for identifier in counts if identifier.startswith('heritage-')]
    if any(counts[identifier] != 1 for identifier in owned):
        raise ValueError('Duplicate generated heritage identity in '+name)
    style_id = 'heritage-home-style' if name == 'index.html' else 'heritage-achievements-style'
    if counts[style_id] != 1:
        raise ValueError('Exactly one heritage stylesheet required in '+name)
    if name == 'index.html':
        if counts['biography'] != 1 or counts['heritage-content'] != 1:
            raise ValueError('Homepage requires one biography section and one heritage-content payload')
        if len(parser.scripts) != 1 or json.loads(parser.scripts[0]) != data:
            raise ValueError('Embedded heritage content differs from its source JSON')
        for source in data['sources']:
            if counts[source_anchor(source['id'])] != 1:
                raise ValueError('Supplemental source anchor missing or duplicated')


def inspect_heritage(root: Path = ROOT) -> dict:
    """Check saved content, five static blocks and generated MD without writes.

    This checks publication consistency and resolved source identities. It does
    not fetch citations, review historical truth or run any scientific model.
    """
    report = {'status': 'failed', 'scope': 'Historical content/source references, five static marker blocks, unique generated identities, embedded JSON and generated inventory consistency',
        'content_path': CONTENT, 'errors': [], 'page_checks': [],
        'document_check': {'path': DOCUMENT}, 'source_references_resolved': False,
        'fact_review_performed': False, 'source_URLs_fetched': False,
        'new_quantum_calls': 0, 'model_API_calls': 0, 'network_calls': 0,
        'files_written': 0, 'source_JSON_modified': False,
        'scientific_records_modified': False}
    errors = report['errors']
    try:
        content_bytes = (root/CONTENT).read_bytes()
        legacy_bytes = (root/'site/data/public-sources.json').read_bytes()
        data = json.loads(content_bytes)
        legacy = json.loads(legacy_bytes)
        sources = validate_content(data, legacy)
        groups = data['biography']+data['stories']+data['source_gaps']
        groups += [item for line in data['lines'] for item in line['materials']]
        references = [value for row in groups for value in row['source_refs']]
        references += [value for row in data['sources'] for value in row['legacy_source_ids']]
        report.update(content_sha256=hashlib.sha256(content_bytes).hexdigest(),
            original_sources_sha256=hashlib.sha256(legacy_bytes).hexdigest(),
            source_references_resolved=True, source_reference_count=len(references),
            referenced_source_ids=sorted(set(references)),
            biography_records=len(data['biography']), story_records=len(data['stories']),
            featured_stories=sum(row['featured'] for row in data['stories']),
            line_records=len(data['lines']), supplemental_sources=len(data['sources']),
            source_gaps=len(data['source_gaps']))
        blocks = render_blocks(data, sources)
        for name, names in PAGE_MARKERS.items():
            page = {'path': 'site/'+name, 'marker_checks': [],
                    'unique_generated_identities_and_payload': False}
            report['page_checks'].append(page)
            try:
                original_bytes = (root/'site'/name).read_bytes()
                original = original_bytes.decode('utf-8')
                expected = replace_marker_blocks(original, blocks[name])
                for marker in names:
                    begin, end = '<!-- '+marker+'_BEGIN -->', '<!-- '+marker+'_END -->'
                    actual = original[original.index(begin):original.index(end)+len(end)]
                    equal = actual == blocks[name][marker]
                    page['marker_checks'].append({'marker': marker, 'equal': equal})
                    if not equal:
                        errors.append('Static heritage block differs from source data: '+name+' / '+marker)
                page.update(equal=original == expected,
                    actual_sha256=hashlib.sha256(original_bytes).hexdigest(),
                    expected_sha256=hashlib.sha256(expected.encode('utf-8')).hexdigest())
                check_rendered_page(name, original, data)
                page['unique_generated_identities_and_payload'] = True
            except (OSError, ValueError, KeyError, TypeError) as error:
                errors.append('Heritage page '+name+': '+str(error))
        expected_document = render_inventory_markdown(data, sources).encode('utf-8')
        path = root/DOCUMENT
        actual_document = path.read_bytes() if path.is_file() else None
        equal = actual_document == expected_document
        report['document_check'].update(present=actual_document is not None, equal=equal,
            expected_sha256=hashlib.sha256(expected_document).hexdigest(),
            actual_sha256=hashlib.sha256(actual_document).hexdigest() if actual_document is not None else None)
        if not equal:
            errors.append('Generated heritage inventory document is absent or differs from source data: '+DOCUMENT)
        if (root/CONTENT).read_bytes() != content_bytes or (root/'site/data/public-sources.json').read_bytes() != legacy_bytes:
            errors.append('Historical content or original source-register bytes changed during inspection')
        report['static_marker_checks'] = sum(len(page['marker_checks']) for page in report['page_checks'])
    except (OSError, ValueError, KeyError, TypeError) as error:
        errors.append(str(error))
    report['status'] = 'passed' if not errors else 'failed'
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Replace existing marker blocks and generate the inventory document')
    args = parser.parse_args()
    if not args.write:
        report = inspect_heritage(ROOT)
        print(json.dumps({'mode': 'check', **report}, ensure_ascii=False))
        return 0 if report['status'] == 'passed' else 1
    try:
        data, sources = load_content()
        blocks = render_blocks(data, sources)
        planned, different = {}, []
        for name in PAGE_MARKERS:
            path = ROOT/'site'/name
            original = path.read_bytes().decode('utf-8')
            expected = replace_marker_blocks(original, blocks[name])
            check_rendered_page(name, expected, data)
            planned[path] = expected.encode('utf-8')
            if original != expected:
                different.append('site/'+name)
        document = ROOT/DOCUMENT
        planned[document] = render_inventory_markdown(data, sources).encode('utf-8')
        if not document.is_file() or document.read_bytes() != planned[document]:
            different.append(DOCUMENT)
        if args.write:
            for path, value in planned.items():
                if not path.is_file() or path.read_bytes() != value:
                    path.write_bytes(value)
        report = inspect_heritage(ROOT)
        print(json.dumps({'mode': 'write', 'changed_paths': different, **report}, ensure_ascii=False))
        return 0 if report['status'] == 'passed' else 1
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({'status': 'failed', 'error': str(error),
            'new_quantum_calls': 0, 'model_API_calls': 0, 'network_calls': 0}, ensure_ascii=False))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
