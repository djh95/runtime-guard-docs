# S11 · MLA RoPE pad-tail（PASS）

公开自洽案例包。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结果 | **PASS** |
| 三层率 | **138 / 39 / 60** |
| Detector | `token_repeat` |
| Origin | `ascend-only` |
| Guard pin | G2 f2aefd068 |
| 模型 | DeepSeek-V2-Lite MLA bf16 |
| Run | 11_mla_rope_pad-20261016T190840 @ 160 cards 4,5 |

## 1 · 现象

常见 digit / collapse 垃圾（如 `1010…`）。`token_repeat` 命中 60/60。

## 2 · 根因

对 [ascend#18798](https://github.com/vllm-project/vllm-ascend/pull/18798) 做逆修复：graph-pad 下把 cos/sin 的 **pad-tail** 喂给 query RoPE（本 pin 上 KV slice 保持正确）。不是 recycle（S10′）。禁止 NaN / fill。

## 3 · Guard 结果

**PASS。** 归档 **138 / 39 / 60**。

## 4 · 复现技巧

DeepSeek-V2-Lite；concurrent 48 变长英文 + 12 条 temp=0；util=0.40；不开 APC。

## 5 · 教学要点

pad-tail 错位 ≠ 回收块未清零。可能撞上同一个 detector，但 root-cause 不同；文本证据见 `evidence/reports/report_sample.json`。

## 定界分析

1. **L1 detect 停点**——detect：`token_repeat` 命中（detect=60）。
2. **L2 class-hint**——L2 class-hint：MLA RoPE pad-tail（间接 KV）；不等于 S25。
3. **标杆 / Q1–Q5**——无 buggy+ref 标杆 → Q1–Q5 不适用 / KV=未知。
4. **结合现象**——无 prompt+completion 样本；detect 以 `evidence/reports/` 为准。
5. **结案要点**——PASS **138 / 39 / 60**。本仓无 `samples/`：precision 仅计数。

## 证据文件

| 文件 | 用途 |
|------|------|
| `evidence/overlay.patch` | 制造异常的静态补丁 |
| `evidence/规格说明.md` | 复现规格（Origin / 锚点 / overlay / knobs / 期望 detector） |
| `evidence/三层计数.json` | 三层明细（trigger / precision / detect） |
| `evidence/跑批结果.json` | 跑批元数据 + 结案摘要 |
| `evidence/samples/` | （无）precision 仅三层计数，见 README 定界节 |
| `evidence/reports/` | Guard detector 报告 |


## 上游 PR 关系

| PR / 链接 | 角色 |
|-----------|------|
| [ascend#18798](https://github.com/vllm-project/vllm-ascend/pull/18798) | **根因修复**（MLA RoPE pad-tail）；本包做 soft-inverse |
