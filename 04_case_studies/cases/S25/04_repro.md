# 4 · 复现（对齐本包）

第三方目标：按本包钉的 pin/模型/overlay 意图，**复现相近三层率与 detector 行为**，再判断 repro / detect / 定界。

与 S11 对照：同 RoPE 相关，root-cause 不同（half-drop vs pad-tail）。

- Pin：G2 f2aefd068
- 模型：Qwen3-8B
- Scenario dir（私有历史配方名）：`25_rope_siso_half_drop`
- 归档 run：25_rope_siso_half_drop-20261017T115523 @ 160 cards 4,5

**禁止：** force-NaN、token fill 等伪造症状（除非 SPEC 明确允许的 weight/scale 类构造且已写在本包）。

历史细节与满量 FE 仍在私有 `runtime-guard-test`；公开以本包为 **latest**。
