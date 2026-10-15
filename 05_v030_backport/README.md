# ⑤ 版本 patch（≤0.30.0 / 未合入 Guard 时）

## 何时需要

| 你的版本 | 怎么做 |
|----------|--------|
| **到 release `0.30.0`（含）** | 原生不支持 Guard；**如需要使用 Guard 能力，则必须打本目录 patch**，之后按 [01 启动](../01_enable_and_start.md) |
| **更晚的版本** | 先查功能文档链接（把 `main` 换成你的 tag/分支）。若 404 / 源码无 `runtime_guard` → 打本目录（或后续版本）patch；若已合入 → 不必打，直接启 |

当前包版本与功能清单见 **[CHANGELOG.md](./CHANGELOG.md)**（以最新 `v0.30-rg.*` 为准）。

## Patch 从哪来？（重要）

**推荐：从 release cherry-pick PR 导出，不要从 main 白名单硬抠。**

| 方式 | 说明 |
|------|------|
| **当前采用** | https://github.com/vllm-project/vllm-ascend/pull/18450 相对其 BASE 的完整 `git diff`（含功能 cherry-pick + static idle 性能 commit） |
| **不推荐** | `main` tip × 路径白名单 → `v0.30.0rc1`（易夹带 main 语境，与 CI 消解结果不一致） |

维护者一键重导：

> 注意：执行前本地 vllm-ascend 仓库需要配置好上游 origin 远程；生成 patch 后务必同步更新 CHANGELOG.md。

```bash
export VLLM_ASCEND_GIT=/path/to/vllm-ascend
git -C "$VLLM_ASCEND_GIT" fetch origin cherry-pick/pr-16849-to-releases-v0.30.0
bash generate_patch_bundle.sh --from-pr 18450
# 然后更新 CHANGELOG.md
```

> 本目录与 patch **不放入** vllm-ascend 代码仓；由文档包/运维包单独分发。

## 你需要什么

| 文件 | 作用 |
|------|------|
| [CHANGELOG.md](./CHANGELOG.md) | **版本、BASE、PR、功能清单**（先看这个） |
| [apply_patch.sh](./apply_patch.sh) | 在 **与 CHANGELOG 中 BASE 一致** 的干净树上按序打 `patches/*.patch` |
| [generate_patch_bundle.sh](./generate_patch_bundle.sh) | 维护者从 PR #18450（或显式 BASE/SOURCE）重导 patch |
| [patches/](./patches/) | 实际 `.patch` 文件 |

## 使用方（一线 / 集成）

```bash
# 1. 检出与 CHANGELOG「BASE」一致的干净树（v0.30-rg.2 示例）
git clone https://github.com/vllm-project/vllm-ascend.git
cd vllm-ascend
git checkout 6d25ba2b3   # 见 CHANGELOG；勿想当然用旧 rc1 除非该包写明

# 2. 确认 patches/ 与 CHANGELOG 版本号一致
# 3. 应用（把下面路径替换为本仓实际本地存放路径）
bash /path/to/runtime-guard-docs/05_v030_backport/apply_patch.sh "$(pwd)"

# 4. 安装 / 重建镜像后，按 01 启动 Guard
```

冲突时脚本会停住——把 `git status` 与冲突文件反馈维护者，**不要强行 --reject 后当生产用**。

## 对应功能（摘要）

以 CHANGELOG 最新包为准；v0.30-rg.2 含：

1. **控制面**：detect / report / `dump_kv`（来自 #16849 cherry-pick）  
2. **Static idle 性能**：默认全关时跳过热路径壳（PR #18450 上追加的 Perf commit）

## 能力与限制（打完 patch 后）

- 需要 **MRV2**；拓扑以 v0.30 worker 为准。  
- Analysis 离线脚本若不在包内，细定界仍要 analysis 工作区（见 [02](../02_problem_localization.md)）。  
- 与 `main` 后续 hardening（若未进 #18450）可能仍有差距——以 PR tip / CHANGELOG 为准，不假装「已等同最新 main」。

> 重要：该 backport 补丁包基于 #18450，**不包含 main 分支 #18644 的鲁棒性修复集合**（qsl 边界、空 list、None accepted、`group_rank` 等边界修复）。

## 相关

- 启动：[../01_enable_and_start.md](../01_enable_and_start.md)  
- 定界：[../02_problem_localization.md](../02_problem_localization.md)  
- Cherry-pick PR：https://github.com/vllm-project/vllm-ascend/pull/18450  
- 功能源 PR：https://github.com/vllm-project/vllm-ascend/pull/16849  
- main 分支鲁棒增强 PR（backport 包不含）：https://github.com/vllm-project/vllm-ascend/pull/18644  
- 上游文档（main）：https://github.com/vllm-project/vllm-ascend/blob/main/docs/source/user_guide/feature_guide/runtime_guard.md
