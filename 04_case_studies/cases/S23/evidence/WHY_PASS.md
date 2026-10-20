# S23 PASS 证据

- Overlay：**constructed**——`load_model` 后置零一层 `o_proj.weight`（always-on）。无 NaN / token-fill 放大器。
- 模型 / 负载：Qwen3-8B，layer=15，temp=0，eager，concurrent 48；util=0.40；卡 `10,11`。
- 三层：**2 / 17 / 48**（trigger / precision / detect）——precision = identical-mode collapse×17；detect = `token_repeat`×48。
- 与 KV / slot / sampler 族区分；skills 侧是 detect-only（不定界）。
- Run：`23_weight_layer_corrupt-20261017T104359` @ 160。
