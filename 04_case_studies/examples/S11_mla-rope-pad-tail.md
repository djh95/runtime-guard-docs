# 案例：MLA RoPE pad-tail（PASS）

## 元信息
- **ID:** S11 · **Type:** KV·PD·pad · **Outcome:** 教学模版
- Guard pin: G2 · 协议: origin-faithful（见 `anomaly-PRINCIPLES.md`）
- 公开角色: **典型模版**（完整 runs/FE 在 test 仓库）

## 教学点
Pad-tail RoPE 脏读；与 recycle-zero 不同 root-cause

## 现象
digit/复读塌缩；`token_repeat`

## 三层率（归档）
`trigger / precision / detect` ≈ **138 / 39 / 60**

## Guard / skills 定界
- Online detect: 是 `token_repeat`
- Skills 到达: L2（间接 KV）
- **非 L4**：不宣称定位到算子行 / commit

## 证据路径（test 仓库）
- Fail-evidence: `runtime-guard-test/tests/build-anomaly-env/fail-evidence/S11/`（`WHY_PASS.md` + `layers.json`）
- Skills run: 无独立 `Sxx-*.md` → 见 `runtime-guard-test/docs/anomaly-skills-runs/batch-pass-wave-20261017.md`

## 备注
无独立 skills-run 文件时见 batch-pass-wave。≠ S10′ recycle。
