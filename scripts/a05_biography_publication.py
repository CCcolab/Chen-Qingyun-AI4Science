"""Bounded A05 history and scope presentation; original scientific data protected."""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path, PurePosixPath
import re

MANIFEST = 'provenance/platform-presentation.v29.json'
PRESENTATION_ID = 'PLATFORM-A05-BIOGRAPHY-20261117-v29'
PREVIOUS_COMMIT = '28b606c4c10535409f8866cda34a4da72e1375e9'
PREVIOUS_MANIFEST = 'provenance/platform-presentation.v28.json'
ROUTES = ('research/index.html', 'topics/refrigerants/index.html')
AI = 'content/ai-research-section.v1.json'
DOCUMENTS = ('content/ai-research-section.v1.json', 'scripts/render_ai_research.py', 'docs/AI_RESEARCH_zh-CN.md', 'content/a05-biography-narrative.v1.json', 'scripts/render_a05_biography.py', 'docs/A05_ACADEMIC_ACHIEVEMENTS_zh-CN.md', 'scripts/a04_biography_publication.py', 'scripts/a01_publication_contract.py', 'scripts/render_heritage.py', 'scripts/a05_biography_publication.py')
PREDECESSOR_FILES = {'site/topics/refrigerants/index.html': ('5d9b5a355b949f67c5de252727f8d4e4e7533abab8a666c49a0f932170153c4e', 10636), 'content/ai-research-section.v1.json': ('096c409f8f8b25565aa6079014d4ffc846f32d3145653b5adca465d7403b450c', 98670), 'docs/AI_RESEARCH_zh-CN.md': ('1acf5a10706382835dab7b98637af169ea9b61b5b3295d943b53dbc8bff46344', 58719), 'site/research/index.html': ('ff6aecc96040dfbee8a28df72ae416c3cef401a6cc32cac5f62dc9414d28afa2', 79537), 'scripts/a04_biography_publication.py': ('c5be09d48b941ecd51f9fb311329662d9f868dd491c2e1babcfa1edf5c1ab18e', 23854), 'scripts/a01_publication_contract.py': ('d21da949447555de43eda8a46d92f3f4f7015b8a15aeb0d2020b191bd622ef51', 310421), 'scripts/render_heritage.py': ('5eaa5bb95ce5d49efa11481ecae9273671aef5584087e52260d4829fce3dd897', 43030)}
PROTECTED_FILES = {'site/index.html': ('8b3532ee45c0fb33912f20a3bd7943043a348f10a370b9c6716e9edf3c0abf41', 257766), 'site/data/public-sources.json': ('94f8b9f6d0849deb9f26f75947205cfc8c4eb0973045fe958f2121237d987062', 33608), 'site/data/achievement-lines.json': ('1c9ec28bf41a7d79214e84a1c07f3bea1e0d91630dd3a88c93c39ff68a9bccec', 39768), 'site/pftb/index.html': ('b2dd711fcb504b676c3d04f2c42876c2a36ae8f616c0b48b8530aed53822c3b5', 101043), 'content/heritage-20261114.v2.json': ('981876c28a6c863874a8bee8840477fcc04e0f117608d06a4a076b2d0d645350', 72392), 'data/pftb1966_table1.csv': ('92af88d5c1307d0a01b418354d2620a0d9eb8a8c68766adedd8be0feec2ff29a', 515), 'results/pftb1966-uv-replay.json': ('c83794634136e2bd08d09b806b400eea603cf1c27c753ca3db2951b9c2c99432', 7691), 'results/REPLAY_REPORT_zh-CN.md': ('062aca44324f015450198a4bcc2ddba6aa98d896c31dbc81de407991d78b800b', 2976)}
OLD_MANIFESTS = {'provenance/platform-presentation.v1.json': '1ade23238a23977b47eaa6a7dd585509fdca3e270615914292e2341721308782', 'provenance/platform-presentation.v2.json': '91434b5bc8fb51e96b604a6c6437cb363c92370347f22fcbd2a825e5498f0348', 'provenance/platform-presentation.v3.json': '2b290301102abd8cacb5a2d73f7393d8c4f851285a882a08df42eecd960ed286', 'provenance/platform-presentation.v4.json': 'cfc0bc4d29c24a846bb76ceaf3246084d406393cc7d04ec105cad539c21e120b', 'provenance/platform-presentation.v5.json': '7ac60223b0e540de62671017728acd54e66d07e8de2721006c476c8d1734bed9', 'provenance/platform-presentation.v6.json': '1077f6b2e3a78be65ea4b50e81907b629f96c9b3599fcf440493c204b33dbcf3', 'provenance/platform-presentation.v7.json': '2463a97b3bf74b629f1863892d75f36276c97bf9a111905b47cc6179b62eaa7f', 'provenance/platform-presentation.v8.json': 'ab2b362cb5c90dc4b782f8989cc127a31944c49998ee45fbded8b8a7ac77c962', 'provenance/platform-presentation.v9.json': '462fdbfe1c4bd6f0c32f39e2597764037b4562904f0acec4cce00f08c9797017', 'provenance/platform-presentation.v10.json': '65954e3ff6b484a010fa5052f5331eab55149d23a468ae354ab236462598ffd3', 'provenance/platform-presentation.v11.json': 'd6eb2a3faed6f030a28ca5b63e3f3512144c9246f39467d300fc279a967bb004', 'provenance/platform-presentation.v12.json': 'aa9efd831558b47646b687e12be30724c4b8be89a0f98ccb8d06ef56cf04e81f', 'provenance/platform-presentation.v13.json': '263b465d22b1a56b8364a0540a65f742948664f9e50e64d759543685768468cc', 'provenance/platform-presentation.v14.json': '3ea28579d130b065fb805942c5c62861d8f6cd24a0027df7fef7cdc41415750b', 'provenance/platform-presentation.v15.json': 'd21bad493ae97587c7b9493813af3393ed9ed98f5a8dfd3a8790270f7ba49aff', 'provenance/platform-presentation.v16.json': '6b975e980d176ecc481449ca5a96ffadadfecae2eb64d97dfdafb75b85b4a3c0', 'provenance/platform-presentation.v17.json': 'b635b2950e37d5387e8fb68da12109ca585833b769eec38cf25911eb86563ee1', 'provenance/platform-presentation.v18.json': '4fa6f43360d5343e119bb7b9e51e0671f1b4b4ef51ba065067459180a710dfd6', 'provenance/platform-presentation.v19.json': '1a056390024ec41126e36c8b8e6a5275415331ec6eeec524da9df8785e23d59b', 'provenance/platform-presentation.v20.json': '34814fabc405812bccc433018f8a197d181a3da9ac617f84cceda51513774b72', 'provenance/platform-presentation.v21.json': 'a353a25fc9586c3fe78de1ad42a20aee4a1c980de59eda4340df4466d9b45593', 'provenance/platform-presentation.v22.json': '3a9a746a565f7942899f5fdffc244121608e39210c7e6eb466203775dc38cae6', 'provenance/platform-presentation.v23.json': '392490c9d1ddc18942ef5b139eb094155a883f1a340e56adfc9512bfa5430a3d', 'provenance/platform-presentation.v24.json': '118a96428bf0a0fce5467fffd8861c419f97ac078aed708b6fd3b5e6318cc242', 'provenance/platform-presentation.v25.json': '61b8e4ebc4e4800253d886a617b98c9590c370c5ae494731edc8135ebf15e9c1', 'provenance/platform-presentation.v26.json': '0215099d811ba22ee7224e17a2603d3fdccd7dd0b7473297d35ceb419966bd2d', 'provenance/platform-presentation.v27.json': 'a49d94aae9d1ab980a17506441fdb6d8629fd29da5ae798aa3737568f0c2344b', 'provenance/platform-presentation.v28.json': '54449b28f3dfb1c2946872f959df5e8bb1fc4a9b8e04f20b9b0f9daacd8704f3'}
EXPECTED_AI_UPDATES = [{'pointer': '/lines/4/question', 'value': '从组分合成到连续工艺和设备应用，陈先生及合作者解决了哪些具体问题？'}, {'pointer': '/lines/4/ai_role', 'value': '关联传记、原刊和工艺文书，整理化学对象、合成与应用环节、合作署名及原报数量口径。'}, {'pointer': '/lines/4/records', 'value': [{'title': '传记主线：合成、连续中试与配套应用', 'summary': '已按传记55–59页及相关年表，整理F-115两条制备路线与F-502试配、HFC-134a液相连续中试、配套冷冻机油和整机协作。30吨级沿用中试表述；1992年12月50台冰箱、四种类型30多个润滑油分别保留原记录的对象和数量。研究与工程合作按书中明确角色介绍。', 'links': [{'title': '具体学术贡献与合作分工', 'url': 'https://github.com/CCcolab/Chen-Qingyun-AI4Science/blob/main/docs/A05_ACADEMIC_ACHIEVEMENTS_zh-CN.md', 'kind': 'repo'}]}, {'title': '原刊与专利：各按文书保存贡献归属', 'summary': '1978年《五氟氯乙烷合成简法》77–79页已取得并核读，原刊集体署“致冷剂小组”；它提供F-115制备研究记录。两份已取得的工艺说明书分别列林永达／梁与达、吴永明／林永达为发明人；传记中的陈先生项目贡献与这些文书署名分别呈现。实例和文字对照保留在下方专业记录中。', 'links': [{'title': '1978年原刊官方题录', 'url': 'https://sioc-journal.cn/Jwk_hxxb/EN/abstract/abstract342568.shtml', 'kind': 'external'}, {'title': 'CN1075708A公开说明书', 'url': 'https://patents.google.com/patent/CN1075708A/zh', 'kind': 'external'}, {'title': 'CN1308043A公开说明书', 'url': 'https://patents.google.com/patent/CN1308043A/zh', 'kind': 'external'}]}, {'title': '环境关切与资料整理的范围', 'summary': '新增介绍沿用1998年林永达、陈庆云合著综述的官方目录与摘要，说明替代物研究与臭氧层保护的联系。本轮完成的是传记关联整理及新增引用的出处、署名和解释核对；历史技术成效归原团队，未新增实验、中试、量化计算或机理验证。', 'links': [{'title': '1998年综述官方目录与摘要', 'url': 'https://manu56.magtech.com.cn/progchem/CN/volumn/volumn_1306.shtml', 'kind': 'external'}]}]}, {'pointer': '/lines/4/boundaries', 'value': ['F-115组分、F-502混合工质、HFC-134a及配套润滑油分别介绍；原团队的制备、中试与装机记录，和平台本轮资料整理分别呈现。', '30吨级不改写为年产能力，50台冰箱及润滑油种类不外推长期性能或市场规模；工艺文书核读不授予介质相态或完整机理资格。']}, {'pointer': '/lines/4/next_step', 'value': '沿已出版传记继续解释合成路线、连续工艺、配套材料和应用合作之间的学术联系；新增引用按其实际支持范围整理，专业记录保留原报数据。'}, {'pointer': '/lines/4/future_question', 'value': '未来如开展AI辅助工艺或配套性能研究，应另行限定材料、工况和可比较指标，并制定独立研究协议；目前仅作设想。'}, {'pointer': '/lines/4/source_links/0/title', 'value': '制冷剂与配套技术的历史成果'}, {'pointer': '/lines/4/source_links/1/title', 'value': 'HFC-134a液相连续中试'}, {'pointer': '/lines/4/boundary_title', 'value': '资料整理的适用范围'}, {'pointer': '/lines/4/next_step_title', 'value': '资料整理的下一步'}]
NEW_FILES = ('content/a05-biography-narrative.v1.json', 'scripts/render_a05_biography.py', 'docs/A05_ACADEMIC_ACHIEVEMENTS_zh-CN.md', 'scripts/a05_biography_publication.py', 'provenance/platform-presentation.v29.json')
REVIEWED_PUBLIC_FILES = {'content/a05-biography-narrative.v1.json': 'd5cb9d73f3804dd4bc6112477eebb9b259c5b1c80cdb0e4b618b3d2c594dc832', 'scripts/render_a05_biography.py': '9c0c06cc028d78fb41c9e0dae96754eefe59062d2f8f7c5ad00d35817f7fd2d4', 'docs/A05_ACADEMIC_ACHIEVEMENTS_zh-CN.md': '1d95bf451dddcdbb5027541bf9052204281feab0b5cd8f41024cd24501f8eb47', 'scripts/render_ai_research.py': '4293b6cd39150c9e77a6b3c02591c34e83b5d86ecdec675ca9253578af0e2552', 'scripts/render_heritage.py': 'ad5acef15a792d58fbaf9ad995564b455257c84b2e53e31ce2eb7e0520a7134d'}
PUBLIC_DISPLAYS = ('content/a05-biography-narrative.v1.json', 'docs/A05_ACADEMIC_ACHIEVEMENTS_zh-CN.md', 'content/ai-research-section.v1.json', 'docs/AI_RESEARCH_zh-CN.md', 'site/topics/refrigerants/index.html', 'site/research/index.html')
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
        raise ValueError('Unsafe or missing A05 biography-presentation file: '+str(name))
    return path


