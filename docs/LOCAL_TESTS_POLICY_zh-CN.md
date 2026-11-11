# 测试文件仅在本机保留

2026-11-11，按用户新要求：`tests/`、`test/` 不再同步到 GitHub。现有本机测试文件保留，从 `main` 和独立研究分支的当前 Git 跟踪中移除；不重写已经发布的历史提交。

本机仓库 `.git/info/exclude` 已排除 `/tests/` 和 `/test/`。它是本地设置；新克隆如需要自己维护测试，也应添加相同本地排除规则。原 `.gitignore` 属于启动包指纹清单，保持原字节。历史测试日志及 19／23 项验收记录均为此前真实记录，继续保留，不改写成当前 CI 执行结果。

## 本机与 GitHub 的执行范围

- 本机保留测试时：`python3 scripts/accept_phase1.py --output scratch/new-local-acceptance`，核验原 19 项成员、在快照运行原完整包检查并执行本地测试。
- GitHub 或无测试的克隆：`python3 scripts/accept_phase1.py --skip-tests --output scratch/new-source-check`，核验原清单中仍分发的 18 项成员；明确排除 `tests/test_uv_replay.py`，不运行原完整包验收器和单元测试。输出 `tests_run: 0`、`tests_status: not_run_by_distribution_policy`，不声称测试通过。
- 两种模式都实际运行 PF1966-UV-T1、逐字节及逐字段比较两份结果，并保留 `review_required`。
- CI 和 Pages 使用第二种模式，仍检查网站原文件指纹、JavaScript 语法、来源编号、站内链接和发布产物范围。

`validate_wsl.py` 仍可从本机原 ZIP 在 Linux 临时文件系统执行原 9 项测试；克隆已提交分支的集成阶段改用无测试分发模式。需要完整本机测试时，应另外在保留 `tests/` 的原本机项目运行第一条命令。

测试分发策略不改变科学代码、原数据、协议、网页正文及发布状态，也不改变已经部署网站的文件字节。
