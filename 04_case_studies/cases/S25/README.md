# S25 · RoPE 后半维丢失（second-half drop）（KV 一致→排除 KV）

公开自洽案例包。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案 | **KV 一致→排除 KV** |
| 检测 | **检出** |
| 三层率 | **462 / 15 / 48**（现行；detect=48/48；trigger/precision 随并发浮动，detect 为判定口径） |
| Detector | `token_repeat`（**threshold=8**） |
| Origin | `ascend-only` |
| Guard pin | G2 `f2aefd068` + 抓 dump 时临时合入 [#19285](https://github.com/vllm-project/vllm-ascend/pull/19285)（非空 `prompt_token_ids`） |
| 模型 | Qwen3-8B · TP2 · CARD=4,5 · `192.168.13.160` / `rg-test-160` |
| Run | 英文河名短句 × 48 并发 + 阈值 8；`keep-set-retest-20261022` |

## 1 · 现象

输出变成反复的数字串（如 `1.1.1…` / `1.0.0…`）；`token_repeat` 检出。样本见 [evidence/samples/](./evidence/samples/)。

## 2 · 案例背景 / 构造

Soft-inverse [ascend#7082](https://github.com/vllm-project/vllm-ascend/pull/7082)：`npu_rotary_embedding` 后恢复未旋转的后半维（缺 store 语义）。不等于 S11 的 pad 长度问题。细节见 [evidence/规格说明.md](./evidence/规格说明.md)；补丁见 [evidence/overlay.patch](./evidence/overlay.patch)。

## 3 · Guard 结果

**检出。** 现行 **462 / 15 / 48**。结案档：**KV 一致→排除 KV**。

钉点 dump 用的 report：`prompt_token_ids` 长度 **14**（非空；依赖抓取时临时 #19285）。对照：同 overlay、无 #19285 时曾出现空 prompt report。

## 4 · 复现技巧（必读）

目标症状（输出反复成 `1.1.1…`）**只在**下列现行复现下稳定出现：

| 项 | 现行复现（照这个做） |
|----|----------------------|
| Overlay | `gen_s25_overlay.py` 就地改 B 树 |
| Prompt | `Name one famous river. One short English sentence. id={i}.`（英文河名短句） |
| 并发 | **48 路同时发请求** |
| 其它 | `max_tokens=48`；temp=0 |
| detector | `token_repeat` **threshold=8** |
| 抓 dump | 需非空 `prompt_token_ids` → 临时合入 #19285（跑完还原） |

**历史错跑（不要照这个结案）：** 曾用「中文回声式」prompt、大约 **8 条串行**、阈值 **16** → 往往打不出 `1.1.1…`，detect=0。那是**复现条件不对**，不是漏检。

## 5 · 定界分析

### 事实

- 现象：`1.1.1…` / `1.0.0…` 复读（`evidence/samples/`）。
- 三层：**462 / 15 / 48**；detector：`token_repeat`（detect=48）。
- 钉点 report（×2，均非空 prompt）：`…894e9755`（n_prompt=14, n_output=8）、`…9da53275`（n_prompt=14, n_output=17）。见 `evidence/reports/`。
- 本包已归档 **≥2 组**异常↔标杆 KV 对账（`evidence/kv_compare.json`；cos_thresh=0.99；shape `[1,128,4,128]`；无全 NaN）。
- history 对比跨度：**`n_tokens = p + o − 1`**（两组分别为 21、30）；**禁止**按 `p+o` 全长比到未写入的末位。
- 标杆 vs 异常：两组对比窗**全程一致**（min-over-layers cos ≥ 0.999986）；首不一致：无。
- 服务器已验证 dump：`…/verified_kv/S25/`（相对 `keep-set-retest-20261022`；全量约 **94M** / 对账用 4×`dp0_tp0` 约 **37M**，**未**入库 GitHub，仅摘要 `kv_compare.json`）。

### 推断

- 对账一致 → **排除 KV cache** 作为本请求坏输出的必要原因。
- 坏输出仍不能从文本推出构造根因；转向非 KV 类（RoPE / 本包构造）。
- 无首不一致 → 推不出「prefill 中途 / 传写 / decode 前」等污染时机窗口。

### 结论

- 结案档：**KV 一致→排除 KV**（本请求对比窗口；两组同跑钉点）。
- 尚未定界到具体算子/构造根因；分析不出 / 证据不足。

## 6 · 证据文件

| 文件 | 用途 |
|------|------|
| `evidence/overlay.patch` | 制造异常的静态补丁 |
| `evidence/规格说明.md` | 复现规格（Origin / 锚点 / overlay / knobs / 期望 detector） |
| `evidence/三层计数.json` | 三层明细（trigger / precision / detect） |
| `evidence/跑批结果.json` | 跑批元数据 + 结案摘要 |
| `evidence/samples/` | prompt + completion 样本 |
| `evidence/reports/` | Guard detector 报告（钉点；非空 `prompt_token_ids`） |
| `evidence/kv_compare.json` | KV 标杆对比摘要（两组 match；history=`p+o-1`） |

## 7 · 上游 PR 关系

| PR / 链接 | 角色 |
|-----------|------|
| [ascend#7082](https://github.com/vllm-project/vllm-ascend/pull/7082) | **根因修复**；本包 soft-inverse |
| [ascend#19285](https://github.com/vllm-project/vllm-ascend/pull/19285) | **抓 dump 辅助**：非空 `prompt_token_ids`；非本案例根因修复 |
