# S48 PASS — residual_negate

- Overlay：fused add-RMSNorm 前 `residual = -residual`。
- 不等于 S31 residual-drop，也不等于 S38 rmsnorm-skip。无 force-write。
- 靠 `logits_finite` 检出（全是 `!!!!`）。
- Run：`48_residual_negate-20261017T165947` @ 160 cards `8,9`。
