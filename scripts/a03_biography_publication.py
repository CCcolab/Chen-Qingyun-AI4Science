"""Bounded A03 history and scope presentation; original scientific data protected."""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path, PurePosixPath
import re

MANIFEST = 'provenance/platform-presentation.v27.json'
PRESENTATION_ID = 'PLATFORM-A03-BIOGRAPHY-20261116-v27'
PREVIOUS_COMMIT = '3c85d86ab406a05f960f477fba40e37632912b38'
PREVIOUS_MANIFEST = 'provenance/platform-presentation.v26.json'
ROUTES = ('pftb/index.html', 'research/index.html')
AI = 'content/ai-research-section.v1.json'
DOCUMENTS = ('content/ai-research-section.v1.json', 'scripts/render_ai_research.py', 'docs/AI_RESEARCH_zh-CN.md', 'content/a03-biography-narrative.v1.json', 'scripts/render_a03_biography.py', 'docs/A03_ACADEMIC_ACHIEVEMENTS_zh-CN.md', 'scripts/a02_biography_publication.py', 'scripts/a01_publication_contract.py', 'scripts/a03_biography_publication.py')
PREDECESSOR_FILES = {'site/pftb/index.html': ('42ca404f2ed70b7a3b0b5d8b0eb742a2509e5a5a70fd0be36a65028e61cbd1f6', 97587), 'content/ai-research-section.v1.json': ('a113f3b6f1170f3a2209b007a88e45e126ef36aa153b73f401e22488a1edefee', 95684), 'scripts/render_ai_research.py': ('c4cfba4d66c616b4a04d258ec4b1f644dd8858cd2734693dd3c8efbd60ed135a', 40484), 'docs/AI_RESEARCH_zh-CN.md': ('fa475e7192d225c2a86ecff9bf227dab4427c207dd0b45b24386d2cc3bbd22b1', 56290), 'site/research/index.html': ('893f3f543cd573cf79275e3b46e9a20cad615ac4670f6a9bbcb5f4799817df02', 77246), 'scripts/a02_biography_publication.py': ('0d65572fc5f9b4b6693050dc5009abcc2e98522e188fcc5ace53041bc39e88a5', 23298), 'scripts/a01_publication_contract.py': ('1c6789296e3b22344ceeea647481af6d12169c1b34a8a13fbcf8fbe0a762c738', 309961)}
PROTECTED_FILES = {'site/index.html': ('8b3532ee45c0fb33912f20a3bd7943043a348f10a370b9c6716e9edf3c0abf41', 257766), 'site/data/public-sources.json': ('94f8b9f6d0849deb9f26f75947205cfc8c4eb0973045fe958f2121237d987062', 33608), 'site/data/achievement-lines.json': ('1c9ec28bf41a7d79214e84a1c07f3bea1e0d91630dd3a88c93c39ff68a9bccec', 39768), 'data/pftb1966_table1.csv': ('92af88d5c1307d0a01b418354d2620a0d9eb8a8c68766adedd8be0feec2ff29a', 515), 'results/pftb1966-uv-replay.json': ('c83794634136e2bd08d09b806b400eea603cf1c27c753ca3db2951b9c2c99432', 7691), 'results/REPLAY_REPORT_zh-CN.md': ('062aca44324f015450198a4bcc2ddba6aa98d896c31dbc81de407991d78b800b', 2976)}
OLD_MANIFESTS = {'provenance/platform-presentation.v1.json': '1ade23238a23977b47eaa6a7dd585509fdca3e270615914292e2341721308782', 'provenance/platform-presentation.v2.json': '91434b5bc8fb51e96b604a6c6437cb363c92370347f22fcbd2a825e5498f0348', 'provenance/platform-presentation.v3.json': '2b290301102abd8cacb5a2d73f7393d8c4f851285a882a08df42eecd960ed286', 'provenance/platform-presentation.v4.json': 'cfc0bc4d29c24a846bb76ceaf3246084d406393cc7d04ec105cad539c21e120b', 'provenance/platform-presentation.v5.json': '7ac60223b0e540de62671017728acd54e66d07e8de2721006c476c8d1734bed9', 'provenance/platform-presentation.v6.json': '1077f6b2e3a78be65ea4b50e81907b629f96c9b3599fcf440493c204b33dbcf3', 'provenance/platform-presentation.v7.json': '2463a97b3bf74b629f1863892d75f36276c97bf9a111905b47cc6179b62eaa7f', 'provenance/platform-presentation.v8.json': 'ab2b362cb5c90dc4b782f8989cc127a31944c49998ee45fbded8b8a7ac77c962', 'provenance/platform-presentation.v9.json': '462fdbfe1c4bd6f0c32f39e2597764037b4562904f0acec4cce00f08c9797017', 'provenance/platform-presentation.v10.json': '65954e3ff6b484a010fa5052f5331eab55149d23a468ae354ab236462598ffd3', 'provenance/platform-presentation.v11.json': 'd6eb2a3faed6f030a28ca5b63e3f3512144c9246f39467d300fc279a967bb004', 'provenance/platform-presentation.v12.json': 'aa9efd831558b47646b687e12be30724c4b8be89a0f98ccb8d06ef56cf04e81f', 'provenance/platform-presentation.v13.json': '263b465d22b1a56b8364a0540a65f742948664f9e50e64d759543685768468cc', 'provenance/platform-presentation.v14.json': '3ea28579d130b065fb805942c5c62861d8f6cd24a0027df7fef7cdc41415750b', 'provenance/platform-presentation.v15.json': 'd21bad493ae97587c7b9493813af3393ed9ed98f5a8dfd3a8790270f7ba49aff', 'provenance/platform-presentation.v16.json': '6b975e980d176ecc481449ca5a96ffadadfecae2eb64d97dfdafb75b85b4a3c0', 'provenance/platform-presentation.v17.json': 'b635b2950e37d5387e8fb68da12109ca585833b769eec38cf25911eb86563ee1', 'provenance/platform-presentation.v18.json': '4fa6f43360d5343e119bb7b9e51e0671f1b4b4ef51ba065067459180a710dfd6', 'provenance/platform-presentation.v19.json': '1a056390024ec41126e36c8b8e6a5275415331ec6eeec524da9df8785e23d59b', 'provenance/platform-presentation.v20.json': '34814fabc405812bccc433018f8a197d181a3da9ac617f84cceda51513774b72', 'provenance/platform-presentation.v21.json': 'a353a25fc9586c3fe78de1ad42a20aee4a1c980de59eda4340df4466d9b45593', 'provenance/platform-presentation.v22.json': '3a9a746a565f7942899f5fdffc244121608e39210c7e6eb466203775dc38cae6', 'provenance/platform-presentation.v23.json': '392490c9d1ddc18942ef5b139eb094155a883f1a340e56adfc9512bfa5430a3d', 'provenance/platform-presentation.v24.json': '118a96428bf0a0fce5467fffd8861c419f97ac078aed708b6fd3b5e6318cc242', 'provenance/platform-presentation.v25.json': '61b8e4ebc4e4800253d886a617b98c9590c370c5ae494731edc8135ebf15e9c1', 'provenance/platform-presentation.v26.json': '0215099d811ba22ee7224e17a2603d3fdccd7dd0b7473297d35ceb419966bd2d'}
EXPECTED_AI_UPDATES = [{'pointer': '/lines/2/question', 'value': '原作者怎样把全氟叔丁基卤化物的制备、特殊反应和光谱比较联系起来？平台能从原表重现哪些数字？'}, {'pointer': '/lines/2/ai_role', 'value': '以传记为主线关联人物、化合物、原论文和学术贡献；对平台新增引用核对出处与转录。已保存的数值工作限于原表波长差、波数蓝移与假定扰动诊断，历史成果归原作者。'}, {'pointer': '/lines/2/records', 'value': [{'title': '历史成果与合作脉络', 'summary': '已将传记42–45页与1966年原论文联系，介绍全氟叔丁基卤化物的制备和结构研究、亲核试剂作用下的反应行为、光谱与诱导效应讨论，并分别说明陈庆云、蒋锡夔、陈秉启、梁梦兰的合作。采用Krespan方法与团队随后开展的研究分开归属；这些是原作者的成果，平台新增的是资料整理。', 'links': [{'title': 'A03（全氟叔丁基（PFtB）化学）：成果、合作与参考资料', 'url': '../pftb/index.html', 'kind': 'site'}]}, {'title': '现有资料与记录', 'summary': '已按1966年原表转录10个波长记录，其中9个配对记录形成6项位移；波长差、波数蓝移与有界扰动诊断属于同批原表数值重放。原刊印刷21页表1及24页实验部分的引用已核对：紫外仪器为Unicam SP-500；20°C注明于核磁共振测量，不能移作紫外温度。这些整理没有补出未知的实验条件或真实不确定度。', 'links': [{'title': 'PF1966-UV-T1数值重放报告', 'url': 'https://github.com/CCcolab/Chen-Qingyun-AI4Science/blob/main/results/REPLAY_REPORT_zh-CN.md', 'kind': 'repo'}, {'title': '原表转录数据', 'url': 'https://github.com/CCcolab/Chen-Qingyun-AI4Science/blob/main/data/pftb1966_table1.csv', 'kind': 'repo'}, {'title': '既有重放结果', 'url': 'https://github.com/CCcolab/Chen-Qingyun-AI4Science/blob/main/results/pftb1966-uv-replay.json', 'kind': 'repo'}, {'title': '1966原刊：表1见印刷21页，仪器见24页', 'url': 'https://sioc-journal.cn/Jwk_hxxb/CN/Y1966/V32/I1/18', 'kind': 'external'}]}]}, {'pointer': '/lines/2/boundaries/1', 'value': '原作者的历史成果不以平台的转录签认为成立前提。平台未开展新的光谱实验、峰拟合或量子化学计算，新增释读保持review_required、release_eligible=false。'}, {'pointer': '/lines/2/next_step', 'value': '围绕原作者已发表的具体结果继续组织学术叙事；只核对平台新增引用，不将反复取得或核验资料作为研究主线。'}, {'pointer': '/lines/2/future_question', 'value': '若今后提出独立研究，应先说明如何区分完整分子的溶剂相互作用与基团效应，并比较已有研究；目前没有启动新实验或模型计算。'}, {'pointer': '/lines/2/source_links', 'value': [{'title': 'A03（全氟叔丁基（PFtB）化学）：历史成果与合作', 'url': '../pftb/index.html', 'kind': 'site'}, {'title': 'A03（全氟叔丁基（PFtB）化学）：原论文论证细读', 'url': '../pftb/index.html#arguments', 'kind': 'site'}]}, {'pointer': '/lines/2/pending_items/0', 'value': '平台保存的是原表转录及数值重放；未重新测量光谱、重建完整谱线或进行峰拟合。'}, {'pointer': '/lines/2/pending_items/1', 'value': '真实峰位不确定度及对应表1的UV温度、浓度和光程不能由现有整理恢复；Unicam SP-500为紫外仪器，20°C属于NMR。显示舍入诊断不是实验误差。'}, {'pointer': '/lines/2/pending_items/2', 'value': '完整碘代物的位移不能直接搬作普适基团常数；不补造CF₃I、C₂F₅I数据，不用六项换算认证反应机理。'}, {'pointer': '/lines/2/future_items/0', 'value': '若未来开展独立光谱或现代模型研究，应先限定化合物、溶剂和可区分的科学问题，比较已有工作并另定协议；目前仅为设想。'}, {'pointer': '/lines/2/future_items/1', 'value': '当前聚焦既有学术成果的呈现与资料整理；M0继续暂停，未启动新的计算或实验。'}, {'pointer': '/lines/2/pending_title', 'value': '适用范围与科学边界'}]
NEW_FILES = ('content/a03-biography-narrative.v1.json', 'scripts/render_a03_biography.py', 'docs/A03_ACADEMIC_ACHIEVEMENTS_zh-CN.md', 'scripts/a03_biography_publication.py', 'provenance/platform-presentation.v27.json')
REVIEWED_PUBLIC_FILES = {'content/a03-biography-narrative.v1.json': '193b5dce331269d1cc41042ab3ec9d3053d1f8911aa54d768866b921e1f64e49', 'scripts/render_a03_biography.py': '872ecaedbf68f278495b6594fc9e65f1823e65077bd4b2ef301487f828857b9c', 'docs/A03_ACADEMIC_ACHIEVEMENTS_zh-CN.md': 'c0ff6a8f7728083c8f660a221dddafc0ee35260d0cac723d392795b1c216cbd2', 'scripts/render_ai_research.py': 'a00ecc2e75f047e100a51ab296f4192c0e93d6de10a70f0754740794faa839f7'}
PUBLIC_DISPLAYS = ('content/a03-biography-narrative.v1.json', 'docs/A03_ACADEMIC_ACHIEVEMENTS_zh-CN.md', 'content/ai-research-section.v1.json', 'docs/AI_RESEARCH_zh-CN.md', 'site/pftb/index.html', 'site/research/index.html')
PFTB_SPEC = {'insertion_offset': 24761, 'insertion_text': '<!-- A03_BIOGRAPHY_HISTORY:BEGIN -->\n<style id="a03-biography-style">.a03-biography-card{margin:24px 0;padding:20px;border:1px solid var(--line);border-radius:8px}.a03-biography-meaning{border-left:3px solid #aa7545;padding-left:14px}.a03-biography-locator{font-size:.85rem;color:var(--muted)}.a03-biography-table{overflow-x:auto}.a03-biography-table table{border-collapse:collapse;min-width:620px;width:100%}.a03-biography-table th,.a03-biography-table td{padding:12px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line)}#a03-biography-history a{overflow-wrap:anywhere}</style>\n<section id="a03-biography-history"><div class="wrap"><div class="sec-head"><h2>A03 全氟叔丁基（PFtB）化学：新化合物、反应行为与电子效应</h2><p>历史成果与合作</p></div><p>《氟缘笃志：陈庆云传》将这项工作放在应用材料研究与基础氟化学相互推动的背景中：六氟丙烯制备过程中少量副产的全氟异丁烯，成为探索全氟叔丁基化学的起点。陈庆云与同事把制备、结构证据、化学反应和光谱比较联系起来，形成了具有开拓意义的基础研究。</p>\n<article class="a03-biography-card" id="a03-biography-contribution-1"><h3>从副产物出发，建立全氟叔丁基卤化物的研究对象</h3><p>传记记载，陈庆云、陈秉启运用Krespan的方法制备全氟叔丁基碘，并开展结构研究；进一步以溴得到相应溴化物。1966年论文将元素分析、红外、氟核磁及化学反应结合起来讨论结构。这里保留原方法的来源：采用和发展已有制备方法，与随后对这些化合物开展的研究分别介绍。</p><p class="a03-biography-meaning"><b>学术意义：</b>其贡献在于把一个具体含氟基团转化为可制备、可表征、可比较反应性的化学对象，为研究全氟烷基的特殊行为提供了材料基础。</p><p class="a03-biography-locator">传记42–44页；1966年原刊18–19页及实验部分 · <a href="#a03-biography-ref-HERITAGE-S01">HERITAGE-S01</a> · <a href="#a03-biography-ref-PF01">PF01</a></p></article>\n<article class="a03-biography-card" id="a03-biography-contribution-2"><h3>研究亲核试剂作用下的特殊反应行为</h3><p>蒋锡夔所关注的位阻和电子效应问题，与陈庆云等人的实验工作相结合。原论文研究全氟叔丁基碘与二乙胺、乙醇—氢氧化钾体系的反应，通过产物与转化关系讨论亲核试剂进攻卤素的解释，而不是简单套用通常的碳中心SN2取代。传记将这项工作联系到后来所称的亲卤反应，体现了从异常反应现象提出基础问题的研究特点。</p><p class="a03-biography-meaning"><b>学术意义：</b>这项工作的开拓性在于探索含氟结构如何改变反应方式。原作者提出的路径、备选解释和后来回顾的评价各有证据层次；不把中间体画式当作直接观测，也不由平台裁定国际优先权。</p><p class="a03-biography-locator">传记43–45页；1966年原刊19–20页、式(3)/(3′)及相关脚注 · <a href="#a03-biography-ref-HERITAGE-S01">HERITAGE-S01</a> · <a href="#a03-biography-ref-PF01">PF01</a></p></article>\n<article class="a03-biography-card" id="a03-biography-contribution-3"><h3>用光谱比较讨论全氟烷基的诱导效应</h3><p>1966年论文比较不同全氟烷基碘代物的紫外吸收及溶剂位移，并结合其他观察讨论诱导效应。传记强调了这一研究对通常经验顺序提出的问题：含氟基团的效应需要联系具体结构和证据判断，不能只按碳原子数或一般烷基经验推断。</p><p class="a03-biography-meaning"><b>学术意义：</b>研究把化合物制备、反应和光谱组织成相互联系的论证。表1直接比较的是三种完整碘代物；原作者更广的基团效应解释，不等于平台已经证明了一个适用于所有体系的基团常数排序。</p><p class="a03-biography-locator">传记45页；1966年原刊20–21页，表1位于印刷21页 · <a href="#a03-biography-ref-HERITAGE-S01">HERITAGE-S01</a> · <a href="#a03-biography-ref-PF01">PF01</a></p></article>\n<h3>共同研究：科学问题、实验与培养</h3><p>1966年原论文署名为陈庆云、蒋锡夔、陈秉启、梁梦兰。传记介绍具体实验参与者和科学讨论的不同角色；以下按这些记述说明合作，不从署名顺序推算个人贡献比例。</p><div class="a03-biography-table" role="region" tabindex="0" aria-label="A03合作分工"><table><caption>传记与原论文所记合作</caption><thead><tr><th scope="col">人物</th><th scope="col">具体工作</th><th scope="col">出处</th></tr></thead><tbody>\n<tr><th scope="row">陈庆云</th><td>参与全氟叔丁基卤化物的制备、结构和反应研究，将材料工作中获得的化学对象推进为基础研究课题。</td><td>传记42–45页；原论文署名</td></tr>\n<tr><th scope="row">蒋锡夔</th><td>围绕含氟卤代物的位阻、电子效应和反应方式提出问题，参与科学讨论并共同署名。</td><td>传记43–45页；原论文署名</td></tr>\n<tr><th scope="row">陈秉启</th><td>与陈庆云共同开展全氟叔丁基碘等化合物的制备及后续实验研究。</td><td>传记44页；原论文署名</td></tr>\n<tr><th scope="row">梁梦兰</th><td>传记列为参与该小课题的实习生；1966年论文共同作者。</td><td>传记44页；原论文18页</td></tr>\n</tbody></table></div><h3>平台的AI辅助整理</h3><p>以上是原作者的历史成果。平台新增工作是资料关联、原文释读及已完成的原表数值重放：六项溶剂位移换算用于检查原表数字与单位，不是光谱实验复现，也不验证反应机理。详细数字、适用范围与未来设想放在下一层AI研究资料页；资料追索清单保存在本地。新增整理保持review_required、release_eligible=false，M0继续暂停。</p><p><a href="../research/index.html#ai-a03">A03 全氟叔丁基化学：AI整理与原表数值重放 →</a></p><details><summary>本段参考资料</summary><ul>\n<li id="a03-biography-ref-HERITAGE-S01"><b>HERITAGE-S01</b> · 朱晶、刘超：《氟缘笃志：陈庆云传》；参考底本42–45页：全氟叔丁基化学的研究缘起、实验、讨论与合作</li>\n<li id="a03-biography-ref-PF01"><b>PF01</b> · <a href="https://sioc-journal.cn/Jwk_hxxb/CN/Y1966/V32/I1/18">陈庆云、蒋锡夔、陈秉启、梁梦兰：全氟和多氟型有机化合物的化学特性——全氟叔丁基碘以及全氟烷基的诱导效应顺序</a>；《化学学报》1966，32(1)：18–25；本文新增引用集中于18–21页，表1见21页</li>\n<li id="a03-biography-ref-HERITAGE-S04"><b>HERITAGE-S04</b> · <a href="https://www.cas.cn/zt/kjzt/kjzlzqzl/kjzlzq/202406/t20240621_5022275.shtml">中国科学院：“上海氟”，何以为？</a>；2024-06-21，陈庆云与陈秉启研究全氟叔丁基碘的回顾段；作为机构历史报道</li>\n</ul></details></div></section>\n<!-- A03_BIOGRAPHY_HISTORY:END -->\n\n', 'questions_old': '<section id="questions">\n  <div class="wrap">\n    <div class="sec-head">\n      <h2>研究问题与AI辅助整理</h2>\n      <p>本专题的 AI 价值是可追溯的资料工作：从原始论证识别命题，逐处对齐后续引文，形成范围明确、可继续查新的问题。页面不接入在线生成服务，没有计算按钮，也没有模拟进度条。</p>\n    </div>\n\n    <div class="ai-grid">\n      <div class="ai-item">\n        <h3>重建原始论证</h3>\n        <p>AI协助拆分观察、解释、假设与限制；人工逐项核对化学式、脚注及页码。产出带来源定位的论证卡。</p>\n        <span class="ai-status">资料与方法工作</span>\n      </div>\n      <div class="ai-item">\n        <h3>对齐被引命题</h3>\n        <p>AI协助识别后续引文的对象、语气和范围变化，保留原作者归属。产出原始命题与后续引文的对照。</p>\n        <span class="ai-status">引证语义整理</span>\n      </div>\n      <div class="ai-item">\n        <h3>形成精确查新问题</h3>\n        <p>先查同一对象、同一命题及接近条件的先行研究，确认缺口后再决定科学计算。</p>\n        <span class="ai-status">待查新 · 不宣称空白</span>\n      </div>\n    </div>\n\n    <details class="q-item" open="">\n      <summary>问题一：原文备选机理是否已有同体系辨析<span class="q-badge b-new">状态：待查新</span></summary>\n      <div class="q-body">\n        <dl>\n          <dt>问题</dt><dd>是否已有针对同一底物、反应对象和接近条件的后续研究，能区分原文保留的路径？</dd>\n          <dt>原文出发点</dt><dd><a href="../index.html#source-pf01">PF01</a>第19–20页式(3)、式(3′)及页脚一步过程讨论。</dd>\n          <dt>下一步证据</dt><dd>先核对最接近的原始文献及反应条件；没有完成前不设定新计算课题。</dd>\n          <dt>不可宣称</dt><dd class="not-claim">不能表述为尚无人研究或本平台首次提出。</dd>\n        </dl>\n      </div>\n    </details>\n\n    <details class="q-item">\n      <summary>问题二：现代回引采用了性质还是完整排序<span class="q-badge b-check">状态：待核查</span></summary>\n      <div class="q-body">\n        <dl>\n          <dt>问题</dt><dd>后续作者使用的是 PFtB 与 CF<sub>3</sub> 的定性比较，还是对原始完整排序进行了独立检验？</dd>\n          <dt>原文出发点</dt><dd><a href="../index.html#source-pf01">PF01</a>第20–21页与PF07第27318页正文[5]。</dd>\n          <dt>下一步证据</dt><dd>逐篇对齐被引句、测量对象、条件和数据；区分回引与新验证。</dd>\n          <dt>当前材料不能证明</dt><dd class="not-claim">当前材料不能证明完整排序已被现代研究全面验证。</dd>\n        </dl>\n      </div>\n    </details>\n\n    <details class="q-item">\n      <summary>问题三：英文刊载与早期传播链怎样对应<span class="q-badge b-fetch">状态：待取原文</span></summary>\n      <div class="q-body">\n        <dl>\n          <dt>问题</dt><dd>取得 Scientia Sinica 原文后，怎样核对两刊的内容对应、页码和后续引用入口？</dd>\n          <dt>出发点</dt><dd><a href="../index.html#source-pf01">PF01</a>、PF28及PF29。</dd>\n          <dt>下一步证据</dt><dd>核对英文全文与1967年题录；不重复计成果或引用。</dd>\n          <dt>性质说明</dt><dd class="not-claim">这是文献核对问题，不是新的化学发现。</dd>\n        </dl>\n      </div>\n    </details>\n\n    <p class="tl-footnote">迭代规则：新资料先核对化学对象与作者，再核对命题、条件和引用用途；对最接近先行工作登记检索库、检索式、日期、全文可得性与正反证据；只有专业复核确认具体缺口，才提出科学计算任务。尚无本平台新量子化学计算或获确认的新化学发现；公开检索未检出不能写成前所未有；没有同条件检验，不能把现代其他底物或反应体系的机制直接套回1966年。</p>\n  </div>\n</section>', 'questions_new': '<section id="questions"><div class="wrap"><div class="sec-head"><h2>AI辅助资料整理与原表数值重放</h2><p>历史成果与平台新增工作分别呈现</p></div><p>本页介绍原作者的化合物、反应研究和原始论证。平台已完成的六项溶剂位移换算，以及假定扰动下的敏感性诊断，集中放在下一层AI研究资料页。它们属于原表数值重放，不能替代独立光谱实验，也不构成机理验证。</p><p>未来研究须从明确的科学问题出发，与已有研究比较后另定协议；目前未启动新计算或实验。新增整理保持<code>review_required</code>、<code>release_eligible=false</code>，M0继续暂停。</p><p><a href="../research/index.html#ai-a03">A03 全氟叔丁基化学：已完成工作、适用范围与未来设想 →</a></p></div></section>', 'followup_old': '<section id="team-follow-up-1980"><div class="wrap"><div class="sec-head"><h2>团队后续研究：1980 年偏氟乙烯调聚</h2><p>同一碘化物，不同的反应问题</p></div><p>1980 年，陈庆云、马振中、蒋锡夔、张元发、贾世茂将全氟叔丁基碘用于偏氟乙烯的自由基调聚，并考察四氯化碳体系，比较产物结构和加成位置。馆藏书目与摘要可查；公开馆藏转录中的结构式仍须回刊本核对。〔<a href="../index.html#source-cq-h13">CQ-H13</a>〕</p><p>这是同一化合物上的团队后续原始研究。1966 年所讨论的亲卤解释与 1980 年自由基调聚各有对象和条件；该记录<strong>不增加独立引文计数</strong>，也不提供对 1966 年机理或其光谱数据的独立复核。〔<a href="../index.html#source-pf01">PF01</a>、<a href="../index.html#source-cq-h13">CQ-H13</a>〕</p><p><a href="../topics/fluoromonomers/index.html#record-fluorinated-oils">返回氟材料与调聚档案</a></p></div></section>', 'followup_new': '<section id="team-follow-up-1980"><div class="wrap"><div class="sec-head"><h2>团队后续研究：1980 年偏氟乙烯调聚</h2><p>同一碘化物，不同的反应问题</p></div><p>1980 年，陈庆云、马振中、蒋锡夔、张元发、贾世茂将全氟叔丁基碘用于偏氟乙烯的自由基调聚，并考察四氯化碳体系，比较产物结构和加成位置。论文全文已取得并整理；具体原刊观察见A02专题的后续调聚研究。〔<a href="../index.html#source-cq-h13">CQ-H13</a>〕</p><p>这是同一化合物上的团队后续原始研究。1966 年所讨论的亲卤解释与 1980 年自由基调聚各有对象和条件；该记录<strong>不增加独立引文计数</strong>，也不提供对 1966 年机理或其光谱数据的独立复核。〔<a href="../index.html#source-pf01">PF01</a>、<a href="../index.html#source-cq-h13">CQ-H13</a>〕</p><p><a href="../topics/fluoromonomers/index.html#a02-vdf-1980">A02 含氟单体、氟橡胶与氟油：后续调聚研究</a></p></div></section>', 'followup_replacements': [('馆藏书目与摘要可查；公开馆藏转录中的结构式仍须回刊本核对。', '论文全文已取得并整理；具体原刊观察见A02专题的后续调聚研究。'), ('../topics/fluoromonomers/index.html#record-fluorinated-oils', '../topics/fluoromonomers/index.html#a02-vdf-1980'), ('返回氟材料与调聚档案', 'A02 含氟单体、氟橡胶与氟油：后续调聚研究')], 'question_index_block': "  DATA.questions.forEach(function(q){\n    index.push({kind:'研究问题', title:q.id+' '+q.title, text:[q.question,q.origin,q.status,q.next_evidence,q.not_claim].join(' '), act:function(){\n      var all = $all('.q-item'); var idx = DATA.questions.indexOf(q);\n      if(all[idx]){ all[idx].open=true; all[idx].scrollIntoView({behavior:'smooth',block:'center'}); }\n    }});\n  });\n"}
ORIGINAL_PFTB_SHA256 = '42ca404f2ed70b7a3b0b5d8b0eb742a2509e5a5a70fd0be36a65028e61cbd1f6'
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
        raise ValueError('Unsafe or missing A03 biography-presentation file: '+str(name))
    return path


