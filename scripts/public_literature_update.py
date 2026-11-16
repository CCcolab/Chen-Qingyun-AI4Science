"""Bounded, reversible presentation of newly checked historical literature.

This layer publishes summaries, never private originals or scientific releases.
It needs no Git history or network during deployment validation.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path, PurePosixPath
import re

from a01_primary_publication import (MANIFEST as A01_PRIMARY_MANIFEST,
    predecessor_bytes as a01_primary_predecessor_bytes, apply as apply_a01_primary_presentation)

MANIFEST = 'provenance/platform-presentation.v24.json'
PRESENTATION_ID = 'PLATFORM-LITERATURE-CHECKS-20261116-v24'
PREVIOUS_COMMIT = 'c8340dd5050224ac8d462560138907a8863fd82e'
PREVIOUS_MANIFEST = 'provenance/platform-presentation.v23.json'
ROUTES = ('research/index.html', 'topics/fluoromonomers/index.html')
AI = 'content/ai-research-section.v1.json'
A02 = 'content/a02-academic-achievements.v1.json'
DOCUMENTS = (AI, 'scripts/render_ai_research.py', 'docs/AI_RESEARCH_zh-CN.md',
             A02, 'docs/A02_ACADEMIC_ACHIEVEMENTS_zh-CN.md',
             'scripts/a01_publication_contract.py', 'scripts/public_literature_update.py')
PREDECESSOR_FILES = {'site/research/index.html': ('bd8902afeb1cede0bcaff717ac4e5fa26bafe027eb0af9786dc39c68e591d706', 52010), 'site/topics/fluoromonomers/index.html': ('226275b67b0ff281f0cc373e6f0ebceb91eea8c22322278a897ed2bdfdd09e11', 60034), 'content/ai-research-section.v1.json': ('b023fb4b35a1a661c310895d59770771618b49de6114e878308c569186165e56', 69152), 'scripts/render_ai_research.py': ('729298ecb6146cba6b9a78bdc2074dabb10b6a2f551f7efaf4d0a4078e29f521', 34792), 'docs/AI_RESEARCH_zh-CN.md': ('e7486227539040ef696f32d646aaa362de55c99ffb32100b6d0f5e88015448fb', 38171), 'content/a02-academic-achievements.v1.json': ('f7372dbd92a20989d814334e297931b38f07ad14c209e27e9f089cc4a720b4b9', 54170), 'docs/A02_ACADEMIC_ACHIEVEMENTS_zh-CN.md': ('1a6de57e4bce730bfd2f1ffe2a26398ab7494d92808f55515324fdbcf34473e8', 41598), 'scripts/a01_publication_contract.py': ('a0a3bb8ad112aa270e08980850e793058dfe958fa8e8f564875609f482d789b5', 308849)}
OLD_MANIFESTS = {'provenance/platform-presentation.v1.json': '1ade23238a23977b47eaa6a7dd585509fdca3e270615914292e2341721308782', 'provenance/platform-presentation.v2.json': '91434b5bc8fb51e96b604a6c6437cb363c92370347f22fcbd2a825e5498f0348', 'provenance/platform-presentation.v3.json': '2b290301102abd8cacb5a2d73f7393d8c4f851285a882a08df42eecd960ed286', 'provenance/platform-presentation.v4.json': 'cfc0bc4d29c24a846bb76ceaf3246084d406393cc7d04ec105cad539c21e120b', 'provenance/platform-presentation.v5.json': '7ac60223b0e540de62671017728acd54e66d07e8de2721006c476c8d1734bed9', 'provenance/platform-presentation.v6.json': '1077f6b2e3a78be65ea4b50e81907b629f96c9b3599fcf440493c204b33dbcf3', 'provenance/platform-presentation.v7.json': '2463a97b3bf74b629f1863892d75f36276c97bf9a111905b47cc6179b62eaa7f', 'provenance/platform-presentation.v8.json': 'ab2b362cb5c90dc4b782f8989cc127a31944c49998ee45fbded8b8a7ac77c962', 'provenance/platform-presentation.v9.json': '462fdbfe1c4bd6f0c32f39e2597764037b4562904f0acec4cce00f08c9797017', 'provenance/platform-presentation.v10.json': '65954e3ff6b484a010fa5052f5331eab55149d23a468ae354ab236462598ffd3', 'provenance/platform-presentation.v11.json': 'd6eb2a3faed6f030a28ca5b63e3f3512144c9246f39467d300fc279a967bb004', 'provenance/platform-presentation.v12.json': 'aa9efd831558b47646b687e12be30724c4b8be89a0f98ccb8d06ef56cf04e81f', 'provenance/platform-presentation.v13.json': '263b465d22b1a56b8364a0540a65f742948664f9e50e64d759543685768468cc', 'provenance/platform-presentation.v14.json': '3ea28579d130b065fb805942c5c62861d8f6cd24a0027df7fef7cdc41415750b', 'provenance/platform-presentation.v15.json': 'd21bad493ae97587c7b9493813af3393ed9ed98f5a8dfd3a8790270f7ba49aff', 'provenance/platform-presentation.v16.json': '6b975e980d176ecc481449ca5a96ffadadfecae2eb64d97dfdafb75b85b4a3c0', 'provenance/platform-presentation.v17.json': 'b635b2950e37d5387e8fb68da12109ca585833b769eec38cf25911eb86563ee1', 'provenance/platform-presentation.v18.json': '4fa6f43360d5343e119bb7b9e51e0671f1b4b4ef51ba065067459180a710dfd6', 'provenance/platform-presentation.v19.json': '1a056390024ec41126e36c8b8e6a5275415331ec6eeec524da9df8785e23d59b', 'provenance/platform-presentation.v20.json': '34814fabc405812bccc433018f8a197d181a3da9ac617f84cceda51513774b72', 'provenance/platform-presentation.v21.json': 'a353a25fc9586c3fe78de1ad42a20aee4a1c980de59eda4340df4466d9b45593', 'provenance/platform-presentation.v22.json': '3a9a746a565f7942899f5fdffc244121608e39210c7e6eb466203775dc38cae6', 'provenance/platform-presentation.v23.json': '392490c9d1ddc18942ef5b139eb094155a883f1a340e56adfc9512bfa5430a3d'}
EXPECTED_JSON_UPDATES = {'content/ai-research-section.v1.json': [{'pointer': '/lines/0/completed_summary', 'value': ['已将1960年第一报英译本647–653页的反应讨论、结构式和实验鉴定关联，形成中文科学释读；下列历史成果归原作者。', '已完成说明书质量—收率账本和指定衍生物摩尔折射的条件性数值重建，分别保留假设与未解释残差。完成计算不等于通过专业科学签认。', '已核明化合物III的MR行未列N，而结构图与元素分析式含N；原文字样并列保存，重建输入约定明确。']}, {'pointer': '/lines/0/literature_checks', 'value': [{'id': 'a01-literature-nitrogen', 'title': '化合物III：结构、MR式与元素分析的原文关系', 'historical_record': '陈庆云、N. P. Gambaryan与I. L. Knuniants的1960年论文给出硝基醇乙酸酯（本篇III）的结构、物性及元素分析，属于六氟丙酮衍生物研究。', 'summary': '原文化合物III的MR计算行印C6F6H5O4，未列N，而同页元素分析式为C6F6H5O4N，前页结构图含–CH2NO2。平台将三处并列说明并保留异文；摩尔折射重建采用与结构图、元素式一致的含N式作为显式输入。', 'source_ids': ['CQ-H12'], 'tables': [{'caption': 'CQ-H12原文化合物III的三处记载', 'columns': ['原文位置', '原报字式／结构', '平台核校范围'], 'rows': [['1114页结构图', '含–CH2NO2的结构', '与下一页物性及分析式并列'], ['1115页MR计算行', 'C6F6H5O4，未列N', '保存该行原字样，不静默补字'], ['1115页元素分析式', 'C6F6H5O4N', '含N式作为与结构／元素式一致的显式重建输入']], 'notes': []}], 'meaning': '把物性重建的分子式输入与原刊不同栏位对齐，读者可以回查计算采用了哪一个明确约定。', 'caveats': ['字样对照不证明原作者计算时删N，不裁定异文成因或真实样品结构。', '此项不是双酚AF结构、收率或机理验证。'], 'links': [{'title': '1960原刊：133卷1113–1116页', 'url': 'https://www.mathnet.ru/rus/dan23922', 'kind': 'external'}], 'scientific_review_status': 'review_required', 'release_eligible': False}]}, {'pointer': '/lines/1/records/2/summary', 'value': '已分开材料牌号、两类调聚产物和不同氟油；本轮完成1980原刊指定胺名、结构编号及产物式对照，保留正文与英文摘要对两种烯烃的不同记载。少量反向异构体线索仍限于四氯化碳体系过渡馏分，未开展新增实验或材料性能验证。'}, {'pointer': '/lines/1/boundaries/2', 'value': '1980原刊已取得并核读；指定胺名、中英文编号及产物式的文内对照已经完成。不同记载并列，尚未据此独立认证样品结构、真实产物或机理；M0继续暂停。'}, {'pointer': '/lines/1/literature_checks', 'value': [{'id': 'a02-literature-transcription', 'title': '胺名与结构编号：按原文语境对应', 'historical_record': '陈庆云、马振中、蒋锡夔、张元发、贾世茂研究偏氟乙烯与全卤代烷烃的调聚和端基衍生转化。', 'summary': '1980年调聚论文中文摘要写“乙二胺”，正文、(C2H5)2NH反应式、实验段及英文摘要则对应二乙胺。平台据正文介绍该项酰胺化转化，同时保留中文摘要原字样。 同篇部分中英文编号不同，例如全氟叔丁基取代烯烃在中文正文编号7、英文摘要编号9，酰胺则为8与10。引用同时给结构、语种和原页，避免仅因编号相同把不同产物混用。', 'source_ids': ['A02-P1980', 'CQ-H13'], 'tables': [{'caption': '同一结构在中英文部分的编号', 'columns': ['结构', '中文正文编号／原页', '英文摘要编号／原页'], 'rows': [['CCl2=CHCF2CH2CF2Cl', '6／176、179–180', '7／183'], ['(CF3)3CCH=CF2', '7／176–177、180', '9／183'], ['(CF3)3CCH2CON(C2H5)2', '8／177、180', '10／183'], ['CCl2=CHCF3', '16／178、182', '14／184']], 'notes': ['胺名对照：175页中文摘要为乙二胺；176–177、180–181页正文／图式／实验及183页英文摘要对应二乙胺。']}], 'meaning': '把端基转化关联到具体结构，而不让篇内编号或胺名异文造成化学对象误配。', 'caveats': ['编号差异和胺名字样的对照已经明确；异文成因和真实样品不由文字核校认定。', '历史实验归原作者；这里是平台AI辅助文献校勘，不是新增实验或机理验证。', '日期出处分别保留：原刊175页页头为1980年4月，期刊网页卷期既有登记为1980-03-15；印刷卷期与网页书目字段分列，不据此推定实际出版日。'], 'links': [{'title': '1980原刊：38卷175–184页', 'url': 'https://sioc-journal.cn/Jwk_hxxb/CN/Y1980/V38/I2/175', 'kind': 'external'}], 'scientific_review_status': 'review_required', 'release_eligible': False}, {'id': 'a02-literature-products', 'title': '产物式与两种烯烃记述：并列保存分歧', 'historical_record': '原论文研究调聚产物脱卤与氟化的后续转化。', 'summary': '中文正文称未发现CCl3CH2CF2CH=CF2，英文摘要却将其列为两种烯烃混合物之一；中文摘要的氟化产物式印为CCl2=CH2CF3，而正文及英文摘要为CCl2=CHCF3。平台保留这些具体差异，暂不选择一版作为实际产物的唯一记录。', 'source_ids': ['A02-P1980', 'CQ-H13'], 'tables': [{'caption': '指定产物的文内差异', 'columns': ['对象', '中文原文', '英文摘要与核校边界'], 'rows': [['CCl3CH2CF2CH=CF2', '176页称未发现；179–180页实验只报告分出的另一式', '183页列为两种烯烃混合物之一；不选择一段作实际产物的唯一记录'], ['氟化产物', '175页摘要印CCl2=CH2CF3；178／182页正文为CCl2=CHCF3', '184页为CCl2=CHCF3；保留原字式及不同编号']], 'notes': []}], 'meaning': '明确哪些是原作者各段落的不同记载，防止从摘要单独提取结构后把同篇文字差别隐藏。', 'caveats': ['“两种烯烃的混合物”不写成可能被理解为diene的“二烯烃”。', '是否实际形成第二种烯烃及异文产生原因，仍需原始分析记录或可归属更正；本条不裁定。', '不把短链调聚物转化移作六氟丙烯试制、历史橡胶或早期氟溴油的技术证据。'], 'links': [{'title': '1980原刊：38卷175–184页', 'url': 'https://sioc-journal.cn/Jwk_hxxb/CN/Y1980/V38/I2/175', 'kind': 'external'}], 'scientific_review_status': 'review_required', 'release_eligible': False}]}, {'pointer': '/lines/2/pending_items/1', 'value': '真实峰位不确定度及对应表1的UV温度、浓度和光程尚不能恢复；原刊紫外仪器Unicam SP-500已核明，20°C属于NMR。缺少的原始测量／校准依据不由平台补造。'}, {'pointer': '/lines/2/literature_checks', 'value': [{'id': 'a03-literature-uv-method', 'title': '原表重放的测量条件与不确定度边界', 'historical_record': '1966论文表1报告三种完整碘代物在所列溶剂中的紫外吸收峰和溶剂位移，用于原作者的电子效应讨论。', 'summary': '原刊24页注明紫外仪器为Unicam SP-500；相邻20°C文字属于核磁共振测量。对18–25页全文的此次核读未找到能明确对应表1的紫外温度、浓度和光程，因此这些条件仍不由平台补填。 原刊峰位显示精度与真实测量不确定度需分开。平台所用±0.05nm只是显示舍入诊断，不能当作仪器精度、实验误差或置信区间；六项换算继续称原表数值重放。', 'source_ids': ['PF01'], 'tables': [{'caption': '1966年原刊21页表1与24页方法段', 'columns': ['信息', '原文核读结果', '使用范围'], 'rows': [['紫外仪器', '24页Unicam SP-500', '仪器字段已明'], ['20°C', '24页文字属于核磁共振测量', '不移作紫外温度'], ['UV温度、浓度、光程', '在所核18–25页未找到明确对应表1的设置', '不以仪器型号或epsilon反推'], ['峰位真实不确定度', '未给足以恢复重复性／校准的不确定度依据', '±0.05 nm只作显示舍入诊断']], 'notes': []}], 'meaning': '把可回查的仪器信息与尚不能恢复的实验设置分开，限定原表数值重放所能回答的问题。', 'caveats': ['六项换算仍是同一原表的数值重放，不称光谱实验复现。', '不能从显示位数推定实验误差、置信区间或普适基团效应，也不据未报告的不确定度否定历史观察。'], 'links': [{'title': '1966原刊：32卷18–25页', 'url': 'https://sioc-journal.cn/Jwk_hxxb/CN/Y1966/V32/I1/18', 'kind': 'external'}], 'scientific_review_status': 'review_required', 'release_eligible': False}]}, {'pointer': '/lines/4/records/0/summary', 'value': '已取得并核读1978年《五氟氯乙烷合成简法》77–79页，集体署名“致冷剂小组”，对象为F-115，不能混作1978年F-53论文。另已取得CN1075708A、CN1308043A两项团队工艺专利说明书，发明人分别为林永达／梁与达、吴永明／林永达，不能改列陈庆云个人专利。配套润滑油、原中试及整机试用原表仍待取得；本平台未新增实验或工艺验证。 两份公开说明书的指定余页与原报实例已完成核读；字式、时间范围的内部差异另列，含量与产率不混为同一指标。'}, {'pointer': '/lines/4/literature_checks', 'value': [{'id': 'a05-literature-technical-text', 'title': '团队工艺说明书中的原报数据', 'historical_record': '制冷剂原刊、传记和团队工艺专利分别记录研究与工程探索。CN1075708A与CN1308043A发明人分别为林永达／梁与达、吴永明／林永达，不改列为陈庆云个人专利。', 'summary': '已核对两份公开说明书的末页实例，组成含量与产率／收率分字段保存。CN1308043A的原栏存在差别：PDF4图式左端印CH3CH2Cl，而同页正文及权利要求1写1,1,1-三氟-2-氯乙烷；PDF5表头印CF3CHCl，典型段印CF3CH2Cl；一般时间写1–7 h，表中第5行为8 h。本平台并列保存这些原字式和时窗，不静默修正，也不据此裁定排印原因。', 'source_ids': ['HERITAGE-S01', 'S1'], 'tables': [{'caption': '团队工艺说明书中的原报数据：原文对照', 'columns': ['文书', '本次核清的原报范围', '原页定位'], 'rows': [['CN1075708A', '5例GC含量／产率（%）依次为82／88、83／85.9、45.6／79.1、80／86.4、73／71；例1–4与例5的起始物不同。', 'PDF4／说明书末页'], ['CN1308043A', '6行原表收率37–68%、含量80–93%；这里只概括该表，不据此评价工业表现。', 'PDF5／说明书3页']], 'notes': []}], 'meaning': '把公开说明书中的化学对象、组成字段与收率字段逐一分开，明确技术文字能够支持什么；与传记所记中试规模、配套润滑油及整机表现分别评价。', 'caveats': ['说明书核读不等于平台实验复现、30吨规模或超临界相态验证，也不证明工业采用、保护范围或当前法律状态。传记的F-133a起点／F-134a含氯句仍按原文保留，不能仅凭HFC-134a身份判定传记必为错字。'], 'links': [{'title': 'CN1075708A公开文书入口', 'url': 'https://patents.google.com/patent/CN1075708A/zh', 'kind': 'external'}, {'title': 'CN1308043A公开文书入口', 'url': 'https://patents.google.com/patent/CN1308043A/zh', 'kind': 'external'}], 'scientific_review_status': 'review_required', 'release_eligible': False}]}, {'pointer': '/lines/5/records/0/summary', 'value': '已取得并核读1982年337–352页、670–673页及1983年1044–1057页三篇原刊。首篇署陈庆云、朱蓉仙、李宗珍、王珊娣、黄维垣，后两篇分别署陈庆云、朱士正，作者表各自登记。CQ-H16主标题原印为“全氟和多氟烷基磺酸的研究 X.”，与既有题录“磺酸酯”异文分列；670页通讯未印系列号。原刊作者名与传记异文保留，不据署名推定个人分工。三个代表断键实例已建立结构—条件—产物对应，原报收率归原作者；不把指定实例的核读扩大为全部谱图、真实结构或通用机理认证。按既有方法核读登记，2003年硅酯／二氟卡宾方法与2010年甲酯／甾体三氟甲基化分别呈现；原刊提交者与核查者名单不属于本项目新取得的专业签认。1989、2000原论文及1991书章全文仍待取得，2024既有陈试剂机理计算仍归原作者。'}, {'pointer': '/lines/5/next_step', 'value': '继续补1989、2000原论文及1991书章；对拟采用的新科学解释明确具体结构、条件和证据，不重复挂起已完成的三个原文实例对照。'}, {'pointer': '/lines/5/literature_checks', 'value': [{'id': 'a06-literature-bond-cleavage', 'title': '原刊中三项具体断键记录', 'historical_record': '1982系列IV署陈庆云、朱蓉仙、李宗珍、王珊娣、黄维垣；1982通讯与1983系列X各署陈庆云、朱士正。原作者比较不同磺酸酯与亲核试剂反应中的C–O／S–O断裂。', 'summary': '已为三个代表实例建立本篇结构定义、介质、原报条件与产物的对应。二乙二醇与DG（二乙二醇二甲醚）分别记录，各篇编号不混用。', 'source_ids': ['CQ-H07', 'CQ-H08', 'CQ-H16'], 'tables': [{'caption': '原刊中三项具体断键记录：原文对照', 'columns': ['原刊与本篇实例', '与比较有关的原报对象/条件', '原报结果与解释层级', '原页定位'], 'rows': [['CQ-H07，1982系列IV，1a', 'KI／二乙二醇；70°C、12.5 h', '2a=HCF2CF2CH2I，原报97%；原作者归为C–O断裂。', '337–338定义；348实验（PDF1–2、12）'], ['CQ-H08，1982通讯，2a', '催化量卤离子；文中KF／DG=二乙二醇二甲醚，−50°C实例', '原报磺酰氟与酰氟，正文称可定量分解；归为S–O断裂，不补造所选行未列的独立收率。', '670式(2)、671反应表及解释（PDF1–2）'], ['CQ-H16，1983系列X，1b', '少量KF／DG；先−70°C、2 h未反应，随后−60±5°C、3.5 h作用完全（均原报GC观察）', '3b酰氟90%、2b磺酰氟93%，归为S–O断裂；本篇产品2/3不等同通讯3/4编号。', '1044定义、1054实验（PDF1、11）']], 'notes': []}], 'meaning': '原文的可对照贡献是：具体酯基结构和反应条件与不同断键产物关联。原作者提出的α-F／β-醚键“屏蔽”及进攻硫解释可按原作者观点介绍，但不能替代独立机理证据。', 'caveats': ['这是有原页定位的历史实验报告核读；所列收率属于原作者，本平台未重复制备、重新鉴定全套谱图或开展DFT。三例不构成全部多氟/全氟酯的普适断键规律；1054页温度计未校正，不新增温度不确定度资格。2003硅酯／二氟卡宾与2010甲酯／甾体三氟甲基化仍分开，旧方法核读登记不写成本轮新增签认。'], 'links': [{'title': '磺酸酯历史专题与原刊题录', 'url': '../topics/perfluorosulfonates/index.html', 'kind': 'site'}], 'scientific_review_status': 'review_required', 'release_eligible': False}]}, {'pointer': '/lines/6/records/0/summary', 'value': '1999与2001年论文的31页、26页SI已取得，已核首页身份；正文仍待取得，全部谱图与机理证据未完成专业核校。申请200510031063.4的CN1752059A与CN1298686C两份说明书已取得，属同一申请的公开／授权版本，陈庆云、曹海萍为共同发明人；两版全文、权利要求合并／重编号与实施例已完成文本对照，不据此判断当前法律状态或工业采用。摘要中的SET解释不作为平台机制认证。'}, {'pointer': '/lines/6/next_step', 'value': '优先补1999、2001两篇正文，并将具体底物／谱图与已持SI对应；同申请专利文本版本对照已完成，SET机理判断仍须相应证据。'}, {'pointer': '/lines/6/literature_checks', 'value': [{'id': 'a07-literature-patent-versions', 'title': '同一申请的公开版与授权公告版', 'historical_record': '陈庆云与曹海萍为申请200510031063.4的共同发明人；CN1752059A与CN1298686C分别为该申请的公开版和历史授权公告版。', 'summary': '已完成两版全文及权利要求的逐项文本对应：13→10包含合并、重编号和具体列举调整。两版各5实施例的原报产物／产率对应一致：I(CF2)6I 72%、F(CF2)6I 59%、I(CF2)8I 80%、F(CF2)8I 66%、I(CF2)4I 67%。两版说明书优选氧化剂文字有调整，不能称全文逐字相同。', 'source_ids': ['HERITAGE-S06'], 'tables': [{'caption': '同一申请的公开版与授权公告版：原文对照', 'columns': ['公开版→授权公告版', '实际文本对照', '原页定位'], 'rows': [['A1＋A3＋A5→C1', '一般方法、氧化剂类别与盐/产物通式在C1合并表达；不等于原A3类别从文书完全消失。', '两版PDF2'], ['A4→C3', 'C3进一步列举三种过硫酸盐和KMnO4；醋酸锰/硫酸高铈类别仍见C1。', '两版PDF2'], ['A7＋A8→C5', '前驱体路径与通式变量合并表达。', '两版PDF2'], ['A13→C10', '溶剂列举重编号；保持原字式，不擅自修正名称。', '两版PDF3']], 'notes': []}], 'meaning': '该文书以含氟烷基亚磺酸盐转化为相应碘化物的技术文字为证，保留共同发明人署名，并使公开/授权版本的具体差别可回查。它与1999、2001两篇论文及其SI属于不同文献层次。', 'caveats': ['这里完成的是历史文书及指定文本版本对照，不判断保护范围等同、侵权、有效性、现行法律状态、工业采用或反应机理。原报产率不等于平台实验。1999/2001 SI已取得不等于正文或全谱核校完成；SET解释仍非平台机制认证。'], 'links': [{'title': 'CN1752059A公开文书入口', 'url': 'https://patents.google.com/patent/CN1752059A/zh', 'kind': 'external'}, {'title': 'CN1298686C授权公告文书入口', 'url': 'https://patents.google.com/patent/CN1298686C/zh', 'kind': 'external'}], 'scientific_review_status': 'review_required', 'release_eligible': False}]}, {'pointer': '/lines/7/records/0/summary', 'value': '2003年SI两卷、2007年SI与CIF、2022年SI及晚年三篇附件已取得，各篇正文的取得状态分别登记。本轮已完成2007晶体模型与SI字段对应，以及2022方法、对象和图表覆盖核读；原件差异并列保存。其他附件仍按其实际阅读范围使用，不能将文件取得或此次文献对应扩大为结构、物性和机理认证。2022既有作者计算与平台未来工作分开，M0继续暂停。'}, {'pointer': '/lines/7/next_step', 'value': '继续补对应正文，以具体科学主张核对所需证据；已有晶体模型对应和既有计算覆盖不再笼统挂作未读，未来问题先与原作者方法及简化范围比较。'}, {'pointer': '/lines/7/literature_checks', 'value': [{'id': 'a08-literature-crystal-models', 'title': '20π大环：结构证据与晶体模型范围', 'historical_record': 'Chao Liu、Dong-Mei Shen与Qing-Yun Chen的2007年研究围绕CF₃取代卟啉，报告还原得到的isophlorin 2、其N-甲基化衍生物3和4，以及Ni配合物5。附件把制备与表征、晶体构型以及核磁/吸收观察并列，为讨论化学修饰、骨架形变与电子结构的关系留下具体资料。非芳香性的表述须对应原文对象，不能只凭20π电子数改称反芳香。', 'summary': '2007年论文附件分别给出isophlorin 2、N-二甲基化3、N-四甲基化4和Ni配合物5的资料。SI S9表1与四份CIF可以一一对应；2—4的晶体总式含溶剂，部分模型存在无序或分占位；5的晶体式与产物母体式一致。须区分各晶体模型、游离产物式和分析样品约定。CIF实际采用约束或混合氢处理，部分非氢原子为各向同性处理；采集角度/权重的SI概述与CIF字段差别照录。平台完成的是材料对应与限定释读，不是重新精修或独立晶体认证。', 'source_ids': ['CQ-R10'], 'tables': [{'caption': '2007年原作者化合物与附件证据', 'columns': ['原作者对象', '证据定位', '平台对照与限度'], 'rows': [['isophlorin 2、N-二甲基化3、N-四甲基化4、Ni配合物5', 'SI S2–S4，S9表1，S10–S12；对应CIF', '将具体分子与各晶体模型对应；不能仅凭20π电子数裁定反芳香性'], ['游离产物式与晶体总式', 'SI表征式及CIF组成／占位字段', '2—4的晶体总式含溶剂，部分模型存在无序或分占位；5的晶体式与产物母体式一致，不把含溶剂总式当游离产物式'], ['精修与采集字段', 'S9概述与CIF的氢／ADP／角度／权重字段', 'CIF含约束或混合氢处理、部分非氢Uiso；保留SI概述与字段差别']], 'notes': []}], 'meaning': '使化学修饰、分子构型与电子性质讨论有具体对象和证据位置，避免把晶体模型或电子计数代作完整结构认证。', 'caveats': ['对应与字段核校不等于重新精修、原始衍射数据验证或独立晶体认证。', '保留原作者Chao Liu、Dong-Mei Shen、Qing-Yun Chen的归属；本轮不是新增制备或DFT。', 'SI与CIF已取得；JACS正文仍未取得，不以附件冒充正文核读。'], 'links': [{'title': '2007年论文与出版社附件', 'url': 'https://pubs.acs.org/doi/10.1021/ja070855c', 'kind': 'external'}, {'title': '2007年出版社SI原件', 'url': 'https://ndownloader.figshare.com/files/4710160', 'kind': 'external'}], 'scientific_review_status': 'review_required', 'release_eligible': False}, {'id': 'a08-literature-existing-theory', 'title': 'Porphyriynes：原作者已有理论研究的对象与模型', 'historical_record': '2022年团队论文报告含三键的18π共轭大环Porphyriynes，并在附件中提供制备、结构和光谱资料，以及原作者已有的DFT/TD-DFT、芳香性描述和候选反应路径计算。实验结构、性质模型与简化路径各有证据范围，后续AI研究应先与这些作者工作比较，保留全部合作者归属。', 'summary': '2022年SI S15—S20以PBE0/6-31G*比较Pyne1与NCTPP的几何、轨道、TD-DFT吸收及芳香性指标；S16另列M062X//6-311+G*/LANL2DZ与SMD/THF用于相关路径模型。性质图中的四苯基大环与S38—S54路径坐标的去苯基简化核须分开：后者名为Pyne1的坐标为C₂₂H₁₈N₄O，实验对象为C₄₆H₃₄N₄O。Scheme S2原标ΔE(kJ/mol)，不能改称活化自由能；所列虚频也不能代替负模和双向IRC连接证据。这些是原作者既有研究，平台本轮没有新计算。', 'source_ids': ['CQ-H20'], 'tables': [{'caption': '2022年原作者实验／性质计算／路径模型分别呈现', 'columns': ['问题', '原文证据与模型', '定位及边界'], 'rows': [['三键局部几何的实验/计算对照', 'Table S5中C13–C14：Pyne1晶体1.221 Å、DFT1.24 Å，NCTPP DFT1.40 Å。 PBE0/6-31G*几何；Figure S4为带四苯基大环的展示', 'S12—S16；Table S5；限定原作者数据对照，不称平台新结构测定或独立优化验证。'], ['吸收与芳香性证据', 'TDDFT表与实验UV-Vis分列；NICS/HOMA/FLU等指标及ACID图分别报告。 Pyne1/NCTPP，PBE0/6-31G*；ACID等值面0.030', 'S6、S15—S20；Figure S3/S6/S7、Table S6—S8；不同指标排序不能合成无条件“芳香性增强”；实验多溶剂谱/CH2Cl2数据与各计算溶剂不擅自等同；轨道差不直接等于实验光学带隙。'], ['候选路径', 'Scheme S2及详细坐标/能量表显示含LiOH/CH3I的候选分支。 原印M062X//6-311+G*/LANL2DZ，SMD/THF；去四苯基的简化核路径', 'S16、S21、S38—S54；图中标示的ΔE不是已核定ΔG‡；打印负频不代完整频率、反应模式和双向IRC；简化路径不冒充实验分子完整机理。']], 'notes': ['方法段S16写Gaussian 09 D01，S55引文写Revision A.02；按两个来源字段保留，不据此擅自改写实际运行版本。']}], 'meaning': '明确原作者已研究的问题、方法与简化范围；后续AI工作须先与这些专业研究比较，不能包装成首次理论研究。', 'caveats': ['本轮只核文献覆盖，不重新计算能量、结构、光谱或芳香性指标，不据合著认定陈先生本人执行计算。', 'Scheme S2原标ΔE(kJ/mol)，不能直接称ΔG‡；不同组分能量需守恒参照，所列单个虚频不代替全频率、目标负模与双向IRC连接证据。', '全分子性质模型与去四苯基简化核路径分别评价；不同芳香性指标排序不合成无条件“芳香性全面增强”。', 'SI已取得，2022正文仍未取得；M0继续暂停，原作者工作不作平台实验或机理验证。'], 'links': [{'title': '2022年论文', 'url': 'https://doi.org/10.1021/acs.orglett.2c00356', 'kind': 'external'}, {'title': '2022年出版社SI原件', 'url': 'https://ndownloader.figshare.com/files/34165511', 'kind': 'external'}], 'scientific_review_status': 'review_required', 'release_eligible': False}]}], 'content/a02-academic-achievements.v1.json': [{'pointer': '/paper/reading_scope', 'value': '已取得原刊175–184页并核读全部10页；指定胺名、中英文结构编号及产物式的文内对照已完成。文献观察、原作者解释与平台核校分开，不授予真实样品结构或机理认证。'}, {'pointer': '/paper/observations/3/finding', 'value': '部分调聚物经后续转化得到烯烃、含氟酰胺与羧酸。正文图式、实验及英文摘要对应二乙胺，中文摘要原印“乙二胺”；该具体文内差异已完成对照并保留原字样，平台AI核校说明另列于研究资料页。'}, {'pointer': '/paper/limits', 'value': ['原文对极性因素的讨论保留原作者解释身份；主要方向不等于100%选择性，谱学与化学互证也不是平台新机理验证。', '所列调聚物、调聚氟溴陀螺油、全氟烃油及氟橡胶牌号不是同一化学对象；产物系列与历史工业产品不能只凭名称相似等同。', '表3的n按该酸式独立定义，不把不同表的编号或计数混用。收率、熔点和紫外数值为历史原报值，不是平台新实验或现代性能认证。', '部分调聚羧酸碱金属盐的乳化用途属原文定性报告；未从该文取得可直接引用的定量乳化性能对照，不据此推断产业采用或环境安全。', '指定胺名、编号和产物式对照已完成；中文正文与英文摘要对两种烯烃的不同记述仍并列保存，不据此选择一版作为实际实验产物或裁定异文成因。']}, {'pointer': '/pending', 'value': ['六氟丙烯原始试制、低温分离装置及交付档案待补；氟橡胶1号前期成果、后续2号／3号的原始牌号、组成与技术交接记录分别核对。', '调聚氟溴陀螺油所引2009年机构史p.291原页、配方和实测质量档案待补，不把传记中的历史应用时态平移为当代现状。', '机构生平写“四氟乙烯”，纪念资料S1写“聚四氟乙烯”；两种投料称谓的关系待原始路线与装置记录核对，不预设为同一物料。', '1963年他组原文确认PTFE热裂与低温分馏的同期技术，但与陈团队供料、合作和原始装置的关联仍未建立；不能借它消除两机构投料称谓差异。', 'FJ-23与历史2号／3号之间的对应文书，以及2号／3号原始配方和实测物性表仍缺；不以现代商业牌号填表。', '1986年FL-G氟氯液体与早期调聚氟溴陀螺油分列；前者有物性原报值和供样致谢，不能直接归陈个人或代作后者性能证据。', '传记p.37从二氟一氯甲烷制四氟乙烯的观察谈起；与机构TFE／PTFE记载的原料、过程层次及批次关系待原始工艺核对，不武断判定矛盾或拼成单一路线。', '《陈庆云访谈》2018-01-03原录音／逐字稿、六氟丙烯同期试制和装置原件未取得；低温分馏分工仍据传记。', 'FJ-23登记与晚近1号授奖回顾分列；1966原证书、历史2号／3号技术物性附件待核。', '氟溴油传记引《中国科学院》2009版p.291缺册次；已定位较早版馆藏与电子书检索途径，未取得目标原页。', '2018本人访谈已定位采集项目与学术检索入口，完整原录、当次档号和采访者仍待核；5月15日照片不转作1月3日采访证据。', '2009版《中国科学院》p.291册次仍未核定；新提供的《中国科学院年鉴·2009》（科学出版社）与目标书分开，需调阅正确分册版权页、目录及p.290–292。']}, {'pointer': '/ai_scope', 'value': '平台AI工作包括已有原刊核读、对象消歧和引据追踪。已区分2018访谈元数据、项目目录、公开专题片、馆藏及目标书页；访谈原录和2009版《中国科学院》p.291均未取得，册次仍待核。历史成果仍归陈先生及原合作者，其他团队资料仅作背景；未新增六氟丙烯试制、装置、2号／3号技术物性或早期氟溴油原件。尚未开展本线新的复算、量化计算、实验或材料性能验证。M0继续暂停；释读保持review_required、release_eligible=false。 指定胺名、结构编号和产物式的AI辅助文献核校已完成，对照与原页见下一层研究资料；历史成果正文与平台新增释读分开，文字校勘不作实验或机理验证。'}]}
RENDERER_SHA256 = 'c4cfba4d66c616b4a04d258ec4b1f644dd8858cd2734693dd3c8efbd60ed135a'
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
        raise ValueError('Unsafe or missing literature-presentation file: '+str(name))
    return path


def _json(root: Path, name: str):
    return json.loads(a01_primary_predecessor_bytes(root, name))


def predecessor_bytes(root: Path, name: str) -> bytes:
    """Recover exact fixed c8340dd bytes before replaying the immutable chain."""
    current = a01_primary_predecessor_bytes(root, name)
    if not (root/MANIFEST).exists():
        return current
    data = _json(root, MANIFEST)
    if not isinstance(data, dict):
        raise ValueError('Literature presentation requires a JSON object')
    records, pool = data.get('reversible_text_files'), data.get('reverse_text_patch_pool')
    if not isinstance(records, list) or not isinstance(pool, list):
        raise ValueError('Literature presentation requires exact reverse text patches')
    matches = [row for row in records if isinstance(row, dict) and row.get('path') == name]
    if not matches:
        if name in PREDECESSOR_FILES:
            raise ValueError('Missing fixed literature predecessor: '+name)
        return current
    if len(matches) != 1 or name not in PREDECESSOR_FILES:
        raise ValueError('Unauthorized or duplicate literature predecessor: '+name)
    row = matches[0]
    old_sha, old_size = PREDECESSOR_FILES[name]
    if (row.get('old_sha256') != old_sha or row.get('old_bytes') != old_size
            or _sha(current) != row.get('new_sha256') or len(current) != row.get('new_bytes')):
        raise ValueError('Literature file differs from complete old/new identities: '+name)
    edits = row.get('edits')
    if not isinstance(edits, list) or not edits:
        raise ValueError('Literature changes require nonempty text edits: '+name)
    chunks, cursor, old_end, delta = [], 0, 0, 0
    for edit in edits:
        if not isinstance(edit, dict) or set(edit) != {'old_offset', 'replacement'}:
            raise ValueError('Invalid literature reverse text edit: '+name)
        offset, replacement = edit['old_offset'], edit['replacement']
        if (type(offset) is not int or offset < old_end or type(replacement) is not int
                or not 0 <= replacement < len(pool)):
            raise ValueError('Overlapping or invalid literature reverse edit: '+name)
        pair = pool[replacement]
        if (not isinstance(pair, dict) or set(pair) != {'old', 'new'}
                or not all(isinstance(pair.get(k), str) for k in ('old', 'new'))
                or pair['old'] == pair['new']):
            raise ValueError('Invalid literature replacement pool')
        before, after = pair['old'].encode('utf-8'), pair['new'].encode('utf-8')
        position = offset+delta
        if position < cursor or current[position:position+len(after)] != after:
            raise ValueError('Literature reverse replacement differs at exact offset: '+name)
        chunks.extend((current[cursor:position], before))
        cursor, old_end = position+len(after), offset+len(before)
        delta += len(after)-len(before)
    rebuilt = b''.join((*chunks, current[cursor:]))
    if _sha(rebuilt) != old_sha or len(rebuilt) != old_size:
        raise ValueError('Literature predecessor cannot be reconstructed exactly: '+name)
    return rebuilt


def _set_pointer(data, pointer: str, value):
    parts = [p.replace('~1', '/').replace('~0', '~') for p in pointer.split('/')[1:]]
    if not pointer.startswith('/') or not parts:
        raise ValueError('Invalid fixed literature JSON pointer')
    parent = data
    for part in parts[:-1]:
        parent = parent[int(part)] if isinstance(parent, list) else parent[part]
    key = int(parts[-1]) if isinstance(parent, list) else parts[-1]
    parent[key] = copy.deepcopy(value)


def _binding(root: Path, name: str) -> dict:
    data = a01_primary_predecessor_bytes(root, name)
    return {'path': name, 'sha256': _sha(data), 'bytes': len(data)}


def apply(root: Path, entries: dict, previous_report: dict) -> tuple[dict, dict]:
    """Validate only the fixed literature update after historical v23 replay."""
    if not (root/MANIFEST).exists():
        if (root/A01_PRIMARY_MANIFEST).exists():
            raise ValueError('A01 primary presentation requires its immutable v24 predecessor')
        return entries, previous_report
    if not (root/PREVIOUS_MANIFEST).is_file():
        raise ValueError('Literature presentation requires the immutable v23 predecessor')
    for name, sha in OLD_MANIFESTS.items():
        if _sha(a01_primary_predecessor_bytes(root, name)) != sha:
            raise ValueError('Historical presentation manifest changed: '+name)
    data = _json(root, MANIFEST)
    required = {
        'schema_version': '24.0', 'presentation_id': PRESENTATION_ID,
        'publication_kind': 'platform_sourced_literature_checks',
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
        'allowed_json_updates': {name: [u['pointer'] for u in updates]
                                 for name, updates in EXPECTED_JSON_UPDATES.items()},
    }
    if (not isinstance(data, dict) or any(data.get(k) != v for k, v in required.items())
            or any(data.get(k) is not required[k] for k in ('release_eligible',
                'scientific_data_unchanged', 'M0_resumed', 'historical_achievement_independent_of_AI_review'))
            or any(type(data.get(k)) is not int or data[k] != 0 for k in ('new_quantum_calls', 'new_model_API_calls'))
            or not isinstance(data.get('authorization'), str) or not data['authorization'].strip()):
        raise ValueError('Unsupported bounded literature presentation v24')
    records, pool = data.get('reversible_text_files'), data.get('reverse_text_patch_pool')
    if (not isinstance(records, list) or not isinstance(pool, list) or not pool
            or any(not isinstance(row, dict) for row in records)
            or len(records) != len(PREDECESSOR_FILES)
            or {row.get('path') for row in records} != set(PREDECESSOR_FILES)
            or len({row.get('path') for row in records}) != len(records)
            or any(not isinstance(row.get('edits'), list) or not row['edits'] or any(
                not isinstance(edit, dict) or type(edit.get('replacement')) is not int
                for edit in row['edits']) for row in records)):
        raise ValueError('Literature presentation may change only its eight fixed predecessor files')
    if {edit['replacement'] for row in records for edit in row['edits']} != set(range(len(pool))):
        raise ValueError('Literature presentation requires exactly its used replacement pool')
    for name, (sha, size) in PREDECESSOR_FILES.items():
        old = predecessor_bytes(root, name)
        if _sha(old) != sha or len(old) != size or old == a01_primary_predecessor_bytes(root, name):
            raise ValueError('Literature predecessor differs from fixed c8340dd: '+name)
    for name, updates in EXPECTED_JSON_UPDATES.items():
        expected = json.loads(predecessor_bytes(root, name))
        for update in updates:
            _set_pointer(expected, update['pointer'], update['value'])
        if _json(root, name) != expected:
            raise ValueError('Literature JSON differs outside its fixed field updates: '+name)
    if _sha(a01_primary_predecessor_bytes(root, 'scripts/render_ai_research.py')) != RENDERER_SHA256:
        raise ValueError('Literature renderer differs from reviewed fixed implementation')
    for name in (AI, A02, 'site/research/index.html', 'site/topics/fluoromonomers/index.html',
                 'docs/AI_RESEARCH_zh-CN.md', 'docs/A02_ACADEMIC_ACHIEVEMENTS_zh-CN.md'):
        text = a01_primary_predecessor_bytes(root, name).decode('utf-8')
        if re.search(r'(?i)private-sources|current-item-register|现阶段待查事项统计|[CD]:[\\/]', text):
            raise ValueError('Private evidence or a local path leaked into public literature display: '+name)
    changes = data.get('changes')
    if (not isinstance(changes, list) or len(changes) != len(ROUTES)
            or any(not isinstance(row, dict) for row in changes)
            or {row.get('path') for row in changes} != set(ROUTES)):
        raise ValueError('Literature presentation may change only its two existing routes')
    updated = {name: dict(row) for name, row in entries.items()}
    json_scripts = re.compile(r'<script\b[^>]*\btype\s*=\s*["\']application/(?:ld\+)?json["\'][^>]*>.*?</script\s*>', re.I | re.S)
    for item in changes:
        route = item['path']; old_entry = entries[route]
        before = predecessor_bytes(root, 'site/'+route)
        after = a01_primary_predecessor_bytes(root, 'site/'+route)
        if (item.get('old_sha256') != old_entry['sha256'] or item.get('old_bytes') != old_entry['bytes']
                or _sha(before) != old_entry['sha256'] or len(before) != old_entry['bytes']
                or item.get('new_sha256') != _sha(after) or item.get('new_bytes') != len(after)
                or before == after or not isinstance(item.get('reason'), str) or not item['reason'].strip()):
            raise ValueError('Literature route differs from complete old/new identities: '+route)
        source, current = before.decode('utf-8'), after.decode('utf-8')
        if json_scripts.findall(source) != json_scripts.findall(current):
            raise ValueError('Literature presentation changed embedded JSON: '+route)
        old_ids = re.findall(r'\bid="([^\"]+)"', source)
        new_ids = re.findall(r'\bid="([^\"]+)"', current)
        if not set(old_ids).issubset(new_ids) or len(new_ids) != len(set(new_ids)):
            raise ValueError('Literature presentation lost or duplicated source/navigation IDs: '+route)
        updated[route] = {**old_entry, 'sha256': _sha(after), 'bytes': len(after), 'presentation_id': PRESENTATION_ID}
    for name, expected in updated.items():
        value = a01_primary_predecessor_bytes(root, 'site/'+name)
        if _sha(value) != expected['sha256'] or len(value) != expected['bytes']:
            raise ValueError('Literature update changed an unlisted website byte: '+name)
    # v24 replays its fixed bytes; v25 checks complete current A01/AI rendering.
    if not (root/A01_PRIMARY_MANIFEST).exists():
        from render_ai_research import inspect_ai_research
        from render_a02_history import inspect_a02_history
        checks = [inspect_ai_research(root), inspect_a02_history(root)]
        if any(c.get('status') != 'passed' for c in checks):
            raise ValueError('Literature display differs from its current source rendering: '+str(checks))
    report = {'path': MANIFEST, 'sha256': _sha(_file(root, MANIFEST).read_bytes()),
        'presentation_id': PRESENTATION_ID, 'publication_kind': required['publication_kind'],
        'changed_paths': list(ROUTES), 'added_paths': [],
        'previous_presentation_commit': PREVIOUS_COMMIT,
        'exact_predecessor_reconstruction': True, 'source_derived_rendering': True,
        'all_v1_v23_manifest_bytes_preserved': True, 'private_originals_not_published': True,
        'homepage_original_JSON_and_scientific_data_preserved': True,
        **{k: required[k] for k in ('scientific_review_status', 'release_eligible',
            'scientific_data_unchanged', 'M0_resumed', 'historical_achievement_independent_of_AI_review')}}
    return apply_a01_primary_presentation(root, updated,
        {**report, 'presentation_chain': [*previous_report['presentation_chain'], report]})
