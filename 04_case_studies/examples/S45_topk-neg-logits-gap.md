# S45 · Top-k on −logits → unique garbage（GAP）

**现象：** **unique** 混合脚本垃圾（finite）；identical-mode 会低估 → layers.json `precision=0` 不可单独当「无 precision」。

**课：** 第三种漏检形态：unique garbage（相对 S01/S07 identical 汤）。

**完整个案（公开自洽）：** [cases/S45/](../cases/S45/) — external five-bar + evidence。
