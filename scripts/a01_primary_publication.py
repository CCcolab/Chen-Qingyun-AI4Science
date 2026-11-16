"""Bounded A01 primary-literature presentation; no science release or execution."""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path, PurePosixPath
import re

MANIFEST = 'provenance/platform-presentation.v25.json'
PRESENTATION_ID = 'PLATFORM-A01-PRIMARY-READING-20261116-v25'
PREVIOUS_COMMIT = 'd4fec688029e7bfa3f826ad4efdb78457e312fbd'
PREVIOUS_MANIFEST = 'provenance/platform-presentation.v24.json'
ROUTES = ('research/index.html', 'topics/early-fluoroketones/index.html')
AI = 'content/ai-research-section.v1.json'
DOCUMENTS = ('content/ai-research-section.v1.json', 'scripts/render_ai_research.py', 'docs/AI_RESEARCH_zh-CN.md', 'scripts/render_a01_history.py', 'docs/A01_FIRST_REPORT_zh-CN.md', 'content/a01-primary-reading.v1.json', 'scripts/render_a01_primary_reading.py', 'docs/A01_PRIMARY_READING_zh-CN.md', 'scripts/a01_publication_contract.py', 'scripts/public_literature_update.py', 'scripts/a01_primary_publication.py')
PREDECESSOR_FILES = {'content/ai-research-section.v1.json': ('8816f7aab7ed0793c621c904fc819ee4738cabd55a2202f8105f13c64c59cf95', 97371), 'docs/AI_RESEARCH_zh-CN.md': ('329ce8ce5d2242cc7bd44e701dafa4db471d379e5a4048459bd20886ec9fdec6', 57707), 'site/research/index.html': ('58215eebbc449f591b832219045e39543394ed0018e85c574ec962b4e15166f4', 78885), 'scripts/render_a01_history.py': ('7633087b1694b3c19d30243e95c3b621684fb8d58545206a8ac8df90825e729c', 15842), 'docs/A01_FIRST_REPORT_zh-CN.md': ('f0b084ea67ab26a09da6f32158bc6e8e1219af46b551b8c39ed5bfb57dec9a18', 7864), 'site/topics/early-fluoroketones/index.html': ('a6da86d7f9ff0f35a5ea044252297a23e5ed71db829f2d184e3ab38a70dce9a2', 250938), 'scripts/a01_publication_contract.py': ('3497c008ed83a7737e46a81c714475586040583646bb6cf950eef0efa8800eff', 309525), 'scripts/public_literature_update.py': ('263909ad01d2fa2c9cb721f8ecbc7bb6aae238f14fdb4d352b3ee41cf6a5a650', 46361)}
PROTECTED_FILES = {'content/a01-historical-achievements.v1.json': ('f59916dd0ab0cc5d23684c102ffeaeb6936632f13975017d367ec7242408b8bd', 27827), 'content/a01-historical-achievements.v2.json': ('c27a28b6922358d52e7bde69c9c6f56df06ac20efe58affc0706c5a0b4b20db8', 39364), 'docs/A01_HISTORICAL_ACHIEVEMENTS_zh-CN.md': ('30f0d767f751088facc2811c16996f8896c64197cfef7b1e18a0e6472d185e3f', 11125), 'site/index.html': ('8b3532ee45c0fb33912f20a3bd7943043a348f10a370b9c6716e9edf3c0abf41', 257766), 'site/achievements/index.html': ('df20daf429c46e89e99085550067e8c1e9f7e283b10b7e8269f38da6a9d380ff', 95867)}
OLD_MANIFESTS = {'provenance/platform-presentation.v1.json': '1ade23238a23977b47eaa6a7dd585509fdca3e270615914292e2341721308782', 'provenance/platform-presentation.v2.json': '91434b5bc8fb51e96b604a6c6437cb363c92370347f22fcbd2a825e5498f0348', 'provenance/platform-presentation.v3.json': '2b290301102abd8cacb5a2d73f7393d8c4f851285a882a08df42eecd960ed286', 'provenance/platform-presentation.v4.json': 'cfc0bc4d29c24a846bb76ceaf3246084d406393cc7d04ec105cad539c21e120b', 'provenance/platform-presentation.v5.json': '7ac60223b0e540de62671017728acd54e66d07e8de2721006c476c8d1734bed9', 'provenance/platform-presentation.v6.json': '1077f6b2e3a78be65ea4b50e81907b629f96c9b3599fcf440493c204b33dbcf3', 'provenance/platform-presentation.v7.json': '2463a97b3bf74b629f1863892d75f36276c97bf9a111905b47cc6179b62eaa7f', 'provenance/platform-presentation.v8.json': 'ab2b362cb5c90dc4b782f8989cc127a31944c49998ee45fbded8b8a7ac77c962', 'provenance/platform-presentation.v9.json': '462fdbfe1c4bd6f0c32f39e2597764037b4562904f0acec4cce00f08c9797017', 'provenance/platform-presentation.v10.json': '65954e3ff6b484a010fa5052f5331eab55149d23a468ae354ab236462598ffd3', 'provenance/platform-presentation.v11.json': 'd6eb2a3faed6f030a28ca5b63e3f3512144c9246f39467d300fc279a967bb004', 'provenance/platform-presentation.v12.json': 'aa9efd831558b47646b687e12be30724c4b8be89a0f98ccb8d06ef56cf04e81f', 'provenance/platform-presentation.v13.json': '263b465d22b1a56b8364a0540a65f742948664f9e50e64d759543685768468cc', 'provenance/platform-presentation.v14.json': '3ea28579d130b065fb805942c5c62861d8f6cd24a0027df7fef7cdc41415750b', 'provenance/platform-presentation.v15.json': 'd21bad493ae97587c7b9493813af3393ed9ed98f5a8dfd3a8790270f7ba49aff', 'provenance/platform-presentation.v16.json': '6b975e980d176ecc481449ca5a96ffadadfecae2eb64d97dfdafb75b85b4a3c0', 'provenance/platform-presentation.v17.json': 'b635b2950e37d5387e8fb68da12109ca585833b769eec38cf25911eb86563ee1', 'provenance/platform-presentation.v18.json': '4fa6f43360d5343e119bb7b9e51e0671f1b4b4ef51ba065067459180a710dfd6', 'provenance/platform-presentation.v19.json': '1a056390024ec41126e36c8b8e6a5275415331ec6eeec524da9df8785e23d59b', 'provenance/platform-presentation.v20.json': '34814fabc405812bccc433018f8a197d181a3da9ac617f84cceda51513774b72', 'provenance/platform-presentation.v21.json': 'a353a25fc9586c3fe78de1ad42a20aee4a1c980de59eda4340df4466d9b45593', 'provenance/platform-presentation.v22.json': '3a9a746a565f7942899f5fdffc244121608e39210c7e6eb466203775dc38cae6', 'provenance/platform-presentation.v23.json': '392490c9d1ddc18942ef5b139eb094155a883f1a340e56adfc9512bfa5430a3d', 'provenance/platform-presentation.v24.json': '118a96428bf0a0fce5467fffd8861c419f97ac078aed708b6fd3b5e6318cc242'}
EXPECTED_AI_UPDATES = [{'pointer': '/lines/0/records/0/summary', 'value': '第一报英译本647–653页全部七页影印图已取得并核读；俄文原刊与专业核译仍待核。另两篇Doklady原页共八页已有AI核读，关键结构转录签认待补。传记p29的证书书影已核见，独立高清原始扫描及细字日期仍待核。 第一报与说明书的原报数据、具体化学贡献和共同署名分别呈现；这是对既有历史成果的资料展开，不作为平台新的科学发现。'}, {'pointer': '/lines/0/records/0/links', 'value': [{'title': '早期原文与分支研究说明', 'url': 'https://github.com/CCcolab/Chen-Qingyun-AI4Science/blob/main/research/a01/README.md', 'kind': 'repo'}, {'title': '第一报全文核读范围与历史证据', 'url': 'https://github.com/CCcolab/Chen-Qingyun-AI4Science/blob/main/docs/A01_FIRST_REPORT_zh-CN.md', 'kind': 'repo'}, {'title': 'A01（全氟酮化学：六氟丙酮与双酚AF）原报数据与共同贡献', 'url': '../topics/early-fluoroketones/index.html#a01-primary-records', 'kind': 'site'}]}]
NEW_FILES = ('content/a01-primary-reading.v1.json', 'scripts/render_a01_primary_reading.py', 'docs/A01_PRIMARY_READING_zh-CN.md', 'scripts/a01_primary_publication.py', 'provenance/platform-presentation.v25.json')
REVIEWED_PUBLIC_FILES = {'content/a01-primary-reading.v1.json': '606f50cef7528a3ed176b9b0ce02c13ee14d6bea802bdd224f243e2dd8478f8d', 'scripts/render_a01_primary_reading.py': '425fe6fa324ab87a94408b2e813aebaa331a82e10d9ee66552967af60caad41f', 'scripts/render_a01_history.py': '500488c6906210e68a8d1478cadc8340d59b455c1b2103d6e34de4653b08bf4b', 'scripts/render_ai_research.py': 'c4cfba4d66c616b4a04d258ec4b1f644dd8858cd2734693dd3c8efbd60ed135a', 'docs/A01_FIRST_REPORT_zh-CN.md': '6f8666b96ee0220c05266e63bf6239ec22205fd1977ce31bb8a6f488d2750071'}
PUBLIC_DISPLAYS = ('content/ai-research-section.v1.json', 'content/a01-primary-reading.v1.json', 'docs/AI_RESEARCH_zh-CN.md', 'docs/A01_FIRST_REPORT_zh-CN.md', 'docs/A01_PRIMARY_READING_zh-CN.md', 'site/research/index.html', 'site/topics/early-fluoroketones/index.html')
BASELINE_SHA256 = '5e3e70988d76ac1d777ff85ee7c1945341e2141767fc77560c6cea39eabab329'
ARCHIVE_SHA256 = 'fa9740d7a244ab4d52885600a312487869d780a82517aa0d0a401215696c4d3e'


