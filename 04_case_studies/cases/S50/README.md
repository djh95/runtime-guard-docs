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

跨请求 identical 的 `!!!!`；`logits_finite`×48。score 侧常见 `token0_collapse`×48。

## 2 · 根因

先 `cat(up, gate)` 再 `npu_swiglu`。不等于 S39 skip-silu。无 force-write。

## 3 · Guard 结果

**PASS。** **58 / 48 / 48**。

## 4 · 复现

SwiGLU 算子 L2 代表。

## 5 · 别人按包能核对什么

bang / NaN·Inf 塌缩可被 `logits_finite` 抓住——对照 S01/S07：那边 logits（采样前的分值）始终有限、无 NaN/Inf，文字却仍是乱码，故漏检。
