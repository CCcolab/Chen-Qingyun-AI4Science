"""Bounded A06 historical narrative; original evidence and scientific data protected."""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path, PurePosixPath
import re

MANIFEST = 'provenance/platform-presentation.v30.json'
PRESENTATION_ID = 'PLATFORM-A06-BIOGRAPHY-20261117-v30'
PREVIOUS_COMMIT = '304ffb1126bee12f041199e3600f2b228c11761e'
PREVIOUS_MANIFEST = 'provenance/platform-presentation.v29.json'
ROUTES = ('research/index.html', 'topics/perfluorosulfonates/index.html', 'topics/chen-reagent/index.html')
AI = 'content/ai-research-section.v1.json'
DOCUMENTS = ('content/ai-research-section.v1.json', 'scripts/render_ai_research.py', 'docs/AI_RESEARCH_zh-CN.md', 'content/a06-biography-narrative.v1.json', 'scripts/render_a06_biography.py', 'docs/A06_ACADEMIC_ACHIEVEMENTS_zh-CN.md', 'scripts/a05_biography_publication.py', 'scripts/a01_publication_contract.py', 'scripts/render_heritage.py', 'scripts/a06_biography_publication.py')
PREDECESSOR_FILES = {'site/topics/perfluorosulfonates/index.html': ('85a6f4330edb7607f61ca217b71d2ef6c12cb1af0d48aaaebf737acf3a212ea5', 8888), 'site/topics/chen-reagent/index.html': ('14f08afd4062c0ae171f24e5fb225e5968b003e885edc206baf08ca352b630df', 19991), 'content/ai-research-section.v1.json': ('51277efbd1a3e04452839a726192215250d9f383bf0ab37f0717039602d5c250', 100648), 'docs/AI_RESEARCH_zh-CN.md': ('98577da04c5f02afb729cfed4768310075267750b5ab0e45fb5aeb4871095453', 59939), 'site/research/index.html': ('58b2ef46e8535e5a767abe6c2904b102de4c77d11f1b693b6eb220c85d61b001', 80919), 'scripts/a05_biography_publication.py': ('58ee54c2e1e6a7ddc50eabb4e99b1a8068626b98a24c66b60c88e24fd8319756', 24062), 'scripts/a01_publication_contract.py': ('f24be4bd8c13df513b762f3d0cdd657343d6161af09ee8650ac986c5156e5ef4', 310651), 'scripts/render_heritage.py': ('ad5acef15a792d58fbaf9ad995564b455257c84b2e53e31ce2eb7e0520a7134d', 43429)}
PROTECTED_FILES = {'site/index.html': ('8b3532ee45c0fb33912f20a3bd7943043a348f10a370b9c6716e9edf3c0abf41', 257766), 'site/data/public-sources.json': ('94f8b9f6d0849deb9f26f75947205cfc8c4eb0973045fe958f2121237d987062', 33608), 'site/data/achievement-lines.json': ('1c9ec28bf41a7d79214e84a1c07f3bea1e0d91630dd3a88c93c39ff68a9bccec', 39768), 'site/pftb/index.html': ('b2dd711fcb504b676c3d04f2c42876c2a36ae8f616c0b48b8530aed53822c3b5', 101043), 'content/heritage-20261114.v2.json': ('981876c28a6c863874a8bee8840477fcc04e0f117608d06a4a076b2d0d645350', 72392), 'content/chen-reagent-achievement.v1.json': ('8d13ee4ecaa36a2208867c2510531c8b0d6eb1e06abb8da52c36dc0d7265bcb1', 3884), 'content/chen-reagent-cas-source.v1.json': ('2125b9eaba7853ab02c378ca7c1d78265bbef2895bb2fa512a2cb53981de05cf', 1518), 'docs/CHEN_REAGENT_ACHIEVEMENT_zh-CN.md': ('aff472de27abf8d24eede857e77ae6aa0ce9d5a3a99cf774319250e08ee9128e', 2350), 'data/pftb1966_table1.csv': ('92af88d5c1307d0a01b418354d2620a0d9eb8a8c68766adedd8be0feec2ff29a', 515), 'results/pftb1966-uv-replay.json': ('c83794634136e2bd08d09b806b400eea603cf1c27c753ca3db2951b9c2c99432', 7691), 'results/REPLAY_REPORT_zh-CN.md': ('062aca44324f015450198a4bcc2ddba6aa98d896c31dbc81de407991d78b800b', 2976)}
OLD_MANIFESTS = {'provenance/platform-presentation.v1.json': '1ade23238a23977b47eaa6a7dd585509fdca3e270615914292e2341721308782', 'provenance/platform-presentation.v2.json': '91434b5bc8fb51e96b604a6c6437cb363c92370347f22fcbd2a825e5498f0348', 'provenance/platform-presentation.v3.json': '2b290301102abd8cacb5a2d73f7393d8c4f851285a882a08df42eecd960ed286', 'provenance/platform-presentation.v4.json': 'cfc0bc4d29c24a846bb76ceaf3246084d406393cc7d04ec105cad539c21e120b', 'provenance/platform-presentation.v5.json': '7ac60223b0e540de62671017728acd54e66d07e8de2721006c476c8d1734bed9', 'provenance/platform-presentation.v6.json': '1077f6b2e3a78be65ea4b50e81907b629f96c9b3599fcf440493c204b33dbcf3', 'provenance/platform-presentation.v7.json': '2463a97b3bf74b629f1863892d75f36276c97bf9a111905b47cc6179b62eaa7f', 'provenance/platform-presentation.v8.json': 'ab2b362cb5c90dc4b782f8989cc127a31944c49998ee45fbded8b8a7ac77c962', 'provenance/platform-presentation.v9.json': '462fdbfe1c4bd6f0c32f39e2597764037b4562904f0acec4cce00f08c9797017', 'provenance/platform-presentation.v10.json': '65954e3ff6b484a010fa5052f5331eab55149d23a468ae354ab236462598ffd3', 'provenance/platform-presentation.v11.json': 'd6eb2a3faed6f030a28ca5b63e3f3512144c9246f39467d300fc279a967bb004', 'provenance/platform-presentation.v12.json': 'aa9efd831558b47646b687e12be30724c4b8be89a0f98ccb8d06ef56cf04e81f', 'provenance/platform-presentation.v13.json': '263b465d22b1a56b8364a0540a65f742948664f9e50e64d759543685768468cc', 'provenance/platform-presentation.v14.json': '3ea28579d130b065fb805942c5c62861d8f6cd24a0027df7fef7cdc41415750b', 'provenance/platform-presentation.v15.json': 'd21bad493ae97587c7b9493813af3393ed9ed98f5a8dfd3a8790270f7ba49aff', 'provenance/platform-presentation.v16.json': '6b975e980d176ecc481449ca5a96ffadadfecae2eb64d97dfdafb75b85b4a3c0', 'provenance/platform-presentation.v17.json': 'b635b2950e37d5387e8fb68da12109ca585833b769eec38cf25911eb86563ee1', 'provenance/platform-presentation.v18.json': '4fa6f43360d5343e119bb7b9e51e0671f1b4b4ef51ba065067459180a710dfd6', 'provenance/platform-presentation.v19.json': '1a056390024ec41126e36c8b8e6a5275415331ec6eeec524da9df8785e23d59b', 'provenance/platform-presentation.v20.json': '34814fabc405812bccc433018f8a197d181a3da9ac617f84cceda51513774b72', 'provenance/platform-presentation.v21.json': 'a353a25fc9586c3fe78de1ad42a20aee4a1c980de59eda4340df4466d9b45593', 'provenance/platform-presentation.v22.json': '3a9a746a565f7942899f5fdffc244121608e39210c7e6eb466203775dc38cae6', 'provenance/platform-presentation.v23.json': '392490c9d1ddc18942ef5b139eb094155a883f1a340e56adfc9512bfa5430a3d', 'provenance/platform-presentation.v24.json': '118a96428bf0a0fce5467fffd8861c419f97ac078aed708b6fd3b5e6318cc242', 'provenance/platform-presentation.v25.json': '61b8e4ebc4e4800253d886a617b98c9590c370c5ae494731edc8135ebf15e9c1', 'provenance/platform-presentation.v26.json': '0215099d811ba22ee7224e17a2603d3fdccd7dd0b7473297d35ceb419966bd2d', 'provenance/platform-presentation.v27.json': 'a49d94aae9d1ab980a17506441fdb6d8629fd29da5ae798aa3737568f0c2344b', 'provenance/platform-presentation.v28.json': '54449b28f3dfb1c2946872f959df5e8bb1fc4a9b8e04f20b9b0f9daacd8704f3', 'provenance/platform-presentation.v29.json': '2206e301c22181e3e1a0d5bcce619dd590b4eca3d2968faee6cfbf9a08ed29b7'}
EXPECTED_AI_UPDATES = [{'pointer': '/lines/5/question', 'value': '磺酸酯断键研究怎样走向二氟卡宾前体与“陈试剂”，原研究者解决了哪些合成问题？'}, {'pointer': '/lines/5/ai_role', 'value': '以传记为主线关联具体反应、试剂结构与合作角色；核对新增引用，保留原刊数据、原作者解释及已有方法核查的范围。'}, {'pointer': '/lines/5/records', 'value': [{'title': '历史成果脉络：从断键问题到试剂功能', 'summary': '已按传记60–69、75–77页整理磺酸酯结构与断键、14种二氟卡宾前体、甲酯陈试剂的发现及接续研究、TFDA合作开发。陈庆云与不同合作者的工作分段介绍，不把历史观察写作平台新发现。', 'links': [{'title': 'A06（磺酸酯、二氟卡宾与三氟甲基化）具体学术贡献与合作分工', 'url': 'https://github.com/CCcolab/Chen-Qingyun-AI4Science/blob/main/docs/A06_ACADEMIC_ACHIEVEMENTS_zh-CN.md', 'kind': 'repo'}]}, {'title': '已有原刊记录与新增引用', 'summary': '已取得并核读的1982／1983三篇原刊及三个代表断键实例保留在下方专业记录中。本轮按实际作者表、结构和条件范围展开历史贡献；1989甲酯与2000硅酯的新增介绍限原出版社摘要支持的用途和作者信息。', 'links': [{'title': '磺酸酯反应与合作专题', 'url': '../topics/perfluorosulfonates/index.html', 'kind': 'site'}, {'title': '陈试剂的发现与方法发展', 'url': '../topics/chen-reagent/index.html#topic-chen-reagent', 'kind': 'site'}]}, {'title': '甲酯、硅酯与历史方法核查分别整理', 'summary': 'MFSDA甲酯与TFDA硅酯分别列示；2003硅酯／二氟卡宾与2010甲酯／甾体三氟甲基化各保留提交者、核查者及卷页。这是既有方法核读登记的关联整理，原刊核查不写成本平台新实验或新增专业签认。', 'links': [{'title': '2003硅酯方法', 'url': 'https://orgsyn.org/demo.aspx?prep=v80p0172', 'kind': 'external'}, {'title': '2010甲酯方法', 'url': 'https://orgsyn.org/demo.aspx?prep=v87p0126', 'kind': 'external'}]}]}, {'pointer': '/lines/5/boundaries', 'value': ['历史实验、原报收率和试剂开发归原研究者；本轮为资料关联与新增引用核对，不授予实验复现或机理验证资格。', '甲酯、硅酯、酸型和金属盐分别介绍；所选断键实例和历史方法核查各有限定范围，后续机理计算归其实际作者。']}, {'pointer': '/lines/5/next_step', 'value': '继续解释具体结构、反应问题和合作研究之间的学术联系；新增引用按原文能够支持的范围呈现，原报实例与已有先行研究分别保留。'}, {'pointer': '/lines/5/future_question', 'value': '未来如提出AI辅助研究，应先限定具体实体、反应条件与可检验问题，并与已有理论工作比较；当前仅为设想，M0保持暂停。'}, {'pointer': '/lines/5/source_links/0/title', 'value': '磺酸酯断键的历史成果'}, {'pointer': '/lines/5/source_links/1/title', 'value': '陈试剂的代表性贡献'}, {'pointer': '/lines/5/source_links/2/title', 'value': '原始论文与命名证据'}, {'pointer': '/lines/5/boundary_title', 'value': '资料整理的适用范围'}, {'pointer': '/lines/5/next_step_title', 'value': '资料整理的下一步'}]
FEATURE_EDITS = (('已核见原出版社题录与作者摘要；原全文及条件转录仍待补。', '此处按原出版社题录与作者摘要介绍试剂功能与反应对象。'), ('原论文全文、原始实验记录和具体条件仍待逐项核校；命名使用不等于全部机理已经证明。', '命名证据、具体反应方法与机理研究各按来源介绍，不从命名推定统一机理。'))
NEW_FILES = ('content/a06-biography-narrative.v1.json', 'scripts/render_a06_biography.py', 'docs/A06_ACADEMIC_ACHIEVEMENTS_zh-CN.md', 'scripts/a06_biography_publication.py', 'provenance/platform-presentation.v30.json')
REVIEWED_PUBLIC_FILES = {'content/a06-biography-narrative.v1.json': '002acd76b0953e00fa034b7f0d840dca957c8b692f113999454f56b4ef6bc96a', 'scripts/render_a06_biography.py': 'b62797c827f8f9d175a5dab67850aa41105e0af7258913878b2bc041a3b3e92b', 'docs/A06_ACADEMIC_ACHIEVEMENTS_zh-CN.md': '1eebc0dbec9fcbe553edbea5ac70c52a685d27661b7e423c16e21e81aa45f288', 'scripts/render_ai_research.py': '4293b6cd39150c9e77a6b3c02591c34e83b5d86ecdec675ca9253578af0e2552', 'scripts/render_heritage.py': 'a24ec93747eae81cd6b6c5c63563a920b2a02952eccb1a48451ebf86633047bc'}
PUBLIC_DISPLAYS = ('content/a06-biography-narrative.v1.json', 'docs/A06_ACADEMIC_ACHIEVEMENTS_zh-CN.md', 'content/ai-research-section.v1.json', 'docs/AI_RESEARCH_zh-CN.md', 'site/topics/perfluorosulfonates/index.html', 'site/topics/chen-reagent/index.html', 'site/research/index.html')
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
        raise ValueError('Unsafe or missing A06 biography-presentation file: '+str(name))
    return path


