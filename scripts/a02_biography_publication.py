"""Bounded biography-led A02 presentation; original research data stay unchanged."""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path, PurePosixPath
import re

MANIFEST = 'provenance/platform-presentation.v26.json'
PRESENTATION_ID = 'PLATFORM-A02-BIOGRAPHY-NARRATIVE-20261116-v26'
PREVIOUS_COMMIT = '37ed9a5008d4623be30713d3c18c48b417d10cfd'
PREVIOUS_MANIFEST = 'provenance/platform-presentation.v25.json'
ROUTES = ('research/index.html', 'topics/fluoromonomers/index.html')
AI = 'content/ai-research-section.v1.json'
DOCUMENTS = ('scripts/render_a02_history.py', 'scripts/render_heritage.py', 'docs/A02_ACADEMIC_ACHIEVEMENTS_zh-CN.md', 'content/ai-research-section.v1.json', 'docs/AI_RESEARCH_zh-CN.md', 'content/a02-biography-narrative.v1.json', 'scripts/render_a02_biography.py', 'scripts/a01_primary_publication.py', 'scripts/a01_publication_contract.py', 'scripts/a02_biography_publication.py')
PREDECESSOR_FILES = {'scripts/render_a02_history.py': ('0d598601ccbbd0064bc95b513055c32c7342459937a5504d5f7af74167be8e9c', 21602), 'scripts/render_heritage.py': ('07b1698b1c0485accd96cc0a6d6730bb164258e003737c9f370919920768f27d', 42653), 'docs/A02_ACADEMIC_ACHIEVEMENTS_zh-CN.md': ('8e714347897b88902c12b714769dee46c59f0788e8b87e82f07a3414c2a1fc85', 41787), 'content/ai-research-section.v1.json': ('6cbea7f1efeec435ebbaca9d80b39431e7fc14f9b27ecae6bf3c4847eb8d9bf4', 97792), 'docs/AI_RESEARCH_zh-CN.md': ('b2a97edbfece2aad7691eb0e18e23cc142802145a427b9569c4a14ef8176ec46', 58068), 'site/topics/fluoromonomers/index.html': ('6972664021418b4337e5bb7785cc6bd77d5d7a96968bdfd41a6a8d7812fa2fa1', 60217), 'site/research/index.html': ('1d5aaf560e21a37bcd865984207f4f931c9b8aee54533a3b3d8f0e87a732fc3c', 79210), 'scripts/a01_primary_publication.py': ('7e10bf18334117a005fced60d7110d31c04184d768c32ad4cd3e2fe80bfa1c5b', 20493), 'scripts/a01_publication_contract.py': ('7689978367a4a9c7b846fc21a191cb284d7d11f7b0a6b1759d51da2aa41c2e59', 309731)}
PROTECTED_FILES = {'content/a02-academic-achievements.v1.json': ('173ebb010d8e8797b1d40d626c0117f1b80aea77f04c3299a63d4d0cec2fc244', 54356), 'site/index.html': ('8b3532ee45c0fb33912f20a3bd7943043a348f10a370b9c6716e9edf3c0abf41', 257766), 'site/data/public-sources.json': ('94f8b9f6d0849deb9f26f75947205cfc8c4eb0973045fe958f2121237d987062', 33608), 'site/data/achievement-lines.json': ('1c9ec28bf41a7d79214e84a1c07f3bea1e0d91630dd3a88c93c39ff68a9bccec', 39768)}
OLD_MANIFESTS = {'provenance/platform-presentation.v1.json': '1ade23238a23977b47eaa6a7dd585509fdca3e270615914292e2341721308782', 'provenance/platform-presentation.v2.json': '91434b5bc8fb51e96b604a6c6437cb363c92370347f22fcbd2a825e5498f0348', 'provenance/platform-presentation.v3.json': '2b290301102abd8cacb5a2d73f7393d8c4f851285a882a08df42eecd960ed286', 'provenance/platform-presentation.v4.json': 'cfc0bc4d29c24a846bb76ceaf3246084d406393cc7d04ec105cad539c21e120b', 'provenance/platform-presentation.v5.json': '7ac60223b0e540de62671017728acd54e66d07e8de2721006c476c8d1734bed9', 'provenance/platform-presentation.v6.json': '1077f6b2e3a78be65ea4b50e81907b629f96c9b3599fcf440493c204b33dbcf3', 'provenance/platform-presentation.v7.json': '2463a97b3bf74b629f1863892d75f36276c97bf9a111905b47cc6179b62eaa7f', 'provenance/platform-presentation.v8.json': 'ab2b362cb5c90dc4b782f8989cc127a31944c49998ee45fbded8b8a7ac77c962', 'provenance/platform-presentation.v9.json': '462fdbfe1c4bd6f0c32f39e2597764037b4562904f0acec4cce00f08c9797017', 'provenance/platform-presentation.v10.json': '65954e3ff6b484a010fa5052f5331eab55149d23a468ae354ab236462598ffd3', 'provenance/platform-presentation.v11.json': 'd6eb2a3faed6f030a28ca5b63e3f3512144c9246f39467d300fc279a967bb004', 'provenance/platform-presentation.v12.json': 'aa9efd831558b47646b687e12be30724c4b8be89a0f98ccb8d06ef56cf04e81f', 'provenance/platform-presentation.v13.json': '263b465d22b1a56b8364a0540a65f742948664f9e50e64d759543685768468cc', 'provenance/platform-presentation.v14.json': '3ea28579d130b065fb805942c5c62861d8f6cd24a0027df7fef7cdc41415750b', 'provenance/platform-presentation.v15.json': 'd21bad493ae97587c7b9493813af3393ed9ed98f5a8dfd3a8790270f7ba49aff', 'provenance/platform-presentation.v16.json': '6b975e980d176ecc481449ca5a96ffadadfecae2eb64d97dfdafb75b85b4a3c0', 'provenance/platform-presentation.v17.json': 'b635b2950e37d5387e8fb68da12109ca585833b769eec38cf25911eb86563ee1', 'provenance/platform-presentation.v18.json': '4fa6f43360d5343e119bb7b9e51e0671f1b4b4ef51ba065067459180a710dfd6', 'provenance/platform-presentation.v19.json': '1a056390024ec41126e36c8b8e6a5275415331ec6eeec524da9df8785e23d59b', 'provenance/platform-presentation.v20.json': '34814fabc405812bccc433018f8a197d181a3da9ac617f84cceda51513774b72', 'provenance/platform-presentation.v21.json': 'a353a25fc9586c3fe78de1ad42a20aee4a1c980de59eda4340df4466d9b45593', 'provenance/platform-presentation.v22.json': '3a9a746a565f7942899f5fdffc244121608e39210c7e6eb466203775dc38cae6', 'provenance/platform-presentation.v23.json': '392490c9d1ddc18942ef5b139eb094155a883f1a340e56adfc9512bfa5430a3d', 'provenance/platform-presentation.v24.json': '118a96428bf0a0fce5467fffd8861c419f97ac078aed708b6fd3b5e6318cc242', 'provenance/platform-presentation.v25.json': '61b8e4ebc4e4800253d886a617b98c9590c370c5ae494731edc8135ebf15e9c1'}
EXPECTED_AI_UPDATES = [{'pointer': '/lines/1/question', 'value': '六氟丙烯制取与低温分离怎样支持氟橡胶研究，调聚氟溴油又怎样连接航天需求？'}, {'pointer': '/lines/1/ai_role', 'value': '以传记主线关联人物、化学对象、原文与用途；整理已有原刊中的具体转化，核对平台新增引用的转录和解释。历史成果与平台AI整理分别呈现。'}, {'pointer': '/lines/1/records', 'value': [{'title': '传记主线：单体、氟橡胶与氟油', 'summary': '依据传记35–39页，呈现六氟丙烯来源与低温分离、氟橡胶2号和3号研制成功，以及调聚氟溴陀螺油从研究室到实验厂生产的接续；按书中叙述保留陈庆云与合作者的分工。', 'links': [{'title': '单体与低温分离', 'url': '../topics/fluoromonomers/index.html#a02-monomers', 'kind': 'site'}, {'title': '氟橡胶研究接续', 'url': '../topics/fluoromonomers/index.html#a02-materials', 'kind': 'site'}, {'title': '调聚氟溴油与合作', 'url': '../topics/fluoromonomers/index.html#record-fluorinated-oils', 'kind': 'site'}]}, {'title': '原作者的后续调聚研究', 'summary': '依据已取得并整理的1980年《化学学报》175–184页原刊，把两类调聚产物、主要加成方向、光谱与化学转化关联。具体研究及原报数据归陈庆云、马振中、蒋锡夔、张元发、贾世茂；与早期航天氟溴油分别介绍。', 'links': [{'title': '原刊观察与转化', 'url': '../topics/fluoromonomers/index.html#a02-vdf-1980', 'kind': 'site'}, {'title': '学术贡献与参考资料', 'url': 'https://github.com/CCcolab/Chen-Qingyun-AI4Science/blob/main/docs/A02_ACADEMIC_ACHIEVEMENTS_zh-CN.md', 'kind': 'repo'}]}, {'title': '平台AI整理的性质', 'summary': '平台整理人物—对象—原文—用途的对应，并保存指定原文字样和结构编号的文献对照。这是对既有历史成果的资料展开，不属于超过原作者工作的新科学发现，也不作为历史成果成立的前置认证。', 'links': [{'title': '合作分工与出处', 'url': '../topics/fluoromonomers/index.html#a02-team-records', 'kind': 'site'}, {'title': 'AI整理与历史成果的关系', 'url': '../topics/fluoromonomers/index.html#a02-ai-materials', 'kind': 'site'}]}]}, {'pointer': '/lines/1/boundaries', 'value': ['历史叙述以传记与机构资料为主线，原作者成果归原作者；1号前期工作、陈先生加入后的单体任务及2号／3号材料工作分别介绍。', '早期调聚氟溴油、其他团队全氟烃油、后来的氟氯液体和1980年具体调聚产物分别评价；不自行补配历史牌号的现代商品对应、组成比例或性能指标。', '平台文献整理不作新增实验、结构或机理验证；原文观察和原作者解释分开，新增释读保持review_required、release_eligible=false，M0继续暂停。']}, {'pointer': '/lines/1/next_step', 'value': '围绕已记载成果完善人物—化学对象—原文—用途的资料关联；新增引用对照对应出处，不以重复核验取代学术内容。'}, {'pointer': '/lines/1/future_question', 'value': '若后续拟开展现代模型或实验，应先限定具体材料与可检验问题，并与原作者工作比较；当前没有启动新计算或实验。'}]
NEW_FILES = ('content/a02-biography-narrative.v1.json', 'scripts/render_a02_biography.py', 'scripts/a02_biography_publication.py', 'provenance/platform-presentation.v26.json')
REVIEWED_PUBLIC_FILES = {'scripts/render_a02_history.py': 'ede516085ede5def83987ccf779b7b17207333280e793c13d5f6b2cede8bdfc1', 'scripts/render_heritage.py': '5eaa5bb95ce5d49efa11481ecae9273671aef5584087e52260d4829fce3dd897', 'content/a02-biography-narrative.v1.json': '37418b8249618689d06840b2c9f3b6d73d2acff10dcfc6f5452db605b4543589', 'scripts/render_a02_biography.py': 'e96f30bac5ac91fcd2c04da0b01458c734743bbce299f27852e8539afaf19fe6'}
PUBLIC_DISPLAYS = ('content/a02-biography-narrative.v1.json', 'docs/A02_ACADEMIC_ACHIEVEMENTS_zh-CN.md', 'content/ai-research-section.v1.json', 'docs/AI_RESEARCH_zh-CN.md', 'site/topics/fluoromonomers/index.html', 'site/research/index.html')
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
        raise ValueError('Unsafe or missing A02 biography-presentation file: '+str(name))
    return path


