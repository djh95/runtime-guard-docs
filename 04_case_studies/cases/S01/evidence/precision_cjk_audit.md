# precision 是否中文误报？

对 160 复判样本（prompt=`用三句话介绍华为昇腾NPU与vLLM推理的关系。`，run `20261020T101951`）核对。

## 输出摘要

通顺中文 + 少量英文专名（华为昇腾 NPU / vLLM），不是乱码。见 [samples/](./samples/)。

## 旧启发式（把 CJK 算 weird）

- weird / 长度 ≈ **0.86**（阈值 0.35）→ 会标 `garbage_mixed_script`
- 24/24 样本全部命中 → 与 runner 自报 precision≈25 同病
- **结论：precision 虚高，是中文误报，不是乱码复现**

## 排除 CJK 后

- weird 比例 ≈ **0.0** → **不应**标 garbage
- 合理标签：普通中英混合
- 复判记 **precision_hits=0**

## 与三层率的关系

| 层 | 旧归档 | 复判（CJK 排除） | 可信度 |
|----|------:|----------------:|--------|
| trigger | 136 | 154 | 可信（触发日志在） |
| precision | 25 | **0** | 旧数不可信 |
| detect | 0 | 0 | 可信（无 report） |
