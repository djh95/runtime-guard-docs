# S10′ PASS evidence

- Overlay: force `needs_kv_cache_zeroing=False` + `BlockPool.get_new_blocks` triggers (inverse #39283/#43741).
- Load: concurrent 64 var-len English prompts + 16 identical temp=0 wave; util=0.35; no APC.
- Layers: **65 / 20 / 79** (trigger / precision / detect) — `token_repeat` reports under `report/token_repeat/`.
- Run: `10_fullattn_recycle_zero-20261016T181551` @ 160 cards `4,5`.
- First sequential Chinese run was false precision (CJK heuristic); do not use `T180428` as FAIL.
