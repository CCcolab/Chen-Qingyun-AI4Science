"""Explicit A01 progress-page exceptions to the preserved YouMind baseline.

This never grants scientific release or modifies the original baseline.
"""
from __future__ import annotations

import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path, PurePosixPath
import re

BASELINE_SHA256 = '5e3e70988d76ac1d777ff85ee7c1945341e2141767fc77560c6cea39eabab329'
ARCHIVE_SHA256 = 'fa9740d7a244ab4d52885600a312487869d780a82517aa0d0a401215696c4d3e'
REVISION_PATH = 'provenance/a01-site-revision.v1.json'
PROGRESS_PATH = 'research/a01/public-progress.v1.json'
REVISION_V2_PATH = 'provenance/a01-site-revision.v2.json'
PROGRESS_V2_PATH = 'research/a01/public-progress.v2.json'
CURRENT_PATH = 'research/a01/public-progress.current.json'
PRESENTATION_PATH = 'provenance/platform-presentation.v1.json'
PRESENTATION_ID = 'PLATFORM-HERITAGE-20261114-v1'
PRESENTATION_PREVIOUS_COMMIT = '74775199743f06f447278ef6aadff526ee604274'
PRESENTATION_V1_SHA256 = '1ade23238a23977b47eaa6a7dd585509fdca3e270615914292e2341721308782'
PRESENTATION_V2_PATH = 'provenance/platform-presentation.v2.json'
PRESENTATION_V2_ID = 'PLATFORM-HERITAGE-20261114-v2'
PRESENTATION_V2_PREVIOUS_COMMIT = '4a42dff633e9f337768e3dc5e16f7c7af72af10d'
PRESENTATION_V2_SHA256 = '91434b5bc8fb51e96b604a6c6437cb363c92370347f22fcbd2a825e5498f0348'
PRESENTATION_V3_PATH = 'provenance/platform-presentation.v3.json'
PRESENTATION_V3_ID = 'PLATFORM-NUMBERING-20261114-v3'
PRESENTATION_V3_PREVIOUS_COMMIT = '50cdd20cd8dfd188986d242baa383d68bd6a6a3f'
PRESENTATION_V3_SHA256 = '2b290301102abd8cacb5a2d73f7393d8c4f851285a882a08df42eecd960ed286'
PRESENTATION_V4_PATH = 'provenance/platform-presentation.v4.json'
PRESENTATION_V4_ID = 'PLATFORM-NAVIGATION-20261114-v4'
PRESENTATION_V4_PREVIOUS_COMMIT = 'c21ae7aa3c424eedce27a7131480eb82bb8461e6'
PRESENTATION_V4_SHA256 = 'cfc0bc4d29c24a846bb76ceaf3246084d406393cc7d04ec105cad539c21e120b'
PRESENTATION_V5_PATH = 'provenance/platform-presentation.v5.json'
PRESENTATION_V5_ID = 'PLATFORM-HERITAGE-ENRICHMENT-20261114-v5'
PRESENTATION_V5_PREVIOUS_COMMIT = 'a95bc602ba3529cfaeca5a51e307b9073823463e'
PRESENTATION_V5_SHA256 = '7ac60223b0e540de62671017728acd54e66d07e8de2721006c476c8d1734bed9'
PRESENTATION_V6_PATH = 'provenance/platform-presentation.v6.json'
PRESENTATION_V6_ID = 'PLATFORM-CHEN-REAGENT-20261114-v6'
PRESENTATION_V6_PREVIOUS_COMMIT = '172ac5f80cb4b38d1bb75b1d03cf328487460618'
PRESENTATION_V6_SHA256 = '1077f6b2e3a78be65ea4b50e81907b629f96c9b3599fcf440493c204b33dbcf3'
PRESENTATION_V7_PATH = 'provenance/platform-presentation.v7.json'
PRESENTATION_V7_ID = 'PLATFORM-CHEN-REAGENT-CAS-20261114-v7'
PRESENTATION_V7_PREVIOUS_COMMIT = 'f42d99bdd78d63e149b17e5d95c094ad68e9cc9d'
PRESENTATION_V7_SHA256 = '2463a97b3bf74b629f1863892d75f36276c97bf9a111905b47cc6179b62eaa7f'
PRESENTATION_V8_PATH = 'provenance/platform-presentation.v8.json'
PRESENTATION_V8_ID = 'PLATFORM-PUBLIC-ACADEMIC-20261114-v8'
PRESENTATION_V8_PREVIOUS_COMMIT = '9ced00530776228af60cdec24c8a830b2fbce06c'
PRESENTATION_V8_SHA256 = 'ab2b362cb5c90dc4b782f8989cc127a31944c49998ee45fbded8b8a7ac77c962'
PRESENTATION_V9_PATH = 'provenance/platform-presentation.v9.json'
PRESENTATION_V9_ID = 'PLATFORM-A01-HISTORICAL-20261114-v9'
PRESENTATION_V9_PREVIOUS_COMMIT = '6eb2cf5117aeeba29160263845e1f5604a8b3102'
A01_HISTORY_SNAPSHOT = 'provenance/a01-history-previous'
A01_HISTORY_CONTENT = 'content/a01-historical-achievements.v1.json'
A01_HISTORY_DOCUMENT = 'docs/A01_HISTORICAL_ACHIEVEMENTS_zh-CN.md'
A01_HISTORY_DOCUMENTS = ('README.md', 'research/a01/README.md', A01_HISTORY_CONTENT,
                         A01_HISTORY_DOCUMENT, 'scripts/render_a01_history.py')
A01_HISTORY_ALLOWED_PATHS = {'index.html', 'achievements/index.html',
                            'topics/early-fluoroketones/index.html'}
PRESENTATION_V9_SHA256 = '462fdbfe1c4bd6f0c32f39e2597764037b4562904f0acec4cce00f08c9797017'
PRESENTATION_V10_PATH = 'provenance/platform-presentation.v10.json'
PRESENTATION_V10_ID = 'PLATFORM-A01-FIRST-REPORT-20261114-v10'
PRESENTATION_V10_PREVIOUS_COMMIT = '14fe8326f2cc42a4d424337f358f3c9386295a95'
PRESENTATION_V10_SHA256 = '65954e3ff6b484a010fa5052f5331eab55149d23a468ae354ab236462598ffd3'
PRESENTATION_V11_PATH = 'provenance/platform-presentation.v11.json'
PRESENTATION_V11_ID = 'PLATFORM-PUBLIC-LINE-LABELS-20261114-v11'
PRESENTATION_V11_PREVIOUS_COMMIT = 'be48dfc22988d7e4870b2e747b7752db88e1d245'
PRESENTATION_V11_SHA256 = 'd6eb2a3faed6f030a28ca5b63e3f3512144c9246f39467d300fc279a967bb004'
PRESENTATION_V12_PATH = 'provenance/platform-presentation.v12.json'
PRESENTATION_V12_ID = 'PLATFORM-AI-RESEARCH-20261114-v12'
PRESENTATION_V12_PREVIOUS_COMMIT = '1c3c6a0f329d5259a53e94bee9227b7a5cb35523'
AI_RESEARCH_ROUTE = 'research/index.html'
AI_RESEARCH_CONTENT = 'content/ai-research-section.v1.json'
AI_RESEARCH_RENDERER = 'scripts/render_ai_research.py'
AI_RESEARCH_DOCUMENT = 'docs/AI_RESEARCH_zh-CN.md'
AI_RESEARCH_ALLOWED_PATHS = {'index.html', 'achievements/index.html'}
# Every editable existing file is bound to the fixed post-v11 commit. New
# source files and the single new HTML route have no predecessor snapshot.
AI_RESEARCH_PREDECESSOR_FILES = {
    'README.md': ('16db2665cb7ac90f8f0eb2a7e6e55b5cd2736a50e4ed66144180f524cb9aa836', 6628),
    'site/index.html': ('51a0d1a3f903722c61994f24d54645e744ca83e7f61b7d9475cef883f8a7e0ee', 254766),
    'site/achievements/index.html': ('eb85fe01abc800fd7d8f29bbf90513a967cb4023caa8d76fdf2976fac35433a8', 95504),
    'scripts/render_a01_history.py': ('b394d27a930f615407383fd99269907e850db11978e4a81bf1e40e03160abbef', 15868),
    'scripts/public_line_labels.py': ('5309aade33395ac33759d2ce2e1d20206883401ab83683b866e9ebd281c60854', 9652),
    'scripts/a01_publication_contract.py': ('24c110c4004de129ed12fcc1896b600820b5f52a18453cb5ebd2f8e77e8e2a41', 109818),
    'scripts/check_site.py': ('0f43747faa721f49f261639e7b11376f36f0dea23a6357f19004c2eaa6c1b487', 21682),
    'scripts/build_site.py': ('15b65cac24ca27be938a6a730cf85fcf483fcec30866ad997339a7535bee90da', 3210),
    'scripts/verify_online.py': ('abce52d29ea822e50b38bd5cf2428a616c3a555a0b8d378710673d410c74f378', 12121),
}
AI_RESEARCH_DOCUMENTS = ('README.md', 'scripts/render_a01_history.py',
    'scripts/public_line_labels.py', 'scripts/a01_publication_contract.py',
    'scripts/check_site.py', 'scripts/build_site.py', 'scripts/verify_online.py',
    AI_RESEARCH_CONTENT, AI_RESEARCH_RENDERER, AI_RESEARCH_DOCUMENT)
PUBLIC_LABEL_MARKDOWN = ('README.md', 'research/a01/README.md',
    'docs/ACADEMIC_ACHIEVEMENTS_zh-CN.md', 'docs/PLATFORM_PURPOSE_zh-CN.md',
    'docs/PLATFORM_ROADMAP_zh-CN.md', 'docs/CHEN_REAGENT_ACHIEVEMENT_zh-CN.md',
    'docs/A01_FIRST_REPORT_zh-CN.md')
PUBLIC_LABEL_RENDERERS = ('scripts/render_heritage.py', 'scripts/render_a01_history.py')
PUBLIC_LABEL_DOCUMENTS = (*PUBLIC_LABEL_MARKDOWN, *PUBLIC_LABEL_RENDERERS,
    'scripts/public_line_labels.py', 'content/achievement-labels.v1.json',
    'scripts/check_site.py', 'scripts/check_navigation.py', 'scripts/a01_publication_contract.py')
# Fixed be48dfc predecessor identities for the only editable prose/renderers.
# The v10-bound subset is also checked by its immutable historical declaration.
PUBLIC_LABEL_PREDECESSOR_DOCUMENTS = {
    'README.md': ('7bc7125d6eb1ab45f192b250478bc4ad719be508178a67932e4ce2654c3f3a78', 6420),
    'research/a01/README.md': ('a7b5fb969b53a3259c334eb55c378586b000563aabfd500ee031f4c7db099739', 6163),
    'docs/ACADEMIC_ACHIEVEMENTS_zh-CN.md': ('cedd6549296183099e5b17ee38d671c6582659ad9ef2eb811eba01ac53a7785c', 68459),
    'docs/PLATFORM_PURPOSE_zh-CN.md': ('85340277bafd18a5579a48176c7f1d44eb42259e2fd2ee547a956bb1451d576a', 4855),
    'docs/PLATFORM_ROADMAP_zh-CN.md': ('045e37f94478890cb12bdab1d70c1c75636d4952adc602dc5d511f2cb27753b6', 6496),
    'docs/CHEN_REAGENT_ACHIEVEMENT_zh-CN.md': ('3dbe6da43c1155ef733728fc5d3e4704ad982760561cdca6252f0e58362929f0', 2302),
    'docs/A01_FIRST_REPORT_zh-CN.md': ('b6de9df1b0dd742ba038bc6bc80ad6ef3ea61663a4f4eadb151345df9cb4f339', 7770),
    'scripts/render_heritage.py': ('f63ceebaac35c67f6072e6ad57379b268737953621967ce9a5536e4f605ade3f', 40839),
    'scripts/render_a01_history.py': ('894c8fe1f76beae187ea0f9d105f6ae71cf8beec4c7a4005c7c780e62ea6fe8c', 15804),
}
A01_FIRST_REPORT_SNAPSHOT = 'provenance/a01-first-report-previous'
A01_FIRST_REPORT_CONTENT = 'content/a01-historical-achievements.v2.json'
A01_FIRST_REPORT_DOCUMENTS = ('README.md', 'research/a01/README.md',
    'scripts/render_a01_history.py', A01_FIRST_REPORT_CONTENT, 'docs/A01_FIRST_REPORT_zh-CN.md')
A01_FIRST_REPORT_OLD_DOCUMENTS = ('README.md', 'research/a01/README.md', 'scripts/render_a01_history.py')
A01_FIRST_REPORT_MARKERS = {'index.html': 'A01_HISTORY_HOME',
    'achievements/index.html': 'A01_HISTORY_SUMMARY',
    'topics/early-fluoroketones/index.html': 'A01_HISTORY_TOPIC'}
PUBLIC_PRESENTATION_SNAPSHOT = 'provenance/public-presentation-previous'
PUBLIC_ACADEMIC_DOCUMENT = 'docs/ACADEMIC_ACHIEVEMENTS_zh-CN.md'
CHEN_REAGENT_CAS_SOURCE_PATH = 'content/chen-reagent-cas-source.v1.json'
PRESENTATION_V6_ALLOWED_PATHS = {'index.html', 'achievements/index.html',
                                 'topics/chen-reagent/index.html'}
CHEN_REAGENT_CONTENT_PATH = 'content/chen-reagent-achievement.v1.json'
CHEN_REAGENT_DOCUMENT = 'docs/CHEN_REAGENT_ACHIEVEMENT_zh-CN.md'
PRESENTATION_V5_README_SNAPSHOT = 'provenance/platform-presentation-v5-documents/README.md'
PRESENTATION_V5_ALLOWED_PATHS = {'index.html', 'achievements/index.html',
    'topics/fluoromonomers/index.html', 'topics/refrigerants/index.html',
    'topics/perfluorosulfonates/index.html', 'topics/chen-reagent/index.html',
    'topics/single-electron-transfer/index.html'}
NUMBERING_PATHS = {'index.html', 'achievements/index.html'}
HERITAGE_CONTENT_PATH = 'content/heritage-20261114.v1.json'
HERITAGE_CONTENT_V2_PATH = 'content/heritage-20261114.v2.json'
HERITAGE_ENRICHMENT_DOCUMENT = 'docs/HERITAGE_ENRICHMENT_20261114_zh-CN.md'
PRESENTATION_V2_README_SNAPSHOT = 'provenance/platform-presentation-v2-documents/README.md'
PRESENTATION_V2_DOCUMENTS = ('README.md', 'docs/PLATFORM_ROADMAP_zh-CN.md',
    HERITAGE_CONTENT_PATH, 'docs/HERITAGE_INVENTORY_20261114_zh-CN.md')
