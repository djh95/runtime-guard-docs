# 离线分析脚本（docs 仓）

对外排障 / keep-set 复现用的读盘脚本。在本目录直接跑。

```bash
export RG_DOCS=/path/to/runtime-guard-docs
SCRIPTS="$RG_DOCS/06_agent_skills/scripts"

python "$SCRIPTS/summarize_reports.py" --help
python "$SCRIPTS/verify_request_kv.py" --help
python "$SCRIPTS/score_completion_samples.py" --help
python "$SCRIPTS/prepare_ref_inputs.py" --help
python "$SCRIPTS/request_from_report.py" --help
python "$SCRIPTS/compare_kv_similarity.py" --help
python "$SCRIPTS/locate_first_divergence.py" --help
python "$SCRIPTS/compare_per_layer.py" --help
python "$SCRIPTS/inspect_kv_dump.py" --help
python "$SCRIPTS/stitch_kv.py" --help
python "$SCRIPTS/correlate_incident.py" --help
```

与 [02 问题定位](../../02_problem_localization/README.md) Step 4、[analysis skill](../analysis/SKILL.md)、[ref-kv-dump](../ref-kv-dump/SKILL.md) 同一套入口。

**KV 对比注意（v5.20.10 硬顺序）：** 新抓前清空本轮 `kv_cache` 工作目录。① **先 shape + 掩未用槽**；② 对**有效槽** (token, layer) **数值扫描并先报**（NaN/Inf/零范数/全零 → `数值问题`，**不算余弦**）；③ **另记未用槽**（多数为 0，偶见有限非零残留；亦可 NaN/Inf——**禁止**写「未用一定填 0」）；④ 相似度只在干净有效格上算。dump 为整 block。默认 `--feed=history` 时 `--num-tokens` 用 **`n_prompt+n_output-1`**（勿用 `p+o` 全长，否则末位假分歧）；或 `stitch_kv --written-only`。勿按 `n_blocks * block_size` 全容量算余弦。表1 有首坏时须带后续 out（可合并）。
