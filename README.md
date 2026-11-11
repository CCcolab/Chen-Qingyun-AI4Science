# 陈庆云学术成就网站与 AI 辅助研究

本地迁移准备项目，目标仓库拟名 `CCcolab/Chen-Qingyun-AI4Science`。仓库尚未创建，当前未设置远程地址、推送或部署。计划由 YouMind 制作和导出网页，由 GitHub 保存源码并使用 GitHub Pages 发布。

本项目同时保留两份独立材料：

- 网站：`upstream/chen-qingyun-a2-citations-candidate.zip`，21 个原始成员完整解到 `site/`，包含 15 个 HTML、两份原始 JSON。ZIP 指纹与研究交接文档一致，预览页没有替代源码。
- 研究：2026-11-11 AI 研究启动包的 20 个文件原样保留在根目录；[原始说明](README_zh-CN.md)与历史环境记录不改写。PF1966-UV-T1 仅为原表数值重放，网站候选结果保持 `review_required`。

## 本地检查

Python 3.10+，无需模型 API 密钥或第三方 Python 库：

```bash
python3 scripts/accept_phase1.py --output scratch/research-check
python3 scripts/check_site.py --output scratch/site-check.json
python3 scripts/build_site.py --output scratch/site-dist
python3 -m http.server 8000 --bind 127.0.0.1 --directory scratch/site-dist
```

验收目录使用新路径。WSL 正式实测记录位于 `validation/`；Windows 和 WSL 环境分开记录。网站构建只输出网页和公开来源数据，研究候选、环境日志及原始 ZIP 不进入 Pages 产物。

网站和研究原成果均归原作者；工程测试通过不代表新的实验、量化计算、机理验证或科学审定。尚未确定再分发许可的原论文全文、传记及照片不加入网站产物。

[迁移与发布交接](docs/GITHUB_PAGES_MIGRATION_zh-CN.md) · [研究接入说明](docs/PHASE1_INTEGRATION_zh-CN.md) · [候选结果接口](docs/WEBSITE_RESULT_CONTRACT_zh-CN.md) · [后续研究入口](docs/NEXT_RESEARCH_GATES_zh-CN.md)
