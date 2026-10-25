---
name: runtime-guard-ref-kv-dump
description: >-
  After verify_request_kv PASS, force-feed report token ids into a clean
  same-model/topology/MODE server, capture native dump_kv ref, and compare
  buggy vs ref (first divergence / per-layer). Requires PASS evidence; do not
  reimplement verify or emit runtime_config JSON. Guard KV path only
  (native dump_kv). After capture: shape/mask unused → numeric scan on used
  slots first (report 数值问题 subtypes) → only then cosine/tables. 必现+detect=0
  may use manual_dump (S07/S45). logits_finite still KV; msprobe last.
---

# Reference KV via native dump_kv

**类型：原子 · 标杆抓取 + 对比。**

**force-feed：** 按报告里的 token id 原样喂给干净服务（禁止再 tokenize 字符串）。

**硬门闩：** 已有 `verify_request_kv` **PASS**（本轮先跑 `runtime-guard-analysis`，或用户出示 PASS 证据）。  
PASS = 脚本确认异常 dump **可读齐全**，可以继续抓清洁标杆；**不是**结案「KV 一致」。无 PASS → 停止抓 ref，先修路径 / 配额 N / `on_trigger`（含 `"dump_kv"`）。  
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

## 跨环境标杆（必现案优先确认）

同机「去 overlay 清洁树」仍是默认路径；若问题**必现**且存在多套环境，按下面做（S50 / `logits_finite` 等尤相关）：

1. **先问使用者**：其他环境是否正常？（例：外部厂商环境有问题，内部自建环境正常。）未确认勿假设「只有本机能出标杆」。  
2. **有「异常环境 + 正常环境」** → 可分别抓：**异常侧** dump（buggy）与 **正常环境** dump（标杆）；再 force-feed / 对比。  
3. **对比前必须对齐代码与权重**（否则不能当干净标杆）：  
   - **权重：** 两边算 **MD5**（或等价校验，如目录 manifest / `sha256sum`）确认一致。  
   - **代码：** 记录并核对 **commit**（及关键 patch / overlay / 热补丁）一致。  
4. **不一致 → 停**：先对齐权重/代码再 dump；禁止拿「碰巧能跑」的他环境当 ref。  
5. 对齐后仍要求：同拓扑 / **同 MODE**；`logits_finite` 路径下标杆侧**未**触发该 detector。

## 抓 ref

```bash
python "$SCRIPTS/prepare_ref_inputs.py" \
  --report <report_*.json> --out ref_inputs.json
```

1. **清洁**服务：同模型 / 同拓扑 / **同 MODE**（勿 eager↔graph 对照）；跨环境时先满足上一节权重 MD5 + 代码 commit 一致。  
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

## 何时抓 dump（含必现 + detect=0）

| 情况 | 怎么抓异常 KV |
|------|----------------|
| detector 已出 report（on_trigger / auto） | 用该 `req_id` 的 dump；缺则同请求补抓 |
| **必现**（或 precision 已坏）但 **detect=0**（乱码漏检等；S07/S45） | **允许 `manual_dump`** 抓异常侧 + 清洁标杆，再走下方硬顺序；**禁止**因 0 报告就跳过 KV / 写成「复现未抓到」 |
| 非必现 / 难复现 | 同样可用 `manual_dump` 抬抓取率 |

抓标杆：同 token force-feed；`logits_finite` 路径下标杆**未**炸。

## 对比硬顺序（抓完 dump 必须按此做；v5.16+ / v5.20.10）

Dump 布局是 **整 block 保存**：`[n_blocks, block_size, H, D]`（`block_ids` 顺序）。  
对比窗只取**有效槽**（history 默认 **`n_prompt + n_output − 1`**）。窗后槽 = **未用槽**（须掩掉再算余弦）。

**有效槽 vs 未用槽（必须分写；v5.20.10）：**

| 区 | 先查什么 | 怎么写 |
|----|----------|--------|
| **有效槽（used）** | 数值问题：全零 / zero_norm / NaN / Inf；否则有限非零再比余弦 | 定界主证据；先报完再进表1/表2 |
| **未用槽（unused）** | 精确全 0 / **有限非零残留** / NaN·Inf | 附注卫生或严重污染；**禁止**写「未用一定填 0」（实机多数为 0，偶见有限非零） |