PRESENTATION_V1_DOCUMENT_SNAPSHOTS = {
    'README.md': 'provenance/platform-presentation-v1-documents/README.md',
    'docs/PLATFORM_PURPOSE_zh-CN.md': 'provenance/platform-presentation-v1-documents/PLATFORM_PURPOSE_zh-CN.md',
    'docs/PLATFORM_ROADMAP_zh-CN.md': 'provenance/platform-presentation-v1-documents/PLATFORM_ROADMAP_zh-CN.md',
}
# Exact complete marker-block bytes from fixed commit 172ac5f, including the
# marker comments. They can be checked in a shallow CI checkout without Git.
FROZEN_HERITAGE_BLOCKS = {
    ('achievements/index.html', 'HERITAGE_INVENTORY'): ('691b8ea25e1143daa670b97b59dc66f16b74e7a137cc1a5053e33fcf44bb45af', 46861),
    ('achievements/index.html', 'HERITAGE_STORIES_ALL'): ('01b9679241342037c3839bdab4e50bf03f59ef5a839707b53ffb22743c685370', 22082),
    ('index.html', 'HERITAGE_LIFE'): ('fb541b99d2d6c9f1e5c6291908a9251dc7321c5eb24b27976e994461771e4346', 10640),
    ('index.html', 'HERITAGE_STORIES'): ('640391a25a838ee4ca40598697852e0cc9e83d116cc952a7f732d1360f1d3d18', 8361),
    ('index.html', 'HERITAGE_SOURCES'): ('98ff5228de42ea0ec044a3a6911a72d0053e7f45e3776b11267fd28e4481aafe', 91313),
    ('topics/chen-reagent/index.html', 'HERITAGE_CONTEXT'): ('145f3456b28ab158f45d0819ccd41a47c93f595ef23c5176267b215b306bd692', 3401),
    ('topics/fluoromonomers/index.html', 'HERITAGE_CONTEXT'): ('b1fec849d5d4b0e32271d7dc14f4634848f7392df37a6ec7dea62bfd1e2fe50a', 4039),
    ('topics/perfluorosulfonates/index.html', 'HERITAGE_CONTEXT'): ('00427d0543b055482a051a5da8b703daa3312e89a6f62f1fccb2c2ad395df9fd', 3525),
    ('topics/refrigerants/index.html', 'HERITAGE_CONTEXT'): ('76b69ca078c8ce82624e740ce9598fc754f537d17178c4e8ae5b8e4a9395320c', 4372),
    ('topics/single-electron-transfer/index.html', 'HERITAGE_CONTEXT'): ('4541764b3da3f99c8bf76c56ad76f30acbe482009d7b800e0251cec7868453e7', 4464),
}
REVISION_V2_SHA256 = '9d1a800ae978b4eef814aa4c0b4c99f6faa35f79b7fd4315edc1aa430a2ad845'
PROGRESS_V2_SHA256 = '0168bad2419df9a16c18fa832116afa3722a783f0186f933c7e7d5b1f6eb7823'
CURRENT_SHA256 = '590b0df398766c8d5908d8cf9da775f71c6412e9364465b0b8b5fd34cd610f10'
PRESENTATION_DOCUMENTS = ('README.md', 'docs/PLATFORM_PURPOSE_zh-CN.md',
                          'docs/PLATFORM_ROADMAP_zh-CN.md')
HISTORICAL_DOCUMENTS = {
    'README_zh-CN.md': {'sha256': 'f8b1baca5be76d565fa786a4c4b88c82bdc574c26ab8fa943566b94b796c2f36', 'bytes': 3111},
    'docs/RESEARCH_ROADMAP_zh-CN.md': {'sha256': 'e8a219f4b971b7d5862b986a1ee0b5ab9fef86352e7d3653ac2462271e322155', 'bytes': 9584},
    'docs/GITHUB_HANDOFF_zh-CN.md': {'sha256': 'd3fb79397cc32e51472c4388693d4fc9d4bd5ef95da01652099c666d282d04cc', 'bytes': 4586},
}
REVISION_V1_SHA256 = '47c875aceb4b37b17a38bfd96eca694b08f3c321b396c2d0f5da4181a72b11bd'
PROGRESS_V1_SHA256 = 'eca8d0ae472c3e49c99d7f8f03cb3e317bc860e5ec29ab95de65c7276f1cd7dd'
TOPIC_PATH = 'topics/early-fluoroketones/index.html'
ALLOWED_CHANGES = {TOPIC_PATH, 'index.html', 'achievements/index.html'}
SHA = re.compile(r'[0-9a-f]{64}')
COMMIT = re.compile(r'[0-9a-f]{40}')


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text('utf-8-sig'))


def project_file(root: Path, name: str) -> Path:
    relative = PurePosixPath(name)
    if (not name or relative.is_absolute() or '..' in relative.parts or '\\' in name
            or relative.as_posix() != name):
        raise ValueError('Unsafe project-relative evidence path: '+str(name))
    candidate = root/name
    if candidate.is_symlink() or not candidate.is_file() or not candidate.resolve().is_relative_to(root.resolve()):
        raise ValueError('Missing or nonregular evidence: '+name)
    return candidate


def ai_research_predecessor_bytes(root: Path, name: str) -> bytes:
    """Reconstruct the fixed v11 edition before replaying its older promises.

    The successor stores only ordered changed UTF-8 segments. Both complete
    identities are checked; no predecessor page or document is copied.
    """
    current = project_file(root, name).read_bytes()
    if not (root/PRESENTATION_V12_PATH).exists():
        return current
    data = read_json(project_file(root, PRESENTATION_V12_PATH))
    if not isinstance(data, dict):
        raise ValueError('AI research presentation must be a JSON object')
    files, pool = data.get('reversible_text_files'), data.get('reverse_text_patch_pool')
    if not isinstance(files, list) or not isinstance(pool, list):
        raise ValueError('AI research requires its exact reversible text patch records')
    matches = [row for row in files if isinstance(row, dict) and row.get('path') == name]
    if not matches:
        return current
    if len(matches) != 1 or name not in AI_RESEARCH_PREDECESSOR_FILES:
        raise ValueError('Unauthorized or duplicate AI research predecessor record: '+name)
    record = matches[0]
    old_sha, old_size = AI_RESEARCH_PREDECESSOR_FILES[name]
    if (record.get('old_sha256') != old_sha or record.get('old_bytes') != old_size
            or hashlib.sha256(current).hexdigest() != record.get('new_sha256')
            or len(current) != record.get('new_bytes')):
        raise ValueError('AI research file differs from its complete old/new identities: '+name)
    edits = record.get('edits')
    if not isinstance(edits, list) or not edits:
        raise ValueError('AI research changes require nonempty text edits: '+name)
    chunks, cursor, old_end, delta = [], 0, 0, 0
    for edit in edits:
        if not isinstance(edit, dict) or set(edit) != {'old_offset', 'replacement'}:
            raise ValueError('Invalid reversible AI research text edit: '+name)
        offset, replacement = edit['old_offset'], edit['replacement']
        if (type(offset) is not int or offset < old_end or type(replacement) is not int
                or not 0 <= replacement < len(pool)):
            raise ValueError('Overlapping or invalid AI research text edit: '+name)
        pair = pool[replacement]
        if (not isinstance(pair, dict) or set(pair) != {'old', 'new'}
                or not all(isinstance(pair.get(key), str) for key in ('old', 'new'))
                or pair['old'] == pair['new']):
            raise ValueError('Invalid AI research text replacement pool')
        before, after = pair['old'].encode('utf-8'), pair['new'].encode('utf-8')
        position = offset+delta
        if position < cursor or current[position:position+len(after)] != after:
            raise ValueError('AI research replacement differs at its exact offset: '+name)
        chunks.extend((current[cursor:position], before))
        cursor, old_end = position+len(after), offset+len(before)
        delta += len(after)-len(before)
    rebuilt = b''.join((*chunks, current[cursor:]))
    if hashlib.sha256(rebuilt).hexdigest() != old_sha or len(rebuilt) != old_size:
        raise ValueError('AI research predecessor cannot be reconstructed exactly: '+name)
    return rebuilt


def ai_research_predecessor_binding(root: Path, name: str) -> dict:
    content = ai_research_predecessor_bytes(root, name)
    return {'path': name, 'sha256': hashlib.sha256(content).hexdigest(), 'bytes': len(content)}


def label_predecessor_bytes(root: Path, name: str) -> bytes:
    """Reconstruct pre-label bytes with bounded, deduplicated text edits.

    Existing historical contracts consume these bytes; final website checks
    still read the actual files. No complete predecessor page is stored.
    """
    current = ai_research_predecessor_bytes(root, name)
    if not (root/PRESENTATION_V11_PATH).exists():
        return current
    data = read_json(project_file(root, PRESENTATION_V11_PATH))
    if not isinstance(data, dict):
        raise ValueError('Public-label presentation must be a JSON object')
    files, pool = data.get('reversible_text_files'), data.get('reverse_text_patch_pool')
    if not isinstance(files, list) or not isinstance(pool, list):
        raise ValueError('Public labels require their exact reversible text patch records')
    matches = [row for row in files if isinstance(row, dict) and row.get('path') == name]
    if not matches:
        return current
    if len(matches) != 1:
        raise ValueError('Duplicate public-label predecessor record: '+name)
    record = matches[0]
    if (hashlib.sha256(current).hexdigest() != record.get('new_sha256')
            or len(current) != record.get('new_bytes')):
        raise ValueError('Current file differs from its exact public-label patch: '+name)
    edits = record.get('edits')
    if not isinstance(edits, list) or not edits:
        raise ValueError('Public-label changes require nonempty text edits: '+name)
    chunks, cursor, old_end, delta = [], 0, 0, 0
    for edit in edits:
        if not isinstance(edit, dict) or set(edit) != {'old_offset', 'replacement'}:
            raise ValueError('Invalid reversible public-label text edit: '+name)
        offset, replacement = edit['old_offset'], edit['replacement']
        if (type(offset) is not int or offset < old_end or type(replacement) is not int
                or not 0 <= replacement < len(pool)):
            raise ValueError('Overlapping or invalid public-label text edit: '+name)
        pair = pool[replacement]
        if (not isinstance(pair, dict) or set(pair) != {'old', 'new'}
                or not all(isinstance(pair.get(key), str) for key in ('old', 'new'))
                or pair['old'] == pair['new']):
            raise ValueError('Invalid public-label text replacement pool')
        before, after = pair['old'].encode('utf-8'), pair['new'].encode('utf-8')
        position = offset+delta
        if position < cursor or current[position:position+len(after)] != after:
            raise ValueError('Public-label replacement differs at its exact offset: '+name)
        chunks.extend((current[cursor:position], before))
        cursor, old_end = position+len(after), offset+len(before)
        delta += len(after)-len(before)
    rebuilt = b''.join((*chunks, current[cursor:]))
    if (hashlib.sha256(rebuilt).hexdigest() != record.get('old_sha256')
            or len(rebuilt) != record.get('old_bytes')):
        raise ValueError('Public-label predecessor cannot be reconstructed exactly: '+name)
    return rebuilt


def label_predecessor_binding(root: Path, name: str) -> dict:
    content = label_predecessor_bytes(root, name)
    return {'path': name, 'sha256': hashlib.sha256(content).hexdigest(), 'bytes': len(content)}


def historical_website_member(root: Path, name: str) -> Path:
    """Read a prior HTML promise from its fixed snapshot during a successor."""
    prefix = PUBLIC_PRESENTATION_SNAPSHOT+'/site/' if (
        (root/PRESENTATION_V8_PATH).exists() and name.endswith('.html')) else 'site/'
    return project_file(root, prefix+name)


def historical_public_readme_binding(root: Path) -> dict:
    declaration = project_file(root, PRESENTATION_V6_PATH)
    if digest(declaration) != PRESENTATION_V6_SHA256:
        raise ValueError('The historical Chen reagent presentation v6 is immutable')
    documents = read_json(declaration).get('editorial_documents')
    matches = [row for row in documents if row.get('path') == 'README.md'] if isinstance(documents, list) else []
    if len(matches) != 1:
        raise ValueError('The frozen v6 declaration must identify one README binding')
    expected = matches[0]
    name = PUBLIC_PRESENTATION_SNAPSHOT+'/README.md'
    snapshot = project_file(root, name)
    if digest(snapshot) != expected['sha256'] or snapshot.stat().st_size != expected['bytes']:
        raise ValueError('The previous public README snapshot differs from its fixed v6 bytes')
    return {'original_path': 'README.md', 'snapshot_path': name,
            'sha256': expected['sha256'], 'bytes': expected['bytes']}


def presentation_v6_document_bindings(root: Path) -> list[dict]:
    historical = historical_public_readme_binding(root) if (root/PRESENTATION_V8_PATH).exists() else None
    bindings = []
    for name in ('README.md', CHEN_REAGENT_CONTENT_PATH, CHEN_REAGENT_DOCUMENT):
        if name == 'README.md' and historical is not None:
            bindings.append({'path': name, 'sha256': historical['sha256'], 'bytes': historical['bytes']})
        else:
            bindings.append(label_predecessor_binding(root, name))
    return bindings


def current_publication(root: Path) -> dict:
    """Resolve the explicit current edition, retaining the original v1 fallback.

    The registry contains paths, not its own digest or an eventual commit SHA.
    Its only supported successor is this authorized five-point diagnosis.
    """
    if not (root/CURRENT_PATH).exists():
        return {'public_progress': PROGRESS_PATH, 'revision_chain': [REVISION_PATH],
                'current_revision': REVISION_PATH, 'legacy': True}
    registry = read_json(project_file(root, CURRENT_PATH))
    if (registry.get('schema_version') != '1.0'
            or registry.get('registry_kind') != 'a01_public_progress_current'
            or registry.get('scientific_review_status') != 'review_required'
            or registry.get('release_eligible') is not False
            or registry.get('public_progress') != PROGRESS_V2_PATH
            or registry.get('current_revision') != REVISION_V2_PATH
            or registry.get('revision_chain') != [REVISION_PATH, REVISION_V2_PATH]):
        raise ValueError('Unsupported current A01 progress registry')
    return {**registry, 'legacy': False}


def current_progress_path(root: Path) -> str:
    return current_publication(root)['public_progress']


def presentation_document_bindings(root: Path) -> list[dict]:
    """Bind the three current editorial documents without changing originals."""
    return [{'path': name, 'sha256': digest(project_file(root, name)),
             'bytes': project_file(root, name).stat().st_size}
            for name in PRESENTATION_DOCUMENTS]


def presentation_v1_snapshot_bindings(root: Path) -> list[dict]:
    """Check old document bytes against the immutable v1 promises, not today.

    These three snapshots are exported from the fixed preceding commit. Their
    exact SHA256 and byte counts must be the values already committed in v1;
    neither current README edits nor this successor can refresh that promise.
    """
    path = project_file(root, PRESENTATION_PATH)
    if digest(path) != PRESENTATION_V1_SHA256:
        raise ValueError('The historical platform presentation v1 is immutable')
    old = read_json(path).get('editorial_documents')
    if (not isinstance(old, list) or len(old) != len(PRESENTATION_DOCUMENTS)
            or [item.get('path') for item in old] != list(PRESENTATION_DOCUMENTS)):
        raise ValueError('Unexpected historical v1 document binding set')
    snapshots = []
    for item in old:
        name = PRESENTATION_V1_DOCUMENT_SNAPSHOTS[item['path']]
        snapshot = project_file(root, name)
        if digest(snapshot) != item['sha256'] or snapshot.stat().st_size != item['bytes']:
            raise ValueError('Historical document snapshot differs from frozen v1 bytes: '+name)
        # Only README and the current platform roadmap are editable in v2.
        # The platform-purpose document remains an unchanged current document.
        if item['path'] == 'docs/PLATFORM_PURPOSE_zh-CN.md':
            current = label_predecessor_binding(root, item['path'])
            if current['sha256'] != item['sha256'] or current['bytes'] != item['bytes']:
                raise ValueError('The platform-purpose document is unchanged in this content edition')
        snapshots.append({'original_path': item['path'], 'snapshot_path': name,
                          'sha256': item['sha256'], 'bytes': item['bytes']})
    return snapshots


