"""Explicit A01 progress-page exceptions to the preserved YouMind baseline.

This never grants scientific release or modifies the original baseline.
"""
from __future__ import annotations

import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path, PurePosixPath
import re

from public_literature_update import (MANIFEST as PRESENTATION_V24_PATH,
    predecessor_bytes as literature_predecessor_bytes, apply as apply_literature_presentation)

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
PRESENTATION_V12_SHA256 = 'aa9efd831558b47646b687e12be30724c4b8be89a0f98ccb8d06ef56cf04e81f'
PRESENTATION_V13_PATH = 'provenance/platform-presentation.v13.json'
PRESENTATION_V13_ID = 'PLATFORM-AI-DIRECT-RESULTS-20261114-v13'
PRESENTATION_V13_PREVIOUS_COMMIT = '858232daae36495e68645ae519441fd7d7a5a9d5'
PRESENTATION_V13_SHA256 = '263b465d22b1a56b8364a0540a65f742948664f9e50e64d759543685768468cc'
PRESENTATION_V14_PATH = 'provenance/platform-presentation.v14.json'
PRESENTATION_V14_ID = 'PLATFORM-REFERENCES-20261115-v14'
PRESENTATION_V14_PREVIOUS_COMMIT = 'f70a8e797a3fe4b70cf21d8f3b86dd679a59306d'
PRESENTATION_V14_SHA256 = '3ea28579d130b065fb805942c5c62861d8f6cd24a0027df7fef7cdc41415750b'
PRESENTATION_V15_PATH = 'provenance/platform-presentation.v15.json'
PRESENTATION_V15_ID = 'PLATFORM-A02-ACADEMIC-20261115-v15'
PRESENTATION_V15_PREVIOUS_COMMIT = '34c405e68a9ab8760d8c14dcb01fd212970d63ca'
A02_HISTORY_ROUTE = 'topics/fluoromonomers/index.html'
A02_HISTORY_CONTENT = 'content/a02-academic-achievements.v1.json'
A02_HISTORY_RENDERER = 'scripts/render_a02_history.py'
A02_HISTORY_DOCUMENT = 'docs/A02_ACADEMIC_ACHIEVEMENTS_zh-CN.md'
A02_ALLOWED_ROUTES = {A02_HISTORY_ROUTE, 'research/index.html', 'achievements/index.html'}
A02_PREDECESSOR_FILES = {
    'site/topics/fluoromonomers/index.html': ('780541f4a1762919c757a6be86b5551fb5ce0679d2778b8a9772d87fc70add94', 10553),
    'site/research/index.html': ('85374c976a94a3ff601e203633285418b8250262eab5eef2a627bb3de1e4b580', 46038),
    'content/ai-research-section.v1.json': ('adabfe9f1a1cd652d117f7b9fc852bd7499487a9aa8a3139bccb47150033c301', 62264),
    'docs/AI_RESEARCH_zh-CN.md': ('7b6429b44a452837b73b10195020028f6a1955b76bfe991ecd5d3ad17f7c339e', 32304),
    'scripts/public_line_labels.py': ('58ccc1c5103519d053d38c61a54039a953b55d0d1d12c5981b07c23071d11322', 9694),
    'scripts/check_site.py': ('5a1b5149d396cbd61b837bfd2679a82e2e8892af5dff5468add9448b371e18ae', 22749),
    'scripts/a01_publication_contract.py': ('7a4dc86795cd5af326c661afc311ac9b0807bb6d3a116e9e6eafabafc6aa3b38', 152291),
    'scripts/render_heritage.py': ('27601353b9e4ed3c1a2129074a7e6eb9e6e16598a01cc36207a0320f9a44dafb', 41039),
    'site/achievements/index.html': ('efb6d576b66c43dc697b4d492fb6eaf98c09b813adec7a12d0c952a1bf926ac0', 95440),
    'docs/ACADEMIC_ACHIEVEMENTS_zh-CN.md': ('8ea379f801fd15ffa8bc1829cc932e6273d97ffc38371d4b6a0fed53a4c4eadc', 69254),
}
A02_DOCUMENTS = (A02_HISTORY_CONTENT, A02_HISTORY_RENDERER, A02_HISTORY_DOCUMENT,
    'content/ai-research-section.v1.json', 'docs/AI_RESEARCH_zh-CN.md',
    'scripts/render_ai_research.py', 'scripts/public_line_labels.py',
    'scripts/check_site.py', 'scripts/a01_publication_contract.py',
    'scripts/render_heritage.py', 'docs/ACADEMIC_ACHIEVEMENTS_zh-CN.md')

PRESENTATION_V15_SHA256 = 'd21bad493ae97587c7b9493813af3393ed9ed98f5a8dfd3a8790270f7ba49aff'
PRESENTATION_V16_PATH = 'provenance/platform-presentation.v16.json'
PRESENTATION_V16_ID = 'PLATFORM-A02-TECHNICAL-RECORDS-20261115-v16'
PRESENTATION_V16_PREVIOUS_COMMIT = '366ab81f49876ee94d326cefce323211dd0367d9'
A02_TECHNICAL_PREDECESSOR_FILES = {'content/a02-academic-achievements.v1.json': ('bf61b6012fe680d86504d2c32fbee972aba43614142d984a4fe20b2d824aa873', 11791), 'scripts/render_a02_history.py': ('b4c45915fc6c9450295328af4c87f6bcbb58808712f53abee366199bf493689c', 11387), 'docs/A02_ACADEMIC_ACHIEVEMENTS_zh-CN.md': ('006f098820b64a59410fc7bac6fddd2fcd0cf4196d2312d1db2dfaba18712196', 9190), 'content/ai-research-section.v1.json': ('01a7d738e4f3ac0c9ca71435d2b2b8b61717f328464c9512c0b3e08a9026424b', 64135), 'docs/AI_RESEARCH_zh-CN.md': ('ca75548d71aeefab686868b3fef6b60d9249fada52f9d6ba530b1d25e3e0ee44', 33775), 'site/topics/fluoromonomers/index.html': ('b073b009f6b9adca2cc2b826d7da2de6778729299df345967f3125bdb73a3552', 18665), 'site/research/index.html': ('b9fb24b89ac3bdde30c8c46f9bcc8d19822490fe97c50f70361d3ac97d7bc77d', 47525), 'site/achievements/index.html': ('e6e2f4ee76e5cb26a80289d386e8a96659eba94b3f6f5ff35746b8c7c5dc055f', 95704), 'docs/ACADEMIC_ACHIEVEMENTS_zh-CN.md': ('d93f7d87d89d064595bb8ccbeb1681d023dd157432c29339d1759a77dbdbfb65', 69545), 'scripts/a01_publication_contract.py': ('fdbccd1ade3d883a253aaab7f27ac8d832053c7c023081bac18dc938b98fc6a7', 170495)}
A02_TECHNICAL_DOCUMENTS = A02_DOCUMENTS

PRESENTATION_V16_SHA256 = '6b975e980d176ecc481449ca5a96ffadadfecae2eb64d97dfdafb75b85b4a3c0'
PRESENTATION_V17_PATH = 'provenance/platform-presentation.v17.json'
PRESENTATION_V17_ID = 'PLATFORM-A02-TEAM-RECORDS-20261115-v17'
PRESENTATION_V17_PREVIOUS_COMMIT = '936ca1d990c0d3f695dd7281b1b01aaa07662a10'
A02_TEAM_PREDECESSOR_FILES = {
    'content/a02-academic-achievements.v1.json': ('79bc1cdfc8898a7e6c9e6615ca4cf6961d9ec05f1891ecf30f2531f5dc2f07c1', 23565),
    'scripts/render_a02_history.py': ('1b529caa86ad9240f376c63f29e67d67022b9ddaefe13aaa87fd88c21b090d1d', 15796),
    'docs/A02_ACADEMIC_ACHIEVEMENTS_zh-CN.md': ('f36d7ac151847c284c3ea2fd08f0816739d392a998b9c05f596c052a5cfb947d', 18023),
    'content/ai-research-section.v1.json': ('40d2e84da4fd6060f34b83fd8a15171acf3ce7cea22f2053d6fa23aa80afeb28', 65074),
    'docs/AI_RESEARCH_zh-CN.md': ('51f74114ec4434281a91beeebae0ece1eb3151aa189846e8b4aa90ceae65847c', 34544),
    'site/topics/fluoromonomers/index.html': ('40cfb1665973b58bec414fd65a6d6ede3a24444c513df5cab01671b0598ade19', 30347),
    'site/research/index.html': ('4137819f6c923b6cf2f7e5592f609705c8ac3ab62c513012ada1c2ed8f8303c5', 48320),
    'site/achievements/index.html': ('58367575451a3f7bb38b75d427af62bd11954d14d848603410f0fdb95a563753', 95787),
    'docs/ACADEMIC_ACHIEVEMENTS_zh-CN.md': ('8dfe0a92f4fd91af063dd907bf677e84db5e3f348d9a57acd6ac12ae9d4e4e97', 69628),
    'scripts/a01_publication_contract.py': ('292718663d46a8c80a57eeb8bc13b3586e5997883a92af1783dbc30d2b5ee1ce', 187171),
}
A02_TEAM_DOCUMENTS = A02_DOCUMENTS

PRESENTATION_V17_SHA256 = 'b635b2950e37d5387e8fb68da12109ca585833b769eec38cf25911eb86563ee1'
PRESENTATION_V18_PATH = 'provenance/platform-presentation.v18.json'
PRESENTATION_V18_ID = 'PLATFORM-A02-CITED-SOURCES-20261115-v18'
PRESENTATION_V18_PREVIOUS_COMMIT = '98e079c03d1d969bc69d0979deb29d921afd5bc2'
A02_SOURCE_TRACE_PREDECESSOR_FILES = {
    'content/a02-academic-achievements.v1.json': ('51c77cc96b4b9db06d695bc5ffdae311ffb2082048ec98adbbe98de9b0b078eb', 38173),
    'scripts/render_a02_history.py': ('47df27ddd51f676847e718a18dc8c57429ac743de13b95eb6eec8d8a5653be1d', 18491),
    'docs/A02_ACADEMIC_ACHIEVEMENTS_zh-CN.md': ('2fa00a8628b9d3d0af028e1472ca852119ad019710b4e846b6ce6b4423e593d8', 29258),
    'content/ai-research-section.v1.json': ('99cba00df70792791a76e50ff4deb7ad20cea58dfef7f6fc4446918cff256b75', 65891),
    'docs/AI_RESEARCH_zh-CN.md': ('c354182622f067853bf6b5b0d6310a6f81aa9f7615361a2febb5f9eb9b60107e', 35191),
    'site/topics/fluoromonomers/index.html': ('ab2ecad195b1cb610f97c5a1d6b2e77a1207cad9188e52b59569627cfddfe17b', 45066),
    'site/research/index.html': ('4b4db2f971bfed41f29325dd8e60313b3ec1dfce40caf743418c42955dd3e48c', 48993),
    'site/achievements/index.html': ('afab8c345bcceb12584ba7b3c00d15daf5f4a87a0eb6d1777e52ab719093755d', 95871),
    'docs/ACADEMIC_ACHIEVEMENTS_zh-CN.md': ('ae083f26ea6a5699f5443335569fb10f95d7a12db24c449489b9cead2fd30072', 69712),
    'scripts/a01_publication_contract.py': ('665aedd2071d06da0530a345aa454c37a5535172fb260fd1e2a3ee449a40698e', 204809),
}
A02_SOURCE_TRACE_DOCUMENTS = A02_DOCUMENTS

PRESENTATION_V18_SHA256 = '4fa6f43360d5343e119bb7b9e51e0671f1b4b4ef51ba065067459180a710dfd6'
PRESENTATION_V19_PATH = 'provenance/platform-presentation.v19.json'
PRESENTATION_V19_ID = 'PLATFORM-A02-ORIGINAL-FOLLOWUP-20261115-v19'
PRESENTATION_V19_PREVIOUS_COMMIT = 'b107b56d597c02230e4dc9365bc6d36411a989a8'
A02_ORIGINAL_FOLLOWUP_ROUTES = {'topics/fluoromonomers/index.html', 'research/index.html'}
A02_ORIGINAL_FOLLOWUP_PREDECESSOR_FILES = {
    'content/a02-academic-achievements.v1.json': ('2c60f209710ded6ec24f90a6170c0e721fcf1540f4bcbef0c29d492d9b6e69ef', 48818),
    'docs/A02_ACADEMIC_ACHIEVEMENTS_zh-CN.md': ('1209c6a935d402b09602b67be54a5c0f7086d00426f80c6c4971df0a3927cabe', 37328),
    'site/topics/fluoromonomers/index.html': ('caaecd0cf044617acf14e07dd8ac6b08fe9391b41506886bb66d6b513c2fb0dd', 55310),
    'content/ai-research-section.v1.json': ('2f3a63d3f431939b169877c4a40ddba867f1dd918e2a5d96b2cbd5f5f049870a', 66703),
    'docs/AI_RESEARCH_zh-CN.md': ('0ed766353417b7f70de17729d0d2876e7a12a0a6270e690ea587d77b14150aa0', 35833),
    'site/research/index.html': ('0e469bd1e8c4a1bb7d9e7d75cda1a9a728d404de77b64c31e3f714de3822a61f', 49661),
    'scripts/a01_publication_contract.py': ('90000776a713ff4cc0441efd52d9c54f6dce3fec5872d27867b1f2109a73efdc', 223315),
}
A02_ORIGINAL_FOLLOWUP_DOCUMENTS = A02_DOCUMENTS

PRESENTATION_V19_SHA256 = '1a056390024ec41126e36c8b8e6a5275415331ec6eeec524da9df8785e23d59b'
PRESENTATION_V20_PATH = 'provenance/platform-presentation.v20.json'
PRESENTATION_V20_ID = 'PLATFORM-A02-HOLDINGS-20261115-v20'
PRESENTATION_V20_PREVIOUS_COMMIT = '11a927d4c10cfbe0a94a394e8f3e5ba2fbb2cf00'
A02_HOLDINGS_ROUTES = {'topics/fluoromonomers/index.html', 'research/index.html'}
A02_HOLDINGS_PREDECESSOR_FILES = {
    'content/a02-academic-achievements.v1.json': ('38c157cd7b3246a5422ac7e44be6157001b9600425201872f129a7b989be4fa9', 52298),
    'docs/A02_ACADEMIC_ACHIEVEMENTS_zh-CN.md': ('0535f885654dd45e34e255fe7a2049530a0d5c14f2356e00680a9d4084c6ee33', 40250),
    'site/topics/fluoromonomers/index.html': ('dc4fd895c13fa819715542825469e808666016e2e1bb7532968c804bede02a6e', 58542),
    'content/ai-research-section.v1.json': ('3006f9133f0c59812468b177e86e55fc8d13d8e2fd92324bd9985f822ad3f930', 66752),
    'docs/AI_RESEARCH_zh-CN.md': ('03bbc0a90435473814efbaaad4c092b6f8ab7786db02bc32bade32b4e86cb68a', 35882),
    'site/research/index.html': ('8a20ce07055fd8207c1038599cc9ccb9baf9e46d8d76233fcb09d4a82024df27', 49710),
    'scripts/a01_publication_contract.py': ('ec97c60295ef2de87702805dfcf5d401e992caaf1a8fe5315db490ec8b1d7559', 241381),
}
A02_HOLDINGS_DOCUMENTS = A02_DOCUMENTS

REFERENCES_PREDECESSOR_FILES = {
    'README.md': ('3031d7cb2b65282f50d60c0dcac561a5c8f86e31497be2016e0875e5a61d11e7', 7366),
    'site/index.html': ('d9e96eb3dc370a9c076a1e0afbcc43b266a69491e63e11d421dc3d1c91698b19', 255067),
    'scripts/a01_publication_contract.py': ('5bfcdb7a612e842b9d9857f485c0ef96142de73f0ff80cd94fd2445fc103227a', 139962),
}
REFERENCES_DOCUMENTS = ('README.md', 'scripts/a01_publication_contract.py')
AI_RESEARCH_ROUTE = 'research/index.html'

PRESENTATION_V22_SHA256 = '3a9a746a565f7942899f5fdffc244121608e39210c7e6eb466203775dc38cae6'
PRESENTATION_V23_PATH = 'provenance/platform-presentation.v23.json'
PRESENTATION_V23_ID = 'PLATFORM-A06-AUTHORS-METHODS-20261116-v23'
PRESENTATION_V23_PREVIOUS_COMMIT = 'b663c63b84d1474d91faf5437f1d61202b8fa8c6'
A06_SUMMARY_ROUTES = {AI_RESEARCH_ROUTE}
A06_SUMMARY_PREDECESSOR_FILES = {'content/ai-research-section.v1.json': ('278647dbc24b3089da7878736d8a6160547b7080d8d99bd2cdbdebd9f0c38e3a', 68858), 'docs/AI_RESEARCH_zh-CN.md': ('b6c2f2d7f84de97cfb22020be553d332b8ed6dd83566c2ec3fe492a495c44d4b', 37877), 'site/research/index.html': ('4427a6cb2adedf7761bf22308cec33bf27d45209f1ecb2f12b4cfb9f0f91e3a7', 51716), 'scripts/a01_publication_contract.py': ('dcf906fa4f6041f418978073e84f76a165ec2ad96c333116259a6b246badf2d8', 294741)}
A06_SUMMARY_DOCUMENTS = ('content/ai-research-section.v1.json', 'scripts/render_ai_research.py', 'docs/AI_RESEARCH_zh-CN.md', 'scripts/a01_publication_contract.py')
A06_SUMMARY_TEXT = '已取得并核读1982年337–352页、670–673页及1983年1044–1057页三篇原刊。首篇署陈庆云、朱蓉仙、李宗珍、王珊娣、黄维垣，后两篇分别署陈庆云、朱士正，作者表各自登记。CQ-H16主标题原印为“全氟和多氟烷基磺酸的研究 X.”，与既有题录“磺酸酯”异文分列；670页通讯未印系列号。原刊作者名与传记异文保留，不据署名推定个人分工。结构、谱图及断键解释仍待专业核校。按既有方法核读登记，2003年硅酯／二氟卡宾方法与2010年甲酯／甾体三氟甲基化分别呈现；原刊提交者与核查者名单不属于本项目新取得的专业签认。1989、2000原论文及1991书章全文仍待取得，2024既有陈试剂机理计算仍归原作者。'


PRESENTATION_V21_SHA256 = 'a353a25fc9586c3fe78de1ad42a20aee4a1c980de59eda4340df4466d9b45593'
PRESENTATION_V22_PATH = 'provenance/platform-presentation.v22.json'
PRESENTATION_V22_ID = 'PLATFORM-ORIGINAL-EVIDENCE-20261116-v22'
PRESENTATION_V22_PREVIOUS_COMMIT = 'e6b42738e5523c31533e72f3af46289bdcc18028'
ORIGINAL_EVIDENCE_ROUTES = {AI_RESEARCH_ROUTE}
ORIGINAL_EVIDENCE_PREDECESSOR_FILES = {'content/ai-research-section.v1.json': ('d3af3ed21cf929b55099b799628e8f224b033be332dbcb4e0d999cf1308ea320', 66871), 'docs/AI_RESEARCH_zh-CN.md': ('99efc0bebe93fc34e4a5953a78db9105271b4e7b08ef8a7af5acf54c687ce674', 36001), 'site/research/index.html': ('55ae69b829c8463f81369be6476f4fb2eb80c9380521e23f2c796a87517b3bd5', 49829), 'scripts/a01_publication_contract.py': ('bd7344b83a58d64f00e7c49eadaa36829770ace5051c4a16ea977499c3ce9dee', 275315)}
ORIGINAL_EVIDENCE_DOCUMENTS = ('content/ai-research-section.v1.json', 'scripts/render_ai_research.py', 'docs/AI_RESEARCH_zh-CN.md', 'scripts/a01_publication_contract.py')
ORIGINAL_EVIDENCE_UPDATES = {'A03': {'summary': '已按1966年原表转录10个波长记录，其中9个配对记录形成6项位移；波长差、波数蓝移与有界扰动诊断属于同批原表数值重放。原刊印刷21页表1及24页实验部分已回查：紫外仪器为Unicam SP-500；20°C注明于核磁共振测量，不能移作紫外温度。紫外测量条件与真实不确定度仍未完整确认，专业转录签认待补。', 'appended_links': [{'title': '1966原刊：表1见印刷21页，仪器见24页', 'url': 'https://sioc-journal.cn/Jwk_hxxb/CN/Y1966/V32/I1/18', 'kind': 'external'}]}, 'A04': {'summary': '已取得并核读1979年《全氟和多氟烷基磺酸的研究 II. 一些多氟烷基醚磺酸的合成》原刊315–324页，324页为同篇英文摘要，署名“全氟磺酸组”。323页致谢记载所内质谱组及上海医药工业研究院核磁组的分析协作。1977年前报和1978年Scientia Sinica原文仍待取得；机构合作登记、论文集体署名与个人分工分别保存，未据此认定个人贡献或完成厂试验证。', 'next_step': '继续追查1977／1978原刊及厂试／扩试原表；将原刊分析协作、机构合作与个人分工按不同证据层级核对。'}, 'A05': {'summary': '已取得并核读1978年《五氟氯乙烷合成简法》77–79页，集体署名“致冷剂小组”，对象为F-115，不能混作1978年F-53论文。另已取得CN1075708A、CN1308043A两项团队工艺专利说明书，发明人分别为林永达／梁与达、吴永明／林永达，不能改列陈庆云个人专利。配套润滑油、原中试及整机试用原表仍待取得；本平台未新增实验或工艺验证。', 'next_step': '优先取得配套润滑油两篇全文与中试／整机原表，核对团队专利技术对象和历史底物指代；不以新取得文件代替工艺验证。'}, 'A06': {'summary': '已取得并核读1982年337–352页、670–673页及1983年1044–1057页三篇原刊。CQ-H16主标题原印为“全氟和多氟烷基磺酸的研究 X.”，与既有题录“磺酸酯”异文分列；670页通讯未印系列号。原刊作者名与传记异文保留，不据署名推定个人分工。结构、谱图及断键解释仍待专业核校。2003／2010方法核查记录保留；1989、2000原论文及1991书章全文仍待取得，2024既有陈试剂机理计算仍归原作者。', 'next_step': '先核三篇原刊的结构、实验条件及姓名异文，再追1989、2000全文与1991书章；原作者的可能机制保留为原作者解释。'}, 'A07': {'summary': '1999与2001年论文的31页、26页SI已取得，已核首页身份；正文仍待取得，全部谱图与机理证据未完成专业核校。申请200510031063.4的CN1752059A与CN1298686C两份说明书已取得，属同一申请的公开／授权版本，陈庆云、曹海萍为共同发明人；版本与技术内容仍待核，不据此判断当前法律状态。摘要中的SET解释不作为平台机制认证。', 'next_step': '优先取两篇正文并核全套SI的谱图与底物对应，区分同一专利的版本；原始应用档案仍待补。'}, 'A08': {'summary': '2003年SI两卷（40＋1页）、2007年13页SI及4份CIF、2022年55页SI，以及晚年三项研究的66／129／11页附件已取得，各篇正文仍待取得。2022年附件S15–S21与S38起已有原作者计算说明及结果，不能把未来AI补算称作首次理论研究，也不能据合著推定陈先生本人完成计算。这些附件目前仅完成文件身份及选定页／字段核对，全套结构、谱图和计算仍待专业核校；文件取得不等于结构、物性或机理认证。', 'next_step': '优先取得对应正文，核对各卷SI及CIF与论文对象的对应关系；先比较既有理论研究，专业核校后再评估未来问题。'}}


