"""Bounded A08 historical narrative; original evidence and scientific data protected."""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path, PurePosixPath
import re

from a09_biography_publication import (MANIFEST as A09_BIOGRAPHY_MANIFEST,
    predecessor_bytes as a09_biography_predecessor_bytes, apply as apply_a09_biography_presentation)

MANIFEST = 'provenance/platform-presentation.v32.json'
PRESENTATION_ID = 'PLATFORM-A08-BIOGRAPHY-20261117-v32'
PREVIOUS_COMMIT = 'd409f17c3ecf0c20648d2105000891d20e67431b'
PREVIOUS_MANIFEST = 'provenance/platform-presentation.v31.json'
ROUTES = ('research/index.html', 'topics/fluorinated-small-rings/index.html', 'topics/fluoroporphyrins/index.html', 'topics/deoxyfluorination/index.html', 'topics/sulfonyl-fluoride/index.html')
AI = 'content/ai-research-section.v1.json'
DOCUMENTS = ('content/ai-research-section.v1.json', 'scripts/render_ai_research.py', 'docs/AI_RESEARCH_zh-CN.md', 'content/a08-biography-narrative.v1.json', 'scripts/render_a08_biography.py', 'docs/A08_ACADEMIC_ACHIEVEMENTS_zh-CN.md', 'scripts/a07_biography_publication.py', 'scripts/a01_publication_contract.py', 'scripts/render_heritage.py', '.github/workflows/research-ci.yml', '.github/workflows/pages.yml', 'scripts/a08_biography_publication.py')
WORKFLOW_TIMEOUT_FILES = ('.github/workflows/research-ci.yml', '.github/workflows/pages.yml')
PREDECESSOR_FILES = {'site/topics/fluorinated-small-rings/index.html': ('2413c83d4319746f41e940c04fe48bdeda28244235f5a9e8697285c187ba412d', 5924), 'site/topics/fluoroporphyrins/index.html': ('24b6bb744b594573487847c89bbb35571ea56bc15d444ebeac3339379dbc1875', 6018), 'site/topics/deoxyfluorination/index.html': ('2aca9c13eb46f9fedfb02a2adfdc9423c207465f58608bcd671838d4d8045df5', 5550), 'site/topics/sulfonyl-fluoride/index.html': ('fe944efbbfa5a7814015235f4ae3aae101db4046b0c9419986d6855d7ed15b49', 5043), 'content/ai-research-section.v1.json': ('6f6f5c6f7f8f5fda5466202cad0471250649b767ce00d564be73d35943becfaf', 103765), 'docs/AI_RESEARCH_zh-CN.md': ('7e6560d75c08374319b0bee2ac7d7e3e489779c45b7b09b15cf003a24fec999d', 61804), 'site/research/index.html': ('0c33d2316060b8aaf35acfc2cd3a5c4472fa2042fc2dadba0d82d89d3f048c29', 82956), 'scripts/a07_biography_publication.py': ('cb0f5e2c64836187c74776fbf29a38013b800170f02096761c22fd30d16a50bb', 24821), 'scripts/a01_publication_contract.py': ('228d1ea7746554fa9798509ddcbca989aa675a2eea455df54e3f2076acf6b373', 311111), '.github/workflows/research-ci.yml': ('ad0506d56e6db0ce45e929f20435f66415c09615f4fccacf5c3b30820897558e', 2599), '.github/workflows/pages.yml': ('d8238e7d4a16ca88245e7a11aad8c4bf452954f57c2d093761f48f659eaf2ddd', 1949)}
PROTECTED_FILES = {'site/index.html': ('8b3532ee45c0fb33912f20a3bd7943043a348f10a370b9c6716e9edf3c0abf41', 257766), 'site/data/public-sources.json': ('94f8b9f6d0849deb9f26f75947205cfc8c4eb0973045fe958f2121237d987062', 33608), 'site/data/achievement-lines.json': ('1c9ec28bf41a7d79214e84a1c07f3bea1e0d91630dd3a88c93c39ff68a9bccec', 39768), 'site/pftb/index.html': ('b2dd711fcb504b676c3d04f2c42876c2a36ae8f616c0b48b8530aed53822c3b5', 101043), 'content/heritage-20261114.v2.json': ('981876c28a6c863874a8bee8840477fcc04e0f117608d06a4a076b2d0d645350', 72392), 'content/chen-reagent-achievement.v1.json': ('8d13ee4ecaa36a2208867c2510531c8b0d6eb1e06abb8da52c36dc0d7265bcb1', 3884), 'content/chen-reagent-cas-source.v1.json': ('2125b9eaba7853ab02c378ca7c1d78265bbef2895bb2fa512a2cb53981de05cf', 1518), 'docs/CHEN_REAGENT_ACHIEVEMENT_zh-CN.md': ('aff472de27abf8d24eede857e77ae6aa0ce9d5a3a99cf774319250e08ee9128e', 2350), 'data/pftb1966_table1.csv': ('92af88d5c1307d0a01b418354d2620a0d9eb8a8c68766adedd8be0feec2ff29a', 515), 'results/pftb1966-uv-replay.json': ('c83794634136e2bd08d09b806b400eea603cf1c27c753ca3db2951b9c2c99432', 7691), 'results/REPLAY_REPORT_zh-CN.md': ('062aca44324f015450198a4bcc2ddba6aa98d896c31dbc81de407991d78b800b', 2976), 'content/a07-biography-narrative.v1.json': ('22e6121f4f3d61e3676a8ec95b76dc22512df0ab550cfb7c403f809f245016db', 13279), 'scripts/render_a07_biography.py': ('01f5e86435bc9f4eac7f04104892a2d875647f1dd6d3e270e38f3ed28d9dde8e', 9726), 'docs/A07_ACADEMIC_ACHIEVEMENTS_zh-CN.md': ('9d73bbb199e8c6d825550429ae35cb3ea8dffbcd4b17e3b73145603080cc487b', 11338), 'scripts/render_heritage.py': ('d4ec4bc12c8fa082f36f436a6d9c06cc65592d1d03ef75504cfc619bab309740', 44310)}
OLD_MANIFESTS = {'provenance/platform-presentation.v1.json': '1ade23238a23977b47eaa6a7dd585509fdca3e270615914292e2341721308782', 'provenance/platform-presentation.v2.json': '91434b5bc8fb51e96b604a6c6437cb363c92370347f22fcbd2a825e5498f0348', 'provenance/platform-presentation.v3.json': '2b290301102abd8cacb5a2d73f7393d8c4f851285a882a08df42eecd960ed286', 'provenance/platform-presentation.v4.json': 'cfc0bc4d29c24a846bb76ceaf3246084d406393cc7d04ec105cad539c21e120b', 'provenance/platform-presentation.v5.json': '7ac60223b0e540de62671017728acd54e66d07e8de2721006c476c8d1734bed9', 'provenance/platform-presentation.v6.json': '1077f6b2e3a78be65ea4b50e81907b629f96c9b3599fcf440493c204b33dbcf3', 'provenance/platform-presentation.v7.json': '2463a97b3bf74b629f1863892d75f36276c97bf9a111905b47cc6179b62eaa7f', 'provenance/platform-presentation.v8.json': 'ab2b362cb5c90dc4b782f8989cc127a31944c49998ee45fbded8b8a7ac77c962', 'provenance/platform-presentation.v9.json': '462fdbfe1c4bd6f0c32f39e2597764037b4562904f0acec4cce00f08c9797017', 'provenance/platform-presentation.v10.json': '65954e3ff6b484a010fa5052f5331eab55149d23a468ae354ab236462598ffd3', 'provenance/platform-presentation.v11.json': 'd6eb2a3faed6f030a28ca5b63e3f3512144c9246f39467d300fc279a967bb004', 'provenance/platform-presentation.v12.json': 'aa9efd831558b47646b687e12be30724c4b8be89a0f98ccb8d06ef56cf04e81f', 'provenance/platform-presentation.v13.json': '263b465d22b1a56b8364a0540a65f742948664f9e50e64d759543685768468cc', 'provenance/platform-presentation.v14.json': '3ea28579d130b065fb805942c5c62861d8f6cd24a0027df7fef7cdc41415750b', 'provenance/platform-presentation.v15.json': 'd21bad493ae97587c7b9493813af3393ed9ed98f5a8dfd3a8790270f7ba49aff', 'provenance/platform-presentation.v16.json': '6b975e980d176ecc481449ca5a96ffadadfecae2eb64d97dfdafb75b85b4a3c0', 'provenance/platform-presentation.v17.json': 'b635b2950e37d5387e8fb68da12109ca585833b769eec38cf25911eb86563ee1', 'provenance/platform-presentation.v18.json': '4fa6f43360d5343e119bb7b9e51e0671f1b4b4ef51ba065067459180a710dfd6', 'provenance/platform-presentation.v19.json': '1a056390024ec41126e36c8b8e6a5275415331ec6eeec524da9df8785e23d59b', 'provenance/platform-presentation.v20.json': '34814fabc405812bccc433018f8a197d181a3da9ac617f84cceda51513774b72', 'provenance/platform-presentation.v21.json': 'a353a25fc9586c3fe78de1ad42a20aee4a1c980de59eda4340df4466d9b45593', 'provenance/platform-presentation.v22.json': '3a9a746a565f7942899f5fdffc244121608e39210c7e6eb466203775dc38cae6', 'provenance/platform-presentation.v23.json': '392490c9d1ddc18942ef5b139eb094155a883f1a340e56adfc9512bfa5430a3d', 'provenance/platform-presentation.v24.json': '118a96428bf0a0fce5467fffd8861c419f97ac078aed708b6fd3b5e6318cc242', 'provenance/platform-presentation.v25.json': '61b8e4ebc4e4800253d886a617b98c9590c370c5ae494731edc8135ebf15e9c1', 'provenance/platform-presentation.v26.json': '0215099d811ba22ee7224e17a2603d3fdccd7dd0b7473297d35ceb419966bd2d', 'provenance/platform-presentation.v27.json': 'a49d94aae9d1ab980a17506441fdb6d8629fd29da5ae798aa3737568f0c2344b', 'provenance/platform-presentation.v28.json': '54449b28f3dfb1c2946872f959df5e8bb1fc4a9b8e04f20b9b0f9daacd8704f3', 'provenance/platform-presentation.v29.json': '2206e301c22181e3e1a0d5bcce619dd590b4eca3d2968faee6cfbf9a08ed29b7', 'provenance/platform-presentation.v30.json': '952cea23bb612648addc4ac5a5e5cc88acae24a67b8dc98661ae49f79710645b', 'provenance/platform-presentation.v31.json': '2d1195067b1ed7cc9a454329cc499a0b07cc01de0d1f8bdfa001214d9cf2c5a4'}
EXPECTED_AI_UPDATES = [{'pointer': '/lines/7/question', 'value': '从含氟小环到卟啉、大环和晚年试剂，具体合成问题怎样形成新的交叉研究？'}, {'pointer': '/lines/7/ai_role', 'value': '以传记关联分子骨架、具体成果和合作角色；核对新增引用，分别整理历史实验、原作者理论研究及平台资料对应。'}, {'pointer': '/lines/7/records', 'value': [{'title': '历史主线与合作故事', 'summary': '已按传记77–86页整理小环后续转化、湖南大学卟啉合作与共同学习、20π大环的发现故事及晚年研究动机；晚期论文按具体原作补入对象和共同作者。', 'links': [{'title': 'A08（交叉研究与晚年拓展）的具体学术贡献与合作', 'url': 'https://github.com/CCcolab/Chen-Qingyun-AI4Science/blob/main/docs/A08_ACADEMIC_ACHIEVEMENTS_zh-CN.md', 'kind': 'repo'}]}, {'title': '小环与不同大环分别关联', 'summary': '2002含碘环丙烯、2006两类含氟产物、2003卟啉修饰、2007 20π isophlorin与2022含三键18π大环分别介绍。2007 SI／四份CIF对应和2022方法／模型覆盖保留在下方专业记录，不把不同分子或电子数合成统一性质结论。', 'links': [{'title': '含氟小环的合成与转化', 'url': '../topics/fluorinated-small-rings/index.html', 'kind': 'site'}, {'title': '卟啉与大环历史专题', 'url': '../topics/fluoroporphyrins/index.html', 'kind': 'site'}]}, {'title': '已有理论与附件核读的范围', 'summary': '2003两卷SI、2007 SI与CIF、2022 SI及晚年三篇附件的已有取得与核读状态保留。2022原作者已有DFT／TD-DFT及路径模型归其实际作者，平台只整理对象、方法和覆盖范围，不据合著认定陈先生本人执行计算，也不作首次理论研究宣称。', 'links': [{'title': '2022原论文及作者研究入口', 'url': 'https://doi.org/10.1021/acs.orglett.2c00356', 'kind': 'external'}]}, {'title': '晚年方法与表面性质分层', 'summary': '2020／2021脱氧氟化体系、2017烯烃双官能化、2020芳基磺酰氟方法和2023两种短链含醚磺酸盐分别按实际对象与作者介绍；表面性质与环境评价分开，未新增实验或计算。', 'links': [{'title': '脱氧氟化历史专题', 'url': '../topics/deoxyfluorination/index.html', 'kind': 'site'}, {'title': '晚年方法与表面活性分子', 'url': '../topics/sulfonyl-fluoride/index.html', 'kind': 'site'}]}]}, {'pointer': '/lines/7/boundaries', 'value': ['历史实验与已有理论计算归原作者；本轮为传记关联和新增引用核对，SI/CIF资料对应不授予平台结构、实验或机理验证资格。', '20π与18π对应不同具体大环；全分子性质计算与简化路径模型各有范围。表面活性或短链结构不证明低毒、可降解、工业替代或商业应用。']}, {'pointer': '/lines/7/next_step', 'value': '继续解释合成方法、分子结构和合作研究之间的学术联系；新增引用按原文范围整理，已有晶体模型和原作者计算覆盖记录分别保留。'}, {'pointer': '/lines/7/future_question', 'value': '未来AI研究应先限定具体分子和可比较量，并与原作者已有实验、DFT／TD-DFT方法及简化模型比较；目前仅为设想，M0保持暂停。'}, {'pointer': '/lines/7/source_links/0/title', 'value': '含氟小环的合成与反应'}, {'pointer': '/lines/7/source_links/1/title', 'value': '卟啉与大环的历史成果'}, {'pointer': '/lines/7/source_links/2/title', 'value': '两种脱氧氟化体系'}, {'pointer': '/lines/7/source_links/3/title', 'value': '晚年构件与表面活性分子'}, {'pointer': '/lines/7/source_links/4/title', 'value': '含氟离子液体相关记录'}, {'pointer': '/lines/7/boundary_title', 'value': '资料整理的适用范围'}, {'pointer': '/lines/7/next_step_title', 'value': '资料整理的下一步'}]
NEW_FILES = ('content/a08-biography-narrative.v1.json', 'scripts/render_a08_biography.py', 'docs/A08_ACADEMIC_ACHIEVEMENTS_zh-CN.md', 'scripts/a08_biography_publication.py', 'provenance/platform-presentation.v32.json')
REVIEWED_PUBLIC_FILES = {'content/a08-biography-narrative.v1.json': 'e33b1834271cfdc42a36d02589c046fa2b5f34a2033ba93beb63201fe91def82', 'scripts/render_a08_biography.py': '5d31f02e19edecfff1612d5656b1b2ed448e39f8a9d79447b88ee7aea4a407f7', 'docs/A08_ACADEMIC_ACHIEVEMENTS_zh-CN.md': 'c64ea7e4cfde67d25cad6c8fc1538c8167ad69cbeea38fcb473e4b3a7e3a7e37', 'scripts/render_ai_research.py': '4293b6cd39150c9e77a6b3c02591c34e83b5d86ecdec675ca9253578af0e2552', 'scripts/render_heritage.py': 'd4ec4bc12c8fa082f36f436a6d9c06cc65592d1d03ef75504cfc619bab309740'}
PUBLIC_DISPLAYS = ('content/a08-biography-narrative.v1.json', 'docs/A08_ACADEMIC_ACHIEVEMENTS_zh-CN.md', 'content/ai-research-section.v1.json', 'docs/AI_RESEARCH_zh-CN.md', 'site/research/index.html', 'site/topics/fluorinated-small-rings/index.html', 'site/topics/fluoroporphyrins/index.html', 'site/topics/deoxyfluorination/index.html', 'site/topics/sulfonyl-fluoride/index.html')
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
        raise ValueError('Unsafe or missing A08 biography-presentation file: '+str(name))
    return path


