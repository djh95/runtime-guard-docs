# 案例：Spec resample RNG/SALT（PASS）

## 元信息
- **ID:** S22 · **Type:** Spec · **Outcome:** 教学模版
- Guard pin: G2 · 协议: origin-faithful（见 `anomaly-PRINCIPLES.md`）
- 公开角色: **典型模版**（完整 runs/FE 在 test 仓库）

## 教学点
非文本主路径：分布性 `spec_acceptance`

## 现象
接受率异常偏低；偶发 `token_repeat`

## 三层率（归档）
`trigger / precision / detect` ≈ **130 / 45 / 48**

## Guard / skills 定界
- Online detect: 是 `spec_acceptance`（主）
- Skills 到达: L2（RNG/SALT）
- **非 L4**：不宣称定位到算子行 / commit

## 证据路径（test 仓库）
- Fail-evidence: `runtime-guard-test/tests/build-anomaly-env/fail-evidence/S22/`（`WHY_PASS.md` + `layers.json`）
- Skills run: `runtime-guard-test/docs/anomaly-skills-runs/S22-20261017.md`

## 备注
典型「独特 detector」课；origin soft-inv #18657。
