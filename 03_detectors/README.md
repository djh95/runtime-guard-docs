# ③ 检测算法总览

每个 detector **单独成文**，便于算法演进时只改一页。全部默认 `enabled: false`。

## 一览

| Detector | 阶段 | 典型现象 | 文档 |
|----------|------|----------|------|
| `token_repeat` | after sample | 复读 / 局部卡词 | [token_repeat.md](./token_repeat.md) |
| `logits_finite` | before sample | NaN/Inf logits | [logits_finite.md](./logits_finite.md) |
| `spec_acceptance` | after spec | Spec 接受率/长度异常 | [spec_acceptance.md](./spec_acceptance.md) |

源码目录：  
https://github.com/vllm-project/vllm-ascend/tree/main/vllm_ascend/observability/runtime_guard/detector

注册表：  
https://github.com/vllm-project/vllm-ascend/blob/main/vllm_ascend/observability/runtime_config/detector_catalog.py

配置字段总表：  
https://github.com/vllm-project/vllm-ascend/blob/main/docs/source/user_guide/configuration/runtime_config.md

相关 PR：

| 说明 | URL |
|------|-----|
| 检测器基础框架合入 PR | https://github.com/vllm-project/vllm-ascend/pull/16849 |
| 性能与鲁棒增强 PR | https://github.com/vllm-project/vllm-ascend/pull/18644 |

## 公共约定

- **命中动作**由 `on_trigger` 控制，默认含 `report`；需要现场时加 `dump_kv`。  
- **报告**只在 last-PP TP0；**dump** 在 last-PP×全部 TP。  
- 达到 `report.max_per_req` 阈值后，**当前这一条请求停止继续检测**，不影响其他请求。  
- 尚未正式合入的配置项（例如旧文档提到的 `token_logprob` / `slot_consistency`），**请勿在配置中启用，该类检测器并未生效**。

## 选用建议（一线）

```text
现象不清 / 偶发复读 → 先 token_repeat（最轻）
怀疑数值炸 / 乱码 → 加 logits_finite
开了 MTP/Eagle 且接受率离谱 → 再开 spec_acceptance
类未定 → 可同时开已合入项做 sweep（先 dump 关，只 report）
```

> 提示：同时开启多个检测器仅建议用于临时排障 sweep；检测器开启会引入 CPU 开销，性能敏感业务排查完成后及时关闭不需要的检测器。

定界流程见 [../02_problem_localization/README.md](../02_problem_localization/README.md)。
