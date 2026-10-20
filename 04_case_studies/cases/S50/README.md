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

1. **L1 detect 停点**——detect：`logits_finite`。
2. **L2 class-hint**——L2 class-hint：SwiGLU gate/up 对调；≠S39。
3. **标杆 / Q1–Q5（KV 排除）**——空 prompt / 包内暂无 buggy+ref **不等于**「Q1–Q5 不适用」。有 report 即可：同 prompt 再 curl 抓服务端 `prompt_token_ids`，与异常 `output_token_ids` 合并后抓标杆 KV，对比异常 KV（一致→排除 KV；不一致→重开 KV 线）。**本案归档尚未附 KV 对比结论**；现行对外结案停在 L1+L2+现象。
4. **结合现象**——见 `evidence/samples/` · `evidence/reports/`。
5. **结案要点**——PASS **58 / 48 / 48**。

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
