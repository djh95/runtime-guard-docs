# S11 PASS 证据

- Overlay：逆 ascend#18798——必要时在 prefill cos/sin 上合成 graph-pad 行，并对 query RoPE 使用 **pad-tail**（本 pin 上 KV slice 保持正确）。无 NaN / fill 放大器。
- 模型 / 负载：DeepSeek-V2-Lite MLA，bf16；concurrent 48 变长英文 + 12 条 temp=0 wave；util=0.40；不开 APC；卡 `4,5`。
- 三层：**138 / 39 / 60**（trigger / precision / detect）——`token_repeat`。
- Run：`11_mla_rope_pad-20261016T190840` @ 160。
- 样本：digit / collapse junk（`1010…`、`_1000…`）；wave2 temp=0 有 divergence。
- 更早的 `T190524`（fp16 + KV pad-tail）曾因 gather dtype EZ1001 崩溃——那不是 FAIL；改为 query-only + bf16 后修好。
