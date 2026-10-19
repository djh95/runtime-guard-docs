# S06 PASS evidence (skills offline archive)

- Overlay: MoE routing bias / topk→0 family (`06_moe_routing_bias`).
- Run: `anomaly-origin-20261016/06_moe_routing_bias-20261016T081459` on **162** cards `0,1`, DeepSeek-V2-Lite.
- Layers (status): trigger **70** / precision **1** / detect report present (`token_repeat`×1 archived).
- Skills: `token_repeat` detect; score labels `mixed_script`+`repeat`; `verify_request_kv` may PASS (KV finite ≠ clear MoE class).
- Note: prior `BLOCKED.md` was setup-era (CANN/OOM) and is superseded — see `BLOCKED.historical.md`.