def _json(root: Path, name: str):
    return json.loads(_file(root, name).read_bytes())


def predecessor_bytes(root: Path, name: str) -> bytes:
    """Recover exact fixed 28b606c bytes before replaying the immutable chain."""
    current = _file(root, name).read_bytes()
    if not (root/MANIFEST).exists():
        return current
    data = _json(root, MANIFEST)
    if not isinstance(data, dict):
        raise ValueError('A05 biography presentation requires a JSON object')
    records, pool = data.get('reversible_text_files'), data.get('reverse_text_patch_pool')
    if not isinstance(records, list) or not isinstance(pool, list):
        raise ValueError('A05 biography presentation requires exact reverse text patches')
    matches = [row for row in records if isinstance(row, dict) and row.get('path') == name]
    if not matches:
        if name in PREDECESSOR_FILES:
            raise ValueError('Missing fixed A05 biography predecessor: '+name)
        return current
    if len(matches) != 1 or name not in PREDECESSOR_FILES:
        raise ValueError('Unauthorized or duplicate A05 biography predecessor: '+name)
    row = matches[0]
    old_sha, old_size = PREDECESSOR_FILES[name]
    if (row.get('old_sha256') != old_sha or row.get('old_bytes') != old_size
            or _sha(current) != row.get('new_sha256') or len(current) != row.get('new_bytes')):
        raise ValueError('A05 biography file differs from complete old/new identities: '+name)
    edits = row.get('edits')
    if not isinstance(edits, list) or not edits:
        raise ValueError('A05 biography changes require nonempty text edits: '+name)
    chunks, cursor, old_end, delta = [], 0, 0, 0
    for edit in edits:
        if not isinstance(edit, dict) or set(edit) != {'old_offset', 'replacement'}:
            raise ValueError('Invalid A05 biography reverse text edit: '+name)
        offset, replacement = edit['old_offset'], edit['replacement']
        if (type(offset) is not int or offset < old_end or type(replacement) is not int
                or not 0 <= replacement < len(pool)):
            raise ValueError('Overlapping or invalid A05 biography reverse edit: '+name)
        pair = pool[replacement]
        if (not isinstance(pair, dict) or set(pair) != {'old', 'new'}
                or not all(isinstance(pair.get(k), str) for k in ('old', 'new'))
                or pair['old'] == pair['new']):
            raise ValueError('Invalid A05 biography replacement pool')
        before, after = pair['old'].encode('utf-8'), pair['new'].encode('utf-8')
        position = offset+delta
        if position < cursor or current[position:position+len(after)] != after:
            raise ValueError('A05 biography reverse replacement differs at exact offset: '+name)
        chunks.extend((current[cursor:position], before))
        cursor, old_end = position+len(after), offset+len(before)
        delta += len(after)-len(before)
    rebuilt = b''.join((*chunks, current[cursor:]))
    if _sha(rebuilt) != old_sha or len(rebuilt) != old_size:
        raise ValueError('A05 biography predecessor cannot be reconstructed exactly: '+name)
    return rebuilt