def _json(root: Path, name: str):
    return json.loads(a09_biography_predecessor_bytes(root, name))


def predecessor_bytes(root: Path, name: str) -> bytes:
    """Recover exact fixed d409f17 bytes before replaying the immutable chain."""
    current = a09_biography_predecessor_bytes(root, name)
    if not (root/MANIFEST).exists():
        return current
    data = _json(root, MANIFEST)
    if not isinstance(data, dict):
        raise ValueError('A08 biography presentation requires a JSON object')
    records, pool = data.get('reversible_text_files'), data.get('reverse_text_patch_pool')
    if not isinstance(records, list) or not isinstance(pool, list):
        raise ValueError('A08 biography presentation requires exact reverse text patches')
    matches = [row for row in records if isinstance(row, dict) and row.get('path') == name]
    if not matches:
        if name in PREDECESSOR_FILES:
            raise ValueError('Missing fixed A08 biography predecessor: '+name)
        return current
    if len(matches) != 1 or name not in PREDECESSOR_FILES:
        raise ValueError('Unauthorized or duplicate A08 biography predecessor: '+name)
    row = matches[0]
    old_sha, old_size = PREDECESSOR_FILES[name]
    if (row.get('old_sha256') != old_sha or row.get('old_bytes') != old_size
            or _sha(current) != row.get('new_sha256') or len(current) != row.get('new_bytes')):
        raise ValueError('A08 biography file differs from complete old/new identities: '+name)
    edits = row.get('edits')
    if not isinstance(edits, list) or not edits:
        raise ValueError('A08 biography changes require nonempty text edits: '+name)
    chunks, cursor, old_end, delta = [], 0, 0, 0
    for edit in edits:
        if not isinstance(edit, dict) or set(edit) != {'old_offset', 'replacement'}:
            raise ValueError('Invalid A08 biography reverse text edit: '+name)
        offset, replacement = edit['old_offset'], edit['replacement']
        if (type(offset) is not int or offset < old_end or type(replacement) is not int
                or not 0 <= replacement < len(pool)):
            raise ValueError('Overlapping or invalid A08 biography reverse edit: '+name)
        pair = pool[replacement]
        if (not isinstance(pair, dict) or set(pair) != {'old', 'new'}
                or not all(isinstance(pair.get(k), str) for k in ('old', 'new'))
                or pair['old'] == pair['new']):
            raise ValueError('Invalid A08 biography replacement pool')
        before, after = pair['old'].encode('utf-8'), pair['new'].encode('utf-8')
        position = offset+delta
        if position < cursor or current[position:position+len(after)] != after:
            raise ValueError('A08 biography reverse replacement differs at exact offset: '+name)
        chunks.extend((current[cursor:position], before))
        cursor, old_end = position+len(after), offset+len(before)
        delta += len(after)-len(before)
    rebuilt = b''.join((*chunks, current[cursor:]))
    if _sha(rebuilt) != old_sha or len(rebuilt) != old_size:
        raise ValueError('A08 biography predecessor cannot be reconstructed exactly: '+name)
    return rebuilt


