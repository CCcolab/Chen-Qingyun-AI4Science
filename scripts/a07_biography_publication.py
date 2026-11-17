"""Bounded A07 historical narrative; original evidence and scientific data protected."""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path, PurePosixPath
import re

from a08_biography_publication import (MANIFEST as A08_BIOGRAPHY_MANIFEST,
    predecessor_bytes as a08_biography_predecessor_bytes, apply as apply_a08_biography_presentation)

MANIFEST = 'provenance/platform-presentation.v31.json'
PRESENTATION_ID = 'PLATFORM-A07-BIOGRAPHY-20261117-v31'
PREVIOUS_COMMIT = '31063d9b0e361ff07c0037e96492bb5f5d57a345'
PREVIOUS_MANIFEST = 'provenance/platform-presentation.v30.json'
ROUTES = ('research/index.html', 'topics/single-electron-transfer/index.html')
AI = 'content/ai-research-section.v1.json'
DOCUMENTS = ('content/ai-research-section.v1.json', 'scripts/render_ai_research.py', 'docs/AI_RESEARCH_zh-CN.md', 'content/a07-biography-narrative.v1.json', 'scripts/render_a07_biography.py', 'docs/A07_ACADEMIC_ACHIEVEMENTS_zh-CN.md', 'scripts/a06_biography_publication.py', 'scripts/a01_publication_contract.py', 'scripts/render_heritage.py', 'scripts/a07_biography_publication.py')
PREDECESSOR_FILES = {'site/topics/single-electron-transfer/index.html': ('79c84f89e25e576a03f34153b9eb85a5ff73815c8265a0222930d889390ea947', 10355), 'content/ai-research-section.v1.json': ('ea127aac6fc88c83b270f7654fab8764b2b9487bff5d58767ff52be7bc6fec04', 101990), 'docs/AI_RESEARCH_zh-CN.md': ('c4ed1a19320c975054a2098d993270dcdd40283ad5ca3642dbb348e675af4162', 60625), 'site/research/index.html': ('318c4168c0e8dbc525105b24230a827ac8ef7b6c4cfa2ae7e77182efd0a43c89', 81673), 'scripts/a06_biography_publication.py': ('20449e28fc911c83275ce438113acdb58222397dce575afe39245e5627c4f285', 26473), 'scripts/a01_publication_contract.py': ('2391673784464cc1b7a7871fd63040953a4ec4ee4f5b3b95b928877dc312176a', 310881), 'scripts/render_heritage.py': ('a24ec93747eae81cd6b6c5c63563a920b2a02952eccb1a48451ebf86633047bc', 43899)}
PROTECTED_FILES = {'site/index.html': ('8b3532ee45c0fb33912f20a3bd7943043a348f10a370b9c6716e9edf3c0abf41', 257766), 'site/data/public-sources.json': ('94f8b9f6d0849deb9f26f75947205cfc8c4eb0973045fe958f2121237d987062', 33608), 'site/data/achievement-lines.json': ('1c9ec28bf41a7d79214e84a1c07f3bea1e0d91630dd3a88c93c39ff68a9bccec', 39768), 'site/pftb/index.html': ('b2dd711fcb504b676c3d04f2c42876c2a36ae8f616c0b48b8530aed53822c3b5', 101043), 'content/heritage-20261114.v2.json': ('981876c28a6c863874a8bee8840477fcc04e0f117608d06a4a076b2d0d645350', 72392), 'content/chen-reagent-achievement.v1.json': ('8d13ee4ecaa36a2208867c2510531c8b0d6eb1e06abb8da52c36dc0d7265bcb1', 3884), 'content/chen-reagent-cas-source.v1.json': ('2125b9eaba7853ab02c378ca7c1d78265bbef2895bb2fa512a2cb53981de05cf', 1518), 'docs/CHEN_REAGENT_ACHIEVEMENT_zh-CN.md': ('aff472de27abf8d24eede857e77ae6aa0ce9d5a3a99cf774319250e08ee9128e', 2350), 'data/pftb1966_table1.csv': ('92af88d5c1307d0a01b418354d2620a0d9eb8a8c68766adedd8be0feec2ff29a', 515), 'results/pftb1966-uv-replay.json': ('c83794634136e2bd08d09b806b400eea603cf1c27c753ca3db2951b9c2c99432', 7691), 'results/REPLAY_REPORT_zh-CN.md': ('062aca44324f015450198a4bcc2ddba6aa98d896c31dbc81de407991d78b800b', 2976), 'content/a06-biography-narrative.v1.json': ('002acd76b0953e00fa034b7f0d840dca957c8b692f113999454f56b4ef6bc96a', 18948), 'scripts/render_a06_biography.py': ('b62797c827f8f9d175a5dab67850aa41105e0af7258913878b2bc041a3b3e92b', 11428), 'docs/A06_ACADEMIC_ACHIEVEMENTS_zh-CN.md': ('1eebc0dbec9fcbe553edbea5ac70c52a685d27661b7e423c16e21e81aa45f288', 14564)}
OLD_MANIFESTS = {'provenance/platform-presentation.v1.json': '1ade23238a23977b47eaa6a7dd585509fdca3e270615914292e2341721308782', 'provenance/platform-presentation.v2.json': '91434b5bc8fb51e96b604a6c6437cb363c92370347f22fcbd2a825e5498f0348', 'provenance/platform-presentation.v3.json': '2b290301102abd8cacb5a2d73f7393d8c4f851285a882a08df42eecd960ed286', 'provenance/platform-presentation.v4.json': 'cfc0bc4d29c24a846bb76ceaf3246084d406393cc7d04ec105cad539c21e120b', 'provenance/platform-presentation.v5.json': '7ac60223b0e540de62671017728acd54e66d07e8de2721006c476c8d1734bed9', 'provenance/platform-presentation.v6.json': '1077f6b2e3a78be65ea4b50e81907b629f96c9b3599fcf440493c204b33dbcf3', 'provenance/platform-presentation.v7.json': '2463a97b3bf74b629f1863892d75f36276c97bf9a111905b47cc6179b62eaa7f', 'provenance/platform-presentation.v8.json': 'ab2b362cb5c90dc4b782f8989cc127a31944c49998ee45fbded8b8a7ac77c962', 'provenance/platform-presentation.v9.json': '462fdbfe1c4bd6f0c32f39e2597764037b4562904f0acec4cce00f08c9797017', 'provenance/platform-presentation.v10.json': '65954e3ff6b484a010fa5052f5331eab55149d23a468ae354ab236462598ffd3', 'provenance/platform-presentation.v11.json': 'd6eb2a3faed6f030a28ca5b63e3f3512144c9246f39467d300fc279a967bb004', 'provenance/platform-presentation.v12.json': 'aa9efd831558b47646b687e12be30724c4b8be89a0f98ccb8d06ef56cf04e81f', 'provenance/platform-presentation.v13.json': '263b465d22b1a56b8364a0540a65f742948664f9e50e64d759543685768468cc', 'provenance/platform-presentation.v14.json': '3ea28579d130b065fb805942c5c62861d8f6cd24a0027df7fef7cdc41415750b', 'provenance/platform-presentation.v15.json': 'd21bad493ae97587c7b9493813af3393ed9ed98f5a8dfd3a8790270f7ba49aff', 'provenance/platform-presentation.v16.json': '6b975e980d176ecc481449ca5a96ffadadfecae2eb64d97dfdafb75b85b4a3c0', 'provenance/platform-presentation.v17.json': 'b635b2950e37d5387e8fb68da12109ca585833b769eec38cf25911eb86563ee1', 'provenance/platform-presentation.v18.json': '4fa6f43360d5343e119bb7b9e51e0671f1b4b4ef51ba065067459180a710dfd6', 'provenance/platform-presentation.v19.json': '1a056390024ec41126e36c8b8e6a5275415331ec6eeec524da9df8785e23d59b', 'provenance/platform-presentation.v20.json': '34814fabc405812bccc433018f8a197d181a3da9ac617f84cceda51513774b72', 'provenance/platform-presentation.v21.json': 'a353a25fc9586c3fe78de1ad42a20aee4a1c980de59eda4340df4466d9b45593', 'provenance/platform-presentation.v22.json': '3a9a746a565f7942899f5fdffc244121608e39210c7e6eb466203775dc38cae6', 'provenance/platform-presentation.v23.json': '392490c9d1ddc18942ef5b139eb094155a883f1a340e56adfc9512bfa5430a3d', 'provenance/platform-presentation.v24.json': '118a96428bf0a0fce5467fffd8861c419f97ac078aed708b6fd3b5e6318cc242', 'provenance/platform-presentation.v25.json': '61b8e4ebc4e4800253d886a617b98c9590c370c5ae494731edc8135ebf15e9c1', 'provenance/platform-presentation.v26.json': '0215099d811ba22ee7224e17a2603d3fdccd7dd0b7473297d35ceb419966bd2d', 'provenance/platform-presentation.v27.json': 'a49d94aae9d1ab980a17506441fdb6d8629fd29da5ae798aa3737568f0c2344b', 'provenance/platform-presentation.v28.json': '54449b28f3dfb1c2946872f959df5e8bb1fc4a9b8e04f20b9b0f9daacd8704f3', 'provenance/platform-presentation.v29.json': '2206e301c22181e3e1a0d5bcce619dd590b4eca3d2968faee6cfbf9a08ed29b7', 'provenance/platform-presentation.v30.json': '952cea23bb612648addc4ac5a5e5cc88acae24a67b8dc98661ae49f79710645b'}
EXPECTED_AI_UPDATES = [{'pointer': '/lines/6/question', 'value': '从溶剂效应到含氟C–Cl活化，陈先生与合作者怎样发展具体氟烷基化方法？'}, {'pointer': '/lines/6/ai_role', 'value': '以传记关联研究问题、发现过程和合作分工；按具体论文区分底物、引发条件、观察与作者解释，核对新增引用。'}, {'pointer': '/lines/6/records', 'value': [{'title': '研究脉络与合作故事', 'summary': '已按传记69–74、83–84页，整理全氟烷基碘的溶剂效应、多种引发方向和含氟氯代物活化；陈亚雄的发现过程、龙正宇与黄小庭等的接续研究分别具名呈现。原脱卤亚磺化发现归黄维垣小组，陈先生团队的方法拓展另行说明。', 'links': [{'title': 'A07（单电子转移与C–Cl活化）的具体学术贡献与合作', 'url': 'https://github.com/CCcolab/Chen-Qingyun-AI4Science/blob/main/docs/A07_ACADEMIC_ACHIEVEMENTS_zh-CN.md', 'kind': 'repo'}]}, {'title': '新增原作引用：从溶剂到具体反应', 'summary': '新增关联1984年碘苯氟烷基化溶剂研究题录、1986年铜体系摘要，以及1999／2001两种C–Cl方法的原摘要。合成结果、抑制实验及未捕获到氟烷基铜的结果、原作者提出的可能SET解释分别呈现；1999摘要的方法贡献不被改写为完整机理证明。', 'links': [{'title': '单电子转移与C–Cl活化历史专题', 'url': '../topics/single-electron-transfer/index.html', 'kind': 'site'}]}, {'title': '已有附件与技术文书记录', 'summary': '1999／2001两份31页、26页SI已取得；正文与SI分层使用。同一申请的CN1752059A和CN1298686C两份完整说明书及权利要求对应核读登记保留；陈庆云、曹海萍为共同发明人。指定版本对照见下方专业记录，本轮没有新增实验或计算。', 'links': [{'title': 'CN1752059A公开文书', 'url': 'https://patents.google.com/patent/CN1752059A/zh', 'kind': 'external'}, {'title': 'CN1298686C历史授权公告文书', 'url': 'https://patents.google.com/patent/CN1298686C/zh', 'kind': 'external'}]}]}, {'pointer': '/lines/6/boundaries', 'value': ['历史方法、原报观察与合作贡献归原作者；平台本轮完成资料关联与新增引用核对，保持review_required。', 'SET解释按具体对象和原作者证据范围介绍；C–Cl活化不等于普遍C–F断裂或PFAS降解，专利文字不证明工业采用或当前法律状态。']}, {'pointer': '/lines/6/next_step', 'value': '继续解释溶剂、引发方式与底物范围之间的学术联系；将新增引用与传记发现过程对应，保留原作者提出解释的层级及已完成的技术文书对照。'}, {'pointer': '/lines/6/future_question', 'value': '未来如开展AI辅助研究，应先限定具体反应、条件和可检验量，再比较竞争解释与既有研究；目前仅为设想，M0继续暂停。'}, {'pointer': '/lines/6/source_links/0/title', 'value': '单电子转移与C–Cl活化的历史成果'}, {'pointer': '/lines/6/source_links/1/title', 'value': '含氟氯代物的具体方法与合作'}, {'pointer': '/lines/6/boundary_title', 'value': '资料整理的适用范围'}, {'pointer': '/lines/6/next_step_title', 'value': '资料整理的下一步'}]
NEW_FILES = ('content/a07-biography-narrative.v1.json', 'scripts/render_a07_biography.py', 'docs/A07_ACADEMIC_ACHIEVEMENTS_zh-CN.md', 'scripts/a07_biography_publication.py', 'provenance/platform-presentation.v31.json')
REVIEWED_PUBLIC_FILES = {'content/a07-biography-narrative.v1.json': '22e6121f4f3d61e3676a8ec95b76dc22512df0ab550cfb7c403f809f245016db', 'scripts/render_a07_biography.py': '01f5e86435bc9f4eac7f04104892a2d875647f1dd6d3e270e38f3ed28d9dde8e', 'docs/A07_ACADEMIC_ACHIEVEMENTS_zh-CN.md': '9d73bbb199e8c6d825550429ae35cb3ea8dffbcd4b17e3b73145603080cc487b', 'scripts/render_ai_research.py': '4293b6cd39150c9e77a6b3c02591c34e83b5d86ecdec675ca9253578af0e2552', 'scripts/render_heritage.py': 'd4ec4bc12c8fa082f36f436a6d9c06cc65592d1d03ef75504cfc619bab309740'}
PUBLIC_DISPLAYS = ('content/a07-biography-narrative.v1.json', 'docs/A07_ACADEMIC_ACHIEVEMENTS_zh-CN.md', 'content/ai-research-section.v1.json', 'docs/AI_RESEARCH_zh-CN.md', 'site/topics/single-electron-transfer/index.html', 'site/research/index.html')
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
        raise ValueError('Unsafe or missing A07 biography-presentation file: '+str(name))
    return path


