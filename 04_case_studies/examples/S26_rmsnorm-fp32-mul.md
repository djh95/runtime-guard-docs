# 案例：RMSNorm fp32 weight-mul（PASS）

## 元信息
- **ID:** S26 · **Type:** RMSNorm · **Outcome:** 教学模版
- Guard pin: G2 · 协议: origin-faithful（见 `anomaly-PRINCIPLES.md`）
- 公开角色: **典型模版**（完整 runs/FE 在 test 仓库）

## 教学点
PR-rooted soft-inv 样板（#42379）

## 现象
digit/复读；`token_repeat`

## 三层率（归档）
`trigger / precision / detect` ≈ **470 / 14 / 48**

## Guard / skills 定界
- Online detect: 是 `token_repeat`
- Skills 到达: L2（norm dtype）
- **非 L4**：不宣称定位到算子行 / commit

## 证据路径（test 仓库）
- Fail-evidence: `runtime-guard-test/tests/build-anomaly-env/fail-evidence/S26/`（`WHY_PASS.md` + `layers.json`）
- Skills run: `runtime-guard-test/docs/anomaly-skills-runs/S26-20261017.md`

## 备注
一 PR → 一类；C 矩阵 ones/zeros 变体不进 docs。
