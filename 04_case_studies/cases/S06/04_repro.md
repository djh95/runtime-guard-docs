# 4 · 复现（对齐本包）

第三方目标：按本包钉的 pin/模型/overlay 意图，**复现相近三层率与 detector 行为**，再判断 repro / detect / 定界。

**历史 BLOCKED：** 部分栈 `aclnnAddRmsNormBias` 缺失或 MoE OOM — 见 `BLOCKED.historical.md`（setup，非 FAIL）。本包标杆是已跑通的 162 归档。

- Pin：G2 f2aefd068
- 模型：DeepSeek-V2-Lite
- Scenario dir（私有历史配方名）：`06_moe_routing_bias`
- 归档 run：06_moe_routing_bias-20261016T081459 @ 162 cards 0,1

**禁止：** force-NaN、token fill 等伪造症状（除非 SPEC 明确允许的 weight/scale 类构造且已写在本包）。

历史细节与满量 FE 仍在私有 `runtime-guard-test`；公开以本包为 **latest**。
