# S43 PASS — embed_scale_blowup

- Overlay：`AscendVocabParallelEmbedding` lookup 后 `mul_(100)`。
- 与 S23 / S41 区分。
- 靠 `token_repeat` 检出（newline collapse）。
- Run：`43_embed_scale_blowup-20261017T153923` @ 160 cards `10,11`。
- 三层：trigger=16 / precision=40 / detect=48。