def _json(root: Path, name: str):
    return json.loads(_file(root, name).read_bytes())


def predecessor_bytes(root: Path, name: str) -> bytes:
    """Recover exact fixed 304ffb1 bytes before replaying the immutable chain."""
    current = _file(root, name).read_bytes()
    if not (root/MANIFEST).exists():
        return current
    data = _json(root, MANIFEST)
    if not isinstance(data, dict):
        raise ValueError('A06 biography presentation requires a JSON object')
    records, pool = data.get('reversible_text_files'), data.get('reverse_text_patch_pool')
    if not isinstance(records, list) or not isinstance(pool, list):
        raise ValueError('A06 biography presentation requires exact reverse text patches')
    matches = [row for row in records if isinstance(row, dict) and row.get('path') == name]
    if not matches:
        if name in PREDECESSOR_FILES:
            raise ValueError('Missing fixed A06 biography predecessor: '+name)
        return current
    if len(matches) != 1 or name not in PREDECESSOR_FILES:
        raise ValueError('Unauthorized or duplicate A06 biography predecessor: '+name)
    row = matches[0]
    old_sha, old_size = PREDECESSOR_FILES[name]
    if (row.get('old_sha256') != old_sha or row.get('old_bytes') != old_size
            or _sha(current) != row.get('new_sha256') or len(current) != row.get('new_bytes')):
        raise ValueError('A06 biography file differs from complete old/new identities: '+name)
    edits = row.get('edits')
    if not isinstance(edits, list) or not edits:
        raise ValueError('A06 biography changes require nonempty text edits: '+name)
    chunks, cursor, old_end, delta = [], 0, 0, 0
    for edit in edits:
        if not isinstance(edit, dict) or set(edit) != {'old_offset', 'replacement'}:
            raise ValueError('Invalid A06 biography reverse text edit: '+name)
        offset, replacement = edit['old_offset'], edit['replacement']
        if (type(offset) is not int or offset < old_end or type(replacement) is not int
                or not 0 <= replacement < len(pool)):
            raise ValueError('Overlapping or invalid A06 biography reverse edit: '+name)
        pair = pool[replacement]
        if (not isinstance(pair, dict) or set(pair) != {'old', 'new'}
                or not all(isinstance(pair.get(k), str) for k in ('old', 'new'))
                or pair['old'] == pair['new']):
            raise ValueError('Invalid A06 biography replacement pool')
        before, after = pair['old'].encode('utf-8'), pair['new'].encode('utf-8')
        position = offset+delta
        if position < cursor or current[position:position+len(after)] != after:
            raise ValueError('A06 biography reverse replacement differs at exact offset: '+name)
        chunks.extend((current[cursor:position], before))
        cursor, old_end = position+len(after), offset+len(before)
        delta += len(after)-len(before)
    rebuilt = b''.join((*chunks, current[cursor:]))
    if _sha(rebuilt) != old_sha or len(rebuilt) != old_size:
        raise ValueError('A06 biography predecessor cannot be reconstructed exactly: '+name)
    return rebuilt


