# S33 PASS — incomplete softcap

- 现行三层：**130 / 17 / 48**（`token_repeat`；detect=48 精确）。
- Overlay：softcap 做 `÷cap + tanh` 后跳过 `*cap` rescale；boot 强制 cap=30。
- 复现要点：**双树写入**（Ascend B + canonical vllm）+ 河名句 48 并发。
- 首轮盲跑：缺双树 / 用中文回声 → 对不上；二次盲跑对齐后 PASS。
- 与 S20（unstable overflow / `!!!!`）区分。
