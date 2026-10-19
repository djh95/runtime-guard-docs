# S48 PASS 100/48/48 residual_negate

- Overlay: residual=-residual before fused add-RMSNorm.
- ≠ S31 residual-drop ≠ S38 rmsnorm-skip. No force-write.
- Detect via logits_finite (all !!!!).
- Run: 48_residual_negate-20261017T165947 @ 160 cards 8,9.