def _json(root: Path, name: str):
    return json.loads(a08_biography_predecessor_bytes(root, name))


def predecessor_bytes(root: Path, name: str) -> bytes:
    """Recover exact fixed 31063d9 bytes before replaying the immutable chain."""
    current = a08_biography_predecessor_bytes(root, name)
    if not (root/MANIFEST).exists():
        return current
    data = _json(root, MANIFEST)
    if not isinstance(data, dict):
        raise ValueError('A07 biography presentation requires a JSON object')
    records, pool = data.get('reversible_text_files'), data.get('reverse_text_patch_pool')
    if not isinstance(records, list) or not isinstance(pool, list):
        raise ValueError('A07 biography presentation requires exact reverse text patches')
    matches = [row for row in records if isinstance(row, dict) and row.get('path') == name]
    if not matches:
        if name in PREDECESSOR_FILES:
            raise ValueError('Missing fixed A07 biography predecessor: '+name)
        return current
    if len(matches) != 1 or name not in PREDECESSOR_FILES:
        raise ValueError('Unauthorized or duplicate A07 biography predecessor: '+name)
    row = matches[0]
    old_sha, old_size = PREDECESSOR_FILES[name]
    if (row.get('old_sha256') != old_sha or row.get('old_bytes') != old_size
            or _sha(current) != row.get('new_sha256') or len(current) != row.get('new_bytes')):
        raise ValueError('A07 biography file differs from complete old/new identities: '+name)
    edits = row.get('edits')
    if not isinstance(edits, list) or not edits:
        raise ValueError('A07 biography changes require nonempty text edits: '+name)
    chunks, cursor, old_end, delta = [], 0, 0, 0
    for edit in edits:
        if not isinstance(edit, dict) or set(edit) != {'old_offset', 'replacement'}:
            raise ValueError('Invalid A07 biography reverse text edit: '+name)
        offset, replacement = edit['old_offset'], edit['replacement']
        if (type(offset) is not int or offset < old_end or type(replacement) is not int
                or not 0 <= replacement < len(pool)):
            raise ValueError('Overlapping or invalid A07 biography reverse edit: '+name)
        pair = pool[replacement]
        if (not isinstance(pair, dict) or set(pair) != {'old', 'new'}
                or not all(isinstance(pair.get(k), str) for k in ('old', 'new'))
                or pair['old'] == pair['new']):
            raise ValueError('Invalid A07 biography replacement pool')
        before, after = pair['old'].encode('utf-8'), pair['new'].encode('utf-8')
        position = offset+delta
        if position < cursor or current[position:position+len(after)] != after:
            raise ValueError('A07 biography reverse replacement differs at exact offset: '+name)
        chunks.extend((current[cursor:position], before))
        cursor, old_end = position+len(after), offset+len(before)
        delta += len(after)-len(before)
    rebuilt = b''.join((*chunks, current[cursor:]))
    if _sha(rebuilt) != old_sha or len(rebuilt) != old_size:
        raise ValueError('A07 biography predecessor cannot be reconstructed exactly: '+name)
    return rebuilt