def _set_pointer(data, pointer: str, value):
    parts = [p.replace('~1', '/').replace('~0', '~') for p in pointer.split('/')[1:]]
    if not pointer.startswith('/') or not parts:
        raise ValueError('Invalid fixed A05 biography JSON pointer')
    parent = data
    for part in parts[:-1]:
        parent = parent[int(part)] if isinstance(parent, list) else parent[part]
    key = int(parts[-1]) if isinstance(parent, list) else parts[-1]
    parent[key] = copy.deepcopy(value)


def _binding(root: Path, name: str) -> dict:
    data = _file(root, name).read_bytes()
    return {'path': name, 'sha256': _sha(data), 'bytes': len(data)}


def apply(root: Path, entries: dict, previous_report: dict) -> tuple[dict, dict]:
    """Validate the current A05-only presentation after exact v28 replay."""
    if not (root/MANIFEST).exists():
        return entries, previous_report
    if not (root/PREVIOUS_MANIFEST).is_file():
        raise ValueError('A05 biography presentation requires its immutable v28 predecessor')
    for name, sha in OLD_MANIFESTS.items():
        if _sha(_file(root, name).read_bytes()) != sha:
            raise ValueError('Historical presentation manifest changed: '+name)
    for name, (sha, size) in PROTECTED_FILES.items():
        value = _file(root, name).read_bytes()
        if _sha(value) != sha or len(value) != size:
            raise ValueError('A01 original source or protected reference changed: '+name)
    data = _json(root, MANIFEST)
    required = {
        'schema_version': '29.0', 'presentation_id': PRESENTATION_ID,
        'publication_kind': 'platform_a05_biography_narrative',
        'previous_presentation_commit': PREVIOUS_COMMIT,
        'previous_presentation': {'path': PREVIOUS_MANIFEST, 'sha256': OLD_MANIFESTS[PREVIOUS_MANIFEST]},
        'original_baseline_sha256': BASELINE_SHA256, 'original_archive_sha256': ARCHIVE_SHA256,
        'allowed_html_paths': list(ROUTES), 'added_html_paths': [], 'additions': [],
        'allowed_display_regions': {'research/index.html': ['ai-a05'], 'topics/refrigerants/index.html': ['main.contents']},
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
        raise ValueError('Unsupported bounded A05 biography presentation v29')
    records, pool = data.get('reversible_text_files'), data.get('reverse_text_patch_pool')
    if (not isinstance(records, list) or not isinstance(pool, list) or not pool
            or any(not isinstance(row, dict) for row in records)
            or len(records) != len(PREDECESSOR_FILES)
            or {row.get('path') for row in records} != set(PREDECESSOR_FILES)
            or len({row.get('path') for row in records}) != len(records)
            or any(not isinstance(row.get('edits'), list) or not row['edits'] or any(
                not isinstance(edit, dict) or type(edit.get('replacement')) is not int
                for edit in row['edits']) for row in records)):
        raise ValueError('A05 biography presentation has an unauthorized predecessor file set')
    if {edit['replacement'] for row in records for edit in row['edits']} != set(range(len(pool))):
        raise ValueError('A05 biography presentation requires exactly its used replacement pool')
    for name, (sha, size) in PREDECESSOR_FILES.items():
        old = predecessor_bytes(root, name)
        if _sha(old) != sha or len(old) != size or old == _file(root, name).read_bytes():
            raise ValueError('A05 biography predecessor differs from fixed 28b606c: '+name)
    expected = json.loads(predecessor_bytes(root, AI))
    for update in EXPECTED_AI_UPDATES:
        _set_pointer(expected, update['pointer'], update['value'])
    if _json(root, AI) != expected:
        raise ValueError('A05 biography JSON changed outside its fixed A05 fields')
    for name, sha in REVIEWED_PUBLIC_FILES.items():
        if _sha(_file(root, name).read_bytes()) != sha:
            raise ValueError('A05 biography source, renderer or document differs from reviewed bytes: '+name)
    for name in PUBLIC_DISPLAYS:
        value = _file(root, name).read_text('utf-8')
        if re.search(r'(?i)private-sources|current-item-register|现阶段待查事项统计|[CD]:[\\/]', value):
            raise ValueError('A05 biography display contains private evidence or a local path: '+name)
    changes = data.get('changes')
    if (not isinstance(changes, list) or len(changes) != len(ROUTES)
            or any(not isinstance(row, dict) for row in changes)
            or {row.get('path') for row in changes} != set(ROUTES)):
        raise ValueError('A05 biography presentation may change only its two existing routes')
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
            raise ValueError('A05 biography route differs from complete old/new identities: '+route)
        source, current = before.decode('utf-8'), after.decode('utf-8')
        if json_scripts.findall(source) != json_scripts.findall(current):
            raise ValueError('A05 biography presentation changed original embedded JSON: '+route)
        old_ids = re.findall(r'\bid="([^\"]+)"', source)
        new_ids = re.findall(r'\bid="([^\"]+)"', current)
        if not set(old_ids).issubset(new_ids) or len(new_ids) != len(set(new_ids)):
            raise ValueError('A05 biography presentation lost or duplicated source/navigation IDs: '+route)
        if route == 'research/index.html':
            pattern = r'<section\b[^>]*\bid="ai-a05"[^>]*>.*?</section>'
            if (len(re.findall(pattern, source, re.S)) != 1 or len(re.findall(pattern, current, re.S)) != 1
                    or re.sub(pattern, '<A05/>', source, flags=re.S) != re.sub(pattern, '<A05/>', current, flags=re.S)):
                raise ValueError('A05 biography changed outside its AI A05 section')
        else:
            pattern = r'(<main\b[^>]*>)(.*?)(</main>)'
            before_main, after_main = list(re.finditer(pattern, source, re.S)), list(re.finditer(pattern, current, re.S))
            if len(before_main) != 1 or len(after_main) != 1:
                raise ValueError('A05 requires one original main region')
            a, b = before_main[0], after_main[0]
            if (a.group(1) != b.group(1) or a.group(3) != b.group(3)
                    or source[:a.start(2)] != current[:b.start(2)]
                    or source[a.end(2):] != current[b.end(2):]):
                raise ValueError('A05 changed original head/header/footer or main wrapper bytes')
        updated[route] = {**old_entry, 'sha256': _sha(after), 'bytes': len(after), 'presentation_id': PRESENTATION_ID}
    for name, expected_entry in updated.items():
        value = _file(root, 'site/'+name).read_bytes()
        if _sha(value) != expected_entry['sha256'] or len(value) != expected_entry['bytes']:
            raise ValueError('A05 biography changed an unlisted website byte: '+name)
    from render_ai_research import inspect_ai_research
    from render_a05_biography import inspect_biography
    checks = [inspect_ai_research(root), inspect_biography(root)]
    if any(c.get('status') != 'passed' for c in checks):
        raise ValueError('A05 biography display differs from source rendering: '+str(checks))
    report = {'path': MANIFEST, 'sha256': _sha(_file(root, MANIFEST).read_bytes()),
        'presentation_id': PRESENTATION_ID, 'publication_kind': required['publication_kind'],
        'changed_paths': list(ROUTES), 'added_paths': [],
        'previous_presentation_commit': PREVIOUS_COMMIT,
        'exact_predecessor_reconstruction': True, 'source_derived_rendering': True,
        'all_v1_v28_manifest_bytes_preserved': True, 'private_originals_not_published': True,
        'original_data_and_embedded_JSON_preserved': True,
        'homepage_achievement_summary_other_lines_and_scientific_data_preserved': True,
        **{k: required[k] for k in ('scientific_review_status', 'release_eligible',
            'scientific_data_unchanged', 'M0_resumed', 'historical_achievement_independent_of_AI_review')}}
    return updated, {**report, 'presentation_chain': [*previous_report['presentation_chain'], report]}
