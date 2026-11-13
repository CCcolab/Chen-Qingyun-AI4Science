# A01阶段进展公开合同

本合同只公开可核查的研究进展，不授予科学签认。A01进展始终保留`scientific_review_status=review_required`及`release_eligible=false`，允许如实公开本轮中心电子检查通过、未通过或执行前阻塞。PF1966-UV-T1候选接口和审定结果导出规则保持独立，不因本合同改变。

## 数据、证据和网页

- 公开数据为`research/a01/public-progress.v1.json`；其实际结果字段与本轮已保存的`public-summary.v1.json`逐字段一致。配置、末次观察值和科学资格分别登记。
- 执行时提交身份未知则保持`execution_commit=null`，使用实际worker／controller源码SHA标识；后补归档提交不得冒充执行提交。
- 先提交协议、代码、轻量结果及阶段报告为S1；后续S2公开数据及网页的证据链接使用S1完整提交SHA，避免文件循环写入自身提交号。未托管的大原始包登记为本地可用、下载URL为null。
- `scripts/render_a01_progress.py`把公开数据生成专题中的静态HTML区块，并内嵌同一JSON。没有JavaScript时仍可读。校验器按全部输入生成值逐字比对完整区块，不只比对内嵌JSON。
- 三个成果分支、原作者、原来源ID及边界分别展示。中心电子检查通过不代表完整曲率、势垒或历史机制通过；SCF精度对原互易误差的影响及根因继续未知。

## 原始网站与显式修订

原`provenance/website-baseline.json`和原YouMind导出ZIP保持字节不变。`provenance/a01-site-revision.v1.json`单独记录本次授权变更：原／新网页SHA和字节数、原因、S1来源提交、公开进展JSON的SHA，以及原基线和原ZIP身份。

本次仅允许专题`topics/early-fluoroketones/index.html`及必要的首页、成果全景页A01展示修订。其余基线成员继续按原指纹检查；PFtB、两份原JSON、51条来源身份及首页原来源登记JSON载荷保留。新的核读进展在专题和进展记录中说明，不静默重写历史源登记。

构建范围仍为原15个HTML、原2个JSON及空`.nojekyll`，共18个发布成员。不复制研究目录、日志、checkpoint或新JSON路由到Pages。公开进展数据在GitHub研究目录保存，网页以静态区块呈现。

`make_a01_site_revision.py`只创建全新修订清单，不刷新旧基线或覆盖已有修订。后续YouMind维护应以本次GitHub网页版本为源；新修订新增版本并显式更新校验合同，不用旧导出覆盖进展。

## 检查与发布

`check_a01_progress.py`验证实际源结果、状态分类、资源加总、固定证据链接和静态网页一致性，不启动DFT、模型API或分发单元测试。它不新增末次能差或密度变化门槛；这些值完整保存，平台末次orbital门槛仍为1e-9。失败／阻塞的科学阶段可以通过如实记录的一致性检查。

CI继续执行`accept_phase1.py --skip-tests`，当前分发单元测试数为0，符合`LOCAL_TESTS_POLICY_zh-CN.md`。研究路径变更触发A01一致性检查；CI不开展SCF或核梯度。

Pages保留显式`workflow_dispatch`。实际发布须在发布分支进入目标提交后触发，记录run ID及使用的完整SHA；在线核对专题实际task/run、状态、日期、科学边界及S1证据链接。HTTP 200、CI绿灯或已建立PR均不能单独证明线上内容已更新。
