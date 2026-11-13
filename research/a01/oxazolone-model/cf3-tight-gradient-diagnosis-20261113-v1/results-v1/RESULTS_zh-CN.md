# 同一M0 CF₃：收紧SCF后的中心梯度与两坐标诊断

`review_required`；`release_eligible=false`。仅分析真实保存数据；CH₃既有结果保留。

实际终态：`completed_five_point_diagnosis`；停止原因：`five_fixed_points_complete`。

| 点 | 实际状态 | 进程返回码 | 末次orbital范数 | 最大原子梯度 / Eh bohr⁻¹ |
|---|---|---:|---:|---:|
| center | complete_qualified_diagnostic_point | 0 | 5.94309346967e-11 | 2.36559350717e-05 |
| C6-y-plus | complete_qualified_diagnostic_point | 0 | 1.39784381378e-10 | 0.000170649079697 |
| C6-y-minus | complete_qualified_diagnostic_point | 0 | 1.07562983517e-10 | 0.000168310381048 |
| C10-y-plus | complete_qualified_diagnostic_point | 0 | 7.70850335738e-11 | 0.000190166890651 |
| C10-y-minus | complete_qualified_diagnostic_point | 0 | 1.77560614514e-10 | 0.000174075364251 |

末次实际orbital范数门槛仍为1e-9；中心梯度门槛仍为原子范数RMS≤3e-4、max≤4.5e-4 Eh/bohr。位移点不要求驻点。

| 两列互易见证 / Eh bohr⁻² | 旧A | 本轮tight |
|---|---:|---:|
| H₂₈,₁₆ | 0.00256417077031 | 0.00256407356162 |
| H₁₆,₂₈ | 0.00106527962999 | 0.00106631605112 |
| 互易差绝对值 | 0.00149889114032 | 0.00149775751051 |

新旧互易差有符号变化：-1.13362981301e-06 Eh/bohr²。
SCF精度对照判断：`no_resolved_change_at_declared_comparison_scale_does_not_exclude_SCF_effects`。

4e-5 Eh/bohr²仅为预先声明的同输入重复性误差传播对照尺度，不是统计显著性，也不放宽原绝对门槛1e-4及完整矩阵相对Frobenius门槛0.001。所有5点合格前不比较互易变化；少数列不能给出全矩阵残差或虚频数。FD1及对角FD2残差见JSON；FD2只作诊断。

本轮实际记录worker：1543.12943816秒；累计已记录worker下界：20.9789136907小时。失败与超时也计入，完整历史CPU时间仍未知。

根因尚未确定；局部精度敏感或未解析出变化均不能唯一归因。CF₃完整曲率与局部极小值资格未授予；不推进鞍点、IRC、势垒或机理解释。

保存数据、真实返回码、身份/指纹和账本对账见[summary.json](summary.json)。公开进展摘要为上一级public-summary.v1.json。
