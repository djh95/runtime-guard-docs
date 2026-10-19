# 案例：KV skip-zero → 有限垃圾（GAP）

## 元信息
- **ID:** S01 · **Type:** KV·PD·pad · **Outcome:** 教学模版
- Guard pin: G2 · 协议: origin-faithful（见 `anomaly-PRINCIPLES.md`）
- 公开角色: **典型模版**（完整 runs/FE 在 test 仓库）

## 教学点
Detector 缺口：有限混合脚本垃圾，非 NaN/复读窗

## 现象
输出有限但仍为乱码/混合脚本；`logits_finite`/`token_repeat` 均易漏

## 三层率（归档）
`trigger / precision / detect` ≈ **136 / 25 / **0****

## Guard / skills 定界
- Online detect: 否（GAP）
- Skills 到达: 弱 L2（samples 提示）
- **非 L4**：不宣称定位到算子行 / commit

## 证据路径（test 仓库）
- Fail-evidence: `runtime-guard-test/tests/build-anomaly-env/fail-evidence/S01/`（`WHY_UNDETECTED.md` + `layers.json`）
- Skills run: `runtime-guard-test/docs/anomaly-skills-runs/S01-20261017.md`

## 备注
与 S10′ 对照：同大类 KV 问题，一边 PASS 一边 GAP。
