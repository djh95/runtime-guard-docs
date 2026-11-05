# MRV1 Runtime Guard backport — CHANGELOG

格式：新版本写在最上方。每条写清：**包版本、各 release BASE、SOURCE、怎么得到、含哪些功能、冒烟**。

上游 PR / commit 对照（living）：**[PR_COMMIT_MAP.md](./PR_COMMIT_MAP.md)**。

## mrv1-rg.2 — 2026-10-21

### 版本与来源

| 项 | 值 |
|----|-----|
| **包版本** | `mrv1-rg.2` |
| **Guard SOURCE** | `9343c9859` + 各 release tip 适配（见 PR） |
| **上游 PR** | `#19337`（v0.23）`#19338`（v0.26）`#19339`（v0.27）`#19340`（v0.28）`#19341`（v0.30 MRV1） |
| **怎么得到** | PR tip 稳定后：`v0.23` / `v0.27` / `v0.28` 用 `git show <pr-tip>` 重导（仍 `git apply --check` 于 docs BASE）；`v0.26` / `v0.30` tip 与 BASE 冲突面不同，**离线 patch 字节保持 rg.1**（仍钉 BASE）；PR tip 为 tip-adapted |
| **相对 rg.1** | `v0.23` / `v0.27` / `v0.28` patch 字节更新（ruff / tip 上下文）；`v0.26` / `v0.30` 离线 patch **未改** |

### 各 release BASE

与 `mrv1-rg.1` 相同（见下行历史表）。冒烟：五档 `apply_patch.sh` 于干净 BASE **OK**。

### 已知限制（新增）

- `v0.26` / `v0.30`：**PR tip ≠ BASE patch 字节**（tip 上 `model_runner_v1` / `worker` 已漂移）；离线仍打 BASE；合入 tip 请用对应 PR。  
- v0.30 MRV1 `#19341` 与 MRV2 `#18450` **互斥**。

### 已知限制（2026-11-04 外部评审补充，尚未随包修复）

外部评审（2026-10-28，钉 `45bc260`）+ 本仓静态核验：**五档同源补丁，全部受影响**。

- **RG01（P1，阻断启服）**：控制面构造时无条件 `from vllm_ascend.logger import apply_ascend_log_level`，但本包只给 `logger.py` 带入 `init_logger_ascend`，五档 BASE 均无该符号 → API 初始化即 `ImportError`，**检测器全关也无法启服**。修复：从 SOURCE `9343c9859` 补入真实 `apply_ascend_log_level` 及依赖闭包（MRV2 `v0.30-rg.3` 已含，可对照移植）；冒烟标准须从 `git apply --check` 升级为真实 `RuntimeConfig` 初始化。
- **RG02（P1，统计口径）**：`accepted_token_nums_fn` 读 `input_batch.num_accepted_tokens_cpu`，该值晚一拍发布，spec_acceptance 报告的接受计数对应**前一步**采样（外部评审 9360 步报告中 8424 个可比位置全部对应前一步）。取数修正需在目标 NPU 回归后合入；此前解读 spec 告警须注意窗口错拍。
- **RG03（P2）**：本包明确不含 main `#18644`，`spec_acceptance.check_all` 无 `None` 保护（短 batch 边界保护已含）；`03_detectors/spec_acceptance.md` 的「None 安全跳过」承诺按 main 口径书写，与本包实现不符。计数为 `None` 时经 soft-fail 抛 `TypeError`，仅跳过本波 spec 检测（服务不崩）。
- **RG04（P2）**：异步报告富化 `_enrich_detail_with_block_meta` 用保存的 `req_idx` 读**当前** `input_batch` 行，不校验行身份；请求结束 / batch 重排后报告 `block_ids` 元数据可能归属错误请求（KV dump 路径另有 finished/reaped 保护）。修复前，报告 `block_ids` 仅供人工参考。

维护更新（2026-11-04，脚本随仓修复，不产生新包版本）：

- `apply_patch.sh`：默认校验 HEAD==CHANGELOG 表列 BASE 且要求干净树，错误基线默认拒绝；三方合并改为 `--3way` 显式选择，`--force-base` 跳过校验。原「打印 BASE 说明但不强制 + 严格失败自动 `--3way`」行为废弃（RG06）。

---

## mrv1-rg.1 — 2026-10-21

### 版本与来源

| 项 | 值 |
|----|-----|
| **包版本** | `mrv1-rg.1` |
| **Guard SOURCE** | `9343c9859`（`feat/runtime-guard-config-v1` tip：V1 restore + 控制面） |
| **适配方式** | 每档 BASE 干净树上复制 `runtime_config` / `runtime_guard`，再最小化改动 `model_runner_v1.py` + `worker.py` + `ascend_config` / `logger`；**不**改 `worker/v2/model_runner.py` |
| **明确不含** | anomaly overlay；main `#18644` / G2 pin `f2aefd068…` |

### 各 release BASE

| Release 目录 | 上游 checkout | BASE full | Patch |
|--------------|---------------|-----------|-------|
| `v0.23.0` | tag `v0.23.0`（post1 兼容） | `5cb98caaadeff42b5b62b996e34bb2aaa29d20fd` | `v0.23.0/patches/0001-runtime-guard-mrv1-wiring.patch` |
| `v0.26.0rc1` | tag `v0.26.0rc1` | `f2f74a16c3c50a76f4349d807918e83edec1e35c` | `v0.26.0rc1/patches/…` |
| `v0.27.1rc1` | tag `v0.27.1rc1` | `3b31886237ed65c435e0965b10e8002ff5769766` | `v0.27.1rc1/patches/…` |
| `v0.28.0rc1` | tag `v0.28.0.rc1` | `96df623103f921df1a4488170d106f36689acb59` | `v0.28.0rc1/patches/…` |
| `v0.30.0` | `6d25ba2b3`（与 `05_v030` / `v0.30-rg.3` **同一 BASE**） | `6d25ba2b3c123bf963966cd583e985979d7a8a7d` | `v0.30.0/patches/…` |

### 对应功能

| 功能 | 说明 |
|------|------|
| Runtime Guard 控制面 | detect / report / `dump_kv`；`runtime_config` 热更入口 |
| **MRV1 接线** | `RuntimeGuardProcessor.bind`；`@runtime_guard_step` + `@runtime_guard_pre_sample_logits` on `execute_model`；`run_sample_phase` + `build_v1_async_gpu_output` on `sample_tokens`；worker `@runtime_guard_idle_step` |
| Detectors | `token_repeat` / `logits_finite` / `spec_acceptance`（默认关） |

### 冒烟

每档在干净 BASE worktree 上 `git apply --check` 通过；`v0.23.0` patch 对 tag `v0.23.0.post1` 亦 `--check` 通过。

### 已知限制

- Analysis 离线包不在此 patch 内。  
- 树必须是表中 BASE（或已验证兼容的 post1）；其它 tip 可能冲突。  
- `v0.30.0` 档与 `05_v030_backport` **互斥**：同 BASE 上打 MRV1 **或** MRV2，勿叠。  
- 本期取消 `v0.18.0`（不建目录）。

---

## 版本号约定

`mrv1-rg.<N>`：面向多 release × MRV1 接线包的第 N 次发布。适用 BASE 以本文件各版本表为准。
