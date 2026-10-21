# S48 · Residual negate（PASS）

公开自洽案例包。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结果 | **PASS** |
| 三层率 | **100 / 48 / 48** |
| Detector | `logits_finite` |
| Origin | `both`（constructed） |
| Guard pin | G2 · `f2aefd068c4bd299d91cf0a1fdf642a3f327308f` |
| Run | 48_residual_negate-20261017T165947 @ builder 机 cards 8,9 |

## 1 · 现象

跨请求内容相同的 `!!!!`；`logits_finite`×48。

## 2 · 根因

fused add-RMSNorm 前 `residual = -residual`。不等于 S31 drop / S38 skip。

## 3 · Guard 结果

**PASS。** **100 / 48 / 48**。

## 4 · 复现技巧

Residual 极性案例。禁止 force-NaN / token fill。

## 5 · 教学要点

极性取反会走到 bang / NaN·Inf 路径，可被 `logits_finite` 抓住；要和 residual-drop 区分开。

## 定界分析

（**L1** = 检测停点 / **L2** = 问题类停点；**不是** Transformer 层号。见 [④ 名词表 · L1/L2](../../README.md#名词怎么读先看这里)。）

1. **现象与证据**——detector：`logits_finite`（`!!!!`）。现象见 `evidence/samples/` · `evidence/reports/`。归档 report prompt 为空（合修前旧归档；见名词表 **report 空 prompt**，非「clear 过早」）。
2. **排除（应做）**——重放抓 ids + 标杆/异常 KV 对比做排除。**本案例归档尚未附 KV 对比结论**。
3. **定界结论**——停在 **L2（问题类停点）**：residual 极性取反；≠S31/S38。**L1（检测停点）**：`logits_finite` 已命中。结案：PASS **100 / 48 / 48**。

## 证据文件

| 文件 | 用途 |
|------|------|
| `evidence/overlay.patch` | 制造异常的静态补丁 |
| `evidence/规格说明.md` | 复现规格（Origin / 锚点 / overlay / knobs / 期望 detector） |
| `evidence/三层计数.json` | 三层明细（trigger / precision / detect） |
| `evidence/跑批结果.json` | 跑批元数据 + 结案摘要 |
| `evidence/samples/` | prompt + completion 样本 |
| `evidence/reports/` | Guard detector 报告（归档 report prompt 为空：合修前旧归档，见名词表 **report 空 prompt**；可读 prompt 看 samples，见 [④ 名词表](../../README.md#名词怎么读先看这里)） |


## 上游 PR 关系

| PR / 链接 | 角色 |
|-----------|------|
| （constructed residual negate） | 无单一上游修复 PR |