PRESENTATION_V20_SHA256 = '34814fabc405812bccc433018f8a197d181a3da9ac617f84cceda51513774b72'
PRESENTATION_V21_PATH = 'provenance/platform-presentation.v21.json'
PRESENTATION_V21_ID = 'PLATFORM-A02-EVIDENCE-BOUNDARY-20261116-v21'
PRESENTATION_V21_PREVIOUS_COMMIT = '7a53bc6d6afcb9b0ea3f3d01ca1bf862cfa84b57'
A02_BOUNDARY_ROUTES = {A02_HISTORY_ROUTE, AI_RESEARCH_ROUTE}
A02_BOUNDARY_PREDECESSOR_FILES = {'content/a02-academic-achievements.v1.json': ('520e16d611f15f08519fa94e1857b0ad4b044b63799648b41ff675551c1c0617', 54017), 'docs/A02_ACADEMIC_ACHIEVEMENTS_zh-CN.md': ('20ec5748a84267ebb773e62c3574f40393c0f9fc6d7b2ae31c826545bb8d6396', 41445), 'site/topics/fluoromonomers/index.html': ('8108f9a3674b61fecb4f2a1a6fb71b2b1a95745eff95bb243d9f5d27a9160f46', 59881), 'content/ai-research-section.v1.json': ('f27d998f4274f2202efcd4a036311c6c8cd1fff3b8a13b3e56512354a2d18aaf', 66739), 'docs/AI_RESEARCH_zh-CN.md': ('1ba9ed4363b1080b6dc51cd568a080fdf44b6f9ff5b3c25247dccacea7ef9704', 35869), 'site/research/index.html': ('c6817f7bea64843a36e21009aa3997feaf57e315fccd7b3e1a5e9e6abaf98223', 49697), 'scripts/a01_publication_contract.py': ('169e46ad2bb8cbaafeb93599b66e5268e5d351533cdfb12d1c5278de1d51bf99', 260043)}
A02_BOUNDARY_DOCUMENTS = A02_DOCUMENTS
A02_BOUNDARY_FINDING = '四氯化碳体系中，分馏、¹⁹F NMR及脱氯化氢反应支持主要单加成结构CCl₃CH₂CF₂Cl；过渡馏分的弱峰被作者解释为可能含极少量反向异构体。全氟叔丁基碘体系的主要结构(CF₃)₃CCH₂CF₂I由元素分析、光谱分析及化学转化等证据归属。'
A02_BOUNDARY_LOCATOR = 'p.176–177；p.179实验'
A02_BOUNDARY_AI_SUMMARY = '已分开材料牌号、两类调聚产物和不同氟油；保留原刊中文摘要与正文胺名等异文，并把少量反向异构体线索限定于四氯化碳体系的过渡馏分。尚未开展本线复算、量化计算、实验或材料性能验证。'
A02_BOUNDARY_AI_LIMIT = '原刊支持主要加成方向；四氯化碳体系过渡馏分的弱峰是作者保留极少量反向异构体可能性的依据，不把该线索推广至两类体系。原作者的极性解释不作平台机制确认，乳化用途也不升级为定量性能或环境安全结论。'

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
AI_RESULTS_PREDECESSOR_FILES = {
    'site/research/index.html': ('634bcb1657be0186a534857501c15d23dd5b9660b28f48465c4019ea7be72739', 24464),
    'content/ai-research-section.v1.json': ('2740f58d7579d73edc9dbebb392f21fc03f21507e0e28584826dfd8d406aba79', 22553),
    'scripts/render_ai_research.py': ('793d13a52ccfdcf8d939d2468d29ab2ee50ce3a972898e722a9dd7103f7e959a', 25962),
    'docs/AI_RESEARCH_zh-CN.md': ('3622e6ca97af8fce5581b86ff449308f0198c0679f1de2cdff1a7d1de1391a4e', 17305),
    'scripts/a01_publication_contract.py': ('50da7b0b377ae7dd08a4bcd5ecb44cc98f8bcf0df21dd30c61ded534f44cb38d', 125747),
}
AI_RESULTS_DOCUMENTS = (AI_RESEARCH_CONTENT, AI_RESEARCH_RENDERER,
    AI_RESEARCH_DOCUMENT, 'scripts/a01_publication_contract.py')
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


def a06_summary_predecessor_bytes(root: Path, name: str) -> bytes:
    """Undo only the four explicitly permitted v23 presentation files."""
    current = literature_predecessor_bytes(root, name)
    if not (root/PRESENTATION_V23_PATH).exists():
        return current
    data = read_json(project_file(root, PRESENTATION_V23_PATH))
    if not isinstance(data, dict):
        raise ValueError('A06 summary presentation must be a JSON object')
    files, pool = data.get('reversible_text_files'), data.get('reverse_text_patch_pool')
    if not isinstance(files, list) or not isinstance(pool, list):
        raise ValueError('A06 summary require exact reversible text patch records')
    matches = [row for row in files if isinstance(row, dict) and row.get('path') == name]
    if not matches:
        return current
    if len(matches) != 1 or name not in A06_SUMMARY_PREDECESSOR_FILES:
        raise ValueError('Unauthorized or duplicate A06 summary predecessor record: '+name)
    record = matches[0]; old_sha, old_size = A06_SUMMARY_PREDECESSOR_FILES[name]
    if (record.get('old_sha256') != old_sha or record.get('old_bytes') != old_size
            or hashlib.sha256(current).hexdigest() != record.get('new_sha256')
            or len(current) != record.get('new_bytes')):
        raise ValueError('A06 summary file differs from its complete old/new identities: '+name)
    edits = record.get('edits')
    if not isinstance(edits, list) or not edits:
        raise ValueError('A06 summary changes require nonempty text edits: '+name)
    chunks, cursor, old_end, delta = [], 0, 0, 0
    for edit in edits:
        if not isinstance(edit, dict) or set(edit) != {'old_offset', 'replacement'}:
            raise ValueError('Invalid reversible A06 summary text edit: '+name)
        offset, replacement = edit['old_offset'], edit['replacement']
        if (type(offset) is not int or offset < old_end or type(replacement) is not int
                or not 0 <= replacement < len(pool)):
            raise ValueError('Overlapping or invalid A06 summary text edit: '+name)
        pair = pool[replacement]
        if (not isinstance(pair, dict) or set(pair) != {'old', 'new'}
                or not all(isinstance(pair.get(key), str) for key in ('old', 'new'))
                or pair['old'] == pair['new']):
            raise ValueError('Invalid A06 summary text replacement pool')
        before, after = pair['old'].encode('utf-8'), pair['new'].encode('utf-8')
        position = offset+delta
        if position < cursor or current[position:position+len(after)] != after:
            raise ValueError('A06 summary replacement differs at its exact offset: '+name)
        chunks.extend((current[cursor:position], before))
        cursor, old_end = position+len(after), offset+len(before)
        delta += len(after)-len(before)
    rebuilt = b''.join((*chunks, current[cursor:]))
    if hashlib.sha256(rebuilt).hexdigest() != old_sha or len(rebuilt) != old_size:
        raise ValueError('A06 summary predecessor cannot be reconstructed exactly: '+name)
    return rebuilt




def original_evidence_predecessor_bytes(root: Path, name: str) -> bytes:
    """Undo only the four explicitly permitted v22 presentation files."""
    current = a06_summary_predecessor_bytes(root, name)
    if not (root/PRESENTATION_V22_PATH).exists():
        return current
    data = read_json(project_file(root, PRESENTATION_V22_PATH))
    if not isinstance(data, dict):
        raise ValueError('Original evidence presentation must be a JSON object')
    files, pool = data.get('reversible_text_files'), data.get('reverse_text_patch_pool')
    if not isinstance(files, list) or not isinstance(pool, list):
        raise ValueError('Original evidence require exact reversible text patch records')
    matches = [row for row in files if isinstance(row, dict) and row.get('path') == name]
    if not matches:
        return current
    if len(matches) != 1 or name not in ORIGINAL_EVIDENCE_PREDECESSOR_FILES:
        raise ValueError('Unauthorized or duplicate Original evidence predecessor record: '+name)
    record = matches[0]; old_sha, old_size = ORIGINAL_EVIDENCE_PREDECESSOR_FILES[name]
    if (record.get('old_sha256') != old_sha or record.get('old_bytes') != old_size
            or hashlib.sha256(current).hexdigest() != record.get('new_sha256')
            or len(current) != record.get('new_bytes')):
        raise ValueError('Original evidence file differs from its complete old/new identities: '+name)
    edits = record.get('edits')
    if not isinstance(edits, list) or not edits:
        raise ValueError('Original evidence changes require nonempty text edits: '+name)
    chunks, cursor, old_end, delta = [], 0, 0, 0
    for edit in edits:
        if not isinstance(edit, dict) or set(edit) != {'old_offset', 'replacement'}:
            raise ValueError('Invalid reversible Original evidence text edit: '+name)
        offset, replacement = edit['old_offset'], edit['replacement']
        if (type(offset) is not int or offset < old_end or type(replacement) is not int
                or not 0 <= replacement < len(pool)):
            raise ValueError('Overlapping or invalid Original evidence text edit: '+name)
        pair = pool[replacement]
        if (not isinstance(pair, dict) or set(pair) != {'old', 'new'}
                or not all(isinstance(pair.get(key), str) for key in ('old', 'new'))
                or pair['old'] == pair['new']):
            raise ValueError('Invalid Original evidence text replacement pool')
        before, after = pair['old'].encode('utf-8'), pair['new'].encode('utf-8')
        position = offset+delta
        if position < cursor or current[position:position+len(after)] != after:
            raise ValueError('Original evidence replacement differs at its exact offset: '+name)
        chunks.extend((current[cursor:position], before))
        cursor, old_end = position+len(after), offset+len(before)
        delta += len(after)-len(before)
    rebuilt = b''.join((*chunks, current[cursor:]))
    if hashlib.sha256(rebuilt).hexdigest() != old_sha or len(rebuilt) != old_size:
        raise ValueError('Original evidence predecessor cannot be reconstructed exactly: '+name)
    return rebuilt




def boundary_predecessor_bytes(root: Path, name: str) -> bytes:
    """Undo only the seven explicitly permitted v21 presentation files."""
    current = original_evidence_predecessor_bytes(root, name)
    if not (root/PRESENTATION_V21_PATH).exists():
        return current
    data = read_json(project_file(root, PRESENTATION_V21_PATH))
    if not isinstance(data, dict):
        raise ValueError('A02 evidence-boundary presentation must be a JSON object')
    files, pool = data.get('reversible_text_files'), data.get('reverse_text_patch_pool')
    if not isinstance(files, list) or not isinstance(pool, list):
        raise ValueError('A02 evidence-boundary require exact reversible text patch records')
    matches = [row for row in files if isinstance(row, dict) and row.get('path') == name]
    if not matches:
        return current
    if len(matches) != 1 or name not in A02_BOUNDARY_PREDECESSOR_FILES:
        raise ValueError('Unauthorized or duplicate A02 evidence-boundary predecessor record: '+name)
    record = matches[0]; old_sha, old_size = A02_BOUNDARY_PREDECESSOR_FILES[name]
    if (record.get('old_sha256') != old_sha or record.get('old_bytes') != old_size
            or hashlib.sha256(current).hexdigest() != record.get('new_sha256')
            or len(current) != record.get('new_bytes')):
        raise ValueError('A02 evidence-boundary file differs from its complete old/new identities: '+name)
    edits = record.get('edits')
    if not isinstance(edits, list) or not edits:
        raise ValueError('A02 evidence-boundary changes require nonempty text edits: '+name)
    chunks, cursor, old_end, delta = [], 0, 0, 0
    for edit in edits:
        if not isinstance(edit, dict) or set(edit) != {'old_offset', 'replacement'}:
            raise ValueError('Invalid reversible A02 evidence-boundary text edit: '+name)
        offset, replacement = edit['old_offset'], edit['replacement']
        if (type(offset) is not int or offset < old_end or type(replacement) is not int
                or not 0 <= replacement < len(pool)):
            raise ValueError('Overlapping or invalid A02 evidence-boundary text edit: '+name)
        pair = pool[replacement]
        if (not isinstance(pair, dict) or set(pair) != {'old', 'new'}
                or not all(isinstance(pair.get(key), str) for key in ('old', 'new'))
                or pair['old'] == pair['new']):
            raise ValueError('Invalid A02 evidence-boundary text replacement pool')
        before, after = pair['old'].encode('utf-8'), pair['new'].encode('utf-8')
        position = offset+delta
        if position < cursor or current[position:position+len(after)] != after:
            raise ValueError('A02 evidence-boundary replacement differs at its exact offset: '+name)
        chunks.extend((current[cursor:position], before))
        cursor, old_end = position+len(after), offset+len(before)
        delta += len(after)-len(before)
    rebuilt = b''.join((*chunks, current[cursor:]))
    if hashlib.sha256(rebuilt).hexdigest() != old_sha or len(rebuilt) != old_size:
        raise ValueError('A02 evidence-boundary predecessor cannot be reconstructed exactly: '+name)
    return rebuilt




def holdings_predecessor_bytes(root: Path, name: str) -> bytes:
    """Undo only the seven explicitly permitted v20 presentation files."""
    current = boundary_predecessor_bytes(root, name)
    if not (root/PRESENTATION_V20_PATH).exists():
        return current
    data = read_json(project_file(root, PRESENTATION_V20_PATH))
    if not isinstance(data, dict):
        raise ValueError('A02 holdings presentation must be a JSON object')
    files, pool = data.get('reversible_text_files'), data.get('reverse_text_patch_pool')
    if not isinstance(files, list) or not isinstance(pool, list):
        raise ValueError('A02 holdings require exact reversible text patch records')
    matches = [row for row in files if isinstance(row, dict) and row.get('path') == name]
    if not matches:
        return current
    if len(matches) != 1 or name not in A02_HOLDINGS_PREDECESSOR_FILES:
        raise ValueError('Unauthorized or duplicate A02 holdings predecessor record: '+name)
    record = matches[0]; old_sha, old_size = A02_HOLDINGS_PREDECESSOR_FILES[name]
    if (record.get('old_sha256') != old_sha or record.get('old_bytes') != old_size
            or hashlib.sha256(current).hexdigest() != record.get('new_sha256')
            or len(current) != record.get('new_bytes')):
        raise ValueError('A02 holdings file differs from its complete old/new identities: '+name)
    edits = record.get('edits')
    if not isinstance(edits, list) or not edits:
        raise ValueError('A02 holdings changes require nonempty text edits: '+name)
    chunks, cursor, old_end, delta = [], 0, 0, 0
    for edit in edits:
        if not isinstance(edit, dict) or set(edit) != {'old_offset', 'replacement'}:
            raise ValueError('Invalid reversible A02 holdings text edit: '+name)
        offset, replacement = edit['old_offset'], edit['replacement']
        if (type(offset) is not int or offset < old_end or type(replacement) is not int
                or not 0 <= replacement < len(pool)):
            raise ValueError('Overlapping or invalid A02 holdings text edit: '+name)
        pair = pool[replacement]
        if (not isinstance(pair, dict) or set(pair) != {'old', 'new'}
                or not all(isinstance(pair.get(key), str) for key in ('old', 'new'))
                or pair['old'] == pair['new']):
            raise ValueError('Invalid A02 holdings text replacement pool')
        before, after = pair['old'].encode('utf-8'), pair['new'].encode('utf-8')
        position = offset+delta
        if position < cursor or current[position:position+len(after)] != after:
            raise ValueError('A02 holdings replacement differs at its exact offset: '+name)
        chunks.extend((current[cursor:position], before))
        cursor, old_end = position+len(after), offset+len(before)
        delta += len(after)-len(before)
    rebuilt = b''.join((*chunks, current[cursor:]))
    if hashlib.sha256(rebuilt).hexdigest() != old_sha or len(rebuilt) != old_size:
        raise ValueError('A02 holdings predecessor cannot be reconstructed exactly: '+name)
    return rebuilt



def holdings_predecessor_binding(root: Path, name: str) -> dict:
    content = holdings_predecessor_bytes(root, name)
    return {'path': name, 'sha256': hashlib.sha256(content).hexdigest(), 'bytes': len(content)}


def original_followup_predecessor_bytes(root: Path, name: str) -> bytes:
    """Undo only the seven explicitly permitted v19 presentation files."""
    current = holdings_predecessor_bytes(root, name)
    if not (root/PRESENTATION_V19_PATH).exists():
        return current
    data = read_json(project_file(root, PRESENTATION_V19_PATH))
    if not isinstance(data, dict):
        raise ValueError('A02 original-followup presentation must be a JSON object')
    files, pool = data.get('reversible_text_files'), data.get('reverse_text_patch_pool')
    if not isinstance(files, list) or not isinstance(pool, list):
        raise ValueError('A02 original-followup require exact reversible text patch records')
    matches = [row for row in files if isinstance(row, dict) and row.get('path') == name]
    if not matches:
        return current
    if len(matches) != 1 or name not in A02_ORIGINAL_FOLLOWUP_PREDECESSOR_FILES:
        raise ValueError('Unauthorized or duplicate A02 original-followup predecessor record: '+name)
    record = matches[0]; old_sha, old_size = A02_ORIGINAL_FOLLOWUP_PREDECESSOR_FILES[name]
    if (record.get('old_sha256') != old_sha or record.get('old_bytes') != old_size
            or hashlib.sha256(current).hexdigest() != record.get('new_sha256')
            or len(current) != record.get('new_bytes')):
        raise ValueError('A02 original-followup file differs from its complete old/new identities: '+name)
    edits = record.get('edits')
    if not isinstance(edits, list) or not edits:
        raise ValueError('A02 original-followup changes require nonempty text edits: '+name)
    chunks, cursor, old_end, delta = [], 0, 0, 0
    for edit in edits:
        if not isinstance(edit, dict) or set(edit) != {'old_offset', 'replacement'}:
            raise ValueError('Invalid reversible A02 original-followup text edit: '+name)
        offset, replacement = edit['old_offset'], edit['replacement']
        if (type(offset) is not int or offset < old_end or type(replacement) is not int
                or not 0 <= replacement < len(pool)):
            raise ValueError('Overlapping or invalid A02 original-followup text edit: '+name)
        pair = pool[replacement]
        if (not isinstance(pair, dict) or set(pair) != {'old', 'new'}
                or not all(isinstance(pair.get(key), str) for key in ('old', 'new'))
                or pair['old'] == pair['new']):
            raise ValueError('Invalid A02 original-followup text replacement pool')
        before, after = pair['old'].encode('utf-8'), pair['new'].encode('utf-8')
        position = offset+delta
        if position < cursor or current[position:position+len(after)] != after:
            raise ValueError('A02 original-followup replacement differs at its exact offset: '+name)
        chunks.extend((current[cursor:position], before))
        cursor, old_end = position+len(after), offset+len(before)
        delta += len(after)-len(before)
    rebuilt = b''.join((*chunks, current[cursor:]))
    if hashlib.sha256(rebuilt).hexdigest() != old_sha or len(rebuilt) != old_size:
        raise ValueError('A02 original-followup predecessor cannot be reconstructed exactly: '+name)
    return rebuilt



def original_followup_predecessor_binding(root: Path, name: str) -> dict:
    content = original_followup_predecessor_bytes(root, name)
    return {'path': name, 'sha256': hashlib.sha256(content).hexdigest(), 'bytes': len(content)}


def trace_predecessor_bytes(root: Path, name: str) -> bytes:
    """Undo only the ten explicitly permitted v18 presentation files."""
    current = original_followup_predecessor_bytes(root, name)
    if not (root/PRESENTATION_V18_PATH).exists():
        return current
    data = read_json(project_file(root, PRESENTATION_V18_PATH))
    if not isinstance(data, dict):
        raise ValueError('A02 source-trace presentation must be a JSON object')
    files, pool = data.get('reversible_text_files'), data.get('reverse_text_patch_pool')
    if not isinstance(files, list) or not isinstance(pool, list):
        raise ValueError('A02 source-trace require exact reversible text patch records')
    matches = [row for row in files if isinstance(row, dict) and row.get('path') == name]
    if not matches:
        return current
    if len(matches) != 1 or name not in A02_SOURCE_TRACE_PREDECESSOR_FILES:
        raise ValueError('Unauthorized or duplicate A02 source-trace predecessor record: '+name)
    record = matches[0]; old_sha, old_size = A02_SOURCE_TRACE_PREDECESSOR_FILES[name]
    if (record.get('old_sha256') != old_sha or record.get('old_bytes') != old_size
            or hashlib.sha256(current).hexdigest() != record.get('new_sha256')
            or len(current) != record.get('new_bytes')):
        raise ValueError('A02 source-trace file differs from its complete old/new identities: '+name)
    edits = record.get('edits')
    if not isinstance(edits, list) or not edits:
        raise ValueError('A02 source-trace changes require nonempty text edits: '+name)
    chunks, cursor, old_end, delta = [], 0, 0, 0
    for edit in edits:
        if not isinstance(edit, dict) or set(edit) != {'old_offset', 'replacement'}:
            raise ValueError('Invalid reversible A02 source-trace text edit: '+name)
        offset, replacement = edit['old_offset'], edit['replacement']
        if (type(offset) is not int or offset < old_end or type(replacement) is not int
                or not 0 <= replacement < len(pool)):
            raise ValueError('Overlapping or invalid A02 source-trace text edit: '+name)
        pair = pool[replacement]
        if (not isinstance(pair, dict) or set(pair) != {'old', 'new'}
                or not all(isinstance(pair.get(key), str) for key in ('old', 'new'))
                or pair['old'] == pair['new']):
            raise ValueError('Invalid A02 source-trace text replacement pool')
        before, after = pair['old'].encode('utf-8'), pair['new'].encode('utf-8')
        position = offset+delta
        if position < cursor or current[position:position+len(after)] != after:
            raise ValueError('A02 source-trace replacement differs at its exact offset: '+name)
        chunks.extend((current[cursor:position], before))
        cursor, old_end = position+len(after), offset+len(before)
        delta += len(after)-len(before)
    rebuilt = b''.join((*chunks, current[cursor:]))
    if hashlib.sha256(rebuilt).hexdigest() != old_sha or len(rebuilt) != old_size:
        raise ValueError('A02 source-trace predecessor cannot be reconstructed exactly: '+name)
    return rebuilt



def trace_predecessor_binding(root: Path, name: str) -> dict:
    content = trace_predecessor_bytes(root, name)
    return {'path': name, 'sha256': hashlib.sha256(content).hexdigest(), 'bytes': len(content)}


def team_predecessor_bytes(root: Path, name: str) -> bytes:
    """Undo only the ten explicitly permitted v17 presentation files."""
    current = trace_predecessor_bytes(root, name)
    if not (root/PRESENTATION_V17_PATH).exists():
        return current
    data = read_json(project_file(root, PRESENTATION_V17_PATH))
    if not isinstance(data, dict):
        raise ValueError('A02 team presentation must be a JSON object')
    files, pool = data.get('reversible_text_files'), data.get('reverse_text_patch_pool')
    if not isinstance(files, list) or not isinstance(pool, list):
        raise ValueError('A02 team require exact reversible text patch records')
    matches = [row for row in files if isinstance(row, dict) and row.get('path') == name]
    if not matches:
        return current
    if len(matches) != 1 or name not in A02_TEAM_PREDECESSOR_FILES:
        raise ValueError('Unauthorized or duplicate A02 team predecessor record: '+name)
    record = matches[0]; old_sha, old_size = A02_TEAM_PREDECESSOR_FILES[name]
    if (record.get('old_sha256') != old_sha or record.get('old_bytes') != old_size
            or hashlib.sha256(current).hexdigest() != record.get('new_sha256')
            or len(current) != record.get('new_bytes')):
        raise ValueError('A02 team file differs from its complete old/new identities: '+name)
    edits = record.get('edits')
    if not isinstance(edits, list) or not edits:
        raise ValueError('A02 team changes require nonempty text edits: '+name)
    chunks, cursor, old_end, delta = [], 0, 0, 0
    for edit in edits:
        if not isinstance(edit, dict) or set(edit) != {'old_offset', 'replacement'}:
            raise ValueError('Invalid reversible A02 team text edit: '+name)
        offset, replacement = edit['old_offset'], edit['replacement']
        if (type(offset) is not int or offset < old_end or type(replacement) is not int
                or not 0 <= replacement < len(pool)):
            raise ValueError('Overlapping or invalid A02 team text edit: '+name)
        pair = pool[replacement]
        if (not isinstance(pair, dict) or set(pair) != {'old', 'new'}
                or not all(isinstance(pair.get(key), str) for key in ('old', 'new'))
                or pair['old'] == pair['new']):
            raise ValueError('Invalid A02 team text replacement pool')
        before, after = pair['old'].encode('utf-8'), pair['new'].encode('utf-8')
        position = offset+delta
        if position < cursor or current[position:position+len(after)] != after:
            raise ValueError('A02 team replacement differs at its exact offset: '+name)
        chunks.extend((current[cursor:position], before))
        cursor, old_end = position+len(after), offset+len(before)
        delta += len(after)-len(before)
    rebuilt = b''.join((*chunks, current[cursor:]))
    if hashlib.sha256(rebuilt).hexdigest() != old_sha or len(rebuilt) != old_size:
        raise ValueError('A02 team predecessor cannot be reconstructed exactly: '+name)
    return rebuilt



def team_predecessor_binding(root: Path, name: str) -> dict:
    content = team_predecessor_bytes(root, name)
    return {'path': name, 'sha256': hashlib.sha256(content).hexdigest(), 'bytes': len(content)}


