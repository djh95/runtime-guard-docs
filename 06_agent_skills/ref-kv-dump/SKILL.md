---
name: runtime-guard-ref-kv-dump
description: >-
  After verify_request_kv PASS, force-feed report token ids into a clean
  same-model/topology/MODE server, capture native dump_kv ref, and compare
  buggy vs ref (first divergence / per-layer). Requires PASS evidence; do not
  reimplement verify or emit runtime_config JSON. Guard KV path only
  (native dump_kv). Also used after logits_finite: finite/unused-zero first;
  msprobe is last, not a substitute.
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
4. 可选：`--feed history`（默认）/ 末 token / `--feed full`。  
5. 收集：`runtime/report/kv_cache/<type>/<ref_req_id>/wave_N/<rank_tag>/`（确认是**本轮清空后新写出**的路径）。  
6. **归档 ref dump** 后再清目录开下一对；勿只留 buggy。

### `--feed=history` 对比长度（踩坑）

默认 history = **`prompt + output[:-1]`**，再 `max_tokens=1` 生成的是 **ref 新 token**，不是异常的最后一个 output。

| 比什么 | 对不对 |
|--------|--------|
| `n_tokens = len(prompt) + len(output) - 1`（只比 feed 跨度） | **对** |
| `n_tokens = len(prompt) + len(output)`（把末 output 也算进去） | **错** — 末位常 NaN / 低 cos / 假 `first_mismatch`→层名 |

末位假分歧 **禁止**写成「KV 不一致→定界」或 `token0@layer_L`。`--feed=full` 时才可按 `prompt+output` 全长比（仍要先 shape、剔未用 0 槽）。

## 对比（两表）— 先形状，再有效 token

Dump 布局是 **整 block 保存**：`[n_blocks, block_size, H, D]`（`block_ids` 顺序）。  
block 内**未写入的 token 槽应为 0**；若把整 block / 超额 slot 算进余弦，零槽会污染相似度（虚高、全 NaN、或假分歧）。

**未用槽分级（必区分）：**

| 未用槽状态 | 含义 | 对结果 |
|------------|------|--------|
| 全 0 | 正常 | — |
| **有限非 0** | 脏写/未清（卫生问题，类 S30 轻） | **一般不致坏结果**；记附注，勿当余弦噪声丢掉，也**勿**单凭此断定输出由此坏 |
| **Inf / NaN** | 数值污染进未用区 | **可影响结果**（严重）；与有效槽非有限同级关注 |

**对比前硬步骤：**

1. **先比形状** — buggy vs ref 各层 `shape` 一致（含 `n_blocks` / `block_size` / heads）；不一致 → 停，查 TP stitch / 错目录 / 不同 MODE，**勿直接算 cos**。  
2. **有效槽有限性（`logits_finite` / 数值炸必做）** — 对 `n_used` 槽计 Inf/NaN；Inf 比单纯 cos 低更重。有效槽已非有限 → 记事实（可归「不一致」类信号），**禁止**用 NaN cos 写层名。  
3. **未用槽分级** — 见上表；分别报 `unused_nonzero_finite` 与 `unused_nonfinite`，勿混为一谈。  
4. **只比有效 token（有限时）** — 与 feed 对齐：默认 history 用 **`n_prompt + n_output - 1`**；full feed 才用 `n_prompt + n_output`；或 `--written-only`。**禁止**按 `n_blocks * block_size` 全容量比。  
5. **逐格数值门闩 → 再余弦（脚本已强制）** — 对每个 (token, layer)：先扫 **NaN / Inf / 零范数**；有问题 → 标 **数值问题**，**不算余弦**。相似度只在干净格上取 min；**禁止**把 NaN 当「最差 cos」排序成伪 `first_mismatch_idx=0 @ layer_*`。有效槽全非有限 → 不定层，只写「有效槽全非有限」。  
6. 有干净格后再跑两表：

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
| **全格 `数值问题` / 无有效余弦** | **不是层定位** — 脚本不再产出可信 `first_mismatch` 层名；记「有效槽全非有限」；并**分级**报未用槽 |
| **有效槽 Inf/NaN** | 数值溢出已进/经 KV；偏计算写入或上游炸 |
| **未用槽有限非 0** | 脏写/卫生；**通常不致坏结果**；附注即可 |
| **未用槽 Inf/NaN** | 可影响结果；严重数值信号 |
| **仅末 token 分歧**（history feed 且按 p+o 全长比） | **多半 feed 跨度错** — 改 `n_tokens=p+o-1` 复核；勿定界到层 |
| **shape 不一致** | 错 dump / 未 stitch / 拓扑或 MODE 不一致 — 先修对齐 |

**TP>1：** 对齐 `tp_rank` / `num_kv_heads`；必要时 `stitch_kv`。  
**生命周期：** 抓前清空工作目录 → 抓后/对账中保留本轮 dump → keep-set 归档后再按配额清临时全量（可留 `.pt` 小样）。

## 有效对账前提（踩坑硬纪律）

1. **同一次异常请求** — buggy report、buggy dump、ref dump、`kv_compare` 必须对齐同一 `req_id`/wave。禁止拿「有 dump 的旧跑」配「新 detect 钉点」。**detect=0 也不授权**混用历史 dump。  
2. **先有有效异常** — 目标形态已复现；dump 覆盖足够 output（勿把 **弱窗** 如仅 o=1 / 非异常 completion 当有效异常 KV）。未满足 → 停，交 investigation 写 **复现未抓到** / 未做有效对账。  
3. **先形状、有效 token** — 见上节；history feed 用 `p+o-1`；勿把 block 尾部未用 0 槽算进相似度。  
4. **全格数值问题 / 仅末位假分歧 ≠ 层定位** — 有效槽全非有限、或 Table1 无有效余弦、或 **只有最后一个 output** 分歧时，先查数值门闩 / feed 跨度 / 空槽；**禁止**写成「首坏 token0 @ layer_L」。有效槽 Inf/NaN 仍是可归档事实（非「复现未抓到」）。  
5. **标杆未炸** — `logits_finite` 路径下 ref 必须未触发该 detector；炸过的 dump 不可当标杆。  
6. **多组验证** — 同一 overlay 至少两组独立异常请求，结论同向再归档③/④。  
7. **空 `prompt_token_ids`** — 勿字符串重 tokenize。优先树含 [#19285](https://github.com/vllm-project/vllm-ascend/pull/19285)（prompt 预缓存不门禁 sample hooks）再抓；否则同 prompt **re-curl** 抓服务端 ids，与异常 `output_token_ids` 合并后再 force-feed。  
8. **短 output** — 只削弱层定位余弦；**不**等于跳过有限性/未用槽检查。

## forbidden

- 无 verify PASS 仍执行  
- 重复实现 `verify_request_kv`  
- 输出 runtime_config JSON；用 msprobe **冒充** KV 对比源  
- **`logits_finite` 后跳过本 skill** 直接 msprobe  
- 用弱 dump / 全 NaN cos / **history 下按 p+o 全长** 的末位假分歧写层定位  
- 把未用槽「有限非 0」与「Inf/NaN」混写成同等严重；忽略有效槽 Inf；混用不同 run  
- 跳过 shape 检查；按整 block 容量（含未用槽）算余弦  
- 用本地 tokenize 字符串冒充服务端 `prompt_token_ids`；用已炸请求当标杆

## Related

`analysis`（门闩）· `investigation`（十问交付）· `config-recommender`（arm dump 配置）· `msprobe-dump`（殿后）