def _json(root: Path, name: str):
    return json.loads(_file(root, name).read_bytes())


def predecessor_bytes(root: Path, name: str) -> bytes:
    """Recover exact fixed 37ed9a5 bytes before replaying the immutable chain."""
    current = _file(root, name).read_bytes()
    if not (root/MANIFEST).exists():
        return current
    data = _json(root, MANIFEST)
    if not isinstance(data, dict):
        raise ValueError('A02 biography presentation requires a JSON object')
    records, pool = data.get('reversible_text_files'), data.get('reverse_text_patch_pool')
    if not isinstance(records, list) or not isinstance(pool, list):
        raise ValueError('A02 biography presentation requires exact reverse text patches')
    matches = [row for row in records if isinstance(row, dict) and row.get('path') == name]
    if not matches:
        if name in PREDECESSOR_FILES:
            raise ValueError('Missing fixed A02 biography predecessor: '+name)
        return current
    if len(matches) != 1 or name not in PREDECESSOR_FILES:
        raise ValueError('Unauthorized or duplicate A02 biography predecessor: '+name)
    row = matches[0]
    old_sha, old_size = PREDECESSOR_FILES[name]
    if (row.get('old_sha256') != old_sha or row.get('old_bytes') != old_size
            or _sha(current) != row.get('new_sha256') or len(current) != row.get('new_bytes')):
        raise ValueError('A02 biography file differs from complete old/new identities: '+name)
    edits = row.get('edits')
    if not isinstance(edits, list) or not edits:
        raise ValueError('A02 biography changes require nonempty text edits: '+name)
    chunks, cursor, old_end, delta = [], 0, 0, 0
    for edit in edits:
        if not isinstance(edit, dict) or set(edit) != {'old_offset', 'replacement'}:
            raise ValueError('Invalid A02 biography reverse text edit: '+name)
        offset, replacement = edit['old_offset'], edit['replacement']
        if (type(offset) is not int or offset < old_end or type(replacement) is not int
                or not 0 <= replacement < len(pool)):
            raise ValueError('Overlapping or invalid A02 biography reverse edit: '+name)
        pair = pool[replacement]
        if (not isinstance(pair, dict) or set(pair) != {'old', 'new'}
                or not all(isinstance(pair.get(k), str) for k in ('old', 'new'))
                or pair['old'] == pair['new']):
            raise ValueError('Invalid A02 biography replacement pool')
        before, after = pair['old'].encode('utf-8'), pair['new'].encode('utf-8')
        position = offset+delta
        if position < cursor or current[position:position+len(after)] != after:
            raise ValueError('A02 biography reverse replacement differs at exact offset: '+name)
        chunks.extend((current[cursor:position], before))
        cursor, old_end = position+len(after), offset+len(before)
        delta += len(after)-len(before)
    rebuilt = b''.join((*chunks, current[cursor:]))
    if _sha(rebuilt) != old_sha or len(rebuilt) != old_size:
        raise ValueError('A02 biography predecessor cannot be reconstructed exactly: '+name)
    return rebuilt


