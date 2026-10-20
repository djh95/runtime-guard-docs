# S50 · SwiGLU gate/up half-swap（PASS）

公开自洽案例包。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结果 | **PASS** |
| 三层率 | **58 / 48 / 48** |
| Detector | `logits_finite` |
| Origin | `both`（constructed） |
| Run | 50_swiglu_swap_halves-20261017T171204 @ 160 cards 12,13 |

## 1 · 现象

跨请求内容相同的 `!!!!`；`logits_finite`×48。score 侧常见 `token0_collapse`×48。

## 2 · 根因

先 `cat(up, gate)` 再 `npu_swiglu`。不等于 S39 skip-silu。无 force-write。

## 3 · Guard 结果

**PASS。** **58 / 48 / 48**。

## 4 · 复现技巧

SwiGLU 算子 L2 代表。

## 5 · 教学要点

bang / NaN·Inf 塌缩可被 `logits_finite` 抓住。对照 **S07**（有限 logits + 乱码 → FAIL+GAP）。**S01** 是 dense 复现未出现，不是「有限乱码漏检」样板。

## 定界分析

1. **现象与证据**——detector：`logits_finite`。现象见 `evidence/samples/` · `evidence/reports/`（跨请求内容相同的 `!!!!`）。归档 report prompt 为空（异步落盘后已清）。
2. **排除（应做）**——重放抓 ids + 标杆/异常 KV 对比做排除。**本案归档尚未附 KV 对比结论**。
3. **定界结论**——停在 **L2**（问题类 = SwiGLU gate/up 对调；≠S39）。**L1**：`logits_finite` 已检出。结案：PASS **58 / 48 / 48**。

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
| （constructed SwiGLU half-swap） | 无单一上游修复 PR |