def presentation_v2_document_bindings(root: Path) -> list[dict]:
    historical_readme = (historical_readme_snapshot_binding(root)
                         if (root/PRESENTATION_V5_PATH).exists() else None)
    bindings = []
    for name in PRESENTATION_V2_DOCUMENTS:
        if name == 'README.md' and historical_readme is not None:
            bindings.append({'path': name, 'sha256': historical_readme['sha256'],
                             'bytes': historical_readme['bytes']})
        else:
            bindings.append(label_predecessor_binding(root, name))
    return bindings


def historical_readme_snapshot_binding(root: Path) -> dict:
    """Verify the v2 README snapshot against its already fixed promise."""
    declaration = project_file(root, PRESENTATION_V2_PATH)
    if digest(declaration) != PRESENTATION_V2_SHA256:
        raise ValueError('The historical content presentation v2 is immutable')
    documents = read_json(declaration).get('editorial_documents')
    matches = [row for row in documents if row.get('path') == 'README.md'] if isinstance(documents, list) else []
    if len(matches) != 1:
        raise ValueError('The frozen v2 declaration must identify one README binding')
    expected = matches[0]
    snapshot = project_file(root, PRESENTATION_V2_README_SNAPSHOT)
    if digest(snapshot) != expected['sha256'] or snapshot.stat().st_size != expected['bytes']:
        raise ValueError('The historical v2 README snapshot differs from its fixed bytes')
    return {'original_path': 'README.md', 'snapshot_path': PRESENTATION_V2_README_SNAPSHOT,
            'sha256': expected['sha256'], 'bytes': expected['bytes']}


def historical_v5_readme_snapshot_binding(root: Path) -> dict:
    """Verify the previous README against the immutable v5 declaration."""
    declaration = project_file(root, PRESENTATION_V5_PATH)
    if digest(declaration) != PRESENTATION_V5_SHA256:
        raise ValueError('The historical enrichment presentation v5 is immutable')
    documents = read_json(declaration).get('editorial_documents')
    matches = [row for row in documents if row.get('path') == 'README.md'] if isinstance(documents, list) else []
    if len(matches) != 1:
        raise ValueError('The frozen v5 declaration must identify one README binding')
    expected = matches[0]
    snapshot = project_file(root, PRESENTATION_V5_README_SNAPSHOT)
    if digest(snapshot) != expected['sha256'] or snapshot.stat().st_size != expected['bytes']:
        raise ValueError('The historical v5 README snapshot differs from its fixed bytes')
    return {'original_path': 'README.md', 'snapshot_path': PRESENTATION_V5_README_SNAPSHOT,
            'sha256': expected['sha256'], 'bytes': expected['bytes']}


def presentation_v5_document_bindings(root: Path) -> list[dict]:
    historical_readme = (historical_v5_readme_snapshot_binding(root)
                         if (root/PRESENTATION_V6_PATH).exists() else None)
    bindings = []
    for name in ('README.md', HERITAGE_ENRICHMENT_DOCUMENT):
        if name == 'README.md' and historical_readme is not None:
            bindings.append({'path': name, 'sha256': historical_readme['sha256'],
                             'bytes': historical_readme['bytes']})
        else:
            path = project_file(root, name)
            bindings.append({'path': name, 'sha256': digest(path), 'bytes': path.stat().st_size})
    return bindings


def protected_heritage_block_bindings(root: Path) -> list[dict]:
    """Check the ten existing historical blocks against their frozen bytes."""
    bindings = []
    for (name, marker), (expected_sha, expected_size) in FROZEN_HERITAGE_BLOCKS.items():
        page = historical_website_member(root, name).read_bytes().decode('utf-8')
        begin, end = '<!-- '+marker+'_BEGIN -->', '<!-- '+marker+'_END -->'
        if page.count(begin) != 1 or page.count(end) != 1 or page.index(end) < page.index(begin):
            raise ValueError('A frozen heritage block is missing or ambiguous: '+name+' '+marker)
        block = page[page.index(begin):page.index(end)+len(end)].encode('utf-8')
        if hashlib.sha256(block).hexdigest() != expected_sha or len(block) != expected_size:
            raise ValueError('A frozen heritage block changed: '+name+' '+marker)
        bindings.append({'path': name, 'marker': marker, 'sha256': expected_sha, 'bytes': expected_size})
    return bindings


def chen_reagent_achievement_binding(root: Path) -> dict:
    """Bind file identity and JSON shape, without certifying historical claims."""
    path = project_file(root, CHEN_REAGENT_CONTENT_PATH)
    value = read_json(path)
    if not isinstance(value, dict) or not value:
        raise ValueError('The Chen reagent historical record must be a nonempty JSON object')
    return {'path': CHEN_REAGENT_CONTENT_PATH, 'sha256': digest(path), 'bytes': path.stat().st_size,
            'content_classification': 'source_attributed_historical_achievement', 'achievement_line': 'A06',
            'validation_scope': 'File identity and JSON object shape only; source interpretation and historical priority require their separate evidence review'}


def heritage_content_binding(root: Path, content_path: str = HERITAGE_CONTENT_PATH) -> dict:
    """Bind the small historical inventory shape; do not certify its claims."""
    path = project_file(root, content_path)
    data = read_json(path)
    sources, lines = data.get('sources'), data.get('lines')
    if not isinstance(sources, list) or not sources or not all(isinstance(row, dict) for row in sources):
        raise ValueError('Heritage inventory requires its separate supplemental sources list')
    ids = [row.get('source_id', row.get('id')) for row in sources]
    if (not all(isinstance(value, str) and re.fullmatch(r'HERITAGE-S[0-9]{2,}', value) for value in ids)
            or len(ids) != len(set(ids))):
        raise ValueError('Supplemental heritage sources require unique HERITAGE-S identities')
    original_ids = {row['id'] for row in read_json(root/'site/data/public-sources.json')['sources']}
    if set(ids) & original_ids:
        raise ValueError('Supplemental heritage sources cannot replace original source identities')
    if not isinstance(lines, list) or not all(isinstance(row, dict) for row in lines):
        raise ValueError('Heritage inventory requires its nine line records')
    line_ids = [row.get('line_id') for row in lines]
    if len(line_ids) != 9 or set(line_ids) != {'A'+str(n).zfill(2) for n in range(1, 10)}:
        raise ValueError('Heritage inventory must retain exactly the stable A01-to-A09 identities')
    if (not isinstance(data.get('biography'), (list, dict))
            or not isinstance(data.get('stories'), list)
            or not isinstance(data.get('source_gaps'), list)):
        raise ValueError('Heritage inventory requires biography, stories and source_gaps records')
    return {'path': content_path, 'sha256': digest(path), 'bytes': path.stat().st_size,
        'content_classification': 'historical_heritage_materials',
        'supplemental_source_namespace': 'HERITAGE-S', 'supplemental_source_ids': ids,
        'stable_line_ids': line_ids,
        'validation_scope': 'File identity, namespace and basic inventory structure only; historical claims and citation quality require their separate review'}


def presentation_protected_bindings(root: Path, entries: dict) -> dict:
    """Read-only protection checks for this one presentation-only overlay."""
    protected = {}
    for name in ('data/public-sources.json', 'data/achievement-lines.json', 'pftb/index.html'):
        path = historical_website_member(root, name)
        expected = entries[name]
        if digest(path) != expected['sha256'] or path.stat().st_size != expected['bytes']:
            raise ValueError('Presentation must retain the original protected website bytes: '+name)
        protected[name] = {'sha256': expected['sha256'], 'bytes': expected['bytes']}
    source_ids = [row['id'] for row in read_json(root/'site/data/public-sources.json')['sources']]
    line_ids = [row['id'] for row in read_json(root/'site/data/achievement-lines.json')['lines']]
    if len(source_ids) != 51 or len(set(source_ids)) != 51 or any(not value for value in source_ids):
        raise ValueError('Presentation must preserve the 51 stable source identities')
    if len(line_ids) != 9 or set(line_ids) != {'A'+str(n).zfill(2) for n in range(1, 10)}:
        raise ValueError('Presentation must preserve the nine achievement identities')
    routes = sorted(name for name in entries if name.endswith('.html'))
    successor_routes = {AI_RESEARCH_ROUTE} if (root/PRESENTATION_V12_PATH).is_file() else set()
    actual_routes = sorted(path.relative_to(root/'site').as_posix()
                           for path in (root/'site').rglob('*.html')
                           if path.relative_to(root/'site').as_posix() not in successor_routes)
    if len(routes) != 15 or actual_routes != routes:
        raise ValueError('Presentation must preserve exactly the original 15 HTML routes')
    historical = []
    for name, expected in HISTORICAL_DOCUMENTS.items():
        path = project_file(root, name)
        if digest(path) != expected['sha256'] or path.stat().st_size != expected['bytes']:
            raise ValueError('Historical implementation document bytes changed: '+name)
        historical.append({'path': name, **expected})
    return {'website_members': protected, 'source_ids': source_ids,
            'achievement_line_ids': line_ids, 'html_routes': routes,
            'historical_documents': historical}


def apply_presentation_v1(root: Path, entries: dict, *, chain: list,
                          use_document_snapshots=False) -> tuple[dict, dict | None]:
    """Apply the independent editorial layer after the frozen scientific chain.

    The overlay changes three existing HTML presentations only. It does not
    select, regenerate or upgrade an A01 scientific record.
    """
    if not (root/PRESENTATION_PATH).exists():
        return entries, None
    if chain != [REVISION_PATH, REVISION_V2_PATH]:
        raise ValueError('Platform presentation requires the frozen v1-to-v2 scientific chain')
    path = project_file(root, PRESENTATION_PATH)
    if digest(path) != PRESENTATION_V1_SHA256:
        raise ValueError('The historical platform presentation v1 is immutable')
    data = read_json(path)
    if (data.get('schema_version') != '1.0'
            or data.get('presentation_id') != PRESENTATION_ID
            or data.get('publication_kind') != 'platform_editorial_presentation'
            or data.get('scientific_review_status') != 'review_required'
            or data.get('release_eligible') is not False
            or data.get('scientific_data_unchanged') is not True
            or data.get('original_baseline_sha256') != BASELINE_SHA256
            or data.get('original_archive_sha256') != ARCHIVE_SHA256
            or data.get('previous_presentation_commit') != PRESENTATION_PREVIOUS_COMMIT):
        raise ValueError('Unsupported platform presentation contract')
    bindings = [('scientific_revision', REVISION_V2_PATH, REVISION_V2_SHA256),
                ('public_progress', PROGRESS_V2_PATH, PROGRESS_V2_SHA256),
                ('current_registry', CURRENT_PATH, CURRENT_SHA256)]
    for field, name, expected in bindings:
        if data.get(field) != {'path': name, 'sha256': expected} or digest(project_file(root, name)) != expected:
            raise ValueError('Platform presentation must retain the frozen scientific binding: '+field)
    if use_document_snapshots:
        document_bindings = [{'path': row['original_path'], 'sha256': row['sha256'], 'bytes': row['bytes']}
                             for row in presentation_v1_snapshot_bindings(root)]
    else:
        document_bindings = presentation_document_bindings(root)
    if data.get('editorial_documents') != document_bindings:
        raise ValueError('Current platform documents differ from the presentation binding')
    if data.get('protected') != presentation_protected_bindings(root, entries):
        raise ValueError('Protected platform identities differ from the presentation binding')
    changes = data.get('changes')
    if not isinstance(changes, list) or len(changes) != 3:
        raise ValueError('Presentation must explicitly bind the three authorized HTML paths')
    updated, seen = {name: dict(value) for name, value in entries.items()}, set()
    for item in changes:
        name = item.get('path')
        if name not in ALLOWED_CHANGES or name in seen:
            raise ValueError('Unauthorized or duplicate presentation path: '+str(name))
        seen.add(name)
        old = entries[name]
        if item.get('old_sha256') != old['sha256'] or item.get('old_bytes') != old['bytes']:
            raise ValueError('Presentation predecessor bytes differ: '+name)
        value, size = item.get('new_sha256'), item.get('new_bytes')
        if (not isinstance(value, str) or not SHA.fullmatch(value) or value == old['sha256']
                or not isinstance(size, int) or isinstance(size, bool) or size <= 0
                or not isinstance(item.get('reason'), str) or not item['reason'].strip()):
            raise ValueError('Incomplete platform presentation change: '+name)
        updated[name] = {**old, 'sha256': value, 'bytes': size,
                         'presentation_id': PRESENTATION_ID}
    return updated, {'path': PRESENTATION_PATH, 'sha256': digest(path),
        'presentation_id': PRESENTATION_ID, 'publication_kind': 'platform_editorial_presentation',
        'changed_paths': sorted(seen), 'previous_presentation_commit': PRESENTATION_PREVIOUS_COMMIT,
        'scientific_data_unchanged': True, 'scientific_review_status': 'review_required',
        'release_eligible': False}


