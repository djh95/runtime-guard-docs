# S10′ PASS 证据

- Overlay：强制 `needs_kv_cache_zeroing=False`，并在 `BlockPool.get_new_blocks` 打 trigger（逆 #39283 / #43741）。
- 负载：concurrent 64 变长英文 prompt + 16 条内容相同的 temp=0 wave；util=0.35；不开 APC。
- 三层：**65 / 20 / 79**（trigger / precision / detect）——`token_repeat` 报告在 `report/token_repeat/`。
- Run：`10_fullattn_recycle_zero-20261016T181551` @ 160 cards `4,5`。
- **本仓无 samples/**：`precision=20` 仅 layers 计数，非原文实锤；detect 以 report 为准。标杆为英文负载 `T181551`。
