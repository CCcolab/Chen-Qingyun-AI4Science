# 绑定具体运行的科学签认

本流程只适用于 PF1966-UV-T1 原表数值重放。签认实现就绪，真实专业签认尚未发生。策略 `reviews/review-policy.json` 目前为 `release_enabled: false`，`authorized_reviewers: []`；禁止为演示伪造人员、机构、原文核校或批准。

## 生成待审材料

在正式 WSL 2、仓库根目录执行，输出路径均须新建；候选历史不覆盖：

```bash
python3 -m chen_research --output scratch/runs/new-run
python3 scripts/review_result.py verify-run --run scratch/runs/new-run/run-manifest.json
python3 scripts/review_result.py preview --run scratch/runs/new-run/run-manifest.json --output scratch/review/new-packet
python3 scripts/review_result.py policy-status
```

默认 CLI 会自动选择带 UTC 和 UUID 的新 `scratch/runs/` 子目录。输入资格不合格时退出失败，不产生成功清单或候选；失败审计另存 `scratch/failures/`。原 `results/` 和 `upstream/pftb1966-v1/` 为历史封存材料，不使用 v2 覆盖。

运行目录包含三份原输入、实际执行模块快照、真实 Python／OS／内核／Git 记录、完整结果、候选和 `publication-payload.json`。`run-manifest.json` 最后生成，绑定每份文件的相对路径、字节数和 SHA-256，并记录实际调用、完成时间和运行 ID。此运行器本身不执行单测，明确记 `tests_run: 0`；完整验收与本机测试另有记录。

预览目录包含待审独立 HTML、完整展示 JSON 和 `review-request.json`。页面同时展示原作者和来源定位、十项观测、六项计算、±0.05 nm 舍入敏感性、比较、排除观测及边界。原文不在包内，登记的扫描指纹不等于本轮重新核过原扫描。

## 专业审阅与独立签名

1. 维护者先核实真实审阅者的姓名、机构、身份、公钥归属和六项审阅资格，按代码评审流程登记唯一 `reviewer_id`、完整姓名、机构与 Ed25519 公钥。私钥仅由审阅者保管，不进项目或 CI。登记策略的变更需要重新生成请求；其 SHA-256 也是签认的一部分。
2. 合格审阅者必须取得协议指纹对应的原 PDF 和扫描页，核对印刷 p.21／PDF 第 4 页表 1、对象、十项转录、单位、六项算术、敏感性、归属、研究边界和发布文案。未完成者保留 `pending`，不能勾选通过。先启用经审核的公钥策略并生成新请求，最后由审阅者签名。
3. 在请求内填写与登记完全一致的身份、UTC 审阅时间、逐项检查和必要意见；只有全部完成才填写 `decision: approved`、`transcription_status: professionally_checked`、`attestation.status: signed`。使用固定命名空间签署该 JSON 的精确字节：

```bash
ssh-keygen -Y sign -f /private/path/reviewer_ed25519 -n chen-qingyun-scientific-review-v1 review-request.json
```

4. 维护者以实际文件执行导出，不能只检查 `approved` 字段：

```bash
python3 scripts/review_result.py export-reviewed \
  --run scratch/runs/new-run/run-manifest.json \
  --review /reviewed/path/review-request.json \
  --signature /reviewed/path/review-request.json.sig \
  --source-pdf /private/path/source.pdf --scan-page /private/path/table-page.png \
  --output scratch/reviewed/new-release
```

验证器核验已登记且未撤销的公钥、固定命名空间、精确签名字节、全项通过、时间、策略指纹、原文和扫描指纹；还重算固定结果并核对完整展示载荷。输入、任何被绑定代码、环境、完整结果或展示内容变化时，原签认失效，须重新运行和审阅。默认无审阅者策略下，此命令应拒绝且不生成审定产物。签名方式依据 [OpenSSH ssh-keygen](https://man.openbsd.org/ssh-keygen) 的 `-Y sign`／`-Y verify`。

审阅未通过时，可在请求副本保留原绑定，填写 `decision: rejected` 或 `insufficient_evidence`、具名身份、时间、范围和意见后独立归档；这两种决定均不能导出审定数据。当前尚无专门的负决定签名核验／登记命令，导出失败日志也不能代替具名否决记录。不要修改既有请求来抹去退回历史。

## 归档和发布

通过后单独导出 `reviewed-results.json`、研究记录 HTML、审阅 JSON 和签名；原候选仍保留。导出目录不直接进入 `site/`，须先完成网站集成评审。维护者应将完整运行目录、审阅记录、签名、策略版本和审定导出一起持久归档到受版本控制的研究记录／正式发布；受限原文只保留访问登记和指纹，私钥永不归档。Actions 30 天附件只供 CI 调试，不能充当永久科研档案。

这套门禁验证证据绑定与署名真实性，专业核校仍由已核实的人承担。单机有权限修改代码／策略的维护者不构成独立可信执行环境；正式发布须同时审查策略与代码变更，按固定提交重验。多任务授权、撤回公告、长期密钥轮换和生产前端消费仍属后续接入。
