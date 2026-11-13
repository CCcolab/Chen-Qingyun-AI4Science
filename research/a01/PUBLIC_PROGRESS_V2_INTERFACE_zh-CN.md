# A01五点精度诊断：公开进展v2

本版只消费同一M0的CF₃底物中心核梯度和C6-y／C10-y四个位移的实际保存结果。它属于噁唑酮反应性支线，不属于双酚AF合成机制验证。状态固定为`review_required`、`release_eligible=false`，不产生审定科学结果。

原[public-progress.v1.json](public-progress.v1.json)、原中心电子试验记录、原阶段历史与原网页修订保持字节不变。v2不回写这些历史资料。正式切换后，`public-progress.current.json`明确指向`public-progress.v2.json`及网页修订链；尚未切换时，共用检查器继续解析v1。

## 实际结果绑定

`execution.result_source`指定本轮科学目录中的`public-summary.v1.json`及实际SHA-256。`diagnosis`逐字段保存该源的五点、旧A／原v3／本轮tight两列、互易比较、科学资格、真实返回码及源指纹；`execution.resources`保留实际账本。网页可见区块和内嵌JSON必须与这些字段一致，不能只改显示值。

内部SCF目标仍为能量`1e-12 Eh`、orbital `1e-10`、最多120周期；验收读取正常extra-cycle后的真实末次orbital范数，要求`≤1e-9`。中心原子梯度门槛为RMS`≤3e-4`、最大范数`≤4.5e-4 Eh/bohr`。位移点不要求驻点；它们须具有正确身份、完整核梯度、合格末次电子残差及真实成功进程退出。未完成和未执行项保留`null`及实际状态，不以0代替。

两列的互易对照单位为`Eh/bohr²`，步长为`0.0005 bohr`。原绝对门槛`1e-4`和完整矩阵相对Frobenius门槛`0.001`均保留。`4e-5`只用于声明过的重复性传播对照，不代表统计显著性，也不是放宽后的合格门槛。五点未全部合格时，精度影响结论保持未知。五点全部合格后，仅按实际局部互易差的变化陈述精度敏感性；无论变化与否，均不唯一确定误差根因。

`scientific_qualification`保持无新完整Hessian、无完整相对残差、无新频率和虚频数、无CF₃局部极小值资格、无鞍点／IRC／势垒／机理认证。CH₃既有结果保留，不用局部tight列拼接旧完整矩阵。

## 累计资源与身份

本批上限为3000秒共享墙钟、每点480秒、最多5次SCF与5次核梯度预约、单worker、4线程；中心合格后还须符合原合同的四个位移整段准入条件。预算不是实际消耗。累计下界从此前`20.55026662453337 worker小时`追加真实worker经过；失败和超时也计入，完整历史和CPU时间仍未知。

执行提交身份保持`null`；实际源码用SHA-256绑定。若运行标识由任务ID与控制器实际开始epoch派生，保留`run_id_role`，不将派生标识冒充控制器原生字段。UTC与北京时间表示同一实际时刻。后补归档提交不代替运行时身份。

## S3证据与S4网页

1. 科学目录完成实际归档及`PUBLIC_FILES.v1.json`，公开文件逐项核对实际SHA和字节。checkpoint、二进制梯度／密度、原始ZIP及本机测试不分发。
2. S3新增科学证据与不含固定提交URL的v2进展。旧v1仍是网页现行入口，因此S3构建不必改动旧网页；CI同时核对现行v1页面和新v2保存数据，后者暂允许归档提交为空。
3. 取得S3完整提交号后，S4将新证据URL固定到S3，再生成静态专题区块和`a01-site-revision.v2.json`。最后新增current登记；登记只存路径，不循环记录自身摘要或自身未来提交。
4. 修订校验从原YouMind基线依次应用v1、v2的old→new声明，核对历史链条，再将最终期望值与实际当前HTML比对。原基线和原ZIP的硬编码SHA不变。

本轮只更新现有专题HTML。原首页及成果页保持v1字节；PFtB正文、两份原JSON、51个来源身份、15个HTML路由及`.nojekyll`发布范围保留。研究JSON继续是仓库资料，专题以静态HTML与内嵌数据消费，浏览器不从研究目录拉取新JSON。

生成和检查命令只读取保存资料，不启动电子结构计算或模型API：

```text
python scripts/build_a01_public_progress_v2.py --science-root <实际科学项目目录>
python scripts/check_a01_progress.py --data research/a01/public-progress.v2.json --data-only --allow-unlinked
# 建立真实S3提交后：
python scripts/build_a01_public_progress_v2.py --science-root <同一目录> --archive-commit <S3完整SHA> --replace
python scripts/render_a01_progress.py --data research/a01/public-progress.v2.json --write
python scripts/make_a01_site_revision_v2.py --evidence-commit <S3完整SHA>
python scripts/check_a01_progress.py
```

成功的资料一致性检查只说明公开记录、证据与网页相符；科学失败或未完整阶段也应如实归档。它不授予科学资格，不统计本机未分发的单测。
