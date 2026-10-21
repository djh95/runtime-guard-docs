# MRV1 Runtime Guard backport — CHANGELOG

格式：新版本写在最上方。每条写清：**包版本、各 release BASE、SOURCE、怎么得到、含哪些功能、冒烟**。

## mrv1-rg.1 — 2026-10-21

### 版本与来源

| 项 | 值 |
|----|-----|
| **包版本** | `mrv1-rg.1` |
| **Guard SOURCE** | `9343c9859`（`feat/runtime-guard-config-v1` tip：V1 restore + 控制面） |
| **适配方式** | 每档 BASE 干净树上复制 `runtime_config` / `runtime_guard`，再外科接线 `model_runner_v1.py` + `worker.py` + `ascend_config` / `logger`；**不**改 `worker/v2/model_runner.py` |
| **明确不含** | anomaly overlay；main `#18644` / G2 pin `f2aefd068…` |

### 各 release BASE

| Release 目录 | 上游 checkout | BASE full | Patch |
|--------------|---------------|-----------|-------|
| `v0.23.0` | tag `v0.23.0`（post1 兼容） | `5cb98caaadeff42b5b62b996e34bb2aaa29d20fd` | `v0.23.0/patches/0001-runtime-guard-mrv1-wiring.patch` |
| `v0.26.0rc1` | tag `v0.26.0rc1` | `f2f74a16c3c50a76f4349d807918e83edec1e35c` | `v0.26.0rc1/patches/…` |
| `v0.27.1rc1` | tag `v0.27.1rc1` | `3b31886237ed65c435e0965b10e8002ff5769766` | `v0.27.1rc1/patches/…` |
| `v0.28.0rc1` | tag `v0.28.0.rc1` | `96df623103f921df1a4488170d106f36689acb59` | `v0.28.0rc1/patches/…` |
| `v0.30.0` | `6d25ba2b3`（与 `05_v030` / `v0.30-rg.2` **同一 BASE**） | `6d25ba2b3c123bf963966cd583e985979d7a8a7d` | `v0.30.0/patches/…` |

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