def _set_pointer(data, pointer: str, value):
    parts = [p.replace('~1', '/').replace('~0', '~') for p in pointer.split('/')[1:]]
    if not pointer.startswith('/') or not parts:
        raise ValueError('Invalid fixed A06 biography JSON pointer')
    parent = data
    for part in parts[:-1]:
        parent = parent[int(part)] if isinstance(parent, list) else parent[part]
    key = int(parts[-1]) if isinstance(parent, list) else parts[-1]
    parent[key] = copy.deepcopy(value)


def _binding(root: Path, name: str) -> dict:
    data = _file(root, name).read_bytes()
    return {'path': name, 'sha256': _sha(data), 'bytes': len(data)}




def _element(source: str, tag: str, identifier: str) -> str:
    starts = list(re.finditer(r'<'+tag+r'\b[^>]*\bid="'+re.escape(identifier)+r'"[^>]*>', source))
    if len(starts) != 1:
        raise ValueError('A06 requires one original identity block: '+identifier)
    start, depth = starts[0].start(), 0
    for token in re.finditer(r'</?'+tag+r'\b[^>]*>', source[start:]):
        depth += -1 if token.group().startswith('</') else 1
        if depth == 0:
            return source[start:start+token.end()]
    raise ValueError('A06 original identity block is unclosed: '+identifier)
