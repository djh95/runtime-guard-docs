# S50 · SwiGLU gate/up half-swap（KV 不一致→定界）

公开自洽案例包。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案 | **KV 不一致→定界** |
| 检测 | **检出** |
| 三层率 | **58 / 48 / 48**（`logits_finite`×48） |
| Detector | `logits_finite` |
| Origin | `both` |
| Guard pin | G2 `f2aefd068` + 抓 dump 时临时合入 [#19285](https://github.com/vllm-project/vllm-ascend/pull/19285)（非空 `prompt_token_ids`） |
| 模型 | Qwen3-8B · TP2 · CARD=4,5 · `192.168.13.160` / `rg-test-160` |
| Run | 英文河名短句 × 48 并发；`keep-set-retest-20261022` |

## 1 · 现象

全请求 `!!!!…`（identical-mode ×48）；采样前 logits 非有限（report：`finite_kind=nan`）。样本见 [evidence/samples/](./evidence/samples/)。

## 2 · 案例背景 / 构造

Soft-inverse：SwiGLU 先 `cat(up, gate)` 再 `npu_swiglu`（gate/up 对调）。细节见 [evidence/规格说明.md](./evidence/规格说明.md)；补丁见 [evidence/overlay.patch](./evidence/overlay.patch)。**构造根因不是本包 KV 定界已证。**

## 3 · Guard 结果

**检出。** 现行 **58 / 48 / 48**（`detect_by.logits_finite=48`）。结案档：**KV 不一致→定界**（v5.16 数值门闩 + 干净格余弦；两组同向）。

钉点 dump report：`prompt_token_ids` 长度 **14**（非空）；dump 时 `output_token_count=1`（早拍窗）。

## 4 · 复现技巧（必读）

| 项 | 现行复现 |
|----|----------|
| Overlay | `gen_s50_overlay.py` 就地改 B 树 |
| Prompt | `Name one famous river. One short English sentence. id={i}.` |
| 并发 | **48** |
| 其它 | temp=0；`max_tokens` 足以出 `!!!!` |
| detector | `logits_finite`（可兼开 `token_repeat`） |
| 抓 dump | 非空 `prompt_token_ids` → 临时 #19285；抓前清 `kv_cache` |
| 标杆 | **清洁树、无 overlay**；须确认 **未**亮 `logits_finite`；manual_dump + force-feed history。必现时也可问他环境是否正常 → 跨环境标杆（须权重 MD5 + 代码 commit 一致；见 skills v5.17） |

## 5 · 定界分析

### 事实

- 现象：全请求 `!!!!…`；`logits_finite` 必现（48/48）。
- 三层：**58 / 48 / 48**。
- 钉点 report（×2）：`…ac611d71`、`…b27e35ba`；均 `prompt=14`、`output_at_dump=1`、`finite_kind=nan`。
- **≥2 组**异常↔清洁标杆（`S50-ref-recap-20261023T094236`；标杆未亮 `logits_finite`；shape `[1,128,4,128]` 一致）。
- history 窗：`n_tokens = p + o − 1 = 14`（prompt token0 起即可比）。
- Dump 含两套层名（各 36）：`layer_36..71` 与 `model.layers.0..35.self_attn.attn`。**双名同一套 KV**：`layer_36` = `model.layers.0`，不是「第 36 层」。
- **v5.16 数值门闩 + 余弦（两对同向）：**

| 对 | first_numeric（model.layers） | first_cos_mismatch（干净格） | 备注 |
|----|-------------------------------|------------------------------|------|
| `…ac611d71` | token **0** @ `model.layers.6`（`buggy_nan`） | token **0** @ `model.layers.3`（cos≈0.989，阈值 0.99） | L5 最差 cos≈-0.017；L0–L2≈1 |
| `…b27e35ba` | token **0** @ `model.layers.6`（`buggy_nan`） | token **0** @ `model.layers.3`（cos≈0.989） | 同向 |

- `layer_36..71`：自 token **0** 起 used 槽 **全 NaN**（全名 natural-sort 的 first_numeric 会先落到 `layer_36`；属并行命名，不作唯一层叙事）。
- `model.layers.6..35`：自 token 0 起 **数值问题**（不算余弦）；L0–L5 有限可算余弦。
- 未用槽：异常侧亦有 NaN（严重）；标杆未用槽全 0。
- 证据：`evidence/kv_compare.json` + `kv_v516_numeric_first.json`；服务器 `verified_kv/S50/ref_recap/`（**.pt 未入库**）。

### 推断

- prompt token0 起：干净格上余弦在 L3 越阈、L5 塌缩，L6+ 已非有限 → **KV 不一致**且可写层事实（非伪 NaN-sort）。
- **不能**单凭此推出「根因=SwiGLU 对调」或「根因=KV 子系统」（前者仅构造背景）。
- **未开 msprobe**（殿后）。

### 结论

- 结案档：**KV 不一致→定界**（v5.16；两组同向；标杆未炸；含 first_numeric / first_cos 层事实）。
- 尚未证到构造根因算子名；需要时再开 `msprobe-dump`。

## 6 · 证据文件

| 文件 | 用途 |
|------|------|
| `evidence/overlay.patch` | 制造异常的静态补丁 |
| `evidence/规格说明.md` | 复现规格 |
| `evidence/三层计数.json` | 三层明细 |
| `evidence/跑批结果.json` | 跑批元数据 + 结案摘要 |
| `evidence/samples/` | prompt + completion 样本 |
| `evidence/reports/` | 钉点 Guard report（非空 prompt；logits_finite） |
| `evidence/kv_compare.json` | v5.16 数值门闩 + 余弦首分歧（两组） |
| `evidence/kv_v516_numeric_first.json` | v5.16 重分析摘要 |
| `evidence/kv_finite_unused.json` | 有限性/未用槽明细 |
| `evidence/kv_pairs_recap.json` | 标杆补抓配对元数据 |

## 7 · 上游 PR 关系

| PR / 链接 | 角色 |
|-----------|------|
| （构造 soft-inverse；见规格） | 案例背景，**非**本包 KV 已证根因 |
| [ascend#19285](https://github.com/vllm-project/vllm-ascend/pull/19285) | **抓 dump 辅助**：非空 `prompt_token_ids` |
