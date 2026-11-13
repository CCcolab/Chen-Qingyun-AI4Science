# A01阶段记录：2026年11月12—13日

全部为 `review_required`，`release_eligible=false`。本页公开阶段摘要；不回写旧报告，不将后补归档提交冒充执行时提交。原始本机报告按路径、SHA-256和字节登记；未分发的原件及原始包不生成下载URL。

<a id="qualification-20261112"></a>
## 2026-11-12｜参照态与驻点资格审计

核清12.511659／29.531754 kcal/mol是非驻点选定几何相对各自底物＋苯胺的单点电子能差，不构成合格DFT势垒；两侧停止结构不构成收敛终态。

原报告路径：`research/a01/qualification-20261112/REPORT_zh-CN.md`。SHA-256：`442818b538f64ea36209d808690f2b54a1b12efda6585bdf1d76ab6f7eefb56d`；8172字节。

<a id="t1-continuation-20261112"></a>
## 2026-11-12｜同层T1探针与分离参照

选定T1仅为非驻点能量／梯度探针；苯胺在受限模型内取得条件性局部极小数值支持，两侧底物参照继续精修。未得到DFT势垒或正式IRC。

原报告路径：`research/a01/oxazolone-model/t1-continuation-20261112/REPORT_zh-CN.md`。SHA-256：`830c37cfb3343d5a5366981d1ba3998799776f692ced913aa874489a733b456d`；13077字节。

<a id="reference-continuation-20261112-v2"></a>
## 2026-11-12｜两侧底物参照续算

CH₃优化与独立梯度通过；CF₃最后完整第18点仍未合格，第19点SCF中断。停止来自单项2400秒SIGALRM，不是7200秒累计期限；该阶段完整曲率未运行。

原报告路径：`research/a01/oxazolone-model/reference-continuation-20261112-v2/REPORT_zh-CN.md`。SHA-256：`231b299797ab2cab62d14cc67593892f9dde1a28aaccbbaea4fb9da8784bb2d2`；6806字节。

<a id="reference-curvature-20261113-v3"></a>
## 2026-11-13｜两侧完整曲率

两侧各157完整梯度和78列、72振动模齐全，诊断谱均0虚频。CH₃通过既定数值一致性检查，支持该受限模型内局部极小；CF₃最大反对称0.0014988913693417868 Eh/bohr²未通过，不能以零虚频补足资格。

原报告路径：`research/a01/oxazolone-model/reference-curvature-20261113-v3/REPORT_zh-CN.md`。SHA-256：`bc5348c2ad13a2b4afe7648c554ef2bc4e94197506ddc62a14cec9f3c4e0760c`；8312字节。

<a id="point-diagnosis-execution-20261113-v1"></a>
## 2026-11-13｜CF₃局部A／B点诊断

A五点重复性通过，互易差0.0014988911403202325 Eh/bohr²。B中心主循环第4轮orbital范数9.689037768617906e-10，末次额外检查1.6225317681152e-9，核梯度前停止；后四点未执行，SCF精度对互易误差的影响未知。

原报告路径：`research/a01/oxazolone-model/cf3-point-diagnosis-execution-20261113-v1/REPORT_zh-CN.md`。SHA-256：`4a041b2a10b630172b949b09e3fb59f129b79bb784ad074917a0ae2e7582eb3f`；6604字节。

<a id="A01-M0-CF3-CENTER-TERMINAL-SCF-20261113-v1"></a>
## 2026-11-13｜中心电子终态残差检查

同一中心电子终态残差检查通过。本轮核梯度调用0；中心结果不提升CF₃完整曲率或势垒资格。

原报告路径：`research/a01/oxazolone-model/cf3-center-terminal-scf-20261113-v1/REPORT_zh-CN.md`。SHA-256：`87230c18ee350108357df3083e4bda03ee1cf228bc9636528c70560af235cfe9`；4529字节。

[机器可读阶段索引](stage-history.v1.json)。各阶段原作者归属及三分支边界见[现行登记](branches.v2.json)。
