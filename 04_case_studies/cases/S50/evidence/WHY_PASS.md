# S50 PASS — swiglu_swap_halves

- Overlay：`cat(up, gate)` 再 `npu_swiglu`。不等于 S39。无 force-write。
- 靠 `logits_finite` 检出。
- Run：`50_swiglu_swap_halves-20261017T171204` @ 160 cards `12,13`。