def technical_predecessor_bytes(root: Path, name: str) -> bytes:
    """Undo only the ten explicitly permitted v16 presentation files."""
    current = team_predecessor_bytes(root, name)
    if not (root/PRESENTATION_V16_PATH).exists():
        return current
    data = read_json(project_file(root, PRESENTATION_V16_PATH))
    if not isinstance(data, dict):
        raise ValueError('A02 technical presentation must be a JSON object')
    files, pool = data.get('reversible_text_files'), data.get('reverse_text_patch_pool')
    if not isinstance(files, list) or not isinstance(pool, list):
        raise ValueError('A02 technical require exact reversible text patch records')
    matches = [row for row in files if isinstance(row, dict) and row.get('path') == name]
    if not matches:
        return current
    if len(matches) != 1 or name not in A02_TECHNICAL_PREDECESSOR_FILES:
        raise ValueError('Unauthorized or duplicate A02 technical predecessor record: '+name)
    record = matches[0]; old_sha, old_size = A02_TECHNICAL_PREDECESSOR_FILES[name]
    if (record.get('old_sha256') != old_sha or record.get('old_bytes') != old_size
            or hashlib.sha256(current).hexdigest() != record.get('new_sha256')
            or len(current) != record.get('new_bytes')):
        raise ValueError('A02 technical file differs from its complete old/new identities: '+name)
    edits = record.get('edits')
    if not isinstance(edits, list) or not edits:
        raise ValueError('A02 technical changes require nonempty text edits: '+name)
    chunks, cursor, old_end, delta = [], 0, 0, 0
    for edit in edits:
        if not isinstance(edit, dict) or set(edit) != {'old_offset', 'replacement'}:
            raise ValueError('Invalid reversible A02 technical text edit: '+name)
        offset, replacement = edit['old_offset'], edit['replacement']
        if (type(offset) is not int or offset < old_end or type(replacement) is not int
                or not 0 <= replacement < len(pool)):
            raise ValueError('Overlapping or invalid A02 technical text edit: '+name)
        pair = pool[replacement]
        if (not isinstance(pair, dict) or set(pair) != {'old', 'new'}
                or not all(isinstance(pair.get(key), str) for key in ('old', 'new'))
                or pair['old'] == pair['new']):
            raise ValueError('Invalid A02 technical text replacement pool')
        before, after = pair['old'].encode('utf-8'), pair['new'].encode('utf-8')
        position = offset+delta
        if position < cursor or current[position:position+len(after)] != after:
            raise ValueError('A02 technical replacement differs at its exact offset: '+name)
        chunks.extend((current[cursor:position], before))
        cursor, old_end = position+len(after), offset+len(before)
        delta += len(after)-len(before)
    rebuilt = b''.join((*chunks, current[cursor:]))
    if hashlib.sha256(rebuilt).hexdigest() != old_sha or len(rebuilt) != old_size:
        raise ValueError('A02 technical predecessor cannot be reconstructed exactly: '+name)
    return rebuilt



def technical_predecessor_binding(root: Path, name: str) -> dict:
    content = technical_predecessor_bytes(root, name)
    return {'path': name, 'sha256': hashlib.sha256(content).hexdigest(), 'bytes': len(content)}


def a02_predecessor_bytes(root: Path, name: str) -> bytes:
    """Undo only the ten explicitly permitted v15 presentation files."""
    current = technical_predecessor_bytes(root, name)
    if not (root/PRESENTATION_V15_PATH).exists():
        return current
    data = read_json(project_file(root, PRESENTATION_V15_PATH))
    if not isinstance(data, dict):
        raise ValueError('A02 presentation must be a JSON object')
    files, pool = data.get('reversible_text_files'), data.get('reverse_text_patch_pool')
    if not isinstance(files, list) or not isinstance(pool, list):
        raise ValueError('A02 require exact reversible text patch records')
    matches = [row for row in files if isinstance(row, dict) and row.get('path') == name]
    if not matches:
        return current
    if len(matches) != 1 or name not in A02_PREDECESSOR_FILES:
        raise ValueError('Unauthorized or duplicate A02 predecessor record: '+name)
    record = matches[0]; old_sha, old_size = A02_PREDECESSOR_FILES[name]
    if (record.get('old_sha256') != old_sha or record.get('old_bytes') != old_size
            or hashlib.sha256(current).hexdigest() != record.get('new_sha256')
            or len(current) != record.get('new_bytes')):
        raise ValueError('A02 file differs from its complete old/new identities: '+name)
    edits = record.get('edits')
    if not isinstance(edits, list) or not edits:
        raise ValueError('A02 changes require nonempty text edits: '+name)
    chunks, cursor, old_end, delta = [], 0, 0, 0
    for edit in edits:
        if not isinstance(edit, dict) or set(edit) != {'old_offset', 'replacement'}:
            raise ValueError('Invalid reversible A02 text edit: '+name)
        offset, replacement = edit['old_offset'], edit['replacement']
        if (type(offset) is not int or offset < old_end or type(replacement) is not int
                or not 0 <= replacement < len(pool)):
            raise ValueError('Overlapping or invalid A02 text edit: '+name)
        pair = pool[replacement]
        if (not isinstance(pair, dict) or set(pair) != {'old', 'new'}
                or not all(isinstance(pair.get(key), str) for key in ('old', 'new'))
                or pair['old'] == pair['new']):
            raise ValueError('Invalid A02 text replacement pool')
        before, after = pair['old'].encode('utf-8'), pair['new'].encode('utf-8')
        position = offset+delta
        if position < cursor or current[position:position+len(after)] != after:
            raise ValueError('A02 replacement differs at its exact offset: '+name)
        chunks.extend((current[cursor:position], before))
        cursor, old_end = position+len(after), offset+len(before)
        delta += len(after)-len(before)
    rebuilt = b''.join((*chunks, current[cursor:]))
    if hashlib.sha256(rebuilt).hexdigest() != old_sha or len(rebuilt) != old_size:
        raise ValueError('A02 predecessor cannot be reconstructed exactly: '+name)
    return rebuilt


def a02_predecessor_binding(root: Path, name: str) -> dict:
    content = a02_predecessor_bytes(root, name)
    return {'path': name, 'sha256': hashlib.sha256(content).hexdigest(), 'bytes': len(content)}


def references_predecessor_bytes(root: Path, name: str) -> bytes:
    """Undo only the three explicitly permitted v14 presentation files."""
    current = a02_predecessor_bytes(root, name)
    if not (root/PRESENTATION_V14_PATH).exists():
        return current
    data = read_json(project_file(root, PRESENTATION_V14_PATH))
    if not isinstance(data, dict):
        raise ValueError('References presentation must be a JSON object')
    files, pool = data.get('reversible_text_files'), data.get('reverse_text_patch_pool')
    if not isinstance(files, list) or not isinstance(pool, list):
        raise ValueError('References require exact reversible text patch records')
    matches = [row for row in files if isinstance(row, dict) and row.get('path') == name]
    if not matches:
        return current
    if len(matches) != 1 or name not in REFERENCES_PREDECESSOR_FILES:
        raise ValueError('Unauthorized or duplicate References predecessor record: '+name)
    record = matches[0]; old_sha, old_size = REFERENCES_PREDECESSOR_FILES[name]
    if (record.get('old_sha256') != old_sha or record.get('old_bytes') != old_size
            or hashlib.sha256(current).hexdigest() != record.get('new_sha256')
            or len(current) != record.get('new_bytes')):
        raise ValueError('References file differs from its complete old/new identities: '+name)
    edits = record.get('edits')
    if not isinstance(edits, list) or not edits:
        raise ValueError('References changes require nonempty text edits: '+name)
    chunks, cursor, old_end, delta = [], 0, 0, 0
    for edit in edits:
        if not isinstance(edit, dict) or set(edit) != {'old_offset', 'replacement'}:
            raise ValueError('Invalid reversible References text edit: '+name)
        offset, replacement = edit['old_offset'], edit['replacement']
        if (type(offset) is not int or offset < old_end or type(replacement) is not int
                or not 0 <= replacement < len(pool)):
            raise ValueError('Overlapping or invalid References text edit: '+name)
        pair = pool[replacement]
        if (not isinstance(pair, dict) or set(pair) != {'old', 'new'}
                or not all(isinstance(pair.get(key), str) for key in ('old', 'new'))
                or pair['old'] == pair['new']):
            raise ValueError('Invalid References text replacement pool')
        before, after = pair['old'].encode('utf-8'), pair['new'].encode('utf-8')
        position = offset+delta
        if position < cursor or current[position:position+len(after)] != after:
            raise ValueError('References replacement differs at its exact offset: '+name)
        chunks.extend((current[cursor:position], before))
        cursor, old_end = position+len(after), offset+len(before)
        delta += len(after)-len(before)
    rebuilt = b''.join((*chunks, current[cursor:]))
    if hashlib.sha256(rebuilt).hexdigest() != old_sha or len(rebuilt) != old_size:
        raise ValueError('References predecessor cannot be reconstructed exactly: '+name)
    return rebuilt


def references_predecessor_binding(root: Path, name: str) -> dict:
    content = references_predecessor_bytes(root, name)
    return {'path': name, 'sha256': hashlib.sha256(content).hexdigest(), 'bytes': len(content)}


def ai_results_predecessor_bytes(root: Path, name: str) -> bytes:
    """Undo only the five explicitly permitted v13 presentation files."""
    current = references_predecessor_bytes(root, name)
    if not (root/PRESENTATION_V13_PATH).exists():
        return current
    data = read_json(project_file(root, PRESENTATION_V13_PATH))
    if not isinstance(data, dict):
        raise ValueError('AI direct-results presentation must be a JSON object')
    files, pool = data.get('reversible_text_files'), data.get('reverse_text_patch_pool')
    if not isinstance(files, list) or not isinstance(pool, list):
        raise ValueError('AI direct results require exact reversible text patch records')
    matches = [row for row in files if isinstance(row, dict) and row.get('path') == name]
    if not matches:
        return current
    if len(matches) != 1 or name not in AI_RESULTS_PREDECESSOR_FILES:
        raise ValueError('Unauthorized or duplicate AI direct-results predecessor record: '+name)
    record = matches[0]; old_sha, old_size = AI_RESULTS_PREDECESSOR_FILES[name]
    if (record.get('old_sha256') != old_sha or record.get('old_bytes') != old_size
            or hashlib.sha256(current).hexdigest() != record.get('new_sha256')
            or len(current) != record.get('new_bytes')):
        raise ValueError('AI direct-results file differs from its complete old/new identities: '+name)
    edits = record.get('edits')
    if not isinstance(edits, list) or not edits:
        raise ValueError('AI direct-results changes require nonempty text edits: '+name)
    chunks, cursor, old_end, delta = [], 0, 0, 0
    for edit in edits:
        if not isinstance(edit, dict) or set(edit) != {'old_offset', 'replacement'}:
            raise ValueError('Invalid reversible AI direct-results text edit: '+name)
        offset, replacement = edit['old_offset'], edit['replacement']
        if (type(offset) is not int or offset < old_end or type(replacement) is not int
                or not 0 <= replacement < len(pool)):
            raise ValueError('Overlapping or invalid AI direct-results text edit: '+name)
        pair = pool[replacement]
        if (not isinstance(pair, dict) or set(pair) != {'old', 'new'}
                or not all(isinstance(pair.get(key), str) for key in ('old', 'new'))
                or pair['old'] == pair['new']):
            raise ValueError('Invalid AI direct-results text replacement pool')
        before, after = pair['old'].encode('utf-8'), pair['new'].encode('utf-8')
        position = offset+delta
        if position < cursor or current[position:position+len(after)] != after:
            raise ValueError('AI direct-results replacement differs at its exact offset: '+name)
        chunks.extend((current[cursor:position], before))
        cursor, old_end = position+len(after), offset+len(before)
        delta += len(after)-len(before)
    rebuilt = b''.join((*chunks, current[cursor:]))
    if hashlib.sha256(rebuilt).hexdigest() != old_sha or len(rebuilt) != old_size:
        raise ValueError('AI direct-results predecessor cannot be reconstructed exactly: '+name)
    return rebuilt


def ai_results_predecessor_binding(root: Path, name: str) -> dict:
    content = ai_results_predecessor_bytes(root, name)
    return {'path': name, 'sha256': hashlib.sha256(content).hexdigest(), 'bytes': len(content)}


def ai_research_predecessor_bytes(root: Path, name: str) -> bytes:
    """Reconstruct the fixed v11 edition before replaying its older promises.

    The successor stores only ordered changed UTF-8 segments. Both complete
    identities are checked; no predecessor page or document is copied.
    """
    current = ai_results_predecessor_bytes(root, name)
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
    if (root/'provenance/platform-presentation.v33.json').is_file():
        successor_routes.add('people/index.html')
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
    if (root/'provenance/platform-presentation.v33.json').exists() and not (root/'provenance/platform-presentation.v32.json').exists():
        raise ValueError('A09 heritage presentation requires its immutable v32 predecessor')
    if (root/'provenance/platform-presentation.v32.json').exists() and not (root/'provenance/platform-presentation.v31.json').exists():
        raise ValueError('A08 biography presentation requires its immutable v31 predecessor')
    if (root/'provenance/platform-presentation.v31.json').exists() and not (root/'provenance/platform-presentation.v30.json').exists():
        raise ValueError('A07 biography presentation requires its immutable v30 predecessor')
    if (root/'provenance/platform-presentation.v30.json').exists() and not (root/'provenance/platform-presentation.v29.json').exists():
        raise ValueError('A06 biography presentation requires its immutable v29 predecessor')
    if (root/'provenance/platform-presentation.v29.json').exists() and not (root/'provenance/platform-presentation.v28.json').exists():
        raise ValueError('A05 biography presentation requires its immutable v28 predecessor')
    if (root/'provenance/platform-presentation.v28.json').exists() and not (root/'provenance/platform-presentation.v27.json').exists():
        raise ValueError('A04 biography presentation requires its immutable v27 predecessor')
    if (root/'provenance/platform-presentation.v27.json').exists() and not (root/'provenance/platform-presentation.v26.json').exists():
        raise ValueError('A03 biography presentation requires its immutable v26 predecessor')
    if (root/'provenance/platform-presentation.v26.json').exists() and not (root/'provenance/platform-presentation.v25.json').exists():
        raise ValueError('A02 biography presentation requires its immutable v25 predecessor')
    if (root/'provenance/platform-presentation.v25.json').exists() and not (root/PRESENTATION_V24_PATH).exists():
        raise ValueError('A01 primary presentation requires its immutable v24 predecessor')
    if (root/PRESENTATION_V24_PATH).exists() and not (root/PRESENTATION_V23_PATH).exists():
        raise ValueError('Literature presentation requires its immutable v23 predecessor')
    if (root/PRESENTATION_V23_PATH).exists() and not (root/PRESENTATION_V22_PATH).exists():
        raise ValueError('A06 summary presentation requires its fixed v22 predecessor')
    if (root/PRESENTATION_V22_PATH).exists() and not (root/PRESENTATION_V21_PATH).exists():
        raise ValueError('Original-evidence presentation requires its fixed v21 predecessor')
    if (root/PRESENTATION_V21_PATH).exists() and not (root/PRESENTATION_V20_PATH).exists():
        raise ValueError('A02 evidence correction requires its fixed v20 predecessor')
    if (root/PRESENTATION_V20_PATH).exists() and not (root/PRESENTATION_V19_PATH).exists():
        raise ValueError('A02 holdings presentation requires its fixed v19 predecessor')
    if (root/PRESENTATION_V19_PATH).exists() and not (root/PRESENTATION_V18_PATH).exists():
        raise ValueError('A02 original-source follow-up requires its fixed v18 predecessor')
    if (root/PRESENTATION_V18_PATH).exists() and not (root/PRESENTATION_V17_PATH).exists():
        raise ValueError('A02 cited sources require their fixed v17 predecessor')
    if (root/PRESENTATION_V17_PATH).exists() and not (root/PRESENTATION_V16_PATH).exists():
        raise ValueError('A02 team records require their fixed v16 predecessor')
    if (root/PRESENTATION_V16_PATH).exists() and not (root/PRESENTATION_V15_PATH).exists():
        raise ValueError('A02 technical records require their fixed v15 predecessor')
    if (root/PRESENTATION_V15_PATH).exists() and not (root/PRESENTATION_V14_PATH).exists():
        raise ValueError('A02 presentation requires its fixed v14 predecessor')
    if (root/PRESENTATION_V14_PATH).exists() and not (root/PRESENTATION_V13_PATH).exists():
        raise ValueError('References presentation requires its fixed v13 predecessor')
    if (root/PRESENTATION_V13_PATH).exists() and not (root/PRESENTATION_V12_PATH).exists():
        raise ValueError('AI direct results require their fixed v12 predecessor')
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


def _publication_members_v41(root: Path, entries: dict) -> list[dict]:
    """Return the exact Pages allowlist, including only authorized new routes.

    The original 21-member/15-HTML baseline remains immutable. Repository
    research data never become publishable merely because they exist.
    """
    baseline_path = project_file(root, 'provenance/website-baseline.json')
    if digest(baseline_path) != BASELINE_SHA256:
        raise ValueError('Publication members require the immutable original baseline')
    original = {row['path'] for row in read_json(baseline_path)['files']}
    original_html = {name for name in original if name.endswith('.html')}
    added = {AI_RESEARCH_ROUTE} if (root/PRESENTATION_V12_PATH).is_file() else set()
    if 'people/index.html' in entries:
        if not (root/'provenance/platform-presentation.v33.json').is_file():
            raise ValueError('The people heritage route requires its explicit v33 presentation')
        added.add('people/index.html')
    if len(original) != 21 or len(original_html) != 15 or set(entries) != original | added:
        raise ValueError('The effective member set may add only the explicit AI research and A09 heritage HTML routes')
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
    documents = [ai_results_predecessor_binding(root, name) for name in AI_RESEARCH_DOCUMENTS]
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
        if old != ai_results_predecessor_bytes(root, name):
            changed_files.add(name)
    if {row['path'] for row in files} != changed_files:
        raise ValueError('AI research text patches must enumerate every and only changed predecessor file')
    from public_line_labels import project_html, project_markdown
    for name in ('README.md', AI_RESEARCH_DOCUMENT):
        current = ai_results_predecessor_bytes(root, name).decode('utf-8')
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
        after = ai_results_predecessor_bytes(root, 'site/'+name)
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
    addition = additions[0]; added = ai_results_predecessor_bytes(root, 'site/'+AI_RESEARCH_ROUTE)
    if (addition.get('sha256') != hashlib.sha256(added).hexdigest() or addition.get('bytes') != len(added)
            or type(addition.get('bytes')) is not int or addition['bytes'] <= 0
            or not isinstance(addition.get('reason'), str) or not addition['reason'].strip()
            or project_html(added.decode('utf-8'), AI_RESEARCH_ROUTE) != added.decode('utf-8')):
        raise ValueError('The new AI research route differs from its exact static HTML binding')
    updated[AI_RESEARCH_ROUTE] = {'path': AI_RESEARCH_ROUTE, 'sha256': addition['sha256'],
        'bytes': addition['bytes'], 'presentation_id': PRESENTATION_V12_ID}
    for name, expected in updated.items():
        member = ai_results_predecessor_binding(root, 'site/'+name)
        if member['sha256'] != expected['sha256'] or member['bytes'] != expected['bytes']:
            raise ValueError('AI research changed an unlisted or bound website byte: '+name)
    members = publication_members(root, updated)
    # A successor reconstructs the complete fixed renderer, source and output
    # bindings above. Its current renderer is evaluated only on its own final
    # source/output below, never on a predecessor edition.
    if not (root/PRESENTATION_V13_PATH).exists():
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
    return apply_ai_direct_results(root, updated,
        {**report, 'presentation_chain': [*previous_report['presentation_chain'], report]})