def apply(root: Path, entries: dict, previous_report: dict) -> tuple[dict, dict]:
    """Validate the current A06-only presentation after exact v29 replay."""
    if not (root/MANIFEST).exists():
        return entries, previous_report
    if not (root/PREVIOUS_MANIFEST).is_file():
        raise ValueError('A06 biography presentation requires its immutable v29 predecessor')
    for name, sha in OLD_MANIFESTS.items():
        if _sha(_file(root, name).read_bytes()) != sha:
            raise ValueError('Historical presentation manifest changed: '+name)
    for name, (sha, size) in PROTECTED_FILES.items():
        value = _file(root, name).read_bytes()
        if _sha(value) != sha or len(value) != size:
            raise ValueError('A01 original source or protected reference changed: '+name)
    data = _json(root, MANIFEST)
    required = {
        'schema_version': '30.0', 'presentation_id': PRESENTATION_ID,
        'publication_kind': 'platform_a06_biography_narrative',
        'previous_presentation_commit': PREVIOUS_COMMIT,
        'previous_presentation': {'path': PREVIOUS_MANIFEST, 'sha256': OLD_MANIFESTS[PREVIOUS_MANIFEST]},
        'original_baseline_sha256': BASELINE_SHA256, 'original_archive_sha256': ARCHIVE_SHA256,
        'allowed_html_paths': list(ROUTES), 'added_html_paths': [], 'additions': [],
        'allowed_display_regions': {'research/index.html': ['ai-a06'], 'topics/perfluorosulfonates/index.html': ['main.contents'], 'topics/chen-reagent/index.html': ['main.contents']},
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
        raise ValueError('Unsupported bounded A06 biography presentation v30')
    records, pool = data.get('reversible_text_files'), data.get('reverse_text_patch_pool')
    if (not isinstance(records, list) or not isinstance(pool, list) or not pool
            or any(not isinstance(row, dict) for row in records)
            or len(records) != len(PREDECESSOR_FILES)
            or {row.get('path') for row in records} != set(PREDECESSOR_FILES)
            or len({row.get('path') for row in records}) != len(records)
            or any(not isinstance(row.get('edits'), list) or not row['edits'] or any(
                not isinstance(edit, dict) or type(edit.get('replacement')) is not int
                for edit in row['edits']) for row in records)):
        raise ValueError('A06 biography presentation has an unauthorized predecessor file set')
    if {edit['replacement'] for row in records for edit in row['edits']} != set(range(len(pool))):
        raise ValueError('A06 biography presentation requires exactly its used replacement pool')
    for name, (sha, size) in PREDECESSOR_FILES.items():
        old = predecessor_bytes(root, name)
        if _sha(old) != sha or len(old) != size or old == _file(root, name).read_bytes():
            raise ValueError('A06 biography predecessor differs from fixed 304ffb1: '+name)
    expected = json.loads(predecessor_bytes(root, AI))
    for update in EXPECTED_AI_UPDATES:
        _set_pointer(expected, update['pointer'], update['value'])
    if _json(root, AI) != expected:
        raise ValueError('A06 biography JSON changed outside its fixed A06 fields')
    for name, sha in REVIEWED_PUBLIC_FILES.items():
        if _sha(_file(root, name).read_bytes()) != sha:
            raise ValueError('A06 biography source, renderer or document differs from reviewed bytes: '+name)
    for name in PUBLIC_DISPLAYS:
        value = _file(root, name).read_text('utf-8')
        if re.search(r'(?i)private-sources|current-item-register|现阶段待查事项统计|[CD]:[\\/]', value):
            raise ValueError('A06 biography display contains private evidence or a local path: '+name)
    changes = data.get('changes')
    if (not isinstance(changes, list) or len(changes) != len(ROUTES)
            or any(not isinstance(row, dict) for row in changes)
            or {row.get('path') for row in changes} != set(ROUTES)):
        raise ValueError('A06 biography presentation may change only its three existing routes')
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
            raise ValueError('A06 biography route differs from complete old/new identities: '+route)
        source, current = before.decode('utf-8'), after.decode('utf-8')
        if json_scripts.findall(source) != json_scripts.findall(current):
            raise ValueError('A06 biography presentation changed original embedded JSON: '+route)
        old_ids = re.findall(r'\bid="([^\"]+)"', source)
        new_ids = re.findall(r'\bid="([^\"]+)"', current)
        if not set(old_ids).issubset(new_ids) or len(new_ids) != len(set(new_ids)):
            raise ValueError('A06 biography presentation lost or duplicated source/navigation IDs: '+route)
        if route == 'research/index.html':
            pattern = r'<section\b[^>]*\bid="ai-a06"[^>]*>.*?</section>'
            if (len(re.findall(pattern, source, re.S)) != 1 or len(re.findall(pattern, current, re.S)) != 1
                    or re.sub(pattern, '<A06/>', source, flags=re.S) != re.sub(pattern, '<A06/>', current, flags=re.S)):
                raise ValueError('A06 biography changed outside its AI A06 section')
        else:
            pattern = r'(<main\b[^>]*>)(.*?)(</main>)'
            before_main, after_main = list(re.finditer(pattern, source, re.S)), list(re.finditer(pattern, current, re.S))
            if len(before_main) != 1 or len(after_main) != 1:
                raise ValueError('A06 requires one original main region')
            a, b = before_main[0], after_main[0]
            if (a.group(1) != b.group(1) or a.group(3) != b.group(3)
                    or source[:a.start(2)] != current[:b.start(2)]
                    or source[a.end(2):] != current[b.end(2):]):
                raise ValueError('A06 changed original head/header/footer or main wrapper bytes')
        if route == 'topics/chen-reagent/index.html':
            for tag, identifier in (('section', 'chen-reagent-contribution'), ('article', 'record-reagent-identity')):
                expected_block = _element(source, tag, identifier)
                if identifier == 'chen-reagent-contribution':
                    for before_text, after_text in FEATURE_EDITS:
                        if expected_block.count(before_text) != 1:
                            raise ValueError('A06 original Chen reagent feature lacks its exact display text')
                        expected_block = expected_block.replace(before_text, after_text, 1)
                if expected_block != _element(current, tag, identifier):
                    raise ValueError('A06 changed the original Chen reagent identity or naming block: '+identifier)
        updated[route] = {**old_entry, 'sha256': _sha(after), 'bytes': len(after), 'presentation_id': PRESENTATION_ID}
    for name, expected_entry in updated.items():
        value = _file(root, 'site/'+name).read_bytes()
        if _sha(value) != expected_entry['sha256'] or len(value) != expected_entry['bytes']:
            raise ValueError('A06 biography changed an unlisted website byte: '+name)
    from render_ai_research import inspect_ai_research
    from render_a06_biography import inspect_biography
    checks = [inspect_ai_research(root), inspect_biography(root)]
    if any(c.get('status') != 'passed' for c in checks):
        raise ValueError('A06 biography display differs from source rendering: '+str(checks))
    report = {'path': MANIFEST, 'sha256': _sha(_file(root, MANIFEST).read_bytes()),
        'presentation_id': PRESENTATION_ID, 'publication_kind': required['publication_kind'],
        'changed_paths': list(ROUTES), 'added_paths': [],
        'previous_presentation_commit': PREVIOUS_COMMIT,
        'exact_predecessor_reconstruction': True, 'source_derived_rendering': True,
        'all_v1_v29_manifest_bytes_preserved': True, 'private_originals_not_published': True,
        'original_data_and_embedded_JSON_preserved': True,
        'homepage_achievement_summary_other_lines_and_scientific_data_preserved': True,
        **{k: required[k] for k in ('scientific_review_status', 'release_eligible',
            'scientific_data_unchanged', 'M0_resumed', 'historical_achievement_independent_of_AI_review')}}
    return updated, {**report, 'presentation_chain': [*previous_report['presentation_chain'], report]}
