# S25 · RoPE second-half drop（PASS · PR-rooted）

公开自洽案例包。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结果 | **PASS**（以 160 concurrent 标杆为准） |
| 三层率 | **462 / 15 / 48** |
| Detector | `token_repeat`（threshold 与 160 对齐时用 8） |
| Origin | `ascend-only` |
| Guard pin | G2 f2aefd068 |
| 模型 | Qwen3-8B |
| Run | 25_rope_siso_half_drop-20261017T115523 @ 160 cards 4,5 |

## 1 · 现象

输出塌成 `1.1.1…` / `1.0.0…` 复读；`token_repeat`×48。样本见 [evidence/samples/](./evidence/samples/)。

## 2 · 根因

Soft-inverse [ascend#7082](https://github.com/vllm-project/vllm-ascend/pull/7082)：`npu_rotary_embedding` 后恢复未旋转的后半维（缺 store 语义）。不等于 S11 的 pad 长度问题。

## 3 · Guard 结果

**PASS。** 归档 **462 / 15 / 48**。

## 4 · 复现：160 成功配方 vs 162 失败配方

别人要复现 PASS，必须对齐 **160 成功配方**，不要用 162 那套短检负载。

| | **160 成功（照这个做）** | **162 曾失败（不要照这个定 FAIL）** |
|--|--------------------------|--------------------------------------|
| Overlay | `gen_s25_overlay.py` **就地改 B 树** | 对静态 patch `git -C B apply` |
| 负载 | **48 并发**；prompt=`Name one famous river. One short English sentence. id={i}.`；`max_tokens=48`；temp=0 | **8 条串行**中英「内存管理」回声；varlen 关 |
| detector | `token_repeat` **threshold=8** | threshold=16（更严） |
| 期望输出特征 | `1.1.1…` / `1.0.0…` 数字塌缩 | 正常中文回声 / 英文释义；**无数字塌缩** |
| layers 印象 | ≈466/15/48 | 高 trigger、detect=0；precision 易被 CJK 误报抬高 |

要点：162 上 trigger 上千只说明 overlay 挂上了；**没有目标塌缩特征时，detect=0 不能写成「检测器漏检」**。先对齐 160 concurrent 河名句再比 detect。

脚本参考（同 pin 复现脚本）：`s25_concurrent_repro.py`、`gen_s25_overlay.py`。

## 5 · 别人按包能核对什么

写 RoPE 案例要写清「不等于 S11」，避免技能表混类。负载配方错了，结论也会错。