def _json(root: Path, name: str):
    return json.loads(_file(root, name).read_bytes())


def predecessor_bytes(root: Path, name: str) -> bytes:
    """Recover exact fixed 3c85d86 bytes before replaying the immutable chain."""
    current = _file(root, name).read_bytes()
    if not (root/MANIFEST).exists():
        return current
    data = _json(root, MANIFEST)
    if not isinstance(data, dict):
        raise ValueError('A03 biography presentation requires a JSON object')
    records, pool = data.get('reversible_text_files'), data.get('reverse_text_patch_pool')
    if not isinstance(records, list) or not isinstance(pool, list):
        raise ValueError('A03 biography presentation requires exact reverse text patches')
    matches = [row for row in records if isinstance(row, dict) and row.get('path') == name]
    if not matches:
        if name in PREDECESSOR_FILES:
            raise ValueError('Missing fixed A03 biography predecessor: '+name)
        return current
    if len(matches) != 1 or name not in PREDECESSOR_FILES:
        raise ValueError('Unauthorized or duplicate A03 biography predecessor: '+name)
    row = matches[0]
    old_sha, old_size = PREDECESSOR_FILES[name]
    if (row.get('old_sha256') != old_sha or row.get('old_bytes') != old_size
            or _sha(current) != row.get('new_sha256') or len(current) != row.get('new_bytes')):
        raise ValueError('A03 biography file differs from complete old/new identities: '+name)
    edits = row.get('edits')
    if not isinstance(edits, list) or not edits:
        raise ValueError('A03 biography changes require nonempty text edits: '+name)
    chunks, cursor, old_end, delta = [], 0, 0, 0
    for edit in edits:
        if not isinstance(edit, dict) or set(edit) != {'old_offset', 'replacement'}:
            raise ValueError('Invalid A03 biography reverse text edit: '+name)
        offset, replacement = edit['old_offset'], edit['replacement']
        if (type(offset) is not int or offset < old_end or type(replacement) is not int
                or not 0 <= replacement < len(pool)):
            raise ValueError('Overlapping or invalid A03 biography reverse edit: '+name)
        pair = pool[replacement]
        if (not isinstance(pair, dict) or set(pair) != {'old', 'new'}
                or not all(isinstance(pair.get(k), str) for k in ('old', 'new'))
                or pair['old'] == pair['new']):
            raise ValueError('Invalid A03 biography replacement pool')
        before, after = pair['old'].encode('utf-8'), pair['new'].encode('utf-8')
        position = offset+delta
        if position < cursor or current[position:position+len(after)] != after:
            raise ValueError('A03 biography reverse replacement differs at exact offset: '+name)
        chunks.extend((current[cursor:position], before))
        cursor, old_end = position+len(after), offset+len(before)
        delta += len(after)-len(before)
    rebuilt = b''.join((*chunks, current[cursor:]))
    if _sha(rebuilt) != old_sha or len(rebuilt) != old_size:
        raise ValueError('A03 biography predecessor cannot be reconstructed exactly: '+name)
    return rebuilt


