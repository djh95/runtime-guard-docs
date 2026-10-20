# S22 PASS 证据

- Overlay：origin 路径——G2 pin 本身已缺 `RESAMPLE_NOISE_SALT`（#18657）；overlay 只在 residual resample 入口打 trigger 日志。无 NaN / token-fill 放大器。
- 模型 / 负载：Qwen3-8B + eagle3，temp=0.8，num_spec=3，eager / util=0.40；concurrent 48；卡 `4,5`。
- 三层：**130 / 45 / 48**（trigger / precision / detect）——precision 侧是 `spec_acceptance` 开火（acceptance_rate 0.0–0.27，mean ~0.07）；detect = 45 条 `spec_acceptance` + 3 条 `token_repeat`。
- 与 S05（NaN argmax / uniform 0）、S20（softcap overflow）区分。
- Run：`22_spec_resample_rng_collide-20261017T101553` @ 160。
