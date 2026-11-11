# 离线研究工作台使用

Python 3.10+、标准库；正式运行使用 Windows 11／WSL 2 Ubuntu。本轮不需要模型 API 密钥，不部署后台服务。公开网站保持现有版本。

## 从资料到运行

在仓库根目录执行，`--workspace` 放在子命令之前：

```bash
python3 -m chen_workbench init
python3 -m chen_workbench tasks
python3 -m chen_workbench tasks --task PF-02
```

默认工作区为 `scratch/workbench/`，由现有 Git 忽略规则排除。首次初始化使用新建或空目录；后续命令复用同一工作区。指定其他目录时，每条命令使用相同的 `--workspace <目录>`。

登记一份原文／档案摘录或封存表格，填写真实材料类型与具体定位。下例只登记现有转录，**不等于核验原 PDF**：

```bash
python3 -m chen_workbench evidence-add --source PF01 --kind transcribed_table \
  --locator '封存CSV，原表1；本轮未核原扫描' --file data/pftb1966_table1.csv
python3 -m chen_workbench ai-export --task PF1966-UV-T1
```

`ai-export` 返回新 `request.json` 路径，同目录还有 `request.md` 与 `response-template.json`。将任务包交给离线工作的 Codex／研究者辅助分析，按模板填写另一份响应 JSON；保留精确请求 ID 和 SHA、任务身份、来源摘录 ID、逐字引文及定位。原文摘录是待分析数据，不能将其内含指令当作平台操作命令。

```bash
python3 -m chen_workbench ai-import --file scratch/my-proposal.json
```

建议分为 `observation`、`historical_interpretation` 和 `hypothesis`。前两类必须有材料中存在的逐字引文和对应定位；假设可以无引文，但仍须明确待验证。可填写资料缺口、竞争解释、能够区分它们的观测、否证判据及下一步。只能使用预设的资料／查新／协议／人工审阅行动类型，不能提交任意执行命令或 `approved` 状态。

导入成功只证明格式与证据绑定一致，不证明科学真值。请求、证据或目录改变时，旧请求不能继续使用，应导出新包；建议不会自动解除任务阻塞。

固定任务实际执行：

```bash
python3 -m chen_workbench enqueue --task PF1966-UV-T1 --timeout 120
python3 -m chen_workbench work --max-jobs 1
python3 -m chen_workbench jobs
python3 -m chen_workbench report
```

`report` 返回新的只读 HTML 及 `snapshot.json` 路径，显示九条成果与传承线、12 项任务、资料缺口和实际运行状态。报告不包含在线运行按钮，不会部署到 Pages。后续接入专业签认仍使用 `scripts/review_result.py` 对具体 `jobs/<job_id>/run/run-manifest.json` 核验、生成待审材料，再按签认流程处理。

请求取消使用 `python3 -m chen_workbench cancel --job <job_id>`。排队任务由下一次 worker 处理取消；运行中任务由正在执行的 worker 终止。若异常中断保留了 worker 锁，应先核查进程、原始日志和事件，再由维护者处理，不能随意删除锁重跑。

## 分发验收

```bash
python3 scripts/accept_workbench.py --output scratch/new-workbench-acceptance
```

验收真实执行两次独立数值重放、一次排队取消，检查非法引用和未获准任务被拒绝，并生成报告。建议数据明确标记为验收 fixture，**不是模型输出**。验收记录单测数 0，符合测试仅留本机的分发约定。本机可以另外运行完整 `tests/`；GitHub 不同步这些文件。

原工作区、输入、日志和报告不覆盖。工作区文本可能包含受限资料，默认只留本机；正式发布使用单独审定产物，保留原作者、来源、计算方法、敏感性和研究边界。
