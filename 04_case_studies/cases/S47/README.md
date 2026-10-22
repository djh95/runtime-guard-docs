# S47 · Attn K/V swap（复现未抓到）

公开自洽案例包。

## 归档钉点

| 项 | 值 |
|----|-----|
| 结案 | **复现未抓到** |
| 检测 | **检出** |
| 三层率 | **58 / 37 / 48** |
| Detector | `token_repeat` |
| Origin | `both`（constructed） |
| Guard pin | G2 · `f2aefd068c4bd299d91cf0a1fdf642a3f327308f` |
| Run | 47_kv_swap-20261017T164919|

## 1 · 现象

CJK / Trail 塌缩；`token_repeat`×48。

## 2 · 根因

在 `reshape_and_cache` / FA 前 swap key/value。不等于 S34 / S35 / S41。

## 3 · Guard 结果

**检出。** **58 / 37 / 48**。结案档：**复现未抓到**。

## 4 · 复现技巧

按本包 pin / overlay 对齐三层率。本包是 Attn 算子问题类（K/V swap）的对外保留代表（构造见「根因」）。

## 5 · 定界分析

### 事实

- 现象 / 检测见上文钉点与 samples（或 reports）。
- **有效 KV 对账：无。** 本包曾归档的 `kv_compare.json` 及其中「首不一致 / 层号 / 余弦」结论**全部撤回**（新旧跑次混用、空 prompt、弱窗、全 NaN 占位等问题，不可信）。

### 推断

- 在重做**同一次异常请求**的有效异常 dump ↔ 标杆对账之前，**不能**得出「排除 KV」或「KV 不一致定界」。
- 坏输出 / 构造预期 ≠ 已证根因。

### 结论

- 结案档：**复现未抓到**（有异常或检出证据，但无有效异常 KV 可对账）。
- **尚未做有效 KV 对账**；分析不出 / 证据不足。


## 6 · 证据文件
| 文件 | 用途 |
|------|------|
| `evidence/overlay.patch` | 制造异常的静态补丁 |
| `evidence/规格说明.md` | 复现规格（Origin / 锚点 / overlay / knobs / 期望 detector） |
| `evidence/三层计数.json` | 三层明细（trigger / precision / detect） |
| `evidence/跑批结果.json` | 跑批元数据 + 结案摘要 |
| `evidence/samples/` | prompt + completion 样本 |
| `evidence/reports/` | Guard detector 报告 |

## 7 · 上游 PR 关系
| PR / 链接 | 角色 |
|-----------|------|
| （constructed K/V swap） | 无单一上游修复 PR；Attn 类代表 |
