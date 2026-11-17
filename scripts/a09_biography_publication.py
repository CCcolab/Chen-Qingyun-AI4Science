"""Bounded A09 historical heritage presentation, independent of eight AI lines."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import re

MANIFEST = 'provenance/platform-presentation.v33.json'
PRESENTATION_ID = 'PLATFORM-A09-ACADEMIC-HERITAGE-20261117-v33'
PREVIOUS_COMMIT = '6156f2368672641bff2b8d56f5e7825cf0ec88ac'
PREVIOUS_MANIFEST = 'provenance/platform-presentation.v32.json'
ROUTES = ('index.html', 'achievements/index.html', 'topics/index.html', 'research/index.html')
ADDED_ROUTE = 'people/index.html'
AI = 'content/ai-research-section.v1.json'
HERITAGE_DOCUMENT = 'docs/ACADEMIC_ACHIEVEMENTS_zh-CN.md'
DOCUMENTS = (AI, 'scripts/render_heritage.py', HERITAGE_DOCUMENT,
    'content/a09-biography-narrative.v1.json', 'scripts/render_a09_biography.py',
    'docs/A09_ACADEMIC_HERITAGE_zh-CN.md', 'scripts/a08_biography_publication.py',
    'scripts/a01_publication_contract.py', 'scripts/a09_biography_publication.py')
NEW_FILES = ('content/a09-biography-narrative.v1.json', 'scripts/render_a09_biography.py',
    'docs/A09_ACADEMIC_HERITAGE_zh-CN.md', 'scripts/a09_biography_publication.py',
    'site/people/index.html', MANIFEST)
PUBLIC_DISPLAYS = (AI, HERITAGE_DOCUMENT, 'docs/A09_ACADEMIC_HERITAGE_zh-CN.md',
    'content/a09-biography-narrative.v1.json', 'site/people/index.html',
    *('site/'+route for route in ROUTES))
BASELINE_SHA256 = '5e3e70988d76ac1d777ff85ee7c1945341e2141767fc77560c6cea39eabab329'
ARCHIVE_SHA256 = 'fa9740d7a244ab4d52885600a312487869d780a82517aa0d0a401215696c4d3e'

# The private freeze step fills only fixed identities after source review.
FROZEN = True
PREDECESSOR_FILES = {'site/index.html': ('8b3532ee45c0fb33912f20a3bd7943043a348f10a370b9c6716e9edf3c0abf41', 257766), 'site/achievements/index.html': ('df20daf429c46e89e99085550067e8c1e9f7e283b10b7e8269f38da6a9d380ff', 95867), 'site/topics/index.html': ('44a5690d1e65195b9ff191d2a7ec37487070cdfafb191ae107962d5e0d7ab73c', 5055), 'site/research/index.html': ('c0df10f504310f69bd9bd233869dfcdef98d44844c928b2aa43a9b32a0f90580', 84579), 'content/ai-research-section.v1.json': ('9d2ed838d32ca17b930f110e7d0d4a63c08c0de5251d899057767e2149779010', 106112), 'scripts/render_heritage.py': ('d4ec4bc12c8fa082f36f436a6d9c06cc65592d1d03ef75504cfc619bab309740', 44310), 'docs/ACADEMIC_ACHIEVEMENTS_zh-CN.md': ('e9c71d5f3a7ad148882aae13847f9bce64d48d8858666285f7c42fbada5181a9', 69708), 'scripts/a08_biography_publication.py': ('d8c0b92e9c18d33135f3f1ed6c656672b028e609b59b0075a1243537c3cdcf84', 27149), 'scripts/a01_publication_contract.py': ('faec6a96a2e0e06a50b76bd892641bb467ed7928f364a23d8293de626ca74a41', 311341)}
PROTECTED_FILES = {'site/data/public-sources.json': ('94f8b9f6d0849deb9f26f75947205cfc8c4eb0973045fe958f2121237d987062', 33608), 'site/data/achievement-lines.json': ('1c9ec28bf41a7d79214e84a1c07f3bea1e0d91630dd3a88c93c39ff68a9bccec', 39768), 'content/heritage-20261114.v2.json': ('981876c28a6c863874a8bee8840477fcc04e0f117608d06a4a076b2d0d645350', 72392), 'content/chen-reagent-achievement.v1.json': ('8d13ee4ecaa36a2208867c2510531c8b0d6eb1e06abb8da52c36dc0d7265bcb1', 3884), 'content/chen-reagent-cas-source.v1.json': ('2125b9eaba7853ab02c378ca7c1d78265bbef2895bb2fa512a2cb53981de05cf', 1518), 'docs/CHEN_REAGENT_ACHIEVEMENT_zh-CN.md': ('aff472de27abf8d24eede857e77ae6aa0ce9d5a3a99cf774319250e08ee9128e', 2350), 'data/pftb1966_table1.csv': ('92af88d5c1307d0a01b418354d2620a0d9eb8a8c68766adedd8be0feec2ff29a', 515), 'results/pftb1966-uv-replay.json': ('c83794634136e2bd08d09b806b400eea603cf1c27c753ca3db2951b9c2c99432', 7691), 'results/REPLAY_REPORT_zh-CN.md': ('062aca44324f015450198a4bcc2ddba6aa98d896c31dbc81de407991d78b800b', 2976), 'content/a07-biography-narrative.v1.json': ('22e6121f4f3d61e3676a8ec95b76dc22512df0ab550cfb7c403f809f245016db', 13279), 'scripts/render_a07_biography.py': ('01f5e86435bc9f4eac7f04104892a2d875647f1dd6d3e270e38f3ed28d9dde8e', 9726), 'docs/A07_ACADEMIC_ACHIEVEMENTS_zh-CN.md': ('9d73bbb199e8c6d825550429ae35cb3ea8dffbcd4b17e3b73145603080cc487b', 11338), 'content/a08-biography-narrative.v1.json': ('e33b1834271cfdc42a36d02589c046fa2b5f34a2033ba93beb63201fe91def82', 28386), 'scripts/render_a08_biography.py': ('5d31f02e19edecfff1612d5656b1b2ed448e39f8a9d79447b88ee7aea4a407f7', 11000), 'docs/A08_ACADEMIC_ACHIEVEMENTS_zh-CN.md': ('c64ea7e4cfde67d25cad6c8fc1538c8167ad69cbeea38fcb473e4b3a7e3a7e37', 22967), 'scripts/render_ai_research.py': ('4293b6cd39150c9e77a6b3c02591c34e83b5d86ecdec675ca9253578af0e2552', 40735), 'docs/AI_RESEARCH_zh-CN.md': ('b6ab17e0db1794a9f33c370349fc84a37e36f5c50e76492577e447fc4b32d2cb', 63386), '.github/workflows/research-ci.yml': ('5353b0fae4b0ad0f3faa2b1275b54bb8a0619e95aec95575153a11de7988e047', 2599), '.github/workflows/pages.yml': ('f56bc01ffd913e0ca987923f1b96be49370d4768ad83a1a283f2dc5560542d7b', 1949)}
OLD_MANIFESTS = {'provenance/platform-presentation.v1.json': '1ade23238a23977b47eaa6a7dd585509fdca3e270615914292e2341721308782', 'provenance/platform-presentation.v2.json': '91434b5bc8fb51e96b604a6c6437cb363c92370347f22fcbd2a825e5498f0348', 'provenance/platform-presentation.v3.json': '2b290301102abd8cacb5a2d73f7393d8c4f851285a882a08df42eecd960ed286', 'provenance/platform-presentation.v4.json': 'cfc0bc4d29c24a846bb76ceaf3246084d406393cc7d04ec105cad539c21e120b', 'provenance/platform-presentation.v5.json': '7ac60223b0e540de62671017728acd54e66d07e8de2721006c476c8d1734bed9', 'provenance/platform-presentation.v6.json': '1077f6b2e3a78be65ea4b50e81907b629f96c9b3599fcf440493c204b33dbcf3', 'provenance/platform-presentation.v7.json': '2463a97b3bf74b629f1863892d75f36276c97bf9a111905b47cc6179b62eaa7f', 'provenance/platform-presentation.v8.json': 'ab2b362cb5c90dc4b782f8989cc127a31944c49998ee45fbded8b8a7ac77c962', 'provenance/platform-presentation.v9.json': '462fdbfe1c4bd6f0c32f39e2597764037b4562904f0acec4cce00f08c9797017', 'provenance/platform-presentation.v10.json': '65954e3ff6b484a010fa5052f5331eab55149d23a468ae354ab236462598ffd3', 'provenance/platform-presentation.v11.json': 'd6eb2a3faed6f030a28ca5b63e3f3512144c9246f39467d300fc279a967bb004', 'provenance/platform-presentation.v12.json': 'aa9efd831558b47646b687e12be30724c4b8be89a0f98ccb8d06ef56cf04e81f', 'provenance/platform-presentation.v13.json': '263b465d22b1a56b8364a0540a65f742948664f9e50e64d759543685768468cc', 'provenance/platform-presentation.v14.json': '3ea28579d130b065fb805942c5c62861d8f6cd24a0027df7fef7cdc41415750b', 'provenance/platform-presentation.v15.json': 'd21bad493ae97587c7b9493813af3393ed9ed98f5a8dfd3a8790270f7ba49aff', 'provenance/platform-presentation.v16.json': '6b975e980d176ecc481449ca5a96ffadadfecae2eb64d97dfdafb75b85b4a3c0', 'provenance/platform-presentation.v17.json': 'b635b2950e37d5387e8fb68da12109ca585833b769eec38cf25911eb86563ee1', 'provenance/platform-presentation.v18.json': '4fa6f43360d5343e119bb7b9e51e0671f1b4b4ef51ba065067459180a710dfd6', 'provenance/platform-presentation.v19.json': '1a056390024ec41126e36c8b8e6a5275415331ec6eeec524da9df8785e23d59b', 'provenance/platform-presentation.v20.json': '34814fabc405812bccc433018f8a197d181a3da9ac617f84cceda51513774b72', 'provenance/platform-presentation.v21.json': 'a353a25fc9586c3fe78de1ad42a20aee4a1c980de59eda4340df4466d9b45593', 'provenance/platform-presentation.v22.json': '3a9a746a565f7942899f5fdffc244121608e39210c7e6eb466203775dc38cae6', 'provenance/platform-presentation.v23.json': '392490c9d1ddc18942ef5b139eb094155a883f1a340e56adfc9512bfa5430a3d', 'provenance/platform-presentation.v24.json': '118a96428bf0a0fce5467fffd8861c419f97ac078aed708b6fd3b5e6318cc242', 'provenance/platform-presentation.v25.json': '61b8e4ebc4e4800253d886a617b98c9590c370c5ae494731edc8135ebf15e9c1', 'provenance/platform-presentation.v26.json': '0215099d811ba22ee7224e17a2603d3fdccd7dd0b7473297d35ceb419966bd2d', 'provenance/platform-presentation.v27.json': 'a49d94aae9d1ab980a17506441fdb6d8629fd29da5ae798aa3737568f0c2344b', 'provenance/platform-presentation.v28.json': '54449b28f3dfb1c2946872f959df5e8bb1fc4a9b8e04f20b9b0f9daacd8704f3', 'provenance/platform-presentation.v29.json': '2206e301c22181e3e1a0d5bcce619dd590b4eca3d2968faee6cfbf9a08ed29b7', 'provenance/platform-presentation.v30.json': '952cea23bb612648addc4ac5a5e5cc88acae24a67b8dc98661ae49f79710645b', 'provenance/platform-presentation.v31.json': '2d1195067b1ed7cc9a454329cc499a0b07cc01de0d1f8bdfa001214d9cf2c5a4', 'provenance/platform-presentation.v32.json': '437a1f8404c35af883fc29ac3155405ede4f2e7eb41b19b128b05dbeb06ed175'}
REVIEWED_PUBLIC_FILES = {'site/index.html': 'ed784916e48d27fce62870476a7083c1de68934c1e96343f4c60e9336fcd6220', 'site/achievements/index.html': '4180b6ef8dd6a12127addc2b3694258f97b0310bbd5cff0b021097550fb4f8f2', 'site/topics/index.html': '9873ad87c1c46126755d9ee346b044e36eaa001394f1d5d1ed8043e1f4c584db', 'site/research/index.html': 'cbc946120f8fa53054d32aa7cfa013f52b0c15147954bfb4705023d910232d28', 'content/ai-research-section.v1.json': 'd7e454c826014ae31e0b1a346e66fc193a39ffc4516a4abecbfa895e7dac90e0', 'scripts/render_heritage.py': '9e0a977a69f8bee2601843d92840ee709f4d15b4e7640d3c20474cf0f61b516e', 'docs/ACADEMIC_ACHIEVEMENTS_zh-CN.md': 'ffdf2222f1d2c12c978f2948174fc1ce36ec88bca43f1f53571d6be389ff5ee7', 'scripts/a08_biography_publication.py': '7be55f61e47db3e6c80054ebb70c9fdbe429d82de5cef801ab984ebda1d3bf3d', 'scripts/a01_publication_contract.py': '0329dcfe1d393e505d49ba40d05a10be0bca7419f9533bc6426ea32be89858ec', 'content/a09-biography-narrative.v1.json': 'ef84978855c9edb156e528e72fd63df75932b4ed165dee94b43fb831794aec50', 'scripts/render_a09_biography.py': 'eab7906278f6258688537ee57ddc941802b54f58a109610f4fee6cc4b02120d0', 'docs/A09_ACADEMIC_HERITAGE_zh-CN.md': '00bd6eb7270a31ef0a9c857fe7f35b67a57abfb6aa41e22089b281380472508a', 'site/people/index.html': 'c70e0b1c08c02566f61adb3e7602a6fe15ef2f9af498d160cd171c2719f7e381'}
EXACT_HTML_REPLACEMENTS = {'index.html': [('<article class="case" id="line-a09"><div class="case-side">研究生培养与学术交流</div><div class="case-main"><h3>A09（学科建设与人才培养）</h3><p><b>研究问题：</b>学风怎样通过训练、合作、期刊和会议延续？</p><p>传记记录陈庆云带学生核查谱图和实验记录、逐步放手选题，以及参与期刊、国际学术会议和跨机构交流。</p><p><a href="#record-publication-index">学风与学术档案 →</a></p><details><summary>依据、边界与下一步</summary><p>传记 p.87–105、110–111、119–122、123–159；<a href="#source-cq-h01">CQ-H01</a>、<a href="#source-cq-h06">CQ-H06</a>、<a href="#source-cq-r28">CQ-R28</a>。共同署名、交流、师承和引文采用各有证据；附录条目不等于独著或论文总数，1987 年统计不是职业排名。</p></details><section class="supporting-record" id="record-publication-index"><h4>学术档案：训练、编目与年度统计</h4><p>传记记录核对实验记录、谱图和结构解释，并逐步让学生独立提出问题。交流、合著、具名核查和直接引文不能互相代替。〔CQ-H01、CQ-R28〕</p><p>传记附录二印刷 p.123–159 序号 1–327，包括发明人证书、团队论文和多类论著，也有待核题录；327 是底本编目数，不是独著或论文总数。〔CQ-H01〕</p><p>新华社 1989 年报道转述对 1987 年科技论文的索引调查：陈庆云有 9 篇被收录，与王文山、张其瑞同为 9 篇。该数字是调查的年度收录数，不是职业生涯排名或被引次数。〔<a href="https://cn.govopendata.com/renminribao/1989/02/11/3/">CQ-H06</a>〕</p></section></div></article>', '<article class="case" id="line-a09"><div class="case-side">独立研究与学术共同体</div><div class="case-main"><h3>A09（学科建设与人才培养）</h3><p>从规范实验到自主选题，从论文初稿到完整谱图讨论，再到高年级带新生、期刊与国际会议服务，传记留下了可具体阅读的学科建设和育人经历。</p><p><a href="people/index.html">学科建设、育人故事与合作传承 →</a></p><p><a href="people/index.html#a09-independent">自主选题与论证训练</a> · <a href="people/index.html#a09-team">团队带教与人才接续</a> · <a href="people/index.html#a09-service">期刊与国际学术服务</a></p><details><summary>学术档案的阅读口径</summary><section class="supporting-record" id="record-publication-index"><h4>学术档案与年度统计的阅读口径</h4><p>传记附录二印刷123–159页编列1–327号论著，包括不同文书及共同成果；编目数不等于独著数或论文总量。</p><p>1989年报道转述对1987年科技论文的索引调查：陈庆云收录9篇，与王文山、张其瑞同为9篇。该数字是调查的年度收录数，不是被引次数、职业排名或全生涯总量。</p><p><a href="people/index.html#a09-academic-archive">出处与统计范围 →</a></p></section></details></div></article>')], 'achievements/index.html': [('<article class="case" id="line-a09"><div class="case-side">研究生培养与学术交流</div><div class="case-main"><h3>A09（学科建设与人才培养）</h3><p><b>研究问题：</b>学风怎样通过训练、合作、期刊和会议延续？</p><p>传记记录陈庆云带学生核查谱图和实验记录、逐步放手选题，以及参与期刊、国际学术会议和跨机构交流。</p><p><a href="#record-publication-index">学风与学术档案 →</a></p><details><summary>依据、边界与下一步</summary><p>传记 p.87–105、110–111、119–122、123–159；<a href="../index.html#source-cq-h01">CQ-H01</a>、<a href="../index.html#source-cq-h06">CQ-H06</a>、<a href="../index.html#source-cq-r28">CQ-R28</a>。共同署名、交流、师承和引文采用各有证据；附录条目不等于独著或论文总数，1987 年统计不是职业排名。</p></details><section class="supporting-record" id="record-publication-index"><h4>学术档案：训练、编目与年度统计</h4><p>传记记录核对实验记录、谱图和结构解释，并逐步让学生独立提出问题。交流、合著、具名核查和直接引文不能互相代替。〔<a href="../index.html#source-cq-h01">CQ-H01</a>、<a href="../index.html#source-cq-r28">CQ-R28</a>〕</p><p>传记附录二印刷 p.123–159 序号 1–327，包括发明人证书、团队论文和多类论著，也有待核题录；327 是底本编目数，不是独著或论文总数。〔<a href="../index.html#source-cq-h01">CQ-H01</a>〕</p><p>新华社 1989 年报道转述对 1987 年科技论文的索引调查：陈庆云有 9 篇被收录，与王文山、张其瑞同为 9 篇。该数字是调查的年度收录数，不是职业生涯排名或被引次数。〔<a href="../index.html#source-cq-h06">CQ-H06</a>〕</p></section></div></article>', '<article class="case" id="line-a09"><div class="case-side">独立研究与学术共同体</div><div class="case-main"><h3>A09（学科建设与人才培养）</h3><p>从规范实验到自主选题，从论文初稿到完整谱图讨论，再到高年级带新生、期刊与国际会议服务，传记留下了可具体阅读的学科建设和育人经历。</p><p><a href="../people/index.html">学科建设、育人故事与合作传承 →</a></p><p><a href="../people/index.html#a09-independent">自主选题与论证训练</a> · <a href="../people/index.html#a09-team">团队带教与人才接续</a> · <a href="../people/index.html#a09-service">期刊与国际学术服务</a></p><details><summary>学术档案的阅读口径</summary><section class="supporting-record" id="record-publication-index"><h4>学术档案与年度统计的阅读口径</h4><p>传记附录二印刷123–159页编列1–327号论著，包括不同文书及共同成果；编目数不等于独著数或论文总量。</p><p>1989年报道转述对1987年科技论文的索引调查：陈庆云收录9篇，与王文山、张其瑞同为9篇。该数字是调查的年度收录数，不是被引次数、职业排名或全生涯总量。</p><p><a href="../people/index.html#a09-academic-archive">出处与统计范围 →</a></p></section></details></div></article>'), ('<article class="heritage-card" id="heritage-line-a09"><h3>A09（学科建设与人才培养）</h3><p>通过具体的研究生训练、团队带教、学术期刊与国际交流，为有机氟化学人才和学术共同体留下持续影响。</p><div class="heritage-achievement-notes"><h4>成果与合作</h4><h5>让写作和谱图讨论成为训练</h5><p>传记保存陈庆云、郭勇关于学生自行写论文及反复修改的具名回忆，并在结语记述带完整谱图讨论结构的要求。由学生提出解释，再用数据和论证检查解释，构成具体的育人方法。</p><p class="heritage-locator">出处定位：传记p93两份具名访谈转引；p111作者总结叙述 <span class="heritage-refs"><a href="../index.html#heritage-source-s01" title="氟缘笃志：陈庆云传（当前本地研究底本）">[HERITAGE-S01]</a></span></p><p class="heritage-meta">待核事项：原访谈、具体论文修订稿及谱图待补；不同叙述性质分别保留。</p><h5>通过期刊与学术委员会服务共同体</h5><p>2009年机构报道记载《有机化学》主编及1991–1998年IUPAC有机化学命名委员会中国国家代表等历史任职；实验室公开名单还保存历届学术委员会的主任记录。这些学术服务与个人研究论文分开整理。</p><p class="heritage-locator">出处定位：2009-02-20机构报道后半段；原有机氟重点实验室第一至第四届学委会名单 <span class="heritage-refs"><a href="../index.html#heritage-source-s09" title="有机所庆贺陈庆云院士八十华诞">[HERITAGE-S09]</a> <a href="../index.html#heritage-source-s11" title="上海有机所：有机氟化学重点实验室历届学术委员会名单">[HERITAGE-S11]</a></span></p><p class="heritage-meta">待核事项：任命文书、同期编委页及学委会任期起止待补，不作为现任职务介绍。</p><h5>同行与学生在学术报告中接续问题</h5><p>2019年九十华诞报告会，杨国英作为学生代表分享经历，Dolbier、肖吉昌、吴生文分别作学术报告。机构报道让合作与育人留下具名事件记录，各报告和研究成果仍归实际报告者与原作者。</p><p class="heritage-locator">出处定位：2019-01-28报道所载2019-01-25活动及报告段 <span class="heritage-refs"><a href="../index.html#heritage-source-s10" title="上海有机所举办陈庆云院士九十华诞学术报告会">[HERITAGE-S10]</a></span></p><p class="heritage-meta">待核事项：原报告文稿、视频授权与会中回忆的原始材料待补。</p></div><details><summary>现有材料及来源定位</summary><ul><li><span class="heritage-tag">印刷p87–111逐页核读，具名访谈与作者叙述已区分</span>教学与团队故事<p class="heritage-locator">出处定位：刘超2018-05-15访谈转引p92、102；结语p106–111 <span class="heritage-refs"><a href="../index.html#heritage-source-s01" title="氟缘笃志：陈庆云传（当前本地研究底本）">[HERITAGE-S01]</a></span></p></li><li><span class="heritage-tag">育人及集体精神有公开出处</span>机构生平与采集工程报道<p class="heritage-locator">出处定位：机构育人段；博物馆2021报道及其郭勇回忆 <span class="heritage-refs"><a href="../index.html#heritage-source-s02" title="上海有机所：陈庆云院士生平">[HERITAGE-S02]</a> <a href="../index.html#heritage-source-s03" title="陈庆云：六十余年研究一种化学元素">[HERITAGE-S03]</a></span></p></li><li><span class="heritage-tag">传记附录和原有来源可定位，目录不等于论文总量</span>交流、期刊、年表与目录<p class="heritage-locator">出处定位：传记p95–105、112–159 <span class="heritage-refs"><a href="../index.html#heritage-source-s01" title="氟缘笃志：陈庆云传（当前本地研究底本）">[HERITAGE-S01]</a></span></p></li><li><span class="heritage-tag">关键页与脚注整页核读，作者叙述及具名访谈转引分别登记</span>论文写作与结构判断的具体训练<p class="heritage-locator">出处定位：传记p90、93、111；陈庆云2018-03-09、郭勇2018-05-15访谈；p111结构确证为作者叙述 <span class="heritage-refs"><a href="../index.html#heritage-source-s01" title="氟缘笃志：陈庆云传（当前本地研究底本）">[HERITAGE-S01]</a></span></p></li><li><span class="heritage-tag">官方图集图注已核读，未取得照片底片与原始拍摄记录</span>1979年国际交流与1985年指导研究的机构图注<p class="heritage-locator">出处定位：传记p95–100、年表p116；SIOC图集1979年交流、1985年与研究生研究反应过程及讨论工作图注 <span class="heritage-refs"><a href="../index.html#heritage-source-s01" title="氟缘笃志：陈庆云传（当前本地研究底本）">[HERITAGE-S01]</a> <a href="../index.html#heritage-source-s08" title="上海有机所陈庆云纪念专题：生平图集">[HERITAGE-S08]</a></span></p></li><li><span class="heritage-tag">2009机构历史报道已核读；原任命文书、逐年编委页待补</span>期刊编辑与国际学术服务<p class="heritage-locator">出处定位：2009-02-20报道后半段：1993年起《有机化学》主编，1991–1998年IUPAC有机化学命名委员会中国国家代表；传记年表p119记1993主编 <span class="heritage-refs"><a href="../index.html#heritage-source-s01" title="氟缘笃志：陈庆云传（当前本地研究底本）">[HERITAGE-S01]</a> <a href="../index.html#heritage-source-s09" title="有机所庆贺陈庆云院士八十华诞">[HERITAGE-S09]</a></span></p></li><li><span class="heritage-tag">任职机构活动正文可核，报告内容和成果各归实际报告人与原作者</span>2019年九十华诞学术报告会中的同行与学生<p class="heritage-locator">出处定位：传记p95–96、年表p122；2019-01-28机构报道中的2019-01-25活动、杨国英学生代表发言及Dolbier／肖吉昌／吴生文三报告 <span class="heritage-refs"><a href="../index.html#heritage-source-s01" title="氟缘笃志：陈庆云传（当前本地研究底本）">[HERITAGE-S01]</a> <a href="../index.html#heritage-source-s10" title="上海有机所举办陈庆云院士九十华诞学术报告会">[HERITAGE-S10]</a></span></p></li><li><span class="heritage-tag">机构历史名单已核；任期起止与原任命文书未取得</span>有机氟化学重点实验室历届学术委员会任职<p class="heritage-locator">出处定位：原有机氟化学重点实验室第一至第四届名单；不与页面上方新实验室第一届名单混淆 <span class="heritage-refs"><a href="../index.html#heritage-source-s11" title="上海有机所：有机氟化学重点实验室历届学术委员会名单">[HERITAGE-S11]</a></span></p></li></ul></details><h4>待核事项</h4><ul><li>原始访谈录音／逐字稿的合法访问与引用许可</li><li>学位论文、培养名单、会议与期刊档案；不得由合著直接推师承</li><li>原始访谈录音／逐字稿及引用许可，具体论文初稿、修订稿、谱图和实验记录</li><li>1979会议程序、报告摘要、邀请／访问函和照片原说明</li><li>期刊主编及IUPAC任职文书、同期编委页、培养档案；不把2009所载人数外推为当前或全生涯统计</li></ul><p><strong>待补文献：</strong>优先补所选育人故事的原访谈和具体学位／会议资料，再逐项扩展人物关系。</p><p class="heritage-meta">平台AI辅助研究：尚无本成果线已完成的平台复现计算或实验验证结果。</p></article>', '<article class="heritage-card" id="heritage-line-a09"><h3>A09（学科建设与人才培养）</h3><p>以独立研究能力、团队人才接续与学术共同体服务为主线，介绍陈庆云的具体育人方法及长期合作。</p><ul><li>自主选题、论文修改与完整谱图讨论。</li><li>高年级带新生、人才梯队衔接及长期同行合作。</li><li>研究生教育、期刊编辑、国际命名与会议服务。</li></ul><p class="heritage-locator">传记78–79、87–105、111、117–122页；机构2009、2019年报道及生平图集，各段出处见专题。</p><p><a href="../people/index.html">A09（学科建设与人才培养）人物与传承专题 →</a> · <a href="../people/index.html#refs">参考资料</a></p></article>')], 'topics/index.html': [('<section class="topic-line" id="topic-line-a09"><h2><a href="../index.html#line-a09">A09（学科建设与人才培养）</a></h2><ul><li><a href="../achievements/index.html#heritage-line-a09">学科建设与人才培养资料</a></li><li><a href="../achievements/index.html#heritage-stories-all">合作与育人故事及出处</a></li></ul></section>', '<section class="topic-line" id="topic-line-a09"><h2><a href="../index.html#line-a09">A09（学科建设与人才培养）</a></h2><ul><li><a href="../people/index.html">学科建设、育人故事与学术传承</a></li><li><a href="../people/index.html#a09-people">人物与合作角色</a></li><li><a href="../people/index.html#a09-ai-collation">AI辅助资料整理</a></li><li><a href="../achievements/index.html#heritage-line-a09">成果与传承汇总</a></li></ul></section>')], 'research/index.html': [('href="../index.html#line-a09"', 'href="../people/index.html"')]}


def _sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _file(root: Path, name: str) -> Path:
    relative = PurePosixPath(name)
    path = root/name
    if (not name or relative.is_absolute() or '..' in relative.parts or '\\' in name
            or relative.as_posix() != name or path.is_symlink() or not path.is_file()
            or not path.resolve().is_relative_to(root.resolve())):
        raise ValueError('Unsafe or missing A09 heritage-presentation file: '+str(name))
    return path


def _json(root: Path, name: str):
    return json.loads(_file(root, name).read_bytes())


def _record_set(data: dict) -> tuple[list, list]:
    records, pool = data.get('reversible_text_files'), data.get('reverse_text_patch_pool')
    row_keys = {'path', 'old_sha256', 'old_bytes', 'new_sha256', 'new_bytes', 'edits'}
    if (not isinstance(records, list) or not isinstance(pool, list) or not pool
            or any(not isinstance(row, dict) or set(row) != row_keys for row in records)
            or len(records) != len(PREDECESSOR_FILES)
            or any(not isinstance(row['path'], str) for row in records)
            or {row['path'] for row in records} != set(PREDECESSOR_FILES)
            or len({row['path'] for row in records}) != len(records)):
        raise ValueError('A09 heritage requires exactly its fixed predecessor file set')
    for pair in pool:
        if (not isinstance(pair, dict) or set(pair) != {'old', 'new'}
                or not all(isinstance(pair[k], str) for k in ('old', 'new'))
                or pair['old'] == pair['new']):
            raise ValueError('Invalid A09 heritage replacement pool')
    used = set()
    for row in records:
        if (any(type(row[k]) is not int or row[k] < 0 for k in ('old_bytes', 'new_bytes'))
                or any(not isinstance(row[k], str) or not re.fullmatch(r'[0-9a-f]{64}', row[k])
                    for k in ('old_sha256', 'new_sha256'))
                or not isinstance(row['edits'], list) or not row['edits']):
            raise ValueError('Incomplete A09 heritage predecessor identity or edits')
        for edit in row['edits']:
            if (not isinstance(edit, dict) or set(edit) != {'old_offset', 'replacement'}
                    or type(edit['old_offset']) is not int or edit['old_offset'] < 0
                    or type(edit['replacement']) is not int
                    or not 0 <= edit['replacement'] < len(pool)):
                raise ValueError('Invalid A09 heritage exact reverse edit')
            used.add(edit['replacement'])
    if used != set(range(len(pool))):
        raise ValueError('A09 heritage requires exactly its used replacement pool')
    return records, pool


def predecessor_bytes(root: Path, name: str) -> bytes:
    """Read untouched bytes directly; reverse only the fixed A09 changed paths.

    Unaffected reads do not validate the whole v33 manifest. apply() does that
    once, including rejecting unauthorized records that the fast path ignores.
    Every invocation reads actual bytes; no path/mtime/global cache is used.
    """
    current = _file(root, name).read_bytes()
    if name not in PREDECESSOR_FILES and name != MANIFEST:
        return current
    if not (root/MANIFEST).exists():
        return current
    data = _json(root, MANIFEST)
    if not isinstance(data, dict):
        raise ValueError('A09 heritage presentation requires a JSON object')
    records, pool = _record_set(data)
    matches = [row for row in records if row['path'] == name]
    if not matches:
        return current  # Only this layer's own immutable declaration can reach here.
    row = matches[0]
    old_sha, old_size = PREDECESSOR_FILES[name]
    if (row['old_sha256'] != old_sha or row['old_bytes'] != old_size
            or _sha(current) != row['new_sha256'] or len(current) != row['new_bytes']):
        raise ValueError('A09 heritage file differs from complete old/new identities: '+name)
    chunks, cursor, old_end, delta = [], 0, 0, 0
    for edit in row['edits']:
        offset = edit['old_offset']
        pair = pool[edit['replacement']]
        before, after = pair['old'].encode('utf-8'), pair['new'].encode('utf-8')
        position = offset+delta
        if (offset < old_end or offset+len(before) > old_size
                or position < cursor or position+len(after) > len(current)
                or current[position:position+len(after)] != after):
            raise ValueError('A09 heritage reverse replacement differs at exact offset: '+name)
        chunks.extend((current[cursor:position], before))
        cursor, old_end = position+len(after), offset+len(before)
        delta += len(after)-len(before)
    rebuilt = b''.join((*chunks, current[cursor:]))
    if _sha(rebuilt) != old_sha or len(rebuilt) != old_size:
        raise ValueError('A09 heritage predecessor cannot be reconstructed exactly: '+name)
    return rebuilt


def _binding(root: Path, name: str) -> dict:
    value = _file(root, name).read_bytes()
    return {'path': name, 'sha256': _sha(value), 'bytes': len(value)}


def _check_html_regions(route: str, before: bytes, after: bytes) -> None:
    source, current = before.decode('utf-8'), after.decode('utf-8')
    expected = source
    replacements = EXACT_HTML_REPLACEMENTS.get(route)
    if not isinstance(replacements, list) or not replacements:
        raise ValueError('A09 route requires fixed reviewed display replacements: '+route)
    for pair in replacements:
        if (not isinstance(pair, tuple) or len(pair) != 2 or not all(isinstance(x, str) for x in pair)
                or pair[0] == pair[1] or expected.count(pair[0]) != 1):
            raise ValueError('Ambiguous or invalid fixed A09 display replacement: '+route)
        expected = expected.replace(pair[0], pair[1], 1)
    if expected != current:
        raise ValueError('A09 changed bytes outside fixed reviewed display regions: '+route)
    scripts = re.compile(r'<script\b[^>]*\btype\s*=\s*["\']application/(?:ld\+)?json["\'][^>]*>.*?</script\s*>', re.I | re.S)
    if scripts.findall(source) != scripts.findall(current):
        raise ValueError('A09 heritage changed original embedded JSON: '+route)
    old_ids = re.findall(r'\bid="([^\"]+)"', source)
    new_ids = re.findall(r'\bid="([^\"]+)"', current)
    if not set(old_ids).issubset(new_ids) or len(new_ids) != len(set(new_ids)):
        raise ValueError('A09 heritage lost or duplicated existing IDs: '+route)


def apply(root: Path, entries: dict, previous_report: dict) -> tuple[dict, dict]:
    """Validate v33's exact bounded historical presentation after v32 replay."""
    if not (root/MANIFEST).exists():
        return entries, previous_report
    if not FROZEN:
        raise ValueError('A09 heritage publication has not been frozen after source review')
    if not (root/PREVIOUS_MANIFEST).is_file():
        raise ValueError('A09 heritage requires its immutable v32 predecessor')
    for name, sha in OLD_MANIFESTS.items():
        if _sha(_file(root, name).read_bytes()) != sha:
            raise ValueError('Historical presentation manifest changed: '+name)
    for name, (sha, size) in PROTECTED_FILES.items():
        value = _file(root, name).read_bytes()
        if _sha(value) != sha or len(value) != size:
            raise ValueError('A09 changed a protected historical, scientific or AI source: '+name)
    data = _json(root, MANIFEST)
    if not isinstance(data, dict):
        raise ValueError('A09 heritage presentation requires a JSON object')
    added_binding = _binding(root, 'site/'+ADDED_ROUTE)
    required = {
        'schema_version': '33.0', 'presentation_id': PRESENTATION_ID,
        'publication_kind': 'platform_a09_academic_heritage',
        'previous_presentation_commit': PREVIOUS_COMMIT,
        'previous_presentation': {'path': PREVIOUS_MANIFEST, 'sha256': OLD_MANIFESTS[PREVIOUS_MANIFEST]},
        'original_baseline_sha256': BASELINE_SHA256, 'original_archive_sha256': ARCHIVE_SHA256,
        'allowed_html_paths': list(ROUTES), 'added_html_paths': [ADDED_ROUTE],
        'allowed_display_regions': {
            'index.html': ['article#line-a09'],
            'achievements/index.html': ['article#line-a09', 'article#heritage-line-a09'],
            'topics/index.html': ['section#topic-line-a09'],
            'research/index.html': ['intro A09 heritage href'],
        },
        'additions': [{'path': ADDED_ROUTE, 'sha256': added_binding['sha256'], 'bytes': added_binding['bytes']}],
        'editorial_documents': [_binding(root, name) for name in DOCUMENTS],
        'protected_website_members': {name: {'sha256': row['sha256'], 'bytes': row['bytes']}
            for name, row in entries.items() if name not in ROUTES},
        'reconstruction_kind': 'deduplicated_exact_utf8_text_edits',
        'scientific_review_status': 'review_required', 'release_eligible': False,
        'scientific_data_unchanged': True, 'M0_resumed': False,
        'historical_achievement_independent_of_AI_review': True,
        'allowed_ai_json_pointers': ['/heritage/url'], 'allowed_new_files': list(NEW_FILES),
    }
    if (any(data.get(k) != v for k, v in required.items())
            or any(data.get(k) is not required[k] for k in ('release_eligible',
                'scientific_data_unchanged', 'M0_resumed', 'historical_achievement_independent_of_AI_review'))
            or any(type(data.get(k)) is not int or data[k] != 0 for k in ('new_quantum_calls', 'new_model_API_calls'))
            or not isinstance(data.get('authorization'), str) or not data['authorization'].strip()):
        raise ValueError('Unsupported bounded A09 historical-heritage presentation v33')
    _record_set(data)
    for name, (sha, size) in PREDECESSOR_FILES.items():
        old = predecessor_bytes(root, name)
        if _sha(old) != sha or len(old) != size or old == _file(root, name).read_bytes():
            raise ValueError('A09 heritage predecessor differs from fixed 6156f23: '+name)
    expected_ai = json.loads(predecessor_bytes(root, AI))
    expected_ai['heritage']['url'] = '../people/index.html'
    if _json(root, AI) != expected_ai:
        raise ValueError('A09 may change only the heritage URL, retaining all eight AI research lines')
    old_document = predecessor_bytes(root, HERITAGE_DOCUMENT).decode('utf-8')
    current_document = _file(root, HERITAGE_DOCUMENT).read_bytes().decode('utf-8')
    a09_document = re.compile(r'^### A09[^\n]*\n.*?(?=^## 人物与合作故事\s*$)', re.M | re.S)
    if (len(a09_document.findall(old_document)) != 1 or len(a09_document.findall(current_document)) != 1
            or a09_document.sub('<A09-INVENTORY/>\n', old_document)
                != a09_document.sub('<A09-INVENTORY/>\n', current_document)):
        raise ValueError('A09 changed another line or story in the heritage inventory document')
    for name, sha in REVIEWED_PUBLIC_FILES.items():
        if _sha(_file(root, name).read_bytes()) != sha:
            raise ValueError('A09 source, renderer or document differs from reviewed bytes: '+name)
    for name in PUBLIC_DISPLAYS:
        value = _file(root, name).read_bytes().decode('utf-8')
        if re.search(r'(?i)private-sources|current-item-register|现阶段待查事项统计|[CD]:[\\/]', value):
            raise ValueError('A09 public display contains private evidence or a local path: '+name)
    changes = data.get('changes')
    if (not isinstance(changes, list) or len(changes) != len(ROUTES)
            or any(not isinstance(row, dict) for row in changes)
            or {row.get('path') for row in changes} != set(ROUTES)):
        raise ValueError('A09 heritage may change only its four existing routes')
    if ADDED_ROUTE in entries:
        raise ValueError('A09 heritage route already exists in its predecessor')
    updated = {name: dict(row) for name, row in entries.items()}
    for item in changes:
        route = item['path']; old_entry = entries[route]
        before = predecessor_bytes(root, 'site/'+route)
        after = _file(root, 'site/'+route).read_bytes()
        if (item.get('old_sha256') != old_entry['sha256'] or item.get('old_bytes') != old_entry['bytes']
                or _sha(before) != old_entry['sha256'] or len(before) != old_entry['bytes']
                or item.get('new_sha256') != _sha(after) or item.get('new_bytes') != len(after)
                or before == after or not isinstance(item.get('reason'), str) or not item['reason'].strip()):
            raise ValueError('A09 route differs from complete old/new identities: '+route)
        _check_html_regions(route, before, after)
        updated[route] = {**old_entry, 'sha256': _sha(after), 'bytes': len(after), 'presentation_id': PRESENTATION_ID}
    updated[ADDED_ROUTE] = {'path': ADDED_ROUTE, 'sha256': added_binding['sha256'],
        'bytes': added_binding['bytes'], 'presentation_id': PRESENTATION_ID}
    for name, entry in updated.items():
        value = _file(root, 'site/'+name).read_bytes()
        if _sha(value) != entry['sha256'] or len(value) != entry['bytes']:
            raise ValueError('A09 heritage changed an unlisted website byte: '+name)
    from render_a09_biography import inspect_biography
    check = inspect_biography(root)
    if check.get('status') != 'passed':
        raise ValueError('A09 historical display differs from its source rendering: '+str(check))
    report = {'path': MANIFEST, 'sha256': _sha(_file(root, MANIFEST).read_bytes()),
        'presentation_id': PRESENTATION_ID, 'publication_kind': required['publication_kind'],
        'changed_paths': list(ROUTES), 'added_paths': [ADDED_ROUTE],
        'previous_presentation_commit': PREVIOUS_COMMIT,
        'exact_predecessor_reconstruction': True, 'source_derived_rendering': True,
        'all_v1_v32_manifest_bytes_preserved': True, 'private_originals_not_published': True,
        'original_data_and_embedded_JSON_preserved': True,
        'eight_AI_research_lines_and_scientific_data_preserved': True,
        **{k: required[k] for k in ('scientific_review_status', 'release_eligible',
            'scientific_data_unchanged', 'M0_resumed', 'historical_achievement_independent_of_AI_review')}}
    return updated, {**report, 'presentation_chain': [*previous_report['presentation_chain'], report]}
