---
name: runtime-guard-ref-kv-dump
description: >-
  Capture a reference KV dump via runtime_guard dump_kv (same token IDs as the
  buggy report) and compare against the buggy kv_cache dir for precision
  localization: first-divergence tables + interpret Q1–Q5. Use after
  verify_request_kv PASS. Native dump_kv only; no msprobe.
---

# Reference KV via native dump_kv

前置：`verify_request_kv` PASS；report 含 `prompt_token_ids` / `output_token_ids`（需 `report.save_sensitive_info: true`）。  
脚本：`PYTHONPATH=$RG_TEST python -m analysis.scripts.<name>`（见 [../README.md](../README.md)）。  
定界口径对齐手册 [02 §5](../../02_problem_localization.md)。

## 为何 force-feed token ids

1. Prefill / decode 路径不同 — 标杆尽量同路径类。  
2. 字符串重 tokenize ≠ report token ids。  
3. 禁止让标杆自行 greedy 生成。

## 抓 ref

```bash
PYTHONPATH="$RG_TEST" python -m analysis.scripts.prepare_ref_inputs \
  --report <report_*.json> --out ref_inputs.json
```

1. 起 **清洁** 服务：同模型 / 同拓扑 / **同 MODE**（勿 eager↔graph 当对照）。  
2. `runtime_config_hot_reload=true`；arm `manual_trigger` 的 `dump_kv`，或 `dump.manual_dump` 水位。  
3. Force-feed：

```bash
PYTHONPATH="$RG_TEST" python -m analysis.scripts.request_from_report \
  --report <report_*.json> \
  --url http://127.0.0.1:8000/v1/completions \
  --model <served-model-name>
# 默认 --feed=history → prompt + output[:-1]
```

也可用 `ref_inputs.json` 的 `force_feed_token_ids` 走 Python token-id API。  
4. 可选三趟：`--feed history` / 再喂最后一 token / `--feed full`。  
5. 收集：`runtime/report/kv_cache/<type>/<ref_req_id>/wave_N/<rank_tag>/`。

## 对比（两表）

```bash
PYTHONPATH="$RG_TEST" python -m analysis.scripts.compare_kv_similarity \
  --buggy-dir <bad_kv_dir> --ref-dir <ref_kv_dir> \
  --buggy-report <buggy.json> --ref-report <ref.json> \
  --block-size 128 --cos-thresh 0.99

PYTHONPATH="$RG_TEST" python -m analysis.scripts.locate_first_divergence \
  --buggy-dir <bad_kv_dir> --ref-dir <ref_kv_dir> \
  --report <buggy.json> --block-size 128 --cos-thresh 0.99

PYTHONPATH="$RG_TEST" python -m analysis.scripts.compare_per_layer \
  --buggy-dir <bad_kv_dir> --ref-dir <ref_kv_dir> --report <buggy.json>
```

- **Table 1**：per-token min-cos → 首坏 token  
- **Table 2**：该 token 的 per-layer cos/maxdiff → 首坏层  

按 investigation **Q1–Q5** 解读；交付用手册定界模板。

### 读表要点

| 信号 | 含义 |
|------|------|
| 无首分歧 / 全程高相似 | 非 KV 内容 → 模型/后采样 |
| prompt 段首坏 | 偏 prefill |
| output 段首坏 | 偏 decode |
| 全层齐坏 | 整包写/传 |
| 从某层起坏 | 该层计算/写出 |
| cos 断崖→0 | 污染/串 block |
| 平台 ~0.8–0.9 | 偏计算误差 |

**TP>1**：先对齐 `tp_rank` / `num_kv_heads`；必要时 `stitch_kv`。  
对比结束后删除临时全量 `kv_cache`（保留 `.pt` 小样证据即可）。

## Related

- `runtime-guard-investigation` — 端到端编排  
- `runtime-guard-analysis` — verify / inspect
