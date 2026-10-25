# S22 · Spec resample 无 SALT（KV 不一致→定界 · 一对分叉 / 一对干净）

公开案例包。G2 pin 上 residual resample 与 rejection 共用随机源、缺少独立 salt；overlay **只打触发日志**（忠于原逻辑，不写 NaN、不填假 token）。检测靠「投机接受率」异常；**输出未必是乱码**。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案 | **KV 不一致→定界**（**一对分叉 / 一对干净**——务必读事实） |
| 检测 | **检出** |
| 三层率 | **116 / 0 / 48**（触发 / 判坏文本 / 报告；接受率检测×47 + 复读×1） |
| Detector | 主看 `spec_acceptance`（投机接受率）；兼开 `token_repeat` |
| Origin | `ascend-only`（+ cousin vLLM#61161）；见规格 |
| Guard pin | G2 `f2aefd068` + 抓 dump 时临时合入 [#19285](https://github.com/vllm-project/vllm-ascend/pull/19285) |
| 模型 | Qwen3-8B + eagle3 草稿 · TP2 · CARD=4,5 |
| Run | `keep-set-retest-20261022` · `S22-layers-20261023T145540` |

## 1 · 现象

投机接受率异常被大量抓住（47/48）；**判坏文本计数为 0**（没有跨请求乱码串）。样本见 [evidence/samples/](./evidence/samples/)。

## 2 · 案例背景 / 构造

Rejection 与 residual resample 共用 RNG、无独立 salt（对照修复 [ascend#18657](https://github.com/vllm-project/vllm-ascend/pull/18657)）。细节见 [evidence/规格说明.md](./evidence/规格说明.md)；补丁见 [evidence/overlay.patch](./evidence/overlay.patch)。

## 3 · Guard 结果

**检出。** **116 / 0 / 48**。结案：**KV 不一致→定界**，但 **两组不同向**——一对在靠后生成步出现相似度分叉，另一对全程干净；无数值崩溃（见事实）。

## 4 · 复现技巧

| 项 | 怎么做 |
|----|--------|
| Overlay | `gen_s22_overlay.py` → `22_spec_resample_rng_collide.patch`（可直接 `git apply`） |
| 模型 | Qwen3-8B + `Qwen3-8B-speculator.eagle3` |
| 负载 | 温度 0.8 · 投机 token 数 3 · 并发 48 |
| detector | 同时开接受率 + 复读（主看接受率） |
| 注意 | 树内 `resample.py` 可能是 CRLF 换行；生成补丁时不要用会剥掉回车的文本模式 |

## 5 · 定界分析

### 事实

- **清洁标杆（≥2 组）：** 干净服务重放对照；**2 组**；shape 一致；有效槽有限（无 NaN/Inf）。对比窗约 `n_prompt=14`，prompt 长度 + 输出长度 − 1≈21 / 20。
- **两组不同向（重要）：** 数值问题格两对都是 **0**；但**余弦只有一对分叉、另一对全程干净**（非两组同向）。
- **对 A：** 靠后的生成步（约第 21 个可比 token，角色 `out[6]`）在 dump 名 `layer_72` 首次余弦低于阈值（≈0.971；同 token 最差≈0.968 @ `layer_73`）。
- **对 B：** 无余弦分歧。
- **模型层 tok0：** 两对在 prompt 第 1 个 token 上 `model.layers.*` 最差仍≈1.0。
- **dump 层数：** 本窗约 74 个名字（含投机相关层），高于普通 36+36；细节以 `evidence/kv_v516_numeric_first.json` 为准。
- 证据：`evidence/kv_*.json`；验证机耐久 `verified_kv/S22/`（**.pt 未入库**；对 1 表2 全层来自本轮 `.pt`）。



### KV 对账表

分桶（可读性）：`≈1`≥0.99；`0.9–0.99`；`0.8–0.9`；`0.6–0.8`；`0.3–0.6`；`0.1–0.3`；`<0.1`（含负值）；数值问题写清子类型。

数据来自本轮 `keep-set-retest-20261022` `.pt`（耐久副本 `verified_kv` / home）；`evidence/kv_v516_numeric_first.json`。**只钉一轮**，未混其他目录。

两对结论**不一致**，分列如下。

**对 1**

**代表对**（`req_id`=`cmpl-b6f0819f7cce6b53-0-b49cdd90`；对比窗 **21** token，其中 prompt **14**）。
**表1 · 每 token 最差格**
| token 序号 | 角色 | 该 token 最差格 |
| --- | --- | --- |
| 0 | prompt[0] | ≈1（最差 layer_67） |
| 1 | prompt[1] | ≈1（最差 layer_67） |
| 2 | prompt[2] | ≈1（最差 layer_61） |
| 3 | prompt[3] | ≈1（最差 layer_61） |
| 4 | prompt[4] | ≈1（最差 layer_69） |
| 5 | prompt[5] | ≈1（最差 layer_61） |
| 6 | prompt[6] | ≈1（最差 layer_71） |
| 7 | prompt[7] | ≈1（最差 layer_71） |
| 8 | prompt[8] | ≈1（最差 layer_71） |
| 9 | prompt[9] | ≈1（最差 layer_59） |
| 10 | prompt[10] | ≈1（最差 layer_47） |
| 11 | prompt[11] | ≈1（最差 layer_61） |
| 12 | prompt[12] | ≈1（最差 layer_73） |
| 13 | prompt[13] | ≈1（最差 layer_63） |
| 14 | out[0] | ≈1（最差 layer_71） |
| 15 | out[1] | ≈1（最差 L33） |
| 16 | out[2] | ≈1（最差 layer_63） |
| 17 | out[3] | ≈1（最差 layer_61） |
| 18 | out[4] | ≈1（最差 layer_63） |
| 19 | out[5] | ≈1（最差 layer_61） |
| 20 | out[6] | 0.9–0.99（0.9678 @ `layer_73`） |

**表2 · 首个出问题的 token 的逐层剖面（全层）** — **首个出问题的 token**（`token_idx=20` role=`out[6]`；`min_cos`≈0.9678 @ `layer_73`）。

| 层（model.layers） | 余弦 | 分桶 |
| --- | --- | --- |
| L0 | ≈1 | ≈1 |
| L1 | ≈1 | ≈1 |
| L2 | ≈1 | ≈1 |
| L3 | ≈1 | ≈1 |
| L4 | ≈1 | ≈1 |
| L5 | ≈1 | ≈1 |
| L6 | ≈1 | ≈1 |
| L7 | ≈1 | ≈1 |
| L8 | ≈1 | ≈1 |
| L9 | ≈1 | ≈1 |
| L10 | ≈1 | ≈1 |
| L11 | ≈1 | ≈1 |
| L12 | ≈1 | ≈1 |
| L13 | ≈1 | ≈1 |
| L14 | ≈1 | ≈1 |
| L15 | ≈1 | ≈1 |
| L16 | ≈1 | ≈1 |
| L17 | ≈1 | ≈1 |
| L18 | ≈1 | ≈1 |
| L19 | ≈1 | ≈1 |
| L20 | ≈1 | ≈1 |
| L21 | ≈1 | ≈1 |
| L22 | ≈1 | ≈1 |
| L23 | ≈1 | ≈1 |
| L24 | ≈1 | ≈1 |
| L25 | ≈1 | ≈1 |
| L26 | ≈1 | ≈1 |
| L27 | ≈1 | ≈1 |
| L28 | ≈1 | ≈1 |
| L29 | ≈1 | ≈1 |
| L30 | ≈1 | ≈1 |
| L31 | ≈1 | ≈1 |
| L32 | ≈1 | ≈1 |
| L33 | ≈1 | ≈1 |
| L34 | ≈1 | ≈1 |
| L35 | ≈1 | ≈1 |
| L36 | ≈1 | ≈1 |

**对 2**（`req_id`=`cmpl-ab0f42815521a8cd-0-a8f36148`；对比窗 **20** token，其中 prompt **14**）。

**表1 · 每 token 最差格**

| token 序号 | 角色 | 该 token 最差格 |
| --- | --- | --- |
| 0 | prompt[0] | ≈1（最差 layer_67） |
| 1 | prompt[1] | ≈1（最差 layer_61） |
| 2 | prompt[2] | ≈1（最差 layer_67） |
| 3 | prompt[3] | ≈1（最差 layer_61） |
| 4 | prompt[4] | ≈1（最差 layer_69） |
| 5 | prompt[5] | ≈1（最差 model.layers.33.self_attn.attn） |
| 6 | prompt[6] | ≈1（最差 layer_71） |
| 7 | prompt[7] | ≈1（最差 layer_61） |
| 8 | prompt[8] | ≈1（最差 layer_63） |
| 9 | prompt[9] | ≈1（最差 layer_69） |
| 10 | prompt[10] | ≈1（最差 model.layers.33.self_attn.attn） |
| 11 | prompt[11] | ≈1（最差 layer_61） |
| 12 | prompt[12] | ≈1（最差 layer_63） |
| 13 | prompt[13] | ≈1（最差 layer_47） |
| 14 | out[0] | ≈1（最差 layer_63） |
| 15 | out[1] | ≈1（最差 layer_61） |
| 16 | out[2] | ≈1（最差 layer_63） |
| 17 | out[3] | ≈1（最差 layer_61） |
| 18 | out[4] | ≈1（最差 layer_63） |
| 19 | out[5] | ≈1（最差 layer_69） |

**表2 · 首个出问题的 token 的逐层剖面** — **无问题 token，跳过**（本对对比窗全程 ≈1；与对 1 结论不一致）。

### 推断

- 一对上已有晚步相似度分歧 → 按门闩记 **KV 不一致→定界**；**非两组同向**，不定界到「缺 salt」唯一路径。
- 根因叙事仍锚定无 SALT 的 shared RNG（规格 / #18657）；本窗 KV 只证明「有分歧窗口」。

### 结论

- 结案档：**KV 不一致→定界**（检出；一对分叉 / 一对干净）。

## 6 · 证据文件

| 文件 | 用途 |
|------|------|
| `evidence/overlay.patch` | 异常构造（无 #19285） |
| `evidence/规格说明.md` | 规格 + 实测 |
| `evidence/三层计数.json` / `跑批结果.json` | 三层 / 摘要 |
| `evidence/samples/` / `reports/` | 样本 / 报告 |
| `evidence/kv_*.json` | 对账 |

## 7 · 上游 PR 关系

| PR / 链接 | 角色 |
|-----------|------|
| [ascend#18657](https://github.com/vllm-project/vllm-ascend/pull/18657) | 根因修复（补 salt） |
| [vLLM#61161](https://github.com/vllm-project/vllm/pull/61161) | cousin |
| [ascend#19285](https://github.com/vllm-project/vllm-ascend/pull/19285) | 抓 dump 辅助（非本 anomaly） |
