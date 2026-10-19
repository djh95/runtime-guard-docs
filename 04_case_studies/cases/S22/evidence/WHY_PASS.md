# S22 PASS evidence

- Overlay: **origin** — G2 pin already lacks `RESAMPLE_NOISE_SALT` (#18657); overlay only arms trigger logs on residual resample entry. No NaN / token-fill amplifiers.
- Model/load: Qwen3-8B + eagle3, temp=0.8, num_spec=3, eager/util=0.40; concurrent 48; cards `4,5`.
- Layers: **130 / 45 / 48** (trigger / precision / detect) — precision = `spec_acceptance` fires (acceptance_rate 0.0–0.27, mean ~0.07); detect = 45 `spec_acceptance` + 3 `token_repeat`.
- Distinct from S05 (NaN argmax / uniform 0) and S20 (softcap overflow).
- Run: `22_spec_resample_rng_collide-20261017T101553` @ 160.
