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

**force-feed：** 按报告里的 token id 原样喂给干净服务（禁止再 tokenize 字符串）。

**硬门闩：** 已有 `verify_request_kv` **PASS**（本轮先跑 `runtime-guard-analysis`，或用户出示 PASS 证据）。无 PASS → 停止，勿抓 ref。  
勿在本 skill 重复实现 verify。勿输出 `runtime_config`（起服/arm dump 配置来自 `config-recommender` 或用户已有 live JSON）。

契约：[SKILLS_METADATA.md](../SKILLS_METADATA.md) · 定界：[02 §5](../../02_problem_localization/README.md)  
脚本：本仓 `../scripts/`（`python "$SCRIPTS/<name>.py"`）

```bash
export RG_DOCS=/path/to/runtime-guard-docs
SCRIPTS="$RG_DOCS/06_agent_skills/scripts"
```

Report 须含 `prompt_token_ids` / `output_token_ids`（`save_sensitive_info: true`）。

## 为何 force-feed token ids

1. Prefill / decode 路径不同 — 标杆尽量同路径类。  
2. 字符串重 tokenize ≠ report token ids。  
3. 禁止标杆自行 greedy 生成。

## 抓前：清空本轮 `kv_cache` 工作目录

**新开一轮抓 dump / 对账之前**，先清空（或移走）本轮将写入的 `kv_cache` 根目录（及本地对照副本），再启服/发请求。  
目的：避免把**上一跑残留**的 `.pt` / wave 目录误当成本次 buggy 或 ref。  
（对照：对账**进行中**勿删正在用的 dump；归档完成后再清。）

## 抓 ref

```bash
python "$SCRIPTS/prepare_ref_inputs.py" \
  --report <report_*.json> --out ref_inputs.json
```

1. **清洁**服务：同模型 / 同拓扑 / **同 MODE**（勿 eager↔graph 对照）。  
2. 热更已开；用 recommender/用户配置 arm `dump_kv`（manual 或 auto）。  
3. Force-feed：

```bash
python "$SCRIPTS/request_from_report.py" \
  --report <report_*.json> \
  --url http://127.0.0.1:8000/v1/completions \
  --model <served-model-name>
# 默认 --feed=history → prompt + output[:-1]
```

也可用 `ref_inputs.json` 的 `force_feed_token_ids`。  
4. 可选：`--feed history` / 末 token / `--feed full`。  
5. 收集：`runtime/report/kv_cache/<type>/<ref_req_id>/wave_N/<rank_tag>/`（确认是**本轮清空后新写出**的路径）。

## 对比（两表）— 先形状，再有效 token

Dump 布局是 **整 block 保存**：`[n_blocks, block_size, H, D]`（`block_ids` 顺序）。  
block 内**未写入的 token 槽常为 0**；若把整 block / 超额 slot 算进余弦，零槽会污染相似度（虚高、全 NaN、或假分歧）。

**对比前硬步骤：**

1. **先比形状** — buggy vs ref 各层 `shape` 一致（含 `n_blocks` / `block_size` / heads）；不一致 → 停，查 TP stitch / 错目录 / 不同 MODE，**勿直接算 cos**。  
2. **只比有效 token** — `n_tokens` = report 实际 `prompt + output` 长度（或脚本 `--written-only` / 等价「写到的最后槽+1」）；**禁止**按 `n_blocks * block_size` 全容量比。  
3. 再跑两表：

```bash
python "$SCRIPTS/compare_kv_similarity.py" \
  --buggy-dir <bad_kv_dir> --ref-dir <ref_kv_dir> \
  --buggy-report <buggy.json> --ref-report <ref.json> \
  --block-size 128 --cos-thresh 0.99

python "$SCRIPTS/locate_first_divergence.py" \
  --buggy-dir <bad_kv_dir> --ref-dir <ref_kv_dir> \
  --report <buggy.json> --block-size 128 --cos-thresh 0.99

python "$SCRIPTS/compare_per_layer.py" \
  --buggy-dir <bad_kv_dir> --ref-dir <ref_kv_dir> --report <buggy.json>
```

- **Table 1**：per-token min-cos → 首坏 token  
- **Table 2**：该 token 的 per-layer → 首坏层  

`stitch_kv` 对照时优先 `--written-only`（或显式 `--max-tokens`），勿默认全 block 比。

解读交 investigation **十问** / 手册 [02 §5](../../02_problem_localization/README.md#5-kv-定界十问检查单有-buggyref-时按序)。

| 信号 | 含义 |
|------|------|
| 无首分歧 / 全程高相似 | 非 KV → 模型/后采样 |
| prompt 段首坏 | 偏 prefill |
| output 段首坏 | 偏 decode |
| 全层齐坏 | 整包写/传 |
| 从某层起坏 | 该层计算/写出 |
| cos 断崖→0 | 污染/串 block |
| 平台 ~0.8–0.9 | 偏计算误差 |
| **全 NaN `min_cos`** | **不是**定位信号 — 见下节；勿读 `first_mismatch_idx`/层名 |
| **shape 不一致** | 错 dump / 未 stitch / 拓扑或 MODE 不一致 — 先修对齐 |

**TP>1：** 对齐 `tp_rank` / `num_kv_heads`；必要时 `stitch_kv`。  
**生命周期：** 抓前清空工作目录 → 抓后/对账中保留本轮 dump → keep-set 归档后再按配额清临时全量（可留 `.pt` 小样）。

## 有效对账前提（踩坑硬纪律）

1. **同一次异常请求** — buggy report、buggy dump、ref dump、`kv_compare` 必须对齐同一 `req_id`/wave。禁止拿「有 dump 的旧跑」配「新 detect 钉点」。**detect=0 也不授权**混用历史 dump。  
2. **先有有效异常** — 目标形态已复现；dump 覆盖足够 output（勿把 **弱窗** 如仅 o=1 / 非异常 completion 当有效异常 KV）。未满足 → 停，交 investigation 写 **复现未抓到** / 未做有效对账。  
3. **先形状、有效 token** — 见上节；勿把 block 尾部未用 0 槽算进相似度。  
4. **全 NaN ≠ token0@layer** — 若 Table1 几乎全 NaN：脚本可能把 idx=0 + 首层名当占位；**禁止**写成「首坏 token0 @ layer_L」。NaN 多因对齐/切片后向量零范数（含误用空槽），**不是**「第 L 层 KV 填了 NaN」。处理：查 shape / `block_ids` / 有效 `n_tokens` / TP stitch → 重 dump 直至出现**有限** cos，再写首分歧。  
5. **多组验证** — 同一 overlay 至少两组独立异常请求，cos 结论同向再归档③/④。  
6. **空 `prompt_token_ids`** — 勿字符串重 tokenize；同 prompt re-curl 抓服务端 ids，与异常 `output_token_ids` 合并后再 force-feed（见 investigation）。

## forbidden

- 无 verify PASS 仍执行  
- 重复实现 `verify_request_kv`  
- 输出 runtime_config JSON；使用 msprobe  
- 用弱 dump / 全 NaN 对比结果写 keep-set ③/④ 或层定位  
- 混用不同 run 的 report 与 dump（含未清空目录导致的残留）  
- 跳过 shape 检查；按整 block 容量（含未用 0 槽）算余弦

## Related

`analysis`（门闩）· `investigation`（十问交付）· `config-recommender`（arm dump 配置）
