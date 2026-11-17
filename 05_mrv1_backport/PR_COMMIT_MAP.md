# Guard PR / commit map（living）

跟踪 **Runtime Guard** 相关上游 PR 与各 release / patch 线对应关系。

**维护规则：**  
**main 新增一个 PR → 其他 release/patch 分支新增对应 commit**（或独立 backport PR）。

本目录的 **MRV1 五档**是 **release-only**（不开 / 不更新 main 上的 V1 接线；main 将去 V1）。main 列填 **N/A（release-only）**。

离线 BASE 与包版本见 [CHANGELOG.md](./CHANGELOG.md)。v0.30 MRV2 包见 [`../05_v030_backport/`](../05_v030_backport/)。

---

## 如何读本表

| 记号 / 列 | 含义 |
|-----------|------|
| **TBD** | 该 release / patch 线**尚无**对应 backport commit 或 PR（账本空位，不是「SHA 未知」）。有了再填。 |
| **N/A** | 该线不适用（如 MRV1 = release-only，main 无 V1 接线）。 |
| **main PR / commit** | 已合入 main 的 Guard 相关变更；commit 为 **merge commit**。 |
| **release 列 `@ SHA`** | 未合入时写 **open PR head SHA**（勿 invent merge commit）；已合入再改 merge SHA。 |
| **离线 patch vs PR tip** | 本仓 `mrv1-rg.*` 的 `patches/*.patch` 是相对 docs **BASE** 生成的，给干净 BASE 离线 `git apply`。open MRV1 PRs（[#19337](https://github.com/vllm-project/vllm-ascend/pull/19337)–[#19341](https://github.com/vllm-project/vllm-ascend/pull/19341)）可能在 release 分支 tip 上还有适配提交。**相关但未必与「PR tip 树」字节相同**，除非按 tip 重导 patch。 |

**当前 tip ≠ 离线 patch 的档（仍钉 BASE 打 patch）：**

- **`v0.26.0rc1`** — PR tip 已 tip-adapt；离线 patch 仍相对 tag BASE `f2f74a16c`。
- **`v0.30.0`（MRV1）** — PR tip 已 rebase 到 `9746cad23`；离线 patch 仍钉 docs BASE `6d25ba2b3`（tip≠patch）。合 tip 请用 [#19341](https://github.com/vllm-project/vllm-ascend/pull/19341)。MRV2 线见 `#18450` / `v0.30-rg.5`。

`v0.23` / `v0.27` / `v0.28` 离线 patch 已按 PR tip 重导且仍 `--check` 于 docs BASE；`v0.28` tip == docs BASE。详见 [CHANGELOG.md](./CHANGELOG.md) `mrv1-rg.2`。

**怎么打离线包：** checkout 对应 **BASE**（见各 `<release>/BASE.md`），再跑 `apply_patch.sh`——**不要**先 checkout open PR tip 再打 docs patch。

---

## 总表

| Change / feature | main PR | main commit | v0.23 PR/commit | v0.26 PR/commit | v0.27 PR/commit | v0.28 PR/commit | v0.30 MRV1 PR/commit | v0.30 MRV2 (#18450) |
|------------------|---------|-------------|-----------------|-----------------|-----------------|-----------------|----------------------|---------------------|
| Runtime Guard control plane (detect / report / `dump_kv`) | [#16849](https://github.com/vllm-project/vllm-ascend/pull/16849) | `83b281c7162d80b99da30ac734b7d95834054af1` | TBD | TBD | TBD | TBD | N/A（MRV1 自带控制面，见下行） | [#18450](https://github.com/vllm-project/vllm-ascend/pull/18450) @ `b5d74a71d`（open；含 `#16849`；BASE `9746cad23`） |
| Hot-path idle bypass + robustness (`#18644`) | [#18644](https://github.com/vllm-project/vllm-ascend/pull/18644) | `3abf581d36eff8637382398635b5f64bc6edb488` | TBD | TBD | TBD | TBD | TBD（未单独 cherry-pick） | [#18450](https://github.com/vllm-project/vllm-ascend/pull/18450) @ `a7beb2e9a`（open；对齐 main `#18644`） |
| Keep prompt when detectors turn on late (`#19285`) | [#19285](https://github.com/vllm-project/vllm-ascend/pull/19285) | `3725f6b36fd18aff3c15bcea6843bbe5133675cf` | TBD | TBD | TBD | TBD | TBD | [#18450](https://github.com/vllm-project/vllm-ascend/pull/18450) @ `0ac331ab8`（open） |
| Soft-purge / on_disabled / config_version (`#21346`) | [#21346](https://github.com/vllm-project/vllm-ascend/pull/21346)（**open**） | — | TBD | TBD | TBD | TBD | TBD | [#18450](https://github.com/vllm-project/vllm-ascend/pull/18450) @ `eee49f551` tip 段（open） |
| Merged due bus + CPU/Gloo due-bits (`#21375`) | [#21375](https://github.com/vllm-project/vllm-ascend/pull/21375)（**open**） | — | TBD | TBD | TBD | TBD | TBD | [#18450](https://github.com/vllm-project/vllm-ascend/pull/18450) @ `6689dbf3f` tip（open） |
| **MRV1 wiring**（`model_runner_v1` + worker idle；release-only） | N/A（release-only；main 无 V1 接线） | N/A | [#19337](https://github.com/vllm-project/vllm-ascend/pull/19337) @ `83e46c019f8b7ce81f18ef36d2efb18a9f9872bb`（open） | [#19338](https://github.com/vllm-project/vllm-ascend/pull/19338) @ `53a6b1da96b3c151852be7b4988e11e61c108539`（open；tip≠BASE patch） | [#19339](https://github.com/vllm-project/vllm-ascend/pull/19339) @ `f678f4e6d8687fb0f7100edac06f96ed2cecb677`（open） | [#19340](https://github.com/vllm-project/vllm-ascend/pull/19340) @ `7508a0e8b0ba47b1cf139e5f3e94d2ff855d9f4d`（open；tip==BASE） | [#19341](https://github.com/vllm-project/vllm-ascend/pull/19341) @ `6efac4499954fc781264bcde0d4e7a3e655e3214`（open；tip≠BASE patch；已 rebase 到 release tip） | **互斥** — 勿与 MRV1 叠打；见 `#18450` / `05_v030_backport` |

---

## main 基线（已合入 Guard 相关）

| # | Title | Merge commit | Merged |
|---|-------|--------------|--------|
| [#16849](https://github.com/vllm-project/vllm-ascend/pull/16849) | `[Feature] Add runtime_guard control plane (detect, report, dump_kv)` | `83b281c7162d80b99da30ac734b7d95834054af1` | 2026-10-12 |
| [#18644](https://github.com/vllm-project/vllm-ascend/pull/18644) | `[Observability][BugFix] Optimize hot-path overhead via static idle bypass and fix robustness issues` | `3abf581d36eff8637382398635b5f64bc6edb488` | 2026-10-20 |
| [#19285](https://github.com/vllm-project/vllm-ascend/pull/19285) | `[BugFix][Observability] Keep prompt when detectors turn on late` | `3725f6b36fd18aff3c15bcea6843bbe5133675cf` | 2026-11-09 |

> 验证：`gh pr list --repo vllm-project/vllm-ascend --state merged --base main --search runtime_guard`。勿把仍 open 的 `#21346` / `#21375` 算进 main 已合入基线（但 v0.30 MRV2 `#18450` / `v0.30-rg.5` 已先行 backport）。

---

## MRV1 release-only PRs（本包）

| Release base | PR | Head SHA（open） | Docs pin | Notes |
|--------------|----|------------------|----------|-------|
| `releases/v0.23.0` | [#19337](https://github.com/vllm-project/vllm-ascend/pull/19337) | `83e46c019f8b7ce81f18ef36d2efb18a9f9872bb` | `v0.23.0/` | 2026-11-17 rebase 到 release tip；离线 patch 仍钉 docs BASE |
| `releases/v0.26.0rc` | [#19338](https://github.com/vllm-project/vllm-ascend/pull/19338) | `53a6b1da96b3c151852be7b4988e11e61c108539` | `v0.26.0rc1/` | 2026-11-17 rebase 到 release tip；**离线 patch ≠ tip 字节**（仍钉 BASE） |
| `releases/v0.27.1rc` | [#19339](https://github.com/vllm-project/vllm-ascend/pull/19339) | `f678f4e6d8687fb0f7100edac06f96ed2cecb677` | `v0.27.1rc1/` | 离线 patch 已按 tip 重导且 check 于 BASE |
| `releases/v0.28.0rc` | [#19340](https://github.com/vllm-project/vllm-ascend/pull/19340) | `7508a0e8b0ba47b1cf139e5f3e94d2ff855d9f4d` | `v0.28.0rc1/` | tip == docs BASE |
| `releases/v0.30.0` | [#19341](https://github.com/vllm-project/vllm-ascend/pull/19341) | `6efac4499954fc781264bcde0d4e7a3e655e3214` | `v0.30.0/` | **≠** `#18450`；已 rebase 到 `9746cad23`；离线 patch 仍钉旧 BASE `6d25ba2b3`；**尚未**带 `#19285`/`#21346`/`#21375`；勿改 `worker/v2/` |

维护者 fork 分支命名约定见内部备忘（不在对外导航展开）。

---

## 维护说明

1. main 再合入 Guard 相关 PR → **先**在本表新增一行（填 main PR + merge commit），**再**为各仍维护的 release/patch 线开 backport 或记 commit；尚无 backport 的格子写 **TBD**（含义见上「如何读本表」）。  
2. MRV1 / MRV2 分列；v0.30 同 BASE 上二选一。  
3. 离线 patch 钉 docs **BASE**（见各 pin `BASE.md`）；上游 PR tip 可能超前 BASE（尤其 `v0.26` / `v0.30`）——**TBD 与 tip≠patch 是两件事**。  
4. 合入或 tip 变更后：更新本表 SHA（未合入用 head + open），并按需重导 `patches/` + bump [CHANGELOG.md](./CHANGELOG.md)。