def _set_pointer(data, pointer: str, value):
    parts = [p.replace('~1', '/').replace('~0', '~') for p in pointer.split('/')[1:]]
    if not pointer.startswith('/') or not parts:
        raise ValueError('Invalid fixed A03 biography JSON pointer')
    parent = data
    for part in parts[:-1]:
        parent = parent[int(part)] if isinstance(parent, list) else parent[part]
    key = int(parts[-1]) if isinstance(parent, list) else parts[-1]
    parent[key] = copy.deepcopy(value)


def _binding(root: Path, name: str) -> dict:
    data = _file(root, name).read_bytes()
    return {'path': name, 'sha256': _sha(data), 'bytes': len(data)}


def _assert_pftb_projection(source: str, current: str) -> None:
    if _sha(source.encode('utf-8')) != ORIGINAL_PFTB_SHA256 or len(source.encode('utf-8')) != 97587:
        raise ValueError('Unexpected original PFtB scientific page')
    spec = PFTB_SPEC
    projected = source[:spec['insertion_offset']]+spec['insertion_text']+source[spec['insertion_offset']:]
    for old, new in [(spec['questions_old'], spec['questions_new']),
                     (spec['followup_old'], spec['followup_new']),
                     (spec['question_index_block'], '')]:
        if projected.count(old) != 1:
            raise ValueError('PFtB approved transformation is not unique')
        projected = projected.replace(old, new, 1)
    if projected != current:
        raise ValueError('PFtB differs outside the four approved transformations')
    if '<script' in spec['insertion_text'].lower():
        raise ValueError('The biography insertion cannot add executable scripts')


