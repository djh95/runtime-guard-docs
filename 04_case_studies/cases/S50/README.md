# S50 · SwiGLU gate/up half-swap（PASS）

公开自洽案例包。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结果 | **PASS** |
| 三层率 | **58 / 48 / 48** |
| Detector | `logits_finite` |
| Origin | `both`（constructed） |
| Guard pin | G2 · `f2aefd068c4bd299d91cf0a1fdf642a3f327308f` |
| Run | 50_swiglu_swap_halves-20261017T171204|

## 1 · 现象

跨请求内容相同的 `!!!!`；`logits_finite`×48。score 侧常见 `token0_collapse`×48。

## 2 · 根因

先 `cat(up, gate)` 再 `npu_swiglu`。不等于 S39 skip-silu。无 force-write。

## 3 · Guard 结果

**PASS。** **58 / 48 / 48**。

## 4 · 复现技巧

按本包 pin / overlay 对齐三层率。本包是 SwiGLU 算子问题类的对外保留代表（构造见「根因」）。

## 5 · 教学要点

bang / NaN·Inf 塌缩可被 `logits_finite` 抓住。对照 **S07**（有限 logits + 乱码 → FAIL+GAP）。**S01** 是 dense 复现未出现，不是「有限乱码漏检」样板。禁把「`!!!!` → 所以 gate/up 对调」写成定界推论。

## 定界分析

### 事实

- 现象：非有限 logits / 异常输出（`evidence/samples/`）。
- 三层见包内计数；detector：`logits_finite`。
- 归档 report：`prompt_token_ids` 为空；本轮 re-curl 合并后对比。
- 本包已归档 KV 对比（cos_thresh=0.99；n_prompt=14 n_cmp_tokens=14；layers=72）。
- 原 dump 条 `prompt_token_ids` 空；同 prompt re-curl 后与异常 `output_token_ids` 合并再抓标杆。
- 首不一致：idx=0 role=prompt span=prompt min_cos=n/a @ layer_36。
- 后续是否恢复≈1：False；output 首 token 余弦=n/a；仅 PD：False。

### 推断

- 对账不一致 → **重开 KV 线**。
- 坏输出仍不可直接写成具体根因。
- 首不一致在 prompt 段 → 偏向 prefill 侧（需结合是否恢复、仅 PD）。

### 结论

- 已定界到：KV 与标杆不一致（重开 KV 线）。
- 尚未定界到具体写/传路径；分析不出 / 证据不足。

## 证据文件

| 文件 | 用途 |
|------|------|
| `evidence/overlay.patch` | 制造异常的静态补丁 |
| `evidence/规格说明.md` | 复现规格（Origin / 锚点 / overlay / knobs / 期望 detector） |
| `evidence/三层计数.json` | 三层明细（trigger / precision / detect） |
| `evidence/跑批结果.json` | 跑批元数据 + 结案摘要 |
| `evidence/samples/` | prompt + completion 样本 |
| `evidence/reports/` | Guard detector 报告（归档 report prompt 为空：合修前旧归档，见名词表 **report 空 prompt**；可读 prompt 看 samples，见 [④ 名词表](../../README.md#名词怎么读先看这里)） |
| `evidence/kv_compare.json` | 最新 KV 标杆对比摘要（余弦 / 首不一致 / 结论） |


## 上游 PR 关系

| PR / 链接 | 角色 |
|-----------|------|
| （constructed SwiGLU half-swap） | 无单一上游修复 PR |
