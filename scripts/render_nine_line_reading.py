"""Render a biography-led academic reading guide from existing public sources."""
from __future__ import annotations

from copy import deepcopy
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path, PurePosixPath
import re

CONTENT = 'content/nine-line-reading.v1.json'
DOCUMENT = 'docs/ACADEMIC_ACHIEVEMENTS_zh-CN.md'
SITE = 'https://cccolab.github.io/Chen-Qingyun-AI4Science/'
REPO = 'https://github.com/CCcolab/Chen-Qingyun-AI4Science/blob/main/'


def load(root: Path) -> dict:
    data = json.loads((root/CONTENT).read_bytes())
    labels = json.loads((root/'content/achievement-labels.v1.json').read_bytes())['labels']
    if (data.get('schema_version'), data.get('scientific_review_status'), data.get('release_eligible'),
            data.get('m0_status'), data.get('model_training_status')) != ('1.0', 'review_required', False, 'paused', 'not_started'):
        raise ValueError('Reading guide must retain its historical/AI scope')
    if [r['id'] for r in data['lines']] != list(labels):
        raise ValueError('Reading guide requires all nine canonical lines exactly once')
    for row in data['lines']:
        if row['name'] != labels[row['id']] or not row['source_ids'] or not row['links']:
            raise ValueError('Reading card needs a canonical name, sources and topic links')
        for key in ('question', 'contribution', 'cooperation', 'source_note'):
            if not isinstance(row[key], str) or not row[key].strip():
                raise ValueError('Incomplete academic reading card: '+key)
        for name in [row['document'], *row['source_documents']]:
            relative = PurePosixPath(name)
            if relative.is_absolute() or '..' in relative.parts or '\\' in name or not (root/name).is_file():
                raise ValueError('Unknown public source document: '+name)
        for link in row['links']:
            path = link['path'].split('#')[0]
            if not path or '..' in PurePosixPath(path).parts or not (root/'site'/path).is_file():
                raise ValueError('Unknown historical topic: '+link['path'])
    if re.search(r'private-sources|file://|[CD]:[\\/]|原始证据待核清单|现阶段待查事项统计', json.dumps(data, ensure_ascii=False)):
        raise ValueError('Private tracking information cannot enter the reading guide')
    return data


def label(row: dict) -> str:
    return row['id']+'（'+row['name']+'）'


def render_guide(root: Path) -> str:
    data = load(root)
    cards = []
    for row in data['lines']:
        # A09 already has a concise, attributed heritage card; retain it exactly.
        if row['id'] == 'A09':
            from render_a09_biography import render_inventory_summary
            cards.append(render_inventory_summary(root))
            continue
        links = ' · '.join('<a href="../'+escape(x['path'], quote=True)+'">'+escape(x['label'])+' →</a>' for x in row['links'])
        cards.append('<article class="heritage-card" id="heritage-line-'+row['id'].lower()+'">'
            + '<h3>'+escape(label(row))+'</h3><p><b>科学问题：</b>'+escape(row['question'])+'</p>'
            + '<p><b>具体贡献：</b>'+escape(row['contribution'])+'</p>'
            + '<p><b>合作与研究接续：</b>'+escape(row['cooperation'])+'</p>'
            + '<p class="heritage-locator">出处：'+escape(row['source_note'])+'</p>'
            + '<p>'+links+'</p><p class="heritage-locator"><a href="'+REPO+escape(row['document'], quote=True)
            + '">原文定位、署名与科学意义</a></p></article>')
    return ('<section id="heritage-inventory" class="wrap heritage-section"><h2>'+escape(data['title'])+'</h2>'
        + '<p>'+escape(data['intro'])+'</p><div class="heritage-grid">'+''.join(cards)+'</div>'
        + '<p>'+escape(data['history_identity'])+'</p><p>'+escape(data['ai_identity'])
        + ' <a href="../research/index.html">进入AI辅助资料整理与研究 →</a></p></section>')


def display_sources(data: dict, guide: dict) -> list[dict]:
    rows = deepcopy(data['sources'])
    if set(guide['source_display_notes']) != {r['id'] for r in rows}:
        raise ValueError('The source overview must retain all eleven source identities')
    for row in rows:
        row.update(guide['source_display_notes'][row['id']])
    return rows