def _set_pointer(data, pointer: str, value):
    parts = [p.replace('~1', '/').replace('~0', '~') for p in pointer.split('/')[1:]]
    if not pointer.startswith('/') or not parts:
        raise ValueError('Invalid fixed A07 biography JSON pointer')
    parent = data
    for part in parts[:-1]:
        parent = parent[int(part)] if isinstance(parent, list) else parent[part]
    key = int(parts[-1]) if isinstance(parent, list) else parts[-1]
    parent[key] = copy.deepcopy(value)


def _binding(root: Path, name: str) -> dict:
    data = a08_biography_predecessor_bytes(root, name)
    return {'path': name, 'sha256': _sha(data), 'bytes': len(data)}


def apply(root: Path, entries: dict, previous_report: dict) -> tuple[dict, dict]:
    """Validate the current A07-only presentation after exact v30 replay."""
    if not (root/MANIFEST).exists():
        if (root/A08_BIOGRAPHY_MANIFEST).exists():
            raise ValueError('A08 biography presentation requires its immutable v31 predecessor')
        return entries, previous_report
    if not (root/PREVIOUS_MANIFEST).is_file():
        raise ValueError('A07 biography presentation requires its immutable v30 predecessor')
    for name, sha in OLD_MANIFESTS.items():
        if _sha(a08_biography_predecessor_bytes(root, name)) != sha:
            raise ValueError('Historical presentation manifest changed: '+name)
    for name, (sha, size) in PROTECTED_FILES.items():
        value = a08_biography_predecessor_bytes(root, name)
        if _sha(value) != sha or len(value) != size:
            raise ValueError('A01 original source or protected reference changed: '+name)
    data = _json(root, MANIFEST)
    required = {
        'schema_version': '31.0', 'presentation_id': PRESENTATION_ID,
        'publication_kind': 'platform_a07_biography_narrative',
        'previous_presentation_commit': PREVIOUS_COMMIT,
        'previous_presentation': {'path': PREVIOUS_MANIFEST, 'sha256': OLD_MANIFESTS[PREVIOUS_MANIFEST]},
        'original_baseline_sha256': BASELINE_SHA256, 'original_archive_sha256': ARCHIVE_SHA256,
        'allowed_html_paths': list(ROUTES), 'added_html_paths': [], 'additions': [],
        'allowed_display_regions': {'research/index.html': ['ai-a07'], 'topics/single-electron-transfer/index.html': ['main.contents']},
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
        raise ValueError('Unsupported bounded A07 biography presentation v31')
    records, pool = data.get('reversible_text_files'), data.get('reverse_text_patch_pool')
    if (not isinstance(records, list) or not isinstance(pool, list) or not pool
            or any(not isinstance(row, dict) for row in records)
            or len(records) != len(PREDECESSOR_FILES)
            or {row.get('path') for row in records} != set(PREDECESSOR_FILES)
            or len({row.get('path') for row in records}) != len(records)
            or any(not isinstance(row.get('edits'), list) or not row['edits'] or any(
                not isinstance(edit, dict) or type(edit.get('replacement')) is not int
                for edit in row['edits']) for row in records)):
        raise ValueError('A07 biography presentation has an unauthorized predecessor file set')
    if {edit['replacement'] for row in records for edit in row['edits']} != set(range(len(pool))):
        raise ValueError('A07 biography presentation requires exactly its used replacement pool')
    for name, (sha, size) in PREDECESSOR_FILES.items():
        old = predecessor_bytes(root, name)
        if _sha(old) != sha or len(old) != size or old == a08_biography_predecessor_bytes(root, name):
            raise ValueError('A07 biography predecessor differs from fixed 31063d9: '+name)
    expected = json.loads(predecessor_bytes(root, AI))
    for update in EXPECTED_AI_UPDATES:
        _set_pointer(expected, update['pointer'], update['value'])
    if _json(root, AI) != expected:
        raise ValueError('A07 biography JSON changed outside its fixed A07 fields')
    for name, sha in REVIEWED_PUBLIC_FILES.items():
        if _sha(a08_biography_predecessor_bytes(root, name)) != sha:
            raise ValueError('A07 biography source, renderer or document differs from reviewed bytes: '+name)
    for name in PUBLIC_DISPLAYS:
        value = a08_biography_predecessor_bytes(root, name).decode('utf-8')
        if re.search(r'(?i)private-sources|current-item-register|现阶段待查事项统计|[CD]:[\\/]', value):
            raise ValueError('A07 biography display contains private evidence or a local path: '+name)
    changes = data.get('changes')
    if (not isinstance(changes, list) or len(changes) != len(ROUTES)
            or any(not isinstance(row, dict) for row in changes)
            or {row.get('path') for row in changes} != set(ROUTES)):
        raise ValueError('A07 biography presentation may change only its two existing routes')
    updated = {name: dict(row) for name, row in entries.items()}
    json_scripts = re.compile(r'<script\b[^>]*\btype\s*=\s*["\']application/(?:ld\+)?json["\'][^>]*>.*?</script\s*>', re.I | re.S)
    for item in changes:
        route = item['path']; old_entry = entries[route]
        before = predecessor_bytes(root, 'site/'+route)
        after = a08_biography_predecessor_bytes(root, 'site/'+route)
        if (item.get('old_sha256') != old_entry['sha256'] or item.get('old_bytes') != old_entry['bytes']
                or _sha(before) != old_entry['sha256'] or len(before) != old_entry['bytes']
                or item.get('new_sha256') != _sha(after) or item.get('new_bytes') != len(after)
                or before == after or not isinstance(item.get('reason'), str) or not item['reason'].strip()):
            raise ValueError('A07 biography route differs from complete old/new identities: '+route)
        source, current = before.decode('utf-8'), after.decode('utf-8')
        if json_scripts.findall(source) != json_scripts.findall(current):
            raise ValueError('A07 biography presentation changed original embedded JSON: '+route)
        old_ids = re.findall(r'\bid="([^\"]+)"', source)
        new_ids = re.findall(r'\bid="([^\"]+)"', current)
        if not set(old_ids).issubset(new_ids) or len(new_ids) != len(set(new_ids)):
            raise ValueError('A07 biography presentation lost or duplicated source/navigation IDs: '+route)
        if route == 'research/index.html':
            pattern = r'<section\b[^>]*\bid="ai-a07"[^>]*>.*?</section>'
            if (len(re.findall(pattern, source, re.S)) != 1 or len(re.findall(pattern, current, re.S)) != 1
                    or re.sub(pattern, '<A07/>', source, flags=re.S) != re.sub(pattern, '<A07/>', current, flags=re.S)):
                raise ValueError('A07 biography changed outside its AI A07 section')
        else:
            pattern = r'(<main\b[^>]*>)(.*?)(</main>)'
            before_main, after_main = list(re.finditer(pattern, source, re.S)), list(re.finditer(pattern, current, re.S))
            if len(before_main) != 1 or len(after_main) != 1:
                raise ValueError('A07 requires one original main region')
            a, b = before_main[0], after_main[0]
            if (a.group(1) != b.group(1) or a.group(3) != b.group(3)
                    or source[:a.start(2)] != current[:b.start(2)]
                    or source[a.end(2):] != current[b.end(2):]):
                raise ValueError('A07 changed original head/header/footer or main wrapper bytes')
        updated[route] = {**old_entry, 'sha256': _sha(after), 'bytes': len(after), 'presentation_id': PRESENTATION_ID}
    for name, expected_entry in updated.items():
        value = a08_biography_predecessor_bytes(root, 'site/'+name)
        if _sha(value) != expected_entry['sha256'] or len(value) != expected_entry['bytes']:
            raise ValueError('A07 biography changed an unlisted website byte: '+name)
    # v31 validates reconstructed bytes; v32 validates the current rendering.
    if not (root/A08_BIOGRAPHY_MANIFEST).exists():
        from render_ai_research import inspect_ai_research
        from render_a07_biography import inspect_biography
        checks = [inspect_ai_research(root), inspect_biography(root)]
        if any(c.get('status') != 'passed' for c in checks):
            raise ValueError('A07 biography display differs from source rendering: '+str(checks))
    report = {'path': MANIFEST, 'sha256': _sha(_file(root, MANIFEST).read_bytes()),
        'presentation_id': PRESENTATION_ID, 'publication_kind': required['publication_kind'],
        'changed_paths': list(ROUTES), 'added_paths': [],
        'previous_presentation_commit': PREVIOUS_COMMIT,
        'exact_predecessor_reconstruction': True, 'source_derived_rendering': True,
        'all_v1_v30_manifest_bytes_preserved': True, 'private_originals_not_published': True,
        'original_data_and_embedded_JSON_preserved': True,
        'homepage_achievement_summary_other_lines_and_scientific_data_preserved': True,
        **{k: required[k] for k in ('scientific_review_status', 'release_eligible',
            'scientific_data_unchanged', 'M0_resumed', 'historical_achievement_independent_of_AI_review')}}
    return apply_a08_biography_presentation(root, updated,
        {**report, 'presentation_chain': [*previous_report['presentation_chain'], report]})