def apply_presentation_overlay(root: Path, entries: dict, *, chain: list) -> tuple[dict, dict | None]:
    """Apply v1, then this bounded historical-content successor if present."""
    if (root/PRESENTATION_V12_PATH).exists() and not (root/PRESENTATION_V11_PATH).exists():
        raise ValueError('AI research presentation requires its fixed v11 predecessor')
    if (root/PRESENTATION_V11_PATH).exists() and not (root/PRESENTATION_V10_PATH).exists():
        raise ValueError('Public line labels require their fixed v10 predecessor')
    if (root/PRESENTATION_V10_PATH).exists() and not (root/PRESENTATION_V9_PATH).exists():
        raise ValueError('A01 first-report presentation requires its fixed v9 predecessor')
    if (root/PRESENTATION_V9_PATH).exists() and not (root/PRESENTATION_V8_PATH).exists():
        raise ValueError('A01 historical presentation requires its fixed v8 predecessor')
    if (root/PRESENTATION_V8_PATH).exists() and not (root/PRESENTATION_V7_PATH).exists():
        raise ValueError('Public academic presentation v8 requires its fixed v7 predecessor')
    if (root/PRESENTATION_V7_PATH).exists() and not (root/PRESENTATION_V6_PATH).exists():
        raise ValueError('CAS source supplement v7 requires its fixed v6 predecessor')
    if (root/PRESENTATION_V6_PATH).exists() and not (root/PRESENTATION_V5_PATH).exists():
        raise ValueError('Chen reagent presentation v6 requires its fixed v5 predecessor')
    if (root/PRESENTATION_V5_PATH).exists() and not (root/PRESENTATION_V4_PATH).exists():
        raise ValueError('Historical enrichment v5 requires its fixed v4 predecessor')
    successor_present = (root/PRESENTATION_V2_PATH).exists()
    if (root/PRESENTATION_V3_PATH).exists() and not successor_present:
        raise ValueError('Numbering correction v3 requires the historical content v2 predecessor')
    previous, v1 = apply_presentation_v1(root, entries, chain=chain,
        use_document_snapshots=successor_present)
    if not successor_present:
        return previous, v1
    if v1 is None:
        raise ValueError('Historical content presentation v2 requires its immutable v1 predecessor')
    path = project_file(root, PRESENTATION_V2_PATH)
    data = read_json(path)
    if (data.get('schema_version') != '2.0'
            or data.get('presentation_id') != PRESENTATION_V2_ID
            or data.get('publication_kind') != 'platform_historical_content'
            or data.get('scientific_review_status') != 'review_required'
            or data.get('release_eligible') is not False
            or data.get('scientific_data_unchanged') is not True
            or data.get('original_baseline_sha256') != BASELINE_SHA256
            or data.get('original_archive_sha256') != ARCHIVE_SHA256
            or data.get('previous_presentation_commit') != PRESENTATION_V2_PREVIOUS_COMMIT
            or data.get('previous_presentation') != {'path': PRESENTATION_PATH, 'sha256': PRESENTATION_V1_SHA256}):
        raise ValueError('Unsupported historical content presentation v2 contract')
    for field, name, expected in [('scientific_revision', REVISION_V2_PATH, REVISION_V2_SHA256),
            ('public_progress', PROGRESS_V2_PATH, PROGRESS_V2_SHA256),
            ('current_registry', CURRENT_PATH, CURRENT_SHA256)]:
        if data.get(field) != {'path': name, 'sha256': expected} or digest(project_file(root, name)) != expected:
            raise ValueError('Historical content overlay changed the frozen scientific binding: '+field)
    if data.get('historical_editorial_documents') != presentation_v1_snapshot_bindings(root):
        raise ValueError('Historical v1 document snapshot binding changed')
    if data.get('editorial_documents') != presentation_v2_document_bindings(root):
        raise ValueError('Current heritage documents differ from the v2 declaration')
    if data.get('historical_content') != heritage_content_binding(root):
        raise ValueError('Supplemental historical content differs from the v2 declaration')
    if data.get('protected') != presentation_protected_bindings(root, previous):
        raise ValueError('Protected original platform identities changed')
    if data.get('ai_research') != {'role': 'separate_supporting_pilot', 'new_quantum_calls': 0,
                                  'new_model_API_calls': 0, 'scientific_data_unchanged': True}:
        raise ValueError('Historical content cannot claim new AI scientific calculations')
    changes = data.get('changes')
    if not isinstance(changes, list) or not 1 <= len(changes) <= len(ALLOWED_CHANGES):
        raise ValueError('Historical content v2 must enumerate its one-to-three existing HTML changes')
    updated, seen = {name: dict(value) for name, value in previous.items()}, set()
    for item in changes:
        name = item.get('path')
        if name not in ALLOWED_CHANGES or name in seen:
            raise ValueError('Unauthorized or duplicate historical content HTML path: '+str(name))
        seen.add(name)
        old = previous[name]
        if item.get('old_sha256') != old['sha256'] or item.get('old_bytes') != old['bytes']:
            raise ValueError('Historical content must bind the actual v1 HTML predecessor: '+name)
        value, size = item.get('new_sha256'), item.get('new_bytes')
        if (not isinstance(value, str) or not SHA.fullmatch(value) or value == old['sha256']
                or not isinstance(size, int) or isinstance(size, bool) or size <= 0
                or not isinstance(item.get('reason'), str) or not item['reason'].strip()):
            raise ValueError('Incomplete historical content HTML change: '+name)
        updated[name] = {**old, 'sha256': value, 'bytes': size, 'presentation_id': PRESENTATION_V2_ID}
    report = {'path': PRESENTATION_V2_PATH, 'sha256': digest(path),
        'presentation_id': PRESENTATION_V2_ID, 'publication_kind': 'platform_historical_content',
        'changed_paths': sorted(seen), 'previous_presentation_commit': PRESENTATION_V2_PREVIOUS_COMMIT,
        'scientific_data_unchanged': True, 'scientific_review_status': 'review_required',
        'release_eligible': False}
    return apply_numbering_correction(root, updated, {**report, 'presentation_chain': [v1, report]})