**未用槽分级（属步骤 1 的 mask/附注，不是余弦主结论）：**

| 未用槽状态 | 含义 | 对结果 |
|------------|------|--------|
| 全 0 / **多数为 0** | 常见正常 | — |
| **有限非 0** | 脏写/未清（卫生） | **一般不致坏结果**；**必须记一笔**，勿单凭此断定输出由此坏 |
| **Inf / NaN** | 数值污染进未用区 | **可影响结果**（严重） |

### 硬步骤（禁止跳步、禁止先写余弦再回头补数值）

1. **形状 + 掩掉未用槽** — buggy vs ref 各层 `shape` 一致（含 `n_blocks` / `block_size` / heads）；不一致 → **停**，查 TP stitch / 错目录 / 不同 MODE，**勿算 cos**。对齐 feed 跨度（history=`n_prompt+n_output-1`；或 `--written-only`）；**禁止**按 `n_blocks*block_size` 全容量比。未用槽按上表分级记账（`unused_nonzero_finite` / `unused_nonfinite`）——有有限非零也要写，勿默认「全 0」。  
2. **有效槽（used）数值扫描 — 必须先报（带子类型）** — 对对比窗内每个有效 (token, layer) 先扫 **全零 / 零范数（zero_norm）/ 溢出 Inf·NaN** 等。有问题 → 标 **数值问题:\<子类型\>**（如 `zero_norm`、`NaN`、`Inf`），在事实/摘要/`kv_compare` 里 **先写清楚**（含能确定的 token/层范围）。**勿只写「数值异常」而不写子类型（证据能区分时）。此步未写完，禁止进入余弦与层表。** 有效槽已非有限或全数值问题 → 可归「不一致」类信号，**不定层**（禁止 NaN cos 伪层名）；仍须把数值事实归档。  
3. **仅对干净格再余弦 → 立刻导出逐 token/逐层 → 表 → 十问** — 相似度只在**无数值问题**的格上算。  
   **抓完 dump / 跑完 compare 后必须立刻**写出 `kv_v516_numeric_first.json`（或等价：`per_token` + 首坏 token 的**全层** `layers[]`），并填 keep-set **表1（每 token 最差格）/ 表2（首坏 token 逐层剖面）**（见 [04](../../04_case_studies/README.md)；表2 **不是** window token0 默认图）。  
   **表1 硬规矩（v5.20.10）：** 有首坏 / 问题 token 时，**必须**再展示其后若干 **out**（可合并如 `out[6]–out[24] 多为 0.6–0.8`，或抽样）；**禁止**停在首坏一行把后续 out 整段省略。仅当对比窗本身止于该 token（如 `n_output=1` → history 仅 prompt）才可写「本包对比窗无后续 out」。  
   **合并区间可选**；合并不了就画全层。**禁止**只留窗摘要 / `first_mismatch` 锚点就结案。有数值问题的格/token 写清子类型，**不编余弦**。然后交 investigation **【事实总结】+ 十问**（[02 §5](../../02_problem_localization/README.md#5-kv-定界十问检查单有-buggyref-时按序)）。交给编排的对比摘要须够 investigation 写成**白话事实**——细则见 investigation「事实写作」。

脚本（步骤 2→3 已强制先查数值问题；调用前仍须按上序解读与落笔；**compare 后立即落盘 JSON + 表**）：

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

- 脚本 Table1/2：per-token / per-layer；与案例页表1/表2 对齐时，数值问题格优先标 **子类型**（`数值问题:zero_norm` / `NaN` / `Inf`…）。  
- `stitch_kv` 优先 `--written-only`（或显式 `--max-tokens`），勿默认全 block 比。  
- **禁止**把 NaN 当「最差 cos」排序成伪 `first_mismatch_idx=0 @ layer_*`。

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
| **仅末 token 分歧**（history feed 且按 prompt+输出全长比） | **多半 feed 跨度错** — 改 `n_tokens = prompt 长度 + 输出长度 − 1` 复核；勿定界到层 |
| **shape 不一致** | 错 dump / 未 stitch / 拓扑或 MODE 不一致 — 先修对齐 |

**TP>1：** 对齐 `tp_rank` / `num_kv_heads`；必要时 `stitch_kv`。  
**生命周期：** 抓前清空工作目录 → 抓后/对账中保留本轮 dump → keep-set 归档后再按配额清临时全量（可留 `.pt` 小样）。

## 有效对账前提（踩坑硬纪律）

0. **只钉一轮** — 写入对外包的 `kv_compare` / `kv_v516_numeric_first` / 表1·表2 必须与该包三层·reports·结案同一 verified 波次。禁止用另一目录残留 `.pt`/JSON（不同 `req_id` 或不同 `keep-set-retest` vs `keepset-kv-compare`）补表或改结案。重跑则整包替换 evidence，旧产物删除或标明 superseded。  
1. **同一次异常请求** — buggy report、buggy dump、ref dump、`kv_compare` 必须对齐同一 `req_id`/wave。禁止拿「有 dump 的旧跑」配「新 detect 钉点」。**detect=0 也不授权**混用历史 dump。  
2. **先有有效异常** — 目标形态已复现；dump 覆盖足够 output（勿把 **弱窗** 如输出只有 1 个 token / 非异常 completion 当有效异常 KV）。未满足 → 停，交 investigation 写 **复现未抓到** / 未做有效对账。  
3. **硬顺序：shape/掩未用 → 有效槽数值先报 → 再余弦/表/十问** — 见上节；history feed 对比跨度用「prompt 长度 + 输出长度 − 1」；勿把 block 尾部未用 0 槽算进相似度。  
4. **全格数值问题 / 仅末位假分歧 ≠ 层定位** — 有效槽全非有限、或表1 无有效余弦、或 **只有最后一个 output** 分歧时，**先落笔数值问题** / 再查 feed 跨度 / 空槽；**禁止**写成「首坏 token0 @ layer_L」。有效槽 Inf/NaN / zero_norm 仍是可归档事实（非「复现未抓到」）。  
5. **标杆未炸** — `logits_finite` 路径下 ref 必须未触发该 detector；炸过的 dump 不可当标杆。  
6. **跨环境标杆先对齐** — 必现案确认他环境是否正常；分环境抓 dump 前核对权重 MD5 + 代码 commit/overlay；不一致先对齐。  
7. **多组验证** — **同波** overlay 至少两组独立异常请求；结论同向 → 对外只归档一组；不同向 → 如实写，禁止揉成假同向。  
8. **空 `prompt_token_ids`** — 勿字符串重 tokenize。优先树含 [#19285](https://github.com/vllm-project/vllm-ascend/pull/19285)（prompt 预缓存不门禁 sample hooks）再抓；否则同 prompt **re-curl** 抓服务端 ids，与异常 `output_token_ids` 合并后再 force-feed。  
9. **短 output** — 只削弱层定位余弦；**不**等于跳过有限性/未用槽检查。

## forbidden

- 无 verify PASS 仍执行  
- 重复实现 `verify_request_kv`  
- 输出 runtime_config JSON；用 msprobe **冒充** KV 对比源  
- **`logits_finite` 后跳过本 skill** 直接 msprobe  
- 用弱 dump / 全 NaN cos / **history 下按 prompt+输出全长** 的末位假分歧写层定位  
- 把未用槽「有限非 0」与「Inf/NaN」混写成同等严重；忽略有效槽 Inf；混用不同 run / **不同波次目录**  
- 用另一波 `req_id` 的表/数组覆盖本轮结案；重跑后保留双套互相矛盾的 evidence  
- 跳过 shape / 未用槽掩码；**跳过有效槽数值扫描就先写余弦或层表**；必现+detect=0 时拒绝 `manual_dump`、硬写成「复现未抓到」；按整 block 容量（含未用槽）算余弦  
- 用本地 tokenize 字符串冒充服务端 `prompt_token_ids`；用已炸请求当标杆  
- 跨环境时**未**核对权重 MD5 / 代码 commit 就把他环境 dump 当干净标杆

## Related

`analysis`（门闩）· `investigation`（十问交付）· `config-recommender`（arm dump 配置）· `msprobe-dump`（殿后）
