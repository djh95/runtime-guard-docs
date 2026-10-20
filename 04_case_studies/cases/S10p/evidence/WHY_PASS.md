# S10′ PASS 证据

- Overlay：强制 `needs_kv_cache_zeroing=False`，并在 `BlockPool.get_new_blocks` 打 trigger（逆 #39283 / #43741）。
- 负载：concurrent 64 变长英文 prompt + 16 条内容相同的 temp=0 wave；util=0.35；不开 APC。
- 三层：**65 / 20 / 79**（trigger / precision / detect）——`token_repeat` 报告在 `report/token_repeat/`。
- Run：`10_fullattn_recycle_zero-20261016T181551` @ 160 cards `4,5`。
- 第一次顺序中文 run 是假 precision（CJK 启发式）；不要把 `T180428` 当成 FAIL。
