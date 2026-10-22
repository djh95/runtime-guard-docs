# S26 · RMSNorm fp32 weight-mul（KV 一致→排除 KV）

公开自洽案例包。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案 | **KV 一致→排除 KV** |
| 检测 | **检出** |
| 三层率 | **470 / 14 / 48**（现行；detect=48/48；trigger/precision 随并发浮动，detect 为判定口径） |
| Detector | `token_repeat`（**threshold=8**） |
| Origin | `both` |
| Guard pin | G2 `f2aefd068` + 抓 dump 时临时合入 [#19285](https://github.com/vllm-project/vllm-ascend/pull/19285)（非空 `prompt_token_ids`） |
| 模型 | Qwen3-8B · TP2 · CARD=4,5 · `192.168.13.160` / `rg-test-160` |
| Run | 英文河名短句 × 48 并发 + 阈值 8；`keep-set-retest-20261022` |

## 1 · 现象

输出变成反复的数字串（如 `1.1.1…` / `1.0.0…`）；`token_repeat` 检出。样本见 [evidence/samples/](./evidence/samples/)。

## 2 · 案例背景 / 构造

Soft-inverse [vLLM#42379](https://github.com/vllm-project/vllm/pull/42379)：`AscendRMSNorm.forward_oot` 用错误的 fp32 乘权公式替代 `npu_rms_norm`。细节见 [evidence/规格说明.md](./evidence/规格说明.md)；补丁见 [evidence/overlay.patch](./evidence/overlay.patch)。

## 3 · Guard 结果

**检出。** 现行 **470 / 14 / 48**。结案档：**KV 一致→排除 KV**。

钉点 dump 用的 report：`prompt_token_ids` 长度 **14**（非空；依赖抓取时临时 #19285）。

## 4 · 复现技巧（必读）

| 项 | 现行复现（照这个做） |
|----|----------------------|
| Overlay | `gen_s26_overlay.py` 就地改 B 树 |
| Prompt | `Name one famous river. One short English sentence. id={i}.` |
| 并发 | **48 路同时发请求** |
| 其它 | `max_tokens=48`；temp=0 |
| detector | `token_repeat` **threshold=8** |
| 抓 dump | 需非空 `prompt_token_ids` → 临时合入 #19285（跑完还原） |

## 5 · 定界分析

### 事实

- 现象：`1.1.1…` / `1.0.0…` 复读（`evidence/samples/`）。
- 三层：**470 / 14 / 48**；detector：`token_repeat`（detect=48）。
- 钉点 report（×2，均非空 prompt）：`…90a56851`（n_prompt=14, n_output=8）、`…a45e21f3`（n_prompt=14, n_output=17）。见 `evidence/reports/`。
- 本包已归档 **≥2 组**异常↔标杆 KV 对账（`evidence/kv_compare.json`；cos_thresh=0.99；无全 NaN）。
- history 对比跨度：**`n_tokens = p + o − 1`**（两组分别为 21、30）。
- 标杆 vs 异常：两组对比窗**全程一致**（min-over-layers cos ≥ 0.999988）；首不一致：无。
- 服务器已验证 dump：`…/verified_kv/S26/`（约 **75M**，**未**入库 GitHub，仅摘要 `kv_compare.json`）。

### 推断

- 对账一致 → **排除 KV cache** 作为本请求坏输出的必要原因。
- 坏输出仍不能从文本推出构造根因；转向非 KV 类（RMSNorm / 本包构造）。
- 无首不一致 → 推不出污染时机窗口。

### 结论

- 结案档：**KV 一致→排除 KV**（本请求对比窗口；两组同跑钉点）。
- 尚未定界到具体算子/构造根因；分析不出 / 证据不足。

## 6 · 证据文件

| 文件 | 用途 |
|------|------|
| `evidence/overlay.patch` | 制造异常的静态补丁 |
| `evidence/规格说明.md` | 复现规格 |
| `evidence/三层计数.json` | 三层明细 |
| `evidence/跑批结果.json` | 跑批元数据 + 结案摘要 |
| `evidence/samples/` | prompt + completion 样本 |
| `evidence/reports/` | Guard detector 报告（钉点；非空 `prompt_token_ids`） |
| `evidence/kv_compare.json` | KV 标杆对比摘要（两组 match；history=`p+o-1`） |

## 7 · 上游 PR 关系

| PR / 链接 | 角色 |
|-----------|------|
| [vLLM#42379](https://github.com/vllm-project/vllm/pull/42379) | **根因修复**；本包 soft-inverse |
| [ascend#19285](https://github.com/vllm-project/vllm-ascend/pull/19285) | **抓 dump 辅助**：非空 `prompt_token_ids`；非本案例根因修复 |
