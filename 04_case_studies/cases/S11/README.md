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

**样本说明：** `evidence/samples/` 已归档标杆 run `T190840` 的 prompt+completion 文本（digit / zero 塌缩；含 `api_response`）——供**阅读 / precision 核对**。本包归档 report 的 `prompt_token_ids` 为空（异步落盘后已清）；**不要**从 sample 字符串再 encode 当 tokenize 标杆。detect 见 [report_sample.json](./evidence/reports/report_sample.json)。通则见 [④ 名词表](../../README.md#名词怎么读先看这里)。

## 2 · 根因

对 [ascend#18798](https://github.com/vllm-project/vllm-ascend/pull/18798) 做逆修复：graph-pad 下把 cos/sin 的 **pad-tail** 喂给 query RoPE（本 pin 上 KV slice 保持正确）。不是 recycle（S10′）。禁止 NaN / fill。

## 3 · Guard 结果

**PASS。** 归档 **138 / 39 / 60**。

## 4 · 复现技巧

DeepSeek-V2-Lite；concurrent 48 变长英文 + 12 条 temp=0；util=0.40；不开 APC。

## 5 · 教学要点

pad-tail 错位 ≠ 回收块未清零。可能撞上同一个 detector，但 root-cause 不同；文本证据见 `evidence/reports/report_sample.json`。

## 定界分析

1. **现象与证据**——detector：`token_repeat` 命中（detect=60）。坏输出（digit / collapse）见 `evidence/samples/`；detect 以 `evidence/reports/` 为准。归档 report prompt 为空（异步落盘后已清）。
2. **排除（应做）**——空 prompt ≠ 不能做 KV 排除：同 prompt 再 curl 抓服务端 ids，与异常 `output_token_ids` 合并后抓标杆/异常 KV 对比（一致→排除 KV 再审 MLA RoPE；不一致→重开 KV）。**本案归档尚未附 KV 对比结论**。
3. **定界结论**——停在 **L2**（问题类 = MLA RoPE pad-tail / 间接 KV；≠S25）。**L1**：`token_repeat` 已检出。结案：PASS **138 / 39 / 60**。

## 证据文件

| 文件 | 用途 |
|------|------|
| `evidence/overlay.patch` | 制造异常的静态补丁 |
| `evidence/规格说明.md` | 复现规格（Origin / 锚点 / overlay / knobs / 期望 detector） |
| `evidence/三层计数.json` | 三层明细（trigger / precision / detect） |
| `evidence/跑批结果.json` | 跑批元数据 + 结案摘要 |
| `evidence/samples/` | 坏输出原文（prompt + completion；自 T190840） |
| `evidence/reports/` | Guard detector 报告（归档 report prompt 为空：异步落盘后已清；可读 prompt 看 samples，见 [④ 名词表](../../README.md#名词怎么读先看这里)） |


## 上游 PR 关系

| PR / 链接 | 角色 |
|-----------|------|
| [ascend#18798](https://github.com/vllm-project/vllm-ascend/pull/18798) | **根因修复**（MLA RoPE pad-tail）；本包做 soft-inverse |
