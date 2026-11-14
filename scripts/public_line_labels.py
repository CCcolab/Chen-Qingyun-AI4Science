"""Describe public achievement references while preserving raw research IDs."""
from __future__ import annotations

import argparse
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
LABEL_PATH = 'content/achievement-labels.v1.json'
LABELS = json.loads((ROOT/LABEL_PATH).read_text('utf-8'))['labels']
ALIASES = {key: [value] for key, value in LABELS.items()}
ALIASES['A01'] += ['全氟酮化学早期研究：六氟丙酮与双酚AF', '全氟酮化学早期研究', '全氟酮化学']
ALIASES['A03'] += ['全氟叔丁基（PFtB）早期研究', 'PFtB 早期研究', 'PFtB早期研究']
ALIASES['A04'] += ['F-53 铬雾抑制剂']
ALIASES['A07'] += ['单电子转移与 C–Cl 活化']
NAMED_ALIASES = {key: list(values) for key, values in ALIASES.items()}
NAMED_ALIASES['A01'] += ['六氟丙酮与双酚 AF', '六氟丙酮与双酚AF']
NAMED_ALIASES['A06'] += ['陈试剂与三氟甲基化 · 磺酸酯与二氟卡宾',
                         '陈试剂、磺酸酯与二氟卡宾',
                         '磺酸酯、二氟卡宾与三氟甲基化（陈试剂）',
                         '磺酸酯与二氟卡宾', '陈试剂与三氟甲基化']
TOKEN = re.compile(r'(?<![A-Za-z0-9_-])A0[1-9](?![A-Za-z0-9_-])')
RANGE = re.compile(r'(?<![A-Za-z0-9_-])A01\s*[—–－-]\s*A09(?![A-Za-z0-9_-])')
VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
DOCUMENTS = ('README.md', 'research/a01/README.md', 'docs/ACADEMIC_ACHIEVEMENTS_zh-CN.md',
             'docs/PLATFORM_PURPOSE_zh-CN.md', 'docs/PLATFORM_ROADMAP_zh-CN.md',
             'docs/CHEN_REAGENT_ACHIEVEMENT_zh-CN.md', 'docs/A01_FIRST_REPORT_zh-CN.md')


def reference(identifier: str) -> str:
    return identifier+'（'+LABELS[identifier]+'）'


def display_text(value: str) -> str:
    value = RANGE.sub('九条成果线', value)
    # Normalize existing named references before adding names to bare ones.
    for identifier, aliases in NAMED_ALIASES.items():
        names = '|'.join(re.escape(a) for a in sorted(set(aliases), key=len, reverse=True))
        pattern = r'(?<![A-Za-z0-9_-])'+identifier+r'(?![A-Za-z0-9_-])[ \t]*(?:[·｜|：:—–-][ \t]*)?(?:'+names+r')'
        def named(match):
            suffix = ' · 陈试剂' if identifier == 'A06' and '陈试剂' in match.group() else ''
            return reference(identifier)+suffix
        value = re.sub(pattern, named, value)
        # This also normalizes pages already projected before an alias was added.
        pattern = re.escape(reference(identifier))+r'[ \t]*(?:[·｜|：:—–-][ \t]*)?(?:'+names+r')'
        value = re.sub(pattern, named, value)
    def expand(match):
        identifier = match.group()
        tail = value[match.end():]
        if tail.startswith('（'+LABELS[identifier]+'）'):
            return identifier
        return reference(identifier)
    value = TOKEN.sub(expand, value)
    stripped = value.strip()
    for identifier, aliases in ALIASES.items():
        if stripped in aliases:
            return value.replace(stripped, LABELS[identifier], 1)
    return value


