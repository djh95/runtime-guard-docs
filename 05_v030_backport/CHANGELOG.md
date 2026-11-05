# v0.30 Runtime Guard backport — CHANGELOG

格式：新版本写在最上方。每条必须写清：**版本号、BASE、SOURCE/PR、怎么得到、含哪些功能**。

## v0.30-rg.3 — 2026-10-21

### 版本与来源

| 项 | 值 |
|----|-----|
| **包版本** | `v0.30-rg.3` |
| **适用基线 BASE** | `6d25ba2b3`（`releases/v0.30.0` 上 Guard 合入前一 commit） |
| **SOURCE tip** | `96046a3f0` |
| **上游 PR（推荐来源）** | https://github.com/vllm-project/vllm-ascend/pull/18450 |
| **PR 分支** | `cherry-pick/pr-16849-to-releases-v0.30.0` |
| **Patch 文件** | `patches/0001-runtime-guard-from-pr18450-6d25ba2b3-to-96046a3f0-20261021.patch` |

### 怎么得到

```text
git diff 6d25ba2b3..96046a3f0
# 等价：generate_patch_bundle.sh --base 6d25ba2b3 --source 96046a3f0
# （--from-pr 18450 在本地已有 PR tip 时亦可；上游 origin 上该分支名可能不可见）
```

即 **PR #18450 在 releases/v0.30.0 上的完整提交区间**（已冲突解决），**不是**从 `main` tip 白名单硬导出。

区间内 commits：

1. `60c99586c` — `[Feature] Add runtime_guard control plane … (#16849)`（cherry-pick）  
2. `96046a3f0` — `[Observability][BugFix] Skip hot shells when fully off and match main #18644`（替换旧 Perf tip `59ea3890d`）

### 对应功能

| 功能 | 说明 |
|------|------|
| Runtime Guard 控制面 | detect / report / `dump_kv`；MRV2 接线 |
| Detectors | `token_repeat` / `logits_finite` / `spec_acceptance`（默认关） |
| Hot-reload / manual dump | 启动参数 + live JSON |
| Static idle 性能 | 无热更/无 detector/无 dump 时跳过 wave/sample/eow 壳（`is_fully_off`） |
| main #18644 鲁棒对齐 | qsl 边界、空 list、None accepted、`group_rank`（`rank_in_group` → `is_first_rank`）等，经 PR tip 第二 commit 带入 |

### 冒烟

在干净 `6d25ba2b3` worktree 上 `git apply --check` / `apply_patch.sh` 一次通过。

### 已知限制

- Analysis 离线包不在此 patch 内。  
- 若你的树不是 `6d25ba2b3`（例如更早的 `v0.30.0rc1`），可能有冲突，需维护者按该 BASE 重导或手工解决冲突（2026-11-04 起 `apply_patch.sh` 对此默认拒绝，`--force-base` / `--3way` 显式选择）。

### 已知限制（2026-11-04 外部评审核验补充）

- **RG04（P2）**：本包与 MRV1 同源携带 `_enrich_detail_with_block_meta` 异步富化路径（以保存的 `req_idx` 读当前 batch 行、不校验行身份）；请求结束 / batch 重排后，报告 `block_ids` 元数据可能归属错误请求（KV dump 路径另有 finished/reaped 保护）。修复前，报告 `block_ids` 仅供人工参考。
- 核验备注：外部评审 RG01（缺 `apply_ascend_log_level`）/ RG03（缺 `None` 保护）仅影响 **MRV1** 包；本包已含模块级 `apply_ascend_log_level` 与 `accepted_token_nums is None` 保护。MRV2 接受统计走 `postprocess_sampled` stash 路径（包内无 `num_accepted_tokens_cpu` 读点），MRV1 的一拍错位结论（RG02）不直接迁移，但 MRV2 也未经同等审计。
- `generate_patch_bundle.sh`（2026-11-04 修复，RG05）：改为临时文件生成、成功后原子替换，空 diff / git 失败 / 中断不再删除已有制品。

---

## v0.30-rg.2 — 2026-10-14（已废弃，勿再分发）

| 项 | 值 |
|----|-----|
| **包版本** | `v0.30-rg.2` |
| **BASE** | `6d25ba2b3` |
| **SOURCE tip** | `59ea3890d`（已非 #18450 tip；第二 commit 已重写） |
| **Patch 文件** | `patches/0001-runtime-guard-from-pr18450-6d25ba2b3-to-59ea3890d-20261014.patch`（已删除） |
| **问题** | tip 不含现行 #18644 对齐；`59ea3890d` 不是 `96046a3f0` 祖先 |

已被 **v0.30-rg.3** 替换。

---

## v0.30-rg.1 — 2026-10-14（已废弃，勿再分发）

| 项 | 值 |
|----|-----|
| **BASE** | `v0.30.0rc1` (`5f828ad63`) |
| **SOURCE** | main 侧 tip `fc283a9d6`（白名单路径 diff） |
| **问题** | 非 release cherry-pick 产物；与 PR #18450 不对齐，易夹带 main 语境 |

已被 **v0.30-rg.2** / **v0.30-rg.3** 替换。

---

## 版本号约定

`v0.30-rg.<N>`：面向 `releases/v0.30.0` 发布线（含 rc）/ 未合入 Guard 树的第 N 次 backport 包。适用 BASE 以本文件各版本表为准（当前推荐 `6d25ba2b3`）。

必填字段：`BASE`、`SOURCE`/`PR`、`怎么得到`、`对应功能`、冒烟结果。
