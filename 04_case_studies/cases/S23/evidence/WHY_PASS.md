# S23 PASS evidence

- Overlay: **constructed** post-`load_model` zero of one layer `o_proj.weight` (always-on). No NaN/token-fill amplifiers.
- Model/load: Qwen3-8B, layer=15, temp=0, eager, concurrent 48; util=0.40; cards `10,11`.
- Layers: **2 / 17 / 48** (trigger / precision / detect) — precision = identical-mode collapse×17; detect = `token_repeat`×48.
- Distinct from KV/slot/sampler families; skills detect-only (no localization).
- Run: `23_weight_layer_corrupt-20261017T104359` @ 160.