class Projector(HTMLParser):
    def __init__(self, source: str):
        super().__init__(convert_charrefs=False)
        self.source, self.stack, self.edits = source, [], []
        self.offsets = [0]
        for line in source.splitlines(keepends=True):
            self.offsets.append(self.offsets[-1]+len(line))
        begin, end = '<!-- A01_PUBLIC_PROGRESS_BEGIN -->', '<!-- A01_PUBLIC_PROGRESS_END -->'
        a, b = source.find(begin), source.find(end)
        self.frozen = (a, b+len(end)) if a >= 0 and b >= a else (-1, -1)
        self.feed(source)
        self.close()

    def position(self):
        line, column = self.getpos()
        return self.offsets[line-1]+column

    def opaque(self, position):
        return self.frozen[0] <= position < self.frozen[1] or any(
            tag in {'script','style','code','pre'} for tag in self.stack)

    def handle_starttag(self, tag, attrs):
        position = self.position()
        if not self.opaque(position):
            raw = self.get_starttag_text()
            pattern = re.compile(r'\b(aria-label|title|alt)\s*=\s*([\"\x27])(.*?)\2', re.S)
            for match in pattern.finditer(raw):
                old = match.group(3)
                new = display_text(old)
                if new != old:
                    self.edits.append((position+match.start(3), position+match.end(3), new))
        if tag not in VOID:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag in self.stack:
            index = len(self.stack)-1-self.stack[::-1].index(tag)
            del self.stack[index:]

    def handle_data(self, value):
        position = self.position()
        if self.opaque(position):
            return
        # Bare numbering is meaningful in a table's explicit ID column.
        if self.stack and self.stack[-1] == 'td' and value.strip() in LABELS:
            return
        new = display_text(value)
        if new != value:
            self.edits.append((position, position+len(value), new))

    def result(self):
        result = self.source
        previous = len(result)+1
        for start, end, value in sorted(self.edits, reverse=True):
            if end > previous:
                raise ValueError('Overlapping achievement label edits')
            result = result[:start]+value+result[end:]
            previous = start
        return result


def _combine_card_headings(source: str) -> str:
    """Place each line ID and name in one heading, leaving dates in the side."""
    pattern = re.compile(r'(<article class="case" id="line-(a0[1-9])"><div class="case-side">)(.*?)(</div><div class="case-main"><h3>)(.*?)(</h3>)', re.S)
    def main_card(match):
        identifier = match.group(2).upper()
        period = re.sub(r'^'+identifier+r'(?:（'+re.escape(LABELS[identifier])+r'）)?\s*[·｜|：:—–-]?\s*', '', match.group(3))
        title = reference(identifier)
        if identifier == 'A06' and '陈试剂' in match.group(5):
            title += ' · 陈试剂'
        return match.group(1)+period+match.group(4)+title+match.group(6)
    source = pattern.sub(main_card, source)
    pattern = re.compile(r'(<article class="heritage-card" id="heritage-line-(a0[1-9])">)<p class="heritage-meta">.*?</p><h3>.*?</h3>', re.S)
    return pattern.sub(lambda match: match.group(1)+'<h3>'+reference(match.group(2).upper())+'</h3>', source)


def project_html(source: str, route: str) -> str:
    if route == 'pftb/index.html':
        return source  # Local AI task IDs in this scientific dataset are separate.
    return Projector(_combine_card_headings(source)).result()


def project_markdown(source: str) -> str:
    rows, fenced, historical = [], False, False
    for line in source.splitlines(keepends=True):
        if '<details>' in line:
            historical = True  # Preserve quoted historical model records in README.
        if line.lstrip().startswith('```'):
            fenced = not fenced
            rows.append(line)
            continue
        if fenced or historical:
            rows.append(line)
            continue
        cells = line.split('|')
        if len(cells) >= 4 and cells[1].strip() in LABELS:
            identifier = cells[1].strip()
            cells[2] = ' '+LABELS[identifier]+' '
            rows.append('|'.join(cells))
        else:
            # URLs and inline code carry source identities, not public labels.
            parts = re.split(r'(`[^`]*`|\]\([^)]*\))', line)
            rows.append(''.join(part if i % 2 else display_text(part) for i,part in enumerate(parts)))
    return ''.join(rows)


def inspect_line_labels(root: Path) -> dict:
    errors, pages = [], []
    for path in sorted((root/'site').rglob('*.html')):
        route = path.relative_to(root/'site').as_posix()
        original = path.read_text('utf-8')
        if project_html(original, route) != original:
            errors.append('Public achievement references are not descriptive: '+route)
        pages.append(route)
    for name in DOCUMENTS:
        original = (root/name).read_text('utf-8')
        if project_markdown(original) != original:
            errors.append('Public document references are not descriptive: '+name)
    return {'status': 'failed' if errors else 'passed', 'pages': len(pages),
            'documents': len(DOCUMENTS), 'labels': LABELS, 'errors': errors,
            'raw_scientific_data_changed': False, 'M0_resumed': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    if args.write:
        for path in sorted((ROOT/'site').rglob('*.html')):
            route = path.relative_to(ROOT/'site').as_posix()
            old = path.read_bytes()
            new = project_html(old.decode('utf-8'), route).encode('utf-8')
            if new != old: path.write_bytes(new)
        for name in DOCUMENTS:
            path = ROOT/name
            old = path.read_bytes()
            new = project_markdown(old.decode('utf-8')).encode('utf-8')
            if new != old: path.write_bytes(new)
    report = inspect_line_labels(ROOT)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report['status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
