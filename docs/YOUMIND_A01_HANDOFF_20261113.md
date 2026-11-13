# YouMind后续维护交接：A01公开研究进展

本文件为维护说明；交接材料已准备不等于YouMind已接收或完成修改。未代用户向YouMind发送消息。

## 当前维护入口

- 网站源码仍沿用YouMind版式，A01专题路径及原锚点保持：`site/topics/early-fluoroketones/index.html`。
- 当前数据入口为`research/a01/public-progress.v1.json`，接口说明为`research/a01/PUBLIC_PROGRESS_INTERFACE_zh-CN.md`；网页中的进展区块由`scripts/render_a01_progress.py`生成。
- 网站名称使用“全氟酮化学早期研究：六氟丙酮反应与六氟双酚A（双酚AF）制备”，三分支分别呈现；单中心电子检查只更新噁唑酮支线。
- 证据归档固定提交以公开数据的`evidence_archive_commit`为准；实际部署版本、Pages运行ID及线上核对记录在部署后最终交接记录中补齐，不能以本说明中的待办代替已完成事实。

## 后续编辑必须保留的范围

保留`review_required`、`release_eligible=false`和“中心电子合格≠完整曲率合格≠势垒验证”。保留既有来源ID、原作者归属、PFtB正文及引用。第117491号说明书与尚缺的授予正页分别登记；AI核读页段不升级为完整专业核译；百年诞辰继续隐藏。

进展区块使用`A01_PUBLIC_PROGRESS_BEGIN/END`标记。不要直接改生成区块中的数字；修改实际公开数据后重新生成并检查。它的内嵌JSON、可见文字及源JSON SHA必须一致。

新A01页面修订记录位于`provenance/a01-site-revision.v1.json`。该记录追加说明授权改动，不替换原`provenance/website-baseline.json`或原导出包历史指纹。后续若在YouMind另行导出，先与GitHub现行源版本逐项合并，再重新登记合法修订；不要用旧导出覆盖当前研究进展。

## 实际交接状态

```json
{
  "materials_prepared": true,
  "YouMind_received": false,
  "YouMind_modified": false,
  "final_publication_commit": null,
  "Pages_run_id": null,
  "online_content_verification": "recorded_in_post_deployment_handoff"
}
```

空值由部署后的本地最终交接包补充；本文件保持提交时的准备记录，不把后补提交号写成执行源码身份。
