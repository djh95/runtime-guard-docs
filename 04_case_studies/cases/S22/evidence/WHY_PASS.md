# S22 PASS 证据

- Overlay：origin 路径——G2 pin 本身已缺 `RESAMPLE_NOISE_SALT`（#18657）；overlay 只在 residual resample 入口打 trigger 日志。无 NaN / token-fill 放大器。
- 模型 / 负载：Qwen3-8B + eagle3，temp=0.8，num_spec=3，eager / util=0.40；concurrent 48。
- 三层（二次盲跑现行）：**126 / 0 / 47**——detect 主靠 `spec_acceptance`。
- 首轮盲跑 blocker：CRLF vs LF patch 上下文对不上（PATCH_FAIL）；锚点脚本 / ignore-whitespace 修复后 PASS 复现。
- 与 S05（NaN argmax）、S20（softcap overflow）区分。
