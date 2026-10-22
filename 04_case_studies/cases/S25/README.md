# S25 · RoPE second-half drop（PASS · PR-rooted）

公开自洽案例包。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结果 | **PASS** |
| 三层率 | **348 / 17 / 48**（现行；detect=48/48；trigger/precision 随并发浮动，detect 为判定口径） |
| Detector | `token_repeat`（**threshold=8**） |
| Origin | `ascend-only` |
| Guard pin | G2 f2aefd068 |
| 模型 | Qwen3-8B |
| Run | 河名句 + 48 并发 + 阈值 8 |

## 1 · 现象

输出塌成 `1.1.1…` / `1.0.0…` 复读；`token_repeat`×48。样本见 [evidence/samples/](./evidence/samples/)。

## 2 · 根因

Soft-inverse [ascend#7082](https://github.com/vllm-project/vllm-ascend/pull/7082)：`npu_rotary_embedding` 后恢复未旋转的后半维（缺 store 语义）。不等于 S11 的 pad 长度问题。

## 3 · Guard 结果

**PASS。** 现行 **348 / 17 / 48**。

## 4 · 复现技巧（必读）

`1.1.1…` 塌缩**只在**下列技巧下稳定出现：

| 项 | 正确（照这个做） |
|----|------------------|
| Overlay | `gen_s25_overlay.py` 就地改 B 树 |
| Prompt | `Name one famous river. One short English sentence. id={i}.` |
| 并发 | **48 并发**（勿串行 8 条） |
| 其它 | `max_tokens=48`；temp=0 |
| detector | `token_repeat` **threshold=8**（勿用 16） |

勿用：中文回声 / 串行 8 / 阈值 16（会无塌缩、detect=0，属错跑法，不是漏检）。

脚本：`s25_concurrent_repro.py`、`gen_s25_overlay.py`。

## 5 · 教学要点

写 RoPE 案例要写清「不等于 S11」。负载技巧错了，结论也会错——无塌缩时 detect=0 不要写成漏检。

## 定界分析

### 事实

- 现象：`1.1.1…` 复读（`evidence/samples/`）。
- 三层：462 / 15 / 48；detector：`token_repeat`×48。
- 归档 report：`prompt_token_ids` 为空（合修前）；本轮对比用非空 ids 的异常 dump（len prompt=14）。
- builder 机 KV 对比（cos_thresh=0.99；n_prompt=14 n_cmp_tokens=20；layers=72）。
- 标杆 vs 异常：对比窗口**全程一致**（min-over-layers cos ≥ thresh）；output 首 token 余弦=0.999993。
- 首不一致：无。

### 推断

- 对账一致 → **排除 KV cache** 作为本请求坏输出的必要原因。
- 坏输出仍不能从文本推出构造根因；转向非 KV 类（见案例背景/构造）。
- 无首不一致 → 推不出污染时机窗口。

### 结论

- 已定界到：可排除 KV cache（本请求对比窗口）。
- 尚未定界到具体算子/构造根因；分析不出 / 证据不足。

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
| [ascend#7082](https://github.com/vllm-project/vllm-ascend/pull/7082) | **根因修复**；本包 soft-inverse |