def render_source_overview(data: dict, sources: dict, root: Path) -> str:
    from render_heritage import source_anchor, public_text, safe_url
    guide = load(root)
    cards = []
    for row in display_sources(data, guide):
        title = escape(row['title'])
        if row['url']:
            title = '<a href="'+escape(safe_url(row['url'], row['id']), quote=True)+'" rel="noopener noreferrer">'+title+'</a>'
        cards.append('<article class="heritage-card" id="'+source_anchor(row['id'])+'"><h3>'
            +escape(row['id'])+' · '+title+'</h3><p class="heritage-meta">'+escape(row['kind'])
            +'</p><p>定位：'+escape(public_text(row['locator']))+'</p><p>'+escape(row['note'])+'</p></article>')
    # Preserve the original registered collection verbatim as the embedded record.
    payload = json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False).replace('&', '\\u0026').replace('<', '\\u003c').replace('>', '\\u003e')
    return ('<section id="heritage-sources" class="wrap heritage-section"><h2>参考资料与出处</h2>'
        +'<p>传记作为研究道路、合作与育人故事的主线；原论文、机构报道和数据库各按资料性质使用。具体学术成果与原文定位见各专题。</p>'
        +'<div class="heritage-grid">'+''.join(cards)+'</div>'
        +'<p>历史成就归陈先生及实际参与者；平台AI辅助阅读、核校与研究在独立资料页说明。</p>'
        +'<script id="heritage-content" type="application/json">\n'+payload+'\n</script></section>')


def render_document(root: Path) -> str:
    from render_heritage import load_content, public_text
    from public_line_labels import project_markdown
    guide = load(root)
    original, sources = load_content(root)
    out = ['# 陈庆云院士学术成就与合作资料', '', guide['intro'], '', '## 九条成果与传承线', '']
    for row in guide['lines']:
        if row['id'] == 'A09':
            from render_a09_biography import render_inventory_markdown_summary
            out += render_inventory_markdown_summary(root)
            continue
        out += ['### '+label(row), '', '**科学问题：**'+row['question'], '', '**具体贡献：**'+row['contribution'], '',
                '**合作与研究接续：**'+row['cooperation'], '', '出处：'+row['source_note'], '',
                ' · '.join('['+link['label']+']('+SITE+link['path']+')' for link in row['links'])
                +' · [原文定位与署名]('+row['document'].split('/')[-1]+')', '']
    out += ['## 人物与合作故事', '']
    for story in original['stories']:
        out += ['### '+story['title'], '', story['text'], '', '资料性质：'+story['source_identity'], '',
                '出处：'+story['locator']+'；'+'、'.join(story['source_refs'])+'。', '']
    out += ['## 参考资料', '']
    for source in display_sources(original, guide):
        title = source['title']
        if source['url']:
            title = '['+title+']('+source['url']+')'
        out += ['### '+source['id']+' · '+title, '', source['kind']+'；定位：'+public_text(source['locator'])+'。', '', source['note'], '']
    out += ['## 历史成果与平台AI辅助研究', '', guide['history_identity'], '', guide['ai_identity'], '',
            '平台新增AI分析保持review_required、release_eligible=false。M0继续暂停，未启动模型后训练。', '']
    return project_markdown('\n'.join(out))


class Ids(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])


def inspect_reading(root: Path) -> dict:
    errors = []
    try:
        data = load(root)
        from public_line_labels import project_html
        summary = (root/'site/achievements/index.html').read_text('utf-8')
        home = (root/'site/index.html').read_text('utf-8')
        original = json.loads((root/'content/heritage-20261114.v2.json').read_bytes())
        if project_html(render_guide(root), 'achievements/index.html') not in summary:
            errors.append('Nine-line guide differs from source rendering')
        if project_html(render_source_overview(original, {}, root), 'index.html') not in home:
            errors.append('Source overview differs from source rendering')
        if (root/DOCUMENT).read_text('utf-8') != render_document(root):
            errors.append('Academic guide document differs from source rendering')
        for html in (summary, home):
            parsed = Ids()
            parsed.feed(html)
            if len(parsed.ids) != len(set(parsed.ids)):
                errors.append('Reading update introduced duplicate anchors')
        for row in data['lines']:
            if summary.count('id="heritage-line-'+row['id'].lower()+'"') != 1:
                errors.append('A reading route is missing or duplicated: '+row['id'])
    except (ValueError, KeyError, OSError, TypeError) as error:
        errors.append(str(error))
    return {'status':'failed' if errors else 'passed', 'errors':errors, 'academic_lines':8, 'heritage_lines':1,
            'scientific_review_status':'review_required', 'release_eligible':False,
            'M0_resumed':False, 'model_training_started':False}
