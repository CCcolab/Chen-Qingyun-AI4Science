# 网站结果接口与 YouMind 交付合同

日期：2026-11-11。适用任务：`PF1966-UV-T1`。本合同对应当前 `input_contract.py`、`uv_replay.py`、`run_record.py` 和 `review_gate.py`，区分历史候选、新运行候选、待审展示载荷和独立审定导出。后续实现变更须同步评审合同，不能把旧结果直接重标为新版本或通过状态。

## 当前接入状态

公开仓库为 [CCcolab/Chen-Qingyun-AI4Science](https://github.com/CCcolab/Chen-Qingyun-AI4Science)，默认分支为 `main`，正式网站为 [GitHub Pages](https://cccolab.github.io/Chen-Qingyun-AI4Science/)。源码、部署、WSL 验收和研究运行各自对应的版本另见 [当前研究状态](CURRENT_RESEARCH_STATUS_zh-CN.md)，不得混用提交或历史测试数。

现有 YouMind 页面与 Pages 尚未消费本合同的新研究数据。`scripts/build_site.py` 仍只发布封存的 15 个 HTML、2 个原始来源 JSON 和空 `.nojekyll`，不将研究候选、日志或新研究页面加入现有网站。候选已经在公开源码仓库可读；“未进入 Pages 展示”不等于“未公开”。

`reviews/review-policy.json` 当前为 `release_enabled: false`、`authorized_reviewers: []`。当前科学审定记录数为 **0**；空目录导出保持 `publication_status: review_required` 和 `records: []`。工程验收、CI 成功、审阅模板和本地预览均不能作为科学签认。

## 四类数据及版本

| 层次 | 文件或产物 | 版本与状态 | 消费规则 |
|---|---|---|---|
| 历史封存结果 | `results/pftb1966-uv-replay.json`、`results/website-candidate.json` | 历史候选 v1 的约定称呼；文件本身没有独立 `schema_version`，保持旧字节与 `review_required` | 仅作为可重跑历史基线；须联读其协议、CSV 和来源登记，不能单独当作完整发布接口 |
| 新完整结果与候选 | 每次独立运行目录的同名两份 JSON | `schema_version: "2.0"`，`input_contract_version: "PF1966-UV-T1.fixed.v2"`；完整结果的 `scientific_review_status`、候选的 `publication_status` 均为 `review_required` | 新候选补足来源与敏感性，但本身不含 run ID、完整结果指纹或科学签名，仍须关联该次清单 |
| 待审展示载荷 | 同次 `publication-payload.json` | `schema_version: "1.0"`，`record_id: "PF1966-UV-T1:<run_id>"`，`publication_status: review_required` | 是本次拟展示内容；其原字节指纹由运行清单及科学审阅绑定，不能仅改状态后发布 |
| 审定目录 | `reviewed-results.json` | 目录 `schema_version: "1.0"`；成功导出时目录和其中记录的 `publication_status` 为 `scientifically_reviewed` | 只能由真实签名通过门禁后另行生成，保留原候选历史；当前没有该类已审定记录 |

`schema_version` 属于各自文件合同：候选的 `2.0` 不能套到载荷或审定目录的 `1.0`。未知版本、缺失必需字段、重复 JSON 键、非有限数字和不符的身份或指纹均应停止导入，不能按“最接近”的旧格式猜测。标准库严格解析与固定任务校验由仓库实现；前端不负责补全、改写或批准输入。

## 新候选与展示载荷字段

新候选保留 `task_id`、`result_type`、`source_ids`、`numeric_summary`、`boundaries`、`data_sha256` 和 `code_sha256`，并提供 `original_authors`、`publication_year`、`source_url`、`location`、`source_pdf_sha256`、`protocol_sha256`、`source_registry_sha256`、`validator_code_sha256`、`observation_ids`、`measurement_id_pairs`、`comparisons`、`experimental_uncertainty_nm`、`display_rounding_assumption` 和 `transcription_review`。

拟展示内容以 `publication-payload.json` 为审阅对象，必须完整保留下列信息：

| 字段 | 固定任务约定与显示要求 |
|---|---|
| `task_id`、`result_type` | `PF1966-UV-T1`、`published_table_numerical_replay`；名称显示为“原表数值重放” |
| `record_id`、`run_id`、`publication_status` | 标识具体运行与展示记录；待审状态清楚可见，不从数值状态推断科学状态 |
| `source` | 完整 PF01 来源登记，包括 `authors`、`title`、`year`、`venue`、`url`、`inspected_location`、`transcribed_field`、`cached_pdf_sha256`、`material_included`、`boundary` 及协议的 `location`；不能只留短引文 |
| `provenance` | `data_sha256`、`protocol_sha256`、`source_registry_sha256`、`code_sha256`、`validator_code_sha256`、`source_pdf_sha256`；清楚标注“原文指纹登记”与“本次重新验得原文”的区别 |
| `observations` | CSV 全部 10 条原表观测，保留稳定编号、对象、分子式、溶剂、波长、来源编号和 PDF／印刷页／表定位 |
| `measurement_id_pairs` | 下表 6 个数值行与原观测编号的显式映射；不按数组位置重新编号 |
| `numeric_summary` | 6 行波长、两种位移尺度及每行的 `display_rounding_intervals`；行键为 `(compound_id, donor_solvent)` |
| `comparisons` | 两种给体 × 两种指标，共 4 组名义顺序和相邻敏感性比较；包含名义差、舍入假设下是否分离及首次区间接触的共同波长半宽 |
| `experimental_uncertainty_nm`、`display_rounding_assumption` | 前者必须为 `null`；后者为人为指定的 ±0.05 nm 独立有界扰动解释，始终与区间一起展示 |
| `excluded_from_comparison` | UV08 的 tC4F9I／CCl4 观测保留，但不属于这 6 行 C6H14—给体配对 |
| `claim_scope`、`boundaries`、`scientific_review` | 科学论断范围、全部边界与该记录的审阅状态；不得仅抽取数字后丢弃这些字段 |

原作者依次为陈庆云、蒋锡夔、陈秉启、梁梦兰；出版年 1966，来源为《化学学报》32(1)，18–25，定位为印刷 p.21 表 1、PDF 第 4 页。网站上线日期不是论文出版年。平台数值整理另列工作身份，已发表成果保留原作者归属。

## 观测映射、数学单位与敏感性

| 数值行键 | 基准观测编号 | 给体观测编号 |
|---|---|---|
| nC3F7I／EtOH | UV01 | UV02 |
| nC3F7I／Et2O | UV01 | UV03 |
| iC3F7I／EtOH | UV04 | UV05 |
| iC3F7I／Et2O | UV04 | UV06 |
| tC4F9I／EtOH | UV07 | UV09 |
| tC4F9I／Et2O | UV07 | UV10 |

`observations` 保留 UV01–UV10；UV08 为 tC4F9I／CCl4。固定数值比较使用其中 9 条观测形成 6 行配对。nC3F7I 与 iC3F7I 虽同为 C3F7I，也不能合并；tC4F9I 为 C4F9I。没有 CF3I 或 C2F5I 的实测行，不能把 n-C3F7I 替换为 C2F5I。

H 为原表 `C6H14` 基准，保持该记号，不擅自指定其异构体；B 为 `EtOH` 或 `Et2O` 给体溶剂，不是苯。原单位“毫微米”在本表数值上等于 nm，不得把相邻 ε 列当作波长。

- `delta_lambda_nm = lambda_h_nm - lambda_b_nm`，单位 nm。
- `blue_shift_cm_inverse = 10^7 × (1/lambda_b_nm - 1/lambda_h_nm)`，单位 cm⁻¹。
- 两种表达由同一批观测换算，不能称为两次独立实验，也不能混画在同一无单位坐标上。
- 每一行的 `display_rounding_intervals` 给出两种指标在各原波长独立 ±0.05 nm 扰动后的范围。6 行区间与共同解释均保留，不把区间画成实验误差棒、仪器精度或置信区间。
- `comparisons` 中 `nominal_order`、`nominal_gap`、`separated_under_display_rounding_assumption` 和 `first_overlap_common_wavelength_half_width_nm` 仅描述固定展示舍入假设下的顺序敏感性；后者单位为 nm，不是统计显著性或实验误差估计。

数值显示的小数位数不代表原始测量精度。新结果仍明确保留：新实验、原谱重拟合、量化计算为 `not_performed`；反应机理、游离阴离子检测、四基团普适顺序为 `not_tested`；新化学发现为 `not_claimed`。量化计算、实验验证和未来假设须使用各自协议与证据，不能由本次原表数值重放推导为完成。

## 运行清单与强绑定

每次新运行写入独立目录，默认位于 `scratch/runs/<UTC>-<uuid>/`，不覆盖 `results/` 或既有运行。`run-manifest.json` 为 `schema_version: "1.0"`、`record_type: fixed_task_run`，在成功生成全部输出后最后写出；没有成功清单的部分目录不是可供审定的成功运行。

清单以相对路径、SHA-256 和字节数绑定 `inputs/` 内 3 份原字节快照、`code/` 内全部当前 `chen_research/*.py` 与 `scripts/accept_phase1.py`、真实 `environment.json`、完整结果、新候选和展示载荷。环境记录实际 OS／内核／Python、Git 提交及 dirty 状态；API 或 CLI 身份如实区分。该运行器本身不执行单测，记录 `tests_run: 0`、`tests_status: not_run_by_runner`，不冒用其它验收记录的测试数。

`verify_run` 不仅相信清单中的哈希：它重新核对各个绑定、当前源码清单与快照、输入资格和算术，重新生成并比较完整结果、候选与展示载荷。代码新增／删除／变化、任一输入或结果变化、运行或环境记录变化都不能复用原审阅。路径不得穿越、使用绝对绑定路径、符号链接或重解析点；已有证据不覆盖。CLI 校验失败另存本地失败记录，不生成成功清单或候选。

`publication-payload.json` 不含自身指纹或完整结果指纹；这两个关联由该次清单和审阅记录的 `binding` 提供，不能假设孤立 payload 已经自证。科学审阅绑定项包括：

- `run_manifest_sha256`：清单原文件字节的 SHA-256。
- `policy_sha256`：本次信任策略原字节。
- `inputs_sha256` 与 `code_sha256`：三份输入和全部绑定源码。
- `complete_result_sha256`、`candidate_result_sha256`、`environment_sha256`、`publication_payload_sha256`：该次完整结果、候选、环境与拟展示内容。

原文 PDF 和表页扫描另以协议登记指纹及审阅 `source_evidence` 绑定，并在审定导出时要求实际文件匹配。当前运行记录明确“本次未重新核验原扫描、专业转录签认待补”；登记过指纹不等于本轮取得、逐格核读或签认通过。

## 科学签认与独立审定导出

流程与操作说明见 [科学审阅](SCIENTIFIC_REVIEW_zh-CN.md)。`scripts/review_result.py` 提供 `verify-run`、`request`、`preview`、`policy-status`、`empty-catalog`、`export-reviewed` 六类命令。`request` 或 `preview` 生成的审阅请求是 `decision: pending`、未具名、检查项为 false、`attestation.status: unsigned` 的模板，绝不是签认。

只有以下条件全部满足，`export-reviewed` 才能生成审定产物：

1. 策略经维护者核实真实审阅者身份与专业资格，登记未撤销的 Ed25519 公钥，并明确启用发布。不得为通过工程验收而虚构审阅者或自动开启策略。
2. 具体审阅记录的任务、run ID、上述全部绑定均吻合；`decision: approved`，审阅时间为明确 UTC 且对应已完成运行，具名信息与策略登记逐项一致。
3. `source_transcription`、`original_attribution`、`units_and_arithmetic`、`sensitivity_and_uncertainty`、`claim_boundaries`、`publication_text` 六项均由真实审阅者确认。审阅范围覆盖绑定展示载荷的论断和边界。
4. 实际原文 PDF 和表页扫描指纹匹配；转录结论为 `professionally_checked`。
5. 对审阅 JSON 的**原字节**存在真实 OpenSSH detached signature，使用命名空间 `chen-qingyun-scientific-review-v1`，经 `ssh-keygen -Y verify` 与注册公钥核验。只填姓名、`approved` 或 `signed` 字符串均不能通过。工具只使用公开验签密钥，不创建或保存审阅者私钥。

缺记录、退回、证据不足、策略关闭、身份未登记／已撤销、签名缺失或不符、原文材料缺失，以及输入／代码／运行／结果／拟展示内容／策略变化，都阻止审定晋级。变更后重新运行、提出审阅并形成新签认；不修改历史候选。

成功导出到全新目录，包含 `reviewed-results.json`、独立 `PF1966-UV-T1.html`、原字节 `review-record.json` 及 `review-record.json.sig`。目录的 `records` 包含载荷的审定副本；该副本保留载荷 `schema_version: "1.0"`，`scientific_review` 记录 `signature_verified`、具名审阅者、时间、审阅／签名／策略指纹及完整 binding。原运行载荷和候选继续为 `review_required`。

当前 `empty-catalog` 只生成空 `records`、`release_enabled`、`policy_sha256` 和待审原因，不能因存在目录文件就显示审定成功。公开源码中的候选也不能被页面过滤器自行升级。

审定导出不会自动复制完整运行目录、策略或原文文件，也不会部署网站。发布前须持久归档该次运行输入、源码、完整结果、环境、清单、策略、审阅记录与签名，以及可依法保存的原文核校材料，并确保与 binding 可核对；仅保存将于 30 天后过期的 Actions 附件不足以保全证据。原文、私人报告及未授权材料不因审阅需要而自动公开。

## YouMind 页面与交付门槛

当前 `preview` 仅在新的本地输出目录生成待审静态 HTML、`candidate-record.json` 和未签审阅请求，用于核对内容与版式。该页面未加入 `site/`、现有 Pages 或 YouMind 正式导出包；不得把预览称为审定结果上线。

交给 YouMind 的下一版独立研究记录建议题为“1966 年表 1：三种碘代物溶剂位移的数值重放”。页面须在可查阅的静态正文中完整呈现来源、原作者、原表 10 条观测、6 行计算与编号映射、公式及单位、6 行舍入区间、4 组顺序敏感性、运行身份、审阅证据入口、完整边界和数据下载。禁用 JavaScript 时核心科学正文仍应可读；不要用摘要卡片替代来源或把人工区间渲染为误差棒。

实际接入顺序为：仓库取得真实科学签认并导出审定目录 → YouMind 仅消费经门禁准许的审定数据 → 制作独立研究记录与导出新版网站 ZIP → 核验 ZIP 来源、成员和指纹，评审更新后的网站基线及发布清单 → Codex 集成并验收 → 按正式流程接入 Pages。仓库工具负责资格与签名验证；前端只能展示准许发布的产物，不根据名称、数字或一个状态字段作科学批准。

继续保留现有 YouMind 页面、PFtB 科学正文、`#s/...` 深链状态、A01–A09 及原始 51 条来源的稳定编号和两个来源 JSON；新记录以独立身份关联 PF01，不借新增页面静默改写原研究结论。新 ZIP 未评审前，现有封存网站基线与构建白名单保持有效。

上线验收须逐项记录项目路径、来源回链、PFtB 深链、禁用脚本的科学正文、下载内容及指纹、候选与审定数据分流、Windows／WSL 对应版本及实际部署提交。当前尚未完成新研究记录的前端消费和这轮线上验收，也没有新的科学签认。本合同固定数据与交付规则，不宣称科研发布闭环已经完成。