def _sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _file(root: Path, name: str) -> Path:
    relative = PurePosixPath(name)
    path = root/name
    if (not name or relative.is_absolute() or '..' in relative.parts or '\\' in name
            or relative.as_posix() != name or path.is_symlink() or not path.is_file()
            or not path.resolve().is_relative_to(root.resolve())):
        raise ValueError('Unsafe or missing A01 primary-presentation file: '+str(name))
    return path


def _json(root: Path, name: str):
    return json.loads(_file(root, name).read_bytes())


def predecessor_bytes(root: Path, name: str) -> bytes:
    """Recover exact fixed d4fec68 bytes before replaying the immutable chain."""
    current = _file(root, name).read_bytes()
    if not (root/MANIFEST).exists():
        return current
    data = _json(root, MANIFEST)
    if not isinstance(data, dict):
        raise ValueError('A01 primary presentation requires a JSON object')
    records, pool = data.get('reversible_text_files'), data.get('reverse_text_patch_pool')
    if not isinstance(records, list) or not isinstance(pool, list):
        raise ValueError('A01 primary presentation requires exact reverse text patches')
    matches = [row for row in records if isinstance(row, dict) and row.get('path') == name]
    if not matches:
        if name in PREDECESSOR_FILES:
            raise ValueError('Missing fixed A01 primary predecessor: '+name)
        return current
    if len(matches) != 1 or name not in PREDECESSOR_FILES:
        raise ValueError('Unauthorized or duplicate A01 primary predecessor: '+name)
    row = matches[0]
    old_sha, old_size = PREDECESSOR_FILES[name]
    if (row.get('old_sha256') != old_sha or row.get('old_bytes') != old_size
            or _sha(current) != row.get('new_sha256') or len(current) != row.get('new_bytes')):
        raise ValueError('A01 primary file differs from complete old/new identities: '+name)
    edits = row.get('edits')
    if not isinstance(edits, list) or not edits:
        raise ValueError('A01 primary changes require nonempty text edits: '+name)
    chunks, cursor, old_end, delta = [], 0, 0, 0
    for edit in edits:
        if not isinstance(edit, dict) or set(edit) != {'old_offset', 'replacement'}:
            raise ValueError('Invalid A01 primary reverse text edit: '+name)
        offset, replacement = edit['old_offset'], edit['replacement']
        if (type(offset) is not int or offset < old_end or type(replacement) is not int
                or not 0 <= replacement < len(pool)):
            raise ValueError('Overlapping or invalid A01 primary reverse edit: '+name)
        pair = pool[replacement]
        if (not isinstance(pair, dict) or set(pair) != {'old', 'new'}
                or not all(isinstance(pair.get(k), str) for k in ('old', 'new'))
                or pair['old'] == pair['new']):
            raise ValueError('Invalid A01 primary replacement pool')
        before, after = pair['old'].encode('utf-8'), pair['new'].encode('utf-8')
        position = offset+delta
        if position < cursor or current[position:position+len(after)] != after:
            raise ValueError('A01 primary reverse replacement differs at exact offset: '+name)
        chunks.extend((current[cursor:position], before))
        cursor, old_end = position+len(after), offset+len(before)
        delta += len(after)-len(before)
    rebuilt = b''.join((*chunks, current[cursor:]))
    if _sha(rebuilt) != old_sha or len(rebuilt) != old_size:
        raise ValueError('A01 primary predecessor cannot be reconstructed exactly: '+name)
    return rebuilt


