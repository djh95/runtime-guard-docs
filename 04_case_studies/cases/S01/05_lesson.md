# 5 · 课（给读者带走的）

1. **有限垃圾是缺口，不是「没异常」。** `logits_finite` 只管 NaN/Inf；汤可以全程有限。  
2. **Trigger ≠ precision ≠ detect。** 本例 136 触发、0 检出；中间「25」还被评分污染。  
3. **同大类对照 S10′：** recycle-zero 能被 `token_repeat` 抓住；skip-zero→有限垃圾这边漏 — 定界时不要只用一个 detector 叙事。  
4. **Origin-faithful：** 不要用强制写 NaN / 填复读 token 造症状；dense+synth 证明路径 ≠ 证明脏读汤。  
5. **文档纪律：** 公开个案要么 **写全**（本包），要么 **删掉**；禁止只留「全文见私有 test」的空壳页。

## 下一步（产品，非本包范围）

Detector GAP 记录：garbled-text / cross-request-identical（S01/S07 族）。实现另开，不在本公开包内承诺时间表。