def inspect_line_numbering(path: Path, *, source: str | None = None,
                           label_location: str = 'auto') -> dict:
    """Check current heading IDs or explicitly reconstructed legacy side IDs.

    v11 puts the public ID/name in each card's main heading and reserves its
    side column for chronology. Historical v3-v10 replay explicitly supplies
    the reconstructed source and keeps its original side-label rule.
    """
    expected = {'record-fluorinated-ionic-liquids': 'line-a08',
                'record-publication-index': 'line-a09'}
    line_ids = ['line-a'+str(n).zfill(2) for n in range(1, 10)]
    expected_numbers = ['A'+str(n).zfill(2) for n in range(1, 10)]
    if label_location not in {'auto', 'side', 'heading'}:
        raise ValueError('Unknown primary achievement label location')
    if (label_location == 'auto' and source is None
            and any((parent/PRESENTATION_V11_PATH).is_file() for parent in path.resolve().parents)):
        label_location = 'heading'

    class NumberingParser(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.stack, self.cards, self.labels, self.records = [], [], [], []
            self.active_labels = []

        def handle_starttag(self, tag, attrs):
            values = dict(attrs)
            ident, classes = values.get('id'), values.get('class', '').split()
            ancestor_ids = [row[1] for row in self.stack]
            if ident in expected:
                self.records.append((ident, expected[ident] in ancestor_ids))
            if ('achievement-detail' in ancestor_ids and tag == 'article' and 'case' in classes):
                self.cards.append(ident)
            owners = [row for row in self.stack if row[1] in line_ids and 'case' in row[2]]
            owner = owners[-1][1] if owners else None
            kind = ('side' if 'case-side' in classes else 'heading' if (
                tag == 'h3' and self.stack and 'case-main' in self.stack[-1][2]) else None)
            if 'achievement-detail' in ancestor_ids and owner is not None and kind is not None:
                self.active_labels.append({'depth': len(self.stack), 'owner': owner,
                                           'kind': kind, 'text': ''})
            if tag not in {'area', 'base', 'br', 'col', 'embed', 'hr', 'img',
                           'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}:
                self.stack.append((tag, ident, classes))

        def handle_data(self, value):
            for label in self.active_labels:
                label['text'] += value

        def handle_endtag(self, tag):
            for position in range(len(self.stack)-1, -1, -1):
                if self.stack[position][0] == tag:
                    closed = [label for label in self.active_labels if label['depth'] >= position]
                    self.labels.extend(closed)
                    self.active_labels = [label for label in self.active_labels if label['depth'] < position]
                    del self.stack[position:]
                    break

    page = NumberingParser()
    page.feed(path.read_text('utf-8') if source is None else source)
    page.close()
    if page.cards != line_ids:
        raise ValueError('The nine primary card IDs must be line-a01 through line-a09 once, in order')
    groups = {kind: [row for row in page.labels if row['kind'] == kind] for kind in ('side', 'heading')}
    def numbers(kind):
        return [match.group(1) if (match := re.match(r'(A0[1-9])\b', row['text'].strip())) else None
                for row in groups[kind]]
    if label_location == 'auto':
        label_location = 'heading' if numbers('heading') == expected_numbers else 'side'
    labels, values = groups[label_location], numbers(label_location)
    if [row['owner'] for row in labels] != line_ids or values != expected_numbers:
        raise ValueError('The primary achievement cards must be numbered A01 through A09 once, in order')
    if label_location == 'heading' and ([row['owner'] for row in groups['side']] != line_ids or any(
            re.search(r'(?<![A-Za-z0-9_-])A0[1-9](?![A-Za-z0-9_-])', row['text'])
            for row in groups['side'])):
        raise ValueError('Current primary card side columns must contain chronology without duplicate achievement IDs')
    if sorted(page.records) != sorted((name, True) for name in expected):
        raise ValueError('Each supplemental archive must appear once within its own achievement line')
    return {'primary_line_labels': values, 'label_location': label_location,
            'supplemental_archives_nested': True}


def apply_numbering_correction(root: Path, entries: dict, previous_report: dict) -> tuple[dict, dict]:
    """Apply only the two-page hierarchy correction without refreshing v2."""
    if not (root/PRESENTATION_V3_PATH).exists():
        if (root/PRESENTATION_V4_PATH).exists():
            raise ValueError('Navigation revision v4 requires its fixed v3 predecessor')
        return entries, previous_report
    if digest(project_file(root, PRESENTATION_V2_PATH)) != PRESENTATION_V2_SHA256:
        raise ValueError('The preceding historical presentation v2 is immutable')
    path = project_file(root, PRESENTATION_V3_PATH)
    data = read_json(path)
    if (data.get('schema_version') != '3.0'
            or data.get('presentation_id') != PRESENTATION_V3_ID
            or data.get('publication_kind') != 'platform_navigation_correction'
            or data.get('scientific_review_status') != 'review_required'
            or data.get('release_eligible') is not False
            or data.get('scientific_data_unchanged') is not True
            or data.get('new_quantum_calls') != 0
            or data.get('previous_presentation_commit') != PRESENTATION_V3_PREVIOUS_COMMIT
            or data.get('previous_presentation') != {'path': PRESENTATION_V2_PATH,
                                                    'sha256': PRESENTATION_V2_SHA256}):
        raise ValueError('Unsupported two-page numbering correction contract')
    changes = data.get('changes')
    if not isinstance(changes, list) or len(changes) != len(NUMBERING_PATHS):
        raise ValueError('The numbering correction must enumerate its two existing HTML pages')
    updated, seen = {name: dict(value) for name, value in entries.items()}, set()
    for item in changes:
        name = item.get('path')
        if name not in NUMBERING_PATHS or name in seen:
            raise ValueError('Unauthorized or duplicate numbering correction path: '+str(name))
        seen.add(name)
        old = entries[name]
        if item.get('old_sha256') != old['sha256'] or item.get('old_bytes') != old['bytes']:
            raise ValueError('Numbering correction must bind the actual v2 predecessor: '+name)
        value, size = item.get('new_sha256'), item.get('new_bytes')
        if (not isinstance(value, str) or not SHA.fullmatch(value) or value == old['sha256']
                or not isinstance(size, int) or isinstance(size, bool) or size <= 0
                or not isinstance(item.get('reason'), str) or not item['reason'].strip()):
            raise ValueError('Incomplete numbering correction: '+name)
        inspect_line_numbering(project_file(root, 'site/'+name),
            source=label_predecessor_bytes(root, 'site/'+name).decode('utf-8'), label_location='side')
        updated[name] = {**old, 'sha256': value, 'bytes': size, 'presentation_id': PRESENTATION_V3_ID}
    report = {'path': PRESENTATION_V3_PATH, 'sha256': digest(path),
        'presentation_id': PRESENTATION_V3_ID, 'publication_kind': 'platform_navigation_correction',
        'changed_paths': sorted(seen), 'previous_presentation_commit': PRESENTATION_V3_PREVIOUS_COMMIT,
        'scientific_data_unchanged': True, 'scientific_review_status': 'review_required',
        'release_eligible': False}
    return apply_navigation_revision(root, updated,
        {**report, 'presentation_chain': [*previous_report['presentation_chain'], report]})


def apply_navigation_revision(root: Path, entries: dict, previous_report: dict) -> tuple[dict, dict]:
    """Apply a bounded editorial revision; preserve the original PFtB and data."""
    if not (root/PRESENTATION_V4_PATH).exists():
        if (root/PRESENTATION_V5_PATH).exists():
            raise ValueError('Historical enrichment v5 requires its fixed v4 predecessor')
        return entries, previous_report
    if digest(project_file(root, PRESENTATION_V3_PATH)) != PRESENTATION_V3_SHA256:
        raise ValueError('The preceding navigation presentation v3 is immutable')
    path = project_file(root, PRESENTATION_V4_PATH)
    data = read_json(path)
    if (data.get('schema_version') != '4.0'
            or data.get('presentation_id') != PRESENTATION_V4_ID
            or data.get('publication_kind') != 'platform_navigation_consistency'
            or data.get('scientific_review_status') != 'review_required'
            or data.get('release_eligible') is not False
            or data.get('scientific_data_unchanged') is not True
            or data.get('new_quantum_calls') != 0
            or data.get('new_model_API_calls') != 0
            or data.get('original_baseline_sha256') != BASELINE_SHA256
            or data.get('original_archive_sha256') != ARCHIVE_SHA256
            or data.get('previous_presentation_commit') != PRESENTATION_V4_PREVIOUS_COMMIT
            or data.get('previous_presentation') != {'path': PRESENTATION_V3_PATH,
                                                    'sha256': PRESENTATION_V3_SHA256}):
        raise ValueError('Unsupported editorial navigation revision v4 contract')
    allowed = {name for name in entries if name.endswith('.html') and name != 'pftb/index.html'}
    if len(allowed) != 14 or data.get('allowed_html_paths') != sorted(allowed):
        raise ValueError('Navigation revision must retain the original fourteen editable HTML routes')
    protected = {name: {'sha256': entries[name]['sha256'], 'bytes': entries[name]['bytes']}
                 for name in ('pftb/index.html', 'data/public-sources.json', 'data/achievement-lines.json')}
    if data.get('protected_website_members') != protected:
        raise ValueError('Navigation revision changed the protected PFtB or source-data binding')
    # The preceding v1-v3 checks already bind the research JSON, heritage data,
    # original source IDs and routes. The displayed technical block stays exact.
    from render_a01_progress import BEGIN, END, render_block
    topic = label_predecessor_bytes(root, 'site/'+TOPIC_PATH).decode('utf-8')
    if (topic.count(BEGIN) != 1 or topic.count(END) != 1
            or topic[topic.index(BEGIN):topic.index(END)+len(END)]
            != render_block(read_json(root/PROGRESS_V2_PATH), PROGRESS_V2_SHA256)):
        raise ValueError('Navigation revision must retain the exact A01 scientific progress block')
    changes = data.get('changes')
    if not isinstance(changes, list) or not 1 <= len(changes) <= len(allowed):
        raise ValueError('Navigation revision must enumerate its edited existing HTML pages')
    updated, seen = {name: dict(value) for name, value in entries.items()}, set()
    for item in changes:
        name = item.get('path')
        if name not in allowed or name in seen:
            raise ValueError('Unauthorized or duplicate navigation revision path: '+str(name))
        seen.add(name)
        old = entries[name]
        if item.get('old_sha256') != old['sha256'] or item.get('old_bytes') != old['bytes']:
            raise ValueError('Navigation revision must bind its actual v3 predecessor: '+name)
        value, size = item.get('new_sha256'), item.get('new_bytes')
        if (not isinstance(value, str) or not SHA.fullmatch(value) or value == old['sha256']
                or not isinstance(size, int) or isinstance(size, bool) or size <= 0
                or not isinstance(item.get('reason'), str) or not item['reason'].strip()):
            raise ValueError('Incomplete navigation revision change: '+name)
        updated[name] = {**old, 'sha256': value, 'bytes': size, 'presentation_id': PRESENTATION_V4_ID}
    report = {'path': PRESENTATION_V4_PATH, 'sha256': digest(path),
        'presentation_id': PRESENTATION_V4_ID, 'publication_kind': 'platform_navigation_consistency',
        'changed_paths': sorted(seen), 'previous_presentation_commit': PRESENTATION_V4_PREVIOUS_COMMIT,
        'scientific_data_unchanged': True, 'scientific_review_status': 'review_required',
        'release_eligible': False}
    return apply_heritage_enrichment(root, updated,
        {**report, 'presentation_chain': [*previous_report['presentation_chain'], report]})


def apply_heritage_enrichment(root: Path, entries: dict, previous_report: dict) -> tuple[dict, dict]:
    """Bind new sourced history without replacing the preceding collection."""
    if not (root/PRESENTATION_V5_PATH).exists():
        return entries, previous_report
    if digest(project_file(root, PRESENTATION_V4_PATH)) != PRESENTATION_V4_SHA256:
        raise ValueError('The preceding historical navigation presentation v4 is immutable')
    path = project_file(root, PRESENTATION_V5_PATH)
    data = read_json(path)
    if (data.get('schema_version') != '5.0'
            or data.get('presentation_id') != PRESENTATION_V5_ID
            or data.get('publication_kind') != 'platform_historical_enrichment'
            or data.get('scientific_review_status') != 'review_required'
            or data.get('release_eligible') is not False
            or data.get('scientific_data_unchanged') is not True
            or type(data.get('new_quantum_calls')) is not int or data['new_quantum_calls'] != 0
            or type(data.get('new_model_API_calls')) is not int or data['new_model_API_calls'] != 0
            or data.get('M0_resumed') is not False
            or data.get('original_baseline_sha256') != BASELINE_SHA256
            or data.get('original_archive_sha256') != ARCHIVE_SHA256
            or data.get('previous_presentation_commit') != PRESENTATION_V5_PREVIOUS_COMMIT
            or data.get('previous_presentation') != {'path': PRESENTATION_V4_PATH,
                                                    'sha256': PRESENTATION_V4_SHA256}):
        raise ValueError('Unsupported historical enrichment v5 contract')
    allowed = PRESENTATION_V5_ALLOWED_PATHS
    if not allowed <= entries.keys() or data.get('allowed_html_paths') != sorted(allowed):
        raise ValueError('Historical enrichment must stay within its seven existing HTML routes')
    # All website members outside this seven-page edit remain exact, including
    # the complete PFtB page, source JSON, directory and A01 scientific page.
    protected = {name: {'sha256': value['sha256'], 'bytes': value['bytes']}
                 for name, value in entries.items() if name not in allowed}
    if data.get('protected_website_members') != protected:
        raise ValueError('Historical enrichment changed a protected website binding')
    for name, expected in protected.items():
        current = historical_website_member(root, name)
        if digest(current) != expected['sha256'] or current.stat().st_size != expected['bytes']:
            raise ValueError('Historical enrichment changed protected website bytes: '+name)
    # v2's existing document and content checks continue to verify the first
    # collection and its report; v5 adds separate successor files only.
    if data.get('previous_historical_content') != heritage_content_binding(root):
        raise ValueError('The preceding historical content collection must remain unchanged')
    if data.get('historical_content') != heritage_content_binding(root, HERITAGE_CONTENT_V2_PATH):
        raise ValueError('The new historical collection differs from its v5 binding')
    if data.get('historical_readme_snapshot') != historical_readme_snapshot_binding(root):
        raise ValueError('The historical README snapshot differs from its v5 binding')
    if data.get('editorial_documents') != presentation_v5_document_bindings(root):
        raise ValueError('The historical enrichment report differs from its v5 binding')
    changes = data.get('changes')
    if not isinstance(changes, list) or not 1 <= len(changes) <= len(allowed):
        raise ValueError('Historical enrichment must enumerate its edited existing HTML pages')
    updated, seen = {name: dict(value) for name, value in entries.items()}, set()
    for item in changes:
        name = item.get('path')
        if name not in allowed or name in seen:
            raise ValueError('Unauthorized or duplicate historical enrichment path: '+str(name))
        seen.add(name)
        old = entries[name]
        if item.get('old_sha256') != old['sha256'] or item.get('old_bytes') != old['bytes']:
            raise ValueError('Historical enrichment must bind its actual v4 predecessor: '+name)
        value, size = item.get('new_sha256'), item.get('new_bytes')
        if (not isinstance(value, str) or not SHA.fullmatch(value) or value == old['sha256']
                or not isinstance(size, int) or isinstance(size, bool) or size <= 0
                or not isinstance(item.get('reason'), str) or not item['reason'].strip()):
            raise ValueError('Incomplete historical enrichment change: '+name)
        updated[name] = {**old, 'sha256': value, 'bytes': size, 'presentation_id': PRESENTATION_V5_ID}
    report = {'path': PRESENTATION_V5_PATH, 'sha256': digest(path),
        'presentation_id': PRESENTATION_V5_ID, 'publication_kind': 'platform_historical_enrichment',
        'changed_paths': sorted(seen), 'previous_presentation_commit': PRESENTATION_V5_PREVIOUS_COMMIT,
        'historical_content_path': HERITAGE_CONTENT_V2_PATH,
        'scientific_data_unchanged': True, 'scientific_review_status': 'review_required',
        'release_eligible': False}
    return apply_chen_reagent_achievement(root, updated,
        {**report, 'presentation_chain': [*previous_report['presentation_chain'], report]})


def apply_chen_reagent_achievement(root: Path, entries: dict, previous_report: dict) -> tuple[dict, dict]:
    """Highlight a sourced historical achievement within three existing pages."""
    if not (root/PRESENTATION_V6_PATH).exists():
        return entries, previous_report
    if digest(project_file(root, PRESENTATION_V5_PATH)) != PRESENTATION_V5_SHA256:
        raise ValueError('The preceding historical enrichment presentation v5 is immutable')
    path = project_file(root, PRESENTATION_V6_PATH)
    data = read_json(path)
    if (data.get('schema_version') != '6.0'
            or data.get('presentation_id') != PRESENTATION_V6_ID
            or data.get('publication_kind') != 'platform_historical_achievement'
            or data.get('scientific_review_status') != 'review_required'
            or data.get('scientific_review_scope') != 'unchanged_platform_research_only'
            or data.get('release_eligible') is not False
            or data.get('historical_achievement_independent_of_AI_review') is not True
            or data.get('scientific_data_unchanged') is not True
            or type(data.get('new_quantum_calls')) is not int or data['new_quantum_calls'] != 0
            or type(data.get('new_model_API_calls')) is not int or data['new_model_API_calls'] != 0
            or data.get('M0_resumed') is not False
            or data.get('original_baseline_sha256') != BASELINE_SHA256
            or data.get('original_archive_sha256') != ARCHIVE_SHA256
            or data.get('previous_presentation_commit') != PRESENTATION_V6_PREVIOUS_COMMIT
            or data.get('previous_presentation') != {'path': PRESENTATION_V5_PATH,
                                                    'sha256': PRESENTATION_V5_SHA256}):
        raise ValueError('Unsupported Chen reagent historical achievement presentation v6')
    allowed = PRESENTATION_V6_ALLOWED_PATHS
    if not allowed <= entries.keys() or data.get('allowed_html_paths') != sorted(allowed):
        raise ValueError('Chen reagent presentation must stay within its three existing HTML routes')
    protected = {name: {'sha256': value['sha256'], 'bytes': value['bytes']}
                 for name, value in entries.items() if name not in allowed}
    if data.get('protected_website_members') != protected:
        raise ValueError('Chen reagent presentation changed a protected website binding')
    for name, expected in protected.items():
        current = historical_website_member(root, name)
        if digest(current) != expected['sha256'] or current.stat().st_size != expected['bytes']:
            raise ValueError('Chen reagent presentation changed protected website bytes: '+name)
    if data.get('protected_heritage_blocks') != protected_heritage_block_bindings(root):
        raise ValueError('Chen reagent presentation changed a frozen heritage block binding')
    if data.get('historical_readme_snapshot') != historical_v5_readme_snapshot_binding(root):
        raise ValueError('The historical v5 README snapshot differs from its v6 binding')
    if data.get('historical_achievement_content') != chen_reagent_achievement_binding(root):
        raise ValueError('The Chen reagent historical record differs from its v6 binding')
    if data.get('editorial_documents') != presentation_v6_document_bindings(root):
        raise ValueError('The current Chen reagent editorial files differ from their v6 bindings')
    changes = data.get('changes')
    if not isinstance(changes, list) or not 1 <= len(changes) <= len(allowed):
        raise ValueError('Chen reagent presentation must enumerate its edited existing HTML pages')
    updated, seen = {name: dict(value) for name, value in entries.items()}, set()
    for item in changes:
        name = item.get('path')
        if name not in allowed or name in seen:
            raise ValueError('Unauthorized or duplicate Chen reagent achievement path: '+str(name))
        seen.add(name)
        old = entries[name]
        if item.get('old_sha256') != old['sha256'] or item.get('old_bytes') != old['bytes']:
            raise ValueError('Chen reagent presentation must bind its actual v5 predecessor: '+name)
        value, size = item.get('new_sha256'), item.get('new_bytes')
        if (not isinstance(value, str) or not SHA.fullmatch(value) or value == old['sha256']
                or not isinstance(size, int) or isinstance(size, bool) or size <= 0
                or not isinstance(item.get('reason'), str) or not item['reason'].strip()):
            raise ValueError('Incomplete Chen reagent historical achievement change: '+name)
        updated[name] = {**old, 'sha256': value, 'bytes': size, 'presentation_id': PRESENTATION_V6_ID}
    report = {'path': PRESENTATION_V6_PATH, 'sha256': digest(path),
        'presentation_id': PRESENTATION_V6_ID, 'publication_kind': 'platform_historical_achievement',
        'changed_paths': sorted(seen), 'previous_presentation_commit': PRESENTATION_V6_PREVIOUS_COMMIT,
        'historical_content_path': CHEN_REAGENT_CONTENT_PATH,
        'scientific_data_unchanged': True, 'scientific_review_status': 'review_required',
        'scientific_review_scope': 'unchanged_platform_research_only',
        'historical_achievement_independent_of_AI_review': True, 'release_eligible': False}
    return apply_chen_reagent_cas_source(root, updated,
        {**report, 'presentation_chain': [*previous_report['presentation_chain'], report]})


def chen_reagent_cas_source_binding(root: Path) -> dict:
    path = project_file(root, CHEN_REAGENT_CAS_SOURCE_PATH)
    value = read_json(path)
    if not isinstance(value, dict) or not value:
        raise ValueError('The CAS source supplement must be a nonempty JSON object')
    return {'path': CHEN_REAGENT_CAS_SOURCE_PATH, 'sha256': digest(path),
            'bytes': path.stat().st_size, 'source_id': 'CR-S03',
            'url': 'https://www.cas.cn/zt/rwzt/2024qm/202403/t20240328_5010119.shtml'}


def apply_chen_reagent_cas_source(root: Path, entries: dict, previous_report: dict) -> tuple[dict, dict]:
    """Add the requested institutional source; inherit all v6 protections."""
    if not (root/PRESENTATION_V7_PATH).exists():
        return entries, previous_report
    if digest(project_file(root, PRESENTATION_V6_PATH)) != PRESENTATION_V6_SHA256:
        raise ValueError('The preceding Chen reagent presentation v6 is immutable')
    path = project_file(root, PRESENTATION_V7_PATH)
    data = read_json(path)
    required = {'schema_version': '7.0', 'presentation_id': PRESENTATION_V7_ID,
        'publication_kind': 'platform_historical_source_supplement',
        'previous_presentation_commit': PRESENTATION_V7_PREVIOUS_COMMIT,
        'previous_presentation': {'path': PRESENTATION_V6_PATH, 'sha256': PRESENTATION_V6_SHA256},
        'original_baseline_sha256': BASELINE_SHA256, 'original_archive_sha256': ARCHIVE_SHA256,
        'allowed_html_paths': sorted(PRESENTATION_V6_ALLOWED_PATHS),
        'source_supplement': chen_reagent_cas_source_binding(root),
        'scientific_review_status': 'review_required',
        'scientific_review_scope': 'unchanged_platform_research_only',
        'release_eligible': False, 'scientific_data_unchanged': True,
        'historical_achievement_independent_of_AI_review': True, 'M0_resumed': False}
    if any(data.get(key) != value for key, value in required.items()) or any(
            data.get(key) is not required[key] for key in ('release_eligible',
                'scientific_data_unchanged', 'historical_achievement_independent_of_AI_review', 'M0_resumed')) or any(
            type(data.get(key)) is not int or data[key] != 0
            for key in ('new_quantum_calls', 'new_model_API_calls')):
        raise ValueError('Unsupported CAS historical source supplement v7')
    # The immutable v6 layer has already checked every other website member,
    # all ten heritage blocks, the old achievement packet, README and report.
    changes = data.get('changes')
    if not isinstance(changes, list) or not 1 <= len(changes) <= len(PRESENTATION_V6_ALLOWED_PATHS):
        raise ValueError('CAS source supplement must enumerate its existing HTML changes')
    updated, seen = {name: dict(value) for name, value in entries.items()}, set()
    for item in changes:
        name = item.get('path')
        if name not in PRESENTATION_V6_ALLOWED_PATHS or name in seen:
            raise ValueError('Unauthorized or duplicate CAS source supplement path: '+str(name))
        seen.add(name)
        old = entries[name]
        value, size = item.get('new_sha256'), item.get('new_bytes')
        if (item.get('old_sha256') != old['sha256'] or item.get('old_bytes') != old['bytes']
                or not isinstance(value, str) or not SHA.fullmatch(value) or value == old['sha256']
                or not isinstance(size, int) or isinstance(size, bool) or size <= 0
                or not isinstance(item.get('reason'), str) or not item['reason'].strip()):
            raise ValueError('Incomplete CAS source supplement change: '+name)
        updated[name] = {**old, 'sha256': value, 'bytes': size, 'presentation_id': PRESENTATION_V7_ID}
    report = {'path': PRESENTATION_V7_PATH, 'sha256': digest(path),
        'presentation_id': PRESENTATION_V7_ID, 'publication_kind': required['publication_kind'],
        'changed_paths': sorted(seen), 'previous_presentation_commit': PRESENTATION_V7_PREVIOUS_COMMIT,
        'source_supplement_path': CHEN_REAGENT_CAS_SOURCE_PATH,
        **{key: required[key] for key in ('scientific_review_status', 'scientific_review_scope',
            'scientific_data_unchanged', 'historical_achievement_independent_of_AI_review', 'release_eligible')}}
    return apply_public_academic_presentation(root, updated,
        {**report, 'presentation_chain': [*previous_report['presentation_chain'], report]})


def public_presentation_snapshot_bindings(root: Path, entries: dict) -> list[dict]:
    bindings = []
    for name in sorted(name for name in entries if name.endswith('.html')):
        snapshot_name = PUBLIC_PRESENTATION_SNAPSHOT+'/site/'+name
        snapshot, expected = project_file(root, snapshot_name), entries[name]
        if digest(snapshot) != expected['sha256'] or snapshot.stat().st_size != expected['bytes']:
            raise ValueError('Previous public HTML snapshot differs from its fixed v7 bytes: '+name)
        bindings.append({'path': name, 'snapshot_path': snapshot_name,
                         'sha256': expected['sha256'], 'bytes': expected['bytes']})
    if len(bindings) != 15:
        raise ValueError('The previous public presentation must retain fifteen HTML snapshots')
    return bindings


def embedded_json_records(source: str) -> list:
    """Read embedded JSON values without executing page scripts."""
    class Records(HTMLParser):
        def __init__(self):
            super().__init__(); self.active = None; self.records = []
        def handle_starttag(self, tag, attrs):
            values = dict(attrs)
            if tag == 'script' and values.get('type', '').lower() in {'application/json', 'application/ld+json'}:
                self.active = [values.get('id'), values['type'].lower(), '']
        def handle_data(self, value):
            if self.active is not None:
                self.active[2] += value
        def handle_endtag(self, tag):
            if tag == 'script' and self.active is not None:
                ident, kind, body = self.active
                self.records.append([ident, kind, json.loads(body)])
                self.active = None
    parser = Records(); parser.feed(source); parser.close()
    return parser.records


def a01_history_predecessor_member(root: Path, name: str) -> Path:
    """Read only the three permitted v8 pages from their immutable predecessor.

    A v9 content addition cannot refresh a v8 promise. Other v8 pages continue
    to be checked against the actual website, including PFtB in its entirety.
    """
    if not (root/PRESENTATION_V9_PATH).exists() or name not in A01_HISTORY_ALLOWED_PATHS:
        return project_file(root, 'site/'+name)
    declaration = project_file(root, PRESENTATION_V8_PATH)
    if digest(declaration) != PRESENTATION_V8_SHA256:
        raise ValueError('The preceding public academic presentation v8 is immutable')
    matches = [row for row in read_json(declaration).get('changes', []) if row.get('path') == name]
    if len(matches) != 1:
        raise ValueError('The fixed v8 declaration must identify one predecessor page: '+name)
    expected = matches[0]
    snapshot = project_file(root, A01_HISTORY_SNAPSHOT+'/site/'+name)
    if digest(snapshot) != expected['new_sha256'] or snapshot.stat().st_size != expected['new_bytes']:
        raise ValueError('A01 historical predecessor differs from fixed v8 bytes: '+name)
    return snapshot


def a01_history_predecessor_readme(root: Path) -> Path:
    if not (root/PRESENTATION_V9_PATH).exists():
        return project_file(root, 'README.md')
    declaration = project_file(root, PRESENTATION_V8_PATH)
    if digest(declaration) != PRESENTATION_V8_SHA256:
        raise ValueError('The preceding public academic presentation v8 is immutable')
    matches = [row for row in read_json(declaration).get('editorial_documents', [])
               if row.get('path') == 'README.md']
    if len(matches) != 1:
        raise ValueError('The fixed v8 declaration must identify one README binding')
    expected = matches[0]
    snapshot = project_file(root, A01_HISTORY_SNAPSHOT+'/README.md')
    if digest(snapshot) != expected['sha256'] or snapshot.stat().st_size != expected['bytes']:
        raise ValueError('A01 historical predecessor README differs from fixed v8 bytes')
    return snapshot


def apply_public_academic_presentation(root: Path, entries: dict, previous_report: dict) -> tuple[dict, dict]:
    """Bind public wording changes while retaining historical and scientific data."""
    if not (root/PRESENTATION_V8_PATH).exists():
        return entries, previous_report
    if digest(project_file(root, PRESENTATION_V7_PATH)) != PRESENTATION_V7_SHA256:
        raise ValueError('The preceding CAS source presentation v7 is immutable')
    path = project_file(root, PRESENTATION_V8_PATH); data = read_json(path)
    snapshots = public_presentation_snapshot_bindings(root, entries)
    documents = []
    for name in ('README.md', PUBLIC_ACADEMIC_DOCUMENT):
        if name == 'README.md':
            document = a01_history_predecessor_readme(root)
            documents.append({'path': name, 'sha256': digest(document), 'bytes': document.stat().st_size})
        else:
            documents.append(label_predecessor_binding(root, name))
    required = {'schema_version': '8.0', 'presentation_id': PRESENTATION_V8_ID,
        'publication_kind': 'platform_public_academic_presentation',
        'previous_presentation_commit': PRESENTATION_V8_PREVIOUS_COMMIT,
        'previous_presentation': {'path': PRESENTATION_V7_PATH, 'sha256': PRESENTATION_V7_SHA256},
        'original_baseline_sha256': BASELINE_SHA256, 'original_archive_sha256': ARCHIVE_SHA256,
        'historical_website_snapshots': snapshots,
        'historical_readme_snapshot': historical_public_readme_binding(root),
        'editorial_documents': documents, 'scientific_review_status': 'review_required',
        'scientific_review_scope': 'unchanged_platform_research_only', 'release_eligible': False,
        'scientific_data_unchanged': True, 'historical_achievement_independent_of_AI_review': True,
        'M0_resumed': False}
    if any(data.get(key) != value for key, value in required.items()) or any(
            data.get(key) is not required[key] for key in ('release_eligible', 'scientific_data_unchanged',
                'historical_achievement_independent_of_AI_review', 'M0_resumed')) or any(
            type(data.get(key)) is not int or data[key] != 0 for key in ('new_quantum_calls', 'new_model_API_calls')):
        raise ValueError('Unsupported public academic presentation v8')
    # Only two public phrases may change in the complete PFtB scientific page.
    previous_pf = project_file(root, PUBLIC_PRESENTATION_SNAPSHOT+'/site/pftb/index.html').read_bytes()
    expected_pf = previous_pf
    for old, new in [('首版的 AI 价值是', '本专题的 AI 价值是'),
                     ('早期研究”首版静态页面', '早期研究”专题静态页面')]:
        old, new = old.encode('utf-8'), new.encode('utf-8')
        if expected_pf.count(old) != 1:
            raise ValueError('Ambiguous historical PFtB public phrase')
        expected_pf = expected_pf.replace(old, new)
    if label_predecessor_bytes(root, 'site/pftb/index.html') != expected_pf:
        raise ValueError('PFtB must retain its complete bytes except the two authorized public phrases')
    from render_a01_progress import BEGIN, END
    old_a01 = project_file(root, PUBLIC_PRESENTATION_SNAPSHOT+'/site/'+TOPIC_PATH).read_bytes().decode('utf-8')
    now_a01 = label_predecessor_bytes(root, 'site/'+TOPIC_PATH).decode('utf-8')
    for source in (old_a01, now_a01):
        if source.count(BEGIN) != 1 or source.count(END) != 1:
            raise ValueError('A01 requires its complete scientific progress block')
    if old_a01[old_a01.index(BEGIN):old_a01.index(END)+len(END)] != now_a01[now_a01.index(BEGIN):now_a01.index(END)+len(END)]:
        raise ValueError('Public wording changes must retain the exact A01 scientific progress block')
    for snapshot in snapshots:
        name = snapshot['path']
        source = (a01_history_predecessor_member(root, name).read_bytes() if name in A01_HISTORY_ALLOWED_PATHS
                  else label_predecessor_bytes(root, 'site/'+name))
        if embedded_json_records(source.decode('utf-8')) != embedded_json_records(
                project_file(root, snapshot['snapshot_path']).read_text('utf-8')):
            raise ValueError('Public wording changes must retain embedded JSON values: '+name)
    changes = data.get('changes'); routes = {name for name in entries if name.endswith('.html')}
    if not isinstance(changes, list) or not 1 <= len(changes) <= len(routes):
        raise ValueError('Public presentation must enumerate its edited existing HTML pages')
    updated, seen = {name: dict(value) for name, value in entries.items()}, set()
    for item in changes:
        name = item.get('path')
        if name not in routes or name in seen:
            raise ValueError('Unauthorized or duplicate public presentation path: '+str(name))
        seen.add(name); old = entries[name]
        value, size = item.get('new_sha256'), item.get('new_bytes')
        if (item.get('old_sha256') != old['sha256'] or item.get('old_bytes') != old['bytes']
                or not isinstance(value, str) or not SHA.fullmatch(value) or value == old['sha256']
                or not isinstance(size, int) or isinstance(size, bool) or size <= 0
                or not isinstance(item.get('reason'), str) or not item['reason'].strip()):
            raise ValueError('Incomplete public academic presentation change: '+name)
        updated[name] = {**old, 'sha256': value, 'bytes': size, 'presentation_id': PRESENTATION_V8_ID}
    if data.get('allowed_html_paths') != sorted(seen):
        raise ValueError('The public presentation allowlist must name exactly its edited pages')
    for name, expected in entries.items():
        if name not in seen:
            current = label_predecessor_binding(root, 'site/'+name)
            if current['sha256'] != expected['sha256'] or current['bytes'] != expected['bytes']:
                raise ValueError('Public presentation changed an unlisted website member: '+name)
    report = {'path': PRESENTATION_V8_PATH, 'sha256': digest(path), 'presentation_id': PRESENTATION_V8_ID,
        'publication_kind': required['publication_kind'], 'changed_paths': sorted(seen),
        'previous_presentation_commit': PRESENTATION_V8_PREVIOUS_COMMIT,
        **{key: required[key] for key in ('scientific_review_status', 'scientific_review_scope',
            'scientific_data_unchanged', 'historical_achievement_independent_of_AI_review', 'release_eligible')}}
    return apply_a01_historical_achievement(root, updated,
        {**report, 'presentation_chain': [*previous_report['presentation_chain'], report]})


def a01_history_snapshot_bindings(root: Path, entries: dict) -> list[dict]:
    bindings = []
    for name in sorted(A01_HISTORY_ALLOWED_PATHS):
        snapshot, expected = a01_history_predecessor_member(root, name), entries[name]
        if digest(snapshot) != expected['sha256'] or snapshot.stat().st_size != expected['bytes']:
            raise ValueError('A01 historical snapshot differs from its predecessor entry: '+name)
        bindings.append({'path': name, 'snapshot_path': snapshot.relative_to(root).as_posix(),
                         'sha256': expected['sha256'], 'bytes': expected['bytes']})
    return bindings


def a01_first_report_predecessor_bytes(root: Path, name: str) -> bytes:
    """Reconstruct v9 using one saved marker; reject every outside-marker edit."""
    current = label_predecessor_bytes(root, 'site/'+name)
    if not (root/PRESENTATION_V10_PATH).exists() or name not in A01_FIRST_REPORT_MARKERS:
        return current
    declaration = project_file(root, PRESENTATION_V9_PATH)
    if digest(declaration) != PRESENTATION_V9_SHA256:
        raise ValueError('The preceding A01 historical presentation v9 is immutable')
    marker = A01_FIRST_REPORT_MARKERS[name]
    begin, end = ('<!-- '+marker+':BEGIN -->').encode(), ('<!-- '+marker+':END -->').encode()
    if current.count(begin) != 1 or current.count(end) != 1 or current.index(end) < current.index(begin):
        raise ValueError('First-report marker is missing or ambiguous: '+name)
    old_block = project_file(root, A01_FIRST_REPORT_SNAPSHOT+'/markers/'+marker+'.html').read_bytes()
    if (old_block.count(begin) != 1 or old_block.count(end) != 1
            or not old_block.startswith(begin) or not old_block.endswith(end)):
        raise ValueError('Invalid saved first-report predecessor marker: '+name)
    rebuilt = current[:current.index(begin)]+old_block+current[current.index(end)+len(end):]
    matches = [row for row in read_json(declaration)['changes'] if row['path'] == name]
    if len(matches) != 1 or hashlib.sha256(rebuilt).hexdigest() != matches[0]['new_sha256'] or len(rebuilt) != matches[0]['new_bytes']:
        raise ValueError('A01 first-report content changed outside its single authorized marker: '+name)
    return rebuilt


def a01_first_report_predecessor_document(root: Path, name: str) -> Path:
    if not (root/PRESENTATION_V10_PATH).exists() or name not in A01_FIRST_REPORT_OLD_DOCUMENTS:
        return project_file(root, name)
    declaration = project_file(root, PRESENTATION_V9_PATH)
    if digest(declaration) != PRESENTATION_V9_SHA256:
        raise ValueError('The preceding A01 historical presentation v9 is immutable')
    matches = [row for row in read_json(declaration)['editorial_documents'] if row['path'] == name]
    snapshot = project_file(root, A01_FIRST_REPORT_SNAPSHOT+'/'+name)
    if len(matches) != 1 or digest(snapshot) != matches[0]['sha256'] or snapshot.stat().st_size != matches[0]['bytes']:
        raise ValueError('First-report document snapshot differs from fixed v9 bytes: '+name)
    return snapshot


def apply_a01_historical_achievement(root: Path, entries: dict, previous_report: dict) -> tuple[dict, dict]:
    """Publish source-attributed A01 history without changing scientific results.

    Bindings certify content identity and bounded scope, not historical priority,
    professional transcription, the original experiments or an AI mechanism.
    """
    if not (root/PRESENTATION_V9_PATH).exists():
        return entries, previous_report
    if digest(project_file(root, PRESENTATION_V8_PATH)) != PRESENTATION_V8_SHA256:
        raise ValueError('The preceding public academic presentation v8 is immutable')
    path = project_file(root, PRESENTATION_V9_PATH); data = read_json(path)
    snapshots = a01_history_snapshot_bindings(root, entries)
    old_readme = a01_history_predecessor_readme(root)
    readme_snapshot = {'original_path': 'README.md',
        'snapshot_path': old_readme.relative_to(root).as_posix(),
        'sha256': digest(old_readme), 'bytes': old_readme.stat().st_size}
    documents = [{'path': name, 'sha256': digest(a01_first_report_predecessor_document(root, name)),
                  'bytes': a01_first_report_predecessor_document(root, name).stat().st_size}
                 for name in A01_HISTORY_DOCUMENTS]
    required = {'schema_version': '9.0', 'presentation_id': PRESENTATION_V9_ID,
        'publication_kind': 'a01_source_attributed_historical_achievement',
        'previous_presentation_commit': PRESENTATION_V9_PREVIOUS_COMMIT,
        'previous_presentation': {'path': PRESENTATION_V8_PATH, 'sha256': PRESENTATION_V8_SHA256},
        'original_baseline_sha256': BASELINE_SHA256, 'original_archive_sha256': ARCHIVE_SHA256,
        'historical_website_snapshots': snapshots, 'historical_readme_snapshot': readme_snapshot,
        'editorial_documents': documents, 'allowed_html_paths': sorted(A01_HISTORY_ALLOWED_PATHS),
        'scientific_review_status': 'review_required', 'release_eligible': False,
        'scientific_data_unchanged': True, 'historical_achievement_independent_of_AI_review': True,
        'M0_resumed': False}
    if any(data.get(key) != value for key, value in required.items()) or any(
            data.get(key) is not required[key] for key in ('release_eligible', 'scientific_data_unchanged',
                'historical_achievement_independent_of_AI_review', 'M0_resumed')) or any(
            type(data.get(key)) is not int or data[key] != 0 for key in ('new_quantum_calls', 'new_model_API_calls')):
        raise ValueError('Unsupported source-attributed A01 historical presentation')
    content = read_json(project_file(root, A01_HISTORY_CONTENT))
    if not isinstance(content, dict) or content.get('achievement_line') != 'A01':
        raise ValueError('A01 historical content requires its separate A01 source record')
    from render_a01_progress import BEGIN, END
    previous = a01_history_predecessor_member(root, TOPIC_PATH).read_bytes().decode('utf-8')
    current = label_predecessor_bytes(root, 'site/'+TOPIC_PATH).decode('utf-8')
    for source in (previous, current):
        if source.count(BEGIN) != 1 or source.count(END) != 1 or source.index(END) < source.index(BEGIN):
            raise ValueError('A01 history must preserve its unambiguous complete scientific progress block')
    if previous[previous.index(BEGIN):previous.index(END)+len(END)] != current[current.index(BEGIN):current.index(END)+len(END)]:
        raise ValueError('A01 historical presentation cannot change frozen scientific progress')
    for snapshot in snapshots:
        name = snapshot['path']
        prior_records = embedded_json_records(project_file(root, snapshot['snapshot_path']).read_text('utf-8'))
        now_records = embedded_json_records(a01_first_report_predecessor_bytes(root, name).decode('utf-8'))
        additions = [row for row in now_records if row[0] == 'a01-historical-achievements']
        retained = [row for row in now_records if row[0] != 'a01-historical-achievements']
        if retained != prior_records:
            raise ValueError('A01 historical presentation must retain every existing embedded JSON record: '+name)
        if len(additions) > 1 or any(row[1] != 'application/json' or row[2] != content for row in additions):
            raise ValueError('Added A01 historical JSON must match the separate source record: '+name)
        if name == TOPIC_PATH and len(additions) != 1:
            raise ValueError('The A01 historical topic must expose its exact separate source JSON')
    changes = data.get('changes')
    if not isinstance(changes, list) or len(changes) != len(A01_HISTORY_ALLOWED_PATHS):
        raise ValueError('A01 historical presentation must enumerate exactly its three existing HTML pages')
    updated, seen = {name: dict(value) for name, value in entries.items()}, set()
    for item in changes:
        name = item.get('path')
        if name not in A01_HISTORY_ALLOWED_PATHS or name in seen:
            raise ValueError('Unauthorized or duplicate A01 historical path: '+str(name))
        seen.add(name); old = entries[name]
        value, size = item.get('new_sha256'), item.get('new_bytes')
        if (item.get('old_sha256') != old['sha256'] or item.get('old_bytes') != old['bytes']
                or not isinstance(value, str) or not SHA.fullmatch(value) or value == old['sha256']
                or type(size) is not int or size <= 0
                or not isinstance(item.get('reason'), str) or not item['reason'].strip()):
            raise ValueError('Incomplete A01 historical presentation change: '+name)
        updated[name] = {**old, 'sha256': value, 'bytes': size, 'presentation_id': PRESENTATION_V9_ID}
    for name, expected in updated.items():
        current = a01_first_report_predecessor_bytes(root, name)
        if hashlib.sha256(current).hexdigest() != expected['sha256'] or len(current) != expected['bytes']:
            raise ValueError('A01 historical publication differs from its bounded website identity: '+name)
    report = {'path': PRESENTATION_V9_PATH, 'sha256': digest(path), 'presentation_id': PRESENTATION_V9_ID,
        'publication_kind': required['publication_kind'], 'changed_paths': sorted(seen),
        'previous_presentation_commit': PRESENTATION_V9_PREVIOUS_COMMIT,
        'historical_sources_path': A01_HISTORY_CONTENT,
        **{key: required[key] for key in ('scientific_review_status', 'scientific_data_unchanged',
            'historical_achievement_independent_of_AI_review', 'release_eligible')}}
    return apply_a01_first_report(root, updated,
        {**report, 'presentation_chain': [*previous_report['presentation_chain'], report]})


def a01_first_report_snapshot_bindings(root: Path) -> list[dict]:
    result = []
    for name, marker in sorted(A01_FIRST_REPORT_MARKERS.items()):
        rebuilt = a01_first_report_predecessor_bytes(root, name)
        path = A01_FIRST_REPORT_SNAPSHOT+'/markers/'+marker+'.html'
        saved = project_file(root, path)
        result.append({'path': name, 'marker': marker, 'snapshot_path': path,
            'sha256': digest(saved), 'bytes': saved.stat().st_size,
            'reconstructed_page_sha256': hashlib.sha256(rebuilt).hexdigest(),
            'reconstructed_page_bytes': len(rebuilt)})
    for name in A01_FIRST_REPORT_OLD_DOCUMENTS:
        saved = a01_first_report_predecessor_document(root, name)
        result.append({'path': name, 'snapshot_path': saved.relative_to(root).as_posix(),
                       'sha256': digest(saved), 'bytes': saved.stat().st_size})
    return result


def apply_a01_first_report(root: Path, entries: dict, previous_report: dict) -> tuple[dict, dict]:
    """Bind source reading inside three existing markers, preserving v1 evidence."""
    if not (root/PRESENTATION_V10_PATH).exists():
        return entries, previous_report
    if digest(project_file(root, PRESENTATION_V9_PATH)) != PRESENTATION_V9_SHA256:
        raise ValueError('The preceding A01 historical presentation v9 is immutable')
    path = project_file(root, PRESENTATION_V10_PATH); data = read_json(path)
    documents = [label_predecessor_binding(root, name) for name in A01_FIRST_REPORT_DOCUMENTS]
    required = {'schema_version': '10.0', 'presentation_id': PRESENTATION_V10_ID,
        'publication_kind': 'a01_first_report_primary_reading',
        'previous_presentation_commit': PRESENTATION_V10_PREVIOUS_COMMIT,
        'previous_presentation': {'path': PRESENTATION_V9_PATH, 'sha256': PRESENTATION_V9_SHA256},
        'original_baseline_sha256': BASELINE_SHA256, 'original_archive_sha256': ARCHIVE_SHA256,
        'allowed_html_paths': sorted(A01_FIRST_REPORT_MARKERS),
        'allowed_marker_blocks': A01_FIRST_REPORT_MARKERS,
        'historical_snapshots': a01_first_report_snapshot_bindings(root),
        'editorial_documents': documents, 'historical_v1_records_retained': True,
        'scientific_review_status': 'review_required', 'release_eligible': False,
        'scientific_data_unchanged': True, 'M0_resumed': False,
        'historical_achievement_independent_of_AI_review': True}
    if any(data.get(key) != value for key, value in required.items()) or any(
            data.get(key) is not required[key] for key in ('release_eligible', 'scientific_data_unchanged',
                'historical_v1_records_retained', 'M0_resumed', 'historical_achievement_independent_of_AI_review')) or any(
            type(data.get(key)) is not int or data[key] != 0 for key in ('new_quantum_calls', 'new_model_API_calls')):
        raise ValueError('Unsupported A01 first-report primary reading presentation')
    content = read_json(project_file(root, A01_FIRST_REPORT_CONTENT))
    if (not isinstance(content, dict) or content.get('achievement_line') != 'A01'
            or content.get('schema_version') != '2.0'
            or not isinstance(content.get('first_report'), dict) or not content['first_report']):
        raise ValueError('First-report reading requires its separate v2 source evidence')
    for name in A01_FIRST_REPORT_MARKERS:
        previous = embedded_json_records(a01_first_report_predecessor_bytes(root, name).decode('utf-8'))
        current = embedded_json_records(label_predecessor_bytes(root, 'site/'+name).decode('utf-8'))
        prior_other = [row for row in previous if row[0] != 'a01-historical-achievements']
        current_other = [row for row in current if row[0] != 'a01-historical-achievements']
        new_source = [row for row in current if row[0] == 'a01-historical-achievements']
        if prior_other != current_other or len(new_source) > 1:
            raise ValueError('First-report reading cannot replace other embedded source records: '+name)
        if any(row[1] != 'application/json' or row[2] != content for row in new_source):
            raise ValueError('First-report embedded source differs from its v2 evidence: '+name)
        if name == TOPIC_PATH and len(new_source) != 1:
            raise ValueError('First-report topic requires one separate v2 source record')
    changes = data.get('changes')
    if not isinstance(changes, list) or len(changes) != len(A01_FIRST_REPORT_MARKERS):
        raise ValueError('First-report presentation requires exactly three existing marker pages')
    updated, seen = {name: dict(value) for name, value in entries.items()}, set()
    for item in changes:
        name = item.get('path')
        if name not in A01_FIRST_REPORT_MARKERS or name in seen:
            raise ValueError('Unauthorized or duplicate first-report path: '+str(name))
        seen.add(name); old = entries[name]
        value, size = item.get('new_sha256'), item.get('new_bytes')
        if (item.get('old_sha256') != old['sha256'] or item.get('old_bytes') != old['bytes']
                or not isinstance(value, str) or not SHA.fullmatch(value) or value == old['sha256']
                or type(size) is not int or size <= 0
                or not isinstance(item.get('reason'), str) or not item['reason'].strip()):
            raise ValueError('Incomplete first-report marker presentation: '+name)
        updated[name] = {**old, 'sha256': value, 'bytes': size, 'presentation_id': PRESENTATION_V10_ID}
    for name, expected in updated.items():
        member = label_predecessor_binding(root, 'site/'+name)
        if member['sha256'] != expected['sha256'] or member['bytes'] != expected['bytes']:
            raise ValueError('First-report website differs from its bounded identity: '+name)
    report = {'path': PRESENTATION_V10_PATH, 'sha256': digest(path), 'presentation_id': PRESENTATION_V10_ID,
        'publication_kind': required['publication_kind'], 'changed_paths': sorted(seen),
        'previous_presentation_commit': PRESENTATION_V10_PREVIOUS_COMMIT,
        'historical_sources_path': A01_FIRST_REPORT_CONTENT, 'marker_only_html_changes': True,
        **{key: required[key] for key in ('scientific_review_status', 'scientific_data_unchanged',
            'historical_achievement_independent_of_AI_review', 'release_eligible')}}
    return apply_public_line_labels(root, updated,
        {**report, 'presentation_chain': [*previous_report['presentation_chain'], report]})


def apply_public_line_labels(root: Path, entries: dict, previous_report: dict) -> tuple[dict, dict]:
    """Apply one deterministic label projection after replaying every old promise.

    The text patches reconstruct exact v10 pages, not a refreshed baseline.
    Current pages must additionally equal the shared names-only projection.
    """
    if not (root/PRESENTATION_V11_PATH).exists():
        return entries, previous_report
    if digest(project_file(root, PRESENTATION_V10_PATH)) != PRESENTATION_V10_SHA256:
        raise ValueError('The preceding first-report presentation v10 is immutable')
    from public_line_labels import project_html, project_markdown
    path = project_file(root, PRESENTATION_V11_PATH); data = read_json(path)
    if not isinstance(data, dict):
        raise ValueError('Public-label presentation must be a JSON object')
    routes = sorted(name for name in entries if name.endswith('.html') and name != 'pftb/index.html')
    documents = [ai_research_predecessor_binding(root, name) for name in PUBLIC_LABEL_DOCUMENTS]
    required = {'schema_version': '11.0', 'presentation_id': PRESENTATION_V11_ID,
        'publication_kind': 'platform_public_line_labels',
        'previous_presentation_commit': PRESENTATION_V11_PREVIOUS_COMMIT,
        'previous_presentation': {'path': PRESENTATION_V10_PATH, 'sha256': PRESENTATION_V10_SHA256},
        'original_baseline_sha256': BASELINE_SHA256, 'original_archive_sha256': ARCHIVE_SHA256,
        'allowed_html_paths': routes, 'editorial_documents': documents,
        'label_projection': {'module': 'scripts/public_line_labels.py',
                             'mapping': 'content/achievement-labels.v1.json'},
        'reconstruction_kind': 'deduplicated_exact_utf8_text_edits',
        'scientific_review_status': 'review_required', 'release_eligible': False,
        'scientific_data_unchanged': True, 'M0_resumed': False,
        'historical_achievement_independent_of_AI_review': True}
    if (len(routes) != 14 or any(data.get(key) != value for key, value in required.items())
            or any(data.get(key) is not required[key] for key in ('release_eligible',
                'scientific_data_unchanged', 'M0_resumed', 'historical_achievement_independent_of_AI_review'))
            or any(type(data.get(key)) is not int or data[key] != 0
                   for key in ('new_quantum_calls', 'new_model_API_calls'))):
        raise ValueError('Unsupported names-only public line-label presentation v11')
    files, pool = data.get('reversible_text_files'), data.get('reverse_text_patch_pool')
    allowed_files = {'site/'+name for name in routes} | set(PUBLIC_LABEL_PREDECESSOR_DOCUMENTS)
    if (not isinstance(files, list) or not isinstance(pool, list) or not pool
            or any(not isinstance(row, dict) or row.get('path') not in allowed_files for row in files)
            or len({row['path'] for row in files}) != len(files)
            or {row['path'] for row in files if row['path'].startswith('site/')} != {'site/'+name for name in routes}):
        raise ValueError('Public labels must enumerate only their exact HTML/prose/renderer text patches')
    if any(not isinstance(row.get('edits'), list) or not row['edits'] or any(
            not isinstance(edit, dict) or type(edit.get('replacement')) is not int
            for edit in row['edits']) for row in files):
        raise ValueError('Public-label text-patch references must be nonempty integer-indexed edits')
    used = {edit['replacement'] for row in files for edit in row['edits']}
    if used != set(range(len(pool))):
        raise ValueError('Public-label replacement pool must contain exactly its used text segments')
    # These fixed identities include prose not otherwise bound in the old chain.
    for name, (old_sha, old_size) in PUBLIC_LABEL_PREDECESSOR_DOCUMENTS.items():
        old = label_predecessor_bytes(root, name)
        if hashlib.sha256(old).hexdigest() != old_sha or len(old) != old_size:
            raise ValueError('Public-label prose/renderer differs from its fixed be48dfc predecessor: '+name)
        if name in PUBLIC_LABEL_MARKDOWN and project_markdown(old.decode('utf-8')).encode('utf-8') != ai_research_predecessor_bytes(root, name):
            raise ValueError('Public prose must equal the shared label projection exactly: '+name)
    changes = data.get('changes')
    if (not isinstance(changes, list) or any(not isinstance(row, dict) for row in changes)
            or [row.get('path') for row in changes] != routes):
        raise ValueError('Public-label changes must enumerate exactly fourteen original HTML routes')
    updated = {name: dict(value) for name, value in entries.items()}
    json_scripts = re.compile(r'<script\b[^>]*\btype\s*=\s*[\"\']application/(?:ld\+)?json[\"\'][^>]*>.*?</script\s*>', re.I | re.S)
    from render_a01_progress import BEGIN, END
    for item in changes:
        name = item['path']; old = entries[name]
        before = label_predecessor_bytes(root, 'site/'+name)
        after = ai_research_predecessor_bytes(root, 'site/'+name)
        source = before.decode('utf-8'); current = after.decode('utf-8')
        if (item.get('old_sha256') != old['sha256'] or item.get('old_bytes') != old['bytes']
                or hashlib.sha256(before).hexdigest() != old['sha256'] or len(before) != old['bytes']
                or item.get('new_sha256') != hashlib.sha256(after).hexdigest() or item.get('new_bytes') != len(after)
                or before == after or not isinstance(item.get('reason'), str) or not item['reason'].strip()):
            raise ValueError('Public-label HTML differs from its complete old/new byte identities: '+name)
        if project_html(source, name) != current:
            raise ValueError('HTML differs from the exact names-only public projection: '+name)
        if json_scripts.findall(source) != json_scripts.findall(current) or embedded_json_records(source) != embedded_json_records(current):
            raise ValueError('Public line labels must preserve every complete embedded JSON record: '+name)
        if name == TOPIC_PATH:
            for value in (source, current):
                if value.count(BEGIN) != 1 or value.count(END) != 1 or value.index(END) < value.index(BEGIN):
                    raise ValueError('Public labels require the unambiguous complete frozen A01 scientific block')
            if source[source.index(BEGIN):source.index(END)+len(END)] != current[current.index(BEGIN):current.index(END)+len(END)]:
                raise ValueError('Public labels cannot alter any A01 scientific-progress byte')
        updated[name] = {**old, 'sha256': item['new_sha256'], 'bytes': item['new_bytes'],
                         'presentation_id': PRESENTATION_V11_ID}
    # Includes both original JSON files and the entire unchanged PFtB archive.
    for name, expected in updated.items():
        member = ai_research_predecessor_binding(root, 'site/'+name)
        if member['sha256'] != expected['sha256'] or member['bytes'] != expected['bytes']:
            raise ValueError('Public line labels changed an unlisted or bound website byte: '+name)
    report = {'path': PRESENTATION_V11_PATH, 'sha256': digest(path), 'presentation_id': PRESENTATION_V11_ID,
        'publication_kind': required['publication_kind'], 'changed_paths': routes,
        'previous_presentation_commit': PRESENTATION_V11_PREVIOUS_COMMIT,
        'names_only_projection': True, 'exact_predecessor_reconstruction': True,
        **{key: required[key] for key in ('scientific_review_status', 'scientific_data_unchanged',
            'historical_achievement_independent_of_AI_review', 'release_eligible')}}
    return apply_ai_research_section(root, updated,
        {**report, 'presentation_chain': [*previous_report['presentation_chain'], report]})


def publication_members(root: Path, entries: dict) -> list[dict]:
    """Return the exact Pages allowlist, including only the authorized new route.

    The original 21-member/15-HTML baseline remains immutable. Repository
    research data never become publishable merely because they exist.
    """
    baseline_path = project_file(root, 'provenance/website-baseline.json')
    if digest(baseline_path) != BASELINE_SHA256:
        raise ValueError('Publication members require the immutable original baseline')
    original = {row['path'] for row in read_json(baseline_path)['files']}
    original_html = {name for name in original if name.endswith('.html')}
    added = {AI_RESEARCH_ROUTE} if (root/PRESENTATION_V12_PATH).is_file() else set()
    if len(original) != 21 or len(original_html) != 15 or set(entries) != original | added:
        raise ValueError('The effective member set may add only the explicit AI research HTML route')
    html = {name for name in entries if name.endswith('.html')}
    public_json = {name for name in entries if name.endswith('.json')}
    if (html != original_html | added or public_json != {
            'data/public-sources.json', 'data/achievement-lines.json'}):
        raise ValueError('Pages must retain the original HTML and two JSON routes, with only the authorized HTML addition')
    return [entries[name] for name in sorted(html | public_json)]


def apply_ai_research_section(root: Path, entries: dict, previous_report: dict) -> tuple[dict, dict]:
    """Add the bounded AI overview and its single second-level static page."""
    if not (root/PRESENTATION_V12_PATH).exists():
        return entries, previous_report
    if digest(project_file(root, PRESENTATION_V11_PATH)) != PRESENTATION_V11_SHA256:
        raise ValueError('The preceding public line-label presentation v11 is immutable')
    path = project_file(root, PRESENTATION_V12_PATH); data = read_json(path)
    if not isinstance(data, dict):
        raise ValueError('AI research presentation must be a JSON object')
    documents = [{'path': name, 'sha256': digest(project_file(root, name)),
                  'bytes': project_file(root, name).stat().st_size} for name in AI_RESEARCH_DOCUMENTS]
    protected = {name: {'sha256': row['sha256'], 'bytes': row['bytes']}
                 for name, row in entries.items() if name not in AI_RESEARCH_ALLOWED_PATHS}
    required = {'schema_version': '12.0', 'presentation_id': PRESENTATION_V12_ID,
        'publication_kind': 'platform_ai_research_overview',
        'previous_presentation_commit': PRESENTATION_V12_PREVIOUS_COMMIT,
        'previous_presentation': {'path': PRESENTATION_V11_PATH, 'sha256': PRESENTATION_V11_SHA256},
        'original_baseline_sha256': BASELINE_SHA256, 'original_archive_sha256': ARCHIVE_SHA256,
        'allowed_html_paths': sorted(AI_RESEARCH_ALLOWED_PATHS),
        'added_html_paths': [AI_RESEARCH_ROUTE], 'editorial_documents': documents,
        'protected_website_members': protected,
        'reconstruction_kind': 'deduplicated_exact_utf8_text_edits',
        'scientific_review_status': 'review_required', 'release_eligible': False,
        'scientific_data_unchanged': True, 'M0_resumed': False,
        'historical_achievement_independent_of_AI_review': True}
    if (any(data.get(key) != value for key, value in required.items())
            or any(data.get(key) is not required[key] for key in ('release_eligible',
                'scientific_data_unchanged', 'M0_resumed', 'historical_achievement_independent_of_AI_review'))
            or any(type(data.get(key)) is not int or data[key] != 0
                   for key in ('new_quantum_calls', 'new_model_API_calls'))
            or not isinstance(data.get('authorization'), str) or not data['authorization'].strip()):
        raise ValueError('Unsupported bounded AI research presentation v12')
    files, pool = data.get('reversible_text_files'), data.get('reverse_text_patch_pool')
    if (not isinstance(files, list) or not files or not isinstance(pool, list) or not pool
            or any(not isinstance(row, dict) or row.get('path') not in AI_RESEARCH_PREDECESSOR_FILES for row in files)
            or len({row['path'] for row in files}) != len(files)
            or any(not isinstance(row.get('edits'), list) or not row['edits'] or any(
                not isinstance(edit, dict) or type(edit.get('replacement')) is not int
                for edit in row['edits']) for row in files)):
        raise ValueError('AI research may enumerate only its exact authorized predecessor text edits')
    used = {edit['replacement'] for row in files for edit in row['edits']}
    if used != set(range(len(pool))):
        raise ValueError('AI research replacement pool must contain exactly its used text segments')
    changed_files = set()
    for name, (old_sha, old_size) in AI_RESEARCH_PREDECESSOR_FILES.items():
        old = ai_research_predecessor_bytes(root, name)
        if hashlib.sha256(old).hexdigest() != old_sha or len(old) != old_size:
            raise ValueError('AI research predecessor differs from its fixed 1c3c6a0 identity: '+name)
        if old != project_file(root, name).read_bytes():
            changed_files.add(name)
    if {row['path'] for row in files} != changed_files:
        raise ValueError('AI research text patches must enumerate every and only changed predecessor file')
    from public_line_labels import project_html, project_markdown
    for name in ('README.md', AI_RESEARCH_DOCUMENT):
        current = project_file(root, name).read_text('utf-8')
        if project_markdown(current) != current:
            raise ValueError('AI research prose must retain canonical named achievement references: '+name)
    changes = data.get('changes')
    if (not isinstance(changes, list) or any(not isinstance(row, dict) for row in changes)
            or [row.get('path') for row in changes] != sorted(AI_RESEARCH_ALLOWED_PATHS)):
        raise ValueError('AI research changes must enumerate its two existing HTML pages')
    updated = {name: dict(row) for name, row in entries.items()}
    json_scripts = re.compile(r'<script\b[^>]*\btype\s*=\s*[\"\']application/(?:ld\+)?json[\"\'][^>]*>.*?</script\s*>', re.I | re.S)
    for item in changes:
        name = item['path']; old = entries[name]
        before = ai_research_predecessor_bytes(root, 'site/'+name)
        after = project_file(root, 'site/'+name).read_bytes()
        source, current = before.decode('utf-8'), after.decode('utf-8')
        if (item.get('old_sha256') != old['sha256'] or item.get('old_bytes') != old['bytes']
                or hashlib.sha256(before).hexdigest() != old['sha256'] or len(before) != old['bytes']
                or item.get('new_sha256') != hashlib.sha256(after).hexdigest() or item.get('new_bytes') != len(after)
                or before == after or not isinstance(item.get('reason'), str) or not item['reason'].strip()):
            raise ValueError('AI research HTML differs from its complete old/new byte identities: '+name)
        if json_scripts.findall(source) != json_scripts.findall(current):
            raise ValueError('AI research must preserve every complete existing embedded JSON byte: '+name)
        if project_html(current, name) != current:
            raise ValueError('AI research HTML must retain canonical named achievement references: '+name)
        updated[name] = {**old, 'sha256': item['new_sha256'], 'bytes': item['new_bytes'],
                         'presentation_id': PRESENTATION_V12_ID}
    additions = data.get('additions')
    if (not isinstance(additions, list) or len(additions) != 1
            or not isinstance(additions[0], dict) or additions[0].get('path') != AI_RESEARCH_ROUTE
            or AI_RESEARCH_ROUTE in entries):
        raise ValueError('AI research may add exactly research/index.html')
    addition = additions[0]; added = project_file(root, 'site/'+AI_RESEARCH_ROUTE)
    if (addition.get('sha256') != digest(added) or addition.get('bytes') != added.stat().st_size
            or type(addition.get('bytes')) is not int or addition['bytes'] <= 0
            or not isinstance(addition.get('reason'), str) or not addition['reason'].strip()
            or project_html(added.read_text('utf-8'), AI_RESEARCH_ROUTE) != added.read_text('utf-8')):
        raise ValueError('The new AI research route differs from its exact static HTML binding')
    updated[AI_RESEARCH_ROUTE] = {'path': AI_RESEARCH_ROUTE, 'sha256': addition['sha256'],
        'bytes': addition['bytes'], 'presentation_id': PRESENTATION_V12_ID}
    for name, expected in updated.items():
        member = project_file(root, 'site/'+name)
        if digest(member) != expected['sha256'] or member.stat().st_size != expected['bytes']:
            raise ValueError('AI research changed an unlisted or bound website byte: '+name)
    members = publication_members(root, updated)
    from render_ai_research import inspect_ai_research
    consistency = inspect_ai_research(root)
    if consistency.get('status') != 'passed':
        raise ValueError('AI research differs from its source-derived rendering: '+str(consistency.get('errors', [])))
    report = {'path': PRESENTATION_V12_PATH, 'sha256': digest(path), 'presentation_id': PRESENTATION_V12_ID,
        'publication_kind': required['publication_kind'],
        'changed_paths': sorted(AI_RESEARCH_ALLOWED_PATHS | {AI_RESEARCH_ROUTE}),
        'added_paths': [AI_RESEARCH_ROUTE], 'previous_presentation_commit': PRESENTATION_V12_PREVIOUS_COMMIT,
        'exact_predecessor_reconstruction': True, 'original_embedded_json_bytes_preserved': True,
        'source_derived_rendering': True, 'published_html_count': len(members)-2,
        'published_json_count': 2, 'published_member_count_with_marker': len(members)+1,
        **{key: required[key] for key in ('scientific_review_status', 'scientific_data_unchanged',
            'historical_achievement_independent_of_AI_review', 'release_eligible', 'M0_resumed')}}
    return updated, {**report, 'presentation_chain': [*previous_report['presentation_chain'], report]}


def effective_website_entries(root: Path, baseline: dict, *, verify_current=True,
                              revision_chain=None, include_presentation=True) -> tuple[dict, dict]:
    """Apply immutable historical declarations, then check only the final bytes.

    A historical revision describes its own old/new bytes. It must not require
    the current website to retain that historical edition's final HTML.
    ``verify_current=False`` is used only to prepare a new explicit revision;
    production checks always use the default and verify every effective member.
    ``include_presentation=False`` reads the unchanged scientific predecessor
    chain when creating its independent platform presentation declaration.
    """
    baseline_path = root/'provenance/website-baseline.json'
    if digest(baseline_path) != BASELINE_SHA256:
        raise ValueError('Original YouMind baseline bytes changed; a revision must not refresh it')
    if baseline.get('archive_sha256') != ARCHIVE_SHA256:
        raise ValueError('Unexpected original export archive identity')
    if digest(project_file(root, 'upstream/chen-qingyun-a2-citations-candidate.zip')) != ARCHIVE_SHA256:
        raise ValueError('Original YouMind export ZIP bytes changed')
    entries = {entry['path']: dict(entry) for entry in baseline['files']}
    selected = current_publication(root)
    chain = revision_chain if revision_chain is not None else selected['revision_chain']
    if chain not in ([REVISION_PATH], [REVISION_PATH, REVISION_V2_PATH]):
        raise ValueError('Unsupported A01 revision chain')
    if not (root/REVISION_PATH).exists():
        if not selected['legacy']:
            raise ValueError('Current A01 registry requires its immutable v1 predecessor')
        return entries, {'present': False, 'changed_paths': [], 'original_baseline_preserved': True}
    stages, all_changed = [], set()
    for edition, name in enumerate(chain, 1):
        revision_path = project_file(root, name)
        revision = read_json(revision_path)
        if edition == 1:
            if digest(revision_path) != REVISION_V1_SHA256 or digest(project_file(root, PROGRESS_PATH)) != PROGRESS_V1_SHA256:
                raise ValueError('The original public progress and revision v1 are immutable')
        if (revision.get('schema_version') != ('1.0' if edition == 1 else '2.0')
                or revision.get('revision_id') != 'A01-PROGRESS-20261113-v'+str(edition)):
            raise ValueError('Unsupported A01 page revision contract')
        if (revision.get('publication_kind') != 'a01_research_progress'
                or revision.get('scientific_review_status') != 'review_required'
                or revision.get('release_eligible') is not False):
            raise ValueError('A01 page revision is public progress only, pending scientific review')
        if revision.get('original_baseline_sha256') != BASELINE_SHA256 or revision.get('original_archive_sha256') != ARCHIVE_SHA256:
            raise ValueError('Revision does not bind the preserved original source identities')
        if edition == 2 and revision.get('previous_revision') != {'path': REVISION_PATH, 'sha256': REVISION_V1_SHA256}:
            raise ValueError('A01 revision v2 must bind its immutable v1 predecessor')
        commit = revision.get('evidence_commit_s1' if edition == 1 else 'evidence_commit_s3')
        if not isinstance(commit, str) or not COMMIT.fullmatch(commit):
            raise ValueError('A01 page revision requires a fixed evidence commit')
        public = revision.get('public_progress', {})
        progress_name = PROGRESS_PATH if edition == 1 else PROGRESS_V2_PATH
        if public.get('path') != progress_name or not isinstance(public.get('sha256'), str) or not SHA.fullmatch(public['sha256']):
            raise ValueError('A01 revision must bind its separate public progress data')
        if digest(project_file(root, progress_name)) != public['sha256']:
            raise ValueError('A01 progress bytes differ from page revision binding')
        progress = read_json(root/progress_name)
        if progress.get('evidence_archive_commit') != commit:
            raise ValueError('A01 page and progress record refer to different evidence commits')
        changes = revision.get('changes')
        if not isinstance(changes, list) or not 1 <= len(changes) <= len(ALLOWED_CHANGES):
            raise ValueError('Revision must explicitly enumerate one to three authorized HTML changes')
        seen = set()
        for item in changes:
            member = item.get('path')
            if member not in ALLOWED_CHANGES or member in seen:
                raise ValueError('Unauthorized or duplicate revised website path: '+str(member))
            seen.add(member)
            old = entries.get(member)
            if old is None or item.get('old_sha256') != old['sha256'] or item.get('old_bytes') != old['bytes']:
                raise ValueError('Revision old bytes must match the preceding effective edition: '+member)
            value, size = item.get('new_sha256'), item.get('new_bytes')
            if (not isinstance(value, str) or not SHA.fullmatch(value) or value == old['sha256']
                    or not isinstance(size, int) or isinstance(size, bool) or size <= 0
                    or not isinstance(item.get('reason'), str) or not item['reason'].strip()
                    or item.get('source_evidence_commit') != commit):
                raise ValueError('Incomplete A01 page revision record: '+member)
            entries[member] = {**old, 'sha256': value, 'bytes': size,
                'original_sha256': old.get('original_sha256', old['sha256']),
                'revision_id': revision['revision_id']}
        if TOPIC_PATH not in seen:
            raise ValueError('An A01 progress revision must update its existing topic page')
        all_changed.update(seen)
        stages.append({'path': name, 'sha256': digest(revision_path),
            'revision_id': revision['revision_id'], 'changed_paths': sorted(seen),
            'public_progress_sha256': public['sha256'], 'evidence_archive_commit': commit})
    presentation = None
    if include_presentation:
        entries, presentation = apply_presentation_overlay(root, entries, chain=chain)
        if presentation:
            all_changed.update(presentation['changed_paths'])
    if verify_current:
        for member in all_changed:
            current = project_file(root, 'site/'+member)
            if digest(current) != entries[member]['sha256'] or current.stat().st_size != entries[member]['bytes']:
                raise ValueError('Current website bytes differ from the final authorized revision: '+member)
    latest = stages[-1]
    return entries, {'present': True, 'path': latest['path'], 'sha256': latest['sha256'],
        'revision_id': latest['revision_id'], 'changed_paths': sorted(all_changed),
        'current_revision_changed_paths': latest['changed_paths'],
        'revision_chain': stages, 'public_progress_path': public['path'],
        'original_baseline_preserved': True, 'original_baseline_sha256': BASELINE_SHA256,
        'public_progress_sha256': public['sha256'], 'current_evidence_commit': commit,
        'evidence_commit_s1': stages[0]['evidence_archive_commit'],
        'publication_kind': 'a01_research_progress', 'scientific_review_status': 'review_required',
        'release_eligible': False, 'presentation': presentation}
