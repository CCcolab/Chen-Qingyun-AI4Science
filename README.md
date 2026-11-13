# 陈庆云院士科学成就的 AI 辅助研究

本平台围绕陈庆云院士及合作者的科学研究，以原始文献、数据和具体问题为依据，运用 AI 辅助核读、结构与对象消歧、数值复算、竞争解释比较和未来研究设计。

[学术成就网站](https://cccolab.github.io/Chen-Qingyun-AI4Science/) · [全氟酮化学早期研究专题](https://cccolab.github.io/Chen-Qingyun-AI4Science/topics/early-fluoroketones/index.html) · [A01 研究记录](research/a01/README.md) · [研究路线图](docs/RESEARCH_ROADMAP_zh-CN.md)

## 研究目标

- **复现**：重建原研究的问题、对象、观察与论证；对有完整数据和方法的结果开展独立复算。
- **验证**：比较可检验的竞争解释，通过适当的计算、对照和不确定性分析，研究原结论的适用范围。
- **拓展**：从原始证据和已有研究的缺口出发，提出可证伪的新问题，经查新和专业研究后推进。

## 当前重点：全氟酮化学早期研究

“六氟丙酮反应与六氟双酚A（双酚AF）制备”按原始出处分为三个独立研究分支：

1. [双酚AF制备记录与计量重建](research/a01/bisphenol-af-yield/README.md)：核对说明书数字与计量假设，保留未解释残差，不称实验复现。
2. [含氟衍生物物性复核](research/a01/molar-refraction/README.md)：复核指定论文的折射性质，不移用为双酚AF结构或性能验证。
3. [噁唑酮反应性模型](research/a01/oxazolone-model/README.md)：限定同一CF₃／CH₃—苯胺／苯模型，逐项核查现代量化证据。

本轮在同一M0的CF₃底物参照完成中心核梯度及C6-y／C10-y四个位移，五点均取得合格电子终态与完整核梯度。两列互易差仍为`0.0014977575105072183 Eh/bohr²`，约为原绝对门槛的14.98倍；相对旧A的有符号变化为`−1.1336298130141913e-6 Eh/bohr²`，小于预先声明的`4e-5`对照尺度。本次未解析出局部互易差的SCF精度影响，不能据此排除SCF或其他数值因素。

一阶能量／梯度差分对照两列通过；对角二阶FD2中C6-y未达诊断容差、C10-y通过，未通过项继续保留。少数列不能授予CF₃完整曲率或局部极小值资格，尚不能解释原文反应性差异，也不作势垒或机理认定。实际结果见[A01公开进展v2](research/a01/public-progress.v2.json)及[本轮报告](research/a01/oxazolone-model/cf3-tight-gradient-diagnosis-20261113-v1/results-v1/RESULTS_zh-CN.md)；[原v1记录](research/a01/public-progress.v1.json)保留，全部保持`review_required`、`release_eligible=false`。

已有 PF1966-UV-T1 工作属于三种碘代物溶剂位移的原表数值重放，保持待审；不作为光谱实验复现或机理验证。

## 研究边界

已发表成果保留原作者与合作团队归属。平台的新分析、复算和未来假设单独标识，并保留可核对的来源与研究条件。

AI 辅助分析不能替代原始材料和专业判断。原表数值重放、量化计算、实验验证与未来假设分别记录；尚未开展的工作不写为已完成，未经充分查新的设想不称首次发现。
