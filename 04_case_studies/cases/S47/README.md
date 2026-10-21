# S47 · Attn K/V swap（PASS）

公开自洽案例包。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结果 | **PASS** |
| 三层率 | **58 / 37 / 48** |
| Detector | `token_repeat` |
| Origin | `both`（constructed） |
| Run | 47_kv_swap-20261017T164919 @ builder 机 cards 10,11 |

## 1 · 现象

CJK / Trail 塌缩；`token_repeat`×48。

## 2 · 根因

在 `reshape_and_cache` / FA 前 swap key/value。不等于 S34 / S35 / S41。

## 3 · Guard 结果

**PASS。** **58 / 37 / 48**。

## 4 · 复现技巧

Attn 算子问题类（定界 **L2**）的对外保留案例代表（K/V swap）。

## 5 · 教学要点

本包归档真相是 **kv_swap**（Attn 前 K/V 对调）；短例文件名若仍写 `attn-qkv-out` 以本包为准。

## 定界分析

（**L1** = 检测停点 / **L2** = 问题类停点；**不是** Transformer 层号。见 [④ 名词表 · L1/L2](../../README.md#名词怎么读先看这里)。）

1. **现象与证据**——detector：`token_repeat`（CJK / Trail 塌缩）。现象见 `evidence/samples/` · `evidence/reports/`。归档 report prompt 为空（合修前旧归档；见名词表 **report 空 prompt**，非「clear 过早」）。
2. **排除（应做）**——重放抓 ids + 标杆/异常 KV 对比做排除。**本案归档尚未附 KV 对比结论**。
3. **定界结论**——停在 **L2（问题类停点）**：Attn 前 K/V 对调；≠S34/S35/S41。**L1（检测停点）**：`token_repeat` 已命中。结案：PASS **58 / 37 / 48**。

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
