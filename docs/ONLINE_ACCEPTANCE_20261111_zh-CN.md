# GitHub 仓库与 Pages 上线验收

日期：2026-11-11，Asia/Shanghai。工程上线验收通过，科学状态继续保持 `review_required`。

- 公开仓库：[CCcolab/Chen-Qingyun-AI4Science](https://github.com/CCcolab/Chen-Qingyun-AI4Science)，默认 `main`。
- 公开网站：[陈庆云院士学术成就](https://cccolab.github.io/Chen-Qingyun-AI4Science/)。
- 发布实现提交：`8259c6a25d0c55ab6350490ac9011592386a3cb4`。
- [Pages 构建与部署 42988099719](https://github.com/CCcolab/Chen-Qingyun-AI4Science/actions/runs/42988099719)：成功；2026-11-11 16:34:57（UTC+8）完成。
- [研究 CI 42988084688](https://github.com/CCcolab/Chen-Qingyun-AI4Science/actions/runs/42988084688)：成功，23 项测试通过，原包 19 项成员完整性及两份数值结果字节／字段比对通过。

仓库在接入前已创建，随后出现并行网站迁移提交；本次合并保留全部历史与同源网站快照，没有强制推送。独立研究分支 `research/phase1-wsl2-20261111` 也已推送。原论文、传记和照片原件未加入仓库。详情见 `REMOTE_INTEGRATION_20261111.md`。

## 线上检查

15 个 HTML 和两份公开 JSON 均 HTTP 200，响应字节数、SHA-256 与正式 YouMind ZIP 基线一致；目录首页别名也与 `index.html` 一致。51 条来源、A01–A09 九条成果线和稳定编号均保持原样。

`results/website-candidate.json`、`validation/` 和原 ZIP 的网站路径最终均返回 404。第一次排除路径请求遇到一次 HTTP 503，原失败记录保留；仅重试该路径后按原判据取得 404，没有降低标准。证据分别为 `validation/20261111-online/http-acceptance.json` 和 `http-resolution.json`。

实际 Chrome 检查：首页 51 张来源卡和 51 个引用按钮；CQ-H22 复制按钮显示成功，检索定位到主索引 1／49；A08 专题目录、成果档案、CQ-H22 首页资料卡回链有效。PFtB `#s/T03/boundary/R92C` 直接访问和刷新均恢复对应状态；切至 `#s/T04/observation/R92B` 后，前进／后退与可见面板一致。已为用户保留公开网站标签页。

浏览器跨页时记录到一条异步消息通道错误，来源未定位；所查页面功能没有观察到相应失败，原消息保存在 `browser-observations.json`。本轮未声称完成系统剪贴板读回、强制拒绝回退或禁 JS 浏览器会话的全覆盖测试。

## 状态、产物与后续发布

下载的真实 CI 产物位于 `validation/20261111-online/ci-artifact/`，其 summary 为 `passed`，23 项测试，数值结果逐字节及逐字段一致；完整结果和候选分别保留 `scientific_review_status: review_required`、`publication_status: review_required`。

Pages 仅发布 15 HTML、两 JSON 和空 `.nojekyll`；研究候选、验收日志和原 ZIP 可以在源码仓库维护，未作为网页产物发布。仓库仍未接入在线模型服务或量化队列，本次也没有新增实验或科学审定。

后续修改通过研究 CI 验证；Pages 发布工作流仅允许人工从 `main` 触发。此次部署后补充的 README、线上证据和本记录不改变已部署网站字节。历史本地文档保留当时的“待上线”状态，当前线上状态以本记录、实际响应和关联工作流为准。
