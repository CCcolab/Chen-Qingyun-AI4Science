# GitHub 研究扩展的接入与验收

日期：2026-11-11。当前只有可独立运行的首项研究程序及交接方案；没有向任何仓库推送、建立在线模型服务或更改 YouMind 页面。

## 平台分工

GitHub Pages 是静态网站托管。GitHub 仓库承担研究源码、数据登记、计算协议、测试与结果版本；GitHub Actions 可承担受控批处理。交互式模型调用和较长的量化计算如有需要，后续接到独立计算服务。不能将浏览器端页面当作常驻计算后台。

官方说明：
- https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages
- https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow

| 组件 | 首期可用内容 | 后续任务 |
|---|---|---|
| 研究登记 | 来源、观测量、计算协议、结果类型和科学边界 | 接回既有 51 条来源与每条成果线，保持稳定 ID |
| 数值执行 | `python3 -m chen_research`，标准库即可运行 | 审阅通过后再加入量化程序，不默认沿用 AI4OrgChem 的科学协议 |
| 结果交付 | 可复核 JSON，输入／代码 SHA-256，来源定位 | GitHub 批处理结果先作为候选，再进入审阅 |
| 网站接入 | `results/website-candidate.json` | 设计原文、重放结果、代码下载、边界和已有工作对照入口 |
| 在线 AI | 本包未实现，不需要模型密钥 | 决定模型服务和运行预算后再开发；模型提取与数值计算分开验收 |

## 保持现有网站稳定

已核验的 YouMind 候选 ZIP SHA-256：

`fa9740d7a244ab4d52885600a312487869d780a82517aa0d0a401215696c4d3e`

本包不改这份前端、PFtB 原科学正文、`#s/...` 状态或两份原始 JSON。网站记录结果时，应新增研究记录，不覆盖历史来源内容。首期结果仍是 `review_required`，不得改为科学审定通过来绕过审核。

## 仓库接入次序

1. 确认该网站实际的源码仓库、默认分支、Pages 发布源和项目路径。本轮连接检索未定位到名含 chen 的可访问目标仓库；这不表示整个 GitHub 上不存在该仓库。本工作区旧 `platforms/chen-qingyun-legacy` 是早期预备材料，不能当作当前网站源码。
2. 在实际仓库开独立审阅分支。若采用独立研究仓库，本包可作为其首期目录；若放在网站仓库中，放入单独的研究维护目录并配置工作目录，不把交接资料直接铺到 Pages 公开目录。
3. 先执行本地测试与数值重放，对照本包已执行结果，再接 CI。最初只设置人工触发或相关研究代码变更触发；不在本包启用定时任务或自动发布。
4. CI 的最小任务为：检验数据和协议 → 单元测试 → 数值重放 → 输出代码／输入指纹及候选结果。没有审阅签认时，只保留候选产物，不向 Pages 发布科学结论。
5. 量化计算使用独立任务合同，单列核数、内存、时限、软件版本、SCF／优化／频率验收和失败状态。本包没有把任何未来计算标成通过。
6. YouMind 后续只消费审阅通过的结果和已批准文案；平台研究任务的实现、测试、日志和源码交给 Codex 维护。

## Windows 11／WSL 2／Ubuntu 验收

在 Windows PowerShell 先检查：

```powershell
wsl -l -v
```

确认目标 Ubuntu 的 VERSION 为 2。将本包解到 Ubuntu Linux 文件系统，进入本包目录执行：

```bash
python3 --version
python3 scripts/verify_delivery.py
python3 -m unittest discover -s tests -v
python3 -m chen_research --output scratch/wsl-replay
diff -u results/pftb1966-uv-replay.json scratch/wsl-replay/pftb1966-uv-replay.json
diff -u results/website-candidate.json scratch/wsl-replay/website-candidate.json
```

科学模块使用 Python 3.10+；现有前端的 Node 24 验收另行保留。Windows／WSL 命令的实际输出、当前 Linux 已执行记录以及未来 GitHub CI／Pages 结果分别保存，不能互相替代。

## 网站呈现与科学验收

PFtB 研究记录建议呈现：原论文与页码 → 原表值 → 本次固定计算 → 名义结果和敏感性 → 可重跑代码 → 未解决问题。标明“原表数值重放”，不使用“已证明阴离子机理”“重现实验”或“新发现”标题。

正式接入后复测实际部署路径、来源回链、PFtB 深链状态、结果下载与禁 JS 正文。模型问答若后续启用，必须返回原始材料定位及证据身份，并允许回答证据不足；不能从若干摘要自动生成“世界首次”的结论。
