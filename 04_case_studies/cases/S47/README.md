# S47 · Attn K/V swap（PASS）

公开自洽案例包。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结果 | **PASS** |
| 三层率 | **58 / 37 / 48** |
| Detector | `token_repeat` |
| Origin | `both`（constructed） |
| Run | 47_kv_swap-20261017T164919 @ 160 cards 10,11 |

## 1 · 现象

CJK / Trail 塌缩；`token_repeat`×48。

## 2 · 根因

在 `reshape_and_cache` / FA 前 swap key/value。不等于 S34 / S35 / S41。

## 3 · Guard 结果

**PASS。** **58 / 37 / 48**。

## 4 · 复现技巧

Attn 算子 L2 的对外保留案例 代表（K/V swap）。

## 5 · 教学要点

本包归档真相是 **kv_swap**（Attn 前 K/V 对调）；短例文件名若仍写 `attn-qkv-out` 以本包为准。

## 定界分析

1. **L1 detect 停点**——detect：`token_repeat`（CJK / Trail 塌缩）。
2. **L2 class-hint**——L2 class-hint：Attn 前 K/V 对调；≠S34/S35/S41。
3. **标杆 / Q1–Q5（KV 排除）**——空 prompt / 包内暂无 buggy+ref **不等于**「Q1–Q5 不适用」。有 report 即可：同 prompt 再 curl 抓服务端 `prompt_token_ids`，与异常 `output_token_ids` 合并后抓标杆 KV，对比异常 KV（一致→排除 KV；不一致→重开 KV 线）。**本案归档尚未附 KV 对比结论**；现行对外结案停在 L1+L2+现象。
4. **结合现象**——见 `evidence/samples/` · `evidence/reports/`。
5. **结案要点**——PASS **58 / 37 / 48**。

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
| （constructed K/V swap） | 无单一上游修复 PR；Attn L2 代表 |
