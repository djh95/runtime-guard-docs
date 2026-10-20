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

跨请求 identical 的 `!!!!`；`logits_finite`×48。

## 2 · 根因

fused add-RMSNorm 前 `residual = -residual`。不等于 S31 drop / S38 skip。

## 3 · Guard 结果

**PASS。** **100 / 48 / 48**。

## 4 · 复现

Residual 极性案例。禁止 force-NaN / token fill。

## 5 · 学完能做什么

极性错误会走到 bang / NaN·Inf 路径；要和 residual-drop 区分开。
