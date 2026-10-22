# S50 · SwiGLU gate/up half-swap（PASS）

公开自洽案例包。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结果 | **PASS** |
| 三层率 | **58 / 48 / 48** |
| Detector | `logits_finite` |
| Origin | `both`（constructed） |
| Guard pin | G2 · `f2aefd068c4bd299d91cf0a1fdf642a3f327308f` |
| Run | 50_swiglu_swap_halves-20261017T171204 @ builder 机 cards 12,13 |

## 1 · 现象

跨请求内容相同的 `!!!!`；`logits_finite`×48。score 侧常见 `token0_collapse`×48。

## 2 · 根因

先 `cat(up, gate)` 再 `npu_swiglu`。不等于 S39 skip-silu。无 force-write。

## 3 · Guard 结果

**PASS。** **58 / 48 / 48**。

## 4 · 复现技巧

按本包 pin / overlay 对齐三层率。本包是 SwiGLU 算子问题类的对外保留代表（构造见「根因」）。

## 5 · 教学要点

bang / NaN·Inf 塌缩可被 `logits_finite` 抓住。对照 **S07**（有限 logits + 乱码 → FAIL+GAP）。**S01** 是 dense 复现未出现，不是「有限乱码漏检」样板。禁把「`!!!!` → 所以 gate/up 对调」写成定界推论。

## 定界分析

### 事实

- 样本：跨请求内容相同的 `!!!!`（`evidence/samples/`）。
- 三层：58 / 48 / 48；detector：`logits_finite`。
- 归档 report `prompt_token_ids` 为空；有 `output_token_ids`。
- 包内无标杆 vs 异常 KV 对账；无同 prompt re-curl ids 归档。

### 推断

- 可确认：塌缩异常且 `logits_finite` 已检出 → PASS 有据。
- 坏输出推不出「SwiGLU gate/up 对调」——构造意图见「根因」。
- 无 KV 对账 → 不能排除或确认 KV。

### 结论

- 已定界到：异常输出 + `logits_finite` 检出。
- **尚未定界到** SwiGLU gate/up；**分析不出 / 证据不足**。
- KV：路径可用；归档尚未附结论。
- **定界结论：L1** = `logits_finite` 已命中；**L2** = 证据不足。

## 证据文件

| 文件 | 用途 |
|------|------|
| `evidence/overlay.patch` | 制造异常的静态补丁 |
| `evidence/规格说明.md` | 复现规格（Origin / 锚点 / overlay / knobs / 期望 detector） |
| `evidence/三层计数.json` | 三层明细（trigger / precision / detect） |
| `evidence/跑批结果.json` | 跑批元数据 + 结案摘要 |
| `evidence/samples/` | prompt + completion 样本 |
| `evidence/reports/` | Guard detector 报告（归档 report prompt 为空：合修前旧归档，见名词表 **report 空 prompt**；可读 prompt 看 samples，见 [④ 名词表](../../README.md#名词怎么读先看这里)） |


## 上游 PR 关系

| PR / 链接 | 角色 |
|-----------|------|
| （constructed SwiGLU half-swap） | 无单一上游修复 PR |
