# YouMind 网站迁移到 GitHub Pages

日期：2026-11-11。用户确认目标仓库尚未创建，拟名 `CCcolab/Chen-Qingyun-AI4Science`，默认分支计划 `main`。本次完成本地迁移工程；仓库创建、实际 URL、推送、GitHub Actions 与线上 Pages 验收仍待接入。

## 采用的基线

内容与布局参考：[总平台预览](https://cdn.youmindassets.com/artifacts/01a1b88d-1c2a-7b9c-877e-2d051b9c337f/index.html)。最新导出来源：[证据回链与完整引用候选包入口](https://cdn.youmindassets.com/artifacts/01a1b931-8fc7-7499-a1ee-c67d17810774/index.html)。该入口依赖上一轮浏览器临时 ZIP；本轮打开后显示原会话不可读取，未生成新包。

已在本机 Downloads 找到此前生成的 `chen-qingyun-a2-citations-candidate.zip`，414473 字节，SHA-256 `fa9740d7a244ab4d52885600a312487869d780a82517aa0d0a401215696c4d3e`，与 AI 研究包交接登记完全匹配。同名带 `(1)` 的副本也相同。正式采用这份已导出的完整 ZIP，未从预览 HTML 重建。

原 ZIP 保存在 `upstream/`；21 个成员原样解到 `site/`，15 个 HTML 覆盖首页、成果全景、专题目录、PFtB 和十一专题。来源追溯及逐文件指纹见 `provenance/website-baseline.json`。

两份原始 JSON 保持原字节：

| 文件 | SHA-256 |
|---|---|
| `site/data/public-sources.json` | `94f8b9f6d0849deb9f26f75947205cfc8c4eb0973045fe958f2121237d987062` |
| `site/data/achievement-lines.json` | `1c9ec28bf41a7d79214e84a1c07f3bea1e0d91630dd3a88c93c39ff68a9bccec` |

PFtB 文件指纹为 `0d4396b85f8cfd772edcf8fe9bc192d845268399e1ed3834e1d83562639ba372`。迁移保持其科学正文、稳定编号和 `#s/...` 状态代码。所有导出页面继续使用原有文案、作者归属与审阅状态。

## 构建、CI 与发布

`scripts/check_site.py` 核对基线、来源、成果线及站内路径；`scripts/build_site.py` 只把 15 HTML、两 JSON 与 `.nojekyll` 写入独立目录。研究的 `results/website-candidate.json` 保持待审，没有进入网站产物，原 ZIP 和工程日志也不进入 Pages。

研究 CI 在相关路径变更或人工触发时检查测试、数值重放及网站构建，不执行发布。`.github/workflows/pages.yml` 是独立发布流程：仅人工触发，且只允许 `main`。构建通过后上传网站产物，部署使用 `github-pages` 环境；目标仓库创建后，应把环境发布分支限制为实际 `main`，并按维护者流程设置审阅。

发布流程固定官方动作提交：[upload-pages-artifact v5.0.0](https://github.com/actions/upload-pages-artifact/releases/tag/v5.0.0)、[deploy-pages v5.0.1](https://github.com/actions/deploy-pages/releases/tag/v5.0.1)。Pages 需在仓库设置选择 GitHub Actions 作为发布源，部署任务使用 `pages: write` 和 `id-token: write`；见[官方自定义工作流说明](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)。本地配置存在不代表远程流程已经执行。

网站 JavaScript 语法验收使用 Node 24.13.1；CI 通过[setup-node v4.4.0](https://github.com/actions/setup-node/releases/tag/v4.4.0)固定安装该版本并要求语法检查执行。首次 WSL 检查没有系统 Node，正式验收使用从 nodejs.org 取得、与官方 SHASUMS256.txt 相符的 Linux 发行包，仅抽出 `bin/node` 到临时 Linux 目录；不写系统目录、不改用户全局配置。重跑 `validate_wsl.py` 时可提供成对 `--node-archive`、`--node-shasums` 路径，或使用环境中已有的原生 Linux Node 24。

## 实际 URL 明确后的接入

1. 核实组织、仓库、可见性、默认分支和权限；按用户要求再添加真实 `origin`，不把拟名当成已存在地址。
2. 推送原包 `main` 基线和研究分支，形成可审阅差异，检查远程 CI。首次合入前保留网站与研究两份来源及本地验收证据。
3. 将已审阅工程合入实际 `main`，启用 Pages 的 GitHub Actions 发布源，人工执行发布工作流。
4. 核验实际网站根路径、项目子路径、15 页响应、来源回链、A08 入口、完整引用复制、PFtB 深链刷新、前进后退及禁用 JS 正文。记录真实部署 URL 和工作流，不以本地预览替代线上验收。

若最终仍采用拟名，预期项目路径为 `/Chen-Qingyun-AI4Science/`；这只是路径测试条件，尚无已部署 URL。当前网站仍是原候选内容，科学签认与页面迁移分别验收。
