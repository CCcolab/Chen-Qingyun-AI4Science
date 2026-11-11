# 严格输入与科研签认门禁：本轮交付

日期：2026-11-11。评审基准 `b5d562c8757bf6282ca657ecf29fc18877b456a7`；实现提交 `c7aed91e9d553a45fb1a13752d0fa61cd68a8106`；正式 WSL 2 验收源码提交 `16f06b67354e7f30ddcaaff090fcbe8eeb1610fd`。独立分支 `research/input-review-gates-20261111`。后续证据／说明提交不改变这两次实际运行所验代码的字节。

## 已完成的工程修正

- F01：所有数值入口校验固定作者、来源、年份、页表、完整协议、十项观测及六对编号映射、单位和原字节指纹；重复 JSON 键、非有限数、不合格字段和输入在候选生成前失败。CLI 另存失败审计，退出 2。固定任务合同不开放任意输入。
- F02：独立运行清单绑定三份原输入、完整包代码、验收程序、真实环境、完整结果、候选及待展示载荷。具名签认模板另绑策略与全部指纹；旧绑定、无签名、未登记身份或非批准决定不能晋级。默认审定导出关闭。
- F03：新完整结果／候选 schema 2.0；同次 manifest 强绑定完整结果、候选和 run ID；展示载荷保留来源、观测、计算、四组顺序敏感性、六项舍入区间及边界。新增独立待审 HTML，审定接口和 YouMind 交付合同就绪。
- F04：包括直接 `write_outputs()` 在内的导出均拒绝覆盖既有结果。本次运行与待审请求实际纳入持久版本档案，不仅存于会过期的 Actions 附件。多任务调度仍未实现。
- F05：原数据、协议、文献、研究队列、SHA 清单、历史结果和网站基线保持原字节；旧 v1 引擎另封存。当前状态集中登记，历史测试数不混作本轮 CI 数量。

## 真实运行与计数

| 检查 | 实际结果 | 证据 |
|---|---|---|
| 本机 WSL 2 完整套件 | 81 项，全部通过，无跳过；测试源码仅留本机 | `validation/20261111-review-gates-local-tests/` |
| Windows 本地套件 | 81 项通过，其中 3 项因符号链接权限跳过；UTF-8 模式 | 本轮本机执行；不作为 WSL 或 GitHub CI 计数 |
| 原 ZIP 完整性及测试 | 原 19 项成员指纹和 9 项测试通过 | WSL r2 原包日志 |
| 封存 v1 数值重放 | 两份结果逐字节及逐字段一致 | r2 `original-result-comparison.json` 与 `integration/legacy-result-comparison.json` |
| 新 v2 结果 | 数学／科学投影与原结果一致；完整运行绑定通过；不声称与旧 schema 全文一致 | r2 `integration/current-numerical-comparison.json`、`current-run-integrity.json` |
| 公开分发验收 | 保留 18 项原清单成员；单测数 0，明确未运行 | r2 `integration/summary.json`；GitHub CI 使用同一分发模式 |
| 网站检查与构建 | 原 ZIP 21 成员加空 `.nojekyll` 共 22 源成员，51 来源，6 段 JS 检查通过；产物 18 文件 | r2 `site-check.json` 和构建日志 |
| 运行／待审门禁 | 验清单、待审页面、请求和空审定目录生成通过；未签认导出退出 2，未创建输出目录 | r2 `gate-checks.json` |

正式环境为 Ubuntu 24.04.4 LTS／WSL 2，内核 `5.15.167.4-microsoft-standard-WSL2`、Python 3.12.3、Linux Node 24.13.1。在 Linux 临时文件系统克隆干净固定提交运行，未修改系统 Node。首次尝试因最终接口文档尚未提交而主动停止；失败日志留在 `validation/20261111-wsl2-review-gates/`，成功重验另用 `-r2`，没有覆盖失败。

## 具体待审记录

完整持久证据：[WSL r2 摘要](../validation/20261111-wsl2-review-gates-r2/summary.json)。运行 ID 为 `ca336d0c-dd92-4b8d-b920-e837c76a3498`，清单 SHA-256 为 `898a94bbdcc78d985d2589ceb3cf75e1a2f9135350ebda0e92361ee7ed069c87`。

- [完整运行清单](../validation/20261111-wsl2-review-gates-r2/integration/current-run/run-manifest.json)
- [独立待审页面](../validation/20261111-wsl2-review-gates-r2/review-packet/PF1966-UV-T1.html)
- [绑定此运行的待审请求](../validation/20261111-wsl2-review-gates-r2/review-packet/review-request.json)
- [空审定数据目录](../validation/20261111-wsl2-review-gates-r2/reviewed-results.json)

这些候选及证据会在公开研究分支可读，尚未进入正式 Pages。浏览器策略阻止本地 `file:` 页面，本轮未完成视觉浏览；HTML 内容和数据关系已由程序核验，不能称为新版网页线上验收。

## 仍需完成

原 PDF／扫描的专业转录核校、真实审阅者身份及公钥登记、具名签认和首次实际审定导出均待补。正向签名底层已用临时测试密钥验证，但没有将测试密钥或测试签名用作科研批准。当前 `review_required`、审定记录 0。

YouMind 后续消费审定接口并交付新 ZIP，再评审新网站基线和新增研究页、部署并验收。当前生产网站部署提交仍为 `8259c6a25d0c55ab6350490ac9011592386a3cb4`，不是本轮研究代码提交。原有 `f0c54cb…` WSL 记录仍保留，其历史计数不替代本轮记录。

多任务调度、资源／并发／取消管理和下一项科研协议尚未开发；后续各成果线先补原文、查新与协议。全部当前计算只属于“原表数值重放”，没有量化计算、实验验证或机理验证；未来假设仍为未检验，原作者归属不变。
