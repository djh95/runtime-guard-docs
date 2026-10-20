# S26 · RMSNorm fp32 weight-mul（PASS · PR-rooted）

公开自洽案例包。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结果 | **PASS** |
| 三层率 | **354 / 16 / 48**（现行；detect=48/48） |
| Detector | `token_repeat`（**threshold=8**） |
| Origin | `both` |
| Guard pin | G2 f2aefd068 |
| 模型 | Qwen3-8B |
| Run | 与 S25 同技巧 |

## 1 · 现象

`1.1.1…` 复读塌缩；`token_repeat`×48。样本见 [evidence/samples/](./evidence/samples/)。

## 2 · 根因

Soft-inverse [vLLM#42379](https://github.com/vllm-project/vllm/pull/42379)：`AscendRMSNorm.forward_oot` 用 fp32-mul 再 cast（错误公式）。属 L2 dtype/cast 类。

## 3 · Guard 结果

**PASS。** 现行 **354 / 16 / 48**。

## 4 · 复现技巧（必读）

与 S25 **同一技巧**——负载形状决定能不能打出目标特征：

| 项 | 正确（照这个做） |
|----|------------------|
| Overlay | `gen_s26_overlay.py` 就地改 B |
| Prompt | `Name one famous river. One short English sentence. id={i}.` |
| 并发 | **48 并发** |
| 其它 | `max_tokens=48`；temp=0 |
| detector | `token_repeat` **threshold=8** |

勿用：中文回声 / 串行 8 / 阈值 16。禁止 force-NaN。脚本：`s26_concurrent_repro.py`、`gen_s26_overlay.py`。

## 5 · 教学要点

对外保留案例里 RMSNorm 的 PR-rooted 代表。复现时先对齐 48 并发河名句 + threshold 8，再谈 PASS/FAIL。

## 定界分析

1. **L1 detect 停点**——detect：`token_repeat`×48（threshold=8）。
2. **L2 class-hint**——L2 class-hint：RMSNorm dtype（fp32-mul）；≠S25/S31。
3. **标杆 / Q1–Q5（KV 排除）**——空 prompt / 包内暂无 buggy+ref **不等于**「Q1–Q5 不适用」。有 report 即可：同 prompt 再 curl 抓服务端 `prompt_token_ids`，与异常 `output_token_ids` 合并后抓标杆 KV，对比异常 KV（一致→排除 KV；不一致→重开 KV 线）。**本案归档尚未附 KV 对比结论**；现行对外结案停在 L1+L2+现象。
4. **结合现象**——见 `evidence/samples/` · `evidence/reports/`。
5. **结案要点**——PASS **354 / 16 / 48**；复现技巧同 S25。

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
| [vLLM#42379](https://github.com/vllm-project/vllm/pull/42379) | **根因修复**；本包 soft-inverse |