def apply_ai_direct_results(root: Path, entries: dict, previous_report: dict) -> tuple[dict, dict]:
    """Deepen only A01/A03 results on the existing static research page."""
    if not (root/PRESENTATION_V13_PATH).exists():
        return entries, previous_report
    if digest(project_file(root, PRESENTATION_V12_PATH)) != PRESENTATION_V12_SHA256:
        raise ValueError('The preceding AI research presentation v12 is immutable')
    path = project_file(root, PRESENTATION_V13_PATH); data = read_json(path)
    if not isinstance(data, dict):
        raise ValueError('AI direct-results presentation must be a JSON object')
    documents = [references_predecessor_binding(root, name) for name in AI_RESULTS_DOCUMENTS]
    protected = {name: {'sha256': row['sha256'], 'bytes': row['bytes']}
                 for name, row in entries.items() if name != AI_RESEARCH_ROUTE}
    required = {'schema_version': '13.0', 'presentation_id': PRESENTATION_V13_ID,
        'publication_kind': 'platform_ai_research_direct_results',
        'previous_presentation_commit': PRESENTATION_V13_PREVIOUS_COMMIT,
        'previous_presentation': {'path': PRESENTATION_V12_PATH, 'sha256': PRESENTATION_V12_SHA256},
        'original_baseline_sha256': BASELINE_SHA256, 'original_archive_sha256': ARCHIVE_SHA256,
        'allowed_html_paths': [AI_RESEARCH_ROUTE], 'added_html_paths': [],
        'allowed_achievement_lines': ['A01', 'A03'], 'editorial_documents': documents,
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
        raise ValueError('Unsupported bounded AI direct-results presentation v13')
    files, pool = data.get('reversible_text_files'), data.get('reverse_text_patch_pool')
    if (not isinstance(files, list) or not files or not isinstance(pool, list) or not pool
            or any(not isinstance(row, dict) or row.get('path') not in AI_RESULTS_PREDECESSOR_FILES for row in files)
            or len({row['path'] for row in files}) != len(files)
            or any(not isinstance(row.get('edits'), list) or not row['edits'] or any(
                not isinstance(edit, dict) or type(edit.get('replacement')) is not int
                for edit in row['edits']) for row in files)):
        raise ValueError('AI direct results may enumerate only their five authorized predecessor text files')
    used = {edit['replacement'] for row in files for edit in row['edits']}
    if used != set(range(len(pool))):
        raise ValueError('AI direct-results replacement pool must contain exactly its used text segments')
    changed_files = set()
    for name, (old_sha, old_size) in AI_RESULTS_PREDECESSOR_FILES.items():
        old = ai_results_predecessor_bytes(root, name)
        if hashlib.sha256(old).hexdigest() != old_sha or len(old) != old_size:
            raise ValueError('AI direct-results predecessor differs from fixed 858232d bytes: '+name)
        if old != references_predecessor_bytes(root, name):
            changed_files.add(name)
    if {row['path'] for row in files} != changed_files:
        raise ValueError('AI direct-results patches must enumerate every and only changed predecessor file')
    previous_content = json.loads(ai_results_predecessor_bytes(root, AI_RESEARCH_CONTENT))
    current_content = json.loads(references_predecessor_bytes(root, AI_RESEARCH_CONTENT))
    if ({key: value for key, value in previous_content.items() if key != 'lines'}
            != {key: value for key, value in current_content.items() if key != 'lines'}):
        raise ValueError('AI direct results cannot alter research metadata, homepage notes or heritage')
    before_lines, after_lines = previous_content.get('lines'), current_content.get('lines')
    line_ids = ['A'+str(n).zfill(2) for n in range(1, 9)]
    if (not isinstance(before_lines, list) or not isinstance(after_lines, list)
            or any(not isinstance(row, dict) for row in before_lines+after_lines)
            or [row.get('id') for row in before_lines] != line_ids
            or [row.get('id') for row in after_lines] != line_ids):
        raise ValueError('AI direct results must preserve the eight ordered canonical research lines')
    changed_lines = []
    for before_line, after_line in zip(before_lines, after_lines):
        identifier = before_line['id']
        if identifier not in {'A01', 'A03'} and before_line != after_line:
            raise ValueError('AI direct results changed an unauthorized research line: '+identifier)
        if any(before_line.get(key) != after_line.get(key) for key in ('name', 'home_summary')):
            raise ValueError('AI direct results must preserve canonical names and homepage summaries: '+identifier)
        if before_line != after_line:
            changed_lines.append(identifier)
    if changed_lines != ['A01', 'A03']:
        raise ValueError('AI direct results must deepen exactly A01 and A03')
    changes = data.get('changes')
    if (not isinstance(changes, list) or len(changes) != 1
            or not isinstance(changes[0], dict) or changes[0].get('path') != AI_RESEARCH_ROUTE
            or data.get('additions') != []):
        raise ValueError('AI direct results may change only the existing research HTML route')
    item = changes[0]; old = entries[AI_RESEARCH_ROUTE]
    before = ai_results_predecessor_bytes(root, 'site/'+AI_RESEARCH_ROUTE)
    after = references_predecessor_bytes(root, 'site/'+AI_RESEARCH_ROUTE)
    if (item.get('old_sha256') != old['sha256'] or item.get('old_bytes') != old['bytes']
            or hashlib.sha256(before).hexdigest() != old['sha256'] or len(before) != old['bytes']
            or item.get('new_sha256') != hashlib.sha256(after).hexdigest() or item.get('new_bytes') != len(after)
            or before == after or not isinstance(item.get('reason'), str) or not item['reason'].strip()):
        raise ValueError('AI direct-results HTML differs from its complete old/new byte identities')
    from public_line_labels import project_html, project_markdown
    if project_html(after.decode('utf-8'), AI_RESEARCH_ROUTE) != after.decode('utf-8'):
        raise ValueError('AI direct results must retain canonical named achievement references')
    document = references_predecessor_bytes(root, AI_RESEARCH_DOCUMENT).decode('utf-8')
    if project_markdown(document) != document:
        raise ValueError('AI direct-results prose must retain canonical named achievement references')
    json_scripts = re.compile(r'<script\b[^>]*\btype\s*=\s*[\"\']application/(?:ld\+)?json[\"\'][^>]*>.*?</script\s*>', re.I | re.S)
    if json_scripts.findall(before.decode('utf-8')) != json_scripts.findall(after.decode('utf-8')):
        raise ValueError('AI direct results cannot replace or add an embedded JSON record')
    updated = {name: dict(row) for name, row in entries.items()}
    updated[AI_RESEARCH_ROUTE] = {**old, 'sha256': item['new_sha256'], 'bytes': item['new_bytes'],
                                'presentation_id': PRESENTATION_V13_ID}
    for name, expected in updated.items():
        member = references_predecessor_binding(root, 'site/'+name)
        if member['sha256'] != expected['sha256'] or member['bytes'] != expected['bytes']:
            raise ValueError('AI direct results changed an unlisted or bound website byte: '+name)
    members = publication_members(root, updated)
    from render_ai_research import inspect_ai_research
    consistency = inspect_ai_research(root)
    if consistency.get('status') != 'passed':
        raise ValueError('AI direct results differ from their source-derived rendering: '+str(consistency.get('errors', [])))
    report = {'path': PRESENTATION_V13_PATH, 'sha256': digest(path), 'presentation_id': PRESENTATION_V13_ID,
        'publication_kind': required['publication_kind'], 'changed_paths': [AI_RESEARCH_ROUTE],
        'added_paths': [], 'changed_achievement_lines': changed_lines,
        'previous_presentation_commit': PRESENTATION_V13_PREVIOUS_COMMIT,
        'exact_predecessor_reconstruction': True, 'source_derived_rendering': True,
        'homepage_and_other_routes_unchanged': True, 'original_embedded_json_bytes_preserved': True,
        'published_html_count': len(members)-2, 'published_json_count': 2,
        'published_member_count_with_marker': len(members)+1,
        **{key: required[key] for key in ('scientific_review_status', 'scientific_data_unchanged',
            'historical_achievement_independent_of_AI_review', 'release_eligible', 'M0_resumed')}}
    return apply_references_presentation(root, updated,
        {**report, 'presentation_chain': [*previous_report['presentation_chain'], report]})


def apply_references_presentation(root: Path, entries: dict, previous_report: dict) -> tuple[dict, dict]:
    """Move source context to a final references section, preserving research."""
    if not (root/PRESENTATION_V14_PATH).exists():
        return entries, previous_report
    if digest(project_file(root, PRESENTATION_V13_PATH)) != PRESENTATION_V13_SHA256:
        raise ValueError('The preceding direct-results presentation v13 is immutable')
    path = project_file(root, PRESENTATION_V14_PATH); data = read_json(path)
    documents = [a02_predecessor_binding(root, name) for name in REFERENCES_DOCUMENTS]
    required = {'schema_version': '14.0', 'presentation_id': PRESENTATION_V14_ID,
        'publication_kind': 'platform_final_references',
        'previous_presentation_commit': PRESENTATION_V14_PREVIOUS_COMMIT,
        'previous_presentation': {'path': PRESENTATION_V13_PATH, 'sha256': PRESENTATION_V13_SHA256},
        'original_baseline_sha256': BASELINE_SHA256, 'original_archive_sha256': ARCHIVE_SHA256,
        'allowed_html_paths': ['index.html'], 'added_html_paths': [], 'additions': [],
        'editorial_documents': documents,
        'protected_website_members': {name: {'sha256': row['sha256'], 'bytes': row['bytes']}
            for name, row in entries.items() if name != 'index.html'},
        'reconstruction_kind': 'deduplicated_exact_utf8_text_edits',
        'scientific_review_status': 'review_required', 'release_eligible': False,
        'scientific_data_unchanged': True, 'M0_resumed': False,
        'historical_achievement_independent_of_AI_review': True}
    if (not isinstance(data, dict) or any(data.get(key) != value for key, value in required.items())
            or any(data.get(key) is not required[key] for key in ('release_eligible',
                'scientific_data_unchanged', 'M0_resumed', 'historical_achievement_independent_of_AI_review'))
            or any(type(data.get(key)) is not int or data[key] != 0
                   for key in ('new_quantum_calls', 'new_model_API_calls'))
            or not isinstance(data.get('authorization'), str) or not data['authorization'].strip()):
        raise ValueError('Unsupported bounded references presentation v14')
    files, pool = data.get('reversible_text_files'), data.get('reverse_text_patch_pool')
    if (not isinstance(files, list) or not isinstance(pool, list) or not pool
            or any(not isinstance(row, dict) for row in files)
            or {row.get('path') for row in files} != set(REFERENCES_PREDECESSOR_FILES)
            or len(files) != len(REFERENCES_PREDECESSOR_FILES)
            or any(not isinstance(row.get('edits'), list) or not row['edits'] or any(
                not isinstance(edit, dict) or type(edit.get('replacement')) is not int
                for edit in row['edits']) for row in files)):
        raise ValueError('References presentation must enumerate its three exact text edits')
    if {edit['replacement'] for row in files for edit in row['edits']} != set(range(len(pool))):
        raise ValueError('References replacement pool must contain exactly its used text segments')
    for name, (old_sha, old_size) in REFERENCES_PREDECESSOR_FILES.items():
        old = references_predecessor_bytes(root, name)
        if hashlib.sha256(old).hexdigest() != old_sha or len(old) != old_size:
            raise ValueError('References predecessor differs from fixed f70a8e7: '+name)
        if old == a02_predecessor_bytes(root, name):
            raise ValueError('References declaration lists an unchanged predecessor file: '+name)
    changes = data.get('changes')
    if (not isinstance(changes, list) or len(changes) != 1
            or not isinstance(changes[0], dict) or changes[0].get('path') != 'index.html'):
        raise ValueError('References may change only the existing homepage')
    item = changes[0]; old = entries['index.html']
    before = references_predecessor_bytes(root, 'site/index.html')
    after = a02_predecessor_bytes(root, 'site/index.html')
    if (item.get('old_sha256') != old['sha256'] or item.get('old_bytes') != old['bytes']
            or hashlib.sha256(before).hexdigest() != old['sha256'] or len(before) != old['bytes']
            or item.get('new_sha256') != hashlib.sha256(after).hexdigest() or item.get('new_bytes') != len(after)
            or not isinstance(item.get('reason'), str) or not item['reason'].strip()):
        raise ValueError('References homepage differs from its complete old/new identities')
    source, current = before.decode('utf-8'), after.decode('utf-8')
    begin, end = '<!-- REFERENCES:BEGIN -->', '<!-- REFERENCES:END -->'
    if current.count(begin) != 1 or current.count(end) != 1:
        raise ValueError('References homepage requires exactly one complete final block')
    a, b = current.index(begin), current.index(end)+len(end)
    if a >= b or not current[b:].startswith('\n</main>'):
        raise ValueError('References must be the final main-content section')
    block = current[a:b]
    if (current[:a]+current[b+1:] != source or block.count('id="references"') != 1
            or '<h2>参考资料</h2>' not in block or block.count('<li ') != 8
            or '致谢' in block or 'ACKNOWLEDGEMENTS' in current):
        raise ValueError('The homepage change must consist only of the final references block')
    readme = a02_predecessor_bytes(root, 'README.md').decode('utf-8')
    previous_readme = references_predecessor_bytes(root, 'README.md').decode('utf-8')
    old_intro = '平台以《氟缘笃志：陈庆云传》、原始论文和机构公开资料为依据，介绍陈先生的研究道路，沿九条成果线呈现开拓性成就、具名合作与育人故事。'
    new_intro = '沿着陈先生的研究道路，按九条成果线呈现开拓性成就、具名合作与育人故事。'
    marker = '## 参考资料'
    if (readme.count(marker) != 1 or readme.rsplit('\n## ', 1)[1].splitlines()[0] != '参考资料'
            or readme.split(marker)[0].rstrip() != previous_readme.replace(old_intro, new_intro, 1).rstrip()
            or readme.count('《氟缘笃志：陈庆云传》') != 1
            or '《氟缘笃志：陈庆云传》' not in readme.split(marker)[1]
            or readme.split(marker)[1].count('\n- **') != 8 or '致谢' in readme):
        raise ValueError('README must move its source context to final references only')
    from public_line_labels import project_html, project_markdown
    if project_html(current, 'index.html') != current or project_markdown(readme) != readme:
        raise ValueError('References must preserve canonical named achievement references')
    updated = {name: dict(row) for name, row in entries.items()}
    updated['index.html'] = {**old, 'sha256': item['new_sha256'], 'bytes': item['new_bytes'],
                              'presentation_id': PRESENTATION_V14_ID}
    for name, expected in updated.items():
        member = a02_predecessor_binding(root, 'site/'+name)
        if member['sha256'] != expected['sha256'] or member['bytes'] != expected['bytes']:
            raise ValueError('References changed an unlisted website byte: '+name)
    members = publication_members(root, updated)
    report = {'path': PRESENTATION_V14_PATH, 'sha256': digest(path), 'presentation_id': PRESENTATION_V14_ID,
        'publication_kind': required['publication_kind'], 'changed_paths': ['index.html'],
        'added_paths': [], 'previous_presentation_commit': PRESENTATION_V14_PREVIOUS_COMMIT,
        'exact_predecessor_reconstruction': True, 'homepage_final_references_only': True,
        'research_and_other_routes_unchanged': True, 'original_embedded_json_bytes_preserved': True,
        'published_member_count_with_marker': len(members)+1,
        **{key: required[key] for key in ('scientific_review_status', 'scientific_data_unchanged',
            'historical_achievement_independent_of_AI_review', 'release_eligible', 'M0_resumed')}}
    return apply_a02_academic_presentation(root, updated,
        {**report, 'presentation_chain': [*previous_report['presentation_chain'], report]})


def apply_a02_academic_presentation(root: Path, entries: dict, previous_report: dict) -> tuple[dict, dict]:
    """Publish bounded A02 history and its separate literature-reading record."""
    if not (root/PRESENTATION_V15_PATH).exists():
        return entries, previous_report
    if digest(project_file(root, PRESENTATION_V14_PATH)) != PRESENTATION_V14_SHA256:
        raise ValueError('The preceding final-references presentation v14 is immutable')
    path = project_file(root, PRESENTATION_V15_PATH); data = read_json(path)
    documents = [technical_predecessor_binding(root, name) for name in A02_DOCUMENTS]
    required = {'schema_version': '15.0', 'presentation_id': PRESENTATION_V15_ID,
        'publication_kind': 'platform_a02_academic_history',
        'previous_presentation_commit': PRESENTATION_V15_PREVIOUS_COMMIT,
        'previous_presentation': {'path': PRESENTATION_V14_PATH, 'sha256': PRESENTATION_V14_SHA256},
        'original_baseline_sha256': BASELINE_SHA256, 'original_archive_sha256': ARCHIVE_SHA256,
        'allowed_html_paths': sorted(A02_ALLOWED_ROUTES), 'added_html_paths': [], 'additions': [],
        'allowed_achievement_lines': ['A02'], 'editorial_documents': documents,
        'protected_website_members': {name: {'sha256': row['sha256'], 'bytes': row['bytes']}
            for name, row in entries.items() if name not in A02_ALLOWED_ROUTES},
        'reconstruction_kind': 'deduplicated_exact_utf8_text_edits',
        'scientific_review_status': 'review_required', 'release_eligible': False,
        'scientific_data_unchanged': True, 'M0_resumed': False,
        'historical_achievement_independent_of_AI_review': True}
    if (not isinstance(data, dict) or any(data.get(key) != value for key, value in required.items())
            or any(data.get(key) is not required[key] for key in ('release_eligible',
                'scientific_data_unchanged', 'M0_resumed', 'historical_achievement_independent_of_AI_review'))
            or any(type(data.get(key)) is not int or data[key] != 0
                   for key in ('new_quantum_calls', 'new_model_API_calls'))
            or not isinstance(data.get('authorization'), str) or not data['authorization'].strip()):
        raise ValueError('Unsupported bounded A02 academic presentation v15')
    files, pool = data.get('reversible_text_files'), data.get('reverse_text_patch_pool')
    if (not isinstance(files, list) or not files or not isinstance(pool, list) or not pool
            or any(not isinstance(row, dict) or row.get('path') not in A02_PREDECESSOR_FILES for row in files)
            or len({row['path'] for row in files}) != len(files)
            or any(not isinstance(row.get('edits'), list) or not row['edits'] or any(
                not isinstance(edit, dict) or type(edit.get('replacement')) is not int
                for edit in row['edits']) for row in files)):
        raise ValueError('A02 may enumerate only its ten permitted predecessor text files')
    if {edit['replacement'] for row in files for edit in row['edits']} != set(range(len(pool))):
        raise ValueError('A02 replacement pool must contain exactly its used text segments')
    changed_files = set()
    for name, (old_sha, old_size) in A02_PREDECESSOR_FILES.items():
        old = a02_predecessor_bytes(root, name)
        if hashlib.sha256(old).hexdigest() != old_sha or len(old) != old_size:
            raise ValueError('A02 predecessor differs from fixed 34c405e bytes: '+name)
        if old != technical_predecessor_bytes(root, name):
            changed_files.add(name)
    if {row['path'] for row in files} != changed_files:
        raise ValueError('A02 text patches must enumerate every and only changed predecessor file')
    previous_content = json.loads(a02_predecessor_bytes(root, AI_RESEARCH_CONTENT))
    current_content = json.loads(technical_predecessor_bytes(root, AI_RESEARCH_CONTENT))
    if ({key: value for key, value in previous_content.items() if key != 'lines'}
            != {key: value for key, value in current_content.items() if key != 'lines'}):
        raise ValueError('A02 cannot alter AI metadata, homepage notes or heritage')
    before_lines, after_lines = previous_content.get('lines'), current_content.get('lines')
    line_ids = ['A'+str(n).zfill(2) for n in range(1, 9)]
    if (not isinstance(before_lines, list) or not isinstance(after_lines, list)
            or any(not isinstance(row, dict) for row in before_lines+after_lines)
            or [row.get('id') for row in before_lines] != line_ids
            or [row.get('id') for row in after_lines] != line_ids):
        raise ValueError('A02 must preserve the eight ordered canonical research lines')
    changed_lines = []
    for before_line, after_line in zip(before_lines, after_lines):
        identifier = before_line['id']
        if identifier != 'A02' and before_line != after_line:
            raise ValueError('A02 changed an unauthorized research line: '+identifier)
        if any(before_line.get(key) != after_line.get(key) for key in ('name', 'home_summary')):
            raise ValueError('A02 must preserve canonical names and homepage summaries: '+identifier)
        if before_line != after_line:
            changed_lines.append(identifier)
    if changed_lines != ['A02']:
        raise ValueError('A02 presentation must deepen exactly its own research record')
    history = json.loads(technical_predecessor_bytes(root, A02_HISTORY_CONTENT))
    if (history.get('achievement_line') != 'A02' or history.get('scientific_review_status') != 'review_required'
            or history.get('release_eligible') is not False or history.get('m0_status') != 'paused'):
        raise ValueError('A02 historical reading must preserve attribution and pending review with M0 paused')
    changes = data.get('changes')
    if (not isinstance(changes, list) or any(not isinstance(row, dict) for row in changes)
            or [row.get('path') for row in changes] != sorted(A02_ALLOWED_ROUTES)):
        raise ValueError('A02 may change exactly its historical topic, research record and source-status inventory')
    from public_line_labels import project_html, project_markdown
    json_scripts = re.compile(r'<script\b[^>]*\btype\s*=\s*[\"\']application/(?:ld\+)?json[\"\'][^>]*>.*?</script\s*>', re.I | re.S)
    updated = {name: dict(row) for name, row in entries.items()}
    for item in changes:
        name = item['path']; old = entries[name]
        before = a02_predecessor_bytes(root, 'site/'+name)
        after = technical_predecessor_bytes(root, 'site/'+name)
        source, current = before.decode('utf-8'), after.decode('utf-8')
        if (item.get('old_sha256') != old['sha256'] or item.get('old_bytes') != old['bytes']
                or hashlib.sha256(before).hexdigest() != old['sha256'] or len(before) != old['bytes']
                or item.get('new_sha256') != hashlib.sha256(after).hexdigest() or item.get('new_bytes') != len(after)
                or before == after or not isinstance(item.get('reason'), str) or not item['reason'].strip()):
            raise ValueError('A02 HTML differs from its complete old/new byte identities: '+name)
        if json_scripts.findall(source) != json_scripts.findall(current):
            raise ValueError('A02 must preserve every existing complete embedded JSON byte: '+name)
        if not set(re.findall(r'\bid="([^"]+)"', source)) <= set(re.findall(r'\bid="([^"]+)"', current)):
            raise ValueError('A02 cannot remove an existing source or navigation anchor: '+name)
        if project_html(current, name) != current:
            raise ValueError('A02 must retain canonical named achievement references: '+name)
        if name == AI_RESEARCH_ROUTE:
            pattern = r'<section\b[^>]*\bid="ai-a02"[^>]*>.*?</section>'
            if (len(re.findall(pattern, source, re.S)) != 1 or len(re.findall(pattern, current, re.S)) != 1
                    or re.sub(pattern, '<A02-RECORD/>', source, flags=re.S) != re.sub(pattern, '<A02-RECORD/>', current, flags=re.S)):
                raise ValueError('Only the A02 section may change on the research page')
        elif name == 'achievements/index.html':
            pattern = r'<article\b[^>]*\bid="heritage-line-a02"[^>]*>.*?</article>'
            if (len(re.findall(pattern, source, re.S)) != 1 or len(re.findall(pattern, current, re.S)) != 1
                    or re.sub(pattern, '<A02-INVENTORY/>', source, flags=re.S) != re.sub(pattern, '<A02-INVENTORY/>', current, flags=re.S)):
                raise ValueError('Only the A02 inventory card may change on the achievement overview')
        else:
            begin, end = '<!-- A02_ACADEMIC_HISTORY:BEGIN -->', '<!-- A02_ACADEMIC_HISTORY:END -->'
            heritage = '<!-- HERITAGE_CONTEXT_BEGIN -->'
            if (current.count(begin) != 1 or current.count(end) != 1
                    or current.index(end) < current.index(begin) or heritage not in source or heritage not in current):
                raise ValueError('A02 topic requires one complete historical block and the retained heritage context')
            old_start = source.index('<article id="topic-fluoromonomers"')
            left, right = current.index(begin), current.index(end)+len(end)
            old_prefix, new_prefix = source[:old_start], current[:left]
            normal = lambda value: re.sub(r'<(title|h1)\b[^>]*>.*?</\1>', '<TOPIC-TITLE/>', value.replace('有机氟化学研究与传承 / 审阅预览', '有机氟化学研究与传承 / 学术成果'), flags=re.S).rstrip()
            if (normal(old_prefix) != normal(new_prefix)
                    or current[right:current.index(heritage)].strip()
                    or source[source.index(heritage):] != current[current.index(heritage):]):
                raise ValueError('A02 may replace only the first two articles, public title and the exact academic eyebrow')
        updated[name] = {**old, 'sha256': item['new_sha256'], 'bytes': item['new_bytes'],
                         'presentation_id': PRESENTATION_V15_ID}
    inventory_path = 'docs/ACADEMIC_ACHIEVEMENTS_zh-CN.md'
    old_inventory = a02_predecessor_bytes(root, inventory_path).decode('utf-8')
    new_inventory = technical_predecessor_bytes(root, inventory_path).decode('utf-8')
    inventory_section = r'^### A02[^\n]*\n.*?(?=^### A0[3-9]|\Z)'
    if (len(re.findall(inventory_section, old_inventory, re.S|re.M)) != 1
            or len(re.findall(inventory_section, new_inventory, re.S|re.M)) != 1
            or re.sub(inventory_section, '<A02-INVENTORY/>', old_inventory, flags=re.S|re.M)
                != re.sub(inventory_section, '<A02-INVENTORY/>', new_inventory, flags=re.S|re.M)):
        raise ValueError('Only the A02 section may change in the academic-achievement inventory document')
    for name in (AI_RESEARCH_DOCUMENT, A02_HISTORY_DOCUMENT, inventory_path):
        prose = technical_predecessor_bytes(root, name).decode('utf-8')
        if project_markdown(prose) != prose:
            raise ValueError('A02 prose must retain canonical named achievement references: '+name)
    for name, expected in updated.items():
        member = technical_predecessor_binding(root, 'site/'+name)
        if member['sha256'] != expected['sha256'] or member['bytes'] != expected['bytes']:
            raise ValueError('A02 changed an unlisted or bound website byte: '+name)
    # When a successor exists its fixed source/renderer/output identities above
    # replay v15. Only the final successor inspects the actual new rendering.
    if not (root/PRESENTATION_V16_PATH).exists():
        from render_a02_history import inspect_a02_history
        from render_ai_research import inspect_ai_research
        for label, consistency in (('historical topic', inspect_a02_history(root)), ('AI reading record', inspect_ai_research(root))):
            if consistency.get('status') != 'passed':
                raise ValueError('A02 '+label+' differs from its source-derived rendering: '+str(consistency.get('errors', [])))
    members = publication_members(root, updated)
    report = {'path': PRESENTATION_V15_PATH, 'sha256': digest(path), 'presentation_id': PRESENTATION_V15_ID,
        'publication_kind': required['publication_kind'], 'changed_paths': sorted(A02_ALLOWED_ROUTES),
        'added_paths': [], 'changed_achievement_lines': changed_lines,
        'previous_presentation_commit': PRESENTATION_V15_PREVIOUS_COMMIT,
        'exact_predecessor_reconstruction': True, 'source_derived_rendering': True,
        'homepage_and_A01_unchanged': True, 'original_embedded_json_bytes_preserved': True,
        'published_member_count_with_marker': len(members)+1,
        **{key: required[key] for key in ('scientific_review_status', 'scientific_data_unchanged',
            'historical_achievement_independent_of_AI_review', 'release_eligible', 'M0_resumed')}}
    return apply_a02_technical_presentation(root, updated,
        {**report, 'presentation_chain': [*previous_report['presentation_chain'], report]})



def apply_a02_technical_presentation(root: Path, entries: dict, previous_report: dict) -> tuple[dict, dict]:
    """Publish scoped technical records without transferring other authorship."""
    if not (root/PRESENTATION_V16_PATH).exists():
        return entries, previous_report
    if digest(project_file(root, PRESENTATION_V15_PATH)) != PRESENTATION_V15_SHA256:
        raise ValueError('The preceding A02 academic presentation v15 is immutable')
    path = project_file(root, PRESENTATION_V16_PATH); data = read_json(path)
    documents = [team_predecessor_binding(root, name) for name in A02_TECHNICAL_DOCUMENTS]
    required = {'schema_version': '16.0', 'presentation_id': PRESENTATION_V16_ID,
        'publication_kind': 'platform_a02_technical_records',
        'previous_presentation_commit': PRESENTATION_V16_PREVIOUS_COMMIT,
        'previous_presentation': {'path': PRESENTATION_V15_PATH, 'sha256': PRESENTATION_V15_SHA256},
        'original_baseline_sha256': BASELINE_SHA256, 'original_archive_sha256': ARCHIVE_SHA256,
        'allowed_html_paths': sorted(A02_ALLOWED_ROUTES), 'added_html_paths': [], 'additions': [],
        'allowed_achievement_lines': ['A02'], 'editorial_documents': documents,
        'protected_website_members': {name: {'sha256': row['sha256'], 'bytes': row['bytes']}
            for name, row in entries.items() if name not in A02_ALLOWED_ROUTES},
        'reconstruction_kind': 'deduplicated_exact_utf8_text_edits',
        'scientific_review_status': 'review_required', 'release_eligible': False,
        'scientific_data_unchanged': True, 'M0_resumed': False,
        'historical_achievement_independent_of_AI_review': True}
    if (not isinstance(data, dict) or any(data.get(key) != value for key, value in required.items())
            or any(data.get(key) is not required[key] for key in ('release_eligible',
                'scientific_data_unchanged', 'M0_resumed', 'historical_achievement_independent_of_AI_review'))
            or any(type(data.get(key)) is not int or data[key] != 0 for key in ('new_quantum_calls', 'new_model_API_calls'))
            or not isinstance(data.get('authorization'), str) or not data['authorization'].strip()):
        raise ValueError('Unsupported bounded A02 technical presentation v16')
    files, pool = data.get('reversible_text_files'), data.get('reverse_text_patch_pool')
    if (not isinstance(files, list) or not files or not isinstance(pool, list) or not pool
            or any(not isinstance(row, dict) or row.get('path') not in A02_TECHNICAL_PREDECESSOR_FILES for row in files)
            or len({row['path'] for row in files}) != len(files)
            or any(not isinstance(row.get('edits'), list) or not row['edits'] or any(
                not isinstance(edit, dict) or type(edit.get('replacement')) is not int for edit in row['edits']) for row in files)):
        raise ValueError('A02 technical records may enumerate only the ten fixed predecessor text files')
    if {edit['replacement'] for row in files for edit in row['edits']} != set(range(len(pool))):
        raise ValueError('Technical replacement pool must contain exactly its used segments')
    changed = set()
    for name, (sha, size) in A02_TECHNICAL_PREDECESSOR_FILES.items():
        old = technical_predecessor_bytes(root, name)
        if hashlib.sha256(old).hexdigest() != sha or len(old) != size:
            raise ValueError('A02 technical predecessor differs from fixed 366ab81: '+name)
        if old != team_predecessor_bytes(root, name):
            changed.add(name)
    if {row['path'] for row in files} != changed:
        raise ValueError('Technical patches must enumerate every and only changed predecessor file')
    old_ai = json.loads(technical_predecessor_bytes(root, AI_RESEARCH_CONTENT))
    current_ai = json.loads(team_predecessor_bytes(root, AI_RESEARCH_CONTENT))
    if ({k:v for k,v in old_ai.items() if k != 'lines'} != {k:v for k,v in current_ai.items() if k != 'lines'}
            or [r.get('id') for r in old_ai['lines']] != ['A'+str(n).zfill(2) for n in range(1,9)]
            or [r.get('id') for r in current_ai['lines']] != [r.get('id') for r in old_ai['lines']]):
        raise ValueError('Technical records must preserve AI metadata and all eight scientific lines')
    for old_line, new_line in zip(old_ai['lines'], current_ai['lines']):
        if old_line['id'] != 'A02' and old_line != new_line:
            raise ValueError('Technical records may update only the A02 AI entry')
        if any(old_line.get(k) != new_line.get(k) for k in ('name','home_summary')):
            raise ValueError('A02 technical records must preserve public names and homepage summaries')
    if old_ai['lines'][1] == current_ai['lines'][1]:
        raise ValueError('Technical records must update the A02 AI entry')
    old_history = json.loads(technical_predecessor_bytes(root, A02_HISTORY_CONTENT))
    history = json.loads(team_predecessor_bytes(root, A02_HISTORY_CONTENT))
    mutable = {'technical_records','sources','pending','ai_scope','inventory_update','technical_retrieval_date'}
    if ({k:v for k,v in old_history.items() if k not in mutable} != {k:v for k,v in history.items() if k not in mutable}
            or history.get('achievement_line') != 'A02' or history.get('scientific_review_status') != 'review_required'
            or history.get('release_eligible') is not False or history.get('m0_status') != 'paused'
            or history.get('new_quantum_calls') != 0 or history.get('new_experiments') != 0):
        raise ValueError('Technical records must preserve existing A02 historical claims and the 1980 paper')
    if not isinstance(history.get('technical_records'), list) or len(history['technical_records']) != 3:
        raise ValueError('Expected exactly three scoped A02 technical records')
    changes = data.get('changes')
    if (not isinstance(changes, list) or any(not isinstance(row, dict) for row in changes)
            or [row.get('path') for row in changes] != sorted(A02_ALLOWED_ROUTES)):
        raise ValueError('Technical records may update exactly the A02 topic, AI record and inventory')
    from public_line_labels import project_html, project_markdown
    json_scripts = re.compile(r'<script\b[^>]*\btype\s*=\s*[\"\']application/(?:ld\+)?json[\"\'][^>]*>.*?</script\s*>', re.I | re.S)
    updated = {name:dict(row) for name,row in entries.items()}
    for item in changes:
        name=item['path']; old=entries[name]
        before=technical_predecessor_bytes(root,'site/'+name); after=team_predecessor_bytes(root,'site/'+name)
        source,current=before.decode('utf-8'),after.decode('utf-8')
        if (item.get('old_sha256') != old['sha256'] or item.get('old_bytes') != old['bytes']
                or hashlib.sha256(before).hexdigest() != old['sha256'] or len(before) != old['bytes']
                or item.get('new_sha256') != hashlib.sha256(after).hexdigest() or item.get('new_bytes') != len(after)
                or before == after or not isinstance(item.get('reason'),str) or not item['reason'].strip()):
            raise ValueError('Technical HTML differs from complete old/new identities: '+name)
        if json_scripts.findall(source) != json_scripts.findall(current):
            raise ValueError('Technical records must preserve every embedded source JSON byte')
        if not set(re.findall(r'\bid="([^\"]+)"',source)) <= set(re.findall(r'\bid="([^\"]+)"',current)):
            raise ValueError('Technical records cannot remove existing navigation/source IDs')
        if project_html(current,name) != current:
            raise ValueError('Technical records must retain canonical named achievement references')
        if name == A02_HISTORY_ROUTE:
            begin,end='<!-- A02_ACADEMIC_HISTORY:BEGIN -->','<!-- A02_ACADEMIC_HISTORY:END -->'
            if any(value.count(begin)!=1 or value.count(end)!=1 for value in (source,current)):
                raise ValueError('Technical topic requires one complete existing A02 marker')
            strip=lambda value:value[:value.index(begin)]+'<A02-HISTORY/>'+value[value.index(end)+len(end):]
            if strip(source) != strip(current):
                raise ValueError('Technical topic may change only inside the A02 historical marker')
        else:
            pattern = (r'<section\b[^>]*\bid="ai-a02"[^>]*>.*?</section>' if name==AI_RESEARCH_ROUTE
                       else r'<article\b[^>]*\bid="heritage-line-a02"[^>]*>.*?</article>')
            if (len(re.findall(pattern,source,re.S))!=1 or len(re.findall(pattern,current,re.S))!=1
                    or re.sub(pattern,'<A02-ONLY/>',source,flags=re.S)!=re.sub(pattern,'<A02-ONLY/>',current,flags=re.S)):
                raise ValueError('Technical records changed outside the A02 entry: '+name)
        updated[name]={**old,'sha256':item['new_sha256'],'bytes':item['new_bytes'],'presentation_id':PRESENTATION_V16_ID}
    inventory='docs/ACADEMIC_ACHIEVEMENTS_zh-CN.md'
    old_doc=technical_predecessor_bytes(root,inventory).decode('utf-8'); new_doc=team_predecessor_bytes(root,inventory).decode('utf-8')
    pattern=r'^### A02[^\n]*\n.*?(?=^### A0[3-9]|\Z)'
    if (len(re.findall(pattern,old_doc,re.S|re.M))!=1 or len(re.findall(pattern,new_doc,re.S|re.M))!=1
            or re.sub(pattern,'<A02-ONLY/>',old_doc,flags=re.S|re.M)!=re.sub(pattern,'<A02-ONLY/>',new_doc,flags=re.S|re.M)):
        raise ValueError('Only A02 may change in the shared academic document')
    for name in (AI_RESEARCH_DOCUMENT,A02_HISTORY_DOCUMENT,inventory):
        prose=team_predecessor_bytes(root,name).decode('utf-8')
        if project_markdown(prose)!=prose:
            raise ValueError('Technical prose lost canonical named achievement references: '+name)
    for name,expected in updated.items():
        member=team_predecessor_binding(root,'site/'+name)
        if member['sha256']!=expected['sha256'] or member['bytes']!=expected['bytes']:
            raise ValueError('Technical records changed an unlisted website byte: '+name)
    # Replay v16 using its fixed source/renderer/output bytes; inspect only the final layer.
    if not (root/PRESENTATION_V17_PATH).exists():
        from render_a02_history import inspect_a02_history
        from render_ai_research import inspect_ai_research
        for label,check in (('A02 history',inspect_a02_history(root)),('AI record',inspect_ai_research(root))):
            if check.get('status')!='passed':
                raise ValueError(label+' differs from its source-derived rendering: '+str(check.get('errors',[])))
    members=publication_members(root,updated)
    report={'path':PRESENTATION_V16_PATH,'sha256':digest(path),'presentation_id':PRESENTATION_V16_ID,
        'publication_kind':required['publication_kind'],'changed_paths':sorted(A02_ALLOWED_ROUTES),'added_paths':[],
        'changed_achievement_lines':['A02'],'previous_presentation_commit':PRESENTATION_V16_PREVIOUS_COMMIT,
        'exact_predecessor_reconstruction':True,'existing_A02_claims_and_1980_paper_preserved':True,
        'source_derived_rendering':True,'homepage_A01_and_original_source_data_unchanged':True,
        'original_embedded_json_bytes_preserved':True,'published_member_count_with_marker':len(members)+1,
        **{key:required[key] for key in ('scientific_review_status','scientific_data_unchanged',
            'historical_achievement_independent_of_AI_review','release_eligible','M0_resumed')}}
    return apply_a02_team_presentation(root, updated,
        {**report,'presentation_chain':[*previous_report['presentation_chain'],report]})


def apply_a02_team_presentation(root: Path, entries: dict, previous_report: dict) -> tuple[dict, dict]:
    """Present attributed team-history evidence, retaining the previous technical background."""
    if not (root/PRESENTATION_V17_PATH).exists():
        return entries, previous_report
    if digest(project_file(root, PRESENTATION_V16_PATH)) != PRESENTATION_V16_SHA256:
        raise ValueError('The preceding A02 technical presentation v16 is immutable')
    path = project_file(root, PRESENTATION_V17_PATH); data = read_json(path)
    documents = [trace_predecessor_binding(root, name) for name in A02_TEAM_DOCUMENTS]
    required = {'schema_version': '17.0', 'presentation_id': PRESENTATION_V17_ID,
        'publication_kind': 'platform_a02_team_records',
        'previous_presentation_commit': PRESENTATION_V17_PREVIOUS_COMMIT,
        'previous_presentation': {'path': PRESENTATION_V16_PATH, 'sha256': PRESENTATION_V16_SHA256},
        'original_baseline_sha256': BASELINE_SHA256, 'original_archive_sha256': ARCHIVE_SHA256,
        'allowed_html_paths': sorted(A02_ALLOWED_ROUTES), 'added_html_paths': [], 'additions': [],
        'allowed_achievement_lines': ['A02'], 'editorial_documents': documents,
        'protected_website_members': {name: {'sha256': row['sha256'], 'bytes': row['bytes']}
            for name, row in entries.items() if name not in A02_ALLOWED_ROUTES},
        'reconstruction_kind': 'deduplicated_exact_utf8_text_edits',
        'scientific_review_status': 'review_required', 'release_eligible': False,
        'scientific_data_unchanged': True, 'M0_resumed': False,
        'historical_achievement_independent_of_AI_review': True}
    if (not isinstance(data, dict) or any(data.get(key) != value for key, value in required.items())
            or any(data.get(key) is not required[key] for key in ('release_eligible',
                'scientific_data_unchanged', 'M0_resumed', 'historical_achievement_independent_of_AI_review'))
            or any(type(data.get(key)) is not int or data[key] != 0 for key in ('new_quantum_calls', 'new_model_API_calls'))
            or not isinstance(data.get('authorization'), str) or not data['authorization'].strip()):
        raise ValueError('Unsupported bounded A02 team presentation v17')
    files, pool = data.get('reversible_text_files'), data.get('reverse_text_patch_pool')
    if (not isinstance(files, list) or not files or not isinstance(pool, list) or not pool
            or any(not isinstance(row, dict) or row.get('path') not in A02_TEAM_PREDECESSOR_FILES for row in files)
            or len({row['path'] for row in files}) != len(files)
            or any(not isinstance(row.get('edits'), list) or not row['edits'] or any(
                not isinstance(edit, dict) or type(edit.get('replacement')) is not int for edit in row['edits']) for row in files)):
        raise ValueError('A02 team records may enumerate only the ten fixed predecessor text files')
    if {edit['replacement'] for row in files for edit in row['edits']} != set(range(len(pool))):
        raise ValueError('Team replacement pool must contain exactly its used segments')
    changed = set()
    for name, (sha, size) in A02_TEAM_PREDECESSOR_FILES.items():
        old = team_predecessor_bytes(root, name)
        if hashlib.sha256(old).hexdigest() != sha or len(old) != size:
            raise ValueError('A02 team predecessor differs from fixed 936ca1d: '+name)
        if old != trace_predecessor_bytes(root, name):
            changed.add(name)
    if {row['path'] for row in files} != changed:
        raise ValueError('Team patches must enumerate every and only changed predecessor file')
    old_ai = json.loads(team_predecessor_bytes(root, AI_RESEARCH_CONTENT))
    current_ai = json.loads(trace_predecessor_bytes(root, AI_RESEARCH_CONTENT))
    if ({k:v for k,v in old_ai.items() if k != 'lines'} != {k:v for k,v in current_ai.items() if k != 'lines'}
            or [r.get('id') for r in old_ai['lines']] != ['A'+str(n).zfill(2) for n in range(1,9)]
            or [r.get('id') for r in current_ai['lines']] != [r.get('id') for r in old_ai['lines']]):
        raise ValueError('Team records must preserve AI metadata and all eight scientific lines')
    for old_line, new_line in zip(old_ai['lines'], current_ai['lines']):
        if old_line['id'] != 'A02' and old_line != new_line:
            raise ValueError('Team records may update only the A02 AI entry')
        if any(old_line.get(k) != new_line.get(k) for k in ('name','home_summary')):
            raise ValueError('A02 team records must preserve public names and homepage summaries')
    if old_ai['lines'][1] == current_ai['lines'][1]:
        raise ValueError('Team records must update the A02 AI entry')
    old_history = json.loads(team_predecessor_bytes(root, A02_HISTORY_CONTENT))
    history = json.loads(trace_predecessor_bytes(root, A02_HISTORY_CONTENT))
    mutable = {'team_records','sources','pending','ai_scope','inventory_update','team_retrieval_date'}
    if ({k:v for k,v in old_history.items() if k not in mutable} != {k:v for k,v in history.items() if k not in mutable}
            or history.get('achievement_line') != 'A02' or history.get('scientific_review_status') != 'review_required'
            or history.get('release_eligible') is not False or history.get('m0_status') != 'paused'
            or history.get('new_quantum_calls') != 0 or history.get('new_experiments') != 0):
        raise ValueError('Team records must preserve existing A02 historical claims and the 1980 paper')
    team_records = history.get('team_records')
    if (not isinstance(team_records, list) or any(not isinstance(row, dict) for row in team_records)
            or [row.get('id') for row in team_records] != ['a02-team-hfp','a02-team-rubber','a02-team-oil']
            or any(row.get('original_records_obtained') is not False for row in team_records)):
        raise ValueError('Expected three attributed A02 team records with original records still unavailable')
    if (not isinstance(history.get('sources'), list)
            or history['sources'][:len(old_history['sources'])] != old_history['sources']):
        raise ValueError('Team records may append sources, preserving every existing source object')
    changes = data.get('changes')
    if (not isinstance(changes, list) or any(not isinstance(row, dict) for row in changes)
            or [row.get('path') for row in changes] != sorted(A02_ALLOWED_ROUTES)):
        raise ValueError('Team records may update exactly the A02 topic, AI record and inventory')
    from public_line_labels import project_html, project_markdown
    json_scripts = re.compile(r'<script\b[^>]*\btype\s*=\s*[\"\']application/(?:ld\+)?json[\"\'][^>]*>.*?</script\s*>', re.I | re.S)
    updated = {name:dict(row) for name,row in entries.items()}
    for item in changes:
        name=item['path']; old=entries[name]
        before=team_predecessor_bytes(root,'site/'+name); after=trace_predecessor_bytes(root,'site/'+name)
        source,current=before.decode('utf-8'),after.decode('utf-8')
        if (item.get('old_sha256') != old['sha256'] or item.get('old_bytes') != old['bytes']
                or hashlib.sha256(before).hexdigest() != old['sha256'] or len(before) != old['bytes']
                or item.get('new_sha256') != hashlib.sha256(after).hexdigest() or item.get('new_bytes') != len(after)
                or before == after or not isinstance(item.get('reason'),str) or not item['reason'].strip()):
            raise ValueError('Team HTML differs from complete old/new identities: '+name)
        if json_scripts.findall(source) != json_scripts.findall(current):
            raise ValueError('Team records must preserve every embedded source JSON byte')
        if not set(re.findall(r'\bid="([^\"]+)"',source)) <= set(re.findall(r'\bid="([^\"]+)"',current)):
            raise ValueError('Team records cannot remove existing navigation/source IDs')
        if project_html(current,name) != current:
            raise ValueError('Team records must retain canonical named achievement references')
        if name == A02_HISTORY_ROUTE:
            begin,end='<!-- A02_ACADEMIC_HISTORY:BEGIN -->','<!-- A02_ACADEMIC_HISTORY:END -->'
            if any(value.count(begin)!=1 or value.count(end)!=1 for value in (source,current)):
                raise ValueError('Team topic requires one complete existing A02 marker')
            strip=lambda value:value[:value.index(begin)]+'<A02-HISTORY/>'+value[value.index(end)+len(end):]
            if strip(source) != strip(current):
                raise ValueError('Team topic may change only inside the A02 historical marker')
            background = r'<article\b[^>]*\bid="a02-technical-records"[^>]*>.*?</article>'
            if (len(re.findall(background, source, re.S)) != 1
                    or re.findall(background, source, re.S) != re.findall(background, current, re.S)):
                raise ValueError('Team records must preserve the complete existing technical-background article')
            team = r'<article\b[^>]*\bid="a02-team-records"[^>]*>.*?</article>'
            if (len(re.findall(team, current, re.S)) != 1
                    or current.index('id="a02-team-records"') > current.index('id="a02-technical-records"')):
                raise ValueError('Attributed A02 team records must precede other-team technical background')
        else:
            pattern = (r'<section\b[^>]*\bid="ai-a02"[^>]*>.*?</section>' if name==AI_RESEARCH_ROUTE
                       else r'<article\b[^>]*\bid="heritage-line-a02"[^>]*>.*?</article>')
            if (len(re.findall(pattern,source,re.S))!=1 or len(re.findall(pattern,current,re.S))!=1
                    or re.sub(pattern,'<A02-ONLY/>',source,flags=re.S)!=re.sub(pattern,'<A02-ONLY/>',current,flags=re.S)):
                raise ValueError('Team records changed outside the A02 entry: '+name)
        updated[name]={**old,'sha256':item['new_sha256'],'bytes':item['new_bytes'],'presentation_id':PRESENTATION_V17_ID}
    inventory='docs/ACADEMIC_ACHIEVEMENTS_zh-CN.md'
    old_doc=team_predecessor_bytes(root,inventory).decode('utf-8'); new_doc=trace_predecessor_bytes(root,inventory).decode('utf-8')
    pattern=r'^### A02[^\n]*\n.*?(?=^### A0[3-9]|\Z)'
    if (len(re.findall(pattern,old_doc,re.S|re.M))!=1 or len(re.findall(pattern,new_doc,re.S|re.M))!=1
            or re.sub(pattern,'<A02-ONLY/>',old_doc,flags=re.S|re.M)!=re.sub(pattern,'<A02-ONLY/>',new_doc,flags=re.S|re.M)):
        raise ValueError('Only A02 may change in the shared academic document')
    for name in (AI_RESEARCH_DOCUMENT,A02_HISTORY_DOCUMENT,inventory):
        prose=trace_predecessor_bytes(root,name).decode('utf-8')
        if project_markdown(prose)!=prose:
            raise ValueError('Team prose lost canonical named achievement references: '+name)
    for name,expected in updated.items():
        member=trace_predecessor_binding(root,'site/'+name)
        if member['sha256']!=expected['sha256'] or member['bytes']!=expected['bytes']:
            raise ValueError('Team records changed an unlisted website byte: '+name)
    # Replay v17 from fixed source/renderer/output bytes; inspect only the final layer.
    if not (root/PRESENTATION_V18_PATH).exists():
        from render_a02_history import inspect_a02_history
        from render_ai_research import inspect_ai_research
        for label,check in (('A02 history',inspect_a02_history(root)),('AI record',inspect_ai_research(root))):
            if check.get('status')!='passed':
                raise ValueError(label+' differs from its source-derived rendering: '+str(check.get('errors',[])))
    members=publication_members(root,updated)
    report={'path':PRESENTATION_V17_PATH,'sha256':digest(path),'presentation_id':PRESENTATION_V17_ID,
        'publication_kind':required['publication_kind'],'changed_paths':sorted(A02_ALLOWED_ROUTES),'added_paths':[],
        'changed_achievement_lines':['A02'],'previous_presentation_commit':PRESENTATION_V17_PREVIOUS_COMMIT,
        'exact_predecessor_reconstruction':True,'existing_A02_claims_1980_paper_and_technical_background_preserved':True,
        'source_derived_rendering':True,'homepage_A01_and_original_source_data_unchanged':True,
        'original_embedded_json_bytes_preserved':True,'published_member_count_with_marker':len(members)+1,
        **{key:required[key] for key in ('scientific_review_status','scientific_data_unchanged',
            'historical_achievement_independent_of_AI_review','release_eligible','M0_resumed')}}
    return apply_a02_source_trace_presentation(root, updated,
        {**report,'presentation_chain':[*previous_report['presentation_chain'],report]})


def apply_a02_source_trace_presentation(root: Path, entries: dict, previous_report: dict) -> tuple[dict, dict]:
    """Trace cited sources without promoting catalogue metadata to obtained original records."""
    if not (root/PRESENTATION_V18_PATH).exists():
        return entries, previous_report
    if digest(project_file(root, PRESENTATION_V17_PATH)) != PRESENTATION_V17_SHA256:
        raise ValueError('The preceding A02 team presentation v17 is immutable')
    path = project_file(root, PRESENTATION_V18_PATH); data = read_json(path)
    documents = [original_followup_predecessor_binding(root, name) for name in A02_SOURCE_TRACE_DOCUMENTS]
    required = {'schema_version': '18.0', 'presentation_id': PRESENTATION_V18_ID,
        'publication_kind': 'platform_a02_cited_sources',
        'previous_presentation_commit': PRESENTATION_V18_PREVIOUS_COMMIT,
        'previous_presentation': {'path': PRESENTATION_V17_PATH, 'sha256': PRESENTATION_V17_SHA256},
        'original_baseline_sha256': BASELINE_SHA256, 'original_archive_sha256': ARCHIVE_SHA256,
        'allowed_html_paths': sorted(A02_ALLOWED_ROUTES), 'added_html_paths': [], 'additions': [],
        'allowed_achievement_lines': ['A02'], 'editorial_documents': documents,
        'protected_website_members': {name: {'sha256': row['sha256'], 'bytes': row['bytes']}
            for name, row in entries.items() if name not in A02_ALLOWED_ROUTES},
        'reconstruction_kind': 'deduplicated_exact_utf8_text_edits',
        'scientific_review_status': 'review_required', 'release_eligible': False,
        'scientific_data_unchanged': True, 'M0_resumed': False,
        'historical_achievement_independent_of_AI_review': True}
    if (not isinstance(data, dict) or any(data.get(key) != value for key, value in required.items())
            or any(data.get(key) is not required[key] for key in ('release_eligible',
                'scientific_data_unchanged', 'M0_resumed', 'historical_achievement_independent_of_AI_review'))
            or any(type(data.get(key)) is not int or data[key] != 0 for key in ('new_quantum_calls', 'new_model_API_calls'))
            or not isinstance(data.get('authorization'), str) or not data['authorization'].strip()):
        raise ValueError('Unsupported bounded A02 cited-source presentation v18')
    files, pool = data.get('reversible_text_files'), data.get('reverse_text_patch_pool')
    if (not isinstance(files, list) or not files or not isinstance(pool, list) or not pool
            or any(not isinstance(row, dict) or row.get('path') not in A02_SOURCE_TRACE_PREDECESSOR_FILES for row in files)
            or len({row['path'] for row in files}) != len(files)
            or any(not isinstance(row.get('edits'), list) or not row['edits'] or any(
                not isinstance(edit, dict) or type(edit.get('replacement')) is not int for edit in row['edits']) for row in files)):
        raise ValueError('A02 cited-source records may enumerate only the ten fixed predecessor text files')
    if {edit['replacement'] for row in files for edit in row['edits']} != set(range(len(pool))):
        raise ValueError('Team replacement pool must contain exactly its used segments')
    changed = set()
    for name, (sha, size) in A02_SOURCE_TRACE_PREDECESSOR_FILES.items():
        old = trace_predecessor_bytes(root, name)
        if hashlib.sha256(old).hexdigest() != sha or len(old) != size:
            raise ValueError('A02 cited-source predecessor differs from fixed 98e079c: '+name)
        if old != original_followup_predecessor_bytes(root, name):
            changed.add(name)
    if {row['path'] for row in files} != changed:
        raise ValueError('Team patches must enumerate every and only changed predecessor file')
    old_ai = json.loads(trace_predecessor_bytes(root, AI_RESEARCH_CONTENT))
    current_ai = json.loads(original_followup_predecessor_bytes(root, AI_RESEARCH_CONTENT))
    if ({k:v for k,v in old_ai.items() if k != 'lines'} != {k:v for k,v in current_ai.items() if k != 'lines'}
            or [r.get('id') for r in old_ai['lines']] != ['A'+str(n).zfill(2) for n in range(1,9)]
            or [r.get('id') for r in current_ai['lines']] != [r.get('id') for r in old_ai['lines']]):
        raise ValueError('Team records must preserve AI metadata and all eight scientific lines')
    for old_line, new_line in zip(old_ai['lines'], current_ai['lines']):
        if old_line['id'] != 'A02' and old_line != new_line:
            raise ValueError('Team records may update only the A02 AI entry')
        if any(old_line.get(k) != new_line.get(k) for k in ('name','home_summary')):
            raise ValueError('A02 team records must preserve public names and homepage summaries')
    if old_ai['lines'][1] == current_ai['lines'][1]:
        raise ValueError('Team records must update the A02 AI entry')
    old_history = json.loads(trace_predecessor_bytes(root, A02_HISTORY_CONTENT))
    history = json.loads(original_followup_predecessor_bytes(root, A02_HISTORY_CONTENT))
    mutable = {'source_trace','sources','pending','ai_scope','inventory_update'}
    if ({k:v for k,v in old_history.items() if k not in mutable} != {k:v for k,v in history.items() if k not in mutable}
            or history.get('achievement_line') != 'A02' or history.get('scientific_review_status') != 'review_required'
            or history.get('release_eligible') is not False or history.get('m0_status') != 'paused'
            or history.get('new_quantum_calls') != 0 or history.get('new_experiments') != 0):
        raise ValueError('Team records must preserve existing A02 historical claims and the 1980 paper')
    team_records = history.get('team_records')
    if (not isinstance(team_records, list) or any(not isinstance(row, dict) for row in team_records)
            or [row.get('id') for row in team_records] != ['a02-team-hfp','a02-team-rubber','a02-team-oil']
            or any(row.get('original_records_obtained') is not False for row in team_records)):
        raise ValueError('Expected three attributed A02 team records with original records still unavailable')
    if (not isinstance(history.get('sources'), list)
            or history['sources'][:len(old_history['sources'])] != old_history['sources']):
        raise ValueError('Team records may append sources, preserving every existing source object')
    source_trace = history.get('source_trace')
    if (not isinstance(source_trace, list) or len(source_trace) != 2
            or any(not isinstance(row, dict) for row in source_trace)):
        raise ValueError('Expected exactly two separately qualified cited-source trace records')
    changes = data.get('changes')
    if (not isinstance(changes, list) or any(not isinstance(row, dict) for row in changes)
            or [row.get('path') for row in changes] != sorted(A02_ALLOWED_ROUTES)):
        raise ValueError('Team records may update exactly the A02 topic, AI record and inventory')
    from public_line_labels import project_html, project_markdown
    json_scripts = re.compile(r'<script\b[^>]*\btype\s*=\s*[\"\']application/(?:ld\+)?json[\"\'][^>]*>.*?</script\s*>', re.I | re.S)
    updated = {name:dict(row) for name,row in entries.items()}
    for item in changes:
        name=item['path']; old=entries[name]
        before=trace_predecessor_bytes(root,'site/'+name); after=original_followup_predecessor_bytes(root,'site/'+name)
        source,current=before.decode('utf-8'),after.decode('utf-8')
        if (item.get('old_sha256') != old['sha256'] or item.get('old_bytes') != old['bytes']
                or hashlib.sha256(before).hexdigest() != old['sha256'] or len(before) != old['bytes']
                or item.get('new_sha256') != hashlib.sha256(after).hexdigest() or item.get('new_bytes') != len(after)
                or before == after or not isinstance(item.get('reason'),str) or not item['reason'].strip()):
            raise ValueError('Team HTML differs from complete old/new identities: '+name)
        if json_scripts.findall(source) != json_scripts.findall(current):
            raise ValueError('Team records must preserve every embedded source JSON byte')
        if not set(re.findall(r'\bid="([^\"]+)"',source)) <= set(re.findall(r'\bid="([^\"]+)"',current)):
            raise ValueError('Team records cannot remove existing navigation/source IDs')
        if project_html(current,name) != current:
            raise ValueError('Team records must retain canonical named achievement references')
        if name == A02_HISTORY_ROUTE:
            begin,end='<!-- A02_ACADEMIC_HISTORY:BEGIN -->','<!-- A02_ACADEMIC_HISTORY:END -->'
            if any(value.count(begin)!=1 or value.count(end)!=1 for value in (source,current)):
                raise ValueError('Team topic requires one complete existing A02 marker')
            strip=lambda value:value[:value.index(begin)]+'<A02-HISTORY/>'+value[value.index(end)+len(end):]
            if strip(source) != strip(current):
                raise ValueError('Team topic may change only inside the A02 historical marker')
            background = r'<article\b[^>]*\bid="a02-technical-records"[^>]*>.*?</article>'
            if (len(re.findall(background, source, re.S)) != 1
                    or re.findall(background, source, re.S) != re.findall(background, current, re.S)):
                raise ValueError('Team records must preserve the complete existing technical-background article')
            team = r'<article\b[^>]*\bid="a02-team-records"[^>]*>.*?</article>'
            if (len(re.findall(team, current, re.S)) != 1
                    or current.index('id="a02-team-records"') > current.index('id="a02-technical-records"')):
                raise ValueError('Attributed A02 team records must precede other-team technical background')
            if re.findall(team, source, re.S) != re.findall(team, current, re.S):
                raise ValueError('Cited sources must preserve the complete existing team-history article')
            trace = r'<article\b[^>]*\bid="a02-source-trace"[^>]*>.*?</article>'
            if len(re.findall(trace, current, re.S)) != 1:
                raise ValueError('Expected one independent A02 cited-source trace article')
        else:
            pattern = (r'<section\b[^>]*\bid="ai-a02"[^>]*>.*?</section>' if name==AI_RESEARCH_ROUTE
                       else r'<article\b[^>]*\bid="heritage-line-a02"[^>]*>.*?</article>')
            if (len(re.findall(pattern,source,re.S))!=1 or len(re.findall(pattern,current,re.S))!=1
                    or re.sub(pattern,'<A02-ONLY/>',source,flags=re.S)!=re.sub(pattern,'<A02-ONLY/>',current,flags=re.S)):
                raise ValueError('Team records changed outside the A02 entry: '+name)
        updated[name]={**old,'sha256':item['new_sha256'],'bytes':item['new_bytes'],'presentation_id':PRESENTATION_V18_ID}
    inventory='docs/ACADEMIC_ACHIEVEMENTS_zh-CN.md'
    old_doc=trace_predecessor_bytes(root,inventory).decode('utf-8'); new_doc=original_followup_predecessor_bytes(root,inventory).decode('utf-8')
    pattern=r'^### A02[^\n]*\n.*?(?=^### A0[3-9]|\Z)'
    if (len(re.findall(pattern,old_doc,re.S|re.M))!=1 or len(re.findall(pattern,new_doc,re.S|re.M))!=1
            or re.sub(pattern,'<A02-ONLY/>',old_doc,flags=re.S|re.M)!=re.sub(pattern,'<A02-ONLY/>',new_doc,flags=re.S|re.M)):
        raise ValueError('Only A02 may change in the shared academic document')
    for name in (AI_RESEARCH_DOCUMENT,A02_HISTORY_DOCUMENT,inventory):
        prose=original_followup_predecessor_bytes(root,name).decode('utf-8')
        if project_markdown(prose)!=prose:
            raise ValueError('Team prose lost canonical named achievement references: '+name)
    for name,expected in updated.items():
        member=original_followup_predecessor_binding(root,'site/'+name)
        if member['sha256']!=expected['sha256'] or member['bytes']!=expected['bytes']:
            raise ValueError('Team records changed an unlisted website byte: '+name)
    # Replay v18 from fixed source/renderer/output bytes; inspect only the final layer.
    if not (root/PRESENTATION_V19_PATH).exists():
        from render_a02_history import inspect_a02_history
        from render_ai_research import inspect_ai_research
        for label,check in (('A02 history',inspect_a02_history(root)),('AI record',inspect_ai_research(root))):
            if check.get('status')!='passed':
                raise ValueError(label+' differs from its source-derived rendering: '+str(check.get('errors',[])))
    members=publication_members(root,updated)
    report={'path':PRESENTATION_V18_PATH,'sha256':digest(path),'presentation_id':PRESENTATION_V18_ID,
        'publication_kind':required['publication_kind'],'changed_paths':sorted(A02_ALLOWED_ROUTES),'added_paths':[],
        'changed_achievement_lines':['A02'],'previous_presentation_commit':PRESENTATION_V18_PREVIOUS_COMMIT,
        'exact_predecessor_reconstruction':True,'existing_A02_history_paper_technical_and_team_records_preserved':True,
        'source_derived_rendering':True,'homepage_A01_and_original_source_data_unchanged':True,
        'original_embedded_json_bytes_preserved':True,'published_member_count_with_marker':len(members)+1,
        **{key:required[key] for key in ('scientific_review_status','scientific_data_unchanged',
            'historical_achievement_independent_of_AI_review','release_eligible','M0_resumed')}}
    return apply_a02_original_followup_presentation(root, updated,
        {**report,'presentation_chain':[*previous_report['presentation_chain'],report]})


def apply_a02_original_followup_presentation(root: Path, entries: dict, previous_report: dict) -> tuple[dict, dict]:
    """Publish only refined trace data and the final A02 AI-record summary."""
    if not (root/PRESENTATION_V19_PATH).exists():
        return entries, previous_report
    if digest(project_file(root, PRESENTATION_V18_PATH)) != PRESENTATION_V18_SHA256:
        raise ValueError('The preceding A02 cited-source presentation v18 is immutable')
    path = project_file(root, PRESENTATION_V19_PATH); data = read_json(path)
    documents = [holdings_predecessor_binding(root, name) for name in A02_ORIGINAL_FOLLOWUP_DOCUMENTS]
    required = {'schema_version': '19.0', 'presentation_id': PRESENTATION_V19_ID,
        'publication_kind': 'platform_a02_original_followup',
        'previous_presentation_commit': PRESENTATION_V19_PREVIOUS_COMMIT,
        'previous_presentation': {'path': PRESENTATION_V18_PATH, 'sha256': PRESENTATION_V18_SHA256},
        'original_baseline_sha256': BASELINE_SHA256, 'original_archive_sha256': ARCHIVE_SHA256,
        'allowed_html_paths': sorted(A02_ORIGINAL_FOLLOWUP_ROUTES), 'added_html_paths': [], 'additions': [],
        'allowed_achievement_lines': ['A02'], 'editorial_documents': documents,
        'protected_website_members': {name: {'sha256': row['sha256'], 'bytes': row['bytes']}
            for name, row in entries.items() if name not in A02_ORIGINAL_FOLLOWUP_ROUTES},
        'reconstruction_kind': 'deduplicated_exact_utf8_text_edits',
        'scientific_review_status': 'review_required', 'release_eligible': False,
        'scientific_data_unchanged': True, 'M0_resumed': False,
        'historical_achievement_independent_of_AI_review': True}
    if (not isinstance(data, dict) or any(data.get(key) != value for key, value in required.items())
            or any(data.get(key) is not required[key] for key in ('release_eligible',
                'scientific_data_unchanged', 'M0_resumed', 'historical_achievement_independent_of_AI_review'))
            or any(type(data.get(key)) is not int or data[key] != 0 for key in ('new_quantum_calls', 'new_model_API_calls'))
            or not isinstance(data.get('authorization'), str) or not data['authorization'].strip()):
        raise ValueError('Unsupported bounded A02 original-followup presentation v19')
    files, pool = data.get('reversible_text_files'), data.get('reverse_text_patch_pool')
    if (not isinstance(files, list) or not files or not isinstance(pool, list) or not pool
            or any(not isinstance(row, dict) or row.get('path') not in A02_ORIGINAL_FOLLOWUP_PREDECESSOR_FILES for row in files)
            or len({row['path'] for row in files}) != len(files)
            or any(not isinstance(row.get('edits'), list) or not row['edits'] or any(
                not isinstance(edit, dict) or type(edit.get('replacement')) is not int for edit in row['edits']) for row in files)):
        raise ValueError('A02 original-followup records may enumerate only the seven fixed predecessor text files')
    if {edit['replacement'] for row in files for edit in row['edits']} != set(range(len(pool))):
        raise ValueError('Team replacement pool must contain exactly its used segments')
    changed = set()
    for name, (sha, size) in A02_ORIGINAL_FOLLOWUP_PREDECESSOR_FILES.items():
        old = original_followup_predecessor_bytes(root, name)
        if hashlib.sha256(old).hexdigest() != sha or len(old) != size:
            raise ValueError('A02 original-followup predecessor differs from fixed b107b56: '+name)
        if old != holdings_predecessor_bytes(root, name):
            changed.add(name)
    if {row['path'] for row in files} != changed:
        raise ValueError('Team patches must enumerate every and only changed predecessor file')
    old_ai = json.loads(original_followup_predecessor_bytes(root, AI_RESEARCH_CONTENT))
    current_ai = json.loads(holdings_predecessor_bytes(root, AI_RESEARCH_CONTENT))
    try:
        summary = current_ai['lines'][1]['records'][-1]['summary']
    except (KeyError, IndexError, TypeError) as error:
        raise ValueError('Missing final A02 AI-record summary') from error
    if (not isinstance(summary, str) or not summary.strip()
            or summary == old_ai['lines'][1]['records'][-1]['summary']):
        raise ValueError('The final A02 AI-record summary must contain the authorized refinement')
    expected_ai = json.loads(json.dumps(old_ai))
    expected_ai['lines'][1]['records'][-1]['summary'] = summary
    if current_ai != expected_ai:
        raise ValueError('Only the final A02 AI-record summary may change in the complete AI registry')
    old_history = json.loads(original_followup_predecessor_bytes(root, A02_HISTORY_CONTENT))
    history = json.loads(holdings_predecessor_bytes(root, A02_HISTORY_CONTENT))
    mutable = {'source_trace','sources'}
    if ({k:v for k,v in old_history.items() if k not in mutable} != {k:v for k,v in history.items() if k not in mutable}
            or history.get('achievement_line') != 'A02' or history.get('scientific_review_status') != 'review_required'
            or history.get('release_eligible') is not False or history.get('m0_status') != 'paused'
            or history.get('new_quantum_calls') != 0 or history.get('new_experiments') != 0):
        raise ValueError('Team records must preserve existing A02 historical claims and the 1980 paper')
    team_records = history.get('team_records')
    if (not isinstance(team_records, list) or any(not isinstance(row, dict) for row in team_records)
            or [row.get('id') for row in team_records] != ['a02-team-hfp','a02-team-rubber','a02-team-oil']
            or any(row.get('original_records_obtained') is not False for row in team_records)):
        raise ValueError('Expected three attributed A02 team records with original records still unavailable')
    if (not isinstance(history.get('sources'), list)
            or history['sources'][:len(old_history['sources'])] != old_history['sources']):
        raise ValueError('Team records may append sources, preserving every existing source object')
    source_trace = history.get('source_trace')
    if (not isinstance(source_trace, list) or any(not isinstance(row, dict) for row in source_trace)
            or [row.get('id') for row in source_trace] != ['a02-trace-interview','a02-trace-book2009']
            or any(row.get('original_obtained') is not False for row in source_trace)
            or source_trace[1].get('volume_confirmed') is not False):
        raise ValueError('The same two trace records must retain unresolved originals and target-page volume')
    changes = data.get('changes')
    if (not isinstance(changes, list) or any(not isinstance(row, dict) for row in changes)
            or [row.get('path') for row in changes] != sorted(A02_ORIGINAL_FOLLOWUP_ROUTES)):
        raise ValueError('Original follow-up may update only the A02 topic and AI record routes')
    from public_line_labels import project_html, project_markdown
    json_scripts = re.compile(r'<script\b[^>]*\btype\s*=\s*[\"\']application/(?:ld\+)?json[\"\'][^>]*>.*?</script\s*>', re.I | re.S)
    updated = {name:dict(row) for name,row in entries.items()}
    for item in changes:
        name=item['path']; old=entries[name]
        before=original_followup_predecessor_bytes(root,'site/'+name); after=holdings_predecessor_bytes(root,'site/'+name)
        source,current=before.decode('utf-8'),after.decode('utf-8')
        if (item.get('old_sha256') != old['sha256'] or item.get('old_bytes') != old['bytes']
                or hashlib.sha256(before).hexdigest() != old['sha256'] or len(before) != old['bytes']
                or item.get('new_sha256') != hashlib.sha256(after).hexdigest() or item.get('new_bytes') != len(after)
                or before == after or not isinstance(item.get('reason'),str) or not item['reason'].strip()):
            raise ValueError('Team HTML differs from complete old/new identities: '+name)
        if json_scripts.findall(source) != json_scripts.findall(current):
            raise ValueError('Team records must preserve every embedded source JSON byte')
        if not set(re.findall(r'\bid="([^\"]+)"',source)) <= set(re.findall(r'\bid="([^\"]+)"',current)):
            raise ValueError('Team records cannot remove existing navigation/source IDs')
        if project_html(current,name) != current:
            raise ValueError('Team records must retain canonical named achievement references')
        if name == A02_HISTORY_ROUTE:
            begin,end='<!-- A02_ACADEMIC_HISTORY:BEGIN -->','<!-- A02_ACADEMIC_HISTORY:END -->'
            if any(value.count(begin)!=1 or value.count(end)!=1 for value in (source,current)):
                raise ValueError('Team topic requires one complete existing A02 marker')
            strip=lambda value:value[:value.index(begin)]+'<A02-HISTORY/>'+value[value.index(end)+len(end):]
            if strip(source) != strip(current):
                raise ValueError('Team topic may change only inside the A02 historical marker')
            background = r'<article\b[^>]*\bid="a02-technical-records"[^>]*>.*?</article>'
            if (len(re.findall(background, source, re.S)) != 1
                    or re.findall(background, source, re.S) != re.findall(background, current, re.S)):
                raise ValueError('Team records must preserve the complete existing technical-background article')
            team = r'<article\b[^>]*\bid="a02-team-records"[^>]*>.*?</article>'
            if (len(re.findall(team, current, re.S)) != 1
                    or current.index('id="a02-team-records"') > current.index('id="a02-technical-records"')):
                raise ValueError('Attributed A02 team records must precede other-team technical background')
            if re.findall(team, source, re.S) != re.findall(team, current, re.S):
                raise ValueError('Cited sources must preserve the complete existing team-history article')
            trace = r'<article\b[^>]*\bid="a02-source-trace"[^>]*>.*?</article>'
            if len(re.findall(trace, current, re.S)) != 1:
                raise ValueError('Expected one independent A02 cited-source trace article')
        else:
            pattern = (r'<section\b[^>]*\bid="ai-a02"[^>]*>.*?</section>' if name==AI_RESEARCH_ROUTE
                       else r'<article\b[^>]*\bid="heritage-line-a02"[^>]*>.*?</article>')
            if (len(re.findall(pattern,source,re.S))!=1 or len(re.findall(pattern,current,re.S))!=1
                    or re.sub(pattern,'<A02-ONLY/>',source,flags=re.S)!=re.sub(pattern,'<A02-ONLY/>',current,flags=re.S)):
                raise ValueError('Team records changed outside the A02 entry: '+name)
        updated[name]={**old,'sha256':item['new_sha256'],'bytes':item['new_bytes'],'presentation_id':PRESENTATION_V19_ID}
    for name in (AI_RESEARCH_DOCUMENT,A02_HISTORY_DOCUMENT):
        prose=holdings_predecessor_bytes(root,name).decode('utf-8')
        if project_markdown(prose)!=prose:
            raise ValueError('Team prose lost canonical named achievement references: '+name)
    for name,expected in updated.items():
        member=holdings_predecessor_binding(root,'site/'+name)
        if member['sha256']!=expected['sha256'] or member['bytes']!=expected['bytes']:
            raise ValueError('Team records changed an unlisted website byte: '+name)
    # Replay v19 from exact reconstructed bytes; inspect only the final layer.
    if not (root/PRESENTATION_V20_PATH).exists():
        from render_a02_history import inspect_a02_history
        from render_ai_research import inspect_ai_research
        for label,check in (('A02 history',inspect_a02_history(root)),('AI record',inspect_ai_research(root))):
            if check.get('status')!='passed':
                raise ValueError(label+' differs from its source-derived rendering: '+str(check.get('errors',[])))
    members=publication_members(root,updated)
    report={'path':PRESENTATION_V19_PATH,'sha256':digest(path),'presentation_id':PRESENTATION_V19_ID,
        'publication_kind':required['publication_kind'],'changed_paths':sorted(A02_ORIGINAL_FOLLOWUP_ROUTES),'added_paths':[],
        'changed_achievement_lines':['A02'],'previous_presentation_commit':PRESENTATION_V19_PREVIOUS_COMMIT,
        'exact_predecessor_reconstruction':True,'existing_A02_history_paper_technical_team_and_inventory_preserved':True,
        'only_final_A02_AI_record_summary_changed':True,
        'source_derived_rendering':True,'homepage_A01_and_original_source_data_unchanged':True,
        'original_embedded_json_bytes_preserved':True,'published_member_count_with_marker':len(members)+1,
        **{key:required[key] for key in ('scientific_review_status','scientific_data_unchanged',
            'historical_achievement_independent_of_AI_review','release_eligible','M0_resumed')}}
    return apply_a02_holdings_presentation(root, updated,
        {**report,'presentation_chain':[*previous_report['presentation_chain'],report]})


def validate_a02_holdings_history(old_history: dict, history: dict) -> None:
    """Keep catalogue identification separate from unobserved historical pages."""
    mutable = {'source_trace', 'sources'}
    if ({k:v for k,v in old_history.items() if k not in mutable}
            != {k:v for k,v in history.items() if k not in mutable}):
        raise ValueError('Holdings may not change A02 history, pending, AI scope, inventory or scientific status')
    old_sources, sources = old_history.get('sources'), history.get('sources')
    if (not isinstance(old_sources, list) or len(old_sources) != 22
            or not isinstance(sources, list) or len(sources) <= len(old_sources)
            or sources[:len(old_sources)] != old_sources):
        raise ValueError('Holdings must preserve the exact twenty-two-source prefix and append evidence')
    old_trace, trace = old_history.get('source_trace'), history.get('source_trace')
    ids = ['a02-trace-interview', 'a02-trace-book2009']
    if (not isinstance(old_trace, list) or not isinstance(trace, list)
            or len(old_trace) != 2 or len(trace) != 2
            or any(not isinstance(row, dict) for row in trace)
            or [row.get('id') for row in old_trace] != ids
            or [row.get('id') for row in trace] != ids
            or trace[0] != old_trace[0] or trace[1] == old_trace[1]
            or trace[1].get('original_obtained') is not False
            or trace[1].get('volume_confirmed') is not False):
        raise ValueError('Only the existing book trace may change; interview and unresolved target-page status are fixed')
    extent = trace[1].get('catalogue_extent')
    expected_keys = {'volume_count', 'page_counts_as_catalogued',
                     'volume_title_mapping_confirmed', 'cited_page_volume_confirmed',
                     'original_book_pages_obtained'}
    if (not isinstance(extent, dict) or set(extent) != expected_keys
            or type(extent.get('volume_count')) is not int or extent['volume_count'] != 3
            or not isinstance(extent.get('page_counts_as_catalogued'), list)
            or any(type(value) is not int for value in extent['page_counts_as_catalogued'])
            or extent['page_counts_as_catalogued'] != [377, 454, 630]
            or any(extent.get(key) is not False for key in (
                'volume_title_mapping_confirmed', 'cited_page_volume_confirmed',
                'original_book_pages_obtained'))):
        raise ValueError('Catalogue extent must remain exactly three stated page counts with unresolved mapping and original pages')


def apply_a02_holdings_presentation(root: Path, entries: dict, previous_report: dict) -> tuple[dict, dict]:
    """Publish only catalogue-qualified book trace and the final A02 AI-record summary."""
    if not (root/PRESENTATION_V20_PATH).exists():
        return entries, previous_report
    if digest(project_file(root, PRESENTATION_V19_PATH)) != PRESENTATION_V19_SHA256:
        raise ValueError('The preceding A02 original-followup presentation v19 is immutable')
    path = project_file(root, PRESENTATION_V20_PATH); data = read_json(path)
    documents = [{'path': name, 'sha256': hashlib.sha256(boundary_predecessor_bytes(root, name)).hexdigest(),
                  'bytes': len(boundary_predecessor_bytes(root, name))} for name in A02_HOLDINGS_DOCUMENTS]
    required = {'schema_version': '20.0', 'presentation_id': PRESENTATION_V20_ID,
        'publication_kind': 'platform_a02_holdings',
        'previous_presentation_commit': PRESENTATION_V20_PREVIOUS_COMMIT,
        'previous_presentation': {'path': PRESENTATION_V19_PATH, 'sha256': PRESENTATION_V19_SHA256},
        'original_baseline_sha256': BASELINE_SHA256, 'original_archive_sha256': ARCHIVE_SHA256,
        'allowed_html_paths': sorted(A02_HOLDINGS_ROUTES), 'added_html_paths': [], 'additions': [],
        'allowed_achievement_lines': ['A02'], 'editorial_documents': documents,
        'protected_website_members': {name: {'sha256': row['sha256'], 'bytes': row['bytes']}
            for name, row in entries.items() if name not in A02_HOLDINGS_ROUTES},
        'reconstruction_kind': 'deduplicated_exact_utf8_text_edits',
        'scientific_review_status': 'review_required', 'release_eligible': False,
        'scientific_data_unchanged': True, 'M0_resumed': False,
        'historical_achievement_independent_of_AI_review': True}
    if (not isinstance(data, dict) or any(data.get(key) != value for key, value in required.items())
            or any(data.get(key) is not required[key] for key in ('release_eligible',
                'scientific_data_unchanged', 'M0_resumed', 'historical_achievement_independent_of_AI_review'))
            or any(type(data.get(key)) is not int or data[key] != 0 for key in ('new_quantum_calls', 'new_model_API_calls'))
            or not isinstance(data.get('authorization'), str) or not data['authorization'].strip()):
        raise ValueError('Unsupported bounded A02 holdings presentation v20')
    files, pool = data.get('reversible_text_files'), data.get('reverse_text_patch_pool')
    if (not isinstance(files, list) or not files or not isinstance(pool, list) or not pool
            or any(not isinstance(row, dict) or row.get('path') not in A02_HOLDINGS_PREDECESSOR_FILES for row in files)
            or len({row['path'] for row in files}) != len(files)
            or any(not isinstance(row.get('edits'), list) or not row['edits'] or any(
                not isinstance(edit, dict) or type(edit.get('replacement')) is not int for edit in row['edits']) for row in files)):
        raise ValueError('A02 holdings records may enumerate only the seven fixed predecessor text files')
    if {edit['replacement'] for row in files for edit in row['edits']} != set(range(len(pool))):
        raise ValueError('Team replacement pool must contain exactly its used segments')
    changed = set()
    for name, (sha, size) in A02_HOLDINGS_PREDECESSOR_FILES.items():
        old = holdings_predecessor_bytes(root, name)
        if hashlib.sha256(old).hexdigest() != sha or len(old) != size:
            raise ValueError('A02 holdings predecessor differs from fixed 11a927d: '+name)
        if old != boundary_predecessor_bytes(root, name):
            changed.add(name)
    if {row['path'] for row in files} != changed:
        raise ValueError('Team patches must enumerate every and only changed predecessor file')
    old_ai = json.loads(holdings_predecessor_bytes(root, AI_RESEARCH_CONTENT))
    current_ai = json.loads(boundary_predecessor_bytes(root, AI_RESEARCH_CONTENT))
    try:
        summary = current_ai['lines'][1]['records'][-1]['summary']
    except (KeyError, IndexError, TypeError) as error:
        raise ValueError('Missing final A02 AI-record summary') from error
    if (not isinstance(summary, str) or not summary.strip()
            or summary == old_ai['lines'][1]['records'][-1]['summary']):
        raise ValueError('The final A02 AI-record summary must contain the authorized refinement')
    expected_ai = json.loads(json.dumps(old_ai))
    expected_ai['lines'][1]['records'][-1]['summary'] = summary
    if current_ai != expected_ai:
        raise ValueError('Only the final A02 AI-record summary may change in the complete AI registry')
    old_history = json.loads(holdings_predecessor_bytes(root, A02_HISTORY_CONTENT))
    history = json.loads(boundary_predecessor_bytes(root, A02_HISTORY_CONTENT))
    validate_a02_holdings_history(old_history, history)
    changes = data.get('changes')
    if (not isinstance(changes, list) or any(not isinstance(row, dict) for row in changes)
            or [row.get('path') for row in changes] != sorted(A02_HOLDINGS_ROUTES)):
        raise ValueError('Original follow-up may update only the A02 topic and AI record routes')
    from public_line_labels import project_html, project_markdown
    json_scripts = re.compile(r'<script\b[^>]*\btype\s*=\s*[\"\']application/(?:ld\+)?json[\"\'][^>]*>.*?</script\s*>', re.I | re.S)
    updated = {name:dict(row) for name,row in entries.items()}
    for item in changes:
        name=item['path']; old=entries[name]
        before=holdings_predecessor_bytes(root,'site/'+name); after=boundary_predecessor_bytes(root,'site/'+name)
        source,current=before.decode('utf-8'),after.decode('utf-8')
        if (item.get('old_sha256') != old['sha256'] or item.get('old_bytes') != old['bytes']
                or hashlib.sha256(before).hexdigest() != old['sha256'] or len(before) != old['bytes']
                or item.get('new_sha256') != hashlib.sha256(after).hexdigest() or item.get('new_bytes') != len(after)
                or before == after or not isinstance(item.get('reason'),str) or not item['reason'].strip()):
            raise ValueError('Team HTML differs from complete old/new identities: '+name)
        if json_scripts.findall(source) != json_scripts.findall(current):
            raise ValueError('Team records must preserve every embedded source JSON byte')
        if not set(re.findall(r'\bid="([^\"]+)"',source)) <= set(re.findall(r'\bid="([^\"]+)"',current)):
            raise ValueError('Team records cannot remove existing navigation/source IDs')
        if project_html(current,name) != current:
            raise ValueError('Team records must retain canonical named achievement references')
        if name == A02_HISTORY_ROUTE:
            begin,end='<!-- A02_ACADEMIC_HISTORY:BEGIN -->','<!-- A02_ACADEMIC_HISTORY:END -->'
            if any(value.count(begin)!=1 or value.count(end)!=1 for value in (source,current)):
                raise ValueError('Team topic requires one complete existing A02 marker')
            strip=lambda value:value[:value.index(begin)]+'<A02-HISTORY/>'+value[value.index(end)+len(end):]
            if strip(source) != strip(current):
                raise ValueError('Team topic may change only inside the A02 historical marker')
            background = r'<article\b[^>]*\bid="a02-technical-records"[^>]*>.*?</article>'
            if (len(re.findall(background, source, re.S)) != 1
                    or re.findall(background, source, re.S) != re.findall(background, current, re.S)):
                raise ValueError('Team records must preserve the complete existing technical-background article')
            team = r'<article\b[^>]*\bid="a02-team-records"[^>]*>.*?</article>'
            if (len(re.findall(team, current, re.S)) != 1
                    or current.index('id="a02-team-records"') > current.index('id="a02-technical-records"')):
                raise ValueError('Attributed A02 team records must precede other-team technical background')
            if re.findall(team, source, re.S) != re.findall(team, current, re.S):
                raise ValueError('Cited sources must preserve the complete existing team-history article')
            trace = r'<article\b[^>]*\bid="a02-source-trace"[^>]*>.*?</article>'
            if len(re.findall(trace, current, re.S)) != 1:
                raise ValueError('Expected one independent A02 cited-source trace article')
        else:
            pattern = (r'<section\b[^>]*\bid="ai-a02"[^>]*>.*?</section>' if name==AI_RESEARCH_ROUTE
                       else r'<article\b[^>]*\bid="heritage-line-a02"[^>]*>.*?</article>')
            if (len(re.findall(pattern,source,re.S))!=1 or len(re.findall(pattern,current,re.S))!=1
                    or re.sub(pattern,'<A02-ONLY/>',source,flags=re.S)!=re.sub(pattern,'<A02-ONLY/>',current,flags=re.S)):
                raise ValueError('Team records changed outside the A02 entry: '+name)
        updated[name]={**old,'sha256':item['new_sha256'],'bytes':item['new_bytes'],'presentation_id':PRESENTATION_V20_ID}
    for name in (AI_RESEARCH_DOCUMENT,A02_HISTORY_DOCUMENT):
        prose=boundary_predecessor_bytes(root,name).decode('utf-8')
        if project_markdown(prose)!=prose:
            raise ValueError('Team prose lost canonical named achievement references: '+name)
    for name,expected in updated.items():
        member=boundary_predecessor_bytes(root,'site/'+name)
        if hashlib.sha256(member).hexdigest()!=expected['sha256'] or len(member)!=expected['bytes']:
            raise ValueError('Team records changed an unlisted website byte: '+name)
    # Historical v20 bytes are reconstructed before checking the final layer.
    if not (root/PRESENTATION_V21_PATH).exists():
        from render_a02_history import inspect_a02_history
        from render_ai_research import inspect_ai_research
        for label,check in (('A02 history',inspect_a02_history(root)),('AI record',inspect_ai_research(root))):
            if check.get('status')!='passed':
                raise ValueError(label+' differs from its source-derived rendering: '+str(check.get('errors',[])))
    members=publication_members(root,updated)
    report={'path':PRESENTATION_V20_PATH,'sha256':digest(path),'presentation_id':PRESENTATION_V20_ID,
        'publication_kind':required['publication_kind'],'changed_paths':sorted(A02_HOLDINGS_ROUTES),'added_paths':[],
        'changed_achievement_lines':['A02'],'previous_presentation_commit':PRESENTATION_V20_PREVIOUS_COMMIT,
        'exact_predecessor_reconstruction':True,'existing_A02_history_paper_technical_team_and_inventory_preserved':True,
        'only_final_A02_AI_record_summary_changed':True,
        'only_book_trace_and_append_only_sources_changed':True,
        'interview_trace_unchanged':True,
        'catalogue_extent_without_volume_or_original_page_promotion':True,
        'source_derived_rendering':True,'homepage_A01_and_original_source_data_unchanged':True,
        'original_embedded_json_bytes_preserved':True,'published_member_count_with_marker':len(members)+1,
        **{key:required[key] for key in ('scientific_review_status','scientific_data_unchanged',
            'historical_achievement_independent_of_AI_review','release_eligible','M0_resumed')}}
    return apply_a02_boundary_presentation(root, updated,
        {**report,'presentation_chain':[*previous_report['presentation_chain'],report]})



def apply_a02_boundary_presentation(root: Path, entries: dict, previous_report: dict) -> tuple[dict, dict]:
    """Correct only the acquired 1980 paper's evidence description and its A02 AI summary."""
    if not (root/PRESENTATION_V21_PATH).exists():
        return entries, previous_report
    if digest(project_file(root, PRESENTATION_V20_PATH)) != PRESENTATION_V20_SHA256:
        raise ValueError('The preceding A02 holdings presentation v20 is immutable')
    path = project_file(root, PRESENTATION_V21_PATH); data = read_json(path)
    documents = [{'path': name, 'sha256': hashlib.sha256(original_evidence_predecessor_bytes(root, name)).hexdigest(),
                  'bytes': len(original_evidence_predecessor_bytes(root, name))} for name in A02_BOUNDARY_DOCUMENTS]
    required = {'schema_version': '21.0', 'presentation_id': PRESENTATION_V21_ID,
        'publication_kind': 'platform_a02_evidence_boundary',
        'previous_presentation_commit': PRESENTATION_V21_PREVIOUS_COMMIT,
        'previous_presentation': {'path': PRESENTATION_V20_PATH, 'sha256': PRESENTATION_V20_SHA256},
        'original_baseline_sha256': BASELINE_SHA256, 'original_archive_sha256': ARCHIVE_SHA256,
        'allowed_html_paths': sorted(A02_BOUNDARY_ROUTES), 'added_html_paths': [], 'additions': [],
        'allowed_achievement_lines': ['A02'], 'editorial_documents': documents,
        'protected_website_members': {name: {'sha256': row['sha256'], 'bytes': row['bytes']}
            for name, row in entries.items() if name not in A02_BOUNDARY_ROUTES},
        'reconstruction_kind': 'deduplicated_exact_utf8_text_edits',
        'scientific_review_status': 'review_required', 'release_eligible': False,
        'scientific_data_unchanged': True, 'M0_resumed': False,
        'historical_achievement_independent_of_AI_review': True}
    if (not isinstance(data, dict) or any(data.get(key) != value for key, value in required.items())
            or any(data.get(key) is not required[key] for key in ('release_eligible',
                'scientific_data_unchanged', 'M0_resumed', 'historical_achievement_independent_of_AI_review'))
            or any(type(data.get(key)) is not int or data[key] != 0 for key in ('new_quantum_calls', 'new_model_API_calls'))
            or not isinstance(data.get('authorization'), str) or not data['authorization'].strip()):
        raise ValueError('Unsupported bounded A02 evidence correction v21')
    files, pool = data.get('reversible_text_files'), data.get('reverse_text_patch_pool')
    if (not isinstance(files, list) or not files or not isinstance(pool, list) or not pool
            or any(not isinstance(row, dict) or row.get('path') not in A02_BOUNDARY_PREDECESSOR_FILES for row in files)
            or len({row['path'] for row in files}) != len(files)
            or any(not isinstance(row.get('edits'), list) or not row['edits'] or any(
                not isinstance(edit, dict) or type(edit.get('replacement')) is not int for edit in row['edits']) for row in files)):
        raise ValueError('A02 evidence correction may enumerate only seven fixed predecessor files')
    if {edit['replacement'] for row in files for edit in row['edits']} != set(range(len(pool))):
        raise ValueError('A02 evidence correction requires exactly its used replacement segments')
    changed = set()
    for name, (sha, size) in A02_BOUNDARY_PREDECESSOR_FILES.items():
        old = boundary_predecessor_bytes(root, name)
        if hashlib.sha256(old).hexdigest() != sha or len(old) != size:
            raise ValueError('A02 evidence predecessor differs from fixed 7a53bc6: '+name)
        if old != original_evidence_predecessor_bytes(root, name):
            changed.add(name)
    if {row['path'] for row in files} != changed or changed != set(A02_BOUNDARY_PREDECESSOR_FILES):
        raise ValueError('A02 evidence correction must enumerate every and only its seven changed files')
    old_history = json.loads(boundary_predecessor_bytes(root, A02_HISTORY_CONTENT))
    expected_history = json.loads(json.dumps(old_history))
    expected_history['paper']['observations'][1]['finding'] = A02_BOUNDARY_FINDING
    expected_history['paper']['observations'][1]['locator'] = A02_BOUNDARY_LOCATOR
    if json.loads(original_evidence_predecessor_bytes(root, A02_HISTORY_CONTENT)) != expected_history:
        raise ValueError('Only the selected 1980 observation finding and locator may change')
    old_ai = json.loads(boundary_predecessor_bytes(root, AI_RESEARCH_CONTENT))
    expected_ai = json.loads(json.dumps(old_ai))
    expected_ai['lines'][1]['records'][2]['summary'] = A02_BOUNDARY_AI_SUMMARY
    expected_ai['lines'][1]['boundaries'][1] = A02_BOUNDARY_AI_LIMIT
    if json.loads(original_evidence_predecessor_bytes(root, AI_RESEARCH_CONTENT)) != expected_ai:
        raise ValueError('Only the corresponding A02 AI summary and boundary sentence may change')
    changes = data.get('changes')
    if (not isinstance(changes, list) or any(not isinstance(row, dict) for row in changes)
            or [row.get('path') for row in changes] != sorted(A02_BOUNDARY_ROUTES)):
        raise ValueError('A02 evidence correction may change only its topic and AI record routes')
    from public_line_labels import project_html, project_markdown
    json_scripts = re.compile(r'<script\b[^>]*\btype\s*=\s*["\']application/(?:ld\+)?json["\'][^>]*>.*?</script\s*>', re.I | re.S)
    updated = {name: dict(row) for name, row in entries.items()}
    for item in changes:
        name = item['path']; old = entries[name]
        before = boundary_predecessor_bytes(root, 'site/'+name)
        after = original_evidence_predecessor_bytes(root, 'site/'+name)
        source, current = before.decode('utf-8'), after.decode('utf-8')
        if (item.get('old_sha256') != old['sha256'] or item.get('old_bytes') != old['bytes']
                or hashlib.sha256(before).hexdigest() != old['sha256'] or len(before) != old['bytes']
                or item.get('new_sha256') != hashlib.sha256(after).hexdigest() or item.get('new_bytes') != len(after)
                or before == after or not isinstance(item.get('reason'), str) or not item['reason'].strip()):
            raise ValueError('A02 evidence HTML differs from complete old/new identities: '+name)
        if json_scripts.findall(source) != json_scripts.findall(current):
            raise ValueError('A02 evidence correction must retain every embedded JSON byte')
        if set(re.findall(r'\bid="([^\"]+)"', source)) != set(re.findall(r'\bid="([^\"]+)"', current)):
            raise ValueError('A02 evidence correction must retain all navigation and source IDs')
        if project_html(current, name) != current:
            raise ValueError('A02 evidence correction lost canonical named achievement references')
        pattern = (r'<article\b[^>]*\bid="a02-vdf-1980"[^>]*>.*?</article>' if name == A02_HISTORY_ROUTE
                   else r'<section\b[^>]*\bid="ai-a02"[^>]*>.*?</section>')
        if (len(re.findall(pattern, source, re.S)) != 1 or len(re.findall(pattern, current, re.S)) != 1
                or re.sub(pattern, '<A02-CORRECTION/>', source, flags=re.S) != re.sub(pattern, '<A02-CORRECTION/>', current, flags=re.S)):
            raise ValueError('A02 evidence correction changed outside the specific source article: '+name)
        updated[name] = {**old, 'sha256': item['new_sha256'], 'bytes': item['new_bytes'], 'presentation_id': PRESENTATION_V21_ID}
    for name in (AI_RESEARCH_DOCUMENT, A02_HISTORY_DOCUMENT):
        prose = original_evidence_predecessor_bytes(root, name).decode('utf-8')
        if project_markdown(prose) != prose:
            raise ValueError('A02 evidence prose lost canonical named achievement references: '+name)
    for name, expected in updated.items():
        member = original_evidence_predecessor_bytes(root, 'site/'+name)
        if hashlib.sha256(member).hexdigest() != expected['sha256'] or len(member) != expected['bytes']:
            raise ValueError('A02 evidence correction changed an unlisted website byte: '+name)
    # v21 is checked against exactly reconstructed bytes; v22 checks final rendering.
    if not (root/PRESENTATION_V22_PATH).exists():
        from render_a02_history import inspect_a02_history
        from render_ai_research import inspect_ai_research
        for label, check in (('A02 history', inspect_a02_history(root)), ('AI record', inspect_ai_research(root))):
            if check.get('status') != 'passed':
                raise ValueError(label+' differs from its source-derived rendering: '+str(check.get('errors', [])))
    members = publication_members(root, updated)
    report = {'path': PRESENTATION_V21_PATH, 'sha256': digest(path), 'presentation_id': PRESENTATION_V21_ID,
        'publication_kind': required['publication_kind'], 'changed_paths': sorted(A02_BOUNDARY_ROUTES), 'added_paths': [],
        'changed_achievement_lines': ['A02'], 'previous_presentation_commit': PRESENTATION_V21_PREVIOUS_COMMIT,
        'exact_predecessor_reconstruction': True, 'source_derived_rendering': True,
        'only_selected_1980_observation_and_A02_AI_description_corrected': True,
        'original_history_team_background_source_trace_and_inventory_preserved': True,
        'homepage_A01_and_original_source_data_unchanged': True,
        'original_embedded_json_bytes_preserved': True, 'published_member_count_with_marker': len(members)+1,
        **{key: required[key] for key in ('scientific_review_status', 'scientific_data_unchanged',
            'historical_achievement_independent_of_AI_review', 'release_eligible', 'M0_resumed')}}
    return apply_original_evidence_presentation(root, updated,
        {**report, 'presentation_chain': [*previous_report['presentation_chain'], report]})


def apply_original_evidence_presentation(root: Path, entries: dict, previous_report: dict) -> tuple[dict, dict]:
    """Integrate six existing original-paper/attachment acquisition records."""
    if not (root/PRESENTATION_V22_PATH).exists():
        return entries, previous_report
    if digest(project_file(root, PRESENTATION_V21_PATH)) != PRESENTATION_V21_SHA256:
        raise ValueError('The preceding v21 presentation is immutable')
    path = project_file(root, PRESENTATION_V22_PATH); data = read_json(path)
    documents = [{'path': name, 'sha256': hashlib.sha256(a06_summary_predecessor_bytes(root, name)).hexdigest(),
                  'bytes': len(a06_summary_predecessor_bytes(root, name))} for name in ORIGINAL_EVIDENCE_DOCUMENTS]
    required = {'schema_version': '22.0', 'presentation_id': PRESENTATION_V22_ID,
        'publication_kind': 'platform_original_evidence_integration',
        'previous_presentation_commit': PRESENTATION_V22_PREVIOUS_COMMIT,
        'previous_presentation': {'path': PRESENTATION_V21_PATH, 'sha256': PRESENTATION_V21_SHA256},
        'original_baseline_sha256': BASELINE_SHA256, 'original_archive_sha256': ARCHIVE_SHA256,
        'allowed_html_paths': sorted(ORIGINAL_EVIDENCE_ROUTES), 'added_html_paths': [], 'additions': [],
        'allowed_achievement_lines': ['A03', 'A04', 'A05', 'A06', 'A07', 'A08'], 'editorial_documents': documents,
        'protected_website_members': {name: {'sha256': row['sha256'], 'bytes': row['bytes']}
            for name, row in entries.items() if name not in ORIGINAL_EVIDENCE_ROUTES},
        'reconstruction_kind': 'deduplicated_exact_utf8_text_edits',
        'scientific_review_status': 'review_required', 'release_eligible': False,
        'source_status_date': '2026-11-16',
        'scientific_data_unchanged': True, 'M0_resumed': False,
        'historical_achievement_independent_of_AI_review': True}
    if (not isinstance(data, dict) or any(data.get(key) != value for key, value in required.items())
            or any(data.get(key) is not required[key] for key in ('release_eligible',
                'scientific_data_unchanged', 'M0_resumed', 'historical_achievement_independent_of_AI_review'))
            or any(type(data.get(key)) is not int or data[key] != 0 for key in ('new_quantum_calls', 'new_model_API_calls'))
            or not isinstance(data.get('authorization'), str) or not data['authorization'].strip()):
        raise ValueError('Unsupported bounded original-evidence integration v22')
    files, pool = data.get('reversible_text_files'), data.get('reverse_text_patch_pool')
    if (not isinstance(files, list) or not files or not isinstance(pool, list) or not pool
            or any(not isinstance(row, dict) or row.get('path') not in ORIGINAL_EVIDENCE_PREDECESSOR_FILES for row in files)
            or len({row['path'] for row in files}) != len(files)
            or any(not isinstance(row.get('edits'), list) or not row['edits'] or any(
                not isinstance(edit, dict) or type(edit.get('replacement')) is not int for edit in row['edits']) for row in files)):
        raise ValueError('Original-evidence integration may enumerate only its four fixed predecessor files')
    if {edit['replacement'] for row in files for edit in row['edits']} != set(range(len(pool))):
        raise ValueError('Original-evidence integration requires exactly its used replacement segments')
    changed = set()
    for name, (sha, size) in ORIGINAL_EVIDENCE_PREDECESSOR_FILES.items():
        old = original_evidence_predecessor_bytes(root, name)
        if hashlib.sha256(old).hexdigest() != sha or len(old) != size:
            raise ValueError('Original-evidence predecessor differs from fixed e6b4273: '+name)
        if old != a06_summary_predecessor_bytes(root, name):
            changed.add(name)
    if {row['path'] for row in files} != changed or changed != set(ORIGINAL_EVIDENCE_PREDECESSOR_FILES):
        raise ValueError('Original-evidence integration must enumerate all and only its four changed files')
    old_ai = json.loads(original_evidence_predecessor_bytes(root, AI_RESEARCH_CONTENT))
    expected_ai = json.loads(json.dumps(old_ai))
    expected_ai['date'] = '2026-11-16'
    for ident, update in ORIGINAL_EVIDENCE_UPDATES.items():
        line = expected_ai['lines'][int(ident[1:])-1]
        fields = {'summary', 'appended_links'} if ident == 'A03' else {'summary', 'next_step'}
        if line['id'] != ident or set(update) != fields:
            raise ValueError('Unexpected original-evidence update fields')
        if not isinstance(update['summary'], str) or not update['summary'].strip():
            raise ValueError('Original-evidence summary must be nonempty')
        line['records'][0]['summary'] = update['summary']
        additions = update.get('appended_links', [])
        if (not isinstance(additions, list) or bool(additions) != (ident == 'A03')
                or any(not isinstance(item, dict)
                or item.get('kind') != 'external'
                or not re.match(r'https://(?:www\.)?sioc-journal\.cn/', item.get('url', ''))
                for item in additions)):
            raise ValueError('Only appended official HTTPS original-paper links are permitted')
        line['records'][0]['links'].extend(additions)
        if ident != 'A03':
            line['next_step'] = update['next_step']
    if set(ORIGINAL_EVIDENCE_UPDATES) != {'A03', 'A04', 'A05', 'A06', 'A07', 'A08'}:
        raise ValueError('Expected exactly six original-paper/attachment record updates')
    if json.loads(a06_summary_predecessor_bytes(root, AI_RESEARCH_CONTENT)) != expected_ai:
        raise ValueError('Only the fixed status date, six summaries, one append-only link list and five next steps may change')
    changes = data.get('changes')
    if (not isinstance(changes, list) or len(changes) != 1 or not isinstance(changes[0], dict)
            or changes[0].get('path') != AI_RESEARCH_ROUTE):
        raise ValueError('Original-evidence integration may change only the existing research page')
    from public_line_labels import project_html, project_markdown
    item = changes[0]; name = AI_RESEARCH_ROUTE; old = entries[name]
    before = original_evidence_predecessor_bytes(root, 'site/'+name)
    after = a06_summary_predecessor_bytes(root, 'site/'+name)
    source, current = before.decode('utf-8'), after.decode('utf-8')
    if (item.get('old_sha256') != old['sha256'] or item.get('old_bytes') != old['bytes']
            or hashlib.sha256(before).hexdigest() != old['sha256'] or len(before) != old['bytes']
            or item.get('new_sha256') != hashlib.sha256(after).hexdigest() or item.get('new_bytes') != len(after)
            or before == after or not isinstance(item.get('reason'), str) or not item['reason'].strip()):
        raise ValueError('Original-evidence HTML differs from complete old/new identities')
    json_scripts = re.compile(r'<script\b[^>]*\btype\s*=\s*["\']application/(?:ld\+)?json["\'][^>]*>.*?</script\s*>', re.I | re.S)
    if json_scripts.findall(source) != json_scripts.findall(current):
        raise ValueError('Original-evidence integration must retain every embedded JSON byte')
    if set(re.findall(r'\bid="([^\"]+)"', source)) != set(re.findall(r'\bid="([^\"]+)"', current)):
        raise ValueError('Original-evidence integration must retain every navigation and source ID')
    if project_html(current, name) != current:
        raise ValueError('Original-evidence integration lost canonical achievement names')
    masked_before, masked_after = source, current
    for ident in ('a03', 'a04', 'a05', 'a06', 'a07', 'a08'):
        pattern = r'<section\b[^>]*\bid="ai-'+ident+r'"[^>]*>.*?</section>'
        if len(re.findall(pattern, source, re.S)) != 1 or len(re.findall(pattern, current, re.S)) != 1:
            raise ValueError('Original-evidence integration requires exactly one section per selected line')
        masked_before = re.sub(pattern, '<ORIGINAL-EVIDENCE-'+ident+'/>', masked_before, flags=re.S)
        masked_after = re.sub(pattern, '<ORIGINAL-EVIDENCE-'+ident+'/>', masked_after, flags=re.S)
    old_date = '资料状态截至'+old_ai['date']+'。'
    new_date = '资料状态截至2026-11-16。'
    if masked_before.count(old_date) != 1 or masked_after.count(new_date) != 1:
        raise ValueError('Expected exactly one old and current research-page status date')
    if masked_before.replace(old_date, new_date) != masked_after:
        raise ValueError('Original-evidence integration changed outside its six research sections and fixed footer date')
    prose = a06_summary_predecessor_bytes(root, AI_RESEARCH_DOCUMENT).decode('utf-8')
    if project_markdown(prose) != prose:
        raise ValueError('Original-evidence document lost canonical achievement names')
    updated = {name: dict(row) for name, row in entries.items()}
    updated[name] = {**old, 'sha256': item['new_sha256'], 'bytes': item['new_bytes'], 'presentation_id': PRESENTATION_V22_ID}
    for member_name, expected in updated.items():
        member = a06_summary_predecessor_bytes(root, 'site/'+member_name)
        if hashlib.sha256(member).hexdigest() != expected['sha256'] or len(member) != expected['bytes']:
            raise ValueError('Original-evidence integration changed an unlisted website byte: '+member_name)
    # Historical v22 uses its exact reconstructed bytes; v23 validates final rendering.
    if not (root/PRESENTATION_V23_PATH).exists():
        from render_ai_research import inspect_ai_research
        check = inspect_ai_research(root)
        if check.get('status') != 'passed':
            raise ValueError('Original-evidence final page differs from source rendering: '+str(check.get('errors', [])))
    members = publication_members(root, updated)
    report = {'path': PRESENTATION_V22_PATH, 'sha256': digest(path), 'presentation_id': PRESENTATION_V22_ID,
        'publication_kind': required['publication_kind'], 'changed_paths': [AI_RESEARCH_ROUTE], 'added_paths': [],
        'changed_achievement_lines': ['A03', 'A04', 'A05', 'A06', 'A07', 'A08'],
        'previous_presentation_commit': PRESENTATION_V22_PREVIOUS_COMMIT,
        'exact_predecessor_reconstruction': True, 'source_derived_rendering': True,
        'only_six_existing_first_records_and_five_next_steps_changed': True,
        'source_and_derived_status_date_fixed_to_20261116': True,
        'A04_through_A08_existing_links_preserved_without_unverified_new_links': True,
        'all_original_authors_source_ids_and_links_preserved': True,
        'homepage_and_historical_achievement_pages_unchanged': True,
        'original_embedded_json_bytes_preserved': True,
        'original_scans_and_private_evidence_registers_not_published': True,
        'published_member_count_with_marker': len(members)+1,
        **{key: required[key] for key in ('scientific_review_status', 'scientific_data_unchanged',
            'historical_achievement_independent_of_AI_review', 'release_eligible', 'M0_resumed')}}
    return apply_a06_summary_presentation(root, updated,
        {**report, 'presentation_chain': [*previous_report['presentation_chain'], report]})


def apply_a06_summary_presentation(root: Path, entries: dict, previous_report: dict) -> tuple[dict, dict]:
    """Clarify only the existing A06 first-record summary and its derived prose."""
    if not (root/PRESENTATION_V23_PATH).exists():
        return entries, previous_report
    if digest(project_file(root, PRESENTATION_V22_PATH)) != PRESENTATION_V22_SHA256:
        raise ValueError('The preceding v22 presentation is immutable')
    path = project_file(root, PRESENTATION_V23_PATH); data = read_json(path)
    documents = [{'path': name, 'sha256': hashlib.sha256(literature_predecessor_bytes(root, name)).hexdigest(),
                  'bytes': len(literature_predecessor_bytes(root, name))} for name in A06_SUMMARY_DOCUMENTS]
    required = {'schema_version': '23.0', 'presentation_id': PRESENTATION_V23_ID,
        'publication_kind': 'platform_a06_authors_methods_clarification',
        'previous_presentation_commit': PRESENTATION_V23_PREVIOUS_COMMIT,
        'previous_presentation': {'path': PRESENTATION_V22_PATH, 'sha256': PRESENTATION_V22_SHA256},
        'original_baseline_sha256': BASELINE_SHA256, 'original_archive_sha256': ARCHIVE_SHA256,
        'allowed_html_paths': sorted(A06_SUMMARY_ROUTES), 'added_html_paths': [], 'additions': [],
        'allowed_achievement_lines': ['A06'], 'allowed_ai_json_pointer': '/lines/5/records/0/summary',
        'editorial_documents': documents,
        'protected_website_members': {name: {'sha256': row['sha256'], 'bytes': row['bytes']}
            for name, row in entries.items() if name not in A06_SUMMARY_ROUTES},
        'reconstruction_kind': 'deduplicated_exact_utf8_text_edits',
        'scientific_review_status': 'review_required', 'release_eligible': False,
        'scientific_data_unchanged': True, 'M0_resumed': False,
        'historical_achievement_independent_of_AI_review': True}
    if (not isinstance(data, dict) or any(data.get(key) != value for key, value in required.items())
            or any(data.get(key) is not required[key] for key in ('release_eligible',
                'scientific_data_unchanged', 'M0_resumed', 'historical_achievement_independent_of_AI_review'))
            or any(type(data.get(key)) is not int or data[key] != 0 for key in ('new_quantum_calls', 'new_model_API_calls'))
            or not isinstance(data.get('authorization'), str) or not data['authorization'].strip()):
        raise ValueError('Unsupported bounded A06 summary clarification v23')
    files, pool = data.get('reversible_text_files'), data.get('reverse_text_patch_pool')
    if (not isinstance(files, list) or not files or not isinstance(pool, list) or not pool
            or any(not isinstance(row, dict) or row.get('path') not in A06_SUMMARY_PREDECESSOR_FILES for row in files)
            or len({row['path'] for row in files}) != len(files)
            or any(not isinstance(row.get('edits'), list) or not row['edits'] or any(
                not isinstance(edit, dict) or type(edit.get('replacement')) is not int for edit in row['edits']) for row in files)):
        raise ValueError('A06 summary may enumerate only its four fixed predecessor files')
    if {edit['replacement'] for row in files for edit in row['edits']} != set(range(len(pool))):
        raise ValueError('A06 summary requires exactly its used replacement segments')
    changed = set()
    for name, (sha, size) in A06_SUMMARY_PREDECESSOR_FILES.items():
        old = a06_summary_predecessor_bytes(root, name)
        if hashlib.sha256(old).hexdigest() != sha or len(old) != size:
            raise ValueError('A06 summary predecessor differs from fixed b663c63: '+name)
        if old != literature_predecessor_bytes(root, name):
            changed.add(name)
    if {row['path'] for row in files} != changed or changed != set(A06_SUMMARY_PREDECESSOR_FILES):
        raise ValueError('A06 summary must enumerate every and only its four changed files')
    old_ai = json.loads(a06_summary_predecessor_bytes(root, AI_RESEARCH_CONTENT))
    expected_ai = json.loads(json.dumps(old_ai))
    if (expected_ai['lines'][5]['id'] != 'A06' or not isinstance(A06_SUMMARY_TEXT, str)
            or not A06_SUMMARY_TEXT.strip() or A06_SUMMARY_TEXT == expected_ai['lines'][5]['records'][0]['summary']):
        raise ValueError('A06 summary requires a fixed nonempty changed first-record summary')
    expected_ai['lines'][5]['records'][0]['summary'] = A06_SUMMARY_TEXT
    if json.loads(literature_predecessor_bytes(root, AI_RESEARCH_CONTENT)) != expected_ai:
        raise ValueError('Only A06 records[0].summary may change; date, links, next steps and all other fields are protected')
    changes = data.get('changes')
    if (not isinstance(changes, list) or len(changes) != 1 or not isinstance(changes[0], dict)
            or changes[0].get('path') != AI_RESEARCH_ROUTE):
        raise ValueError('A06 summary may change only the existing research page')
    from public_line_labels import project_html, project_markdown
    item = changes[0]; route = AI_RESEARCH_ROUTE; old = entries[route]
    before = a06_summary_predecessor_bytes(root, 'site/'+route)
    after = literature_predecessor_bytes(root, 'site/'+route)
    source, current = before.decode('utf-8'), after.decode('utf-8')
    if (item.get('old_sha256') != old['sha256'] or item.get('old_bytes') != old['bytes']
            or hashlib.sha256(before).hexdigest() != old['sha256'] or len(before) != old['bytes']
            or item.get('new_sha256') != hashlib.sha256(after).hexdigest() or item.get('new_bytes') != len(after)
            or before == after or not isinstance(item.get('reason'), str) or not item['reason'].strip()):
        raise ValueError('A06 summary HTML differs from complete old/new identities')
    json_scripts = re.compile(r'<script\b[^>]*\btype\s*=\s*["\']application/(?:ld\+)?json["\'][^>]*>.*?</script\s*>', re.I | re.S)
    if json_scripts.findall(source) != json_scripts.findall(current):
        raise ValueError('A06 summary must retain every embedded JSON byte')
    if set(re.findall(r'\bid="([^\"]+)"', source)) != set(re.findall(r'\bid="([^\"]+)"', current)):
        raise ValueError('A06 summary must retain every navigation and source ID')
    if project_html(current, route) != current:
        raise ValueError('A06 summary lost canonical named achievement references')
    pattern = r'<section\b[^>]*\bid="ai-a06"[^>]*>.*?</section>'
    if (len(re.findall(pattern, source, re.S)) != 1 or len(re.findall(pattern, current, re.S)) != 1
            or re.sub(pattern, '<A06-SUMMARY/>', source, flags=re.S) != re.sub(pattern, '<A06-SUMMARY/>', current, flags=re.S)):
        raise ValueError('A06 summary changed outside its unique existing A06 section')
    prose = literature_predecessor_bytes(root, AI_RESEARCH_DOCUMENT).decode('utf-8')
    if project_markdown(prose) != prose:
        raise ValueError('A06 summary document lost canonical achievement names')
    updated = {name: dict(row) for name, row in entries.items()}
    updated[route] = {**old, 'sha256': item['new_sha256'], 'bytes': item['new_bytes'], 'presentation_id': PRESENTATION_V23_ID}
    for name, expected in updated.items():
        member = literature_predecessor_bytes(root, 'site/'+name)
        if hashlib.sha256(member).hexdigest() != expected['sha256'] or len(member) != expected['bytes']:
            raise ValueError('A06 summary changed an unlisted website byte: '+name)
    # Replay v23 using its exact reconstructed bytes; v24 checks final rendering.
    if not (root/PRESENTATION_V24_PATH).exists():
        from render_ai_research import inspect_ai_research
        check = inspect_ai_research(root)
        if check.get('status') != 'passed':
            raise ValueError('A06 summary final page differs from source rendering: '+str(check.get('errors', [])))
    members = publication_members(root, updated)
    report = {'path': PRESENTATION_V23_PATH, 'sha256': digest(path), 'presentation_id': PRESENTATION_V23_ID,
        'publication_kind': required['publication_kind'], 'changed_paths': [AI_RESEARCH_ROUTE], 'added_paths': [],
        'changed_achievement_lines': ['A06'], 'previous_presentation_commit': PRESENTATION_V23_PREVIOUS_COMMIT,
        'exact_predecessor_reconstruction': True, 'source_derived_rendering': True,
        'only_A06_first_record_summary_changed': True,
        'date_all_links_next_steps_and_other_AI_fields_preserved': True,
        'homepage_historical_pages_and_original_scientific_data_preserved': True,
        'previous_method_reading_register_inherited_without_new_expert_signoff': True,
        'original_embedded_json_bytes_preserved': True,
        'published_member_count_with_marker': len(members)+1,
        **{key: required[key] for key in ('scientific_review_status', 'scientific_data_unchanged',
            'historical_achievement_independent_of_AI_review', 'release_eligible', 'M0_resumed')}}
    return apply_literature_presentation(root, updated,
        {**report, 'presentation_chain': [*previous_report['presentation_chain'], report]})


def _effective_website_entries_v35(root: Path, baseline: dict, *, verify_current=True,
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


def _effective_website_entries_v36(root: Path, baseline: dict, *, verify_current=True,
                              revision_chain=None, include_presentation=True) -> tuple[dict, dict]:
    """Replay v1-v35 on exact data, then apply only the bounded reader layer."""
    arguments = {'verify_current': verify_current, 'revision_chain': revision_chain,
                 'include_presentation': include_presentation}
    if (root/'provenance/platform-presentation.v36.json').is_file():
        from reader_navigation_publication import apply
        return apply(root, baseline, _effective_website_entries_v35, **arguments)
    return _effective_website_entries_v35(root, baseline, **arguments)


def _effective_website_entries_v37(root: Path, baseline: dict, *, verify_current=True,
                              revision_chain=None, include_presentation=True) -> tuple[dict, dict]:
    """Replay the exact prior chain before the bounded academic reading layer."""
    arguments = {'verify_current': verify_current, 'revision_chain': revision_chain,
                 'include_presentation': include_presentation}
    if (root/'provenance/platform-presentation.v37.json').is_file():
        from academic_deepening_publication import apply
        return apply(root, baseline, _effective_website_entries_v36, **arguments)
    return _effective_website_entries_v36(root, baseline, **arguments)


def _effective_website_entries_v38(root: Path, baseline: dict, *, verify_current=True,
                              revision_chain=None, include_presentation=True) -> tuple[dict, dict]:
    """Replay the exact prior chain before the bounded reader journey."""
    arguments = {'verify_current': verify_current, 'revision_chain': revision_chain,
                 'include_presentation': include_presentation}
    if (root/'provenance/platform-presentation.v38.json').is_file():
        from reader_journey_publication import apply
        return apply(root, baseline, _effective_website_entries_v37, **arguments)
    return _effective_website_entries_v37(root, baseline, **arguments)


def _effective_website_entries_v39(root: Path, baseline: dict, *, verify_current=True,
                              revision_chain=None, include_presentation=True) -> tuple[dict, dict]:
    """Replay the exact prior chain before the bounded achievement display."""
    arguments = {'verify_current': verify_current, 'revision_chain': revision_chain,
                 'include_presentation': include_presentation}
    if (root/'provenance/platform-presentation.v39.json').is_file():
        from achievement_display_publication import apply
        return apply(root, baseline, _effective_website_entries_v38, **arguments)
    return _effective_website_entries_v38(root, baseline, **arguments)


def _effective_website_entries_v40(root: Path, baseline: dict, *, verify_current=True,
                              revision_chain=None, include_presentation=True) -> tuple[dict, dict]:
    """Replay the complete v39 chain before the bounded A03 navigation fix."""
    arguments = {'verify_current': verify_current, 'revision_chain': revision_chain,
                 'include_presentation': include_presentation}
    if (root/'provenance/platform-presentation.v40.json').is_file():
        from a03_navigation_publication import apply
        return apply(root, baseline, _effective_website_entries_v39, **arguments)
    return _effective_website_entries_v39(root, baseline, **arguments)


def _effective_website_entries_v41(root: Path, baseline: dict, *, verify_current=True,
                              revision_chain=None, include_presentation=True) -> tuple[dict, dict]:
    """Replay the complete v40 chain before the bounded Home entry order fix."""
    arguments = {'verify_current': verify_current, 'revision_chain': revision_chain,
                 'include_presentation': include_presentation}
    if (root/'provenance/platform-presentation.v41.json').is_file():
        from home_entry_order_publication import apply
        return apply(root, baseline, _effective_website_entries_v40, **arguments)
    return _effective_website_entries_v40(root, baseline, **arguments)


def _effective_website_entries_v42(root: Path, baseline: dict, *, verify_current=True,
                              revision_chain=None, include_presentation=True) -> tuple[dict, dict]:
    """Replay the complete v41 chain before the bounded Homepage portrait fix."""
    arguments = {'verify_current': verify_current, 'revision_chain': revision_chain,
                 'include_presentation': include_presentation}
    if (root/'provenance/platform-presentation.v42.json').is_file():
        from home_portrait_publication import apply
        return apply(root, baseline, _effective_website_entries_v41, **arguments)
    return _effective_website_entries_v41(root, baseline, **arguments)


def _publication_members_v42(root: Path, entries: dict) -> list[dict]:
    """Keep the prior allowlist and permit the single frozen homepage portrait."""
    if (root/'provenance/platform-presentation.v42.json').is_file():
        from home_portrait_publication import publication_members as portrait_publication_members
        return portrait_publication_members(root, entries, _publication_members_v41)
    return _publication_members_v41(root, entries)


def _effective_website_entries_v43(root: Path, baseline: dict, *, verify_current=True,
                              revision_chain=None, include_presentation=True) -> tuple[dict, dict]:
    """Replay the complete v42 chain before the bounded Homepage portrait fix."""
    arguments = {'verify_current': verify_current, 'revision_chain': revision_chain,
                 'include_presentation': include_presentation}
    if (root/'provenance/platform-presentation.v43.json').is_file():
        from home_portrait_replacement_publication import apply
        return apply(root, baseline, _effective_website_entries_v42, **arguments)
    return _effective_website_entries_v42(root, baseline, **arguments)


def _publication_members_v43(root: Path, entries: dict) -> list[dict]:
    """Keep the prior allowlist and permit the single frozen replacement portrait."""
    if (root/'provenance/platform-presentation.v43.json').is_file():
        from home_portrait_replacement_publication import publication_members as portrait_publication_members
        return portrait_publication_members(root, entries, _publication_members_v42)
    return _publication_members_v42(root, entries)


def _effective_website_entries_v44(root: Path, baseline: dict, *, verify_current=True,
                              revision_chain=None, include_presentation=True) -> tuple[dict, dict]:
    """Replay the complete v43 chain before the bounded Lifespan format fix."""
    arguments = {'verify_current': verify_current, 'revision_chain': revision_chain,
                 'include_presentation': include_presentation}
    if (root/'provenance/platform-presentation.v44.json').is_file():
        from home_lifespan_format_publication import apply
        return apply(root, baseline, _effective_website_entries_v43, **arguments)
    return _effective_website_entries_v43(root, baseline, **arguments)


def _publication_members_v44(root: Path, entries: dict) -> list[dict]:
    """Use the exact v43 view while retaining the complete existing allowlist."""
    if (root/'provenance/platform-presentation.v44.json').is_file():
        from home_lifespan_format_publication import publication_members as lifespan_publication_members
        return lifespan_publication_members(root, entries, _publication_members_v43)
    return _publication_members_v43(root, entries)


def _effective_website_entries_v45(root: Path, baseline: dict, *, verify_current=True,
                              revision_chain=None, include_presentation=True) -> tuple[dict, dict]:
    """Replay the complete v44 chain before the bounded Stories deepening fix."""
    arguments = {'verify_current': verify_current, 'revision_chain': revision_chain,
                 'include_presentation': include_presentation}
    if (root/'provenance/platform-presentation.v45.json').is_file():
        from home_stories_deepening_publication import apply
        return apply(root, baseline, _effective_website_entries_v44, **arguments)
    return _effective_website_entries_v44(root, baseline, **arguments)


def _publication_members_v45(root: Path, entries: dict) -> list[dict]:
    """Use the exact v44 view while retaining the complete existing allowlist."""
    if (root/'provenance/platform-presentation.v45.json').is_file():
        from home_stories_deepening_publication import publication_members as stories_publication_members
        return stories_publication_members(root, entries, _publication_members_v44)
    return _publication_members_v44(root, entries)


def _effective_website_entries_v46(root: Path, baseline: dict, *, verify_current=True,
                              revision_chain=None, include_presentation=True) -> tuple[dict, dict]:
    """Replay the complete v45 chain before the bounded Site deduplication fix."""
    arguments = {'verify_current': verify_current, 'revision_chain': revision_chain,
                 'include_presentation': include_presentation}
    if (root/'provenance/platform-presentation.v46.json').is_file():
        from site_deduplication_publication import apply
        return apply(root, baseline, _effective_website_entries_v45, **arguments)
    return _effective_website_entries_v45(root, baseline, **arguments)


def _publication_members_v46(root: Path, entries: dict) -> list[dict]:
    """Use the exact v45 view while retaining the complete existing allowlist."""
    if (root/'provenance/platform-presentation.v46.json').is_file():
        from site_deduplication_publication import publication_members as lifespan_publication_members
        return lifespan_publication_members(root, entries, _publication_members_v45)
    return _publication_members_v45(root, entries)


def effective_website_entries(root: Path, baseline: dict, *, verify_current=True,
                              revision_chain=None, include_presentation=True) -> tuple[dict, dict]:
    """Replay the complete v46 chain before the bounded International stories fix."""
    arguments = {'verify_current': verify_current, 'revision_chain': revision_chain,
                 'include_presentation': include_presentation}
    if (root/'provenance/platform-presentation.v47.json').is_file():
        from international_stories_publication import apply
        return apply(root, baseline, _effective_website_entries_v46, **arguments)
    return _effective_website_entries_v46(root, baseline, **arguments)


def publication_members(root: Path, entries: dict) -> list[dict]:
    """Use the exact v46 view while retaining the complete existing allowlist."""
    if (root/'provenance/platform-presentation.v47.json').is_file():
        from international_stories_publication import publication_members as stories_publication_members
        return stories_publication_members(root, entries, _publication_members_v46)
    return _publication_members_v46(root, entries)
