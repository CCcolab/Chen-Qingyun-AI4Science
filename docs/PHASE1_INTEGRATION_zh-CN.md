# 第一阶段本地接入说明

日期：2026-11-11。这里是独立研究仓库的接入准备。用户已明确：仓库尚未创建，拟名 `CCcolab/Chen-Qingyun-AI4Science`，默认分支计划 `main`，正式网站计划 GitHub Pages，YouMind 负责制作、预览和导出。仓库创建、远程配置、推送与线上发布均留待实际 URL 明确之后。原始 README、交接文档和结果保留为启动包的历史快照；本次正式环境验收另存，不能以改写历史记录的方式补上。

本地项目：`D:\AI4Science\Chen-Qingyun-2029\Chen_Qingyun_AI_Research_20261111`。原包基线提交为 `f6af9e5f0c87cc569e3bf77b4ac8a8a90eb6d482`，分支为 `research/phase1-wsl2-20261111`。当前没有远程仓库。机器未配置 Git 作者，本仓库使用本地自动化身份 `Codex <codex@localhost>`；这只是代码导入与工程提交身份，原科学作者仍以来源登记为准。

## 原包完整性与扩展目录

用户 ZIP SHA-256：`623127d317b3a4ecc51052e43816286a3dd04eb95f41fc8bf7c3bb8d76bc2d4f`。原包共 20 文件；`SHA256SUMS` 列出除清单自身外的 19 文件。所有原文件保持原字节。`.gitattributes` 禁止文本行尾转换，以保护数据、代码和历史结果指纹。

原 `scripts/verify_delivery.py` 严格要求目录只有原包成员，因此不能直接在新增文件后的目录用它断言“整个交付包完整”。新 `scripts/accept_phase1.py` 固定原清单指纹、检查 19 成员，在临时原包快照中运行原验收器，再执行整个集成目录的测试、重放及两份 JSON 的逐字节和逐字段比较。新增文件由 Git 及验收时的 `source-inventory.json` 记录。

## 重跑

在项目目录，Ubuntu Python 3.10+ 可执行离线集成验收：

```bash
python3 scripts/accept_phase1.py --output scratch/new-acceptance
```

输出目录必须新建或为空。该命令记录实际环境；只有在 WSL 2 中运行才能形成 WSL 证据。

正式 WSL 验收从原 ZIP 重新解出完整包，并把当前已提交分支克隆到 Linux 临时文件系统；原包与集成版分别执行测试和数值任务：

```powershell
wsl -d Ubuntu-24.04 --exec python3 /mnt/d/AI4Science/Chen-Qingyun-2029/Chen_Qingyun_AI_Research_20261111/scripts/validate_wsl.py --output /mnt/d/AI4Science/Chen-Qingyun-2029/Chen_Qingyun_AI_Research_20261111/validation/new-wsl2
```

运行前先提交要验收的实现；脚本只克隆已提交代码，并在证据中记录提交号。临时 Linux 目录在完成后移除，完整输出和日志保存在指定目录。Windows 版本、WSL 发行版列表和关联时间另存主机证据。每次使用新目录，保留失败记录。

## CI 配置及发布边界

`.github/workflows/research-ci.yml` 面向独立研究仓库：Ubuntu 24.04、Python 3.12、仅人工或研究相关路径变更触发，只读权限，上传候选结果和验收证据。未配置定时任务或部署。若最终嵌入网站仓库，须按研究子目录调整 `paths`、工作目录、脚本路径和产物路径，并在实际仓库中运行验证。

Actions 使用已核验的官方发布固定提交，不把配置存在写成远程 CI 已通过：

| 动作 | 固定发布 | 官方来源 |
|---|---|---|
| checkout | v4.3.1 | https://github.com/actions/checkout/releases/tag/v4.3.1 |
| setup-python | v5.6.0 | https://github.com/actions/setup-python/releases/tag/v5.6.0 |
| upload-artifact | v4.6.2 | https://github.com/actions/upload-artifact/releases/tag/v4.6.2 |

## 待补的接入信息

- 实际 GitHub 仓库 URL、默认分支、写入权限、研究目录位置和分支保护规则。
- 正式 YouMind 页面及对应源码、Pages 发布源（若使用）、构建方式和正确的前端基线。
- 科学审阅者、转录签认及候选转为正式发布产物的流程。
- 项目的代码与数据许可。原包未附 LICENSE，不推定原论文全文或现有素材可再次分发。

用户补充目标规划前，连接检索 `Chen`、`Qingyun` 未返回目标。旧 Starter 数据中只有建议仓库 `CCcolab/Chen-Qingyun-Legacy`；本轮连接读取返回 404，不能判定其不存在。该旧拟名不是本次目标。未创建远程仓库、推送或发布。

交接文档登记的前端 ZIP 指纹为 `fa9740d7a244ab4d52885600a312487869d780a82517aa0d0a401215696c4d3e`。现存 `Chen_Qingyun_YouMind_Starter_20261101.zip` 为 `4b6ef282d11efdd7396d8648dbb856d38b99fae5ee2b05dedd8d1ba09c6880eb`，`Chen_PFtB_Source_Candidate_20261104.zip` 为 `d9ec71125bcc867764e1d4229e719c5d0912d72af714e29d745fce20b59f7bb9`。两者均不能自动替代正式基线；已保留原文件和原始 JSON。

网站候选读取规则见 `WEBSITE_RESULT_CONTRACT_zh-CN.md`；未来研究入口见 `NEXT_RESEARCH_GATES_zh-CN.md`。本次工程验收不改变 `review_required`，也不构成独立科学审定。
