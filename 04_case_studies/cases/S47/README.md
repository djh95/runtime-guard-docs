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

- 三层：58 / 37 / 48；detector：`token_repeat`（CJK / Trail 塌缩；`evidence/samples/` · `evidence/reports/`）。
- 归档 report `prompt_token_ids` 为空；有 `output_token_ids`。
- 包内无标杆 vs 异常 KV 对账结果。

### 推断

- 可确认：塌缩异常且 `token_repeat` 已检出。
- 坏输出推不出「Attn 前 K/V 对调」；KV 排除路径可用，包内未附 → **定界分析不出** 该算子细因（§2 非定界已证）。

### 结论

- 已定界到：塌缩异常 + `token_repeat` 检出。
- **尚未定界到** K/V 对调；**分析不出 / 证据不足**。
- KV：路径可用；归档尚未附结论。
- **定界结论：L1** = `token_repeat` 已命中；**L2** = 证据不足。
- 结案：PASS **58 / 37 / 48**。


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
| （constructed K/V swap） | 无单一上游修复 PR；Attn L2 代表 |