def _set_pointer(data, pointer: str, value):
    parts = [p.replace('~1', '/').replace('~0', '~') for p in pointer.split('/')[1:]]
    if not pointer.startswith('/') or not parts:
        raise ValueError('Invalid fixed A08 biography JSON pointer')
    parent = data
    for part in parts[:-1]:
        parent = parent[int(part)] if isinstance(parent, list) else parent[part]
    key = int(parts[-1]) if isinstance(parent, list) else parts[-1]
    parent[key] = copy.deepcopy(value)


def _binding(root: Path, name: str) -> dict:
    data = a09_biography_predecessor_bytes(root, name)
    return {'path': name, 'sha256': _sha(data), 'bytes': len(data)}


def apply(root: Path, entries: dict, previous_report: dict) -> tuple[dict, dict]:
    """Validate the current A08-only presentation after exact v31 replay."""
    if not (root/MANIFEST).exists():
        if (root/A09_BIOGRAPHY_MANIFEST).exists():
            raise ValueError('A09 heritage presentation requires its immutable v32 predecessor')
        return entries, previous_report
    if not (root/PREVIOUS_MANIFEST).is_file():
        raise ValueError('A08 biography presentation requires its immutable v31 predecessor')
    for name, sha in OLD_MANIFESTS.items():
        if _sha(a09_biography_predecessor_bytes(root, name)) != sha:
            raise ValueError('Historical presentation manifest changed: '+name)
    for name, (sha, size) in PROTECTED_FILES.items():
        value = a09_biography_predecessor_bytes(root, name)
        if _sha(value) != sha or len(value) != size:
            raise ValueError('A01 original source or protected reference changed: '+name)
    data = _json(root, MANIFEST)
    required = {
        'schema_version': '32.0', 'presentation_id': PRESENTATION_ID,
        'publication_kind': 'platform_a08_biography_narrative',
        'previous_presentation_commit': PREVIOUS_COMMIT,
        'previous_presentation': {'path': PREVIOUS_MANIFEST, 'sha256': OLD_MANIFESTS[PREVIOUS_MANIFEST]},
        'original_baseline_sha256': BASELINE_SHA256, 'original_archive_sha256': ARCHIVE_SHA256,
        'allowed_html_paths': list(ROUTES), 'added_html_paths': [], 'additions': [],
        'allowed_display_regions': {route: ['ai-a08'] if route == 'research/index.html' else ['main.contents'] for route in ROUTES},
        'editorial_documents': [_binding(root, name) for name in DOCUMENTS],
        'protected_website_members': {name: {'sha256': row['sha256'], 'bytes': row['bytes']}
            for name, row in entries.items() if name not in ROUTES},
        'reconstruction_kind': 'deduplicated_exact_utf8_text_edits',
        'scientific_review_status': 'review_required', 'release_eligible': False,
        'scientific_data_unchanged': True, 'M0_resumed': False,
        'historical_achievement_independent_of_AI_review': True,
        'allowed_ai_json_pointers': [u['pointer'] for u in EXPECTED_AI_UPDATES],
        'allowed_new_files': list(NEW_FILES),
        'workflow_timeout_changes': {name: {'occurrence': 1, 'from_minutes': 10, 'to_minutes': 40, 'all_other_bytes_preserved': True} for name in WORKFLOW_TIMEOUT_FILES},
    }
    if (not isinstance(data, dict) or any(data.get(k) != v for k, v in required.items())
            or any(data.get(k) is not required[k] for k in ('release_eligible',
                'scientific_data_unchanged', 'M0_resumed', 'historical_achievement_independent_of_AI_review'))
            or any(type(data.get(k)) is not int or data[k] != 0 for k in ('new_quantum_calls', 'new_model_API_calls'))
            or not isinstance(data.get('authorization'), str) or not data['authorization'].strip()):
        raise ValueError('Unsupported bounded A08 biography presentation v32')
    records, pool = data.get('reversible_text_files'), data.get('reverse_text_patch_pool')
    if (not isinstance(records, list) or not isinstance(pool, list) or not pool
            or any(not isinstance(row, dict) for row in records)
            or len(records) != len(PREDECESSOR_FILES)
            or {row.get('path') for row in records} != set(PREDECESSOR_FILES)
            or len({row.get('path') for row in records}) != len(records)
            or any(not isinstance(row.get('edits'), list) or not row['edits'] or any(
                not isinstance(edit, dict) or type(edit.get('replacement')) is not int
                for edit in row['edits']) for row in records)):
        raise ValueError('A08 biography presentation has an unauthorized predecessor file set')
    if {edit['replacement'] for row in records for edit in row['edits']} != set(range(len(pool))):
        raise ValueError('A08 biography presentation requires exactly its used replacement pool')
    for name, (sha, size) in PREDECESSOR_FILES.items():
        old = predecessor_bytes(root, name)
        if _sha(old) != sha or len(old) != size or old == a09_biography_predecessor_bytes(root, name):
            raise ValueError('A08 biography predecessor differs from fixed d409f17: '+name)
    for name in WORKFLOW_TIMEOUT_FILES:
        old = predecessor_bytes(root, name)
        if (old.count(b'    timeout-minutes: 10') != (2 if name.endswith('pages.yml') else 1)
                or old.replace(b'    timeout-minutes: 10', b'    timeout-minutes: 40', 1) != a09_biography_predecessor_bytes(root, name)):
            raise ValueError('A08 may only extend the first workflow job timeout: '+name)
    expected = json.loads(predecessor_bytes(root, AI))
    for update in EXPECTED_AI_UPDATES:
        _set_pointer(expected, update['pointer'], update['value'])
    if _json(root, AI) != expected:
        raise ValueError('A08 biography JSON changed outside its fixed A08 fields')
    for name, sha in REVIEWED_PUBLIC_FILES.items():
        if _sha(a09_biography_predecessor_bytes(root, name)) != sha:
            raise ValueError('A08 biography source, renderer or document differs from reviewed bytes: '+name)
    for name in PUBLIC_DISPLAYS:
        value = a09_biography_predecessor_bytes(root, name).decode('utf-8')
        if re.search(r'(?i)private-sources|current-item-register|现阶段待查事项统计|[CD]:[\\/]', value):
            raise ValueError('A08 biography display contains private evidence or a local path: '+name)
    changes = data.get('changes')
    if (not isinstance(changes, list) or len(changes) != len(ROUTES)
            or any(not isinstance(row, dict) for row in changes)
            or {row.get('path') for row in changes} != set(ROUTES)):
        raise ValueError('A08 biography presentation may change only its five existing routes')
    updated = {name: dict(row) for name, row in entries.items()}
    json_scripts = re.compile(r'<script\b[^>]*\btype\s*=\s*["\']application/(?:ld\+)?json["\'][^>]*>.*?</script\s*>', re.I | re.S)
    for item in changes:
        route = item['path']; old_entry = entries[route]
        before = predecessor_bytes(root, 'site/'+route)
        after = a09_biography_predecessor_bytes(root, 'site/'+route)
        if (item.get('old_sha256') != old_entry['sha256'] or item.get('old_bytes') != old_entry['bytes']
                or _sha(before) != old_entry['sha256'] or len(before) != old_entry['bytes']
                or item.get('new_sha256') != _sha(after) or item.get('new_bytes') != len(after)
                or before == after or not isinstance(item.get('reason'), str) or not item['reason'].strip()):
            raise ValueError('A08 biography route differs from complete old/new identities: '+route)
        source, current = before.decode('utf-8'), after.decode('utf-8')
        if json_scripts.findall(source) != json_scripts.findall(current):
            raise ValueError('A08 biography presentation changed original embedded JSON: '+route)
        old_ids = re.findall(r'\bid="([^\"]+)"', source)
        new_ids = re.findall(r'\bid="([^\"]+)"', current)
        if not set(old_ids).issubset(new_ids) or len(new_ids) != len(set(new_ids)):
            raise ValueError('A08 biography presentation lost or duplicated source/navigation IDs: '+route)
        if route == 'research/index.html':
            pattern = r'<section\b[^>]*\bid="ai-a08"[^>]*>.*?</section>'
            if (len(re.findall(pattern, source, re.S)) != 1 or len(re.findall(pattern, current, re.S)) != 1
                    or re.sub(pattern, '<A08/>', source, flags=re.S) != re.sub(pattern, '<A08/>', current, flags=re.S)):
                raise ValueError('A08 biography changed outside its AI A08 section')
        else:
            pattern = r'(<main\b[^>]*>)(.*?)(</main>)'
            before_main, after_main = list(re.finditer(pattern, source, re.S)), list(re.finditer(pattern, current, re.S))
            if len(before_main) != 1 or len(after_main) != 1:
                raise ValueError('A08 requires one original main region')
            a, b = before_main[0], after_main[0]
            if (a.group(1) != b.group(1) or a.group(3) != b.group(3)
                    or source[:a.start(2)] != current[:b.start(2)]
                    or source[a.end(2):] != current[b.end(2):]):
                raise ValueError('A08 changed original head/header/footer or main wrapper bytes')
        updated[route] = {**old_entry, 'sha256': _sha(after), 'bytes': len(after), 'presentation_id': PRESENTATION_ID}
    for name, expected_entry in updated.items():
        value = a09_biography_predecessor_bytes(root, 'site/'+name)
        if _sha(value) != expected_entry['sha256'] or len(value) != expected_entry['bytes']:
            raise ValueError('A08 biography changed an unlisted website byte: '+name)
    from render_ai_research import inspect_ai_research
    from render_a08_biography import inspect_biography
    checks = [inspect_ai_research(root), inspect_biography(root)]
    if any(c.get('status') != 'passed' for c in checks):
        raise ValueError('A08 biography display differs from source rendering: '+str(checks))
    report = {'path': MANIFEST, 'sha256': _sha(_file(root, MANIFEST).read_bytes()),
        'presentation_id': PRESENTATION_ID, 'publication_kind': required['publication_kind'],
        'changed_paths': list(ROUTES), 'added_paths': [],
        'previous_presentation_commit': PREVIOUS_COMMIT,
        'exact_predecessor_reconstruction': True, 'source_derived_rendering': True,
        'all_v1_v31_manifest_bytes_preserved': True, 'private_originals_not_published': True,
        'original_data_and_embedded_JSON_preserved': True, 'only_two_workflow_job_timeouts_extended': True,
        'homepage_achievement_summary_other_lines_and_scientific_data_preserved': True,
        **{k: required[k] for k in ('scientific_review_status', 'release_eligible',
            'scientific_data_unchanged', 'M0_resumed', 'historical_achievement_independent_of_AI_review')}}
    return apply_a09_biography_presentation(root, updated,
        {**report, 'presentation_chain': [*previous_report['presentation_chain'], report]})
