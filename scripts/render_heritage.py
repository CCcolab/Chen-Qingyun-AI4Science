"""Render the bounded 2026-11-14 historical-heritage content and inventory.

Default: check source-bound marker blocks and the enrichment document.
--write: replace five existing blocks, insert or update the five authorized
topic-context blocks, and generate the new document. The v1 collection and
document remain unchanged. No scientific-data change, network or QM backend.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
from public_line_labels import project_html, project_markdown
import re
from urllib.parse import quote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
CONTENT = 'content/heritage-20261114.v2.json'
DOCUMENT = 'docs/ACADEMIC_ACHIEVEMENTS_zh-CN.md'
PREVIOUS_CONTENT = 'content/heritage-20261114.v1.json'
PREVIOUS_SHA256 = 'ba2aac21a10ed38ed6a4d796c904fa6fb539afd7f2fa370fc91b4274fb54d135'
PAGE_MARKERS = {
    'index.html': ('HERITAGE_LIFE', 'HERITAGE_STORIES', 'HERITAGE_SOURCES'),
    'achievements/index.html': ('HERITAGE_INVENTORY', 'HERITAGE_STORIES_ALL'),
}
CONTEXT_PATHS = {
    'topics/fluoromonomers/index.html': 'A02',
    'topics/refrigerants/index.html': 'A05',
    'topics/perfluorosulfonates/index.html': 'A06',
    'topics/chen-reagent/index.html': 'A06',
    'topics/single-electron-transfer/index.html': 'A07',
}
LINE_IDS = {'A'+str(index).zfill(2) for index in range(1, 10)}
SOURCE_ID = re.compile(r'HERITAGE-S[0-9]{2,}')

# Apply only to narrative fields. Titles, names, quotations and the embedded
# source payload retain their original wording and identity.
PUBLIC_NARRATIVE_FIELDS = {
    'text', 'contribution', 'status', 'kind', 'note', 'ai_status', 'detail',
    'current_treatment', 'next_document', 'remaining_gap', 'source_identity',
    'locator', 'history_identity', 'AI_identity',
}
QUOTED_TEXT = re.compile(r'(《[^》]*》|“[^”]*”|‘[^’]*’|"[^"\n]*")')


def public_text(value: str) -> str:
    """Remove editorial-batch wording outside quoted passages and titles."""
    replacements = (
        ('第二版重读', '已核读'), ('已分工逐章核读', '已逐章核读'),
        ('本轮新增核见', '已核见'), ('本轮整页核见', '整页已核见'),
        ('本轮补见', '已核读'), ('本轮核读登记', '资料登记'),
        ('本轮已', '已'), ('本轮未', '尚未'), ('本轮只', '仅'),
        ('本轮仅', '仅'), ('本轮确认', '已确认'), ('本轮核读', '已核读'),
        ('本轮不续算', 'M0保持暂停'),
        ('不是本轮取得的完整专利说明书', '尚未取得完整专利说明书'),
        ('不是新取得的工艺实验报告', '不作为工艺实验报告'),
        ('全文／补充资料', '全文／支持信息（SI）'),
        ('原文和补充资料', '原文和支持信息（SI）'),
        ('平台新增AI核读', '平台AI辅助研究的核读'),
        ('平台新增机制结论', '平台AI辅助研究的机制结论'),
        ('平台新增实验验证', '平台实验验证'),
        ('平台新增实验', '平台实验'),
    )
    parts = QUOTED_TEXT.split(value)
    for index in range(0, len(parts), 2):
        part = parts[index]
        # This identifies an editorial registration, not a scientific citation.
        part = re.sub(r'^既有CQ-[RH]\d+来源的本轮核读登记。', '', part)
        for old, new in replacements:
            part = part.replace(old, new)
        parts[index] = part
    return ''.join(parts)


def public_projection(value):
    """Return display-only prose; never mutate the evidence collection."""
    value = deepcopy(value)

    def project(item):
        if isinstance(item, list):
            return [project(child) for child in item]
        if not isinstance(item, dict):
            return item
        for key, child in item.items():
            if key == 'm0_status' and child == 'M0继续暂停，仅保存此前阶段记录；本轮为历史资料补充，不开展量化计算或模型API调用。':
                item[key] = '历史资料整理与AI研究分开，M0保持暂停。'
            elif key == 'ai_status' and child == '本轮为史料整理，未登记本线已完成的复现计算或实验结果。':
                item[key] = '尚无本成果线已完成的平台复现计算或实验验证结果。'
            elif key == 'ai_status' and isinstance(child, str):
                item[key] = public_text(child).replace('本轮为史料整理', '历史资料整理')
            elif key == 'reading_scope' and isinstance(child, list):
                item[key] = [public_text(row) for row in child]
            elif key in PUBLIC_NARRATIVE_FIELDS and isinstance(child, str):
                item[key] = public_text(child)
            elif isinstance(child, (dict, list)):
                item[key] = project(child)
        return item

    return project(value)


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
    if (data.get('edition_id') != 'CQ-HERITAGE-COLLECTION-20261114-v2'
            or data.get('previous_edition') != {'path': PREVIOUS_CONTENT, 'sha256': PREVIOUS_SHA256}):
        raise ValueError('The enrichment must bind the exact immutable v1 collection')
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
        for number, item in enumerate(_records(row.get('achievement_notes'), row['line_id']+'.achievement_notes', nonempty=True)):
            location = row['line_id']+'.achievement_notes['+str(number)+']'
            for key in ('title', 'text', 'remaining_gap'):
                text(item.get(key), location+'.'+key)
            refs(item, location, nonempty=True)
        text_list(row.get('gaps'), row['line_id']+'.gaps', nonempty=True)
    contexts = _records(data.get('topic_contexts'), 'topic_contexts', nonempty=True)
    _unique_ids(contexts, 'topic_contexts', 'path')
    if {row['path'] for row in contexts} != set(CONTEXT_PATHS):
        raise ValueError('The enrichment must enumerate the five authorized topic-context pages')
    by_line, by_story = {row['line_id']: row for row in lines}, {row['id']: row for row in stories}
    for row in contexts:
        name, number = row['path'], row.get('line_id')
        if number != CONTEXT_PATHS[name]:
            raise ValueError('Topic context belongs to a different achievement line: '+name)
        indices = row.get('note_indices')
        if (not isinstance(indices, list) or len(indices) != len(set(indices))
                or any(not isinstance(n, int) or isinstance(n, bool) or not 0 <= n < len(by_line[number]['achievement_notes']) for n in indices)):
            raise ValueError('Topic context requires valid unique note indices: '+name)
        selected = text_list(row.get('story_ids'), name+'.story_ids')
        if len(selected) != len(set(selected)) or not (indices or selected):
            raise ValueError('Topic context requires unique selections and nonempty content: '+name)
        if any(identifier not in by_story or number not in by_story[identifier]['line_ids'] for identifier in selected):
            raise ValueError('Topic context selects an unknown or unrelated story: '+name)
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
    if hashlib.sha256((root/PREVIOUS_CONTENT).read_bytes()).hexdigest() != PREVIOUS_SHA256:
        raise ValueError('The previous historical collection bytes changed')
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
.heritage-achievement-notes h5{font-size:1em;margin:.9rem 0 .3rem;line-height:1.5}
.heritage-achievement-notes{border-top:1px solid #d9e2df;margin-top:1rem;padding-top:.6rem}
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
    data = public_projection(data)
    cards = []
    for row in data['biography']:
        cards.append('<article class="heritage-card"><p class="heritage-meta">'+esc(row['period'])+'</p><h3>'+esc(row['title'])+'</h3><p>'+esc(row['text'])+'</p>'+_locator(row, sources)+'</article>')
    return _style('heritage-home-style')+'\n<section id="biography" class="heritage-section" aria-label="生平与学术历程"><h2>生平与学术历程</h2><p>'+esc(data['scope']['history_identity'])+'</p><div class="heritage-grid">'+''.join(cards)+'</div></section>'


def _story_card(row: dict, sources: dict, *, prefix='') -> str:
    row = public_projection(row)
    people = '、'.join(row['people'])
    tags = ''.join('<span class="heritage-tag">'+esc(value)+'</span>' for value in row['line_ids'])
    return ('<article class="heritage-card" id="heritage-story-'+esc(row['id'].lower())+'"><p class="heritage-meta">'+esc(row['theme'])+'</p><h3>'+esc(row['title'])+'</h3><p class="heritage-meta">人物：'+esc(people)+'</p><p>'+esc(row['text'])+'</p>'+tags+'<p class="heritage-meta">资料性质：'+esc(row['source_identity'])+'</p>'+_locator(row, sources, prefix=prefix)+'<details><summary>仍待补齐的材料</summary><p>'+esc(row['remaining_gap'])+'</p></details></article>')


def render_featured_stories(data: dict, sources: dict) -> str:
    data = public_projection(data)
    cards = ''.join(_story_card(row, sources) for row in data['stories'] if row['featured'])
    if not cards:
        cards = '<p>相关故事及出处尚待整理。</p>'
    return '<section id="heritage-stories" class="wrap heritage-section"><h2>人物与合作的故事</h2><p>故事分别标示传记叙述、口述回忆或转引的资料性质，保留参与者与待补原件。</p><div class="heritage-grid">'+cards+'</div><p><a href="achievements/index.html#heritage-stories-all">查看全部故事与出处</a></p></section>'


def render_sources(data: dict, sources: dict) -> str:
    original_data = data
    data = public_projection(data)
    rows = []
    for row in data['sources']:
        title = esc(row['title'])
        if row['url'] is not None:
            title = '<a href="'+esc(safe_url(row['url'], row['id']))+'" rel="noopener noreferrer">'+title+'</a>'
        rows.append('<article class="heritage-card" id="'+esc(source_anchor(row['id']))+'"><h3>'+esc(row['id'])+' · '+title+'</h3><p class="heritage-meta">'+esc(row['kind'])+'</p><p>定位：'+esc(row['locator'])+'</p><p>'+esc(row['note'])+'</p></article>')
    gaps = []
    for row in data['source_gaps']:
        gaps.append('<article class="heritage-card"><h4>'+esc(row['title'])+'</h4><p>'+esc(row['detail'])+'</p><p>当前处理：'+esc(row['current_treatment'])+'</p>'+_locator(row, sources)+'</article>')
    book = data['book']
    authors = '、'.join(book['authors']) if isinstance(book['authors'], list) else book['authors']
    reading = '<ul>'+''.join('<li>'+esc(value)+'</li>' for value in book['reading_scope'])+'</ul>'
    payload = json.dumps(original_data, ensure_ascii=False, indent=2, allow_nan=False).replace('&', '\\u0026').replace('<', '\\u003c').replace('>', '\\u003e')
    return ('<section id="heritage-sources" class="wrap heritage-section"><h2>资料来源与待核事项</h2><p>各项资料注明来源、文献定位与待核事项。</p><details><summary>文献范围与书本信息</summary><p>'+esc(authors)+'：《'+esc(book['title'])+'》。'+esc(book['edition_note'])+'</p><p class="heritage-meta">资料文件信息：'+esc(book['file_name'])+'；SHA256 '+esc(book['sha256'])+'；PDF共'+esc(book['page_count'])+'页。正文页码映射的偏移量为'+esc(book['printed_page_to_pdf_offset'])+'页。</p>'+reading+'</details><div class="heritage-grid">'+''.join(rows)+'</div><details><summary>待核事项与当前处理</summary><div class="heritage-grid">'+''.join(gaps)+'</div></details><details><summary>历史资料与平台AI辅助研究</summary>'+_boundary(data)+'<p>'+esc(data['scope']['m0_status'])+'</p></details><script id="heritage-content" type="application/json">\n'+payload+'\n</script></section>')


def render_inventory(data: dict, sources: dict) -> str:
    data = public_projection(data)
    cards = []
    for row in sorted(data['lines'], key=lambda value: value['line_id']):
        notes = '<div class="heritage-achievement-notes"><h4>成果与合作</h4>'+''.join(
            render_achievement_note(item, sources, prefix='../index.html', heading='h5')
            for item in row['achievement_notes'])+'</div>'
        materials = []
        for item in row['materials']:
            materials.append('<li><span class="heritage-tag">'+esc(item['status'])+'</span>'+esc(item['text'])+_locator(item, sources, prefix='../index.html')+'</li>')
        gaps = ''.join('<li>'+esc(value)+'</li>' for value in row['gaps'])
        cards.append('<article class="heritage-card" id="heritage-line-'+row['line_id'].lower()+'"><p class="heritage-meta">'+row['line_id']+'</p><h3>'+esc(row['title'])+'</h3><p>'+esc(row['contribution'])+'</p>'+notes+'<details><summary>现有材料及来源定位</summary><ul>'+''.join(materials)+'</ul></details><h4>待核事项</h4><ul>'+gaps+'</ul><p><strong>待补文献：</strong>'+esc(row['next_document'])+'</p><p class="heritage-meta">平台AI辅助研究：'+esc(row['ai_status'])+'</p></article>')
    return _style('heritage-achievements-style')+'\n<section id="heritage-inventory" class="wrap heritage-section"><h2>九条成果与传承线：资料</h2>'+_boundary(data)+'<div class="heritage-grid">'+''.join(cards)+'</div></section>'


def render_all_stories(data: dict, sources: dict) -> str:
    data = public_projection(data)
    return '<section id="heritage-stories-all" class="wrap heritage-section"><h2>全部人物与合作故事</h2><p>以下为历史资料整理，各则均保留资料性质、页码或定位与尚缺原件。</p><div class="heritage-grid">'+''.join(_story_card(row, sources, prefix='../index.html') for row in data['stories'])+'</div></section>'


def render_achievement_note(row: dict, sources: dict, *, prefix='', heading='h3') -> str:
    row = public_projection(row)
    if heading not in {'h3', 'h5'}:
        raise ValueError('Unsupported achievement-note heading level')
    return ('<'+heading+'>'+esc(row['title'])+'</'+heading+'><p>'+esc(row['text'])+'</p>'
        +_locator(row, sources, prefix=prefix)+'<p class="heritage-meta">待核事项：'
        +esc(row['remaining_gap'])+'</p>')


def render_topic_context(context: dict, data: dict, sources: dict) -> str:
    data = public_projection(data)
    line = next(row for row in data['lines'] if row['line_id'] == context['line_id'])
    stories = {row['id']: row for row in data['stories']}
    cards = ['<article class="heritage-card">'+render_achievement_note(
        line['achievement_notes'][index], sources, prefix='../../index.html')+'</article>'
        for index in context['note_indices']]
    related = ''
    if context['story_ids']:
        related = '<div class="heritage-related-stories"><h3>相关合作故事</h3><ul>'+''.join(
            '<li><a href="../../achievements/index.html#heritage-story-'+esc(identifier.lower())+'">'
            +esc(stories[identifier]['title'])+'</a></li>' for identifier in context['story_ids'])+'</ul></div>'
    return (_style('heritage-context-style')+'\n<section id="heritage-context" class="heritage-section">'
        '<h2>成果与合作</h2><p>以下按'+esc(context['line_id'])+'成果线呈现传记与公开资料中的历史记录，'
        '保留参与者、来源定位及待核事项；平台AI辅助研究另行登记。</p><div class="heritage-grid">'
        +''.join(cards)+'</div>'+related+'<p><a href="../../achievements/index.html#heritage-line-'
        +esc(context['line_id'].lower())+'">查看本成果线的资料</a> · '
        '<a href="../../achievements/index.html#heritage-stories-all">查看全部合作与育人故事</a></p></section>')


def _md(value) -> str:
    result = str(value).replace('\\', '\\\\').replace('<', '&lt;').replace('>', '&gt;')
    return re.sub(r'([`*\[\]])', r'\\\1', result).replace('\r\n', '\n').replace('\n', ' ')


def _md_refs(refs: list, sources: dict) -> str:
    return '；'.join(_md(value)+'（'+_md(source_title(sources[value]))+'）' for value in refs) if refs else '暂无可回链来源'


def render_inventory_markdown(data: dict, sources: dict) -> str:
    data = public_projection(data)
    book = data['book']
    authors = '、'.join(book['authors']) if isinstance(book['authors'], list) else book['authors']
    rows = ['# 陈庆云院士学术成就与合作资料', '', '资料截至：'+_md(data['date'])+'。', '',
        '## 文献范围与书本信息', '', _md(authors)+'：《'+_md(book['title'])+'》。'+_md(book['edition_note']), '',
        '资料文件：'+_md(book['file_name'])+'；SHA256 `'+book['sha256']+'`；PDF '+str(book['page_count'])+'页，正文页码映射偏移量 '+str(book['printed_page_to_pdf_offset'])+'。', '']
    rows += ['- '+_md(value) for value in book['reading_scope']]
    rows += ['', '## 生平与学术历程', '']
    for row in data['biography']:
        rows += ['### '+_md(row['period'])+' · '+_md(row['title']), '', _md(row['text']), '',
            '出处：'+_md_refs(row['source_refs'], sources)+'；定位：'+_md(row['locator'])+'。', '']
    rows += ['## 九条成果与传承线', '']
    for row in sorted(data['lines'], key=lambda value: value['line_id']):
        rows += ['### '+row['line_id']+' · '+_md(row['title']), '', _md(row['contribution']), '', '成果与合作：', '']
        for item in row['achievement_notes']:
            rows += ['#### '+_md(item['title']), '', _md(item['text']), '',
                '出处：'+_md_refs(item['source_refs'], sources)+'；定位：'+_md(item['locator'])+'。', '',
                '待核事项：'+_md(item['remaining_gap']), '']
        rows += ['现有材料：', '']
        for item in row['materials']:
            rows += ['- **'+_md(item['status'])+'**：'+_md(item['text'])+'；出处：'+_md_refs(item['source_refs'], sources)+'；定位：'+_md(item['locator'])+'。']
        rows += ['', '待核事项：', '']+['- '+_md(value) for value in row['gaps']]
        rows += ['', '待补文献：'+_md(row['next_document']), '', '平台AI辅助研究：'+_md(row['ai_status']), '']
    rows += ['## 人物与合作故事', '']
    for row in data['stories']:
        rows += ['### '+_md(row['title']), '', '主题：'+_md(row['theme'])+'；关联：'+_md('、'.join(row['line_ids']))+'；人物：'+_md('、'.join(row['people']))+'。', '',
            _md(row['text']), '', '资料性质：'+_md(row['source_identity']), '',
            '出处：'+_md_refs(row['source_refs'], sources)+'；定位：'+_md(row['locator'])+'。', '', '仍待补齐：'+_md(row['remaining_gap']), '']
    rows += ['## 资料来源', '']
    for row in data['sources']:
        rows += ['### '+row['id']+' · '+_md(row['title']), '', '资料类型：'+_md(row['kind'])+'；定位：'+_md(row['locator'])+'。', '', _md(row['note']), '']
        if row['url']:
            rows += ['来源链接：['+_md(row['title'])+'](<'+safe_url(row['url'], row['id'])+'>)', '']
    rows += ['## 待核事项与当前处理', '']
    for row in data['source_gaps']:
        rows += ['### '+_md(row['title']), '', _md(row['detail']), '', '当前处理：'+_md(row['current_treatment']), '',
            '出处：'+_md_refs(row['source_refs'], sources)+'；定位：'+_md(row['locator'])+'。', '']
    rows += ['## 历史成果与平台AI辅助研究', '', _md(data['scope']['history_identity']), '',
        _md(data['scope']['AI_identity']), '', _md(data['scope']['m0_status']), '',
        '历史成果归原作者及合作团队；历史资料的整理不构成平台新开展的实验验证或量化结果。', '']
    return project_markdown('\n'.join(rows))


def marker_block(name: str, body: str) -> str:
    return '<!-- '+name+'_BEGIN -->\n'+body+'\n<!-- '+name+'_END -->'


def render_blocks(data: dict, sources: dict) -> dict:
    blocks = {
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
    for context in data['topic_contexts']:
        blocks[context['path']] = {'HERITAGE_CONTEXT': marker_block(
            'HERITAGE_CONTEXT', render_topic_context(context, data, sources))}
    return {name: {marker: project_html(body, name) for marker, body in markers.items()}
            for name, markers in blocks.items()}


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


def update_page(name: str, original: str, blocks: dict, *, allow_context_insert=False) -> str:
    """Only the authorized topic pages may acquire their first context block."""
    if name in CONTEXT_PATHS:
        begin, end = '<!-- HERITAGE_CONTEXT_BEGIN -->', '<!-- HERITAGE_CONTEXT_END -->'
        if begin not in original and end not in original and allow_context_insert:
            if original.count('</main>') != 1 or re.search(r'\bid=["\']heritage-context["\']', original):
                raise ValueError('Topic context requires a single main boundary and unused identity: '+name)
            return original.replace('</main>', '\n'+blocks['HERITAGE_CONTEXT']+'\n</main>', 1)
    return replace_marker_blocks(original, blocks)


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
    style_id = ('heritage-home-style' if name == 'index.html' else
                'heritage-context-style' if name in CONTEXT_PATHS else 'heritage-achievements-style')
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
    elif name in CONTEXT_PATHS and counts['heritage-context'] != 1:
        raise ValueError('Each selected topic requires one historical-context section')


def inspect_heritage(root: Path = ROOT) -> dict:
    """Check saved content, source-bound static blocks and MD without writes.

    This checks publication consistency and resolved source identities. It does
    not fetch citations, review historical truth or run any scientific model.
    """
    report = {'status': 'failed', 'scope': 'Historical content/source references, five home/inventory blocks, authorized topic contexts, unique generated identities, embedded JSON and enrichment-document consistency',
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
        data, sources = load_content(root)
        groups = data['biography']+data['stories']+data['source_gaps']
        groups += [item for line in data['lines'] for item in line['materials']]
        groups += [item for line in data['lines'] for item in line['achievement_notes']]
        references = [value for row in groups for value in row['source_refs']]
        references += [value for row in data['sources'] for value in row['legacy_source_ids']]
        report.update(content_sha256=hashlib.sha256(content_bytes).hexdigest(),
            original_sources_sha256=hashlib.sha256(legacy_bytes).hexdigest(),
            source_references_resolved=True, source_reference_count=len(references),
            referenced_source_ids=sorted(set(references)),
            biography_records=len(data['biography']), story_records=len(data['stories']),
            featured_stories=sum(row['featured'] for row in data['stories']),
            line_records=len(data['lines']), supplemental_sources=len(data['sources']),
            source_gaps=len(data['source_gaps']),
            achievement_notes=sum(len(row['achievement_notes']) for row in data['lines']),
            topic_contexts=len(data['topic_contexts']), previous_edition_preserved=True)
        blocks = render_blocks(data, sources)
        for name, rendered in blocks.items():
            page = {'path': 'site/'+name, 'marker_checks': [],
                    'unique_generated_identities_and_payload': False}
            report['page_checks'].append(page)
            try:
                original_bytes = (root/'site'/name).read_bytes()
                original = original_bytes.decode('utf-8')
                expected = update_page(name, original, rendered)
                for marker in rendered:
                    begin, end = '<!-- '+marker+'_BEGIN -->', '<!-- '+marker+'_END -->'
                    actual = original[original.index(begin):original.index(end)+len(end)]
                    equal = actual == rendered[marker]
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
    parser.add_argument('--write', action='store_true', help='Update source-bound blocks, insert authorized topic contexts and generate the new enrichment document')
    args = parser.parse_args()
    if not args.write:
        report = inspect_heritage(ROOT)
        print(json.dumps({'mode': 'check', **report}, ensure_ascii=False))
        return 0 if report['status'] == 'passed' else 1
    try:
        data, sources = load_content()
        blocks = render_blocks(data, sources)
        planned, different = {}, []
        for name, rendered in blocks.items():
            path = ROOT/'site'/name
            original = path.read_bytes().decode('utf-8')
            expected = update_page(name, original, rendered, allow_context_insert=True)
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
