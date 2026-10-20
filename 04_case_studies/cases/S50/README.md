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
| （constructed SwiGLU half-swap） | 无单一上游修复 PR |
