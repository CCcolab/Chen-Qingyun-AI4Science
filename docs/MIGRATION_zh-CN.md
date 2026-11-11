# GitHub 迁移执行说明

本说明适用于 Windows 11／WSL 2（Ubuntu）。当前交付保留 15 个 HTML 与两份 JSON 原始字节，另加 `.nojekyll`、检查工具、审计清单及发布配置。不是 YouMind 原完整 ZIP 的重新命名副本。

## 目标与来源

目标：`CCcolab/Chen-Qingyun-AI4Science`；默认分支 `main`；GitHub Pages 使用 GitHub Actions，仅发布 `site/`。

来源为此前从“证据回链与完整引用候选包”独立解包并复验的 17 个网页及数据文件。生成器地址只作追溯，不是应上线的网站入口：

https://cdn.youmindassets.com/artifacts/01a1b931-8fc7-7499-a1ee-c67d17810774/index.html

当前可用的是已提取文件，未把不在当前环境中的原始完整 ZIP 宣称为重新解压验证。迁移清单记录所有网页文件的 SHA-256。PFtB 页面另与早一轮完整候选包比对一致；两份 JSON 的原始 A2 哈希仍被检查器单独保护。

## 本机 Codex 接续

先在 PowerShell 运行 `wsl --list --verbose`，确认目标 Ubuntu 的 VERSION 为 2。随后在该 Ubuntu 的 `~/projects/` 内操作，优先使用 WSL 文件系统。

如果仓库已由本轮操作创建，先克隆它，再将本包内容覆盖到克隆目录；不要覆盖 `.git/`：

```bash
mkdir -p ~/projects
cd ~/projects
git clone https://github.com/CCcolab/Chen-Qingyun-AI4Science.git
cd Chen-Qingyun-AI4Science
# 在此将本迁移包的项目目录内容复制进来，再继续。
python3 tools/check_site.py --http --prefix /Chen-Qingyun-AI4Science/
node tools/check_js.mjs
git status --short
git add site audit tools docs README.md NOTICE.md .gitattributes .gitignore .github
git diff --cached --stat
git commit -m "Migrate verified YouMind website and add GitHub Pages checks"
git push origin main
```

仅当仓库确实不存在且当前目录尚不是其他仓库时，已登录的 GitHub CLI 可创建并推送新仓库：

```bash
git init -b main
git add site audit tools docs README.md NOTICE.md .gitattributes .gitignore .github
git diff --cached --stat
git commit -m "Migrate verified YouMind website and add GitHub Pages checks"
gh repo create CCcolab/Chen-Qingyun-AI4Science --public --source=. --remote=origin --push
```

不自动更改机器的 GitHub 登录、密钥或已存在仓库配置。如果遇到已有提交，先克隆并正常提交；不要使用强制推送覆盖历史。

## 启用 Pages

在目标仓库 `Settings → Pages → Build and deployment → Source` 选择 `GitHub Actions`。确认默认分支为 `main`。

如果工作流在启用 Pages 前已失败，在 `Actions → Validate and publish website → Run workflow` 重新运行，分支选择 `main`。检查 validate 与 deploy 两个任务均成功，以 deployment 输出地址为准，不把期望 URL 当成已上线证据。

发布配置来源：GitHub 官方 Pages 自定义工作流文档；Node 24 使用 setup-node 官方示例中的 v7。各版本以本次核对日 2026-11-11 为准。

- https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages
- https://github.com/actions/setup-node

## 发布后核查

在真实 Pages URL 检查首页、成果全景、专题目录和全部专题可直接打开及刷新。重点检查：

1. 专题目录中含氟离子液体入口到 `achievements/#record-fluorinated-ionic-liquids`。
2. 全景页 A08 的 CQ-H22、A09 的 CQ-H01／CQ-R28／CQ-H06 能回到首页对应卡片。
3. 首页 51 个来源卡片及完整引用复制；权限拒绝时能手动选择文本。
4. PFtB `#s/T02/boundary/R92C`、普通导航、刷新、前进后退与弹窗焦点。
5. 320／360／768／1440px 布局、打印及禁 JS 静态正文。

自动 HTTP 检查验证根路径和仓库名前缀下文件返回字节、目录入口及静态锚点。它没有操作浏览器、执行客户端脚本或检验实际剪贴板；这些应按 WSL 验收表和 Pages 实测补录。

## 回退和后续

发生问题先查看失败步骤和变更；已发布版本使用 `git revert` 新增回退提交，并观察 Pages 成功部署。保留失败记录和相应提交号。

YouMind 后续交付通过分支导入、比对和复验。研究扩展不在此次网页迁移中自动启用；AI 密钥不得进入 `site/`、前端脚本或 Git 历史。