def apply(root: Path, entries: dict, previous_report: dict) -> tuple[dict, dict]:
    """Validate the current A03-only presentation after exact v26 replay."""
    if not (root/MANIFEST).exists():
        return entries, previous_report
    if not (root/PREVIOUS_MANIFEST).is_file():
        raise ValueError('A03 biography presentation requires its immutable v26 predecessor')
    for name, sha in OLD_MANIFESTS.items():
        if _sha(_file(root, name).read_bytes()) != sha:
            raise ValueError('Historical presentation manifest changed: '+name)
    for name, (sha, size) in PROTECTED_FILES.items():
        value = _file(root, name).read_bytes()
        if _sha(value) != sha or len(value) != size:
            raise ValueError('A01 original source or protected reference changed: '+name)
    data = _json(root, MANIFEST)
    required = {
        'schema_version': '27.0', 'presentation_id': PRESENTATION_ID,
        'publication_kind': 'platform_a03_biography_narrative',
        'previous_presentation_commit': PREVIOUS_COMMIT,
        'previous_presentation': {'path': PREVIOUS_MANIFEST, 'sha256': OLD_MANIFESTS[PREVIOUS_MANIFEST]},
        'original_baseline_sha256': BASELINE_SHA256, 'original_archive_sha256': ARCHIVE_SHA256,
        'allowed_html_paths': list(ROUTES), 'added_html_paths': [], 'additions': [],
        'allowed_PFtB_transformations': ['hero_after_history_insertion', 'questions_scope_section', 'followup_acquisition_status_and_link', 'remove_questions_search_index'],
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
        raise ValueError('Unsupported bounded A03 biography presentation v27')
    records, pool = data.get('reversible_text_files'), data.get('reverse_text_patch_pool')
    if (not isinstance(records, list) or not isinstance(pool, list) or not pool
            or any(not isinstance(row, dict) for row in records)
            or len(records) != len(PREDECESSOR_FILES)
            or {row.get('path') for row in records} != set(PREDECESSOR_FILES)
            or len({row.get('path') for row in records}) != len(records)
            or any(not isinstance(row.get('edits'), list) or not row['edits'] or any(
                not isinstance(edit, dict) or type(edit.get('replacement')) is not int
                for edit in row['edits']) for row in records)):
        raise ValueError('A03 biography presentation has an unauthorized predecessor file set')
    if {edit['replacement'] for row in records for edit in row['edits']} != set(range(len(pool))):
        raise ValueError('A03 biography presentation requires exactly its used replacement pool')
    for name, (sha, size) in PREDECESSOR_FILES.items():
        old = predecessor_bytes(root, name)
        if _sha(old) != sha or len(old) != size or old == _file(root, name).read_bytes():
            raise ValueError('A03 biography predecessor differs from fixed 3c85d86: '+name)
    expected = json.loads(predecessor_bytes(root, AI))
    for update in EXPECTED_AI_UPDATES:
        _set_pointer(expected, update['pointer'], update['value'])
    if _json(root, AI) != expected:
        raise ValueError('A03 biography JSON changed outside its fixed A03 fields')
    for name, sha in REVIEWED_PUBLIC_FILES.items():
        if _sha(_file(root, name).read_bytes()) != sha:
            raise ValueError('A03 biography source, renderer or document differs from reviewed bytes: '+name)
    for name in PUBLIC_DISPLAYS:
        value = _file(root, name).read_text('utf-8')
        if re.search(r'(?i)private-sources|current-item-register|现阶段待查事项统计|[CD]:[\\/]', value):
            raise ValueError('A03 biography display contains private evidence or a local path: '+name)
    changes = data.get('changes')
    if (not isinstance(changes, list) or len(changes) != len(ROUTES)
            or any(not isinstance(row, dict) for row in changes)
            or {row.get('path') for row in changes} != set(ROUTES)):
        raise ValueError('A03 biography presentation may change only its two existing routes')
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
            raise ValueError('A03 biography route differs from complete old/new identities: '+route)
        source, current = before.decode('utf-8'), after.decode('utf-8')
        if json_scripts.findall(source) != json_scripts.findall(current):
            raise ValueError('A03 biography presentation changed original embedded JSON: '+route)
        old_ids = re.findall(r'\bid="([^\"]+)"', source)
        new_ids = re.findall(r'\bid="([^\"]+)"', current)
        if not set(old_ids).issubset(new_ids) or len(new_ids) != len(set(new_ids)):
            raise ValueError('A03 biography presentation lost or duplicated source/navigation IDs: '+route)
        if route == 'pftb/index.html':
            _assert_pftb_projection(source, current)
        else:
            pattern = r'<section\b[^>]*\bid="ai-a03"[^>]*>.*?</section>'
            if (len(re.findall(pattern, source, re.S)) != 1 or len(re.findall(pattern, current, re.S)) != 1
                    or re.sub(pattern, '<A03/>', source, flags=re.S) != re.sub(pattern, '<A03/>', current, flags=re.S)):
                raise ValueError('A03 biography changed outside its AI A03 section')
        updated[route] = {**old_entry, 'sha256': _sha(after), 'bytes': len(after), 'presentation_id': PRESENTATION_ID}
    for name, expected_entry in updated.items():
        value = _file(root, 'site/'+name).read_bytes()
        if _sha(value) != expected_entry['sha256'] or len(value) != expected_entry['bytes']:
            raise ValueError('A03 biography changed an unlisted website byte: '+name)
    from render_ai_research import inspect_ai_research
    from render_a03_biography import inspect_biography
    checks = [inspect_ai_research(root), inspect_biography(root)]
    if any(c.get('status') != 'passed' for c in checks):
        raise ValueError('A03 biography display differs from source rendering: '+str(checks))
    report = {'path': MANIFEST, 'sha256': _sha(_file(root, MANIFEST).read_bytes()),
        'presentation_id': PRESENTATION_ID, 'publication_kind': required['publication_kind'],
        'changed_paths': list(ROUTES), 'added_paths': [],
        'previous_presentation_commit': PREVIOUS_COMMIT,
        'exact_predecessor_reconstruction': True, 'source_derived_rendering': True,
        'all_v1_v26_manifest_bytes_preserved': True, 'private_originals_not_published': True,
        'original_PFtB_science_and_embedded_JSON_preserved': True,
        'homepage_achievement_summary_other_lines_and_scientific_data_preserved': True,
        **{k: required[k] for k in ('scientific_review_status', 'release_eligible',
            'scientific_data_unchanged', 'M0_resumed', 'historical_achievement_independent_of_AI_review')}}
    return updated, {**report, 'presentation_chain': [*previous_report['presentation_chain'], report]}
