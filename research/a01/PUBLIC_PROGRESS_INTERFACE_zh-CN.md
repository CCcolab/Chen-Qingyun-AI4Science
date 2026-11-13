# A01公开研究进展接口

`public-progress.v1.json`公开实际研究阶段及其证据，状态固定为`review_required`、`release_eligible=false`。公开范围由[本阶段进展合同](public-progress-contract.v1.json)登记。它与PF1966-UV-T1的`results/website-candidate.json`分开，不生成该接口的审定发布产物。科学计算失败或执行前阻塞也可如实公开，CI绿灯只表示资料与页面一致，不表示科学终态成功。

## 身份、数值与未知项

- `execution.task_id/run_id`标识任务与实际运行；时间同时保存UTC和`Asia/Shanghai`。`execution.execution_commit`保持未知值`null`，实际运行源码使用`code_sha256`绑定。后补的证据或网页提交不能冒充运行提交。
- `execution.result_source`指向已提交的实际`public-summary.v1.json`及其SHA-256。公开字段必须与该源逐字段一致，不能只修改网页显示值。
- `execution.result.orbital_norm`是正常extra-cycle之后的实际末次电子轨道残差。内部配置`conv_tol_grad=1e-10`不保证末次通过；平台最终要求仍为`≤1e-9`。能量变化与密度变化如实保存，不追加新的末次能量验收门槛。
- 核梯度调用和预约为已知的0；未计算的核梯度、位移、完整Hessian、频率与势垒不能以数值0表示。未知数值使用`null`并说明原因。
- `execution.resources`区分本批实际worker经过、历史已记录下界和完整历史／CPU未知量。计划额度不计作实际消耗，失败过程也追加真实经过时间。
- `qualifications`分开记录中心电子终态、完整曲率及DFT势垒；中心通过不会修改CF₃完整曲率未合格、SCF对互易误差影响未知或根因未知的状态。CH₃保留此前受限模型内的条件性局部极小数值支持。

## 原始归属与三个分支

`branches`保留三条独立成果支线、稳定来源ID和原作者登记顺序：双酚AF制备记录与计量重建、含氟衍生物物性复核、噁唑酮反应性模型。本轮仅属于第三支线的现代离线计算，不验证双酚AF制备机制，不宣称实验复现、机理确认或首次发现。

原文核读范围为1960年133卷p.1113–1116、134卷p.1367–1370的AI阅读；另行重读过相关首页和第117491号的一页说明书。完整专业核译／结构转录签认仍待补；授予正页未取得，不由现有说明书补写1959授予落款。

## 固定证据与两次提交

S1归档协议、执行代码、轻量输入／实际结果、阶段摘要和证据索引。S1版本的`evidence_archive_commit`及固定URL暂为`null`。取得S1完整SHA后，S2填入`evidence_archive_commit=S1`，`evidence[].fixed_url`必须指向`https://github.com/CCcolab/Chen-Qingyun-AI4Science/blob/<S1>/<path>`。不在文件中循环写入自身提交号。

2026年11月12—13日的公开阶段摘要见[STAGE_HISTORY_20261113_zh-CN.md](STAGE_HISTORY_20261113_zh-CN.md)和[机器索引](stage-history.v1.json)。没有随当前公开提交分发的旧本机报告只登记其原路径、SHA与字节，不能给出虚假的GitHub blob链接。原始大包没有公开下载时，`raw_archive.download_url=null`并说明本机保留；轻量公开证据单独列明。

## 网页消费

[`scripts/render_a01_progress.py`](../../scripts/render_a01_progress.py)把该JSON生成专题内的静态HTML，浏览器无JavaScript时仍可读。页面保留`A01_PUBLIC_PROGRESS_BEGIN/END`标记及同一数据的`application/json#a01-public-progress`；校验器检查嵌入数据、实际源JSON SHA与完整可见区块一致。它不是在浏览器端从研究目录请求文件。

JSON仍位于研究目录，Pages保持原15个HTML、两份既有JSON和`.nojekyll`的明确发布范围。原YouMind导出指纹与来源基线保留，授权页面变更通过独立A01修订清单登记。PFtB正文、两份原JSON及51条来源不因本接口变化而放宽。

```text
python scripts/build_a01_public_progress.py --science-root <实际本机科学项目目录>
python scripts/build_a01_public_progress.py --science-root <同一目录> --archive-commit <S1完整SHA> --replace
python scripts/render_a01_progress.py --write
python scripts/check_a01_progress.py
```

上述生成／检查只读保存的科学结果，不启动DFT或模型API。构建器拒绝无意覆盖，`--replace`用于明确的S2固定链接版本。`tests/`和`test/`遵守本机保留、不向GitHub重新分发的政策。
