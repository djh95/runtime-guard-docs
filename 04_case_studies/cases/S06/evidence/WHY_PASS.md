# S06 PASS 证据（skills offline archive）

- Overlay：MoE routing bias / topk→0 族（`06_moe_routing_bias`）。
- Run：`anomaly-origin-20261016/06_moe_routing_bias-20261016T081459`，机器 **162**，卡 `0,1`，模型 DeepSeek-V2-Lite。
- 三层（status）：trigger **70** / precision **1** / detect 有归档报告（`token_repeat`×1）。
- Skills：`token_repeat` 检出；score 标签含 `mixed_script` + `repeat`；`verify_request_kv` 可能仍 PASS（KV finite ≠ 清 MoE 类）。
- 说明：更早的 `BLOCKED.md` 是 setup 时代产物，已被本归档取代——历史细节见 `BLOCKED.historical.md`。
