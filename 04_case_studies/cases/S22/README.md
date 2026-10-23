# S22 · Spec resample 无 SALT（KV 不一致→定界 · 一对分/一对 clean）

公开自洽案例包。G2 pin 缺 `RESAMPLE_NOISE_SALT`；overlay 只打 trigger 日志（origin-faithful）。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案 | **KV 不一致→定界**（一对分 / 一对 clean） |
| 检测 | **检出** |
| 三层率 | **116 / 0 / 48**（`spec_acceptance`×47 + `token_repeat`×1） |
| Detector | `spec_acceptance`（兼 `token_repeat`） |
| Origin | `ascend-only`（+ cousin vLLM#61161）；见规格 |
| Guard pin | G2 `f2aefd068` + 抓 dump 时临时合入 [#19285](https://github.com/vllm-project/vllm-ascend/pull/19285) |
| 模型 | Qwen3-8B + eagle3 · TP2 · CARD=4,5 · `192.168.13.160` / `rg-test-160` |
| Run | `keep-set-retest-20261022` · `S22-layers-20261023T145540` |

## 1 · 现象

投机接受率异常被抓住（`spec_acceptance` 47/48）；**输出未必是乱码**（precision=0，无跨请求乱码文本）。样本见 [evidence/samples/](./evidence/samples/)。

## 2 · 案例背景 / 构造

Rejection 与 residual resample 共用 RNG、无独立 salt（inverse [ascend#18657](https://github.com/vllm-project/vllm-ascend/pull/18657)）。细节见 [evidence/规格说明.md](./evidence/规格说明.md)；补丁见 [evidence/overlay.patch](./evidence/overlay.patch)。

## 3 · Guard 结果

**检出。** **116 / 0 / 48**。结案档：**KV 不一致→定界**（**两组不同向**：一对在靠后的生成步、高编号 dump 层出现余弦分歧；另一对全程干净；数值门闩无命中；模型层在 prompt 第 1 个 token 上两侧≈1.0）。细节见 `evidence/kv_*.json`。

## 4 · 复现技巧

| 项 | 现行复现 |
|----|----------|
| Overlay | `gen_s22_overlay.py` → `22_spec_resample_rng_collide.patch`（2348 B；PLAIN apply OK） |
| 模型 | Qwen3-8B + `Qwen3-8B-speculator.eagle3` |
| 负载 | `temperature=0.8` · `num_speculative_tokens=3` · concurrency 48 |
| detector | `both`（主看 `spec_acceptance`） |
| 注意 | 树内 `resample.py` 为 CRLF；勿用剥 CR 的 text-mode diff |

## 5 · 定界分析

### 事实

- **≥2 组**清洁标杆；shape 一致；有效槽有限。
- **v5.16：** 数值问题格 **0**（两对）。
- **余弦：** 对 A — `first_cos_mismatch` @ **token_idx=20**（`out[6]`）dump `layer_72`（cos≈0.971；min≈0.968 @ `layer_73`）；对 B — **无** cos 分歧。
- `model.layers.*` tok0 两对最差仍 ≈1.0；`first_cos_mismatch_model_layers_tok0` = null。
- precision=0：本窗不靠乱码文本，靠 acceptance 检测 + KV。
- 证据：`evidence/kv_*.json`（**.pt 未入库**；服务器 `verified_kv/S22/`）。

### 推断

- 有效槽在一对上已出现晚步余弦分歧 → 按 keep-set 门闩记 **KV不一致→定界**；**非两组同向**，不定界到 resample 源码行 / salt 缺失的唯一路径。
- 根因叙事仍锚定「无 SALT 的 shared RNG」（规格 / #18657），本窗 KV 只证明「有分歧窗口」，不单独证明 salt。

### 结论

- 结案档：**KV 不一致→定界**（检出；一对分、一对 clean；无数值门闩命中）。

## 6 · 证据文件

| 文件 | 用途 |
|------|------|
| `evidence/overlay.patch` | 异常构造（platform + resample trigger；无 #19285） |
| `evidence/规格说明.md` | 规格 + 实测钉点 |
| `evidence/三层计数.json` / `跑批结果.json` | 三层 / 摘要 |
| `evidence/samples/` / `reports/` | 样本 / 报告 |
| `evidence/kv_*.json` | 对账（v5.16） |

## 7 · 上游 PR 关系

| PR / 链接 | 角色 |
|-----------|------|
| [ascend#18657](https://github.com/vllm-project/vllm-ascend/pull/18657) | **根因修复**（`RESAMPLE_NOISE_SALT`） |
| [vLLM#61161](https://github.com/vllm-project/vllm/pull/61161) | cousin |
| [ascend#19285](https://github.com/vllm-project/vllm-ascend/pull/19285) | dump 抓取前置（非本 anomaly） |
