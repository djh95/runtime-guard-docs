---
name: apply-mrv1-patch
description: >-
  Apply Runtime Guard MRV1 wiring from runtime-guard-docs/05_mrv1_backport
  onto a clean vllm-ascend BASE for one of: v0.23.0, v0.26.0rc1, v0.27.1rc1,
  v0.28.0rc1, v0.30.0. Wiring only (no anomaly overlay). For v0.30 MRV2 use
  apply-v030-mrv2-patch instead.
---

# apply-mrv1-patch（支持 MRV1）

**类型：运维 / 接线。** 对干净 BASE 树打 `05_mrv1_backport` 的 Guard→**Model Runner V1** 补丁。

包说明：[05_mrv1_backport/README.md](../../05_mrv1_backport/README.md) · [CHANGELOG](../../05_mrv1_backport/CHANGELOG.md)

## When

- 目标 release 在第一期 5 档内，且运行 **MRV1**
- 源码无 `runtime_guard`，或仅有 V2 接线而你需要 V1

## Not this skill

| 需求 | 改用 |
|------|------|
| v0.30 × **MRV2** | `apply-v030-mrv2-patch` → `05_v030_backport` |
| anomaly overlay / G2 pin | 案例包 / test 仓；**不是**本接线包 |
| 未适配 release（如 v0.18） | 停；标未适配，勿硬套 |

## Steps

1. 读 CHANGELOG / `<release>/BASE.md`，checkout **BASE**（`v0.28.0rc1` → tag `v0.28.0.rc1`；`v0.30.0` → `6d25ba2b3`）。  
2. 确认未叠打 `05_v030`（尤其 v0.30）。  
3. 执行：

```bash
bash /path/to/runtime-guard-docs/05_mrv1_backport/apply_patch.sh \
  --release <v0.23.0|v0.26.0rc1|v0.27.1rc1|v0.28.0rc1|v0.30.0> \
  /path/to/vllm-ascend
```

4. 重建 / 安装后按 [01](../../01_enable_and_start/README.md) 启 Guard（**MRV1**）。  
5. 记录 `git rev-parse HEAD` 与所用 `--release`。

冲突 → 停，回报 `git status`；勿 `--reject` 当生产。
