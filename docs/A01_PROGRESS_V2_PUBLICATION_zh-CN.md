# A01五点精度诊断的阶段公开

本次公开范围是同一M0 CF₃底物的中心核梯度及C6-y／C10-y四个位移，用来判断局部互易差对SCF精度设置的响应。实际计算状态、成功与失败点、停止原因、全精度互易值和累计资源以新科学目录的`public-summary.v1.json`及公开证据为准。发布代码只读取这些结果，不启动计算。

新接口合同为`research/a01/public-progress-contract.v2.json`，接口细则见[公开进展v2说明](../research/a01/PUBLIC_PROGRESS_V2_INTERFACE_zh-CN.md)。现行版本通过`research/a01/public-progress.current.json`选择。原v1 JSON、原v1网页修订、原阶段索引和原分支登记保持字节不变；新网页修订按原基线→v1→v2衔接，不刷新原YouMind基线。

S3先归档实际科学证据与未绑定归档提交号的新进展；S4再将公开链接固定到S3，并更新专题静态内容、内嵌JSON和独立修订清单。运行源码以实际SHA绑定，后补提交不冒充执行时提交；current登记及修订文件均不记录自身未来提交，避免循环身份。

网页仍沿用YouMind主题，只更换现有A01研究区块。五点表展示末次orbital残差、最大原子梯度和真实退出码；互易表并列旧A与tight结果。源证据详情保持默认折叠，未计算的完整曲率、相对Frobenius残差和虚频数不以0显示。两列局部结果即使落在原绝对门槛内，也不改判CF₃完整曲率或局部极小值资格；CH₃既有结果保留。

CI与Pages继续调用共用的一致性检查及构建命令，执行量化计算数和分发单测数均为0。构建产物仍只有原15个HTML、两份原JSON和`.nojekyll`；研究数据与原始大包不随Pages发布。上线后需核对固定部署版本、内嵌任务／运行身份、`review_required`、`release_eligible=false`以及固定S3证据的实际响应字节。
