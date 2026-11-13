# 同一CF₃中心：同一中心电子终态残差检查通过

**review_required；release_eligible=false。** 本轮实际执行一次原CF₃底物中心SCF，核梯度预约及调用均为0。任务号 `A01-M0-CF3-CENTER-TERMINAL-SCF-20261113-v1`。

内部能量目标保持1e-12 Eh，内部orbital目标由1e-9收紧至1e-10；最终平台要求仍为末次实际orbital范数≤1e-9。保留正常extra-cycle，不改PySCF判停、不追加SCF或Fock评估。原26原子完整精度Bohr坐标和原中心pre-center初猜均保持；不是以上轮B终态作新种子。

| 本轮实际结果 | 数值／状态 |
|---|---|
| 中心电子检查 | 同一中心电子终态残差检查通过 |
| 后端SCF收敛标志 | True |
| 全精度末次orbital范数 | 1.149604674925448e-10 |
| 最终验收门槛 | 1e-9 |
| 末次DFT总能，含核排斥及溶剂项／Eh | -1262.3124362190952 |
| 末次能量变化／Eh | 3.1832314562052488e-12 |
| 末次密度变化范数 | 2.0168325945868175e-10 |
| 电子数／AO数 | 154／319 |
| TIGHT_GRAD_CONV_TOL | True |
| 真实worker返回码 | 0 |
| 真实Linux控制器返回码 | 0 |
| 核梯度预约／调用 | 0／0 |

orbital范数是后端定义的电子轨道残差，不是核梯度Eh/bohr。末次ΔE与密度变化照实保存，不从内部配置推断末次ΔE必定≤1e-12，也不在运行后增添独立能量门槛。模型元数据保留的grid／auxbasis响应字段只是原模型信息，本轮没有计算或验证核梯度响应。实际软件身份与源码SHA在[公开摘要](public-summary.v1.json)及[证据索引](evidence-index.v1.json)登记；执行时提交号为null，后续归档／网页提交不冒充执行时提交。

原B主循环第4轮orbital范数9.689037768617906e-10，末次extra-cycle为1.6225317681152e-9，故旧B在核梯度前停止。本轮对照见[新旧中心对照](center-comparison.v1.json)。上述变化不证明随机误差、SCF为原Hessian误差根因或迭代次数不足。

## 执行与资源

实际开始UTC：2026-11-13T09:58:29.951558+00:00；结束UTC：2026-11-13T10:00:52.606549+00:00。时区展示采用Asia/Shanghai，对应开始2026-11-13T17:58:29.951558+08:00。共享600秒、单点480秒、最多1次SCF、核梯度0、单worker／4线程／4000MB软内存、max_cycle120的限额没有重置或延长。

真实worker process elapsed为142.09926652908325秒，即0.039472018480300901 worker小时；本批执行墙钟142.66218233108521秒。历史下界20.510794606053071小时加本轮真实经过后为至少 **20.550266624533371 worker小时**。这些不是CPU时间或完整历史总量，预算额度不当作已消耗。此前被中断的WSL transport权限等待未建立科学raw或预约，属于工程等待、新增量化0；本次实际过程独立计时。

实际SCF预约／启动／电子完整为1／1／1；核梯度预约／启动／完整均0。停止状态：`center_electronic_terminal_check_passed`；worker错误：`None`。真实过程与预算见[进程记录](public-evidence/process-result.v1.json)、[共享账本](public-evidence/budget.v1.json)，末次全精度值及迭代历史见[电子末次诊断](public-evidence/final-scf-diagnostics.v1.json)和[SCF原始日志](public-evidence/pyscf.log)。

## 保存数据复核与科学边界

[独立保存checkpoint复核](independent-checkpoint-review.v1.json)只读HDF5核总能、0／2占据、154电子、AO维度与坐标身份及指纹，新增量化0；不把这种保存数据复核称为独立量化复算或实验验证。[入口核验](entry-verification.v1.json)覆盖静态无核梯度路径、一次预约上限及CLI拒绝；合成标量与模拟检查不冒充真实DFT或native硬超时实测。

**中心电子检查通过不等于完整曲率通过，更不等于势垒验证。** 本轮没有中心核梯度、后四个位移、Hessian或频率，因此SCF精度对原互易误差的影响仍未知，原CF₃完整曲率资格仍未通过，根因仍未知，没有合格势垒排序。CH₃封存结果、旧矩阵／日志／结论及原作者归属保留。未检验轨道稳定性；不扩展体系、不自动开始后续量化。

本地完整证据包保存在本机本研究目录的 `review-bundle.v1.zip`，公开下载URL为null；checkpoint及seed仅本机保留。公开轻量机器摘要见[公开摘要](public-summary.v1.json)，证据指纹和本地包真实SHA见[证据索引](evidence-index.v1.json)。本地完整研究记录并不表示所有原始文件已上传GitHub。
