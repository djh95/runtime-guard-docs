---
name: runtime-guard-ref-kv-dump
description: >-
  After verify_request_kv PASS, force-feed report token ids into a clean
  same-model/topology/MODE server, capture native dump_kv ref, and compare
  buggy vs ref (first divergence / per-layer). Requires PASS evidence; do not
  reimplement verify or emit runtime_config JSON. No msprobe.
---

# Reference KV via native dump_kv

**类型：原子 · 标杆抓取 + 对比。**

**硬门闩：** 已有 `verify_request_kv` **PASS**（本轮先跑 `runtime-guard-analysis`，或用户出示 PASS 证据）。无 PASS → 停止，勿抓 ref。  
勿在本 skill 重复实现 verify。勿输出 `runtime_config`（起服/arm dump 配置来自 `config-recommender` 或用户已有 live JSON）。

契约：[SKILLS_METADATA.md](./SKILLS_METADATA.md) · 定界：[02 §5](https://github.com/djh95/runtime-guard-docs/blob/main/02_problem_localization.md)  
脚本：`PYTHONPATH=$RG_TEST python -m analysis.scripts.<name>`

Report 须含 `prompt_token_ids` / `output_token_ids`（`save_sensitive_info: true`）。

## 为何 force-feed token ids

1. Prefill / decode 路径不同 — 标杆尽量同路径类。  
2. 字符串重 tokenize ≠ report token ids。  
3. 禁止标杆自行 greedy 生成。

## 抓 ref

```bash
PYTHONPATH="$RG_TEST" python -m analysis.scripts.prepare_ref_inputs \
  --report <report_*.json> --out ref_inputs.json
```

1. **清洁**服务：同模型 / 同拓扑 / **同 MODE**（勿 eager↔graph 对照）。  
2. 热更已开；用 recommender/用户配置 arm `dump_kv`（manual 或 auto）。  
3. Force-feed：

```bash
PYTHONPATH="$RG_TEST" python -m analysis.scripts.request_from_report \
  --report <report_*.json> \
  --url http://127.0.0.1:8000/v1/completions \
  --model <served-model-name>
# 默认 --feed=history → prompt + output[:-1]
```

也可用 `ref_inputs.json` 的 `force_feed_token_ids`。  
4. 可选：`--feed history` / 末 token / `--feed full`。  
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
- **Table 2**：该 token 的 per-layer → 首坏层  

解读交 investigation **Q1–Q5** / 手册定界模板。

| 信号 | 含义 |
|------|------|
| 无首分歧 / 全程高相似 | 非 KV → 模型/后采样 |
| prompt 段首坏 | 偏 prefill |
| output 段首坏 | 偏 decode |
| 全层齐坏 | 整包写/传 |
| 从某层起坏 | 该层计算/写出 |
| cos 断崖→0 | 污染/串 block |
| 平台 ~0.8–0.9 | 偏计算误差 |

**TP>1：** 对齐 `tp_rank` / `num_kv_heads`；必要时 `stitch_kv`。  
对比后删临时全量 `kv_cache`（可留 `.pt` 小样）。

## forbidden

- 无 verify PASS 仍执行  
- 重复实现 `verify_request_kv`  
- 输出 runtime_config JSON；使用 msprobe

## Related

`analysis`（门闩）· `investigation`（Q1–Q5 交付）· `config-recommender`（arm dump 配置）
