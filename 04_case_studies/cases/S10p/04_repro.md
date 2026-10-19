# 4 · 复现（对齐本包）

第三方目标：按本包钉的 pin/模型/overlay 意图，**复现相近三层率与 detector 行为**，再判断 repro / detect / 定界。

Overlay：force `needs_kv_cache_zeroing=False` + `BlockPool.get_new_blocks` triggers。Load：concurrent 64 var-len EN + 16 identical temp=0；util=0.35；no APC。

**Caveat：** 更早顺序中文 run（`T180428`）曾假 precision（CJK 启发式）— **不要**当标杆；标杆是 `T181551` 英文负载。

- Pin：G2 f2aefd068
- 模型：Qwen3-8B（English concurrent load；见 status）
- Scenario dir（私有历史配方名）：`10_fullattn_recycle_zero`
- 归档 run：10_fullattn_recycle_zero-20261016T181551 @ 160 cards 4,5

**禁止：** force-NaN、token fill 等伪造症状（除非 SPEC 明确允许的 weight/scale 类构造且已写在本包）。

历史细节与满量 FE 仍在私有 `runtime-guard-test`；公开以本包为 **latest**。