def _set_pointer(data, pointer: str, value):
    parts = [p.replace('~1', '/').replace('~0', '~') for p in pointer.split('/')[1:]]
    if not pointer.startswith('/') or not parts:
        raise ValueError('Invalid fixed A02 biography JSON pointer')
    parent = data
    for part in parts[:-1]:
        parent = parent[int(part)] if isinstance(parent, list) else parent[part]
    key = int(parts[-1]) if isinstance(parent, list) else parts[-1]
    parent[key] = copy.deepcopy(value)


def _binding(root: Path, name: str) -> dict:
    data = _file(root, name).read_bytes()
    return {'path': name, 'sha256': _sha(data), 'bytes': len(data)}


def apply(root: Path, entries: dict, previous_report: dict) -> tuple[dict, dict]:
    """Validate the current A02-only presentation after exact v25 replay."""
    if not (root/MANIFEST).exists():
        return entries, previous_report
    if not (root/PREVIOUS_MANIFEST).is_file():
        raise ValueError('A02 biography presentation requires its immutable v25 predecessor')
    for name, sha in OLD_MANIFESTS.items():
        if _sha(_file(root, name).read_bytes()) != sha:
            raise ValueError('Historical presentation manifest changed: '+name)
    for name, (sha, size) in PROTECTED_FILES.items():
        value = _file(root, name).read_bytes()
        if _sha(value) != sha or len(value) != size:
            raise ValueError('A01 original source or protected reference changed: '+name)
    data = _json(root, MANIFEST)
    required = {
        'schema_version': '26.0', 'presentation_id': PRESENTATION_ID,
        'publication_kind': 'platform_a02_biography_narrative',
        'previous_presentation_commit': PREVIOUS_COMMIT,
        'previous_presentation': {'path': PREVIOUS_MANIFEST, 'sha256': OLD_MANIFESTS[PREVIOUS_MANIFEST]},
        'original_baseline_sha256': BASELINE_SHA256, 'original_archive_sha256': ARCHIVE_SHA256,
        'allowed_html_paths': list(ROUTES), 'added_html_paths': [], 'additions': [],
        'allowed_marker_blocks': {'research/index.html': ['ai-a02'],
            'topics/fluoromonomers/index.html': ['A02_ACADEMIC_HISTORY', 'HERITAGE_CONTEXT']},
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
        raise ValueError('Unsupported bounded A02 biography presentation v26')
    records, pool = data.get('reversible_text_files'), data.get('reverse_text_patch_pool')
    if (not isinstance(records, list) or not isinstance(pool, list) or not pool
            or any(not isinstance(row, dict) for row in records)
            or len(records) != len(PREDECESSOR_FILES)
            or {row.get('path') for row in records} != set(PREDECESSOR_FILES)
            or len({row.get('path') for row in records}) != len(records)
            or any(not isinstance(row.get('edits'), list) or not row['edits'] or any(
                not isinstance(edit, dict) or type(edit.get('replacement')) is not int
                for edit in row['edits']) for row in records)):
        raise ValueError('A02 biography presentation has an unauthorized predecessor file set')
    if {edit['replacement'] for row in records for edit in row['edits']} != set(range(len(pool))):
        raise ValueError('A02 biography presentation requires exactly its used replacement pool')
    for name, (sha, size) in PREDECESSOR_FILES.items():
        old = predecessor_bytes(root, name)
        if _sha(old) != sha or len(old) != size or old == _file(root, name).read_bytes():
            raise ValueError('A02 biography predecessor differs from fixed 37ed9a5: '+name)
    expected = json.loads(predecessor_bytes(root, AI))
    for update in EXPECTED_AI_UPDATES:
        _set_pointer(expected, update['pointer'], update['value'])
    if _json(root, AI) != expected:
        raise ValueError('A02 biography JSON changed outside its fixed A02 fields')
    for name, sha in REVIEWED_PUBLIC_FILES.items():
        if _sha(_file(root, name).read_bytes()) != sha:
            raise ValueError('A02 biography source, renderer or document differs from reviewed bytes: '+name)
    for name in PUBLIC_DISPLAYS:
        value = _file(root, name).read_text('utf-8')
        if re.search(r'(?i)private-sources|current-item-register|现阶段待查事项统计|[CD]:[\\/]', value):
            raise ValueError('A02 biography display contains private evidence or a local path: '+name)
    changes = data.get('changes')
    if (not isinstance(changes, list) or len(changes) != len(ROUTES)
            or any(not isinstance(row, dict) for row in changes)
            or {row.get('path') for row in changes} != set(ROUTES)):
        raise ValueError('A02 biography presentation may change only its two existing routes')
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
            raise ValueError('A02 biography route differs from complete old/new identities: '+route)
        source, current = before.decode('utf-8'), after.decode('utf-8')
        if json_scripts.findall(source) != json_scripts.findall(current):
            raise ValueError('A02 biography presentation changed original embedded JSON: '+route)
        old_ids = re.findall(r'\bid="([^\"]+)"', source)
        new_ids = re.findall(r'\bid="([^\"]+)"', current)
        if not set(old_ids).issubset(new_ids) or len(new_ids) != len(set(new_ids)):
            raise ValueError('A02 biography presentation lost or duplicated source/navigation IDs: '+route)
        patterns = ([r'<section\b[^>]*\bid="ai-a02"[^>]*>.*?</section>']
                    if route == 'research/index.html' else
                    [r'<!-- A02_ACADEMIC_HISTORY:BEGIN -->.*?<!-- A02_ACADEMIC_HISTORY:END -->',
                     r'<!-- HERITAGE_CONTEXT_BEGIN -->.*?<!-- HERITAGE_CONTEXT_END -->'])
        masked_before, masked_after = source, current
        for index, pattern in enumerate(patterns):
            if len(re.findall(pattern, source, re.S)) != 1 or len(re.findall(pattern, current, re.S)) != 1:
                raise ValueError('A02 biography requires each bounded marker exactly once: '+route)
            sentinel = '<A02-BIOGRAPHY-'+str(index)+'/>'
            masked_before = re.sub(pattern, sentinel, masked_before, flags=re.S)
            masked_after = re.sub(pattern, sentinel, masked_after, flags=re.S)
        if masked_before != masked_after:
            raise ValueError('A02 biography presentation changed outside its bounded blocks: '+route)
        updated[route] = {**old_entry, 'sha256': _sha(after), 'bytes': len(after), 'presentation_id': PRESENTATION_ID}
    for name, expected_entry in updated.items():
        value = _file(root, 'site/'+name).read_bytes()
        if _sha(value) != expected_entry['sha256'] or len(value) != expected_entry['bytes']:
            raise ValueError('A02 biography changed an unlisted website byte: '+name)
    from render_ai_research import inspect_ai_research
    from render_a02_history import inspect_a02_history
    from render_a02_biography import inspect_biography
    from render_heritage import inspect_heritage
    checks = [inspect_ai_research(root), inspect_a02_history(root), inspect_biography(root), inspect_heritage(root)]
    if any(c.get('status') != 'passed' for c in checks):
        raise ValueError('A02 biography display differs from source rendering: '+str(checks))
    report = {'path': MANIFEST, 'sha256': _sha(_file(root, MANIFEST).read_bytes()),
        'presentation_id': PRESENTATION_ID, 'publication_kind': required['publication_kind'],
        'changed_paths': list(ROUTES), 'added_paths': [],
        'previous_presentation_commit': PREVIOUS_COMMIT,
        'exact_predecessor_reconstruction': True, 'source_derived_rendering': True,
        'all_v1_v25_manifest_bytes_preserved': True, 'private_originals_not_published': True,
        'original_A02_source_and_embedded_JSON_preserved': True,
        'homepage_achievement_summary_other_lines_and_scientific_data_preserved': True,
        **{k: required[k] for k in ('scientific_review_status', 'release_eligible',
            'scientific_data_unchanged', 'M0_resumed', 'historical_achievement_independent_of_AI_review')}}
    return updated, {**report, 'presentation_chain': [*previous_report['presentation_chain'], report]}
