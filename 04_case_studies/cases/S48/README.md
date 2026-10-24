# S48 · Residual negate（KV 不一致→定界）

公开自洽案例包。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案 | **KV 不一致→定界** |
| 检测 | **检出** |
| 三层率 | **44 / 48 / 48**（`logits_finite`×48） |
| Detector | `logits_finite` |
| Origin | `both` |
| Guard pin | G2 `f2aefd068` + 抓 dump 时临时合入 [#19285](https://github.com/vllm-project/vllm-ascend/pull/19285)（非空 `prompt_token_ids`） |
| 模型 | Qwen3-8B · TP2 · CARD=4,5 · `192.168.13.160` / `rg-test-160` |
| Run | `keep-set-retest-20261022` · `S48-layers-20261023T103724` / `S48-pr19285-20261023T103909` / `S48-ref-recap-20261023T104049` |

## 1 · 现象

全请求 `!!!!…`（identical-mode ×48）；采样前 logits 非有限。样本见 [evidence/samples/](./evidence/samples/)。

## 2 · 案例背景 / 构造

Soft-inverse：fused add-RMSNorm 前 `residual = -residual`。细节见 [evidence/规格说明.md](./evidence/规格说明.md)；补丁见 [evidence/overlay.patch](./evidence/overlay.patch)。**构造根因不是本包 KV 定界已证。**

## 3 · Guard 结果

**检出。** 现行 **44 / 48 / 48**（`detect_by.logits_finite=48`）。结案档：**KV 不一致→定界**（有限性/未用槽分级；**非**余弦层定位）。

钉点 dump report：`prompt_token_ids` 长度 **14**（非空）；dump 时 `output_token_count=1`（早拍窗）。

## 4 · 复现技巧（必读）

| 项 | 现行复现 |
|----|----------|
| Overlay | `gen_s48_overlay.py` 就地改 B 树 |
| Prompt | 英文河名短句 ×48 |
| 并发 | **48** |
| detector | `logits_finite` |
| 抓 dump | 非空 `prompt_token_ids` → 临时 #19285；抓前清 `kv_cache` |
| 标杆 | **清洁树、无 overlay**；须确认 **未**亮 `logits_finite`；manual_dump + force-feed history |

## 5 · 定界分析

### 事实

- **现象与检测：** 全请求 `!!!!…`；`logits_finite` 48/48 命中。三层 **44 / 48 / 48**。
- **清洁标杆（≥2 组）：** 干净服务重放对照；标杆**未**亮 `logits_finite`；shape `[1,128,4,128]`。钉点 report：prompt=14，**`output_at_dump=1`（o=1）**，history 按 `p+o−1` 长度为 14。
- **两对同向（有限性，不定层）：** 异常侧**有效槽全是 NaN**（无 Inf）；**未用槽也有 NaN**（严重，不是「仅有限非 0 的卫生脏写」）。标杆侧有效槽有限、未用槽全 0。
- **为何不定「第一坏层」：** 余弦要两边都是可比较的有限数。有效槽已是 NaN → **没有有效余弦格**，不能写「第几层先分叉」。短生成窗（o=1）也削弱层定位。
- 证据：`evidence/kv_compare.json`、`kv_finite_unused.json`；`verified_kv/S48/`（**.pt 未入库**）。

### 推断

- 有效槽已非有限 + 标杆洁净 → **不能排除**「坏值已进/经 KV」；属 **KV 不一致**类信号。
- 未用槽 NaN 加重严重度；**不能**单凭 KV 推出「根因=residual 取反」。
- 有效槽全是 NaN，没法用余弦找「第一坏层」；短生成窗进一步削弱层定位。
- **未开 msprobe**（殿后）。

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
