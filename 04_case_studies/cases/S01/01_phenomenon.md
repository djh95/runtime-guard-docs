# 1 · 现象

**对外可读症状：** 服务仍 200、logits 有限，但 completion 可能是乱码 / 混合脚本「汤」，或（在错误评分下）被记成 garbage。

**本包归档可见样本**（[evidence/sample_01.json](./evidence/sample_01.json)）实际是通顺中英散文（华为 NPU / vLLM 介绍），**不是**汤。现网 scorer 会标 `mixed_script`，不会标 `garbage_mixed_script`。

**为何仍写进个案：**  
归档 `status.json` 记了 `precision_hits=25` 与一串 `garbage_mixed_script:completion_*.json` 文件名，但那些 completion **未随 FE 落盘**；唯一可见样本是散文。个案要教的是：

1. **有限垃圾是 detector 类缺口**（≠ NaN、≠ 复读窗）；  
2. **当时 precision 计数不可直接当「汤已复现」铁证**（见 [04](./04_repro_then_vs_now.md)）。

**对照：** 真·混合脚本汤见同缺口族 **S07**（本公开仓仅短例）；同大类能检的是 **S10′** recycle-zero。
