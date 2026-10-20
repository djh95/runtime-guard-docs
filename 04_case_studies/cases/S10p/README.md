# S10′ · FullAttn recycle-zero（PASS）

公开自洽个案包。漏检对照：[S01](../S01/)。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结果 | **PASS** |
| 三层率 | **65 / 20 / 79** |
| Detector | `token_repeat` |
| Origin | `both` |
| Guard pin | G2 f2aefd068 |
| 模型 | Qwen3-8B（英文并发负载） |
| Run | 10_fullattn_recycle_zero-20261016T181551 @ 160 cards 4,5 |

## 1 · 现象

输出塌成短语复读或一串 `xxxx`。`token_repeat` 命中很多（detect 79 / 80 请求）。样本见 [evidence/samples/](./evidence/samples/)（若有）与 layers。

## 2 · 根因

FullAttention 不进 `needs_kv_cache_zeroing` 管线，回收 block 时 partial-tail 仍带脏 K/V（[#39283](https://github.com/vllm-project/vllm/pull/39283)、[#43741](https://github.com/vllm-project/vllm/pull/43741)）。

对照 S01：S01 是进了 zeroer 再 skip；S10′ 是 FullAttn **从来不进** zeroing。

## 3 · Guard 结果

**PASS。** 期望 `token_repeat`。归档 **65 / 20 / 79**。

## 4 · 复现

Overlay：强制 `needs_kv_cache_zeroing=False`，在 `BlockPool.get_new_blocks` 打 trigger。负载：concurrent 64 变长英文 + 16 条 identical temp=0；util=0.35；不开 APC。

**注意：** 更早顺序中文 run（`T180428`）曾假 precision（CJK 启发式）——不要当标杆。标杆是 `T181551` 英文负载。

## 5 · 教学要点

同大类 KV 脏读：**S10′ 能检**（recycle），**S01 漏检**（skip-zero→有限垃圾）。定界时不要只讲一个 detector。
