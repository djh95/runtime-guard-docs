# S47 PASS — kv_swap

- Overlay：在 `reshape_and_cache` / FA 前 swap key/value。
- 与 S34 / S35 / S41 区分。
- 靠 `token_repeat` 检出（CJK / Trail 塌缩）。
- Run：`47_kv_swap-20261017T164919` @ 160 cards `10,11`。
- 三层：trigger=58 / precision=37 / detect=48。
