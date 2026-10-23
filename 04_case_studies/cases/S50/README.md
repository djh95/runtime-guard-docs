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

**检出。** 现行 **58 / 48 / 48**（`detect_by.logits_finite=48`）。结案档：**KV 不一致→定界**（有限性/未用槽分级；**非** NaN-cos 层定位）。

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
| 标杆 | **清洁树、无 overlay**；须确认 **未**亮 `logits_finite`；manual_dump + force-feed history |

## 5 · 定界分析

### 事实

- 现象：全请求 `!!!!…`；`logits_finite` 必现（48/48）。
- 三层：**58 / 48 / 48**。
- 钉点 report（×2）：`…ac611d71`、`…b27e35ba`；均 `prompt=14`、`output_at_dump=1`、`finite_kind=nan`。
- **≥2 组**异常↔清洁标杆（2026-10-23 Asia/Shanghai 补抓 `S50-ref-recap-20261023T094236`；标杆侧 `logits_finite` 未触发；shape `[1,128,4,128]` 一致）。
- history 窗：`n_tokens = p + o − 1 = 14`（短窗；只做有限性/未用槽，**不做层定位**）。
- **异常侧：** 有效槽 **全 NaN**（无 Inf）；未用槽 **亦有 NaN**（按 v5.15 分级属**可影响结果**；非「仅有限非 0 卫生脏写」）。
- **标杆侧：** 有效槽有限；未用槽全 0。
- 证据：`evidence/kv_compare.json` + `kv_finite_unused.json`；服务器 `verified_kv/S50/ref_recap/`（**.pt 未入库**）。

### 推断

- 有效槽已非有限 + 标杆洁净 → **不能排除**「坏值已进/经 KV」；属 **KV 不一致**类信号。
- 未用槽 NaN 加重严重度；**不能**单凭 KV 推出「根因=KV 子系统」或「根因=SwiGLU 对调」（后者仅构造背景）。
- 全 NaN cos **不定层**；短 o=1 窗进一步削弱层定位。
- **未开 msprobe**（殿后；本包不停在算子名）。

### 结论

- 结案档：**KV 不一致→定界**（有限性/未用槽事实；两组同向；标杆未炸）。
- 尚未定界到具体算子/构造根因；分析不出 / 证据不足；需要时再开 `msprobe-dump`。

## 6 · 证据文件

| 文件 | 用途 |
|------|------|
| `evidence/overlay.patch` | 制造异常的静态补丁 |
| `evidence/规格说明.md` | 复现规格 |
| `evidence/三层计数.json` | 三层明细 |
| `evidence/跑批结果.json` | 跑批元数据 + 结案摘要 |
| `evidence/samples/` | prompt + completion 样本 |
| `evidence/reports/` | 钉点 Guard report（非空 prompt；logits_finite） |
| `evidence/kv_compare.json` | 两组有限性/未用槽分级摘要 |
| `evidence/kv_finite_unused.json` | 明细（含 worst_head） |
| `evidence/kv_pairs_recap.json` | 标杆补抓配对元数据 |

## 7 · 上游 PR 关系

| PR / 链接 | 角色 |
|-----------|------|
| （构造 soft-inverse；见规格） | 案例背景，**非**本包 KV 已证根因 |
| [ascend#19285](https://github.com/vllm-project/vllm-ascend/pull/19285) | **抓 dump 辅助**：非空 `prompt_token_ids` |
