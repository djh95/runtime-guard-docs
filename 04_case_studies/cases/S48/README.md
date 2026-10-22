# S48 · Residual negate（KV 不一致→定界）

公开自洽案例包。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案 | **KV 不一致→定界** |
| 检测 | **检出** |
| 三层率 | **100 / 48 / 48** |
| Detector | `logits_finite` |
| Origin | `both`（constructed） |
| Guard pin | G2 · `f2aefd068c4bd299d91cf0a1fdf642a3f327308f` |
| Run | 48_residual_negate-20261017T165947|

## 1 · 现象

跨请求内容相同的 `!!!!`；`logits_finite`×48。

## 2 · 根因

fused add-RMSNorm 前 `residual = -residual`。不等于 S31 drop / S38 skip。

## 3 · Guard 结果

**检出。** **100 / 48 / 48**。结案档：**KV 不一致→定界**。

## 4 · 复现技巧

Residual 极性案例。禁止 force-NaN / token fill。

## 定界分析

### 事实

- 现象：非有限 logits / 异常输出（`evidence/samples/`）。
- 三层见包内计数；detector：`logits_finite`。
- 本包已归档 KV 对比（cos_thresh=0.99；n_prompt=14 n_cmp_tokens=14；layers=72）。
- 首不一致：idx=0 role=prompt span=prompt min_cos=n/a @ layer_36。
- 后续是否恢复≈1：False；output 首 token 余弦=n/a；仅 PD：False。

### 推断

- 对账不一致 → **重开 KV 线**。
- 坏输出仍不可直接写成具体根因。
- 首不一致在 prompt 段 → 偏向 prefill 侧（需结合是否恢复、仅 PD）。

### 结论

- 结案档：**KV 不一致→定界**（重开 KV 线）。
- 尚未定界到具体写/传路径；分析不出 / 证据不足。

## 证据文件

| 文件 | 用途 |
|------|------|
| `evidence/overlay.patch` | 制造异常的静态补丁 |
| `evidence/规格说明.md` | 复现规格（Origin / 锚点 / overlay / knobs / 期望 detector） |
| `evidence/三层计数.json` | 三层明细（trigger / precision / detect） |
| `evidence/跑批结果.json` | 跑批元数据 + 结案摘要 |
| `evidence/samples/` | prompt + completion 样本 |
| `evidence/reports/` | Guard detector 报告 |
| `evidence/kv_compare.json` | 最新 KV 标杆对比摘要（余弦 / 首不一致 / 结论） |

## 上游 PR 关系

| PR / 链接 | 角色 |
|-----------|------|
| （constructed residual negate） | 无单一上游修复 PR |
