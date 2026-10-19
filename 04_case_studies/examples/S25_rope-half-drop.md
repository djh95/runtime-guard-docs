# 案例：RoPE 第二半写丢（PASS）

## 元信息
- **ID:** S25 · **Type:** RoPE·positions · **Outcome:** 教学模版
- Guard pin: G2 · 协议: origin-faithful（见 `anomaly-PRINCIPLES.md`）
- 公开角色: **典型模版**（完整 runs/FE 在 test 仓库）

## 教学点
PR-rooted RoPE soft-inv（#7082）

## 现象
digit/`1.1.1…` 复读；`token_repeat`

## 三层率（归档）
`trigger / precision / detect` ≈ **462 / 15 / 48**

## Guard / skills 定界
- Online detect: 是 `token_repeat`
- Skills 到达: L2（RoPE half）
- **非 L4**：不宣称定位到算子行 / commit

## 证据路径（test 仓库）
- Fail-evidence: `runtime-guard-test/tests/build-anomaly-env/fail-evidence/S25/`（`WHY_PASS.md` + `layers.json`）
- Skills run: `runtime-guard-test/docs/anomaly-skills-runs/S25-20261017.md`

## 备注
≠ S11 pad-tail；≠ S28 style-flip（后者不进模版）。
