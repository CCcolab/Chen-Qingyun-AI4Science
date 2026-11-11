# 陈庆云院士学术成就

陈庆云院士学术成就展示与 AI for Science 研究平台。YouMind 负责网页建设，GitHub 保存版本并通过 GitHub Pages 发布；正式本地环境为 **Windows 11／WSL 2（Ubuntu）**。

本次迁移快照：2026-11-11。保留 YouMind 最新独立复验版本的 15 个 HTML 页面与两份 JSON 数据，新增发布和检查工具；9 条成果线、51 条来源和原有科学边界不变。百年诞辰展示仍暂不启用。

目标仓库：`CCcolab/Chen-Qingyun-AI4Science`，默认分支：`main`。

预期 Pages 地址（须以实际成功部署为准）：https://cccolab.github.io/Chen-Qingyun-AI4Science/

## 本地使用

在 WSL 2／Ubuntu 中进入仓库，确认 Python 3 和 Node.js 24 可用，然后运行：

```bash
python3 tools/check_site.py --http
node tools/check_js.mjs
python3 tools/serve_site.py --port 8000
```

浏览器分别打开 http://localhost:8000/ 和 http://localhost:8000/Chen-Qingyun-AI4Science/ 。

`site/` 是唯一公开网页目录。页面无需 npm 安装或构建；Node 24 只用于内嵌 JavaScript 语法检查。`tools/`、`audit/`、`docs/` 不会被上传为 Pages 网页。

## 迁移与验收

- [仓库创建、发布与回退](docs/MIGRATION_zh-CN.md)
- [Windows 11／WSL 2 验收清单](docs/WSL2_ACCEPTANCE_zh-CN.md)
- [YouMind 后续交付约定](docs/YOUMIND_HANDOFF_zh-CN.md)
- [网页原始字节清单](audit/site-manifest.json)
- [当前环境自动检查记录](audit/validation-report.json)

当前自动检查只验证文件、引用目标、两路径 HTTP 和 JavaScript 语法。它不证明 Windows／WSL 2 实测、真实剪贴板行为、浏览器交互全部通过或科学论断已完成审定。实际 GitHub 部署状态以仓库 Actions／Pages 为准。

## 后续 AI 扩展

研究代码和计算结果需在独立分支逐项加入；本快照尚未接入在线 AI 服务或复算任务。论文归属、史料事实、已发表的他人成果、AI 推断及待检验假说须分别标示。不得把自动生成的内容直接升级为已复现结果或原创发现。

网页中保留的 `review_candidate`、定位与科学边界继续有效。迁移不改变其学术审定状态。见 [来源与使用说明](NOTICE.md)。
