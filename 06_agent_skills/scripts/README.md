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

**KV 对比注意：** 新抓前清空本轮 `kv_cache` 工作目录。对比时**先核对层 shape**；dump 为整 block，未用槽常为 0——只用 report 有效 token 数（或 `stitch_kv --written-only` / `--max-tokens`），勿按 `n_blocks * block_size` 全容量算余弦。
