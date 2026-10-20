# S25 · RoPE second-half drop（PASS · PR-rooted）

公开自洽案例包。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结果 | **PASS** |
| 三层率 | **348 / 17 / 48**（二次盲跑对齐后现行；detect=48 精确） |
| Detector | `token_repeat`（**threshold=8**） |
| Origin | `ascend-only` |
| Guard pin | G2 f2aefd068 |
| 模型 | Qwen3-8B |
| Run | 二次盲跑对齐（河名句 + 48 并发 + 阈值 8） |

## 1 · 现象

输出塌成 `1.1.1…` / `1.0.0…` 复读；`token_repeat`×48。样本见 [evidence/samples/](./evidence/samples/)。

## 2 · 根因

Soft-inverse [ascend#7082](https://github.com/vllm-project/vllm-ascend/pull/7082)：`npu_rotary_embedding` 后恢复未旋转的后半维（缺 store 语义）。不等于 S11 的 pad 长度问题。

## 3 · Guard 结果

**PASS。** 现行 **348 / 17 / 48**。

## 4 · 复现配方（必读）

`1.1.1…` 塌缩**只在**下列配方下稳定出现：

| 项 | 正确（照这个做） |
|----|------------------|
| Overlay | `gen_s25_overlay.py` 就地改 B 树 |
| Prompt | `Name one famous river. One short English sentence. id={i}.` |
| 并发 | **48 并发**（勿串行 8 条） |
| 其它 | `max_tokens=48`；temp=0 |
| detector | `token_repeat` **threshold=8**（勿用 16） |

首轮盲跑曾记「FAIL detect=0」——**不是**检测器漏检 /「特征佯差」，而是**配方错了**：用了中文回声 + 串行 8 请求 + threshold 16。对齐上表后二次盲跑 → **348 / 17 / 48** PASS（detect=48 精确）。

脚本：`s25_concurrent_repro.py`、`gen_s25_overlay.py`。

## 5 · 别人按包能核对什么

写 RoPE 案例要写清「不等于 S11」。负载配方错了，结论也会错——无塌缩时 detect=0 不要写成漏检。
