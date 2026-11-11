# Windows 11／WSL 2（Ubuntu）验收

正式本地环境是 Windows 11／WSL 2（Ubuntu）。云端 Linux 或 GitHub Actions 的检查均为辅助验证，不能替代本表，也不能改写为“WSL 2 已验证”。本表交付时各项均待本机记录。

## 环境和自动检查

PowerShell：

```powershell
wsl --list --verbose
```

记录 Windows 版本、Ubuntu 发行版、目标发行版 VERSION=2、验收日期及人员。

WSL 2／Ubuntu 仓库目录：

```bash
uname -a
cat /etc/os-release
git --version
python3 --version
node --version
python3 tools/check_site.py --http --prefix /Chen-Qingyun-AI4Science/ --report /tmp/chen-wsl2-check.json
node tools/check_js.mjs
python3 tools/serve_site.py --port 8000
```

Node 应为 24.x。若缺少所需工具，先使用本机已有的软件管理方式安装，再重新记录实际版本。静态站本身无需 npm 构建。

## 浏览器验收

在 Windows Chrome／Edge 分别访问 `http://localhost:8000/` 与 `http://localhost:8000/Chen-Qingyun-AI4Science/`。本地两路径各做一次；真实 GitHub Pages 再单独复测。

| 项目 | 操作与预期 | 本机结果 |
| --- | --- | --- |
| 文件完整性 | 15 HTML、51 来源、9 成果线；两份 JSON、PFtB 及原始网页哈希检查通过 | 未测 |
| 15 页入口 | 首页、全景、目录、PFtB 和 11 个其他专题直接访问及 F5 均可用 | 未测 |
| A08 入口 | 专题目录的含氟离子液体入口到全景 A08 对应条目 | 未测 |
| 证据回链 | CQ-H22、CQ-H01、CQ-R28、CQ-H06 到首页准确卡片；刷新定位保留 | 未测 |
| 来源与复制 | 51 张卡；CQ-H22／CQ-R08／CQ-H01 复制后粘贴到 Windows 文本编辑器，字段与年份完整；无原网址不虚构网址 | 未测 |
| 权限受限 | 实际拒绝剪贴板权限后显示可选完整文本，不显示虚假成功；完成后恢复个人设置 | 未测 |
| PFtB 状态 | 进入 T02/boundary/R92C，普通导航与 CTA 后 F5 保留 `#s/...`；前后退恢复；控制台无异常 | 未测 |
| 键盘操作 | 弹窗首次焦点、立即 Shift+Tab、Tab 陷阱、Esc、还焦；跳到正文后焦点在 main | 未测 |
| 自适应 | 320／360／768／1440px 无横向溢出；固定导航不遮挡目标 | 未测 |
| 打印 | 实际打印预览及保存 PDF，正文、引用、边界和分页可读 | 未测 |
| 禁 JS／文件 | 禁 JS 阅读静态正文；file:// 单列其功能限制，不和 HTTP 混报 | 未测 |
| GitHub Pages | Actions 成功，真实网址上述主要路径、复制及 PFtB 状态复验 | 未测 |

不得通过脚本注入假剪贴板成功结果替代系统粘贴证据。没有真实权限拒绝证据时，该分支保留未测。iOS／Android 如未实测也继续注明未测。

## 记录

- 日期、验收人、Windows／Ubuntu／Node／浏览器版本：待补。
- Git 提交号、访问前缀与实际 URL：待补。
- 通过项、失败步骤、控制台错误及截图或日志位置：待补。
- 当前云端自动检查记录在 `audit/validation-report.json`，不属于本机验收结论。
