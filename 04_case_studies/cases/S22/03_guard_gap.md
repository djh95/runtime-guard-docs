# 3 · Guard 结果

**判定：PASS**

分布性课：主 detector 是 **`spec_acceptance`**，不是 logits_finite。

| 层 | 归档 |
|----|------|
| trigger / precision / detect | **130 / 45 / 48** |
| 期望 detector | spec_acceptance（主）+ token_repeat |

证据文件见 `evidence/`（WHY / layers / samples / overlay 摘录）。
