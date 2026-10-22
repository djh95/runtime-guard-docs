# S26 · RMSNorm fp32 weight-mul（PASS · PR-rooted）

公开自洽案例包。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结果 | **PASS** |
| 三层率 | **354 / 16 / 48**（现行；detect=48/48；trigger/precision 随并发浮动，detect 为判定口径） |
| Detector | `token_repeat`（**threshold=8**） |
| Origin | `both` |
| Guard pin | G2 f2aefd068 |
| 模型 | Qwen3-8B |
| Run | 与 S25 同技巧 |

## 1 · 现象

输出变成反复的数字串（如 `1.1.1…`）；`token_repeat`×48。样本见 [evidence/samples/](./evidence/samples/)。

## 2 · 根因

Soft-inverse [vLLM#42379](https://github.com/vllm-project/vllm/pull/42379)：`AscendRMSNorm.forward_oot` 用 fp32-mul 再 cast（错误公式）。属 dtype/cast 问题类（构造已知；定界须另有对账事实）。

## 3 · Guard 结果

**PASS。** 现行 **354 / 16 / 48**。

## 4 · 复现技巧（必读）

与 S25 **同一现行复现**——负载形状决定能不能打出 `1.1.1…`：

| 项 | 现行复现（照这个做） |
|----|----------------------|
| Overlay | `gen_s26_overlay.py` 就地改 B |
| Prompt | `Name one famous river. One short English sentence. id={i}.`（英文河名短句） |
| 并发 | **48 路同时发请求** |
| 其它 | `max_tokens=48`；temp=0 |
| detector | `token_repeat` **threshold=8** |
| 脚本 | `s26_concurrent_repro.py`、`gen_s26_overlay.py` |

**历史错跑（不要照这个结案）：** 曾用「中文回声式」prompt、大约 **8 条串行**请求、阈值 **16** → 往往打不出数字复读、detect=0。这是复现条件不对，不是漏检。勿用强制写 NaN 伪造症状。

## 定界分析

### 事实

- 现象：`1.1.1…` 复读（`evidence/samples/`）。
- 三层见包内计数；detector：`token_repeat`。
- 归档 report：`prompt_token_ids` 为空；本轮 re-curl 合并后对比。
- 本包已归档 KV 对比（cos_thresh=0.99；n_prompt=14 n_cmp_tokens=20；layers=72）。
- 原 dump 条 `prompt_token_ids` 空；同 prompt re-curl 后与异常 `output_token_ids` 合并再抓标杆。
- 首不一致：idx=12 role=prompt span=prompt min_cos=0.153994 @ layer_69。
- 后续是否恢复≈1：False；output 首 token 余弦=0.562271；仅 PD：False。

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
| [vLLM#42379](https://github.com/vllm-project/vllm/pull/42379) | **根因修复**；本包 soft-inverse（按上游修复反向注入） |
