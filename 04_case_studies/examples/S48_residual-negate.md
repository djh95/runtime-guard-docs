# 案例：Residual negate（PASS）

## 元信息
- **ID:** S48 · **Type:** Residual · **Outcome:** 教学模版
- Guard pin: G2 · 协议: origin-faithful（见 `anomaly-PRINCIPLES.md`）
- 公开角色: **典型模版**（完整 runs/FE 在 test 仓库）

## 教学点
残差极性错 → `!!!!` / `logits_finite`

## 现象
全请求 bang 塌缩

## 三层率（归档）
`trigger / precision / detect` ≈ **100 / 48 / 48**

## Guard / skills 定界
- Online detect: 是 `logits_finite`
- Skills 到达: L2
- **非 L4**：不宣称定位到算子行 / commit

## 证据路径（test 仓库）
- Fail-evidence: `runtime-guard-test/tests/build-anomaly-env/fail-evidence/S48/`（`WHY_PASS.md` + `layers.json`）
- Skills run: `runtime-guard-test/docs/anomaly-skills-runs/S48-20261017.md`

## 备注
≠ S31 residual-drop（不进公开模版）。
