# 网站候选结果接口：PF1966-UV-T1

日期：2026-11-11。本文规定本地接入准备阶段的读取合同；实际网站源码仓库、项目路径、发布分支和部署流程尚未确认。本文和测试不代表网站已经接入、部署或完成科学审阅。

## 文件与身份

`results/website-candidate.json` 是静态候选数据，不是可执行服务。它须与同次运行的 `pftb1966-uv-replay.json`、`data/sources.json`、`protocols/pftb1966_uv.json` 一起审阅。候选文件没有作者、页码、原文指纹和扰动解释，不能单独作为完整科学证据。

| 字段 | 本期约定 | 读取规则 |
|---|---|---|
| `task_id` | `PF1966-UV-T1` | 稳定任务编号；作为新增研究记录的身份，不替换原有来源记录 |
| `result_type` | `published_table_numerical_replay` | 显示为“原表数值重放” |
| `publication_status` | `review_required` | 保持待审；测试或 CI 通过不能将其升级为科学审定通过 |
| `source_ids` | `["PF01"]` | 按原编号关联来源登记，不重编原站 51 条来源 |
| `numeric_summary` | 6 行，三个完整碘代物 × 两种给体溶剂 | 以 `(compound_id, donor_solvent)` 组成行键；n、i 两种异构体不能按相同分子式合并 |
| `boundaries` | 原导出全部边界字段 | 与数字一起呈现；不允许只取数字而丢弃研究边界 |
| `data_sha256`、`code_sha256` | 小写 64 位 SHA-256 | 与同次完整结果和实际 CSV、数值模块核对；不是科学审阅签名 |

这是单一任务的合同，候选 JSON 目前没有独立 `schema_version`。接入方应检查上述固定任务身份和字段；以后扩展任务或字段前先明确版本迁移，不从未登记字段推断新功能。

## 数字、单位与敏感性

每行保留 `compound_id`、`formula`、`baseline_solvent`、`donor_solvent`、`lambda_h_nm`、`lambda_b_nm`、`delta_lambda_nm`、`blue_shift_cm_inverse` 和 `display_rounding_intervals`。

- 测量对象为 `nC3F7I`、`iC3F7I`、`tC4F9I`；对应分子式分别为 C3F7I、C3F7I、C4F9I。没有 CF3I 或 C2F5I 的实测行。
- 基准保持原表记号 C6H14，不进一步指定异构体；给体为 EtOH、Et2O。B 不是苯。
- `delta_lambda_nm = lambda_h_nm - lambda_b_nm`，单位 nm；`blue_shift_cm_inverse = 10^7 × (1/lambda_b_nm - 1/lambda_h_nm)`，单位 cm⁻¹。不得把两种尺度混作同一观测量。
- `display_rounding_intervals` 是每个原波长独立作 ±0.05 nm 有界扰动后的区间。读取完整结果的 `display_rounding_assumption` 与 `experimental_uncertainty_nm: null` 一起解释，不画成实验误差棒或置信区间。
- 名义顺序与相邻比较的敏感性在完整结果的 `comparisons`，不在网站候选文件中。需要呈现顺序稳健性时必须同时读取完整结果。

候选导出没有传递 CSV 的 `measurement_id`，现有读取器也未校验该列非空、唯一。接入方必须保留原 CSV 并建立下列观测编号映射，不能从候选行顺序重编编号。新增回归检查对本期 CSV 的编号唯一性及固定映射作核对；这不等于原读取器已经具备通用编号校验。

| 候选行键 | 基准观测编号 | 给体观测编号 |
|---|---|---|
| nC3F7I／EtOH | UV01 | UV02 |
| nC3F7I／Et2O | UV01 | UV03 |
| iC3F7I／EtOH | UV04 | UV05 |
| iC3F7I／Et2O | UV04 | UV06 |
| tC4F9I／EtOH | UV07 | UV09 |
| tC4F9I／Et2O | UV07 | UV10 |

UV08 为 tC4F9I／CCl4 原记录，保留在数据中，不进入这 6 行给体比较。上述 UV 编号与任务、来源编号分别维护。

## 来源、原作者与结果边界

用 `source_ids` 关联 `data/sources.json` 的 `source_id`，再与协议的 `source_id`、`original_authors`、`location`、`source_pdf_sha256` 及完整结果核对。原研究作者依次为陈庆云、蒋锡夔、陈秉启、梁梦兰；出版年为 1966，定位为《化学学报》32(1)，印刷 p.21 表 1，PDF 第 4 页。平台的数值重放另列身份，不改写已发表成果的归属。包内没有原论文 PDF；原文指纹登记不等于本次重新取得并核验了原文文件。

结果明确保留：新实验、原谱重拟合和量化计算均 `not_performed`；反应机理、游离阴离子和四基团普适顺序均 `not_tested`；新化学发现 `not_claimed`。量化计算、实验验证和未来假设应使用各自记录及证据，不向本结果补写“已完成”。

原导出的 `boundaries.phase1_status` 反映启动包交付时的状态。后续本机 WSL 验收属于单独工程记录，不能据此删除科学边界或把网站候选状态改为通过。

## 接入与审阅门槛

1. 导入前核对身份、6 行完整性、来源关联、原作者、单位、边界和指纹；缺失或不符时停止导入并记录原因。
2. 结果以独立研究记录关联 PF01。保持现有 YouMind 页面、PFtB 科学正文、`#s/...` 深链状态、稳定编号和原始来源 JSON；本期不改这些文件。
3. 待审候选可供维护者查看。只有独立科学审阅形成明确签认并完成网站文案审阅后，才可依正式发布流程生成另一份审定发布产物；本期导出器始终保留 `review_required`。
4. 实际接入后另验部署路径、来源回链、PFtB 深链、下载链接和禁用 JavaScript 的科学正文。由于目标仓库未知，这些页面检查尚未执行。

本期使用 Python 标准库运行 `python3 -m unittest discover -s tests -v`。`tests/test_website_contract.py` 检查现有候选及新导出、来源关联、原作者、行键、扰动语义和指纹。它不提供通用 JSON Schema 校验器，也不代表已有前端消费了该接口。

交接文档登记了既有 YouMind 候选 ZIP 指纹；本工作区现存的两个 ZIP 均未匹配该指纹，不能指定其中任何一个为正式前端基线。待实际仓库与正确基线包确认后，再作完整网站回归。