def _set_pointer(data, pointer: str, value):
    parts = [p.replace('~1', '/').replace('~0', '~') for p in pointer.split('/')[1:]]
    if not pointer.startswith('/') or not parts:
        raise ValueError('Invalid fixed A01 primary JSON pointer')
    parent = data
    for part in parts[:-1]:
        parent = parent[int(part)] if isinstance(parent, list) else parent[part]
    key = int(parts[-1]) if isinstance(parent, list) else parts[-1]
    parent[key] = copy.deepcopy(value)


def _binding(root: Path, name: str) -> dict:
    data = _file(root, name).read_bytes()
    return {'path': name, 'sha256': _sha(data), 'bytes': len(data)}


def apply(root: Path, entries: dict, previous_report: dict) -> tuple[dict, dict]:
    """Validate the current A01-only presentation after exact v24 replay."""
    if not (root/MANIFEST).exists():
        return entries, previous_report
    if not (root/PREVIOUS_MANIFEST).is_file():
        raise ValueError('A01 primary presentation requires its immutable v24 predecessor')
    for name, sha in OLD_MANIFESTS.items():
        if _sha(_file(root, name).read_bytes()) != sha:
            raise ValueError('Historical presentation manifest changed: '+name)
    for name, (sha, size) in PROTECTED_FILES.items():
        value = _file(root, name).read_bytes()
        if _sha(value) != sha or len(value) != size:
            raise ValueError('A01 original source or protected reference changed: '+name)
    data = _json(root, MANIFEST)
    required = {
        'schema_version': '25.0', 'presentation_id': PRESENTATION_ID,
        'publication_kind': 'platform_a01_systematic_primary_reading',
        'previous_presentation_commit': PREVIOUS_COMMIT,
        'previous_presentation': {'path': PREVIOUS_MANIFEST, 'sha256': OLD_MANIFESTS[PREVIOUS_MANIFEST]},
        'original_baseline_sha256': BASELINE_SHA256, 'original_archive_sha256': ARCHIVE_SHA256,
        'allowed_html_paths': list(ROUTES), 'added_html_paths': [], 'additions': [],
        'editorial_documents': [_binding(root, name) for name in DOCUMENTS],
        'protected_website_members': {name: {'sha256': row['sha256'], 'bytes': row['bytes']}
            for name, row in entries.items() if name not in ROUTES},
        'reconstruction_kind': 'deduplicated_exact_utf8_text_edits',
        'scientific_review_status': 'review_required', 'release_eligible': False,
        'scientific_data_unchanged': True, 'M0_resumed': False,
        'historical_achievement_independent_of_AI_review': True,
        'allowed_ai_json_pointers': [u['pointer'] for u in EXPECTED_AI_UPDATES],
        'allowed_new_files': list(NEW_FILES),
    }
    if (not isinstance(data, dict) or any(data.get(k) != v for k, v in required.items())
            or any(data.get(k) is not required[k] for k in ('release_eligible',
                'scientific_data_unchanged', 'M0_resumed', 'historical_achievement_independent_of_AI_review'))
            or any(type(data.get(k)) is not int or data[k] != 0 for k in ('new_quantum_calls', 'new_model_API_calls'))
            or not isinstance(data.get('authorization'), str) or not data['authorization'].strip()):
        raise ValueError('Unsupported bounded A01 primary presentation v25')
    records, pool = data.get('reversible_text_files'), data.get('reverse_text_patch_pool')
    if (not isinstance(records, list) or not isinstance(pool, list) or not pool
            or any(not isinstance(row, dict) for row in records)
            or len(records) != len(PREDECESSOR_FILES)
            or {row.get('path') for row in records} != set(PREDECESSOR_FILES)
            or len({row.get('path') for row in records}) != len(records)
            or any(not isinstance(row.get('edits'), list) or not row['edits'] or any(
                not isinstance(edit, dict) or type(edit.get('replacement')) is not int
                for edit in row['edits']) for row in records)):
        raise ValueError('A01 primary presentation has an unauthorized predecessor file set')
    if {edit['replacement'] for row in records for edit in row['edits']} != set(range(len(pool))):
        raise ValueError('A01 primary presentation requires exactly its used replacement pool')
    for name, (sha, size) in PREDECESSOR_FILES.items():
        old = predecessor_bytes(root, name)
        if _sha(old) != sha or len(old) != size or old == _file(root, name).read_bytes():
            raise ValueError('A01 primary predecessor differs from fixed d4fec68: '+name)
    expected = json.loads(predecessor_bytes(root, AI))
    for update in EXPECTED_AI_UPDATES:
        _set_pointer(expected, update['pointer'], update['value'])
    if _json(root, AI) != expected:
        raise ValueError('A01 primary JSON changed outside its fixed A01 fields')
    for name, sha in REVIEWED_PUBLIC_FILES.items():
        if _sha(_file(root, name).read_bytes()) != sha:
            raise ValueError('A01 primary source, renderer or document differs from reviewed bytes: '+name)
    for name in PUBLIC_DISPLAYS:
        value = _file(root, name).read_text('utf-8')
        if re.search(r'(?i)private-sources|current-item-register|现阶段待查事项统计|[CD]:[\\/]', value):
            raise ValueError('A01 primary display contains private evidence or a local path: '+name)
    changes = data.get('changes')
    if (not isinstance(changes, list) or len(changes) != len(ROUTES)
            or any(not isinstance(row, dict) for row in changes)
            or {row.get('path') for row in changes} != set(ROUTES)):
        raise ValueError('A01 primary presentation may change only its two existing routes')
    updated = {name: dict(row) for name, row in entries.items()}
    json_scripts = re.compile(r'<script\b[^>]*\btype\s*=\s*["\']application/(?:ld\+)?json["\'][^>]*>.*?</script\s*>', re.I | re.S)
    for item in changes:
        route = item['path']; old_entry = entries[route]
        before = predecessor_bytes(root, 'site/'+route)
        after = _file(root, 'site/'+route).read_bytes()
        if (item.get('old_sha256') != old_entry['sha256'] or item.get('old_bytes') != old_entry['bytes']
                or _sha(before) != old_entry['sha256'] or len(before) != old_entry['bytes']
                or item.get('new_sha256') != _sha(after) or item.get('new_bytes') != len(after)
                or before == after or not isinstance(item.get('reason'), str) or not item['reason'].strip()):
            raise ValueError('A01 primary route differs from complete old/new identities: '+route)
        source, current = before.decode('utf-8'), after.decode('utf-8')
        if json_scripts.findall(source) != json_scripts.findall(current):
            raise ValueError('A01 primary presentation changed original embedded JSON: '+route)
        old_ids = re.findall(r'\bid="([^\"]+)"', source)
        new_ids = re.findall(r'\bid="([^\"]+)"', current)
        if not set(old_ids).issubset(new_ids) or len(new_ids) != len(set(new_ids)):
            raise ValueError('A01 primary presentation lost or duplicated source/navigation IDs: '+route)
        pattern = (r'<section\b[^>]*\bid="ai-a01"[^>]*>.*?</section>'
                   if route == 'research/index.html' else
                   r'<!-- A01_HISTORY_TOPIC:BEGIN -->.*?<!-- A01_HISTORY_TOPIC:END -->')
        if (len(re.findall(pattern, source, re.S)) != 1 or len(re.findall(pattern, current, re.S)) != 1
                or re.sub(pattern, '<A01-PRIMARY/>', source, flags=re.S) !=
                   re.sub(pattern, '<A01-PRIMARY/>', current, flags=re.S)):
            raise ValueError('A01 primary presentation changed outside its bounded A01 block: '+route)
        updated[route] = {**old_entry, 'sha256': _sha(after), 'bytes': len(after), 'presentation_id': PRESENTATION_ID}
    for name, expected_entry in updated.items():
        value = _file(root, 'site/'+name).read_bytes()
        if _sha(value) != expected_entry['sha256'] or len(value) != expected_entry['bytes']:
            raise ValueError('A01 primary changed an unlisted website byte: '+name)
    from render_ai_research import inspect_ai_research
    from render_a01_history import inspect_a01_history
    from render_a01_primary_reading import inspect_primary_reading
    checks = [inspect_ai_research(root), inspect_a01_history(root), inspect_primary_reading(root)]
    if any(c.get('status') != 'passed' for c in checks):
        raise ValueError('A01 primary display differs from source rendering: '+str(checks))
    report = {'path': MANIFEST, 'sha256': _sha(_file(root, MANIFEST).read_bytes()),
        'presentation_id': PRESENTATION_ID, 'publication_kind': required['publication_kind'],
        'changed_paths': list(ROUTES), 'added_paths': [],
        'previous_presentation_commit': PREVIOUS_COMMIT,
        'exact_predecessor_reconstruction': True, 'source_derived_rendering': True,
        'all_v1_v24_manifest_bytes_preserved': True, 'private_originals_not_published': True,
        'original_A01_source_and_embedded_JSON_preserved': True,
        'homepage_achievement_summary_other_lines_and_scientific_data_preserved': True,
        **{k: required[k] for k in ('scientific_review_status', 'release_eligible',
            'scientific_data_unchanged', 'M0_resumed', 'historical_achievement_independent_of_AI_review')}}
    return updated, {**report, 'presentation_chain': [*previous_report['presentation_chain'], report]}
