# S11 PASS evidence

- Overlay: inverse ascend#18798 — synth graph-pad rows on prefill cos/sin when needed, apply **pad-tail** for query RoPE (KV slice kept correct on this pin). No NaN/fill amplifiers.
- Model/load: DeepSeek-V2-Lite MLA, bf16, concurrent 48 var-len EN + 12 temp=0 wave; util=0.40; no APC; cards `4,5`.
- Layers: **138 / 39 / 60** (trigger / precision / detect) — `token_repeat`.
- Run: `11_mla_rope_pad-20261016T190840` @ 160.
- Samples: digit/collapse junk (`1010…`, `_1000…`); wave2 temp=0 divergence.
- Prior `T190524` (fp16 + KV pad-tail) crashed gather dtype EZ1001 — not FAIL; query-only + bf16 fixed.
