# precision 是否中文误报？

对可见样本 `sample_01`（prompt=`用三句话介绍华为昇腾NPU与vLLM推理的关系。`）核对。

## 输出摘要

```
…
```

这是通顺中文说明文字，不是乱码。

## 旧启发式（把 CJK 算 weird）

- weird 字符数 / 长度 ≈ **0.000**（阈值 0.35）
- 旧逻辑会标 `garbage_mixed_script` → 与归档 precision_notes 一致
- **结论：对这篇散文，precision 是中文误报，不是乱码复现**

## 排除 CJK 后

- weird 比例 ≈ **0.000** → **不应**标 garbage
- 合理标签：普通中英混合 / 非 garbage

## 与三层率的关系

| 层 | 数 | 可信度 |
|----|---:|--------|
| trigger | 136 | 可信（触发日志在） |
| precision | 25 | **不可信**（CJK 误计；且对应 completion 未落盘） |
| detect | 0 | 可信（无 report） |

layers.json 的 precision_notes 列出的 `completion_*.json` **未随本包归档**；唯一可见样本即上文散文。
