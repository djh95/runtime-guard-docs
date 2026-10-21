---
name: apply-v030-mrv2-patch
description: >-
  Apply Runtime Guard MRV2 wiring from runtime-guard-docs/05_v030_backport
  onto a clean releases/v0.30.0 BASE (v0.30-rg.*). Wiring only (no anomaly
  overlay). For MRV1 on v0.30 or older releases use apply-mrv1-patch.
---

# apply-v030-mrv2-patch（支持 0.30 MRV2）

**类型：运维 / 接线。** 对干净 `releases/v0.30.0` BASE 打 `05_v030_backport` 的 Guard→**Model Runner V2** 补丁。

包说明：[05_v030_backport/README.md](https://github.com/djh95/runtime-guard-docs/blob/main/05_v030_backport/README.md) · [CHANGELOG](https://github.com/djh95/runtime-guard-docs/blob/main/05_v030_backport/CHANGELOG.md)

## When

- 发布线 **`releases/v0.30.0`**（含 rc），源码无 Guard，且跑 **MRV2**

## Not this skill

| 需求 | 改用 |
|------|------|
| 任意 release × **MRV1**（含 v0.30 MRV1） | `apply-mrv1-patch` → `05_mrv1_backport` |
| anomaly / G2 | 案例包；非本接线包 |

## Steps

1. 读 CHANGELOG，checkout **BASE**（现行 `v0.30-rg.3` → `6d25ba2b3`；SOURCE `#18450` @ `96046a3f0`，含 #18644）。  
2. 确认未叠打 `05_mrv1_backport/v0.30.0`。  
3. 执行：

```bash
bash /path/to/runtime-guard-docs/05_v030_backport/apply_patch.sh \
  /path/to/vllm-ascend
```

4. 重建 / 安装后按 [01](https://github.com/djh95/runtime-guard-docs/blob/main/01_enable_and_start/README.md) 启 Guard（**MRV2**）。  
5. 记录 `git rev-parse HEAD` 与包版本（CHANGELOG）。

冲突 → 停，回报 `git status`。
