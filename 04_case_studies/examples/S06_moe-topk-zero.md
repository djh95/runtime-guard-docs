# 案例：MoE topk→0（PASS）

## 元信息
- **ID:** S06 · **Type:** MoE · **Outcome:** 教学模版
- Guard pin: G2 · 协议: origin-faithful（见 `anomaly-PRINCIPLES.md`）
- 公开角色: **典型模版**（完整 runs/FE 在 test 仓库）

## 教学点
MoE 路由最简 L2；公开模板只留这一个 MoE

## 现象
复读塌缩；`token_repeat`

## 三层率（归档）
`trigger / precision / detect` ≈ **70 / 1 / PASS（归档 detect）**

## Guard / skills 定界
- Online detect: 是 `token_repeat`
- Skills 到达: L2（MoE 路由）
- **非 L4**：不宣称定位到算子行 / commit

## 证据路径（test 仓库）
- Fail-evidence: `runtime-guard-test/tests/build-anomaly-env/fail-evidence/S06/`（`WHY_PASS.md` + `layers.json`）
- Skills run: `runtime-guard-test/docs/anomaly-skills-runs/S06-20261017.md`

## 备注
S16–S19 等同族不进公开模版（饱和）。
