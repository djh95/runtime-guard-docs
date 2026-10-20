# S48 · Residual negate（PASS）

公开自洽案例包。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结果 | **PASS** |
| 三层率 | **100 / 48 / 48** |
| Detector | `logits_finite` |
| Origin | `both`（constructed） |
| Run | 48_residual_negate-20261017T165947 @ 160 cards 8,9 |

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

1. **L1 detect 停点**——detect：`logits_finite`（`!!!!`）。
2. **L2 class-hint**——L2 class-hint：residual 极性取反；≠S31/S38。
3. **标杆 / Q1–Q5（KV 排除）**——空 prompt / 包内暂无 buggy+ref **不等于**「Q1–Q5 不适用」。有 report 即可：同 prompt 再 curl 抓服务端 `prompt_token_ids`，与异常 `output_token_ids` 合并后抓标杆 KV，对比异常 KV（一致→排除 KV；不一致→重开 KV 线）。**本案归档尚未附 KV 对比结论**；现行对外结案停在 L1+L2+现象。
4. **结合现象**——见 `evidence/samples/` · `evidence/reports/`。
5. **结案要点**——PASS **100 / 48 / 48**。

## 证据文件

| 文件 | 用途 |
|------|------|
| `evidence/overlay.patch` | 制造异常的静态补丁 |
| `evidence/规格说明.md` | 复现规格（Origin / 锚点 / overlay / knobs / 期望 detector） |
| `evidence/三层计数.json` | 三层明细（trigger / precision / detect） |
| `evidence/跑批结果.json` | 跑批元数据 + 结案摘要 |
| `evidence/samples/` | prompt + completion 样本 |
| `evidence/reports/` | Guard detector 报告（归档 report prompt 为空：异步落盘后已清；可读 prompt 看 samples，见 [④ 名词表](../../README.md#名词怎么读先看这里)） |


## 上游 PR 关系

| PR / 链接 | 角色 |
|-----------|------|
| （constructed residual negate） | 无单一上游修复 PR |
