# Guard PR / commit map（living）

跟踪 **Runtime Guard** 相关上游 PR 与各 release / patch 线对应关系。

**规则（拇指法则）：**  
**main 新增一个 PR → 其他 release/patch 分支新增对应 commit**（或独立 backport PR）。

本目录的 **MRV1 五档**是 **release-only**（不开 / 不更新 main 上的 V1 接线；main 将去 V1）。main 列填 **N/A（release-only）**。

离线 BASE 与包版本见 [CHANGELOG.md](./CHANGELOG.md)。v0.30 MRV2 包见 [`../05_v030_backport/`](../05_v030_backport/)。

---

## 总表

| Change / feature | main PR | main commit | v0.23 PR/commit | v0.26 PR/commit | v0.27 PR/commit | v0.28 PR/commit | v0.30 MRV1 PR/commit | v0.30 MRV2 (#18450) |
|------------------|---------|-------------|-----------------|-----------------|-----------------|-----------------|----------------------|---------------------|
| Runtime Guard control plane (detect / report / `dump_kv`) | [#16849](https://github.com/vllm-project/vllm-ascend/pull/16849) | `83b281c7162d80b99da30ac734b7d95834054af1` | TBD | TBD | TBD | TBD | N/A（MRV1 自带控制面，见下行） | [#18450](https://github.com/vllm-project/vllm-ascend/pull/18450) @ `60c99586c53ce8fe71070e515d0bca8ba7c0dc74`（open；含 `#16849` cherry-pick） |
| Hot-path idle bypass + robustness (`#18644`) | [#18644](https://github.com/vllm-project/vllm-ascend/pull/18644) | `3abf581d36eff8637382398635b5f64bc6edb488` | TBD | TBD | TBD | TBD | TBD（未单独 cherry-pick） | [#18450](https://github.com/vllm-project/vllm-ascend/pull/18450) @ `96046a3f045907829da492a9625e22dcbdade9e9`（open；第二 commit，对齐 main `#18644`） |
| **MRV1 wiring**（`model_runner_v1` + worker idle；release-only） | N/A（release-only；main 无 V1 接线） | N/A | [#19337](https://github.com/vllm-project/vllm-ascend/pull/19337) @ `6a8aac343f0087f2abe50dab7134bc9e6ac8a818` | [#19338](https://github.com/vllm-project/vllm-ascend/pull/19338) @ `2685ed88ec0fcc08a411e2d120e1be0b9656b1a1` | [#19339](https://github.com/vllm-project/vllm-ascend/pull/19339) @ `f678f4e6d8687fb0f7100edac06f96ed2cecb677` | [#19340](https://github.com/vllm-project/vllm-ascend/pull/19340) @ `7508a0e8b0ba47b1cf139e5f3e94d2ff855d9f4d` | [#19341](https://github.com/vllm-project/vllm-ascend/pull/19341) @ `8b11f6fa7ebe65dbb5b808590468cd7be8735cdc` | **互斥** — 勿与 MRV1 叠打；见 `#18450` / `05_v030_backport` |

---

## main 基线（当前恰好 2 个已合入 Guard PR）

| # | Title | Merge commit | Merged |
|---|-------|--------------|--------|
| [#16849](https://github.com/vllm-project/vllm-ascend/pull/16849) | `[Feature] Add runtime_guard control plane (detect, report, dump_kv)` | `83b281c7162d80b99da30ac734b7d95834054af1` | 2026-10-12 |
| [#18644](https://github.com/vllm-project/vllm-ascend/pull/18644) | `[Observability][BugFix] Optimize hot-path overhead via static idle bypass and fix robustness issues` | `3abf581d36eff8637382398635b5f64bc6edb488` | 2026-10-20 |

> 验证：`gh pr list --repo vllm-project/vllm-ascend --state merged --base main --search runtime_guard` + `git log origin/main --grep=runtime_guard`。勿把未合入项（如 open `#19285`）算进 main 基线。

---

## MRV1 release-only PRs（本包）

| Release base | PR | Head SHA | Docs pin | Notes |
|--------------|----|----------|----------|-------|
| `releases/v0.23.0` | [#19337](https://github.com/vllm-project/vllm-ascend/pull/19337) | `6a8aac343f0087f2abe50dab7134bc9e6ac8a818` | `v0.23.0/` | |
| `releases/v0.26.0rc` | [#19338](https://github.com/vllm-project/vllm-ascend/pull/19338) | `2685ed88ec0fcc08a411e2d120e1be0b9656b1a1` | `v0.26.0rc1/` | tip-adapted `sample_tokens`（保留 `_input_fits_in_drafter`） |
| `releases/v0.27.1rc` | [#19339](https://github.com/vllm-project/vllm-ascend/pull/19339) | `f678f4e6d8687fb0f7100edac06f96ed2cecb677` | `v0.27.1rc1/` | |
| `releases/v0.28.0rc` | [#19340](https://github.com/vllm-project/vllm-ascend/pull/19340) | `7508a0e8b0ba47b1cf139e5f3e94d2ff855d9f4d` | `v0.28.0rc1/` | tip == docs BASE |
| `releases/v0.30.0` | [#19341](https://github.com/vllm-project/vllm-ascend/pull/19341) | `8b11f6fa7ebe65dbb5b808590468cd7be8735cdc` | `v0.30.0/` | **≠** `#18450`；勿改 `worker/v2/` |

Fork heads：`djh95:cherry-pick/mrv1-runtime-guard-to-releases-<line>`。

---

## 维护说明

1. main 再合入 Guard 相关 PR → **先**在本表新增一行（填 main PR + merge commit），**再**为各仍维护的 release/patch 线开 backport 或记 commit，空列写 TBD。  
2. MRV1 / MRV2 分列；v0.30 同 BASE 上二选一。  
3. 离线 patch 钉 docs **BASE**（见各 pin `BASE.md`）；上游 PR tip 可能超前 BASE（尤其 `v0.26` / `v0.30`）。  
4. 合入或 tip 变更后：更新本表 SHA，并按需重导 `patches/` + bump [CHANGELOG.md](./CHANGELOG.md)。
