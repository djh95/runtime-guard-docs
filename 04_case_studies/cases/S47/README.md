# S47 · Attn K/V swap（PASS）

公开自洽案例包。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结果 | **PASS** |
| 三层率 | **58 / 37 / 48** |
| Detector | `token_repeat` |
| Origin | `both`（constructed） |
| Guard pin | G2 · `f2aefd068c4bd299d91cf0a1fdf642a3f327308f` |
| Run | 47_kv_swap-20261017T164919 @ builder 机 cards 10,11 |

## 1 · 现象

CJK / Trail 塌缩；`token_repeat`×48。

## 2 · 根因

在 `reshape_and_cache` / FA 前 swap key/value。不等于 S34 / S35 / S41。

## 3 · Guard 结果

**PASS。** **58 / 37 / 48**。

## 4 · 复现技巧

按本包 pin / overlay 对齐三层率。本包是 Attn 算子问题类（K/V swap）的对外保留代表（构造见「根因」）。

## 5 · 教学要点

本包归档真相是 **kv_swap**（Attn 前 K/V 对调）；短例文件名若仍写 `attn-qkv-out` 以本包为准。禁把「CJK 塌缩 → 所以 K/V 对调」写成定界推论。

## 定界分析

### 事实

- 现象：CJK / Trail 塌缩（`evidence/samples/`）。
- 三层：58 / 37 / 48；detector：`token_repeat`×48。
- 归档 report：`prompt_token_ids` 为空；有 `output_token_ids`。
- 尚未做 KV 对比（未抓标杆/异常 KV 或未写入本包）。

### 推断

- 可确认：塌缩异常已出现，且 `token_repeat` 已检出。
- 坏输出推不出「Attn 前 K/V 对调」——构造见「根因」。
- 无对账事实 → 推不出污染时机。

### 结论

- 已定界到：塌缩异常 + `token_repeat` 检出。
- 尚未定界到 K/V 对调；分析不出 / 证据不足。

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
| （constructed K/V swap） | 无单一上游修复 PR；Attn 类代表 |
