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

## 证据文件

| 文件 | 用途 |
|------|------|
| `evidence/status.json` | 结案摘要 |
| `evidence/layers.json` | 三层明细 |
| `evidence/samples/` | 样本 |
| `evidence/reports/` | logits_finite report |
| `evidence/overlay.patch` | overlay |
| `evidence/runtime_config.json` | 运行配置 |
| `evidence/SPEC_excerpt.md` | SPEC 摘录 |
| `evidence/WHY_PASS.md` | 为何 PASS |

## 上游 PR 关系

| PR / 链接 | 角色 |
|-----------|------|
| （constructed residual negate） | 无单一上游修复 PR |
