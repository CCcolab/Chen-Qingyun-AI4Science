# 陈庆云学术成就网站与 AI 辅助研究

正式源码仓库：[CCcolab/Chen-Qingyun-AI4Science](https://github.com/CCcolab/Chen-Qingyun-AI4Science)，默认分支 `main`。YouMind 负责网页制作和导出，GitHub 保存源码并使用 GitHub Pages 发布。网站内容保持原作者归属；研究结果继续保留 `review_required`。

公开网站：[陈庆云院士学术成就](https://cccolab.github.io/Chen-Qingyun-AI4Science/)。2026-11-11 已完成 GitHub Actions 发布和线上验收；见[上线验收记录](docs/ONLINE_ACCEPTANCE_20261111_zh-CN.md)。

本项目同时保留两份独立材料：

- 网站：`upstream/chen-qingyun-a2-citations-candidate.zip`，21 个原始成员完整解到 `site/`，包含 15 个 HTML、两份原始 JSON。ZIP 指纹与研究交接文档一致，预览页没有替代源码。
- 研究：保留启动包的科学代码、数据、协议和历史结果；测试文件仅留本机，不再同步到 GitHub。原 SHA 清单、[原始说明](README_zh-CN.md)与历史环境记录保留，当前分发范围见[同步策略](docs/LOCAL_TESTS_POLICY_zh-CN.md)。PF1966-UV-T1 仅为原表数值重放，网站候选结果保持 `review_required`。

## 本地检查

Python 3.10+，无需模型 API 密钥或第三方 Python 库：

```bash
python3 scripts/accept_phase1.py --skip-tests --output scratch/research-check
python3 scripts/check_site.py --output scratch/site-check.json
python3 scripts/build_site.py --output scratch/site-dist
python3 -m http.server 8000 --bind 127.0.0.1 --directory scratch/site-dist
```

验收目录使用新路径。WSL 正式实测记录位于 `validation/`；Windows 和 WSL 环境分开记录。网站构建只输出网页和公开来源数据，研究候选、环境日志及原始 ZIP 不进入 Pages 产物。

上述命令适用于 GitHub 克隆。原本机保留 `tests/` 时，去掉 `--skip-tests` 可执行完整本地测试；本地 Git 排除规则阻止其继续加入提交。GitHub CI 和 Pages 只做保留源码完整性、固定数值重放、结果比对和网站检查，单测明确记录为未运行。

网站和研究原成果均归原作者；工程测试通过不代表新的实验、量化计算、机理验证或科学审定。尚未确定再分发许可的原论文全文、传记及照片不加入网站产物。

[迁移与发布交接](docs/GITHUB_PAGES_MIGRATION_zh-CN.md) · [研究接入说明](docs/PHASE1_INTEGRATION_zh-CN.md) · [候选结果接口](docs/WEBSITE_RESULT_CONTRACT_zh-CN.md) · [后续研究入口](docs/NEXT_RESEARCH_GATES_zh-CN.md)

针对 `b5d562c` 的评审，当前研究分支新增固定输入 v2 严格校验、完整运行快照和具名签认门禁。原 `results/` 及 v1 引擎封存不改；新 CLI 默认写入新的 `scratch/runs/` 目录。当前审阅者登记为空、审定导出关闭，独立研究页面仅供待审预览。详见[当前科研发布状态](docs/CURRENT_RESEARCH_STATUS_zh-CN.md)及[签认操作流程](docs/SCIENTIFIC_REVIEW_zh-CN.md)。

原包及首次本地验收文档保留当时状态；后续线上执行以 GitHub Actions 和实际部署记录为准。仓库原初始提交及其 README 均已保留在历史中，见[初始仓库说明存档](docs/REMOTE_INITIAL_README_20261111.md)。

接入时仓库还新增了同源网站迁移快照；其历史、[使用说明](NOTICE.md)、[迁移文档](docs/MIGRATION_zh-CN.md)、[YouMind 交付约定](docs/YOUMIND_HANDOFF_zh-CN.md)及 `tools/` 检查工具一并保留。正式发布仍使用本仓库 `scripts/` 的联合验收与独立 Pages 流程。
