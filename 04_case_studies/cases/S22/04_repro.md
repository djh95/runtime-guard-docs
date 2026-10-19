# 4 · 复现（对齐本包）

第三方目标：按本包钉的 pin/模型/overlay 意图，**复现相近三层率与 detector 行为**，再判断 repro / detect / 定界。

eager/util=0.40；concurrent 48。

- Pin：G2 f2aefd068（已缺 RESAMPLE_NOISE_SALT）
- 模型：Qwen3-8B + eagle3，temp=0.8，num_spec=3
- Scenario dir（私有历史配方名）：`22_spec_resample_rng_collide`
- 归档 run：22_spec_resample_rng_collide-20261017T101553 @ 160 cards 4,5

**禁止：** force-NaN、token fill 等伪造症状（除非 SPEC 明确允许的 weight/scale 类构造且已写在本包）。

历史细节与满量 FE 仍在私有 `runtime-guard-test`；公开以本包为 **latest**。
